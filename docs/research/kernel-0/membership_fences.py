"""Asynchronous member changes with delayed, duplicable enable certificates."""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    # Each configured member was issued an enable certificate in that round.
    configs: tuple
    target: int | None
    floors: tuple
    opened: tuple

    @property
    def epoch(self):
        return len(self.configs) - 1


def bit(mask, i):
    return bool(mask & (1 << i))


def put(values, i, value):
    return values[:i] + (value,) + values[i + 1:]


def steps(s, limit, variant):
    n = len(s.opened)
    old = s.configs[-1]
    e = s.epoch
    if s.target is None and e < limit:
        for target in range(1 << n):
            yield f"begin {target:b}", replace(s, target=target)
    if s.target is not None:
        for i in range(n):
            if bit(old, i) and s.floors[i] <= e:
                yield f"fence {i} for {e+1}", replace(s, floors=put(s.floors, i, e+1),
                                                      opened=put(s.opened, i, -1))
        # The model reads the durable fence. A verified matching receipt can
        # implement this positive test because floors never decrease.
        required = old
        if variant == "intersection":
            required &= s.target
        if variant == "opened only":
            required &= sum(1 << i for i, h in enumerate(s.opened) if h == e)
        if all(not bit(required, i) or s.floors[i] > e for i in range(n)):
            yield f"commit {s.target:b}", replace(s, configs=s.configs + (s.target,),
                                                 target=None)
    for i in range(n):
        for h, members in enumerate(s.configs):
            if bit(members, i) and h >= s.floors[i] and s.opened[i] != h:
                yield f"deliver enable({i},{h})", replace(s, opened=put(s.opened, i, h))
        if variant == "lose floor" and s.floors[i] > 0:
            yield f"recover {i} without floor", replace(s, floors=put(s.floors, i, 0),
                                                       opened=put(s.opened, i, -1))


def search(n, rounds, variant):
    initial = State(((1 << n) - 1,), None, (0,) * n, (-1,) * n)
    paths = {initial: None}
    todo = deque([initial])
    terminal = set()
    while todo:
        state = todo.popleft()
        for i, h in enumerate(state.opened):
            if h >= 0 and (h != state.epoch or not bit(state.configs[-1], i)):
                trace = [f"append at {i} with {h}"]
                while paths[state] is not None:
                    state, action = paths[state]
                    trace.append(action)
                return len(paths), list(reversed(trace))
        if state.epoch == rounds and all(
            h == (rounds if bit(state.configs[-1], i) else -1)
            for i, h in enumerate(state.opened)
        ):
            terminal.add(state.configs)
        for action, successor in steps(state, rounds, variant):
            if successor not in paths:
                paths[successor] = (state, action)
                todo.append(successor)
    assert len(terminal) == (1 << n) ** rounds
    return len(paths), None


if __name__ == "__main__":
    for gates, changes in ((1, 4), (2, 3), (3, 2)):
        states, trace = search(gates, changes, "complete")
        assert trace is None
        print(f"{gates} gates / {changes} changes: {states} states")
    for mutant in ("intersection", "opened only", "lose floor"):
        _, trace = search(2, 2, mutant)
        assert trace is not None
        print(mutant, " -> ".join(trace))
