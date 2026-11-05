#!/usr/bin/env python3
"""Old/new whole move expectation independent of manager implementation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
PAYLOAD='actual selected D write / μ';X=b'accepted-post-move-content\x00\n'
class Violation(Exception):pass
def expect(v,why):
    if not v:raise Violation(why)
def frame(e):
    expect(json.loads(e['raw_line'])==e['frame'],'wire/frame contradiction');return e['frame']
def observed(o):
    for f in o['files'].values():expect(hashlib.sha256(bytes.fromhex(f['raw_hex'])).hexdigest()==f['sha256'],'actual file hash mismatch')
    expect(json.loads(bytes.fromhex(o['files'][o['selected']]['raw_hex']))==o['state'],'selected raw record differs from reported state')
    expect(bytes.fromhex(o['files']['CURRENT']['raw_hex']).decode().strip()==o['selected'],'actual selector differs')
    expect(len(o['contents'])==1 and o['contents'][0]['raw_hex']==X.hex() and o['contents'][0]['sha256']==hashlib.sha256(X).hexdigest(),'accepted fixture bytes lost/changed')
    units=o['state']['work_units'];expect(set(units)=={'P','C','Q','D'} and units['D']['parent']=='C' and units['D']['depends_on']==['C'],'whole dependent structure changed')
    return units
def check(c):
    try:
        kind=c['kind'];before=c['before'];after=c['after_process'];observed(before);units=observed(after);cold=frame(c['cold_ready'])
        expect(c['children'][0]['exit_ns']<after['ns']<c['children'][1]['start_ns'],'post-reap/root-only cold ordering absent')
        expect(cold['snapshot']['state']==after['state'] and cold['snapshot']['selected']==after['selected'],'fresh process did not select actual whole current state')
        expect(all(u['sealed'] and not u['active'] for u in units.values()) and after['state']['current_ingress'] is None,'move cut not sealed/inactive')
        old=kind in ('before_record','after_record','write-positive');new=kind in ('after_selector','uninterrupted')
        if old:expect(after['state']==before['state'],'pre-selector cut/positive did not retain exact old record')
        if new:
            expect(units['C']['parent']=='Q' and units['C']['latent_ceiling']==units['D']['latent_ceiling']==['read'],'new whole move missing retained descendant ceilings')
            expect(after['state']['events'][-1]['op']=='authorized_sealed_whole_move','new state not original authorized move')
        if kind in ('before_record','after_record','after_selector','split-mutant'):
            gate=frame(c['move_observation']);expect(gate['event']=='GATE' and c['children'][0]['exit']==-9,'actual retained gate/process kill absent')
            expect(c['children'][0]['stdout_remainder']=='' and len(c['children'][0]['events'])==2,'unexpected output/response after gated pending move')
        if kind=='after_record':
            expect('record-000002.json' in after['files'] and after['selected']=='record-000001.json','unselected published record not actually present/ignored')
        if kind=='before_record':expect('record-000002.json.tmp' in after['files'] and after['selected']=='record-000001.json','prepared full-record temp not actually present/ignored')
        if kind=='uninterrupted':
            move=frame(c['move_observation']);expect(move['result']['reply']['result']=='COMMITTED' and json.loads(bytes.fromhex(move['result']['manager_wire_hex']))==move['result']['reply'],'original move actual manager ACK absent')
        activation=frame(c['activation']);write=frame(c['write']);observed(write['snapshot']);observed(c['final'])
        expect(activation['result']['reply']['result']=='COMMITTED' and activation['end_ns']<write['start_ns'],'activation not separate current authorized event')
        allowed=kind in ('split-mutant','write-positive')
        expect(write['result']['reply']['allowed']==allowed and (c['final']['effect_raw_hex']==PAYLOAD.encode().hex() if allowed else c['final']['effect_raw_hex'] is None),'literal policy/effect outcome mismatch')
        expect(after['permissions']['D']==(['read','write'] if allowed else ['read']),'literal permissions differ')
        if kind=='split-mutant':
            expect(units['C']['parent']=='Q' and 'latent_ceiling' not in units['C'] and 'latent_ceiling' not in units['D'],'split mutation was not a selected invariant-valid half move')
            return dict(status='SUPPORTED',observation='split-publication control selects sealed graph-valid half move; cold activation permits concrete forbidden D-write')
        return dict(status='SUPPORTED',observation='actual old/new whole move cold state and retained bytes; write '+('positive' if allowed else 'denied after separate activation'))
    except Violation as error:return dict(status='VIOLATION',reason=str(error))
    except (KeyError,TypeError,ValueError,IndexError) as error:return dict(status='INCOMPLETE',reason=str(error))
def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());expect('harness_failure' not in d,'harness failed');result={name:check(c) for name,c in d['cases'].items()}
    assert len(result)==6 and all(v['status']=='SUPPORTED' for v in result.values()),result
    missing=copy.deepcopy(d['cases']['after_selector']);del missing['after_process']
    bad=copy.deepcopy(d['cases']['before_record']);bad['after_process']['state']['work_units']['C']['parent']='Q'
    controls=dict(missing_postreap_state=check(missing),contradictory_selected_record=check(bad));assert controls['missing_postreap_state']['status']=='INCOMPLETE' and controls['contradictory_selected_record']['status']=='VIOLATION',controls
    children=[p for c in d['cases'].values() for p in c['children']];assert len(children)==len({p['pid'] for p in children})==12
    events=[]
    for child in children:
        expect(child['start_ns']<child['ready_ns']<child['exit_ns']<=child['stdout_eof_ns'] and not child['stdout_remainder'] and not child['stderr'],'child/EOF lifecycle evidence inconsistent')
        ready=frame(child['events'][0]);assert ready['source_sha256']==d['source_hashes']['l5/move-cuts/worker.py'] and ready['l5_source_sha256']==d['source_hashes']['l5/l5_integrated.py']
        for event in child['events']:
            f=frame(event);expect(f['pid']==child['pid'] and child['start_ns']<event['received_ns']<child['exit_ns'],'process frame attribution mismatch')
        events += [(child['start_ns'],1),(child['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==1
    for path,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-protected-work-unit-f3/lifecycle/'+path]);assert hashlib.sha256(raw).hexdigest()==digest
    print(json.dumps(dict(cases=result,controls=controls,owned_children=12,maximum_observed_child_concurrency=maximum,source_hashes_verified=True,
                         qualification='synthetic existing accepted fixture/trusted single-holder live filesystem; process loss only, no fsync/native confinement/full T12/F3/F4 or power-loss claim'),indent=2,sort_keys=True))
if __name__=='__main__':main()
