"""Decision search on actual containment filters versus a betweenness order oracle."""
from collections import Counter
from itertools import combinations, permutations

from mixed_placement_authority import direct


def compiled_rights(n, patterns):
    """One right per forbidden partial assignment (new_mask, old_mask)."""
    full = (1 << len(patterns)) - 1
    filters = [full]
    for i in range(n):
        old = sum(1 << j for j, (a, _) in enumerate(patterns) if not (a >> i & 1))
        new = sum(1 << j for j, (_, b) in enumerate(patterns) if not (b >> i & 1))
        filters.extend((full, old, new))
    results = []
    for installed in range(1 << n):
        parent = [0]
        for i in range(n):
            switch = 1 + 3*i
            tail = switch + 3 if i + 1 < n else 0
            parent.extend((switch + 1 + ((installed >> i) & 1), tail, tail))
        result = direct(parent, filters, 1)
        answer = sum(1 << j for j, (a, b) in enumerate(patterns)
                     if installed & a == a and not installed & b)
        assert result == answer
        results.append(result)
    return results


def can_finish(n, rights, forbidden):
    reached = {0}
    for s in range(1 << n):
        if s not in reached:
            continue
        for i in range(n):
            t = s | (1 << i)
            if not rights[t] & forbidden:
                reached.add(t)
    return (1 << n) - 1 in reached


def ordering_check(n):
    triples = [(a, b, c) for a, c in combinations(range(n), 2)
               for b in range(n) if b not in (a, c)]
    patterns = []
    for a, b, c in triples:
        ends = (1 << a) | (1 << c)
        patterns.extend(((1 << b, ends), (ends, 1 << b)))
    rights = compiled_rights(n, patterns)
    covered = []
    for order in permutations(range(n)):
        position = {v: i for i, v in enumerate(order)}
        covered.append(sum(1 << j for j, (a, b, c) in enumerate(triples)
                           if min(position[a], position[c]) < position[b] < max(position[a], position[c])))
    counts = Counter()
    for constraints in range(1 << len(triples)):
        forbidden = sum(3 << (2*j) for j in range(len(triples)) if constraints >> j & 1)
        answer = can_finish(n, rights, forbidden)
        assert answer == any(constraints & mask == constraints for mask in covered)
        counts[answer] += 1
    print("betweenness to relocation", n, dict(counts))


def greedy_check(n):
    patterns = [(1 << i, others) for i in range(n) for others in range(1, 1 << n)
                if not others & (1 << i)]
    rights = compiled_rights(n, patterns)
    counts = Counter()
    for selected in range(1 << len(patterns)):
        done = 0
        while True:
            enabled = [i for i in range(n) if not done & (1 << i) and
                       not rights[done | (1 << i)] & selected]
            if not enabled:
                break
            done |= 1 << enabled[0]
        answer = done == (1 << n) - 1
        assert answer == can_finish(n, rights, selected)
        if not answer:
            # Check a deadlock certificate using the original prerequisites.
            for i in range(n):
                if done >> i & 1:
                    continue
                assert any(selected >> j & 1 and a == 1 << i and not done & b
                           for j, (a, b) in enumerate(patterns))
        counts[answer] += 1
    print("one new switch per forbidden pattern", n, dict(counts))


if __name__ == "__main__":
    ordering_check(4)
    greedy_check(3)
