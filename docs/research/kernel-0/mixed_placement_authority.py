"""Compare path propagation with complete mixtures of containment placements."""
from functools import lru_cache
from itertools import product

from concurrent_reparenting import is_tree, union_acyclic


def any_mixture(old, new, boundary):
    # For each unit, each bit represents one effect or one fixed policy context.
    @lru_cache(None)
    def propagate(i):
        if i == 0:
            return boundary[0]
        return boundary[i] & (propagate(old[i]) | propagate(new[i]))
    return tuple(propagate(i) for i in range(len(old)))


def direct(parents, boundary, i):
    permit = boundary[0]
    while i:
        permit &= boundary[i]
        i = parents[i]
    return permit


def compare(n):
    trees = [(0,) + p for p in product(range(n+1), repeat=n) if is_tree((0,) + p)]
    # Bit m is the context in which unit j permits the effect iff bit j-1 of m is set.
    contexts = range(1 << n)
    full = (1 << len(contexts)) - 1
    boundary = [full] + [sum(1 << m for m in contexts if m & (1 << j)) for j in range(n)]
    pairs = invisible = 0
    for old, new in product(trees, repeat=2):
        if not union_acyclic(old, new):
            continue
        pairs += 1
        predicted = any_mixture(old, new, boundary)
        actual = [0] * (n+1)
        for parents in product(*(set(choices) for choices in zip(old, new))):
            for i in range(1, n+1):
                actual[i] |= direct(parents, boundary, i)
        assert tuple(actual[1:]) == predicted[1:]
        for i in range(1, n+1):
            endpoints = direct(old, boundary, i) | direct(new, boundary, i)
            invisible += (predicted[i] & ~endpoints).bit_count()
    print(n, "nonroot units;", pairs, "compatible tree pairs;", invisible,
          "unit/context cases allowing an effect only in a mixture")


def switches(n):
    # Switch i points to one of two fixed filters; both lead to the next switch.
    # All selectable placements are trees, for every bit pattern.
    all_rights = (1 << n) - 1
    old, new, boundary = [0], [0], [all_rights]
    for i in range(n):
        switch = 1 + 3*i
        tail = switch + 3 if i + 1 < n else 0
        old.extend((switch + 1, tail, tail))
        new.extend((switch + 2, tail, tail))
        boundary.extend((all_rights, all_rights ^ (1 << i), all_rights ^ (1 << ((i-1) % n))))
    assert union_acyclic(old, new)
    assert any_mixture(old, new, boundary)[1] == all_rights
    for bits in product((False, True), repeat=n):
        mixed = old.copy()
        for i, installed in enumerate(bits):
            if installed:
                mixed[1+3*i] = new[1+3*i]
        observed = direct(mixed, boundary, 1)
        expected = sum(1 << i for i in range(n) if bits[i] and not bits[(i+1) % n])
        assert observed == expected
        assert (observed == 0) == (all(bits) or not any(bits))


if __name__ == "__main__":
    for size in (2, 3, 4):
        compare(size)
    for size in range(2, 13):
        switches(size)
    print("indivisible observable moves verified for 2..12 switches")
