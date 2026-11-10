# ASES-4 native F3 acceptance and owning-domain slice

Frozen 10 November 2026. Authority is complete Work Notes ASES-4, not ASES-2's
queue. Base #24 `e2b81e844216b66771256068d8358dcd7e042298` retains #15/#11.
Consume #18 `c384e62f` and #27 `06d86e93` without copying unrelated evidence.
Comparator: Work Unit A–L, Closure C1–C13/H13/H14, Verification F3/F4/T12/T13/
T15/T23 at `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`.

## Native authority and representation

Add an isolated F3-side **Owner** interface. Explicit trusted initial management
establishes empty sealed P/C/Q/D with intrinsic identity/genesis/created-by/project.
The interface creates the graph and issues identity; no caller-submitted graph,
pair certificate or metadata alias confers acceptance/ownership. P permits write,
Q permits read; D is a real native-created dependent of C.

Retain native L5 schema1/immutable record/CURRENT as the single selected source
for native ownership, registrations, selected world, epoch, child lifecycle,
pending effects and logical disposition. Add a supported `native_owner` extension.
Reuse actual original L5 manager_roundtrip and graph/permissions/enabled/content
checks. Replace only its publication helper with the same algorithm plus file
and directory fsync before ACK. No new global database or Kernel primitive.

Place original L6 Store at ROOT/protected, so its objects are the actual
protected/objects read by original L5 verified_content. L6 is an owned storage
inventory, not a second alias asserted to be C. Native bootstrap establishes this
complete domain. L6's sealed inventory has no exposed interior attachment;
global C/D use is the L5 relationship. Required administrative boundary/provenance
records remain protected at the issuer even after data-envelope removal.

Protected bootstrap records the actual F1 source DB path and device/inode.
Current host/store identity and truthful opaque F1 observations remain disclosed
premises, not rollback resistance or invented semantic truth. Ordinary recovery
does not bootstrap or obtain observations from the test supervisor.

Every supported operation and append admission orders guards as F1 BEGIN
IMMEDIATE -> stable L5 management-writer flock -> L6 BEGIN IMMEDIATE. A native
L6 phase may COMMIT while F1/flock remain held; no other supported owner can
interleave. A initially assumes trusted participating owner entrypoints; B adds
the actual #27 distinct owner/worker UID route. Same-owner-UID compromise stays
outside that boundary.

## Transition contract

- `establish` is explicit initialization only. No accepted-object fixture.
- `accept` reads actual selected F1 subject/pair and retained observations under
  the real F1 transaction; a request supplies no trusted acceptance bundle.
  Native L6 put/fsync/COMMIT first prepares exact bytes as bounded material.
  Native L5 CURRENT publication then issues a registration ID, exact pair/world,
  material reference, native domain/D ownership, selected content and new epoch.
  This publication is **F3 acceptance**. Exact selected duplicate observes its
  existing registration without new material/epoch. Same bytes/new opaque world
  are a distinct acceptance. Retain older registrations/material until authorized
  disposition; never modify/delete required F1 observations.
  Native L6's local `kind=candidate` records the preparation origin; it is not
  the global F3 acceptance authority. Its later F3-selected material remains a
  live catalogued durable dependent. Consumers must read the protected native
  registration, not promote a local kind label into accepted meaning. Both local
  kinds equally block removal and receive the same physical integrity checks.
- Preparation and acceptance are explicit recoverable stages, not an atomic
  cross-store transfer. Prepared-only material stays owned and blocks removal.
  Loss after CURRENT requires readback, never a no-effect denial. Unknown files
  and directories block removal. Recovery uses native retained state, not memory.
- `seal` disables ingress and active units, increments epoch, preserves work.
  `move`/`activate` call actual L5 manager logic. `recover` validates the supported
  whole owner/material view, preserves work and publishes a fresh sealed epoch
  before explicit activation. Constructor/read does not mutate or bootstrap.
- `dispose_child(D)` is an explicit sealed decision: drop D's live references,
  mark it logically disposed, retain historical intrinsic metadata. Original fixed
  graph nodes stay interpretable; native_owner distinguishes live vs disposed D.
- `dispose_content(id)` requires sealed/live domain, D disposed, no pending effect.
  Publish logical disposition in CURRENT before native L6 dispose/unlink. Lost
  cleanup remains bounded and blocks removal; explicit cleanup completes only a
  retained authorized decision. F1 source evidence is never erased.
- `remove` requires all children/content/candidates dispositioned, no pending
  effects and complete actual inventory empty. Publish native logical removal,
  then finish native L6 remove/rmdir. Report logical shared-domain disposition and
  physical data-envelope cleanup separately; no secure erasure claim.

## F4 integration, parent-owned

Extend existing #24/#15 append guard with a native-owner profile. Configuration
identifies protected owner root only: no test pair/import alias/epoch/root subset.
Envelope values are expected comparisons against the issuer's current native
record. Reread actual F1 selected/retained pair, L5 full path/selector/actual bytes,
native registration/lifecycle and L6 inventory under guards through real append.
Legacy test-only profile remains explicitly distinct.

Retain pending effect in protected owner record before append; after actual
append/fsync retain local accepted seq. Any gap stays pending and blocks removal.
After reservation/append uncertainty is not a no-effect denial. Parent integrates
actual F4 validated journal/current cut and fresh live witness settlement; no
CLI accepting `published=true` or a caller certificate. Reuse exact retry/cold:
historical observation after disposition never grants a new append. No remote
cancellation or external exactly-once guarantee.

## Deciding native histories

Establish -> actual F1 accept -> native F3 accept -> authorized D/F4 effect ->
seal/move/activate -> denied D use -> removal blocked by child/object/pending ->
actual publication settlement -> sealed authorized disposition -> removal/readback.
Also duplicate registration, same-byte changed world, stale selector/epoch, lost
reply/restart, preparation crash, interrupted disposition, unknown debris,
competing creation/removal and a useful neighboring continuation.

Native backend native_owner.py/owner CLI; parent owns existing admission/native
sink integration; native harness/checker separate. Python reuses actual existing
Python component boundaries as a disposable experiment, not a new framework.
Freeze public API before implementation. Preserve pins, raw process/SQLite/bytes/
selector/witness evidence and negative controls. No independent CI/review/PR
inventory, backup work, production, provider workload, host config or main merge.
