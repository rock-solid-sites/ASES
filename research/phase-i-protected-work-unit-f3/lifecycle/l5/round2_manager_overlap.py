#!/usr/bin/env python3
"""Falsify extending serialized L5 check/publish to overlapping managers."""
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import select
import subprocess
import sys
import tempfile
import time
import l5_integrated as l5
import test_post_move_grant as fixture

HERE=Path(__file__).resolve().parent

def emit(**kw):print(json.dumps({'pid':os.getpid(),'ns':time.monotonic_ns(),**kw}),flush=True)
def request(op):
    return {'op':'authorize_move','child':'C','destination':'Q'} if op=='move' else {'op':'authorize_activate'}
def worker(root,op):
    name,st=l5.load_current(root)
    original=l5.commit
    def gate(root,state,event):
        emit(stage='commit_entry_after_manager_checks',base_record=name,event=event)
        assert sys.stdin.buffer.readline()==b'publish\n'
        return original(root,state,event)
    l5.commit=gate
    req,reply=fixture.request(l5,root,st,**request(op))
    emit(stage='reply',request=req,response=reply)

def recv(p):
    assert select.select([p.stdout],[],[],4)[0], 'worker event timeout'
    return json.loads(p.stdout.readline())
def files(root):return fixture.files(root)
def overlap(root):
    st,meta=fixture.setup(root);procs=[]
    initial=copy.deepcopy(st)
    try:
        for op in ['move','activate']:
            procs.append(subprocess.Popen([sys.executable,__file__,'--worker',str(root),op],stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0))
        gates=[recv(p) for p in procs]
        assert all(g['stage']=='commit_entry_after_manager_checks' for g in gates)
        assert len({g['base_record'] for g in gates})==1
        replies=[]
        for p in procs:
            p.stdin.write(b'publish\n');p.stdin.flush()
            replies.append(recv(p));p.wait(timeout=4)
        errors=[p.stderr.read().decode() for p in procs]
        assert [p.returncode for p in procs]==[0,0] and errors==['','']
        records={p.name:json.loads(p.read_text()) for p in sorted((root/'protected').glob('record-*.json'))}
        name,final=l5.load_current(root)
        assert all(r['response']['result']=='COMMITTED' for r in replies)
        moved=records[replies[0]['response']['record']]
        assert moved['work_units']['C']['parent']=='Q'
        assert final['work_units']['C']['parent']=='P' and final['work_units']['C']['active']
        assert not any(e.get('op')=='authorized_sealed_whole_move' for e in final['events'])
        assert any(e.get('op')=='separately-authorized_activation' for e in final['events'])
        assert l5.verified_content(root,meta)==fixture.X
        return {'initial':initial,'gates':gates,'replies':replies,'exits':[p.returncode for p in procs],
                'stderr':errors,'records':records,'selected_record':name,'final':final,'files':files(root),
                'accepted_bytes_hex':fixture.X.hex(),'interpretation':'two acknowledged operations; selected state loses prior move'}
    finally:
        for p in procs:
            if p.poll() is None:p.kill();p.wait(timeout=4)
            for f in [p.stdin,p.stdout,p.stderr]:f.close()

def serial(root,fresh):
    st,meta=fixture.setup(root);old=copy.deepcopy(st)
    _,move=fixture.request(l5,root,st,**request('move'))
    if fresh:_,candidate=l5.load_current(root)
    else:candidate=old
    before=files(root)
    req,reply=fixture.request(l5,root,candidate,**request('activate'))
    after=files(root);name,final=l5.load_current(root)
    assert move['result']=='COMMITTED' and final['work_units']['C']['parent']=='Q'
    assert l5.verified_content(root,meta)==fixture.X
    if fresh:
        assert reply['result']=='COMMITTED' and final['work_units']['C']['active']
        assert any(e.get('op')=='authorized_sealed_whole_move' for e in final['events'])
    else:
        assert reply=={'result':'DENY','reason':'management-state-not-current'} and before==after
    return {'move':move,'activation_request':req,'activation_reply':reply,'files_before':before,'files_after':after,
            'selected_record':name,'final':final}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    if len(sys.argv)>1:worker(Path(sys.argv[2]),sys.argv[3]);return
    with tempfile.TemporaryDirectory(prefix='ases-round2-manager-') as td:
        root=Path(td);results={}
        for n in ['overlap','serial_stale','serial_fresh']:
            path=root/n;path.mkdir()
            results[n]=overlap(path) if n=='overlap' else serial(path,n=='serial_fresh')
        assert sum(p.stat().st_size for p in root.rglob('*') if p.is_file())<1_048_576
    print(json.dumps({'schema':'ases.f3-manager-overlap.v1','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'l5_integrated.py',HERE/'test_post_move_grant.py',HERE/'test_management_conformance.py']},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},'cases':results},indent=2,sort_keys=True))
if __name__=='__main__':main()
