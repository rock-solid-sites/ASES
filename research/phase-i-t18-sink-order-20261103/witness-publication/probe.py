#!/usr/bin/env python3
"""Actual management/publication gaps and bounded revoke ACK barrier controls."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('publication_support',HERE.parent/'sink-witness/probe.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
SOURCE=HERE/'publication_sink.py'

def witness_status(w):return support.wrapper.managed.base.call(w.port,'GET','/status')[1]
def restore(path,snapshot):
    start=time.monotonic_ns();before=support.local_probe.snapshot(path)
    with path.open('wb') as stream:
        stream.write(bytes.fromhex(snapshot['raw_hex']));stream.flush();os.fsync(stream.fileno())
    return dict(start_ns=start,end_ns=time.monotonic_ns(),before=before,after=support.local_probe.snapshot(path))

def success_case(root,barrier):
    witness=support.Child([sys.executable,str(support.SOURCE),'--witness','selected-root-A'])
    module=support.facade(witness,'eligibility');source=SOURCE if barrier else support.SOURCE
    state=root/'state'
    try:
        writer=support.history.Session(module,source,state)
        try:
            support.history.bootstrap(writer)
            initial=support.call(witness,'/publish',dict(state=support.observed(writer.sink)))
            writer.submit('before-positive',1,'before-publication-x')
            older=support.local_probe.snapshot(writer.sink.journal)
            writer.post('revoke','/revoke',{})
            revoked=support.observed(writer.sink)
            witness_after_revoke=witness_status(witness)
        finally: original=writer.close()
        rollback=restore(state/'sink-effects.jsonl',older)
        recovered=support.history.Session(module,source,state,True)
        try:
            recovered.submit('post-revoke-rolled',1,'x')
            late=None
            if not barrier:
                late=support.call(witness,'/publish',dict(state=revoked))
                recovered.submit('after-late-publication',1,'not-x-late')
        finally: recovery=recovered.close()
        cold=support.history.Session(module,source,state,True).close()
        final_witness=witness_status(witness)
    finally: exit_witness=witness.close()
    return dict(barrier=barrier,writer=original,recovery=recovery,cold=cold,initial_publication=initial,
                older_actual_acknowledged=older,rollback=rollback,witness_after_revoke=witness_after_revoke,
                late_publication=late,witness_status=final_witness,witness=exit_witness)

def failure_case(root,fault):
    witness=support.Child([sys.executable,str(support.SOURCE),'--witness','selected-root-A'])
    module=support.facade(witness,'eligibility');state=root/'state'
    writer=support.history.Session(module,SOURCE,state)
    try:
        support.history.bootstrap(writer)
        initial=support.call(witness,'/publish',dict(state=support.observed(writer.sink)))
        writer.submit('before-positive',1,'before-failed-publication')
        if fault=='missing':
            configured=None;before=witness_status(witness);exit_witness=witness.close()
        else:
            configured=support.call(witness,'/fault',dict(publish_fault=fault));before=witness_status(witness)
        writer.post('revoke','/revoke',{})
        writer.submit('after-failed-revoke',1,'not-x-failed')
        after=witness_status(witness) if witness.process.poll() is None else None
    finally: original=writer.close()
    try:
        cold=support.history.Session(module,SOURCE,state,True)
        try:cold.submit('cold-old-denial',1,'not-x-cold')
        finally:cold_data=cold.close()
    finally:
        if witness.process.poll() is None:exit_witness=witness.close()
    return dict(fault=fault,writer=original,cold=cold_data,initial_publication=initial,configured=configured,
                witness_before=before,witness_after=after,witness=exit_witness)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-witness-publication-') as directory:
        root=Path(directory)
        cases=dict(delayed=success_case(root/'delayed',False),barrier=success_case(root/'barrier',True))
        failures={f:failure_case(root/f,f) for f in ('reject','wrong_nonce','missing')}
        files=[SOURCE,HERE/'probe.py',HERE.parent/'sink-witness/witness_sink.py',HERE.parent/'sink-witness/probe.py',
               HERE.parent/'managed-revocation/managed_sink.py',HERE.parent/'managed-revocation/replay_probe.py',
               HERE.parent/'managed-revocation/probe.py',HERE.parent/'run.py']
        print(json.dumps(dict(schema='ases.witness-publication-history',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                                               executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                              cases=cases,publication_failures=failures),indent=2,sort_keys=True))
if __name__=='__main__':main()
