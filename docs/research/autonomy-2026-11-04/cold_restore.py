#!/usr/bin/env python3
"""Re-fetch indexed evidence into a new remote-only clone and validate it."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

COORD='research/autonomy-20261103-run'
REMOTE='https://github.com/rock-solid-sites/ASES.git'
INDEX='docs/research/autonomy-2026-11-04/experiment-index.json'
VALIDATOR='docs/research/autonomy-2026-11-04/validate_index.py'

def run(argv,cwd=None):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True,timeout=60)
    if p.returncode:raise RuntimeError(json.dumps({'argv':argv,'exit':p.returncode,'stderr':p.stderr}))
    return p

def main():
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='ases-round2-cold-') as td:
        root=Path(td)/'repository'
        clone=run(['git','clone','--quiet','--single-branch','--branch',COORD,REMOTE,str(root)])
        coordinator=run(['git','rev-parse','HEAD'],root).stdout.strip()
        d=json.loads((root/INDEX).read_text())
        branches=sorted(d['branch_tips'])
        fetch=run(['git','fetch','--quiet','--no-tags','origin',*[f'refs/heads/{b}:refs/remotes/origin/{b}' for b in branches]],root)
        validation=run([sys.executable,VALIDATOR],root)
        # A corrupted digest must be rejected against fetched bytes, not just shape checked.
        altered=json.loads((root/INDEX).read_text())
        altered['experiments'][0]['raw_evidence'][0]['sha256']='0'*64
        (root/INDEX).write_text(json.dumps(altered))
        negative=subprocess.run([sys.executable,VALIDATOR],cwd=root,text=True,capture_output=True,timeout=10)
        assert negative.returncode!=0 and 'AssertionError' in negative.stderr
        artifact_count=sum(len(e['raw_evidence']) for e in d['experiments'])
        restored=[]
        for e in d['experiments']:
            # Implementation is also present at the pin, separately from the raw digest.
            raw=run(['git','show',e['source_sha']+':'+e['implementation']],root).stdout.encode()
            restored.append({'id':e['id'],'source_sha':e['source_sha'],'implementation_sha256':hashlib.sha256(raw).hexdigest()})
        tips={b:run(['git','rev-parse','refs/remotes/origin/'+b],root).stdout.strip() for b in branches}
        print(json.dumps({'schema':'ases.autonomy.cold-restoration.v1','coordinator_fetched_sha':coordinator,
                          'remote':REMOTE,'fetched_branch_tips':tips,'indexed_snapshot_tips':d['branch_tips'],
                          'validation':{'exit':validation.returncode,'stdout':validation.stdout,'stderr':validation.stderr},
                          'tampered_digest_control':{'exit':negative.returncode,'detected':'AssertionError' in negative.stderr},
                          'restored_experiments':restored,'raw_artifact_count':artifact_count,
                          'elapsed_seconds':time.monotonic()-started,
                          'limits':'Remote-only cold clone, same coordinator/host and GitHub origin; not independent archive, clean-machine execution or long-term retention proof'},indent=2,sort_keys=True))
if __name__=='__main__':main()
