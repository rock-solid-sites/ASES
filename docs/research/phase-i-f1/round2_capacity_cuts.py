#!/usr/bin/env python3
"""Guarded/ detached capacity claims across rollback and committed lost ACK."""
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


def emit(event,**kw):print(json.dumps({'event':event,'pid':os.getpid(),'ns':time.monotonic_ns(),**kw}),flush=True)
def worker(path,owner,mode):
    db=sqlite3.connect(path,isolation_level=None,timeout=4)
    db.execute('PRAGMA synchronous=FULL')
    assert db.execute('PRAGMA journal_mode').fetchone()[0]=='delete'
    emit('ready');assert sys.stdin.readline().strip()=='start'
    if mode=='detached':
        count=db.execute('SELECT count(*) FROM reservations').fetchone()[0]
        emit('precheck',count=count);assert sys.stdin.readline().strip()=='proceed'
    emit('begin_attempt')
    db.execute('BEGIN IMMEDIATE');emit('begin_acquired')
    if mode!='detached':count=db.execute('SELECT count(*) FROM reservations').fetchone()[0]
    if count:
        db.execute('ROLLBACK');emit('denied',count=count);return
    db.execute('INSERT INTO reservations VALUES (?)',(owner,))
    db.execute('INSERT INTO effects VALUES (?)',(owner,))
    if mode=='gate':
        emit('prepared');assert sys.stdin.readline().strip()=='commit'
    db.execute('COMMIT');emit('committed',count=count)
    assert sys.stdin.readline().strip()=='ack'
    emit('ack');db.close()

def receive(p,events):
    assert select.select([p.stdout],[],[],4)[0], 'event timeout'
    r=json.loads(p.stdout.readline());events.append(r);return r

def send(p,s):p.stdin.write((s+'\n').encode());p.stdin.flush()
def observe(path):
    with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=4) as db:
        return {'integrity':db.execute('PRAGMA integrity_check').fetchone()[0],
                'reservations':[r[0] for r in db.execute('SELECT owner FROM reservations ORDER BY owner')],
                'effects':[r[0] for r in db.execute('SELECT owner FROM effects ORDER BY owner')]}
def case(root,name):
    path=root/(name+'.sqlite')
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA journal_mode=DELETE')
        db.execute('CREATE TABLE reservations(owner TEXT NOT NULL)')
        db.execute('CREATE TABLE effects(owner TEXT NOT NULL)')
    procs=[];events={'A':[],'B':[]}
    try:
        for owner,mode in [('A','gate'),('B','detached' if name=='detached_after_commit' else 'guarded')]:
            p=subprocess.Popen([sys.executable,__file__,'--worker',str(path),owner,mode],
                               stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
            procs.append(p);assert receive(p,events[owner])['event']=='ready'
        a,b=procs
        send(a,'start')
        assert [receive(a,events['A'])['event'] for _ in range(3)]==['begin_attempt','begin_acquired','prepared']
        precommit_observer=observe(path)
        assert precommit_observer['reservations']==precommit_observer['effects']==[]
        send(b,'start')
        if name=='detached_after_commit':
            pre=receive(b,events['B']);assert pre['event']=='precheck' and pre['count']==0
        else:
            assert receive(b,events['B'])['event']=='begin_attempt'
        if name!='kill_before_commit':
            send(a,'commit');assert receive(a,events['A'])['event']=='committed'
        at_cut_observer=observe(path)
        kill_start=time.monotonic_ns();a.kill();a.wait(timeout=4);reaped=time.monotonic_ns()
        assert a.returncode==-9
        if name=='detached_after_commit':
            send(b,'proceed');assert receive(b,events['B'])['event']=='begin_attempt'
        acquired=receive(b,events['B']);assert acquired['event']=='begin_acquired'
        decision=receive(b,events['B'])
        if decision['event']=='committed':
            before_ack=observe(path);send(b,'ack');assert receive(b,events['B'])['event']=='ack'
        else:before_ack=observe(path)
        b.wait(timeout=4);assert b.returncode==0
        final=observe(path)
        expected=['B'] if name=='kill_before_commit' else ['A'] if name=='kill_after_commit' else ['A','B']
        assert final['integrity']=='ok' and final['reservations']==final['effects']==expected
        assert at_cut_observer['reservations']==([] if name=='kill_before_commit' else ['A'])
        if name!='detached_after_commit':
            attempt=next(e for e in events['B'] if e['event']=='begin_attempt')
            assert attempt['ns']<kill_start<acquired['ns']
        errors={owner:p.stderr.read().decode() for owner,p in zip(['A','B'],procs)}
        assert set(errors.values())=={''}
        assert path.stat().st_size<1_048_576
        return {'events':events,'kill_start_ns':kill_start,'reaped_ns':reaped,'exits':[p.returncode for p in procs],
                'stderr':errors,'precommit_observer':precommit_observer,'at_cut_observer':at_cut_observer,
                'before_B_ack':before_ack,'cold_observer':final,'capacity_invariant':len(expected)<=1}
    finally:
        for p in procs:
            if p.poll() is None:p.kill();p.wait(timeout=4)
            for f in [p.stdin,p.stdout,p.stderr]:f.close()

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    if len(sys.argv)>1 and sys.argv[1]=='--worker':worker(*sys.argv[2:]);return
    with tempfile.TemporaryDirectory(prefix='ases-round2-capacity-') as td:
        cases={n:case(Path(td),n) for n in ['kill_before_commit','kill_after_commit','detached_after_commit']}
    print(json.dumps({'schema':'ases.f1-capacity-cuts.v1','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'environment':{'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,
                                     'executable':sys.executable,'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                      'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':main()
