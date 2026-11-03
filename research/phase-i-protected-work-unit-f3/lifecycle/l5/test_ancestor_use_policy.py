#!/usr/bin/env python3
"""Pure policy checks for ancestor attenuation; no host confinement claim."""
import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import l5_integrated as l5


def state():
    return {
        'schema': 1,
        'current_ingress': 'W-L5',
        'work_units': {
            'P': {'id': 'P', 'parent': None, 'active': True, 'sealed': False,
                  'grants': ['read', 'write']},
            'Q': {'id': 'Q', 'parent': None, 'active': True, 'sealed': False,
                  'grants': ['read', 'write']},
            'C': {'id': 'C', 'parent': 'Q', 'active': True, 'sealed': False,
                  'grants': ['read', 'write'], 'latent_ceiling': ['read']},
            'D': {'id': 'D', 'parent': 'C', 'depends_on': ['C'], 'active': True,
                  'sealed': False, 'grants': ['read', 'write'],
                  'latent_ceiling': ['read']},
        },
    }


def main():
    current = state()
    assert l5.enabled(current, 'D', 'W-L5')
    assert l5.permissions(current, 'D') == {'read'}
    assert 'read' in l5.permissions(current, 'D')
    assert 'write' not in l5.permissions(current, 'D')

    # Adversarial current authority record: D remains active while ancestor Q
    # is sealed/inactive. The frozen manager API cannot create this record;
    # this tests the mediator's fail-closed interpretation if it is presented.
    bad_ancestor = copy.deepcopy(current)
    bad_ancestor['work_units']['Q'].update(active=False, sealed=True)
    assert l5.graph_valid(bad_ancestor)
    assert not l5.enabled(bad_ancestor, 'D', 'W-L5')

    # The prior D-only guard would permit use on that same record.
    unsafe_mutant_allows = (
        l5.graph_valid(bad_ancestor)
        and bad_ancestor['current_ingress'] == 'W-L5'
        and bad_ancestor['work_units']['D']['active']
        and not bad_ancestor['work_units']['D']['sealed']
        and 'read' in l5.permissions(bad_ancestor, 'D')
    )
    assert unsafe_mutant_allows

    revoked_ancestor = copy.deepcopy(current)
    revoked_ancestor['work_units']['Q']['grants'] = []
    assert l5.enabled(revoked_ancestor, 'D', 'W-L5')
    assert 'read' not in l5.permissions(revoked_ancestor, 'D')
    assert 'write' not in l5.permissions(revoked_ancestor, 'D')

    # An ancestor that is merely inactive also blocks use, even if not sealed.
    inactive_ancestor = copy.deepcopy(current)
    inactive_ancestor['work_units']['C'].update(active=False, sealed=False)
    assert not l5.enabled(inactive_ancestor, 'D', 'W-L5')

    print('PASS: compliant positive use remains enabled with attenuated read-only rights')
    print('PASS: sealed/inactive ancestor blocks use despite active unsealed D')
    print('PASS: prior D-only policy admits the unsafe ancestor record (mutation detected)')
    print('PASS: ancestor grant revocation removes descendant read and write rights')
    print('PASS: inactive ancestor blocks use')
    print('LIMIT: ancestor-state adversarial record is not reachable through frozen manager operations')


if __name__ == '__main__':
    main()
