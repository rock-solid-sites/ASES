#!/usr/bin/env python3
import ctypes
"""L2 live replacement witness, reusing only L1's tested Landlock setup."""
import base64,hashlib,json,os,platform,socket,subprocess,sys,time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'l1'))
import l1
HERE=Path(__file__).resolve().parent; ROOT=HERE/'lab'; X=l1.X
AUTH=r'''import base64,hashlib,json,os,socket,sys
root=sys.argv[1]; w1=socket.socket(fileno=int(sys.argv[2])); w2=socket.socket(fileno=int(sys.argv[3])); a=socket.socket(fileno=int(sys.argv[4])); st=root+'/protected'; objs=st+'/objects'; src=root+'/source/candidate-x.bin'; gen=0; presented=None

def recv(s): return s.makefile('rb',buffering=0).readline()
def send(s,d): s.sendall((json.dumps(d,sort_keys=True)+'\n').encode())
def readstate(): n=open(st+'/CURRENT').read().strip(); return n,json.load(open(st+'/'+n))
def commit(d,blob=None):
 global gen
 gen+=1
 if blob is not None:
  h=hashlib.sha256(blob).hexdigest(); q=objs+'/'+h+'.bin'; t=q+'.tmp'; open(t,'xb').write(blob); os.replace(t,q); d['work_units']['C']['accepted']={'identity':'C-content-'+h[:16],'sha256':h,'object':'objects/'+h+'.bin','size':len(blob),'provenance':{'actor':'worker-ingress-W1','source':'candidate-x.bin','presented_sha256':h}}
 n='record-%06d.json'%gen; t=st+'/'+n+'.tmp'; open(t,'x').write(json.dumps(d,sort_keys=True,separators=(',',':'))); os.replace(t,st+'/'+n); t=st+'/CURRENT.tmp'; open(t,'x').write(n+'\n'); os.replace(t,st+'/CURRENT'); return n
def allowed(d,ingress):
 p=d['work_units']['P']; c=d['work_units']['C']; return ingress==d['current_ingress'] and p['active'] and c['active'] and 'read' in p['grants'] and 'read' in c['grants']
d={'schema':1,'policy':'L1-read-only-mediated-v1','current_ingress':'W1','work_units':{'P':{'id':'P','parent':None,'active':False,'grants':[],'accepted':None},'C':{'id':'C','parent':'P','active':False,'grants':[],'accepted':None}},'events':[]}; commit(d); send(a,{'event':'authority-ready','pid':os.getpid()})
q=json.loads(recv(w1)); n,d0=readstate(); p=d0['work_units']['P']; c=d0['work_units']['C']; empty=not p['active'] and not c['active'] and not p['grants'] and not c['grants'] and c['accepted'] is None
send(w1,{'result':'DENY','reason':'missing-full-path-grant','bytes':0,'initial_empty':empty})
while True:
 q=json.loads(recv(a)); n,d=readstate()
 if q['op']=='grant_read': d['work_units']['P']['grants']=['read']; d['work_units']['C']['grants']=['read']; d['events'].append({'op':'grant_read','actor':'initial-manager'}); send(a,{'result':'COMMITTED','record':commit(d)})
 elif q['op']=='activate':
  d['work_units']['P']['active']=True; d['work_units']['C']['active']=True; d['events'].append({'op':'activate','actor':'initial-manager'}); send(a,{'result':'COMMITTED','record':commit(d)}); send(w1,{'event':'activation-current'}); req=json.loads(recv(w1))
  if req.get('op')=='read' and allowed(d,'W1'):
   blob=open(src,'rb').read(); presented=hashlib.sha256(blob).hexdigest(); send(w1,{'result':'OK','bytes':base64.b64encode(blob).decode(),'sha256':presented}); req=json.loads(recv(w1)); blob2=base64.b64decode(req['bytes'],validate=True)
   if hashlib.sha256(blob2).hexdigest()==presented:
    d=readstate()[1]; d['events'].append({'op':'accept','sha256':presented,'actor':'worker-ingress-W1'}); name=commit(d,blob2); send(w1,{'result':'ACCEPTED','record':name,'sha256':presented,'identity':readstate()[1]['work_units']['C']['accepted']['identity']})
   else: send(w1,{'result':'DENY','reason':'content-mismatch'})
 elif q['op']=='replace':
  d=readstate()[1]; d['current_ingress']='W2'; d['events'].append({'op':'replace','old':'W1','new':'W2'}); name=commit(d); send(a,{'result':'COMMITTED','record':name,'current_ingress':'W2'}); send(w1,{'event':'replacement-committed'}); old=json.loads(recv(w1)); d=readstate()[1]
  if old.get('op')=='read' and not allowed(d,'W1'): send(w1,{'result':'DENY','reason':'stale-ingress','bytes':0,'current_ingress':d['current_ingress']})
  else: send(w1,{'result':'UNEXPECTED_ALLOW','bytes':0})
  send(w2,{'event':'activation-current'}); fresh=json.loads(recv(w2)); d=readstate()[1]
  if fresh.get('op')=='read' and allowed(d,'W2') and d['work_units']['C']['accepted']:
   blob=open(st+'/'+d['work_units']['C']['accepted']['object'],'rb').read(); send(w2,{'result':'OK','bytes':base64.b64encode(blob).decode(),'sha256':hashlib.sha256(blob).hexdigest(),'ingress':'W2'})
  else: send(w2,{'result':'DENY','reason':'not-current-or-not-granted','bytes':0})
 elif q['op']=='stop': send(a,{'result':'STOPPED'}); break
'''
WORK=r'''import base64,hashlib,json,socket,sys
s=socket.socket(fileno=int(sys.argv[1])); root=sys.argv[2]; role=sys.argv[3]
def send(q): s.sendall((json.dumps(q)+'\n').encode())
def recv(): return json.loads(s.makefile('rb',buffering=0).readline())
def emit(q): print(json.dumps(q,sort_keys=True),flush=True)
if role=='W1':
 send({'op':'read'}); first=recv(); emit({'event':'missing-grant','reply':first,'pid':__import__('os').getpid()}); act=recv(); send({'op':'read'}); r=recv(); b=base64.b64decode(r['bytes']) if r.get('result')=='OK' else b''; accepted={'result':'not-attempted'}
 if b: send({'op':'accept','bytes':base64.b64encode(b).decode()}); accepted=recv()
 emit({'event':'w1-before-replacement','activation':act,'read':r.get('result'),'bytes_hex':b.hex(),'sha256':hashlib.sha256(b).hexdigest(),'accept':accepted,'pid':__import__('os').getpid()})
 trigger=recv(); send({'op':'read'}); stale=recv(); emit({'event':'w1-after-replacement','trigger':trigger,'reply':stale,'pid':__import__('os').getpid()})
else:
 act=recv(); send({'op':'read'}); r=recv(); b=base64.b64decode(r['bytes']) if r.get('result')=='OK' else b''; emit({'event':'w2-after-replacement','activation':act,'reply':r,'bytes_hex':b.hex(),'sha256':hashlib.sha256(b).hexdigest(),'pid':__import__('os').getpid()})
'''
def sendadmin(s,op):
 s.sendall((json.dumps({'op':op})+'\n').encode()); return json.loads(s.makefile('rb',buffering=0).readline())
def main():
 if len(sys.argv)>1 and sys.argv[1]=='--auth': exec(compile(AUTH,'<authority>','exec'),{'__name__':'__main__'}); return
 if ROOT.exists(): raise RuntimeError('L2 lab exists; refusing overwrite')
 (ROOT/'source').mkdir(parents=True); (ROOT/'protected'/'objects').mkdir(parents=True); (ROOT/'source'/'candidate-x.bin').write_bytes(X)
 p1,c1=socket.socketpair(); p2,c2=socket.socketpair(); pa,ca=socket.socketpair()
 h=subprocess.Popen([sys.executable,'-S','-c',AUTH,str(ROOT),str(c1.fileno()),str(c2.fileno()),str(ca.fileno())],pass_fds=(c1.fileno(),c2.fileno(),ca.fileno()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); c1.close(); c2.close(); ca.close(); ready=json.loads(pa.makefile('rb',buffering=0).readline())
 w1=subprocess.Popen([sys.executable,'-S','-c',WORK,str(p1.fileno()),str(ROOT),'W1'],pass_fds=(p1.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); p1.close()
 missing=json.loads(w1.stdout.readline()); grant=sendadmin(pa,'grant_read'); activation=sendadmin(pa,'activate'); before=json.loads(w1.stdout.readline())
 replacement=sendadmin(pa,'replace')
 w2=subprocess.Popen([sys.executable,'-S','-c',WORK,str(p2.fileno()),str(ROOT),'W2'],pass_fds=(p2.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,close_fds=True); p2.close()
 stale=json.loads(w1.stdout.readline()); fresh=json.loads(w2.stdout.readline()); rc1=w1.wait(timeout=3); rc2=w2.wait(timeout=3); stop=sendadmin(pa,'stop'); h.wait(timeout=3); trace=h.stdout.read(); pa.close()
 digest=hashlib.sha256(X).hexdigest(); out={'status':'completed','pass':missing['reply'].get('result')=='DENY' and missing['reply'].get('initial_empty') and before['read']=='OK' and before['sha256']==digest and before['accept']['result']=='ACCEPTED' and replacement.get('current_ingress')=='W2' and stale['reply'].get('reason')=='stale-ingress' and stale['reply'].get('bytes')==0 and fresh['reply'].get('result')=='OK' and fresh['sha256']==digest and fresh['bytes_hex']==X.hex() and rc1==0 and rc2==0,'python':sys.version,'kernel':platform.release(),'landlock_abi':ctypes.CDLL(None).syscall(444,None,0,1),'root':str(ROOT),'expected_sha256':digest,'authority_ready':ready,'grant':grant,'activation':activation,'replacement_commit':replacement,'w1_missing':missing,'w1_before_replacement':before,'w1_after_replacement':stale,'w2_after_replacement':fresh,'worker_returncodes':{'W1':rc1,'W2':rc2},'stop':stop,'authority_trace':trace.strip(),'pids':{'H':h.pid,'W1':before['pid'],'W2':fresh['pid']},'limits':{'timeout_seconds':20,'virtual_memory_kib':524288}}
 (HERE/'raw-run.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n'); print(json.dumps(out,sort_keys=True,indent=2));
 if not out['pass']: raise SystemExit(1)
if __name__=='__main__': main()