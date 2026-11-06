"""Bounded independent state explorer for Phase I authority/publication semantics.

This is an abstract reference model, not the original implementation/checker.
Exhaustively enumerate event strings to depth 7; fail on safety invariant breach.
A deliberately unsafe mutation must produce a counterexample.
"""
from dataclasses import dataclass, replace
from itertools import product
import json

EVENTS=("commit", "publish", "ack", "lose_receipt", "restart", "competing_writer", "check")
DEPTH=7

@dataclass(frozen=True)
class State:
    local: int=0
    published: int=0
    acknowledged: int=0
    writer: int=1
    refused: bool=False
    ambiguity: bool=False

def transition(s,event,unsafe=False):
    if event=="commit":
        return replace(s,local=s.local+1) if not s.refused else s
    if event=="publish":
        return replace(s,published=s.local) if not s.refused and s.writer==1 else s
    if event=="ack":
        if unsafe: return replace(s,acknowledged=s.local)
        return replace(s,acknowledged=s.local) if not s.refused and s.published==s.local else s
    if event=="lose_receipt":
        return replace(s,ambiguity=True)
    if event=="restart":
        return replace(s,refused=s.published!=s.local)
    if event=="competing_writer":
        return replace(s,writer=2,refused=True)
    if event=="check":
        return replace(s,ambiguity=False) if s.published==s.local else s
    raise ValueError(event)

def safety(s):
    return s.acknowledged<=s.published<=s.local

def explore(unsafe=False):
    reached={State()}
    paths={State():()}
    checked=0
    for depth in range(1,DEPTH+1):
        nxt=set()
        for s in reached:
            for event in EVENTS:
                t=transition(s,event,unsafe)
                checked+=1
                path=paths[s]+(event,)
                if not safety(t):
                    return {"safe":False,"counterexample":list(path),"state":t.__dict__,
                            "depth":depth,"transitions_checked":checked}
                if t not in paths:paths[t]=path
                nxt.add(t)
        reached=nxt
    return {"safe":True,"depth":DEPTH,"distinct_states":len(paths),
            "transitions_checked":checked}

def main():
    good=explore(False)
    mutant=explore(True)
    assert good["safe"],good
    assert not mutant["safe"],"unsafe premature-ACK mutant escaped"
    assert mutant["counterexample"],mutant
    print(json.dumps({"model":"abstract F4 local/published/ack cut",
                      "guarantee":"acknowledged <= published <= local",
                      "valid_model":good,"unsafe_mutant":mutant,
                      "scope":"bounded depth 7, finite event alphabet; not implementation refinement or distributed durability proof"},indent=2))

if __name__=="__main__":main()
