#!/usr/bin/env python3
"""Bounded manager grant checks; no live worker or host-confinement claim."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import tempfile
import l5_integrated as l5
import test_management_conformance as fixture

HERE = Path(__file__).resolve().parent
X = b'accepted-post-move-content\x00\n'


def files(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def setup(root):
    st = fixture.state(parent='P', parent_grants=['read'])
    meta = {'identity':'accepted-x', 'object':'objects/x.bin',
            'sha256':hashlib.sha256(X).hexdigest(), 'size':len(X)}
    st['work_units']['C']['accepted_contents'] = [meta]
    st['work_units']['D']['accepted_contents'] = []
    fixture.publish(root, st)
    objects = root / 'protected' / 'objects'
    objects.mkdir()
    (objects / 'x.bin').write_bytes(X)
    return st, meta


def request(module, root, st, op, **kw):
    req = {'op':op, 'authorized_by':'initial-manager', 'credential':module.CREDENTIAL, **kw}
    client, server = socket.socketpair()
    try:
        _, reply = module.manager_roundtrip(client, server, req, st, root)
        assert json.loads(client.makefile('rb', buffering=0).readline()) == reply
        return req, reply
    finally:
        client.close(); server.close()


def assert_content(module, root, st, meta):
    assert st['work_units']['C']['id'] == 'C'
    assert st['work_units']['D']['parent'] == 'C'
    assert st['work_units']['C']['accepted_contents'][0] == meta
    assert module.verified_content(root, meta) == X


def active_observation(module, root, st):
    with tempfile.TemporaryDirectory(prefix='f3-grant-activate-') as td:
        copied = Path(td) / 'case'
        shutil.copytree(root, copied)
        candidate = copy.deepcopy(st)
        req, response = request(module, copied, candidate, 'authorize_activate')
        assert response['result'] == 'COMMITTED'
        _, published = module.load_current(copied)
        rights = sorted(module.permissions(published, 'D'))
        current = module.enabled(published, 'D', 'W-L5')
        stale = module.enabled(published, 'D', 'W-old')
        return {'request':req, 'activation':response, 'rights':rights,
                'read_allowed':current and 'read' in rights,
                'write_allowed':current and 'write' in rights,
                'old_ingress_read_allowed':stale and 'read' in rights,
                'old_ingress_write_allowed':stale and 'write' in rights,
                'selected_record':published}


def deny_case(name, mutate, request_kwargs, expected):
    with tempfile.TemporaryDirectory(prefix='f3-grant-deny-') as td:
        root = Path(td); st, meta = setup(root)
        _, moved = request(l5, root, st, 'authorize_move', child='C', destination='Q')
        assert moved['result'] == 'COMMITTED'
        mutate(root, st)
        before_files = files(root); before_state = copy.deepcopy(st)
        req, response = request(l5, root, st, 'authorize_grant', **request_kwargs)
        assert response == {'result':'DENY', 'reason':expected}
        assert before_files == files(root) and before_state == st
        assert_content(l5, root, st, meta)
        return {'case':name, 'request':req, 'response':response,
                'store_before':before_files, 'store_after':files(root),
                'state_unchanged':before_state == st}


def publish_change(root, st):
    l5.commit(root, st, {'op':'test-fixture-input'})


def main():
    cases = []
    common = {'unit':'C', 'capability':'write'}
    no_op = lambda root, st: None
    cases.append(deny_case('bad_credential', no_op, {**common, 'credential':'wrong'}, 'management-authorization-required'))
    cases.append(deny_case('bad_principal', no_op, {**common, 'authorized_by':'wrong'}, 'management-authorization-required'))
    cases.append(deny_case('D_before_C', no_op, {'unit':'D','capability':'write'}, 'grant-not-supported-by-current-path'))
    cases.append(deny_case('unsupported_unit', no_op, {'unit':'P','capability':'write'}, 'unsupported-grant'))
    cases.append(deny_case('unsupported_capability', no_op, {'unit':'C','capability':'execute'}, 'unsupported-grant'))
    def no_parent(root, st):
        st['work_units']['Q']['grants'] = ['read']; publish_change(root, st)
    def no_local(root, st):
        st['work_units']['C']['grants'] = ['read']; publish_change(root, st)
    def unsealed(root, st):
        st['work_units']['Q']['sealed'] = False; publish_change(root, st)
    def active(root, st):
        _, response = request(l5, root, st, 'authorize_activate')
        assert response['result'] == 'COMMITTED'
    def stale(root, st):
        other = copy.deepcopy(st); publish_change(root, other)
    def already_granted(root, st):
        _, response = request(l5, root, st, 'authorize_grant', **common)
        assert response['result'] == 'COMMITTED'
    for name, mutation, reason in [('no_parent_write',no_parent,'grant-not-supported-by-current-path'),
                                   ('no_target_local_write',no_local,'grant-not-supported-by-current-path'),
                                   ('unsealed',unsealed,'grant-requires-current-inactive-sealed-moved-state'),
                                   ('active',active,'grant-requires-current-inactive-sealed-moved-state'),
                                   ('stale_record',stale,'management-state-not-current'),
                                   ('already_granted',already_granted,'grant-not-supported-by-current-path')]:
        cases.append(deny_case(name, mutation, common, reason))

    with tempfile.TemporaryDirectory(prefix='f3-grant-positive-') as td:
        root = Path(td); st, meta = setup(root)
        _, move = request(l5, root, st, 'authorize_move', child='C', destination='Q')
        assert move['result'] == 'COMMITTED'
        assert_content(l5, root, st, meta)
        move_only = active_observation(l5, root, st)
        assert move_only['read_allowed'] and not move_only['write_allowed'] and not move_only['old_ingress_read_allowed']
        req_c, grant_c = request(l5, root, st, 'authorize_grant', **common)
        assert grant_c['result'] == 'COMMITTED'
        assert st['work_units']['D']['latent_ceiling'] == ['read']
        assert_content(l5, root, st, meta)
        c_only = active_observation(l5, root, st)
        assert c_only['read_allowed'] and not c_only['write_allowed']
        req_d, grant_d = request(l5, root, st, 'authorize_grant', unit='D', capability='write')
        assert grant_d['result'] == 'COMMITTED'
        assert_content(l5, root, st, meta)
        both = active_observation(l5, root, st)
        assert both['read_allowed'] and both['write_allowed'] and not both['old_ingress_read_allowed'] and not both['old_ingress_write_allowed']
        assert len({move['record'],grant_c['record'],grant_d['record'],both['activation']['record']}) == 4
        positive = {'move':move, 'move_only':move_only, 'C_request':req_c, 'C_grant':grant_c,
                    'C_only':c_only, 'D_request':req_d, 'D_grant':grant_d, 'both':both,
                    'accepted_identity':meta['identity'], 'accepted_bytes_hex':X.hex(),
                    'accepted_sha256':meta['sha256'], 'files':files(root)}

    source = (HERE / 'l5_integrated.py').read_text()
    original = "unit['latent_ceiling']=sorted(set(unit['latent_ceiling'])|{'write'})"
    mutant = original + "\n    if target=='C': st['work_units']['D']['latent_ceiling']=['read','write']"
    assert source.count(original) == 1
    with tempfile.TemporaryDirectory(prefix='f3-grant-mutant-') as td:
        folder = Path(td); path = folder / 'l5_mutant.py'
        path.write_text(source.replace(original, mutant))
        spec = importlib.util.spec_from_file_location('l5_mutant', path)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        root = folder / 'fixture'; root.mkdir(); st, meta = setup(root)
        _, move = request(mod, root, st, 'authorize_move', child='C', destination='Q')
        _, grant = request(mod, root, st, 'authorize_grant', **common)
        assert move['result'] == grant['result'] == 'COMMITTED'
        observed = active_observation(mod, root, st)
        assert observed['write_allowed'] and st['work_units']['D']['latent_ceiling'] == ['read','write']
        assert_content(mod, root, st, meta)
        mutation = {'mutant_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'move':move, 'C_only_grant':grant, 'D_observation':observed,
                    'independent_observer_violation':'D write enabled without its own grant'}

    out = {'bounds':{'denial_cases':len(cases), 'positive_sequences':1, 'mutation_cases':1,
                     'enumerated':False, 'truncated':False}, 'denials':cases,
           'positive':positive, 'mutant':mutation}
    print(json.dumps(out, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
