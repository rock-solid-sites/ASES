#!/usr/bin/env python3
"""Read-only managed replay claim, mutation, limit and missing-evidence checks."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from check import Incomplete, Violation, need, expect, rows

def session(value):
    need(type(value['pid']) is int, 'missing child identity')
    expect(value['start_ns'] < value['ready_ns'] < value['exit_ns'] and value['exit'] == -9, 'child lifecycle')
    end = value['ready_ns']
    for step in value['steps']:
        expect(end < step['start_ns'] < step['end_ns'] < value['exit_ns'], 'call/return/process precedence')
        end = step['end_ns']
        journal = rows(step['journal'])
        expect([r for r in journal if r['event'] == 'effect_accepted'] == step['observed']['effects'], 'journal/effect mismatch')
        if step['response']['status'] in (200,201):
            expect(any(r['seq'] == step['response']['body']['event_seq'] for r in journal), 'ACK without durable event')
    journal = rows(value['final_journal'])
    expect([r for r in journal if r['event'] == 'effect_accepted'] == value['final_status']['effects'], 'final effects mismatch')
    return {s['label']:s for s in value['steps']}

def history(case, exact=False):
    try:
        writer, recovery, cold = case['writer'], case['recovery'], case['cold']
        w = session(writer); r = session(recovery)
        need(writer['recover'] is False and recovery['recover'] is True, 'missing explicit fresh/recover mode')
        expect(writer['journal_path'] == recovery['journal_path'], 'recovery used different journal path')
        expect(writer['final_journal'] == recovery['ready_journal'], 'runtime input bytes discontinuity')
        expect(writer['exit_ns'] < recovery['start_ns'], 'writer not reaped before restart')
        expected = writer['final_status']
        actual = recovery['ready_status']
        for key in ('holder','created','granted','active','authority_version','obligations','effects'):
            expect(expected[key] == actual[key], 'recovery state mismatch: '+key)
        if exact:
            expect(w['commit']['response']['status'] == 201 and w['replace']['response']['status'] == 200, 'original obligation/replacement ACK missing')
            expect(actual['holder'] == 'new' and actual['authority_version'] == 2 and actual['active'] is False,
                   'recovered replacement eligibility mismatch')
            expect(r['current-inactive']['response']['status'] == 409 and r['deliver']['response']['status'] == 201, 'exact/current profile distinction')
            expect(r['deliver']['observed']['effects'][0]['payload'] == 'x', 'exact payload lost')
        else:
            need(w['ack-before']['response']['status'] == 201 and w['revoke']['response']['status'] == 200, 'original ACK/revoke evidence absent')
            expect(actual['authority_version'] == 1 and actual['granted'] is actual['active'] is False,
                   'revocation eligibility not retained')
            expect(r['post-restart-revoke']['response']['status'] == 409, 'equal old token accepted after acknowledged revoke/restart')
            for label in ('inactive','old'): expect(r[label]['response']['status'] == 409, label+' negative failed')
            expect(r['ack-new']['response']['status'] == 201, 'new current positive failed')
        session(cold)
        expect(cold['journal_path'] == recovery['journal_path'] and cold['ready_journal'] == recovery['final_journal'], 'second restart journal continuity')
        expect(recovery['exit_ns'] < cold['start_ns'], 'recovery not reaped before cold restart')
        for key in ('holder','granted','active','authority_version','obligations','effects'):
            expect(recovery['final_status'][key] == cold['ready_status'][key], 'second restart state lost: '+key)
        return dict(status='SUPPORTED',scope='selected current-journal managed replay history')
    except Incomplete as error: return dict(status='INCOMPLETE',reason=str(error))
    except Violation as error: return dict(status='VIOLATION',reason=str(error))
    except (KeyError,ValueError,TypeError,IndexError) as error: return dict(status='INCOMPLETE',reason=str(error))

def refusal(value):
    expect(type(value['pid']) is int and value['start_ns'] < value['exit_ns'], 'refusal process metadata')
    expect(value['exit'] != 0 and not value['stdout'].strip(), 'invalid history served before ready')
    expect(bytes.fromhex(value['before_raw_hex']) == bytes.fromhex(value['after']['raw_hex']), 'refusal changed bytes')

def main():
    data = json.loads(Path(sys.argv[1]).read_bytes())
    results = {k:history(v,k=='exact_obligation') for k,v in data['cases'].items()}
    assert results['reference']['status'] == results['exact_obligation']['status'] == 'SUPPORTED', results
    assert results['replay_resurrection']['status'] == 'VIOLATION', results
    weak=data['cases']['replay_resurrection']
    by={s['label']:s for s in weak['recovery']['steps']}
    assert by['post-restart-revoke']['response']['status'] == 201
    assert any(e['payload']=='x' for e in weak['recovery']['final_status']['effects'])
    refusal(weak['cold'])  # Strict parser rejects the mutation's unlicensed effect.
    for value in data['invalid_controls'].values(): refusal(value)
    rollback=data['rollback_limit']; session(rollback)
    assert rollback['steps'][0]['response']['status'] == 201
    assert rollback['ready_status']['authority_version']==1 and rollback['ready_status']['active'] is True
    children=[c[part] for c in data['cases'].values() for part in ('writer','recovery','cold')]
    children += list(data['invalid_controls'].values()) + [rollback]
    children.sort(key=lambda c:c['start_ns'])
    assert len({c['pid'] for c in children})==len(children)==20
    assert all(a['exit_ns'] < b['start_ns'] for a,b in zip(children,children[1:]))
    no_ack=copy.deepcopy(data['cases']['reference']); del no_ack['writer']['steps'][-1]['response']
    no_journal=copy.deepcopy(data['cases']['reference']); del no_journal['recovery']['ready_journal']
    controls=dict(missing_revoke_ack=history(no_ack),missing_recovery_bytes=history(no_journal))
    assert all(v['status']=='INCOMPLETE' for v in controls.values()),controls
    root=Path(__file__).resolve().parent
    for name,key in [('managed_sink.py','source_sha256'),('replay_probe.py','runner_sha256'),('probe.py','helper_sha256')]:
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==data[key]
    print(json.dumps(dict(histories=results,invalid_startup_controls=len(data['invalid_controls']),
                          owned_processes=len(children),maximum_observed_child_concurrency=1,
                          missing_evidence_controls=controls,rollback_limit='older authentic prefix accepted; no nonrollback witness',
                          qualification='coordinator read-only checker, no independent replay review'),indent=2,sort_keys=True))

if __name__ == '__main__': main()
