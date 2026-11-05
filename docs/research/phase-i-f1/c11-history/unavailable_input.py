#!/usr/bin/env python3
"""Actual recovered holder read versus new acceptance with no required input."""
import hashlib,importlib.util,json,platform,resource,sqlite3,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('unavailable_validation_support',HERE/'input-validation/probe.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
support=v.support

def one(root,explicit):
    root.mkdir();path=root/'store.sqlite';old=dict(v.history.STABLE,consumer_evidence='retained before unavailable-input test')
    support.service.persistent.initialize(str(path),'work','independent')
    with sqlite3.connect(path,isolation_level=None) as db:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)')
        db.execute('CREATE TABLE consumer_archive(accepted_content TEXT PRIMARY KEY,record TEXT NOT NULL)')
    bootstrap=v.holder(path,'bootstrap',old,-1)
    try:setup=[bootstrap.call(support.inherited.wire(q)) for q in (support.model.Request('establish'),support.model.Request('grant',target=0,value=7))]
    finally:bootstrap_exit=bootstrap.close()
    holder=v.holder(path,'writer',v.history.NEW if explicit else None)
    try:
        before=holder.call(dict(kind='read'))
        attempt=holder.call(support.inherited.wire(support.model.Request('accept',0,value=1)))
    finally:holder_exit=holder.close()
    cold=v.holder(path,'recovered')
    try:query=cold.call(dict(kind='read')) if cold.meta['ready'] else None
    finally:cold_exit=cold.close()
    return dict(explicit_input=explicit,bootstrap=dict(process=bootstrap_exit,calls=setup),writer=holder_exit,before=before,attempt=attempt,
                recovered=cold_exit,recovery_query=query,diagnostic=v.diagnostic(path),
                trace=[json.loads(row) for row in (root/'writer.trace.jsonl').read_text().splitlines()])

def main(phase):
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    with tempfile.TemporaryDirectory(prefix='ases-c11-unavailable-') as directory:
        root=Path(directory);cases=dict(unavailable=one(root/'unavailable',False),explicit=one(root/'explicit',True))
        files=[HERE/'history_service.py',HERE/'unavailable_input.py',HERE/'input-validation/probe.py',HERE/'probe.py',
               HERE.parent/'c11-sqlite/probe.py',HERE.parent/'c11-sqlite/c11_service.py',
               support.service.HERE.parents[1]/'kernel-0/kernel0_recovery_service.py',support.service.HERE.parents[1]/'kernel-0/kernel0_service.py']
        base=HERE.parents[1]
        print(json.dumps(dict(schema='ases.c11-unavailable-input',version=1,phase=phase,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                              environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
                              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),cases=cases),indent=2,sort_keys=True))
if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('baseline','fixed'):raise SystemExit('usage: unavailable_input.py {baseline|fixed}')
    main(sys.argv[1])
