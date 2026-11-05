#!/usr/bin/env python3
"""Native prepare visibility with actual locked-reader COMMIT failure/control."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('resource_commit_support',HERE/'probe.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def release(reader):
    start=time.monotonic_ns();reader.execute('ROLLBACK')
    return dict(start_ns=start,end_ns=time.monotonic_ns(),in_transaction=reader.in_transaction)
def actual_recovery(path):
    start=time.monotonic_ns()
    db=base.db_open(path)
    try:
        rows=[row[0] for row in db.execute('SELECT holder FROM claims ORDER BY holder')]
        integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
    finally:db.close()
    return dict(start_ns=start,end_ns=time.monotonic_ns(),claims=rows,integrity=integrity)
def one(root,kind):
    root.mkdir();path=root/'ledger.sqlite'
    db=base.db_open(path);db.execute('CREATE TABLE claims(holder TEXT PRIMARY KEY)');db.close()
    original,allocated=base.native(0);assert original is not None
    port=original.getsockname()[1];original.close();initial_close_ns=time.monotonic_ns()
    reader=sqlite3.connect(path,isolation_level=None,timeout=2)
    reader_start=time.monotonic_ns();reader.execute('BEGIN')
    reader_claims=[r[0] for r in reader.execute('SELECT holder FROM claims')]
    held=dict(pid=os.getpid(),start_ns=reader_start,snapshot_ns=time.monotonic_ns(),claims=reader_claims,in_transaction=reader.in_transaction,
              journal_mode=reader.execute('PRAGMA journal_mode').fetchone()[0])
    child=base.Child('--B',dict(db=str(path),port=port,variant='native-guarded',prepare_gate=True,busy_timeout_ms=100))
    reader_closed=False
    try:
        prepared=child.read()
        native_while_uncommitted=base.probe_bind(port)
        read_at_gate=dict(ns=time.monotonic_ns(),claims=[r[0] for r in reader.execute('SELECT holder FROM claims')],in_transaction=reader.in_transaction)
        released=None;continuation=None;outcome=None
        if kind=='killed':
            process=child.finish(kill=True)
            released=release(reader)
        else:
            if kind=='released':released=release(reader)
            continuation=time.monotonic_ns();outcome=child.command('commit')
            if kind=='busy':
                reader_after=dict(ns=time.monotonic_ns(),in_transaction=reader.in_transaction)
                process=child.finish();released=release(reader)
            else:
                live_native_probe=base.probe_bind(port)
                process=child.finish(kill=True)
        reader.close();reader_closed=True
        recovered=actual_recovery(path);native_after=base.probe_bind(port)
    finally:
        if not reader_closed:
            if reader.in_transaction:reader.execute('ROLLBACK')
            reader.close()
        if child.process.poll() is None:child.finish(kill=True)
    return dict(kind=kind,port=port,parent_allocated=allocated,initial_native_close_ns=initial_close_ns,reader_held=held,
                prepared=prepared,native_while_uncommitted=native_while_uncommitted,reader_at_gate=read_at_gate,
                continue_ns=continuation,reader_release=released,reader_after_failed_commit=reader_after if kind=='busy' else None,
                outcome=outcome,live_native_probe=live_native_probe if kind=='released' else None,process=process,
                recovered_ledger=recovered,native_after=native_after)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    try:
        with tempfile.TemporaryDirectory(prefix='ases-native-commit-failure-') as directory:
            root=Path(directory);cases={kind:one(root/kind,kind) for kind in ('busy','released','killed')}
            print(json.dumps(dict(schema='ases.native-prepared-commit-failure',version=1,
                                  execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                                  source_hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('probe.py','commit_failure_probe.py')},
                                  environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
                                  executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                                  cases=cases,children=[c.meta for c in base.OWNED]),indent=2,sort_keys=True))
    finally:
        for child in base.OWNED:
            if child.process.poll() is None:child.finish(kill=True)
if __name__=='__main__':main()
