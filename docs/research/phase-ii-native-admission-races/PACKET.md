# Native authority revocation versus F4 append

ASES-4 priorities A/B follow-through. Parent draft #30, frozen source
f7b16ddbf34034ce1a0967c37cd92d5869f7e399. Reuse its actual F1 producer,
protected F3 issuer/owner, native L5/L6 state and composed F4 append path.
The existing native probe covers candidate/removal races, movement denial and
publication/reply loss. This extension tests native revocation versus append
at the actual existing before-admission and guarded gates; it is not a new
admission model or independent CI/review exercise.

## Architecture and eligible competing operations

Use Owner.seal versus F4 append from an initially live, accepted, active D
with actual write permission. A move itself requires sealing first, so a
move/append race would have an ineligible starting point. Sealing is the
eligible current-authority revocation. After sealing, perform the real fixed
move to Q and activation to show a freshly selected envelope still fails the
actual read-only path, rather than merely relying on stale metadata.

Append-first: pause native F4 at its existing guarded stage, after current
F1/L5/L6 checks and native effect reservation, before local journal append.
A separate real owner process attempts seal while those guards are held.
Capture its actual busy/refusal response and unchanged current selection and
material at that stage. Release F4; one append/publication succeeds. Retry
seal after the append settles, then move/activate. A new request with the
current native epoch/selector must fail the actual path check with no append.
The historical exact-ID result may remain observable, but grants no new use.

Seal-first: pause F4 at existing before-admission, before owner locks or effect
reservation. Commit seal with the actual owner. Release F4; the old envelope
must fail without an append/reservation. A fresh current selector/epoch must
also fail while sealed. Perform real move/activation and verify current-envelope
new-ID denial through the read-only path. Keep outer F4 authority/version current
so a protocol-level cold seal is not mistaken for native admission denial.

## Implementation boundary and evidence

Add only a bounded native probe and focused checker in this directory. Reuse
existing process/fixture helpers; no copied service model, preinstalled accepted
object, caller graph or evidence-pair alias. Production source should stay
unchanged because both gates already exist. If an actual missing interface
blocks the history, preserve the exact response and report it before inventing
a new hook or weakening the claim.

Capture actual subprocess IDs/frames, gate entry/release, requests/replies,
selected immutable CURRENT records, F1 selected/retained records, L6 inventory
and owned bytes, journal events/bytes and publication/witness results. Use direct
read snapshots while the owner guard is held; a second owner read may itself
be busy. Compare the state immediately before and after a refused contender,
accounting for the expected reserved-effect CURRENT transition before the gate.
Use consistent SQLite read snapshots/backups if WAL makes a plain file copy
incomplete. Preserve earlier instrumentation failures separately.

The checker must derive the assertions from raw selected state and journal,
not accept an admission certificate or summary boolean as authority. Check
exactly one successful append in append-first, zero in seal-first, no changes
from refused contenders, actual post-move D permission denial, stable material
and retained F1 evidence, and exact historical result without new effect.
Include two altered-evidence controls (invented append after revocation and a
changed owner selection during a supposedly refused contender) and require
rejection. Do not rerun the parent twelve histories without a source change.

WHY: close the concurrency proof gap between the native issuer and append guard.
WHAT: existing real processes, locks, selected state, bytes and journal boundary.
HOW CERTAIN: experimental until the two native histories and raw checker pass.
WHAT NOT TESTED: hostile same-UID/root, whole-host power loss, remote exactly-once
delivery, arbitrary rollback, generalized F3 confinement or automatic cancellation.
