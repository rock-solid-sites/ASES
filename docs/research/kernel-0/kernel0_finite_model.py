#!/usr/bin/env python3
"""Finite research witness, not a service or a general Kernel-0 implementation.

Run with Python 3.10+: python3 kernel0_finite_model.py --output Kernel-0-Finite-Model-results.json
No dependencies, network, randomness, clocks, or persistent service state.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, fields, replace
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path


POSITIONS = (0, 0, 0, 1)  # Consumer interpretation only; contexts 0 -> 1 -> 2.
X, Y, CONTENT = 1, 2, 4
MANAGER = -1


@dataclass(frozen=True)
class Profile:
    name: str
    coupled: bool = False
    exclusive: bool = False


@dataclass(frozen=True)
class State:
    established: bool = False
    data: tuple[int, int] = (0, 0)
    content: int = -1  # -1 absent; 0 and 1 stand for two required byte strings.
    issued: int = 0  # Proof witness for non-reuse, not a mandated kernel record.
    rights: tuple[int, ...] = (0, 0, 0, 0)
    parents: tuple[int, ...] = (-1, -1, -1, -1)


@dataclass(frozen=True)
class Request:
    kind: str
    evidence: int = MANAGER
    target: int = 0
    value: int = 0
    other: int = 0
    authentic: bool = True

    def label(self):
        who = "management" if self.evidence == MANAGER else f"a{self.evidence}"
        return f"{self.kind}({who}, {self.target}, {self.value}, {self.other})"


def invariant(s: State, p: Profile) -> bool:
    if not s.established:
        return s == State()
    if s.content not in (0, 1) or any(d not in (0, 1) for d in s.data):
        return False
    if p.coupled and sum(s.data) > 1:
        return False
    active = [i for i, r in enumerate(s.rights) if r]
    if any(not s.issued & (1 << i) for i in active):
        return False
    if any(sum(POSITIONS[i] == pos for i in active) > 1 for pos in (0, 1)):
        return False
    if p.exclusive and len(active) > 1:
        return False
    for i, parent in enumerate(s.parents):
        if parent != -1:
            if i != 3 or parent not in (0, 1, 2) or not s.rights[i]:
                return False
            if s.rights[i] & ~s.rights[parent]:
                return False
    return all(0 <= r <= 7 for r in s.rights)


def candidate(s: State, q: Request, weakness: str = "") -> State | None:
    """Explicit consumer G and E. None means G fails; I is checked separately."""
    if not q.authentic and weakness != "forgery":
        return None
    k, a, t, v = q.kind, q.evidence, q.target, q.value
    if weakness == "confusion" and a in (0, 1, 2) and not s.rights[a]:
        a = next((i for i in (0, 1, 2) if s.rights[i]), a)
    management = a == MANAGER
    if k == "establish":
        return replace(s, established=True, content=0) if management and not s.established else None
    if not s.established:
        return None
    rights, parents = list(s.rights), list(s.parents)
    issued = s.issued

    def fresh(i):
        return not rights[i] and (weakness == "reuse" or not issued & (1 << i))

    def restrict(i, mask):
        rights[i] = mask
        if not mask:
            parents[i] = -1
        for child, parent in enumerate(parents):
            if parent == i:
                rights[child] &= mask  # Declared cascading attenuation policy.
                if not rights[child]:
                    parents[child] = -1

    if k == "grant":
        if not management or not fresh(t) or not 1 <= v <= 7:
            return None
        rights[t], parents[t], issued = v, -1, issued | (1 << t)
    elif k == "restrict":
        if not management or not rights[t] or v & ~rights[t]:
            return None
        restrict(t, v)
    elif k == "replace":
        new = q.other
        if not management or not rights[t] or not fresh(new) or POSITIONS[t] != POSITIONS[new]:
            return None
        previous = rights[t]
        restrict(t, 0)
        rights[new], parents[new], issued = previous, -1, issued | (1 << new)
    elif k == "delegate":
        if a not in (0, 1, 2) or t != 3 or not rights[a] or not fresh(t) or not 1 <= v <= 7:
            return None
        if v & ~rights[a] and weakness != "amplify":
            return None
        rights[t], parents[t], issued = v, a, issued | (1 << t)
    else:
        needed = {"set": 1 << t, "flip": 1 << t, "accept": CONTENT, "resume": X,
                  "pair": X | Y, "mixed": X}.get(k)
        if needed is None or a not in range(4) or needed & ~rights[a]:
            return None
        if k == "mixed":  # One proposal: set x=1 AND grant authority as a worker.
            return None
        if k == "accept":
            return replace(s, content=v)
        if k == "resume":
            # A consumer continuation uses the actual accepted content, not
            # merely the existence of a reference. Wrong/missing bytes deny.
            return replace(s, data=(v, s.data[1])) if v == s.content else None
        data = list(s.data)
        if k == "pair":
            data = [v & 1, (v >> 1) & 1]
        else:
            data[t] = v if k == "set" else 1 - data[t]
        return replace(s, data=tuple(data))
    return replace(s, rights=tuple(rights), parents=tuple(parents), issued=issued)


def resolve(s, q, p, weakness=""):
    out = candidate(s, q, weakness)
    if out is not None and (invariant(out, p) or weakness in ("amplify", "exclusivity")):
        return out, "commit"
    if weakness == "partial" and q.kind == "mixed" and s.rights[q.evidence] & X:
        return replace(s, data=(1, s.data[1])), "deny"
    return s, "deny"


def catalog():
    yield Request("establish")
    for a in range(4):
        for rights in range(1, 8):
            yield Request("grant", target=a, value=rights)
        for rights in range(8):
            yield Request("restrict", target=a, value=rights)
        for t, v in product(range(2), repeat=2):
            yield Request("set", a, t, v)
        for t in range(2):
            yield Request("flip", a, t)
        for v in range(2):
            yield Request("accept", a, value=v)
            yield Request("resume", a, value=v)
        for v in range(4):
            yield Request("pair", a, value=v)
        yield Request("mixed", a)
    for old, new in permutations(range(3), 2):
        yield Request("replace", target=old, other=new)
    for a, rights in product(range(3), range(1, 8)):
        yield Request("delegate", a, target=3, value=rights)


def check_edge(s, q, out, outcome, p):
    assert invariant(out, p), ("invariant", q, s, out)
    if outcome == "deny":
        assert out == s, ("denial mutated", q)
        return
    assert q.authentic
    assert s.issued & ~out.issued == 0
    if q.kind in ("grant", "restrict", "replace", "delegate"):
        assert (out.established, out.data, out.content) == (s.established, s.data, s.content)
    if q.kind in ("set", "flip", "pair", "accept", "resume"):
        assert (out.established, out.rights, out.parents, out.issued) == (
            s.established, s.rights, s.parents, s.issued)
        needed = CONTENT if q.kind == "accept" else X | Y if q.kind == "pair" else 1 << q.target
        assert s.rights[q.evidence] & needed == needed
        if q.kind == "resume":
            assert q.value == s.content and out.data[0] == s.content
        if q.kind in ("set", "flip"):
            expected = q.value if q.kind == "set" else 1 - s.data[q.target]
            assert out.data[q.target] == expected and out.data[1 - q.target] == s.data[1 - q.target]
        if q.kind == "pair":
            assert out.data == (q.value & 1, (q.value >> 1) & 1)
        if q.kind == "accept":
            assert out.content == q.value and out.data == s.data
        else:
            assert out.content == s.content
    if q.kind in ("establish", "grant", "restrict", "replace"):
        assert q.evidence == MANAGER
    if q.kind in ("grant", "delegate"):
        assert not s.issued & (1 << q.target)
    if q.kind == "replace":
        assert not s.issued & (1 << q.other)
        assert not out.rights[q.target]
    if q.kind == "delegate":
        assert out.rights[q.target] & ~s.rights[q.evidence] == 0


def authoritative_graph(p):
    requests = tuple(catalog())
    queue, seen = deque([State()]), {State()}
    counts = {"states": 0, "edges": 0, "commit_edges": 0, "deny_edges": 0}
    kinds = set()
    while queue:
        s = queue.popleft()
        counts["states"] += 1
        for q in requests:
            out, outcome = resolve(s, q, p)
            check_edge(s, q, out, outcome, p)
            counts["edges"] += 1
            counts[outcome + "_edges"] += 1
            if outcome == "commit":
                kinds.add(q.kind)
            if out not in seen:
                seen.add(out)
                queue.append(out)
    assert {"establish", "grant", "restrict", "replace", "set", "flip", "pair", "accept", "resume"} <= kinds
    if not p.exclusive:
        assert "delegate" in kinds
    return dict(profile=p.name, requests_per_state=len(requests), committed_kinds=sorted(kinds), **counts)


def established(*grants, p=Profile("independent")):
    s, outcome = resolve(State(), Request("establish"), p)
    assert outcome == "commit"
    for a, rights in grants:
        s, outcome = resolve(s, Request("grant", target=a, value=rights), p)
        assert outcome == "commit"
    return s


def apply_trace(s, requests, p, weakness=""):
    trace = []
    for q in requests:
        before = s
        s, outcome = resolve(s, q, p, weakness)
        trace.append({"event": q.label(), "outcome": outcome,
                      "before": asdict(before), "after": asdict(s)})
    return s, trace


def merge_effect(current, observed, proposed):
    """Deliberately broken detached validation: apply old-view writes now."""
    changes = {}
    for f in fields(State):
        old, new, now = getattr(observed, f.name), getattr(proposed, f.name), getattr(current, f.name)
        if isinstance(old, tuple):
            changes[f.name] = tuple(n if n != o else c for o, n, c in zip(old, new, now))
        elif f.name == "issued":
            changes[f.name] = now | new
        else:
            changes[f.name] = new if old != new else now
    return replace(current, **changes)


@dataclass(frozen=True)
class Flight:
    state: State
    phases: tuple[int, ...]  # 0 unstarted, 1 submitted, 2 observed, 3 resolved, 4 reply, 5 reply lost
    observations: tuple[State | None, ...]
    outcomes: tuple[str, ...]
    alive: int
    before: frozenset[tuple[int, int]] = frozenset()  # Response-before-invocation edges.


def flight_explore(name, initial, requests, owners, p, weakness="", death=True, replay_after=False):
    """Enumerate all reachable interleavings, including all executor death cuts.

    Submission copies the complete proposal into the retained boundary. All
    executor-only evidence/candidate material is represented by alive; death
    clears it. Submitted copies are not executor-owned. Pre-submit death can
    leave an operation permanently unstarted. No fairness is assumed.
    """
    n = len(requests)
    alive = sum(1 << e for e in set(owners) if e >= 0)
    start = Flight(initial, (0,) * n, (None,) * n, ("",) * n, alive)
    queue, parents = deque([start]), {start: None}
    edges, commits, denials, losses = 0, 0, 0, 0
    seen_results, violation = set(), None

    def path(node):
        result = []
        while parents[node] is not None:
            prev, label = parents[node]
            result.append(label)
            node = prev
        return list(reversed(result))

    def add(s, out, label):
        nonlocal edges
        edges += 1
        if out not in parents:
            parents[out] = s, label
            queue.append(out)

    while queue:
        s = queue.popleft()
        seen_results.add((s.outcomes, s.state.data))
        for i, q in enumerate(requests):
            phase = s.phases[i]
            phases, obs, results = list(s.phases), list(s.observations), list(s.outcomes)
            owner_live = owners[i] < 0 or bool(s.alive & (1 << owners[i]))
            out, precedence = s.state, s.before
            if phase == 0:
                if not owner_live or replay_after and i == 1 and s.phases[0] != 5:
                    continue
                precedence |= frozenset((j, i) for j in range(n) if s.phases[j] == 4)
                label = f"{i}: invoke/copy {q.label()}"
                phases[i] = 1
            elif phase == 1:
                obs[i], phases[i] = s.state, 2
                label = f"{i}: observe {s.state}"
            elif phase == 2:
                expected = resolve(s.state, q, p)
                if weakness == "stale_view":
                    proposed, result = resolve(obs[i], q, p)
                    out = merge_effect(s.state, obs[i], proposed) if result == "commit" else s.state
                else:
                    out, result = resolve(s.state, q, p, weakness)
                if (out, result) != expected and violation is None:
                    violation = {"trace": path(s) + [f"{i}: {result} -> {out}"],
                                 "current_view_requires": expected[1],
                                 "expected_state": asdict(expected[0]), "actual_state": asdict(out)}
                if not weakness:
                    check_edge(s.state, q, out, result, p)
                commits += result == "commit"
                denials += result == "deny"
                results[i], phases[i] = result, 3
                label = f"{i}: {result} -> {out}"
            elif phase == 3:
                phases[i] = 5
                lost = replace(s, phases=tuple(phases))
                add(s, lost, f"{i}: acknowledgement lost")
                losses += 1
                if not owner_live:
                    continue
                phases[i] = 4
                label = f"{i}: acknowledgement delivered"
            else:
                continue
            add(s, Flight(out, tuple(phases), tuple(obs), tuple(results), s.alive, precedence), label)
        if death:
            for e in range(4):
                if s.alive & (1 << e):
                    out = replace(s, alive=s.alive & ~(1 << e))
                    assert out.state == s.state  # Authority is NOT implicitly revoked by death.
                    add(s, out, f"lose executor {e}: erase all its private material")
    if weakness:
        assert violation is not None, ("mutant survived", name, weakness)
    else:
        assert violation is None
    return {"name": name, "weakness": weakness or None, "states": len(parents), "edges": edges,
            "commit_edges": commits, "deny_edges": denials, "lost_ack_edges": losses,
            "both_commit_reachable": any(all(o == "commit" for o in outcomes) for outcomes, _ in seen_results),
            "repeated_flip_returns_to_start": all(q.kind == "flip" for q in requests) and any(
                all(o == "commit" for o in outcomes) and data == initial.data for outcomes, data in seen_results),
            "counterexample": violation}


def serial_witness(initial, operations, accepted, precedence, final=None):
    """Independent history oracle: search all orders; input edges may be cyclic.

    Operations are tiny (guard, effect) functions, separate from State/resolve.
    A witness is an order of the entire accepted set, never pairwise voting.
    """
    for order in permutations(accepted):
        rank = {a: i for i, a in enumerate(order)}
        if any(a in rank and b in rank and rank[a] >= rank[b] for a, b in precedence):
            continue
        s = initial
        for i in order:
            guard, effect = operations[i]
            if not guard(s):
                break
            s = effect(s)
        else:
            if final is None or s == final:
                return list(order)
    return None


def history_attacks():
    counts = {"cases": 0, "accepted": 0, "rejected": 0, "pairwise_false_positives": 0}
    directed = tuple(permutations(range(3), 2))
    cycle_example = None
    # Enumerate all eight required observation patterns, all accepted
    # subsets, and all 64 precedence relations INCLUDING the cyclic ones.
    for expected in product((0, 1), repeat=3):
        operations = []
        for i in range(3):
            read = (i + 1) % 3
            operations.append((lambda s, r=read, v=expected[i]: s[r] == v,
                               lambda s, w=i: tuple(1 if j == w else v for j, v in enumerate(s))))
        for mask in range(8):
            accepted = tuple(i for i in range(3) if mask & (1 << i))
            for bits in range(64):
                edges = frozenset(e for j, e in enumerate(directed) if bits & (1 << j))
                witness = serial_witness((0, 0, 0), operations, accepted, edges)
                # A second algorithm derives necessary read/write constraints
                # and removes vertices with no predecessors. Compare it with
                # full serial execution, not with the scheduling loop.
                dependencies = {(a, b) for a, b in edges if a in accepted and b in accepted}
                possible = True
                for reader in accepted:
                    writer = (reader + 1) % 3
                    if writer in accepted:
                        dependencies.add((writer, reader) if expected[reader] else (reader, writer))
                    elif expected[reader]:
                        possible = False
                remaining = set(accepted)
                while remaining:
                    roots = {a for a in remaining if not any(b in remaining and c == a for b, c in dependencies)}
                    if not roots:
                        break
                    remaining -= roots
                assert (witness is not None) == (possible and not remaining)
                pairwise = all(serial_witness((0, 0, 0), operations, pair, edges) is not None
                               for pair in combinations(accepted, 2))
                # Singleton validity is also required of the deliberately weak checker.
                pairwise &= all(serial_witness((0, 0, 0), operations, (i,), edges) is not None for i in accepted)
                counts["cases"] += 1
                counts["accepted" if witness is not None else "rejected"] += 1
                if pairwise and witness is None:
                    counts["pairwise_false_positives"] += 1
                    if expected == (0, 0, 0) and mask == 7 and bits == 0:
                        cycle_example = {"observations": ["A: y=0", "B: z=0", "C: x=0"],
                                         "effects": ["A: x=1", "B: y=1", "C: z=1"],
                                         "required_order": ["A<B", "B<C", "C<A"],
                                         "pair_orders": [[0, 1], [1, 2], [2, 0]],
                                         "weak_trace": ["initiate A, B, C", "observe all guards at (0,0,0)",
                                                        "apply A from old observation", "apply B from old observation",
                                                        "apply C from old observation: (1,1,1)"],
                                         "whole_set_witness": witness}
    assert cycle_example is not None
    # Revocation is completed before an affected request is initiated.
    operations = [(lambda s: True, lambda s: (False, s[1])),
                  (lambda s: s[0], lambda s: (s[0], 1))]
    overlapping = serial_witness((True, 0), operations, (0, 1), frozenset())
    completed_first = serial_witness((True, 0), operations, (0, 1), frozenset({(0, 1)}))
    assert overlapping == [1, 0] and completed_first is None
    # A coherent view cannot be assembled from individually truthful components.
    views = [(True, 0), (False, 0), (False, 1)]
    torn = [(a, b) for a in range(3) for b in range(3) if views[a][0] and views[b][1] == 1]
    assert torn == [(0, 2)] and not any(a and b == 1 for a, b in views)
    return dict(counts, cycle=cycle_example,
                real_time={"overlapping_order": overlapping, "completed_before_initiated_order": completed_first},
                torn_view={"coherent_views": views, "false_admission_by_components": torn})


@dataclass(frozen=True)
class ContentState:
    current: bool = True
    alive: bool = True
    private: int = 0
    accepted: int = -1  # Accepted identity/hash alone in the local-reference mutant.
    retained: int = -1
    replacement: bool = False
    resumed: int = -1


def content_explore(mode):
    def meaning(s):
        if s.accepted == -1:
            return -1
        return s.retained if mode == "copy" else s.private

    start = ContentState()
    queue, paths = deque([start]), {start: []}
    edges, violation, stale_violation, continuation = 0, None, None, None
    while queue:
        s = queue.popleft()
        transitions = []
        if s.alive:
            if mode != "hash_only" or s.accepted == -1:
                transitions.extend((f"private candidate := {v}", replace(s, private=v), False) for v in (0, 1))
            transitions.append(("lose executor and ALL private bytes", replace(s, alive=False, private=-1), False))
        if s.alive and s.current:
            transitions.append(("guarded accept", replace(s, accepted=s.private,
                                                          retained=s.private if mode == "copy" else -1), True))
        if s.current:
            transitions.append(("guarded revoke", replace(s, current=False), True))
        if not s.replacement:
            transitions.append(("guarded replacement with fresh evidence", replace(s, current=False, replacement=True), True))
        if s.replacement and meaning(s) != -1:
            transitions.append(("replacement consumes required accepted bytes", replace(s, resumed=meaning(s)), True))
        for label, out, guarded in transitions:
            edges += 1
            bad = (not guarded and meaning(s) != meaning(out)) or (out.accepted != -1 and meaning(out) == -1)
            if mode == "hash_only":
                # This mutant promises an immutable reference but loses its only holder.
                bad = out.accepted != -1 and meaning(out) == -1
            if bad and violation is None:
                violation = {"trace": paths[s] + [label], "before": asdict(s), "after": asdict(out),
                             "meaning_before": meaning(s), "meaning_after": meaning(out)}
            if bad and not s.current and label.startswith("private candidate") and stale_violation is None:
                stale_violation = {"trace": paths[s] + [label], "before": asdict(s), "after": asdict(out)}
            if label == "replacement consumes required accepted bytes" and not s.alive and out.resumed == out.accepted == 1 and continuation is None:
                continuation = paths[s] + [label]
            if out not in paths:
                paths[out] = paths[s] + [label]
                queue.append(out)
    assert (violation is None) == (mode == "copy")
    if mode == "copy":
        assert continuation is not None
    else:
        assert continuation is None
    if mode == "live":
        assert stale_violation is not None
    return {"mode": mode, "states": len(paths), "edges": edges, "counterexample": violation,
            "stale_writer_counterexample": stale_violation, "continuation_after_loss": continuation}


def direct_witnesses():
    p = Profile("independent")
    s = State()
    sequence = [Request("establish"), Request("grant", target=0, value=7),
                Request("set", 0, 0, 1), Request("accept", 0, value=1),
                Request("replace", target=0, other=1), Request("resume", 1, value=1), Request("flip", 1, 0),
                Request("replace", target=1, other=2), Request("set", 2, 0, 1),
                Request("grant", target=3, value=Y), Request("set", 3, 1, 1)]
    final, successful = apply_trace(s, sequence, p)
    assert all(t["outcome"] == "commit" for t in successful)
    assert final.data == (1, 1) and final.content == 1 and final.rights == (0, 0, 7, Y)
    base = established((0, 7))
    tests = {}
    variants = {
        "confusion": [Request("replace", target=0, other=1), Request("set", 0, 0, 1)],
        "reuse": [Request("restrict", target=0, value=0), Request("grant", target=0, value=7), Request("set", 0, 0, 1)],
        "partial": [Request("mixed", 0)],
        "forgery": [Request("set", 0, 0, 1, authentic=False)],
        "amplify": [Request("restrict", target=0, value=X), Request("delegate", 0, 3, 7)],
        "exclusivity": [Request("grant", target=3, value=Y)],
    }
    for weakness, qs in variants.items():
        profile = Profile("exclusive", exclusive=True) if weakness == "exclusivity" else p
        good, reference = apply_trace(base, qs, profile)
        bad, mutant = apply_trace(base, qs, profile, weakness)
        assert bad != good, weakness
        tests[weakness] = {"reference": reference, "mutant": mutant}
    # Same observable evidence cannot yield the required two different answers.
    admission_tables = [{"answer_for_shared_observation": answer,
                         "old_denied": not answer, "replacement_admitted": answer} for answer in (False, True)]
    assert not any(t["old_denied"] and t["replacement_admitted"] for t in admission_tables)
    # A physical old producer with genuinely new transferable evidence is eligible.
    replaced, _ = apply_trace(base, [Request("replace", target=0, other=1)], p)
    refreshed, refresh_trace = apply_trace(replaced, [Request("set", 1, 0, 1)], p)
    assert refreshed.data == (1, 0)  # Deliberately no physical-source exclusion claim.
    # Split a declared pair effect and lose the executor before completing/recording it.
    proposed = candidate(base, Request("pair", 0, value=3))
    partial = replace(base, data=(1, 0))
    assert partial not in (base, proposed)
    crash_cuts = []
    for old, new in product(product((0, 1), repeat=2), repeat=2):
        for cut in range(3):
            visible = tuple(new[i] if i < cut else old[i] for i in range(2))
            if visible not in (old, new):
                crash_cuts.append({"before": old, "whole": new, "writes_before_loss": cut, "partial": visible})
    assert len(crash_cuts) == 4  # All 16 before/after pairs, all 3 death cuts.
    declared, retargeted = Request("set", 0, 0, 0), Request("set", 0, 0, 1)
    intended, _ = resolve(base, declared, p)
    swapped, _ = resolve(base, retargeted, p)
    assert intended != swapped and invariant(swapped, p)
    # These are reachable pairs, not invented invalid states. Erasing the
    # named distinction collapses histories with different future behavior.
    revoked, _ = apply_trace(base, [Request("restrict", target=0)], p)
    independent_child, _ = apply_trace(base, [Request("grant", target=3, value=Y)], p)
    delegated_child, _ = apply_trace(base, [Request("delegate", 0, 3, Y)], p)
    distinctions = []
    for name, left, right, q, profile in [
        ("issued versus never issued", established(), revoked, Request("grant", target=0, value=7), p),
        ("current authority scope", established((0, X)), established((0, Y)), Request("set", 0, 0, 1), p),
        ("delegation dependency", independent_child, delegated_child, Request("restrict", target=0), p),
        ("required accepted content", base, replace(base, content=1), Request("resume", 0, value=1), p),
        ("invariant-relevant work field", base, replace(base, data=(1, 0)), Request("set", 0, 1, 1), Profile("coupled", coupled=True)),
    ]:
        l, r = resolve(left, q, profile), resolve(right, q, profile)
        assert invariant(left, profile) and invariant(right, profile) and l != r
        distinctions.append({"distinction": name, "left": asdict(left), "right": asdict(right),
                             "future_request": q.label(), "left_result": [asdict(l[0]), l[1]],
                             "right_result": [asdict(r[0]), r[1]]})
    # Superseded requests remain stale even after a second replacement.
    old_requests = [Request("set", 0, 0, 0), Request("set", 1, 0, 0)]
    _, stale_replays = apply_trace(final, old_requests, p)
    assert all(t["outcome"] == "deny" for t in stale_replays)
    return {"success": successful, "mutants": tests, "indistinguishable_evidence": admission_tables,
            "distinction_witnesses": distinctions, "replay_after_two_replacements": stale_replays,
            "new_evidence_at_old_physical_producer": refresh_trace,
            "split_effect_crash": {"trace": ["submit pair := (1,1)", "validate", "write x := 1",
                                              "executor dies before y write / whole-effect record"],
                                   "before": asdict(base), "whole": asdict(proposed), "actual": asdict(partial),
                                   "cuts_examined": 48, "invalid_cuts": crash_cuts},
            "mutable_proposal": {"declared": declared.label(), "later_retargeted": retargeted.label(),
                                  "required": asdict(intended), "actual": asdict(swapped),
                                  "violation": "invariant and authority hold, but the declared whole effect changed"},
            "co_located_view_loss": {"before": asdict(base), "after": asdict(State()),
                                      "violation": "executor death erased continuing work, content and authority"}}


def run():
    profiles = (Profile("independent"), Profile("coupled", coupled=True), Profile("exclusive", exclusive=True))
    graphs = []
    for p in profiles:
        graphs.append(authoritative_graph(p))
        print(f"authoritative {p.name}: {graphs[-1]['states']} states, {graphs[-1]['edges']} edges", flush=True)
    p, coupled = profiles[:2]
    base, parallel = established((0, 7)), established((0, 7), (3, Y))
    cases = [
        ("replacement race", base, (Request("set", 0, 0, 1), Request("replace", target=0, other=1)), (0, -1), p),
        ("revocation race", base, (Request("set", 0, 0, 1), Request("restrict", target=0)), (0, -1), p),
        ("compatible fields", parallel, (Request("set", 0, 0, 1), Request("set", 3, 1, 1)), (0, 3), p),
        ("coupled fields", parallel, (Request("set", 0, 0, 1), Request("set", 3, 1, 1)), (0, 3), coupled),
        ("exclusive grant race", established(), (Request("grant", target=0, value=X), Request("grant", target=3, value=Y)), (-1, -1), profiles[2]),
        ("delegation versus parent restriction", base, (Request("delegate", 0, 3, Y), Request("restrict", target=0, value=X)), (0, -1), p),
        ("denied composite and loss", base, (Request("mixed", 0),), (0,), p),
        ("whole pair and loss", base, (Request("pair", 0, value=3),), (0,), p),
    ]
    flights = [flight_explore(*case) for case in cases]
    assert flights[2]["both_commit_reachable"] and not flights[3]["both_commit_reachable"]
    assert not flights[4]["both_commit_reachable"]
    flights.append(flight_explore("lost acknowledgement then replay", base,
                                  (Request("flip", 0, 0), Request("flip", 0, 0)), (0, 0), p,
                                  replay_after=True))
    assert flights[-1]["repeated_flip_returns_to_start"]
    mutants = [flight_explore(*cases[i], weakness="stale_view") for i in (0, 1, 3, 4, 5)]
    return {"format": 1, "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "authoritative_graphs": graphs, "interleavings": flights, "detached_validation_mutants": mutants,
            "history_oracle": history_attacks(), "content_boundary": [content_explore(m) for m in ("copy", "live", "hash_only")],
            "witnesses": direct_witnesses()}


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without -O: verification assertions must be enabled.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = run()
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "all checks passed; all deliberate mutants detected",
                      "authoritative_states": sum(g["states"] for g in results["authoritative_graphs"]),
                      "interleaving_states": sum(g["states"] for g in results["interleavings"]),
                      "history_cases": results["history_oracle"]["cases"]}, sort_keys=True))
