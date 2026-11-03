#!/usr/bin/env python3
"""Three constructive legal pairs exposing outcome-insufficient observations."""
import argparse,hashlib,json,resource,sys,time
from dataclasses import asdict
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];K=HERE.parent;sys.path.insert(0,str(HERE));import timing_event_model as t
m=t.model;Q=m.Request
MASK=frozenset({'rights','parents','data'})
def path(p,requests):
 state=m.State();steps=[]
 for q in requests:
  assert q in t.CATALOG;before=state;state,result=m.resolve(state,q,p);assert result=='commit';m.check_edge(before,q,state,result,p);steps.append({'request':asdict(q),'after':asdict(state),'outcome':result})
 return state,steps
def fixture(p,name):
 e=Q('establish');g=Q('grant',target=0,value=7)
 if name=='established':return ([],[e],Q('establish'))
 if name=='content':return ([e,g],[e,g,Q('accept',evidence=0,value=1)],Q('resume',evidence=0,value=0))
 return ([e],[e,Q('grant',target=0,value=1),Q('restrict',target=0,value=0)],Q('grant',target=0,value=1))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case-cap',type=int,default=9);a=ap.parse_args()
 if not 1<=a.case_cap<=9:ap.error('case cap 1..9')
 t0=time.monotonic();source=K/'kernel0_finite_model.py';before=hashlib.sha256(source.read_bytes()).hexdigest();rows=[]
 for p in t.PROFILES:
  for name in ('established','content','issued'):
   if len(rows)>=a.case_cap:
    print(json.dumps({'status':'incomplete','cases':len(rows),'states':len(rows)*2,'next':{'profile':p.name,'pair':name}},sort_keys=True));return 2
   l,r,q=fixture(p,name);s,ls=path(p,l);v,rs=path(p,r);assert q in t.CATALOG and m.invariant(s,p) and m.invariant(v,p)
   diffs=[f for f in t.FIELDS if getattr(s,f)!=getattr(v,f)]
   assert diffs==({'established':['established','content'],'content':['content'],'issued':['issued']}[name])
   assert t.project(s,MASK)==t.project(v,MASK) and t.project(s,MASK|{name})!=t.project(v,MASK|{name})
   out1,k1=m.resolve(s,q,p);out2,k2=m.resolve(v,q,p);assert (k1,k2)==('commit','deny')
   rows.append({'profile':p.name,'pair':name,'differing_fields':diffs,'histories':[ls,rs],'inputs':[asdict(s),asdict(v)],'request':asdict(q),'baseline_view':t.project(s,MASK),'augmented_views':[t.project(s,MASK|{name}),t.project(v,MASK|{name})],'outcomes':[k1,k2],'successors':[asdict(out1),asdict(out2)],'projected_successors':[t.project(out1,MASK),t.project(out2,MASK)]})
 after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after
 print(json.dumps({'status':'complete_bounded','cases':len(rows),'input_states':len(rows)*2,'oracle_resolutions_under_test':len(rows)*2,'baseline_mask':sorted(MASK),'results':rows,'source_sha256':before,'elapsed_seconds':time.monotonic()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
