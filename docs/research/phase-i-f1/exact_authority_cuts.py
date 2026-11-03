#!/usr/bin/env python3
"""Exact authority-and-witness agreement across process-loss cuts."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import two_store_crash_cuts as base


def reader(root):
    root = Path(root)
    authority = base.read_store(root / 'authority.sqlite')
    witness = base.read_store(root / 'witness.sqlite')
    candidates = {}
    for name in ('old', 'new'):
        path = root / (name + '.sqlite')
        with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True) as db:
            integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
            epoch = db.execute('SELECT epoch FROM image').fetchone()[0]
            contents = {k:v.hex() for k,v in db.execute('SELECT name,value FROM contents ORDER BY name')}
        digest = base.sha(path)
        authority_match = epoch == authority['epoch'] and digest == authority['digest']
        witness_match = epoch == witness['epoch'] and digest == witness['digest']
        candidates[name] = {'integrity':integrity, 'epoch':epoch, 'digest':digest,
                            'contents':contents, 'authority_match':authority_match,
                            'witness_match':witness_match,
                            'admitted': integrity == 'ok' and authority_match and witness_match}
    print(json.dumps({'pid':os.getpid(), 'authority':authority, 'witness':witness, 'candidates':candidates}))


def main():
    results = {}
    cases = [('initial', 'record-first', 0, 'old'), ('record_first_cut', 'record-first', 1, None),
             ('witness_first_cut', 'witness-first', 1, None),
             ('record_first_complete', 'record-first', 2, 'new'),
             ('witness_first_complete', 'witness-first', 2, 'new')]
    for name, order, count, expected in cases:
        with tempfile.TemporaryDirectory(prefix='f1-exact-') as tmp:
            root = Path(tmp)
            base.make_image(root / 'old.sqlite', 0)
            base.make_image(root / 'new.sqlite', 1)
            old_hash, new_hash = base.sha(root / 'old.sqlite'), base.sha(root / 'new.sqlite')
            base.make_store(root / 'authority.sqlite', old_hash)
            base.make_store(root / 'witness.sqlite', old_hash)
            writer = subprocess.Popen([sys.executable, base.__file__, 'writer', tmp, order, str(count), new_hash],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            try:
                writer_info = json.loads(writer.stdout.readline())
                writer.kill()
                exit_code = writer.wait(timeout=5)
                assert exit_code == -9
                rec = subprocess.run([sys.executable, __file__, 'reader', tmp], text=True,
                                     capture_output=True, timeout=5, check=True)
                recovered = json.loads(rec.stdout)
                assert recovered['pid'] != writer_info['pid']
                assert recovered['authority']['integrity'] == recovered['witness']['integrity'] == 'ok'
                assert all(c['integrity'] == 'ok' for c in recovered['candidates'].values())
                admitted = [n for n,c in recovered['candidates'].items() if c['admitted']]
                assert admitted == ([] if expected is None else [expected])
                expected_authority = 1 if (order == 'record-first' and count >= 1) or count == 2 else 0
                assert recovered['authority']['epoch'] == expected_authority
                for candidate in recovered['candidates'].values():
                    if candidate['admitted']:
                        assert candidate['epoch'] == expected_authority
                        assert candidate['digest'] == (old_hash if expected_authority == 0 else new_hash)
                results[name] = {'writer':writer_info, 'writer_exit':exit_code,
                                 'expected_authority_epoch':expected_authority,
                                 'expected_admitted':expected, 'recovery':recovered}
            finally:
                if writer.poll() is None:
                    writer.kill()
                    writer.wait(timeout=5)
                writer.stdin.close()
                writer.stdout.close()
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reader':
        reader(sys.argv[2])
    else:
        main()
