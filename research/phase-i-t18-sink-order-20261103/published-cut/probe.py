#!/usr/bin/env python3
"""Actual published-cut ACKs, rollback/meaning controls and publication divergence."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import secrets
import select
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent;SOURCE=HERE/'cut_sink.py';ROOT='selected-root-A'
spec=importlib.util.spec_from_file_location('published_probe_support',HERE.parent/'sink-witness/probe.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
spec=importlib.util.spec_from_file_location('published_cut_source',SOURCE)
cut=importlib.util.module_from_spec(spec);spec.loader.exec_module(cut)

def wcall(w,path,**fields):
    body=dict(root=ROOT,nonce=secrets.token_hex(16),**fields);start=time.monotonic_ns()
    code,reply=s.wrapper.managed.base.call(w.port,'POST',path,body)
    return dict(path=path,request=body,start_ns=start,end_ns=time.monotonic_ns(),status=code,response=reply)
def wstatus(w):return s.wrapper.managed.base.call(w.port,'GET','/status')[1]
def fault_write(journal,raw):
    before=s.local_probe.snapshot(journal);start=time.monotonic_ns()
    with journal.open('wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return dict(start_ns=start,end_ns=time.monotonic_ns(),before=before,after=s.local_probe.snapshot(journal))
def attempt(root,w):
    journal=root/'sink-effects.jsonl';start=time.monotonic_ns()
    p=subprocess.Popen([sys.executable,str(SOURCE),'--sink','recover',str(journal),str(w.port),'published-cut',ROOT],
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
    readable=select.select([p.stdout],[],[],3)[0];line=p.stdout.readline() if readable else b''
    frame=json.loads(line) if line else None
    if not readable or frame is not None and frame.get('ready') is True:p.kill()
    out,err=p.communicate(timeout=3)
    return dict(start_ns=start,exit_ns=time.monotonic_ns(),pid=p.pid,exit=p.returncode,frame=frame,
                startup_raw_hex=line.hex(),remaining_stdout_hex=out.hex(),stderr=err.decode(),journal_after=s.local_probe.snapshot(journal))

def one(root,kind):
    w=s.Child([sys.executable,str(SOURCE),'--witness',ROOT]);module=s.facade(w,'published-cut');state=root/'state';journal=state/'sink-effects.jsonl'
    children=[];extra={}
    try:
        init=wcall(w,'/init',cut=cut.GENESIS)
        writer=s.history.Session(module,SOURCE,state)
        try:
            s.history.bootstrap(writer);prefix=s.local_probe.snapshot(journal)
            writer.submit('cut-x',1,'persisted cut x / μ')
            writer.post('cut-q','/commit-obligation',dict(authority_version=1,obligation_id='q',payload='owed cut q / μ'))
            acknowledged=s.local_probe.snapshot(journal);after_ack=s.observed(writer.sink);w_after_ack=wstatus(w)
            if kind=='publication_rejected':
                extra['fault_configuration']=wcall(w,'/fault',reject_publish=True)
                writer.submit('local-unACKed-z',1,'locally committed without publication / μ')
                extra['after_local_commit']=s.local_probe.snapshot(journal)
                writer.submit('blocked-later',1,'must not append after divergence')
                extra['after_later']=s.local_probe.snapshot(journal)
            if kind=='positive':extra['stale_cas']=wcall(w,'/publish',previous=cut.GENESIS,candidate=cut.GENESIS,expected_revision=1)
        finally:original=writer.close();children.append(original)
        if kind=='positive':
            recovered=s.history.Session(module,SOURCE,state,True)
            try:recovered.submit('cut-y',1,'new after published-cut recovery / μ')
            finally:extra['recovered']=recovered.close();children.append(extra['recovered'])
            extra['cold']=s.history.Session(module,SOURCE,state,True).close();children.append(extra['cold'])
        else:
            if kind=='rollback':extra['controlled_fault']=fault_write(journal,bytes.fromhex(prefix['raw_hex']))
            if kind=='forged_same_sequence':
                rows=[json.loads(line) for line in bytes.fromhex(acknowledged['raw_hex']).splitlines()]
                effect=next(row for row in rows if row['event']=='effect_accepted')
                effect['payload']='persisted cut z / μ';effect['payload_sha256']=hashlib.sha256(effect['payload'].encode()).hexdigest()
                raw=b''.join(json.dumps(row,sort_keys=True).encode()+b'\n' for row in rows)
                extra['controlled_fault']=fault_write(journal,raw)
            extra['original_parser_control']=cut.ORIGINAL_STATE(journal,True).snapshot()
            extra['before_refusal']=s.local_probe.snapshot(journal)
            extra['startup_refusal']=attempt(state,w);children.append(extra['startup_refusal'])
        final_witness=wstatus(w);alive=w.process.poll() is None
    finally:witness_process=w.close();children.append(witness_process)
    return dict(kind=kind,init=init,original=original,prefix=prefix,acknowledged_journal=acknowledged,after_ack_status=after_ack,
                witness_after_ack=w_after_ack,witness_status=final_witness,witness_alive=alive,witness=witness_process,children=children,**extra)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-published-cut-') as directory:
        root=Path(directory);cases={kind:one(root/kind,kind) for kind in ('positive','rollback','forged_same_sequence','publication_rejected')}
        files=[SOURCE,HERE/'probe.py',HERE.parent/'sink-witness/probe.py',HERE.parent/'managed-revocation/managed_sink.py',
               HERE.parent/'managed-revocation/replay_probe.py',HERE.parent/'managed-revocation/probe.py',HERE.parent/'run.py']
        print(json.dumps(dict(schema='ases.published-cut-witness',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),cases=cases),indent=2,sort_keys=True))
if __name__=='__main__':main()
