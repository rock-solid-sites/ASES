#!/usr/bin/env python3
"""Actual original replace cuts and fresh current-selector reconstruction."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import select
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import worker
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import test_post_move_grant as fixture
HERE=Path(__file__).resolve().parent;LIFE=HERE.parent.parent;SOURCE=HERE/'worker.py';PAYLOAD='actual selected D write / μ'
class Child:
    def __init__(self,root,phase='none'):
        self.data=dict(start_ns=time.monotonic_ns(),phase=phase,events=[])
        self.process=subprocess.Popen([sys.executable,str(SOURCE),str(root),phase],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.data['pid']=self.process.pid
        try:self.ready=self.read();self.data['ready_ns']=time.monotonic_ns()
        except BaseException:self.process.kill();self.process.communicate(timeout=3);raise
    def read(self):
        if not select.select([self.process.stdout],[],[],3)[0]:raise TimeoutError('move frame timeout')
        raw=self.process.stdout.readline()
        if not raw:raise RuntimeError('move worker closed: '+self.process.stderr.read())
        event=dict(raw_line=raw,frame=json.loads(raw),received_ns=time.monotonic_ns());self.data['events'].append(event);return event
    def ask(self,op,**fields):
        begin=time.monotonic_ns();self.process.stdin.write(json.dumps(dict(op=op,**fields))+'\n');self.process.stdin.flush()
        value=self.read();value['request_started_ns']=begin;return value
    def close(self,kill=False):
        if self.process.poll() is None:
            if kill:self.process.kill()
            else:self.process.stdin.write('{"op":"stop"}\n');self.process.stdin.flush()
        self.data.update(exit=self.process.wait(timeout=3),exit_ns=time.monotonic_ns())
        self.data.update(stdout_remainder=self.process.stdout.read(),stdout_eof_ns=time.monotonic_ns(),stderr=self.process.stderr.read())
        self.process.stdin.close();self.process.stdout.close();self.process.stderr.close();return self.data
def one(root,kind):
    root.mkdir();st,meta=fixture.setup(root)
    if kind=='write-positive':st['work_units']['P']['grants']=['read','write'];fixture.fixture.publish(root,st)
    before=worker.observe(root);original=Child(root,kind);extra={}
    try:
        if kind!='write-positive':extra['move_observation']=original.ask('split_mutant' if kind=='split-mutant' else 'move')
    finally:first=original.close(kind in ('before_record','after_record','after_selector','split-mutant'))
    after=worker.observe(root);cold=Child(root)
    try:
        ready=cold.ready;activation=cold.ask('activate');write=cold.ask('write',payload=PAYLOAD)
    finally:fresh=cold.close()
    return dict(kind=kind,before=before,after_process=after,cold_ready=ready,activation=activation,write=write,final=worker.observe(root),children=[first,fresh],**extra)
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2);root=Path(tempfile.mkdtemp(prefix='ases-l5-move-cuts-'))
    files=[SOURCE,Path(__file__),HERE/'check.py',HERE.parent/'l5_integrated.py',HERE.parent/'test_post_move_grant.py',HERE.parent/'test_management_conformance.py',LIFE/'l1/l1.py']
    data=dict(schema='ases.l5.actual-move-cuts',version=1,execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
              source_hashes={str(p.relative_to(LIFE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),start_ns=time.monotonic_ns(),cases={})
    try:
        for kind in ('before_record','after_record','after_selector','uninterrupted','split-mutant','write-positive'):data['cases'][kind]=one(root/kind,kind)
    except BaseException:
        data.update(harness_failure=traceback.format_exc(),retained_disposable_root=str(root),end_ns=time.monotonic_ns());print(json.dumps(data,indent=2,sort_keys=True));raise
    else:data['end_ns']=time.monotonic_ns();print(json.dumps(data,indent=2,sort_keys=True));shutil.rmtree(root)
if __name__=='__main__':main()
