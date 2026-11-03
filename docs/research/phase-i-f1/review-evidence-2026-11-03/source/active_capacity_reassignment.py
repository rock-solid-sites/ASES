#!/usr/bin/env python3
"""Selected exclusive-use capacity policy around inherited F1 operations."""
from collections import Counter
from dataclasses import replace
import json
import phase_i_f1_model as f1


def run(name, start_s, recheck, complete):
    state = f1.initial()
    active = set()
    saved_quiet = None
    trace = []
    counts = Counter()

    def observe():
        errors = []
        if len(active) > 1:
            errors.append('active-use-exceeds-one-unit')
        if any(x != state.capacity_reserved for x in active):
            errors.append('active-use-without-current-reservation')
        return errors

    def log(kind, event, outcome, reason=None):
        counts[kind + '_' + outcome] += 1
        trace.append({'kind':kind, 'event':event, 'outcome':outcome, 'reason':reason,
                      'reservation':state.capacity_reserved, 'consumed':state.capacity_consumed,
                      'active':sorted(active), 'independent_violations':observe()})

    def f1_event(event):
        nonlocal state
        outcome, state, reason = f1.resolve(state, event, f1.REFERENCE)
        if f1.invariant(state, f1.REFERENCE):
            raise RuntimeError((event, f1.invariant(state, f1.REFERENCE)))
        if outcome == 'commit' and event[0] == 'consume_capacity':
            active.add(event[1])
        log('f1', event, outcome, reason)
        return outcome

    assert f1_event(('reserve_capacity', f1.S)) == 'commit'
    saved_quiet = not active
    log('wrapper', 'prepare_reassignment_while_quiet', 'commit')
    if start_s:
        assert f1_event(('consume_capacity', f1.S)) == 'commit'
    for event in (('stop',), ('recover_start',), ('recover_step', f1.P),
                  ('recover_step', f1.S), ('activate_image',)):
        assert f1_event(event) == 'commit'
    if complete:
        assert f1.S in active and state.capacity_reserved == f1.S
        active.remove(f1.S)
        state = replace(state, capacity_consumed=False)
        log('wrapper', 'complete_S_use', 'commit')
    eligible = not active if recheck else saved_quiet
    if eligible:
        assert state.capacity_reserved == f1.S
        state = replace(state, capacity_reserved=f1.C, capacity_consumed=False)
        assert f1.invariant(state, f1.REFERENCE) is None
        log('wrapper', 'reassign_S_to_C', 'commit')
    else:
        log('wrapper', 'reassign_S_to_C', 'deny', 'active-S-use')
    c_result = f1_event(('consume_capacity', f1.C))
    return {'name':name, 'trace':trace, 'counts':dict(sorted(counts.items())),
            'C_consume':c_result, 'final_violations':observe()}


def main():
    cases = [run('hazard_reference', True, True, False),
             run('hazard_stale_mutant', True, False, False),
             run('completed_reference', True, True, True),
             run('quiet_reference', False, True, False)]
    by_name = {c['name']:c for c in cases}
    assert by_name['hazard_reference']['C_consume'] == 'deny'
    assert not by_name['hazard_reference']['final_violations']
    assert by_name['hazard_stale_mutant']['C_consume'] == 'commit'
    assert 'active-use-exceeds-one-unit' in by_name['hazard_stale_mutant']['final_violations']
    for name in ('completed_reference', 'quiet_reference'):
        assert by_name[name]['C_consume'] == 'commit' and not by_name[name]['final_violations']
    totals = sum((Counter(c['counts']) for c in cases), Counter())
    print(json.dumps({'bounds':{'histories':len(cases), 'enumerated':False, 'truncated':False,
                                 'totals':dict(sorted(totals.items()))},
                      'cases':by_name}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
