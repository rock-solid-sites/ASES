#!/usr/bin/env python3
"""Read-only publication/management ACK evidence, including partial outcomes."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('publication_check_support',HERE.parent/'sink-witness/check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
need,expect=support.need,support.expect

def success(case):
    try:
        writer,recovery,cold=case['writer'],case['recovery'],case['cold']
        w=support.session(writer);r=support.session(recovery);support.session(cold)
        expect(w['before-positive']['response']['status']==201 and w['revoke']['response']['status']==200,'positive/revoke ACK missing')
        expect(writer['exit_ns']<case['rollback']['start_ns']<case['rollback']['end_ns']<recovery['start_ns'],'rollback lifecycle')
        expect(case['older_actual_acknowledged']==case['rollback']['after']==recovery['ready_journal'],'authentic prior prefix mismatch')
        expect(w['revoke']['end_ns']<r['post-revoke-rolled']['start_ns'],'send before management ACK')
        expect(writer['final_status']['granted'] is writer['final_status']['active'] is False,'local revoke not committed')
        expect(recovery['ready_status']['granted'] is recovery['ready_status']['active'] is True,'rollback did not restore old eligibility')
        exchange=r['post-revoke-rolled']['observed']['witness_log'][-1]
        expect(exchange['valid'] is True and exchange['response']['pid']==case['witness']['pid'],'witness exchange identity')
        expect(exchange['request']['nonce']==exchange['response']['nonce'],'fresh check nonce absent')
        has_x=any(e['payload']=='x' for e in recovery['final_status']['effects'])
        if case['barrier']:
            publication=w['revoke']['observed']['publication_log'][-1]
            expect(publication['valid'] is True and w['revoke']['start_ns']<publication['start_ns']<publication['end_ns']<w['revoke']['end_ns'],
                   'publication not validated inside revoke before ACK')
            expect(publication['response']==w['revoke']['response']['body']['witness_publication'],'ACK publication identity mismatch')
            expect(any(e['path']=='/publish' and e['request']==publication['request'] and e['response']==publication['response']
                       for e in case['witness_status']['log']),'external witness publication not observed')
            expect(case['witness_after_revoke']['current']['active'] is False and exchange['response']['current']['active'] is False,'witness lacks revoked state')
            expect(r['post-revoke-rolled']['response']['status']==409 and not has_x,'barrier admitted rolled eligibility')
            expect(not recovery['ready_status']['publication_log'],'startup republished possibly rolled state')
        else:
            expect(case['witness_after_revoke']['current']['active'] is True and exchange['response']['current']['active'] is True,
                   'delayed witness not actually stale')
            expect(r['post-revoke-rolled']['response']['status']==201 and has_x,'delayed update negative control did not discriminate')
            expect(r['post-revoke-rolled']['end_ns']<case['late_publication']['start_ns']<case['late_publication']['end_ns']
                   <r['after-late-publication']['start_ns'],'late publication order')
            expect(r['after-late-publication']['response']['status']==409,'late update did not deny future use')
        expect(recovery['final_journal']==cold['ready_journal'] and recovery['final_status']['effects']==cold['ready_status']['effects'],
               'ACKed accepted effects not cold-retained')
        return dict(status='SUPPORTED' if case['barrier'] else 'COUNTEREXAMPLE',scope='selected revoke publication/ACK ordering')
    except support.Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except support.Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def failure(case):
    writer=case['writer'];w=support.session(writer);support.session(case['cold'])
    step=w['revoke'];reply=step['response']['body']
    assert step['response']['status']==503 and reply['local_control_committed'] is True
    event=next(e for e in support.journal(step['journal']) if e['seq']==reply['local_event_seq'])
    assert event['event']=='managed_revoked' and step['observed']['granted'] is step['observed']['active'] is False
    publication=step['observed']['publication_log'][-1]
    assert publication['valid'] is False
    assert w['after-failed-revoke']['response']['status']==409
    assert case['cold']['ready_journal']==writer['final_journal']
    assert case['cold']['ready_status']['granted'] is case['cold']['ready_status']['active'] is False
    assert case['cold']['steps'][0]['response']['status']==409
    fault=case['fault']
    if fault=='reject':
        assert publication['response_status']==503 and case['witness_after']['current']['active'] is True
        result='local durable revoke; witness rejected without update; no success revoke ACK'
    elif fault=='wrong_nonce':
        assert publication['response_status']==200 and publication['response']['nonce']!=publication['request']['nonce']
        assert case['witness_after']['current']['active'] is False
        result='local and witness updated; unusable nonce response; no success revoke ACK'
    else:
        assert publication['response'] is None and publication['error'] and case['witness']['exit_ns']<step['start_ns']
        result='local durable revoke; witness already killed/reaped; no success revoke ACK'
    return result

def main():
    data=json.loads(Path(sys.argv[1]).read_bytes())
    cases={k:success(v) for k,v in data['cases'].items()}
    assert cases['delayed']['status']=='COUNTEREXAMPLE' and cases['barrier']['status']=='SUPPORTED',cases
    failures={k:failure(v) for k,v in data['publication_failures'].items()}
    no_publication=copy.deepcopy(data['cases']['barrier']);del no_publication['writer']['steps'][-1]['observed']['publication_log']
    no_journal=copy.deepcopy(data['cases']['barrier']);del no_journal['writer']['steps'][-1]['journal']
    incomplete=dict(missing_publication=success(no_publication),missing_local_revoke_bytes=success(no_journal))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[c[k] for c in data['cases'].values() for k in ('writer','recovery','cold','witness')]
    children += [c[k] for c in data['publication_failures'].values() for k in ('writer','cold','witness')]
    assert len(children)==len({c['pid'] for c in children})==17
    events=[]
    for c in children:
        assert c['exit']==-9
        events += [(c['start_ns'],1),(c['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert maximum==2 and active==0
    for path,digest in data['source_hashes'].items():assert hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest()==digest
    print(json.dumps(dict(cases=cases,publication_failures=failures,incomplete_controls=incomplete,
                          owned_children=len(children),maximum_observed_child_concurrency=maximum,
                          qualification='selected trusted-manager revoke path only; no independent barrier review'),indent=2,sort_keys=True))
if __name__=='__main__':main()
