#!/usr/bin/env python3
"""Read-only witness projection evidence and missing-metadata discriminator."""
import copy
import hashlib
import json
from pathlib import Path
import sys

class Incomplete(Exception):pass
class Violation(Exception):pass
def need(v,msg):
    if not v:raise Incomplete(msg)
def expect(v,msg):
    if not v:raise Violation(msg)
def journal(snapshot):
    raw=bytes.fromhex(snapshot['raw_hex'])
    need(snapshot['exists'] and raw.endswith(b'\n'),'missing complete journal')
    need(hashlib.sha256(raw).hexdigest()==snapshot['sha256'],'digest mismatch')
    return [json.loads(line) for line in raw.splitlines()]
def session(value):
    expect(value['start_ns']<value['ready_ns']<value['exit_ns'] and value['exit']==-9,'process order/reap')
    previous=value['ready_ns']
    for step in value['steps']:
        expect(previous<step['start_ns']<step['end_ns']<value['exit_ns'],'HTTP/process precedence')
        previous=step['end_ns']
        rows=journal(step['journal'])
        expect([e for e in rows if e['event']=='effect_accepted']==step['observed']['effects'],'journal/effect mismatch')
        if step['response']['status'] in (200,201):
            expect(any(e['seq']==step['response']['body']['event_seq'] for e in rows),'ACK without event')
    return {s['label']:s for s in value['steps']}
def projection_case(case):
    try:
        writer=case['writer'];recovery=case['recovery'];retained=case['retained'];cold=case['cold']
        w=session(writer);r=session(recovery);t=session(retained);session(cold)
        expect(w['before-positive']['response']['status']==201 and w['revoke']['response']['status']==200,'positive/revoke control')
        expect(t['retained-revoke']['response']['status']==409,'current retained revoke did not deny')
        expect(writer['final_journal']==retained['ready_journal'],'retained journal discontinuity')
        expect(case['rollback']['old_actual_acknowledged']==case['rollback']['restored']==recovery['ready_journal'],
               'rollback/recovery differs from authentic earlier ACKed prefix')
        seq=[w['revoke']['end_ns'],case['revoke_publish']['start_ns'],case['revoke_publish']['end_ns'],
             writer['exit_ns'],retained['start_ns'],retained['exit_ns'],case['rollback']['start_ns'],case['rollback']['end_ns'],
             recovery['start_ns'],recovery['ready_ns'],r['post-revoke-rolled']['start_ns']]
        need(all(type(n) is int for n in seq),'missing management/witness/rollback/send timestamp')
        expect(all(a<b for a,b in zip(seq,seq[1:])),'revoke/witness/recovery/send precedence')
        expect(case['witness_alive_after_all_sink_restarts'] is True,'external witness did not survive rollback')
        witness=case['witness'];status=case['witness_status']
        need(type(witness['pid']) is int and witness['pid']==status['pid'],'witness process identity missing')
        expect(witness['start_ns']<writer['start_ns'] and cold['exit_ns']<witness['exit_ns'] and witness['exit']==-9,'witness lifetime')
        current=status['current']
        expect(current['authority_version']==1 and current['granted'] is current['active'] is False,'witness not actually aware of revoke')
        step=r['post-revoke-rolled'];need(step['observed']['witness_log'],'missing actual sink witness exchange')
        exchange=step['observed']['witness_log'][-1];query=exchange['request'];reply=exchange['response']
        expect(query['candidate']['authority_version']==1 and query['candidate']['granted'] is query['candidate']['active'] is True,
               'local rollback candidate not eligible gen1')
        expect(query['nonce']==reply['nonce'] and exchange['valid'] is True and reply['pid']==witness['pid'],'fresh reply identity mismatch')
        need(any(e['path']=='/check' and e['request']==query and e['response']==reply for e in status['log']),
             'external process did not record actual exchange')
        expect(reply['current']==current and reply['publication']==2,'reply not from published revoked state')
        expect(step['start_ns']<exchange['start_ns']<exchange['end_ns']<step['end_ns'],'query not inside actual submit interval')
        expect(cold['ready_journal']==recovery['final_journal'] and cold['ready_status']['effects']==recovery['final_status']['effects'],
               'ACK/result not retained on actual cold restart')
        profile=case['profile'];accepted=step['response']['status']==201
        has_x=any(e['payload']=='x' for e in step['observed']['effects'])
        expect(accepted==has_x==reply['allowed']==exchange['admitted'],'acceptance/journal/witness disagreement')
        if profile=='generation':expect(accepted,'generation-only negative control failed to discriminate')
        else:expect(not accepted and step['response']['status']==409,'eligibility witness accepted stale local state')
        return dict(status='COUNTEREXAMPLE' if accepted else 'SUPPORTED',
                    observation='live witness knows revoke, generation unchanged; stale x ACKed/retained' if accepted else 'stale eligible tuple denied by actual live witness')
    except Incomplete as error:return dict(status='INCOMPLETE',reason=str(error))
    except Violation as error:return dict(status='VIOLATION',reason=str(error))
    except (KeyError,ValueError,TypeError,IndexError) as error:return dict(status='INCOMPLETE',reason=str(error))
def main():
    data=json.loads(Path(sys.argv[1]).read_bytes())
    cases={k:projection_case(v) for k,v in data['cases'].items()}
    assert cases['generation']['status']=='COUNTEREXAMPLE' and cases['eligibility']['status']=='SUPPORTED',cases
    controls=data['protocol_controls'];s=session(controls['session'])
    assert [s[k]['response']['status'] for k in ('positive','wrong-nonce','positive-after-reset','missing-witness')]==[201,409,201,409]
    wrong=s['wrong-nonce']['observed']['witness_log'][-1]
    assert wrong['response']['allowed'] is True and wrong['valid'] is False and wrong['admitted'] is False
    missing=s['missing-witness']['observed']['witness_log'][-1]
    assert missing['response'] is None and missing['valid'] is False and missing['error']
    assert controls['witness']['exit_ns']<s['missing-witness']['start_ns']
    assert [e['payload'] for e in s['missing-witness']['observed']['effects']]==['protocol-positive','protocol-reset-positive']
    children=[c[k] for c in data['cases'].values() for k in ('writer','retained','recovery','cold','witness')]
    children += [controls['session'],controls['witness']]
    assert len(children)==len({c['pid'] for c in children})==12
    events=[]
    for c in children:
        assert c['exit']==-9
        events += [(c['start_ns'],1),(c['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    no_time=copy.deepcopy(data['cases']['eligibility']);del no_time['revoke_publish']['end_ns']
    no_reply=copy.deepcopy(data['cases']['eligibility']);del no_reply['recovery']['steps'][0]['observed']['witness_log']
    incomplete=dict(missing_publication_ack=projection_case(no_time),missing_witness_exchange=projection_case(no_reply))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    here=Path(__file__).resolve().parent
    for path,expected in data['source_hashes'].items():assert hashlib.sha256((here.parent/path).read_bytes()).hexdigest()==expected
    print(json.dumps(dict(cases=cases,protocol_controls='positive/nonce/reset/missing as predicted',
                          owned_children=len(children),maximum_observed_child_concurrency=maximum,
                          incomplete_controls=incomplete,qualification='selected trusted supervisor/endpoint; coordinator checker, no independent review'),indent=2,sort_keys=True))
if __name__=='__main__':main()
