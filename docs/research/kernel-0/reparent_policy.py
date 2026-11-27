"""Reference truth tables versus minimal-support calculations for a moved grant."""
from collections import Counter
from itertools import combinations


def subset(a, b):
    return a & b == a


def minimal(terms):
    terms = set(terms)
    return frozenset(t for t in terms if not any(u != t and subset(u, t) for u in terms))


def all_policies(n):
    # Enumerate antichains incrementally. Two comparable supports are redundant.
    families = [frozenset()]
    for term in range(1 << n):
        new = [f | {term} for f in families
               if all(not subset(t, term) and not subset(term, t) for t in f)]
        families.extend(new)
    return families


def holds(family, live):
    return any(subset(t, live) for t in family)


def mismatch(old, new):
    return next((s for s in new if not holds(old, s)), None)


def project(old, visible):
    return frozenset(t for t in old if subset(t, visible))


def run():
    n = 4
    states = range(1 << n)
    families = all_policies(n)
    assert len(families) == 168
    tables = {family: sum(1 << s for s in states if holds(family, s)) for family in families}
    counts = Counter()
    for old in families:
        for new in families:
            witness = mismatch(old, new)
            widened = tables[new] & ~tables[old]
            assert (witness is not None) == bool(widened)
            if witness is not None:
                assert widened & (1 << witness)
            meet = minimal(a | b for a in old for b in new)
            assert tables[meet] == tables[old] & tables[new]
            counts["widens" if widened else "safe"] += 1
            if widened and holds(old, 15) == holds(new, 15):
                counts["hidden at move"] += 1
        for visible in states:
            retained = project(old, visible)
            for live in states:
                same_view = [s for s in states if s & visible == live & visible]
                assert holds(retained, live) == all(holds(old, s) for s in same_view)
    print("policy pairs", dict(counts))
    print("all 168 policies x 16 visibility masks x 16 live states checked")
    for n in range(1, 12):
        all_live = (1 << n) - 1
        old = {1 << i for i in range(n)}
        for k in range(n):
            for revoked in combinations(old, k):
                assert holds(old, all_live ^ sum(revoked))
        assert not holds(old, 0) and holds({0}, 0)
    print("simultaneous-withdrawal examples verified for 1..11 grants")


if __name__ == "__main__":
    run()
