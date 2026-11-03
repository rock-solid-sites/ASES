#!/usr/bin/env python3
import argparse,itertools,json,resource,sys,time
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m=t.model; p=t.PROFILES[0]; initial=m.established((0,7),p=p)
q={'write':m.Request('set',evidence=0,target=0,value=1),'revoke':m.Request('restrict',target=0,value=0)}
assert all(x in t.CATALOG for x in q.values())
def cases():
 chain=('revoke_invoke','revoke_commit','revoke_return','write_invoke','write_resolve','write_return')
 for mode in ('current','stale'):
  for slot in range(5): yield mode,slot,chain[:slot]+('cache',)+chain[slot:]
def run(mode,slot,o):
 state=initial; cache=None; outcomes={}; trace=[{'event':'start','state':asdict(state)}]
 for e in o:
  if e=='cache': cache=state
  elif e=='revoke_commit': state,outcomes['revoke']=m.resolve(state,q['revoke'],p)
  elif e=='write_resolve':
   if mode=='current': state,outcomes['write']=m.resolve(state,q['write'],p)
   else:
    candidate,result=m.resolve(cache,q['write'],p); outcomes['write']=result
    if result=='commit': state=m.merge_effect(state,cache,candidate)
  trace.append({'event':e,'state':asdict(state),'outcomes':outcomes.copy()})
 candidates=[]
 for order in itertools.permutations(('write','revoke')):
  s=initial; outs={}
  for op in order: s,outs[op]=m.resolve(s,q[op],p)
  candidates.append({'order':order,'final':asdict(s),'outcomes':outs,'final_match':s==state,'outcomes_match':outs==outcomes,'precedence':order.index('revoke')<order.index('write')})
 return {'mode':mode,'cache_slot':slot,'schedule':o,'cache_before_commit':o.index('cache')<o.index('revoke_commit'), 'final':asdict(state),'outcomes':outcomes,'candidates':candidates,'trace':trace}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--case-cap',type=int,default=10); ap.add_argument('--state-cap',type=int,default=80); a=ap.parse_args()
 if not 1<=a.case_cap<=10 or not 1<=a.state_cap<=80: ap.error('bounds')
 t0=time.monotonic(); rows=[]; states=0
 for i,(mode,slot,o) in enumerate(cases()):
  if len(rows)>=a.case_cap or states+8>a.state_cap:
   print(json.dumps({'status':'incomplete','cases':len(rows),'cuts':states,'reason':'case_cap' if len(rows)>=a.case_cap else 'state_cap','next':{'index':i,'mode':mode,'cache_slot':slot,'schedule':o}},sort_keys=True)); return 2
  rows.append(run(mode,slot,o)); states+=8
 counts={}
 for r in rows:
  cs=r['candidates']; f=any(c['final_match'] for c in cs); fo=any(c['final_match'] and c['outcomes_match'] for c in cs); p=any(c['final_match'] and c['outcomes_match'] and c['precedence'] for c in cs)
  key=f"{r['mode']}/{'pre' if r['cache_before_commit'] else 'post'}/final={f}/outcomes={fo}/precedence={p}"; counts[key]=counts.get(key,0)+1
  assert f and fo and p==(r['mode']=='current' or not r['cache_before_commit'])
 print(json.dumps({'status':'complete_bounded','cases':len(rows),'cuts':states,'steps':len(rows)*7,'serial_candidates':len(rows)*2,'counts':counts,'results':rows,'elapsed_seconds':time.monotonic()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
