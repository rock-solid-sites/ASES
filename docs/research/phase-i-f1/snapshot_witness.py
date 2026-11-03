#!/usr/bin/env python3
"""Snapshot freshness discriminator with a supervisor-held digest witness."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

X = b'accepted\x00one\n'
Y = b'accepted\x00two\n'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def backup(db, path):
    with sqlite3.connect(path) as dest:
        db.backup(dest)


def writer(directory):
    root = Path(directory)
    with sqlite3.connect(root / 'live.sqlite') as db:
        db.execute('CREATE TABLE records (name TEXT PRIMARY KEY, value BLOB NOT NULL)')
        db.execute('CREATE TABLE metadata (epoch INTEGER NOT NULL)')
        db.execute('INSERT INTO metadata VALUES (0)')
        db.execute('INSERT INTO records VALUES (?, ?)', ('x', X))
        db.commit()
        old = root / 'old.sqlite'
        backup(db, old)
        db.execute('INSERT INTO records VALUES (?, ?)', ('y', Y))
        db.execute('UPDATE metadata SET epoch=1')
        db.commit()
        current = root / 'current.sqlite'
        backup(db, current)
        print(json.dumps({'pid': os.getpid(), 'old': str(old), 'current': str(current),
                          'old_digest': digest(old), 'current_digest': digest(current)}), flush=True)
        sys.stdin.read()


def receiver():
    request = json.load(sys.stdin)
    path = request['path']
    observed = digest(path)
    with sqlite3.connect('file:' + path + '?mode=ro', uri=True) as db:
        integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity != 'ok':
            result = {'decision':'deny', 'reason':'integrity', 'integrity':integrity}
        elif request['witness'] is None:
            result = {'decision':'deny', 'reason':'witness-unavailable', 'integrity':integrity}
        elif request['compare'] and observed != request['witness']:
            result = {'decision':'deny', 'reason':'digest-mismatch', 'integrity':integrity}
        else:
            result = {'decision':'accept', 'reason':None, 'integrity':integrity,
                      'epoch': db.execute('SELECT epoch FROM metadata').fetchone()[0],
                      'records': {key: value.hex() for key, value in db.execute('SELECT name,value FROM records ORDER BY name')}}
    result.update({'observed_digest':observed, 'pid':os.getpid()})
    print(json.dumps(result))


def main():
    with tempfile.TemporaryDirectory(prefix='f1-snapshot-') as directory:
        process = subprocess.Popen([sys.executable, __file__, 'writer', directory],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            record = json.loads(process.stdout.readline())
            old_digest, current_digest = digest(record['old']), digest(record['current'])
            assert old_digest == record['old_digest'] and current_digest == record['current_digest']
            assert old_digest != current_digest
            process.kill()
            exit_code = process.wait(timeout=5)
            assert exit_code == -9
            cases = [('current_with_witness', 'current', current_digest, True),
                     ('old_with_witness', 'old', current_digest, True),
                     ('current_without_witness', 'current', None, True),
                     ('old_comparison_bypassed', 'old', current_digest, False)]
            results = {}
            for name, snapshot, witness, compare in cases:
                request = {'path':record[snapshot], 'witness':witness, 'compare':compare}
                proc = subprocess.run([sys.executable, __file__, 'receiver'], input=json.dumps(request),
                                      text=True, capture_output=True, timeout=5, check=True)
                out = json.loads(proc.stdout)
                out['oracle_current_if_accepted'] = (None if out['decision'] != 'accept'
                                                     else out['observed_digest'] == current_digest
                                                     and out['epoch'] == 1
                                                     and out['records'] == {'x':X.hex(), 'y':Y.hex()})
                results[name] = out
            assert len({v['pid'] for v in results.values()} | {record['pid']}) == 5
            assert all(v['integrity'] == 'ok' for v in results.values())
            assert results['current_with_witness']['oracle_current_if_accepted'] is True
            assert results['old_with_witness']['reason'] == 'digest-mismatch'
            assert results['current_without_witness']['reason'] == 'witness-unavailable'
            assert results['old_comparison_bypassed']['oracle_current_if_accepted'] is False
            print(json.dumps({'writer_pid':record['pid'], 'writer_exit':exit_code,
                              'old_digest':old_digest, 'trusted_current_digest':current_digest,
                              'cases':results}, indent=2, sort_keys=True))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdin.close()
            process.stdout.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'writer':
        writer(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == 'receiver':
        receiver()
    else:
        main()
