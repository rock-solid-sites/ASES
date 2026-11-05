#!/usr/bin/env python3
"""Small replayable counterexample to original diagnostic Obs, no exploration rerun."""
from dataclasses import asdict
import hashlib,json,platform,resource,subprocess,sys
from pathlib import Path
import phase_i_f1_model as m
HERE=Path(__file__).resolve().parent

def obs(s):
    return (s.uses,tuple((w,s.wu(w).present,s.wu(w).sealed,s.wu(w).parent) for w in m.WORLDS),tuple(g[2] for g in s.mgmt))
def history(path):
    s=m.initial();trace=[]
    for ev in path:
        outcome,s,reason=m.resolve(s,ev,m.REFERENCE)
        assert outcome=='commit' and m.invariant(s,m.REFERENCE) is None
        trace.append(dict(event=ev,outcome=outcome,reason=reason))
    event=('use',m.C,m.SINK,m.W,m.B_GEN)
    guard=m.guard(s,event,m.REFERENCE)
    oracle=m.oracle_use_permitted(s,m.C,m.SINK,m.W,m.B_GEN,m.REFERENCE)
    outcome,next_state,reason=m.resolve(s,event,m.REFERENCE)
    assert oracle==(guard is None)==(outcome=='commit')
    return s,dict(prefix=trace,state=asdict(s),observation=obs(s),original_guard_reason=guard,
                  independent_oracle_allowed=oracle,next_event=event,next_outcome=outcome,next_reason=reason,
                  next_invariant=m.invariant(next_state,m.REFERENCE),next_state=asdict(next_state))
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    paths={'initial':(), 'granted':(('grant',m.P,m.SINK,m.RW),('grant',m.C,m.SINK,m.RW))}
    states={};results={}
    for name,path in paths.items():states[name],results[name]=history(path)
    assert obs(states['initial'])==obs(states['granted'])
    assert results['initial']['next_outcome']=='deny' and results['granted']['next_outcome']=='commit'
    diagnostic=m.observational_equivalence({m.key(s):m.Node(paths[name],s) for name,s in states.items()})
    assert diagnostic['equivalent'] is False
    extended={name:(obs(s),tuple(s.wu(w).grants for w in m.WORLDS)) for name,s in states.items()}
    assert extended['initial']!=extended['granted']
    print(json.dumps(dict(schema='ases.f1-observation-witness.v1',execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                         source_hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('round2_observation_witness.py','phase_i_f1_model.py')},
                         environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()),
                         histories=results,original_diagnostic=diagnostic,grants_distinguish_this_pair=True,
                         qualification='two original reachable histories, adequate next-use difference omitted from diagnostic Obs; no general sufficient/minimal representation or product defect/full F1 closure'),indent=2,sort_keys=True))
if __name__=='__main__':main()
