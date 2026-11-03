#!/usr/bin/env python3
"""Record actual post-replacement HTTP calls against the pinned disposable sink."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'run.py'
NEEDLE='''                    if token != state.version:
                        state.emit_locked(
                            "sink_rejected",'''
REPLACEMENT='''                    if False and token != state.version:
                        state.emit_locked(
                            "sink_rejected",'''


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def invoke(module, port, path, body):
    started=time.monotonic_ns()
    status, data=module.call(port,'POST',path,body)
    completed=time.monotonic_ns()
    return {'request':{'method':'POST','path':path,'body':body}, 'start_monotonic_ns':started,
            'completion_monotonic_ns':completed, 'response':{'status':status,'body':data}}


def case(module, root, variant):
    sink=module.RunningSink('sink-ordered',root)
    try:
        steps=[]
        for path,body in [('/submit',{'authority_version':1,'request_id':'before-current','payload':'before-x'}),
                          ('/replace',{}),
                          ('/submit',{'authority_version':1,'request_id':'after-stale','payload':'stale-x'}),
                          ('/submit',{'authority_version':2,'request_id':'after-current','payload':'current-x'})]:
            step=invoke(module,sink.port,path,body)
            step['sink_snapshot']=module.latest_status(sink)
            steps.append(step)
        raw=sink.journal.read_bytes()
        pid=sink.process.pid
    finally:
        exit_code=sink.kill_and_reap()
    return {'variant':variant, 'sink_pid':pid, 'sink_exit':exit_code, 'steps':steps,
            'journal_raw_hex':raw.hex(), 'journal_sha256':hashlib.sha256(raw).hexdigest()}


def main():
    source=SOURCE.read_text()
    assert source.count(NEEDLE)==1
    with tempfile.TemporaryDirectory(prefix='f3-t18-postsend-') as td:
        root=Path(td)
        mutant_path=root/'sink_mutant.py'
        mutant_path.write_text(source.replace(NEEDLE,REPLACEMENT,1))
        safe=load(SOURCE,'t18_sink_original')
        mutant=load(mutant_path,'t18_sink_bypass')
        cases={'reference':case(safe,root/'reference','reference'),
               'bypass_mutant':case(mutant,root/'bypass','bypass')}
        print(json.dumps({'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
                          'mutant_sha256':hashlib.sha256(mutant_path.read_bytes()).hexdigest(),
                          'mutation':'replace first submit current-version comparison with False',
                          'bounds':{'cases':2,'sinks_concurrent':1,'enumerated':False,'truncated':False},
                          'cases':cases},indent=2,sort_keys=True))

if __name__=='__main__': main()
