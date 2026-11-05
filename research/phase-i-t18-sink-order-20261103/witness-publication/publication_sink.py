#!/usr/bin/env python3
"""Selected revoke publication-before-success barrier; no startup auto-publication."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys
import threading
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('publication_witness',HERE.parent/'sink-witness/witness_sink.py')
witness=importlib.util.module_from_spec(spec);spec.loader.exec_module(witness)

def serve(journal,recover,port,root,stage=None,gate_path=None):
    original=witness.managed.State
    class Published(original):
        def __init__(self,*args,**kwargs):
            self.publication_log=[]
            super().__init__(*args,**kwargs)
        def apply(self,path,data):
            def gate(point):
                if stage!=point:
                    return
                evidence=dict(point=point,pid=os.getpid(),monotonic_ns=time.monotonic_ns(),
                              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              local_state={key:getattr(self,'version' if key=='authority_version' else key) for key in witness.FIELDS})
                Path(gate_path).write_text(json.dumps(evidence,sort_keys=True))
                threading.Event().wait(30)
                raise RuntimeError('test gate timed out without owned-process termination')
            if path=='/revoke':
                gate('before_local')
            status,reply=super().apply(path,data)
            if path!='/revoke' or status!=200:
                return status,reply
            gate('local_committed')
            candidate={key:getattr(self,'version' if key=='authority_version' else key) for key in witness.FIELDS}
            query=dict(state=candidate,nonce=secrets.token_hex(16))
            event=dict(start_ns=time.monotonic_ns(),request=query,local_event_seq=reply['event_seq'])
            try:
                code,response=witness.managed.base.call(port,'POST','/publish',query)
                valid=(code==200 and response.get('outcome')=='published' and response.get('nonce')==query['nonce']
                       and response.get('root')==root and response.get('state')==candidate)
                event.update(response=response,response_status=code,valid=valid)
            except Exception as error:
                valid=False;event.update(response=None,valid=False,error=type(error).__name__)
            event['end_ns']=time.monotonic_ns();self.publication_log.append(event)
            if not valid:
                return 503,dict(outcome='management-publication-unknown',local_control_committed=True,
                                local_event_seq=reply['event_seq'],authority_version=self.version)
            gate('witness_published')
            return status,dict(reply,witness_publication=response)
        def snapshot(self):
            return dict(super().snapshot(),publication_log=list(self.publication_log))
    witness.managed.State=Published
    witness.guarded_server(journal,recover,port,'eligibility',root)

if __name__=='__main__':
    if len(sys.argv) not in (7,9) or sys.argv[1]!='--sink' or sys.argv[2] not in ('fresh','recover') or sys.argv[5]!='eligibility':
        raise SystemExit('usage: --sink MODE JOURNAL WITNESS_PORT eligibility ROOT [GATE_STAGE GATE_FILE]')
    stage,gate_path=(sys.argv[7],sys.argv[8]) if len(sys.argv)==9 else (None,None)
    if stage not in (None,'before_local','local_committed','witness_published'):
        raise SystemExit('unsupported test gate')
    serve(Path(sys.argv[3]),sys.argv[2]=='recover',int(sys.argv[4]),sys.argv[6],stage,gate_path)
