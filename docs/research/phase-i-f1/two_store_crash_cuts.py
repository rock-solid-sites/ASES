#!/usr/bin/env python3
"""Process-loss cuts across separate authority and witness SQLite commits."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_image(path, epoch):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE contents (name TEXT PRIMARY KEY, value BLOB)')
        db.execute('CREATE TABLE image (epoch INTEGER)')
        db.execute('INSERT INTO image VALUES (?)', (epoch,))
        db.execute('INSERT INTO contents VALUES (?, ?)', ('x', b'x\x00'))
        if epoch == 1:
            db.execute('INSERT INTO contents VALUES (?, ?)', ('y', b'y\n'))


def make_store(path, hash_value):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE state (epoch INTEGER, digest TEXT)')
        db.execute('INSERT INTO state VALUES (?, ?)', (0, hash_value))


def update(path, hash_value):
    with sqlite3.connect(path) as db:
        db.execute('UPDATE state SET epoch = ?, digest = ?', (1, hash_value))


def writer(root, order, count, new_hash):
    names = {'record-first': ['authority.sqlite', 'witness.sqlite'],
             'witness-first': ['witness.sqlite', 'authority.sqlite']}
    for name in names[order][:count]:
        update(Path(root) / name, new_hash)
    print(json.dumps({'pid':os.getpid(), 'commits':names[order][:count]}), flush=True)
    sys.stdin.read()


def read_store(path):
    with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True) as db:
        integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
        row = db.execute('SELECT epoch,digest FROM state').fetchone()
        return {'integrity':integrity, 'epoch':row[0], 'digest':row[1]}


def reader(root):
    root = Path(root)
    authority = read_store(root / 'authority.sqlite')
    witness = read_store(root / 'witness.sqlite')
    candidates = {}
    for name in ('old', 'new'):
        path = root / (name + '.sqlite')
        with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True) as db:
            integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
            epoch = db.execute('SELECT epoch FROM image').fetchone()[0]
            contents = {k:v.hex() for k,v in db.execute('SELECT name,value FROM contents ORDER BY name')}
        image_hash = sha(path)
        eligible = epoch <= authority['epoch']
        matches = image_hash == witness['digest'] and epoch == witness['epoch']
        admitted = integrity == 'ok' and eligible and matches
        candidates[name] = {'integrity':integrity, 'epoch':epoch, 'digest':image_hash,
                            'contents':contents, 'eligible':eligible, 'matches_witness':matches,
                            'admitted':admitted,
                            'oracle_current_if_admitted': (epoch == authority['epoch'] and image_hash == authority['digest']) if admitted else None}
    print(json.dumps({'pid':os.getpid(), 'authority':authority, 'witness':witness, 'candidates':candidates}))


def main():
    results = {}
    for name, order, count in [('initial', 'record-first', 0), ('record_first_cut', 'record-first', 1),
                               ('witness_first_cut', 'witness-first', 1),
                               ('record_first_complete', 'record-first', 2),
                               ('witness_first_complete', 'witness-first', 2)]:
        with tempfile.TemporaryDirectory(prefix='f1-cuts-') as tmp:
            root = Path(tmp)
            make_image(root / 'old.sqlite', 0)
            make_image(root / 'new.sqlite', 1)
            old_hash, new_hash = sha(root / 'old.sqlite'), sha(root / 'new.sqlite')
            assert old_hash != new_hash
            make_store(root / 'authority.sqlite', old_hash)
            make_store(root / 'witness.sqlite', old_hash)
            proc = subprocess.Popen([sys.executable, __file__, 'writer', tmp, order, str(count), new_hash],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            try:
                writer_info = json.loads(proc.stdout.readline())
                proc.kill()
                exit_code = proc.wait(timeout=5)
                assert exit_code == -9
                out = subprocess.run([sys.executable, __file__, 'reader', tmp], text=True,
                                     capture_output=True, timeout=5, check=True)
                recovered = json.loads(out.stdout)
                assert recovered['pid'] != writer_info['pid']
                assert recovered['authority']['integrity'] == recovered['witness']['integrity'] == 'ok'
                assert all(c['integrity'] == 'ok' for c in recovered['candidates'].values())
                results[name] = {'writer':writer_info, 'writer_exit':exit_code, 'recovery':recovered}
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=5)
                proc.stdin.close()
                proc.stdout.close()
    c = lambda name: results[name]['recovery']['candidates']
    assert c('initial')['old']['oracle_current_if_admitted'] is True
    assert c('record_first_cut')['old']['oracle_current_if_admitted'] is False
    assert not c('record_first_cut')['new']['admitted']
    assert not any(x['admitted'] for x in c('witness_first_cut').values())
    for name in ('record_first_complete', 'witness_first_complete'):
        assert c(name)['new']['oracle_current_if_admitted'] is True
        assert not c(name)['old']['admitted']
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'writer':
        writer(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) > 1 and sys.argv[1] == 'reader':
        reader(sys.argv[2])
    else:
        main()
