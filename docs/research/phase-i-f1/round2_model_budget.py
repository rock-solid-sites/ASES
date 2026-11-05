#!/usr/bin/env python3
"""One30s unchanged original first-context probe; no implicit full-model verdict."""
import hashlib,json,platform,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    sources=['round2_model_budget.py','round2_model_timeout.py','phase_i_f1_model.py']
    hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in sources}
    start=time.monotonic()
    p=subprocess.Popen([sys.executable,str(HERE/'round2_model_timeout.py'),'default_first_context'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    timed_out=False
    try:out,err=p.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        timed_out=True;p.kill();out,err=p.communicate(timeout=2)
    elapsed=time.monotonic()-start
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)  # This parent's first/only child so far.
    events=[json.loads(line) for line in out.splitlines()]
    phases=[e['phase'] for e in events]
    if timed_out:status='timed_out_inconclusive'
    elif p.returncode==2 and phases[-1]=='declared_bound_exception':status='declared_state_bound_inconclusive'
    elif p.returncode==0 and phases[-1]=='observation_complete':status='first_context_completed'
    elif 'MemoryError' in err:status='memory_limit_inconclusive'
    else:status='unexpected_execution_failure'
    unchanged=hashes=={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in sources}
    assert unchanged
    print(json.dumps(dict(schema='ases.f1-model-budget.v1',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                         source_sha256=hashes,environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                         executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()),
                         command=[sys.executable,str(HERE/'round2_model_timeout.py'),'default_first_context'],
                         bounds=dict(wall_seconds=30,child_virtual_bytes=256*1024*1024,context='containment-and-grants',model_unchanged=True),
                         pid=p.pid,exit=p.returncode,timed_out=timed_out,status=status,elapsed_seconds=elapsed,
                         child_cpu_seconds=usage.ru_utime+usage.ru_stime,child_lifetime_peak_rss_kib=usage.ru_maxrss,
                         events=events,stdout=out,stderr=err,source_stable=unchanged,
                         limits='One original first context only, original declared bound. No full driver/other contexts/semantic checks/attacks or generic F1 acceptance. Incomplete is no pass/fail; do not keep doubling solely for counts.'),indent=2,sort_keys=True))
if __name__=='__main__':main()
