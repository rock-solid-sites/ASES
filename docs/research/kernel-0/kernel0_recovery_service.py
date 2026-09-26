#!/usr/bin/env python3
"""Bounded persistent holder. Trusted bootstrap only; see Crash-Recovery.md."""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys
import threading

import kernel0_service as core


class Store:
    def __init__(self, path, root, profile):
        self.db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=rw', uri=True,
                                  isolation_level=None, check_same_thread=False)
        self.db.execute('PRAGMA synchronous=FULL')
        mode = self.db.execute('PRAGMA journal_mode').fetchone()[0]
        if mode != 'delete':
            raise ValueError('only declared rollback-journal profile accepted')
        self.root, self.profile = root, profile
        self.read()  # Fail before exposing any endpoint.

    def read(self):
        row = self.db.execute('SELECT root, profile, version, view FROM kernel WHERE id=1').fetchone()
        if row is None or row[:3] != (self.root, self.profile, 1):
            raise ValueError('recovery root/profile/schema mismatch')
        raw = json.loads(row[3], object_pairs_hook=core.unique_object)
        for field in ('data', 'rights', 'parents', 'cycle'):
            raw[field] = tuple(raw[field])
        state = core.View(**raw)
        if not core.valid(state, self.profile):
            raise ValueError('invalid recovered whole view')
        return state

    def write(self, state):
        self.db.execute('UPDATE kernel SET view=? WHERE id=1',
                        (json.dumps(asdict(state), sort_keys=True),))


def initialize(path, root, profile):
    if profile not in ('independent', 'coupled', 'exclusive'):
        raise ValueError('unknown policy')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    with sqlite3.connect(path, isolation_level=None) as db:
        db.execute('PRAGMA journal_mode=DELETE')
        db.execute('PRAGMA synchronous=FULL')
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE TABLE kernel (id INTEGER PRIMARY KEY CHECK(id=1), root TEXT NOT NULL, '
                   'profile TEXT NOT NULL, version INTEGER NOT NULL, view TEXT NOT NULL)')
        db.execute('INSERT INTO kernel VALUES(1,?,?,1,?)',
                   (root, profile, json.dumps(asdict(core.View()), sort_keys=True)))
        db.execute('COMMIT')


class Boundary:
    def __init__(self, config):
        self.store = Store(config['path'], config['root'], config['profile'])
        self.profile = config['profile']
        self.lock = threading.Lock()

    def propose(self, current, context, q):
        return core.candidate(current, context, q, self.profile)

    def resolve(self, context, q, gate):
        with self.lock:
            db = self.store.db
            db.execute('BEGIN IMMEDIATE')
            try:
                current = self.store.read()
                if q is None or q.kind == 'read':
                    db.execute('ROLLBACK')
                    return {'outcome': 'deny' if q is None else 'read', 'state': asdict(current)}
                candidate = self.propose(current, context, q)
                admitted = candidate is not None and core.valid(candidate, self.profile)
                gate('validated')
                if admitted:
                    self.store.write(candidate)
                    gate('prepared')
                    gate('commit_enter')
                    db.execute('COMMIT')
                    gate('durable')
                    current = candidate
                else:
                    db.execute('ROLLBACK')
                result = {'outcome': 'commit' if admitted else 'deny', 'state': asdict(current)}
            except Exception:
                if db.in_transaction:
                    db.execute('ROLLBACK')
                raise  # Handler fails closed; no fabricated deny after uncertain commit.
        gate('published')
        return result


def serve(config, boundary=None):
    boundary = Boundary(config) if boundary is None else boundary
    schedule = config.get('gate')
    used = threading.Event()

    def handle(lane, context, fd):
        def gate(stage):
            if (schedule and not used.is_set() and schedule['lane'] == lane
                    and schedule['kind'] == q.kind and schedule['stage'] == stage):
                used.set()
                os.write(schedule['event_fd'], b'G')
                os.read(schedule['release_fd'], 1)

        with socket.socket(fileno=fd) as conn, conn.makefile('rb') as incoming:
            while True:
                raw = incoming.readline(core.MAX_FRAME + 1)
                if not raw or len(raw) > core.MAX_FRAME or not raw.endswith(b'\n'):
                    return
                try:
                    q = core.decode(raw)
                except (ValueError, TypeError, RecursionError):
                    q = None
                if q is not None:
                    gate('received')
                reply = boundary.resolve(context, q, gate)
                if q is not None:
                    gate('before_ack')
                try:
                    conn.sendall(json.dumps(reply).encode() + b'\n')
                except (BrokenPipeError, ConnectionResetError):
                    return

    threads = []
    for lane, (context, fd) in enumerate(config['channels']):
        if context not in (-1, 0, 1, 2, 3):
            raise ValueError('unrecognized trusted association')
        thread = threading.Thread(target=handle, args=(lane, context, fd), daemon=True)
        thread.start()
        threads.append(thread)
    print('ready', flush=True)
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    config = json.loads(sys.argv[2] if sys.argv[1] == '--initialize' else sys.argv[1])
    if sys.argv[1] == '--initialize':
        initialize(config['path'], config['root'], config['profile'])
    else:
        serve(config)
