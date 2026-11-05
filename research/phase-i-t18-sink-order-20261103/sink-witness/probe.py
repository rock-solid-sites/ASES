#!/usr/bin/env python3
"""Actual surviving-witness/rolled-sink histories, with bounded protocol controls."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import select
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
MANAGED=HERE.parent/'managed-revocation'
sys.path.insert(0,str(MANAGED))
import replay_probe as history
import probe as local_probe

SOURCE=HERE/'witness_sink.py'
spec=importlib.util.spec_from_file_location('witness_wrapper',SOURCE)
wrapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(wrapper)

class Child:
    def __init__(self,argv):
        self.meta=dict(start_ns=time.monotonic_ns(),argv=argv)
        self.process=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        readable,_,_=select.select([self.process.stdout],[],[],3)
        line=self.process.stdout.readline() if readable else ''
        if not line:
            self.process.kill();self.process.wait(timeout=2)
            raise RuntimeError('child not ready: '+self.process.stderr.read())
        self.ready=json.loads(line);self.port=self.ready['port']
        self.meta.update(pid=self.process.pid,ready_ns=time.monotonic_ns())
    def close(self):
        self.process.kill();self.meta['exit']=self.process.wait(timeout=2)
        self.meta['exit_ns']=time.monotonic_ns();self.meta['stderr']=self.process.stderr.read()
        self.process.stdout.close();self.process.stderr.close()
        return self.meta

class Sink(Child):
    def __init__(self,source,root,recover,witness,profile):
        root.mkdir(parents=True,exist_ok=True)
        self.journal=root/'sink-effects.jsonl'
        super().__init__([sys.executable,str(source),'--sink','recover' if recover else 'fresh',str(self.journal),
                          str(witness.port),profile,'selected-root-A'])

def facade(witness,profile):
    return SimpleNamespace(base=wrapper.managed.base,
                           RunningSink=lambda source,root,recover=False:Sink(source,root,recover,witness,profile))

def call(witness,path,body):
    start=time.monotonic_ns()
    code,reply=wrapper.managed.base.call(witness.port,'POST',path,body)
    return dict(path=path,body=body,start_ns=start,end_ns=time.monotonic_ns(),status=code,response=reply)

def observed(sink):
    return wrapper.managed.base.call(sink.port,'GET','/status')[1]

def main_case(root,profile):
    witness=Child([sys.executable,str(SOURCE),'--witness','selected-root-A'])
    module=facade(witness,profile);state_root=root/'state'
    try:
        writer=history.Session(module,SOURCE,state_root)
        try:
            history.bootstrap(writer)
            initial_publish=call(witness,'/publish',dict(state=observed(writer.sink)))
            writer.submit('before-positive',1,'before-witness-x')
            old=local_probe.snapshot(writer.sink.journal)
            writer.post('revoke','/revoke',{})
            revoke_publish=call(witness,'/publish',dict(state=observed(writer.sink)))
        finally: original=writer.close()
        retained=history.Session(module,SOURCE,state_root,True)
        try: retained.submit('retained-revoke',1,'not-x-retained')
        finally: retained_data=retained.close()
        rollback_start=time.monotonic_ns()
        journal=state_root/'sink-effects.jsonl'
        before_rollback=local_probe.snapshot(journal)
        with journal.open('wb') as stream:
            stream.write(bytes.fromhex(old['raw_hex']));stream.flush();os.fsync(stream.fileno())
        rollback=dict(start_ns=rollback_start,end_ns=time.monotonic_ns(),before=before_rollback,
                      restored=local_probe.snapshot(journal),old_actual_acknowledged=old)
        restored=history.Session(module,SOURCE,state_root,True)
        try: restored.submit('post-revoke-rolled',1,'x')
        finally: restored_data=restored.close()
        cold=history.Session(module,SOURCE,state_root,True).close()
        witness_status=wrapper.managed.base.call(witness.port,'GET','/status')[1]
        alive=witness.process.poll() is None
    finally: witness_exit=witness.close()
    return dict(profile=profile,writer=original,retained=retained_data,rollback=rollback,recovery=restored_data,cold=cold,
                initial_publish=initial_publish,revoke_publish=revoke_publish,witness_status=witness_status,
                witness_alive_after_all_sink_restarts=alive,witness=witness_exit)

def protocol_case(root):
    witness=Child([sys.executable,str(SOURCE),'--witness','selected-root-A'])
    module=facade(witness,'eligibility');session=history.Session(module,SOURCE,root/'state')
    try:
        history.bootstrap(session)
        publication=call(witness,'/publish',dict(state=observed(session.sink)))
        session.submit('positive',1,'protocol-positive')
        wrong=call(witness,'/fault',dict(wrong_nonce=True))
        session.submit('wrong-nonce',1,'not-x-nonce')
        reset=call(witness,'/fault',dict(wrong_nonce=False))
        session.submit('positive-after-reset',1,'protocol-reset-positive')
        witness_status=wrapper.managed.base.call(witness.port,'GET','/status')[1]
        witness_exit=witness.close()
        session.submit('missing-witness',1,'not-x-missing')
    finally:
        if witness.process.poll() is None: witness.close()
        data=session.close()
    return dict(session=data,publication=publication,wrong_nonce=wrong,reset=reset,
                witness_status=witness_status,witness=witness_exit)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-sink-witness-') as directory:
        root=Path(directory)
        cases={profile:main_case(root/profile,profile) for profile in ('generation','eligibility')}
        protocol=protocol_case(root/'protocol')
        files=[SOURCE,HERE/'probe.py',MANAGED/'managed_sink.py',MANAGED/'replay_probe.py',MANAGED/'probe.py',HERE.parent/'run.py']
        print(json.dumps(dict(schema='ases.sink-witness-history',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                                               executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                              cases=cases,protocol_controls=protocol),indent=2,sort_keys=True))

if __name__=='__main__':main()
