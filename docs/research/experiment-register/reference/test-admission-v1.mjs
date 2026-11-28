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
  // COMPLETE reviews must not coerce JSON values into verdict property keys.
  const setAuthority=(c,mode)=>{
    c.authority.mode=mode;
    if(mode==="MANUAL_REVIEW_EXCEPTION") c.authority.reason="Explicit owner disposition";
  };
  const malformedVerdicts=[
    ["missing",undefined], ["null",null], ["number",1], ["boolean",true],
    ["object",{}], ["noncoercible object",{toString:null,valueOf:null}],
    ["array alias",["ACCEPT"]],
  ];
  for(const mode of ["NORMAL","MANUAL_REVIEW_EXCEPTION"]){
    for(const [label,value] of malformedVerdicts){
      cases.push([`malformed COMPLETE verdict ${label} ${mode}`,(p,c)=>{
        setAuthority(c,mode);
        if(value===undefined) delete c.review.verdict;
        else c.review.verdict=JSON.parse(JSON.stringify(value));
      },"REVIEW_RECORD_INVALID_OR_STALE"]);
    }
    cases.push([`malformed nonindependent COMPLETE verdict ${mode}`,(p,c)=>{
      setAuthority(c,mode);c.review.independent=false;c.review.verdict=["ACCEPT"];
    },"REVIEW_RECORD_INVALID_OR_STALE"]);
    cases.push([`malformed optional COMPLETE verdict ${mode}`,(p,c)=>{
      setAuthority(c,mode);c.review_policy.required=false;c.review.verdict=["ACCEPT"];
    },"REVIEW_RECORD_INVALID_OR_STALE"]);
    for(const status of ["INCOMPLETE","FAILED"]){
      const manual=mode==="MANUAL_REVIEW_EXCEPTION";
      cases.push([`${status} without verdict ${mode}`,(p,c)=>{
        setAuthority(c,mode);c.review.status=status;delete c.review.verdict;
      },manual?"ELIGIBLE_FOR_ATOMIC_CLAIM":"REVIEW_INCOMPLETE",
        manual?"MANUAL_EXCEPTION:REVIEW_INCOMPLETE":undefined]);
    }
    const manual=mode==="MANUAL_REVIEW_EXCEPTION";
    cases.push([`unknown string verdict ${mode}`,(p,c)=>{
      setAuthority(c,mode);c.review.verdict="UNKNOWN";
    },manual?"ELIGIBLE_FOR_ATOMIC_CLAIM":"REVIEW_ACTION_CONFLICT_OR_UNCHECKED",
      manual?"MANUAL_EXCEPTION:REVIEW_ACTION_CONFLICT_OR_UNCHECKED":undefined]);
  }
  // Pin all four resource-cap combinations independently at each rejection clause.
  for(const [requests,tokens] of [[0,0],[10,1000],[0,1000],[10,0]]){
    const coupled=(requests===0)===(tokens===0);
    cases.push([`plan cap pair ${requests}/${tokens}`,(p,c)=>{
      Object.assign(p.limits,{model_requests:requests,completion_tokens:tokens});
      c.dispatch.request={...p.limits};c.dispatch.remaining={...p.limits};
    },coupled?"ELIGIBLE_FOR_ATOMIC_CLAIM":"INVALID_REGISTRATION"]);
    cases.push([`dispatch cap pair ${requests}/${tokens}`,(p,c)=>{
      Object.assign(p.limits,{model_requests:10,completion_tokens:1000});
      c.dispatch.remaining={...p.limits};
      Object.assign(c.dispatch.request,{model_requests:requests,completion_tokens:tokens});
    },coupled?"ELIGIBLE_FOR_ATOMIC_CLAIM":"ENVELOPE_EXCEEDED_OR_UNKNOWN"]);
  }
  const results=cases.map(([name,mutate,expected,expectedDisposition])=>{
    const [p,c]=fixture();mutate(p,c);
    const before=JSON.stringify([p,c]);
    let got,actual,error;
    try {got=evaluate(p,c);actual=got.status==="BLOCK"?got.reason:got.status;}
    catch(e){actual="THREW";error=`${e.name}: ${e.message}`;}
    const unchanged=before===JSON.stringify([p,c]);
    return {name,expected,actual,error,expectedDisposition,actualDisposition:got?.review_disposition,
      pass:actual===expected&&unchanged&&(expectedDisposition===undefined||got?.review_disposition===expectedDisposition)};
  });
  return {count:results.length,passed:results.filter(x=>x.pass).length,results};
}
const report = runTests(evaluateAdmission);
console.log(JSON.stringify(report,null,2));
if (report.passed !== report.count) process.exitCode = 1;
