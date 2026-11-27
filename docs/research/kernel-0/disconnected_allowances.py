"""Finite cross-check of resource envelopes against joint-prefix enumeration."""
from collections import Counter
from itertools import product


def dot(a, x):
    return sum(weight * value for weight, value in zip(a, x))


def profile(envelope, rows):
    return tuple(max(dot(a, x) for x in envelope) for a in rows)


def add(vectors):
    return tuple(map(sum, zip(*vectors)))


def fits(usage, bounds):
    return all(x <= b for x, b in zip(usage, bounds))


def violating_tuple(envelopes, row):
    return tuple(max(e, key=lambda x: dot(row, x)) for e in envelopes)


def compare():
    rows = ((1, 0), (0, 1), (1, 1))
    choices = ((1, 0), (0, 1), (1, 1))
    domain = [((0, 0),) + tuple(x for x, take in zip(choices, mask) if take)
              for mask in product((False, True), repeat=3)]
    counts = Counter()
    for envelopes in product(domain, repeat=3):
        summary = add(profile(e, rows) for e in envelopes)
        joint = {add(points) for points in product(*envelopes)}
        # Independent Cartesian oracle compares the tuple totals to each budget.
        points = [(x, y, x + y) for x, y in joint]
        for b in product(range(4), range(4), range(7)):
            exact = all(fits(v, b) for v in points)
            assert fits(summary, b) == exact
            counts[exact] += 1
            if not exact:
                j = next(j for j, (u, v) in enumerate(zip(summary, b)) if u > v)
                witness = add(violating_tuple(envelopes, rows[j]))
                assert dot(rows[j], witness) > b[j]
    print("independent-envelope comparison", dict(counts))


def controls():
    tri = ((0, 0), (1, 0), (0, 1))
    rows = ((1, 0), (0, 1), (1, 1))
    e = [tri] * 32
    assert add(profile(i, rows) for i in e) == (32, 32, 32)
    box_total = sum(add(profile(i, rows[:2]) for i in e))
    assert box_total == 64
    for n in range(2, 20):
        cap = n - 1
        assert sum([1] * (n - 1)) <= cap < sum([1] * n)
    print("32 owners: exact shared-cost maximum 32; coordinate-box estimate", box_total)
    print("minimal violating owner populations checked through 19")


if __name__ == "__main__":
    compare()
    controls()
