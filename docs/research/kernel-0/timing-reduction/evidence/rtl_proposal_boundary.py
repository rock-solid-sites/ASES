#!/usr/bin/env python3
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];K=HERE.parent;D=K/'direct-rtl';sys.path.insert(0,str(HERE));import timing_event_model as t
sys.path.insert(0,str(D));import correspondence as c
m=t.model;Q=m.Request;p=t.PROFILES[0];E=Path(__file__).resolve().parent;TOOL=Path('/tmp/ases-kernel-rtl-tool/root/usr');WORK=Path('/tmp/ases-kernel-proposal-rtl');WORK.mkdir(exist_ok=True)
sources=[D/'kernel0.v',D/'correspondence.py',K/'kernel0_finite_model.py',E/'rtl_proposal_boundary_tb.v']
def hashes():return {str(x.relative_to(K)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}
def limit():resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
def run(args):
 try:
  x=subprocess.run(list(map(str,args)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=10,preexec_fn=limit);return {'argv':list(map(str,args)),'exit':x.returncode,'output':x.stdout}
 except subprocess.TimeoutExpired as e:return {'argv':list(map(str,args)),'exit':'timeout','output':str(e.stdout)}
def main():
 start=time.monotonic();before=hashes();e=Q('establish');g=Q('grant',target=0,value=7);a=Q('set',evidence=0,target=0,value=1);b=Q('set',evidence=0,target=1,value=0);h=Q('set',evidence=0,target=1,value=1)
 assert all(q in t.CATALOG for q in (e,g,a,b,h));s=m.State()
 for q in (e,g):s,k=m.resolve(s,q,p);assert k=='commit'
 outs=[]
 for q in (a,b,h):
  z,k=m.resolve(s,q,p);assert k=='commit';outs.append(z)
 assert len(set(outs))==3
 words=[*(c.encode_request(q) for q in (e,g,a,b,h)),c.encode_state(s),*(c.encode_state(z) for z in outs)]
 assert words[4] == ((words[2]&~(3<<7)) | (words[3]&(3<<7)))
 text=' '.join(f'{x:x}' for x in words)+'\n';vec=WORK/'vectors';vec.write_text(text);binary=WORK/'run.vvp';ivl=TOOL/'lib/x86_64-linux-gnu/ivl'
 comp=run([TOOL/'bin/iverilog','-B',ivl,'-g2012','-s','proposal_boundary_tb','-o',binary,D/'kernel0.v',E/'rtl_proposal_boundary_tb.v']);assert comp['exit']==0,comp
 good=run([TOOL/'bin/vvp',binary,f'+vectors={vec}']);bad=run([TOOL/'bin/vvp',binary,f'+vectors={vec}','+bad']);assert good['exit']==0 and 'PASS four' in good['output'];assert bad['exit']!=0 and 'case=2 state=' in bad['output']
 after=hashes();assert before==after
 print(json.dumps({'status':'complete_bounded','vector_text':text,'before_words':words,'compile':comp,'positive':good,'negative':bad,'source_sha256_before':before,'source_sha256_after':after,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True))
if __name__=='__main__':main()
