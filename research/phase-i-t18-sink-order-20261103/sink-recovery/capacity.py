#!/usr/bin/env python3
"""Real ACKed journal growth and corresponding bounded-admission controls."""
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

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py';CAP=65536

def invoke(m,s,path,body):
    try:return post.invoke(m,s.port,path,body)
    except Exception as exc:return {'request':{'path':path,'body':body},'response':None,'error':type(exc).__name__+': '+str(exc)}
def fill(m,s):
    calls=[]
    for i in range(10):
        r=invoke(m,s,'/submit',{'authority_version':1,'request_id':'grow-'+str(i),'payload':'x'*7168})
        calls.append(r)
        if r['response'] is None or s.journal.stat().st_size>CAP:break
    return calls
def failed_recovery(path):
    p=subprocess.run([sys.executable,str(SOURCE),'--server','recover-ordered',str(path)],
                     capture_output=True,text=True,timeout=4)
    assert p.returncode!=0 and not p.stdout
    return {'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}

def case(m,root,phase,full=False):
    s=m.RunningSink('sink-ordered',root)
    try:
        calls=fill(m,s);filled=strict.snapshot(s.journal)
        controls={}
        if phase=='fixed':
            assert calls[-1]['response'] is None
            if full:
                status=m.latest_status(s);seq=max(e['seq'] for e in status['events'])+1
                template={'seq':seq,'event':'effect_accepted','request_id':'exact-fill','payload':'',
                          'presented_version':1,'accepted_under_version':1,'check_mode':'sink-ordered'}
                overhead=len((json.dumps(template,sort_keys=True)+'\n').encode())
                count=CAP-s.journal.stat().st_size-overhead
                assert 0<count<8192
                filler=invoke(m,s,'/submit',{'authority_version':1,'request_id':'exact-fill','payload':'z'*count})
                assert filler['response']['status']==201 and s.journal.stat().st_size==CAP
                controls['exact_fill']=filler
            before_fail=strict.snapshot(s.journal);state_before=m.latest_status(s)
            controls['oversized_obligation']=invoke(m,s,'/commit-obligation',{'authority_version':1,'obligation_id':'too-large','payload':'q'*7168})
            assert controls['oversized_obligation']['response'] is None
            assert strict.snapshot(s.journal)==before_fail
            controls['absent_obligation']=invoke(m,s,'/deliver-obligation',{'obligation_id':'too-large'})
            assert controls['absent_obligation']['response']['status']==409
            controls['replacement']=invoke(m,s,'/replace',{})
            if full:
                assert controls['replacement']['response'] is None
                assert m.latest_status(s)['authority_version']==state_before['authority_version']==1
                controls['small_effect']=invoke(m,s,'/submit',{'authority_version':1,'request_id':'at-cap','payload':'small'})
                assert controls['small_effect']['response'] is None
                assert strict.snapshot(s.journal)==before_fail
            else:
                assert controls['replacement']['response']['status']==200
                controls['stale']=invoke(m,s,'/submit',{'authority_version':1,'request_id':'after-growth-stale','payload':'small'})
                controls['small_effect']=invoke(m,s,'/submit',{'authority_version':2,'request_id':'after-growth-current','payload':'small'})
                assert controls['stale']['response']['status']==409 and controls['small_effect']['response']['status']==201
            state_after=m.latest_status(s)
        journal=strict.snapshot(s.journal)
        assert len(bytes.fromhex(journal['raw_hex']))<131072
    finally:
        s.process.kill();out,err=s.process.communicate(timeout=4)
    if phase=='baseline':
        assert journal['exists'] and len(bytes.fromhex(journal['raw_hex']))>CAP
        assert all(r['response']['status']==201 for r in calls)
        recovery=failed_recovery(root/'sink-effects.jsonl')
    else:
        cold=m.RunningSink('recover-ordered',root)
        try:
            recovered=m.latest_status(cold)
            assert recovered['authority_version']==(1 if full else 2)
            assert recovered['effects']==state_after['effects']
            assert all(e['event']!='obligation_committed' for e in recovered['events'])
            cold_journal=strict.snapshot(cold.journal);assert cold_journal==journal
        finally:cold_exit=cold.kill_and_reap()
        recovery={'status':recovered,'sink_exit':cold_exit,'journal':cold_journal}
    result={'calls':calls,'filled':filled,'controls':controls,'journal':journal,'recovery':recovery,
            'sink_exit':s.process.returncode,'sink_stdout':out,'sink_stderr':err}
    if phase=='fixed':result.update(state_before=state_before,state_after=state_after)
    return result

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    phase=sys.argv[1];assert phase in ['baseline','fixed']
    m=post.load(SOURCE,'capacity_sink')
    with tempfile.TemporaryDirectory(prefix='ases-sink-cap-') as td:
        cases={'growth':case(m,Path(td)/'growth',phase)}
        if phase=='fixed':cases['exact_cap']=case(m,Path(td)/'exact-cap',phase,True)
    print(json.dumps({'schema':'ases.sink-recovery-capacity.v1','phase':phase,
                      'execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,Path(__file__)]},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                      'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':main()
