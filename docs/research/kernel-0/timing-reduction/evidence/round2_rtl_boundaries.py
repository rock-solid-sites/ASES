#!/usr/bin/env python3
"""Compile unchanged RTL and literal vectors; no semantic oracle/codec imports."""
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
K=HERE.parents[1];D=K/'direct-rtl'
TOOL=Path('/tmp/ases-round2-rtl/root/usr')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def limit():resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
def run(argv):
    start=time.monotonic()
    p=subprocess.run(list(map(str,argv)),text=True,capture_output=True,timeout=10,preexec_fn=limit)
    return {'argv':list(map(str,argv)),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed':time.monotonic()-start}
def main():
    source=(D/'kernel0.v').read_text()
    needle='''RESTRICT: if (current_rights!=0 && (value & ~current_rights)==0) begin
                        proposed[8+3*target +: 3]=value;'''
    assert source.count('if (reset) begin')==source.count(needle)==1
    variants={'reference':source,'reset_loses_precedence':source.replace('if (reset) begin','if (reset && !valid) begin'),
              'restriction_erases_issued':source.replace(needle,needle+'\n                        proposed[4+target]=0;')}
    results={}
    with tempfile.TemporaryDirectory(prefix='ases-round2-rtl-') as td:
        root=Path(td)
        for name,text in variants.items():
            path=root/(name+'.v');path.write_text(text);binary=root/(name+'.vvp')
            comp=run([TOOL/'bin/iverilog','-B',TOOL/'lib/x86_64-linux-gnu/ivl','-g2012','-s','sequence_tb','-o',binary,path,D/'sequence_tb.v'])
            assert comp['exit']==0,comp
            sim=run([TOOL/'bin/vvp',binary,'+vectors='+str(HERE/'round2-rtl-boundaries.vectors')])
            results[name]={'compile':comp,'simulate':sim,'rtl_sha256':sha(path),'binary_sha256':sha(binary)}
    assert results['reference']['simulate']['exit']==0
    assert 'cycles=21' in results['reference']['simulate']['stdout']
    for name,seq in [('reset_loses_precedence',16),('restriction_erases_issued',6)]:
        assert results[name]['simulate']['exit']!=0
        assert 'sequence='+str(seq)+' ' in results[name]['simulate']['stdout']
    sourcepaths=[D/'kernel0.v',D/'sequence_tb.v',K/'Kernel-0-Finite-Model.md',K/'Kernel-0-Direct-RTL-Result.md',Path(__file__),HERE/'round2-rtl-boundaries.vectors']
    print(json.dumps({'schema':'ases.kernel.literal-rtl.v1','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'environment':{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,
                                     'tool_version':run([TOOL/'bin/vvp','-V'])},
                      'source_hashes':{str(p.relative_to(K)):sha(p) for p in sourcepaths},
                      'tool_hashes':{str(p.relative_to(TOOL)):sha(p) for p in [TOOL/'bin/iverilog',TOOL/'bin/vvp',TOOL/'lib/x86_64-linux-gnu/ivl/ivl']},
                      'package_sha256':sha(Path('/tmp/ases-round2-rtl/iverilog.deb')),
                      'literal_vectors':(HERE/'round2-rtl-boundaries.vectors').read_text(),'results':results},indent=2,sort_keys=True))
if __name__=='__main__':main()
