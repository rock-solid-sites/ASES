"""Replay distinguishability and differential checking of prefix reclamation."""
from collections import deque
from dataclasses import dataclass
from itertools import permutations
from math import comb, perm


def count_views(n):
    for k in range(n + 1):
        exact = set()
        presence = set()
        for accepted in permutations(range(n), k):
            answers = tuple(accepted.index(i) + 1 if i in accepted else 0 for i in range(n))
            exact.add(answers)
            presence.add(tuple(bool(answer) for answer in answers))
        assert len(exact) == perm(n, k)
        assert len(presence) == comb(n, k)
    print(f"N={n}: exact and membership counts agree for every k")


@dataclass(frozen=True)
class State:
    current: bool
    floor: int
    # Reference log retains (key, payload) in append order.
    log: tuple
    # Sparse receipts above the floor, in acceptance order.
    retained: tuple


def step(s, action, key, payload, window, mutant):
    if action == "retire":
        return State(False, s.floor, s.log, s.retained), None
    if action == "release":
        if key <= s.floor:
            return s, None
        accepted = {n for n, _ in s.log}
        required = range(s.floor + 1, key + 1)
        spec_allowed = all(i in accepted for i in required)
        covered = sum(1 for n, _, _ in s.retained if n <= key)
        allowed = (covered == key - s.floor)
        if mutant == "maximum":
            allowed = any(n == key for n, _, _ in s.retained)
        if allowed != spec_allowed:
            return s, ("release allowed", spec_allowed, allowed)
        if not allowed:
            return s, None
        rest = tuple(row for row in s.retained if row[0] > key)
        return State(s.current, key, s.log, rest), None

    # Independent specification: derive the first matching outcome by scanning
    # the full sequence and evaluating the release contract.
    spec = None
    if key <= s.floor:
        spec = "released"
    else:
        for receipt, (old_key, old_payload) in enumerate(s.log, 1):
            if key == old_key:
                spec = receipt if payload == old_payload else "conflict"
                break
        if spec is None:
            if not s.current:
                spec = "stale"
            elif key > s.floor + window:
                spec = "outside window"
            else:
                spec = len(s.log) + 1

    records = {n: (v, r) for n, v, r in s.retained}
    log = s.log
    retained = s.retained
    if key <= s.floor and mutant != "forget floor":
        result = "released"
    elif key in records:
        v, receipt = records[key]
        result = receipt if payload == v else "conflict"
    elif not s.current:
        result = "stale"
    elif key > s.floor + window:
        result = "outside window"
    else:
        result = s.floor + len(records) + 1
        log += ((key, payload),)
        retained += ((key, payload, result),)
    if result != spec:
        return s, (spec, result)
    assert len(retained) <= window
    return State(s.current, s.floor, log, retained), None


def search(n, window, mutant="none"):
    initial = State(True, 0, (), ())
    seen = {initial: None}
    queue = deque([initial])
    actions = [("call", i, v) for i in range(1, n + 1) for v in (0, 1)]
    actions += [("release", i, None) for i in range(1, n + 1)]
    actions.append(("retire", 0, None))
    while queue:
        s = queue.popleft()
        for action in actions:
            nxt, difference = step(s, *action, window, mutant)
            if difference:
                path = [action]
                while seen[s]:
                    s, previous = seen[s]
                    path.append(previous)
                return len(seen), list(reversed(path)), difference
            if nxt not in seen:
                seen[nxt] = s, action
                queue.append(nxt)
    return len(seen), [], None


if __name__ == "__main__":
    count_views(8)
    for n, w in ((3, 1), (4, 2), (5, 3)):
        count, _, err = search(n, w)
        assert err is None
        print(n, w, count, "reachable states")
    for mutant in ("maximum", "forget floor"):
        _, path, err = search(3, 2, mutant)
        assert err is not None
        print(mutant, path, err)
