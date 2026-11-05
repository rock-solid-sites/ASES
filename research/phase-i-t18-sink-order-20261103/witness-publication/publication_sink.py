#!/usr/bin/env python3
"""Selected revoke publication-before-success barrier; no startup auto-publication."""
import importlib.util
from pathlib import Path
import secrets
import sys
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('publication_witness',HERE.parent/'sink-witness/witness_sink.py')
witness=importlib.util.module_from_spec(spec);spec.loader.exec_module(witness)

def serve(journal,recover,port,root):
    original=witness.managed.State
    class Published(original):
        def __init__(self,*args,**kwargs):
            self.publication_log=[]
            super().__init__(*args,**kwargs)
        def apply(self,path,data):
            status,reply=super().apply(path,data)
            if path!='/revoke' or status!=200:
                return status,reply
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
            return status,dict(reply,witness_publication=response)
        def snapshot(self):
            return dict(super().snapshot(),publication_log=list(self.publication_log))
    witness.managed.State=Published
    witness.guarded_server(journal,recover,port,'eligibility',root)

if __name__=='__main__':
    if len(sys.argv)!=7 or sys.argv[1]!='--sink' or sys.argv[2] not in ('fresh','recover') or sys.argv[5]!='eligibility':
        raise SystemExit('usage: --sink MODE JOURNAL WITNESS_PORT eligibility ROOT')
    serve(Path(sys.argv[3]),sys.argv[2]=='recover',int(sys.argv[4]),sys.argv[6])
