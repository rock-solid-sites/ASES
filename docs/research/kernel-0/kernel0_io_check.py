#!/usr/bin/env python3
"""Actual positional-write/sync/unlink cuts; process loss, NOT power loss."""
from __future__ import annotations

import argparse
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
import kernel0_recovery_check as h

HERE = Path(__file__).resolve().parent


class InstrumentedHolder(h.Holder):
    def __init__(self, path, library, cut, split=None):
        pairs = [socket.socketpair() for _ in h.CONTEXTS]
        self.clients = [pair[0] for pair in pairs]
        for conn in self.clients:
            conn.settimeout(10)
        self.event, event_write = os.pipe()
        release_read, self.release = os.pipe()
        config = {'path': str(path), 'root': 'work', 'profile': 'independent',
                  'channels': [[a, pair[1].fileno()] for a, pair in zip(h.CONTEXTS, pairs)]}
        inherited = [pair[1].fileno() for pair in pairs] + [event_write, release_read]
        environment = os.environ.copy()
        environment.update({'LD_PRELOAD': str(library) + (' ' + environment['LD_PRELOAD']
                            if environment.get('LD_PRELOAD') else ''),
                            'K0_IO_DIRECTORY': str(path.parent), 'K0_IO_EVENT_FD': str(event_write),
                            'K0_IO_RELEASE_FD': str(release_read), 'K0_IO_CUT': str(cut)})
        if split:
            environment.update({'K0_IO_SPLIT_AT': str(split[0]), 'K0_IO_SPLIT_BYTES': str(split[1])})
        self.proc = subprocess.Popen([sys.executable, str(HERE / 'kernel0_recovery_service.py'),
                                      json.dumps(config)], pass_fds=inherited, env=environment,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        h.CHILDREN.append(self.proc)
        for _, server in pairs:
            server.close()
        os.close(event_write)
        os.close(release_read)
        h.ready(self.proc)
        assert not select.select([self.event], [], [], 0)[0], 'unexpected startup I/O: trace must be scoped to tested request'

    def event_line(self):
        assert select.select([self.event], [], [], 10)[0], 'instrumented cut was not reached'
        line = bytearray()
        while not line.endswith(b'\n'):
            piece = os.read(self.event, 1)
            assert piece, 'interposer ended before a complete event'
            line.extend(piece)
        return json.loads(line)


def control(directory, library, q):
    directory.mkdir()
    path = directory / 'authority.db'
    initial = h.setup(path)
    holder = InstrumentedHolder(path, library, 0)
    events = []
    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(holder.request, q)
        deadline = time.monotonic() + 10
        while not future.done() or select.select([holder.event], [], [], 0)[0]:
            assert time.monotonic() < deadline, 'control trace timeout'
            if select.select([holder.event], [], [], 0.05)[0]:
                events.append(holder.event_line())
        reply = future.result()
    expected, outcome = m.resolve(initial, q, m.Profile('independent'))
    assert outcome == reply['outcome'] == 'commit' and h.abstract(reply['state']) == expected
    assert any(e['op'] in ('pwrite', 'pwrite64') and e['file'] == 'authority.db' for e in events)
    assert any(e['op'] in ('pwrite', 'pwrite64') and e['file'] == 'authority.db-journal' for e in events)
    assert any(e['op'] in ('fsync', 'fdatasync') for e in events)
    assert any(e['op'] == 'unlink' and e['file'] == 'authority.db-journal' for e in events)
    for index, event in enumerate(events, 1):
        assert event['index'] == index
        if event['phase'] == 'after':
            wanted = event['size'] if event['op'] in ('pwrite', 'pwrite64') else 0
            assert event['result'] == wanted
    complete_image = sha256(path.read_bytes()).hexdigest()
    holder.kill()
    restarted = h.Holder(path)
    assert restarted.read() == expected
    restarted.kill()
    return events, complete_image


def replay(directory, library, q, reference, cut):
    directory.mkdir()
    path = directory / 'authority.db'
    initial = h.setup(path)
    expected, _ = m.resolve(initial, q, m.Profile('independent'))
    holder = InstrumentedHolder(path, library, cut)
    observed = []
    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(holder.request, q)
        for index in range(cut):
            event = holder.event_line()
            assert event == reference[index], (cut, event, reference[index])
            observed.append(event)
        killed = holder.kill()
        try:
            response = future.result(timeout=10)
        except (EOFError, OSError):
            response = None
        assert response is None, 'pause was expected before any success response'
    # Restart has no preload and receives no oracle state or stored parent view.
    recovered_holder = h.Holder(path)
    recovered = recovered_holder.read()
    assert recovered in (initial, expected), (q, cut, recovered)
    replay_q = m.Request('flip', 0)
    final, wanted = m.resolve(recovered, replay_q, m.Profile('independent'))
    actual = recovered_holder.request(replay_q)
    assert actual['outcome'] == wanted and h.abstract(actual['state']) == final
    restarted = recovered_holder.proc.pid
    recovered_holder.kill()
    return {'cut': reference[cut-1], 'observed_prefix_length': len(observed),
            'killed_pid': killed, 'restarted_pid': restarted,
            'recovered_endpoint': 'new' if recovered == expected else 'old',
            'recovered': asdict(recovered), 'old_evidence_replay': wanted}


def torn_write(directory, library, q, reference, before_event, length, complete_image):
    directory.mkdir()
    path = directory / 'authority.db'
    initial = h.setup(path)
    old_image = sha256(path.read_bytes()).hexdigest()
    holder = InstrumentedHolder(path, library, before_event + 1, (before_event, length))
    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(holder.request, q)
        for index in range(before_event):
            assert holder.event_line() == reference[index]
        partial = holder.event_line()
        assert partial['phase'] == 'partial' and partial['file'] == 'authority.db'
        assert partial['size'] == partial['result'] == length
        # Observe the physically mixed file while the real first sub-write is
        # complete. Never feed these bytes back into recovery.
        mixed_image = sha256(path.read_bytes()).hexdigest()
        holder.kill()
        try:
            response = future.result(timeout=10)
        except (EOFError, OSError):
            response = None
        assert response is None
    recovered = h.Holder(path)
    actual = recovered.read()
    assert actual == initial, 'uncommitted partial write must roll back'
    recovered.kill()
    return {'interrupted_write': reference[before_event - 1], 'partial_write': partial,
            'old_image_sha256': old_image, 'complete_image_sha256': complete_image,
            'mixed_image_sha256': mixed_image, 'physically_mixed': mixed_image not in (old_image, complete_image),
            'recovered_endpoint': 'old', 'qualification': 'test library splits a write then holder is actually killed'}


def run(output, control_only=False):
    compiler = subprocess.check_output(['cc', '--version'], text=True).splitlines()[0]
    with tempfile.TemporaryDirectory(prefix='kernel0-io-') as tmp:
        directory = Path(tmp)
        library = directory / 'kernel0_io_interposer.so'
        command = ['cc', '-shared', '-fPIC', '-std=c11', '-Wall', '-Wextra', '-Werror',
                   str(HERE / 'kernel0_io_interposer.c'), '-ldl', '-o', str(library)]
        subprocess.run(command, check=True, capture_output=True)
        library_hash = sha256(library.read_bytes()).hexdigest()
        cases = []
        for q in (m.Request('pair', 0, value=3), m.Request('accept', 0, value=1),
                  m.Request('replace', target=0, other=1)):
            reference, complete_image = control(directory / (q.kind + '-control'), library, q)
            cases.append({'operation': asdict(q), 'control_trace': reference, 'cuts': [], 'torn_writes': []})
            if not control_only:
                for cut in range(1, len(reference)+1):
                    cases[-1]['cuts'].append(replay(directory / f'{q.kind}-{cut}', library, q, reference, cut))
                for event in reference:
                    if event['op'] in ('pwrite', 'pwrite64') and event['phase'] == 'before' and event['file'] == 'authority.db':
                        for length in (event['size'] // 2, event['size'] - 16):
                            cases[-1]['torn_writes'].append(torn_write(
                                directory / f"{q.kind}-torn-{event['index']}-{length}", library, q,
                                reference, event['index'], length, complete_image))
                assert any(x['physically_mixed'] for x in cases[-1]['torn_writes'])
                assert {case['recovered_endpoint'] for case in cases[-1]['cuts']} == {'old', 'new'}
                # At least one kill follows a real main-database write but still
                # recovers old state: a substantive rollback, not only lost memory.
                assert any(case['cut']['op'] in ('pwrite', 'pwrite64') and case['cut']['phase'] == 'after'
                           and case['cut']['file'] == 'authority.db' and case['recovered_endpoint'] == 'old'
                           for case in cases[-1]['cuts'])
    result = {'profile': 'SIGKILL at observed storage-call boundaries; OS/storage remain live',
              'control_only': control_only, 'cases': cases,
              'runtime': {'python': sys.version, 'sqlite': sqlite3.sqlite_version,
                          'platform': platform.platform(), 'compiler': compiler},
              'library_sha256': library_hash, 'compile_flags': command[1:7] + ['-ldl'],
              'sources': {p.name: sha256(p.read_bytes()).hexdigest() for p in
                          (Path(__file__), HERE / 'kernel0_io_interposer.c', HERE / 'kernel0_recovery_service.py',
                           HERE / 'kernel0_recovery_check.py', HERE / 'kernel0_service.py', Path(m.__file__))}}
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'control_points': [len(c['control_trace']) for c in cases],
                      'actual_crash_cuts': sum(len(c['cuts']) for c in cases),
                      'deliberate_partial_writes': sum(len(c['torn_writes']) for c in cases),
                      'observed_calls': sorted({e['op'] for c in cases for e in c['control_trace']})}))


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('checks require Python without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--control-only', action='store_true')
    args = parser.parse_args()
    run(args.output, args.control_only)
