#!/usr/bin/env python3
"""Cold recovery refusal controls and a genuine nonpersistent-event sequence gap."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import post_replacement_send as post
import f4_gate_qualification as strict

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py'

def encode(rows):return b''.join((json.dumps(r,sort_keys=True)+'\n').encode() for r in rows)
def startup(root,raw,mode='recover-ordered'):
    root.mkdir();path=root/'journal.jsonl'
    if raw is not None:path.write_bytes(raw)
    p=subprocess.Popen([sys.executable,str(SOURCE),'--server',mode,str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:out,err=p.communicate(timeout=4)
    except subprocess.TimeoutExpired:
        p.kill();out,err=p.communicate(timeout=2)
        raise AssertionError('invalid recovery did not fail before readiness: '+out)
    assert p.returncode!=0 and not out.strip(), (out,err)
    return {'exit':p.returncode,'stdout':out,'stderr':err,'journal_exists':raw is not None,
            'journal_raw_hex':None if raw is None else raw.hex(),
            'journal_sha256':None if raw is None else hashlib.sha256(raw).hexdigest()}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    raw=json.loads((HERE/'fixed.raw.json').read_text())
    authority=bytes.fromhex(raw['cases']['authority']['journal_before']['raw_hex'])
    obligations=bytes.fromhex(raw['cases']['obligation']['journal_after']['raw_hex'])
    rows=[json.loads(l) for l in authority.splitlines()]
    wrong_version=copy.deepcopy(rows);next(r for r in wrong_version if r['event']=='authority_replaced')['previous_version']=9
    unknown=copy.deepcopy(rows);unknown[0]['event']='unknown-event'
    duplicate=copy.deepcopy(rows);duplicate[-1]['seq']=duplicate[0]['seq']
    exact=[json.loads(l) for l in obligations.splitlines()]
    wrong_hash=copy.deepcopy(exact);wrong_hash[0]['payload_sha256']='0'*64
    missing_q=[r for r in exact if r['event']!='obligation_committed']
    lines=authority.splitlines();lines[0]=lines[0][:-1]+b',"seq":1}'
    cases={'missing':None,'empty':b'','truncated':authority[:-5],'wrong_replacement':encode(wrong_version),
           'unknown_event':encode(unknown),'duplicate_sequence':encode(duplicate),'wrong_obligation_hash':encode(wrong_hash),
           'missing_obligation':encode(missing_q),'duplicate_json_key':b'\n'.join(lines)+b'\n'}
    with tempfile.TemporaryDirectory(prefix='ases-sink-recovery-controls-') as td:
        root=Path(td);out={n:startup(root/n,b) for n,b in cases.items()}
        out['implicit_fresh_existing']=startup(root/'implicit',authority,'sink-ordered')
        module=post.load(SOURCE,'gap_source');sink=module.RunningSink('sink-ordered',root/'gap')
        try:
            inputs=[('/submit',{'authority_version':1,'request_id':'gap-positive','payload':'live'}),
                    ('/submit',{'authority_version':0,'request_id':'gap-denied','payload':'stale'}),
                    ('/commit-obligation',{'authority_version':1,'obligation_id':'gap-q','payload':'exact'}),('/replace',{})]
            observations=[post.invoke(module,sink.port,path,b) for path,b in inputs]
            before=module.latest_status(sink);journal_before=strict.snapshot(sink.journal)
        finally:old_exit=sink.kill_and_reap()
        assert [s['response']['status'] for s in observations]==[201,409,201,200]
        new=module.RunningSink('recover-ordered',root/'gap')
        try:
            restored=module.latest_status(new)
            response=post.invoke(module,new.port,'/submit',{'authority_version':2,'request_id':'gap-after','payload':'new-current'})
            final=module.latest_status(new);journal_after=strict.snapshot(new.journal)
        finally:new_exit=new.kill_and_reap()
        persisted_before=[json.loads(l)['seq'] for l in bytes.fromhex(journal_before['raw_hex']).splitlines()]
        persisted_after=[json.loads(l)['seq'] for l in bytes.fromhex(journal_after['raw_hex']).splitlines()]
        assert persisted_before==[1,3,4] and persisted_after==[1,3,4,5]
        assert [e['seq'] for e in restored['events']]==[1,3,4] and restored['authority_version']==2
        assert response['response']['status']==201 and final['events'][-1]['seq']==5
        gap={'before_calls':observations,'before_status':before,'restored_status':restored,'after_call':response,
             'after_status':final,'journal_before':journal_before,'journal_after':journal_after,'exits':[old_exit,new_exit]}
    print(json.dumps({'schema':'ases.sink-recovery-controls.v1','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'refusals':out,'sequence_gap':gap},indent=2,sort_keys=True))
if __name__=='__main__':main()
