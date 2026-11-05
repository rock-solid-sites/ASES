#!/usr/bin/env python3
"""Actual uninterrupted ACK/failure/files/recovery lineage; no journal fixture copy."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time
import probe as prefix

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py'
spec=importlib.util.spec_from_file_location('continuous_io_probe',HERE.parent/'io-failure/probe.py')
io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)

def one(m,root,name,stage):
    marks={'io_start_ns':time.monotonic_ns()}
    actual=io.case(SOURCE.read_text(),root,'partial')
    marks['io_done_ns']=time.monotonic_ns()
    state=root/'state';journal=state/'sink-effects.jsonl'
    surviving=prefix.strict.snapshot(journal)
    assert surviving==actual['journal_after_later']
    assert actual['first']['response']['status']==201
    assert actual['fault']['response'] is actual['later']['response'] is None
    gate=None
    if stage:
        marks['gate_start_ns']=time.monotonic_ns();gate=prefix.cut(state,stage);marks['gate_done_ns']=time.monotonic_ns()
    s=m.RunningSink('recover-ordered-prefix',state)
    try:
        marks['recovery_ready_ns']=time.monotonic_ns()
        restored=m.latest_status(s)
        restored_bytes=prefix.strict.snapshot(journal)
        assert restored_bytes==actual['acknowledged_journal']
        assert [e['request_id'] for e in restored['effects']]==['ack-before']
        new=prefix.post.invoke(m,s.port,'/submit',{'authority_version':1,'request_id':'continuous-new','payload':'continuous-retained-π'})
        assert new['response']['status']==201
        accepted=m.latest_status(s);after=prefix.strict.snapshot(journal)
    finally:exit1=s.kill_and_reap()
    marks['new_sink_reaped_ns']=time.monotonic_ns()
    cold=prefix.recover(m,state,'recover-ordered');marks['final_cold_reaped_ns']=time.monotonic_ns()
    assert accepted['effects']==cold['status']['effects']
    original=bytes.fromhex(surviving['raw_hex'])
    quarantine=journal.with_name(journal.name+'.quarantine-'+hashlib.sha256(original).hexdigest())
    assert quarantine.read_bytes()==original
    assert sum(p.stat().st_size for p in root.rglob('*') if p.is_file())<262144
    return {'name':name,'stage':stage,'journal_path':str(journal),'marks':marks,
            'actual_writer_history':actual,'same_surviving_journal':surviving,'gate':gate,
            'restored':restored,'restored_journal':restored_bytes,'new_call':new,'after':accepted,'after_journal':after,
            'new_sink_exit':exit1,'cold':cold,'quarantine_sha256':hashlib.sha256(quarantine.read_bytes()).hexdigest(),
            'quarantine_raw_hex':quarantine.read_bytes().hex(),'files':prefix.files(state)}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    m=prefix.post.load(SOURCE,'continuous_source')
    real_popen=subprocess.Popen;children=[];maximum=0
    def observed(argv,*args,**kwargs):
        nonlocal maximum
        started=time.monotonic_ns();p=real_popen(argv,*args,**kwargs)
        record={'proc':p,'pid':p.pid,'argv':list(map(str,argv)),'start_ns':started}
        children.append(record)
        real_wait=p.wait
        def observed_wait(*args,**kwargs):
            code=real_wait(*args,**kwargs)
            record.setdefault('exit_observed_ns',time.monotonic_ns())
            return code
        p.wait=observed_wait
        maximum=max(maximum,sum(c['proc'].returncode is None for c in children))
        return p
    cases={}
    with tempfile.TemporaryDirectory(prefix='ases-continuous-history-') as td:
        subprocess.Popen=observed
        try:
            for name,stage in [('uninterrupted',None),('quarantined','quarantined'),('prepared','prepared'),('published','published')]:
                start=len(children)
                cases[name]=one(m,Path(td)/name,name,stage)
                cases[name]['child_pids']=[c['pid'] for c in children[start:]]
        finally:
            subprocess.Popen=real_popen
            for c in children:
                if c['proc'].poll() is None:
                    c['proc'].kill();c['proc'].communicate(timeout=4);c['forced_cleanup']=True
    assert maximum==1 and not any(c.get('forced_cleanup') for c in children)
    assert all(c['proc'].returncode in (-9,1) and c.get('exit_observed_ns',0)>c['start_ns'] for c in children)
    observations=[{k:v for k,v in c.items() if k!='proc'}|{'exit':c['proc'].returncode} for c in children]
    sourcepaths=[SOURCE,Path(__file__),Path(io.__file__),Path(prefix.__file__)]
    print(json.dumps({'schema':'ases.continuous-prefix-history.v1',
                      'execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_hashes':{str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sourcepaths},
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                      'bounds':{'histories':4,'max_concurrent_owned_children':maximum,'children':len(children),'enumerated':False},
                      'children':observations,'cases':cases},indent=2,sort_keys=True))
if __name__=='__main__':main()
