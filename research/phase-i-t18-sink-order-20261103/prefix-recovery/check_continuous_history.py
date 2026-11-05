#!/usr/bin/env python3
"""Read-only selected whole-history consistency check; no producer pass flags."""
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
class Incomplete(Exception):pass
class Violation(Exception):pass
def need(ok,msg):
    if not ok:raise Incomplete(msg)
def expect(ok,msg):
    if not ok:raise Violation(msg)
def journal(snapshot,parse=True):
    need(isinstance(snapshot,dict) and snapshot.get('exists') is True,'missing journal observation')
    try:raw=bytes.fromhex(snapshot['raw_hex'])
    except (KeyError,ValueError,TypeError):raise Incomplete('journal bytes missing')
    need(hashlib.sha256(raw).hexdigest()==snapshot.get('sha256'),'journal digest mismatch')
    if not parse:return raw
    need(raw.endswith(b'\n'),'missing complete record framing')
    try:rows=[json.loads(l) for l in raw.splitlines()]
    except ValueError:raise Incomplete('malformed complete record observation')
    need(all(isinstance(r,dict) for r in rows),'missing record fields')
    return raw,rows
def effects(status):
    need(isinstance(status,dict) and isinstance(status.get('effects'),list),'missing full effects observation')
    return status['effects']

def check(d):
    try:
        cases=d['cases'];children=d['children']
        need(set(cases)=={'uninterrupted','quarantined','prepared','published'},'missing history')
        need(isinstance(children,list) and len(children)>0,'missing process observations')
        bypid={p['pid']:p for p in children}
        need(len(bypid)==len(children),'duplicate process identity')
        previous_end=0
        for p in children:
            need(type(p.get('start_ns')) is int and type(p.get('exit_observed_ns')) is int,'missing process boundary timestamp')
            expect(previous_end<=p['start_ns']<p['exit_observed_ns'],'owned process intervals overlap/out of order')
            expect(p.get('exit') in (-9,1),'unexpected owned process exit')
            previous_end=p['exit_observed_ns']
        for name,c in cases.items():
            old=c['actual_writer_history'];first=old['first'];new=c['new_call'];marks=c['marks']
            need(first['response']['status']==201 and new['response']['status']==201,'missing genuine success observations')
            old_body=first['request']['body'];new_body=new['request']['body']
            ids=[old_body['request_id'],new_body['request_id']]
            need(ids==['ack-before','continuous-new'],'missing selected request identity')
            need(old['fault']['response'] is None and old['later']['response'] is None,'missing unknown caller observations')
            need(old['fault'].get('error') and old['later'].get('error'),'missing no-reply evidence')
            expect(old['sink_exit']==c['new_sink_exit']==c['cold']['sink_exit']==-9,'required process death absent')
            expect(old['cold']['ready'] is False and old['cold']['exit']!=0,'strict initial refusal absent')
            need(any(t.get('stage')=='partial_write_then_exception' and 0<t['returned']<t['requested'] for t in old['io_trace']),
                 'partial append evidence missing')
            ack_bytes,ack_rows=journal(old['acknowledged_journal'])
            need(len(ack_rows)==1 and ack_rows[0].get('request_id')==ids[0],'prior ACK/record correlation missing')
            expect(ack_rows[0].get('payload')==old_body['payload'],'prior ACK payload not retained')
            fault_bytes=journal(old['journal_after_fault'],False)
            expect(fault_bytes.startswith(ack_bytes) and not fault_bytes.endswith(b'\n'),'selected append-only tail relation not observed')
            expect(journal(old['journal_after_later'],False)==fault_bytes,'journal changed after persistence failure')
            expect(journal(c['same_surviving_journal'],False)==fault_bytes,'surviving journal discontinuity')
            expect(c['quarantine_raw_hex']==fault_bytes.hex() and c['quarantine_sha256']==hashlib.sha256(fault_bytes).hexdigest(),
                   'original uncertain bytes not retained')
            expect(journal(c['restored_journal'])[0]==ack_bytes,'recovered prefix differs from actual ACKed state')
            recovered=effects(c['restored'])
            expect([e.get('request_id') for e in recovered]==ids[:1] and recovered[0].get('payload')==old_body['payload'],
                   'recovered observation loses or invents earlier ACK')
            final=effects(c['cold']['status']);after=effects(c['after'])
            expect([e.get('request_id') for e in final]==ids,'final recovered observation loses or invents ACKed effect')
            expect([e.get('payload') for e in final]==[old_body['payload'],new_body['payload']],'recovered ACKed payload mismatch')
            expect(after==final,'newly ACKed state differs from cold observation')
            for snap in [c['after_journal'],c['cold']['journal']]:
                _,rows=journal(snap)
                expect(rows==final,'durable records and complete recovered observation differ')
            expect(c['restored']['authority_version']==c['after']['authority_version']==c['cold']['status']['authority_version']==1,
                   'selected currentness version changed')
            seq=[first['start_monotonic_ns'],first['completion_monotonic_ns'],marks['io_done_ns'],
                 marks['recovery_ready_ns'],new['start_monotonic_ns'],new['completion_monotonic_ns'],marks['final_cold_reaped_ns']]
            need(all(type(n) is int for n in seq),'missing invocation/reply/process timestamps')
            expect(all(a<b for a,b in zip(seq,seq[1:])),'return/process/invocation precedence violated')
            if name!='uninterrupted':
                g=c['gate'];need(isinstance(g,dict),'missing selected gate')
                expect(g['gate']==name and g['exit']==-9 and g['stdout']==g['stderr']=='','gate/ready/death mismatch')
                expect(marks['io_done_ns']<marks['gate_start_ns']<marks['gate_done_ns']<marks['recovery_ready_ns'],'gate crash precedence violated')
            need(c.get('child_pids') and all(pid in bypid for pid in c['child_pids']),'missing owned process IDs')
            for pid in c['child_pids']:
                p=bypid[pid];argv=p['argv']
                need('--server' in argv,'unknown child role')
                i=argv.index('--server')
                expect(argv[i+2]==c['journal_path'],'journal path discontinuity across original/recovery process')
        return {'status':'SUPPORTED_SELECTED_CONTINUOUS_HISTORIES','histories':len(cases),'owned_children':len(children),
                'unknown_outcomes':'failed/blocked requests remain no-reply; no automatic denial or retry inference'}
    except (KeyError,TypeError,Incomplete) as exc:return {'status':'INCOMPLETE','reason':str(exc)}
    except Violation as exc:return {'status':'VIOLATION','reason':str(exc)}

def main():
    d=json.loads((HERE/'continuous-history.raw.json').read_text())
    out={'baseline':check(d),'controls':{}}
    for name in ['lost_old_ACK','missing_ACK_metadata','missing_boundary','missing_gate']:
        bad=copy.deepcopy(d)
        if name=='lost_old_ACK':bad['cases']['uninterrupted']['cold']['status']['effects'].pop(0)
        elif name=='missing_ACK_metadata':del bad['cases']['uninterrupted']['actual_writer_history']['first']
        elif name=='missing_boundary':del bad['children'][0]['exit_observed_ns']
        else:del bad['cases']['published']['gate']
        out['controls'][name]=check(bad)
    assert out['baseline']['status']=='SUPPORTED_SELECTED_CONTINUOUS_HISTORIES',out
    assert out['controls']['lost_old_ACK']['status']=='VIOLATION',out
    assert all(out['controls'][n]['status']=='INCOMPLETE' for n in ['missing_ACK_metadata','missing_boundary','missing_gate']),out
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
