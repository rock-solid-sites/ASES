#!/usr/bin/env python3
"""Read-only artifact audit; no additional synthesis/proof execution."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent;OUT=HERE/'evidence'
class Incomplete(Exception):pass
class Violation(Exception):pass
def expect(value,why):
    if not value:raise Violation(why)
def audit(d):
    try:
        expect(d['source_hashes']==d['source_hashes_after'],'source changed during execution')
        for path,digest in d['source_hashes'].items():
            raw=subprocess.check_output(['git','show',d['execution_sha']+':docs/research/kernel-0/'+path])
            expect(hashlib.sha256(raw).hexdigest()==digest,'source pin/hash mismatch')
        for name,job in d['jobs'].items():
            expect(not job['timed_out'] and job['wall_seconds']<=45 and job['peak_rss_kib']>0,'job limit/metric mismatch')
            for kind in ('script','stdout','stderr'):
                expect(hashlib.sha256((OUT/job[kind]).read_bytes()).hexdigest()==job[kind+'_sha256'],'artifact digest mismatch')
            expect(job['exit']==(1 if name=='mutant-reset-base' else 0),'unexpected job exit')
        counts={}
        for name in ('original','compact'):
            circuit=d['circuits'][name]
            expect(hashlib.sha256((OUT/circuit['netlist']).read_bytes()).hexdigest()==circuit['netlist_sha256'],'mapped circuit digest mismatch')
            expect(hashlib.sha256((OUT/circuit['miter']).read_bytes()).hexdigest()==circuit['miter_sha256'],'output miter digest mismatch')
            proof=(OUT/(name+'-equiv.stdout.txt')).read_text()
            count=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',proof)[-1]
            expect(int(count[0])>0 and count[1]=='0' and 'Equivalence successfully proven!' in proof,'unproven equivalence points')
            counts[name]=int(count[0])
            base=(OUT/(name+'-reset-base.stdout.txt')).read_text();script=(OUT/(name+'-reset-base.ys')).read_text()
            expect('SAT proof finished - no model found: SUCCESS!' in base and '-seq 4 -set-at 1 reset 1' in script
                   and '-prove trigger 0 -prove-skip 1' in script,'explicit post-reset bounded proof absent')
        mutation=(OUT/'mutant-reset-base.stdout.txt').read_text()
        expect(d['mutation']['counterexample_exists'] and 'SAT proof finished - model found: FAIL!' in mutation,'mutation failed without semantic counterexample')
        # On -verify failure Yosys's buffered text table may end mid-row. Its
        # independently written WaveJSON model retains all four clock frames.
        model=json.loads((OUT/'mutant-counterexample.json').read_bytes());frames={}
        for row in model['signal']:
            if row['name'] not in ('reset','valid','trigger','gold_committed','gate_committed'):continue
            previous=None
            for step,symbol in enumerate(row['wave']):
                if symbol in '01':previous=int(symbol)
                elif symbol=='.':pass
                elif symbol=='4':previous=None
                else:raise Incomplete('unhandled scalar WaveJSON symbol')
                if step:frames.setdefault(step,{})[row['name']]=previous
        if set(frames)!=set(range(1,5)) or any(value is None for frame in frames.values() for value in frame.values()):
            raise Incomplete('missing concrete scalar clock frame')
        expect(frames[1]['reset']==1 and any(step>=2 and f['valid']==f['trigger']==1
                   and f['gold_committed']!=f['gate_committed'] for step,f in frames.items()),'post-initial-reset mutation witness absent')
        return dict(status='SUPPORTED',proven_equivalence_points=counts,mutation_clock_frames=frames,
                    qualification='all tool equivalence points proved plus separate top-output reset-base steps2..4; no unconditional resetless or independent full-semantics proof')
    except Violation as error:return dict(status='VIOLATION',reason=str(error))
    except Incomplete as error:return dict(status='INCOMPLETE',reason=str(error))
    except (KeyError,IndexError,TypeError,FileNotFoundError) as error:return dict(status='INCOMPLETE',reason=str(error))
def main():
    d=json.loads((HERE/'result.json').read_bytes());result=audit(d);assert result['status']=='SUPPORTED',result
    missing=copy.deepcopy(d);del missing['circuits'];bad=copy.deepcopy(d);bad['jobs']['compact-equiv']['exit']=1
    controls=dict(missing_circuit_manifest=audit(missing),contradicted_proof_exit=audit(bad))
    assert controls['missing_circuit_manifest']['status']=='INCOMPLETE' and controls['contradicted_proof_exit']['status']=='VIOLATION',controls
    print(json.dumps(dict(result=result,controls=controls),indent=2,sort_keys=True))
if __name__=='__main__':main()
