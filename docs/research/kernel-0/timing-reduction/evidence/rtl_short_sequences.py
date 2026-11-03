#!/usr/bin/env python3
"""Finite product of fixed oracle traces checked on the unmodified RTL."""
import argparse,collections,hashlib,itertools,json,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];K=HERE.parent;D=K/'direct-rtl';sys.path.insert(0,str(HERE));import timing_event_model as t
sys.path.insert(0,str(D));import correspondence as c
m=t.model;Q=m.Request;TOOL=Path('/tmp/ases-kernel-rtl-tool/root/usr');WORK=Path('/tmp/ases-kernel-short-rtl');WORK.mkdir(exist_ok=True)
SOURCES=[D/'kernel0.v',D/'sequence_tb.v',D/'correspondence.py',K/'kernel0_finite_model.py']
ACTIONS=[('grant3',Q('grant',target=3,value=1)),('delegate3',Q('delegate',evidence=0,target=3,value=1)),('restrict0',Q('restrict',target=0,value=0)),('restrict1',Q('restrict',target=0,value=1)),('setx',Q('set',evidence=0,target=0,value=1)),('sety',Q('set',evidence=0,target=1,value=1))]
def hashes():return {str(p.relative_to(K)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES}
def limit():resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
def run(args):
 try:
  p=subprocess.run(list(map(str,args)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=10,preexec_fn=limit);return {'argv':list(map(str,args)),'exit':p.returncode,'output':p.stdout}
 except subprocess.TimeoutExpired as e:return {'argv':list(map(str,args)),'exit':'timeout','output':str(e.stdout)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case-cap',type=int,default=432);a=ap.parse_args()
 if not 1<=a.case_cap<=432:ap.error('case cap must be 1..432')
 start=time.monotonic();before=hashes();per={};count=0
 assert all(q in t.CATALOG for _,q in ACTIONS)
 for p in t.PROFILES[:2]:
  lines=[]; manifest=[]; summary=collections.Counter()
  for order in itertools.product(range(6),repeat=3):
   if count>=a.case_cap:
    print(json.dumps({'status':'incomplete','reason':'case_cap','completed_cases':count,'next':{'profile':p.name,'action_indices':order,'actions':[ACTIONS[i][0] for i in order]},'simulation':'not_run'},sort_keys=True));return 2
   s=m.State();lines.append('1 1 7fff 000000 0 0'); sequence=[]
   for i,q in enumerate([Q('establish'),Q('grant',target=0,value=7)]+[ACTIONS[j][1] for j in order]):
    prior=s;s,kind=m.resolve(s,q,p);m.check_edge(prior,q,s,kind,p)
    if i>=2:
     label=ACTIONS[order[i-2]][0];summary[f'action/{label}/{kind}']+=1
     old='linked' if prior.parents[3]>=0 else 'none';new='linked' if s.parents[3]>=0 else 'none';summary[f'parent/{old}_to_{new}']+=1
    lines.append(f'0 1 {c.encode_request(q):04x} {c.encode_state(s):06x} 1 {int(kind=="commit")}');sequence.append(kind)
   manifest.append({'actions':[ACTIONS[j][0] for j in order],'outcomes':sequence,'first_cycle':len(lines)-6});count+=1
  per[p.name]={'vector_text':'\n'.join(lines)+'\n','manifest':manifest,'counts':dict(sorted(summary.items())),'cases':len(manifest),'cycles':len(lines)}
 assert count==432 and sum(x['cycles'] for x in per.values())==2592
 for p in t.PROFILES[:2]:
  d=per[p.name];positive=WORK/(p.name+'.vectors');positive.write_text(d['vector_text']);ls=d['vector_text'].splitlines();fields=ls[1].split();fields[3]=f'{int(fields[3],16)^2:06x}';ls[1]=' '.join(fields);negative=WORK/(p.name+'-bad.vectors');negative.write_text('\n'.join(ls)+'\n')
  binary=WORK/(p.name+'.vvp');ivl=TOOL/'lib/x86_64-linux-gnu/ivl'
  comp=run([TOOL/'bin/iverilog','-B',ivl,'-g2012','-s','sequence_tb','-P',f'sequence_tb.COUPLED={int(p.coupled)}','-o',binary,D/'kernel0.v',D/'sequence_tb.v'])
  if comp['exit']!=0:raise RuntimeError(json.dumps(comp))
  good=run([TOOL/'bin/vvp',binary,f'+vectors={positive}']);bad=run([TOOL/'bin/vvp',binary,f'+vectors={negative}']);d['compile']=comp;d['positive']=good;d['negative']=bad
  if good['exit']!=0 or f'PASS sequential cycles={d["cycles"]}' not in good['output']:raise RuntimeError(json.dumps({'profile':p.name,'positive':good,'manifest':d['manifest']}))
  assert bad['exit']!=0 and 'sequence=1' in bad['output']
 after=hashes();assert before==after
 print(json.dumps({'status':'complete_bounded','cases':count,'cycles':2592,'profiles':per,'source_sha256_before':before,'source_sha256_after':after,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
