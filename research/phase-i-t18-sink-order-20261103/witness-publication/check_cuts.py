#!/usr/bin/env python3
"""Read-only pre-reply death-cut/retained outcome checks; no recovery oracle input."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cuts_check_support',HERE.parent/'sink-witness/check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
expect,need=support.expect,support.need

def cut(case,source_hash):
    try:
        stage=case['stage'];writer=case['writer'];gate=case['gate'];request=case['request']
        need(request['response'] is None and request.get('error'),'missing actual no-response observation')
        need(gate['point']==stage and gate['pid']==writer['pid'] and gate['source_sha256']==source_hash,'gate not bound to stage/process/source')
        expect(json.loads(bytes.fromhex(case['gate_raw_hex']))==gate,'raw gate evidence mismatch')
        expect(writer['start_ns']<writer['ready_ns']<request['start_ns']<gate['monotonic_ns']<writer['exit_ns'],
               'actual process/request/gate/death order')
        expect(gate['monotonic_ns']<request['end_ns']<case['recovery']['start_ns'],'request completion/recovery order')
        expect(writer['exit']==-9,'actual serving process not killed/reaped')
        before=support.journal(case['actual_before_journal']);at=support.journal(case['journal_at_gate'])
        expect(writer['steps'][-1]['response']['status']==201,'prior positive ACK missing')
        expect(writer['steps'][-1]['journal']==case['actual_before_journal'],'before-cut actual ACK journal differs')
        committed=stage!='before_local';remote_published=stage=='witness_published'
        expect(at==before if not committed else at[:-1]==before and at[-1]['event']=='managed_revoked',
               'local durable outcome does not match held cut')
        expect(gate['local_state']['granted'] is (not committed) and gate['local_state']['active'] is (not committed),'gate local eligibility')
        remote=case['witness_at_gate']
        expect(remote['current']['active'] is (not remote_published) and remote['publication']==(2 if remote_published else 1),
               'external publication outcome does not match cut')
        recovery,cold=case['recovery'],case['cold']
        support.session(recovery);support.session(cold)
        expect(recovery['journal_path']==writer['journal_path']==cold['journal_path'],'not same journal path')
        expect(recovery['ready_journal']==case['journal_at_gate'],'recovery input changed from actual surviving journal')
        expect(recovery['ready_status']['granted'] is (not committed) and recovery['ready_status']['active'] is (not committed),'recovery eligibility mismatch')
        expect(not recovery['ready_status']['publication_log'],'recovery used automatic external publication')
        expected_code=409 if committed else 201
        expect(recovery['steps'][0]['response']['status']==expected_code,'actual after-cut current-use outcome')
        expect(cold['ready_journal']==recovery['final_journal'] and cold['ready_status']['effects']==recovery['final_status']['effects'],'second restart loses ACKed effect')
        expect(recovery['ready_status']['effects']==[e for e in before if e['event']=='effect_accepted'],'pre-cut ACK not recovered')
        expect(case['witness']['pid']==remote['pid']==case['witness_status']['pid'] and case['witness']['exit']==-9,'witness identity/reap')
        expect(case['witness']['start_ns']<writer['start_ns'] and cold['exit_ns']<case['witness']['exit_ns'],'witness survival')
        return dict(status='SUPPORTED',caller='no success response',local_revoke_committed=committed,
                    witness_revoke_published=remote_published,after_recovery_status=expected_code)
    except support.Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except support.Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    data=json.loads(Path(sys.argv[1]).read_bytes());key='witness-publication/publication_sink.py'
    results={k:cut(v,data['source_hashes'][key]) for k,v in data['cases'].items()}
    assert all(v['status']=='SUPPORTED' for v in results.values()),results
    positive=data['uninterrupted'];steps=support.session(positive['writer']);revoke=steps['revoke']
    assert revoke['response']['status']==200
    publication=revoke['observed']['publication_log'][-1]
    assert publication['valid'] is True and publication['end_ns']<revoke['end_ns']
    assert positive['witness_status']['current']['active'] is False
    missing_gate=copy.deepcopy(data['cases']['local_committed']);del missing_gate['gate']
    missing_reply=copy.deepcopy(data['cases']['local_committed']);del missing_reply['request']['response']
    incomplete=dict(missing_gate=cut(missing_gate,data['source_hashes'][key]),missing_reply=cut(missing_reply,data['source_hashes'][key]))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[c[k] for c in data['cases'].values() for k in ('writer','recovery','cold','witness')]
    children += [positive['writer'],positive['witness']]
    assert len(children)==len({c['pid'] for c in children})==14
    events=[]
    for c in children:
        assert c['exit']==-9
        events += [(c['start_ns'],1),(c['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    for path,digest in data['source_hashes'].items():assert hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest()==digest
    print(json.dumps(dict(cases=results,uninterrupted='success200 after validated publication',
                          incomplete_controls=incomplete,owned_children=len(children),maximum_observed_child_concurrency=maximum,
                          interpretation='same no-success-response category, three definite local/remote outcomes; no automatic retry inference',
                          qualification='actual process termination/current same journal, not physical power loss or independent review'),indent=2,sort_keys=True))
if __name__=='__main__':main()
