#!/usr/bin/env python3
"""File-only prefix recovery plus actual process-death publication cuts."""
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
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import post_replacement_send as post
import f4_gate_qualification as strict

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py';IO=HERE.parent/'io-failure'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def files(root):
    return {p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(root.iterdir()) if p.is_file()}
def cut(root,stage):
    er,ew=os.pipe();rr,rw=os.pipe()
    p=subprocess.Popen([sys.executable,str(SOURCE),'--server','recover-ordered-prefix',str(root/'sink-effects.jsonl'),
                        '--recovery-gate',stage,'--recovery-event-fd',str(ew),'--recovery-release-fd',str(rr)],
                       pass_fds=[ew,rr],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    os.close(ew);os.close(rr)
    try:
        assert select.select([er],[],[],4)[0] and os.read(er,1)==b'G', 'gate not reached'
        assert not select.select([p.stdout],[],[],0)[0], 'readiness before recovery gate'
        journal=strict.snapshot(root/'sink-effects.jsonl');manifest=files(root)
        p.kill();out,err=p.communicate(timeout=4)
        assert p.returncode==-9 and not out and not err
        return {'gate':stage,'pid':p.pid,'exit':p.returncode,'stdout':out,'stderr':err,'journal_at_gate':journal,'files_at_gate':manifest}
    finally:
        if p.poll() is None:p.kill();p.communicate(timeout=4)
        os.close(er);os.close(rw)

def recover(m,root,mode):
    sink=m.RunningSink(mode,root)
    try:
        status=m.latest_status(sink);journal=strict.snapshot(sink.journal)
    finally:code=sink.kill_and_reap()
    return {'status':status,'journal':journal,'sink_exit':code,'files':files(root)}
def history(m,root,raw,expected,stage):
    root.mkdir();path=root/'sink-effects.jsonl';path.write_bytes(raw)
    gate=cut(root,stage) if stage else None
    if gate:
        held=bytes.fromhex(gate['journal_at_gate']['raw_hex'])
        assert held==(raw if stage=='quarantined' else expected)
    sink=m.RunningSink('recover-ordered-prefix',root)
    try:
        restored=m.latest_status(sink);journal_restored=strict.snapshot(path)
        assert bytes.fromhex(journal_restored['raw_hex'])==expected
        assert [e['request_id'] for e in restored['effects']]==['ack-before']
        assert restored['authority_version']==1
        response=post.invoke(m,sink.port,'/submit',{'authority_version':1,'request_id':'post-prefix','payload':'continued-exact-π'})
        assert response['response']['status']==201
        after=m.latest_status(sink);journal_after=strict.snapshot(path)
        assert [e['request_id'] for e in after['effects']]==['ack-before','post-prefix']
    finally:exit1=sink.kill_and_reap()
    cold=recover(m,root,'recover-ordered')
    assert cold['status']['effects']==after['effects']
    quarantine=path.with_name(path.name+'.quarantine-'+sha(raw))
    assert quarantine.read_bytes()==raw
    assert sum(p.stat().st_size for p in root.iterdir() if p.is_file())<262144
    return {'gate':gate,'restored':restored,'journal_restored':journal_restored,'new_call':response,
            'after':after,'journal_after':journal_after,'first_exit':exit1,'cold':cold,
            'quarantine_sha256':sha(quarantine.read_bytes()),'quarantine_raw_hex':quarantine.read_bytes().hex()}

def refuse(root,raw,mode='recover-ordered-prefix',wrong_quarantine=False):
    root.mkdir();path=root/'sink-effects.jsonl';path.write_bytes(raw)
    if wrong_quarantine:path.with_name(path.name+'.quarantine-'+sha(raw)).write_bytes(b'wrong')
    before=files(root)
    p=subprocess.run([sys.executable,str(SOURCE),'--server',mode,str(path)],capture_output=True,text=True,timeout=4)
    assert p.returncode!=0 and not p.stdout and files(root)==before
    return {'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'raw_hex':raw.hex(),
            'sha256':sha(raw),'files_before':before,'files_after':files(root)}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    fixed=json.loads((IO/'fixed.raw.json').read_text());old=json.loads((IO/'baseline.raw.json').read_text())
    raw=bytes.fromhex(fixed['cases']['partial']['journal_after_fault']['raw_hex'])
    expected=bytes.fromhex(fixed['cases']['partial']['acknowledged_journal']['raw_hex'])
    assert raw.startswith(expected) and not raw.endswith(b'\n')
    m=post.load(SOURCE,'prefix_sink')
    with tempfile.TemporaryDirectory(prefix='ases-prefix-recovery-') as td:
        root=Path(td)
        histories={n:history(m,root/n,raw,expected,stage) for n,stage in
                   [('uninterrupted',None),('cut-quarantined','quarantined'),('cut-published','published')]}
        bad_bool=json.loads(expected);bad_bool['presented_version']=True
        bool_prefix=(json.dumps(bad_bool)+'\n').encode()+b'partial'
        controls={'later_ACK_behind_malformed_tail':bytes.fromhex(old['cases']['partial']['journal_after_later']['raw_hex']),
                  'duplicate_seq_after_sync_error':bytes.fromhex(old['cases']['sync']['journal_after_later']['raw_hex']),
                  'no_complete_prefix':b'{"seq":1','boolean_prefix':bool_prefix,
                  'malformed_complete_then_tail':expected+b'not-json\npartial'}
        refused={n:refuse(root/n,v) for n,v in controls.items()}
        refused['wrong_quarantine']=refuse(root/'wrong-quarantine',raw,wrong_quarantine=True)
        refused['strict_default_partial']=refuse(root/'strict-default',raw,'recover-ordered')
        healthy=bytes.fromhex(fixed['cases']['healthy']['journal_after_later']['raw_hex'])
        healthy_root=root/'complete-positive';healthy_root.mkdir();(healthy_root/'sink-effects.jsonl').write_bytes(healthy)
        complete=recover(m,healthy_root,'recover-ordered-prefix')
        assert len(complete['status']['effects'])==3 and complete['status']['recovery_info']['tail_bytes']==0
        assert len(complete['files'])==1
        # Outside selected relation: actual ACKed final record truncated.
        rows=healthy.splitlines(keepends=True);truncated_acked=b''.join(rows[:-1])+rows[-1][:len(rows[-1])//2]
        corrupt_root=root/'outside-acked-truncation';corrupt_root.mkdir();(corrupt_root/'sink-effects.jsonl').write_bytes(truncated_acked)
        outside=recover(m,corrupt_root,'recover-ordered-prefix')
        assert len(outside['status']['effects'])==2
        assert fixed['cases']['healthy']['later']['response']['status']==201
    print(json.dumps({'schema':'ases.prefix-recovery.v1',
                      'execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_hashes':{p.name:sha(p.read_bytes()) for p in [SOURCE,Path(__file__)]},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':sha(Path(sys.executable).read_bytes())},
                      'fault_fixture_original_hex':raw.hex(),'oracle_prior_ACK_prefix_hex':expected.hex(),
                      'histories':histories,'refusals':refused,'complete_positive':complete,
                      'outside_relation_ACKed_truncation':{'actual_prior_ACK':fixed['cases']['healthy']['later'],
                        'full_original_hex':healthy.hex(),'truncated_hex':truncated_acked.hex(),'recovery':outside,
                        'interpretation':'accepted2/3 prior ACKed records: file shape cannot establish interrupted-new-unACKed-tail premise'}},
                     indent=2,sort_keys=True))
if __name__=='__main__':main()
