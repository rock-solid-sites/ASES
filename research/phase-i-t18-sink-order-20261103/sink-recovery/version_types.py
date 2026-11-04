#!/usr/bin/env python3
"""Strict authority-version types; selected genuine integer journals are neighbors."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import sys
import tempfile
import controls

HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'run.py'
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    original=json.loads((HERE/'fixed.raw.json').read_text())
    effects=[json.loads(l) for l in bytes.fromhex(original['cases']['authority']['journal_before']['raw_hex']).splitlines()]
    obligations=[json.loads(l) for l in bytes.fromhex(original['cases']['obligation']['journal_before']['raw_hex']).splitlines()]
    cases={}
    for label,field in [('accepted','accepted_under_version'),('presented','presented_version')]:
        for kind,value in [('bool',True),('float',1.0)]:
            rows=copy.deepcopy(effects);rows[0][field]=value
            cases[label+'_'+kind]=controls.encode(rows)
    for kind,value in [('bool',True),('float',1.0)]:
        rows=copy.deepcopy(obligations);rows[0]['committed_under_version']=value
        cases['committed_'+kind]=controls.encode(rows)
    with tempfile.TemporaryDirectory(prefix='ases-sink-version-types-') as td:
        results={n:controls.startup(Path(td)/n,raw) for n,raw in cases.items()}
    print(json.dumps({'schema':'ases.sink-version-types.v1','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'refusals':results,'limits':'6 neighboring malformed journals; genuine integer cases exercised by separate live probe'},indent=2,sort_keys=True))
if __name__=='__main__':main()
