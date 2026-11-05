#!/usr/bin/env python3
"""Five actual single-lane holder histories; no observation oracle in recovery."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import select
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import c11_service as service

sys.path.insert(0,str(service.HERE.parents[1]/'kernel-0'))
import kernel0_recovery_check as inherited
import kernel0_finite_model as model

HERE=Path(__file__).resolve().parent;SOURCE=HERE/'c11_service.py'
WORLDS={name:dict(identity_genesis='genesis-'+name,created_by='creator-'+name,project='project-'+name,
                  consumer_evidence='accepted evidence '+name+' / μ') for name in ('A','B')}

class Holder:
    def __init__(self,path,label,mode='atomic',observations=None,context=0,stage=None):
        self.client,server=socket.socketpair();self.client.settimeout(3)
        self.event,event_write=os.pipe();release_read,self.release=os.pipe()
        config=dict(path=str(path),root='work',profile='independent',channels=[[context,server.fileno()]],
                    observation_mode=mode,trace=str(path.parent/(label+'.trace.jsonl')))
        if observations is not None:config['observations']=observations
        fds=[server.fileno()]
        if stage:
            config['gate']=dict(lane=0,kind='accept',stage=stage,event_fd=event_write,release_fd=release_read)
            fds += [event_write,release_read]
        self.meta=dict(start_ns=time.monotonic_ns(),config=config)
        self.process=subprocess.Popen([sys.executable,str(SOURCE),json.dumps(config)],pass_fds=fds,
                                      stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        server.close();os.close(event_write);os.close(release_read)
        assert select.select([self.process.stdout],[],[],3)[0],'holder startup timeout'
        assert self.process.stdout.readline()==b'ready\n','holder startup failure'
        self.meta.update(pid=self.process.pid,ready_ns=time.monotonic_ns())
    def call(self,request):
        result=dict(request=request,start_ns=time.monotonic_ns())
        try:
            self.client.sendall(inherited.packet(request));result['response']=inherited.receive(self.client)
        except (EOFError,ConnectionResetError,BrokenPipeError,TimeoutError) as error:
            result.update(response=None,error=type(error).__name__)
        result['end_ns']=time.monotonic_ns();return result
    def gated(self):
        assert select.select([self.event],[],[],3)[0],'required inherited gate absent'
        assert os.read(self.event,1)==b'G'
        return dict(stage=self.meta['config']['gate']['stage'],pid=self.process.pid,observed_ns=time.monotonic_ns(),raw_hex='47')
    def close(self,close_client=True):
        self.process.kill();self.meta['exit']=self.process.wait(timeout=3);self.meta['exit_ns']=time.monotonic_ns()
        self.meta['stderr']=self.process.stderr.read().decode()
        self.process.stdout.close();self.process.stderr.close()
        if close_client:self.client.close()
        os.close(self.event);os.close(self.release)
        return self.meta

def files(root):
    return {p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in root.iterdir() if p.is_file()}

def independent(path):
    start=time.monotonic_ns()
    child=subprocess.Popen([sys.executable,str(SOURCE),'--reader',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    out,err=child.communicate(timeout=4)
    return dict(start_ns=start,exit_ns=time.monotonic_ns(),pid=child.pid,exit=child.returncode,stderr=err,observation=json.loads(out))

def one(root,name,world,mode,stage):
    root.mkdir();path=root/'store.sqlite'
    service.persistent.initialize(str(path),'work','independent')
    with sqlite3.connect(path,isolation_level=None) as db:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)')
    bootstrap=Holder(path,'bootstrap',context=-1)
    try:
        setup=[bootstrap.call(inherited.wire(q)) for q in (model.Request('establish'),model.Request('grant',target=0,value=7))]
    finally:bootstrap_exit=bootstrap.close()
    writer=Holder(path,'writer',mode,WORLDS[world],stage=stage)
    request=inherited.wire(model.Request('accept',0,value=0))
    if stage:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future=executor.submit(writer.call,request)
            try:gate=writer.gated()
            finally:writer_exit=writer.close(close_client=False)
            try:accept=future.result(timeout=4)
            finally:writer.client.close()
    else:
        accept=writer.call(request);gate=None;writer_exit=writer.close()
    at_loss=files(root)
    recovered=Holder(path,'recovered')  # No original observations supplied.
    try:query=recovered.call(dict(kind='read'))
    finally:recovered_exit=recovered.close()
    raw=independent(path)
    trace=root/'writer.trace.jsonl'
    return dict(name=name,world=world,mode=mode,stage=stage,declared_original_observations=WORLDS[world],
                bootstrap=dict(process=bootstrap_exit,calls=setup),writer=writer_exit,accept=accept,gate=gate,
                files_at_loss=at_loss,recovered=recovered_exit,recovered_query=query,independent_reader=raw,
                writer_trace=[json.loads(line) for line in trace.read_text().splitlines()],final_files=files(root))

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    selected=[('atomic-A','A','atomic','durable'),('atomic-B','B','atomic','durable'),
              ('split-gap','A','split','durable'),('atomic-before','A','atomic','prepared'),('split-ack','A','split',None)]
    with tempfile.TemporaryDirectory(prefix='ases-c11-sqlite-') as directory:
        root=Path(directory);cases={name:one(root/name,name,world,mode,stage) for name,world,mode,stage in selected}
        sources=[SOURCE,HERE/'probe.py',service.HERE.parents[1]/'kernel-0/kernel0_recovery_service.py',
                 service.HERE.parents[1]/'kernel-0/kernel0_service.py',service.HERE.parents[1]/'kernel-0/kernel0_recovery_check.py',
                 service.HERE.parents[1]/'kernel-0/kernel0_finite_model.py']
        base=HERE.parents[1]
        print(json.dumps(dict(schema='ases.f1-c11-sqlite-history',version=1,
                              execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                              environment=dict(platform=platform.platform(),python=sys.version,sqlite=sqlite3.sqlite_version,
                                               executable=sys.executable,executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                                               address_space_bytes=256*1024*1024),
                              source_hashes={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},cases=cases),indent=2,sort_keys=True))

if __name__=='__main__':main()
