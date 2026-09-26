#!/usr/bin/env python3
"""Existential whole-history checker and separate-process trace collection."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import threading

import kernel0_finite_model as m
import kernel0_recovery_check as h


def state(raw):
    return m.State(raw['established'], tuple(raw['data']), raw['content'], raw['issued'],
                   tuple(raw['rights']), tuple(raw['parents']))


def explanation(history):
    events = history['events']
    profile = m.Profile(history['profile'], coupled=history['profile'] == 'coupled')
    assert m.invariant(state(history['initial']), profile)
    requests = {e['id']: m.Request(**e['request']) for e in events if e['event'] == 'invoke'}
    ids = sorted(requests)
    assert ids == list(range(len(ids)))
    # status: not invoked=0, pending=1, resolved=2, abandoned=3, returned=4
    # resolved views/outcomes remain checker metadata, not service input.
    @lru_cache(None)
    def search(index, current, status, answers, live):
        if index == len(events):
            return ()
        event = events[index]
        kind = event['event']
        # First attempt to consume this observed event, otherwise resolve another
        # outstanding call in the interval before it. Search all eligible orders.
        next_status = list(status)
        permitted = True
        new_current, new_live = current, live
        if kind == 'invoke':
            i = event['id']
            permitted = live and status[i] == 0
            next_status[i] = 1
        elif kind == 'return':
            i = event['id']
            if event['outcome'] == 'unknown':
                permitted = not live and status[i] in (2, 3)
            else:
                permitted = status[i] == 2 and answers[i] == (event['outcome'], state(event['state']))
            next_status[i] = 4
        elif kind == 'crash':
            permitted = live
            new_live = False
            next_status = [3 if x == 1 else x for x in status]
        elif kind == 'recover':
            permitted = not live and current == state(event['state'])
            new_live = True
        else:
            raise ValueError(event)
        if permitted:
            suffix = search(index + 1, new_current, tuple(next_status), answers, new_live)
            if suffix is not None:
                return ({'observed_event': index, 'kind': kind},) + suffix
        if live:
            for i in ids:
                if status[i] == 1:
                    successor, outcome = m.resolve(current, requests[i], profile)
                    statuses, replies = list(status), list(answers)
                    statuses[i], replies[i] = 2, (outcome, successor)
                    suffix = search(index, successor, tuple(statuses), tuple(replies), live)
                    if suffix is not None:
                        return ({'resolve_before_event': index, 'id': i, 'outcome': outcome,
                                 'state': asdict(successor)},) + suffix
        return None
    witness = search(0, state(history['initial']), (0,) * len(ids), (None,) * len(ids), True)
    return {'accepted': witness is not None, 'witness': witness, 'search_states': search.cache_info().currsize}


class Recorder:
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()

    def record(self, event):
        with self.lock:
            self.events.append(event)

    def request(self, holder, q, lane, i, invoked):
        self.record({'event': 'invoke', 'id': i, 'request': asdict(q)})
        invoked.set()
        try:
            reply = holder.call(h.wire(q), lane)
            result = {'event': 'return', 'id': i, 'outcome': reply['outcome'],
                      'state': asdict(h.abstract(reply['state']))}
        except (EOFError, OSError):
            with self.lock:
                assert any(e['event'] == 'crash' for e in self.events), 'unexpected transport failure'
            result = {'event': 'return', 'id': i, 'outcome': 'unknown'}
        self.record(result)
        return result


def collect(directory):
    fixtures = [
        ('independent_pair', 'independent', m.Request('pair', 0, value=3), 1, 'durable',
         m.Request('flip', 0, target=1), 5, False),
        ('coupled_fields', 'coupled', m.Request('set', 0, value=1), 1, 'prepared',
         m.Request('set', 0, target=1, value=1), 5, False),
        ('replacement_then_old', 'independent', m.Request('replace', target=0, other=1), 0, 'published',
         m.Request('set', 0, value=1), 1, True),
        ('old_ingress_replaced', 'independent', m.Request('set', 0, value=1), 1, 'received',
         m.Request('replace', target=0, other=1), 0, True),
        ('accepted_then_resume', 'independent', m.Request('accept', 0, value=1), 1, 'published',
         m.Request('resume', 0, value=1), 5, True),
    ]
    histories = []
    for repeat in range(3):
        for name, profile, first, lane0, stage, second, lane1, wait_second in fixtures:
            path = directory / f'{name}-{repeat}.db'
            initial = h.setup(path, profile)
            holder = h.Holder(path, profile, gate={'lane': lane0, 'kind': first.kind, 'stage': stage})
            record = Recorder()
            with ThreadPoolExecutor(2) as pool:
                event0, event1 = threading.Event(), threading.Event()
                f0 = pool.submit(record.request, holder, first, lane0, 0, event0)
                holder.gated()
                f1 = pool.submit(record.request, holder, second, lane1, 1, event1)
                assert event1.wait(10)
                if wait_second:
                    f1.result(timeout=10)
                record.record({'event': 'crash'})
                killed_pid = holder.kill()
                f0.result(timeout=10)
                f1.result(timeout=10)
            restarted = h.Holder(path, profile)
            record.record({'event': 'recover', 'state': asdict(restarted.read())})
            record.request(restarted, m.Request('flip', 0), 1, 2, threading.Event())
            # A final crash/recovery observation also tests the post-restart call.
            record.record({'event': 'crash'})
            restarted.kill()
            restarted = h.Holder(path, profile)
            record.record({'event': 'recover', 'state': asdict(restarted.read())})
            final_pid = restarted.proc.pid
            restarted.kill()
            history = {'name': f'{name}-{repeat}', 'profile': profile, 'initial': asdict(initial),
                       'events': record.events, 'killed_pid': killed_pid, 'final_holder_pid': final_pid}
            verdict = explanation(history)
            assert verdict['accepted'], history
            history['refinement'] = verdict
            histories.append(history)
    return histories


def mutation_checks():
    initial = m.State(True, (0, 0), 0, 1, (7, 0, 0, 0), (-1,) * 4)
    replace_q = m.Request('replace', target=0, other=1)
    replacement, _ = m.resolve(initial, replace_q, m.Profile('independent'))
    old = m.Request('set', 0, value=1)
    unsafe = replace(replacement, data=(1, 0))
    def invoke(i, q):
        return {'event': 'invoke', 'id': i, 'request': asdict(q)}
    def reply(i, outcome, s):
        return {'event': 'return', 'id': i, 'outcome': outcome, 'state': asdict(s)}
    examples = {
        'stale_after_acknowledged_replace': [invoke(0, replace_q), reply(0, 'commit', replacement),
            invoke(1, old), reply(1, 'commit', unsafe)],
        'acknowledged_replacement_rolled_back': [invoke(0, replace_q), reply(0, 'commit', replacement),
            {'event': 'crash'}, {'event': 'recover', 'state': asdict(initial)}],
        'unacknowledged_partial_pair': [invoke(0, m.Request('pair', 0, value=3)),
            {'event': 'crash'}, {'event': 'return', 'id': 0, 'outcome': 'unknown'},
            {'event': 'recover', 'state': asdict(replace(initial, data=(1, 0)))}],
        # Each response is plausible from the initial view but together cannot
        # have that pair of whole returned views in one serial history.
        'incompatible_success_snapshots': [invoke(0, m.Request('set', 0, value=1)),
            invoke(1, m.Request('set', 0, target=1, value=1)),
            reply(0, 'commit', replace(initial, data=(1, 0))),
            reply(1, 'commit', replace(initial, data=(0, 1)))],
    }
    results = []
    for name, events in examples.items():
        history = {'name': name, 'profile': 'independent', 'initial': asdict(initial), 'events': events}
        verdict = explanation(history)
        assert not verdict['accepted'], name
        # Delete events only if the remainder remains structurally complete:
        # bounded examples are already short; preserve all semantically necessary
        # invocation/response/recovery structure rather than claim global minima.
        results.append({'history': history, 'refinement': verdict})
    # Unknown outcome really has both alternatives, not an oracle-chosen one.
    pair = m.Request('pair', 0, value=3)
    pair_state, _ = m.resolve(initial, pair, m.Profile('independent'))
    unknowns = []
    for recovered in (initial, pair_state):
        history = {'name': 'unknown_can_be_old_or_new', 'profile': 'independent', 'initial': asdict(initial),
                   'events': [invoke(0, pair), {'event': 'crash'},
                              {'event': 'return', 'id': 0, 'outcome': 'unknown'},
                              {'event': 'recover', 'state': asdict(recovered)}]}
        verdict = explanation(history)
        assert verdict['accepted']
        unknowns.append({'history': history, 'refinement': verdict})
    return {'rejected': results, 'accepted_unknown_alternatives': unknowns}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    with tempfile.TemporaryDirectory(prefix='kernel0-traces-') as tmp:
        result = {'histories': collect(Path(tmp)), 'oracle_discrimination': mutation_checks()}
    result['sources'] = {p.name: sha256(p.read_bytes()).hexdigest() for p in
                         (Path(__file__), Path(m.__file__), Path(h.__file__),
                          h.HERE / 'kernel0_recovery_service.py', h.HERE / 'kernel0_service.py')}
    result['qualification'] = 'finite existential trace refinement under abstract policy and crash projection; not independent review'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'actual_histories': len(result['histories']), 'rejected_mutations': 4,
                      'accepted_unknown_alternatives': 2}))
