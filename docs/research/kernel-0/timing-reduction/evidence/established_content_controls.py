#!/usr/bin/env python3
"""Controls for a dependency derived directly from the legal-state invariant."""
import argparse,hashlib,json,resource,sys,time
from dataclasses import asdict,replace
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];K=HERE.parent;sys.path.insert(0,str(HERE));import timing_event_model as t
m=t.model
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--state-cap',type=int,default=15);a=ap.parse_args()
 if not 1<=a.state_cap<=15:ap.error('state cap 1..15')
 t0=time.monotonic();src=K/'kernel0_finite_model.py';before=hashlib.sha256(src.read_bytes()).hexdigest();rows=[]
 for p in t.PROFILES:
  fixtures=[('empty',m.State(),True),('established_content0',m.State(True,content=0),True),('established_content1',m.State(True,content=1),True),('absent_content0',replace(m.State(),content=0),False),('established_absent_content',m.State(True,content=-1),False)]
  for name,s,want in fixtures:
   if len(rows)>=a.state_cap:
    print(json.dumps({'status':'incomplete','checks':len(rows),'next':{'profile':p.name,'fixture':name}},sort_keys=True));return 2
   actual=m.invariant(s,p);inferred=s.content!=-1;assert actual==want and (not actual or s.established==inferred)
   rows.append({'profile':p.name,'fixture':name,'state':asdict(s),'legal':actual,'reconstructed_established':inferred})
 after=hashlib.sha256(src.read_bytes()).hexdigest();assert before==after
 print(json.dumps({'status':'complete_bounded','checks':len(rows),'legal':sum(r['legal'] for r in rows),'illegal':sum(not r['legal'] for r in rows),'results':rows,'source_sha256':before,'elapsed_seconds':time.monotonic()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
