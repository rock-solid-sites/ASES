# Management conformance repair preregistration

**Status: preregistered before implementation.** This is a bounded repair to the frozen L5 helper under the declared single-holder, no-concurrent-writer assumption.

## Canonical basis

`Phase-I-Closure.md` says activation is a separate current authorized event that creates only supported currently allowed routes, recomputes full-path constraints after a move/recovery, and cannot rely on historical grants/observations (line 558). Recovery is sealed before activation (line 556); the L5 implementation packet requires L4/L5 transitions from sealed state. The move itself is a sealed whole transition (line 557). The conformance checks will therefore require the supplied state to equal the currently selected published record, and activation input to be fully sealed and inactive before publishing active/unsealed state.

No concurrency guarantee is added: current-record comparison plus commit relies on the selected single-holder/no-concurrent-writer assumption.

## Smallest patch

1. In `manager_roundtrip`, after authentication and before dispatch, load `CURRENT` and compare a canonical serialization of supplied `st` to the selected record's parsed state. Deny mismatches without changing selector or store.
2. Make activation accept the supported positive parent cases (C under P before relocation or Q after relocation), but require all Work Units inactive and sealed, no current ingress, and a structurally valid graph. Then record activation through the existing handler.
3. Change the integrated positive control to call that handler; remove direct activation mutation/commit from the control flow.

## Preregistered controls and expected outcomes

- Fresh current move and activation: COMMITTED with distinct selected records and correct event/current ingress.
- Replay of the previously captured authentic stale bootstrap state after fresh move+activation: DENY; selector and every protected-store file remain byte-identical.
- Wrong credential against the fresh current record: DENY; selector and store remain byte-identical.
- Current but unsealed/inactive activation input fixture: DENY; selector and store remain byte-identical.
- Compliant positive activation under P and post-move activation under Q both occur through `manager_roundtrip`.

## Bounds and claim limits

One temporary record root per case; manager API only; no worker or host confinement. Preserve prior stale-state stress result. A direct test fixture may construct a malformed current record for the sealed-precondition control, but this is not a claimed reachable manager transition. No check-and-commit concurrency claim, host enforcement claim, L5/L6 acceptance, or general manager service is in scope.
