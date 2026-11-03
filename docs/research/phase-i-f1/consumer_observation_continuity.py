#!/usr/bin/env python3
"""C11 finite distinguishability witness around F1's existing loss transitions."""
import json
import phase_i_f1_model as f1

FIELDS = ('identity_genesis', 'created_by', 'project', 'consumer_evidence')
WORLDS = {
    'A': ('work-A', 'creator-A', 'project-A', 'evidence-A'),
    'B': ('work-B', 'creator-B', 'project-B', 'evidence-B'),
}
EVENTS = (("grant", f1.P, f1.SINK, f1.RW), ("grant", f1.C, f1.SINK, f1.RW),
          ("accept_x", f1.C, f1.B_GEN), ("stop",), ("recover_start",),
          ("recover_step", f1.P), ("recover_step", f1.C), ("activate_image",))


def query(state, retained, display_cache):
    # The display cache is deliberately irrelevant to these declared observations.
    del display_cache
    values = dict(zip(FIELDS, retained)) if retained is not None else {k: None for k in FIELDS}
    return {'accepted_x':state.accepted_x, **values}


def history(world, retain):
    state = f1.initial()
    retained = WORLDS[world]
    expected = dict(zip(FIELDS, WORLDS[world]))  # external pre-loss observer only
    trace = []
    before_loss = None
    for event in EVENTS:
        if event[0] == 'stop':
            before_loss = query(state, retained, 'cached-display')
        outcome, state, reason = f1.resolve(state, event, f1.REFERENCE)
        if outcome != 'commit' or f1.invariant(state, f1.REFERENCE):
            raise RuntimeError((event, outcome, reason, f1.invariant(state, f1.REFERENCE)))
        if event[0] == 'stop' and not retain:
            retained = None
        trace.append({'event':event, 'outcome':outcome, 'reason':reason,
                      'accepted_x':state.accepted_x, 'engine':state.engine, 'image':state.image})
    recovered = query(state, retained, None)
    checks = {field: recovered[field] == expected[field] for field in FIELDS}
    return {'trace':trace, 'pre_loss_query':before_loss, 'recovered_query':recovered,
            'oracle_field_matches':checks, 'cache_drop_preserves_query':
            query(state, retained, 'cached-display') == recovered,
            'f1_final_state': repr(state)}


def main():
    results = {variant: {world: history(world, retain) for world in WORLDS}
               for variant, retain in [('reference', True), ('bytes_only_mutant', False)]}
    for world in WORLDS:
        assert all(results['reference'][world]['oracle_field_matches'].values())
        assert not any(results['bytes_only_mutant'][world]['oracle_field_matches'].values())
        assert results['reference'][world]['recovered_query']['accepted_x']
        assert results['bytes_only_mutant'][world]['recovered_query']['accepted_x']
        assert results['reference'][world]['f1_final_state'] == results['bytes_only_mutant'][world]['f1_final_state']
        assert all(results[v][world]['cache_drop_preserves_query'] for v in results)
    assert results['reference']['A']['recovered_query'] != results['reference']['B']['recovered_query']
    assert results['bytes_only_mutant']['A']['recovered_query'] == results['bytes_only_mutant']['B']['recovered_query']
    assert results['reference']['A']['f1_final_state'] == results['reference']['B']['f1_final_state']
    print(json.dumps({'bounds':{'histories':4, 'events_per_history':len(EVENTS),
                                'total_committed_events':4*len(EVENTS),
                                'enumerated':False, 'truncated':False}, 'results':results}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
