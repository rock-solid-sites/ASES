#!/usr/bin/env python3
"""Concrete external-to-rollback-domain authority, with detached/replay controls."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import secrets
import select
import shutil
import subprocess
import sys
import tempfile
import two_store_crash_cuts as base

HERE=Path(__file__).resolve().parent

def authority(initial):
    current=initial
    seq=0
    for line in sys.stdin:
        q=json.loads(line);seq+=1
        if q['op']=='advance': current=q['current']
        response={'pid':os.getpid(),'seq':seq,'nonce':q['nonce'],'current':current}
        if q['op']=='admit': response['admitted']=q['candidate']==current
        print(json.dumps(response),flush=True)

def local(root):
    a=base.read_store(root/'authority.sqlite');w=base.read_store(root/'witness.sqlite')
    candidates={}
    for n in ['old','new']:
        p=root/(n+'.sqlite')
        import sqlite3
        with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as db:
            integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
            epoch=db.execute('SELECT epoch FROM image').fetchone()[0]
        c={'epoch':epoch,'digest':base.sha(p)}
        candidates[n]={'identity':c,'integrity':integrity,'locally_admitted':integrity=='ok' and
                       a['integrity']==w['integrity']=='ok' and
                       c=={k:a[k] for k in c}=={k:w[k] for k in c}}
    print(json.dumps({'pid':os.getpid(),'authority':a,'witness':w,'candidates':candidates}))

def read_local(root):
    p=subprocess.run([sys.executable,__file__,'--local',str(root)],capture_output=True,text=True,timeout=4,check=True)
    return {'exit':p.returncode,'stderr':p.stderr,'observation':json.loads(p.stdout)}

class Endpoint:
    def __init__(self,current):
        self.p=subprocess.Popen([sys.executable,__file__,'--authority',json.dumps(current)],
                                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.log=[]
    def call(self,op,**fields):
        q={'op':op,'nonce':secrets.token_hex(16),**fields}
        self.p.stdin.write(json.dumps(q)+'\n');self.p.stdin.flush()
        assert select.select([self.p.stdout],[],[],4)[0], 'endpoint timeout'
        response=json.loads(self.p.stdout.readline())
        assert response['nonce']==q['nonce'] and response['pid']==self.p.pid
        self.log.append({'request':q,'response':response})
        return self.log[-1]
    def close(self):
        self.p.kill();out,err=self.p.communicate(timeout=4)
        assert self.p.returncode==-9 and not err and not out
        return {'pid':self.p.pid,'exit':self.p.returncode,'stdout':out,'stderr':err}

def guarded(endpoint,obs,name):
    c=obs['observation']['candidates'][name]
    if not c['locally_admitted']:return {'admitted':False,'reason':'local-disagreement'}
    if endpoint is None:return {'admitted':False,'reason':'endpoint-unavailable'}
    r=endpoint.call('admit',candidate=c['identity'])
    return {'admitted':r['response']['admitted'],'reason':'serialized-endpoint','exchange':r}

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    if len(sys.argv)>1 and sys.argv[1]=='--authority':authority(json.loads(sys.argv[2]));return
    if len(sys.argv)>1 and sys.argv[1]=='--local':local(Path(sys.argv[2]));return
    with tempfile.TemporaryDirectory(prefix='ases-round2-witness-') as td:
        root=Path(td)
        for n,e in [('old',0),('new',1)]:base.make_image(root/(n+'.sqlite'),e)
        old={'epoch':0,'digest':base.sha(root/'old.sqlite')}
        new={'epoch':1,'digest':base.sha(root/'new.sqlite')}
        for name in ['authority','witness']:
            base.make_store(root/(name+'.sqlite'),old['digest'])
            shutil.copyfile(root/(name+'.sqlite'),root/(name+'-snapshot.sqlite'))
        endpoint=Endpoint(old)
        try:
            obs0=read_local(root)
            initial=guarded(endpoint,obs0,'old')
            cached=endpoint.call('query')
            advance=endpoint.call('advance',current=new)
            # Advance both local stores, then really restore authentic old SQLite bytes.
            for name in ['authority','witness']:
                base.update(root/(name+'.sqlite'),new['digest'])
            local_current=read_local(root)
            current=guarded(endpoint,local_current,'new')
            for name in ['authority','witness']:
                shutil.copyfile(root/(name+'-snapshot.sqlite'),root/(name+'.sqlite'))
            rolled=read_local(root)
            candidate=rolled['observation']['candidates']['old']
            detached={'admitted':candidate['locally_admitted'] and candidate['identity']==cached['response']['current'],
                      'cached_exchange':cached,'known_current_at_admission':advance['response']['current']}
            serialized=guarded(endpoint,rolled,'old')
            fresh=endpoint.call('query')
            replay={'old_response':cached['response'],'fresh_request':fresh['request'],
                    'admitted':cached['response']['nonce']==fresh['request']['nonce']}
            alive_at_local_rollback=endpoint.p.poll() is None
        finally: endpoint_exit=endpoint.close()
        missing=guarded(None,rolled,'old')
        rollback_endpoint=Endpoint(old)
        try: both_rolled=guarded(rollback_endpoint,rolled,'old')
        finally: rollback_exit=rollback_endpoint.close()
        assert initial['admitted'] and current['admitted']
        assert detached['admitted'] and old!=new and alive_at_local_rollback
        assert not serialized['admitted'] and not missing['admitted'] and not replay['admitted']
        assert both_rolled['admitted']
        assert {n:c['locally_admitted'] for n,c in rolled['observation']['candidates'].items()}=={'old':True,'new':False}
        assert sum(p.stat().st_size for p in root.iterdir())<1_048_576
        result={'schema':'ases.f1-live-witness.v1','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'base_sha256':hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),
                'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                               'executable_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
                'identities':{'old':old,'new':new},'local_initial':obs0,'local_current':local_current,'local_rolled':rolled,
                'endpoint_transcript':endpoint.log,'endpoint_survived_local_rollback':alive_at_local_rollback,
                'cases':{'initial_positive':initial,'current_positive':current,'detached_stale_accept':detached,
                         'serialized_stale_reject':serialized,'replayed_response':replay,'endpoint_missing':missing,
                         'endpoint_rolled_back':both_rolled},'endpoint_exit':endpoint_exit,
                'rolled_endpoint_transcript':rollback_endpoint.log,'rolled_endpoint_exit':rollback_exit}
        print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
