#!/usr/bin/env python3
"""Actual partial bytes through a scoped short-return API shim."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import post_replacement_send as post
import f4_gate_qualification as strict

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'run.py'
BASE='589cee0'
PAYLOAD='short-write-effect-π\nimmutable'

def case(source,root,name,fault):
    log=root/'write-observations.jsonl';root.mkdir()
    needle='written = os.write(fd, payload[offset:])' if 'written = os.write' in source else 'os.write(fd, payload)'
    replacement='written = shim_write(fd, payload[offset:])' if needle.startswith('written') else 'shim_write(fd, payload)'
    assert source.count(needle)==1
    shim="""
def shim_write(fd, payload):
    requested = len(payload)
    result = 0 if FAULT_ZERO else os.write(fd, payload[:max(1, requested//2)])
    with open(TRACE_PATH, 'a') as trace:
        trace.write(json.dumps({'requested':requested,'returned':result})+'\\n')
    return result

""".replace('FAULT_ZERO',repr(fault=='zero')).replace('TRACE_PATH',repr(str(log)))
    mutated=source if fault=='normal' else source.replace(needle,replacement).replace('\n\nclass SinkState:',shim+'\nclass SinkState:')
    path=root/'sink.py';path.write_text(mutated)
    module=post.load(path,'sink_'+name)
    sink=module.RunningSink('f4',root/'case')
    try:
        try:
            code,body=module.call(sink.port,'POST','/effect',{'request_id':name,'payload':PAYLOAD,'cut':'normal'})
            client={'http_status':code,'body':body}
        except Exception as exc:client={'http_status':None,'error':type(exc).__name__+': '+str(exc)}
        snap=strict.snapshot(sink.journal)
        recovery=strict.reader(sink.journal)
    finally:
        sink.process.kill();stdout,stderr=sink.process.communicate(timeout=4)
    return {'client':client,'journal':snap,'fresh_reader':recovery,'sink_exit':sink.process.returncode,
            'sink_stdout':stdout,'sink_stderr':stderr,'source_sha256':hashlib.sha256(mutated.encode()).hexdigest(),
            'write_observations':[] if not log.exists() else [json.loads(l) for l in log.read_text().splitlines()]}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    phase=sys.argv[1]
    if phase=='baseline':
        source=subprocess.check_output(['git','show',BASE+':research/phase-i-t18-sink-order-20261103/run.py'],text=True)
        variants=[('normal','normal'),('short_return','short')]
    else:
        assert phase=='fixed';source=SOURCE.read_text();variants=[('short_return_fixed','short'),('zero_return_fixed','zero')]
    with tempfile.TemporaryDirectory(prefix='ases-round2-shortwrite-') as td:
        cases={n:case(source,Path(td)/n,n,f) for n,f in variants}
    if phase=='baseline':
        assert cases['normal']['client']['http_status']==201 and cases['normal']['fresh_reader']['observation']['state']=='VALID'
        assert cases['short_return']['client']['http_status']==201 and cases['short_return']['fresh_reader']['observation']['state']=='REFUSED'
    else:
        c=cases['short_return_fixed'];assert c['client']['http_status']==201 and c['fresh_reader']['observation']['state']=='VALID'
        assert c['fresh_reader']['observation']['effects'][0]['payload_hex']==PAYLOAD.encode().hex()
        assert len(c['write_observations'])>1
        z=cases['zero_return_fixed'];assert z['client']['http_status'] is None and z['fresh_reader']['observation']['state']=='EMPTY'
        assert len(z['write_observations'])==1
    assert all(c['sink_exit']==-9 for c in cases.values())
    print(json.dumps({'schema':'ases.f4-short-write.v1','phase':phase,'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'payload_hex':PAYLOAD.encode().hex(),'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                                                       'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':main()
