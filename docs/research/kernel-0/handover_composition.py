"""Reproduce the two finite experiments in One-handover-across-resource-owners.md."""

from collections import Counter, deque
from dataclasses import dataclass, replace
from itertools import permutations, product


def common_cut(starts, ends, resources, old):
    """Calls at each sink are listed in its observed decision order; R is last."""
    latest_old = starts[-1]
    earliest_new = ends[-1]
    for sink in set(resources):
        latest_start = -1
        saw_new = False
        for i, resource in enumerate(resources):
            if resource != sink:
                continue
            latest_start = max(latest_start, starts[i])
            if latest_start >= ends[i] or (old[i] and saw_new):
                return False
            if old[i]:
                latest_old = max(latest_old, starts[i])
            else:
                earliest_new = min(earliest_new, ends[i])
                saw_new = True
    return latest_old < earliest_new


def serial_oracle(starts, ends, resources):
    """Run every serial order consistent with endpoints and each sink's order."""
    handover = len(resources)
    possible = set()
    for order in permutations(range(handover + 1)):
        position = {op: i for i, op in enumerate(order)}
        if any(ends[b] < starts[a] for i, a in enumerate(order) for b in order[i + 1:]):
            continue
        if any(position[a] > position[b] for b in range(handover)
               for a in range(b) if resources[a] == resources[b]):
            continue
        possible.add(tuple(position[i] < position[handover] for i in range(handover)))
    return possible


def check_histories():
    counts = Counter()
    # All five partitions of three labelled probes into owners, up to owner names.
    layouts = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2))
    for events in permutations(range(8)):
        starts = tuple(events.index(e) for e in range(0, 8, 2))
        ends = tuple(events.index(e) for e in range(1, 8, 2))
        if any(s > e for s, e in zip(starts, ends)):
            continue
        for resources in layouts:
            possible = serial_oracle(starts, ends, resources)
            for old in product((False, True), repeat=3):
                answer = common_cut(starts, ends, resources, old)
                if answer != (old in possible):
                    raise AssertionError((events, resources, old))
                counts[answer] += 1
    print(f"endpoint histories: {counts[True]} feasible, {counts[False]} infeasible")


@dataclass(frozen=True)
class State:
    current: int
    preparing: bool
    # 2e: open for e. 2e+1: frozen, with a durable vote for the move to e+1.
    gates: tuple[int, ...]
    receipts: frozenset[int] = frozenset()

    def gate_step(self, i, value):
        return replace(self, gates=self.gates[:i] + (value,) + self.gates[i + 1:])


def steps(state, rounds, variant):
    epoch = state.current
    if epoch < rounds and not state.preparing:
        yield f"begin {epoch + 1}", replace(state, preparing=True)
    for i, gate in enumerate(state.gates):
        if state.preparing and gate == 2 * epoch:
            yield f"freeze {i}", state.gate_step(i, gate + 1)
        if state.preparing and i not in state.receipts:
            current_vote = gate == 2 * epoch + 1
            # A completed previous round produced a genuine but obsolete vote.
            replay_vote = variant == "unbound vote" and epoch > 0
            if current_vote or replay_vote:
                yield f"record vote {i}", replace(state, receipts=state.receipts | {i})
        if gate % 2 and gate // 2 < epoch:
            yield f"activate {i}", state.gate_step(i, gate + 1)
        if gate % 2 and variant == "forget freeze":
            yield f"restore old gate {i}", state.gate_step(i, gate - 1)
    required = len(state.gates) - (variant == "omit last")
    if state.preparing and all(i in state.receipts for i in range(required)):
        yield f"commit {epoch + 1}", replace(state, current=epoch + 1, preparing=False,
                                            receipts=frozenset())


def bad_probe(state, variant):
    for i, gate in enumerate(state.gates):
        for origin in range(state.current + 1):
            if gate % 2:
                if variant != "early stale":
                    continue  # unresolved: no terminal decision or append
                accepted = False
            else:
                accepted = gate // 2 == origin
            if accepted != (origin == state.current):
                return f"sink {i}, tenure {origin}, {'append' if accepted else 'stale'}"
    return None


def explore(sinks, rounds, variant):
    start = State(0, False, (0,) * sinks)
    paths = {start: None}
    todo = deque([start])
    reached_final = False
    while todo:
        state = todo.popleft()
        mismatch = bad_probe(state, variant)
        if mismatch:
            path = [mismatch]
            while paths[state] is not None:
                state, action = paths[state]
                path.append(action)
            return len(paths), list(reversed(path))
        if state.gates == (2 * rounds,) * sinks and state.current == rounds:
            reached_final = True
        for action, new in steps(state, rounds, variant):
            if new not in paths:
                paths[new] = (state, action)
                todo.append(new)
    if not reached_final:
        raise AssertionError("missing fully activated successor")
    return len(paths), None


if __name__ == "__main__":
    check_histories()
    for sinks in range(1, 5):
        count, counterexample = explore(sinks, 3, "barrier")
        if counterexample:
            raise AssertionError(counterexample)
        print(f"barrier, {sinks} sinks, 3 replacements: {count} reachable states")
    for variant in ("early stale", "omit last", "unbound vote", "forget freeze"):
        _, trace = explore(2, 2, variant)
        if trace is None:
            raise AssertionError(f"missed control: {variant}")
        print(variant, " -> ".join(trace), sep=": ")
