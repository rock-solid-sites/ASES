#!/usr/bin/env python3
"""Retain progress from first original context without changing the model."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent

def child(kind):
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    import phase_i_f1_model as m
    start=time.monotonic()
    def emit(**data):print(json.dumps({'elapsed':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**data}),flush=True)
    def progress(_sig,frame):
        while frame:
            if frame.f_code.co_name=='explore':
                loc=frame.f_locals
                emit(phase='explore_progress',context=loc.get('context'),seen=len(loc.get('seen',{})),
                     queued=len(loc.get('queue',[])),commits=loc.get('commits'))
                break
            frame=frame.f_back
    emit(phase='import_complete',pid=os.getpid(),kind=kind)
    if kind=='import':return
    signal.signal(signal.SIGALRM,progress);signal.setitimer(signal.ITIMER_REAL,.5,.5)
    emit(phase='explore_start',context='containment-and-grants')
    try:
        seen,commits,denials,violations=m.explore(m.REFERENCE,'containment-and-grants',limit=100 if kind=='cap100' else None)
        emit(phase='explore_complete',seen=len(seen),commits=commits,violations=len(violations))
        emit(phase='observation_start')
        obs=m.observational_equivalence(seen)
        emit(phase='observation_complete',result=obs)
    except RuntimeError as exc:
        emit(phase='declared_bound_exception',message=str(exc))
        return 2
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    return 0

def main():
    if len(sys.argv)>1:return child(sys.argv[1])
    cases={}
    for kind in ['import','cap100','default_first_context']:
        t=time.monotonic()
        p=subprocess.Popen([sys.executable,__file__,kind],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        timed_out=False
        try:out,err=p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            timed_out=True;p.kill();out,err=p.communicate(timeout=2)
        cases[kind]={'exit':p.returncode,'timed_out':timed_out,'elapsed':time.monotonic()-t,
                     'stdout':out,'stderr':err,'events':[json.loads(l) for l in out.splitlines()]}
    assert cases['import']['exit']==0 and cases['cap100']['exit']==2
    assert cases['cap100']['events'][-1]['phase']=='declared_bound_exception'
    print(json.dumps({'schema':'ases.f1-model-timeout.v1','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'hashes':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['round2_model_timeout.py','phase_i_f1_model.py']},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                      'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':raise SystemExit(main())
