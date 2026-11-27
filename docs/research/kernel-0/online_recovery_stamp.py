"""Distinguish external stamp maintainers under common replayable update suffixes."""
from collections import Counter, defaultdict, deque
from itertools import combinations, product

from recovery_anchor import conflict_graph


def set_version(state, coord, value):
    return state[:coord] + (max(state[coord], value),) + state[coord+1:]


def check(limits, scopes):
    states = list(product(*(range(k+1) for k in limits)))
    conflicts = conflict_graph(states, scopes, limits)
    # Seed with pairs distinguished by one actual feasible probe. Work backward
    # over identical update inputs until reaching every distinguishable pair.
    predecessors = defaultdict(set)
    distance = {}
    todo = deque()
    for a, b in combinations(states, 2):
        pair = (a, b)
        if b in conflicts[a]:
            distance[pair] = 0
            todo.append(pair)
        for i, cap in enumerate(limits):
            for value in range(1, cap+1):
                x, y = set_version(a, i, value), set_version(b, i, value)
                if x != y:
                    predecessors[tuple(sorted((x, y)))].add(pair)
    while todo:
        pair = todo.popleft()
        for prev in predecessors[pair]:
            if prev not in distance:
                distance[prev] = distance[pair]+1
                todo.append(prev)
    for a, b in combinations(states, 2):
        lengths = []
        for scope in scopes:
            pos = sum(a[i] < b[i] for i in scope)
            neg = sum(a[i] > b[i] for i in scope)
            if pos + neg:
                lengths.append(min(pos, neg))
        assert distance.get((a, b)) == min(lengths, default=None)
    print(limits, scopes, "pairs by minimum update suffix", dict(sorted(Counter(distance.values()).items())))


if __name__ == "__main__":
    check((1, 1, 1, 1), ((0, 1, 2, 3),))
    check((2, 2, 2, 2), ((0, 1, 2, 3),))
    check((2, 2, 2, 2), ((0, 1), (1, 2), (2, 3)))
    check((2, 1, 3), ((0,), (1, 2)))
    check((1, 2, 1), ((0, 2),))  # unqueried version is truly unobservable
