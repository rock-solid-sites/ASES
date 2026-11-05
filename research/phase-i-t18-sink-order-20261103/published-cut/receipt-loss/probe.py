#!/usr/bin/env python3
"""Actual remote CAS update with a deliberately closed, unsent HTTP reply."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent;BASE=HERE.parent.parent
spec=importlib.util.spec_from_file_location('published_receipt_support',HERE.parent/'probe.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
s=p.s;SOURCE=p.SOURCE

def one(root,kind):
    w=s.Child([sys.executable,str(SOURCE),'--witness',p.ROOT]);module=s.facade(w,'published-cut')
    state=root/'state';journal=state/'sink-effects.jsonl';children=[];extra={}
    try:
        init=p.wcall(w,'/init',cut=p.cut.GENESIS)
        writer=s.history.Session(module,SOURCE,state)
        try:
            s.history.bootstrap(writer);writer.submit('earlier-ack',1,'earlier actually ACKed effect / μ')
            prior=s.local_probe.snapshot(journal);w_before=p.wstatus(w)
            fault=p.wcall(w,'/fault',reject_publish=kind=='rejected',drop_publish_reply_once=kind=='lost')
            writer.submit('receipt-z',1,'locally committed receipt outcome / μ')
            after_z=s.local_probe.snapshot(journal);w_after_z=p.wstatus(w)
            writer.submit('next-after-outcome',1,'next after receipt outcome / μ')
            after_next=s.local_probe.snapshot(journal)
        finally:original=writer.close();children.append(original)
        if kind=='rejected':
            extra['startup_refusal']=p.attempt(state,w);children.append(extra['startup_refusal'])
        else:
            recovered=s.history.Session(module,SOURCE,state,True)
            try:recovered.submit('fresh-after-restart',1,'new after real process restart / μ')
            finally:extra['recovered']=recovered.close();children.append(extra['recovered'])
            extra['cold']=s.history.Session(module,SOURCE,state,True).close();children.append(extra['cold'])
        final=p.wstatus(w);alive=w.process.poll() is None
    finally:witness=w.close();children.append(witness)
    return dict(kind=kind,init=init,fault=fault,prior_journal=prior,witness_before=w_before,original=original,
                after_z=after_z,witness_after_z=w_after_z,after_next=after_next,witness_final=final,
                witness_alive=alive,witness=witness,children=children,**extra)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    files=[SOURCE,HERE.parent/'probe.py',HERE.parent/'check.py',HERE/'probe.py',HERE/'check.py',BASE/'sink-witness/probe.py',
           BASE/'sink-witness/witness_sink.py',BASE/'managed-revocation/managed_sink.py',
           BASE/'managed-revocation/replay_probe.py',BASE/'managed-revocation/probe.py',BASE/'run.py']
    with tempfile.TemporaryDirectory(prefix='ases-cut-receipt-') as directory:
        root=Path(directory);cases={kind:one(root/kind,kind) for kind in ('positive','lost','rejected')}
        print(json.dumps(dict(schema='ases.published-cut-receipt-loss',version=1,
                             execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                             source_hashes={str(f.relative_to(BASE)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
                             environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                             executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                             cases=cases),indent=2,sort_keys=True))
if __name__=='__main__':main()
