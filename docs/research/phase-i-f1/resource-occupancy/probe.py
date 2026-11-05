#!/usr/bin/env python3
"""Actual owned listener lifetime versus guarded SQLite capacity bookkeeping."""
import array
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import select
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
OWNED=[]
def emit(stage,**fields):print(json.dumps(dict(stage=stage,pid=os.getpid(),ns=time.monotonic_ns(),**fields),sort_keys=True),flush=True)
def identity(sock):
    stat=os.fstat(sock.fileno())
    return dict(device=stat.st_dev,inode=stat.st_ino,address=list(sock.getsockname()),accepting=sock.getsockopt(socket.SOL_SOCKET,socket.SO_ACCEPTCONN))
def db_open(path):
    db=sqlite3.connect(path,isolation_level=None,timeout=2);db.execute('PRAGMA synchronous=FULL');return db
def sql(db,trace,statement,args=()):
    start=time.monotonic_ns()
    try:result=db.execute(statement,args)
    except sqlite3.Error as error:
        trace.append(dict(sql=statement.split()[0],start_ns=start,end_ns=time.monotonic_ns(),in_transaction=db.in_transaction,
                          outcome='error',sqlite_errorcode=error.sqlite_errorcode,sqlite_errorname=error.sqlite_errorname))
        raise
    trace.append(dict(sql=statement.split()[0],start_ns=start,end_ns=time.monotonic_ns(),in_transaction=db.in_transaction,outcome='returned'))
    return result
def native(port):
    start=time.monotonic_ns();sock=socket.socket()
    try:
        sock.bind(('127.0.0.1',port));sock.listen(1)
        return sock,dict(start_ns=start,end_ns=time.monotonic_ns(),bound=True,identity=identity(sock))
    except OSError as error:
        sock.close()
        return None,dict(start_ns=start,end_ns=time.monotonic_ns(),bound=False,errno=error.errno,error=type(error).__name__)

def owner(config):
    sock,acquired=native(0)
    if sock is None:raise RuntimeError('owned ephemeral listener unavailable')
    db=db_open(config['db']);trace=[]
    sql(db,trace,'BEGIN IMMEDIATE');sql(db,trace,'INSERT INTO claims VALUES(?)',('A',));sql(db,trace,'COMMIT')
    emit('owner_ready',native=acquired,sql_trace=trace)
    for line in sys.stdin:
        op=json.loads(line)['op'];trace=[]
        if op=='release-ledger':
            sql(db,trace,'BEGIN IMMEDIATE');sql(db,trace,'DELETE FROM claims WHERE holder=?',('A',));sql(db,trace,'COMMIT')
            emit('ledger_released',native_identity=identity(sock),sql_trace=trace)
        elif op=='transfer':
            with socket.socket(fileno=config['transfer_fd']) as channel:
                channel.sendmsg([b'owned-listener'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[sock.fileno()]))])
            emit('descriptor_transferred',native_identity=identity(sock))
        elif op=='close-resource':
            prior=identity(sock);sock.close();sock=None;emit('resource_closed',prior_identity=prior)
        elif op=='quit':
            if sock is not None:sock.close()
            db.close();emit('owner_exit');return
        else:raise ValueError('unknown owned test command')

def keeper(fd):
    with socket.socket(fileno=fd) as channel:
        data,ancillary,flags,_=channel.recvmsg(64,socket.CMSG_SPACE(array.array('i').itemsize))
    assert data==b'owned-listener' and flags==0 and len(ancillary)==1
    assert ancillary[0][:2]==(socket.SOL_SOCKET,socket.SCM_RIGHTS)
    descriptors=array.array('i');descriptors.frombytes(ancillary[0][2]);assert len(descriptors)==1
    sock=socket.socket(fileno=descriptors[0]);prior=identity(sock)
    emit('keeper_ready',native_identity=prior)
    assert json.loads(sys.stdin.readline())['op']=='close'
    sock.close();emit('keeper_closed',prior_identity=prior)

def contender(config):
    db=db_open(config['db']);trace=[]
    if 'busy_timeout_ms' in config:db.execute('PRAGMA busy_timeout='+str(int(config['busy_timeout_ms'])))
    sql(db,trace,'BEGIN IMMEDIATE')
    count=db.execute('SELECT COUNT(*) FROM claims').fetchone()[0]
    if count>=1:
        sql(db,trace,'ROLLBACK');emit('denied',reason='ledger-capacity',sql_trace=trace);return
    if config['variant']=='ledger-only':
        sql(db,trace,'INSERT INTO claims VALUES(?)',('B',));sql(db,trace,'COMMIT')
        emit('claim_ack',ack_kind='ledger-only-before-native-acquisition',sql_trace=trace)
        sock,result=native(config['port']);emit('native_result',native=result)
        if sock is not None:sock.close()
        return
    sock,result=native(config['port'])
    if sock is None:
        sql(db,trace,'ROLLBACK');emit('denied',reason='native-resource-busy',native=result,sql_trace=trace);return
    sql(db,trace,'INSERT INTO claims VALUES(?)',('B',))
    if config.get('prepare_gate'):
        emit('native_prepared',native=result,sql_trace=trace,busy_timeout_ms=db.execute('PRAGMA busy_timeout').fetchone()[0])
        assert json.loads(sys.stdin.readline())['op']=='commit'
    try:sql(db,trace,'COMMIT')
    except sqlite3.Error as error:
        failure=dict(error=type(error).__name__,sqlite_errorcode=error.sqlite_errorcode,sqlite_errorname=error.sqlite_errorname,
                     in_transaction_before_cleanup=db.in_transaction,native_identity_before_cleanup=identity(sock))
        if db.in_transaction:sql(db,trace,'ROLLBACK')
        sock.close();closed_ns=time.monotonic_ns()
        emit('acquisition_commit_error',failure=failure,sql_trace=trace,native_closed_ns=closed_ns,success_ack=False)
        return
    emit('acquisition_ack',native=result,sql_trace=trace)
    assert json.loads(sys.stdin.readline())['op']=='close'
    sock.close();sql(db,trace,'BEGIN IMMEDIATE');sql(db,trace,'DELETE FROM claims WHERE holder=?',('B',));sql(db,trace,'COMMIT')
    emit('acquisition_closed',sql_trace=trace)

class Child:
    def __init__(self,role,argument,pass_fds=()):
        self.buffer=b'';self.meta=dict(role=role,start_ns=time.monotonic_ns())
        value=str(argument) if role=='--keeper' else json.dumps(argument)
        self.process=subprocess.Popen([sys.executable,__file__,role,value],pass_fds=pass_fds,
                                      stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        self.meta['pid']=self.process.pid;OWNED.append(self)
    def read(self):
        deadline=time.monotonic()+3
        while b'\n' not in self.buffer:
            remaining=deadline-time.monotonic()
            if remaining<=0 or not select.select([self.process.stdout],[],[],remaining)[0]:raise TimeoutError('owned child frame timeout')
            chunk=os.read(self.process.stdout.fileno(),4096)
            if not chunk:raise EOFError('owned child frame absent')
            self.buffer+=chunk
        line,self.buffer=self.buffer.split(b'\n',1)
        return dict(json.loads(line),parent_received_ns=time.monotonic_ns(),wire_utf8_hex=line.hex())
    def command(self,op):
        self.process.stdin.write((json.dumps(dict(op=op))+'\n').encode());self.process.stdin.flush();return self.read()
    def finish(self,kill=False):
        if 'exit' in self.meta:return self.meta
        if kill and self.process.poll() is None:self.process.kill()
        out,err=self.process.communicate(timeout=3)
        self.meta.update(exit=self.process.returncode,exit_ns=time.monotonic_ns(),remaining_stdout_hex=(self.buffer+out).hex(),stderr=err.decode())
        return self.meta

def ledger(path):
    with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True) as db:
        return dict(claims=[r[0] for r in db.execute('SELECT holder FROM claims ORDER BY holder')],integrity=db.execute('PRAGMA integrity_check').fetchone()[0])
def probe_bind(port):
    sock,result=native(port)
    if sock is not None:sock.close()
    return result
def b_attempt(path,port,variant):
    child=Child('--B',dict(db=str(path),port=port,variant=variant));first=child.read()
    if variant=='ledger-only':
        second=child.read();process=child.finish()
        return child,dict(first=first,second=second,process=process,ledger=ledger(path))
    if first['stage']=='denied':process=child.finish()
    else:process=None
    return child,dict(first=first,process=process,ledger=ledger(path))

def one(root,kind):
    root.mkdir();path=root/'ledger.sqlite'
    with db_open(path) as db:db.execute('CREATE TABLE claims(holder TEXT PRIMARY KEY)')
    transfer=socket.socketpair(type=socket.SOCK_SEQPACKET) if kind=='retained' else None
    config=dict(db=str(path))
    if transfer:config['transfer_fd']=transfer[0].fileno()
    a=Child('--A',config,(transfer[0].fileno(),) if transfer else ())
    if transfer:transfer[0].close()
    initial=a.read();port=initial['native']['identity']['address'][1]
    kept=None;handoff=None;k=None
    if transfer:
        k=Child('--keeper',transfer[1].fileno(),(transfer[1].fileno(),));transfer[1].close()
        handoff=a.command('transfer');kept=k.read()
    before_release=ledger(path);released=a.command('release-ledger');empty=ledger(path)
    unbacked=None;cleanup=None;busy=None;closed=None
    if kind=='live':
        _,unbacked=b_attempt(path,port,'ledger-only')
        with db_open(path) as db:
            trace=[];sql(db,trace,'BEGIN IMMEDIATE');sql(db,trace,'DELETE FROM claims WHERE holder=?',('B',));sql(db,trace,'COMMIT')
        cleanup=dict(sql_trace=trace,ledger=ledger(path))
        _,busy=b_attempt(path,port,'native-guarded')
        closed=a.command('close-resource')
    else:
        a_exit=a.finish(kill=True)
        if kind=='retained':
            _,busy=b_attempt(path,port,'native-guarded')
            closed=k.command('close');k_exit=k.finish()
    free_before=probe_bind(port)
    b,acquired=b_attempt(path,port,'native-guarded')
    occupied_probe=probe_bind(port)
    if kind=='live':a_quit=a.command('quit');a_exit=a.finish()
    else:a_quit=None
    acquired['process']=b.finish(kill=True)
    after_death=dict(ledger=ledger(path),native_probe=probe_bind(port))
    return dict(kind=kind,port=port,initial=initial,ledger_before_release=before_release,release_ack=released,ledger_after_release=empty,
                handoff=handoff,keeper_ready=kept,unbacked=unbacked,explicit_unbacked_cleanup=cleanup,
                busy=busy,close_ack=closed,free_before_acquisition=free_before,acquisition=acquired,
                occupied_probe=occupied_probe,A_exit=a_exit,A_quit=a_quit,keeper_exit=k_exit if k else None,
                after_B_termination=after_death)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    try:
        with tempfile.TemporaryDirectory(prefix='ases-resource-occupancy-') as directory:
            root=Path(directory);cases={kind:one(root/kind,kind) for kind in ('live','terminated','retained')}
            print(json.dumps(dict(schema='ases.native-resource-occupancy',version=1,
                                  execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                  environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
                                  executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                                  cases=cases,children=[c.meta for c in OWNED]),indent=2,sort_keys=True))
    finally:
        for child in OWNED:
            if child.process.poll() is None:child.finish(kill=True)

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--A':owner(json.loads(sys.argv[2]))
    elif len(sys.argv)==3 and sys.argv[1]=='--B':contender(json.loads(sys.argv[2]))
    elif len(sys.argv)==3 and sys.argv[1]=='--keeper':keeper(int(sys.argv[2]))
    else:main()
