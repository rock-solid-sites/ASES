#!/usr/bin/env python3
"""Scoped storage error injection; actual appended bytes remain observable."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import select
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import post_replacement_send as post
import f4_gate_qualification as strict

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py'

def call(m,s,request_id):
    body={'authority_version':1,'request_id':request_id,'payload':'journal-'+request_id+'-π'}
    try:return post.invoke(m,s.port,'/submit',body)
    except Exception as exc:return {'request':body,'response':None,'error':type(exc).__name__+': '+str(exc)}
def cold(m,path):
    p=subprocess.Popen([sys.executable,str(SOURCE),'--server','recover-ordered',str(path)],
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        assert select.select([p.stdout],[],[],4)[0], 'cold start timeout'
        line=p.stdout.readline()
        if not line:
            out,err=p.communicate(timeout=4)
            assert p.returncode!=0
            return {'ready':False,'exit':p.returncode,'stdout':out,'stderr':err}
        ready=json.loads(line)
        code,status=m.call(ready['port'],'GET','/status')
        assert code==200
        return {'ready':True,'readiness':ready,'status':status}
    finally:
        if p.poll() is None:p.kill();p.communicate(timeout=4)

def case(source,root,mode):
    root.mkdir();trace=root/'io.jsonl'
    shim="""
_IO_FAULT = False
_SYNC_PENDING = False
def _io_trace(**data):
    with open(TRACE, 'a') as f: f.write(json.dumps(data)+'\\n')
def _io_write(fd, payload):
    global _IO_FAULT, _SYNC_PENDING
    target = b'"request_id": "fault-once"' in payload
    if target and not _IO_FAULT and MODE == 'partial':
        count = os.write(fd, payload[:len(payload)//2])
        _IO_FAULT = True
        _io_trace(stage='partial_write_then_exception', requested=len(payload), returned=count)
        raise OSError(5, 'injected exception after partial append')
    count = os.write(fd, payload)
    if target and not _IO_FAULT and MODE == 'sync': _SYNC_PENDING = True
    _io_trace(stage='write_returned', requested=len(payload), returned=count)
    return count
def _io_sync(fd):
    global _IO_FAULT, _SYNC_PENDING
    if _SYNC_PENDING and not _IO_FAULT:
        _SYNC_PENDING = False
        _IO_FAULT = True
        _io_trace(stage='injected_sync_exception')
        raise OSError(5, 'injected sync API exception')
    os.fsync(fd)
    _io_trace(stage='sync_returned')

""".replace('TRACE',repr(str(trace))).replace('MODE',repr(mode))
    assert source.count('written = os.write(fd, payload[offset:])')==1
    assert source.count('os.fsync(fd)')==1
    text=source.replace('written = os.write(fd, payload[offset:])','written = _io_write(fd, payload[offset:])')
    text=text.replace('os.fsync(fd)','_io_sync(fd)').replace('\n\nclass SinkState:',shim+'\nclass SinkState:')
    path=root/'shim_sink.py';path.write_text(text)
    m=post.load(path,'io_shim_'+mode);s=m.RunningSink('sink-ordered',root/'state')
    try:
        first=call(m,s,'ack-before');assert first['response']['status']==201
        acknowledged=strict.snapshot(s.journal)
        fault=call(m,s,'fault-once');status_fault=m.latest_status(s);journal_fault=strict.snapshot(s.journal)
        later=call(m,s,'after-failure');status_later=m.latest_status(s);journal_later=strict.snapshot(s.journal)
        if mode=='healthy':assert fault['response']['status']==later['response']['status']==201
        else:assert fault['response'] is None
    finally:
        s.process.kill();out,err=s.process.communicate(timeout=4)
    recovered=cold(m,s.journal)
    if mode=='healthy':assert len(recovered['status']['effects'])==3
    return {'first':first,'acknowledged_journal':acknowledged,'fault':fault,'status_after_fault':status_fault,
            'journal_after_fault':journal_fault,'later':later,'status_after_later':status_later,
            'journal_after_later':journal_later,'sink_exit':s.process.returncode,'sink_stdout':out,'sink_stderr':err,
            'cold':recovered,'io_trace':[json.loads(l) for l in trace.read_text().splitlines()],
            'shim_source_sha256':hashlib.sha256(text.encode()).hexdigest()}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    phase=sys.argv[1];assert phase in ['baseline','fixed']
    source=SOURCE.read_text()
    with tempfile.TemporaryDirectory(prefix='ases-sink-io-') as td:
        cases={n:case(source,Path(td)/n,n) for n in ['healthy','partial','sync']}
    if phase=='baseline':
        assert cases['partial']['later']['response']['status']==201
        assert cases['sync']['later']['response']['status']==201
        assert not cases['partial']['cold']['ready']
        assert not cases['sync']['cold']['ready']
        assert 'invalid durable sequence' in cases['sync']['cold']['stderr']
    else:
        assert cases['partial']['later']['response'] is cases['sync']['later']['response'] is None
        assert cases['partial']['status_after_fault']['persistence_failed']
        assert cases['sync']['status_after_fault']['persistence_failed']
        assert cases['partial']['journal_after_fault']==cases['partial']['journal_after_later']
        assert len(cases['sync']['cold']['status']['effects'])==2
    print(json.dumps({'schema':'ases.sink-io-failure.v1','phase':phase,
                      'execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,Path(__file__)]},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                      'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':main()
