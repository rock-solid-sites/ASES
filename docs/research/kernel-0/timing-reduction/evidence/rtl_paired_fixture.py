#!/usr/bin/env python3
"""Fixed six-vector comparison of frozen RTL with frozen oracle."""
import hashlib,json,resource,subprocess,sys,time
from dataclasses import replace,asdict
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]; K=HERE.parent; D=K/'direct-rtl'
sys.path.insert(0,str(HERE)); import timing_event_model as t
sys.path.insert(0,str(D)); import correspondence as c
m=t.model; TOOL=Path('/tmp/ases-kernel-rtl-tool/root/usr'); WORK=Path('/tmp/ases-kernel-paired-rtl'); WORK.mkdir(exist_ok=True)
sources=[D/'kernel0.v',D/'exhaustive_tb.v',D/'correspondence.py',K/'kernel0_finite_model.py']
def hashes(): return {str(p.relative_to(K)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
def limit(): resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
def command(argv):
 try:
  p=subprocess.run(list(map(str,argv)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=10,preexec_fn=limit)
  return {'argv':list(map(str,argv)),'exit':p.returncode,'output':p.stdout}
 except subprocess.TimeoutExpired as e: return {'argv':list(map(str,argv)),'exit':'timeout','output':str(e.stdout)}
def main():
 started=time.monotonic(); before=hashes(); vectors={}; cases={}
 for p in t.PROFILES[:2]:
  root=m.established((0,7),p=p); independent,a=m.resolve(root,m.Request('grant',target=3,value=1),p); dependent,b=m.resolve(root,m.Request('delegate',evidence=0,target=3,value=1),p)
  assert (a,b)==('commit','commit') and all(m.invariant(s,p) for s in (independent,dependent))
  assert t.project(independent,{'rights'})==t.project(dependent,{'rights'}) and independent.parents!=dependent.parents
  pairs=[('independent_parent',independent,m.Request('restrict',target=0,value=0)),('dependent_parent',dependent,m.Request('restrict',target=0,value=0))]
  if p.coupled:
   variant=replace(independent,data=(0,1)); assert m.invariant(variant,p)
   assert t.project(independent,{'rights','parents'})==t.project(variant,{'rights','parents'})
   pairs += [('data_zero',independent,m.Request('set',evidence=0,target=0,value=1)),('data_one',variant,m.Request('set',evidence=0,target=0,value=1))]
  rows=[]
  for name,s,q in pairs:
   assert q in t.CATALOG; out,kind=m.resolve(s,q,p)
   rows.append({'name':name,'state':asdict(s),'request':asdict(q),'successor':asdict(out),'outcome':kind,'word':f'{c.encode_state(s):06x} {c.encode_request(q):04x} {c.encode_state(out):06x} {int(kind=="commit")}'} )
  if p.coupled: assert [x['outcome'] for x in rows[-2:]]==['commit','deny']
  cases[p.name]=rows
  positive=WORK/(p.name+'.vectors'); positive.write_text(''.join(x['word']+'\n' for x in rows))
  parts=rows[0]['word'].split(); parts[2]=f'{int(parts[2],16)^2:06x}'
  negative=WORK/(p.name+'-bad.vectors'); negative.write_text(' '.join(parts)+'\n')
  binary=WORK/(p.name+'.vvp'); compiler=TOOL/'bin/iverilog'; vvp=TOOL/'bin/vvp'; ivl=TOOL/'lib/x86_64-linux-gnu/ivl'
  comp=command([compiler,'-B',ivl,'-g2012','-s','exhaustive_tb','-P',f'exhaustive_tb.COUPLED={int(p.coupled)}','-o',binary,D/'kernel0.v',D/'exhaustive_tb.v'])
  if comp['exit']!=0: raise RuntimeError(json.dumps({'phase':'compile','result':comp}))
  good=command([vvp,binary,f'+vectors={positive}']); bad=command([vvp,binary,f'+vectors={negative}'])
  assert good['exit']==0 and f'PASS exhaustive vectors={len(rows)}' in good['output']
  assert bad['exit']!=0 and 'case=0' in bad['output'] and 'actual=' in bad['output']
  vectors[p.name]={'positive_text':positive.read_text(),'negative_text':negative.read_text(),'compile':comp,'positive':good,'negative':bad}
 after=hashes(); assert before==after
 print(json.dumps({'status':'complete_bounded','cases':cases,'runs':vectors,'source_sha256_before':before,'source_sha256_after':after,'tool_package_sha256':hashlib.sha256(Path('/tmp/ases-kernel-rtl-tool/iverilog.deb').read_bytes()).hexdigest(),'tool_version':command([TOOL/'bin/iverilog','-B',TOOL/'lib/x86_64-linux-gnu/ivl','-V']),'elapsed_seconds':time.monotonic()-started,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
