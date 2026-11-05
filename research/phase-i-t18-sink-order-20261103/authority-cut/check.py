#!/usr/bin/env python3
"""Current authority evidence does not certify retained accepted whole-cut history."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

FIELDS=('created','granted','active','authority_version','holder')
class Incomplete(Exception):pass
class Violation(Exception):pass
def need(v,msg):
    if not v:raise Incomplete(msg)
def expect(v,msg):
    if not v:raise Violation(msg)
def rows(snapshot):
    raw=bytes.fromhex(snapshot['raw_hex']);need(snapshot['exists'] and raw.endswith(b'\n'),'missing complete observed journal')
    expect(hashlib.sha256(raw).hexdigest()==snapshot['sha256'],'journal digest mismatch')
    return [json.loads(line) for line in raw.splitlines()]
def same(a,b):return all(a[k]==b[k] for k in ('exists','raw_hex','sha256'))
def authority(state):return {key:state[key] for key in FIELDS}
def check(d):
    try:
        original=d['original'];proper=d['proper_current_journal_recovery'];rolled=d['rolled'];cold=d['cold'];marks=d['marks']
        by={step['label']:step for step in original['steps']};x=by['old-ACKed-x'];q=by['committed-q']
        need(x['response']['status']==q['response']['status']==201,'missing original actual content/obligation ACK')
        expect(d['original_authority']==d['current_authority']==authority(d['accepted_status']),'acceptance changed authority fixture')
        expect(x['end_ns']<q['start_ns']<q['end_ns']<d['current_publish']['start_ns']<d['current_publish']['end_ns']<original['exit_ns'],
               'current authority publication not after actual x/q ACKs')
        expect(d['current_publish']['response']['publication']==2 and d['current_publish']['body']['state']==d['current_authority'],
               'actual post-ACK authority publication absent')
        before_rows=rows(d['accepted_journal']);prefix_rows=rows(d['prefix'])
        expect([r['seq'] for r in before_rows]==[1,2,3,4,5] and [r['event'] for r in before_rows][-2:]==['effect_accepted','obligation_committed'],
               'original accepted history not observed')
        expect(before_rows[:3]==prefix_rows and len(prefix_rows)==3,'not authentic earlier management prefix')
        expect(same(original['final_journal'],d['accepted_journal']) and same(proper['ready_journal'],d['accepted_journal'])
               and same(d['before_rollback'],d['accepted_journal']),'proper current-journal lineage changed')
        expect([e['request_id'] for e in proper['ready_status']['effects']]==['old-ACKed-x']
               and proper['ready_status']['obligations']=={'q':q['body']['payload']},'positive proper recovery did not retain x/q')
        expect(proper['exit_ns']<marks['rollback_start_ns']<marks['rollback_end_ns']<rolled['start_ns'],'rollback lifecycle')
        expect(same(d['prefix'],d['after_rollback']) and same(d['after_rollback'],rolled['ready_journal']),'rollback/runtime actual input mismatch')
        expect(authority(rolled['ready_status'])==d['current_authority'] and rolled['ready_status']['effects']==[]
               and rolled['ready_status']['obligations']=={},'rolled state not same-authority/different accepted history')
        y=rolled['steps'][0];lost_q=rolled['steps'][1]
        need(y['response']['status']==201 and y['observed']['witness_log'],'missing actual new acceptance/live witness exchange')
        exchange=y['observed']['witness_log'][-1];reply=exchange['response']
        expect(exchange['valid'] and exchange['admitted'] and reply['allowed'] and reply['nonce']==exchange['request']['nonce'],
               'new actual sink use not admitted by fresh valid witness')
        expect(reply['current']==d['current_authority'] and reply['publication']==2 and reply['pid']==d['witness']['pid'],
               'witness was not genuinely current published authority')
        expect(y['response']['body']['event_seq']==x['response']['body']['event_seq']==4,'same-authority sequence reuse not observed')
        expect(lost_q['path']=='/deliver-obligation' and lost_q['response']['status']==409,'missing committed obligation was not actually queried')
        expect([e['request_id'] for e in cold['ready_status']['effects']]==['new-ACKed-y'] and cold['ready_status']['obligations']=={},
               'final strict recovery not missing old x/q')
        expect(same(rolled['final_journal'],cold['ready_journal']),'new actual ACK journal not preserved')
        witness=d['witness_status'];need(d['witness_alive'] and witness['pid']==d['witness']['pid'],'witness surviving process evidence missing')
        expect(witness['current']==d['current_authority']==d['witness_before_loss']['current'],'authority witness rolled/changed')
        expect(d['witness']['start_ns']<original['start_ns'] and cold['exit_ns']<d['witness']['exit_ns'],'witness lifetime did not span rollback')
        for event in witness['log']:
            if event['path']=='/publish':expect(set(event['request']['state'])==set(FIELDS),'content/oracle supplied as witness authority input')
        expect(any(e['path']=='/check' and e['request']==exchange['request'] and e['response']==reply for e in witness['log']),
               'external witness did not record actual admission exchange')
        return dict(status='COUNTEREXAMPLE',observation='genuinely current live authority admits new use from valid old cut missing earlier ACKed x/committed q')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());result=check(d);assert result['status']=='COUNTEREXAMPLE',result
    no_ack=copy.deepcopy(d);del next(s for s in no_ack['original']['steps'] if s['label']=='old-ACKed-x')['response']
    no_witness=copy.deepcopy(d);del no_witness['rolled']['steps'][0]['observed']['witness_log']
    incomplete=dict(missing_prior_ack=check(no_ack),missing_live_exchange=check(no_witness));assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[d[k] for k in ('original','proper_current_journal_recovery','rolled','cold','witness')]
    assert len({c['pid'] for c in children})==len(children)==5
    events=[]
    for c in children:
        assert c['exit']==-9
        events += [(c['start_ns'],1),(c['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    for path,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-t18-sink-order-20261103/'+path])
        assert hashlib.sha256(raw).hexdigest()==digest
    print(json.dumps(dict(result=result,incomplete_controls=incomplete,owned_children=len(children),maximum_observed_child_concurrency=maximum,
                          source_hashes_verified=True,qualification='authority-only promise unchanged; deliberate rollback outside trusted-current-journal premise, no physical-power-loss or aggregate C7/F4 proof'),indent=2,sort_keys=True))
if __name__=='__main__':main()
