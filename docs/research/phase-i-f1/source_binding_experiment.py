#!/usr/bin/env python3
"""Exhaust a tiny source-binding extension around the inherited F1 guard."""
from collections import deque
from dataclasses import dataclass
import json
import phase_i_f1_model as f1

LIMIT = 100
CASES = (("replacement_current", "replacement", f1.B_GEN),
         ("old_with_current", "old", f1.B_GEN),
         ("replacement_stale", "replacement", f1.B_GEN - 1))

@dataclass(frozen=True)
class Fixture:
    attempted: int = 0
    accepted: int = 0


def setup():
    state = f1.initial()
    for event in (("grant", f1.P, f1.SINK, f1.RW),
                  ("grant", f1.C, f1.SINK, f1.RW)):
        outcome, state, reason = f1.resolve(state, event, f1.REFERENCE)
        if outcome != "commit":
            raise RuntimeError((event, outcome, reason))
    return state


def evaluate(state, source, generation, binding):
    event = ("use", f1.C, f1.SINK, f1.W, generation)
    reason = f1.guard(state, event, f1.REFERENCE)
    if reason:
        return "deny", reason
    if binding and source != "replacement":
        return "deny", "source-association-mismatch"
    outcome, _, reason = f1.resolve(state, event, f1.REFERENCE)
    return outcome, reason


def search(binding):
    state = setup()
    start = Fixture()
    queue = deque([start])
    seen = {start}
    attempts = commits = denies = violations = 0
    denied_by = {}
    witnesses = {}
    truncated = False
    while queue:
        node = queue.popleft()
        for i, (name, source, generation) in enumerate(CASES):
            bit = 1 << i
            if node.attempted & bit:
                continue
            attempts += 1
            outcome, reason = evaluate(state, source, generation, binding)
            if outcome not in ("commit", "deny"):
                raise RuntimeError((name, outcome, reason))
            committed = outcome == "commit"
            commits += committed
            denies += not committed
            if reason:
                denied_by[reason] = denied_by.get(reason, 0) + 1
            # Observer is independent of the admission switch: it asks who
            # actually produced each accepted effect in the fixture premise.
            if committed and source == "old":
                violations += 1
            witnesses.setdefault(name, {"source": source, "generation": generation,
                                        "outcome": outcome, "reason": reason,
                                        "physical_source_invariant": not (committed and source == "old")})
            nxt = Fixture(node.attempted | bit, node.accepted | (bit if committed else 0))
            if nxt not in seen:
                if len(seen) >= LIMIT:
                    truncated = True
                    continue
                seen.add(nxt)
                queue.append(nxt)
    return {"binding_enforced": binding, "states": len(seen), "attempted_transitions": attempts,
            "committed_transitions": commits, "denied_transitions": denies,
            "violating_transitions": violations, "denied_by": denied_by,
            "state_limit": LIMIT, "truncated": truncated, "witnesses": witnesses}


def main():
    baseline, weakened = search(True), search(False)
    assert not baseline["truncated"] and not weakened["truncated"]
    assert baseline["violating_transitions"] == 0 and weakened["violating_transitions"] > 0
    assert baseline["witnesses"]["replacement_current"]["outcome"] == "commit"
    assert baseline["witnesses"]["old_with_current"]["reason"] == "source-association-mismatch"
    assert baseline["witnesses"]["replacement_stale"]["reason"].startswith("stale-evidence")
    assert weakened["witnesses"]["old_with_current"]["outcome"] == "commit"
    print(json.dumps({"baseline": baseline, "weakened_binding": weakened}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
