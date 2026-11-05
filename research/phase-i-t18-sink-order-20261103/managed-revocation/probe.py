#!/usr/bin/env python3
"""Bounded real HTTP histories; checker owns the verdict, not this runner."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / 'managed_sink.py'
BASE = HERE.parent / 'run.py'
FIXTURES = ROOT / 'docs/architecture/core-substrate/fixtures-f2/fixtures.json'
NEEDLE = 'return self.created and self.granted and self.active and token == self.version'
REPLACEMENT = 'return self.created and token == self.version'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fixtures(value):
    if isinstance(value, dict):
        if str(value.get('id', '')).startswith('T18-'):
            yield value
        else:
            for child in value.values():
                yield from fixtures(child)
    elif isinstance(value, list):
        for child in value:
            yield from fixtures(child)


def load():
    spec = importlib.util.spec_from_file_location('managed_probe_source', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(journal):
    raw = journal.read_bytes() if journal.exists() else b''
    return dict(exists=journal.exists(), raw_hex=raw.hex(), sha256=digest(raw))


def one(module, source, root, variant, fixture):
    begin = time.monotonic_ns()
    sink = module.RunningSink(source, root)
    ready = time.monotonic_ns()
    steps = []
    def step(label, path, body):
        start = time.monotonic_ns()
        code, reply = module.base.call(sink.port, 'POST', path, body)
        end = time.monotonic_ns()
        status_code, status = module.base.call(sink.port, 'GET', '/status')
        steps.append(dict(label=label, request=dict(path=path, body=body), start_ns=start, end_ns=end,
                          response=dict(status=code, body=reply), status_code=status_code,
                          observed=status, journal=snapshot(sink.journal)))
    def submit(label, token, payload):
        step(label, '/submit', dict(authority_version=token, request_id=label, payload=payload))
    try:
        if 'initial_state' in fixture and 'events' in fixture['initial_state']:
            for event in fixture['initial_state']['events']:
                name = event['ev']
                step(name, '/' + name, dict(authority_version=1) if name == 'activate' else {})
                if variant == 'reference' and name in ('create', 'grant'):
                    submit('after-' + name, 0 if name == 'create' else 1, 'not-x-' + name)
            submit('before-positive', 1, 'before-x')
            step('revoke', '/revoke', {})
            submit('post-revoke', 1, 'x')
            if variant == 'reference':
                step('regrant', '/grant', {})
                submit('regrant-inactive', 2, 'not-x-regrant')
                step('reactivate', '/activate', dict(authority_version=2))
                submit('fresh-positive', 2, 'fresh-x')
                submit('old-negative', 1, 'not-x-old')
        else:
            for path, body in [('/create', {}), ('/grant', {}), ('/activate', dict(authority_version=1))]:
                step(path[1:], path, body)
            step('commit-before-fixture', '/commit-obligation', dict(authority_version=1, obligation_id='m', payload='x'))
            step('replace', '/replace', dict(holder=fixture['events'][0]['to']))
            submit('replacement-inactive', 2, 'not-x-current')
            step('m', '/deliver-obligation', dict(obligation_id='m'))
        final = snapshot(sink.journal)
    finally:
        exit_code = sink.kill_and_reap()
        exited = time.monotonic_ns()
    refusal_start = time.monotonic_ns()
    refusal = subprocess.run([sys.executable, str(source), '--server', str(sink.journal)],
                             capture_output=True, text=True, timeout=4)
    refusal_end = time.monotonic_ns()
    return dict(variant=variant, fixture_id=fixture['id'], steps=steps, final_journal=final,
                source_sha256=digest(source.read_bytes()), sink_pid=sink.process.pid,
                start_ns=begin, ready_ns=ready, exit_ns=exited, exit=exit_code,
                restart=dict(pid_not_recorded=True, start_ns=refusal_start, end_ns=refusal_end,
                             exit=refusal.returncode, stdout=refusal.stdout, stderr=refusal.stderr,
                             journal_after=snapshot(sink.journal)))


def main():
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    source = SOURCE.read_text()
    assert source.count(NEEDLE) == 1
    frozen = {f['id']: f for f in fixtures(json.loads(FIXTURES.read_bytes()))}
    rev = frozen['T18-use-current-sink-order-after-revocation']
    exact = frozen['T18-exact-obligation-delivery-after-replacement']
    module = load()
    with tempfile.TemporaryDirectory(prefix='ases-managed-t18-') as directory:
        root = Path(directory)
        mutant = root / 'mutant' / 'managed-revocation' / SOURCE.name
        mutant.parent.mkdir(parents=True)
        mutant.write_text(source.replace(NEEDLE, REPLACEMENT, 1))
        (mutant.parent.parent / 'run.py').write_bytes(BASE.read_bytes())
        cases = dict(reference=one(module, SOURCE, root / 'ref', 'reference', rev),
                     equality_only=one(module, mutant, root / 'mut', 'equality_only', rev),
                     exact_obligation=one(module, SOURCE, root / 'exact', 'exact_obligation', exact))
        print(json.dumps(dict(schema='ases.t18.managed-history', version=1,
                              execution_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                              environment=dict(platform=platform.platform(), python=sys.version, executable=sys.executable,
                                               executable_sha256=digest(Path(sys.executable).read_bytes()),
                                               max_child_concurrency=1, address_space_limit=256*1024*1024),
                              source_sha256=digest(SOURCE.read_bytes()), base_sha256=digest(BASE.read_bytes()),
                              runner_sha256=digest(Path(__file__).read_bytes()), fixture_sha256=digest(FIXTURES.read_bytes()),
                              fixtures=[rev, exact], mutation=dict(before=NEEDLE, after=REPLACEMENT,
                                                                  sha256=digest(mutant.read_bytes())), cases=cases),
                         indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
