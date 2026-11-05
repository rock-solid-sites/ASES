#!/usr/bin/env python3
"""Frozen compact encoding proof, literal controls, and same-flow synthesis."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import signal
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent;K=HERE.parent;D=K/'direct-rtl'
TOOLS=Path('/tmp/ases-round2-synthesis/root/usr/bin')
IV=Path('/tmp/ases-round2-rtl/root/usr')
OUT=HERE/'evidence'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def limit():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(40,41))
def job(name,argv,expected=0):
    start=time.monotonic();metrics=OUT/(name+'.metrics')
    cmd=list(map(str,argv))
    timed_out=False
    with (OUT/(name+'.stdout.txt')).open('w') as out, (OUT/(name+'.stderr.txt')).open('w') as err:
        p=subprocess.Popen(cmd,stdout=out,stderr=err,preexec_fn=limit,start_new_session=True)
        while True:
            pid,status,usage=os.wait4(p.pid,os.WNOHANG)
            if pid:
                break
            if time.monotonic()-start>45:
                timed_out=True
                os.killpg(p.pid,signal.SIGKILL)
                pid,status,usage=os.wait4(p.pid,0)
                break
            time.sleep(.01)
        p.returncode=os.waitstatus_to_exitcode(status)
    p.stdout=(OUT/(name+'.stdout.txt')).read_text()
    p.stderr=(OUT/(name+'.stderr.txt')).read_text()
    metrics.write_text(json.dumps({'elapsed_seconds':time.monotonic()-start,'max_rss_kib':usage.ru_maxrss,
                                   'exit':p.returncode,'timed_out':timed_out})+'\n')
    result={'argv':cmd,'exit':p.returncode,'elapsed_seconds':time.monotonic()-start,
            'stdout_path':name+'.stdout.txt','stderr_path':name+'.stderr.txt',
            'stdout_sha256':sha(OUT/(name+'.stdout.txt')),'stderr_sha256':sha(OUT/(name+'.stderr.txt')),
            'time_metrics':metrics.read_text()}
    assert (p.returncode==0 if expected==0 else p.returncode!=0),result
    return result,p.stdout,p.stderr
def ys(name,text,expected=0):
    path=OUT/(name+'.ys');path.write_text(text+'\n')
    result,out,err=job(name,[TOOLS/'yosys','-Q','-T','-s',path],expected)
    result['script_path']=path.name;result['script_sha256']=sha(path)
    return result,out,err

def main():
    OUT.mkdir(exist_ok=True)
    start=time.monotonic()
    sourcepaths=[D/'kernel0.v',D/'sequence_tb.v',HERE/'compact.v',HERE/'contracts.v',
                 K/'timing-reduction/evidence/round2-rtl-boundaries.vectors',Path(__file__)]
    before={str(p.relative_to(K)):sha(p) for p in sourcepaths}
    results={}
    with tempfile.TemporaryDirectory(prefix='ases-compact-rtl-') as td:
        root=Path(td);bad=root/'compact-mutant.v'
        text=(HERE/'compact.v').read_text()
        assert text.count("code-5'd7")==1
        bad.write_text(text.replace("code-5'd7","code-5'd6"))
        for name,top,compact,expected in [('codec','codec_contract',HERE/'compact.v',0),
                                        ('step','step_contract',HERE/'compact.v',0),
                                        ('mutant-codec','codec_contract',bad,1)]:
            script=f'read_verilog {D/"kernel0.v"} {compact} {HERE/"contracts.v"}; prep -top {top} -flatten; sat -prove bad 0 -show-inputs -verify'
            result,out,err=ys(name,script,expected)
            if expected==0:assert 'SAT proof finished - no model found: SUCCESS!' in out
            else:assert 'proof did fail' in err or 'model found: FAIL!' in out
            results[name]=result
        tb=root/'compact-sequence.v'
        original=(D/'sequence_tb.v').read_text()
        assert original.count('kernel0_machine #(')==1
        tb.write_text(original.replace('kernel0_machine #(','kernel0_compact_machine #('))
        vectors=K/'timing-reduction/evidence/round2-rtl-boundaries.vectors'
        for name,compact,expected in [('literal',HERE/'compact.v',0),('mutant-literal',bad,1)]:
            binary=root/(name+'.vvp')
            comp,_,_=job(name+'-compile',[IV/'bin/iverilog','-B',IV/'lib/x86_64-linux-gnu/ivl','-g2012',
                          '-s','sequence_tb','-o',binary,D/'kernel0.v',compact,tb])
            sim,out,err=job(name,[IV/'bin/vvp',binary,'+vectors='+str(vectors)],expected)
            if expected==0:assert 'PASS sequential cycles=21' in out
            else:assert 'sequence=8 ' in out
            results[name]={'compile':comp,'simulate':sim,'binary_sha256':sha(binary)}
        synthesis={}
        for name,top in [('baseline','kernel0_machine'),('compact','kernel0_compact_machine')]:
            stats=root/(name+'-stats.json');net=root/(name+'-netlist.json')
            script=(f'read_verilog {D/"kernel0.v"} {HERE/"compact.v"}; '
                    f'chparam -set COUPLED 0 -set EXCLUSIVE 0 {top}; synth -top {top} -flatten -noabc; '
                    f'abc -exe {TOOLS/"berkeley-abc"} -g simple; clean; check -assert; '
                    f'tee -o {stats} stat -json; ltp -noff; write_json {net}')
            result,out,err=ys('synth-'+name,script)
            data=json.loads(stats.read_text());module=data['modules']['\\'+top]
            types=module['num_cells_by_type'];ff=sum(n for typ,n in types.items() if 'DFF' in typ)
            latches=sum(n for typ,n in types.items() if 'LATCH' in typ)
            levels=int(re.search(r'Longest topological path.*length=(\d+)',out).group(1))
            (OUT/(name+'-stats.json')).write_text(stats.read_text())
            synthesis[name]={'job':result,'total_cells':module['num_cells'],'ff_cells':ff,
                             'combinational_cells':module['num_cells']-ff-latches,'latches':latches,
                             'memories':module['num_memories'],'logic_levels':levels,'cell_types':types,
                             'netlist_sha256':sha(net),'stats_path':name+'-stats.json'}
        assert synthesis['baseline']['ff_cells']==24 and synthesis['compact']['ff_cells']==20
        assert all(v['latches']==v['memories']==0 for v in synthesis.values())
    after={str(p.relative_to(K)):sha(p) for p in sourcepaths};assert before==after
    versions={}
    for name,cmd in [('yosys',[TOOLS/'yosys','-V']),('abc',[TOOLS/'berkeley-abc','-c','version'])]:
        p=subprocess.run(list(map(str,cmd)),text=True,capture_output=True,timeout=5)
        versions[name]={'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    result={'schema':'ases.kernel.compact-encoding.v1','execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'source_hashes_before':before,'source_hashes_after':after,'contracts_and_controls':results,
            'synthesis':synthesis,'versions':versions,
            'tool_sha256':{str(p):sha(p) for p in [TOOLS/'yosys',TOOLS/'berkeley-abc',IV/'bin/iverilog',IV/'bin/vvp']},
            'packages':{'yosys':sha(Path('/tmp/ases-round2-synthesis/yosys.deb')),'abc':sha(Path('/tmp/ases-round2-synthesis/abc.deb'))},
            'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                           'executable_sha256':sha(Path(sys.executable))},'elapsed_seconds':time.monotonic()-start,
            'limits':'Independent profile; frozen transition reused; shape-constrained codec/step SAT plus21 literal cycles, not universal Kernel semantics/minimality or physical timing'}
    (HERE/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'synthesis':synthesis,'elapsed_seconds':result['elapsed_seconds']},indent=2))
if __name__=='__main__':main()
