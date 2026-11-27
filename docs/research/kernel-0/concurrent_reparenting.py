"""Exhaustively compare mixed parent edits with a compressed cycle check."""
from collections import Counter
from itertools import product


def is_tree(parents):
    for child in range(1, len(parents)):
        seen = set()
        while child:
            if child in seen:
                return False
            seen.add(child)
            child = parents[child]
    return True


def union_acyclic(old, new):
    moved = {i for i in range(1, len(old)) if old[i] != new[i]}
    stop = {0: 0, **{i: i for i in moved}}

    def endpoint(i):
        path = []
        while i not in stop:
            path.append(i)
            i = old[i]
        for j in path:
            stop[j] = stop[i]
        return stop[i]

    parents = {i: {endpoint(old[i]), endpoint(new[i])} - {0} for i in moved}
    # Independent topological elimination on the compressed graph.
    while parents:
        ready = {i for i, deps in parents.items() if not deps}
        if not ready:
            return False
        parents = {i: deps - ready for i, deps in parents.items() if i not in ready}
    return True


def depth(parents, i):
    hops = 0
    while i:
        i = parents[i]
        hops += 1
    return hops


def compare(n):
    forests = [(0,) + p for p in product(range(n+1), repeat=n) if is_tree((0,) + p)]
    counts = Counter()
    for old, new in product(forests, repeat=2):
        moved = [i for i in range(1, n+1) if old[i] != new[i]]
        safe = singleton_safe = True
        for chosen in product((False, True), repeat=len(moved)):
            mixed = list(old)
            for i, take in zip(moved, chosen):
                if take:
                    mixed[i] = new[i]
            legal = is_tree(mixed)
            safe &= legal
            if sum(chosen) == 1:
                singleton_safe &= legal
        assert safe == union_acyclic(old, new)
        counts["all mixtures safe" if safe else "some mixture cyclic"] += 1
        if singleton_safe and not safe:
            counts["escapes endpoint and singleton checks"] += 1
        mixed = list(old)
        for i in sorted(moved, key=lambda j: depth(new, j)):
            mixed[i] = new[i]
            assert is_tree(mixed)
        assert tuple(mixed) == new
    print(n, "nonroot units", len(forests), "trees", dict(counts))


if __name__ == "__main__":
    for n in range(1, 5):
        compare(n)
    for n in range(2, 10):
        # Moved vertices 1..n and an additional bridge n+1.
        # The all-but-bridge mixture contains a cycle, the full target is a tree.
        old = (0,) + (0,) * n + (1,)
        new = (0,) + tuple(range(2, n + 2)) + (0,)
        assert is_tree(old) and is_tree(new) and not union_acyclic(old, new)
        for bits in product((False, True), repeat=n + 1):
            mixed = (0,) + tuple(b if take else a for a, b, take in zip(old[1:], new[1:], bits))
            assert is_tree(mixed) == (not all(bits[:-1]) or bits[-1])
    print("arbitrarily long mixed-cycle family checked through nine required new edges")
