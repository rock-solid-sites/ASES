#!/usr/bin/env python3
"""Manager current-record and activation guards; disposable records only."""
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
import socket

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import l5_integrated as l5


def state(parent='P', parent_grants=None):
    return {
        'schema': 1,
        'events': [{'op': 'bootstrap'}],
        'current_ingress': None,
        'work_units': {
            'P': {'id': 'P', 'parent': None, 'active': False, 'sealed': True,
                  'grants': parent_grants or ['read']},
            'C': {'id': 'C', 'parent': parent, 'active': False, 'sealed': True,
                  'grants': ['read', 'write']},
            'Q': {'id': 'Q', 'parent': None, 'active': False, 'sealed': True,
                  'grants': ['read', 'write']},
            'D': {'id': 'D', 'parent': 'C', 'depends_on': ['C'], 'active': False,
                  'sealed': True, 'grants': ['read', 'write']},
        },
    }


def publish(root, st, name='record-000001.json'):
    protected = root / 'protected'
    protected.mkdir(exist_ok=True)
    path = protected / name
    path.write_text(json.dumps(st, sort_keys=True, separators=(',', ':')) + '\n')
    (protected / 'CURRENT').write_text(name + '\n')
    return path


def snapshot(root):
    return {p.name: p.read_bytes() for p in sorted((root / 'protected').iterdir())}


def snapshot_hash(data):
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}
    return hashes, hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def call(root, st, op, credential=None, **kw):
    client, server = socket.socketpair()
    try:
        request = {'op': op, 'authorized_by': 'initial-manager',
                   'credential': credential if credential is not None else l5.CREDENTIAL, **kw}
        _, response = l5.manager_roundtrip(client, server, request, st, root)
        assert json.loads(client.makefile('rb', buffering=0).readline()) == response
        return response
    finally:
        client.close()
        server.close()


def main():
    trace = {'preregistration': 'MANAGEMENT-CONFORMANCE-PREREGISTRATION.md', 'steps': []}
    # Fresh authorized move and activation establish two distinct current records.
    with tempfile.TemporaryDirectory(prefix='ases-manager-fresh-') as td:
        root = Path(td)
        current = state(parent_grants=['read', 'write'])
        publish(root, current)
        stale = copy.deepcopy(current)
        trace['steps'].append({'case': 'fresh', 'step': 'bootstrap', 'record': 'record-000001.json',
                               'store_hashes': snapshot_hash(snapshot(root))[0]})
        moved = call(root, current, 'authorize_move', child='C', destination='Q')
        assert moved['result'] == 'COMMITTED'
        name, current = l5.load_current(root)
        assert name == moved['record']
        activated = call(root, current, 'authorize_activate')
        assert activated['result'] == 'COMMITTED'
        active_name, active = l5.load_current(root)
        assert active_name != name and active['current_ingress'] == 'W-L5'
        assert active['events'][-1]['op'] == 'separately-authorized_activation'
        trace['steps'].append({'case': 'fresh', 'step': 'move', 'response': moved,
                               'record': name, 'record_sha256': hashlib.sha256((root / 'protected' / name).read_bytes()).hexdigest()})
        trace['steps'].append({'case': 'fresh', 'step': 'activation', 'response': activated,
                               'record': active_name, 'record_sha256': hashlib.sha256((root / 'protected' / active_name).read_bytes()).hexdigest(),
                               'current_ingress': active['current_ingress'], 'last_event': active['events'][-1]})
        print('PASS: fresh move and activation commit through manager as distinct records')

        before = snapshot(root)
        before_hashes, before_hash = snapshot_hash(before)
        stale_reply = call(root, stale, 'authorize_move', child='C', destination='Q')
        assert stale_reply == {'result': 'DENY', 'reason': 'management-state-not-current'}
        after = snapshot(root)
        after_hashes, after_hash = snapshot_hash(after)
        assert before == after
        trace['steps'].append({'case': 'stale', 'response': stale_reply,
                               'selector_before': before['CURRENT'].decode().strip(),
                               'selector_after': after['CURRENT'].decode().strip(),
                               'store_hash_before': before_hash, 'store_hash_after': after_hash,
                               'byte_identical': before_hashes == after_hashes})
        print('PASS: stale authentic state denied; selector and all stored bytes unchanged')

        before = snapshot(root)
        before_hashes, before_hash = snapshot_hash(before)
        wrong_credential = call(root, active, 'authorize_activate', credential='wrong')
        assert wrong_credential == {'result': 'DENY', 'reason': 'management-authorization-required'}
        after_hashes, after_hash = snapshot_hash(snapshot(root))
        assert before == snapshot(root)
        trace['steps'].append({'case': 'wrong_credential', 'response': wrong_credential,
                               'store_hash_before': before_hash, 'store_hash_after': after_hash,
                               'byte_identical': before_hashes == after_hashes})
        print('PASS: wrong credential denied; selector and all stored bytes unchanged')

    # Malformed current authority fixture: C is moved but Q is unsealed while
    # every unit remains inactive. This is an input precondition test, not a
    # claimed reachable manager transition.
    with tempfile.TemporaryDirectory(prefix='ases-manager-unsealed-') as td:
        root = Path(td)
        malformed = state(parent='Q')
        malformed['work_units']['Q']['sealed'] = False
        publish(root, malformed)
        before = snapshot(root)
        before_hashes, before_hash = snapshot_hash(before)
        response = call(root, malformed, 'authorize_activate')
        assert response == {'result': 'DENY', 'reason': 'activation-requires-current-inactive-sealed-state'}
        after_hashes, after_hash = snapshot_hash(snapshot(root))
        assert before == snapshot(root)
        trace['steps'].append({'case': 'unsealed_fixture', 'response': response,
                               'store_hash_before': before_hash, 'store_hash_after': after_hash,
                               'byte_identical': before_hashes == after_hashes,
                               'reachable_through_manager': False})
        print('PASS: unsealed activation input denied; selector and store unchanged')
        print('LIMIT: unsealed fixture is directly published and is not a manager-reachable history')

    trace['decision'] = {'fresh_activation_through_manager': True,
                         'stale_state_denied_without_store_change': True,
                         'wrong_credential_denied_without_store_change': True,
                         'unsealed_activation_denied_without_store_change': True,
                         'concurrency_claim': 'none; check-then-commit assumes serialized single holder'}
    Path(__file__).with_name('management-conformance-raw.json').write_text(
        json.dumps(trace, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    main()
