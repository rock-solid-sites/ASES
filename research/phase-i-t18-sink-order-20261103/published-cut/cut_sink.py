#!/usr/bin/env python3
"""Selected exact-byte published-cut witness and ACK-coupled managed sink."""
import fcntl
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import socket
import sys
import threading
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('published_cut_managed',HERE.parent/'managed-revocation/managed_sink.py')
managed=importlib.util.module_from_spec(spec);spec.loader.exec_module(managed)
ORIGINAL_STATE=managed.State
FIELDS=('created','granted','active','authority_version','holder')
GENESIS=dict(authority=dict(created=False,granted=False,active=False,authority_version=0,holder='old'),
             journal_sha256=hashlib.sha256(b'').hexdigest())

def validate_cut(cut):
    if not isinstance(cut,dict) or set(cut)!= {'authority','journal_sha256'}:raise ValueError('invalid cut shape')
    authority=cut['authority']
    if (not isinstance(authority,dict) or set(authority)!=set(FIELDS)
            or any(type(authority[k]) is not bool for k in ('created','granted','active'))
            or type(authority['authority_version']) is not int or authority['authority_version']<0
            or not isinstance(authority['holder'],str)
            or not isinstance(cut['journal_sha256'],str) or re.fullmatch('[0-9a-f]{64}',cut['journal_sha256']) is None):
        raise ValueError('invalid typed cut fields')

def witness_server(root):
    lock=threading.Lock();state=dict(current=None,revision=0,reject_publish=False,drop_publish_reply_once=False,log=[])
    class Handler(managed.base.make_handler(None)):
        def do_GET(self):
            if self.path!='/status':self.send_json(404,dict(error='unknown route'));return
            with lock:self.send_json(200,dict(root=root,pid=os.getpid(),**state))
        def do_POST(self):
            data=self.read_json();start=time.monotonic_ns()
            with lock:
                status=200;suppress=False
                def envelope(**fields):return dict(root=root,pid=os.getpid(),nonce=data.get('nonce'),revision=state['revision'],current=state['current'],**fields)
                try:
                    if data.get('root')!=root or not isinstance(data.get('nonce'),str):raise ValueError('root/nonce missing')
                    if self.path=='/init':
                        validate_cut(data['cut'])
                        if state['current'] is not None:status,reply=409,envelope(initialized=False)
                        else:state['current']=data['cut'];state['revision']=1;reply=envelope(initialized=True)
                    elif self.path=='/check':
                        validate_cut(data['candidate']);reply=envelope(allowed=state['current']==data['candidate'])
                    elif self.path=='/publish':
                        validate_cut(data['previous']);validate_cut(data['candidate'])
                        if state['reject_publish']:status,reply=503,envelope(published=False,reason='injected-publication-rejection')
                        elif (type(data.get('expected_revision')) is not int or data['expected_revision']!=state['revision']
                              or data['previous']!=state['current']):status,reply=409,envelope(published=False,reason='stale-cas')
                        else:
                            state['current']=data['candidate'];state['revision']+=1;reply=envelope(published=True)
                            if state['drop_publish_reply_once']:
                                state['drop_publish_reply_once']=False;suppress=True
                    elif self.path=='/fault':
                        if type(data.get('reject_publish')) is not bool:raise ValueError('Boolean fault flag required')
                        if 'drop_publish_reply_once' in data:
                            if type(data['drop_publish_reply_once']) is not bool:raise ValueError('Boolean drop flag required')
                            state['drop_publish_reply_once']=data['drop_publish_reply_once']
                        state['reject_publish']=data['reject_publish'];reply=envelope(configured=True)
                    else:status,reply=404,envelope(error='unknown route')
                except (ValueError,KeyError,TypeError) as error:status,reply=400,envelope(error=str(error))
                state['log'].append(dict(path=self.path,request=data,response=reply,status=status,reply_suppressed=suppress,
                                        start_ns=start,end_ns=time.monotonic_ns()))
            if suppress:
                self.close_connection=True
                try:self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:pass
                self.connection.close();return
            self.send_json(status,reply)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
    print(json.dumps(dict(ready=True,port=server.server_address[1],pid=os.getpid())),flush=True)
    server.serve_forever(poll_interval=.05)

class StartupMismatch(ValueError):
    def __init__(self,cut,observation):
        super().__init__('published-cut-unavailable');self.cut=cut;self.observation=observation

def serve_sink(journal,recover,port,root):
    journal.parent.mkdir(parents=True,exist_ok=True)
    guard_path=journal.parent/'sink-writer.lock';fd=os.open(guard_path,os.O_RDWR|os.O_CREAT,0o600)
    stat=os.fstat(fd);guard=dict(path=str(guard_path),device=stat.st_dev,inode=stat.st_ino)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps(dict(ready=False,reason='writer-guard-busy',guard=guard)),flush=True);return 75
        class State(ORIGINAL_STATE):
            def __init__(self,*args,**kwargs):
                self.cut_protocol_log=[]
                super().__init__(*args,**kwargs)
                current=self.cut();proof=self.check_cut(current)
                if not proof['valid']:raise StartupMismatch(current,proof)
            def cut(self):
                raw=self.journal.read_bytes() if self.journal.exists() else b''
                return dict(authority={key:getattr(self,'version' if key=='authority_version' else key) for key in FIELDS},
                            journal_sha256=hashlib.sha256(raw).hexdigest())
            def exchange(self,path,**fields):
                request=dict(root=root,nonce=secrets.token_hex(16),**fields)
                event=dict(path=path,request=request,start_ns=time.monotonic_ns())
                try:
                    code,reply=managed.base.call(port,'POST',path,request)
                    transport_valid=(code==200 and reply.get('root')==root and reply.get('nonce')==request['nonce']
                                     and type(reply.get('revision')) is int)
                    event.update(response=reply,status=code,transport_valid=transport_valid)
                except Exception as error:event.update(response=None,status=None,transport_valid=False,error=type(error).__name__)
                event['end_ns']=time.monotonic_ns();self.cut_protocol_log.append(event);return event
            def check_cut(self,current):
                proof=self.exchange('/check',candidate=current);reply=proof['response']
                proof['valid']=bool(proof['transport_valid'] and reply.get('allowed') is True and reply.get('current')==current)
                return proof
            def apply(self,path,data):
                before=self.cut();proof=self.check_cut(before)
                if not proof['valid']:return 503,dict(outcome='published-cut-unavailable',local_control_committed=False)
                status,reply=super().apply(path,data)
                after=self.cut()
                if after==before:return status,reply
                publication=self.exchange('/publish',previous=before,candidate=after,expected_revision=proof['response']['revision'])
                received=publication['response']
                valid=bool(publication['transport_valid'] and received.get('published') is True and received.get('current')==after
                           and received['revision']==proof['response']['revision']+1)
                publication['valid']=valid
                if not valid:return 503,dict(outcome='cut-publication-unknown',local_control_committed=True,local_event_seq=reply.get('event_seq'))
                return status,dict(reply,published_revision=received['revision'],published_journal_sha256=after['journal_sha256'])
            def snapshot(self):
                return dict(super().snapshot(),actual_cut=self.cut(),cut_protocol_log=list(self.cut_protocol_log),writer_guard=guard)
        managed.State=State
        try:managed.serve(journal,recover)
        except StartupMismatch as error:
            print(json.dumps(dict(ready=False,reason=str(error),local_parse_complete=True,local_cut=error.cut,witness_observation=error.observation,guard=guard)),flush=True);return 1
        except (ValueError,OSError) as error:
            print(json.dumps(dict(ready=False,reason=str(error),error=type(error).__name__,guard=guard)),flush=True);return 1
    finally:os.close(fd)
    return 0

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--witness':witness_server(sys.argv[2])
    elif len(sys.argv)==7 and sys.argv[1]=='--sink' and sys.argv[2] in ('fresh','recover') and sys.argv[5]=='published-cut':
        raise SystemExit(serve_sink(Path(sys.argv[3]),sys.argv[2]=='recover',int(sys.argv[4]),sys.argv[6]))
    else:raise SystemExit('usage: --witness ROOT | --sink MODE JOURNAL PORT published-cut ROOT')
