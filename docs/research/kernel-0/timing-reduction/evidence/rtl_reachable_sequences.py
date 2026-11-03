#!/usr/bin/env python3
import hashlib,json,resource,subprocess,sys,time
from dataclasses import asdict,replace
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]; K=HERE.parent; D=K/'direct-rtl';sys.path.insert(0,str(HERE));import timing_event_model as t
sys.path.insert(0,str(D));import correspondence as c
m=t.model; TOOL=Path('/tmp/ases-kernel-rtl-tool/root/usr');WORK=Path('/tmp/ases-kernel-sequence-rtl');WORK.mkdir(exist_ok=True)
sources=[D/'kernel0.v',D/'sequence_tb.v',D/'correspondence.py',K/'kernel0_finite_model.py']
def hashes():return {str(x.relative_to(K)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}
def limit():resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
def run(argv):
 try:
  p=subprocess.run(list(map(str,argv)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=10,preexec_fn=limit);return {'argv':list(map(str,argv)),'exit':p.returncode,'output':p.stdout}
 except subprocess.TimeoutExpired as e:return {'argv':list(map(str,argv)),'exit':'timeout','output':str(e.stdout)}
def main():
 start=time.monotonic(); before=hashes(); outputs={}; Q=m.Request; total=0
 for p in t.PROFILES[:2]:
  root=m.established((0,7),p=p); independent,_=m.resolve(root,Q('grant',target=3,value=1),p); dependent,_=m.resolve(root,Q('delegate',evidence=0,target=3,value=1),p)
  traces=[('independent_parent',[Q('establish'),Q('grant',target=0,value=7),Q('grant',target=3,value=1),Q('restrict',target=0,value=0)],independent),('dependent_parent',[Q('establish'),Q('grant',target=0,value=7),Q('delegate',evidence=0,target=3,value=1),Q('restrict',target=0,value=0)],dependent)]
  if p.coupled:traces.append(('coupled_data',[Q('establish'),Q('grant',target=0,value=7),Q('grant',target=3,value=1),Q('set',evidence=0,target=1,value=1),Q('set',evidence=0,target=0,value=1)],replace(independent,data=(0,1))))
  lines=[]; recorded=[]
  for name,qs,target in traces:
   state=m.State();lines.append('1 1 7fff 000000 0 0'); steps=[]
   for i,q in enumerate(qs):
    lines.append(f'0 0 7fff {c.encode_state(state):06x} 0 0')
    if i==len(qs)-1:assert state==target
    prev=state;state,kind=m.resolve(state,q,p);m.check_edge(prev,q,state,kind,p)
    lines.append(f'0 1 {c.encode_request(q):04x} {c.encode_state(state):06x} 1 {int(kind=="commit")}')
    steps.append({'request':asdict(q),'before':asdict(prev),'after':asdict(state),'outcome':kind})
   if name=='coupled_data':assert steps[-1]['outcome']=='deny'
   recorded.append({'name':name,'steps':steps})
  total+=len(lines); assert total<=60
  positive=WORK/(p.name+'.vectors');positive.write_text('\n'.join(lines)+'\n');negative=WORK/(p.name+'-bad.vectors');parts=lines[0].split();parts[3]='000002';negative.write_text(' '.join(parts)+'\n')
  binary=WORK/(p.name+'.vvp'); ivl=TOOL/'lib/x86_64-linux-gnu/ivl'; compile=run([TOOL/'bin/iverilog','-B',ivl,'-g2012','-s','sequence_tb','-P',f'sequence_tb.COUPLED={int(p.coupled)}','-o',binary,D/'kernel0.v',D/'sequence_tb.v'])
  if compile['exit']!=0:raise RuntimeError(json.dumps(compile))
  good=run([TOOL/'bin/vvp',binary,f'+vectors={positive}']);bad=run([TOOL/'bin/vvp',binary,f'+vectors={negative}'])
  assert good['exit']==0 and f'PASS sequential cycles={len(lines)}' in good['output']
  assert bad['exit']!=0 and 'sequence=0' in bad['output']
  outputs[p.name]={'traces':recorded,'positive_text':positive.read_text(),'negative_text':negative.read_text(),'compile':compile,'positive':good,'negative':bad,'cycles':len(lines)}
 after=hashes();assert before==after
 print(json.dumps({'status':'complete_bounded','profiles':outputs,'cycles':total,'source_sha256_before':before,'source_sha256_after':after,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True))
if __name__=='__main__':main()
