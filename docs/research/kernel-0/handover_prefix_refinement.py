"""Finite trace and prefix checks for a Work Unit handover with a pending append."""

from itertools import combinations, permutations, product


def trace(accepted, coin, evidence, reported_cut=None):
    replacement = "replace" if reported_cut is None else "replace_and_report"
    reply = "ok" if reported_cut is None else ("ok", reported_cut)
    events = [("call", "append"), ("call", replacement)]
    if evidence == "early" and accepted:
        events.append(("append_commit", "X"))
    events.extend([("return", (replacement, reply)), ("coin", coin)])
    if evidence == "late":
        events.append(("decision", accepted))
    events.extend([
        ("return", ("append", "accepted" if accepted else "stale")),
        ("call", "read"),
        ("return", ("read", accepted)),
    ])
    return tuple(events)


def linearizations(history):
    """All sequential completions of the operations invoked in this prefix."""
    invoked = {value: at for at, (kind, value) in enumerate(history) if kind == "call"}
    completed = {value[0]: (at, value[1])
                 for at, (kind, value) in enumerate(history) if kind == "return"}
    pending = sorted(invoked.keys() - completed.keys())
    for size in range(len(pending) + 1):
        for chosen in combinations(pending, size):
            for order in permutations((*completed, *chosen)):
                positions = {op: at for at, op in enumerate(order)}
                if any(
                    reply_at < invoked[later] and positions[earlier] > positions[later]
                    for earlier, (reply_at, _) in completed.items() for later in order
                ):
                    continue
                current_old = True
                contents = False
                outcomes = []
                for operation in order:
                    if operation == "append":
                        reply = "accepted" if current_old else "stale"
                        contents = current_old or contents
                    elif operation in {"replace", "replace_and_report"}:
                        reply = "ok" if operation == "replace" else ("ok", contents)
                        current_old = False
                    else:
                        reply = contents
                    if operation in completed and completed[operation][1] != reply:
                        break
                    outcomes.append((operation, reply))
                else:
                    yield tuple(outcomes)


def is_prefix(shorter, longer):
    return longer[:len(shorter)] == shorter


def check_histories(histories):
    children = {}
    for history in histories:
        for end in range(len(history) + 1):
            prefix = history[:end]
            children.setdefault(prefix, set())
            if end:
                children[prefix[:-1]].add(prefix)

    sequences = {prefix: tuple(linearizations(prefix)) for prefix in children}
    assert all(sequences.values()), "ordinary linearizability failed"

    def has_solution(prefix, chosen):
        return any(
            is_prefix(chosen, candidate)
            and all(has_solution(child, candidate) for child in children[prefix])
            for candidate in sequences[prefix]
        )

    return len(children), has_solution((), ())


def check_cut_alphabet():
    # Include every speculative stale completion in addition to the required
    # earlier accepted operations. Even these larger prefix sets are disjoint.
    for width in range(1, 6):
        prefixes = {}
        for subset in range(1 << width):
            accepted = tuple(i for i in range(width) if subset & (1 << i))
            unaccepted = tuple(i for i in range(width) if not subset & (1 << i))
            witness_count = 0
            for accepted_order in permutations(accepted):
                for size in range(len(unaccepted) + 1):
                    for stale_order in permutations(unaccepted, size):
                        linearized = (*accepted_order, "replace", *stale_order)
                        assert prefixes.setdefault(linearized, subset) == subset
                        witness_count += 1
            assert witness_count
        assert len(set(prefixes.values())) == 1 << width
        print(f"{width} pending appends: {len(set(prefixes.values()))} disjoint cut classes")


def main():
    honest_cases = tuple(product((False, True), repeat=2))
    late_cases = tuple((coin, coin) for coin in (False, True))
    for label, cases, evidence, expected in [
        ("honest, public", honest_cases, None, False),
        ("honest, witnessed", honest_cases, "early", True),
        ("late, public", late_cases, None, False),
        ("late, witnessed", late_cases, "late", False),
    ]:
        histories = [trace(accepted, coin, evidence) for accepted, coin in cases]
        prefixes, has_prefix_map = check_histories(histories)
        assert has_prefix_map == expected
        print(f"{label}: {prefixes} legal prefixes, prefix map {has_prefix_map}")

    assert {trace(*case, None) for case in late_cases} < {
        trace(*case, None) for case in honest_cases
    }
    for disposition in (False, True):
        assert sum(disposition == coin for coin in (False, True)) == 1
    assert sum(accepted == coin for accepted, coin in late_cases) == 2
    print("late public traces are a strict subset; coin matches 2/2 instead of 1/2")

    reported = [trace(accepted, coin, None, accepted)
                for accepted, coin in honest_cases]
    prefixes, has_prefix_map = check_histories(reported)
    assert has_prefix_map
    for declared in (False, True):
        disagreeing = trace(not declared, not declared, "late", declared)
        assert not tuple(linearizations(disagreeing))
    print(f"cut in replacement reply: {prefixes} legal prefixes, both false reports rejected")
    check_cut_alphabet()


if __name__ == "__main__":
    main()
