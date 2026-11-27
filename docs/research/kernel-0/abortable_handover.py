"""Safety and reachable controls for attempts that can abort without all votes."""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    # log[r] is (selected tenure, membership) after decision r (oracle history).
    log: tuple
    target: int | None
    # Each gate has (greatest processed attempt, open tenure or -1, last vote).
    gates: tuple

    def gate(self, i, values):
        return replace(self, gates=self.gates[:i] + (values,) + self.gates[i + 1:])


def member(mask, i):
    return bool(mask & (1 << i))


def steps(s, rounds, mutant, dynamic=False):
    d = len(s.log) - 1
    q = d + 1
    current, members = s.log[-1]
    if s.target is None and d < rounds:
        targets = range(1 << len(s.gates)) if dynamic else (members,)
        for target in targets:
            yield f"begin {q} for {target:b}", replace(s, target=target)
    if s.target is not None:
        yield f"abort {q}", replace(s, log=s.log + (s.log[-1],), target=None)
        # Replay of any authentic vote is possible. The last vote suffices
        # to decide whether a vote for the unique pending attempt can exist.
        required = members & s.target if mutant == "intersection" else members
        if all(not member(required, i) or v == q or (mutant == "reuse abort vote" and v > current)
               for i, (_, _, v) in enumerate(s.gates)):
            yield f"commit {q}", replace(s, log=s.log + ((q, s.target),), target=None)
    for i, (t, h, v) in enumerate(s.gates):
        for r in range(t + 1, d + int(s.target is not None) + 1):
            if member(s.log[r - 1][1], i):
                yield f"prepare {r} at {i}", s.gate(i, (r, -1, r))
        for r, (c, mask) in enumerate(s.log):
            installed = c if member(mask, i) else -1
            if (r >= t or mutant == "accept older summary") and (t, h) != (r, installed):
                yield f"summary {r} at {i}", s.gate(i, (r, installed, v))


def run(n, rounds, mutant="none", dynamic=False):
    # Keep the last gate initially absent in the dynamic case, even if n=1.
    members = (1 << (n - int(dynamic))) - 1
    start = State(((0, members),), None,
                  tuple((0, 0 if member(members, i) else -1, 0) for i in range(n)))
    todo = deque([start])
    paths = {start: None}
    while todo:
        s = todo.popleft()
        c, members = s.log[-1]
        if any(h >= 0 and (h != c or not member(members, i))
               for i, (_, h, _) in enumerate(s.gates)):
            path = ["append at open gate with obsolete tenure"]
            while paths[s]:
                s, action = paths[s]
                path.append(action)
            return len(paths), list(reversed(path))
        if s.target is None:
            # One latest authentic summary per lagging gate suffices to reopen
            # all of them, with no intermediate decisions replayed.
            d = len(s.log) - 1
            for i, (t, h, v) in enumerate(s.gates):
                installed = c if member(members, i) else -1
                if (t, h) != (d, installed):
                    assert (f"summary {d} at {i}", s.gate(i, (d, installed, v))) in steps(
                        s, rounds, mutant, dynamic)
        for action, nxt in steps(s, rounds, mutant, dynamic):
            if nxt not in paths:
                paths[nxt] = s, action
                todo.append(nxt)
    return len(paths), None


if __name__ == "__main__":
    for n, rounds in ((1, 5), (2, 4), (3, 3)):
        count, path = run(n, rounds)
        assert path is None
        print(n, rounds, count)
    for mutant in ("reuse abort vote", "accept older summary"):
        _, path = run(2, 2, mutant)
        assert path
        print(mutant, " -> ".join(path))

    for n, rounds in ((1, 4), (2, 3), (3, 2)):
        count, path = run(n, rounds, dynamic=True)
        assert path is None
        print("changing membership", n, rounds, count)
    _, path = run(2, 2, "intersection", dynamic=True)
    assert path
    print("intersection", " -> ".join(path))
