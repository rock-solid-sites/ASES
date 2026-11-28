"""Enumerate membership changes, issued summaries and admission after selector loss."""

from collections import defaultdict, deque
from dataclasses import dataclass, replace


CLOSED = -1


@dataclass(frozen=True)
class State:
    decisions: tuple
    gates: tuple
    target: int | None = None
    issued: frozenset = frozenset({0})


def contains(mask, gate):
    return bool(mask & (1 << gate))


def move_gate(state, index, gate):
    return replace(state, gates=state.gates[:index] + (gate,) + state.gates[index + 1:])


def deliveries(state):
    for index, (floor, open_tenure) in enumerate(state.gates):
        for number in state.issued:
            tenure, membership = state.decisions[number]
            selected = tenure if contains(membership, index) else CLOSED
            if number >= floor and (number, selected) != (floor, open_tenure):
                yield f"deliver summary {number} at {index}", move_gate(
                    state, index, (number, selected)
                )


def steps(state, rounds):
    decided = len(state.decisions) - 1
    current, members = state.decisions[-1]
    pending = decided + 1
    if state.target is None and decided < rounds:
        for target in range(1 << len(state.gates)):
            yield f"begin {pending} for {target:b}", replace(state, target=target)
    if state.target is not None:
        yield f"abort {pending}", replace(
            state, decisions=state.decisions + ((current, members),), target=None
        )
        if all(
            not contains(members, index) or gate == (pending, CLOSED)
            for index, gate in enumerate(state.gates)
        ):
            yield f"commit {pending}", replace(
                state, decisions=state.decisions + ((pending, state.target),), target=None
            )
    if decided not in state.issued:
        yield f"issue summary {decided}", replace(state, issued=state.issued | {decided})
    for index, (floor, _) in enumerate(state.gates):
        for number in range(floor + 1, decided + 1 + int(state.target is not None)):
            if contains(state.decisions[number - 1][1], index):
                yield f"deliver prepare {number} at {index}", move_gate(
                    state, index, (number, CLOSED)
                )
    yield from deliveries(state)


def reachable(gates, rounds):
    initial_members = 1
    initial = State(((0, initial_members),), ((0, 0),) + ((0, CLOSED),) * (gates - 1))
    paths = {initial: ()}
    queue = deque([initial])
    while queue:
        state = queue.popleft()
        for action, successor in steps(state, rounds):
            if successor not in paths:
                paths[successor] = (*paths[state], action)
                queue.append(successor)
    return paths


def old_admission_channels(state):
    # Direct continuation oracle. A presently open gate may append at once.
    # Otherwise try every distinct deliverable old summary and append on arrival.
    result = {index for index, (_, tenure) in enumerate(state.gates) if tenure != CLOSED}
    for _, successor in deliveries(state):
        result.update(index for index, (_, tenure) in enumerate(successor.gates)
                      if tenure != CLOSED)
    return frozenset(result)


def issuance_ceilings(state):
    return tuple(max(
        (number for number in state.issued if contains(state.decisions[number][1], index)),
        default=-1,
    ) for index in range(len(state.gates)))


def required_by_bounds(ceilings, floors):
    return frozenset(index for index, (ceiling, floor) in enumerate(zip(ceilings, floors))
                     if ceiling >= floor)


def fence_and_commit(state, fenced, new_members):
    fresh = len(state.decisions)
    gates = tuple((fresh, CLOSED) if index in fenced else gate
                  for index, gate in enumerate(state.gates))
    # Recovery does not add any summary from the rolled-back selector image.
    return replace(state, gates=gates,
                   decisions=state.decisions + ((fresh, new_members),))


def audit(gate_count, rounds):
    paths = reachable(gate_count, rounds)
    universe = frozenset(range(gate_count))
    views = defaultdict(dict)
    checks = 0
    strict = 0
    latent = 0
    for state in paths:
        if state.target is not None:
            continue
        current, members = state.decisions[-1]
        exposure = old_admission_channels(state)
        assert all(contains(members, gate) for gate in exposure)
        assert all(tenure == CLOSED or tenure == current for _, tenure in state.gates)
        ceilings = issuance_ceilings(state)
        assert exposure == required_by_bounds(ceilings, (gate[0] for gate in state.gates))
        latent += any(state.gates[gate][1] == CLOSED for gate in exposure)
        for mask in range(1 << gate_count):
            fenced = frozenset(gate for gate in universe if contains(mask, gate))
            after = fence_and_commit(state, fenced, 1)
            assert old_admission_channels(after) == exposure - fenced
            floors = (floor if gate in fenced else 0
                      for gate, (floor, _) in enumerate(state.gates))
            journal_required = required_by_bounds(ceilings, floors)
            assert exposure <= journal_required
            if journal_required <= fenced and any(
                contains(members, gate) for gate in universe - fenced
            ):
                strict += 1
            checks += 1

            # The responder returns its local floor and open tenure, with no
            # membership payload. Its subsequent fresh fence can be identical
            # across these worlds. Every selector restores the initial image.
            view = (len(state.decisions), current, tuple(
                (gate, state.gates[gate]) for gate in sorted(fenced)
            ))
            key = bool(exposure - fenced), any(
                contains(members, gate) for gate in universe - fenced
            )
            if fenced and all(contains(members, gate) for gate in fenced):
                worlds = views[view]
                if key not in worlds or len(paths[state]) < len(paths[worlds[key]]):
                    worlds[key] = state

    conflicts = [worlds for worlds in views.values()
                 if (False, False) in worlds and (True, True) in worlds]
    assert conflicts and strict and latent
    print(f"{gate_count} gates, {rounds} attempts: {len(paths)} states, "
          f"{checks} fence checks, {latent} states with a latent open, "
          f"{len(conflicts)} blind observation conflicts, "
          f"{strict} safe journal-based cases with an unavailable current member")
    if gate_count == 2:
        conflict = min(conflicts, key=lambda worlds: sum(
            len(paths[worlds[key]]) for key in ((False, False), (True, True))
        ))
        for key, label in [((False, False), "unavailable gate absent"),
                           ((True, True), "unavailable gate exposed")]:
            print(f"  {label}: {' -> '.join(paths[conflict[key]])}")


def check_availability_signature():
    for variable_gates in range(1, 9):
        sets = tuple(
            frozenset(gate for gate in range(variable_gates) if contains(mask, gate))
            for mask in range(1 << variable_gates)
        )
        signatures = {tuple(exposed <= available for available in sets) for exposed in sets}
        assert len(signatures) == len(sets)
    print("8 variable gates: all 256 exposure sets have distinct availability signatures")


def main():
    audit(2, 3)
    audit(3, 2)
    check_availability_signature()


if __name__ == "__main__":
    main()
