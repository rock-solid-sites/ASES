#!/usr/bin/env python3
"""Authentic journal substitution; logical-root labels exist only in fixture oracle."""
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

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py'

def bootstrap(module,root,payload):
    sink=module.RunningSink('sink-ordered',root)
    try:
        calls=[post.invoke(module,sink.port,'/commit-obligation',{'authority_version':1,'obligation_id':'q','payload':payload}),
               post.invoke(module,sink.port,'/replace',{})]
        assert [s['response']['status'] for s in calls]==[201,200]
        journal=strict.snapshot(sink.journal);status=module.latest_status(sink)
    finally:code=sink.kill_and_reap()
    return {'calls':calls,'journal':journal,'status':status,'sink_exit':code}

def deliver(module,root):
    sink=module.RunningSink('recover-ordered',root)
    try:
        initial=module.latest_status(sink)
        call=post.invoke(module,sink.port,'/deliver-obligation',{'obligation_id':'q'})
        status=module.latest_status(sink);journal=strict.snapshot(sink.journal)
    finally:code=sink.kill_and_reap()
    assert call['response']['status']==201
    return {'initial_status':initial,'delivery':call,'final_status':status,'journal':journal,'sink_exit':code}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    module=post.load(SOURCE,'affinity_sink')
    with tempfile.TemporaryDirectory(prefix='ases-sink-root-') as td:
        root=Path(td);a=root/'A';b=root/'B'
        alpha='logical-root-A-exact-π';beta='logical-root-B-exact-β'
        A=bootstrap(module,a,alpha);B=bootstrap(module,b,beta)
        assert A['journal']['sha256']!=B['journal']['sha256']
        correct=deliver(module,a)
        assert correct['final_status']['effects'][-1]['payload']==alpha
        before_swap=strict.snapshot(a/'sink-effects.jsonl')
        authentic_b=bytes.fromhex(B['journal']['raw_hex'])
        (a/'sink-effects.jsonl').write_bytes(authentic_b)
        after_swap=strict.snapshot(a/'sink-effects.jsonl')
        assert after_swap==B['journal']
        swapped=deliver(module,a)
        effect=swapped['final_status']['effects'][-1]
        assert effect['payload']==beta and effect['payload']!=alpha and effect['obligation_id']=='q'
        assert hashlib.sha256(effect['payload'].encode()).hexdigest()==effect['payload_sha256']
        assert all(x['sink_exit']==-9 for x in [A,B,correct,swapped])
        result={'schema':'ases.sink-root-affinity.v1','execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,Path(__file__)]},
                'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                               'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                'fixture_expected_A_payload_hex':alpha.encode().hex(),'A':A,'B':B,'correct_A_recovery':correct,
                'A_before_swap':before_swap,'A_after_swap_authentic_B_bytes':after_swap,'swapped_A_recovery':swapped,
                'interpretation':'Valid replay and payload digest accept authentic B journal at A path; expected root remains a trusted external/custody premise'}
        print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
