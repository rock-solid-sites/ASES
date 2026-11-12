# Concurrent native acceptance and an overlapping producer world update

ASES-4 A/B follow-through, frozen parent draft #30 at
f7b16ddbf34034ce1a0967c37cd92d5869f7e399. Add bounded native histories and a
focused raw checker, not another ownership model or production API. Existing
source guards and material-prepared gate should suffice; preserve parent code.

## Eligible history

Use the actual setup helpers to establish native world A. Through the real F1
producer, select world C with identical subject bytes, retaining A. Before
holding a guard, start two real owner processes so startup reads themselves do
not confound the operation. First owner accepts C and pauses at the existing
material-prepared gate after native L6 preparation but before selecting the new
registration. Second owner attempts accept against that same current C.
Capture its actual lock/busy result and direct state before/after, requiring
no second preparation or issuer selection. Release the first owner; one C
registration and material become selected. Retry the second owner: it must
return that exact registration as duplicate with no extra object, epoch change
or selection. Keep the earlier A object/registration accounted for.

While the first acceptance holds its real F1 transaction and owner guards,
request a real producer update to world D using the same bytes. Capture the
actual busy response, or a bounded pending request that commits only after
release; do not fabricate a particular scheduling result. Direct F1 snapshots
before release must remain C and the accepted C registration must bind that
protected world. If the producer is refused, retry it after first-owner commit.
Record actual request/release/response timing and disclose what was observed;
no universal liveness or scheduler claim follows from a finite overlap.

With current F1 now D but native selection C, activate the real native D unit
on its original write-granting P/C path. Configure the actual F4 sink. A fresh
current native epoch/selector/envelope C must fail specifically at the native
F1 selected/retained comparison, despite identical content and actual D write
permission. Outer F4 authority stays current; no effect reservation or append.
Then seal and accept current D through the real owner and reactivate it. A
fresh D-world envelope must produce one real published effect. A, C and D have
different issuer registrations/worlds while content bytes remain equal and all
retained material/inventory is accounted for. No caller graph or evidence pair
confers authority.

## Evidence and checks

Reuse actual F1/L5/L6/native owner/F4 process helpers. Capture gate/process
frames, actual requests/replies/times, selected immutable CURRENT records,
consistent F1/L6 snapshots, raw material, journal and fresh witness protocol.
A second owner read while guards are held may itself be busy; take direct raw
snapshots for refused-contender comparisons. Source hashes must cover the
existing essential native manifest and directly executed composition files,
not an exhaustive repository/runtime inventory.

The checker derives state from raw records/bytes and actual source functions;
summary PASS or an admission certificate is not authority. Assert exactly one
new C registration/preparation, idempotent duplicate retry, correct protected
world at acceptance, no native/F4 side effect on stale-world current-use denial,
then exactly one authorized D-world effect. Require two altered-evidence
controls to reject: a duplicate issuer/material insertion and a fabricated
accepted event under mismatched current F1 world. Preserve failed instrument
attempts separately. Do not rerun old twelve histories absent source changes.

If the real producer cannot express the overlap with supported APIs, retain the
concrete response and finish duplicate acceptance plus post-change denial/
authorized counterpart. Do not change production semantics to force an outcome.

WHY: test issuer serialization and opaque world identity across actual components.
WHAT: existing native transactions, selected records, physical preparation and
F4 append/publication. HOW CERTAIN: experimental until bounded histories and raw
checks pass. WHAT NOT TESTED: hostile same-UID/root, arbitrary rollback/power loss,
remote exactly-once delivery, fairness, or generalized F3 confinement.
