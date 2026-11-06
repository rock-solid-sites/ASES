#!/usr/bin/env python3
"""Bounded cross-boundary F1/F3/F4 composition model, not a native integration proof.

The source-specific probes use different fixture identities and runtimes. These
synthetic transitions describe proposed cross-component contracts only.
"""
import argparse
from collections import deque
from dataclasses import dataclass, replace
import json

DEPTH=13
EVENTS=("accept_pair","ack_accept","attach_object","seal_unit","move_whole",
        "activate","write_d","append_event","publish","ack_publication",
        "lose_receipt","recheck_cut","revoke_writer","restart","crash","remove_unit")

@dataclass(frozen=True)
class S:
    content: int=0
    evidence: int=0
    f1_ack: int=0
    object: int=0
    sealed: bool=False
    moved: bool=False
    ceiling: str="rw"
    active: bool=False
    forbidden_effect: bool=False
    removed: bool=False
    local: int=0
    published: int=0
    ack: int=0
    ack_validated: bool=False
    witness_revision: int=0
    owner_epoch: int=1
    writer_epoch: int=1
    receipt_lost: bool=False
    rechecked: bool=False
    online: bool=True

def step(s,e,mutant=""):
    if e=="accept_pair":
        if not s.online or s.content: return None
        return replace(s,content=1,evidence=0 if mutant=="split_accept" else 1)
    if e=="ack_accept":
        if not s.online or s.f1_ack or not s.content: return None
        if not s.evidence and mutant!="ack_without_evidence": return None
        return replace(s,f1_ack=1)
    if e=="attach_object":
        if not s.online or s.object or (not s.f1_ack and mutant!="unbound_import"): return None
        return replace(s,object=1)
    if e=="seal_unit":
        if not s.online or not s.object or s.sealed: return None
        return replace(s,sealed=True)
    if e=="move_whole":
        if not s.online or not s.sealed or s.moved or s.removed: return None
        return replace(s,moved=True,ceiling="rw" if mutant=="split_move" else "read")
    if e=="activate":
        if not s.online or not s.sealed or s.active or s.removed: return None
        return replace(s,active=True)
    if e=="write_d":
        if not s.online or not s.active or not s.object or s.removed: return None
        if s.moved and mutant!="write_after_move": return None
        return replace(s,forbidden_effect=s.forbidden_effect or s.moved)
    if e=="append_event":
        if not s.online or not s.object or not s.f1_ack or not s.active or s.local or s.removed: return None
        return replace(s,local=1)
    if e=="publish":
        if not s.online or s.published or (not s.local and mutant!="uncommitted_publish"):
            return None
        if s.owner_epoch!=s.writer_epoch: return None
        return replace(s,published=1,witness_revision=s.witness_revision+1,rechecked=False)
    if e=="ack_publication":
        if not s.online or s.ack: return None
        matched=(s.local==s.published==1 and s.owner_epoch==s.writer_epoch)
        if not matched and mutant!="premature_ack": return None
        return replace(s,ack=1,ack_validated=matched)
    if e=="lose_receipt":
        if not s.online or not s.published or s.receipt_lost or s.ack: return None
        if mutant=="lost_receipt_is_ack":
            return replace(s,receipt_lost=True,ack=1,ack_validated=False)
        return replace(s,receipt_lost=True)
    if e=="recheck_cut":
        if not s.online or not s.receipt_lost or s.rechecked: return None
        if s.owner_epoch!=s.writer_epoch and mutant!="stale_recheck": return None
        return replace(s,rechecked=True,ack_validated=False)
    if e=="revoke_writer":
        if not s.online or s.owner_epoch>1: return None
        return replace(s,owner_epoch=2)
    if e=="crash":
        return replace(s,online=False) if s.online else None
    if e=="restart":
        return replace(s,online=True) if not s.online else None
    if e=="remove_unit":
        if not s.online or s.removed or not s.sealed: return None
        if s.object and mutant!="orphan_removal": return None
        return replace(s,removed=True)
    raise ValueError(e)

def invariant(s):
    return (s.evidence==s.content and
            (not s.f1_ack or s.content==s.evidence==1) and
            (not s.object or s.f1_ack==1) and
            (not s.moved or (s.sealed and s.ceiling=="read")) and
            not s.forbidden_effect and
            not (s.removed and s.object) and
            s.ack<=s.published<=s.local<=s.object and
            (not s.ack or s.ack_validated) and
            s.witness_revision>=s.published)

def search(mutant="",depth=DEPTH):
    initial=S()
    visited={initial}
    todo=deque([(initial,())])
    transitions=0
    max_depth=0
    while todo:
        state,history=todo.popleft()
        max_depth=max(max_depth,len(history))
        if len(history)>=depth:continue
        for event in EVENTS:
            next_state=step(state,event,mutant)
            if next_state is None:continue
            transitions+=1
            seq=history+(event,)
            if not invariant(next_state):
                return {"safe":False,"counterexample":list(seq),
                        "counterexample_state":next_state.__dict__,
                        "transitions":transitions,"states":len(visited),"depth":len(seq)}
            if next_state not in visited:
                visited.add(next_state)
                todo.append((next_state,seq))
    return {"safe":True,"states":len(visited),"transitions":transitions,"depth_bound":depth,
            "max_reached_depth":max_depth}

MUTANTS=("split_accept","ack_without_evidence","unbound_import","split_move",
         "write_after_move","uncommitted_publish","premature_ack",
         "lost_receipt_is_ack","orphan_removal")

def validate_neighbors():
    cases={
        "normal_ack":("accept_pair","ack_accept","attach_object","seal_unit",
                      "activate","append_event","publish","ack_publication"),
        "move_then_recover":("accept_pair","ack_accept","attach_object","seal_unit",
                             "move_whole","crash","restart","activate","append_event","publish"),
        "receipt_loss_then_check":("accept_pair","ack_accept","attach_object",
                                  "seal_unit","activate","append_event","publish","lose_receipt","recheck_cut"),
        "fenced_writer":("accept_pair","ack_accept","attach_object","seal_unit",
                         "activate","append_event","revoke_writer"),
    }
    final={}
    for name,history in cases.items():
        s=S()
        for event in history:
            t=step(s,event)
            assert t is not None,(name,event)
            assert invariant(t),(name,event,t)
            s=t
        if name=="fenced_writer":
            assert step(s,"publish") is None,"stale owner published"
        if name=="move_then_recover":
            assert step(s,"write_d") is None,"moved work unit wrote"
        final[name]={"events":len(history),"safe":True}
    return final

def run():
    valid=search()
    assert valid["safe"] and valid["transitions"]>=100,valid
    mutants={}
    for variant in MUTANTS:
        result=search(variant)
        assert not result["safe"] and result["counterexample"],(variant,result)
        mutants[variant]=result
    return {"claim":"bounded typed F1->F3->F4 composition safety obligations",
            "valid":valid,"unsafe_variants":mutants,"valid_neighbors":validate_neighbors(),
            "assurance":"SYNTHETIC_ONLY",
            "limitations":"No native interoperation, common real fixture, refinement relation, nonrollback witness, or crash-durability proof"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--depth",type=int,default=DEPTH)
    a=p.parse_args()
    if a.depth!=DEPTH: raise SystemExit("depth bound frozen at 13 for this campaign")
    print(json.dumps(run(),sort_keys=True,indent=2))
