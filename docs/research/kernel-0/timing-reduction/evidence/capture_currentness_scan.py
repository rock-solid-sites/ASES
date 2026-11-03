#!/usr/bin/env python3
import argparse,itertools,json,resource,sys,time
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m=t.model;p=t.PROFILES[0]; initial=m.established((0,7),p=p)
q={'write':m.Request('set',evidence=0,target=0,value=1),'revoke':m.Request('restrict',target=0,value=0)}
assert all(v in t.CATALOG for v in q.values())
def cases():
 for mode in ('current','stale'):
  for o in itertools.permutations(('begin','capture','end','revoke','monitor')):
   if o.index('begin')<o.index('capture')<o.index('end') and o.index('revoke')<o.index('monitor'): yield mode,o+('resolve',)
def run(mode,o):
 state=initial; version=0; v0=v1=None; snapshot=None; monitored=None; outs={}; trace=[{'event':'start','state':asdict(state),'version':version}]
 for e in o:
  if e=='begin': v0=version
  elif e=='capture': snapshot=state
  elif e=='end': v1=version
  elif e=='revoke': state,outs['revoke']=m.resolve(state,q['revoke'],p); version+=1
  elif e=='monitor': monitored=state
  elif v0==v1:
   if mode=='current': state,outs['write']=m.resolve(state,q['write'],p)
   else:
    proposed,kind=m.resolve(snapshot,q['write'],p); outs['write']=kind
    if kind=='commit': state=m.merge_effect(state,snapshot,proposed)
  trace.append({'event':e,'state':asdict(state),'version':version,'outcomes':outs.copy()})
 accepted=v0==v1; serial=[]
 ops=('revoke','monitor','write') if accepted else ('revoke','monitor')
 for order in itertools.permutations(ops):
  if order.index('revoke')>order.index('monitor'): continue
  s=initial; so={}; view=None
  for op in order:
   if op=='monitor': view=s
   else: s,so[op]=m.resolve(s,q[op],p)
  serial.append({'order':order,'final':asdict(s),'outcomes':so,'monitor':asdict(view),'matches':s==state and so==outs and view==monitored})
 return {'mode':mode,'schedule':o,'versions':[v0,v1],'accepted':accepted,'snapshot':asdict(snapshot),'monitor':asdict(monitored),'outcomes':outs,'final':asdict(state),'candidates':serial,'trace':trace}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--case-cap',type=int,default=20); ap.add_argument('--state-cap',type=int,default=140); a=ap.parse_args()
 if not 1<=a.case_cap<=20 or not 1<=a.state_cap<=140: ap.error('bounds')
 t0=time.monotonic(); rows=[]; states=0
 for i,(mode,o) in enumerate(cases()):
  if len(rows)>=a.case_cap or states+7>a.state_cap:
   print(json.dumps({'status':'incomplete','cases':len(rows),'cuts':states,'reason':'case_cap' if len(rows)>=a.case_cap else 'state_cap','next':{'index':i,'mode':mode,'schedule':o}},sort_keys=True)); return 2
  rows.append(run(mode,o)); states+=7
 assert len(rows)==20
 counts={}
 for r in rows:
  before=r['schedule'].index('end')<r['schedule'].index('revoke'); witness=any(c['matches'] for c in r['candidates'])
  k=f"{r['mode']}/{'accepted' if r['accepted'] else 'withheld'}/{'capture_before_revoke' if before else 'other'}/{'witness' if witness else 'no_witness'}";counts[k]=counts.get(k,0)+1
  assert witness == (r['mode']=='current' or not before)
 print(json.dumps({'status':'complete_bounded','cases':len(rows),'cuts':states,'steps':len(rows)*6,'serial_candidates':sum(len(r['candidates']) for r in rows),'counts':counts,'results':rows,'elapsed_seconds':time.monotonic()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
