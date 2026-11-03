#!/usr/bin/env python3
"""Bounded paired-state falsification of a declared observation style."""
from dataclasses import asdict
from pathlib import Path
import json, resource, sys, time
started = time.monotonic()
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import timing_event_model as t
m = t.model
results = []
for p in t.PROFILES[:2]:
    root = m.established((0, 7), p=p)
    independent, a = m.resolve(root, m.Request('grant', target=3, value=1), p)
    dependent, b = m.resolve(root, m.Request('delegate', evidence=0, target=3, value=1), p)
    assert (a, b) == ('commit', 'commit')
    assert independent != dependent and m.invariant(independent, p) and m.invariant(dependent, p)
    assert all(getattr(independent, f) == getattr(dependent, f) for f in t.FIELDS if f != 'parents')
    q = m.Request('restrict', target=0, value=0)
    assert q in t.CATALOG
    styles = [t.minimal_style(q, s) for s in (independent, dependent)]
    outputs = [m.resolve(s, q, p) for s in (independent, dependent)]
    assert styles[0] == styles[1] and 'parents' not in styles[0]
    assert t.project(independent, styles[0]) == t.project(dependent, styles[0])
    assert t.project(independent, t.ALL_FIELDS) != t.project(dependent, t.ALL_FIELDS)
    assert [o for _, o in outputs] == ['commit', 'commit']
    assert outputs[0][0].rights[3] == 1 and outputs[1][0].rights[3] == 0
    assert t.project(outputs[0][0], styles[0]) != t.project(outputs[1][0], styles[0])
    results.append({'profile': p.name, 'request': asdict(q), 'declared_style': sorted(styles[0]),
      'before': [asdict(independent), asdict(dependent)],
      'outcome': [o for _, o in outputs], 'after': [asdict(s) for s, _ in outputs],
      'same_style_input': True, 'different_full_input': True, 'different_style_successor': True})
assert 2 * len(results) <= 100
print(json.dumps({'elapsed_seconds': time.monotonic() - started,
 'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'status':'PASS', 'pairs':len(results), 'legal_input_states':2*len(results),
 'resolutions_under_test':2*len(results), 'state_cap':100,
 'claim':'the fixture disproves sufficiency of the declared style for these states and request',
 'results':results}, sort_keys=True))
