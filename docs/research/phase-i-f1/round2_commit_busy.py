#!/usr/bin/env python3
"""Real SQLite COMMIT lock failure through unchanged holder Boundary.resolve."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import select
import sqlite3
import subprocess
import sys
import tempfile
import time
import sqlite_full_holder_recovery as old

HERE=Path(__file__).resolve().parent

def lock_reader(path):
    db=sqlite3.connect(path,isolation_level=None)
    db.execute('BEGIN')
    row=db.execute('SELECT view FROM kernel WHERE id=1').fetchone()
    print(json.dumps({'pid':os.getpid(),'stage':'read_lock_held','view_sha256':hashlib.sha256(row[0].encode()).hexdigest()}),flush=True)
    if sys.stdin.readline()!='release\n':
        return 2
    db.execute('ROLLBACK')
    db.close()
    print(json.dumps({'pid':os.getpid(),'stage':'released'}),flush=True)
    return 0

def holder(config):
    log=Path(os.environ['F1_COMMIT_LOG'])
    class Trace:
        def __init__(self,db): self.db=db
        def __getattr__(self,name): return getattr(self.db,name)
        def execute(self,sql,*args):
            start=time.monotonic_ns()
            try:
                result=self.db.execute(sql,*args)
            except sqlite3.Error as exc:
                with log.open('a') as f:
                    f.write(json.dumps({'sql':sql,'outcome':'error','code':exc.sqlite_errorcode,
                                        'name':exc.sqlite_errorname,'message':str(exc),
                                        'in_transaction':self.db.in_transaction,'start_ns':start,
                                        'end_ns':time.monotonic_ns()})+'\n')
                raise
            with log.open('a') as f:
                f.write(json.dumps({'sql':sql,'outcome':'completed','in_transaction':self.db.in_transaction,
                                    'start_ns':start,'end_ns':time.monotonic_ns()})+'\n')
            return result
    class Instrumented(old.service.Store):
        def __init__(self,*args):
            super().__init__(*args)
            self.db.execute('PRAGMA busy_timeout=100')
            assert self.db.execute('PRAGMA busy_timeout').fetchone()[0]==100
            self.db=Trace(self.db)
    old.service.Store=Instrumented
    old.service.serve(config)

def release(proc):
    proc.stdin.write('release\n');proc.stdin.flush()
    out,err=proc.communicate(timeout=4)
    assert proc.returncode==0 and not err
    return {'exit':proc.returncode,'stdout':out,'stderr':err}

def case(root,name):
    root.mkdir()
    path=root/'store.sqlite';log=root/'trace.jsonl'
    old.check.setup(path)
    h=old.check.Holder(path)
    try:
        zero=h.request(old.model.Request('accept',0,value=0))
        assert zero['outcome']=='commit'
    finally: bootstrap=old.stop_holder(h)
    before=old.independent(path)
    locker=subprocess.Popen([sys.executable,__file__,'--lock',str(path)],stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    h=None
    try:
        assert select.select([locker.stdout],[],[],4)[0], 'reader readiness timeout'
        lock_info=json.loads(locker.stdout.readline())
        assert lock_info['view_sha256']==before['view_sha256']
        lock_release=release(locker) if name=='released_control' else None
        os.environ['F1_COMMIT_LOG']=str(log)
        try: h=old.check.Holder(path,service_path=Path(__file__).resolve())
        finally: del os.environ['F1_COMMIT_LOG']
        try:
            reply=h.request(old.model.Request('accept',0,value=1))
            client={'kind':'reply','reply':reply}
        except (EOFError,ConnectionResetError,BrokenPipeError,TimeoutError) as exc:
            client={'kind':type(exc).__name__,'message':str(exc)}
        # The competing reader is still alive while writer has failed/rolled back.
        locker_alive_before_release=locker.poll() is None
        tested=old.stop_holder(h);h=None
        if lock_release is None: lock_release=release(locker)
    finally:
        if h is not None: old.stop_holder(h)
        if locker.poll() is None:
            locker.kill();locker.communicate(timeout=2)
    after=old.independent(path)
    cold=old.check.Holder(path)
    try: cold_read=cold.call({'kind':'read'})
    finally: cold_exit=old.stop_holder(cold)
    trace=[json.loads(x) for x in log.read_text().splitlines()]
    update=next(x for x in trace if x['sql'].startswith('UPDATE'))
    commit=next(x for x in trace if x['sql']=='COMMIT')
    assert update['outcome']=='completed' and update['in_transaction']
    assert update['end_ns']<commit['start_ns']
    if name=='held_reader':
        assert commit['outcome']=='error' and commit['code']==sqlite3.SQLITE_BUSY and commit['in_transaction']
        assert any(x['sql']=='ROLLBACK' and x['outcome']=='completed' and not x['in_transaction'] for x in trace)
        assert client['kind']!='reply' and after['view_utf8_hex']==before['view_utf8_hex']
        assert locker_alive_before_release
    else:
        assert commit['outcome']=='completed' and not commit['in_transaction']
        assert client['reply']['outcome']=='commit' and client['reply']['state']['content']==old.core.CONTENTS[1]
        assert after['view']==client['reply']['state']
    assert before['integrity']==after['integrity']=='ok' and cold_read['state']==after['view']
    return {'bootstrap_exit':bootstrap,'prior_ack':zero,'before':before,'lock_info':lock_info,
            'locker_alive_before_release':locker_alive_before_release,'lock_release':lock_release,
            'client':client,'trace':trace,'holder_exit':tested,'after':after,'cold_read':cold_read,
            'cold_exit':cold_exit,'files':old.file_bytes(root)}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    if len(sys.argv)==3 and sys.argv[1]=='--lock': return lock_reader(sys.argv[2])
    if len(sys.argv)==2 and sys.argv[1].startswith('{'):
        holder(json.loads(sys.argv[1]));return 0
    with tempfile.TemporaryDirectory(prefix='ases-round2-commit-') as td:
        results={n:case(Path(td)/n,n) for n in ['released_control','held_reader']}
    print(json.dumps({'schema':'ases.f1-commit-busy.v1','environment':{'python':sys.version,'sqlite':sqlite3.sqlite_version,
                       'platform':platform.platform(),'executable':sys.executable,
                       'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                      'hashes':{str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                [Path(__file__),HERE/'sqlite_full_holder_recovery.py',old.KERNEL/'kernel0_recovery_service.py',old.KERNEL/'kernel0_recovery_check.py']},
                      'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'cases':results},indent=2,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
