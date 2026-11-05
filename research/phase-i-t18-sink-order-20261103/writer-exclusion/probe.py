#!/usr/bin/env python3
"""Actual same-root startup overlap; no journal fixture passed to recovery."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import select
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py';GUARDED=HERE/'guarded_sink.py';OWNED=[]
spec=importlib.util.spec_from_file_location('writer_probe_base',SOURCE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def snapshot(path):
    raw=path.read_bytes() if path.exists() else b''
    return dict(exists=path.exists(),raw_hex=raw.hex(),sha256=hashlib.sha256(raw).hexdigest(),ns=time.monotonic_ns())
def same_bytes(a,b):return all(a[k]==b[k] for k in ('exists','raw_hex','sha256'))

class Sink:
    def __init__(self,root,guarded,mode='sink-ordered'):
        root.mkdir(parents=True,exist_ok=True);self.journal=root/'sink-effects.jsonl'
        self.meta=dict(start_ns=time.monotonic_ns(),journal_path=str(self.journal),guarded=guarded,mode=mode)
        self.process=subprocess.Popen([sys.executable,str(GUARDED if guarded else SOURCE),'--server',mode,str(self.journal)],
                                      stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        self.meta['pid']=self.process.pid;OWNED.append(self)
        readable=select.select([self.process.stdout],[],[],3)[0]
        line=self.process.stdout.readline() if readable else b''
        frame=json.loads(line) if line else None
        self.ready=frame is not None and frame.get('ready') is True
        self.meta.update(ready=self.ready,startup_frame=frame,startup_raw_hex=line.hex(),startup_observed_ns=time.monotonic_ns())
        if self.ready:self.port=frame['port']
        else:
            if not readable:self.process.kill()
            self.stop(kill=False)
    def stop(self,kill=True):
        if 'exit' in self.meta:return self.meta
        if kill and self.process.poll() is None:self.process.kill()
        out,err=self.process.communicate(timeout=3)
        self.meta.update(exit=self.process.returncode,exit_ns=time.monotonic_ns(),remaining_stdout_hex=out.hex(),stderr=err.decode())
        return self.meta
    def status(self):return base.call(self.port,'GET','/status')[1]
    def submit(self,name):
        request=dict(authority_version=1,request_id=name,payload='payload-'+name)
        start=time.monotonic_ns();code,reply=base.call(self.port,'POST','/submit',request)
        end=time.monotonic_ns()
        return dict(request=request,start_ns=start,end_ns=end,response=dict(status=code,body=reply),status=self.status(),journal=snapshot(self.journal))

def overlap(root,mixed):
    a=Sink(root,mixed);after_a=snapshot(a.journal)
    b=Sink(root,False);before=snapshot(a.journal)
    try:
        first=a.submit('A');second=b.submit('B');a_status=a.status();b_status=b.status();raw=snapshot(a.journal)
    finally:ae=a.stop();be=b.stop()
    cold=Sink(root,mixed,'recover-ordered')
    try:cold_status=cold.status() if cold.ready else None
    finally:ce=cold.stop()
    return dict(mixed=mixed,A=ae,B=be,journal_after_A_ready=after_a,journal_before_requests=before,
                first=first,second=second,A_final=a_status,B_final=b_status,after=raw,cold=ce,cold_status=cold_status,
                after_cold=snapshot(a.journal))

def reference(root):
    a=Sink(root,True);before=snapshot(a.journal)
    b=Sink(root,True);after_block=snapshot(a.journal)
    first=a.submit('first');ae=a.stop()
    fresh=Sink(root,True);fresh_exit=fresh.stop();after_fresh=snapshot(a.journal)
    recovered=Sink(root,True,'recover-ordered')
    try:
        restored=recovered.status();ready_journal=snapshot(recovered.journal);second=recovered.submit('second')
    finally:recovered_exit=recovered.stop()
    cold=Sink(root,True,'recover-ordered')
    try:final=cold.status();final_journal=snapshot(cold.journal)
    finally:cold_exit=cold.stop()
    return dict(A=ae,blocked_B=b.meta,journal_before=before,journal_after_block=after_block,first=first,
                fresh_refusal=fresh_exit,after_fresh=after_fresh,recovered=recovered_exit,restored=restored,
                recovered_ready_journal=ready_journal,second=second,cold=cold_exit,final=final,final_journal=final_journal)

def distinct(root):
    a=Sink(root/'A',True);b=Sink(root/'B',True)
    try:first=a.submit('root-A');second=b.submit('root-B')
    finally:ae=a.stop();be=b.stop()
    cold=[]
    for path in (root/'A',root/'B'):
        recovered=Sink(path,True,'recover-ordered')
        try:status=recovered.status();raw=snapshot(recovered.journal)
        finally:process=recovered.stop()
        cold.append(dict(process=process,status=status,journal=raw))
    return dict(A=ae,B=be,first=first,second=second,cold=cold)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    try:
        with tempfile.TemporaryDirectory(prefix='ases-sink-writer-') as directory:
            root=Path(directory)
            cases=dict(original_overlap=overlap(root/'original',False),guarded_restart=reference(root/'reference'),
                       nonparticipating_writer=overlap(root/'mixed',True),distinct_roots=distinct(root/'distinct'))
            print(json.dumps(dict(schema='ases.sink-writer-exclusion',version=1,
                                  execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                                  source_hashes={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,GUARDED,HERE/'probe.py')},
                                  environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                                  executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),
                                  cases=cases,children=[c.meta for c in OWNED]),indent=2,sort_keys=True))
    finally:
        for child in OWNED:
            if child.process.poll() is None:child.stop()
if __name__=='__main__':main()
