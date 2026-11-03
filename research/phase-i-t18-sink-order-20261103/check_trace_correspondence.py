#!/usr/bin/env python3
"""Read-only correspondence for recorded T18/F4 cases, not a fixture executor."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = ROOT / 'docs/architecture/core-substrate/fixtures-f2/fixtures.json'
VERIFY = ROOT / 'docs/architecture/core-substrate/Phase-I-Verification.md'
CLOSURE = ROOT / 'docs/architecture/core-substrate/Phase-I-Closure.md'
FIXED_F2 = '5fb690d4ba7544a4a7eb5fce9ca1e54485543d64'
SINK_SOURCE = 'b631bfae01faff1f32a8f81993386cdc3a36eb63'

class Incomplete(Exception): pass
class Violation(Exception): pass


def need(value, message):
    if not value: raise Incomplete(message)


def expect(value, message):
    if not value: raise Violation(message)


def one(events, kind, request_id=None):
    found = [e for e in events if e.get('event') == kind and
             (request_id is None or e.get('request_id') == request_id)]
    need(len(found) == 1, f'missing/ambiguous event: {kind} {request_id}')
    return found[0]


def reply(scenario, key, code, outcome):
    value = scenario.get(key)
    need(isinstance(value,list) and len(value)==2 and isinstance(value[1],dict), f'missing response {key}')
    expect(value[0] == code and value[1].get('outcome') == outcome, f'unexpected response {key}')
    return value[1]


def baseline(scenario):
    status = scenario.get('status'); need(isinstance(status,dict),'missing status')
    events = status.get('events'); effects = status.get('effects'); journal = scenario.get('journal')
    need(isinstance(events,list) and isinstance(effects,list) and isinstance(journal,list), 'missing event/effect/journal list')
    need(all(isinstance(e,dict) and type(e.get('seq')) is int for e in events),'malformed events')
    need([e['seq'] for e in events] == list(range(1,len(events)+1)), 'missing, unordered or duplicate event')
    try: persisted = [json.loads(line) for line in journal]
    except (ValueError, TypeError): raise Incomplete('malformed recorded journal')
    need(all(isinstance(e,dict) for e in persisted),'malformed journal object')
    expected = [e for e in events if e.get('event') in ('effect_accepted','obligation_committed','authority_replaced')]
    need(persisted == expected,'journal/event correspondence incomplete')
    need(effects == [e for e in events if e.get('event') == 'effect_accepted'], 'effects/event correspondence incomplete')
    return events


def ordered_check(record, mode):
    try:
        scenario = record['scenarios'][mode]
        events = baseline(scenario)
        rep = one(events,'authority_replaced')
        need(all(k in rep for k in ('previous_version','current_version')),'missing replacement versions')
        expect((rep['previous_version'],rep['current_version']) == (1,2),'wrong replacement transition')
        reply(scenario,'authority_replacement',200,'replaced')
        if mode == 'sink_ordered':
            held = one(events,'request_held','stale-v1')
            denied = one(events,'sink_rejected','stale-v1')
            need(all(k in denied for k in ('presented_version','current_version')),'missing denial versions')
            expect(held['seq'] < rep['seq'] < denied['seq'], 'stale request was not held before replacement and rejected after')
            expect((denied['presented_version'],denied['current_version']) == (1,2),'wrong stale/current versions')
            reply(scenario,'delayed_old_v1',409,'rejected')
            expect(not any(e.get('event')=='effect_accepted' and e.get('request_id')=='stale-v1' for e in events),'stale effect accepted')
            old = one(events,'effect_accepted','live-v1'); new = one(events,'effect_accepted','live-v2')
            need(all('presented_version' in e and 'accepted_under_version' in e for e in (old,new)), 'missing accepted versions')
            expect(old['presented_version']==old['accepted_under_version']==1 and new['presented_version']==new['accepted_under_version']==2,'current positive version mismatch')
            expect(old['seq'] < rep['seq'] < new['seq'],'positive effect ordering mismatch')
            expect(reply(scenario,'live_v1',201,'accepted').get('event_seq') == old['seq'],'old reply mismatch')
            expect(reply(scenario,'new_current_v2',201,'accepted').get('event_seq') == new['seq'],'new reply mismatch')
            return {'status':'SUPPORTED_ANALOG', 'reason':'held old request rejected after replacement; current requests accepted',
                    'evidence_seq':{'held':held['seq'],'replacement':rep['seq'],'rejected':denied['seq']},
                    'f2_fixture_status':'prepared-only',
                    'unresolved':'request was initiated before replacement, while F2 sink_send follows revoke; replacement is not automatically equivalent to that revoke'}
        held = one(events,'request_held','stale-v1-mutant')
        pre = one(events,'detached_permission_read','stale-v1-mutant')
        accepted = one(events,'effect_accepted','stale-v1-mutant')
        need(all(k in pre for k in ('allowed','presented_version','observed_version')) and
             all(k in accepted for k in ('presented_version','accepted_under_version')),'missing mutation metadata')
        expect(pre['seq'] < held['seq'] < rep['seq'] < accepted['seq'],'detached schedule mismatch')
        expect(pre['allowed'] is True and pre['presented_version']==pre['observed_version']==1 and
               accepted['presented_version']==1 and accepted['accepted_under_version']==2,'stale mutation version mismatch')
        expect(reply(scenario,'delayed_old_v1',201,'accepted').get('event_seq')==accepted['seq'],'mutant acknowledgement mismatch')
        return {'status':'VIOLATION', 'reason':'detached old authority check accepted stale request after replacement',
                'evidence_seq':{'old_check':pre['seq'],'replacement':rep['seq'],'stale_accept':accepted['seq']}}
    except (KeyError,TypeError,Incomplete) as exc:
        return {'status':'INCOMPLETE','reason':str(exc)}
    except Violation as exc:
        return {'status':'VIOLATION','reason':str(exc)}


def exact_check(record):
    try:
        s=record['scenarios']['sink_ordered']; events=baseline(s)
        commit=one(events,'obligation_committed'); rep=one(events,'authority_replaced')
        deliver=one(events,'effect_accepted','obligation:q-1')
        need(all(k in commit for k in ('obligation_id','payload','payload_sha256','committed_under_version')) and
             all(k in deliver for k in ('obligation_id','payload','payload_sha256','check_mode','accepted_under_version')),'missing obligation metadata')
        payload_hash=hashlib.sha256(commit['payload'].encode()).hexdigest()
        expect(commit['seq']<rep['seq']<deliver['seq'],'obligation order mismatch')
        expect(commit['obligation_id']==deliver['obligation_id']=='q-1' and commit['payload']==deliver['payload'] and
               commit['payload_sha256']==deliver['payload_sha256']==payload_hash,'obligation payload/identity mismatch')
        expect(commit['committed_under_version']==1 and deliver['accepted_under_version']==2 and
               deliver['check_mode']=='committed-exact-obligation','obligation profile/version mismatch')
        expect(reply(s,'obligation_commit_v1',201,'committed').get('event_seq')==commit['seq'],'obligation commit reply mismatch')
        expect(reply(s,'exact_obligation_after_replacement',201,'accepted').get('event_seq')==deliver['seq'],'obligation delivery reply mismatch')
        return {'status':'SUPPORTED_ANALOG','reason':'matching exact committed obligation delivered after replacement',
                'evidence_seq':{'commit':commit['seq'],'replacement':rep['seq'],'accept':deliver['seq']},
                'unresolved':'client-send event not separately logged; profile-specific analogy, not use-current authorization'}
    except (KeyError,TypeError,Incomplete) as exc: return {'status':'INCOMPLETE','reason':str(exc)}
    except Violation as exc: return {'status':'VIOLATION','reason':str(exc)}


def f4_check(record, name):
    try:
        s=record['scenarios'][name]
        need(all(k in s for k in ('client_observation','client_process_returncode','sink_process_returncode',
                                 'cold_recovery_process_returncode','recovered','journal_raw_hex','journal_sha256')),'missing F4 observation')
        try: raw=bytes.fromhex(s['journal_raw_hex'])
        except (ValueError,TypeError): raise Incomplete('invalid journal hex')
        need(hashlib.sha256(raw).hexdigest()==s['journal_sha256'],'journal hash mismatch')
        need(not raw or raw.endswith(b'\n'),'truncated journal framing')
        try: events=[json.loads(x) for x in raw.splitlines()]
        except (ValueError,UnicodeError): raise Incomplete('malformed journal record')
        need(all(isinstance(e,dict) for e in events),'malformed journal object')
        need([e.get('seq') for e in events]==list(range(1,len(events)+1)),'journal sequence missing')
        recovered=s['recovered']; need(isinstance(recovered,dict) and recovered.get('ok') is True and
                                        isinstance(recovered.get('effects'),list),'cold reader incomplete')
        need(s['cold_recovery_process_returncode']==0 and s['client_process_returncode']==0 and s['sink_process_returncode']==-9,
             'missing required process/recovery evidence')
        need(recovered.get('record_count')==len(events) and recovered.get('journal_bytes')==len(raw),'cold journal summary mismatch')
        effects=[]
        for e in events:
            need(e.get('event')=='effect_accepted' and all(k in e for k in ('payload','payload_utf8_hex','payload_sha256','request_id')),'missing effect fields')
            try: payload=bytes.fromhex(e['payload_utf8_hex'])
            except (ValueError,TypeError): raise Incomplete('invalid payload bytes')
            need(payload == e['payload'].encode() and hashlib.sha256(payload).hexdigest()==e['payload_sha256'],'payload bytes/hash mismatch')
            effects.append({'seq':e['seq'],'request_id':e['request_id'],'payload_utf8_hex':payload.hex(),
                            'payload_sha256':e['payload_sha256'],'payload_base64':base64.b64encode(payload).decode()})
        need(recovered['effects']==effects,'independent recovery differs from raw journal')
        expected_hash=record.get('payload_reference_sha256'); need(isinstance(expected_hash,str),'missing expected payload hash')
        need(all(e['request_id']=='effect-'+name and e['payload_sha256']==expected_hash for e in effects),'wrong effect identity or payload')
        client=s['client_observation']; need(isinstance(client,dict) and 'http_status' in client,'missing client observation')
        status=client['http_status']
        if status == 201:
            need(isinstance(client.get('body'),dict) and client['body'].get('outcome')=='accepted','malformed ACK')
            if not effects:
                return {'status':'VIOLATION','reason':'success ACK without a recoverable matching effect', 'effects':0,
                        'limitation':'empty and missing journal are indistinguishable in recorded runner'}
            need(len(effects)==1 and client['body'].get('event_seq')==effects[0]['seq'],'ACK/effect sequence mismatch')
            return {'status':'SUPPORTED_ANALOG','reason':'success reply and one exact recovered effect', 'effects':1,
                    'limitation':'gate events and fsync timing are not retained in raw output; process death only'}
        need(status is None and isinstance(client.get('error'),str) and client['error'],'unrecognized client outcome')
        if len(effects)==1:
            return {'status':'UNKNOWN_CALLER_COMMITTED_EFFECT','reason':'no reply; independent reader recovered one exact effect',
                    'limitation':'no retry recorded; F2 power-loss case not reproduced'}
        need(len(effects)==0,'unexpected effect count')
        return {'status':'UNKNOWN_CALLER_NO_RECOVERED_EFFECT','reason':'no reply and reader reports zero effects; not a denial',
                'limitation':'empty and missing journal indistinguishable; gate event not retained'}
    except (KeyError,TypeError,Incomplete) as exc: return {'status':'INCOMPLETE','reason':str(exc)}
    except Violation as exc: return {'status':'VIOLATION','reason':str(exc)}


def truncated_control(record):
    try:
        s=record['scenarios']['truncated_record_control']
        raw=bytes.fromhex(s['mutated_journal_raw_hex'])
        need(hashlib.sha256(raw).hexdigest()==s['mutated_journal_sha256'],'truncated hash mismatch')
        need(raw and not raw.endswith(b'\n'),'truncation evidence absent')
        r=s['recovered']; need(s['cold_recovery_process_returncode']==2 and r.get('ok') is False and
                               isinstance(r.get('error'),str) and 'truncated' in r['error'] and 'effects' not in r,
                               'reader refusal evidence absent')
        return {'status':'INCOMPLETE','reason':'fresh reader refused truncated journal; no empty successful recovery'}
    except (KeyError,TypeError,ValueError,Incomplete) as exc: return {'status':'INCOMPLETE','reason':str(exc)}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    fixtures=json.loads(FIXTURE.read_text())
    by_id={f['id']:f for f in fixtures['fixtures']}
    use=by_id['T18-use-current-sink-order-after-revocation']
    exact=by_id['T18-exact-obligation-delivery-after-replacement']
    t07=by_id['T07-acknowledged-commit-survives-crash-lost-reply']
    assert use['status']=='prepared-only' and use['expected_observation']['sink']=='rejected'
    assert [e['ev'] for e in use['events']][:2]==['revoke','sink_send']
    assert exact['expected_observation']['sink']=='accepted'
    assert any(e.get('power_loss') is True for e in t07['events'])
    recorded=json.loads((HERE/'results.json').read_text())
    f4=json.loads((HERE/'F4-results.json').read_text())
    out={'ordered':ordered_check(recorded,'sink_ordered'), 'exact_obligation':exact_check(recorded),
         'detached_mutant':ordered_check(recorded,'detached_check_mutation'),
         'f4':{n:f4_check(f4,n) for n in ('uninterrupted','preaccept','accepted_before_ack','early_ack_mutant')},
         'recorded_truncated_control':truncated_control(f4)}
    missing=copy.deepcopy(recorded); missing['scenarios']['sink_ordered']['status']['events'].pop(2)
    truncated=copy.deepcopy(f4); raw=bytes.fromhex(truncated['scenarios']['uninterrupted']['journal_raw_hex'])[:-1]
    truncated['scenarios']['uninterrupted']['journal_raw_hex']=raw.hex()
    truncated['scenarios']['uninterrupted']['journal_sha256']=hashlib.sha256(raw).hexdigest()
    malformed=copy.deepcopy(f4); bad=b'{not-json}\n'
    malformed['scenarios']['uninterrupted']['journal_raw_hex']=bad.hex()
    malformed['scenarios']['uninterrupted']['journal_sha256']=hashlib.sha256(bad).hexdigest()
    omitted=copy.deepcopy(f4); del omitted['scenarios']['accepted_before_ack']['client_observation']
    absent=copy.deepcopy(recorded); del absent['scenarios']['sink_ordered']
    out['corruption_controls']={'missing_event':ordered_check(missing,'sink_ordered'),
                                'truncated_journal':f4_check(truncated,'uninterrupted'),
                                'malformed_journal':f4_check(malformed,'uninterrupted'),
                                'missing_client_observation':f4_check(omitted,'accepted_before_ack'),
                                'missing_scenario':ordered_check(absent,'sink_ordered')}
    assert out['ordered']['status']=='SUPPORTED_ANALOG' and out['exact_obligation']['status']=='SUPPORTED_ANALOG'
    assert out['detached_mutant']['status']=='VIOLATION' and out['f4']['early_ack_mutant']['status']=='VIOLATION'
    assert out['f4']['uninterrupted']['status']=='SUPPORTED_ANALOG'
    assert out['f4']['accepted_before_ack']['status']=='UNKNOWN_CALLER_COMMITTED_EFFECT'
    assert out['f4']['preaccept']['status']=='UNKNOWN_CALLER_NO_RECOVERED_EFFECT'
    assert all(x['status']=='INCOMPLETE' for x in out['corruption_controls'].values())
    pinned=subprocess.run(['git','show',FIXED_F2+':docs/architecture/core-substrate/fixtures-f2/fixtures.json'],
                          cwd=ROOT,capture_output=True,check=True).stdout
    sink_source=subprocess.run(['git','show',SINK_SOURCE+':research/phase-i-t18-sink-order-20261103/run.py'],
                               cwd=ROOT,capture_output=True,check=True).stdout
    assert hashlib.sha256(pinned).hexdigest()==sha(FIXTURE)
    out['provenance']={'f2_commit':FIXED_F2,'f2_fixture_sha256':sha(FIXTURE),
                       'verification_sha256':sha(VERIFY),'closure_sha256':sha(CLOSURE),
                       't18_source_commit':SINK_SOURCE,'t18_source_sha256':hashlib.sha256(sink_source).hexdigest(),
                       'f4_source_sha256':sha(HERE/'run.py'), 'recorded_f4_source_sha256':f4['f4_implementation_sha256'],
                       't18_raw_sha256':sha(HERE/'results.json'), 'f4_raw_sha256':sha(HERE/'F4-results.json')}
    assert out['provenance']['f4_source_sha256']==out['provenance']['recorded_f4_source_sha256']
    out['coverage']={'t18_use_current_fixture':'prepared-only; recorded schedule is narrower analogy',
                     't18_exact':'accepted-order correspondence with client-send event unlogged',
                     't07_power_loss':'not tested; real process death only',
                     'missing_vs_empty_journal':'not distinguishable by recorded recovery',
                     'gate_event_and_fsync_timing':'not retained in F4 raw events',
                     'other_T01_T24_F3_host_acceptance':'not tested'}
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
