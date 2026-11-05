#!/usr/bin/env python3
"""Prepared recovery material stays nonauthoritative across process termination."""
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import probe

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py'
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    io=json.loads((HERE.parent/'io-failure/fixed.raw.json').read_text())
    partial=bytes.fromhex(io['cases']['partial']['journal_after_fault']['raw_hex'])
    prefix=bytes.fromhex(io['cases']['partial']['acknowledged_journal']['raw_hex'])
    other=json.loads((HERE.parent/'sink-recovery/fixed.raw.json').read_text())
    alternate=bytes.fromhex(other['cases']['obligation']['journal_before']['raw_hex'])
    assert [json.loads(l)['event'] for l in alternate.splitlines()]==['obligation_committed','authority_replaced']
    m=probe.post.load(SOURCE,'prepared_cut_sink')
    with tempfile.TemporaryDirectory(prefix='ases-prefix-prepared-') as td:
        root=Path(td);cases={}
        for name,substitute in [('prepared_original',False),('prepared_other_valid_journal',True)]:
            path=root/name;path.mkdir();journal=path/'sink-effects.jsonl';journal.write_bytes(partial)
            gate=probe.cut(path,'prepared')
            temp=path/'sink-effects.jsonl.prefix.tmp'
            assert journal.read_bytes()==partial and temp.read_bytes()==prefix
            original_manifest=probe.files(path)
            before_temp=temp.read_bytes()
            if substitute:temp.write_bytes(alternate)
            substituted_manifest=probe.files(path)
            assert journal.read_bytes()==partial
            sink=m.RunningSink('recover-ordered-prefix',path)
            try:
                restored=m.latest_status(sink)
                assert restored['authority_version']==1 and [e['request_id'] for e in restored['effects']]==['ack-before']
                assert journal.read_bytes()==prefix and not temp.exists()
                response=probe.post.invoke(m,sink.port,'/submit',{'authority_version':1,'request_id':'prepared-continued','payload':'continued'})
                assert response['response']['status']==201
                final=m.latest_status(sink)
            finally:code=sink.kill_and_reap()
            cold=probe.recover(m,path,'recover-ordered')
            assert cold['status']['effects']==final['effects']
            cases[name]={'gate':gate,'prepared_original_hex':before_temp.hex(),
                         'prepared_replaced_hex':alternate.hex() if substitute else before_temp.hex(),
                         'files_before_substitution':original_manifest,'files_after_substitution':substituted_manifest,
                         'restored':restored,'new_call':response,'final':final,'exit':code,'cold':cold}
    print(json.dumps({'schema':'ases.prefix-prepared-cut.v1',
                      'execution_base_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'cases':cases,'limits':'same-host current journal and interrupted-new-tail premise; prepared temp is explicitly uncommitted'},indent=2,sort_keys=True))
if __name__=='__main__':main()
