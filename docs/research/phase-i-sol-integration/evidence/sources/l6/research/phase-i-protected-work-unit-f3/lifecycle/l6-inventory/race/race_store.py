#!/usr/bin/env python3
"""Gate unchanged inventory guard; contrast detached empty scan mutation."""
import json
import os
from pathlib import Path
import resource
import sqlite3
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import store as base

ORIGINAL_SNAPSHOT=base.snapshot;ACTIVE=None
def snapshot(root):
    value=ORIGINAL_SNAPSHOT(root)
    if ACTIVE is not None and ACTIVE.scan_gate:
        ACTIVE.scan_gate=False;ACTIVE.gate('inventory-scanned-under-write-lock')
    return value
base.snapshot=snapshot
class Store(base.Store):
    scan_gate=False
    def apply(self,q):
        global ACTIVE
        if q['op']=='remove' and q.get('profile')=='detached-scan':
            value=ORIGINAL_SNAPSHOT(self.root)
            if value['files'] or any(not row['disposed'] for row in value['dependencies']):return dict(result='DENY',reason='durable-dependents-remain')
            self.gate('inventory-empty-before-write-lock')
            self.cx.execute('BEGIN IMMEDIATE');self.cx.execute('UPDATE unit SET live=0');self.cx.execute('COMMIT')
            return dict(result='COMMITTED',logical_unit_removed=True,physical_boundary_removed=False,profile='detached-scan')
        ACTIVE=self;self.scan_gate=q['op']=='remove' and q.get('gate')=='scan'
        try:return super().apply(q)
        finally:ACTIVE=None;self.scan_gate=False
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2);root=Path(sys.argv[1])
    try:state=Store(root)
    except ValueError as error:
        base.emit(dict(event='REFUSED',pid=os.getpid(),ns=time.monotonic_ns(),reason=str(error),snapshot=ORIGINAL_SNAPSHOT(root)));return 1
    base.emit(dict(event='READY',pid=os.getpid(),ns=time.monotonic_ns(),source_sha256=base.digest(Path(__file__).read_bytes()),
                   base_source_sha256=base.digest(Path(base.__file__).read_bytes()),snapshot=ORIGINAL_SNAPSHOT(root)))
    for line in sys.stdin:
        q=json.loads(line)
        if q['op']=='stop':break
        begin=time.monotonic_ns()
        try:reply=state.apply(q)
        except sqlite3.Error as error:
            reply=dict(result='DENY',reason='native-sql-error',error=str(error),sqlite_errorcode=error.sqlite_errorcode,
                       sqlite_errorname=error.sqlite_errorname,in_transaction=state.cx.in_transaction)
        base.emit(dict(event='RESPONSE',pid=os.getpid(),start_ns=begin,end_ns=time.monotonic_ns(),request=q,reply=reply,
                       sql_trace=list(state.trace),snapshot=ORIGINAL_SNAPSHOT(root)))
    state.cx.close();return 0
if __name__=='__main__':raise SystemExit(main())
