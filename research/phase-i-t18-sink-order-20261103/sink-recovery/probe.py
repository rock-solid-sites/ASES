#!/usr/bin/env python3
"""Actual kill/restart of serving sink, separate from journal-only decoding."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import subprocess
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import post_replacement_send as post
import f4_gate_qualification as strict

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'run.py'

def call(module,sink,path,body):
    r=post.invoke(module,sink.port,path,body);r['status']=module.latest_status(sink);return r

def case(module,root,kind,restart_mode):
    sink=module.RunningSink('sink-ordered',root);before=[]
    try:
        if kind=='authority':
            before.append(call(module,sink,'/submit',{'request_id':'before-v1','authority_version':1,'payload':'before'}))
        else:
            before.append(call(module,sink,'/commit-obligation',{'obligation_id':'q','authority_version':1,'payload':'retained-exact-π'}))
        before.append(call(module,sink,'/replace',{}))
        if kind=='authority':
            before.append(call(module,sink,'/submit',{'request_id':'before-v2','authority_version':2,'payload':'current'}))
        journal_before=strict.snapshot(sink.journal)
        status_before=module.latest_status(sink)
    finally:first_exit=sink.kill_and_reap()
    restarted=module.RunningSink(restart_mode,root)
    try:
        restored_status=module.latest_status(restarted)
        restored_journal=strict.snapshot(restarted.journal)
        assert journal_before==restored_journal
        after=[]
        if kind=='authority':
            after.append(call(module,restarted,'/submit',{'request_id':'after-stale','authority_version':1,'payload':'stale-after-restart'}))
            after.append(call(module,restarted,'/submit',{'request_id':'after-current','authority_version':2,'payload':'current-after-restart'}))
        else:after.append(call(module,restarted,'/deliver-obligation',{'obligation_id':'q'}))
        journal_after=strict.snapshot(restarted.journal)
    finally:second_exit=restarted.kill_and_reap()
    return {'before':before,'status_before':status_before,'journal_before':journal_before,'first_exit':first_exit,
            'restored_status':restored_status,'restored_journal_before_requests':restored_journal,
            'after':after,'journal_after':journal_after,'second_exit':second_exit}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    phase=sys.argv[1]
    assert phase in ['baseline','fixed']
    mode='sink-ordered' if phase=='baseline' else 'recover-ordered'
    module=post.load(SOURCE,'sink_recovery_probe')
    with tempfile.TemporaryDirectory(prefix='ases-serving-recovery-') as td:
        cases={k:case(module,Path(td)/k,k,mode) for k in ['authority','obligation']}
    a=cases['authority'];o=cases['obligation']
    assert [s['response']['status'] for s in a['before']]==[201,200,201]
    assert [s['response']['status'] for s in o['before']]==[201,200]
    assert all(c['first_exit']==c['second_exit']==-9 for c in cases.values())
    if phase=='baseline':
        assert a['restored_status']['authority_version']==o['restored_status']['authority_version']==1
        assert [s['response']['status'] for s in a['after']]==[201,409]
        assert o['after'][0]['response']['status']==409
    else:
        assert a['restored_status']['authority_version']==o['restored_status']['authority_version']==2
        assert [s['response']['status'] for s in a['after']]==[409,201]
        assert o['after'][0]['response']['status']==201
        event=o['after'][0]['status']['effects'][-1]
        assert event['obligation_id']=='q' and event['payload']=='retained-exact-π'
        assert event['payload_sha256']==hashlib.sha256(event['payload'].encode()).hexdigest()
    print(json.dumps({'schema':'ases.serving-sink-recovery.v1','phase':phase,
                      'execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'base_semantics':'HEAD at invocation; source hashes identify actual executed bytes',
                      'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,Path(__file__)]},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':main()
