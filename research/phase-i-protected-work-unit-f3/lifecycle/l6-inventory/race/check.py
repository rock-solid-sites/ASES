#!/usr/bin/env python3
"""Check actual phantom schedule and the common write-boundary premise."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('inventory_race_check_support',HERE.parent/'check.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
expect=p.expect;frame=p.frame;state=p.state
Z='new candidate during removal scan / μ'
def check(c):
    try:
        kind=c['kind'];removal=frame(c['removal']);final=c['final_before_exit'];state(final)
        for child in c['children']:
            expect(child['start_ns']<child['exit_ns'] and child['exit'] in (0,1),'child lifecycle contradiction')
            if 'events' not in child:continue
            expect(child['ready_ns']<child['exit_ns']<=child['stdout_eof_ns'] and child['stdout_remainder']=='','EOF evidence missing or unexpected unparsed output')
            for event in child['events']:
                f=frame(event);expect(f['pid']==child['pid'] and child['start_ns']<event['received_ns']<child['exit_ns'],'process attribution mismatch')
        if kind=='creator-first':
            created=frame(c['creator_ack']);read=frame(c['read'])
            expect(created['reply']['result']=='COMMITTED' and created['end_ns']<removal['start_ns'],'creator did not actually commit first')
            expect(removal['reply']['result']=='DENY' and final['live'] and read['reply']['raw_hex']==Z.encode().hex(),'fresh complete inventory failed to retain prior candidate')
            return dict(status='SUPPORTED',observation='creator actual COMMIT/ACK first; ordinary guarded removal denies and exact candidate remains readable by management')
        gate=frame(c['gate']);created=frame(c['creator_attempt']);overlap=c['at_overlap'];state(overlap)
        expect(gate['ns']<created['start_ns']<created['end_ns']<removal['end_ns'],'actual gated overlap precedence absent')
        if kind=='guarded':
            expect(gate['phase']=='inventory-scanned-under-write-lock' and gate['in_transaction'] is True,'original write guard not held across scan')
            error=created['reply'];expect(error['result']=='DENY' and error['reason']=='native-sql-error' and error['sqlite_errorcode']==5
                   and error['sqlite_errorname']=='SQLITE_BUSY' and error['in_transaction'] is False,'not actual pre-file SQLite competition')
            expect(overlap['live'] and not overlap['files'] and not overlap['dependencies'],'overlapping creator wrote file/catalog before write lock')
            later=frame(c['later_creator']);expect(removal['reply']['result']=='COMMITTED' and later['reply']==dict(result='DENY',reason='unit-removed'), 'removal/later creator result wrong')
            expect(not final['live'] and not final['objects_directory_exists'] and not final['files'],'guarded removal stranded data')
            cold=frame(c['cold']['events'][0]);expect(state(cold['snapshot'])==state(final),'cold management did not retain actual empty tombstone')
            return dict(status='SUPPORTED',observation='held common write transaction yields actual pre-file SQLITE_BUSY; empty removal succeeds, later same creator denies removed unit, cold tombstone unchanged')
        expect(gate['phase']=='inventory-empty-before-write-lock' and gate['in_transaction'] is False,'detached scan did not release write boundary')
        expect(created['reply']['result']=='COMMITTED' and overlap['live'] and overlap['files']['z']['raw_hex']==Z.encode().hex()
               and overlap['dependencies'][0]['disposed']==0,'intervening actual candidate acceptance/bytes absent')
        expect(removal['reply']['result']=='COMMITTED' and not final['live'] and final['files']==overlap['files'] and final['dependencies']==overlap['dependencies'],
               'detached logical-removal counterexample not observed')
        cold=c['cold_refusal'];expect(cold['exit']==1 and json.loads(cold['stdout'])==cold['frame'] and cold['frame']['event']=='REFUSED'
               and cold['frame']['reason']=='removed-unit-has-surviving-material' and state(cold['snapshot'])==state(final),'inconsistent cold material not refused unchanged')
        return dict(status='SUPPORTED',observation='detached empty scan followed by actual creator ACK permits stale logical removal with live dependent; cold management refuses without discarding bytes')
    except p.Violation as error:return dict(status='VIOLATION',reason=str(error))
    except (KeyError,TypeError,ValueError,IndexError) as error:return dict(status='INCOMPLETE',reason=str(error))
def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());expect('harness_failure' not in d,'harness failed');result={name:check(c) for name,c in d['cases'].items()}
    assert len(result)==3 and all(r['status']=='SUPPORTED' for r in result.values()),result
    missing=copy.deepcopy(d['cases']['guarded']);del missing['creator_attempt']
    bad=copy.deepcopy(d['cases']['guarded']);bad['creator_attempt']['frame']['reply']['sqlite_errorcode']=0
    controls=dict(missing_creator_observation=check(missing),contradictory_wire=check(bad));assert controls['missing_creator_observation']['status']=='INCOMPLETE' and controls['contradictory_wire']['status']=='VIOLATION',controls
    children=[c for case in d['cases'].values() for c in case['children']];assert len(children)==len({c['pid'] for c in children})==8
    events=[]
    for child in children:
        events += [(child['start_ns'],1),(child['exit_ns'],-1)]
        if 'events' in child:
            ready=frame(child['events'][0]);assert ready['source_sha256']==d['source_hashes']['race/race_store.py'] and ready['base_source_sha256']==d['source_hashes']['store.py']
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    for path,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/'+path]);assert hashlib.sha256(raw).hexdigest()==digest
    print(json.dumps(dict(cases=result,controls=controls,owned_children=len(children),maximum_observed_child_concurrency=maximum,source_hashes_verified=True,
                         qualification='selected flat-root/cooperative creators/SQLite serialization; logical store policy, not native confinement/full T12/T15/L6/F3/F4 or power-loss guarantee'),indent=2,sort_keys=True))
if __name__=='__main__':main()
