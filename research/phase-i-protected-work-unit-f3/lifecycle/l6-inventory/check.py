#!/usr/bin/env python3
"""Differentiate complete directory inventory, catalog projection and logical disposal."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
X='accepted x with retained identity / μ';Z='unaccepted durable candidate z / μ'
class Violation(Exception):pass
def expect(v,why):
    if not v:raise Violation(why)
def frame(event):
    expect(json.loads(event['raw_line'])==event['frame'],'wire/parsed frame contradiction')
    return event['frame']
def state(value):
    expect(value['sealed'] and value['integrity_check']=='ok','not sealed or SQL integrity failed')
    for name,file in value['files'].items():
        raw=bytes.fromhex(file['raw_hex']);expect(hashlib.sha256(raw).hexdigest()==file['sha256'] and len(raw)==file['size'],'actual object bytes/hash mismatch')
    expect(value['unknown_files']==sorted(set(value['files'])-{r['name'] for r in value['dependencies']}),'catalog/directory inventory contradiction')
    return {k:value[k] for k in ('live','sealed','dependencies','files','unknown_files','objects_directory_exists')}
def check(name,c):
    try:
        for child in c['children']:
            expect(child['start_ns']<child['ready_ns']<child['exit_ns'] and child['exit'] in (0,-9),'process lifecycle mismatch')
            for event in child['events']:
                f=frame(event);expect(f['pid']==child['pid'] and child['start_ns']<event['received_ns']<child['exit_ns'],'process/frame attribution mismatch')
                if f['event']=='READY':state(f['snapshot'])
                if f['event']=='RESPONSE':
                    expect(event['request_started_ns']<f['start_ns']<f['end_ns']<event['received_ns'],'actual caller-response precedence')
                    state(f['snapshot'])
        if name.startswith('orphan'):
            gate=frame(c['gate']);before=c['before_kill'];after=c['after_kill'];state(before);state(after)
            expect(gate['event']=='GATE' and gate['phase']=='file-fsynced-row-uncommitted' and gate['in_transaction'] is True
                   and gate['local_dependency_rows']==1,'actual post-file/precommit gate absent')
            expect(c['children'][0]['exit']==-9 and c['children'][0]['exit_ns']<after['observation_ns'],'writer not killed/reaped before recovery observation')
            expect(before['dependencies']==after['dependencies']==[] and after['unknown_files']==['z']
                   and after['files']['z']['raw_hex']==Z.encode().hex(),'uncommitted row rollback/surviving durable candidate not observed')
            ready=frame(c['children'][1]['events'][0]);expect(ready['snapshot']['reconstruction_status']=='unresolved-unregistered-material','unknown bytes silently treated as successful empty recovery')
            response=frame(c['removal']);final=c['final'];state(final)
            expect(final['files']==after['files'],'unregistered bytes changed/discarded')
            if c['weak']:
                expect(response['reply']['result']=='COMMITTED' and not final['live'] and final['files'], 'catalog-only mutation did not admit logical removal with surviving material')
                return dict(status='SUPPORTED',observation='counterexample: all catalog rows empty yet actual unregistered candidate survives logical removal; no native exposure claim')
            expect(response['reply']['result']=='DENY' and state(final)==state(after),'directory guard failed to retain unresolved sealed unit unchanged')
            return dict(status='SUPPORTED',observation='actual fsynced unregistered candidate survives SQL rollback/process death; enclosing-directory guard denies removal unchanged')
        if name=='interrupted_disposition':
            original=[frame(e) for e in c['original_steps']];expect([f['reply']['result'] for f in original]==['COMMITTED','COMMITTED','READ'],'actual acceptance/candidate/read positives absent')
            expect(original[2]['reply']['raw_hex']==X.encode().hex(),'actual accepted x differs')
            gate=frame(c['gate']);expect(gate['phase']=='disposition-committed-before-unlink-reply' and not gate['in_transaction'],'disposition did not commit at selected gate')
            expect(c['children'][1]['exit']==-9 and c['children'][1]['exit_ns']<c['after_kill']['observation_ns'],'actual postcommit disposer termination absent')
            after=c['after_kill'];state(after);records={r['name']:r for r in after['dependencies']}
            expect(records['x']['disposed']==1 and records['z']['disposed']==0 and after['files']['x']['raw_hex']==X.encode().hex()
                   and after['files']['z']['raw_hex']==Z.encode().hex(),'post-disposition recovery lost/misclassified surviving bytes')
            expect(state(frame(c['recovered_ready'])['snapshot'])==state(after),'fresh root-only process did not reconstruct actual current disposition')
            steps=[frame(e) for e in c['recovered_steps']]
            expect([f['reply']['result'] for f in steps]==['DENY','READ','DENY','COMMITTED','DENY','COMMITTED','COMMITTED'],'interrupted disposition continuation differs')
            expect(steps[0]['reply']['reason']=='logically-disposed' and 'raw_hex' not in steps[0]['reply'],'old logical x reference still exposes disposed bytes')
            expect(steps[1]['reply']['raw_hex']==Z.encode().hex(),'live candidate z not retained exactly')
            expect(set(steps[3]['snapshot']['files'])=={'z'} and steps[3]['snapshot']['files']['z']==after['files']['z'],'disposed-x cleanup damaged survivor z')
            expect(not c['final']['live'] and not c['final']['objects_directory_exists'] and not c['final']['files'],'final empty unit removal incomplete')
            return dict(status='SUPPORTED',observation='post-disposition-COMMIT/pre-unlink kill leaves no success ACK; fresh sealed management rejects old logical x, retains z, denies premature removal and completes explicit cleanup/disposition/empty removal')
        result=frame(c['removal']);expect(result['reply']['result']=='COMMITTED' and not c['final']['live'] and not c['final']['objects_directory_exists'],'empty positive failed')
        return dict(status='SUPPORTED',observation='independently empty sealed unit removal succeeds')
    except Violation as error:return dict(status='VIOLATION',reason=str(error))
    except (KeyError,TypeError,ValueError,IndexError) as error:return dict(status='INCOMPLETE',reason=str(error))
def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());expect('harness_failure' not in d,'harness failed')
    result={name:check(name,c) for name,c in d['cases'].items()};assert len(result)==4 and all(r['status']=='SUPPORTED' for r in result.values()),result
    missing=copy.deepcopy(d['cases']['orphan_reference']);del missing['after_kill']
    bad=copy.deepcopy(d['cases']['orphan_reference']);del bad['after_kill']['files']['z']
    controls=dict(missing_recovery_observation=check('orphan_reference',missing),contradictory_inventory=check('orphan_reference',bad))
    assert controls['missing_recovery_observation']['status']=='INCOMPLETE' and controls['contradictory_inventory']['status']=='VIOLATION',controls
    for path,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/'+path]);assert hashlib.sha256(raw).hexdigest()==digest
    children=[p for case in d['cases'].values() for p in case['children']];assert len(children)==len({p['pid'] for p in children})==8
    events=[]
    for p in children:
        ready=frame(p['events'][0]);assert ready['source_sha256']==d['source_hashes']['store.py']
        events += [(p['start_ns'],1),(p['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==1
    print(json.dumps(dict(cases=result,controls=controls,owned_children=len(children),maximum_observed_child_concurrency=maximum,source_hashes_verified=True,
                         qualification='flat enclosing-root/all cooperative writers/trusted management and process-loss profile; policy/store evidence, no native confinement/full L6/T13/T23/F3/F4 or power-loss closure'),indent=2,sort_keys=True))
if __name__=='__main__':main()
