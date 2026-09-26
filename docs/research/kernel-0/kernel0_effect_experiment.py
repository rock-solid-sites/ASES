#!/usr/bin/env python3
"""One immutable decision-authorized effect, with a separate persistent sink."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile

import kernel0_finite_model as m
import kernel0_service as core
import kernel0_recovery_service as source
import kernel0_recovery_check as harness

HERE = Path(__file__).resolve().parent


class EffectBoundary(source.Boundary):
    def propose(self, current, context, q):
        # A stricter finite consumer: the single intent can only become present.
        # No producer can overwrite an obligation or create a second identity.
        if q.kind == 'accept' and q.value != core.CONTENTS[1]:
            return None
        if q.kind not in ('establish', 'grant', 'restrict', 'replace', 'accept'):
            return None
        return super().propose(current, context, q)


def sink_main(config):
    db = sqlite3.connect(Path(config['path']).resolve().as_uri() + '?mode=rw', uri=True,
                         isolation_level=None)
    db.execute('PRAGMA synchronous=FULL')
    conn = socket.socket(fileno=config['fd'])  # Issued ONLY to the trusted mediator.
    print('ready', flush=True)
    while True:
        try:
            request = harness.receive(conn)
        except EOFError:
            return
        if request == {'kind': 'read'}:
            count = db.execute('SELECT count FROM sink').fetchone()[0]
            conn.sendall(harness.packet({'count': count}))
            continue
        if request != {'kind': 'deliver', 'payload': core.CONTENTS[1]}:
            conn.sendall(harness.packet({'outcome': 'deny'}))
            continue
        db.execute('BEGIN IMMEDIATE')
        db.execute('UPDATE sink SET count=count+1')
        if config.get('cut') == 'prepared':
            os.write(config['event_fd'], b'G')
            os.read(config['release_fd'], 1)
        db.execute('COMMIT')  # Irreversible acceptance within this effect alphabet.
        if config.get('cut') == 'accepted':
            os.write(config['event_fd'], b'G')
            os.read(config['release_fd'], 1)
        conn.sendall(harness.packet({'outcome': 'accepted'}))


class Sink:
    def __init__(self, path, cut=None):
        parent, child = socket.socketpair()
        parent.settimeout(10)
        self.conn = parent
        self.event, event_write = os.pipe()
        release_read, self.release = os.pipe()
        config = {'path': str(path), 'fd': child.fileno(), 'cut': cut,
                  'event_fd': event_write, 'release_fd': release_read}
        self.proc = subprocess.Popen([sys.executable, str(Path(__file__)), '--sink', json.dumps(config)],
                                     pass_fds=[child.fileno(), event_write, release_read],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        harness.CHILDREN.append(self.proc)
        child.close()
        os.close(event_write)
        os.close(release_read)
        harness.ready(self.proc)

    def send(self):
        self.conn.sendall(harness.packet({'kind': 'deliver', 'payload': core.CONTENTS[1]}))

    def read(self):
        self.conn.sendall(harness.packet({'kind': 'read'}))
        return harness.receive(self.conn)['count']

    def gated(self):
        assert __import__('select').select([self.event], [], [], 10)[0]
        assert os.read(self.event, 1) == b'G'

    def kill(self):
        self.proc.kill()
        self.proc.wait(timeout=10)
        assert self.proc.returncode == -9
        error = self.proc.stderr.read().decode()
        assert not error, error
        self.conn.close()
        self.proc.stdout.close()
        self.proc.stderr.close()
        os.close(self.event)
        os.close(self.release)


def provision(directory, name):
    authority, sink = directory / f'{name}-authority.db', directory / f'{name}-sink.db'
    harness.setup(authority)
    with sqlite3.connect(sink) as db:
        db.execute('CREATE TABLE sink(count INTEGER NOT NULL)')
        db.execute('INSERT INTO sink VALUES(0)')
    return authority, sink


def holder(path, gate=None):
    return harness.Holder(path, gate=gate, service_path=Path(__file__))


def mediated_send(h, sink):
    # This read is trusted mediation of a MONOTONE obligation, not a read of
    # revocable producer permission. Payload cannot change after commitment.
    if h.read().content != 1:
        return False
    sink.send()
    return True


def experiment(directory):
    result = {}
    q = m.Request('accept', 0, value=1)
    revoke = m.Request('restrict', target=0, value=0)
    for cut in ('received', 'validated', 'prepared', 'durable', 'before_ack'):
        path, sink_path = provision(directory, cut)
        h = holder(path, gate={'lane': 1, 'kind': 'accept', 'stage': cut})
        worker = harness.Worker()
        worker.attach(h.clients[1])
        worker.submit(harness.wire(q))
        h.gated()
        h.kill()
        assert worker.result()['outcome'] == 'unknown'
        worker.close()
        h = holder(path)
        sink = Sink(sink_path)
        sent = mediated_send(h, sink)
        if sent:
            assert harness.receive(sink.conn)['outcome'] == 'accepted'
        count = sink.read()
        assert count == int(cut in ('durable', 'before_ack'))
        result[f'source_{cut}'] = {'sent': sent, 'effects': count}
        h.kill()
        sink.kill()

    for cut in ('prepared', 'accepted'):
        path, sink_path = provision(directory, 'sink-' + cut)
        h = holder(path)
        assert h.request(q)['outcome'] == 'commit'
        sink = Sink(sink_path, cut)
        assert mediated_send(h, sink)
        sink.gated()
        sink.kill()
        sink = Sink(sink_path)
        before = sink.read()
        assert before == int(cut == 'accepted')
        assert mediated_send(h, sink)
        assert harness.receive(sink.conn)['outcome'] == 'accepted'
        after = sink.read()
        assert after == before + 1
        result[f'sink_{cut}_then_retry'] = {'before_retry': before, 'after_retry': after}
        h.kill()
        sink.kill()

    path, sink_path = provision(directory, 'revocation')
    h = holder(path)
    sink = Sink(sink_path)
    assert h.request(q)['outcome'] == 'commit'
    assert h.request(m.Request('accept', 0, value=0))['outcome'] == 'deny'
    assert h.request(revoke)['outcome'] == 'commit'
    assert h.request(q)['outcome'] == 'deny'
    assert mediated_send(h, sink)
    assert harness.receive(sink.conn)['outcome'] == 'accepted'
    assert sink.read() == 1
    result['decision_before_revocation_effect_after'] = {'effects': 1, 'permitted_by_profile': True,
                                                        'new_decision_with_old_evidence': 'deny',
                                                        'overwrite_obligation': 'deny'}
    h.kill()
    sink.kill()
    return result


def run(output):
    with tempfile.TemporaryDirectory(prefix='kernel0-effects-') as tmp:
        result = experiment(Path(tmp))
    payload = {'profile': 'one monotone durable intent; duplicate effects allowed; trusted mediator ingress',
               'experiments': result, 'sources': {p.name: sha256(p.read_bytes()).hexdigest() for p in
                (Path(__file__), HERE / 'kernel0_recovery_service.py', HERE / 'kernel0_recovery_check.py',
                 HERE / 'kernel0_service.py', HERE / 'kernel0_finite_model.py')},
               'runtime': {'python': sys.version, 'sqlite': sqlite3.sqlite_version}}
    output.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    if sys.argv[1] == '--sink':
        sink_main(json.loads(sys.argv[2]))
    elif sys.argv[1] == '--output':
        if not __debug__:
            raise SystemExit('checks require Python without -O')
        run(Path(sys.argv[2]))
    else:
        config = json.loads(sys.argv[1])
        source.serve(config, EffectBoundary(config))
