"""Two membership-rollback witnesses for the abortable protocol.

Each witness is a complete, hand-driven data-point history, not an
exhaustive enumeration: the scenarios apply the published membership rules
step by step and assert the end conditions directly.  They demonstrate
that a selector which resumes with the membership view of a genuine
earlier image fails on both sides of the dichotomy recorded in the run
log:

  witness A  a removed gate whose removal summary never reached it keeps
             its escaped vote deliverable, and that vote co-authorizes
             the resumed selector's replacement of an already-committed
             attempt;
  witness B  a true current member absent from the stale membership view
             never receives the prepare of a later resumed attempt, stays
             open at the displaced tenure, and accepts an append under an
             obsolete tenure after that attempt commits.

Protocol rules follow the membership study: prepares go to the outgoing
membership M, commit q requires a receipt from every member of M and
installs the attempt's proposed membership N, and a summary (r, b, M_r)
binds the decided attempt, its selected tenure and the membership of that
decision; a gate applies it only at or above its floor, opening for b when
the summary includes it and otherwise advancing its floor while closed.
Votes are channel state and survive the selector's image restore.

Run from the repository root:
  python3 docs/research/kernel-0/glm-g4/membership_rollback_witness.py
"""


def snapshot(state):
    """A genuine earlier selector image: deep-copied durable state."""
    return dict(d=state["d"], c=state["c"], pending=state["pending"],
                members=set(state["members"]),
                receipts=set(state["receipts"]),
                proposal=set(state["proposal"]),
                decisions={k: (kind, b, set(m))
                          for k, (kind, b, m) in state["decisions"].items()})


def start(state, proposal):
    q = state["d"] + 1
    state["pending"] = q
    state["proposal"] = set(proposal)
    state["receipts"] = set()
    return "start %d (proposes membership %s)" % (q, sorted(proposal))


def prepare(state, gates, channel, outgoing):
    """Issue prepares for the pending attempt to every outgoing member."""
    q = state["pending"]
    for g in outgoing:
        t, h, mode = gates[g]
        if q > t:
            gates[g] = (q, h, 0)
            channel.add((q, g))
    return "prepare %d -> members %s" % (q, sorted(outgoing))


def deliver_vote(state, channel, g):
    q = state["pending"]
    assert (q, g) in channel, "no deliverable vote for the attempt"
    state["receipts"].add(g)
    return "vote %d from gate %d" % (q, g)


def commit(state, outgoing, proposal):
    """Commit the pending attempt with receipts from every outgoing member."""
    q = state["pending"]
    assert state["receipts"] >= set(outgoing), "incomplete outgoing receipts"
    state["d"] = state["c"] = q
    state["pending"] = 0
    state["members"] = set(proposal)
    state["decisions"][q] = ("commit", q, set(proposal))
    return "commit %d (outgoing %s, installs %s)" % (
        q, sorted(outgoing), sorted(proposal))


def restore(state, image):
    """The selector restores a genuine earlier image; gates stay true."""
    state.clear()
    state.update(snapshot(image))
    return "selector restores image d=%d M=%s" % (
        state["d"], sorted(state["members"]))


def summary(state, gates, r):
    """Issue and deliver the decided summary for attempt r to every gate."""
    kind, b, members = state["decisions"][r]
    for g in gates:
        t, h, mode = gates[g]
        if r >= t:
            if g in members:
                gates[g] = (r, b, 1)
            else:
                gates[g] = (r, h, 0)
    return "summary (r=%d, b=%d, M=%s) delivered" % (r, b, sorted(members))


def witness_a():
    """A removed gate's escaped vote co-authorizes the resumed commit."""
    state = dict(d=0, c=0, pending=0, members={0, 1}, receipts=set(),
                 proposal=set(), decisions={})
    gates = {0: (0, 0, 1), 1: (0, 0, 1)}
    channel = set()
    steps = []

    steps.append(start(state, {0}))                    # propose removing 1
    image = snapshot(state)                            # genuine pending image
    steps.append(prepare(state, gates, channel, state["members"]))
    steps.append(deliver_vote(state, channel, 0))
    steps.append(deliver_vote(state, channel, 1))
    steps.append(commit(state, state["members"], {0}))  # true commit removes 1
    steps.append(summary(state, gates, 1))             # gate 1 misses this

    true_members = set(state["members"])
    assert true_members == {0}, "gate 1 was removed by the true commit"
    assert gates[1] == (1, 0, 0), "gate 1 closed, never told of removal"

    steps.append(restore(state, image))               # stale view {0, 1}
    assert state["pending"] == 1
    steps.append(deliver_vote(state, channel, 0))      # escaped votes still
    steps.append(deliver_vote(state, channel, 1))      # deliverable
    steps.append(commit(state, state["members"], {0}))

    # The resumed replacement of an already-committed attempt was
    # co-authorized by the removed gate's escaped vote: the commit rule
    # demanded a receipt from every member of the stale view, and gate 1
    # belongs to that view although the true current membership excludes it.
    assert state["d"] == 1, "the resumed selector re-decided attempt 1"
    assert 1 in state["receipts"], "the removed gate's vote was counted"
    assert true_members == {0}
    print("witness A: removed gate 1 co-authorized the resumed commit of"
          " attempt 1")
    for s in steps:
        print("  " + s)
    return steps


def witness_b():
    """A true member omitted from the stale view serves a stale tenure."""
    state = dict(d=0, c=0, pending=0, members={0}, receipts=set(),
                 proposal=set(), decisions={})
    gates = {0: (0, 0, 1), 1: (0, 0, 1)}
    channel = set()
    steps = []

    steps.append(start(state, {0, 1}))                 # propose adding 1
    image = snapshot(state)                             # genuine pending image
    steps.append(prepare(state, gates, channel, state["members"]))  # member 0
    steps.append(deliver_vote(state, channel, 0))
    steps.append(commit(state, state["members"], {0, 1}))
    steps.append(summary(state, gates, 1))             # gate 1 joins, opens

    true_members = set(state["members"])
    assert true_members == {0, 1}
    assert gates[1] == (1, 1, 1), "gate 1 joined and opened at tenure 1"

    steps.append(restore(state, image))                # stale view {0}
    steps.append(deliver_vote(state, channel, 0))       # escaped vote for 1
    steps.append(commit(state, state["members"], {0}))  # re-decides attempt 1
    steps.append(start(state, {0}))                    # next attempt fences
    steps.append(prepare(state, gates, channel, state["members"]))  # {0} only
    steps.append(deliver_vote(state, channel, 0))
    steps.append(commit(state, state["members"], {0}))  # installs tenure 2

    # Gate 1 is a true current member, never prepared by the resumed
    # attempts, and is still open at the displaced tenure 1: any append
    # delivered now is accepted under an obsolete tenure although the
    # replacement to tenure 2 has already committed.
    assert gates[1] == (1, 1, 1), "gate 1 was never fenced"
    assert state["c"] == 2, "the resumed selector installed tenure 2"
    print("witness B: true member 1 open at obsolete tenure 1 after the"
          " replacement to 2")
    for s in steps:
        print("  " + s)
    return steps


def main():
    witness_a()
    print()
    witness_b()
    print("verified: both membership-rollback failure shapes are reachable"
          " under the published rules with a genuine-image restore")


if __name__ == "__main__":
    main()
