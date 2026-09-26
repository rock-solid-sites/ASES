#!/usr/bin/env python3
"""Negative generalization witnesses and finite sanity checks, NOT an unbounded proof."""
import argparse
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path


def acyclic(vertices, edges):
    remaining = set(vertices)
    while remaining:
        ready = {v for v in remaining if not any(a in remaining and b == v for a, b in edges)}
        if not ready:
            return False
        remaining -= ready
    return True


def run():
    vertices = tuple(range(4))
    cycle = {(0, 1), (1, 2), (2, 3), (3, 0)}
    triples = list(combinations(vertices, 3))
    assert not acyclic(vertices, cycle)
    assert all(acyclic(vs, {(a, b) for a, b in cycle if a in vs and b in vs}) for vs in triples)
    reuse = []
    for size in range(1, 9):
        labels = [n % size for n in range(size + 1)]
        assert labels[0] == labels[-1]
        reuse.append({'admission_alphabet_size': size, 'successive_grants': labels,
                      'old_retained_observation': labels[0], 'new_current_observation': labels[-1]})
    parents = {1: 0, 2: 1}
    active = {0, 1, 2}
    one_hop = active - {0} - {child for child, parent in parents.items() if parent == 0}
    assert one_hop == {2}
    removed = {0}
    while True:
        larger = removed | {child for child, parent in parents.items() if parent in removed}
        if larger == removed:
            break
        removed = larger
    assert not active - removed
    commutations = 0
    for width in range(2, 6):
        for state in product((0, 1), repeat=width):
            for a, b in combinations(range(width), 2):
                def flip(s, i):
                    return s[:i] + (1-s[i],) + s[i+1:]
                assert flip(flip(state, a), b) == flip(flip(state, b), a)
                commutations += 1
    return {'four_cycle_not_detected_by_all_triples': {'edges': sorted(cycle), 'triples': triples},
            'finite_label_wraparound': reuse,
            'one_hop_delegation_does_not_generalize': {'parents': parents, 'remaining': sorted(one_hop)},
            'disjoint_field_commutation_sanity_cases': commutations,
            'qualification': 'bounded checks support examples; parametric hand arguments are in Generalization.md',
            'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    result = run()
    parser.parse_args().output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'negative_families': 3, 'commutation_sanity_cases': result['disjoint_field_commutation_sanity_cases']}))
