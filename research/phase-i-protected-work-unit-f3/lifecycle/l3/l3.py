#!/usr/bin/env python3
"""L3: actual H=M process loss, CPU-only worker continuation, cold sealed readback."""
import base64,ctypes,hashlib,json,os,platform,signal,socket,subprocess,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'l1'))
import l1
HERE=Path(__file__).resolve().parent; ROOT=HERE/'lab'; X=l1.X; EVENTS=[]
AUTH=r'''import base64,hashlib,json,os,socket,sys
root=sys.argv[2]; w=socket.socket(fileno=int(sys.argv[3])); a=socket.socket(fileno=int(sys.argv[4])); st=root+'/protected'; objs=st+'/objects'; src=root+'/source/candidate-x.bin'; gen=0; presented=None
def recv(s): return s.makefile('rb',buffering=0).readline()
def send(s,d): s.sendall((json.dumps(d,sort_keys=True)+'\n').encode())
def state(): n=open(st+'/CURRENT').read().strip(); return n,json.load(open(st+'/'+n))
def commit(d,blob=None):
 global gen
 gen+=1
 if blob is not None:
  h=hashlib.sha256(blob).hexdigest(); dest=objs+'/'+h+'.bin'; open(dest+'.tmp','xb').write(blob); os.replace(dest+'.tmp',dest); d['work_units']['C']['accepted']={'identity':'C-content-'+h[:16],'sha256':h,'object':'objects/'+h+'.bin','size':len(blob),'provenance':{'actor':'worker-ingress-W1','source':'candidate-x.bin','presented_sha256':h}}
 n='record-%06d.json'%gen; open(st+'/'+n+'.tmp','x').write(json.dumps(d,sort_keys=True,separators=(',',':'))); os.replace(st+'/'+n+'.tmp',st+'/'+n); open(st+'/CURRENT.tmp','x').write(n+'\n'); os.replace(st+'/CURRENT.tmp',st+'/CURRENT'); return n
def allowed(d):
 p=d['work_units']['P']; c=d['work_units']['C']; return d['current_ingress']=='W1' and p['active'] and c['active'] and 'read' in p['grants'] and 'read' in c['grants']
d={'schema':1,'policy':'L1-read-only-mediated-v1','current_ingress':'W1','work_units':{'P':{'id':'P','parent':None,'active':False,'grants':[],'accepted':None},'C':{'id':'C','parent':'P','active':False,'grants':[],'accepted':None}},'events':[]}; commit(d); send(a,{'event':'authority-ready','pid':os.getpid()}); req=json.loads(recv(w)); n,d0=state(); p=d0['work_units']['P']; c=d0['work_units']['C']; empty=not p['active'] and not c['active'] and not p['grants'] and not c['grants'] and c['accepted'] is None; send(w,{'result':'DENY','reason':'missing-full-path-grant','bytes':0,'initial_empty':empty})
while True:
 raw=recv(a)
 if not raw: break
 q=json.loads(raw); n,d=state()
 if q['op']=='grant': d['work_units']['P']['grants']=['read']; d['work_units']['C']['grants']=['read']; d['events'].append({'op':'grant_read','actor':'initial-manager'}); send(a,{'result':'COMMITTED','record':commit(d)})
 elif q['op']=='activate':
  d['work_units']['P']['active']=True; d['work_units']['C']['active']=True; d['events'].append({'op':'activate','actor':'initial-manager'}); send(a,{'result':'COMMITTED','record':commit(d)}); send(w,{'event':'activation-current'}); req=json.loads(recv(w))
  if req.get('op')=='read' and allowed(d):
   data=open(src,'rb').read(); presented=hashlib.sha256(data).hexdigest(); send(w,{'result':'OK','bytes':base64.b64encode(data).decode(),'sha256':presented}); req=json.loads(recv(w)); offered=base64.b64decode(req['bytes'],validate=True)
   if hashlib.sha256(offered).hexdigest()==presented:
    d=state()[1]; d['events'].append({'op':'accept','actor':'worker-ingress-W1','sha256':presented}); name=commit(d,offered); send(w,{'result':'ACCEPTED','record':name,'identity':state()[1]['work_units']['C']['accepted']['identity'],'sha256':presented})
   else: send(w,{'result':'DENY','reason':'content-mismatch','bytes':0})
  else: send(w,{'result':'DENY','reason':'missing-full-path-grant','bytes':0})
'''
WORK=r'''import base64,hashlib,json,os,signal,socket,sys,threading,time
s=socket.socket(fileno=int(sys.argv[1])); root=sys.argv[2]
def send(q): s.sendall((json.dumps(q)+'\n').encode())
def recv(): return json.loads(s.makefile('rb',buffering=0).readline())
def emit(q): print(json.dumps(q,sort_keys=True),flush=True)
signal.signal(signal.SIGUSR1,lambda sig,frame: event.set()); event=threading.Event(); send({'op':'read'}); missing=recv(); direct={}
for n,p in [('source',root+'/source/candidate-x.bin'),('alias',root+'/alias-x')]:
 try: fd=os.open(p,os.O_RDONLY); os.close(fd); direct[n]={'result':'allowed'}
 except OSError as e: direct[n]={'result':'denied','errno':e.errno}
emit({'event':'pre-loss-denial','pid':os.getpid(),'reply':missing,'direct_paths':direct}); act=recv(); send({'op':'read'}); r=recv(); b=base64.b64decode(r['bytes']) if r.get('result')=='OK' else b''; send({'op':'accept','bytes':base64.b64encode(b).decode()}); accepted=recv(); emit({'event':'accepted-before-loss','pid':os.getpid(),'activation':act,'read':r['result'],'bytes_hex':b.hex(),'sha256':hashlib.sha256(b).hexdigest(),'accepted':accepted}); event.wait(8); start=time.monotonic_ns(); x=0; count=0; until=time.monotonic()+0.08
while time.monotonic()<until: x=(x*1664525+1013904223)&0xffffffff; count+=1
end=time.monotonic_ns()
try: send({'op':'read'}); reply=recv()
except OSError as e: reply={'result':'IOERROR','errno':e.errno,'detail':str(e)}
paths={}
for n,p in [('source',root+'/source/candidate-x.bin'),('alias',root+'/alias-x')]:
 try: fd=os.open(p,os.O_RDONLY); os.close(fd); paths[n]={'result':'allowed'}
 except OSError as e: paths[n]={'result':'denied','errno':e.errno}
try: fd=os.open(root+'/source/candidate-x.bin',os.O_WRONLY); os.close(fd); write={'result':'allowed'}
except OSError as e: write={'result':'denied','errno':e.errno}
emit({'event':'post-loss','pid':os.getpid(),'signal_received':event.is_set(),'cpu_start_ns':start,'cpu_end_ns':end,'cpu_iterations':count,'cpu_value':x,'retained_ingress_reply':reply,'direct_paths':paths,'direct_write_open':write})
'''
RECOVERY=r'''import hashlib,json,os,sys
root=sys.argv[1]; st=root+'/protected'; name=open(st+'/CURRENT').read().strip()
if '/' in name or not name.startswith('record-') or not name.endswith('.json'): raise SystemExit('unsupported-current-selector')
d=json.load(open(st+'/'+name))
if d.get('schema')!=1 or d.get('policy')!='L1-read-only-mediated-v1': raise SystemExit('unsupported-policy')
c=d['work_units']['C']; accepted=c['accepted']; rel=accepted['object']
if not rel.startswith('objects/') or '..' in rel.split('/'): raise SystemExit('invalid-object-reference')
b=open(st+'/'+rel,'rb').read(); h=hashlib.sha256(b).hexdigest()
if h!=accepted['sha256'] or len(b)!=accepted['size']: raise SystemExit('accepted-content-mismatch')
recovered={}
for key,u in d['work_units'].items(): recovered[key]={'id':u['id'],'parent':u['parent'],'grants':u['grants'],'active':False,'sealed':True,'execution_ingress':None,'accepted':u['accepted']}
print(json.dumps({'event':'cold-recovery','pid':os.getpid(),'record':name,'policy':d['policy'],'reconstructed':recovered,'content_sha256':h,'content_size':len(b),'content_hex':b.hex(),'sealed_before_use':all(u['sealed'] and not u['active'] and u['execution_ingress'] is None for u in recovered.values())},sort_keys=True))
'''
def sendadmin(s,op): s.sendall((json.dumps({'op':op})+'\n').encode()); return json.loads(s.makefile('rb',buffering=0).readline())
def main():
 if len(sys.argv)>1 and sys.argv[1]=='--authority': exec(compile(AUTH,'<authority>','exec'),{'__name__':'__main__'}); return
 if len(sys.argv)>1 and sys.argv[1]=='--recovery': exec(compile(RECOVERY,'<recovery>','exec'),{'__name__':'__main__'}); return
 if ROOT.exists(): raise RuntimeError('L3 lab exists; refusing overwrite')
 (ROOT/'source').mkdir(parents=True); (ROOT/'protected'/'objects').mkdir(parents=True); (ROOT/'source'/'candidate-x.bin').write_bytes(X); os.symlink('source/candidate-x.bin',ROOT/'alias-x')
 wc,ws=socket.socketpair(); ac,asrv=socket.socketpair(); h=w=None
 try:
  h=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--authority',str(ROOT),str(ws.fileno()),str(asrv.fileno())],pass_fds=(ws.fileno(),asrv.fileno()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); ws.close(); asrv.close(); ready=json.loads(ac.makefile('rb',buffering=0).readline())
  w=subprocess.Popen([sys.executable,'-S','-c',WORK,str(wc.fileno()),str(ROOT)],pass_fds=(wc.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); wc.close(); missing=json.loads(w.stdout.readline()); EVENTS.append(missing); grant=sendadmin(ac,'grant'); activation=sendadmin(ac,'activate'); baseline=json.loads(w.stdout.readline()); EVENTS.append(baseline)
  if not baseline['accepted'].get('result')=='ACCEPTED': raise RuntimeError('nonvacuous acceptance failed')
  kill_ns=time.monotonic_ns(); os.kill(h.pid,signal.SIGKILL); hrc=h.wait(timeout=2); reaped_ns=time.monotonic_ns(); alive=(w.poll() is None); os.kill(w.pid,signal.SIGUSR1); post=json.loads(w.stdout.readline()); EVENTS.append(post); wrc=w.wait(timeout=3)
  recovery=subprocess.run([sys.executable,'-S','-c',RECOVERY,str(ROOT)],capture_output=True,text=True,timeout=3,check=True); recovered=json.loads(recovery.stdout); EVENTS.append(recovered)
  out={'status':'completed','pass':missing['reply']['result']=='DENY' and missing['reply']['initial_empty'] and baseline['accepted']['result']=='ACCEPTED' and hrc==-signal.SIGKILL and alive and post['signal_received'] and post['cpu_iterations']>0 and post['retained_ingress_reply']['result']=='IOERROR' and all(v['result']=='denied' for v in post['direct_paths'].values()) and post['direct_write_open']['result']=='denied' and recovered['sealed_before_use'] and recovered['content_hex']==X.hex() and recovered['content_sha256']==hashlib.sha256(X).hexdigest(),'python':sys.version,'kernel':platform.release(),'landlock_abi':ctypes.CDLL(None).syscall(444,None,0,1),'authority_pid':h.pid,'authority_returncode':hrc,'worker_pid':w.pid,'worker_returncode':wrc,'authority_ready':ready,'management_grant':grant,'management_activation':activation,'worker_pre_loss_denial':missing,'worker_pre_loss_acceptance':baseline,'kill_requested_ns':kill_ns,'authority_reaped_ns':reaped_ns,'worker_alive_after_reap':alive,'worker_post_loss':post,'cold_recovery':recovered,'root':str(ROOT),'expected_x_sha256':hashlib.sha256(X).hexdigest(),'failure_profile':'authority-process-SIGKILL; host kernel/filesystem remain live; no OS-crash/power-loss inference','limits':{'timeout_seconds':20,'virtual_memory_kib':524288}}
  (HERE/'raw-run.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n'); print(json.dumps(out,sort_keys=True,indent=2))
  if not out['pass']: raise SystemExit(1)
 except BaseException as e:
  if h is not None and h.poll() is None: h.kill(); h.wait(timeout=2)
  if w is not None and w.poll() is None: w.kill(); w.wait(timeout=2)
  (HERE/'raw-failure.json').write_text(json.dumps({'error':repr(e),'traceback':traceback.format_exc(),'events':EVENTS},sort_keys=True,indent=2)+'\n'); raise
if __name__=='__main__': main()