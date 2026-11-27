"""Exact finite-field recovery versus direct ambiguity under lost failure domains."""
from collections import Counter
from itertools import combinations, product


def observation(rows, word):
    return tuple((row & word).bit_count() % 2 for row in rows)


def span(rows):
    basis = {0}
    for row in rows:
        basis |= {v ^ row for v in basis}
    return basis


def margin(groups, required, bits):
    distances = []
    for difference in range(1, 1 << bits):
        if any(observation(required, difference)):
            distances.append(sum(any(observation(g, difference)) for g in groups))
    return min(distances, default=len(groups) + 1)


def compare():
    bits = 3
    words = range(1 << bits)
    # Four labelled fragments. In the second layout one domain holds two.
    layouts = ((0, 1, 2, 3), (0, 0, 1, 2))
    totals = Counter()
    for rows in combinations(words, 4):
        for layout in layouts:
            domains = range(max(layout) + 1)
            groups = [[r for r, d in zip(rows, layout) if d == i] for i in domains]
            for required in ((1,), (3, 4), (1, 2, 4)):
                fatal = len(groups) + 1
                for mask in range(1 << len(groups)):
                    survivors = [r for r, d in zip(rows, layout) if not mask >> d & 1]
                    algebra = set(required) <= span(survivors)
                    answers = {}
                    exact = True
                    for x in words:
                        view = observation(survivors, x)
                        need = observation(required, x)
                        if view in answers and answers[view] != need:
                            exact = False
                        answers[view] = need
                    assert algebra == exact
                    if not exact:
                        fatal = min(fatal, mask.bit_count())
                    totals[exact] += 1
                assert margin(groups, required, bits) == fatal
    print("row-space versus direct decode", dict(totals))


def verify_examples():
    parity = ((1,), (2,), (3,))
    assert margin(parity, (1, 2), 2) == 2
    colocated = ((1, 2), (3,))
    assert margin(colocated, (1, 2), 2) == 1
    replicas = ((1,), (1,), (0,))
    assert margin(replicas, (1,), 2) == 2
    assert margin(replicas, (1, 2), 2) == 0
    # Compare directly the ambiguity thresholds for corrupt/erased blocks.
    for groups, required in ((parity, (1, 2)), (replicas, (1,))):
        distance = margin(groups, required, 2)
        for errors, erasures in product(range(3), repeat=2):
            views = {}
            ambiguity = False
            for x in range(4):
                original = [observation(g, x)[0] for g in groups]
                for received in product((0, 1, None), repeat=len(groups)):
                    if received.count(None) > erasures:
                        continue
                    if sum(y is not None and y != z for y, z in zip(received, original)) > errors:
                        continue
                    needed = observation(required, x)
                    if received in views and views[received] != needed:
                        ambiguity = True
                    views[received] = needed
            assert ambiguity == (2 * errors + erasures >= distance)
    print("grouping, projection and error/erasure controls passed")


if __name__ == "__main__":
    compare()
    verify_examples()
