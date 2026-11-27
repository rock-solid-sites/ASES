"""Exact migration test and constrained histories of release-authority changes."""
from collections import Counter, deque
from itertools import product

from independent_seals import signature


def subset(a, b):
    return a & b == a


def migration_check():
    policies = list(product(range(4), repeat=3))
    count = Counter()
    for old, new in product(policies, repeat=2):
        monotone = all(not subset(old[i], old[j]) or subset(new[i], new[j])
                       for i in range(3) for j in range(3))
        observed = {}
        possible = True
        for z in range(8):
            before, after = signature(z, old), signature(z, new)
            if before in observed and observed[before] != after:
                possible = False
            observed[before] = after
        assert possible == monotone
        if possible:
            for before, after in observed.items():
                representatives = sum(1 << old.index(term) for term in before)
                assert signature(representatives, new) == after
        count[possible] += 1
    print("exact one-step migration", dict(count))


def distinguish(left, right, moves, releases):
    """Explore paired machines with identical external inputs and optional assertions."""
    start = (0, left, right)
    seen = {start}
    todo = deque([start])
    causes = (left | right).bit_length()
    while todo:
        mode, a, b = todo.popleft()
        if bool(a) != bool(b):
            return True
        next_states = [(n, a, b) for n in moves[mode]]
        next_states.extend((mode, a & ~h, b & ~h) for h in releases[mode])
        next_states.extend((mode, a | (1 << i), b | (1 << i)) for i in range(causes))
        for s in next_states:
            if s not in seen:
                seen.add(s)
                todo.append(s)
    return False


def assignment_path(n, clauses):
    # Clause is a pair of bitmasks (positive literals, negative literals).
    # At each layer the two upgrade branches correspond to a truth assignment.
    moves = [[1, 2]] + [[] for _ in range(2*n)]
    release = [[] for _ in moves]
    for i in range(n):
        for val in (False, True):
            m = 1 + 2*i + int(val)
            if i+1 < n:
                moves[m] = [1 + 2*(i+1), 2 + 2*(i+1)]
            release[m] = [sum(1 << j for j, (pos, neg) in enumerate(clauses)
                              if (pos if val else neg) & (1 << i))]
    return moves, release


def formula_check():
    # Exhaust all subsets of the eight nonempty, nontautological clauses on two variables.
    n = 2
    clauses = [(p, q) for p, q in product(range(1 << n), repeat=2) if p | q and not p & q]
    count = Counter()
    for selected in range(1 << len(clauses)):
        formula = [c for j, c in enumerate(clauses) if selected >> j & 1]
        satisfiable = any(all((p & assignment) or (q & ~assignment) for p, q in formula)
                          for assignment in range(1 << n))
        moves, releases = assignment_path(n, formula)
        # The left state has an unreleasable cause. Extra common assertions
        # cannot clear an initial right-side cause, so use release-only search here.
        start = (0, (1 << len(formula)) - 1)
        seen = {start}
        todo = deque([start])
        while todo:
            mode, remain = todo.popleft()
            if not remain:
                break
            nxt = [(i, remain) for i in moves[mode]]
            nxt += [(mode, remain & ~h) for h in releases[mode]]
            for node in nxt:
                if node not in seen:
                    seen.add(node)
                    todo.append(node)
        else:
            remain = 1
        assert (remain == 0) == satisfiable
        count[satisfiable] += 1
    print("constrained migration paths versus truth assignments", dict(count))


if __name__ == "__main__":
    migration_check()
    # p survives both modes, a only clears in A, b only clears in B.
    for local in ([[2]], [[4]]):
        assert not distinguish(1, 6, [[]], local)
    assert distinguish(1, 6, [[1], []], [[2], [4]])
    formula_check()
