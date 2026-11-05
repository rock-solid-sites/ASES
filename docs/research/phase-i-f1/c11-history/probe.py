#!/usr/bin/env python3
"""Two authentic earlier-evidence histories; latest-only versus retained archive."""
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'c11-sqlite'))
spec=importlib.util.spec_from_file_location('history_physical_support',HERE.parent/'c11-sqlite/probe.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
SOURCE=HERE/'history_service.py'
STABLE=dict(identity_genesis='stable-genesis',created_by='stable-creator',project='stable-project')
NEW=dict(STABLE,consumer_evidence='required later evidence M / μ')

def holder(path,label,profile,observations=None,context=0,stage=None):
    return support.Holder(path,label,observations=observations,context=context,stage=stage,
                          extra_config=dict(retention_profile=profile),service_source=SOURCE)

def independent(path,profile):
    start=time.monotonic_ns()
    child=subprocess.Popen([sys.executable,str(SOURCE),'--reader',str(path),profile],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    out,err=child.communicate(timeout=4)
    return dict(start_ns=start,exit_ns=time.monotonic_ns(),pid=child.pid,exit=child.returncode,stderr=err,observation=json.loads(out))

def one(root,profile,world):
    root.mkdir();path=root/'store.sqlite';old=dict(STABLE,consumer_evidence='required earlier evidence '+world+' / μ')
    support.service.persistent.initialize(str(path),'work','independent')
    with sqlite3.connect(path,isolation_level=None) as db:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)')
        db.execute('CREATE TABLE consumer_archive(accepted_content TEXT PRIMARY KEY,record TEXT NOT NULL)')
    bootstrap=holder(path,'bootstrap',profile,old,-1)
    try:setup=[bootstrap.call(support.inherited.wire(q)) for q in (support.model.Request('establish'),support.model.Request('grant',target=0,value=7))]
    finally:bootstrap_exit=bootstrap.close()
    writer=holder(path,'writer',profile,NEW,stage='durable')
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future=executor.submit(writer.call,support.inherited.wire(support.model.Request('accept',0,value=1)))
        try:gate=writer.gated()
        finally:writer_exit=writer.close(close_client=False)
        try:accept=future.result(timeout=4)
        finally:writer.client.close()
    at_loss=support.files(root)
    recovered=holder(path,'recovered',profile)  # No original old/new tuples or oracle.
    try:query=recovered.call(dict(kind='read'))
    finally:recovered_exit=recovered.close()
    raw=independent(path,profile)
    trace=[json.loads(line) for line in (root/'writer.trace.jsonl').read_text().splitlines()]
    return dict(profile=profile,world=world,required_earlier=old,required_later=NEW,bootstrap=dict(process=bootstrap_exit,calls=setup),
                writer=writer_exit,accept=accept,gate=gate,files_at_loss=at_loss,recovered=recovered_exit,recovered_query=query,
                independent_reader=raw,writer_trace=trace,final_files=support.files(root))

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-c11-history-') as directory:
        root=Path(directory)
        cases={profile+'-'+world:one(root/(profile+'-'+world),profile,world) for profile in ('latest','archive') for world in ('A','B')}
        files=[SOURCE,HERE/'probe.py',HERE.parent/'c11-sqlite/c11_service.py',HERE.parent/'c11-sqlite/probe.py',
               support.service.HERE.parents[1]/'kernel-0/kernel0_recovery_service.py',support.service.HERE.parents[1]/'kernel-0/kernel0_service.py',
               support.service.HERE.parents[1]/'kernel-0/kernel0_recovery_check.py',support.service.HERE.parents[1]/'kernel-0/kernel0_finite_model.py']
        base=HERE.parents[1]
        print(json.dumps(dict(schema='ases.c11-required-history',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
                                               executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                              cases=cases),indent=2,sort_keys=True))
if __name__=='__main__':main()
