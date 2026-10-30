#!/usr/bin/env python3
"""Bounded L5 host witness: mediated write effect and sealed P-to-Q move."""
import hashlib, json, os, platform, socket, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
LIFE=HERE.parent
sys.path.insert(0,str(LIFE/'l1'))
import l1
X=b'F3-lifecycle-x-v1\n'
EXPECTED=hashlib.sha256(X).hexdigest()
WORKER=r'''import json,os,socket,sys
s=socket.socket(fileno=int(sys.argv[1]))
def ask(op,**kw):
 s.sendall((json.dumps({'op':op,**kw},sort_keys=True)+'\n').encode()); return json.loads(s.makefile('rb',buffering=0).readline())
read=ask('read_x')
write=ask('write',payload='post-move-forbidden' if sys.argv[2]=='move' else 'authorized-positive')
print(json.dumps({'pid':os.getpid(),'read':read,'write':write},sort_keys=True),flush=True)
'''
def commit(state_path, state, event):
 state['events'].append(event)
 tmp=state_path.with_suffix('.tmp')
 tmp.write_text(json.dumps(state,sort_keys=True,separators=(',',':'))+'\n')
 os.replace(tmp,state_path)
 return hashlib.sha256(state_path.read_bytes()).hexdigest()
def permissions(state):
 c=state['C']; p=state.get(c['parent']); path=set(c['grants'])
 if p is not None: path &= set(p['grants'])
 path &= set(c.get('latent_ceiling',c['grants']))
 return path
def run_case(name, *, parent_grants, move=False, mutant=False):
 root=Path(tempfile.mkdtemp(prefix='ases-l5-'+name+'-'))
 (root/'effects').mkdir(); content=HERE.parent/'l4'/'lab'/'protected'/'objects'/f'{EXPECTED}.bin'
 assert content.read_bytes()==X and hashlib.sha256(content.read_bytes()).hexdigest()==EXPECTED
 state_path=root/'CURRENT.json'
 state={'schema':1,'id':'C','sealed':False,'active':True,'current_ingress':'W1','C':{'id':'C','parent':'P','grants':['read','write'],'latent_ceiling':['read','write']},'P':{'id':'P','grants':parent_grants},'Q':{'id':'Q','grants':['read','write']},'events':[]}
 commit(state_path,state,{'op':'initialize','actor':'initial-manager','record':'whole'})
 if move:
  # The move captures the old full-path ceiling before changing containment.
  old_effective=sorted(permissions(state))
  state['sealed']=True; state['active']=False; state['current_ingress']=None
  state['C']['latent_ceiling']=['read','write'] if mutant else old_effective
  state['C']['parent']='Q'
  move_hash=commit(state_path,state,{'op':'sealed_whole_move','actor':'initial-manager','from':'P','to':'Q','captured_old_effective':old_effective,'mutant_dropped_latent':mutant})
  state['sealed']=False; state['active']=True; state['current_ingress']='W1'
  activation_hash=commit(state_path,state,{'op':'fresh_authorized_activation','actor':'initial-manager','ingress':'W1'})
 else:
  move_hash=None; activation_hash=hashlib.sha256(state_path.read_bytes()).hexdigest()
 parent,schild=socket.socketpair()
 proc=subprocess.Popen([sys.executable,'-S','-c',WORKER,str(schild.fileno()),'move' if move else 'positive'],pass_fds=(schild.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,close_fds=True)
 schild.close(); checks=[]; effects=[]
 try:
  stream=parent.makefile('rb',buffering=0)
  for _ in range(2):
   req=json.loads(stream.readline()); st=json.loads(state_path.read_text()); effect={'read_x':'read','write':'write'}.get(req['op']); allowed=st['active'] and not st['sealed'] and st['current_ingress']=='W1' and effect in permissions(st)
   decision={'actor_pid':os.getpid(),'worker_pid':proc.pid,'record_sha256':hashlib.sha256(state_path.read_bytes()).hexdigest(),'op':req['op'],'parent':st['C']['parent'],'effective':sorted(permissions(st)),'allowed':allowed,'ingress':st['current_ingress']}
   checks.append(decision)
   if req['op']=='read_x' and allowed:
    reply={'result':'OK','bytes_hex':X.hex(),'sha256':EXPECTED,'identity':'C-accepted-x'}
   elif req['op']=='write' and allowed:
    target=root/'effects'/'write-effect.bin'; payload=req['payload'].encode(); temp=target.with_suffix('.tmp'); temp.write_bytes(payload); os.replace(temp,target)
    effects.append({'path':str(target),'bytes_hex':target.read_bytes().hex(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'committed_before_ack':target.exists()})
    reply={'result':'COMMITTED','effect_sha256':effects[-1]['sha256']}
   else: reply={'result':'DENY','reason':'current-effective-permission'}
   parent.sendall((json.dumps(reply,sort_keys=True)+'\n').encode())
  stdout,stderr=proc.communicate(timeout=3)
  assert proc.returncode==0,(proc.returncode,stderr)
  obs=json.loads(stdout)
  out={'case':name,'authority_pid':os.getpid(),'worker_pid':proc.pid,'move_record_sha256':move_hash,'activation_record_sha256':activation_hash,'actual_checks':checks,'worker_observation':obs,'effects':effects,'current_state':json.loads(state_path.read_text()),'accepted_x_sha256_before_after':EXPECTED,'accepted_x_bytes_unchanged':content.read_bytes()==X,'routes':{'worker_to_authority':'one inherited socketpair fd; request-by-request H authorization','authority_to_effect':'mediator-only atomic replace in disposable effects/','worker_direct_filesystem':'Landlock confined; no target or accepted-object fd passed','accepted_x_mutation':'none'}}
  return out
 finally:
  parent.close()
  if proc.poll() is None: proc.kill(); proc.wait()
def main():
 positive=run_case('authorized-write-control',parent_grants=['read','write'])
 safe=run_case('latent-ceiling-preserved',parent_grants=['read'],move=True)
 mutant=run_case('latent-ceiling-dropped-mutant',parent_grants=['read'],move=True,mutant=True)
 checks={'positive_write_succeeded':positive['worker_observation']['write']['result']=='COMMITTED','moved_read_succeeded':safe['worker_observation']['read']['result']=='OK','moved_write_denied':safe['worker_observation']['write']['result']=='DENY','mutant_forbidden_write_succeeded':mutant['worker_observation']['write']['result']=='COMMITTED','mutant_effect_detected':bool(mutant['effects']) and not safe['effects'],'content_unchanged':all(x['accepted_x_bytes_unchanged'] for x in (positive,safe,mutant)),'checks_observed':all(len(x['actual_checks'])==2 for x in (positive,safe,mutant))}
 result={'status':'L5-PASS' if all(checks.values()) else 'L5-FAIL','python':sys.version,'kernel':platform.release(),'landlock_abi':l1.ctypes.CDLL(None).syscall(444,None,0,1),'source_sha256':__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),'cases':{'positive':positive,'latent_preserved':safe,'unsafe_mutant':mutant},'acceptance':checks,'limits':{'cases':3,'worker_requests_each':2,'outer_timeout_seconds':20,'virtual_memory_kib':524288}}
 (HERE/'l5-write-raw.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n'); print(json.dumps(result,sort_keys=True,indent=2))
 if not all(checks.values()): raise SystemExit(1)
if __name__=='__main__': main()
