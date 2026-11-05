#!/usr/bin/env python3
"""Read-only startup-overlap, guarded recovery and mandatory-participation evidence."""
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
def same(a,b):return all(a[k]==b[k] for k in ('exists','raw_hex','sha256'))
def rows(snapshot):
    raw=bytes.fromhex(snapshot['raw_hex']);need(snapshot['exists'] and raw.endswith(b'\n'),'missing complete journal observation')
    expect(hashlib.sha256(raw).hexdigest()==snapshot['sha256'],'journal digest mismatch')
    result=[json.loads(line) for line in raw.splitlines()]
    need(all(type(row.get('seq')) is int and row.get('event')=='effect_accepted' for row in result),'missing durable event identity')
    return result
def startup(value,ready):
    need(type(value['ready']) is bool and type(value['pid']) is int and type(value['startup_observed_ns']) is int,'missing startup/process observation')
    expect(value['ready'] is ready and value['start_ns']<value['startup_observed_ns']<value['exit_ns'],'startup/readiness/death order')
    if value['startup_raw_hex']:
        expect(json.loads(bytes.fromhex(value['startup_raw_hex']))==value['startup_frame'],'startup raw/decoded mismatch')
    if ready:expect(value['exit']==-9,'actual serving owner not killed/reaped')
def accepted(call,name,seq):
    expect(call['response']['status']==201 and call['response']['body']['event_seq']==seq,'actual ACK/sequence mismatch')
    expect(call['request']['request_id']==name and call['start_ns']<call['end_ns'],'request identity/timestamps')
    expect(any(r['request_id']==name and r['payload']==call['request']['payload'] and r['seq']==seq for r in rows(call['journal'])),
           'ACK lacks exact durable payload/event')
def reason(process):
    frame=process['startup_frame']
    return frame.get('reason','') if frame else process['stderr']
def overlap(c):
    try:
        startup(c['A'],True);startup(c['B'],True);startup(c['cold'],False)
        need(not c['journal_after_A_ready']['exists'] and not c['journal_before_requests']['exists'],'missing prepared-only fresh-journal schedule')
        expect(c['A']['startup_observed_ns']<c['B']['start_ns']<c['B']['startup_observed_ns']<c['journal_before_requests']['ns']
               <c['first']['start_ns']<c['first']['end_ns']<c['second']['start_ns'],'both-ready-before-first-request precedence')
        expect(c['A']['journal_path']==c['B']['journal_path']==c['cold']['journal_path'],'different journals do not test writer exclusion')
        accepted(c['first'],'A',1);accepted(c['second'],'B',1)
        records=rows(c['after']);expect([r['seq'] for r in records]==[1,1] and [r['request_id'] for r in records]==['A','B'],'duplicate global sequence not observed')
        expect([r['request_id'] for r in c['A_final']['effects']]==['A'] and [r['request_id'] for r in c['B_final']['effects']]==['B'],'separate process views not observed')
        expect(c['cold']['exit']==1 and 'invalid durable sequence' in reason(c['cold']) and c['cold_status'] is None,'strict refusal not caused by duplicate sequence')
        expect(same(c['after'],c['after_cold']),'strict refusal modified accepted journal bytes')
        return dict(status='COUNTEREXAMPLE',observation='both ready before append, two actual201/seq1, strict recovery refuses; all ACKed bytes still present')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))
def reference(c):
    try:
        for key in ('A','recovered','cold'):startup(c[key],True)
        for key in ('blocked_B','fresh_refusal'):startup(c[key],False)
        expect(c['blocked_B']['exit']==75 and reason(c['blocked_B'])=='writer-guard-busy','second trusted holder not excluded')
        need(not c['journal_before']['exists'] and not c['journal_after_block']['exists'],'guard control not before first journal append')
        expect(c['blocked_B']['exit_ns']<c['first']['start_ns'],'blocked holder not prior to first actual effect')
        accepted(c['first'],'first',1)
        expect(c['A']['exit_ns']<c['fresh_refusal']['start_ns']<c['fresh_refusal']['exit_ns']<c['recovered']['start_ns'],
               'old owner/fresh refusal/recovery precedence')
        expect(c['fresh_refusal']['exit']==1 and 'existing journal requires explicit recovery mode' in reason(c['fresh_refusal']),
               'existing fresh mode reset instead of refusal')
        expect(same(c['first']['journal'],c['after_fresh']) and same(c['after_fresh'],c['recovered_ready_journal']),
               'actual journal lineage changed before recovery')
        expect(c['restored']['effects']==rows(c['first']['journal']),'prior ACK not reconstructed before ready')
        accepted(c['second'],'second',2)
        expect([r['request_id'] for r in rows(c['final_journal'])]==['first','second'] and c['final']['effects']==rows(c['final_journal']),
               'second current-journal restart loses actual ACK')
        guards=[c[key]['startup_frame']['guard'] for key in ('A','blocked_B','fresh_refusal','recovered','cold')]
        expect(all(g==guards[0] for g in guards),'guard inode/path/device changed within selected trusted-root history')
        return dict(status='SUPPORTED',observation='cooperative guard excludes second pre-append startup; actual kill/recovery retains two ACKs/seq1,2')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))
def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());c=d['cases']
    results=dict(original_overlap=overlap(c['original_overlap']),nonparticipating_writer=overlap(c['nonparticipating_writer']),
                 guarded_restart=reference(c['guarded_restart']))
    assert results['original_overlap']['status']==results['nonparticipating_writer']['status']=='COUNTEREXAMPLE',results
    assert results['guarded_restart']['status']=='SUPPORTED',results
    roots=c['distinct_roots'];startup(roots['A'],True);startup(roots['B'],True)
    expect(roots['A']['startup_frame']['guard']['inode']!=roots['B']['startup_frame']['guard']['inode'],'distinct roots share one global guard')
    accepted(roots['first'],'root-A',1);accepted(roots['second'],'root-B',1)
    for item,name in zip(roots['cold'],('root-A','root-B')):
        startup(item['process'],True);expect([r['request_id'] for r in item['status']['effects']]==[name],'distinct root recovery mixed effects')
    no_start=copy.deepcopy(c['original_overlap']);del no_start['B']['startup_observed_ns']
    no_bytes=copy.deepcopy(c['guarded_restart']);del no_bytes['recovered_ready_journal']
    incomplete=dict(missing_startup=overlap(no_start),missing_recovery_bytes=reference(no_bytes))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=d['children'];assert len(children)==len({p['pid'] for p in children})==15
    events=[]
    for child in children:
        assert child['exit'] in (-9,1,75) and not child['remaining_stdout_hex']
        events += [(child['start_ns'],1),(child['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    for name,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-t18-sink-order-20261103/'+name])
        assert hashlib.sha256(raw).hexdigest()==digest
    print(json.dumps(dict(cases=results,distinct_roots='both acquired/ACKed/cold recovered independently',incomplete_controls=incomplete,
                          owned_children=len(children),maximum_observed_child_concurrency=maximum,source_hashes_verified=True,
                          qualification='trusted cooperative all-writer/stable-inode/current-root profile; no untrusted confinement, root authentication, power loss or aggregate F4/F1 closure'),indent=2,sort_keys=True))
if __name__=='__main__':main()
