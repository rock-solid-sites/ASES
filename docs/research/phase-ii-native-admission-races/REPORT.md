---
title: Native Revocation versus F4 Append Histories
program: EDASES
layer: Research
document_type: Experimental Report
status: Active
authority: Derived
dependencies:
  - PACKET.md
  - SCHEMA.md
downstream_consumers:
  - check.py
---
# Native revocation versus F4 append

## Result

The two bounded histories completed against the actual native owner and F4
implementation. Raw process frames, immutable `CURRENT` records, direct F1 and
L6 SQLite snapshots, owned material, journal bytes, witness status, exact-ID
retry, and executed source hashes are in
[`evidence/run-06/raw.json`](evidence/run-06/raw.json). The raw schema is
described in [SCHEMA.md](SCHEMA.md). This report records observations; the
independent checker owns assertion derivation.

### Append first

F4 reached its existing `guarded` gate after native authority checks and effect
reservation. A separate owner process attempted the actual `seal` operation.
It returned `DENY` with `OperationalError: database is locked`,
`durable_phase_changed: false`, and `owner_selection_changed: false`. Direct
snapshots taken at the gate and after the contender preserve the same selected
owner record and material. The reserved effect at the gate is the expected
transition made before the gate.

After releasing F4, the actual append and witness publication succeeded once
(effect event sequence 4). The owner then committed `seal`, followed by the real
move to Q and activation. A request carrying the newly selected current
envelope was denied with `native-current-path-denied`; it added no effect. The
exact earlier effect remains visible in F4 status as historical data.

After fresh-ID denial, the probe submitted the original request again through
the actual F4 `/submit` path with its original payload, request ID, and outer
authority version 1. The response was HTTP 200 `already-accepted` for event
sequence 4. It did not create another journal event or change the journal SHA.
The local sink cut and witness cut before and after the retry remained at that
same journal SHA, and the final journal still contains one `effect_accepted`
row. The separate `historical_status` GET is retained as a status observation,
not as evidence of the exact-ID retry.

### Seal first

F4 paused at its existing `before-admission` gate before owner guards and
reservation. A separate owner process committed `seal` while the gate was
held. Releasing F4 caused the original envelope to fail with
`stale-native-epoch`. The journal had no accepted effect and the selected
owner's effect map remained empty. A newly constructed envelope for the sealed
current selection also failed. The real move and activation then succeeded;
the fresh post-move envelope was denied with `native-current-path-denied`.

F4's outer authority remained at current version 1 in both histories. The
recorded rejections are native admission outcomes, not cold outer-authority
rejections.

## Evidence quality and limits

**WHY:** These histories address whether owner sealing can race with actual F4
append at the existing admission and guarded stages.

**WHAT:** Evidence comes from the reused F1/F3/L5/L6/F4 processes, their exact
request/reply frames, selected immutable records, SQLite backups, material
bytes, journal events, and witness status.

**HOW CERTAIN:** Experimental, bounded to the two captured process histories;
independent raw-state checking is recorded separately.

**WHAT NOT TESTED:** Hostile same-UID or root actors, whole-host power loss,
remote exactly-once delivery, arbitrary rollback, generalized F3 confinement,
or automatic cancellation.

The failed instrumentation runs are preserved at `evidence/run-01` through
`evidence/run-03`; successful `run-04` is preserved as the capture before exact
retry coverage, and `run-05` preserves the retry capture before complete source
provenance was added. The final capture is `run-06`. Production sources were
not modified.
