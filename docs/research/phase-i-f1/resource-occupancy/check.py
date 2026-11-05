#!/usr/bin/env python3
"""Read-only ledger/native-lifetime distinction and actual reference controls."""
import copy
import errno
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
def frame(value,stage):
    need(value['stage']==stage and type(value['pid']) is int,'missing actor/frame identity')
    wire=json.loads(bytes.fromhex(value['wire_utf8_hex']))
    expect(wire=={k:v for k,v in value.items() if k not in ('parent_received_ns','wire_utf8_hex')},'raw frame mismatch')
    expect(value['ns']<value['parent_received_ns'],'caller observation before sent frame')
def claims(value,expected):
    expect(value['integrity']=='ok' and value['claims']==expected,'actual ledger contents mismatch')
def busy(value):
    frame(value['first'],'denied')
    expect(value['first']['reason']=='native-resource-busy' and value['first']['native']['bound'] is False
           and value['first']['native']['errno']==errno.EADDRINUSE,'not an actual native occupancy denial')
    trace=value['first']['sql_trace']
    expect([s['sql'] for s in trace]==['BEGIN','ROLLBACK'] and trace[-1]['in_transaction'] is False,'busy denial wrote/committed claim')
    claims(value['ledger'],[])
def check(c):
    try:
        kind=c['kind'];initial=c['initial'];released=c['release_ack'];acquired=c['acquisition'];ack=acquired['first']
        frame(initial,'owner_ready');frame(released,'ledger_released');frame(ack,'acquisition_ack')
        address=['127.0.0.1',c['port']]
        expect(initial['native']['bound'] and initial['native']['identity']['address']==address
               and initial['native']['identity']['accepting']==1,'initial actual listener not established')
        claims(c['ledger_before_release'],['A']);claims(c['ledger_after_release'],[])
        expect(released['native_identity']==initial['native']['identity'],'release unexpectedly closed/replaced native resource')
        trace=released['sql_trace'];expect([r['sql'] for r in trace]==['BEGIN','DELETE','COMMIT'] and not trace[-1]['in_transaction'],
                                          'actual release COMMIT absent')
        expect(trace[-1]['end_ns']<released['ns'],'release ACK before SQLite COMMIT returned')
        if kind=='live':
            weak=c['unbacked'];frame(weak['first'],'claim_ack');frame(weak['second'],'native_result')
            expect(released['parent_received_ns']<weak['process']['start_ns'],'B initiated before actual release ACK observed')
            expect(weak['first']['ns']<weak['second']['native']['start_ns'] and weak['second']['native']['bound'] is False
                   and weak['second']['native']['errno']==errno.EADDRINUSE,'ledger-only path not an actual unbacked acquisition')
            claims(weak['ledger'],['B']);claims(c['explicit_unbacked_cleanup']['ledger'],[]);busy(c['busy'])
            frame(c['close_ack'],'resource_closed')
            expect(c['close_ack']['parent_received_ns']<ack['native']['start_ns'],'guarded acquisition preceded owned native close')
            expect(c['A_exit']['exit']==0,'live-owner close control missing')
        elif kind=='terminated':
            expect(c['A_exit']['exit']==-9 and c['A_exit']['exit_ns']<ack['native']['start_ns'],'owner death control missing')
        else:
            frame(c['handoff'],'descriptor_transferred');frame(c['keeper_ready'],'keeper_ready');busy(c['busy']);frame(c['close_ack'],'keeper_closed')
            expect(c['keeper_ready']['native_identity']==initial['native']['identity'],'SCM_RIGHTS reference not the original listener')
            expect(c['A_exit']['exit']==-9 and c['A_exit']['exit_ns']<c['busy']['process']['start_ns'],'busy test did not follow owner reap')
            expect(c['keeper_exit']['exit']==0 and c['keeper_exit']['exit_ns']<ack['native']['start_ns'],'success preceded retained fd close')
        expect(c['free_before_acquisition']['bound'] is True,'native positive precondition not actually available')
        expect(ack['native']['bound'] is True and ack['native']['identity']['address']==address and ack['native']['identity']['accepting']==1,
               'successful guarded ACK lacks actual resource')
        trace=ack['sql_trace'];expect([s['sql'] for s in trace]==['BEGIN','INSERT','COMMIT'],'guarded claim transaction missing')
        expect(ack['native']['end_ns']<trace[-1]['start_ns']<trace[-1]['end_ns']<ack['ns'],'bind/COMMIT/ACK order')
        claims(acquired['ledger'],['B'])
        expect(c['occupied_probe']['bound'] is False and c['occupied_probe']['errno']==errno.EADDRINUSE,'independent live-ACK occupancy control failed')
        expect(acquired['process']['exit']==-9 and acquired['process']['exit_ns']<c['after_B_termination']['native_probe']['start_ns'],'B termination not observed')
        claims(c['after_B_termination']['ledger'],['B']);expect(c['after_B_termination']['native_probe']['bound'],'ephemeral native release after B death not observed')
        return dict(status='SUPPORTED',observation='ledger conservation, actual acquisition and descriptor lifetime distinguished',
                    weak_ledger_only_unbacked_ack=(kind=='live'),durable_claim_survives_ephemeral_native_release=True)
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());result={k:check(v) for k,v in d['cases'].items()}
    assert all(v['status']=='SUPPORTED' for v in result.values()),result
    no_transfer=copy.deepcopy(d['cases']['retained']);del no_transfer['keeper_ready']['wire_utf8_hex']
    no_native=copy.deepcopy(d['cases']['live']);del no_native['acquisition']['first']['native']
    incomplete=dict(missing_transfer_evidence=check(no_transfer),missing_native_evidence=check(no_native))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=d['children'];assert len(children)==len({c['pid'] for c in children})==10
    events=[]
    for c in children:
        assert c['exit'] in (-9,0) and not c['stderr'] and not c['remaining_stdout_hex']
        events += [(c['start_ns'],1),(c['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    source=subprocess.check_output(['git','show',d['execution_sha']+':docs/research/phase-i-f1/resource-occupancy/probe.py'])
    assert hashlib.sha256(source).hexdigest()==d['source_sha256']
    print(json.dumps(dict(cases=result,incomplete_controls=incomplete,owned_children=len(children),maximum_observed_child_concurrency=maximum,
                          source_hash_verified=True,qualification='selected owned ephemeral listener backing at ACK, not host confinement/durable native restoration or failure of prior SQL-only scope'),indent=2,sort_keys=True))
if __name__=='__main__':main()
