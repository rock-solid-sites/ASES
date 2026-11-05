#!/usr/bin/env python3
"""Fixed public induction property; no repeat of mapping or no-reset control."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent;K=PARENT.parent
spec=importlib.util.spec_from_file_location('corrected_public_tools',PARENT/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    start=time.monotonic();m.HERE=HERE/'corrected';m.OUT=m.HERE/'evidence';m.OUT.mkdir(parents=True,exist_ok=True)
    paths=[m.SOURCE,m.COMPACT,PARENT/'run.py',Path(__file__),HERE/'reset_monitor.v',HERE/'CORRECTION.md']
    paths += [PARENT/'evidence'/name for name in ['original-mapped.v','compact-mapped.v','original-miter.v','compact-miter.v']]
    m.RESULT=dict(schema='ases.kernel.mapped-public-induction-corrected',version=1,jobs={},
                  execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  source_hashes={str(p.relative_to(K)):sha(p) for p in paths},
                  environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                  executable_sha256=sha(Path(sys.executable)),address_space_bytes=512*1024*1024),
                  tool_hashes={str(m.TOOLS/'yosys'):sha(m.TOOLS/'yosys')});m.save()
    for name,top in [('original','kernel0_machine'),('compact','kernel0_compact_machine')]:
        script=m.source(top)+f'read_verilog {PARENT/"evidence"/(name+"-mapped.v")} {PARENT/"evidence"/(name+"-miter.v")} {HERE/"reset_monitor.v"}; prep -top reset_monitored_miter -flatten; '
        m.job(name+'-public-induct',script+'sat -seq 2 -tempinduct -maxsteps 4 -set-at 1 reset 1 -prove trigger 0 -show-inputs -show-outputs -verify')
    m.RESULT['source_hashes_after']={str(p.relative_to(K)):sha(p) for p in paths}
    m.RESULT['elapsed_seconds']=time.monotonic()-start
    m.RESULT['qualification']='Public output induction after sampled trusted synchronous reset; only assurance monitor initialized, product registers initially unconstrained. Shared formal toolchain/two-state edge model; not independent original-semantics or physical/hardware-fault proof.'
    m.save();assert m.RESULT['source_hashes']==m.RESULT['source_hashes_after']
    for name in ('original','compact'):
        job=m.RESULT['jobs'][name+'-public-induct'];out=(m.OUT/(name+'-public-induct.stdout.txt')).read_text()
        assert job['exit']==0 and not job['timed_out'] and 'Induction step proven: SUCCESS!' in out,(name,job)
    print(json.dumps(dict(exits={k:v['exit'] for k,v in m.RESULT['jobs'].items()},elapsed_seconds=m.RESULT['elapsed_seconds']),indent=2,sort_keys=True))
if __name__=='__main__':main()
