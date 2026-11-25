"""Finite schedule enumeration for one attachment, fresh writes and ordered tenures."""
from functools import lru_cache


def explore(width, last, rule):
    """Each tenure can emit once while current. Delivery may be delayed forever."""
    @lru_cache(None)
    def visit(current, sent, pending):
        # IDs in pending identify origins to the observer. Admission sees only tag.
        events = []
        if not sent:
            events.append(("send", current, True, pending | {current}))
        if current < last:
            next_tag = (current + 1) % width
            collision = any(origin % width == next_tag for origin in pending)
            if rule != "drain" or not collision:
                events.append(("replace", current + 1, False, pending))
        bad = None
        for origin in sorted(pending):
            matches = origin % width == current % width
            accepted = matches or rule == "cached"
            if accepted != (origin == current):
                bad = (f"deliver({origin}) at {current}",)
                break
            events.append((f"deliver({origin})", current, sent, pending - {origin}))
        for event, successor, emitted, queue in events:
            suffix = visit(successor, emitted, queue)
            if suffix is not None and (bad is None or 1 + len(suffix) < len(bad)):
                bad = (event,) + suffix
        return bad

    return visit(0, False, frozenset())


if __name__ == "__main__":
    for width in range(1, 6):
        for rule in ("tag", "cached", "drain"):
            witness = explore(width, width + 1, rule)
            expected = {"tag": width + 2, "cached": 3, "drain": None}[rule]
            assert (len(witness) if witness else None) == expected
            print(width, rule, " -> ".join(witness) if witness else "no mismatch")
