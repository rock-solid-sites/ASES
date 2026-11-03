#!/usr/bin/env python3
"""Enumerate validated reads with three bounded publication abstractions."""
import argparse,itertools,json,resource,time
PRE=(0,1); POST=(1,0)
def cases():
 for mode in ('whole','late','bracketed'):
  for pub in ((0,1),(1,0)):
   for read in ((0,1),(1,0)):
    chain=(f'p{pub[0]}',f'p{pub[1]}','begin',f'r{read[0]}',f'r{read[1]}','end')
    for o in itertools.permutations(chain):
     if all(o.index(chain[a])<o.index(chain[b]) for a,b in ((0,1),(2,3),(3,4),(4,5))): yield mode,pub,read,o

def run(mode,pub,read,o):
 visible=list(PRE); ver=0; seen=[None,None]; start=None; end=None; trace=[{'event':'start','visible':visible.copy(),'version':ver}]
 for e in o:
  if e=='begin': start=ver
  elif e=='end': end=ver
  elif e[0]=='r': seen[int(e[1])]=visible[int(e[1])]
  else:
   i=int(e[1]); first=i==pub[0]
   if mode=='whole':
    if not first: visible[:]=POST; ver+=2
   elif mode=='late':
    visible[i]=POST[i]
    if not first: ver+=2
   else:
    ver+=1; visible[i]=POST[i]
  trace.append({'event':e,'visible':visible.copy(),'version':ver,'observed':seen.copy()})
 first=o.index(f'r{read[0]}'); last=o.index(f'r{read[1]}'); commit=o.index(f'p{pub[1]}')
 cuts=[{'after_events':k,'state':list(POST if commit<k else PRE)} for k in range(first,last+2)]
 coherent=any(c['state']==seen for c in cuts); accepted=start==end and start%2==0
 return {'mode':mode,'publication_order':pub,'read_order':read,'schedule':o,'versions':[start,end],'observed':seen,'accepted':accepted,'coherent':coherent,'eligible_cuts':cuts,'trace':trace}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--schedule-cap',type=int,default=180); ap.add_argument('--state-cap',type=int,default=1260); a=ap.parse_args()
 if not 1<=a.schedule_cap<=180 or not 1<=a.state_cap<=1260: ap.error('bounds')
 t=time.monotonic(); rows=[]; states=0
 for i,(mode,pub,read,o) in enumerate(cases()):
  if len(rows)>=a.schedule_cap or states+7>a.state_cap:
   print(json.dumps({'status':'incomplete','completed':len(rows),'cuts':states,'reason':'schedule_cap' if len(rows)>=a.schedule_cap else 'state_cap','next':{'index':i,'mode':mode,'pub':pub,'read':read,'schedule':o}},sort_keys=True)); return 2
  rows.append(run(mode,pub,read,o)); states+=7
 assert len(rows)==180
 counts={}
 for r in rows:
  k=f"{r['mode']}/{'accepted' if r['accepted'] else 'rejected'}/{'coherent' if r['coherent'] else 'incoherent'}"; counts[k]=counts.get(k,0)+1
 assert all(r['coherent'] for r in rows if r['accepted'] and r['mode'] in ('whole','bracketed'))
 assert any(r['accepted'] and not r['coherent'] for r in rows if r['mode']=='late')
 print(json.dumps({'status':'complete_bounded','schedules':len(rows),'cuts':states,'steps':len(rows)*6,'counts':counts,'results':rows,'elapsed_seconds':time.monotonic()-t,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
