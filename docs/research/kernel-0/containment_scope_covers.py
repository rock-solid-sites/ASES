"""Check authority-scope placement over containment trees and a direct policy."""

from functools import cache
from itertools import combinations
from random import Random


def nontrivial_splits(mask):
    pivot = mask & -mask
    rest = mask ^ pivot
    subset = (rest - 1) & rest
    while True:
        yield pivot | subset, rest ^ subset
        if not subset:
            return
        subset = (subset - 1) & rest


@cache
def all_trees(mask):
    if mask.bit_count() == 1:
        return (mask,)
    return tuple(
        (left, right)
        for a, b in nontrivial_splits(mask)
        for left in all_trees(a)
        for right in all_trees(b)
    )


@cache
def extent(tree):
    if isinstance(tree, int):
        return tree
    return extent(tree[0]) | extent(tree[1])


def maximal_cover(tree, scope):
    covered = extent(tree) & scope
    if not covered:
        return ()
    if covered == extent(tree):
        return (extent(tree),)
    return maximal_cover(tree[0], scope) + maximal_cover(tree[1], scope)


def explicit_cost(tree, scopes):
    covers = [maximal_cover(tree, scope) for scope in scopes]
    assert all(sum(nodes) == scope for nodes, scope in zip(covers, scopes))
    return sum(map(len, covers))


def dynamic_minimum(universe, scopes):
    @cache
    def score(mask):
        if mask.bit_count() == 1:
            return 0
        common = sum(mask & scope == mask for scope in scopes)
        return common + max(score(a) + score(b) for a, b in nontrivial_splits(mask))

    return sum(scope.bit_count() for scope in scopes) - score(universe)


def laminar(scopes):
    return all(a & b in (0, a, b) for a, b in combinations(scopes, 2))


def check_hierarchies():
    checked = 0
    for included in range(128):
        scopes = tuple(scope for scope in range(1, 8) if included & (1 << (scope - 1)))
        minimum = min(explicit_cost(tree, scopes) for tree in all_trees(7))
        assert minimum == dynamic_minimum(7, scopes)
        assert (minimum == len(scopes)) == laminar(scopes)
        checked += 1
    print(f"{checked} scope families on three leaves: minima and laminar criterion agree")

    random = Random(20261128)
    for _ in range(160):
        scopes = tuple(random.sample(range(1, 32), random.randrange(32)))
        assert min(explicit_cost(tree, scopes) for tree in all_trees(31)) == dynamic_minimum(
            31, scopes
        )
    print(f"160 families on five leaves: recurrence agrees with all {len(all_trees(31))} trees")

    for size in range(2, 10):
        leaves = tuple(1 << index for index in range(size))
        universe = sum(leaves)
        pairs = tuple(a | b for a, b in combinations(leaves, 2))
        assert dynamic_minimum(universe, pairs) == 2 * len(pairs) - size // 2
        complements = tuple(universe ^ leaf for leaf in leaves)
        depth = size.bit_length() - 1
        expected = size * depth + 2 * (size - (1 << depth))
        assert dynamic_minimum(universe, complements) == expected
    print("pair and complement minimum families agree through nine leaves")


def append_allowed(target, requested, current, blocked, scopes):
    return requested == current and all(
        not (target & scope) for index, scope in enumerate(scopes) if blocked & (1 << index)
    )


def check_cross_cutting_fixture():
    leaves = (1, 2, 4)
    scopes = (1 | 2, 2 | 4)
    current = 0
    blocked = 0
    received = []
    accepted = []
    for actor, target in [
        ("append", 2), ("block", 0), ("replace", 1), ("append old", 4),
        ("append", 4), ("block", 1), ("release", 0), ("append", 1),
        ("append", 2), ("release", 1), ("append", 2),
    ]:
        if actor == "block":
            blocked |= 1 << target
        elif actor == "release":
            blocked &= ~(1 << target)
        elif actor == "replace":
            current = target
        else:
            assert target in leaves
            allowed = append_allowed(target, 0 if actor == "append old" else current,
                                     current, blocked, scopes)
            received.append(allowed)
            if allowed:
                accepted.append(target)
    assert received == [True, False, True, True, False, True]
    assert accepted == [2, 4, 1, 2]
    print("cross-cutting fixture: replacement retains content and two independent vetoes")


if __name__ == "__main__":
    check_hierarchies()
    check_cross_cutting_fixture()
