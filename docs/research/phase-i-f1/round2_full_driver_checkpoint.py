#!/usr/bin/env python3
"""Bounded original-driver telemetry; does not alter transitions or check results."""
import hashlib,json,os,platform,resource,signal,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def child(report):
    resource.setrlimit(resource.RLIMIT_AS,(1024*1024*1024,)*2)
    import phase_i_f1_model as m
    start=time.monotonic();active=[]
    def emit(**data):
        event=dict(elapsed=time.monotonic()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**data)
        os.write(1,(json.dumps(event,sort_keys=True)+'\n').encode())
    def monitor(name,fn):
        def run(*args,**kwargs):
            context=kwargs.get('context',args[1] if name=='explore' and len(args)>1 else None)
            entry=dict(function=name)
            if name=='explore':
                context=context or 'all';profile=kwargs.get('p',args[0] if args else m.REFERENCE)
                entry.update(context=context,profile=profile.__dict__,declared_state_bound=kwargs.get('limit') or m.CONTEXT_BOUNDS[context])
            active.append(entry);emit(phase='enter',**entry)
            try:result=fn(*args,**kwargs)
            except BaseException as error:
                emit(phase='exception',error=type(error).__name__,message=str(error),**entry);raise
            else:
                output={}
                if name=='explore':
                    output=dict(states=len(result[0]),commits=result[1],denials=sum(result[2].values()),violations=len(result[3]),
                                violation_examples=result[3][:2],use_oracle_failure_count=len(m.USE_ORACLE_FAILURES))
                elif name=='semantic_checks':output=dict(checks=len(result),failed_checks=[r for r in result if not r['passed']])
                elif name=='observational_equivalence':output=dict(result=result)
                else:output=dict(result_type=type(result).__name__,result_count=len(result))
                emit(phase='return',**entry,**output);return result
            finally:active.pop()
        return run
    for name in ('explore','semantic_checks','observational_equivalence','run_witnesses','attack_report'):
        setattr(m,name,monitor(name,getattr(m,name)))
    def progress(_signal,frame):
        output=dict(active=active[-1] if active else None)
        while frame:
            if frame.f_code.co_name=='explore':
                loc=frame.f_locals;output.update(context=loc.get('context'),seen=len(loc.get('seen',{})),
                                               queued=len(loc.get('queue',[])),commits=loc.get('commits'));break
            frame=frame.f_back
        emit(phase='progress',**output)
    signal.signal(signal.SIGALRM,progress);signal.setitimer(signal.ITIMER_REAL,1,1)
    emit(phase='driver_start',pid=os.getpid())
    try:
        code=m.main(['--output',str(report)]);emit(phase='driver_return',exit=code);return code
    finally:signal.setitimer(signal.ITIMER_REAL,0)

def main():
    hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('round2_full_driver_checkpoint.py','phase_i_f1_model.py')}
    with tempfile.TemporaryDirectory(prefix='ases-full-model-phase-') as directory:
        report=Path(directory)/'original-report.json';start=time.monotonic()
        p=subprocess.Popen([sys.executable,__file__,'--child',str(report)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        timeout=False
        try:out,err=p.communicate(timeout=40)
        except subprocess.TimeoutExpired:timeout=True;p.kill();out,err=p.communicate(timeout=2)
        elapsed=time.monotonic()-start;usage=resource.getrusage(resource.RUSAGE_CHILDREN)
        events=[];other=[]
        for line in out.splitlines():
            try:events.append(json.loads(line))
            except ValueError:other.append(line)
        artifact=None
        if report.exists():
            raw=report.read_bytes();destination=HERE/'round2-full-driver.report.json'
            with destination.open('xb') as stream:stream.write(raw)
            artifact=dict(path=destination.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        if timeout:status='timed_out_inconclusive'
        elif artifact is not None:status='original_driver_completed'
        elif 'MemoryError' in err:status='memory_limit_inconclusive'
        elif any(e.get('error')=='RuntimeError' and 'state bound exceeded' in e.get('message','') for e in events):status='declared_state_bound_inconclusive'
        else:status='unexpected_execution_failure'
        assert hashes=={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in hashes}
        print(json.dumps(dict(schema='ases.full-model-phase-checkpoint.v1',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              source_hashes=hashes,environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()),
                              bounds=dict(wall_seconds=40,child_virtual_bytes=1024*1024*1024),pid=p.pid,exit=p.returncode,
                              timed_out=timeout,status=status,elapsed_seconds=elapsed,child_cpu_seconds=usage.ru_utime+usage.ru_stime,
                              child_lifetime_peak_rss_kib=usage.ru_maxrss,events=events,stdout=out,stderr=err,other_stdout=other,original_report=artifact,
                              source_stable=True,limits='Original abstract driver/function results preserved, telemetry overhead unquantified. Incomplete is no pass/fail. Known context-inapplicable helper caveat not new. No host/power-loss or generic F1/PhaseI closure.'),indent=2,sort_keys=True))
if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--child':raise SystemExit(child(Path(sys.argv[2])))
    main()
