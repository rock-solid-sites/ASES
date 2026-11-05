#!/usr/bin/env python3
"""Read-only selected T18 evidence check; never launches the serving implementation."""
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
class Incomplete(Exception): pass
class Violation(Exception): pass
def need(condition, message):
    if not condition: raise Incomplete(message)
def expect(condition, message):
    if not condition: raise Violation(message)
def rows(snapshot):
    raw = bytes.fromhex(snapshot['raw_hex'])
    need(snapshot['exists'] and raw.endswith(b'\n'), 'missing complete journal observation')
    need(hashlib.sha256(raw).hexdigest() == snapshot['sha256'], 'journal digest mismatch')
    result = [json.loads(line) for line in raw.splitlines()]
    need(all(type(r.get('seq')) is int and isinstance(r.get('event'), str) for r in result), 'missing event identity')
    expect(all(a['seq'] < b['seq'] for a, b in zip(result, result[1:])), 'durable sequence not increasing')
    return result

def check_case(case, exact=False):
    try:
        steps = case['steps']
        need(steps and type(case['sink_pid']) is int, 'missing process identity')
        expect(case['exit'] == -9, 'serving child not killed/reaped')
        previous = case['ready_ns']
        expect(case['start_ns'] < previous, 'startup/ready order')
        by = {}
        for step in steps:
            label = step['label']
            need(label not in by, 'ambiguous step label')
            by[label] = step
            need(type(step['start_ns']) is type(step['end_ns']) is int, 'missing call/return timestamps')
            expect(previous < step['start_ns'] < step['end_ns'], 'return-before-invocation order violated')
            previous = step['end_ns']
            need(step['status_code'] == 200 and isinstance(step['observed']['effects'], list), 'missing sink observation')
            journal = rows(step['journal'])
            expect([r for r in journal if r['event'] == 'effect_accepted'] == step['observed']['effects'],
                   'journal/effect observation mismatch')
            for effect in step['observed']['effects']:
                expect(hashlib.sha256(effect['payload'].encode()).hexdigest() == effect['payload_sha256'], 'effect payload hash')
            code = step['response']['status']
            if code in (200, 201):
                seq = step['response']['body']['event_seq']
                expect(any(r['seq'] == seq for r in journal), 'ACK lacks persisted event')
        expect(previous < case['exit_ns'] < case['restart']['start_ns'] < case['restart']['end_ns'], 'process/restart precedence')
        expect(case['restart']['exit'] != 0 and not case['restart']['stdout'].strip(), 'existing journal boot served/reset state')
        need('existing journal requires explicit recovery mode' in case['restart']['stderr'], 'startup refusal cause missing')
        expect(case['restart']['journal_after'] == case['final_journal'] == steps[-1]['journal'], 'refusal changed journal')
        def code(label, expected):
            expect(by[label]['response']['status'] == expected, label + ': unexpected response')
        for label in ('create', 'grant', 'activate'): code(label, 200)
        if exact:
            for label in ('commit-before-fixture', 'm'): code(label, 201)
            code('replace', 200); code('replacement-inactive', 409)
            replacement = by['replace']['observed']
            expect(replacement['holder'] == 'new' and replacement['authority_version'] == 2 and replacement['active'] is False,
                   'position advance/current activation evidence')
            expect(by['replace']['end_ns'] < by['m']['start_ns'], 'delivery sent before replacement ACK')
            commit = next(r for r in rows(by['commit-before-fixture']['journal']) if r['event'] == 'obligation_committed')
            effect = by['m']['observed']['effects']
            expect(len(effect) == 1 and effect[0]['payload'] == commit['payload'] == 'x'
                   and effect[0]['obligation_id'] == commit['obligation_id'] == 'm'
                   and effect[0]['check_mode'] == 'committed-exact-obligation', 'exact authorized payload not delivered')
        else:
            code('before-positive', 201); code('revoke', 200)
            revoked = by['revoke']['observed']; sent = by['post-revoke']
            need(by['revoke']['end_ns'] < sent['start_ns'], 'send-after-revoke ordering missing')
            expect(revoked['granted'] is revoked['active'] is False and revoked['authority_version'] == 1,
                   'revoke/current-generation state wrong')
            expect(sent['request']['body'] == dict(authority_version=1, request_id='post-revoke', payload='x'),
                   'post-revoke request identity')
            code('post-revoke', 409)
            expect(not any(e['payload'] == 'x' for e in sent['observed']['effects']), 'post-revoke effect accepted')
            if case['variant'] == 'reference':
                for label in ('after-create', 'after-grant', 'regrant-inactive', 'old-negative'): code(label, 409)
                for label in ('regrant', 'reactivate'): code(label, 200)
                code('fresh-positive', 201)
                expect(by['fresh-positive']['observed']['authority_version'] == 2, 'fresh generation not advanced')
        return dict(status='SUPPORTED', scope='selected flat-unit concrete history')
    except Incomplete as error: return dict(status='INCOMPLETE', reason=str(error))
    except Violation as error: return dict(status='VIOLATION', reason=str(error))
    except (KeyError, TypeError, ValueError, IndexError, StopIteration) as error:
        return dict(status='INCOMPLETE', reason='missing/invalid evidence: ' + str(error))

def main():
    data = json.loads(Path(sys.argv[1]).read_bytes())
    result = {name: check_case(case, name == 'exact_obligation') for name, case in data['cases'].items()}
    assert result['reference']['status'] == result['exact_obligation']['status'] == 'SUPPORTED', result
    assert result['equality_only']['status'] == 'VIOLATION', result
    missing = copy.deepcopy(data['cases']['reference'])
    del next(s for s in missing['steps'] if s['label'] == 'revoke')['end_ns']
    missing_journal = copy.deepcopy(data['cases']['reference'])
    del next(s for s in missing_journal['steps'] if s['label'] == 'post-revoke')['journal']
    controls = dict(missing_revoke_reply=check_case(missing), missing_journal=check_case(missing_journal))
    assert all(c['status'] == 'INCOMPLETE' for c in controls.values()), controls
    source = (HERE / 'managed_sink.py').read_bytes()
    base = (HERE.parent / 'run.py').read_bytes()
    fixture = HERE.parents[2] / 'docs/architecture/core-substrate/fixtures-f2/fixtures.json'
    assert hashlib.sha256(source).hexdigest() == data['source_sha256']
    assert hashlib.sha256(base).hexdigest() == data['base_sha256']
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == data['fixture_sha256']
    assert hashlib.sha256((HERE / 'probe.py').read_bytes()).hexdigest() == data['runner_sha256']
    print(json.dumps(dict(cases=result, controls=controls, source_fixture_runner_hashes='match',
                         qualification='coordinator-authored checker, not independent review'), indent=2, sort_keys=True))

if __name__ == '__main__': main()
