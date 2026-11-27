"""Compare a fence certificate with enumeration of minimal future checks."""
from collections import Counter
from itertools import permutations, product


def reachable(frontier, edges, fenced):
    adjacency = {}
    for src, dst, label in edges:
        if label not in fenced:
            adjacency.setdefault(src, []).append(dst)
    region = set(frontier)
    pending = list(region)
    while pending:
        for dst in adjacency.get(pending.pop(), ()):
            if dst not in region:
                region.add(dst)
                pending.append(dst)
    return region


def certificate(frontier, edges, fenced, bad, region):
    return (set(frontier) <= region and bad not in region
            and all(src not in region or dst in region or label in fenced
                    for src, dst, label in edges))


def minimal_supports(frontier, edges, bad):
    """Simple-path oracle. Cycles may be erased while preserving a subset of labels."""
    supports = set()

    def paths(v, seen, checks):
        if v == bad:
            supports.add(frozenset(checks))
            return
        for src, dst, label in edges:
            if src == v and dst not in seen:
                extra = {label} if label is not None else set()
                paths(dst, seen | {dst}, checks | extra)

    for v in frontier:
        paths(v, {v}, set())
    return [s for s in supports if not any(t < s for t in supports)]


def exhaust():
    arcs = tuple(permutations(range(3), 2))
    counts = Counter()
    for labels in product(("-", None, "a", "b"), repeat=len(arcs)):
        edges = [(a, b, label) for (a, b), label in zip(arcs, labels) if label != "-"]
        for frontier in ({0}, {1}, {0, 1}):
            supports = minimal_supports(frontier, edges, 2)
            for fences in (set(), {"a"}, {"b"}, {"a", "b"}):
                region = reachable(frontier, edges, fences)
                safe = all(fences & s for s in supports)
                assert safe == (2 not in region)
                assert safe == certificate(frontier, edges, fences, 2, region)
                counts[safe] += 1
    print("graph / frontier / fence combinations", dict(counts))


def prefix_example():
    # A cached permit from the first gate is stored in state 1.
    edges = [(0, 1, "a"), (1, 2, "b")]
    for frontier in ({0}, {0, 1}):
        print("two-stage path", sorted(frontier), minimal_supports(frontier, edges, 2))
    assert certificate({0}, edges, {"a"}, 2, {0})
    assert not certificate({0, 1}, edges, {"a"}, 2, {0})
    assert 2 in reachable({0, 1}, edges, {"a"})
    assert certificate({0, 1}, edges, {"b"}, 2, {0, 1})
    # A preauthorized completion awaiting unguarded delivery.
    assert 3 in reachable({0, 1, 2}, edges + [(2, 3, None)], {"a", "b"})


if __name__ == "__main__":
    exhaust()
    prefix_example()
