#!/usr/bin/env python3
"""Independent audit of one receipt-loss probe capture."""
import hashlib, json, sys, subprocess
from pathlib import Path

class Missing(Exception): pass
class Conflict(Exception): pass
def need(ok, why):
    if not ok: raise Missing(why)
def agree(ok, why):
    if not ok: raise Conflict(why)
def rows(s):
    need(s.get('exists') and 'raw_hex' in s and 'sha256' in s, 'journal snapshot absent')
    b=bytes.fromhex(s['raw_hex'])
    need(b.endswith(b'\n'), 'journal is not complete newline terminated bytes')
    agree(hashlib.sha256(b).hexdigest()==s['sha256'], 'journal digest contradicts bytes')
    return [json.loads(x) for x in b.splitlines()]
def event_ids(s): return [x['request_id'] for x in rows(s) if x.get('event')=='effect_accepted']
def same(a,b): return all(a.get(k)==b.get(k) for k in ('exists','raw_hex','sha256'))
def pub(step):
    entries=[x for x in step['observed']['cut_protocol_log'] if x.get('path')=='/publish']
    need(entries, 'sink publish exchange absent')
    return entries[-1]
def audit(name,c):
    try:
        need(c['kind']==name, 'case label mismatch')
        orig=c['original']; steps={s['label']:s for s in orig['steps']}
        need(set(('earlier-ack','receipt-z','next-after-outcome'))<=steps.keys(), 'caller step evidence absent')
        need(orig['start_ns']<orig['ready_ns']<orig['exit_ns'] and orig['exit']==-9, 'original process lifecycle incomplete')
        agree(orig['source_sha256']==d_hashes['published-cut/cut_sink.py'], 'sink source identity differs from captured source manifest')
        for label,s in steps.items():
            agree(orig['ready_ns']<s['start_ns']<s['end_ns']<orig['exit_ns'], 'caller/process ordering conflict')
            j=rows(s['journal'])
            need(s['response'] is not None and s['response'].get('status') is not None, 'caller response absent')
            if label=='earlier-ack':
                agree(s['response']['status']==201 and any(r.get('seq')==s['response']['body'].get('event_seq') for r in j), 'prior ACK lacks persisted event')
            if label=='receipt-z':
                agree(any(r.get('request_id')=='receipt-z' for r in j), 'receipt-z caller event absent from local bytes')
        need(event_ids(c['prior_journal'])==['earlier-ack'], 'prior ACK snapshot missing or unexpected')
        agree('earlier-ack' in event_ids(c['after_z']), 'later journal discarded prior ACK')
        z=steps['receipt-z'];later=steps['next-after-outcome'];px=pub(z)
        need(c['witness_alive'] and c['witness']['pid']==c['witness_before']['pid']==c['witness_after_z']['pid']==c['witness_final']['pid'], 'same live witness identity evidence absent')
        need(c['fault']['status']==200 and c['fault']['response']['configured'] is True, 'fault configuration receipt absent')
        remote=[x for x in c['witness_after_z']['log'] if x.get('path')=='/publish']
        need(remote, 'witness publish log absent')
        remote=remote[-1]
        agree(remote['request']==px['request'], 'sink publish and witness CAS request differ')
        agree(remote['response']['nonce']==px['request']['nonce'] and remote['response']['root']==px['request']['root'], 'witness response attribution conflicts')
        agree(remote['response']['pid']==c['witness']['pid'], 'publish served by another witness process')
        if name=='lost':
            need(remote.get('reply_suppressed') is True, 'actual lost-reply evidence absent')
            agree(remote['status']==200 and remote['response']['published'] is True, 'lost reply was not after successful CAS')
            agree(c['witness_after_z']['revision']==c['witness_before']['revision']+1, 'successful CAS revision did not advance')
            agree(c['witness_after_z']['current']==remote['response']['current'], 'witness status contradicts CAS current cut')
            agree(c['witness_after_z']['current']['journal_sha256']==c['after_z']['sha256'], 'CAS current cut is not actual local bytes')
            need(not px.get('transport_valid') and px.get('response') is None and px.get('error'), 'sink transport failure was not recorded')
            agree(z['response']['status']==503 and z['response']['body']['local_control_committed'] is True, 'lost receipt response misstates local effect')
            agree(later['response']['status']==201, 'matching-current later caller operation failed')
            checks=[x for x in later['observed']['cut_protocol_log'] if x.get('path')=='/check' and x['start_ns']>z['end_ns']]
            need(checks, 'fresh post-outcome check absent')
            agree(checks[-1]['valid'] and checks[-1]['request']['nonce']!=px['request']['nonce'], 'later check is not fresh and valid')
            agree(checks[-1]['request']['candidate']['journal_sha256']==c['after_z']['sha256'], 'later check candidate is not captured actual cut')
            final_ids=['earlier-ack','receipt-z','next-after-outcome']
            expect_recovery(c, orig, final_ids)
            agree(c['witness_final']['current']==c['cold']['ready_status']['actual_cut'], 'second cold cut differs from witness')
            return {'status':'SUPPORTED','finding':'Witness CAS advanced to the actual receipt-z journal before suppressing its reply; sink returned 503 with local commit recorded, then a fresh check admitted the next operation and two same-file cold recoveries retained prior ACK, z, and later effect.'}
        if name=='positive':
            agree(remote['status']==200 and remote['reply_suppressed'] is False and remote['response']['published'] is True, 'positive publication response absent/contradictory')
            agree(z['response']['status']==201 and px.get('valid') is True, 'positive sink ACK not validated')
            agree(c['witness_after_z']['current']['journal_sha256']==c['after_z']['sha256'], 'positive current cut mismatch')
            expect_recovery(c,orig,['earlier-ack','receipt-z','next-after-outcome'])
            return {'status':'SUPPORTED','finding':'Delivered publication receipt produced the positive ACK; later operation and current-file recovery retained journal effects.'}
        if name=='rejected':
            agree(remote['status']==503 and remote['reply_suppressed'] is False and remote['response']['published'] is False, 'rejection was not delivered before update')
            agree(c['witness_before']['revision']==c['witness_after_z']['revision']==c['witness_final']['revision'] and c['witness_before']['current']==c['witness_final']['current'], 'rejected publish changed witness current cut')
            agree(z['response']['status']==503 and z['response']['body']['local_control_committed'] is True, 'rejected publish response misstates local commit')
            agree(later['response']['status']==503 and later['response']['body']['local_control_committed'] is False and same(c['after_z'],c['after_next']), 'later request appended after rejected divergence')
            r=c['startup_refusal'];need(r['frame'] is not None, 'startup refusal frame absent')
            agree(r['frame']['ready'] is False and r['frame']['local_parse_complete'] is True and r['exit']==1, 'startup did not refuse parsed divergent state')
            agree(same(c['after_z'],r['journal_after']), 'startup refusal discarded or changed local record')
            agree(r['frame']['witness_observation']['response']['allowed'] is False, 'startup refusal lacks actual mismatch observation')
            return {'status':'SUPPORTED','finding':'Delivered 503 rejection left witness at the old cut; z remained locally committed, later append was blocked, and startup refused without changing the journal.'}
        raise Missing('unrecognized case')
    except Missing as e: return {'status':'INCOMPLETE','reason':str(e)}
    except Conflict as e: return {'status':'VIOLATION','reason':str(e)}
    except (KeyError,TypeError,ValueError,IndexError,StopIteration) as e: return {'status':'INCOMPLETE','reason':str(e)}
def expect_recovery(c,orig,ids):
    r=c['recovered'];cold=c['cold']
    need(r['start_ns']>orig['exit_ns'] and r['ready_ns']<r['exit_ns'] and r['exit']==-9, 'actual recovery process lifecycle absent')
    agree(same(orig['final_journal'],r['ready_journal']), 'recovery did not use same final journal bytes')
    agree(event_ids(r['ready_journal'])==ids, 'recovery lost or added events')
    need(cold['start_ns']>r['exit_ns'] and cold['ready_ns']<cold['exit_ns'] and cold['exit']==-9, 'second cold process lifecycle absent')
    agree(event_ids(cold['ready_journal'])==ids+['fresh-after-restart'], 'second cold recovery lost/adds event')
def main():
    global d_hashes
    d=json.loads(Path(sys.argv[1]).read_bytes())
    d_hashes=d['source_hashes']
    for rel,digest in d_hashes.items():
        blob=subprocess.check_output(['git','show',d['execution_sha']+':research/phase-i-t18-sink-order-20261103/'+rel])
        agree(hashlib.sha256(blob).hexdigest()==digest, 'captured source hash conflicts with execution commit: '+rel)
    result={k:audit(k,v) for k,v in d['cases'].items()}
    children=[x for c in d['cases'].values() for x in c['children']]
    need(len(children)==11 and len({x['pid'] for x in children})==11, 'child ownership count/identity incomplete')
    timeline=[]
    for x in children:
        agree(x['exit'] in (-9,1) and x['start_ns']<x['exit_ns'], 'child lifecycle conflict')
        timeline += [(x['start_ns'],1),(x['exit_ns'],-1)]
    active=peak=0
    for _,delta in sorted(timeline): active+=delta;peak=max(peak,active)
    agree(active==0 and peak<=2, 'child concurrency bound violated')
    report={'schema':d.get('schema'),'execution_sha':d.get('execution_sha'),'cases':result,'owned_children':len(children),'max_concurrency':peak,'source_hashes_verified':True,
            'qualification':'One selected live witness/current-root receipt-loss experiment. Does not establish witness power-loss durability, nonrollback against hostile storage, reconciliation of genuine divergence, or generic C7/F4 proof.'}
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__': main()
