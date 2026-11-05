#!/usr/bin/env python3
"""Native preparation and real COMMIT failure, without claiming atomic rollback."""
import copy
import errno
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_failure_check_support',HERE/'check.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
need,expect=base.need,base.expect

def check(c):
    try:
        kind=c['kind'];p=c['prepared'];base.frame(p,'native_prepared')
        expect(c['reader_held']['in_transaction'] is True and c['reader_held']['claims']==[] and c['reader_held']['journal_mode']=='delete',
               'real shared-reader premise not observed')
        expect(c['initial_native_close_ns']<c['process']['start_ns']<p['ns'] and p['native']['bound'] and p['busy_timeout_ms']==100,
               'owned native preparation/busy timeout absent')
        expect(p['native']['identity']['address']==['127.0.0.1',c['port']] and p['native']['identity']['accepting']==1,'prepared native resource identity')
        expect([s['sql'] for s in p['sql_trace']]==['BEGIN','INSERT'] and p['sql_trace'][-1]['in_transaction'],
               'prepared gate not before actual COMMIT')
        expect(c['native_while_uncommitted']['bound'] is False and c['native_while_uncommitted']['errno']==errno.EADDRINUSE,
               'independent native reservation visibility absent')
        expect(p['parent_received_ns']<c['native_while_uncommitted']['start_ns']<c['reader_at_gate']['ns']
               and c['reader_at_gate']['claims']==[] and c['reader_at_gate']['in_transaction'],
               'native visibility/empty uncommitted ledger observation order')
        expect(c['recovered_ledger']['integrity']=='ok' and c['native_after']['bound'] is True,'final native/database cleanup not observed')
        if kind=='killed':
            need(c['outcome'] is None and c['continue_ns'] is None,'missing actual precommit kill/no-success-ACK observation')
            expect(c['process']['exit']==-9 and c['recovered_ledger']['claims']==[],'prepared kill retained a committed claim')
            return dict(status='SUPPORTED',observation='actual SIGKILL before COMMIT, no success ACK, native free/no claim after recovery')
        outcome=c['outcome'];need(outcome is not None,'missing actual outcome frame')
        expect(c['reader_at_gate']['ns']<c['continue_ns']<outcome['ns'],'prepared continuation/outcome precedence')
        if kind=='busy':
            base.frame(outcome,'acquisition_commit_error')
            failure=outcome['failure'];trace=outcome['sql_trace']
            expect(failure['sqlite_errorcode']==sqlite3.SQLITE_BUSY and failure['sqlite_errorname']=='SQLITE_BUSY'
                   and failure['in_transaction_before_cleanup'] is True,'actual confirmed COMMIT_BUSY absent')
            expect(failure['native_identity_before_cleanup']==p['native']['identity'],'native resource did not survive until COMMIT error')
            expect([s['sql'] for s in trace]==['BEGIN','INSERT','COMMIT','ROLLBACK'] and trace[-2]['outcome']=='error'
                   and trace[-2]['sqlite_errorcode']==sqlite3.SQLITE_BUSY and trace[-1]['in_transaction'] is False,'error/rollback SQL trace')
            expect(trace[-1]['end_ns']<outcome['native_closed_ns']<outcome['ns'] and outcome['success_ack'] is False,'cleanup/success-ACK classification')
            expect(c['reader_after_failed_commit']['in_transaction'] is True and c['process']['exit']==0
                   and c['recovered_ledger']['claims']==[],'busy control changed reader/committed claim')
            return dict(status='SUPPORTED',observation='native prepare was externally visible; actual COMMIT_BUSY then rollback/close, no success ACK/claim')
        base.frame(outcome,'acquisition_ack')
        expect(c['reader_release']['in_transaction'] is False and c['reader_release']['end_ns']<c['continue_ns'],'positive reader not actually released')
        expect(outcome['sql_trace'][-1]['sql']=='COMMIT' and outcome['sql_trace'][-1]['outcome']=='returned'
               and outcome['native']['end_ns']<outcome['sql_trace'][-1]['end_ns']<outcome['ns'],'positive native/commit/ACK order')
        expect(c['live_native_probe']['bound'] is False and c['live_native_probe']['errno']==errno.EADDRINUSE,'positive ACK not backed while alive')
        expect(c['process']['exit']==-9 and c['recovered_ledger']['claims']==['B'],'positive durable B row lost')
        return dict(status='SUPPORTED',observation='released-reader positive COMMIT/ACK and native backing; native released on B death/durable row remains')
    except base.Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except base.Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());result={k:check(c) for k,c in d['cases'].items()}
    assert all(v['status']=='SUPPORTED' for v in result.values()),result
    contradiction=copy.deepcopy(d['cases']['busy']);del contradiction['outcome']['failure']
    no_error=copy.deepcopy(d['cases']['busy']);no_error['outcome']=base.omit_frame_field(no_error['outcome'],'failure')
    no_visibility=copy.deepcopy(d['cases']['busy']);del no_visibility['native_while_uncommitted']
    incomplete=dict(missing_commit_error=check(no_error),missing_native_visibility=check(no_visibility))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    contradictory=check(contradiction);assert contradictory['status']=='VIOLATION',contradictory
    children=d['children'];assert len(children)==len({c['pid'] for c in children})==3
    children.sort(key=lambda c:c['start_ns'])
    assert all(c['exit'] in (-9,0) and not c['stderr'] and not c['remaining_stdout_hex'] for c in children)
    assert all(a['exit_ns']<b['start_ns'] for a,b in zip(children,children[1:]))
    for name,digest in d['source_hashes'].items():
        raw=subprocess.check_output(['git','show',d['execution_sha']+':docs/research/phase-i-f1/resource-occupancy/'+name])
        assert hashlib.sha256(raw).hexdigest()==digest
    print(json.dumps(dict(cases=result,incomplete_controls=incomplete,owned_children=len(children),maximum_observed_child_concurrency=1,
                          contradictory_evidence_control=contradictory,
                          source_hashes_verified=True,qualification='visible tentative reservation and actual SQL failure, not failure-atomic whole effect or universal denial semantics'),indent=2,sort_keys=True))
if __name__=='__main__':main()
