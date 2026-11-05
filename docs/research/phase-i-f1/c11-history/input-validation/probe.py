#!/usr/bin/env python3
"""Invalid companion observation inputs, actual commit/rollback and ready boundary."""
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
spec=importlib.util.spec_from_file_location('validation_history_support',HERE.parent/'probe.py')
history=importlib.util.module_from_spec(spec);spec.loader.exec_module(history)
support=history.support;SOURCE=history.SOURCE;FIXTURE=HERE/'invalid-missing.sqlite'

def holder(path,label,observations=None,context=0):
    return support.Holder(path,label,observations=observations,context=context,extra_config=dict(retention_profile='archive'),
                          service_source=SOURCE,allow_startup_failure=True)
def inspect(path):
    with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True) as db:
        view=db.execute('SELECT view FROM kernel WHERE id=1').fetchone()[0]
        latest=db.execute('SELECT record FROM consumer_observations WHERE id=1').fetchone()[0]
        archived=[r[0] for r in db.execute('SELECT record FROM consumer_archive ORDER BY accepted_content')]
        print(json.dumps(dict(diagnostic_only=True,integrity=db.execute('PRAGMA integrity_check').fetchone()[0],
                              view=json.loads(view),view_raw_hex=view.encode().hex(),latest=json.loads(latest),latest_raw_hex=latest.encode().hex(),
                              archived=[json.loads(r) for r in archived],archived_raw_hex=[r.encode().hex() for r in archived]),sort_keys=True))
def diagnostic(path):
    start=time.monotonic_ns()
    p=subprocess.Popen([sys.executable,__file__,'--inspect',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    out,err=p.communicate(timeout=4)
    return dict(pid=p.pid,start_ns=start,exit_ns=time.monotonic_ns(),exit=p.returncode,stderr=err,observation=json.loads(out))
def one(root,name,phase):
    root.mkdir();path=root/'store.sqlite';old=dict(history.STABLE,consumer_evidence='accepted earlier validation evidence')
    support.service.persistent.initialize(str(path),'work','independent')
    with sqlite3.connect(path,isolation_level=None) as db:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)')
        db.execute('CREATE TABLE consumer_archive(accepted_content TEXT PRIMARY KEY,record TEXT NOT NULL)')
    bootstrap=holder(path,'bootstrap',old,-1)
    try:setup=[bootstrap.call(support.inherited.wire(q)) for q in (support.model.Request('establish'),support.model.Request('grant',target=0,value=7))]
    finally:bootstrap_exit=bootstrap.close()
    seed=None
    if name=='conflict':
        initial=holder(path,'seed',history.NEW)
        try:seed_call=initial.call(support.inherited.wire(support.model.Request('accept',0,value=1)))
        finally:seed=dict(process=initial.close(),call=seed_call)
    candidate=dict(history.NEW)
    if name=='missing':del candidate['consumer_evidence']
    if name=='type':candidate['consumer_evidence']=42
    if name=='conflict':candidate['consumer_evidence']='conflicting same-content evidence'
    writer=holder(path,'writer',candidate)
    try:request=writer.call(support.inherited.wire(support.model.Request('accept',0,value=1))) if writer.meta['ready'] else None
    finally:writer_exit=writer.close()
    recovered=holder(path,'recovered')
    try:query=recovered.call(dict(kind='read')) if recovered.meta['ready'] else None
    finally:recovered_exit=recovered.close()
    raw=diagnostic(path);trace_path=root/'writer.trace.jsonl'
    artifact=None
    if phase=='baseline' and name=='missing':
        data=path.read_bytes()
        with FIXTURE.open('xb') as stream:stream.write(data)
        artifact=dict(path=FIXTURE.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    return dict(name=name,candidate=candidate,bootstrap=dict(process=bootstrap_exit,calls=setup),seed=seed,
                writer=writer_exit,request=request,recovered=recovered_exit,recovery_query=query,diagnostic=raw,
                writer_trace=[json.loads(line) for line in trace_path.read_text().splitlines()] if trace_path.exists() else [],artifact=artifact)

def artifact_recovery():
    before=hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    h=holder(FIXTURE,'retained-invalid-recovery')
    try:query=h.call(dict(kind='read')) if h.meta['ready'] else None
    finally:process=h.close()
    return dict(before_sha256=before,after_sha256=hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),process=process,query=query)

def main(phase):
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-c11-input-validation-') as directory:
        root=Path(directory)
        cases={name:one(root/name,name,phase) for name in ('valid','missing','type','conflict')}
        fixture=artifact_recovery()
        files=[SOURCE,HERE/'probe.py',HERE.parent/'probe.py',HERE.parents[1]/'c11-sqlite/c11_service.py',HERE.parents[1]/'c11-sqlite/probe.py',
               support.service.HERE.parents[1]/'kernel-0/kernel0_recovery_service.py',support.service.HERE.parents[1]/'kernel-0/kernel0_service.py']
        base=HERE.parents[2]
        print(json.dumps(dict(schema='ases.c11-required-input-validation',version=1,phase=phase,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
                                               executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                              cases=cases,retained_invalid_artifact=fixture),indent=2,sort_keys=True))

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--inspect':inspect(sys.argv[2])
    elif len(sys.argv)==2 and sys.argv[1] in ('baseline','fixed'):main(sys.argv[1])
    else:raise SystemExit('usage: probe.py {baseline|fixed} | --inspect PATH')
