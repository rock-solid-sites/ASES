#!/usr/bin/env python3
import argparse,hashlib,json,resource,sys,time
from dataclasses import asdict
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];K=HERE.parent;sys.path.insert(0,str(HERE));import timing_event_model as t
m=t.model;Q=m.Request
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case-cap',type=int,default=9);a=ap.parse_args()
 if not 1<=a.case_cap<=9:ap.error('case cap 1..9')
 start=time.monotonic();src=K/'kernel0_finite_model.py';before=hashlib.sha256(src.read_bytes()).hexdigest();rows=[]
 linkedbase=m.established((0,7),p=t.PROFILES[0]);linked,kind=m.resolve(linkedbase,Q('delegate',evidence=0,target=3,value=1),t.PROFILES[0]);assert kind=='commit' and linked.parents[3]==0
 for p in t.PROFILES:
  for name in ('grant_while_active','delegate_while_active','revoke_then_grant'):
   if len(rows)>=a.case_cap:
    print(json.dumps({'status':'incomplete','cases':len(rows),'next':{'profile':p.name,'case':name}},sort_keys=True));return 2
   s=m.established((0,7),p=p);history=[]
   qs={'grant_while_active':[Q('grant',target=3,value=1)],'delegate_while_active':[Q('delegate',evidence=0,target=3,value=1)],'revoke_then_grant':[Q('restrict',target=0,value=0),Q('grant',target=3,value=1)]}[name]
   for q in qs:
    assert q in t.CATALOG;old=s;s,result=m.resolve(s,q,p);m.check_edge(old,q,s,result,p);history.append({'request':asdict(q),'outcome':result,'state':asdict(s)})
   expected='deny' if p.exclusive and name!='revoke_then_grant' else 'commit';assert result==expected
   if p.exclusive:assert s.parents==(-1,-1,-1,-1) and not m.invariant(linked,p)
   if name=='delegate_while_active' and not p.exclusive:assert s.parents[3]==0
   rows.append({'profile':p.name,'case':name,'history':history,'linked_candidate_legal':m.invariant(linked,p),'linked_candidate':asdict(linked)})
 after=hashlib.sha256(src.read_bytes()).hexdigest();assert before==after
 print(json.dumps({'status':'complete_bounded','cases':len(rows),'results':rows,'source_sha256':before,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
