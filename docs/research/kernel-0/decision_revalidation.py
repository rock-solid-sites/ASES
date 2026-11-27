"""Compute which observations can justify a specified effect at the commit cut."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, product


def conflict_masks(states, decision):
    masks = set()
    for a, b in combinations(states, 2):
        if decision[a] != decision[b]:
            masks.add(sum(1 << i for i, (x, y) in enumerate(zip(a, b)) if x != y))
    return masks


def projection(s, mask):
    return tuple(x for i, x in enumerate(s) if mask & (1 << i))


def uniform(states, decision, mask):
    answers = {}
    for s in states:
        view = projection(s, mask)
        if view in answers and answers[view] != decision[s]:
            return False
        answers[view] = decision[s]
    return True


def crosscheck():
    states = list(product(range(2), repeat=3))
    counts = Counter()
    # All nonempty reachable subsets and all binary decisions on that subset.
    # A ternary vector encodes absent state, answer 0 or answer 1.
    for spec in product((-1, 0, 1), repeat=len(states)):
        decision = {s: d for s, d in zip(states, spec) if d >= 0}
        if not decision:
            continue
        conflicts = conflict_masks(decision, decision)
        for mask in range(8):
            exact = all(mask & diff for diff in conflicts)
            assert exact == uniform(decision, decision, mask)
            counts[exact] += 1
    print("truth-table projections", dict(counts))


def descendants(start, edges):
    reachable = {start}
    pending = [start]
    while pending:
        for nxt in edges[pending.pop()]:
            if nxt not in reachable:
                reachable.add(nxt)
                pending.append(nxt)
    return reachable


def retry_example():
    # States are (current-at-P, nonce record). Nonce values encode the
    # selected request's absence, same accepted payload, or a conflicting one.
    states = list(product((False, True), ("absent", "same", "other")))
    edges = {s: set() for s in states}
    decision = {}
    for s in states:
        current, record = s
        if current:
            edges[s].add((False, record))
            if record == "absent":
                edges[s].update(((True, "other"), (True, "same")))
        decision[s] = {"same": "replay", "other": "conflict"}.get(
            record, "append" if current else "stale")
    for s in states:
        futures = descendants(s, edges)
        sufficient = [mask for mask in range(4) if uniform(futures, decision, mask)]
        minimal = [m for m in sufficient if not any(k != m and (k & m) == k for k in sufficient)]
        assert minimal == ([3] if s == (True, "absent") else [0])
        print(s, len(futures), "minimum fields", minimal[0].bit_count())


def adaptive_depth(decision):
    @lru_cache(None)
    def depth(futures):
        if len({decision[s] for s in futures}) == 1:
            return 0
        candidates = []
        for i in range(len(next(iter(futures)))):
            groups = {}
            for s in futures:
                groups.setdefault(s[i], set()).add(s)
            if len(groups) > 1:
                candidates.append(1 + max(depth(frozenset(g)) for g in groups.values()))
        return min(candidates)
    return depth(frozenset(decision))


def selectable_policy():
    for k in (1, 2):
        branches = 2 ** k
        decision = {}
        for s in product((0, 1), repeat=k + branches):
            address = sum(s[i] << i for i in range(k))
            decision[s] = s[k + address]
        conflicts = conflict_masks(decision, decision)
        fixed = min(mask.bit_count() for mask in range(1 << (k + branches))
                    if all(mask & diff for diff in conflicts))
        adaptive = adaptive_depth(decision)
        assert (fixed, adaptive) == (k + branches, k + 1)
        print(branches, "possible bindings: fixed/adaptive", fixed, adaptive)


if __name__ == "__main__":
    crosscheck()
    retry_example()
    selectable_policy()
