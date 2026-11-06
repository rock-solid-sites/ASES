#!/usr/bin/env python3
"""Bounded abstract F1 C11 and F3 L5/L6 state-space exploration.

Separate executable reference models and invariants, not an implementation proof.
"""
import argparse
from collections import deque
from dataclasses import dataclass, replace
import json


@dataclass(frozen=True)
class F1:
    content: int = 0
    evidence: tuple = (0, "genesis")
    pending: str = ""
    staged: tuple = ()
    committed: tuple = ((0, "genesis"),)
    acked: tuple = ()
    online: bool = True


def f1_step(s, e, mutant="none"):
    if e.startswith("begin_"):
        return replace(s, pending=e[-1], staged=()) if s.online and not s.pending else None
    if e == "stage_evidence":
        if not s.online or not s.pending:
            return None
        return replace(s, staged=(0 if mutant == "misbound_evidence" else 1, s.pending))
    if e == "commit":
        if not s.online or not s.pending:
            return None
        if mutant == "split_commit":
            return replace(s, content=1, pending="", staged=())
        if s.staged != (1, s.pending) and not (mutant == "misbound_evidence" and s.staged):
            return None
        return replace(s, content=1, evidence=s.staged, pending="", staged=(),
                       committed=s.committed + (s.staged,))
    if e == "ack":
        if not s.online:
            return None
        if mutant == "premature_ack" and s.pending:
            return replace(s, acked=s.acked + ((1, s.pending),))
        if s.pending or s.evidence not in s.committed:
            return None
        return replace(s, acked=s.acked + (s.evidence,))
    if e == "crash":
        return replace(s, online=False, pending="", staged=()) if s.online else None
    if e == "restart":
        return replace(s, online=True) if not s.online else None
    raise ValueError(e)


def f1_invariant(s):
    return (s.content == s.evidence[0] and
            all(binding in s.committed for binding in s.acked))


@dataclass(frozen=True)
class L5:
    selector: str = "old"
    parent_c: str = "P"
    ceiling_c: str = "read-write"
    ceiling_d: str = "read-write"
    sealed: bool = False
    prepared: bool = False
    active: bool = False
    forbidden_write: bool = False
    online: bool = True


def l5_step(s, e, mutant="none"):
    if e == "seal":
        return replace(s, sealed=True, active=False) if s.online and not s.sealed else None
    if e == "prepare_move":
        return replace(s, prepared=True) if s.online and s.sealed and s.selector == "old" else None
    if e == "publish":
        if not s.online or not s.prepared or s.selector != "old":
            return None
        if mutant == "split_publication":
            return replace(s, selector="new", parent_c="Q", prepared=False)
        return replace(s, selector="new", parent_c="Q", ceiling_c="read",
                       ceiling_d="read", prepared=False)
    if e == "activate":
        return replace(s, active=True) if s.online and s.sealed and not s.active else None
    if e == "write_D":
        if not s.online or not s.active:
            return None
        if s.ceiling_d != "read-write" and mutant != "bypass_ceiling":
            return None
        return replace(s, forbidden_write=s.forbidden_write or s.selector == "new")
    if e == "crash":
        return replace(s, online=False, active=False, prepared=False) if s.online else None
    if e == "restart":
        return replace(s, online=True) if not s.online else None
    raise ValueError(e)


def l5_invariant(s):
    return (not s.forbidden_write and
            (s.selector != "new" or (s.parent_c == "Q" and
                                     s.ceiling_c == "read" and s.ceiling_d == "read")))


@dataclass(frozen=True)
class L6:
    live: bool = True
    dependency: bool = False
    lock_held: bool = False
    removing: bool = False
    scanned_empty: bool = False
    removed: bool = False
    creator_denied: bool = False
    online: bool = True


def l6_step(s, e, mutant="none"):
    if e == "begin_remove":
        return replace(s, removing=True, lock_held=mutant != "detached_scan") if s.online and s.live and not s.removing else None
    if e == "scan_empty":
        return replace(s, scanned_empty=True) if s.online and s.removing and not s.dependency else None
    if e == "creator_commit":
        if not s.online or not s.live:
            return None
        return replace(s, creator_denied=True) if s.lock_held else replace(s, dependency=True)
    if e == "remove":
        if not s.online or not s.removing or not s.scanned_empty:
            return None
        if mutant != "detached_scan" and (not s.lock_held or s.dependency):
            return None
        return replace(s, live=False, removed=True, removing=False,
                       lock_held=False, scanned_empty=False)
    if e == "crash":
        return replace(s, online=False, removing=False, scanned_empty=False,
                       lock_held=False) if s.online else None
    if e == "restart":
        return replace(s, online=True) if not s.online else None
    raise ValueError(e)


def l6_invariant(s):
    return not (s.removed and s.dependency)


SPECS = {
    "f1": (F1(), ("begin_A", "begin_B", "stage_evidence", "commit", "ack", "crash", "restart"),
           f1_step, f1_invariant, ("split_commit", "premature_ack", "misbound_evidence"), 7),
    "f3-l5": (L5(), ("seal", "prepare_move", "publish", "activate", "write_D", "crash", "restart"),
              l5_step, l5_invariant, ("split_publication", "bypass_ceiling"), 8),
    "f3-l6": (L6(), ("begin_remove", "scan_empty", "creator_commit", "remove", "crash", "restart"),
              l6_step, l6_invariant, ("detached_scan",), 8),
}


def explore(spec, mutant="none"):
    initial, events, transition, invariant, _, bound = spec
    frontier = deque([(initial, ())])
    seen = {initial}
    checked = 0
    while frontier:
        state, path = frontier.popleft()
        if len(path) == bound:
            continue
        for event in events:
            nxt = transition(state, event, mutant)
            if nxt is None:
                continue
            checked += 1
            witness = path + (event,)
            if not invariant(nxt):
                return {"safe": False, "counterexample": list(witness),
                        "counterexample_state": nxt.__dict__,
                        "depth": len(witness), "states_seen": len(seen),
                        "transitions_checked": checked}
            if nxt not in seen:
                seen.add(nxt)
                frontier.append((nxt, witness))
    return {"safe": True, "depth_bound": bound,
            "states_seen": len(seen), "transitions_checked": checked}


def trace(spec, events):
    state = spec[0]
    for event in events:
        nxt = spec[2](state, event)
        assert nxt is not None, (events, event, state)
        state = nxt
    return state


def run(name):
    spec = SPECS[name]
    valid = explore(spec)
    assert valid["safe"] and valid["transitions_checked"] > 0, valid
    unsafe = {}
    for mutant in spec[4]:
        result = explore(spec, mutant)
        assert not result["safe"] and result["counterexample"], (name, mutant, result)
        unsafe[mutant] = result
    if name == "f1":
        for world in ("A", "B"):
            result = trace(spec, ("begin_" + world, "stage_evidence", "commit", "ack", "crash", "restart"))
            assert result.content == 1 and result.evidence == (1, world) and result.acked[-1] == (1, world)
        assert trace(spec, ("begin_A", "crash", "restart")).evidence == (0, "genesis")
    elif name == "f3-l5":
        moved = trace(spec, ("seal", "prepare_move", "publish", "crash", "restart", "activate"))
        assert moved.selector == "new" and moved.ceiling_d == "read"
        assert spec[2](moved, "write_D") is None
        assert trace(spec, ("seal", "prepare_move", "crash", "restart")).selector == "old"
    else:
        removal = trace(spec, ("begin_remove", "scan_empty", "creator_commit", "remove"))
        assert removal.removed and not removal.dependency and removal.creator_denied
        prior_creator = trace(spec, ("creator_commit", "begin_remove"))
        assert spec[2](prior_creator, "scan_empty") is None
    return {"model": name, "valid": valid, "unsafe_mutants": unsafe,
            "positive_neighbors_checked": True,
            "scope": "bounded abstract state model only; not concrete implementation refinement or power-loss proof"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=tuple(SPECS) + ("all",), default="all")
    args = p.parse_args()
    result = [run(n) for n in SPECS] if args.model == "all" else run(args.model)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
