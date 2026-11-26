import {reduce,mayAdvance,render} from './reconcile.mjs';

function tests(){
  let n=0;const check=(v,label)=>{if(!v)throw Error(label);n++};
  const ev=(revision,more={})=>({kind:"observe",route:"test",authorized:true,revision,source:"https://example.org/"+revision,relevant:true,note:"affects composition",...more});
  const bad=(fn,label)=>{let threw=false;try{fn()}catch{threw=true}check(threw,label)};
  const a=reduce(null,ev("v1")).state;check(!mayAdvance(a,true),"pending blocks affected");check(mayAdvance(a,false),"unaffected progresses");check(!reduce(a,ev("v1")).changed,"duplicate no-op");
  bad(()=>reduce(a,ev("v1",{kind:"resolve",disposition:"applied"})),"cannot resolve before consult");
  const b=reduce(a,ev("v2")).state;const c=reduce(b,ev("v1",{kind:"consult",note:"exact source read"})).state;
  const d=reduce(c,ev("v1",{kind:"resolve",disposition:"applied",note:"evidence incorporated"})).state;check(d.entries[0].status==="applied"&&d.entries[1].status==="pending"&&!mayAdvance(d,true),"old ack preserves new pending");
  check(!reduce(d,ev("v1")).changed,"replayed old event no-op");
  const e=reduce(d,ev("v3",{relevant:false,note:"outside reviewed impact scope"})).state;check(e.entries[2].status==="not_applicable"&&!mayAdvance(e,true),"irrelevant cannot clear pending");
  bad(()=>reduce(e,ev("v4",{authorized:false})),"denied no effect");check(e.entries.length===3,"denied state unchanged");
  bad(()=>reduce(e,ev("v2",{route:"other"})),"wrong route rejected");bad(()=>reduce(e,ev("unknown",{kind:"consult"})),"unknown revision rejected");
  const f=reduce(e,ev("v2",{kind:"consult",note:"source read"})).state;const g=reduce(f,ev("v2",{kind:"resolve",disposition:"unresolved",note:"conflicting evidence"})).state;check(!mayAdvance(g,true),"unresolved remains blocking");
  const h=reduce(g,ev("v2",{kind:"consult",note:"rechecked"})).state;const i=reduce(h,ev("v2",{kind:"resolve",disposition:"not_applicable",note:"scope excluded after review"})).state;check(mayAdvance(i,true),"terminal all reconciled");check(!reduce(i,ev("v2",{kind:"resolve",disposition:"not_applicable",note:"scope excluded after review"})).changed,"duplicate ack no-op");
  const retry=reduce(a,ev("v2")).state;check(JSON.stringify(retry)===JSON.stringify(b),"lost write/retry deterministic");check(JSON.stringify(a)===JSON.stringify(reduce(null,ev("v1")).state),"no input mutation");
  check(render(i).includes("0 unreconciled"),"derived flag status");return n;
}
console.log(`${tests()} assertions passed`);
