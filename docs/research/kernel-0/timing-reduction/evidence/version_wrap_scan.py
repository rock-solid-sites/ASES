#!/usr/bin/env python3
import argparse,itertools,json,resource,time
STATES=((0,0),(1,0),(1,1))
def cases():
 for mode in ('unbounded','mod4'):
  for read in ((0,1),(1,0)):
   chain=('c1','c2','begin',f'r{read[0]}',f'r{read[1]}','end')
   for o in itertools.permutations(chain):
    if all(o.index(chain[a])<o.index(chain[b]) for a,b in ((0,1),(2,3),(3,4),(4,5))): yield mode,read,o

def run(mode,read,o):
 step=0; ver=0; captured=[None,None]; v0=None; v1=None; trace=[{'event':'start','state':STATES[0],'version':0}]
 for e in o:
  if e[0]=='c':
   step+=1; ver=ver+2 if mode=='unbounded' else (ver+2)%4
  elif e=='begin': v0=ver
  elif e=='end': v1=ver
  else: captured[int(e[1])]=STATES[step][int(e[1])]
  trace.append({'event':e,'state':STATES[step],'version':ver,'observed':captured.copy()})
 first=o.index(f'r{read[0]}'); last=o.index(f'r{read[1]}')
 cuts=[{'after_events':k,'state':STATES[sum(o.index(c)<k for c in ('c1','c2'))]} for k in range(first,last+2)]
 return {'mode':mode,'read_order':read,'schedule':o,'versions':[v0,v1],'observed':captured,'accepted':v0==v1 and v0%2==0,'coherent':any(tuple(captured)==c['state'] for c in cuts),'eligible_cuts':cuts,'trace':trace}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--schedule-cap',type=int,default=60); ap.add_argument('--state-cap',type=int,default=420); a=ap.parse_args()
 if not 1<=a.schedule_cap<=60 or not 1<=a.state_cap<=420: ap.error('bounds')
 t=time.monotonic(); rows=[]; states=0
 for i,(mode,read,o) in enumerate(cases()):
  if len(rows)>=a.schedule_cap or states+7>a.state_cap:
   print(json.dumps({'status':'incomplete','completed':len(rows),'cuts':states,'reason':'schedule_cap' if len(rows)>=a.schedule_cap else 'state_cap','next':{'index':i,'mode':mode,'read':read,'schedule':o}},sort_keys=True)); return 2
  rows.append(run(mode,read,o)); states+=7
 assert len(rows)==60
 counts={}
 for r in rows:
  k=f"{r['mode']}/{'accepted' if r['accepted'] else 'rejected'}/{'coherent' if r['coherent'] else 'incoherent'}"; counts[k]=counts.get(k,0)+1
 assert all(r['coherent'] for r in rows if r['accepted'] and r['mode']=='unbounded')
 assert any(not r['coherent'] for r in rows if r['accepted'] and r['mode']=='mod4')
 print(json.dumps({'status':'complete_bounded','schedules':len(rows),'cuts':states,'steps':len(rows)*6,'counts':counts,'results':rows,'elapsed_seconds':time.monotonic()-t,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
