"""Verify lower and upper recovery-stamp certificates from observable probe conflicts."""
from collections import defaultdict
from itertools import combinations, product
from math import prod


def partitions(items):
    if not items:
        yield ()
        return
    i, *rest = items
    for blocks in partitions(rest):
        yield ((i,),) + blocks
        for j in range(len(blocks)):
            yield blocks[:j] + ((i,) + blocks[j],) + blocks[j+1:]


def conflict_graph(states, blocks, limits, ancestors_only=True):
    graph = {s: set() for s in states}
    for block in blocks:
        outcomes = defaultdict(lambda: ([], []))
        for current in states:
            image = tuple(current[i] for i in block)
            caps = image if ancestors_only else tuple(limits[i] for i in block)
            for offered in product(*(range(k+1) for k in caps)):
                outcomes[offered][offered == image].append(current)
        for incorrect, correct in outcomes.values():
            for good in correct:
                graph[good].update(incorrect)
            for bad in incorrect:
                graph[bad].update(correct)
    return graph


def stamp(s, blocks):
    return tuple(sum(s[i] for i in block) for block in blocks)


def chain(block, limits):
    current = [0] * len(block)
    yield tuple(current)
    for j, coord in enumerate(block):
        for _ in range(limits[coord]):
            current[j] += 1
            yield tuple(current)


def lower_clique(blocks, limits):
    for pieces in product(*(chain(block, limits) for block in blocks)):
        state = [0] * len(limits)
        for block, piece in zip(blocks, pieces):
            for i, value in zip(block, piece):
                state[i] = value
        yield tuple(state)


def check(limits):
    states = list(product(*(range(k+1) for k in limits)))
    for blocks in partitions(list(range(len(limits)))):
        graph = conflict_graph(states, blocks, limits)
        proposed = {s: stamp(s, blocks) for s in states}
        assert all(proposed[s] != proposed[t] for s in states for t in graph[s])
        clique = list(lower_clique(blocks, limits))
        size = prod(1 + sum(limits[i] for i in block) for block in blocks)
        assert len(clique) == len(set(clique)) == len(set(proposed.values())) == size
        assert all(t in graph[s] for s, t in combinations(clique, 2))
    whole = (tuple(range(len(limits))),)
    arbitrary = conflict_graph(states, whole, limits, ancestors_only=False)
    assert all(len(neighbours) == len(states)-1 for neighbours in arbitrary.values())
    print("limits", limits, "whole", sum(limits)+1, "singleton", len(states),
          "partitions", sum(1 for _ in partitions(list(range(len(limits))))))


if __name__ == "__main__":
    for bounds in ((1, 1), (1, 2, 3), (1, 1, 1, 1), (2, 2, 2, 2)):
        check(bounds)
