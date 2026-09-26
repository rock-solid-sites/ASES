#!/usr/bin/env python3
"""Real holder SIGKILL/restart experiments; original abstract reducer is oracle."""
from __future__ import annotations

import argparse
import atexit
import array
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import select
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time

import kernel0_finite_model as m
import kernel0_service as core
import kernel0_recovery_service as persistent

HERE = Path(__file__).resolve().parent
CONTEXTS = (-1, 0, 1, 2, 3, 0)
CHILDREN = []


def cleanup():
    for proc in CHILDREN:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)


atexit.register(cleanup)


def wire(q):
    obj = {k: getattr(q, k) for k in ('kind', 'target', 'value', 'other')}
    if q.kind in ('accept', 'resume'):
        obj['value'] = core.CONTENTS[q.value]
    return obj


def abstract(raw):
    return m.State(raw['established'], tuple(raw['data']),
                   -1 if raw['content'] is None else core.CONTENTS.index(raw['content']),
                   raw['issued'], tuple(raw['rights']), tuple(raw['parents']))


def packet(obj):
    return json.dumps(obj).encode() + b'\n'


def receive(conn):
    buf = bytearray()
    while not buf.endswith(b'\n'):
        part = conn.recv(1)
        if not part:
            raise EOFError('holder lost')
        buf.extend(part)
    return json.loads(buf)


def ready(proc):
    if not select.select([proc.stdout], [], [], 10)[0]:
        proc.kill()
        proc.wait(timeout=10)
        raise AssertionError('child startup timeout')
    line = proc.stdout.readline()
    if line != b'ready\n':
        raise AssertionError((line, proc.stderr.read().decode()))


class Worker:
    """Control channel is trusted supervisor; only holder channel carries proposals."""
    def __init__(self):
        parent, child = socket.socketpair(type=socket.SOCK_SEQPACKET)
        self.control = parent
        self.control.settimeout(10)
        self.proc = subprocess.Popen([sys.executable, str(Path(__file__)), '--worker', str(child.fileno())],
                                     pass_fds=[child.fileno()], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     bufsize=0)
        CHILDREN.append(self.proc)
        child.close()
        ready(self.proc)

    def attach(self, conn):
        fds = array.array('i', [conn.fileno()])
        self.control.sendmsg([b'attach'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])
        assert self.control.recv(100) == b'attached'

    def submit(self, obj, partial=False):
        self.control.send(json.dumps({'obj': obj, 'partial': partial}).encode())

    def result(self):
        return json.loads(self.control.recv(65536))

    def request(self, q):
        self.submit(wire(q))
        return self.result()

    def close(self):
        self.proc.kill()
        self.proc.wait(timeout=10)
        error = self.proc.stderr.read().decode()
        self.control.close()
        self.proc.stdout.close()
        self.proc.stderr.close()
        assert not error, error


def worker_main(fd):
    control = socket.socket(fileno=fd)
    conn = None
    print('ready', flush=True)
    while True:
        data, ancillary, flags, _ = control.recvmsg(65536, socket.CMSG_SPACE(4))
        if not data:
            return
        if data == b'attach':
            descriptors = array.array('i')
            descriptors.frombytes(ancillary[0][2][:4])
            if conn is not None:
                conn.close()
            conn = socket.socket(fileno=descriptors[0])
            conn.settimeout(10)
            control.send(b'attached')
        else:
            request = json.loads(data)
            raw = packet(request['obj'])
            try:
                conn.sendall(raw[:len(raw)//2] if request['partial'] else raw)
                if request['partial']:
                    control.send(json.dumps({'stage': 'partial-sent'}).encode())
                reply = receive(conn)
            except (EOFError, BrokenPipeError, ConnectionResetError):
                reply = {'outcome': 'unknown'}
            control.send(json.dumps(reply).encode())


class Holder:
    def __init__(self, path, profile='independent', root='work', gate=None):
        pairs = [socket.socketpair() for _ in CONTEXTS]
        self.clients = [p[0] for p in pairs]
        for conn in self.clients:
            conn.settimeout(10)
        self.event, event_write = os.pipe()
        release_read, self.release = os.pipe()
        config = {'path': str(path), 'root': root, 'profile': profile,
                  'channels': [[a, pair[1].fileno()] for a, pair in zip(CONTEXTS, pairs)]}
        fds = [pair[1].fileno() for pair in pairs]
        if gate:
            config['gate'] = dict(gate, event_fd=event_write, release_fd=release_read)
            fds += [event_write, release_read]
        self.proc = subprocess.Popen([sys.executable, str(HERE / 'kernel0_recovery_service.py'), json.dumps(config)],
                                     pass_fds=fds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        CHILDREN.append(self.proc)
        for _, server in pairs:
            server.close()
        os.close(event_write)
        os.close(release_read)
        ready(self.proc)

    def call(self, obj, lane=0):
        self.clients[lane].sendall(packet(obj))
        return receive(self.clients[lane])

    def request(self, q):
        return self.call(wire(q), CONTEXTS.index(q.evidence))

    def read(self):
        return abstract(self.call({'kind': 'read'})['state'])

    def gated(self):
        assert select.select([self.event], [], [], 10)[0], 'cut not reached'
        assert os.read(self.event, 1) == b'G'

    def release_gate(self):
        os.write(self.release, b'R')

    def kill(self):
        pid = self.proc.pid
        self.proc.kill()
        self.proc.wait(timeout=10)
        assert self.proc.returncode == -9
        error = self.proc.stderr.read().decode()
        assert not error, error
        self.proc.stdout.close()
        self.proc.stderr.close()
        for conn in self.clients:
            conn.close()
        os.close(self.event)
        os.close(self.release)
        return pid


def setup(path, profile='independent'):
    persistent.initialize(str(path), 'work', profile)
    h = Holder(path, profile)
    s = m.State()
    p = m.Profile(profile, coupled=profile == 'coupled', exclusive=profile == 'exclusive')
    for q in (m.Request('establish'), m.Request('grant', target=0, value=7)):
        s, outcome = m.resolve(s, q, p)
        reply = h.request(q)
        assert reply['outcome'] == outcome and abstract(reply['state']) == s
    h.kill()
    return s


def crash_cuts(directory):
    results = []
    ops = (m.Request('pair', 0, value=3), m.Request('accept', 0, value=1),
           m.Request('replace', target=0, other=1), m.Request('restrict', target=0, value=0))
    stages = ('partial_ingress', 'received', 'validated', 'prepared', 'commit_enter',
              'durable', 'published', 'before_ack', 'acknowledged')
    for q in ops:
        for stage in stages:
            path = directory / f'{q.kind}-{stage}.db'
            before = setup(path)
            expected, outcome = m.resolve(before, q, m.Profile('independent'))
            assert outcome == 'commit'
            gate = None if stage in ('partial_ingress', 'acknowledged') else {
                'stage': stage, 'kind': q.kind, 'lane': CONTEXTS.index(q.evidence)}
            h = Holder(path, gate=gate)
            worker = Worker()
            worker.attach(h.clients[CONTEXTS.index(q.evidence)])
            worker.submit(wire(q), partial=stage == 'partial_ingress')
            reply = None
            if stage == 'partial_ingress':
                assert worker.result() == {'stage': 'partial-sent'}
            if stage == 'acknowledged':
                reply = worker.result()
                assert reply['outcome'] == 'commit'
            elif stage != 'partial_ingress':
                h.gated()
            killed = h.kill()
            if reply is None:
                assert worker.result()['outcome'] == 'unknown'
            restarted = Holder(path)
            recovered = restarted.read()
            post_commit = stage in ('durable', 'published', 'before_ack', 'acknowledged')
            assert recovered == (expected if post_commit else before), (q, stage, recovered)
            # The SAME worker process survives holder loss and receives only its
            # original context association; recovered rights still govern it.
            worker.attach(restarted.clients[CONTEXTS.index(q.evidence)])
            replay = m.Request('flip', 0)
            old_worker = Worker()
            old_worker.attach(restarted.clients[1])
            final, wanted = m.resolve(recovered, replay, m.Profile('independent'))
            actual = old_worker.request(replay)
            assert actual['outcome'] == wanted and abstract(actual['state']) == final
            results.append({'operation': q.label(), 'cut': stage, 'killed_pid': killed,
                            'restarted_pid': restarted.proc.pid, 'surviving_worker_pid': worker.proc.pid,
                            'recovered': asdict(recovered), 'old_authority_replay': wanted,
                            'acknowledged': reply is not None})
            old_worker.close()
            worker.close()
            restarted.kill()
    return results


def continuing_and_cold(directory):
    results = []
    for mode in ('cold', 'continuing'):
        path = directory / f'{mode}.db'
        setup(path)
        h = Holder(path)
        old, current = Worker(), Worker()
        old.attach(h.clients[1])
        assert old.request(m.Request('accept', 0, value=1))['outcome'] == 'commit'
        assert h.request(m.Request('replace', target=0, other=1))['outcome'] == 'commit'
        current.attach(h.clients[2])
        accepted = h.read()
        old_pid, current_pid = old.proc.pid, current.proc.pid
        killed = h.kill()
        if mode == 'cold':
            old.close()
            current.close()
        h = Holder(path)
        assert h.read() == accepted
        if mode == 'continuing':
            old.attach(h.clients[1])
            current.attach(h.clients[2])
            assert old.request(m.Request('flip', 0))['outcome'] == 'deny'
            reply = current.request(m.Request('resume', 1, value=1))
            assert reply['outcome'] == 'commit' and reply['state']['data'][0] == 1
            assert (old.proc.pid, current.proc.pid) == (old_pid, current_pid)
            old.close()
            current.close()
        else:
            assert h.request(m.Request('replace', target=1, other=2))['outcome'] == 'commit'
            fresh = Worker()
            fresh.attach(h.clients[3])
            reply = fresh.request(m.Request('resume', 2, value=1))
            assert reply['outcome'] == 'commit' and reply['state']['data'][0] == 1
            fresh.close()
        results.append({'mode': mode, 'killed_pid': killed, 'restarted_pid': h.proc.pid,
                        'retained_content_used': reply['state']['content'], 'final': reply['state']})
        h.kill()
    return results


def order_and_replay(directory):
    path = directory / 'order.db'
    setup(path, 'coupled')
    h = Holder(path, 'coupled', gate={'lane': 1, 'kind': 'set', 'stage': 'received'})
    worker = Worker()
    worker.attach(h.clients[1])
    worker.submit(wire(m.Request('set', 0, value=1)))
    h.gated()
    assert h.request(m.Request('replace', target=0, other=1))['outcome'] == 'commit'
    h.release_gate()
    assert worker.result()['outcome'] == 'deny'
    h.kill()
    h = Holder(path, 'coupled')
    worker.attach(h.clients[1])
    assert worker.request(m.Request('set', 0, value=1))['outcome'] == 'deny'
    # Conflict racing through two channels with the new context.
    worker.attach(h.clients[2])
    qx, qy = m.Request('set', 1, value=1), m.Request('set', 1, target=1, value=1)
    worker.submit(wire(qx))
    # Same context on one endpoint cannot multiplex frames; use management
    # channel only for management. Sequential peer here demonstrates durable
    # predecessor visibility; concurrent independent lanes are tested below.
    rx = worker.result()
    ry = worker.request(qy)
    assert [rx['outcome'], ry['outcome']].count('commit') == 1
    observed = h.read()
    h.kill()
    h = Holder(path, 'coupled')
    assert h.read() == observed
    worker.close()
    h.kill()

    path = directory / 'concurrent.db'
    setup(path, 'coupled')
    h = Holder(path, 'coupled')
    with ThreadPoolExecutor(2) as pool:
        futures = [pool.submit(h.call, wire(q), lane) for q, lane in
                   ((m.Request('set', 0, value=1), 1), (m.Request('set', 0, target=1, value=1), 5))]
        replies = [f.result() for f in futures]
    assert [r['outcome'] for r in replies].count('commit') == 1
    final = h.read()
    h.kill()
    h = Holder(path, 'coupled')
    assert h.read() == final
    h.kill()
    return {'stale_ingress_after_acknowledged_replacement': 'deny',
            'stale_replay_after_restart': 'deny', 'conflicting_commit_count': 1,
            'concurrent_replies': replies, 'retained_final': asdict(final)}


def root_and_limit(directory):
    path = directory / 'root.db'
    setup(path)
    outcomes = []
    for candidate_path, root, profile in ((path, 'wrong', 'independent'),
                                         (path, 'work', 'coupled'),
                                         (directory / 'missing.db', 'work', 'independent')):
        config = {'path': str(candidate_path), 'root': root, 'profile': profile, 'channels': []}
        proc = subprocess.run([sys.executable, str(HERE / 'kernel0_recovery_service.py'), json.dumps(config)],
                              capture_output=True, timeout=10)
        assert proc.returncode != 0 and b'ready' not in proc.stdout
        outcomes.append({'case': [candidate_path.name, root, profile], 'startup': 'rejected'})
    assert not (directory / 'missing.db').exists()
    # Explicit negative experiment: same-root rollback BELOW the trusted boundary
    # is not detected by the selected realization. Preserve it, never claim otherwise.
    snapshot = path.read_bytes()  # no writer, no hot journal at this point
    h = Holder(path)
    assert h.request(m.Request('restrict', target=0, value=0))['outcome'] == 'commit'
    h.kill()
    path.write_bytes(snapshot)
    h = Holder(path)
    reply = h.request(m.Request('flip', 0))
    assert reply['outcome'] == 'commit'
    h.kill()
    return {'fail_closed': outcomes, 'outside_profile_same_root_rollback': {
        'trace': ['save valid old image', 'acknowledge revocation', 'kill holder',
                  'restore old same-root image', 'restart', 'old authority flip commits'],
        'observed': reply, 'disposition': 'trusted-current-storage assumption is necessary'}}


def commit_races(directory):
    results = []
    for n in range(18):
        path = directory / f'commit-race-{n}.db'
        before = setup(path)
        q = m.Request('pair', 0, value=3)
        expected, _ = m.resolve(before, q, m.Profile('independent'))
        h = Holder(path, gate={'lane': 1, 'kind': 'pair', 'stage': 'commit_enter'})
        worker = Worker()
        worker.attach(h.clients[1])
        worker.submit(wire(q))
        h.gated()
        h.release_gate()
        delay = (0, 0.0001, 0.001)[n % 3]
        if delay:
            time.sleep(delay)
        h.kill()
        reply = worker.result()
        h = Holder(path)
        recovered = h.read()
        assert recovered in (before, expected)
        if reply['outcome'] == 'commit':
            assert recovered == expected
        results.append({'delay_seconds': delay, 'reply': reply['outcome'],
                        'recovered': 'new' if recovered == expected else 'old'})
        worker.close()
        h.kill()
    return {'qualification': 'race around commit call; no claim to instruction-level or SQLite I/O coverage',
            'runs': results}


def lost_ack_retry(directory):
    path = directory / 'retry.db'
    setup(path)
    h = Holder(path, gate={'lane': 1, 'kind': 'flip', 'stage': 'durable'})
    worker = Worker()
    worker.attach(h.clients[1])
    q = m.Request('flip', 0)
    worker.submit(wire(q))
    h.gated()
    h.kill()
    assert worker.result()['outcome'] == 'unknown'
    h = Holder(path)
    assert h.read().data[0] == 1
    worker.attach(h.clients[1])
    reply = worker.request(q)
    assert reply['outcome'] == 'commit' and reply['state']['data'][0] == 0
    denied = worker.request(m.Request('mixed', 0))
    assert denied['outcome'] == 'deny' and denied['state'] == reply['state']
    worker.close()
    h.kill()
    return {'durable_with_lost_reply': 1, 'after_authorized_retry': 0,
            'exactly_once': False, 'partial_composite_denial': 'no effect'}


def run(output):
    with tempfile.TemporaryDirectory(prefix='kernel0-recovery-') as temp:
        directory = Path(temp)
        result = {'failure_class': 'actual SIGKILL of separate authority process; OS/storage stay live',
                  'cuts': crash_cuts(directory), 'recovery_modes': continuing_and_cold(directory),
                  'ordering': order_and_replay(directory), 'root_and_limit': root_and_limit(directory),
                  'commit_races': commit_races(directory), 'lost_ack_retry': lost_ack_retry(directory)}
    result['runtime'] = {'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version,
                         'platform': platform.platform()}
    result['sources'] = {p.name: sha256(p.read_bytes()).hexdigest() for p in
                         (Path(__file__), HERE / 'kernel0_recovery_service.py',
                          HERE / 'kernel0_service.py', HERE / 'kernel0_finite_model.py')}
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'crash_cuts': len(result['cuts']), 'recovery_modes': 2,
                      'same_root_rollback': 'confirmed outside-boundary failure'}))


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    if sys.argv[1] == '--worker':
        worker_main(int(sys.argv[2]))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--output', type=Path, required=True)
        run(parser.parse_args().output)
