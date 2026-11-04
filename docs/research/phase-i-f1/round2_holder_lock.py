#!/usr/bin/env python3
"""Candidate flock guard around the unchanged real holder, with reference controls."""
import array
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import select
import signal
import socket
import subprocess
import sys
import tempfile
import time
import sqlite_full_holder_recovery as inherited

HERE=Path(__file__).resolve().parent

def emit(**kw):print(json.dumps({'pid':os.getpid(),'ns':time.monotonic_ns(),**kw}),flush=True)
def ident(fd):
    s=os.fstat(fd);return {'device':s.st_dev,'inode':s.st_ino}
def locked_service(config):
    fd=os.open(config['guard_path'],os.O_RDWR|os.O_CREAT,0o600)
    identity=ident(fd)
    try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError as exc:
        emit(result='blocked',identity=identity,errno=exc.errno);os.close(fd);return 75
    emit(result='guard_acquired',identity=identity)
    if config.get('transfer_fd') is not None:
        with socket.socket(fileno=config['transfer_fd']) as s:
            s.sendmsg([b'lock'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]))])
    try:inherited.service.serve(config)
    finally:os.close(fd)
    return 0

def keeper(sockfd):
    with socket.socket(fileno=sockfd) as s:
        data,anc,flags,_=s.recvmsg(32,socket.CMSG_SPACE(array.array('i').itemsize))
    assert data==b'lock' and flags==0 and len(anc)==1
    assert anc[0][:2]==(socket.SOL_SOCKET,socket.SCM_RIGHTS)
    fds=array.array('i');fds.frombytes(anc[0][2]);assert len(fds)==1
    fd=fds[0];emit(result='retained_descriptor',identity=ident(fd))
    assert sys.stdin.buffer.readline()==b'close\n'
    os.close(fd);emit(result='descriptor_closed');return 0

def readline(p):
    assert select.select([p.stdout],[],[],4)[0], 'startup/readiness timeout'
    return p.stdout.readline()

class Holder:
    def __init__(self,root,transfer=None,context=0):
        self.client,server=socket.socketpair();self.client.settimeout(4)
        conf={'path':str(root/'store.sqlite'),'root':'work','profile':'independent',
              'channels':[[context,server.fileno()]],'guard_path':str(root/'holder.lock')}
        fds=[server.fileno()]
        if transfer is not None:conf['transfer_fd']=transfer.fileno();fds.append(transfer.fileno())
        self.p=subprocess.Popen([sys.executable,__file__,json.dumps(conf)],pass_fds=fds,
                                stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        server.close();self.guard=json.loads(readline(self.p))
        self.blocked=self.guard['result']=='blocked'
        if self.blocked:
            out,err=self.p.communicate(timeout=4);self.client.close()
            assert self.p.returncode==75 and not out and not err
            self.blocked_exit={'exit':self.p.returncode,'stdout':out.decode(),'stderr':err.decode()}
        else:assert readline(self.p)==b'ready\n'
    def call(self,q):
        self.client.sendall(inherited.check.packet(q));return inherited.check.receive(self.client)
    def accept(self,value):return self.call(inherited.check.wire(inherited.model.Request('accept',0,value=value)))
    def close(self):
        if self.p.poll() is None:self.p.kill()
        out,err=self.p.communicate(timeout=4);self.client.close()
        return {'pid':self.p.pid,'exit':self.p.returncode,'stdout':out.decode(),'stderr':err.decode()}

def setup(root):
    root.mkdir();inherited.service.initialize(str(root/'store.sqlite'),'work','independent')
    bootstrap=Holder(root,context=-1)
    try:
        for q in [inherited.model.Request('establish'),inherited.model.Request('grant',target=0,value=7)]:
            assert bootstrap.call(inherited.check.wire(q))['outcome']=='commit'
    finally:bootstrap.close()
def acquire(root,owned,transfer=None):
    h=Holder(root,transfer);owned.append(h);return h

def wait_stopped(p):
    deadline=time.monotonic()+4
    while time.monotonic()<deadline:
        pid,status=os.waitpid(p.pid,os.WUNTRACED|os.WNOHANG)
        if pid:
            assert os.WIFSTOPPED(status) and os.WSTOPSIG(status)==signal.SIGSTOP
            return {'pid':pid,'wait_status':status,'stop_signal':os.WSTOPSIG(status)}
        time.sleep(.01)
    raise TimeoutError('SIGSTOP not observed')

def case(root,mode):
    setup(root);owned=[];retainer=None
    try:
        if mode=='retained_descriptor':
            send,recv=socket.socketpair(type=socket.SOCK_SEQPACKET)
            retainer=subprocess.Popen([sys.executable,__file__,'--keeper',str(recv.fileno())],pass_fds=[recv.fileno()],
                                      stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
            recv.close()
            try:a=acquire(root,owned,send)
            finally:send.close()
            kept=json.loads(readline(retainer));assert kept['identity']==a.guard['identity']
        else:a=acquire(root,owned)
        assert not a.blocked
        first=a.accept(1);assert first['outcome']=='commit'
        before=inherited.independent(root/'store.sqlite');assert before['view']==first['state']
        if mode=='ordinary':
            b=acquire(root,owned);assert b.blocked
            os.kill(a.p.pid,signal.SIGSTOP);stop=wait_stopped(a.p)
            paused=acquire(root,owned);assert paused.blocked
            os.kill(a.p.pid,signal.SIGCONT)
            alive_read=a.call({'kind':'read'});assert alive_read['state']==first['state']
            a_exit=a.close()
            takeover=acquire(root,owned);assert not takeover.blocked
            recovered=takeover.call({'kind':'read'});assert recovered['state']==first['state']
            second=takeover.accept(0);assert second['outcome']=='commit'
            return {'first_ack':first,'A_guard':a.guard,'B_refusal':b.guard,'B_exit':b.blocked_exit,
                    'stopped':stop,'stopped_refusal':paused.guard,'resumed_read':alive_read,'A_exit':a_exit,
                    'takeover_guard':takeover.guard,'takeover_recovery':recovered,'second_ack':second,
                    'takeover_exit':takeover.close(),'cold':inherited.independent(root/'store.sqlite')}
        if mode=='retained_descriptor':
            a_exit=a.close();b=acquire(root,owned);assert b.blocked
            assert retainer.poll() is None
            retainer.stdin.write(b'close\n');retainer.stdin.flush()
            out,err=retainer.communicate(timeout=4);assert retainer.returncode==0 and not err
            takeover=acquire(root,owned);assert not takeover.blocked
            recovered=takeover.call({'kind':'read'});assert recovered['state']==first['state']
            return {'first_ack':first,'A_guard':a.guard,'keeper':kept,'A_exit':a_exit,'B_refusal_after_reap':b.guard,
                    'B_exit':b.blocked_exit,'keeper_exit':retainer.returncode,'keeper_stdout':out.decode(),
                    'takeover_guard':takeover.guard,'takeover_recovery':recovered,'takeover_exit':takeover.close()}
        assert mode=='replaced_lock_object'
        old_identity=a.guard['identity'];(root/'holder.lock').unlink()
        b=acquire(root,owned);assert not b.blocked and b.guard['identity']!=old_identity
        first_again=a.accept(0);second=b.accept(1)
        assert first_again['outcome']==second['outcome']=='commit'
        assert a.p.poll() is None and b.p.poll() is None
        return {'initial_ack':first,'A_guard':a.guard,'B_guard':b.guard,'both_alive_at_ACK':True,
                'A_ack_after_B_activation':first_again,'B_ack':second,'A_exit':a.close(),'B_exit':b.close(),
                'cold':inherited.independent(root/'store.sqlite'),
                'interpretation':'different inode locks allow two eligible real services; stable protected lock identity required'}
    finally:
        for h in owned:h.close()
        if retainer and retainer.poll() is None:
            retainer.kill();retainer.communicate(timeout=4)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    if len(sys.argv)>1:
        return keeper(int(sys.argv[2])) if sys.argv[1]=='--keeper' else locked_service(json.loads(sys.argv[1]))
    with tempfile.TemporaryDirectory(prefix='ases-round2-holderlock-') as td:
        cases={n:case(Path(td)/n,n) for n in ['ordinary','retained_descriptor','replaced_lock_object']}
        assert sum(p.stat().st_size for p in Path(td).rglob('*') if p.is_file())<1_048_576
    print(json.dumps({'schema':'ases.f1-holder-lock.v1','execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'base_semantics':'HEAD at invocation; exact source bytes separately hashed',
                      'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),inherited.KERNEL/'kernel0_recovery_service.py',inherited.KERNEL/'kernel0_recovery_check.py']},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':raise SystemExit(main())
