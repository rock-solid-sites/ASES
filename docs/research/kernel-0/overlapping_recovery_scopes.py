"""Certify optimal external stamp counts for laminar and pairwise recovery scopes."""
from itertools import combinations, product
from math import prod

from recovery_anchor import conflict_graph, lower_clique, stamp


def certify(graph, colors, clique, size):
    assert len(set(colors.values())) == len(clique) == size
    assert all(colors[s] != colors[t] for s in graph for t in graph[s])
    assert all(t in graph[s] for s, t in combinations(clique, 2))


def residue_blocks(scopes):
    blocks = []
    for scope in scopes:
        children = set().union(*(s for s in scopes if s < scope))
        rest = scope - children
        if rest:
            blocks.append(tuple(sorted(rest)))
    return blocks


def laminar_check():
    limits = (1, 2, 1)
    nodes = set(range(len(limits)))
    states = list(product(*(range(k+1) for k in limits)))
    options = [frozenset(x) for k in range(1, 4) for x in combinations(nodes, k)]
    count = 0
    for bits in product((False, True), repeat=len(options)):
        family = [s for s, take in zip(options, bits) if take]
        if set().union(*family) != nodes or any(a & b and not (a <= b or b <= a)
                                               for a, b in combinations(family, 2)):
            continue
        graph = conflict_graph(states, [tuple(sorted(s)) for s in family], limits)
        blocks = residue_blocks(family)
        colors = {s: stamp(s, blocks) for s in states}
        clique = list(lower_clique(blocks, limits))
        size = prod(1 + sum(limits[i] for i in b) for b in blocks)
        certify(graph, colors, clique, size)
        count += 1
    print("laminar covering families on three components", count)


def bipartition(n, edges):
    sides = {0: False}
    todo = [0]
    mismatch = False
    while todo:
        i = todo.pop()
        for a, b in edges:
            if i not in (a, b):
                continue
            j = b if i == a else a
            if j in sides:
                mismatch |= sides[j] == sides[i]
            else:
                sides[j] = not sides[i]
                todo.append(j)
    return len(sides) == n, None if mismatch else sides


def pairs_check(limits):
    n = len(limits)
    states = list(product(*(range(k+1) for k in limits)))
    options = list(combinations(range(n), 2))
    counts = [0, 0]
    for bits in product((False, True), repeat=len(options)):
        edges = [edge for edge, take in zip(options, bits) if take]
        connected, sides = bipartition(n, edges)
        if not connected:
            continue
        graph = conflict_graph(states, edges, limits)
        if sides is None:
            certify(graph, {s: s for s in states}, states, len(states))
        else:
            colors = {}
            clique = []
            for s in states:
                z = [k-x if sides[i] else x for i, (k, x) in enumerate(zip(limits, s))]
                least = min(z)
                colors[s] = tuple(value-least for value in z)
                if least == 0:
                    clique.append(s)
            certify(graph, colors, clique, len(states)-prod(limits))
        counts[sides is None] += 1
    print("limits", limits, "connected bipartite / odd-cycle graphs", counts)


if __name__ == "__main__":
    laminar_check()
    pairs_check((1, 2, 3))
    pairs_check((2, 2, 2, 2))
    states = list(product((0, 1), repeat=3))
    scopes = ((0, 1), (0, 2), (0, 1, 2))
    graph = conflict_graph(states, scopes, (1, 1, 1))
    a, b = (1, 0, 0), (0, 1, 1)
    certify(graph, {s: a if s == b else s for s in states}, [s for s in states if s != b], 7)
    assert len({stamp(s, scopes) for s in states}) == 8
    print("nonlaminar pair-plus-whole control: 8 sum tuples, 7 optimal values")
