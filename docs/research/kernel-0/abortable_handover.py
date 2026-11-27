"""Safety and reachable controls for attempts that can abort without all votes."""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    # log[r] is the selected tenure after deciding attempt r (oracle history).
    log: tuple
    pending: bool
    # Each gate has (greatest processed attempt, open tenure or -1, last vote).
    gates: tuple

    def gate(self, i, values):
        return replace(self, gates=self.gates[:i] + (values,) + self.gates[i + 1:])


def steps(s, rounds, mutant):
    d = len(s.log) - 1
    q = d + 1
    if not s.pending and d < rounds:
        yield f"begin {q}", replace(s, pending=True)
    if s.pending:
        yield f"abort {q}", replace(s, log=s.log + (s.log[-1],), pending=False)
        # Replay of any authentic vote is possible. The last vote suffices
        # to decide whether a vote for the unique pending attempt can exist.
        if all(v == q or (mutant == "reuse abort vote" and v > s.log[-1])
               for _, _, v in s.gates):
            yield f"commit {q}", replace(s, log=s.log + (q,), pending=False)
    for i, (t, h, v) in enumerate(s.gates):
        for r in range(t + 1, d + int(s.pending) + 1):
            yield f"prepare {r} at {i}", s.gate(i, (r, -1, r))
        for r, c in enumerate(s.log):
            if (r >= t or mutant == "accept older summary") and (t, h) != (r, c):
                yield f"summary ({r},{c}) at {i}", s.gate(i, (r, c, v))


def run(n, rounds, mutant="none"):
    start = State((0,), False, ((0, 0, 0),) * n)
    todo = deque([start])
    paths = {start: None}
    while todo:
        s = todo.popleft()
        if any(h >= 0 and h != s.log[-1] for _, h, _ in s.gates):
            path = ["append at open gate with obsolete tenure"]
            while paths[s]:
                s, action = paths[s]
                path.append(action)
            return len(paths), list(reversed(path))
        if not s.pending:
            # One latest authentic summary per lagging gate suffices to reopen
            # all of them, with no intermediate decisions replayed.
            d, c = len(s.log) - 1, s.log[-1]
            for i, (t, h, v) in enumerate(s.gates):
                if (t, h) != (d, c):
                    assert (f"summary ({d},{c}) at {i}", s.gate(i, (d, c, v))) in steps(
                        s, rounds, mutant)
        for action, nxt in steps(s, rounds, mutant):
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
