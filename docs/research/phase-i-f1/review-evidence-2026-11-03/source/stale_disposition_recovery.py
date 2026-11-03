#!/usr/bin/env python3
"""Stale empty-inventory decision across F1's abstract loss relation."""
from collections import Counter
import json
import phase_i_f1_model as f1


def run(name, create, recheck, transfer):
    state = f1.initial()
    owner = None  # None = no object yet; afterwards S or Q even if removed.
    saved_empty = None
    trace = []
    counts = Counter()

    def observe():
        return [] if owner is None or state.wu(owner).present else [f'z-unbounded:{owner}']

    def entry(kind, event, outcome, reason=None):
        counts[kind + '_' + outcome] += 1
        trace.append({'kind':kind, 'event':event, 'outcome':outcome, 'reason':reason,
                      'z_owner':owner, 'S_present':state.wu(f1.S).present,
                      'Q_present':state.wu(f1.Q).present,
                      'independent_violations':observe()})

    def f1_event(event):
        nonlocal state
        outcome, state, reason = f1.resolve(state, event, f1.REFERENCE)
        if f1.invariant(state, f1.REFERENCE):
            raise RuntimeError(('inherited invariant', event, f1.invariant(state, f1.REFERENCE)))
        entry('f1', event, outcome, reason)
        return outcome

    assert f1_event(('seal', f1.S)) == 'commit'
    saved_empty = owner != f1.S
    entry('wrapper', 'prepare_empty_inventory', 'commit')
    if create:
        assert state.wu(f1.S).present and state.wu(f1.S).sealed
        owner = f1.S
        entry('wrapper', 'authorized_create_unaccepted_z', 'commit')
    for event in (('stop',), ('recover_start',), ('recover_step', f1.P),
                  ('recover_step', f1.S), ('activate_image',)):
        assert f1_event(event) == 'commit'

    def remove():
        eligible = owner != f1.S if recheck else saved_empty
        if not eligible:
            entry('wrapper', 'remove_S_current_inventory', 'deny', 'dependent-z-present')
            return 'deny'
        return f1_event(('remove', f1.S))

    first = remove()
    if transfer:
        assert first == 'deny' and owner == f1.S and state.wu(f1.Q).present
        owner = f1.Q
        entry('wrapper', 'authorized_transfer_z_to_Q', 'commit')
        assert remove() == 'commit'
    return {'name':name, 'trace':trace, 'counts':dict(sorted(counts.items())),
            'first_remove':first, 'final_z_owner':owner,
            'final_violations':observe(), 'final_S_present':state.wu(f1.S).present}


def main():
    cases = [run('hazard_reference', True, True, False),
             run('hazard_stale_mutant', True, False, False),
             run('empty_reference', False, True, False),
             run('empty_stale_mutant', False, False, False),
             run('transfer_reference', True, True, True)]
    by_name = {c['name']:c for c in cases}
    assert by_name['hazard_reference']['first_remove'] == 'deny'
    assert not by_name['hazard_reference']['final_violations']
    assert by_name['hazard_stale_mutant']['first_remove'] == 'commit'
    assert by_name['hazard_stale_mutant']['final_violations'] == ['z-unbounded:S']
    assert all(by_name[n]['first_remove'] == 'commit' and not by_name[n]['final_violations']
               for n in ('empty_reference', 'empty_stale_mutant'))
    assert by_name['transfer_reference']['final_z_owner'] == f1.Q
    assert not by_name['transfer_reference']['final_S_present']
    assert not by_name['transfer_reference']['final_violations']
    totals = sum((Counter(c['counts']) for c in cases), Counter())
    print(json.dumps({'bounds':{'histories':len(cases), 'enumerated':False,
                                 'truncated':False, 'totals':dict(sorted(totals.items()))},
                      'cases':by_name}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
