#!/usr/bin/env python3
"""Execute the preregistered disposable-record manager currentness probe."""
import copy
import hashlib
import json
import tempfile
from pathlib import Path
import socket

import l5_integrated as l5


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initial_state():
    return {
        'schema': 1,
        'events': [{'op': 'bootstrap'}],
        'current_ingress': None,
        'work_units': {
            'P': {'id': 'P', 'parent': None, 'active': False, 'sealed': True,
                  'grants': ['read']},
            'C': {'id': 'C', 'parent': 'P', 'active': False, 'sealed': True,
                  'grants': ['read', 'write']},
            'Q': {'id': 'Q', 'parent': None, 'active': False, 'sealed': True,
                  'grants': ['read', 'write']},
            'D': {'id': 'D', 'parent': 'C', 'depends_on': ['C'], 'active': False,
                  'sealed': True, 'grants': ['read', 'write']},
        },
    }


def call(root, state, request):
    client, server = socket.socketpair()
    try:
        _, response = l5.manager_roundtrip(client, server, request, state, root)
        wire_response = json.loads(client.makefile('rb', buffering=0).readline())
        assert wire_response == response
        return response
    finally:
        client.close()
        server.close()


def main():
    trace = {'preregistration': 'MANAGEMENT-CURRENTNESS-PREREGISTRATION.md', 'steps': []}
    with tempfile.TemporaryDirectory(prefix='ases-manager-currentness-') as td:
        root = Path(td)
        protected = root / 'protected'
        protected.mkdir()
        current = initial_state()
        initial_record = protected / 'record-000001.json'
        initial_record.write_text(json.dumps(current, sort_keys=True, separators=(',', ':')) + '\n')
        (protected / 'CURRENT').write_text(initial_record.name + '\n')
        stale0 = copy.deepcopy(current)
        trace['steps'].append({'step': 'bootstrap', 'record': initial_record.name,
                               'sha256': digest(initial_record)})

        moved = call(root, current, {'op': 'authorize_move', 'authorized_by': 'initial-manager',
                                     'credential': l5.CREDENTIAL, 'child': 'C', 'destination': 'Q'})
        assert moved['result'] == 'COMMITTED', moved
        moved_name, moved_state = l5.load_current(root)
        moved_path = protected / moved_name
        trace['steps'].append({'step': 'fresh_authorized_move', 'response': moved,
                               'record': moved_name, 'sha256': digest(moved_path),
                               'parent_C': moved_state['work_units']['C']['parent'],
                               'current_ingress': moved_state['current_ingress']})

        activated = call(root, moved_state, {'op': 'authorize_activate',
                                             'authorized_by': 'initial-manager',
                                             'credential': l5.CREDENTIAL})
        assert activated['result'] == 'COMMITTED', activated
        active_name, active_state = l5.load_current(root)
        active_path = protected / active_name
        assert active_name != moved_name and digest(active_path) != digest(moved_path)
        trace['steps'].append({'step': 'fresh_authorized_activation', 'response': activated,
                               'record': active_name, 'sha256': digest(active_path),
                               'parent_C': active_state['work_units']['C']['parent'],
                               'current_ingress': active_state['current_ingress'],
                               'activation_events': [e for e in active_state['events']
                                                    if e.get('op') == 'separately-authorized_activation']})

        selector_before = (protected / 'CURRENT').read_text()
        current_bytes_before = active_path.read_bytes()
        stale_response = call(root, stale0, {'op': 'authorize_move',
                                             'authorized_by': 'initial-manager',
                                             'credential': l5.CREDENTIAL,
                                             'child': 'C', 'destination': 'Q'})
        selected_after, selected_state = l5.load_current(root)
        selector_after = (protected / 'CURRENT').read_text()
        selected_path = protected / selected_after.strip()
        trace['steps'].append({'step': 'stale_authorized_move_replay', 'response': stale_response,
                               'selector_before': selector_before.strip(),
                               'selector_after': selector_after.strip(),
                               'selected_record': selected_after,
                               'selected_sha256': digest(selected_path),
                               'previous_current_sha256': hashlib.sha256(current_bytes_before).hexdigest(),
                               'selected_parent_C': selected_state['work_units']['C']['parent'],
                               'selected_current_ingress': selected_state['current_ingress'],
                               'selected_event_ops': [e.get('op') for e in selected_state['events']]})
        trace['decision'] = {
            'fresh_current_positive_pass': moved['result'] == 'COMMITTED' and activated['result'] == 'COMMITTED',
            'expected_stale_denial': stale_response['result'] == 'DENY' and selector_after == selector_before,
            'observed_selector_unchanged': selector_after == selector_before,
            'invariant_counterexample': stale_response['result'] == 'COMMITTED' and selected_after != active_name,
            'qualification': 'assumption-stress only: direct harness retained and resubmitted an old state object; no in-profile caller path established',
        }
        trace['bounds'] = {'manager_calls': 3, 'successful_transitions_before_replay': 2,
                           'record_root': 'temporary directory', 'worker': False,
                           'host_confinement': False}

    out = Path(__file__).with_name('management-currentness-raw.json')
    out.write_text(json.dumps(trace, sort_keys=True, indent=2) + '\n')
    print(json.dumps(trace, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
