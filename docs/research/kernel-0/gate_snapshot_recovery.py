"""Restore a genuine earlier local gate image while leaving authentic messages live."""
from collections import Counter, defaultdict, deque

from abortable_handover import State, member, steps


def actual_images(n, rounds):
    """Per reachable state, collect all gate-zero images from a path to that state."""
    members = (1 << n) - 1
    start = State(((0, members),), None, ((0, 0, 0),) * n)
    seen = defaultdict(set)
    pending = deque([(start, (0, 0))])
    while pending:
        s, image = pending.popleft()
        if image in seen[s]:
            continue
        seen[s].add(image)
        for _, nxt in steps(s, rounds, "none", dynamic=True):
            pending.append((nxt, image))
            pending.append((nxt, nxt.gates[0][:2]))
    return seen


def failures(s):
    d = len(s.log) - 1
    c, members = s.log[-1]
    t, h, escaped = s.gates[0]
    wrong_open = h >= 0 and (not member(members, 0) or h != c)
    obsolete = any(member(mask, 0) and (binding != c or not member(members, 0))
                   for binding, mask in s.log[t:])
    exposed_vote = (s.target is not None and escaped == d + 1
                    and (h >= 0 or t < d + 1))
    return wrong_open, obsolete, exposed_vote


def bad_append(s):
    c, members = s.log[-1]
    return any(h >= 0 and (h != c or not member(members, i))
               for i, (_, h, _) in enumerate(s.gates))


def compare(n, rounds):
    restored = set()
    safe_regressions = 0
    for s, images in actual_images(n, rounds).items():
        # v is evidence that escaped the gate, even when no receipt reached the selector yet.
        for t, h in images:
            candidate = s.gate(0, (t, h, s.gates[0][2]))
            restored.add(candidate)
            if t < s.gates[0][0] and not any(failures(candidate)):
                safe_regressions += 1
    # Independent oracle: enumerate all remaining protocol interleavings and
    # propagate actual bad appends backwards through the combined state graph.
    predecessors = defaultdict(set)
    todo = deque(restored)
    seen = set(restored)
    bad = set()
    while todo:
        s = todo.popleft()
        if bad_append(s):
            bad.add(s)
            continue
        for _, nxt in steps(s, rounds, "none", dynamic=True):
            predecessors[nxt].add(s)
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    todo = deque(bad)
    while todo:
        nxt = todo.popleft()
        for s in predecessors[nxt] - bad:
            bad.add(s)
            todo.append(s)
    counts = Counter()
    for s in restored:
        reason = failures(s)
        assert any(reason) == (s in bad), (s, reason)
        # In a genuine open image a summary at its own t explains the mode.
        assert not reason[0] or reason[1]
        d = len(s.log) - 1
        t, _, escaped = s.gates[0]
        older, active = reason[1], s.target is not None and escaped == d + 1
        assert (older or (active and t < d + 1)) == (s in bad)
        counts[reason] += 1
    safe = counts[(False, False, False)]
    print(n, rounds, "images", len(restored), "safe", safe, "unsafe", len(restored)-safe)
    print("safe strict floor regressions (source/image pairs)", safe_regressions)
    print("isolated failures (open, summary, vote)",
          [counts[tuple(i == j for i in range(3))] for j in range(3)])
    assert all(counts[tuple(i == j for i in range(3))] for j in (1, 2))


if __name__ == "__main__":
    compare(1, 3)
    compare(2, 2)
