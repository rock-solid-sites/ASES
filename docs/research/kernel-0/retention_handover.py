"""Track physical possession of one immutable version through holder changes."""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    # The history supplies arbitrarily delayed authentic summaries for the oracle.
    history: tuple
    target: int | None
    # Each holder stores (largest processed attempt, bytes pinned, last hold vote).
    holders: tuple

    def at(self, i, value):
        return replace(self, holders=self.holders[:i] + (value,) + self.holders[i+1:])


def named(mask, i):
    return bool(mask & (1 << i))


def steps(s, limit, variant):
    d = len(s.history) - 1
    q = d + 1
    m = s.history[-1]
    if s.target is None and d < limit:
        for n in range(1, 1 << len(s.holders)):
            yield f"begin {q} for {n:b}", replace(s, target=n)
    if s.target is not None:
        yield f"abort {q}", replace(s, history=s.history + (m,), target=None)
        needed = s.target & m if variant == "overlap only" else s.target
        if all(not named(needed, i) or v == q for i, (_, _, v) in enumerate(s.holders)):
            yield f"commit {q}", replace(s, history=s.history + (s.target,), target=None)
    for i, (t, held, v) in enumerate(s.holders):
        if any(h for _, h, _ in s.holders):
            # Conservatively allow a delayed hold from *every* past attempt.
            # Aborted proposal memberships are unnecessary for this overapproximation.
            last = q if s.target is not None and named(s.target, i) else d
            for r in range(t + 1, last + 1):
                yield f"pin bytes at {i} for {r}", s.at(i, (r, True, max(v, r)))
        for r, mask in enumerate(s.history):
            if r >= t or variant == "old deletion":
                # A summary can release a copy, but cannot fabricate missing bytes.
                keep = held and named(mask, i)
                if (r, keep) != (t, held):
                    yield f"apply summary {r} at {i}", s.at(i, (r, keep, v))


def search(n, limit, variant="complete", whole_loss=False):
    start = State((1,), None, tuple((0, i == 0, 0) for i in range(n)))
    paths = {start: None}
    todo = deque([start])
    while todo:
        s = todo.popleft()
        m = s.history[-1]
        missing = any(named(m, i) and not held for i, (_, held, _) in enumerate(s.holders))
        bad = not any(held for _, held, _ in s.holders) if whole_loss else missing
        if bad:
            path = ["no physical copy" if whole_loss else "required copy missing"]
            while paths[s]:
                s, action = paths[s]
                path.append(action)
            return len(paths), list(reversed(path))
        if s.target is None and variant == "complete":
            d = len(s.history) - 1
            assert all(t <= d for t, _, _ in s.holders)
            for i, (t, held, v) in enumerate(s.holders):
                wanted = named(m, i)
                if (t, held) != (d, wanted):
                    assert (f"apply summary {d} at {i}", s.at(i, (d, wanted, v))) in steps(
                        s, limit, variant)
        for action, nxt in steps(s, limit, variant):
            if nxt not in paths:
                paths[nxt] = s, action
                todo.append(nxt)
    return len(paths), None


if __name__ == "__main__":
    for n, limit in ((2, 3), (3, 2), (4, 2)):
        count, path = search(n, limit)
        assert path is None
        print(n, limit, count)
    for mutant in ("overlap only", "old deletion"):
        for all_gone in (False, True):
            _, path = search(2, 2, mutant, whole_loss=all_gone)
            assert path
            print(mutant, " -> ".join(path))
