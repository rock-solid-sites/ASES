#!/usr/bin/env python3
"""Finite logical capture/publication cut graphs; no physical timing model."""
import argparse
from collections import deque
from dataclasses import asdict, replace
from pathlib import Path
import json, resource, sys, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m = t.model
p = t.PROFILES[0]
base = m.established((0, 7), p=p)
offers = (m.Request('pair', evidence=0, value=0), m.Request('pair', evidence=0, value=3))
assert all(q in t.CATALOG for q in offers)
assert base.data == (0, 0)
whole, outcome = m.resolve(base, offers[1], p)
assert outcome == 'commit' and whole.data == (1, 1)
assert m.resolve(base, offers[0], p) == (base, 'commit')


def successors(mode, s):
    stage = s[0]
    if mode == 'whole_capture':
        if stage == 'start': return [('captured', q.value) for q in offers]
        if stage == 'captured': return [('published', s[1])]
    if mode == 'mixed_capture':
        if stage == 'start': return [('low', q.value & 1) for q in offers]
        if stage == 'low': return [('captured', s[1] | (q.value & 2)) for q in offers]
        if stage == 'captured': return [('published', s[1])]
    if mode in ('whole_publication', 'split_publication'):
        if stage == 'start': return [('candidate',)]
        if stage == 'candidate':
            if mode == 'whole_publication': return [('published',)]
            return [('partial',0), ('partial',1)]
        if stage == 'partial': return [('published',)]
    return []


def observation(mode, s):
    """Each graph state is an observation cut; candidate remains unexposed."""
    if mode.endswith('capture'):
        if s[0] != 'published': return {'view':asdict(base), 'valid':True}
        q = m.Request('pair', evidence=0, value=s[1])
        assert q in t.CATALOG
        out, kind = m.resolve(base, q, p)
        assert kind == 'commit'
        valid = any(q == offered and (out, kind) == m.resolve(base, offered, p)
                    for offered in offers)
        return {'view':asdict(out), 'proposal_value':q.value, 'offered':q in offers, 'valid':valid}
    if s[0] == 'published': view = whole
    elif s[0] == 'partial':
        data = list(base.data); data[s[1]] = whole.data[s[1]]
        view = replace(base, data=tuple(data))
        assert m.invariant(view, p)  # State validity alone cannot establish whole publication.
    else: view = base
    return {'view':asdict(view), 'valid':view in (base, whole)}


def explore(mode, budget):
    root = ('start',)
    if budget < 1:
        return {'status':'incomplete', 'reason':'state_cap', 'next_graph_root':list(root),
                'states':0, 'transitions':0, 'cut_count':0}
    seen = {root}; queue = deque([root]); transitions = 0; cuts = []
    while queue:
        s = queue.popleft()
        cut = observation(mode, s)
        cuts.append({'state':list(s), **cut})
        for nxt in successors(mode,s):
            if nxt not in seen and len(seen) >= budget:
                return {'status':'incomplete', 'reason':'state_cap', 'states':len(seen),
                    'transitions':transitions, 'cut_count':len(cuts), 'processed_state':list(s),
                    'rejected_next_state':list(nxt), 'queued_states':len(queue)}
            transitions += 1
            if nxt not in seen:
                seen.add(nxt); queue.append(nxt)
    violations = [c for c in cuts if not c['valid']]
    return {'status':'complete','states':len(seen),'transitions':transitions,
            'cut_count':len(cuts),'violating_cut_count':len(violations),
            'violating_cuts':violations, 'cuts':cuts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-cap', type=int, default=1000)
    args = parser.parse_args()
    if not 1 <= args.state_cap <= 1000: parser.error('state cap must be in 1..1000')
    started = time.monotonic(); used = 0; results = {}
    for mode in ('whole_capture','mixed_capture','whole_publication','split_publication'):
        result = explore(mode, args.state_cap - used)
        results[mode] = result; used += result['states']
        if result['status'] != 'complete':
            print(json.dumps({'status':'incomplete','state_cap':args.state_cap,
                  'states_discovered':used,'stopped_graph':mode,'graphs':results},sort_keys=True))
            return 2
    assert results['whole_capture']['violating_cut_count'] == 0
    assert {x['proposal_value'] for x in results['mixed_capture']['violating_cuts']} == {1,2}
    assert results['whole_publication']['violating_cut_count'] == 0
    assert {tuple(x['view']['data']) for x in results['split_publication']['violating_cuts']} == {(1,0),(0,1)}
    print(json.dumps({'status':'complete_bounded_fixture', 'state_cap':args.state_cap,
        'states_discovered':used,'transitions':sum(v['transitions'] for v in results.values()),
        'cuts':sum(v['cut_count'] for v in results.values()), 'graphs':results,
        'elapsed_seconds':time.monotonic()-started,
        'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope':'logical cut abstraction, not physical timing or a global contract'},sort_keys=True))
    return 0
if __name__ == '__main__': raise SystemExit(main())
