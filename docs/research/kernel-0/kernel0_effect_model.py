#!/usr/bin/env python3
"""Finite decision-authorized sink profile; no delivery uniqueness or fairness."""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from pathlib import Path


@dataclass(frozen=True)
class State:
    current: bool = True
    observed_permission: bool | None = None
    phase: int = 0  # idle, observed, tentative, committed, ack, denied/lost
    intent: bool = False
    committed: bool = False  # ghost history fact, never a delivery input
    source_live: bool = True
    source_crashes: int = 0
    sink_live: bool = True
    sink_crashes: int = 0
    wire: bool = False
    accepted: int = 0
    irrevocable: int = 0  # ghost effects; cannot be erased by a sink restart
    visible: int = 0
    ack: bool = False
    revoked_at_decision: bool = False


def edges(s, weakness=''):
    if s.source_live:
        if s.current:
            yield 'revoke producer', replace(s, current=False), None
        if s.phase == 0:
            yield 'submit and observe permission', replace(s, phase=1, observed_permission=s.current), None
        if s.phase == 1:
            if s.current or (weakness == 'stale_authorization' and s.observed_permission):
                yield 'prepare intent', replace(s, phase=2), None
            else:
                yield 'deny revoked decision', replace(s, phase=5), None
        if s.phase == 2:
            if s.current or (weakness == 'stale_authorization' and s.observed_permission):
                new = replace(s, phase=3, intent=True, committed=True,
                              revoked_at_decision=not s.current)
                yield 'durable guarded decision', new, ('stale authority at decision' if not s.current else None)
            else:
                yield 'deny changed permission', replace(s, phase=5), None
        if s.phase == 3:
            yield 'decision acknowledgement', replace(s, phase=4), None
        if s.source_crashes < 2:
            new = replace(s, source_live=False, wire=False, observed_permission=None, source_crashes=s.source_crashes + 1,
                          phase=5 if s.phase in (1, 2, 3) else s.phase)
            if weakness == 'volatile_intent':
                new = replace(new, intent=False)
            yield 'source crash', new, None
            if s.wire:
                yield 'source crash (message survives)', replace(new, wire=True), None
    else:
        new = replace(s, source_live=True)
        error = 'committed obligation lost' if s.committed and not s.intent and s.accepted == 0 else None
        yield 'source recovery', new, error

    if s.source_live and not s.wire and (s.intent or (weakness == 'send_tentative' and s.phase == 2)):
        new = replace(s, wire=True)
        if weakness == 'forget_on_send':
            new = replace(new, intent=False)
        yield 'send obligation to sink', new, None
    if s.sink_live and s.wire and s.accepted < 2:
        new = replace(s, wire=False, accepted=s.accepted + 1, irrevocable=s.irrevocable + 1, ack=False)
        error = None if s.committed else 'irreversible effect without authoritative commitment'
        yield 'sink irrevocably accepts', new, error
    if s.sink_live and s.visible < s.accepted:
        yield 'external observation', replace(s, visible=s.accepted), None
    if s.sink_live and s.accepted and not s.ack:
        yield 'sink acknowledgement', replace(s, ack=True), None
    if s.sink_live and s.sink_crashes < 2:
        new = replace(s, sink_live=False, sink_crashes=s.sink_crashes + 1, wire=False, ack=False)
        if weakness == 'volatile_sink':
            new = replace(new, accepted=0, visible=0)
        yield 'sink crash', new, None
        if s.wire:
            yield 'sink crash (message survives)', replace(new, wire=True), None
    if not s.sink_live:
        new = replace(s, sink_live=True)
        yield 'sink recovery', new, ('accepted consequence disappeared' if s.accepted != s.irrevocable else None)
    if weakness == 'cancel_on_revoke' and not s.current and s.intent:
        yield 'discard obligation because producer revoked', replace(s, intent=False), (
            'committed required consequence no longer recoverable' if s.accepted == 0 else None)


def path(parents, state, last=None):
    result = []
    while parents[state] is not None:
        previous, event = parents[state]
        result.append({'event': event, 'after': asdict(state)})
        state = previous
    result.reverse()
    if last:
        event, new, error = last
        result.append({'event': event, 'after': asdict(new), 'violation': error})
    return result


def explore(weakness=''):
    start = State()
    parents = {start: None}
    queue = deque([start])
    witnesses = {}
    transitions = 0
    while queue:
        s = queue.popleft()
        targets = {'delayed_after_revoke': not s.current and s.accepted > 0,
                   'duplicates_allowed': s.accepted == 2,
                   'crash_recovered_delivery': s.source_crashes > 0 and s.accepted > 0,
                   'sink_survives_lost_ack': s.sink_crashes > 0 and s.accepted > 0 and not s.ack}
        for name, condition in targets.items():
            if condition and name not in witnesses:
                witnesses[name] = path(parents, s)
        for label, new, error in edges(s, weakness):
            transitions += 1
            if error:
                return {'weakness': weakness, 'states': len(parents), 'edges': transitions,
                        'counterexample': path(parents, s, (label, new, error))}
            if new not in parents:
                parents[new] = (s, label)
                queue.append(new)
    return {'weakness': weakness, 'states': len(parents), 'edges': transitions,
            'counterexample': None, 'witnesses': witnesses}


def pinned_histories():
    decision = ['submit and observe permission', 'prepare intent', 'durable guarded decision']
    histories = {
        'revocation_before_decision': ['submit and observe permission', 'revoke producer', 'deny revoked decision'],
        'authorized_before_revoke_accepted_after': decision + ['revoke producer', 'send obligation to sink',
                                                               'sink irrevocably accepts', 'external observation'],
        'accepted_before_revoke_visible_after': decision + ['send obligation to sink', 'sink irrevocably accepts',
                                                            'revoke producer', 'external observation'],
        'crash_before_intent': decision[:2] + ['source crash', 'source recovery'],
        'crash_after_intent': decision + ['source crash', 'source recovery', 'send obligation to sink',
                                         'sink irrevocably accepts'],
        'inflight_survives_source_crash': decision + ['send obligation to sink', 'source crash (message survives)',
                                                    'sink irrevocably accepts'],
        'sink_accept_lost_ack_retry': decision + ['send obligation to sink', 'sink irrevocably accepts',
                                                 'sink crash', 'sink recovery', 'send obligation to sink',
                                                 'sink irrevocably accepts'],
    }
    output = {}
    for name, events in histories.items():
        s = State()
        trace = []
        for label in events:
            _, s, error = next(e for e in edges(s) if e[0] == label)
            assert error is None
            trace.append({'event': label, 'after': asdict(s)})
        if name == 'crash_before_intent':
            assert not s.intent and not s.accepted
        if name == 'sink_accept_lost_ack_retry':
            assert s.accepted == 2
        output[name] = trace
    return output


def run():
    reference = explore()
    assert reference['counterexample'] is None and len(reference['witnesses']) == 4
    mutants = [explore(w) for w in ('stale_authorization', 'volatile_intent', 'send_tentative',
                                    'forget_on_send', 'volatile_sink', 'cancel_on_revoke')]
    assert all(x['counterexample'] for x in mutants)
    return {'reference': reference, 'weakened': mutants, 'pinned_histories': pinned_histories(),
            'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'bounds': 'one monotone intent, one payload, two effects, two crashes per process',
            'claim': 'fixture closure, safety and existential successes; no fairness or cutoff theorem'}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    result = run()
    parser.parse_args().output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'states': result['reference']['states'], 'edges': result['reference']['edges'],
                      'mutants': len(result['weakened'])}))
