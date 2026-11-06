#!/usr/bin/env python3
"""Disposable flat dependency store; trusted management, no execution confinement."""
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import sqlite3
import sys
import time

def digest(raw):return hashlib.sha256(raw).hexdigest()
def emit(value):print(json.dumps(value,sort_keys=True),flush=True)
def bootstrap(root):
    root.mkdir(mode=0o700);(root/'objects').mkdir(mode=0o700)
    cx=sqlite3.connect(root/'catalog.sqlite',isolation_level=None)
    cx.executescript('PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; CREATE TABLE unit(live INTEGER NOT NULL,sealed INTEGER NOT NULL); CREATE TABLE dependencies(name TEXT PRIMARY KEY,kind TEXT NOT NULL,sha256 TEXT NOT NULL,size INTEGER NOT NULL,disposed INTEGER NOT NULL); BEGIN IMMEDIATE; INSERT INTO unit VALUES(1,1); COMMIT;');cx.close()
def snapshot(root):
    cx=sqlite3.connect('file:'+str(root/'catalog.sqlite')+'?mode=ro',uri=True,isolation_level=None)
    live,sealed=cx.execute('SELECT live,sealed FROM unit').fetchone()
    rows=[dict(zip(('name','kind','sha256','size','disposed'),row)) for row in cx.execute('SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name')]
    integrity=cx.execute('PRAGMA integrity_check').fetchone()[0];cx.close()
    files={}
    if (root/'objects').exists():
        for path in sorted((root/'objects').iterdir()):
            if not path.is_file() or path.is_symlink():raise ValueError('unsupported non-flat object')
            raw=path.read_bytes();st=path.stat();files[path.name]=dict(raw_hex=raw.hex(),sha256=digest(raw),size=len(raw),inode=st.st_ino,mode=st.st_mode&0o777)
    known={row['name'] for row in rows};unknown=sorted(set(files)-known)
    return dict(observation_ns=time.monotonic_ns(),integrity_check=integrity,live=bool(live),sealed=bool(sealed),dependencies=rows,files=files,unknown_files=unknown,
                objects_directory_exists=(root/'objects').exists(),reconstruction_status='unresolved-unregistered-material' if unknown else 'current-logical-records')

class Store:
    def __init__(self,root):
        self.root=root;self.trace=[]
        if not (root/'catalog.sqlite').is_file():raise ValueError('missing-current-catalog-no-bootstrap')
        self.cx=sqlite3.connect(root/'catalog.sqlite',isolation_level=None,timeout=.15)
        self.cx.set_trace_callback(lambda sql:self.trace.append(dict(ns=time.monotonic_ns(),sql=sql)))
        self.cx.execute('PRAGMA journal_mode=DELETE');self.cx.execute('PRAGMA synchronous=FULL')
        value=snapshot(root)
        if not value['sealed']:raise ValueError('unsupported active unit')
        if not value['live'] and value['files']:raise ValueError('removed-unit-has-surviving-material')
        for row in value['dependencies']:
            if row['disposed']:continue
            if row['name'] not in value['files'] or any(row[k]!=value['files'][row['name']][k] for k in ('sha256','size')):
                raise ValueError('missing-inconsistent-live-dependent')
    def gate(self,phase):
        emit(dict(event='GATE',phase=phase,pid=os.getpid(),ns=time.monotonic_ns(),in_transaction=self.cx.in_transaction,
                  local_dependency_rows=self.cx.execute('SELECT COUNT(*) FROM dependencies').fetchone()[0],sql_trace=list(self.trace)))
        if sys.stdin.readline().strip()!='continue':raise RuntimeError('gate continuation not supplied')
    def apply(self,q):
        op=q['op'];name=q.get('name')
        if name is not None and (not isinstance(name,str) or re.fullmatch('[a-z]+',name) is None):raise ValueError('invalid flat object name')
        if op=='read':
            row=self.cx.execute('SELECT kind,sha256,size,disposed FROM dependencies WHERE name=?',(name,)).fetchone()
            if not row:return dict(result='DENY',reason='unregistered')
            if row[3]:return dict(result='DENY',reason='logically-disposed')
            raw=(self.root/'objects'/name).read_bytes()
            if digest(raw)!=row[1] or len(raw)!=row[2]:raise ValueError('live-dependent-integrity')
            return dict(result='READ',name=name,kind=row[0],raw_hex=raw.hex(),sha256=digest(raw))
        self.cx.execute('BEGIN IMMEDIATE')
        if not self.cx.execute('SELECT live FROM unit').fetchone()[0]:
            self.cx.execute('ROLLBACK');return dict(result='DENY',reason='unit-removed')
        if op=='put':
            if snapshot(self.root)['unknown_files']:
                self.cx.execute('ROLLBACK');return dict(result='DENY',reason='unresolved-unregistered-material')
            kind=q['kind'];raw=q['payload'].encode();path=self.root/'objects'/name
            if kind not in ('accepted','candidate'):raise ValueError('invalid dependent kind')
            with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            self.cx.execute('INSERT INTO dependencies VALUES(?,?,?,?,0)',(name,kind,digest(raw),len(raw)))
            if q.get('gate')=='precommit':self.gate('file-fsynced-row-uncommitted')
            self.cx.execute('COMMIT');return dict(result='COMMITTED',name=name,kind=kind,sha256=digest(raw))
        if op=='dispose':
            row=self.cx.execute('SELECT disposed FROM dependencies WHERE name=?',(name,)).fetchone()
            if not row or row[0]:
                self.cx.execute('ROLLBACK');return dict(result='DENY',reason='not-live-dependent')
            self.cx.execute('UPDATE dependencies SET disposed=1 WHERE name=?',(name,));self.cx.execute('COMMIT')
            if q.get('gate')=='postcommit':self.gate('disposition-committed-before-unlink-reply')
            (self.root/'objects'/name).unlink();return dict(result='COMMITTED',name=name,logical_disposition=True)
        if op=='cleanup':
            row=self.cx.execute('SELECT disposed FROM dependencies WHERE name=?',(name,)).fetchone()
            if not row or not row[0]:
                self.cx.execute('ROLLBACK');return dict(result='DENY',reason='cleanup-requires-disposition')
            (self.root/'objects'/name).unlink();self.cx.execute('COMMIT');return dict(result='COMMITTED',name=name,cleanup=True)
        if op=='remove':
            value=snapshot(self.root);catalog_live=self.cx.execute('SELECT COUNT(*) FROM dependencies WHERE disposed=0').fetchone()[0]
            if q.get('profile')=='catalog-only':blocked=catalog_live!=0
            else:blocked=bool(value['files']) or catalog_live!=0
            if blocked:
                self.cx.execute('ROLLBACK');return dict(result='DENY',reason='durable-dependents-remain',inventory=sorted(value['files']))
            self.cx.execute('UPDATE unit SET live=0');self.cx.execute('COMMIT')
            # Weak mutation demonstrates logical removal admission only. It does
            # not pretend an ordinary POSIX directory's protection disappeared.
            if q.get('profile')=='catalog-only':return dict(result='COMMITTED',logical_unit_removed=True,physical_boundary_removed=False,profile='catalog-only')
            (self.root/'objects').rmdir();return dict(result='COMMITTED',logical_unit_removed=True,directory_removed=True,profile='directory-inventory')
        self.cx.execute('ROLLBACK');raise ValueError('unsupported operation')

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    root=Path(sys.argv[1]);store=Store(root)
    emit(dict(event='READY',pid=os.getpid(),ns=time.monotonic_ns(),source_sha256=digest(Path(__file__).read_bytes()),snapshot=snapshot(root)))
    for line in sys.stdin:
        q=json.loads(line)
        if q['op']=='stop':break
        begin=time.monotonic_ns();reply=store.apply(q)
        emit(dict(event='RESPONSE',pid=os.getpid(),start_ns=begin,end_ns=time.monotonic_ns(),request=q,reply=reply,
                  sql_trace=list(store.trace),snapshot=snapshot(root)))
    store.cx.close()
if __name__=='__main__':main()
