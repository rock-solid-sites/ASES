#!/usr/bin/env python3
"""Two processes, one SQLite capacity unit, explicit pre-ACK observation."""
import json
import os
from pathlib import Path
import select
import sqlite3
import subprocess
import sys
import tempfile
import phase_i_f1_model as f1

TIMEOUT = 5


def send(message):
    print(json.dumps(message), flush=True)


def worker(path, owner, variant):
    with sqlite3.connect(path, isolation_level=None, timeout=TIMEOUT) as db:
        db.execute('PRAGMA synchronous=FULL')
        assert db.execute('PRAGMA journal_mode').fetchone()[0] == 'delete'
        send({'event':'ready', 'pid':os.getpid(), 'owner':owner})
        assert sys.stdin.readline().strip() == 'start'
        if variant == 'detached':
            count = db.execute('SELECT count(*) FROM reservations').fetchone()[0]
            send({'event':'precheck', 'owner':owner, 'count':count})
            assert sys.stdin.readline().strip() == 'proceed'
        db.execute('BEGIN IMMEDIATE')
        if variant == 'reference':
            count = db.execute('SELECT count(*) FROM reservations').fetchone()[0]
        if count != 0:
            db.execute('ROLLBACK')
            send({'event':'denied', 'owner':owner, 'count_seen':count})
            return
        db.execute('INSERT INTO reservations(owner) VALUES (?)', (owner,))
        db.execute('INSERT INTO effects(owner) VALUES (?)', (owner,))
        db.execute('COMMIT')
        send({'event':'committed', 'owner':owner, 'count_seen':count})
        assert sys.stdin.readline().strip() == 'ack'
        send({'event':'ack', 'owner':owner})


def receive(proc):
    readable, _, _ = select.select([proc.stdout], [], [], TIMEOUT)
    if not readable:
        raise TimeoutError(f'child {proc.pid} timed out')
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError(f'child {proc.pid} closed output')
    return json.loads(line)


def write(proc, command):
    proc.stdin.write((command + '\n').encode())
    proc.stdin.flush()


def run_case(root, variant):
    path = Path(root) / (variant + '.sqlite')
    with sqlite3.connect(path, isolation_level=None) as db:
        assert db.execute('PRAGMA journal_mode=DELETE').fetchone()[0] == 'delete'
        db.execute('PRAGMA synchronous=FULL')
        db.execute('CREATE TABLE reservations (owner TEXT NOT NULL)')
        db.execute('CREATE TABLE effects (owner TEXT NOT NULL)')
    procs = []
    try:
        for owner in ('C', 'S'):
            procs.append(subprocess.Popen([sys.executable, __file__, 'worker', str(path), owner, variant],
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, bufsize=0))
        ready = [receive(p) for p in procs]
        assert all(e['event'] == 'ready' for e in ready)
        assert len({e['pid'] for e in ready}) == 2
        for p in procs:
            write(p, 'start')
        prechecks = []
        if variant == 'detached':
            prechecks = [receive(p) for p in procs]
            assert all(e['event'] == 'precheck' and e['count'] == 0 for e in prechecks)
            for p in procs:
                write(p, 'proceed')
        decisions = [receive(p) for p in procs]
        assert all(e['event'] in ('committed', 'denied') for e in decisions)
        with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True, timeout=TIMEOUT) as db:
            before_ack = {'integrity':db.execute('PRAGMA integrity_check').fetchone()[0],
                          'reservations':[r[0] for r in db.execute('SELECT owner FROM reservations ORDER BY owner')],
                          'effects':[r[0] for r in db.execute('SELECT owner FROM effects ORDER BY owner')]}
        committed = sorted(e['owner'] for e in decisions if e['event'] == 'committed')
        assert before_ack['integrity'] == 'ok'
        assert before_ack['reservations'] == before_ack['effects'] == committed
        for p, decision in zip(procs, decisions):
            if decision['event'] == 'committed':
                write(p, 'ack')
        acks = [receive(p) for p, d in zip(procs, decisions) if d['event'] == 'committed']
        assert sorted(e['owner'] for e in acks if e['event'] == 'ack') == committed
        exits = [p.wait(timeout=TIMEOUT) for p in procs]
        assert exits == [0, 0]
        assert len(committed) == (1 if variant == 'reference' else 2)
        return {'ready':ready, 'prechecks':prechecks, 'decisions':decisions,
                'pre_ack_observer':before_ack, 'acks':acks, 'exits':exits,
                'capacity_invariant':len(before_ack['reservations']) <= 1}
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
                p.wait(timeout=TIMEOUT)
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()


def f1_control():
    state = f1.initial()
    outcomes = []
    for owner in (f1.C, f1.S):
        result, state, reason = f1.resolve(state, ('reserve_capacity', owner), f1.REFERENCE)
        outcomes.append({'owner':owner, 'outcome':result, 'reason':reason})
    assert [x['outcome'] for x in outcomes] == ['commit', 'deny']
    return {'outcomes':outcomes, 'final_owner':state.capacity_reserved,
            'invariant':f1.invariant(state, f1.REFERENCE)}


def main():
    with tempfile.TemporaryDirectory(prefix='f1-sqlite-race-') as directory:
        reference = run_case(directory, 'reference')
        mutant = run_case(directory, 'detached')
        assert reference['capacity_invariant'] and not mutant['capacity_invariant']
        print(json.dumps({'reference':reference, 'detached_mutant':mutant,
                          'f1_serial_control':f1_control(),
                          'bounds':{'schedules':2, 'writers_per_schedule':2, 'enumerated':False,
                                    'truncated':False}, 'sqlite':sqlite3.sqlite_version}, indent=2, sort_keys=True))

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        worker(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        main()
