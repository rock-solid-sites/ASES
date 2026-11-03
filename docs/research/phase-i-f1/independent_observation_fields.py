#!/usr/bin/env python3
"""Finite cross-product distinguishing individually lost C11 observations."""
from itertools import product, combinations
import json
import phase_i_f1_model as f1
import consumer_observation_continuity as prior

FIELDS, EVENTS = prior.FIELDS, prior.EVENTS


def run(values, erased):
    state = f1.initial()
    retained = values
    for event in EVENTS:
        outcome, state, reason = f1.resolve(state, event, f1.REFERENCE)
        if outcome != 'commit' or f1.invariant(state, f1.REFERENCE) is not None:
            raise RuntimeError((event, outcome, reason, f1.invariant(state, f1.REFERENCE)))
        if event[0] == 'stop' and erased is not None:
            retained = tuple(None if i == erased else v for i, v in enumerate(retained))
    observed = prior.query(state, retained, None)
    checks = {field: observed[field] == values[i] for i, field in enumerate(FIELDS)}
    return {'observed':observed, 'oracle_matches':checks, 'f1_state':repr(state)}


def main():
    worlds = {''.join(map(str, bits)): tuple(f'{field}-{bit}' for field, bit in zip(FIELDS, bits))
              for bits in product((0, 1), repeat=4)}
    variants = [('reference', None)] + [('erase_' + field, i) for i, field in enumerate(FIELDS)]
    results = {}
    for name, erased in variants:
        observations = {world:run(values, erased) for world, values in worlds.items()}
        collision_pairs = []
        for a, b in combinations(worlds, 2):
            if observations[a]['observed'] == observations[b]['observed']:
                collision_pairs.append([a, b])
        expected_pairs = 0 if erased is None else 8
        assert len(collision_pairs) == expected_pairs
        for a, b in collision_pairs:
            assert sum(x != y for x, y in zip(worlds[a], worlds[b])) == 1
            assert worlds[a][erased] != worlds[b][erased]
        mismatches = {field:sum(not v['oracle_matches'][field] for v in observations.values()) for field in FIELDS}
        assert all(mismatches[field] == (16 if i == erased else 0) for i, field in enumerate(FIELDS))
        assert all(v['observed']['accepted_x'] for v in observations.values())
        results[name] = {'field_mismatches':mismatches, 'collision_pairs':collision_pairs,
                         'observations':observations}
    assert len({v['f1_state'] for r in results.values() for v in r['observations'].values()}) == 1
    print(json.dumps({'bounds':{'worlds':len(worlds), 'variants':len(variants),
                                'fixed_histories':len(worlds)*len(variants),
                                'committed_f1_events':len(worlds)*len(variants)*len(EVENTS),
                                'transition_graph_enumerated':False, 'world_product_exhausted':True,
                                'truncated':False}, 'worlds':worlds, 'results':results}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
