#!/usr/bin/env python3
"""Finite interleavings of two reservations; not a runtime allocator."""
from collections import Counter, deque
from dataclasses import dataclass, replace
import json

CAPACITY = 2
LIMIT = 10_000
NAMES = ('C', 'S')
EVENTS = tuple((op, i) for op in ('prepare', 'commit', 'consume') for i in range(2))

@dataclass(frozen=True)
class State:
    attempted: int = 0
    prepared: tuple = (False, False)
    reserved: tuple = (0, 0)
    allocated: tuple = (0, 0)
    consumed: tuple = (0, 0)


def step(s, op, i, qty, recheck):
    values = list(getattr(s, {'prepare':'prepared', 'commit':'reserved', 'consume':'consumed'}[op]))
    if op == 'prepare':
        if qty[i] > CAPACITY - sum(s.reserved):
            return s, 'deny', 'insufficient-at-prepare'
        values[i] = True
        return replace(s, prepared=tuple(values)), 'commit', None
    if op == 'commit':
        if not s.prepared[i]:
            return s, 'deny', 'not-prepared'
        if recheck and qty[i] > CAPACITY - sum(s.reserved):
            return s, 'deny', 'insufficient-at-commit'
        values[i] = qty[i]
        return replace(s, reserved=tuple(values), allocated=tuple(values)), 'commit', None
    if s.consumed[i] >= s.allocated[i]:
        return s, 'deny', 'no-unconsumed-allocation'
    values[i] += 1
    return replace(s, consumed=tuple(values)), 'commit', None


def violations(s):
    errors = []
    if sum(s.reserved) > CAPACITY:
        errors.append('reservation-sum-exceeds-capacity')
    for i in range(2):
        if s.allocated[i] != s.reserved[i] or s.consumed[i] > s.allocated[i]:
            errors.append('allocation-or-consumption-inconsistent:' + NAMES[i])
    return errors


def search(qty, recheck):
    root = State()
    queue = deque([(root, [])])
    seen = {root}
    counts = Counter()
    witnesses = {}
    truncated = False
    while queue:
        state, path = queue.popleft()
        for bit, (op, i) in enumerate(EVENTS):
            if state.attempted & (1 << bit):
                continue
            after, outcome, reason = step(state, op, i, qty, recheck)
            after = replace(after, attempted=state.attempted | (1 << bit))
            errors = violations(after)
            event = {'event': op + '_' + NAMES[i], 'outcome': outcome, 'reason': reason,
                     'reserved': after.reserved, 'allocated': after.allocated,
                     'consumed': after.consumed, 'violations': errors}
            next_path = path + [event]
            counts['attempted'] += 1
            counts[outcome] += 1
            if reason:
                counts['deny:' + reason] += 1
            if errors:
                counts['violation_edges'] += 1
                witnesses.setdefault('over_reservation', next_path)
            if reason == 'insufficient-at-commit':
                witnesses.setdefault('competing_commit_denied', next_path)
            if reason == 'no-unconsumed-allocation' and op == 'consume':
                witnesses.setdefault('unallocated_consumption_denied', next_path)
            if after.reserved == (1, 1) and after.consumed == (1, 1):
                witnesses.setdefault('both_allocate_and_consume', next_path)
            if after not in seen:
                if len(seen) >= LIMIT:
                    truncated = True
                else:
                    seen.add(after)
                    queue.append((after, next_path))
    return {'quantities': qty, 'commit_recheck': recheck, 'states': len(seen),
            'counts': dict(sorted(counts.items())), 'limit': LIMIT,
            'truncated': truncated, 'witnesses': witnesses}


def repeat_control():
    s = State()
    trace = []
    for op in ('prepare', 'commit', 'consume', 'consume'):
        s, outcome, reason = step(s, op, 0, (1, 1), True)
        trace.append({'event': op + '_C', 'outcome': outcome, 'reason': reason,
                      'reserved': s.reserved, 'consumed': s.consumed, 'violations': violations(s)})
    assert [e['outcome'] for e in trace] == ['commit', 'commit', 'commit', 'deny']
    return trace


def main():
    conflict = search((2, 1), True)
    mutant = search((2, 1), False)
    fitting = search((1, 1), True)
    assert not any(r['truncated'] for r in (conflict, mutant, fitting))
    assert conflict['counts'].get('violation_edges', 0) == 0
    assert 'competing_commit_denied' in conflict['witnesses']
    assert mutant['counts']['violation_edges'] > 0
    assert 'both_allocate_and_consume' in fitting['witnesses']
    assert fitting['counts'].get('violation_edges', 0) == 0
    print(json.dumps({'conflict_reference': conflict, 'conflict_mutant': mutant,
                      'fitting_reference': fitting, 'repeat_consumption_control': repeat_control()},
                     indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
