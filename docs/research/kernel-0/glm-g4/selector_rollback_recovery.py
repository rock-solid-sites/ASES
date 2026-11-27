"""Selector image restore versus never-rolled-back gate floors and spool.

Phase one explores the abortable handover protocol without failure and
records, for every reachable state, the genuine earlier selector images
along actual paths.  Phase two restores each image while keeping gates,
votes and summaries from the true state, then enumerates every continuation
under one of five resumption rule sets:

  original   the protocol rules unchanged; numbering restarts at the image.
  numbering  the selector renumbers past every trace visible at restore
             (gate floors plus issued summaries) but may still decide and
             publish before its first lineage-extending commit.
  blocked    numbering unchanged (the image is verbatim) but summaries are
             withheld until one lineage-extending commit.
  repaired   renumbering plus that withholding.
  deferred   renumbering; aborts (not summaries) are withheld until one
             lineage-extending commit.

A continuation is harmful when an open gate holds a tenure different from
the authoritative lineage tenure: an open gate accepts whole appends under
its stored tenure, so such a state accepts an append under an obsolete or
never-authorized tenure.  The lineage tenure starts at the true selector's
last committed attempt and advances only through restored-run commits that
cannot re-decide any absorbed attempt: a commit at q extends the lineage
exactly when q exceeds every restore-time trace (gate floors and issued
summary numbers) or q is the true world's still-pending attempt.  Traces
below that bound were either decided, and immutable, or belong to the true
pending attempt, which only its own decision may settle.

Run from the repository root:
  python3 docs/research/kernel-0/glm-g4/selector_rollback_recovery.py 1 3 4
  python3 docs/research/kernel-0/glm-g4/selector_rollback_recovery.py 2 2 4
"""
from __future__ import annotations

import sys
from collections import deque

# State = (selector, gates, votes, summaries).
# selector = (d, c, pending, receipts, bindings): d last decided attempt,
#   c last committed attempt (the selected tenure), pending 0 or d+1,
#   receipts gates whose vote for pending is in hand, bindings[r-1] the
#   tenure selected at decision r (r itself exactly when r committed).
# gates: tuples (t, h, mode) with mode 1 open / 0 closed; t the floor, h the
#   tenure of the last applied summary (initially the first tenure 0).
# votes: frozenset of (attempt, gate) ever issued, still deliverable.
# summaries: frozenset of (r, b) ever issued, still deliverable.

ORIGINAL = "original"
NUMBERING = "numbering"
BLOCKED = "blocked"
REPAIRED = "repaired"
DEFERRED = "deferred"
RULES = (ORIGINAL, NUMBERING, BLOCKED, REPAIRED, DEFERRED)
RENUMBERED = (NUMBERING, REPAIRED, DEFERRED)
WITHHELD_SUMMARY = (BLOCKED, REPAIRED)  # summaries wait for a fresh commit
WITHHELD_ABORT = (DEFERRED,)           # aborts wait for a fresh commit

GATES = 1  # set by run()


def floors(gates):
    return max(g[0] for g in gates)


def traces(state):
    """Highest attempt number that left any restore-visible trace."""
    channel = max((r for r, _b in state[3]), default=0)
    return max(floors(state[1]), channel)


def fresh(q, m_abs, d_star):
    """A commit at q is lineage-extending unless it re-decides an
    absorbed attempt.  Traces bound decided attempts and the pending one."""
    return q > m_abs or q == d_star + 1


def fresh_tenure(bindings, m_abs, d_star):
    best = 0
    for q in range(1, len(bindings) + 1):
        if bindings[q - 1] == q and fresh(q, m_abs, d_star):
            best = max(best, q)
    return best


def lineage(state, c_star, m_abs, d_star):
    return max(c_star, fresh_tenure(state[0][4], m_abs, d_star))


def wrong_gate(state, c_star, m_abs, d_star):
    c_now = lineage(state, c_star, m_abs, d_star)
    for t, h, mode in state[1]:
        if mode and h != c_now:
            return h, c_now
    return None


def step(state, rule, cap, unblocked):
    """Yield (label, successor) for one protocol step under `rule`."""
    (d, c, pending, receipts, bindings), gates, votes, summaries = state
    everyone = frozenset(range(GATES))

    if not pending and d < cap:
        yield "start %d" % (d + 1), (
            (d + 1, c, d + 1, frozenset(), bindings), gates, votes, summaries)

    if pending:
        for g in range(GATES):
            t, h, mode = gates[g]
            if pending > t:
                new_gates = list(gates)
                new_gates[g] = (pending, h, 0)
                yield "prepare %d -> gate %d" % (pending, g), (
                    state[0], tuple(new_gates), votes | {(pending, g)},
                    summaries)

    for q, g in sorted(votes):
        if q == pending and g not in receipts:
            yield "vote %d from gate %d" % (q, g), (
                (d, c, pending, receipts | {g}, bindings), gates, votes,
                summaries)

    if pending and (rule not in WITHHELD_ABORT or unblocked):
        yield "abort %d" % pending, (
            (pending, c, 0, frozenset(), bindings + (c,)), gates, votes,
            summaries)

    if pending and receipts >= everyone:
        yield "commit %d" % pending, (
            (pending, pending, 0, frozenset(), bindings + (pending,)), gates,
            votes, summaries)

    if rule not in WITHHELD_SUMMARY or unblocked:
        for r in range(1, len(bindings) + 1):
            if bindings[r - 1] is None:
                continue  # a renumbered skip: no decision was made at r
            pair = (r, bindings[r - 1])
            if pair not in summaries:
                yield "summary (%d,%d)" % pair, (
                    state[0], gates, votes, summaries | {pair})

    for r, b in sorted(summaries):
        for g in range(GATES):
            t, h, mode = gates[g]
            if r >= t and (not mode or h != b or t != r):
                new_gates = list(gates)
                new_gates[g] = (r, b, 1)
                yield "summary (%d,%d) -> gate %d" % (r, b, g), (
                    state[0], tuple(new_gates), votes, summaries)


def initial():
    return ((0, 0, 0, frozenset(), ()),
            tuple((0, 0, 1) for _ in range(GATES)),
            frozenset(), frozenset())


def renumber(state, m_abs):
    """Jump the decision number past every restore-visible trace.

    Numbers in the skipped window have no decision record; a placeholder
    keeps later bindings aligned with their decision numbers and prevents
    the selector from publishing summaries for decisions it never made.
    """
    (d, c, pending, receipts, bindings), gates, votes, summaries = state
    d = max(d, m_abs)
    pad = (None,) * (d - len(bindings))
    return (d, c, 0, frozenset(), bindings + pad), gates, votes, summaries


def phase_one(cap):
    """BFS the true protocol; return {state: set of (image, trace) pairs}.

    Each entry records a selector state that was genuinely current at some
    earlier point of an actual path, with the highest restore-visible trace
    at that moment, for every reachable state of the search.
    """
    start = initial()
    images = {start: set()}
    seen = {start}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for label, nxt in step(state, ORIGINAL, cap, True):
            if nxt not in seen:
                seen.add(nxt)
                images.setdefault(nxt, set())
                queue.append(nxt)
    changed = True
    while changed:
        changed = False
        for state in seen:
            tag = (state[0], traces(state))
            for label, nxt in step(state, ORIGINAL, cap, True):
                add = images[state] | {tag}
                if not add <= images[nxt]:
                    images[nxt] |= add
                    changed = True
    return images


def continue_from(restored, c_star, m_abs, d_star, rule, cap, verdicts):
    """BFS continuations under `rule`; return (harmful, labels, end, visited).

    `verdicts` caches proven-safe frontier states across runs sharing the
    same lineage context (c_star, m_abs, d_star, rule, withholding flag).
    """
    state = renumber(restored, m_abs) if rule in RENUMBERED else restored
    unblocked = fresh_tenure(state[0][4], m_abs, d_star) > 0
    key0 = (state, rule, unblocked, c_star, m_abs, d_star)
    if verdicts.get(key0) is False:
        return False, None, None, {key0}
    queue = deque([(state, unblocked, ())])
    visited = {key0}
    while queue:
        cur, ub, path = queue.popleft()
        if wrong_gate(cur, c_star, m_abs, d_star):
            return True, list(path), cur, visited
        for label, nxt in step(cur, rule, cap, ub):
            nub = ub or fresh_tenure(nxt[0][4], m_abs, d_star) > 0
            key = (nxt, rule, nub, c_star, m_abs, d_star)
            if len(nxt[0][4]) > cap or key in visited:
                continue
            if verdicts.get(key) is False:
                continue
            visited.add(key)
            queue.append((nxt, nub, path + (label,)))
    for key in visited:
        verdicts[key] = False
    return False, None, None, visited


def classify(end, c_star, m_abs, d_star):
    h, c_now = wrong_gate(end, c_star, m_abs, d_star)
    return "stale" if h < c_now else "forged"


def two_worlds_support():
    """One gate view and one message, two required verdicts.

    World A: attempt 1 genuinely committed; the lagging gate must absorb
    (1,1) and reopen, or the protocol's one-summary catch-up fails.
    World B: attempt 1 was aborted, the selector restored an earlier image
    and re-committed 1 from the retained receipt; absorbing the same
    message installs a tenure the true history never authorized.  The
    gate's own state and the arriving message are identical in both
    worlds, so no gate-local rule can separate them.
    """
    saved = GATES
    globals()["GATES"] = 1
    gate = ((1, 0, 0),)
    world_a = ((1, 1, 0, frozenset(), (1,)), gate,
               frozenset({(1, 0)}), frozenset({(1, 1)}))
    world_b = ((1, 1, 0, frozenset(), (1,)), gate,
               frozenset({(1, 0)}), frozenset({(1, 0), (1, 1)}))
    successors = {}
    for world in (world_a, world_b):
        for label, nxt in step(world, ORIGINAL, 4, True):
            if label == "summary (1,1) -> gate 0":
                successors[id(world)] = nxt
    succ_a, succ_b = successors[id(world_a)], successors[id(world_b)]
    assert succ_a[1] == succ_b[1], "gate-side effect differs"
    assert wrong_gate(succ_a, 1, 1, 1) is None, "A must reopen for catch-up"
    assert wrong_gate(succ_b, 0, 1, 1), "B must not accept the forged tenure"
    globals()["GATES"] = saved
    print("two-worlds support verified: identical gate inputs, opposite"
          " required verdicts")


def run(gates, attempts, cap):
    global GATES
    GATES = gates
    images = phase_one(attempts)
    states = sorted(images, key=repr)
    print("phase one: %d states, %d gate(s), attempts <= %d"
          % (len(states), gates, attempts))

    for state in states:
        d, c = state[0][0], state[0][1]
        assert all(g[0] <= d + 1 for g in state[1]), "floor beyond horizon"
        assert all(not g[2] or g[1] == c for g in state[1]), "true drift"
    recorded = sum(len(images[s]) for s in states)
    for state in states:
        assert traces(state) <= state[0][0] + 1, "trace beyond pending"
        for image, trace in images[state]:
            assert trace <= image[0] + 1, "image trace lemma"
    print("true-world open-gate invariant and image trace lemma verified on"
          " %d image records" % recorded)

    verdicts = {}
    stats = {r: dict(checked=0, harmful=0, stale=0, forged=0, best=None,
                     redecided=0, converged=0)
             for r in RULES}
    for state in states:
        c_star = state[0][1]
        d_star = state[0][0]
        m_abs = traces(state)
        for image, _trace in images[state]:
            if image == state[0]:
                continue
            restored = (image, state[1], state[2], state[3])
            for rule in RULES:
                stats[rule]["checked"] += 1
                hit, path, end, visited = continue_from(
                    restored, c_star, m_abs, d_star, rule, cap, verdicts)
                redecided = False
                converged = False
                for key in visited:
                    bindings = key[0][0][4]
                    if fresh_tenure(bindings, m_abs, d_star) > 0:
                        converged = True  # the run reached a fresh,
                        # lineage-extending commit and resumed normal service
                    for q in range(len(image[4]) + 1,
                                   min(len(bindings), m_abs) + 1):
                        if bindings[q - 1] == q:
                            redecided = True  # a commit re-decided a traced
                            # attempt: a grant was authorized that the true
                            # decision history had already settled otherwise.
                            break
                    if redecided:
                        break
                if converged:
                    stats[rule]["converged"] += 1
                if redecided:
                    stats[rule]["redecided"] += 1
                if not hit:
                    if rule in RENUMBERED:
                        # Renumbered rules decide only above every trace.
                        for key in visited:
                            bindings = key[0][0][4]
                            for q in range(len(image[4]) + 1,
                                           min(len(bindings), m_abs) + 1):
                                assert bindings[q - 1] != q, \
                                    "renumbered rule re-decided a traced state"
                    continue
                stats[rule]["harmful"] += 1
                kind = classify(end, c_star, m_abs, d_star)
                stats[rule][kind] += 1
                best = stats[rule]["best"]
                if best is None or len(path) < len(best[1]):
                    stats[rule]["best"] = (
                        kind, path, end, c_star, m_abs, d_star)

    for rule in RULES:
        s = stats[rule]
        print("rule %-9s runs %5d harmful %5d stale %d forged %d"
              " redecided-grants %d converged %d"
              % (rule, s["checked"], s["harmful"], s["stale"], s["forged"],
                 s["redecided"], s["converged"]))
    assert stats[REPAIRED]["converged"] > 0, "repaired verdicts are vacuous"
    assert stats[BLOCKED]["converged"] > 0, "blocked verdicts are vacuous"
    for rule in RULES:
        s = stats[rule]
        if s["best"]:
            kind, path, end, c_star, m_abs, d_star = s["best"]
            print("  rule %s, shortest %s witness, %d steps:"
                  % (rule, kind, len(path)))
            print("    " + " | ".join(path))
            wrong = wrong_gate(end, c_star, m_abs, d_star)
            print("    ends open at tenure %d, lineage %d, traces %d"
                  % (wrong[0], wrong[1], m_abs))

    assert stats[ORIGINAL]["harmful"] > 0, "expected original-rule failure"
    assert stats[NUMBERING]["harmful"] > 0, "numbering alone must fail"
    assert stats[BLOCKED]["harmful"] == 0, "blocked repair failed"
    assert stats[REPAIRED]["harmful"] == 0, "repaired rule failed"
    two_worlds_support()
    print("verified: original and numbering-only resumptions admit a stale"
          " or forged open; blocked and repaired resumptions hold on every"
          " restored image")


if __name__ == "__main__":
    gates = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    run(gates, attempts, cap)
