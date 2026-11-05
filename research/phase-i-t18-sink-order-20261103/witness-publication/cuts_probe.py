#!/usr/bin/env python3
"""Actual no-reply/process-cut evidence; recovery never receives gate observations."""
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cuts_publication_support',HERE/'probe.py')
publication=importlib.util.module_from_spec(spec);spec.loader.exec_module(publication)
support=publication.support;SOURCE=publication.SOURCE

def no_reply(port):
    observation=dict(start_ns=time.monotonic_ns(),request=dict(path='/revoke',body={}))
    try:
        code,reply=support.wrapper.managed.base.call(port,'POST','/revoke',{})
        observation['response']=dict(status=code,body=reply)
    except Exception as error:
        observation.update(response=None,error=type(error).__name__)
    observation['end_ns']=time.monotonic_ns()
    return observation

def one(root,stage):
    witness=support.Child([sys.executable,str(support.SOURCE),'--witness','selected-root-A'])
    base_module=support.facade(witness,'eligibility');state=root/'state';gate_path=root/'gate.json'
    def start(source,where,recover=False):
        if recover:return support.Sink(source,where,True,witness,'eligibility')
        where.mkdir(parents=True,exist_ok=True)
        sink=support.Sink.__new__(support.Sink);sink.journal=where/'sink-effects.jsonl'
        support.Child.__init__(sink,[sys.executable,str(source),'--sink','fresh',str(sink.journal),str(witness.port),
                                    'eligibility','selected-root-A',stage,str(gate_path)])
        return sink
    module=SimpleNamespace(base=base_module.base,RunningSink=start)
    try:
        writer=support.history.Session(module,SOURCE,state)
        support.history.bootstrap(writer)
        initial=support.call(witness,'/publish',dict(state=support.observed(writer.sink)))
        writer.submit('ack-before-cut',1,'retained-before-cut')
        prefix=support.local_probe.snapshot(writer.sink.journal)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future=executor.submit(no_reply,writer.sink.port)
            deadline=time.monotonic()+1.5;gate=None
            while time.monotonic()<deadline:
                try:gate=json.loads(gate_path.read_bytes())
                except (FileNotFoundError,ValueError):time.sleep(.005);continue
                break
            if gate is None:
                writer.sink.process.kill();writer.sink.process.wait(timeout=2)
                raise RuntimeError('required gate not observed')
            at_gate=support.local_probe.snapshot(writer.sink.journal)
            remote_at_gate=publication.witness_status(witness)
            writer.sink.process.kill();exit_code=writer.sink.process.wait(timeout=2)
            exit_ns=time.monotonic_ns();request=future.result(timeout=3)
        writer.data.update(exit=exit_code,exit_ns=exit_ns,stderr=writer.sink.process.stderr.read())
        writer.sink.process.stdout.close();writer.sink.process.stderr.close()
        recovered=support.history.Session(base_module,SOURCE,state,True)
        try:recovered.submit('after-cut-current',1,'post-cut-probe')
        finally:recovery=recovered.close()
        cold=support.history.Session(base_module,SOURCE,state,True).close()
        final_witness=publication.witness_status(witness)
    finally:
        if 'writer' in locals() and writer.sink.process.poll() is None:
            writer.sink.process.kill();writer.sink.process.wait(timeout=2)
        witness_exit=witness.close()
    return dict(stage=stage,writer=writer.data,initial_publication=initial,actual_before_journal=prefix,
                request=request,gate=gate,gate_raw_hex=gate_path.read_bytes().hex(),journal_at_gate=at_gate,
                witness_at_gate=remote_at_gate,recovery=recovery,cold=cold,witness_status=final_witness,witness=witness_exit)

def control(root):
    witness=support.Child([sys.executable,str(support.SOURCE),'--witness','selected-root-A'])
    module=support.facade(witness,'eligibility');writer=support.history.Session(module,SOURCE,root/'state')
    try:
        support.history.bootstrap(writer)
        initial=support.call(witness,'/publish',dict(state=support.observed(writer.sink)))
        writer.post('revoke','/revoke',{})
        remote=publication.witness_status(witness)
    finally:data=writer.close();wit=witness.close()
    return dict(writer=data,initial_publication=initial,witness_status=remote,witness=wit)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-publication-cuts-') as directory:
        root=Path(directory)
        cases={stage:one(root/stage,stage) for stage in ('before_local','local_committed','witness_published')}
        positive=control(root/'positive')
        files=[SOURCE,HERE/'cuts_probe.py',HERE/'probe.py',HERE.parent/'sink-witness/witness_sink.py',
               HERE.parent/'sink-witness/probe.py',HERE.parent/'managed-revocation/managed_sink.py',
               HERE.parent/'managed-revocation/replay_probe.py',HERE.parent/'managed-revocation/probe.py',HERE.parent/'run.py']
        print(json.dumps(dict(schema='ases.management-pre-reply-cuts',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                                               executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                              cases=cases,uninterrupted=positive),indent=2,sort_keys=True))
if __name__=='__main__':main()
