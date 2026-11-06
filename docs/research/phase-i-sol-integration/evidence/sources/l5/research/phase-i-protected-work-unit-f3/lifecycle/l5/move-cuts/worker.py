#!/usr/bin/env python3
"""Original L5 publication gates and root-only current-record observation."""
import hashlib
import json
import os
from pathlib import Path
import resource
import socket
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import l5_integrated as l5
ORIGINAL_REPLACE=os.replace
def digest(raw):return hashlib.sha256(raw).hexdigest()
def emit(value):print(json.dumps(value,sort_keys=True),flush=True)
def observe(root):
    name,st=l5.load_current(root)
    if not l5.graph_valid(st):raise ValueError('invalid current graph')
    files={}
    for path in sorted((root/'protected').rglob('*')):
        if path.is_file():
            raw=path.read_bytes();files[str(path.relative_to(root/'protected'))]=dict(raw_hex=raw.hex(),sha256=digest(raw))
    contents=[]
    for meta in st['work_units']['C']['accepted_contents']:
        raw=l5.verified_content(root,meta);contents.append(dict(metadata=meta,raw_hex=raw.hex(),sha256=digest(raw)))
    effect=root/'effects/D.bin'
    return dict(ns=time.monotonic_ns(),selected=name,state=st,files=files,contents=contents,
                permissions={key:sorted(l5.permissions(st,key)) for key in ('C','D')},
                enabled_D=l5.enabled(st,'D','W-L5'),effect_raw_hex=effect.read_bytes().hex() if effect.exists() else None)
def manage(root,op):
    _,st=l5.load_current(root);client,server=socket.socketpair()
    req=dict(op=op,authorized_by='initial-manager',credential=l5.CREDENTIAL)
    if op=='authorize_move':req.update(child='C',destination='Q')
    try:
        _,reply=l5.manager_roundtrip(client,server,req,st,root)
        raw=client.makefile('rb',buffering=0).readline();assert json.loads(raw)==reply
        return dict(request=req,reply=reply,manager_wire_hex=raw.hex())
    finally:client.close();server.close()
def gate(root,phase,src=None,dst=None):
    emit(dict(event='GATE',pid=os.getpid(),ns=time.monotonic_ns(),phase=phase,src=str(src),dst=str(dst),snapshot=observe(root)))
    if sys.stdin.readline().strip()!='continue':raise RuntimeError('gate not continued')
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2);root=Path(sys.argv[1]);phase=sys.argv[2]
    emit(dict(event='READY',pid=os.getpid(),ns=time.monotonic_ns(),source_sha256=digest(Path(__file__).read_bytes()),
              l5_source_sha256=digest(Path(l5.__file__).read_bytes()),snapshot=observe(root)))
    for line in sys.stdin:
        req=json.loads(line);op=req['op']
        if op=='stop':break
        begin=time.monotonic_ns()
        if op=='move':
            def replace(src,dst):
                dst=Path(dst);record=dst.name.startswith('record-') and dst.suffix=='.json'
                if record and phase=='before_record':gate(root,phase,src,dst)
                ORIGINAL_REPLACE(src,dst)
                if record and phase=='after_record':gate(root,phase,src,dst)
                if dst.name=='CURRENT' and phase=='after_selector':gate(root,phase,src,dst)
            l5.os.replace=replace
            try:result=manage(root,'authorize_move')
            finally:l5.os.replace=ORIGINAL_REPLACE
        elif op=='split_mutant':
            _,st=l5.load_current(root);st['work_units']['C']['parent']='Q'
            l5.commit(root,st,dict(op='mutant-parent-only-publication'))
            gate(root,'mutant-half-selected')
            for key in ('C','D'):st['work_units'][key]['latent_ceiling']=['read']
            l5.commit(root,st,dict(op='mutant-late-ceilings'));result=dict(reply=dict(result='COMMITTED'),mutation=True)
        elif op=='activate':result=manage(root,'authorize_activate')
        elif op=='write':
            _,st=l5.load_current(root);allowed=l5.enabled(st,'D','W-L5') and 'write' in l5.permissions(st,'D')
            if allowed:
                target=root/'effects';target.mkdir(exist_ok=True);(target/'D.bin').write_bytes(req['payload'].encode())
            result=dict(reply=dict(result='COMMITTED' if allowed else 'DENY',allowed=allowed))
        else:raise ValueError('unsupported selected operation')
        emit(dict(event='RESPONSE',pid=os.getpid(),start_ns=begin,end_ns=time.monotonic_ns(),request=req,result=result,snapshot=observe(root)))
if __name__=='__main__':main()
