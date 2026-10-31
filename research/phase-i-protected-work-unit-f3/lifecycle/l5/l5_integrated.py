#!/usr/bin/env python3
"""L5 integration witness bootstrapped from the unmodified L4 lifecycle."""
import hashlib, json, os, shutil, socket, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
LIFE=HERE.parent
sys.path.insert(0,str(LIFE/'l1'))
import l1
VALID={'read','write'}
CREDENTIAL='test-manager-credential-not-a-production-secret'
WORKER=r'''import json,socket,sys
s=socket.socket(fileno=int(sys.argv[1]))
def ask(op,**kw):
 s.sendall((json.dumps({'op':op,**kw},sort_keys=True)+'\n').encode())
 return json.loads(s.makefile('rb',buffering=0).readline())
print(json.dumps({'read':ask('read_x'),'write':ask('write_d')},sort_keys=True),flush=True)
'''
def digest(b): return hashlib.sha256(b).hexdigest()
def load_current(root):
 st=root/'protected'; name=(st/'CURRENT').read_text().strip()
 if '/' in name or not name.startswith('record-') or not name.endswith('.json'): raise ValueError('bad-current-selector')
 return name,json.loads((st/name).read_text())
def verified_content(root,meta):
 st=(root/'protected').resolve(); rel=Path(meta['object'])
 if rel.is_absolute() or '..' in rel.parts or not rel.parts or rel.parts[0]!='objects': raise ValueError('bad-object-reference')
 p=(st/rel).resolve(strict=True)
 if st not in p.parents: raise ValueError('object-escaped-protected-store')
 b=p.read_bytes()
 if digest(b)!=meta['sha256'] or len(b)!=meta['size']: raise ValueError('accepted-content-integrity-failed')
 return b
def graph_valid(st):
 units=st['work_units']
 if not isinstance(units,dict) or set(units)!={'P','C','Q','D'}: return False
 for key,u in units.items():
  if u.get('id')!=key or not isinstance(u.get('grants'),list) or len(set(u['grants']))!=len(u['grants']) or not set(u['grants'])<=VALID: return False
  parent=u.get('parent')
  if parent is not None and parent not in units: return False
  ceiling=u.get('latent_ceiling')
  if ceiling is not None and (not isinstance(ceiling,list) or len(set(ceiling))!=len(ceiling) or not set(ceiling)<=VALID): return False
 for key in units:
  seen=set(); cur=key
  while cur is not None:
   if cur in seen: return False
   seen.add(cur); cur=units[cur].get('parent')
 return units['P']['parent'] is None and units['Q']['parent'] is None and units['C']['parent'] in {'P','Q'} and units['D']['parent']=='C' and units['D'].get('depends_on')==['C']
def permissions(st,key):
 if not graph_valid(st): raise ValueError('invalid-structure')
 out=set(VALID); cur=key
 while cur is not None:
  u=st['work_units'][cur]; out &= set(u['grants'])
  if 'latent_ceiling' in u: out &= set(u['latent_ceiling'])
  cur=u['parent']
 return out
def commit(root,st,event):
 path=root/'protected'; old,_=load_current(root); n=int(old[7:13])+1
 st['events'].append(event); name=f'record-{n:06d}.json'
 tmp=path/(name+'.tmp'); tmp.write_text(json.dumps(st,sort_keys=True,separators=(',',':'))+'\n'); os.replace(tmp,path/name)
 cur=path/'CURRENT.tmp'; cur.write_text(name+'\n'); os.replace(cur,path/'CURRENT')
 return name,hashlib.sha256((path/name).read_bytes()).hexdigest()
def l4_bootstrap():
 tmp=Path(tempfile.mkdtemp(prefix='ases-l5-l4-')); src=tmp/'lifecycle'; shutil.copytree(LIFE,src,ignore=shutil.ignore_patterns('__pycache__','lab','*.pyc'))
 run=subprocess.run([sys.executable,'-S',str(src/'l4'/'l4.py')],capture_output=True,text=True,timeout=20,check=True)
 root=src/'l4'/'lab'; name,st=load_current(root)
 if st.get('policy')!='L1-read-only-mediated-v1' or not st['work_units']['C'].get('accepted_contents'): raise ValueError('L4 accepted state missing')
 # Retain L4's real accepted object references, and extend that current record with
 # the bounded L5 hierarchy and the dependent D that must travel with C.
 st['work_units']['P'].update(parent=None,grants=['read'])
 st['work_units']['C'].update(parent='P',grants=['read','write'],active=False)
 st['work_units']['Q']={'id':'Q','parent':None,'active':False,'sealed':True,'grants':['read','write'],'accepted_contents':[]}
 y=st['work_units']['C']['accepted_contents'][-1]
 st['work_units']['D']={'id':'D','parent':'C','depends_on':['C'],'active':False,'sealed':True,'grants':['read','write'],'accepted_contents':[y]}
 for u in st['work_units'].values(): u.update(active=False,sealed=True)
 st['current_ingress']=None
 # Append an explicit, atomic current L5 extension to the actual L4 record history.
 new,_=commit(root,st,{'op':'l5-bootstrap-from-l4','source_l4_record':name,'accepted_content_count':len(st['work_units']['C']['accepted_contents'])})
 return tmp,root,new,run.stdout,run.stderr
def manager_roundtrip(client,server,req,st,root):
 client.sendall((json.dumps(req,sort_keys=True)+'\n').encode())
 q=json.loads(server.makefile('rb',buffering=0).readline())
 ok=q.get('authorized_by')=='initial-manager' and q.get('credential')==CREDENTIAL
 result={'result':'DENY','reason':'management-authorization-required'}
 if ok and q.get('op')=='authorize_move':
  if not graph_valid(st) or st['current_ingress'] is not None or any(u['active'] or not u['sealed'] for u in st['work_units'].values()): result={'result':'DENY','reason':'move-requires-current-valid-sealed-state'}
  elif q.get('child')!='C' or q.get('destination')!='Q': result={'result':'DENY','reason':'unsupported-move'}
  else:
   prior={k:sorted(permissions(st,k)) for k in ('C','D')}; st['work_units']['C']['parent']='Q'
   for k in ('C','D'): st['work_units'][k]['latent_ceiling']=prior[k]
   if not graph_valid(st): result={'result':'DENY','reason':'invalid-resulting-structure'}
   else:
    name,h=commit(root,st,{'op':'authorized_sealed_whole_move','actor':q['authorized_by'],'from':'P','to':'Q','included':['C','D'],'old_effective':prior})
    result={'result':'COMMITTED','record':name,'record_sha256':h,'old_effective':prior}
 elif ok and q.get('op')=='authorize_activate':
  if not graph_valid(st) or st['current_ingress'] is not None or st['work_units']['C']['parent']!='Q' or any(u['active'] for u in st['work_units'].values()): result={'result':'DENY','reason':'activation-requires-moved-sealed-state'}
  else:
   st['current_ingress']='W-L5'; st['work_units']['P']['active']=True; st['work_units']['Q']['active']=True; st['work_units']['C']['active']=True; st['work_units']['D']['active']=True
   for u in st['work_units'].values(): u['sealed']=False
   name,h=commit(root,st,{'op':'separately-authorized_activation','actor':q['authorized_by'],'ingress':'W-L5'})
   result={'result':'COMMITTED','record':name,'record_sha256':h,'ingress':'W-L5'}
 server.sendall((json.dumps(result,sort_keys=True)+'\n').encode()); return q,result
def run_case(label,parent_grants,move,mutant=False):
 tmp,root,l4record,l4out,l4err=l4_bootstrap(); l4_raw=json.loads((root.parent/'raw-run.json').read_text()); (HERE/f'l5-integrated-l4-{label}.json').write_text(json.dumps(l4_raw,sort_keys=True,indent=2)+'\n'); state_name,st=load_current(root); st['work_units']['P']['grants']=parent_grants
 # Test the established socket management boundary: an unauthorized request is
 # actually received, denied, and leaves the current state byte-for-byte intact.
 before=json.dumps(st,sort_keys=True); a,b=socket.socketpair(); unauthorized={'op':'authorize_move','authorized_by':'intruder','credential':'wrong','child':'C','destination':'Q'}
 _,denial=manager_roundtrip(a,b,unauthorized,st,root)
 unauthorized_no_mutation=json.dumps(st,sort_keys=True)==before
 if not unauthorized_no_mutation: raise AssertionError('unauthorized management mutated state')
 move_reply=None; activation_reply=None; management=[]
 if move:
  oldc=sorted(permissions(st,'C')); oldd=sorted(permissions(st,'D'))
  st['work_units']['P']['active']=False
  _,move_reply=manager_roundtrip(a,b,{'op':'authorize_move','authorized_by':'initial-manager','credential':CREDENTIAL,'child':'C','destination':'Q'},st,root); management.append(move_reply)
  if move_reply['result']!='COMMITTED': raise AssertionError(move_reply)
  if mutant:
   st['work_units']['C']['latent_ceiling']=['read','write']; st['work_units']['D']['latent_ceiling']=['read','write']
   commit(root,st,{'op':'unsafe_mutant_drop_latent_restrictions'})
  _,activation_reply=manager_roundtrip(a,b,{'op':'authorize_activate','authorized_by':'initial-manager','credential':CREDENTIAL},st,root); management.append(activation_reply)
 else:
  # Positive control has separately authorized current activation without a move.
  st['work_units']['P']['grants']=['read','write']; st['work_units']['P']['active']=False
  # Seed C->P active state is enabled only by management control.
  st['work_units']['C']['parent']='P'; st['current_ingress']=None
  st['work_units']['P']['active']=True; st['work_units']['C']['active']=True; st['work_units']['D']['active']=True; st['work_units']['Q']['active']=False
  for u in st['work_units'].values(): u['sealed']=False
  name,h=commit(root,st,{'op':'separately-authorized_positive_control_activation','actor':'initial-manager','ingress':'W-L5'})
  activation_reply={'result':'COMMITTED','record':name,'record_sha256':h,'ingress':'W-L5'}; st['current_ingress']='W-L5'
  # Persist current ingress exactly as activated.
  name,h=commit(root,st,{'op':'positive_control_ingress_current','actor':'initial-manager'})
  a.close(); b.close()
 if move: a.close(); b.close()
 if not graph_valid(st): raise AssertionError('post-transition graph invalid')
 if move and permissions(st,'D') != (set(VALID) if mutant else {'read'}): raise AssertionError(('unexpected effective D permissions',permissions(st,'D')))
 obj=st['work_units']['C']['accepted_contents'][0]; accepted=verified_content(root,obj)
 pair,child=socket.socketpair()
 worker=subprocess.Popen([sys.executable,'-S','-c',WORKER,str(child.fileno())],pass_fds=(child.fileno(),),preexec_fn=l1.confine,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,close_fds=True); child.close()
 conn=socket.socket(fileno=pair.detach()); stream=conn.makefile('rb',buffering=0); checks=[]; effects=[]
 for _ in range(2):
  req=json.loads(stream.readline()); cur_name,current=load_current(root); valid=graph_valid(current); rights=permissions(current,'D') if valid else set()
  enabled=valid and current.get('current_ingress')=='W-L5' and current['work_units']['D']['active'] and not current['work_units']['D']['sealed']
  allowed=enabled and (('read' in rights) if req['op']=='read_x' else ('write' in rights))
  if req['op']=='read_x' and allowed:
   blob=verified_content(root,current['work_units']['C']['accepted_contents'][0]); reply={'result':'OK','bytes_hex':blob.hex(),'sha256':digest(blob),'identity':current['work_units']['C']['accepted_contents'][0]['identity']}
  elif req['op']=='write_d' and allowed:
   target=root/'effects'; target.mkdir(exist_ok=True); dest=target/'D-write.bin'; payload=b'authorized-positive' if label=='positive' else b'forbidden-after-move'; tmpfile=dest.with_suffix('.tmp'); tmpfile.write_bytes(payload); os.replace(tmpfile,dest); effects.append({'bytes_hex':dest.read_bytes().hex(),'sha256':digest(dest.read_bytes())}); reply={'result':'COMMITTED','effect_sha256':effects[-1]['sha256']}
  else: reply={'result':'DENY','reason':'current-verified-full-path-permission'}
  checks.append({'op':req['op'],'record':cur_name,'record_sha256':digest((root/'protected'/cur_name).read_bytes()),'worker_pid':worker.pid,'current_ingress':current.get('current_ingress'),'parent_C':current['work_units']['C']['parent'],'D_effective':sorted(rights),'allowed':allowed,'reply':reply}); conn.sendall((json.dumps(reply,sort_keys=True)+'\n').encode())
 stdout,stderr=worker.communicate(timeout=3); observation=json.loads(stdout)
 current_name,final=load_current(root); cmeta=final['work_units']['C']['accepted_contents'][0]; finalblob=verified_content(root,cmeta)
 result={'case':label,'l4_record_before_l5':l4record,'l4_run_pass':True,'l4_raw_sha256':digest((root.parent/'raw-run.json').read_bytes()),'l4_raw':l4_raw,'worker_pid':worker.pid,'activation':activation_reply,'move':move_reply,'management':management,'management_denial':{'request':unauthorized,'response':denial,'state_unchanged':unauthorized_no_mutation},'move_event':next((e for e in final['events'] if e.get('op')=='authorized_sealed_whole_move'),None),'activation_event':next((e for e in final['events'] if e.get('op')=='separately-authorized_activation'),None),'accepted_content_metadata':cmeta,'unauthorized_move_denied_without_mutation':denial['result']=='DENY' and unauthorized_no_mutation,'worker_observation':observation,'mediator_checks':checks,'effects':effects,'final_record':current_name,'accepted_x_sha256':digest(finalblob),'accepted_x_bytes_hex':finalblob.hex(),'accepted_x_unchanged':digest(finalblob)==digest(accepted),'dependent_D':{'parent':final['work_units']['D']['parent'],'depends_on':final['work_units']['D']['depends_on'],'included_in_move':not move or final['work_units']['D']['parent']=='C'},'graph_valid':graph_valid(final),'D_effective':sorted(permissions(final,'D')),'source_l4_raw_stderr':l4err}
 shutil.rmtree(tmp)
 return result
def adversarial_structure_controls():
 bad={'schema':1,'work_units':{'P':{'id':'P','parent':'C','grants':['read']},'C':{'id':'C','parent':'P','grants':['read','write']},'Q':{'id':'Q','parent':None,'grants':['read','write']},'D':{'id':'D','parent':'C','depends_on':['C'],'grants':['read','write']}},'current_ingress':None}
 cycle_rejected=not graph_valid(bad); bad['work_units']['P']['parent']=None; bad['work_units']['D']['parent']='MISSING'; dangling_rejected=not graph_valid(bad); bad['work_units']['D']['parent']='C'; bad['work_units']['D']['grants']=['execute']; invalid_right_rejected=not graph_valid(bad)
 return {'cycle_rejected':cycle_rejected,'dangling_parent_rejected':dangling_rejected,'unknown_permission_rejected':invalid_right_rejected}
def main():
 positive=run_case('positive',['read'],False)
 safe=run_case('safe',['read'],True)
 mutant=run_case('weakened',['read'],True,True)
 structures=adversarial_structure_controls()
 checks={'positive_concrete_write':positive['worker_observation']['write']['result']=='COMMITTED' and bool(positive['effects']),'accepted_read_from_verified_l4_storage':safe['worker_observation']['read']['result']=='OK' and safe['worker_observation']['read']['sha256']==safe['accepted_x_sha256'],'safe_move_write_denied':safe['worker_observation']['write']['result']=='DENY' and not safe['effects'],'weakened_mutant_write_effect':mutant['worker_observation']['write']['result']=='COMMITTED' and bool(mutant['effects']),'dependent_D_preserved':safe['dependent_D']['included_in_move'] and safe['D_effective']==['read'],'separate_move_and_activation':safe['move']['record']!=safe['activation']['record'],'accepted_content_unchanged':all(x['accepted_x_unchanged'] for x in (positive,safe,mutant)),**structures}
 out={'source_sha256':digest(Path(__file__).read_bytes()),'status':'L5-INTEGRATED-PASS' if all(checks.values()) else 'L5-INTEGRATED-FAIL','python':sys.version,'kernel':os.uname().release,'cases':{'positive':positive,'safe':safe,'weakened':mutant},'structural_controls':structures,'acceptance':checks,'limits':{'profile':'single local trusted mediator and disposable L4-derived fixture','management_credential':'test-only shared secret; no physical manager identity claim','atomicity':'same-filesystem atomic replace, no fsync/crash/rollback claim','routes':'one inherited Unix socket per worker; no hostile descendants, SCM_RIGHTS, network or alternate mount coverage','cases':3,'write_operations_per_case':1,'does_not_claim':'full F3/F5 closure'}}
 (HERE/'l5-integrated-raw.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n'); print(json.dumps(out,sort_keys=True,indent=2))
 if not all(checks.values()): raise SystemExit(1)
if __name__=='__main__': main()
