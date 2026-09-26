#!/usr/bin/env python3
"""Two-domain witness: local bits and authority; one coupled reservation invariant."""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


@dataclass(frozen=True)
class State:
    bits: tuple[int, int] = (0, 0)
    slots: tuple[int, int] = (0, 0)
    authority: tuple[int, int] = (0, 0)  # 0 old, 1 replacement, -1 revoked
    live: tuple[bool, bool] = (True, True)


@dataclass(frozen=True)
class Op:
    kind: str
    domain: int
    evidence: int = 0
    scope: int = 0
    peer: int = 0


def put(xs, i, value):
    return xs[:i] + (value,) + xs[i+1:]


def valid(s):
    return sum(s.slots) <= 1 and all(x in (0, 1) for x in s.bits + s.slots)


def step(s, q, weakness=''):
    d, peer = q.domain, 1-q.domain
    if q.kind in ('crash', 'recover'):
        return replace(s, live=put(s.live, d, q.kind == 'recover')), 'lifecycle'
    if not s.live[d]:
        return s, 'pending'
    if q.kind == 'replace':
        if s.authority[d] != 0:
            return s, 'deny'
        return replace(s, authority=put(s.authority, d, 1)), 'commit'
    if q.kind == 'revoke':
        return replace(s, authority=put(s.authority, d, -1)), 'commit'
    if q.scope != d and weakness != 'erase_scope':
        return s, 'deny'
    if q.evidence != s.authority[d] or q.evidence not in (0, 1):
        return s, 'deny'
    if weakness == 'global_availability' and not all(s.live):
        return s, 'pending'
    if q.kind == 'flip':
        return replace(s, bits=put(s.bits, d, 1-s.bits[d])), 'commit'
    if q.kind == 'release':
        return replace(s, slots=put(s.slots, d, 0)), 'commit'
    if q.kind == 'reserve':
        if not s.live[peer]:
            return s, 'pending'
        if s.slots[peer]:
            return s, 'deny'
        return replace(s, slots=put(s.slots, d, 1)), 'commit'
    if q.kind == 'move':
        if not s.live[peer]:
            return s, 'pending'
        if s.slots[d] != 1 or s.slots[peer] or q.peer != s.authority[peer] or q.peer not in (0, 1):
            return s, 'deny'
        return replace(s, slots=put(put(s.slots, d, 0), peer, 1)), 'commit'
    raise ValueError(q)


def catalog():
    for d in range(2):
        for kind in ('crash', 'recover', 'replace', 'revoke'):
            yield Op(kind, d)
        for kind, evidence, scope in product(('flip', 'reserve', 'release'), range(2), range(2)):
            yield Op(kind, d, evidence, scope)
        for evidence, peer in product(range(2), repeat=2):
            yield Op('move', d, evidence, d, peer)


def footprint(q):
    d, peer = q.domain, 1-q.domain
    if q.kind != 'flip':
        raise ValueError('parallel-step witness deliberately restricted to independent work')
    return {f'authority{d}', f'bit{d}', f'live{d}'}, {f'bit{d}'}


def graph():
    start = State()
    parents = {start: None}
    queue = deque([start])
    count = 0
    parallel_count = 0
    live_independence = None
    operations = tuple(catalog())
    while queue:
        s = queue.popleft()
        assert valid(s)
        for q in operations:
            new, outcome = step(s, q)
            count += 1
            assert valid(new)
            if outcome in ('deny', 'pending'):
                assert new == s
            if q.kind in ('crash', 'recover'):
                assert (new.bits, new.slots, new.authority) == (s.bits, s.slots, s.authority)
            if q.kind == 'flip' and outcome == 'commit':
                assert q.scope == q.domain and q.evidence == s.authority[q.domain]
                assert new.slots == s.slots and new.authority == s.authority
                if not s.live[1-q.domain]:
                    live_independence = {'before': asdict(s), 'operation': asdict(q), 'after': asdict(new)}
            if new not in parents:
                parents[new] = (s, q)
                queue.append(new)
        a, b = Op('flip', 0, s.authority[0], 0), Op('flip', 1, s.authority[1], 1)
        sa, oa = step(s, a)
        sb, ob = step(s, b)
        if oa == ob == 'commit':
            ra, wa = footprint(a)
            rb, wb = footprint(b)
            assert not (wa & (rb | wb) or wb & (ra | wa))
            ab, ob2 = step(sa, b)
            ba, oa2 = step(sb, a)
            simultaneous = replace(s, bits=(1-s.bits[0], 1-s.bits[1]))
            assert ab == ba == simultaneous and oa2 == ob2 == 'commit'
            parallel_count += 1
    assert parallel_count and live_independence
    return {'states': len(parents), 'edges': count, 'unordered_parallel_steps': parallel_count,
            'local_work_while_other_down': live_independence}


def trace(ops, start=State(), weakness=''):
    s = start
    result = []
    for q in ops:
        before = s
        s, outcome = step(s, q, weakness)
        result.append({'operation': asdict(q), 'before': asdict(before), 'outcome': outcome, 'after': asdict(s)})
    return s, result


def attacks():
    output = {}
    # Two overlapping reservations each read both slots empty, then independently
    # write their own row. Their local orders are individually legal, union is not.
    start = State()
    qa, qb = Op('reserve', 0, scope=0), Op('reserve', 1, scope=1)
    a, oa = step(start, qa)
    b, ob = step(start, qb)
    torn_union = replace(start, slots=(a.slots[0], b.slots[1]))
    assert oa == ob == 'commit' and not valid(torn_union)
    output['detached_cross_domain_guard'] = {'trace': ['A reads slots 00', 'B reads slots 00',
        'A commits its reservation', 'B commits its reservation'], 'final': asdict(torn_union),
        'disposition': 'coupled admission needs one coherent view/order'}
    _, serial = trace([qa, qb])
    assert serial[-1]['outcome'] == 'deny'
    output['coherent_reference'] = serial
    # Domain labels coincide numerically; authentic evidence for B is still not A.
    q = Op('flip', 0, evidence=0, scope=1)
    correct, co = step(start, q)
    weak, wo = step(start, q, 'erase_scope')
    assert co == 'deny' and wo == 'commit'
    output['erased_authority_scope'] = {'proposal': asdict(q), 'correct': co, 'weakened': wo, 'after': asdict(weak)}
    down, _ = step(start, Op('crash', 0))
    local = Op('flip', 1, scope=1)
    correct, co = step(down, local)
    weak, wo = step(down, local, 'global_availability')
    assert co == 'commit' and wo == 'pending'
    output['accidental_global_requirement'] = {'trace': ['crash A', 'B local flip'],
        'reference': co, 'global_gate': wo, 'classification': 'unnecessary availability dependency, not safety failure'}
    # Splitting a declared transfer across independently recoverable rows loses
    # the resource, even though the exclusion invariant remains true.
    reserved, _ = step(start, qa)
    moved, outcome = step(reserved, Op('move', 0, scope=0, peer=0))
    partial = replace(reserved, slots=(0, 0))
    assert outcome == 'commit' and partial != reserved and partial != moved and valid(partial)
    output['partial_transfer_recovery'] = {'trace': ['reserve A', 'begin transfer A to B',
        'durably clear A', 'crash before durably setting B', 'recover both rows'],
        'before': asdict(reserved), 'partial': asdict(partial), 'whole': asdict(moved),
        'disposition': 'whole-effect obligation stronger than invariant alone'}
    # Recovery of one participant may not load an unrelated old local image of
    # a completed joint transfer: it is not a predecessor-closed cut.
    mixed = replace(moved, slots=(reserved.slots[0], moved.slots[1]))
    assert not valid(mixed)
    output['incompatible_joint_recovery'] = {'before': asdict(reserved), 'committed': asdict(moved),
        'recover_A_from_pre_transfer': asdict(mixed), 'disposition': 'joint effect constrains compatible recovery cuts'}
    final, witness = trace([qa, Op('move', 0, scope=0, peer=0), Op('crash', 0),
                            Op('flip', 1, scope=1), Op('recover', 0),
                            Op('replace', 0), Op('flip', 0, scope=0), Op('flip', 0, evidence=1, scope=0)])
    assert witness[-2]['outcome'] == 'deny' and witness[-1]['outcome'] == 'commit'
    output['successful_coupling_local_recovery_and_replacement'] = witness
    return output


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    result = {'reference': graph(), 'attacks': attacks(),
              'bounds': 'two domains; two local bits; one reserved resource; two contexts per domain; no depth cutoff',
              'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    parser.parse_args().output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['reference']))
