function readState(content){
  const marker="\n## Related-work reconciliation (pilot)\n";
  const start=content.indexOf(marker);
  if(start<0)return {state:null,start:-1,end:-1};
  if(content.indexOf(marker,start+marker.length)>=0)throw Error("ambiguous reconciliation section");
  const tail=content.slice(start+marker.length);
  const match=tail.match(/```json\n([\s\S]*?)\n```/);
  if(!match)throw Error("missing reconciliation state");
  const end=start+marker.length+match.index+match[0].length;
  return {state:JSON.parse(match[1]),start,end};
}

async function project({readPage,compareAndSet,event,reduce,render,maxAttempts=3}){
  if(!Number.isInteger(maxAttempts)||maxAttempts<1||maxAttempts>5)throw Error("invalid retry bound");
  let lastError,attempts=0,writes=0;
  while(attempts++<maxAttempts){
    let old;
    try{old=await readPage()}catch(e){lastError=e;continue}
    const location=readState(old.content);
    const next=reduce(location.state,event);
    if(!next.changed)return {status:"verified_noop",attempts,writes,state:next.state,revision:old.revision};
    const marker="\n## Related-work reconciliation (pilot)\n";
    let content;
    if(location.state===null){
      const h=old.content.match(/^# [^\n]+\n/m);
      if(!h)throw Error("missing main heading");
      const top="\n\n**Revision-scoped related work:** [current pending sources and disposition](#related-work-reconciliation-pilot). Review before advancing the affected question; unrelated work can continue. [Pilot procedure](/wiki/projektor-ases-topic-register-pilot).\n";
      content=old.content.replace(h[0],h[0]+top)+"\n"+marker+"\n"+render(next.state);
    }else{
      content=old.content.slice(0,location.start)+marker+"\n"+render(next.state).trimEnd()+old.content.slice(location.end);
    }
    try{
      writes++;
      await compareAndSet({revision:old.revision,content});
      const current=await readPage();
      if(current.content===content)return {status:"verified_write",attempts,writes,state:next.state,revision:current.revision};
      lastError=Error("write readback differs; retry from fresh state");
    }catch(e){lastError=e}
  }
  throw Error("bounded reconciliation failed: "+String(lastError));
}

export {readState,project};
