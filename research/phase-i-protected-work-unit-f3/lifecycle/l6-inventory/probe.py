#!/usr/bin/env python3
"""Actual unregistered preparation and interrupted logical disposition."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import select
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback
import store

HERE=Path(__file__).resolve().parent;SOURCE=HERE/'store.py'
X='accepted x with retained identity / μ';Z='unaccepted durable candidate z / μ'
class Child:
    def __init__(self,root):
        self.meta=dict(start_ns=time.monotonic_ns());self.events=[]
        self.process=subprocess.Popen([sys.executable,str(SOURCE),str(root)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.meta['pid']=self.process.pid
        try:self.ready=self.read();self.meta['ready_ns']=time.monotonic_ns()
        except BaseException:
            self.process.kill();self.process.communicate(timeout=3);raise
    def read(self):
        if not select.select([self.process.stdout],[],[],3)[0]:raise TimeoutError('store frame timeout')
        line=self.process.stdout.readline()
        if not line:raise RuntimeError('store closed without frame: '+self.process.stderr.read())
        event=dict(received_ns=time.monotonic_ns(),raw_line=line,frame=json.loads(line));self.events.append(event);return event
    def ask(self,**q):
        start=time.monotonic_ns();self.process.stdin.write(json.dumps(q)+'\n');self.process.stdin.flush();event=self.read();event['request_started_ns']=start;return event
    def close(self,kill=False):
        if self.process.poll() is None:
            if kill:self.process.kill()
            else:self.process.stdin.write('{"op":"stop"}\n');self.process.stdin.flush()
        self.meta.update(exit=self.process.wait(timeout=3),exit_ns=time.monotonic_ns(),stderr=self.process.stderr.read(),events=self.events)
        self.process.stdin.close();self.process.stdout.close();self.process.stderr.close();return self.meta
def orphan(root,weak):
    store.bootstrap(root);writer=Child(root)
    try:
        gate=writer.ask(op='put',name='z',kind='candidate',payload=Z,gate='precommit');before_kill=store.snapshot(root)
    finally:killed=writer.close(True)
    after_kill=store.snapshot(root);recovered=Child(root)
    try:removal=recovered.ask(op='remove',profile='catalog-only' if weak else 'directory-inventory')
    finally:cold=recovered.close()
    return dict(weak=weak,gate=gate,before_kill=before_kill,after_kill=after_kill,removal=removal,final=store.snapshot(root),children=[killed,cold])
def disposition(root):
    store.bootstrap(root);writer=Child(root);steps=[]
    try:
        steps.append(writer.ask(op='put',name='x',kind='accepted',payload=X));steps.append(writer.ask(op='put',name='z',kind='candidate',payload=Z))
        steps.append(writer.ask(op='read',name='x'))
    finally:original=writer.close()
    before=store.snapshot(root);disposer=Child(root)
    try:gate=disposer.ask(op='dispose',name='x',gate='postcommit')
    finally:killed=disposer.close(True)
    after_kill=store.snapshot(root);fresh=Child(root)
    try:
        ready=fresh.ready;steps_after=[]
        for q in [dict(op='read',name='x'),dict(op='read',name='z'),dict(op='remove'),dict(op='cleanup',name='x'),
                  dict(op='remove'),dict(op='dispose',name='z'),dict(op='remove')]:steps_after.append(fresh.ask(**q))
    finally:recovered=fresh.close()
    return dict(original_steps=steps,before=before,gate=gate,after_kill=after_kill,recovered_ready=ready,
                recovered_steps=steps_after,final=store.snapshot(root),children=[original,killed,recovered])
def empty(root):
    store.bootstrap(root);child=Child(root)
    try:removal=child.ask(op='remove')
    finally:process=child.close()
    return dict(removal=removal,final=store.snapshot(root),children=[process])
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2);start=time.monotonic_ns()
    root=Path(tempfile.mkdtemp(prefix='ases-l6-inventory-'))
    data=dict(schema='ases.l6.durable-inventory',version=1,execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
              source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,Path(__file__),HERE/'check.py']},
              environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,executable=sys.executable,
              executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),address_space_bytes=256*1024*1024),start_ns=start,cases={})
    try:
        for name,run in [('orphan_reference',lambda:orphan(root/'orphan-reference',False)),('orphan_catalog_mutant',lambda:orphan(root/'orphan-mutant',True)),
                         ('interrupted_disposition',lambda:disposition(root/'disposition')),('empty_positive',lambda:empty(root/'empty'))]:data['cases'][name]=run()
    except BaseException:
        data.update(harness_failure=traceback.format_exc(),retained_disposable_root=str(root),end_ns=time.monotonic_ns())
        print(json.dumps(data,indent=2,sort_keys=True));raise
    else:
        data['end_ns']=time.monotonic_ns();print(json.dumps(data,indent=2,sort_keys=True));shutil.rmtree(root)
if __name__=='__main__':main()
