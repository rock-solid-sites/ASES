#!/usr/bin/env python3
"""Trusted-local experimental witness and actual managed sink guard wrapper."""
import http.server
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('witness_managed', HERE.parent/'managed-revocation/managed_sink.py')
managed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(managed)
FIELDS = ('created', 'granted', 'active', 'authority_version', 'holder')

def projection(state, profile):
    return {key: state[key] for key in (('authority_version',) if profile == 'generation' else FIELDS)}

def witness_server(root):
    lock = threading.Lock()
    state = dict(current=None, publication=0, wrong_nonce=False, log=[])
    class Handler(managed.base.make_handler(None)):
        def do_GET(self):
            if self.path != '/status':
                self.send_json(404,dict(error='unknown route')); return
            with lock:
                self.send_json(200,dict(root=root,pid=os.getpid(),**state))

        def do_POST(self):
            data = self.read_json()
            start = time.monotonic_ns()
            with lock:
                if self.path == '/publish':
                    # Trusted supervisor; monotonic freshness is an external premise.
                    state['current'] = {key:data['state'][key] for key in FIELDS}
                    state['publication'] += 1
                    reply = dict(outcome='published',publication=state['publication'])
                elif self.path == '/fault':
                    state['wrong_nonce'] = bool(data['wrong_nonce'])
                    reply = dict(outcome='configured')
                elif self.path == '/check':
                    profile = data['profile']
                    allowed = (profile in ('generation','eligibility') and data['root']==root
                               and state['current'] is not None
                               and projection(data['candidate'],profile)==projection(state['current'],profile))
                    reply = dict(allowed=allowed,nonce='wrong-nonce' if state['wrong_nonce'] else data['nonce'],
                                 root=root,profile=profile,pid=os.getpid(),current=state['current'],
                                 publication=state['publication'])
                else:
                    self.send_json(404,dict(error='unknown route')); return
                state['log'].append(dict(path=self.path,request=data,response=reply,
                                         start_ns=start,end_ns=time.monotonic_ns()))
            self.send_json(200,reply)
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    server.daemon_threads = True
    print(json.dumps(dict(ready=True,port=server.server_address[1],pid=os.getpid())),flush=True)
    server.serve_forever(poll_interval=0.05)

def guarded_server(journal, recover, port, profile, root):
    original = managed.State
    class Guarded(original):
        def __init__(self, *args, **kwargs):
            self.witness_log=[]
            super().__init__(*args,**kwargs)
        def eligible(self,token):
            if not super().eligible(token):
                return False
            query=dict(root=root,profile=profile,candidate={key:getattr(self,'version' if key=='authority_version' else key) for key in FIELDS},
                       nonce=secrets.token_hex(16))
            event=dict(request=query,start_ns=time.monotonic_ns())
            try:
                code, reply = managed.base.call(port,'POST','/check',query)
                valid = (code==200 and reply.get('nonce')==query['nonce'] and reply.get('root')==root
                         and reply.get('profile')==profile and type(reply.get('allowed')) is bool)
                event.update(response=reply,response_status=code,valid=valid)
                admitted=valid and reply['allowed']
            except Exception as error:
                event.update(response=None,valid=False,error=type(error).__name__)
                admitted=False
            event.update(end_ns=time.monotonic_ns(),admitted=admitted)
            self.witness_log.append(event)
            return admitted
        def snapshot(self):
            return dict(super().snapshot(),witness_log=list(self.witness_log),witness_profile=profile,witness_root=root)
    managed.State=Guarded
    managed.serve(journal,recover)

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--witness':
        witness_server(sys.argv[2])
    elif len(sys.argv)==7 and sys.argv[1]=='--sink':
        _,_,mode,journal,port,profile,root=sys.argv
        if mode not in ('fresh','recover') or profile not in ('generation','eligibility'):
            raise SystemExit('unsupported selected profile')
        guarded_server(Path(journal),mode=='recover',int(port),profile,root)
    else:
        raise SystemExit('usage: --witness ROOT | --sink {fresh,recover} JOURNAL WITNESS_PORT PROFILE ROOT')
