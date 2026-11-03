#!/usr/bin/env python3
"""Bounded finite paired-state observational oracle; no global sufficiency claim."""
import argparse
from dataclasses import replace
from itertools import combinations
from pathlib import Path
import json, resource, sys, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m = t.model

def old_style(q, s, p):
    """Preserved unsafe control: the inherited parent perturbation changes nothing."""
    out, kind = m.resolve(s, q, p)
    kept = set()
    for field in t.types(q)['reads'] | t.types(q)['writes']:
        alt = replace(s, **{field:t._other_value(getattr(s, field))})
        other, other_kind = m.resolve(alt, q, p)
        if other_kind != kind or t.encode_word(other) != t.encode_word(out):
            kept.add(field)
    return frozenset(kept)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--states-per-profile', type=int, choices=(4, 6), required=True)
    parser.add_argument('--pair-case-cap', type=int, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    masks = {'unsafe_rights':frozenset({'rights'}), 'rights_parents':frozenset({'rights','parents'}),
             'rights_parents_data':frozenset({'rights','parents','data'})}
    requests = [m.Request('restrict', target=0, value=0), m.Request('set', evidence=0, target=0, value=1)]
    assert all(q in t.CATALOG for q in requests)
    counters = {name:{'pair_cases':0,'same_projection':0,'mismatches':0, 'examples':[]} for name in masks}
    controls = []
    evaluated = states_seen = 0
    for p in t.PROFILES[:2]:
        root = m.established((0,7), p=p)
        independent, a = m.resolve(root, m.Request('grant',target=3,value=1), p)
        dependent, b = m.resolve(root, m.Request('delegate',evidence=0,target=3,value=1), p)
        assert (a,b) == ('commit','commit')
        states = [independent, dependent, replace(independent,content=1), replace(dependent,content=1),
                  replace(independent,data=(0,1)), replace(dependent,data=(0,1))][:args.states_per_profile]
        assert len(set(states)) == len(states) and all(m.invariant(s,p) for s in states)
        states_seen += len(states)
        q = requests[0]
        old = [old_style(q,s,p) for s in states[:2]]
        fixed = [t.minimal_style(q,s,p) for s in states[:2]]
        assert all('parents' not in x for x in old) and all('parents' in x for x in fixed)
        controls.append({'profile':p.name,'old_styles':[sorted(x) for x in old],
                         'fixed_styles':[sorted(x) for x in fixed]})
        for (i,s),(j,v) in combinations(enumerate(states),2):
            for q in requests:
                # Independently specified observation oracle: same visible pre-state
                # must determine outcome and visible whole successor for fixed q.
                out1, kind1 = m.resolve(s,q,p)
                out2, kind2 = m.resolve(v,q,p)
                for name, mask in masks.items():
                    if evaluated >= args.pair_case_cap:
                        raise SystemExit(json.dumps({'status':'incomplete','reason':'pair_case_cap',
                          'completed_pair_cases':evaluated,'next':[p.name,i,j,q.label(),name]}))
                    evaluated += 1
                    c = counters[name]; c['pair_cases'] += 1
                    if t.project(s,mask) != t.project(v,mask):
                        continue
                    c['same_projection'] += 1
                    if (kind1,t.project(out1,mask)) != (kind2,t.project(out2,mask)):
                        c['mismatches'] += 1
                        if len(c['examples']) < 3:
                            c['examples'].append({'profile':p.name,'pair':[i,j], 'request':q.label(),
                                                  'outcomes':[kind1,kind2],
                                                  'visible_successors':[t.project(out1,mask),t.project(out2,mask)]})
    assert counters['unsafe_rights']['mismatches'] > 0
    assert counters['rights_parents_data']['same_projection'] > 0 and counters['rights_parents_data']['mismatches'] == 0
    if args.states_per_profile == 4:
        assert counters['rights_parents']['mismatches'] == 0
    else:
        assert counters['rights_parents']['mismatches'] > 0
    print(json.dumps({'status':'complete_bounded_fixture','source_revision':'0be418c77',
        'profiles':['independent','coupled'],'states_per_profile':args.states_per_profile,
        'state_count':states_seen,'requests':len(requests),'masks':{k:sorted(v) for k,v in masks.items()},
        'pair_case_cap':args.pair_case_cap,'pair_cases_completed':evaluated,'counters':counters,
        'old_and_repaired_control':controls,'elapsed_seconds':time.monotonic()-started,
        'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'limit':'finite fixture and two requests only; not proof of global mask sufficiency'},sort_keys=True))
if __name__ == '__main__': main()
