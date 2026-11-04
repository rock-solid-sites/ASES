#!/usr/bin/env python3
"""Qualify recorded HEAD versus exact executed source without rewriting raw."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
SINK='research/phase-i-t18-sink-order-20261103/run.py'
PINS={'baseline':'589cee0','fixed':'43ddd00633ecf4d909021a47f89052f1dca1cfcf'}
# Resolve abbreviated historical prereg pin once; output retains the full SHA.
PINS['baseline']=subprocess.check_output(['git','rev-parse','589cee0'],text=True).strip()

def digest_at(pin):return hashlib.sha256(subprocess.check_output(['git','show',pin+':'+SINK])).hexdigest()
def qualify(raw,phase):
    expected=digest_at(PINS[phase])
    assert raw['source_sha256']==expected, 'source bytes not matched by implementation pin'
    base=raw['source_revision'];at_head=digest_at(base)
    return {'execution_base_sha':base,'executed_sink_sha256':expected,'implementation_commit':PINS[phase],
            'head_sink_sha256':at_head,'executed_sink_matches_execution_head':expected==at_head,
            'interpretation':'HEAD is invocation base only; exact executed source is identified by content hash and implementation pin'}

def main():
    out={}
    for phase in ['baseline','fixed']:
        path=HERE/(phase+'.raw.json');raw=json.loads(path.read_text())
        out[phase]={'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**qualify(raw,phase)}
        wrong=copy.deepcopy(raw);wrong['source_sha256']='0'*64
        try:qualify(wrong,phase)
        except AssertionError:out[phase]['wrong_source_digest_control']='REFUSED'
        else:raise AssertionError('corrupt source binding accepted')
    assert out['baseline']['executed_sink_matches_execution_head']
    assert not out['fixed']['executed_sink_matches_execution_head']
    print(json.dumps({'schema':'ases.f4-execution-provenance-qualification.v1','records':out,
                      'limits':'Retrospective source-byte binding, not authentication of execution or a claim the dirty status was contemporaneously recorded'},indent=2,sort_keys=True))
if __name__=='__main__':main()
