#!/usr/bin/env python3
"""L1: one H=M mediator, one worker, process-death storage profile only."""
import base64, ctypes, hashlib, json, os, platform, signal, socket, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE/'lab'; SOURCE=ROOT/'source'/'candidate-x.bin'; STATE=ROOT/'protected'; OBJECTS=STATE/'objects'
X=b'F3-lifecycle-x-v1\n'; SYS_CREATE,SYS_ADD,SYS_RESTRICT=444,445,446; READ_FILE,READ_DIR=4,8; HANDLED_FS=8190
AUTH=r'''import base64,hashlib,json,os,socket,sys
root, wf, af=sys.argv[2],int(sys.argv[3]),int(sys.argv[4]); state=root+'/protected'; objects=state+'/objects'; source=root+'/source/candidate-x.bin'
w=socket.socket(fileno=wf); a=socket.socket(fileno=af); presented=None; gen=0

def readstate():
 name=open(state+'/CURRENT').read().strip(); return name,json.load(open(state+'/'+name))
def commit(d,blob=None):
 global gen
 gen+=1
 if blob is not None:
  h=hashlib.sha256(blob).hexdigest(); dst=objects+'/'+h+'.bin'; tmp=dst+'.tmp'; open(tmp,'xb').write(blob); os.replace(tmp,dst)
  d['work_units']['C']['accepted']={'identity':'C-content-'+h[:16],'sha256':h,'object':'objects/'+h+'.bin','size':len(blob),'provenance':{'actor':'worker-ingress-W1','source':'candidate-x.bin','presented_sha256':h}}
 name='record-%06d.json'%gen; tmp=state+'/'+name+'.tmp'; open(tmp,'x').write(json.dumps(d,sort_keys=True,separators=(',',':'))); os.replace(tmp,state+'/'+name)
 tmp=state+'/CURRENT.tmp'; open(tmp,'x').write(name+'\n'); os.replace(tmp,state+'/CURRENT'); return name
def recvline(s): return s.makefile('rb',buffering=0).readline()
def send(s,d): s.sendall((json.dumps(d,sort_keys=True)+'\n').encode())
d={'schema':1,'policy':'L1-read-only-mediated-v1','work_units':{'P':{'id':'P','parent':None,'active':False,'grants':[],'accepted':None},'C':{'id':'C','parent':'P','active':False,'grants':[],'accepted':None}},'events':[]}
commit(d); print(json.dumps({'event':'authority_ready','pid':os.getpid()}),flush=True)
initial_name, initial=readstate(); p0=initial['work_units']['P']; c0=initial['work_units']['C']; observation={k:{'active':v['active'],'grants':v['grants'],'accepted':v['accepted'],'parent':v['parent']} for k,v in initial['work_units'].items()}; allowed0=p0['active'] and c0['active'] and 'read' in p0['grants'] and 'read' in c0['grants']; print(json.dumps({'event':'initial_boundary','record':initial_name,'work_units':observation}),flush=True); q=json.loads(recvline(w)); send(w,{'result':'DENY','reason':'missing-full-path-grant','bytes':0,'initial_state':observation} if not allowed0 else {'result':'UNEXPECTED_ALLOW','reason':'initial-path-grant-present','bytes':0,'initial_state':observation})
while True:
 # Manager acts only through its separate control channel; worker requests are sequenced by test.
 raw=recvline(a)
 if not raw: break
 q=json.loads(raw); d=readstate()[1]
 if q['op']=='grant_read': d['work_units']['P']['grants']=['read']; d['work_units']['C']['grants']=['read']; d['events'].append({'op':'grant_read','actor':'initial-manager'}); send(a,{'result':'COMMITTED','record':commit(d)})
 elif q['op']=='activate': d['work_units']['P']['active']=True; d['work_units']['C']['active']=True; d['events'].append({'op':'activate','actor':'initial-manager'}); send(a,{'result':'COMMITTED','record':commit(d)}); send(w,{'event':'activation-current'})
 # Manager loop receives a subsequent 'stop' only after worker completed.
 if q['op']=='stop': break
 # Worker requests are multiplexed by manager signal: after activation, process exactly READ then ACCEPT.
 if q['op']=='activate':
  q=json.loads(recvline(w)); p=d['work_units']['P']; c=d['work_units']['C']; allowed=p['active'] and c['active'] and 'read' in p['grants'] and 'read' in c['grants']
  if q.get('op')!='read_candidate' or not allowed: send(w,{'result':'DENY','reason':'missing-full-path-grant','bytes':0}); continue
  data=open(source,'rb').read(); presented=hashlib.sha256(data).hexdigest(); send(w,{'result':'OK','bytes':base64.b64encode(data).decode(),'sha256':presented})
  q=json.loads(recvline(w)); blob=base64.b64decode(q['bytes'],validate=True); h=hashlib.sha256(blob).hexdigest()
  if h!=presented: send(w,{'result':'DENY','reason':'candidate-content-mismatch','bytes':0}); continue
  d=readstate()[1]; d['events'].append({'op':'accept','actor':'worker-ingress-W1','sha256':h}); name=commit(d,blob); send(w,{'result':'ACCEPTED','record':name,'identity':readstate()[1]['work_units']['C']['accepted']['identity'],'sha256':h,'bytes':len(blob)})
'''
WORK=r'''import base64,json,os,socket,sys
s=socket.socket(fileno=int(sys.argv[1])); root=sys.argv[2]
def ask(q): s.sendall((json.dumps(q)+'\n').encode()); return json.loads(s.makefile('rb',buffering=0).readline())
def emit(x): print(json.dumps(x,sort_keys=True),flush=True)
missing=ask({'op':'read_candidate'}); paths={}
for n,p in [('current',root+'/protected/CURRENT'),('source',root+'/source/candidate-x.bin'),('symlink',root+'/alias-x')]:
 try: fd=os.open(p,os.O_RDONLY); os.close(fd); paths[n]={'result':'allowed'}
 except OSError as e: paths[n]={'result':'denied','errno':e.errno}
emit({'event':'missing_grant','pid':os.getpid(),'reply':missing,'direct_paths':paths})
activation=json.loads(s.makefile('rb',buffering=0).readline())
read=ask({'op':'read_candidate'}); data=base64.b64decode(read['bytes']) if read.get('result')=='OK' else b''
accepted=ask({'op':'accept','bytes':base64.b64encode(data).decode()}) if data else {'result':'not-attempted'}
emit({'event':'authorized_read_and_accept','pid':os.getpid(),'activation':activation,'read_result':read['result'],'read_hex':data.hex(),'read_sha256':__import__('hashlib').sha256(data).hexdigest(),'accept':accepted})
'''
READER=r'''import hashlib,json,os,sys
root=sys.argv[2]; st=root+'/protected'; name=open(st+'/CURRENT').read().strip(); d=json.load(open(st+'/'+name)); a=d['work_units']['C']['accepted']; b=open(st+'/'+a['object'],'rb').read(); print(json.dumps({'reader_pid':os.getpid(),'record':name,'identity':a['identity'],'sha256':hashlib.sha256(b).hexdigest(),'size':len(b),'bytes_hex':b.hex(),'provenance':a['provenance'],'work_units':d['work_units']},sort_keys=True))
'''
def add_rule(libc,rs,path):
 if not os.path.exists(path): return
 fd=os.open(path,getattr(os,'O_PATH',0o10000000)|os.O_CLOEXEC)
 class Rule(ctypes.Structure): _fields_=[('allowed_access',ctypes.c_uint64),('parent_fd',ctypes.c_int)]
 r=Rule(READ_FILE if os.path.isfile(path) else READ_FILE|READ_DIR,fd)
 if libc.syscall(SYS_ADD,ctypes.c_int(rs),ctypes.c_int(1),ctypes.byref(r),ctypes.c_uint(0))!=0: raise OSError(ctypes.get_errno(),'landlock_add_rule',path)
 os.close(fd)
def confine():
 libc=ctypes.CDLL(None,use_errno=True); attr=ctypes.c_uint64(HANDLED_FS); rs=libc.syscall(SYS_CREATE,ctypes.byref(attr),ctypes.c_size_t(8),ctypes.c_uint(0))
 if rs<0: raise OSError(ctypes.get_errno(),'landlock_create_ruleset')
 for p in ('/usr','/lib','/lib64','/etc/ld.so.cache'): add_rule(libc,rs,p)
 if libc.prctl(38,1,0,0,0)!=0: raise OSError(ctypes.get_errno(),'PR_SET_NO_NEW_PRIVS')
 if libc.syscall(SYS_RESTRICT,ctypes.c_int(rs),ctypes.c_uint(0))!=0: raise OSError(ctypes.get_errno(),'landlock_restrict_self')
 os.close(rs)
def submode(mode):
 if mode=='--authority': exec(compile(AUTH,'<authority>','exec'),{'__name__':'__main__'})
 elif mode=='--worker': exec(compile(WORK,'<worker>','exec'),{'__name__':'__main__'})
 elif mode=='--reader': exec(compile(READER,'<reader>','exec'),{'__name__':'__main__'})
def main():
 if len(sys.argv)>1 and sys.argv[1].startswith('--'): return submode(sys.argv[1])
 if ROOT.exists(): raise RuntimeError('lab already exists; refusing overwrite')
 (ROOT/'source').mkdir(parents=True); (STATE/'objects').mkdir(parents=True); SOURCE.write_bytes(X); os.symlink('source/candidate-x.bin',ROOT/'alias-x')
 wc,ws=socket.socketpair(); ac,asrv=socket.socketpair()
 h=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--authority',str(ROOT),str(ws.fileno()),str(asrv.fileno())],pass_fds=(ws.fileno(),asrv.fileno()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); ws.close(); asrv.close(); ready=h.stdout.readline()
 worker=subprocess.Popen([sys.executable,'-S','-c',WORK,str(wc.fileno()),str(ROOT)],pass_fds=(wc.fileno(),),preexec_fn=confine,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); wc.close()
 missing=json.loads(worker.stdout.readline());
 def admin(op):
  ac.sendall((json.dumps({'op':op})+'\n').encode()); return json.loads(ac.makefile('rb',buffering=0).readline())
 grant=admin('grant_read'); activate=admin('activate'); workerline=worker.stdout.readline(); worker_rc=worker.wait(timeout=3)
 ac.close(); h.wait(timeout=3); hline=h.stdout.read()
 reader=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--reader',str(ROOT)],capture_output=True,text=True,timeout=3,check=True); observed=json.loads(reader.stdout)
 result={'status':'completed','python':sys.version,'kernel':platform.release(),'landlock_abi':ctypes.CDLL(None).syscall(SYS_CREATE,None,0,1),'authority_pid':h.pid,'worker_pid':worker.pid,'reader':observed,'worker_missing_grant':missing,'worker_after_grant':json.loads(workerline),'management_grant_commit':grant,'management_activation_commit':activate,'authority_ready':ready.strip(),'authority_trace':hline.strip(),'worker_returncode':worker_rc,'expected_sha256':hashlib.sha256(X).hexdigest(),'root':str(ROOT),'limits':{'outer_timeout_seconds':20,'virtual_memory_kib':524288}}
 result['pass']=missing['reply'].get('result')=='DENY' and missing['reply'].get('reason')=='missing-full-path-grant' and all(not v['active'] and not v['grants'] and v['accepted'] is None for v in missing['reply']['initial_state'].values()) and all(v['result']=='denied' for v in missing['direct_paths'].values()) and result['worker_after_grant']['read_result']=='OK' and result['worker_after_grant']['accept']['result']=='ACCEPTED' and observed['bytes_hex']==X.hex() and observed['sha256']==hashlib.sha256(X).hexdigest() and observed['provenance']['actor']=='worker-ingress-W1' and worker_rc==0
 (HERE/'raw-result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print(json.dumps(result,sort_keys=True,indent=2))
 if not result['pass']: raise SystemExit(1)
if __name__=='__main__': main()
