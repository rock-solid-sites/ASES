#!/usr/bin/env python3
"""Actual managed ACK/revoke/restart histories and explicit rollback limit."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time
import probe

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'managed_sink.py'

class Session:
    def __init__(self, module, source, root, recover=False):
        self.module = module
        self.data = dict(source_sha256=probe.digest(source.read_bytes()), start_ns=time.monotonic_ns(), recover=recover, steps=[])
        self.sink = module.RunningSink(source, root, recover)
        self.data.update(pid=self.sink.process.pid, ready_ns=time.monotonic_ns(), journal_path=str(self.sink.journal))
        self.data['ready_status'] = module.base.call(self.sink.port, 'GET', '/status')[1]
        self.data['ready_journal'] = probe.snapshot(self.sink.journal)

    def post(self, label, path, body):
        start = time.monotonic_ns()
        code, reply = self.module.base.call(self.sink.port, 'POST', path, body)
        end = time.monotonic_ns()
        observation = self.module.base.call(self.sink.port, 'GET', '/status')[1]
        self.data['steps'].append(dict(label=label, path=path, body=body, start_ns=start, end_ns=end,
                                       response=dict(status=code, body=reply), observed=observation,
                                       journal=probe.snapshot(self.sink.journal)))

    def submit(self, label, token, payload):
        self.post(label, '/submit', dict(authority_version=token, request_id=label, payload=payload))

    def close(self):
        self.data['final_status'] = self.module.base.call(self.sink.port, 'GET', '/status')[1]
        self.data['final_journal'] = probe.snapshot(self.sink.journal)
        self.sink.process.kill()
        self.data['exit'] = self.sink.process.wait(timeout=2)
        self.data['exit_ns'] = time.monotonic_ns()
        self.data['stderr'] = self.sink.process.stderr.read()
        self.sink.process.stdout.close(); self.sink.process.stderr.close()
        return self.data


def bootstrap(session):
    for path, body in [('/create', {}), ('/grant', {}), ('/activate', dict(authority_version=1))]:
        session.post(path[1:], path, body)


def revoked_history(module, source, recovery_source, root, weak=False):
    writer = Session(module, source, root)
    try:
        bootstrap(writer)
        writer.submit('ack-before', 1, 'retained-before-revoke')
        prefix = probe.snapshot(writer.sink.journal)
        writer.post('revoke', '/revoke', {})
    finally: original = writer.close()
    recovery = Session(module, recovery_source, root, True)
    try:
        recovery.submit('post-restart-revoke', 1, 'x')
        if not weak:
            recovery.post('regrant', '/grant', {})
            recovery.submit('inactive', 2, 'not-active')
            recovery.post('activate-new', '/activate', dict(authority_version=2))
            recovery.submit('ack-new', 2, 'retained-new-π')
            recovery.submit('old', 1, 'not-current')
    finally: restored = recovery.close()
    cold = attempt(root/'sink-effects.jsonl') if weak else Session(module, recovery_source, root, True).close()
    return dict(writer=original, recovery=restored, cold=cold, older_acknowledged_prefix=prefix)


def exact_history(module, root):
    writer = Session(module, SOURCE, root)
    try:
        bootstrap(writer)
        writer.post('commit', '/commit-obligation', dict(authority_version=1, obligation_id='m', payload='x'))
        writer.post('replace', '/replace', dict(holder='new'))
    finally: original = writer.close()
    recovery = Session(module, SOURCE, root, True)
    try:
        recovery.submit('current-inactive', 2, 'not-active')
        recovery.post('deliver', '/deliver-obligation', dict(obligation_id='m'))
    finally: restored = recovery.close()
    cold = Session(module, SOURCE, root, True).close()
    return dict(writer=original, recovery=restored, cold=cold)


def attempt(journal):
    raw = journal.read_bytes()
    start = time.monotonic_ns()
    child = subprocess.Popen([sys.executable, str(SOURCE), '--recover', str(journal)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = child.communicate(timeout=4)
    return dict(start_ns=start, exit_ns=time.monotonic_ns(), pid=child.pid, exit=child.returncode,
                stdout=out, stderr=err, before_raw_hex=raw.hex(), after=probe.snapshot(journal))


def refused(root, raw):
    root.mkdir()
    journal = root / 'sink-effects.jsonl'; journal.write_bytes(raw)
    return attempt(journal)


def main():
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024,)*2)
    module = probe.load()
    text = SOURCE.read_text()
    needle = '            self.replay()\n'
    assert text.count(needle) == 1
    with tempfile.TemporaryDirectory(prefix='ases-managed-replay-') as directory:
        root = Path(directory)
        weak = root / 'weak' / 'managed-revocation' / SOURCE.name
        weak.parent.mkdir(parents=True)
        weak.write_text(text.replace(needle, needle + '            if not self.granted:\n                self.granted = self.active = True\n', 1))
        (weak.parent.parent / 'run.py').write_bytes(probe.BASE.read_bytes())
        cases = dict(reference=revoked_history(module, SOURCE, SOURCE, root/'reference'),
                     replay_resurrection=revoked_history(module, SOURCE, weak, root/'weak-state', True),
                     exact_obligation=exact_history(module, root/'exact'))
        acknowledged = bytes.fromhex(cases['reference']['writer']['final_journal']['raw_hex'])
        rows = [json.loads(line) for line in acknowledged.splitlines()]
        def changed(index, key, value):
            copy = json.loads(json.dumps(rows)); copy[index][key] = value
            return b''.join(json.dumps(row).encode()+b'\n' for row in copy)
        invalid = dict(empty=b'', truncated=acknowledged[:-1], unknown=changed(-1,'event','unknown'),
                       bool_seq=changed(0,'seq',True), bool_generation=changed(1,'current_version',True),
                       wrong_unit=changed(0,'unit','other'), wrong_profile=changed(0,'profile','other'),
                       activation_after_revoke=acknowledged+json.dumps(dict(rows[2],seq=rows[-1]['seq']+1)).encode()+b'\n',
                       stale_regrant=acknowledged+json.dumps(dict(rows[1],seq=rows[-1]['seq']+1)).encode()+b'\n',
                       duplicate_key=acknowledged.replace(b'"seq": 1',b'"seq": 1, "seq": 1',1))
        controls = {name:refused(root/('invalid-'+name), raw) for name,raw in invalid.items()}
        rollback_root = root/'rollback'; rollback_root.mkdir()
        older = bytes.fromhex(cases['reference']['older_acknowledged_prefix']['raw_hex'])
        (rollback_root/'sink-effects.jsonl').write_bytes(older)  # Explicit outside-premise limit control.
        rollback = Session(module, SOURCE, rollback_root, True)
        try: rollback.submit('rolled-back-token',1,'rollback-limit')
        finally: rollback_data=rollback.close()
        result = dict(schema='ases.managed-replay-history',version=1,
                      execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=probe.ROOT,text=True).strip(),
                      environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                                       executable_sha256=probe.digest(Path(sys.executable).read_bytes()),address_space_bytes=256*1024*1024),
                      source_sha256=probe.digest(SOURCE.read_bytes()),base_sha256=probe.digest(probe.BASE.read_bytes()),
                      runner_sha256=probe.digest(Path(__file__).read_bytes()),helper_sha256=probe.digest((HERE/'probe.py').read_bytes()),
                      weak_recovery_sha256=probe.digest(weak.read_bytes()),cases=cases,invalid_controls=controls,rollback_limit=rollback_data)
        print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__': main()
