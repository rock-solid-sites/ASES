#!/usr/bin/env python3
"""Raw local/remote outcome checks; loss is different from rejection."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('receipt_check_support',HERE.parent/'check.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
need=p.need;expect=p.expect

def ids(snapshot):return [r['request_id'] for r in p.rows(snapshot) if r['event']=='effect_accepted']
def check(c):
    try:
        kind=c['kind'];steps=p.session(c['original']);z=steps['receipt-z'];later=steps['next-after-outcome']
        need(steps['earlier-ack']['response']['status']==201,'no actual earlier positive ACK')
        expect(ids(c['prior_journal'])==['earlier-ack'],'prior actual ACK not retained')
        expect('receipt-z' in ids(c['after_z']),'z not actually locally committed')
        need(c['witness_alive'],'missing live witness observation')
        expect(c['witness_before']['pid']==c['witness_after_z']['pid']==c['witness_final']['pid']==c['witness']['pid'],
               'different witness process substituted')
        need(c['fault']['status']==200 and c['fault']['response']['configured'] is True,'fault configuration not observed')
        publication=next(e for e in reversed(z['observed']['cut_protocol_log']) if e['path']=='/publish')
        remote=[e for e in c['witness_after_z']['log'] if e['path']=='/publish'][-1]
        expect(remote['request']==publication['request'],'local and remote exchange attribution mismatch')
        expect(remote['response']['current']==c['witness_after_z']['current'],'remote recorded state differs from actual status')
        if kind=='rejected':
            expect(z['response']['status']==503 and z['response']['body']['local_control_committed'] is True,'rejection lost local commit status')
            expect(remote['status']==publication['status']==503 and remote['reply_suppressed'] is False
                   and remote['response']['published'] is False,'rejection was not pre-update with delivered failure')
            expect(c['witness_before']['revision']==c['witness_after_z']['revision']==c['witness_final']['revision']
                   and c['witness_before']['current']==c['witness_final']['current'],'rejected publish changed current witness')
            expect(later['response']['status']==503 and later['response']['body']['local_control_committed'] is False
                   and p.same(c['after_z'],c['after_next']),'rejection permitted later append')
            refusal=c['startup_refusal'];frame=refusal['frame'];need(frame is not None,'startup frame absent')
            expect(frame['ready'] is False and frame['local_parse_complete'] is True and refusal['exit']==1
                   and frame['witness_observation']['response']['allowed'] is False,'divergent restart not refused')
            expect(p.same(c['after_z'],refusal['journal_after']),'refusal discarded local unACKed record')
            return dict(status='SUPPORTED',observation='delivered publication rejection: old witness cut, retained local z, later/no-startup denial')
        expect(remote['status']==200 and remote['response']['published'] is True
               and c['witness_after_z']['revision']==c['witness_before']['revision']+1
               and c['witness_after_z']['current']['journal_sha256']==c['after_z']['sha256'],
               'actual successful z witness update absent')
        if kind=='lost':
            need(remote['reply_suppressed'] is True,'missing actual reply suppression evidence')
            need('error' in publication,'missing sink transport exception observation')
            expect(publication['response'] is None and publication['status'] is None and not publication['valid']
                   and not publication['transport_valid'],'sink received/validated a supposed lost response')
            expect(z['response']['status']==503 and z['response']['body']['local_control_committed'] is True,
                   'lost receipt incorrectly reported success or absent local effect')
        else:
            expect(remote['reply_suppressed'] is False and z['response']['status']==201 and publication['valid'],
                   'uninterrupted positive did not ACK validated publication')
        expect(later['response']['status']==201,'matching-cut later acceptance did not succeed')
        later_checks=[e for e in later['observed']['cut_protocol_log'] if e['path']=='/check' and e['start_ns']>z['end_ns']]
        need(later_checks,'no fresh later current-cut check')
        expect(later_checks[-1]['valid'] and later_checks[-1]['request']['nonce']!=publication['request']['nonce']
               and later_checks[-1]['request']['candidate']['journal_sha256']==c['after_z']['sha256'],
               'later access did not validate actual matching local cut with new nonce')
        recovered=c['recovered'];p.session(recovered);p.session(c['cold'])
        expect(p.same(c['original']['final_journal'],recovered['ready_journal'])
               and ids(recovered['ready_journal'])==['earlier-ack','receipt-z','next-after-outcome'],
               'actual current-file recovery lost earlier/unknown/later events')
        expect(ids(c['cold']['ready_journal'])==['earlier-ack','receipt-z','next-after-outcome','fresh-after-restart']
               and c['witness_final']['current']==c['cold']['ready_status']['actual_cut'],'second cold state/published cut mismatch')
        return dict(status='SUPPORTED',observation='actual witness update; '+('lost response yields503/local committed, fresh check permits later access and current-file recovery' if kind=='lost' else 'validated reply yields201; later access/recovery positive'))
    except p.Incomplete as error:return dict(status='INCOMPLETE',reason=str(error))
    except p.Violation as error:return dict(status='VIOLATION',reason=str(error))
    except (KeyError,TypeError,ValueError,StopIteration,IndexError) as error:return dict(status='INCOMPLETE',reason=str(error))

def main():
    data=json.loads(Path(sys.argv[1]).read_bytes());result={name:check(case) for name,case in data['cases'].items()}
    assert all(r['status']=='SUPPORTED' for r in result.values()),result
    missing=copy.deepcopy(data['cases']['lost']);del missing['witness_after_z']
    absent=check(missing);assert absent['status']=='INCOMPLETE',absent
    contradiction=copy.deepcopy(data['cases']['lost']);contradiction['witness_after_z']['revision']=contradiction['witness_before']['revision']
    contradicted=check(contradiction);assert contradicted['status']=='VIOLATION',contradicted
    for path,digest in data['source_hashes'].items():
        raw=subprocess.check_output(['git','show',data['execution_sha']+':research/phase-i-t18-sink-order-20261103/'+path])
        assert hashlib.sha256(raw).hexdigest()==digest
    children=[child for case in data['cases'].values() for child in case['children']]
    assert len(children)==len({child['pid'] for child in children})==11
    events=[]
    for child in children:
        assert child['exit'] in (-9,1);events += [(child['start_ns'],1),(child['exit_ns'],-1)]
    active=maximum=0
    for _,delta in sorted(events):active+=delta;maximum=max(active,maximum)
    assert active==0 and maximum==2
    print(json.dumps(dict(cases=result,missing_witness_evidence=absent,contradictory_revision=contradicted,owned_children=len(children),maximum_observed_child_concurrency=maximum,
                         source_hashes_verified=True,qualification='conditional trusted live witness and current root; no absent-effect inference from missing receipt, no divergence reconciliation or generic C7/F4 proof'),indent=2,sort_keys=True))
if __name__=='__main__':main()
