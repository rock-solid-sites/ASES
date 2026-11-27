"""Minimize visible behavior of a Work Unit with independently assertable vetoes."""
from collections import Counter
from itertools import product


def minimum(clauses):
    terms = set(clauses)
    return frozenset(t for t in terms if not any(u != t and u & t == u for u in terms))


def signature(vetoes, releases):
    return minimum(releases[i] for i in range(len(releases)) if vetoes >> i & 1)


def machine(releases, groups):
    states = range(1 << len(releases))
    clear_masks = [sum(1 << i for i, allowed in enumerate(releases) if allowed >> g & 1)
                   for g in range(groups)]
    return [[s | (1 << i) for i in range(len(releases))] + [s & ~mask for mask in clear_masks]
            for s in states]


def bisimulation(transitions):
    # Each management action always acknowledges. A separate query says whether
    # the reference veto set is empty. Refine until no future query separates more states.
    classes = [int(s == 0) for s in range(len(transitions))]
    while True:
        table = {}
        refined = []
        for s, successors in enumerate(transitions):
            key = (classes[s], tuple(classes[t] for t in successors))
            refined.append(table.setdefault(key, len(table)))
        if len(set(classes)) == len(table):
            return refined
        classes = refined


def verify(releases, groups):
    transitions = machine(releases, groups)
    classes = bisimulation(transitions)
    sigs = [signature(s, releases) for s in range(len(transitions))]
    for s, row in enumerate(transitions):
        clauses = sigs[s]
        for i, nxt in enumerate(row[:len(releases)]):
            assert minimum(clauses | {releases[i]}) == sigs[nxt]
        for g, nxt in enumerate(row[len(releases):]):
            assert frozenset(t for t in clauses if not (t >> g & 1)) == sigs[nxt]
        for other in range(s):
            assert (sigs[s] == sigs[other]) == (classes[s] == classes[other])
            if sigs[s] != sigs[other]:
                # Pick an unhit clause from one side; release its complement.
                for left, right in ((sigs[s], sigs[other]), (sigs[other], sigs[s])):
                    clause = next((t for t in left if not any(u & t == u for u in right)), None)
                    if clause is not None:
                        break
                assert clause is not None
                a, b = s, other
                for g in range(groups):
                    if not (clause >> g & 1):
                        a = transitions[a][len(releases) + g]
                        b = transitions[b][len(releases) + g]
                assert (a == 0) != (b == 0)
    return len(set(classes))


if __name__ == "__main__":
    counts = Counter(verify(releases, 3) for releases in product(range(8), repeat=3))
    print("3 causes, 3 release operations; minimal state count -> number of interfaces", dict(sorted(counts.items())))
    for n in range(1, 9):
        releases = [1 << i for i in range(n)]
        assert len(set(bisimulation(machine(releases, n)))) == 1 << n
        assert len(set(bisimulation(machine([1] * n, 1)))) == 2
    print("independent and jointly releasable veto families checked through 8 causes")
    assert signature(1, (1, 1)) == signature(2, (1, 1))
    split = machine((3, 1), 2)
    assert split[1][-1] == 0 and split[2][-1] != 0
    print("a new release authority distinguishes previously equivalent histories")
