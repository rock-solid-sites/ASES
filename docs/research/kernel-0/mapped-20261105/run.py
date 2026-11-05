#!/usr/bin/env python3
"""Retain mapped circuits and separate induction from a synchronous reset base."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;K=HERE.parent;OUT=HERE/'evidence'
TOOLS=Path('/tmp/ases-round2-synthesis/root/usr/bin')
SOURCE=K/'direct-rtl/kernel0.v';COMPACT=K/'encoding-20261105/compact.v'
RESULT=dict(schema='ases.kernel.mapped-correspondence',version=1,jobs={},circuits={})
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save():(HERE/'result.json').write_text(json.dumps(RESULT,indent=2,sort_keys=True)+'\n')
def limit():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(40,41))
def job(name,script):
    path=OUT/(name+'.ys');path.write_text(script+'\n');start=time.monotonic();timed_out=False
    argv=[str(TOOLS/'yosys'),'-Q','-T','-s',str(path)]
    with (OUT/(name+'.stdout.txt')).open('w') as stdout,(OUT/(name+'.stderr.txt')).open('w') as stderr:
        process=subprocess.Popen(argv,stdout=stdout,stderr=stderr,preexec_fn=limit,start_new_session=True)
        while True:
            pid,status,usage=os.wait4(process.pid,os.WNOHANG)
            if pid:break
            if time.monotonic()-start>45:
                timed_out=True;os.killpg(process.pid,signal.SIGKILL);pid,status,usage=os.wait4(process.pid,0);break
            time.sleep(.01)
        process.returncode=os.waitstatus_to_exitcode(status)
    record=dict(argv=argv,exit=process.returncode,timed_out=timed_out,wall_seconds=time.monotonic()-start,
                user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,peak_rss_kib=usage.ru_maxrss,
                script=path.name,script_sha256=digest(path),stdout=name+'.stdout.txt',stderr=name+'.stderr.txt',
                stdout_sha256=digest(OUT/(name+'.stdout.txt')),stderr_sha256=digest(OUT/(name+'.stderr.txt')))
    RESULT['jobs'][name]=record;save();return record
def source(top):
    return (f'read_verilog {SOURCE} {COMPACT}; chparam -set COUPLED 0 -set EXCLUSIVE 0 {top}; '
            f'hierarchy -top {top}; proc; flatten; opt; memory; opt; rename {top} gold; ')
def wrapper(gate):
    return f'''module output_miter(input clk,reset,valid,input [14:0] proposal,output trigger,
    output [21:0] gold_state,gate_state,output gold_resolved,gate_resolved,gold_committed,gate_committed);
    gold a(clk,reset,valid,proposal,gold_state,gold_resolved,gold_committed);
    {gate} b(clk,reset,valid,proposal,gate_state,gate_resolved,gate_committed);
    assign trigger=(gold_state!=gate_state)||(gold_resolved!=gate_resolved)||(gold_committed!=gate_committed);
endmodule
'''
def main():
    OUT.mkdir(exist_ok=True);start=time.monotonic()
    paths=[SOURCE,COMPACT,Path(__file__),HERE/'IMPLEMENTATION-PACKET.md']
    RESULT.update(execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  source_hashes={str(p.relative_to(K)):digest(p) for p in paths},
                  environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
                  executable_sha256=digest(Path(sys.executable)),address_space_bytes=512*1024*1024),
                  tool_hashes={str(p):digest(p) for p in [TOOLS/'yosys',TOOLS/'berkeley-abc']})
    save()
    for name,top in [('original','kernel0_machine'),('compact','kernel0_compact_machine')]:
        gate='mapped_'+name;net=OUT/(name+'-mapped.v');miter=OUT/(name+'-miter.v');miter.write_text(wrapper(gate))
        synthesis=job(name+'-synth',f'read_verilog {SOURCE} {COMPACT}; chparam -set COUPLED 0 -set EXCLUSIVE 0 {top}; synth -top {top} -flatten -noabc; abc -exe {TOOLS/"berkeley-abc"} -g simple; clean; check -assert; rename {top} {gate}; write_verilog -noattr {net}')
        assert synthesis['exit']==0 and not synthesis['timed_out'],'synthesis did not complete'
        RESULT['circuits'][name]=dict(netlist=net.name,netlist_sha256=digest(net),miter=miter.name,miter_sha256=digest(miter));save()
        induction=job(name+'-equiv',source(top)+f'read_verilog {net}; proc; opt; equiv_make gold {gate} equiv; prep -top equiv -flatten; equiv_simple -seq 2; equiv_induct -seq 2; equiv_status -assert')
        base=job(name+'-reset-base',source(top)+f'read_verilog {net} {miter}; prep -top output_miter -flatten; sat -seq 4 -set-at 1 reset 1 -prove trigger 0 -prove-skip 1 -show-inputs -show-outputs -verify')
        RESULT['circuits'][name].update(induction_exit=induction['exit'],reset_base_exit=base['exit']);save()
        if name=='compact':
            bad=OUT/'mutant-wrapper.v';bad.write_text('''module mutated_compact(input clk,reset,valid,input [14:0] proposal,output [21:0] state,output resolved,committed);
    wire actual_committed;
    mapped_compact inner(clk,reset,valid,proposal,state,resolved,actual_committed);
    assign committed=actual_committed ^ valid;
endmodule
''')
            bad_miter=OUT/'mutant-miter.v';bad_miter.write_text(wrapper('mutated_compact'))
            mutation=job('mutant-reset-base',source(top)+f'read_verilog {net} {bad} {bad_miter}; prep -top output_miter -flatten; sat -seq 4 -set-at 1 reset 1 -prove trigger 0 -prove-skip 1 -show-inputs -show-outputs -dump_json {OUT/"mutant-counterexample.json"} -dump_vcd {OUT/"mutant-counterexample.vcd"} -verify')
            RESULT['mutation']=dict(exit=mutation['exit'],wrapper_sha256=digest(bad),miter_sha256=digest(bad_miter),
                                    counterexample_exists=(OUT/'mutant-counterexample.json').exists());save()
    RESULT['elapsed_seconds']=time.monotonic()-start
    RESULT['source_hashes_after']={str(p.relative_to(K)):digest(p) for p in paths}
    RESULT['qualification']='independent profile only; convergence proof and separate reset-base, shared toolchain, not physical timing, universal semantics, resetless/hardware-fault guarantee'
    save()
    assert RESULT['source_hashes']==RESULT['source_hashes_after']
    for name in ('original','compact'):
        assert RESULT['circuits'][name]['induction_exit']==RESULT['circuits'][name]['reset_base_exit']==0
        assert 'Equivalence successfully proven!' in (OUT/(name+'-equiv.stdout.txt')).read_text()
        assert 'SAT proof finished - no model found: SUCCESS!' in (OUT/(name+'-reset-base.stdout.txt')).read_text()
    assert RESULT['mutation']['exit']!=0 and RESULT['mutation']['counterexample_exists']
    assert 'SAT proof finished - model found: FAIL!' in (OUT/'mutant-reset-base.stdout.txt').read_text()
    print(json.dumps(dict(circuits=RESULT['circuits'],mutation=RESULT['mutation'],elapsed_seconds=RESULT['elapsed_seconds']),indent=2,sort_keys=True))
if __name__=='__main__':main()
