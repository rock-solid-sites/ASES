import {evaluateAdmission} from "./admission-v1.mjs";
export function runTests(evaluate) {
  const rev = "a".repeat(64), stale = "b".repeat(64);
  const limits={runs:1,wall_seconds:120,model_requests:0,completion_tokens:0,cash_microusd:0};
  function fixture(){
    return [{experiment_id:"EX-TEST",decision_id:"D-1",parent:"ASES-TEST",
      objective:"Choose whether to retain a local technique",kind:"DECISION",
      prior_search:"Inspected prior report; missing comparative evidence",
      evidence:["git:verified-fixture"],uncertainty:"Does comparison improve support?",
      least_method:"One deterministic paired query",scope:"Read-only public fixture",
      outcomes:{positive:"Retain",negative:"Discard",inconclusive:"Stop with unknown"},
      limits:{...limits},stop:"One run or 120 seconds",evidence_home:"git:results"},
      {verified_revision:rev,active_revision:rev,experiment_id:"EX-TEST",decision_id:"D-1",
       parent:"ASES-TEST",state:"OPEN",stop_reached:false,
       qualification:{revision:rev,status:"READY",receipt:"qualification-receipt"},
       review_policy:{revision:rev,required:true,reason:"Material decision",receipt:"policy-receipt"},
       review:{revision:rev,status:"COMPLETE",receipt:"raw-review-receipt",independent:true,
         verdict:"ACCEPT",action:"ADMIT",meaning_checked:true},
       authority:{revision:rev,experiment_id:"EX-TEST",decision_id:"D-1",
         status:"AUTHORIZED",mode:"NORMAL",receipt:"operator-event"},
       dispatch:{id:"dispatch-1",revision:rev,claim_state:"UNCLAIMED",
         ledger_receipt:"ledger-snapshot",request:{...limits},remaining:{...limits}}}];
  }
  const cases=[
    ["accepted bounded plan",()=>{},"ELIGIBLE_FOR_ATOMIC_CLAIM"],
    ["routine no fresh review", (p,c)=>{c.review=null;c.review_policy.required=false;},"ELIGIBLE_FOR_ATOMIC_CLAIM"],
    ["missing outcome",p=>delete p.outcomes.inconclusive,"INVALID_REGISTRATION"],
    ["no decision difference",p=>p.outcomes.negative=p.outcomes.positive,"INVALID_REGISTRATION"],
    ["unknown model cap",p=>p.limits.model_requests=1,"INVALID_REGISTRATION"],
    ["wrong parent",(p,c)=>c.parent="OTHER","IDENTITY_OR_REVISION_MISMATCH"],
    ["stale plan",(p,c)=>c.active_revision=stale,"IDENTITY_OR_REVISION_MISMATCH"],
    ["closed decision",(p,c)=>c.state="RESOLVED","DECISION_OR_EXPERIMENT_NOT_OPEN"],
    ["stop reached",(p,c)=>c.stop_reached=true,"STOP_REACHED_OR_UNKNOWN"],
    ["stop unknown",(p,c)=>delete c.stop_reached,"STOP_REACHED_OR_UNKNOWN"],
    ["reuse prior evidence",(p,c)=>c.qualification.status="REUSE","QUALIFICATION_REUSE"],
    ["source block cannot be waived",(p,c)=>{c.qualification.status="BLOCKED";c.authority.mode="MANUAL_REVIEW_EXCEPTION";c.authority.reason="Override review only";},"QUALIFICATION_BLOCKED"],
    ["stale qualification",(p,c)=>c.qualification.revision=stale,"QUALIFICATION_MISSING_OR_STALE"],
    ["unclassified review policy",(p,c)=>delete c.review_policy.required,"REVIEW_POLICY_UNKNOWN"],
    ["review absent",(p,c)=>c.review=null,"REVIEW_MISSING"],
    ["reasoning only failure",(p,c)=>c.review.status="INCOMPLETE","REVIEW_INCOMPLETE"],
    ["same family unverified",(p,c)=>c.review.independent=false,"REVIEW_INDEPENDENCE_UNVERIFIED"],
    ["OP01 label action mismatch",(p,c)=>{c.review.verdict="IMPLEMENT";c.review.action="ADMIT";},"REVIEW_ACTION_CONFLICT_OR_UNCHECKED"],
    ["prose meaning unchecked",(p,c)=>c.review.meaning_checked=false,"REVIEW_ACTION_CONFLICT_OR_UNCHECKED"],
    ["reduce blocks current revision",(p,c)=>{c.review.verdict="REDUCE";c.review.action="REVISE";},"REVIEW_REDUCE"],
    ["reuse verdict",(p,c)=>{c.review.verdict="REUSE";c.review.action="USE_EVIDENCE";},"REVIEW_REUSE"],
    ["implement verdict",(p,c)=>{c.review.verdict="IMPLEMENT";c.review.action="TRANSFER";},"REVIEW_IMPLEMENT"],
    ["defer verdict",(p,c)=>{c.review.verdict="DEFER";c.review.action="DEFER";},"REVIEW_DEFER"],
    ["reject verdict",(p,c)=>{c.review.verdict="REJECT";c.review.action="CLOSE";},"REVIEW_REJECT"],
    ["stale review",(p,c)=>c.review.revision=stale,"REVIEW_RECORD_INVALID_OR_STALE"],
    ["manual OP01 adjudication",(p,c)=>{c.review.verdict="IMPLEMENT";c.review.action="ADMIT";c.authority.mode="MANUAL_REVIEW_EXCEPTION";c.authority.reason="Explicit operator decision after adjudication";},"ELIGIBLE_FOR_ATOMIC_CLAIM"],
    ["exception without reason",(p,c)=>c.authority.mode="MANUAL_REVIEW_EXCEPTION","AUTHORITY_MISSING_OR_STALE"],
    ["accept not authority",(p,c)=>c.authority.status="PENDING","AUTHORITY_MISSING_OR_STALE"],
    ["stale authorization",(p,c)=>c.authority.revision=stale,"AUTHORITY_MISSING_OR_STALE"],
    ["duplicate claim",(p,c)=>c.dispatch.claim_state="CLAIMED","DISPATCH_ALREADY_CLAIMED_OR_UNVERIFIED"],
    ["stale dispatch",(p,c)=>c.dispatch.revision=stale,"DISPATCH_ALREADY_CLAIMED_OR_UNVERIFIED"],
    ["exhausted aggregate runs",(p,c)=>c.dispatch.remaining.runs=0,"ENVELOPE_EXCEEDED_OR_UNKNOWN"],
    ["cash expansion",(p,c)=>c.dispatch.request.cash_microusd=1,"ENVELOPE_EXCEEDED_OR_UNKNOWN"],
    ["remaining cannot exceed plan",(p,c)=>c.dispatch.remaining.runs=2,"ENVELOPE_EXCEEDED_OR_UNKNOWN"],
    ["boolean not a numeric cap",(p,c)=>c.dispatch.request.runs=true,"ENVELOPE_EXCEEDED_OR_UNKNOWN"],
    ["manual cannot exceed budget",(p,c)=>{c.authority.mode="MANUAL_REVIEW_EXCEPTION";c.authority.reason="Explicit";c.dispatch.request.wall_seconds=121;},"ENVELOPE_EXCEEDED_OR_UNKNOWN"],
  ];
  const results=cases.map(([name,mutate,expected])=>{
    const [p,c]=fixture();mutate(p,c);
    const before=JSON.stringify([p,c]);const got=evaluate(p,c);
    const actual=got.status==="BLOCK"?got.reason:got.status;
    const unchanged=before===JSON.stringify([p,c]);
    return {name,expected,actual,pass:actual===expected&&unchanged};
  });
  return {count:results.length,passed:results.filter(x=>x.pass).length,results};
}
const report = runTests(evaluateAdmission);
console.log(JSON.stringify(report,null,2));
if (report.passed !== report.count) process.exitCode = 1;
