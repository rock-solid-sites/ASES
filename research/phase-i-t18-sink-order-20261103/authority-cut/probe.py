#!/usr/bin/env python3
"""Actual current authority witness with a rolled accepted-content/obligation cut."""
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
spec=importlib.util.spec_from_file_location('authority_cut_support',HERE.parent/'sink-witness/probe.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
FIELDS=('created','granted','active','authority_version','holder')
def authority(state):return {key:state[key] for key in FIELDS}
def witness_status(w):return s.wrapper.managed.base.call(w.port,'GET','/status')[1]

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-authority-cut-') as directory:
        root=Path(directory);state_root=root/'state';journal=state_root/'sink-effects.jsonl'
        witness=s.Child([sys.executable,str(s.SOURCE),'--witness','selected-root-A'])
        module=s.facade(witness,'eligibility');marks={}
        try:
            writer=s.history.Session(module,s.SOURCE,state_root)
            try:
                s.history.bootstrap(writer)
                original_authority=authority(s.observed(writer.sink))
                prefix=s.local_probe.snapshot(journal);marks['prefix_ns']=time.monotonic_ns()
                first_publish=s.call(witness,'/publish',dict(state=original_authority))
                writer.submit('old-ACKed-x',1,'required accepted x / μ')
                writer.post('committed-q','/commit-obligation',dict(authority_version=1,obligation_id='q',payload='owed exact q / μ'))
                accepted=s.observed(writer.sink);accepted_journal=s.local_probe.snapshot(journal)
                current_authority=authority(accepted)
                current_publish=s.call(witness,'/publish',dict(state=current_authority))  # Authority fields only, no x/q/oracle.
                before_loss_witness=witness_status(witness)
            finally:original=writer.close()
            proper=s.history.Session(module,s.SOURCE,state_root,True).close()
            marks['rollback_start_ns']=time.monotonic_ns()
            before_rollback=s.local_probe.snapshot(journal)
            with journal.open('wb') as stream:
                stream.write(bytes.fromhex(prefix['raw_hex']));stream.flush();os.fsync(stream.fileno())
            after_rollback=s.local_probe.snapshot(journal);marks['rollback_end_ns']=time.monotonic_ns()
            rolled=s.history.Session(module,s.SOURCE,state_root,True)
            try:
                rolled.submit('new-ACKed-y',1,'accepted y after stale cut / μ')
                rolled.post('lost-q-delivery','/deliver-obligation',dict(obligation_id='q'))
            finally:rolled_data=rolled.close()
            cold=s.history.Session(module,s.SOURCE,state_root,True).close()
            final_witness=witness_status(witness)
            witness_alive=witness.process.poll() is None
        finally:witness_exit=witness.close()
        files=[HERE/'probe.py',s.SOURCE,HERE.parent/'sink-witness/probe.py',HERE.parent/'managed-revocation/managed_sink.py',
               HERE.parent/'managed-revocation/replay_probe.py',HERE.parent/'managed-revocation/probe.py',HERE.parent/'run.py']
        print(json.dumps(dict(schema='ases.authority-current-versus-accepted-cut',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                              original_authority=original_authority,current_authority=current_authority,original=original,
                              prefix=prefix,accepted_status=accepted,accepted_journal=accepted_journal,
                              first_publish=first_publish,current_publish=current_publish,witness_before_loss=before_loss_witness,
                              proper_current_journal_recovery=proper,marks=marks,before_rollback=before_rollback,after_rollback=after_rollback,
                              rolled=rolled_data,cold=cold,witness_status=final_witness,witness_alive=witness_alive,witness=witness_exit),indent=2,sort_keys=True))
if __name__=='__main__':main()
