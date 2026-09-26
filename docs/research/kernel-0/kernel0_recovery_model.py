#!/usr/bin/env python3
"""Finite recovery projection over the unchanged Kernel-0 policy oracle.

BFS reaches closure for each explicitly bounded fixture. Ghost truth and trace
metadata are checker state, NEVER input to recovery. No service code is imported.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from pathlib import Path

import kernel0_finite_model as m

P = m.Profile('independent')


def initial():
    s, _ = m.resolve(m.State(), m.Request('establish'), P)
    return m.resolve(s, m.Request('grant', target=0, value=7), P)[0]


@dataclass(frozen=True)
class Machine:
    disk: m.State
    memory: m.State | None
    truth: m.State  # oracle only; never read in a recovery assignment
    phases: tuple[int, ...]  # 0 idle,1 ingress,2 validated,3 prepared,4 committed,5 ack,6 denied,7 lost
    candidates: tuple[m.State | None, ...]
    lock: int = -1
    live: bool = True
    crashes: int = 0
    bindings: tuple[int, ...] = (0, 1, 2, 3)
    orphaned: int = 0
    root: str = 'work'
    lost_ack: bool = False
    recovered: bool = False
    continued: bool = False
    carried_content: bool = False


def set_item(xs, i, value):
    return xs[:i] + (value,) + xs[i + 1:]


def edges(s, qs, policy, recovery, weakness):
    """Yield (event, successor, violation). Checks use independent policy truth."""
    def out(label, new, error=None):
        return label, new, error

    if not s.live:
        disk = s.disk
        root = s.root
        if weakness == 'rollback':
            disk = initial()  # authentic original image of the SAME work
        if weakness == 'root_confusion':
            root, disk = 'other-work', initial()
        if weakness == 'forget_consumed':
            disk = replace(disk, issued=sum(1 << i for i, r in enumerate(disk.rights) if r))
        if weakness == 'undo_unacknowledged' and s.lost_ack:
            disk = initial()
        if root != 'work' and weakness != 'root_confusion':
            return  # fail closed, never silently initialize
        bindings = (0, 1, 2, 3) if recovery == 'continuing' else (-2,) * 4
        if weakness == 'binding_confusion':
            active = next((i for i in range(3) if disk.rights[i]), -2)
            bindings = (active, 1, 2, 3)
        new = replace(s, disk=disk, memory=disk, live=True, bindings=bindings,
                      recovered=True, root=root)
        error = ('wrong recovery root' if root != 'work' else
                 'recovered view differs from committed whole cut' if disk != s.truth else None)
        # Reuse weakening checked behaviorally, not only as a structural mismatch.
        if weakness == 'forget_consumed':
            error = None
        yield out('recover', new, error)
        return

    if s.crashes < 2:
        lost = any(phase == 4 for phase in s.phases)
        new = replace(s, memory=None, live=False, lock=-1, crashes=s.crashes + 1,
                      phases=tuple(7 if phase in (1, 2, 3, 4) else phase for phase in s.phases),
                      candidates=(None,) * len(qs), bindings=(-2,) * 4,
                      orphaned=s.orphaned | s.disk.issued, lost_ack=s.lost_ack or lost,
                      carried_content=s.disk.content == 1)
        yield out('crash: erase all service volatile state', new)

    if recovery == 'cold' and s.recovered:
        for i in range(4):
            if (s.bindings[i] == -2 and s.disk.rights[i]
                    and not s.orphaned & (1 << i)):
                yield out(f'trusted fresh attach a{i}',
                          replace(s, bindings=set_item(s.bindings, i, i)))

    for i, q in enumerate(qs):
        phase = s.phases[i]
        if phase == 0:
            if q.evidence >= 0 and s.bindings[q.evidence] == -2:
                continue
            yield out(f'{i}: ingress {q.label()}',
                      replace(s, phases=set_item(s.phases, i, 1)))
        elif phase == 1 and (s.lock == -1 or weakness == 'detached_validation'):
            evidence = s.bindings[q.evidence] if q.evidence >= 0 else -1
            if evidence == -2:
                continue
            candidate, outcome = m.resolve(s.memory, replace(q, evidence=evidence), policy)
            if outcome == 'deny':
                yield out(f'{i}: deny', replace(s, phases=set_item(s.phases, i, 6)))
            else:
                yield out(f'{i}: validate', replace(
                    s, lock=i if weakness != 'detached_validation' else -1,
                    phases=set_item(s.phases, i, 2), candidates=set_item(s.candidates, i, candidate)))
        elif phase == 2:
            yield out(f'{i}: prepare tentative whole image',
                      replace(s, phases=set_item(s.phases, i, 3)))
        elif phase == 3:
            candidate = s.candidates[i]
            expected, outcome = m.resolve(s.truth, q, policy)
            error = None if outcome == 'commit' and candidate == expected else 'not a current guarded whole commitment'
            disk = candidate
            if weakness == 'torn' and q.kind == 'pair':
                disk = replace(candidate, data=(candidate.data[0], s.disk.data[1]))
            if weakness == 'content_reference' and q.kind == 'accept':
                disk = replace(candidate, content=-1)
            if weakness == 'mixed_cut' and q.kind == 'replace':
                disk = replace(candidate, content=initial().content, data=initial().data)
            if weakness == 'early_ack':
                # Success becomes an observed commitment although recoverable state is old.
                new = replace(s, truth=expected, memory=candidate, lock=-1,
                              phases=set_item(s.phases, i, 5))
                yield out(f'{i}: acknowledge volatile publication WITHOUT durable commitment', new, error)
            else:
                new = replace(s, disk=disk, memory=candidate, truth=expected, lock=-1,
                              phases=set_item(s.phases, i, 4),
                              continued=s.continued or (s.recovered and s.carried_content
                                                       and q.kind == 'resume' and q.value == 1))
                yield out(f'{i}: recoverable commitment', new, error)
        elif phase == 4:
            yield out(f'{i}: acknowledgement', replace(s, phases=set_item(s.phases, i, 5)))


def trace_to(parents, state, last=None):
    events = []
    while parents[state] is not None:
        before, event = parents[state]
        events.append({'event': event, 'after': asdict(state)})
        state = before
    events.reverse()
    if last:
        label, new, error = last
        events.append({'event': label, 'after': asdict(new), 'violation': error})
    return events


def explore(name, qs, policy=P, recovery='continuing', weakness=''):
    start = Machine(initial(), initial(), initial(), (0,) * len(qs), (None,) * len(qs))
    parents = {start: None}
    queue = deque([start])
    count = 0
    success = None
    while queue:
        s = queue.popleft()
        if s.continued and success is None:
            success = trace_to(parents, s)
        for label, new, error in edges(s, qs, policy, recovery, weakness):
            count += 1
            if error:
                return {'name': name, 'recovery': recovery, 'weakness': weakness,
                        'states': len(parents), 'edges': count,
                        'counterexample': trace_to(parents, s, (label, new, error))}
            if new not in parents:
                parents[new] = (s, label)
                queue.append(new)
    return {'name': name, 'recovery': recovery, 'weakness': weakness,
            'states': len(parents), 'edges': count, 'counterexample': None,
            'successful_recovery': success}


def fixtures():
    q = m.Request
    replacement = q('replace', target=0, other=1)
    return [
        ('whole_pair', (q('pair', 0, value=3),), P),
        ('accept_content', (q('accept', 0, value=1), q('resume', 0, value=1)), P),
        ('replacement_old_replay', (replacement, q('flip', 0)), P),
        ('revocation_old_replay', (q('restrict', target=0, value=0), q('flip', 0)), P),
        ('replacement_new_continuation', (replacement, q('resume', 1, value=0)), P),
        ('accept_replace', (q('accept', 0, value=1), replacement), P),
        ('retained_content_fresh_continuation', (q('accept', 0, value=1), replacement,
                                               q('resume', 1, value=1)), P),
        ('precrash_request_and_replay', (q('flip', 0), replacement, q('flip', 0)), P),
        ('work_replace', (q('set', 0, value=1), replacement), P),
        ('interacting_fields', (q('set', 0, target=0, value=1), q('set', 0, target=1, value=1)),
         m.Profile('coupled', coupled=True)),
        ('compatible_fields', (q('set', 0, target=0, value=1), q('set', 0, target=1, value=1)), P),
        ('no_reuse', (q('restrict', target=0, value=0), q('grant', target=0, value=7), q('flip', 0)), P),
    ]


def run():
    reference = [explore(name, qs, p, mode) for name, qs, p in fixtures()
                 for mode in ('cold', 'continuing')]
    assert all(r['counterexample'] is None for r in reference)
    for mode in ('cold', 'continuing'):
        assert any(r['recovery'] == mode and r['successful_recovery'] for r in reference)
    mapping = {'early_ack': 'whole_pair', 'rollback': 'replacement_old_replay',
               'torn': 'whole_pair', 'content_reference': 'accept_content',
               'mixed_cut': 'accept_replace', 'binding_confusion': 'replacement_old_replay',
               'undo_unacknowledged': 'whole_pair', 'root_confusion': 'whole_pair',
               'detached_validation': 'interacting_fields', 'forget_consumed': 'no_reuse'}
    weakened = []
    for weakness, target in mapping.items():
        name, qs, p = next(f for f in fixtures() if f[0] == target)
        result = explore(name, qs, p, weakness=weakness)
        assert result['counterexample'], weakness
        # Also exercise a completed acknowledgement before the same crash.
        if weakness in ('rollback', 'torn', 'content_reference', 'mixed_cut', 'binding_confusion'):
            s = Machine(initial(), initial(), initial(), (0,) * len(qs), (None,) * len(qs))
            completed_trace = []
            for event in result['counterexample']:
                if event['event'].startswith('crash'):
                    for j, phase in enumerate(s.phases):
                        if phase == 4:
                            label, s, error = next(e for e in edges(s, qs, p, 'continuing', weakness)
                                                   if e[0] == f'{j}: acknowledgement')
                            completed_trace.append({'event': label, 'after': asdict(s)})
                label, s, error = next(e for e in edges(s, qs, p, 'continuing', weakness)
                                       if e[0] == event['event'])
                completed_trace.append({'event': label, 'after': asdict(s), 'violation': error})
            assert error
            result['acknowledged_counterexample'] = completed_trace
        weakened.append(result)
    return {'claim': 'bounded fixture closure only; no cutoff or unbounded refinement theorem',
            'bounds': {'max_crashes': 2, 'max_requests': 3, 'contexts': 4,
                       'work_fields': 2, 'content_atoms': 2},
            'sources': {p.name: sha256(p.read_bytes()).hexdigest() for p in
                        (Path(__file__), Path(m.__file__))},
            'reference': reference, 'weakened': weakened}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'reference_states': sum(x['states'] for x in result['reference']),
                      'reference_edges': sum(x['edges'] for x in result['reference']),
                      'mutants_detected': len(result['weakened'])}))
