#!/usr/bin/env python3
"""Check actual induction markers/initial assumptions; no tool rerun."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
HERE=Path(__file__).resolve().parent
class Violation(Exception):pass
def expect(v,why):
    if not v:raise Violation(why)
def audit(d):
    try:
        expect(d['source_hashes']==d['source_hashes_after'],'source/netlist changed during proof')
        for path,digest in d['source_hashes'].items():
            raw=subprocess.check_output(['git','show',d['execution_sha']+':docs/research/kernel-0/'+path])
            expect(hashlib.sha256(raw).hexdigest()==digest,'source revision/hash mismatch')
        proofs={}
        for name in ('original','compact'):
            job=d['jobs'][name+'-public-induct'];root=HERE/'corrected/evidence'
            expect(job['exit']==0 and not job['timed_out'] and job['wall_seconds']<=45,'induction tool failed/exceeded bound')
            for kind in ('script','stdout','stderr'):
                expect(hashlib.sha256((root/job[kind]).read_bytes()).hexdigest()==job[kind+'_sha256'],'proof artifact digest mismatch')
            out=(root/job['stdout']).read_text();script=(root/job['script']).read_text()
            initial=re.findall(r'^Final init constraint equation: (.*)$',out,re.M)
            expect(initial==["\\armed = 1'0"],'product initial-state constraint silently added or monitor initialization absent')
            expect('Base case for induction length 1 proven.' in out and 'Induction step proven: SUCCESS!' in out,'actual base/induction result absent')
            expect('-tempinduct -maxsteps 4 -set-at 1 reset 1 -prove trigger 0' in script
                   and '-prove-skip' not in script and '-set-init' not in script,'frozen property/bounds changed')
            proofs[name]=dict(base_length=1,induction_success=True,initial_constraints=initial)
        old=json.loads((HERE/'result.json').read_bytes())
        for name in ('original','compact'):
            job=old['jobs'][name+'-public-induct'];err=(HERE/'evidence'/job['stderr']).read_text()
            expect(job['exit']==1 and "Options -prove-skip and -tempinduct don't work" in err,'initial option incompatibility not preserved')
        neg=old['jobs']['compact-no-reset'];out=(HERE/'evidence'/neg['stdout']).read_text()
        expect(neg['exit']==1 and 'SAT proof finished - model found: FAIL!' in out,'no-reset control failed without semantic model')
        model=json.loads((HERE/'evidence/no-reset-counterexample.json').read_bytes())
        expect(any(s['name']=='trigger' and '1' in s['wave'] for s in model['signal']),'no-reset actual output difference absent')
        return dict(status='SUPPORTED',proofs=proofs,no_reset_control='arbitrary independent initial-state counterexample, not a reachable-after-reset product defect',qualification=d['qualification'])
    except Violation as error:return dict(status='VIOLATION',reason=str(error))
    except (KeyError,TypeError,FileNotFoundError) as error:return dict(status='INCOMPLETE',reason=str(error))
def main():
    d=json.loads((HERE/'corrected/result.json').read_bytes());result=audit(d);assert result['status']=='SUPPORTED',result
    missing=copy.deepcopy(d);del missing['jobs']['compact-public-induct'];bad=copy.deepcopy(d);bad['jobs']['original-public-induct']['exit']=1
    controls=dict(missing_proof=audit(missing),contradictory_exit=audit(bad));assert controls['missing_proof']['status']=='INCOMPLETE' and controls['contradictory_exit']['status']=='VIOLATION',controls
    print(json.dumps(dict(result=result,controls=controls),indent=2,sort_keys=True))
if __name__=='__main__':main()
