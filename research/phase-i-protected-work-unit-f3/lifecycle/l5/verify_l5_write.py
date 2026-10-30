#!/usr/bin/env python3
"""Independent raw-evidence checks for the bounded L5 write/move witness."""
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('l5-write-raw.json')
d=json.loads(p.read_text()); cases=d['cases']; pos=cases['positive']; safe=cases['latent_preserved']; mut=cases['unsafe_mutant']; x='46332d6c6966656379636c652d782d76310a'; xhash='1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061'
def check(name,ok):
 print(('PASS' if ok else 'FAIL')+' '+name)
 return ok
results=[]
results.append(check('raw source hash matches executed implementation',hashlib.sha256(Path(__file__).with_name('l5_write.py').read_bytes()).hexdigest()==d['source_sha256']))
results.append(check('positive configuration has P and C read/write and an actual committed effect',pos['current_state']['P']['grants']==['read','write'] and pos['current_state']['C']['grants']==['read','write'] and pos['worker_observation']['write']['result']=='COMMITTED' and len(pos['effects'])==1 and pos['effects'][0]['committed_before_ack']))
results.append(check('positive effect bytes/hash are independently consistent',bytes.fromhex(pos['effects'][0]['bytes_hex'])==b'authorized-positive' and hashlib.sha256(bytes.fromhex(pos['effects'][0]['bytes_hex'])).hexdigest()==pos['effects'][0]['sha256']))
state=safe['current_state']
results.append(check('whole move records C under Q, with P read-only, local C read/write, and retained read ceiling',state['C']['parent']=='Q' and state['P']['grants']==['read'] and state['Q']['grants']==['read','write'] and state['C']['grants']==['read','write'] and state['C']['latent_ceiling']==['read'] and state['events'][1]['op']=='sealed_whole_move' and state['events'][1]['captured_old_effective']==['read']))
results.append(check('fresh ingress reads exact retained x then write is denied without effect',safe['worker_observation']['read']['result']=='OK' and safe['worker_observation']['read']['sha256']==xhash and safe['worker_observation']['read']['bytes_hex']==x and safe['worker_observation']['write']['result']=='DENY' and not safe['effects']))
results.append(check('mediator checks are tied to moved current record and distinct worker identity',len(safe['actual_checks'])==2 and all(q['parent']=='Q' and q['ingress']=='W1' and q['worker_pid']==safe['worker_pid'] and q['record_sha256']==safe['activation_record_sha256'] for q in safe['actual_checks']) and safe['actual_checks'][0]['allowed'] and not safe['actual_checks'][1]['allowed']))
results.append(check('weakened ceiling admits same post-move write and concrete effect is observed',mut['current_state']['C']['parent']=='Q' and mut['current_state']['C']['latent_ceiling']==['read','write'] and mut['worker_observation']['write']['result']=='COMMITTED' and len(mut['effects'])==1 and mut['actual_checks'][1]['allowed']))
results.append(check('accepted x was unchanged in all cases',all(c['accepted_x_bytes_unchanged'] and c['accepted_x_sha256_before_after']==xhash for c in (pos,safe,mut))))
results.append(check('worker process IDs are distinct from the authority and each other',len({d['cases'][k]['worker_pid'] for k in ('positive','latent_preserved','unsafe_mutant')})==3 and all(d['cases'][k]['worker_pid']!=d['cases'][k]['authority_pid'] for k in ('positive','latent_preserved','unsafe_mutant'))))
raise SystemExit(0 if all(results) else 1)
