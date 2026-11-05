#!/usr/bin/env python3
"""Actual creator/remover overlap; EOF metadata retained for every process."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
spec=importlib.util.spec_from_file_location('inventory_race_probe_support',HERE.parent/'probe.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.SOURCE=HERE/'race_store.py';Z='new candidate during removal scan / μ'
class Child(p.Child):
    def resume(self,gate):
        self.process.stdin.write('continue\n');self.process.stdin.flush();event=self.read();event['request_started_ns']=gate['request_started_ns'];return event
    def close(self,kill=False):
        if self.process.poll() is None:
            if kill:self.process.kill()
            else:self.process.stdin.write('{"op":"stop"}\n');self.process.stdin.flush()
        code=self.process.wait(timeout=3);wait_ns=time.monotonic_ns()
        remainder=self.process.stdout.read();eof_ns=time.monotonic_ns();stderr=self.process.stderr.read()
        self.meta.update(exit=code,exit_ns=wait_ns,stdout_remainder=remainder,stdout_eof_ns=eof_ns,stderr=stderr,events=self.events)
        self.process.stdin.close();self.process.stdout.close();self.process.stderr.close();return self.meta
def attempt(root):
    start=time.monotonic_ns();child=subprocess.Popen([sys.executable,str(p.SOURCE),str(root)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    out,err=child.communicate(timeout=3)
    return dict(start_ns=start,pid=child.pid,exit_ns=time.monotonic_ns(),exit=child.returncode,stdout=out,stderr=err,frame=json.loads(out),snapshot=p.store.snapshot(root))
def one(root,kind):
    p.store.bootstrap(root);remover=Child(root);creator=Child(root);extra={};children=[]
    try:
        if kind=='creator-first':
            extra['creator_ack']=creator.ask(op='put',name='z',kind='candidate',payload=Z)
            extra['removal']=remover.ask(op='remove')
            extra['read']=remover.ask(op='read',name='z')
        else:
            extra['gate']=remover.ask(op='remove',profile='detached-scan' if kind=='detached' else 'directory-inventory',gate='scan')
            extra['creator_attempt']=creator.ask(op='put',name='z',kind='candidate',payload=Z)
            extra['at_overlap']=p.store.snapshot(root)
            extra['removal']=remover.resume(extra['gate'])
            if kind=='guarded':extra['later_creator']=creator.ask(op='put',name='z',kind='candidate',payload=Z)
        extra['final_before_exit']=p.store.snapshot(root)
    finally:
        children.append(remover.close());children.append(creator.close())
    if kind=='detached':extra['cold_refusal']=attempt(root);children.append(extra['cold_refusal'])
    if kind=='guarded':extra['cold']=Child(root).close();children.append(extra['cold'])
    return dict(kind=kind,children=children,**extra)
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2);root=Path(tempfile.mkdtemp(prefix='ases-l6-race-'))
    paths=[HERE/'race_store.py',Path(__file__),HERE/'check.py',HERE.parent/'store.py',HERE.parent/'probe.py']
    data=dict(schema='ases.l6.inventory-phantom',version=1,execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
              source_hashes={str(path.relative_to(HERE.parent)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
              environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),start_ns=time.monotonic_ns(),cases={})
    try:
        for kind in ('guarded','detached','creator-first'):data['cases'][kind]=one(root/kind,kind)
    except BaseException:
        data.update(harness_failure=traceback.format_exc(),retained_disposable_root=str(root),end_ns=time.monotonic_ns());print(json.dumps(data,indent=2,sort_keys=True));raise
    else:data['end_ns']=time.monotonic_ns();print(json.dumps(data,indent=2,sort_keys=True));shutil.rmtree(root)
if __name__=='__main__':main()
