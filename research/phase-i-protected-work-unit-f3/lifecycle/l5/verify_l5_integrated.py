#!/usr/bin/env python3
"""Independent checks over L5 integration raw observations and L4 evidence."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
raw_path=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'l5-integrated-raw.json'
d=json.loads(raw_path.read_text()); cases=d['cases']; pos=cases['positive']; safe=cases['safe']; mutant=cases['weakened']; outcomes=[]
def check(name,ok):
 print(('PASS ' if ok else 'FAIL ')+name); outcomes.append(bool(ok))
check('raw source digest matches the executed integration source',hashlib.sha256((HERE/'l5_integrated.py').read_bytes()).hexdigest()==d['source_sha256'])
for name,c in cases.items():
 evidence=json.loads((HERE/f'l5-integrated-l4-{name}.json').read_text())
 l4=c['l4_raw']; contents=l4['final_independent_readback']['contents']
 check(name+' retained independent L4 run evidence',evidence==l4 and l4['pass'] is True and l4['status']=='completed')
 check(name+' retains both exact accepted L4 contents',len(contents)==2 and all(bytes.fromhex(x['hex']) and hashlib.sha256(bytes.fromhex(x['hex'])).hexdigest()==x['sha256'] for x in contents))
accepted_x=pos['l4_raw']['expected']['x_sha256']
check('post-move read is exact x from retained and hash-verified L4 accepted storage',safe['worker_observation']['read']['result']=='OK' and safe['worker_observation']['read']['sha256']==accepted_x and safe['worker_observation']['read']['bytes_hex']==pos['l4_raw']['expected']['x_hex'] and safe['accepted_content_metadata']['sha256']==accepted_x)
check('accepted x identity/provenance is retained from L4',safe['worker_observation']['read']['identity']==safe['accepted_content_metadata']['identity'] and safe['accepted_content_metadata']['provenance']['presented_sha256']==accepted_x)
check('C and dependent D moved together under Q, D remains child/dependent of C',safe['move_event']['included']==['C','D'] and safe['move_event']['from']=='P' and safe['move_event']['to']=='Q' and safe['dependent_D']['parent']=='C' and safe['dependent_D']['depends_on']==['C'])
check('full transitive path preserves read-only effective ceiling for D',safe['D_effective']==['read'] and safe['move_event']['old_effective']=={'C':['read'],'D':['read']} and safe['graph_valid'])
check('move and activation are distinct authorized whole records',safe['move']['result']=='COMMITTED' and safe['activation']['result']=='COMMITTED' and safe['move']['record']!=safe['activation']['record'] and safe['activation_event']['op']=='separately-authorized_activation')
check('unauthorized management request is denied with no state mutation',safe['management_denial']['response']['result']=='DENY' and safe['management_denial']['state_unchanged'])
check('safe move permits verified read, denies write, and creates no effect',safe['worker_observation']['read']['result']=='OK' and safe['worker_observation']['write']['result']=='DENY' and not safe['effects'] and all(x['allowed'] is False for x in safe['mediator_checks'] if x['op']=='write_d'))
check('positive control commits concrete write effect',pos['worker_observation']['write']['result']=='COMMITTED' and len(pos['effects'])==1 and bytes.fromhex(pos['effects'][0]['bytes_hex'])==b'authorized-positive' and hashlib.sha256(bytes.fromhex(pos['effects'][0]['bytes_hex'])).hexdigest()==pos['effects'][0]['sha256'])
check('weakened restriction mutation admits same post-move write',mutant['worker_observation']['write']['result']=='COMMITTED' and mutant['D_effective']==['read','write'] and len(mutant['effects'])==1)
check('accepted object bytes/hash remain unchanged in all cases',all(c['accepted_x_unchanged'] and c['accepted_x_sha256']==accepted_x and c['accepted_x_bytes_hex']==pos['l4_raw']['expected']['x_hex'] for c in cases.values()))
check('cycle, dangling parent, and unknown permission structures are rejected',all(d['structural_controls'].values()))
check('every runtime case reports a valid final graph and the bounded status',all(c['graph_valid'] for c in cases.values()) and d['status']=='L5-INTEGRATED-PASS')
raise SystemExit(0 if all(outcomes) else 1)
