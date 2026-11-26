function reduce(state,event){
  const fail=(message)=>{throw new Error(message)};
  if(!event||event.authorized!==true)fail("access not established");
  if(typeof event.route!=="string"||!event.route.trim())fail("route required");
  const s=state===null?{route:event.route,entries:[]} : JSON.parse(JSON.stringify(state));
  if(s.route!==event.route||!Array.isArray(s.entries))fail("route mismatch");
  const key=event.revision;
  if(typeof key!=="string"||!key.trim())fail("revision required");
  const e=s.entries.find(x=>x.revision===key);
  const note=typeof event.note==="string"?event.note.trim():"";
  if(event.kind==="observe"){
    if(e)return {state:s,changed:false};
    if(typeof event.relevant!=="boolean"||!note||typeof event.source!=="string"||!event.source.startsWith("https://"))fail("reviewed scope and source required");
    s.entries.push({revision:key,source:event.source,impact:note,status:event.relevant?"pending":"not_applicable",receipt:event.relevant?null:note,disposition:event.relevant?null:note});
    return {state:s,changed:true};
  }
  if(!e)fail("unknown revision");
  if(event.kind==="consult"){
    if(e.status==="consulted"&&e.receipt===note)return {state:s,changed:false};
    if(!["pending","unresolved"].includes(e.status)||!note)fail("consultation receipt required");
    e.status="consulted";e.receipt=note;e.disposition=null;
  }else if(event.kind==="resolve"){
    if(!["applied","not_applicable","unresolved"].includes(event.disposition)||!note)fail("disposition and reason required");
    if(e.status===event.disposition&&e.disposition===note)return {state:s,changed:false};
    if(e.status!=="consulted")fail("consult exact revision first");
    e.status=event.disposition;e.disposition=note;
  }else fail("unknown event");
  return {state:s,changed:true};
}

function mayAdvance(state,affected){
  if(affected===false)return true;
  if(affected!==true||!state||!Array.isArray(state.entries))return false;
  return state.entries.every(e=>["applied","not_applicable"].includes(e.status));
}

function render(state){
  const pending=state.entries.filter(e=>!["applied","not_applicable"].includes(e.status));
  return `**RELATED WORK — ${pending.length} unreconciled source revision(s).** Before advancing the affected question, consult the exact source and record a disposition in this existing checkpoint using the pilot reducer. No change of scope is authorized.\n\n`+state.entries.map(e=>`- ${e.status.toUpperCase()} — [source](${e.source}): ${e.impact}${e.disposition?" — "+e.disposition:""}`).join("\n")+"\n\n```json\n"+JSON.stringify(state,null,2)+"\n```\n";
}

export {reduce,mayAdvance,render};
