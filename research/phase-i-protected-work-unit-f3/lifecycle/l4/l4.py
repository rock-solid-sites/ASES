#!/usr/bin/env python3
"""L4: cold sealed reconstruction, fresh activation, x/y continuation."""
import base64,ctypes,hashlib,json,os,platform,signal,socket,subprocess,sys,threading,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'l1'))
import l1
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'l3'))
import l3
HERE=Path(__file__).resolve().parent; ROOT=HERE/'lab'; X=b'F3-lifecycle-x-v1\n'; Y=b'F3-lifecycle-y-v1\n'; EVENTS=[]
WORK1=r'''import base64,hashlib,json,os,signal,socket,sys,threading,time
s=socket.socket(fileno=int(sys.argv[1])); root=sys.argv[2]
def send(q): s.sendall((json.dumps(q)+'\n').encode())
def recv(): return json.loads(s.makefile('rb',buffering=0).readline())
def emit(q): print(json.dumps(q,sort_keys=True),flush=True)
e1=threading.Event(); e2=threading.Event(); signal.signal(signal.SIGUSR1,lambda a,b:e1.set()); signal.signal(signal.SIGUSR2,lambda a,b:e2.set()); send({'op':'read'}); deny=recv(); paths={}
for n,p in [('source',root+'/source/candidate-x.bin'),('alias',root+'/alias-x')]:
 try: f=os.open(p,os.O_RDONLY); os.close(f); paths[n]={'result':'allowed'}
 except OSError as e: paths[n]={'result':'denied','errno':e.errno}
emit({'event':'old-ingress-initial-denial','pid':os.getpid(),'reply':deny,'paths':paths}); act=recv(); send({'op':'read'}); r=recv(); b=base64.b64decode(r['bytes']) if r.get('result')=='OK' else b''; send({'op':'accept','bytes':base64.b64encode(b).decode()}); a=recv(); emit({'event':'old-w1-accepted-x','pid':os.getpid(),'activation':act,'read':r.get('result'),'accept':a,'bytes_hex':b.hex(),'sha256':hashlib.sha256(b).hexdigest()}); e1.wait(8); start=time.monotonic_ns(); count=0; x=0; end_at=time.monotonic()+0.08
while time.monotonic()<end_at: x=(x*1664525+1013904223)&0xffffffff; count+=1
cpu_end=time.monotonic_ns()
try: send({'op':'read'}); lost=recv()
except OSError as e: lost={'result':'IOERROR','errno':e.errno,'detail':str(e)}
emit({'event':'old-w1-after-h-loss','pid':os.getpid(),'cpu_start_ns':start,'cpu_end_ns':cpu_end,'cpu_iterations':count,'reply':lost}); e2.wait(8)
try: send({'op':'read'}); later=recv()
except OSError as e: later={'result':'IOERROR','errno':e.errno,'detail':str(e)}
emit({'event':'old-w1-after-fresh-activation','pid':os.getpid(),'reply':later})
'''
WORK2=r'''import base64,hashlib,json,socket,sys
s=socket.socket(fileno=int(sys.argv[1]))
def send(q): s.sendall((json.dumps(q)+'\n').encode())
def recv(): return json.loads(s.makefile('rb',buffering=0).readline())
act=recv(); send({'op':'read_x'}); rx=recv(); bx=base64.b64decode(rx['bytes']) if rx.get('result')=='OK' else b''; send({'op':'read_candidate_y'}); cy=recv(); by=base64.b64decode(cy['bytes']) if cy.get('result')=='OK' else b''; send({'op':'accept_y','bytes':base64.b64encode(by).decode()}); ack=recv(); send({'op':'read_y'}); ry=recv(); read_y=base64.b64decode(ry['bytes']) if ry.get('result')=='OK' else b''; print(json.dumps({'event':'fresh-w2-x-y','pid':__import__('os').getpid(),'activation':act,'read_x':rx['result'],'x_hex':bx.hex(),'x_sha256':hashlib.sha256(bx).hexdigest(),'candidate_y':cy['result'],'accept_y':ack,'read_y':ry['result'],'y_hex':read_y.hex(),'y_sha256':hashlib.sha256(read_y).hexdigest()},sort_keys=True),flush=True)
'''
AUTH2=r'''import base64,hashlib,json,os,socket,sys
root=sys.argv[2]; w=socket.socket(fileno=int(sys.argv[3])); a=socket.socket(fileno=int(sys.argv[4])); st=root+'/protected'; srcy=root+'/source/candidate-y.bin'
def recv(s): return s.makefile('rb',buffering=0).readline()
def send(s,d): s.sendall((json.dumps(d,sort_keys=True)+'\n').encode())
def load(): n=open(st+'/CURRENT').read().strip(); d=json.load(open(st+'/'+n)); return n,d
def valid_obj(meta):
 rel=meta['object']
 if not rel.startswith('objects/') or '..' in rel.split('/'): raise ValueError('bad-object-ref')
 b=open(st+'/'+rel,'rb').read(); h=hashlib.sha256(b).hexdigest()
 if h!=meta['sha256'] or len(b)!=meta['size']: raise ValueError('content-integrity-failed')
 return b
def commit(d,blob=None,provenance=None):
 n,_=load(); gen=int(n[7:13])+1
 if blob is not None:
  h=hashlib.sha256(blob).hexdigest(); target=st+'/objects/'+h+'.bin'
  if not os.path.exists(target): open(target+'.tmp','xb').write(blob); os.replace(target+'.tmp',target)
  m={'identity':'C-content-'+h[:16],'sha256':h,'object':'objects/'+h+'.bin','size':len(blob),'provenance':provenance}
  d['work_units']['C']['accepted_contents'].append(m)
 name='record-%06d.json'%gen; open(st+'/'+name+'.tmp','x').write(json.dumps(d,sort_keys=True,separators=(',',':'))); os.replace(st+'/'+name+'.tmp',st+'/'+name); open(st+'/CURRENT.tmp','x').write(name+'\n'); os.replace(st+'/CURRENT.tmp',st+'/CURRENT'); return name
n,d=load(); c=d['work_units']['C']; xmeta=c['accepted']; xb=valid_obj(xmeta)
if d.get('schema')!=1 or d.get('policy')!='L1-read-only-mediated-v1' or not xmeta: raise SystemExit('unsupported-or-incomplete-current-record')
# Cold reconstruction retains the record meaning but creates no bearer and stays sealed.
for unit in d['work_units'].values(): unit['active']=False
c['accepted_contents']=[xmeta]; d['current_ingress']=None
send(a,{'event':'recovered-sealed','record':n,'x_sha256':hashlib.sha256(xb).hexdigest(),'sealed':all(not u['active'] for u in d['work_units'].values()),'ingress':None})
q=json.loads(recv(a))
if q.get('op')!='authorize_activate' or q.get('authorized_by')!='initial-manager': send(a,{'result':'DENY','reason':'fresh-management-required'}); raise SystemExit(0)
d['current_ingress']='W2'; d['work_units']['P']['active']=True; d['work_units']['C']['active']=True; d['events'].append({'op':'fresh_activate','actor':'initial-manager','ingress':'W2'}); name=commit(d); send(a,{'result':'COMMITTED','record':name,'ingress':'W2'}); send(w,{'event':'fresh-activation','record':name})
q=json.loads(recv(w)); n,d=load(); c=d['work_units']['C']; x=valid_obj(c['accepted_contents'][0])
if q.get('op')=='read_x' and d.get('current_ingress')=='W2' and c['active']: send(w,{'result':'OK','bytes':base64.b64encode(x).decode(),'sha256':hashlib.sha256(x).hexdigest()})
else: send(w,{'result':'DENY','bytes':0})
q=json.loads(recv(w)); y=open(srcy,'rb').read(); yh=hashlib.sha256(y).hexdigest()
if q.get('op')=='read_candidate_y': send(w,{'result':'OK','bytes':base64.b64encode(y).decode(),'sha256':yh})
else: send(w,{'result':'DENY','bytes':0})
q=json.loads(recv(w)); offered=base64.b64decode(q['bytes'],validate=True)
if q.get('op')=='accept_y' and hashlib.sha256(offered).hexdigest()==yh:
 n,d=load(); d['events'].append({'op':'accept','actor':'worker-ingress-W2','sha256':yh}); name=commit(d,offered,{'actor':'worker-ingress-W2','source':'candidate-y.bin','presented_sha256':yh}); send(w,{'result':'ACCEPTED','record':name,'identity':d['work_units']['C']['accepted_contents'][-1]['identity'],'sha256':yh})
else: send(w,{'result':'DENY','reason':'candidate-content-mismatch'})
q=json.loads(recv(w)); n,d=load(); y=valid_obj(d['work_units']['C']['accepted_contents'][-1])
if q.get('op')=='read_y' and d.get('current_ingress')=='W2': send(w,{'result':'OK','bytes':base64.b64encode(y).decode(),'sha256':hashlib.sha256(y).hexdigest()})
else: send(w,{'result':'DENY','bytes':0})
'''
VERIFY=r'''import hashlib,json,os,sys
root=sys.argv[1]; st=root+'/protected'; n=open(st+'/CURRENT').read().strip(); d=json.load(open(st+'/'+n)); out=[]
for m in d['work_units']['C']['accepted_contents']:
 b=open(st+'/'+m['object'],'rb').read(); h=hashlib.sha256(b).hexdigest(); out.append({'identity':m['identity'],'sha256':h,'size':len(b),'hex':b.hex(),'provenance':m['provenance']})
print(json.dumps({'record':n,'contents':out,'current_ingress':d['current_ingress'],'events':d['events']},sort_keys=True))
'''
def admin(s,q): s.sendall((json.dumps(q)+'\n').encode()); return json.loads(s.makefile('rb',buffering=0).readline())
def main():
 if len(sys.argv)>1 and sys.argv[1]=='--h1': exec(compile(l3.AUTH,'<H1>','exec'),{'__name__':'__main__'}); return
 if len(sys.argv)>1 and sys.argv[1]=='--h2': exec(compile(AUTH2,'<H2>','exec'),{'__name__':'__main__'}); return
 if ROOT.exists(): raise RuntimeError('L4 lab exists; refusing overwrite')
 (ROOT/'source').mkdir(parents=True); (ROOT/'protected'/'objects').mkdir(parents=True); (ROOT/'source'/'candidate-x.bin').write_bytes(X); (ROOT/'source'/'candidate-y.bin').write_bytes(Y); os.symlink('source/candidate-x.bin',ROOT/'alias-x')
 wc,ws=socket.socketpair(); ac,asrv=socket.socketpair(); h1=w1=h2=w2=None
 try:
  h1=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--h1',str(ROOT),str(ws.fileno()),str(asrv.fileno())],pass_fds=(ws.fileno(),asrv.fileno()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); ws.close(); asrv.close(); ready=json.loads(ac.makefile('rb',buffering=0).readline())
  w1=subprocess.Popen([sys.executable,'-S','-c',WORK1,str(wc.fileno()),str(ROOT)],pass_fds=(wc.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); wc.close(); denial=json.loads(w1.stdout.readline()); grant=admin(ac,{'op':'grant','authorized_by':'initial-manager'}); activation=admin(ac,{'op':'activate','authorized_by':'initial-manager'}); accepted=json.loads(w1.stdout.readline()); kill_ns=time.monotonic_ns(); os.kill(h1.pid,signal.SIGKILL); h1rc=h1.wait(timeout=2); reap_ns=time.monotonic_ns(); w1alive=w1.poll() is None; os.kill(w1.pid,signal.SIGUSR1); lost=json.loads(w1.stdout.readline())
  cold=subprocess.run([sys.executable,'-S','-c',l3.RECOVERY,str(ROOT)],capture_output=True,text=True,timeout=3,check=True); cold_state=json.loads(cold.stdout)
  p2,s2=socket.socketpair(); padmin,adminserv=socket.socketpair(); h2=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--h2',str(ROOT),str(s2.fileno()),str(adminserv.fileno())],pass_fds=(s2.fileno(),adminserv.fileno()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); s2.close(); adminserv.close(); recovered=json.loads(padmin.makefile('rb',buffering=0).readline()); authorize=admin(padmin,{'op':'authorize_activate','authorized_by':'initial-manager'})
  w2=subprocess.Popen([sys.executable,'-S','-c',WORK2,str(p2.fileno())],pass_fds=(p2.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); p2.close(); fresh=json.loads(w2.stdout.readline()); os.kill(w1.pid,signal.SIGUSR2); old_after=json.loads(w1.stdout.readline()); w1rc=w1.wait(timeout=2); w2rc=w2.wait(timeout=2)
  verified=subprocess.run([sys.executable,'-S','-c',VERIFY,str(ROOT)],capture_output=True,text=True,timeout=3,check=True); final=json.loads(verified.stdout); h2.wait(timeout=2); stop={'result':'exited-after-route-sequence'}; padmin.close(); out={'status':'completed','python':sys.version,'kernel':platform.release(),'landlock_abi':ctypes.CDLL(None).syscall(444,None,0,1),'root':str(ROOT),'failure_profile':'H1 SIGKILL/reap; host remains live; H2 cold reconstruction; no OS crash/power loss','h1_pid':h1.pid,'h1_returncode':h1rc,'h1_kill_requested_ns':kill_ns,'h1_reaped_ns':reap_ns,'w1_pid':accepted['pid'],'w1_alive_after_h1_reap':w1alive,'w1_missing_grant':denial,'w1_accept_x':accepted,'w1_after_h1_loss':lost,'cold_reader':cold_state,'h2_pid':h2.pid,'h2_reconstructed_sealed':recovered,'fresh_management_activation':authorize,'w2':fresh,'w1_after_fresh_activation':old_after,'final_independent_readback':final,'returncodes':{'W1':w1rc,'W2':w2rc},'h2_stop':stop,'expected':{'x_hex':X.hex(),'x_sha256':hashlib.sha256(X).hexdigest(),'y_hex':Y.hex(),'y_sha256':hashlib.sha256(Y).hexdigest()},'limits':{'timeout_seconds':20,'virtual_memory_kib':524288}}
  out['pass']=h1rc==-signal.SIGKILL and w1alive and lost['reply']['result']=='IOERROR' and lost['cpu_iterations']>0 and cold_state['sealed_before_use'] and recovered['event']=='recovered-sealed' and recovered['sealed'] and authorize['result']=='COMMITTED' and fresh['x_hex']==X.hex() and fresh['y_hex']==Y.hex() and fresh['accept_y']['result']=='ACCEPTED' and old_after['reply']['result']=='IOERROR' and final['contents'][0]['hex']==X.hex() and final['contents'][1]['hex']==Y.hex() and w1rc==0 and w2rc==0
  (HERE/'raw-run.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n'); print(json.dumps(out,sort_keys=True,indent=2));
  if not out['pass']: raise SystemExit(1)
 except BaseException as e:
  for p in (h1,h2,w1,w2):
   if p is not None and p.poll() is None: p.kill(); p.wait(timeout=2)
  (HERE/'raw-failure.json').write_text(json.dumps({'error':repr(e),'traceback':traceback.format_exc()},sort_keys=True,indent=2)+'\n'); raise
if __name__=='__main__': main()