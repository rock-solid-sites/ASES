#!/usr/bin/env python3
"""Successful published-cut ACK correlation and honest divergence limits."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

class Incomplete(Exception):pass
class Violation(Exception):pass
def need(v,msg):
    if not v:raise Incomplete(msg)
def expect(v,msg):
    if not v:raise Violation(msg)
def rows(snapshot):
    raw=bytes.fromhex(snapshot['raw_hex']);need(snapshot['exists'] and raw.endswith(b'\n'),'missing complete actual journal')
    expect(hashlib.sha256(raw).hexdigest()==snapshot['sha256'],'journal digest mismatch')
    return [json.loads(line) for line in raw.splitlines()]
def same(a,b):return all(a[k]==b[k] for k in ('exists','raw_hex','sha256'))
def session(value):
    expect(value['start_ns']<value['ready_ns']<value['exit_ns'] and value['exit']==-9,'actual serving process lifecycle')
    last=value['ready_ns']
    for step in value['steps']:
        expect(last<step['start_ns']<step['end_ns']<value['exit_ns'],'invocation/response/process precedence')
        last=step['end_ns'];journal=rows(step['journal']);body=step['response']['body']
        expect([e for e in journal if e['event']=='effect_accepted']==step['observed']['effects'],'journal/live effect mismatch')
        if step['response']['status'] in (200,201):
            expect(any(e['seq']==body['event_seq'] for e in journal),'successful ACK has no local persisted event')
            expect(body['published_journal_sha256']==step['journal']['sha256'],'ACK not bound to actual journal')
            publication=next(p for p in reversed(step['observed']['cut_protocol_log']) if p['path']=='/publish')
            expect(publication['valid'] and publication['response']['published'] is True
                   and publication['response']['revision']==body['published_revision'],'ACK publication receipt not validated')
            expect(publication['request']['candidate']['journal_sha256']==step['journal']['sha256']
                   and publication['end_ns']<step['end_ns'],'published bytes/ACK precedence mismatch')
    return {step['label']:step for step in value['steps']}
def check(c):
    try:
        kind=c['kind'];original=c['original'];by=session(original)
        need(by['cut-x']['response']['status']==by['cut-q']['response']['status']==201,'missing actual original x/q ACKs')
        expect(c['init']['status']==200 and c['init']['response']['initialized'] is True,'trusted genesis initialization absent')
        expected=c['after_ack_status']['actual_cut']
        expect(expected['journal_sha256']==c['acknowledged_journal']['sha256']==c['witness_after_ack']['current']['journal_sha256'],
               'acknowledged current cut not actually published')
        need(c['witness_alive'] and c['witness']['pid']==c['witness_status']['pid'],'live witness evidence absent')
        expect(c['witness']['start_ns']<original['start_ns'] and all(p['exit_ns']<c['witness']['exit_ns'] for p in c['children'] if p['pid']!=c['witness']['pid']),
               'witness did not survive all sink processes')
        if kind=='positive':
            by_new=session(c['recovered']);session(c['cold'])
            expect(same(original['final_journal'],c['recovered']['ready_journal']),'positive current journal lineage')
            expect([e['request_id'] for e in c['recovered']['ready_status']['effects']]==['cut-x']
                   and c['recovered']['ready_status']['obligations']=={'q':by['cut-q']['body']['payload']},'positive prior commitments missing at ready')
            expect(by_new['cut-y']['response']['status']==201,'new positive after recovery failed')
            expect([e['request_id'] for e in c['cold']['ready_status']['effects']]==['cut-x','cut-y']
                   and c['cold']['ready_status']['obligations']=={'q':by['cut-q']['body']['payload']},'second recovery lost actual ACKs')
            expect(c['stale_cas']['status']==409 and c['stale_cas']['response']['reason']=='stale-cas','stale publisher control did not discriminate')
            expect(c['witness_status']['current']==c['cold']['ready_status']['actual_cut'],'final published cut/current file mismatch')
            return dict(status='SUPPORTED',observation='actual management/x/q/y ACKs follow validated publication and same-file recovery retains all commitments')
        refusal=c['startup_refusal'];frame=refusal['frame']
        need(frame is not None and frame['ready'] is False and frame['local_parse_complete'] is True,'missing post-parser pre-ready refusal observation')
        expect(json.loads(bytes.fromhex(refusal['startup_raw_hex']))==frame,'startup raw frame mismatch')
        expect(refusal['exit']==1 and frame['reason']=='published-cut-unavailable','refusal not caused by current-cut check')
        proof=frame['witness_observation'];expect(proof['transport_valid'] and not proof['valid'] and proof['response']['allowed'] is False,'actual valid mismatch response absent')
        expect(frame['local_cut']['authority']==proof['response']['current']['authority']
               and frame['local_cut']['journal_sha256']!=proof['response']['current']['journal_sha256'],'not same-authority/different journal cut')
        expect(same(c['before_refusal'],refusal['journal_after']),'startup changed mismatching journal bytes')
        expect(c['witness_status']['revision']==c['witness_after_ack']['revision'] and c['witness_status']['current']==expected,
               'startup/failure auto-published possibly stale state')
        if kind=='rollback':
            expect(same(c['controlled_fault']['after'],c['prefix']) and c['original_parser_control']['effects']==[],'rollback not genuine management prefix')
            return dict(status='SUPPORTED',observation='authentic older same-authority cut rejected before ready, current witness unchanged')
        if kind=='forged_same_sequence':
            before=rows(c['acknowledged_journal']);after=rows(c['controlled_fault']['after'])
            expect(len(bytes.fromhex(c['acknowledged_journal']['raw_hex']))==len(bytes.fromhex(c['controlled_fault']['after']['raw_hex']))
                   and [r['seq'] for r in before]==[r['seq'] for r in after],'forged control changed byte length/sequence')
            expect(c['original_parser_control']['effects'][0]['payload']=='persisted cut z / μ','original strict parser did not accept coherent mutation')
            return dict(status='SUPPORTED',observation='coherent self-hashed same-authority/seq/length payload mutation rejected by published cut before ready')
        z=by['local-unACKed-z'];later=by['blocked-later']
        expect(z['response']['status']==503 and z['response']['body']['local_control_committed'] is True,'failed publication hid local definite commit')
        expect(any(r.get('request_id')=='local-unACKed-z' for r in rows(c['after_local_commit'])),'unACKed local record not retained')
        expect(later['response']['status']==503 and later['response']['body']['local_control_committed'] is False
               and same(c['after_local_commit'],c['after_later']),'later operation appended after divergence')
        expect(any(e['path']=='/publish' and e['status']==503 for e in c['witness_status']['log']),'actual rejected witness publication absent')
        expect(any(e['request_id']=='local-unACKed-z' for e in c['original_parser_control']['effects']),'cold refusal discarded unACKed irreversible local record')
        return dict(status='SUPPORTED',observation='publication rejection preserves local unACKed record, blocks later append/startup without pretending two-store atomicity')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError,StopIteration) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());result={k:check(v) for k,v in d['cases'].items()}
    assert all(v['status']=='SUPPORTED' for v in result.values()),result
    no_ack=copy.deepcopy(d['cases']['positive']);del next(s for s in no_ack['original']['steps'] if s['label']=='cut-x')['response']
    no_refusal=copy.deepcopy(d['cases']['rollback']);del no_refusal['startup_refusal']
    incomplete=dict(missing_success_ack=check(no_ack),missing_startup_observation=check(no_refusal));assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[p for c in d['cases'].values() for p in c['children']];assert len(children)==len({p['pid'] for p in children})==13
    events=[]
    for p in children:
        assert p['exit'] in (-9,1)
        events += [(p['start_ns'],1),(p['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    for path,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-t18-sink-order-20261103/'+path]);assert hashlib.sha256(raw).hexdigest()==digest
    print(json.dumps(dict(cases=result,incomplete_controls=incomplete,owned_children=len(children),maximum_observed_child_concurrency=maximum,
                          source_hashes_verified=True,qualification='trusted live published-cut witness/current root/serialized writer; divergence availability unresolved, no power loss/nonrollback establishment or generic C7/F4 proof'),indent=2,sort_keys=True))
if __name__=='__main__':main()
