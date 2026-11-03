// ASES scheduler evidence adapters v0.2. Pure, read-only, UTC only.
// No provider calls, no side effects, no inferred native slot identity.
export function utcMs(s,label) {
  if (typeof s!=="string" || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(s)) throw new Error("UTC_ISO_REQUIRED:"+label);
  const n=Date.parse(s); if(!Number.isFinite(n)) throw new Error("INVALID_TIMESTAMP:"+label); return n;
}
export function cronSlots(firstUtc,periodMinutes,asOfUtc) {
  const f=utcMs(firstUtc,"first"),a=utcMs(asOfUtc,"asOf");
  if(!Number.isSafeInteger(periodMinutes)||periodMinutes<1||periodMinutes>10080) throw new Error("INVALID_INTERVAL");
  const count=a<f?0:Math.floor((a-f)/(periodMinutes*60000))+1;
  if(count>10000) throw new Error("SLOT_LIMIT");
  return Array.from({length:count},(_,i)=>new Date(f+i*periodMinutes*60000).toISOString());
}
export function minimumLateness(firstUtc,periodMinutes,runCreatedUtc) {
  const f=utcMs(firstUtc,"first"),r=utcMs(runCreatedUtc,"created");
  if(!Number.isSafeInteger(periodMinutes)||periodMinutes<1||periodMinutes>10080) throw new Error("INVALID_INTERVAL");
  if(r<f) return {latest_possible_slot_utc:null,minimum_lateness_ms:null,reason:"BEFORE_FIRST_ELIGIBLE_SLOT"};
  const last=f+Math.floor((r-f)/(periodMinutes*60000))*periodMinutes*60000;
  return {latest_possible_slot_utc:new Date(last).toISOString(),minimum_lateness_ms:r-last,reason:"LOWER_BOUND_ONLY_SLOT_UNATTRIBUTED"};
}
export function githubReadback({payload,workflowId,firstEvaluableUtc,periodMinutes,asOfUtc}) {
  const first=utcMs(firstEvaluableUtc,"first");
  const asOf=utcMs(asOfUtc,"asOf");
  if(!Number.isSafeInteger(workflowId)) throw new Error("INVALID_WORKFLOW");
  const expected=cronSlots(firstEvaluableUtc,periodMinutes,asOfUtc).length;
  if(!payload || !Array.isArray(payload.workflow_runs) || !Number.isSafeInteger(payload.total_count) || payload.total_count<payload.workflow_runs.length)
    return {status:"OBSERVER_UNAVAILABLE",reason:"MALFORMED_OR_MISSING_COLLECTION",expected_slots:expected,runs:[]};
  const xs=payload.workflow_runs;
  const dated=xs.every(r=>r&&typeof r==="object"&&Number.isFinite(Date.parse(r.created_at)));
  if(!dated) return {status:"OBSERVER_UNAVAILABLE",reason:"INVALID_RUN_CREATED_AT",expected_slots:expected,runs:[]};
  const sorted=xs.every((r,i)=>i===0||Date.parse(xs[i-1].created_at)>=Date.parse(r.created_at));
  const complete=sorted && (payload.total_count===xs.length || (xs.length>0 && Date.parse(xs[xs.length-1].created_at)<=first));
  const matched=xs.filter(r=>r.workflow_id===workflowId&&r.event==="schedule"&&Date.parse(r.created_at)>=first&&Date.parse(r.created_at)<=asOf);
  if(new Set(matched.map(r=>String(r.id))).size!==matched.length) throw new Error("DUPLICATE_RUN_ID");
  return {
    status: complete?"OK":"OBSERVER_PARTIAL",
    reason:complete?"WINDOW_COVERED":"PAGINATION_OR_ORDER_INSUFFICIENT",
    expected_slots:expected,
    window_completeness:complete,
    returned_count:xs.length,
    collection_total_count:payload.total_count,
    run_creations_observed:matched.length,
    slot_attribution:matched.length?"SLOT_ATTRIBUTION_UNRESOLVED":"NO_RUN_VISIBLE_AS_OF_QUERY",
    permanently_missing_triggers:"NOT_ESTABLISHED",
    runs: matched.map(r=>({id:r.id,created_at:r.created_at,conclusion:r.conclusion??null,status:r.status??null,source:"schedule",...minimumLateness(firstEvaluableUtc,periodMinutes,r.created_at)}))
  };
}
export function gitlabReadback({pipelines,schedules,expectedSchedules=[],expectedRef=null,scheduleQueryStatus="UNAVAILABLE",pipelineQueryStatus="OK"}) {
  if(pipelineQueryStatus!=="OK"||!Array.isArray(pipelines))
    return {status:"OBSERVER_UNAVAILABLE",scheduled_pipelines:[],expected_slots:null};
  // A partial list (one of two planned schedules) is not sufficient.
  // Valid metadata still cannot establish an activation-adjusted slot denominator.
  const scheduleVerified=scheduleQueryStatus==="OK"
    &&Array.isArray(schedules)&&Array.isArray(expectedSchedules)&&expectedSchedules.length>0
    &&expectedSchedules.every(e=>schedules.some(s=>
      Number.isSafeInteger(s.id)&&s.active===true&&typeof s.created_at==="string"
      &&typeof s.next_run_at==="string"&&Number.isFinite(Date.parse(s.next_run_at))
      &&s.description===e.description&&s.cron===e.cron
      &&s.cron_timezone===(e.timezone||"UTC")&&s.ref===(e.ref||expectedRef)));
  const scheduled=pipelines.filter(x=>x.source==="schedule").map(x=>({id:x.id,created_at:x.created_at,status:x.status,sha:x.sha,ref:x.ref}));
  return {status:scheduleVerified?"CONFIGURATION_OBSERVED":"CONFIGURATION_UNVERIFIED",expected_slots:null,
   scheduled_pipelines:scheduled,unscheduled_pipelines:pipelines.filter(x=>x.source!=="schedule").map(x=>({id:x.id,source:x.source})),
   slot_attribution:scheduled.length?"SLOT_ATTRIBUTION_UNRESOLVED":"NO_SCHEDULED_PIPELINES_VISIBLE_AS_OF_QUERY",
   note:"No eligible denominator without individually verified activation times and slot definitions"};
}
