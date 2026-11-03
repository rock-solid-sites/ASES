#!/usr/bin/env python3
"""Test actual holder error handling under a disposable SQLite page ceiling."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sqlite3
import subprocess
import sys
import tempfile

KERNEL = Path(__file__).resolve().parent.parent / 'kernel-0'
sys.path.insert(0, str(KERNEL))
import kernel0_finite_model as model
import kernel0_recovery_check as check
import kernel0_recovery_service as service
import kernel0_service as core


def stats(db):
    return {name:db.execute('PRAGMA ' + name).fetchone()[0]
            for name in ('page_size', 'page_count', 'max_page_count')}


def holder(config):
    log_path = os.environ['F1_FULL_LOG']
    requested = int(os.environ['F1_FULL_PAGES'])
    class InstrumentedStore(service.Store):
        def log(self, entry):
            with open(log_path, 'a', encoding='utf-8') as out:
                out.write(json.dumps(entry, sort_keys=True) + '\n')
        def __init__(self, *args):
            super().__init__(*args)
            before = stats(self.db)
            target = before['page_count'] if requested == 0 else requested
            actual = self.db.execute('PRAGMA max_page_count=' + str(target)).fetchone()[0]
            after = stats(self.db)
            self.log({'stage':'cap_setup', 'pid':os.getpid(), 'before':before,
                      'requested':target, 'pragma_return':actual, 'after':after})
            if actual != target or after['max_page_count'] != target:
                raise RuntimeError('configured page cap was not achieved')
        def write(self, state):
            self.log({'stage':'before_write', 'pid':os.getpid(), 'stats':stats(self.db)})
            try:
                super().write(state)
            except sqlite3.Error as exc:
                self.log({'stage':'write_error', 'pid':os.getpid(), 'stats':stats(self.db),
                          'error_type':type(exc).__name__, 'message':str(exc),
                          'sqlite_errorcode':exc.sqlite_errorcode,
                          'sqlite_errorname':exc.sqlite_errorname})
                raise
    service.Store = InstrumentedStore
    service.serve(config)


def reader(path):
    with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True, timeout=10) as db:
        row = db.execute('SELECT root,profile,version,view FROM kernel WHERE id=1').fetchone()
        raw = row[3].encode('utf-8')
        print(json.dumps({'pid':os.getpid(), 'integrity':db.execute('PRAGMA integrity_check').fetchone()[0],
                          'root':row[0], 'profile':row[1], 'version':row[2],
                          'view':json.loads(row[3]), 'view_utf8_hex':raw.hex(),
                          'view_sha256':hashlib.sha256(raw).hexdigest(), 'stats':stats(db)}))


def independent(path):
    result = subprocess.run([sys.executable, __file__, '--reader', str(path)],
                            capture_output=True, text=True, timeout=10, check=True)
    return json.loads(result.stdout)


def file_bytes(root):
    sizes = {p.name:p.stat().st_size for p in Path(root).iterdir() if p.is_file()}
    assert sum(sizes.values()) <= 1_048_576, sizes
    return sizes


def stop_holder(h):
    pid = h.proc.pid
    h.proc.kill()
    code = h.proc.wait(timeout=10)
    stderr = h.proc.stderr.read().decode()
    h.proc.stdout.close()
    h.proc.stderr.close()
    for conn in h.clients:
        conn.close()
    os.close(h.event)
    os.close(h.release)
    assert code == -9
    return {'pid':pid, 'exit':code, 'stderr':stderr}


def run_case(root, variant):
    case = Path(root) / variant
    case.mkdir()
    path, log_path = case / 'store.sqlite', case / 'instrumentation.jsonl'
    check.setup(path)
    h = check.Holder(path)
    try:
        zero = h.request(model.Request('accept', 0, value=0))
        assert zero['outcome'] == 'commit' and zero['state']['content'] == core.CONTENTS[0]
    finally:
        prior_holder = stop_holder(h)
    with sqlite3.connect(path, isolation_level=None) as db:
        db.execute("CREATE INDEX fixture_growth ON kernel (CASE WHEN instr(view, 'one') > 0 THEN hex(zeroblob(4096)) ELSE '' END)")
        setup_stats = stats(db)
    before = independent(path)
    assert before['integrity'] == 'ok' and before['view'] == zero['state']
    setup_sizes = file_bytes(case)
    os.environ['F1_FULL_LOG'] = str(log_path)
    os.environ['F1_FULL_PAGES'] = '0' if variant == 'capped' else '64'
    try:
        h = check.Holder(path, service_path=Path(__file__).resolve())
    finally:
        del os.environ['F1_FULL_LOG']
        del os.environ['F1_FULL_PAGES']
    try:
        try:
            reply = h.request(model.Request('accept', 0, value=1))
            client = {'observation':'reply', 'reply':reply}
        except (EOFError, ConnectionResetError, BrokenPipeError, TimeoutError) as exc:
            client = {'observation':type(exc).__name__, 'message':str(exc)}
    finally:
        tested_holder = stop_holder(h)
    logs = [json.loads(line) for line in log_path.read_text().splitlines()]
    recovered = independent(path)
    cold = check.Holder(path)
    try:
        cold_read = cold.call({'kind':'read'})
    finally:
        cold_holder = stop_holder(cold)
    sizes = file_bytes(case)
    assert recovered['integrity'] == 'ok' and cold_read['state'] == recovered['view']
    assert before['root'] == recovered['root'] == 'work'
    assert before['profile'] == recovered['profile'] == 'independent'
    assert before['version'] == recovered['version'] == 1
    assert len(logs) >= 2 and logs[0]['stage'] == 'cap_setup'
    deciding = [e for e in logs if e['stage'] == 'before_write']
    assert len(deciding) == 1 and deciding[0]['stats']['max_page_count'] == logs[0]['requested']
    if variant == 'capped':
        errors = [e for e in logs if e['stage'] == 'write_error']
        assert len(errors) == 1 and errors[0]['sqlite_errorcode'] == sqlite3.SQLITE_FULL
        assert client['observation'] != 'reply'
        assert recovered['view_utf8_hex'] == before['view_utf8_hex']
        assert recovered['view'] == zero['state']
    else:
        assert not [e for e in logs if e['stage'] == 'write_error']
        assert client['observation'] == 'reply' and client['reply']['outcome'] == 'commit'
        assert client['reply']['state']['content'] == core.CONTENTS[1]
        assert recovered['view'] == client['reply']['state']
    return {'setup_stats':setup_stats, 'setup_files':setup_sizes, 'zero_ack':zero,
            'prior_holder':prior_holder, 'before':before, 'instrumentation':logs,
            'client':client, 'tested_holder':tested_holder, 'after':recovered,
            'cold_holder':cold_holder, 'cold_read':cold_read, 'final_files':sizes}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))
    with tempfile.TemporaryDirectory(prefix='f1-sqlite-full-') as directory:
        results = {name:run_case(directory, name) for name in ('neighbor', 'capped')}
        print(json.dumps({'platform':platform.platform(), 'python':sys.version.split()[0],
                          'sqlite':sqlite3.sqlite_version, 'bounds':{'fixed_cases':2,
                          'enumerated':False, 'truncated':False, 'address_space_bytes':512*1024*1024,
                          'max_temporary_bytes_per_case':1_048_576}, 'cases':results}, indent=2, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--reader':
        reader(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1].startswith('{'):
        holder(json.loads(sys.argv[1]))
    else:
        main()
