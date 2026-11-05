#!/usr/bin/env python3
"""Public-output induction against retained netlists, without new synthesis."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;PARENT=HERE.parent;K=PARENT.parent
spec=importlib.util.spec_from_file_location('mapped_induction_tools',PARENT/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    start=time.monotonic();m.HERE=HERE;m.OUT=HERE/'evidence';m.OUT.mkdir(exist_ok=True)
    paths=[m.SOURCE,m.COMPACT,PARENT/'run.py',HERE/'run.py',HERE/'IMPLEMENTATION-PACKET.md']
    paths += [PARENT/'evidence'/name for name in ['original-mapped.v','compact-mapped.v','original-miter.v','compact-miter.v']]
    m.RESULT=dict(schema='ases.kernel.mapped-public-induction',version=1,jobs={},
                  execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  source_hashes={str(p.relative_to(K)):sha(p) for p in paths},
                  environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                                   executable_sha256=sha(Path(sys.executable)),address_space_bytes=512*1024*1024),
                  tool_hashes={str(m.TOOLS/'yosys'):sha(m.TOOLS/'yosys')})
    m.save()
    for name,top in [('original','kernel0_machine'),('compact','kernel0_compact_machine')]:
        prelude=m.source(top)+f'read_verilog {PARENT/"evidence"/(name+"-mapped.v")} {PARENT/"evidence"/(name+"-miter.v")}; prep -top output_miter -flatten; '
        m.job(name+'-public-induct',prelude+'sat -seq 2 -tempinduct -maxsteps 4 -set-at 1 reset 1 -prove trigger 0 -prove-skip 1 -show-inputs -show-outputs -verify')
        if name=='compact':
            m.job('compact-no-reset',prelude+f'sat -seq 2 -prove trigger 0 -show-inputs -show-outputs -dump_json {m.OUT/"no-reset-counterexample.json"} -dump_vcd {m.OUT/"no-reset-counterexample.vcd"} -verify')
    m.RESULT['source_hashes_after']={str(p.relative_to(K)):sha(p) for p in paths}
    m.RESULT['elapsed_seconds']=time.monotonic()-start
    m.RESULT['qualification']='Direct public-output induction after explicit first-step synchronous reset, arbitrary defined inputs thereafter; shared formal toolchain, no original-semantics independence/physical/hardware fault claim'
    m.save()
    assert m.RESULT['source_hashes']==m.RESULT['source_hashes_after']
    for name in ('original','compact'):
        job=m.RESULT['jobs'][name+'-public-induct'];out=(m.OUT/(name+'-public-induct.stdout.txt')).read_text()
        assert job['exit']==0 and not job['timed_out'] and 'Induction step proven: SUCCESS!' in out,(name,job)
    negative=m.RESULT['jobs']['compact-no-reset'];out=(m.OUT/'compact-no-reset.stdout.txt').read_text()
    assert negative['exit']==1 and not negative['timed_out'] and 'SAT proof finished - model found: FAIL!' in out
    assert (m.OUT/'no-reset-counterexample.json').exists()
    print(json.dumps(dict(exits={name:v['exit'] for name,v in m.RESULT['jobs'].items()},elapsed_seconds=m.RESULT['elapsed_seconds'],source_hashes_verified_stable=True),indent=2,sort_keys=True))
if __name__=='__main__':main()
