"""Check completed histories with a known selector order and observed local edges."""
from collections import Counter, deque
from itertools import permutations, product


def schedule(allowed, edges):
    """Return a legal order and phase levels, or a conflicting precedence path."""
    successors = [[] for _ in allowed]
    incoming = [0] * len(allowed)
    for a, b in edges:
        successors[a].append(b)
        incoming[b] += 1
    ready = deque(i for i, count in enumerate(incoming) if not count)
    bound = [0] * len(allowed)
    parent = [None] * len(allowed)
    levels = {}
    order = []
    while ready:
        i = ready.popleft()
        level = next((p for p in sorted(allowed[i]) if p >= bound[i]), None)
        if level is None:
            path = [i]
            while parent[path[-1]] is not None:
                path.append(parent[path[-1]])
            return None, tuple(reversed(path))
        order.append(i)
        levels[i] = level
        for j in successors[i]:
            if level > bound[j]:
                bound[j], parent[j] = level, i
            incoming[j] -= 1
            if incoming[j] == 0:
                ready.append(j)
    if len(order) != len(allowed):
        return None, "cycle"
    return sorted(order, key=levels.get), levels


def convex_conflict(intervals, edges):
    """(lower after, upper before) for every probe or handover.

    Probes use their inclusive phase bounds; handover j uses (j, j-1).
    Return a pair with a separating reachable precedence, or a cycle.
    """
    reach = [set() for _ in intervals]
    for a, b in edges:
        reach[a].add(b)
    for via in range(len(reach)):
        for row in reach:
            if via in row:
                row.update(reach[via])
    for a, row in enumerate(reach):
        if a in row:
            return "cycle"
        for b in row:
            if intervals[a][0] > intervals[b][1]:
                return a, b
    return None


def oracle(probes, edges):
    """Run the two transitions and inspect each probe in every serial history."""
    for order in permutations(range(len(probes) + 2)):
        pos = {op: i for i, op in enumerate(order)}
        if any(pos[a] >= pos[b] for a, b in edges):
            continue
        phase = 0
        for op in order:
            if op < len(probes):
                if phase not in probes[op]:
                    break
            elif op == len(probes) + phase:
                phase += 1
            else:
                break
        else:
            return True
    return False


def crosscheck():
    # All directed precedence inputs on 2 probes + 2 handovers, subject to
    # their known handover order. Include impossible/cyclic observations.
    arcs = [(a, b) for a in range(4) for b in range(4)
            if a != b and {a, b} != {2, 3}]
    masks = [frozenset(i for i in range(3) if mask >> i & 1)
             for mask in range(1, 8)]
    counts = Counter()
    convex = Counter()
    for bits in product((0, 1), repeat=len(arcs)):
        edges = {(2, 3)} | {edge for edge, include in zip(arcs, bits) if include}
        for probes in product(masks, repeat=2):
            allowed = [{2 * p for p in phases} for phases in probes] + [{1}, {3}]
            order, detail = schedule(allowed, edges)
            ok = order is not None
            if ok != oracle(probes, edges):
                raise AssertionError((probes, edges, order))
            if all(len(p) == max(p) - min(p) + 1 for p in probes):
                intervals = [(min(p), max(p)) for p in probes] + [(1, 0), (2, 1)]
                conflict = convex_conflict(intervals, edges)
                assert (conflict is None) == ok
                convex[ok] += 1
            if ok:
                assert all(order.index(a) < order.index(b) for a, b in edges)
                assert all(detail[i] in allowed[i] for i in order)
                assert [detail[i] for i in order] == sorted(detail.values())
            elif detail != "cycle":
                assert all(edge in edges for edge in zip(detail, detail[1:]))
                bound = 0
                for i in detail[:-1]:
                    bound = min(p for p in allowed[i] if p >= bound)
                assert all(p < bound for p in allowed[detail[-1]])
            counts[ok] += 1
    print("serial comparison", dict(counts))
    print("convex precedence comparison", dict(convex))


def long_obstructions():
    for n in range(2, 12):
        # Handovers span all probes. Record the probes in client order.
        probes = [set(range(n)) - {i} for i in range(n)]
        for drop in [None, *range(n)]:
            retained = [p for i, p in enumerate(probes) if i != drop]
            m = len(retained)
            allowed = [{2 * p for p in phases} for phases in retained]
            allowed += [{2 * i + 1} for i in range(n - 1)]
            edges = [(i, i + 1) for i in range(m - 1)]
            edges += [(i, i + 1) for i in range(m, len(allowed) - 1)]
            order, _ = schedule(allowed, edges)
            assert (order is None) == (drop is None)
    print("minimal negative-comparison chains verified for 2..11 phases")


if __name__ == "__main__":
    crosscheck()
    long_obstructions()
