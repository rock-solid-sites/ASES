#!/usr/bin/env python3
"""Read-only check of F4 observations, without relying on producer pass fields."""
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def check(d):
    try:
        for name, c in d['cases'].items():
            assert c['sink_exit']==-9 and c['client_exit']==0
            assert c['client_stderr']==''
            assert c['client_start_ns'] < c['kill_start_ns'] < c['reaped_ns']
            assert c['journal_live']==c['journal_after']
            for phase in ['live_reader','cold_reader']:
                r=c[phase]; o=r['observation']; j=c['journal_after']
                assert r['stderr']==''
                if name in ['preaccept','early_ack']:
                    assert not j['exists'] and j['raw_hex'] is None
                    assert o['state']=='MISSING' and r['exit']==3
                else:
                    raw=bytes.fromhex(j['raw_hex'])
                    assert raw.endswith(b'\n') and j['exists']
                    assert hashlib.sha256(raw).hexdigest()==j['sha256']==o['sha256']
                    rows=[json.loads(l) for l in raw.splitlines()]
                    assert len(rows)==1 and rows[0]['request_id']==name
                    assert rows[0]['payload_utf8_hex']==d['payload_hex']
                    assert hashlib.sha256(bytes.fromhex(d['payload_hex'])).hexdigest()==rows[0]['payload_sha256']
                    assert rows[0] in c['status']['effects']
                    assert rows[0] in c['status']['events']
                    assert o['state']=='VALID' and r['exit']==0 and len(o['effects'])==1
                    assert o['effects'][0]['request_id']==name and o['effects'][0]['payload_hex']==d['payload_hex']
            assert c['client']['http_status']==(201 if name in ['normal','early_ack'] else None)
            if name!='normal':
                expected={'preaccept':'request_waiting_before_accept','accepted':'accepted_waiting_before_ack',
                          'early_ack':'early_ack_waiting_before_accept'}[name]
                events=c['status']['events']
                gate=next(e for e in events if e['event']==expected)
                assert gate['request_id']==name and c['status']['waiting']==1
                assert c['gate_observed_ns'] < c['kill_start_ns']
                if name=='accepted':
                    assert events[0]['seq']==gate['accepted_event_seq']==1 and gate['seq']==2
                if name in ['preaccept','early_ack']:
                    assert c['status']['effects']==[]
            if name in ['normal','early_ack']:
                assert c['client_completed_ns'] < c['kill_start_ns']
        assert set(d['cases'])=={'normal','preaccept','accepted','early_ack'}
        for n,state,code in [('empty','EMPTY',0),('missing','MISSING',3),('malformed','REFUSED',2),('truncated','REFUSED',2)]:
            assert d['controls'][n]['observation']['state']==state and d['controls'][n]['exit']==code
        return 'SUPPORTED_SELECTED_PROCESS_LOSS_MAPPING'
    except (KeyError,ValueError,AssertionError,StopIteration,TypeError):
        return 'INCOMPLETE_OR_INCONSISTENT'

def main():
    d=json.loads((HERE/'round2-f4-gates.raw.json').read_text())
    result={'baseline':check(d),'controls':{}}
    for label in ['missing_gate','missing_file_observation','missing_client','truncated_journal']:
        bad=copy.deepcopy(d)
        if label=='missing_gate': bad['cases']['accepted']['status']['events'].pop()
        elif label=='missing_file_observation': del bad['cases']['preaccept']['journal_after']['exists']
        elif label=='missing_client': del bad['cases']['accepted']['client']
        else: bad['cases']['normal']['journal_after']['raw_hex']=bad['cases']['normal']['journal_after']['raw_hex'][:-10]
        result['controls'][label]=check(bad)
    print(json.dumps(result,indent=2))
    assert result['baseline']=='SUPPORTED_SELECTED_PROCESS_LOSS_MAPPING'
    assert set(result['controls'].values())=={'INCOMPLETE_OR_INCONSISTENT'}

if __name__=='__main__': main()
