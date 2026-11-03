# Management currentness experiment preregistration

**Status: preregistered before execution.** This is a disposable-record policy experiment against the frozen L5 manager helper, not host confinement or F3 acceptance.

## Question and bounded profile

Question: does an authorized manager operation require the state it changes to be the current published authority record, or can it commit using an authentic but stale in-memory state object? The frozen helper receives `st` as an argument and `commit()` selects the next record number from `CURRENT`; the experiment will observe whether it also compares the supplied state's identity/content with the current published record.

The only protocol operations used are the frozen `authorize_move` and `authorize_activate`. No manager service, authorization scheme, grant operation, or canonical requirement will be added. Since this helper models a single holder, a stale object supplied to it is an assumption stress test unless the trace demonstrates that the declared single-holder profile itself can retain and submit that object.

## Preregistered trace

1. Create a disposable protected directory with one minimal sealed bootstrap record and selector.
2. Copy that state as `stale0` before any manager operation.
3. Send valid `authorize_move(C, Q)` with the current state through the existing `manager_roundtrip`; require COMMITTED and verify record SHA plus selector.
4. Send valid `authorize_activate` with the newly current state; require COMMITTED and verify a distinct record SHA plus selector. This is the fresh-current positive control.
5. Submit a valid `authorize_move(C, Q)` using unchanged `stale0`, with the same valid manager identity/credential. Capture response, selector before/after, committed record bytes/hash, event list, current ingress, parent relation, and whether earlier activation event/history is preserved.

## Decision rule

Expected currentness behavior: step 5 is DENY, selector and all published bytes remain unchanged, and the reason identifies stale/current-record mismatch. A commit based on `stale0`, a changed selector, or loss/regression of the fresh activation state is a currentness counterexample for the tested helper interface.

If step 5 commits, report it as an assumption-stress result unless an in-profile path is shown that lets the one declared manager holder retain and submit the stale object. Do not call it an in-profile exploit based on a direct test-harness reference alone. If currentness is a trusted single-holder premise rather than an implemented check, preserve that distinction.

Bounds: one disposable record root, three manager calls, two successful transitions plus at most one stale replay, no worker, external route, filesystem policy, or host mutation. Stop after raw trace and decision are recorded.
