---
title: Native pending-effect admission — compiled implementation packet
version: 0.1.0
program: ASES
layer: Research
document_type: Implementation Packet
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-23
---

# Native pending-effect admission — compiled implementation packet

**Operation:** implement and verify one bounded experimental repair. **Technical owner:** WNASES-4 / draft [PR #43](https://github.com/rock-solid-sites/ASES/pull/43). **Source to inspect, unchanged before work:** `rock-solid-sites/ASES@e91fb4b14875487dee9c19cc764e72655ba534c0` (PR #43); parent native custody/recovery chain #38 → #36 → #35 → #30. **Status:** specification compiled from pinned source and captured baseline; implementation and post-change tests **not run**.

## Established facts and corrected scope

The original `docs/research/phase-ii-native-pending-admission/REPORT.md` at the pinned head records genuine native `guarded`-gate EOF, not manually injected reservations. Its corrected `run-02` captured two distinct `reserved` IDs with no journal `effect_accepted` and unchanged witness cut; after one unresolved A, the normal fresh B was later published. Original `run-01` had live-writer sequencing mistakes and is not the definitive recovery observation. Existing strict reconciliation and local observation refuse eventless A without altering protected state.

**Correction to the old PACKET:** `seal` is allowed with a pending effect (observed and source-confirmed). `dispose_child` is denied with `pending-in-domain-effect`. Do not add a seal guard as part of this repair. The original packet's phrase “seal/disposition remains blocked” is false for seal.

## Frozen behavior and scope

1. In **one native Owner**, while any effect has a status other than `published`, a previously unseen request ID cannot reserve a new effect. This is a conservative availability constraint, not a recovery/cancellation guarantee.
2. The existing *same-ID* exact accepted replay/lookup remains an observation and must not be blocked by the new-ID rule. Do not change receipt/recovery semantics or silently grant a fresh effect from an old ID. A duplicate attempting a new reservation remains a duplicate; it is not a second effect.
3. A known pre-reservation rejection must remain an ordinary admission denial. It must not become `native-effect-requires-reconciliation`, create a retained reservation, or claim local publication uncertainty.
4. An already-reserved effect remains retained and unknown until the existing supported explicit reconciliation/local observation can establish its actual journal/witness evidence. Eventless reservations cannot be fabricated into published effects, cancelled, erased or retried as new dispatch.
5. Preserve current F1 observation and selected world, protected native F3 registration, L5 CURRENT and epoch, L6 retained bytes/inventory, real F4 append/witness/retry path, and owner/worker custody. No new registry, database, status/schema, global lock, synthetic source, generic timeout, or Kernel primitive.
6. `seal` and `recover` retain their existing lifecycle semantics. Any pending effect continues to block dependent/content/domain disposition according to the existing owner guards; do not broaden this task into a seal-policy redesign.

## Exact implementation seam (source-inspected)

- `docs/research/phase-ii-native-ownership/native_owner.py`, `Session.pending()` (line 294 in pinned head) already means “any status != published”. `Session.reserve_effect()` (304–307) currently checks only duplicate ID and commits a `reserved` record. Retain duplicate-ID check **first**, then enforce `not self.pending()` before mutation/commit.
- `docs/research/phase-ii-native-ownership/native_sink.py`, `NativeAdmission.guard()` (53–144): within the existing `with self.owner.locked() as session:` and **after the existing native authority/retained-material checks**, perform the matching new-ID/pending precheck **before** the code sets `reserved = True` and calls `session.reserve_effect(...)` (currently lines 120–123). A known refusal should flow through the existing `legacy.Denied` path. `Denied` is a `ValueError` subclass; setting the uncertainty flag first converts its refusal into a misleading reconciliation error.
- Preserve the owner guard's current F1 `BEGIN IMMEDIATE`, L5 writer flock and L6 `BEGIN IMMEDIATE` ordering, rather than a separate check-then-use path. Confirm rejection is immutable by reading the owner, F1, journal and witness states before/after.
- `docs/research/phase-ii-native-pending-admission/baseline_probe.py` is a reusable native process fixture. Existing #35/#36 explicit recovery probes and #38 UID custody report are regression sources. Do not copy their huge evidence directories into a new PR.

If live observation contradicts any claim above, preserve the contradictory evidence and return the minimum decision to the technical owner instead of redesigning the model.

## Falsifiable acceptance histories

| ID | Actual history and required observation |
| --- | --- |
| A1 | Fresh A reaches real `guarded` EOF pre-append: exactly one `reserved` A, no accepted journal event, unchanged witness/current cut. Existing uncertainty response remains truthful. |
| A2 | With A pending, fresh B is refused *before reservation*; owner `effects` count, owner selection, F1, L6, journal bytes, witness cut/revision unchanged. No `native-effect-requires-reconciliation` or false `owner_reservation_committed` claim for B. |
| A3 | Repeated B and fresh C cannot grow pending effects; duplicate/refusal classification remains accurate without owner mutation. |
| A4 | From a fresh clean fixture, normal sequential A then B publish two distinct effects; neither blocks the next once the prior effect is actually `published`. |
| A5 | A genuinely journaled, published-but-unsettled original effect is settled by existing explicit #35/#36 recovery (incl. fsync-gap/local observation where supported); exact old replay/lookup works and new current B can subsequently be admitted. No second append for the old effect. |
| A6 | With an eventless pending A, `seal` remains allowed; `dispose_child` / applicable content/domain disposal refuse without destroying A or owner/source evidence; strict reconcile/observe do not invent an A event. |
| A7 | Rerun affected #35/#36 parent histories once against repaired code; retain their precise positive/negative evidence. Include at least one altered-evidence control that the independent checker rejects. |

Record actual HTTP/Unix response fields rather than assuming a fixed error-code shape beyond the required truthful classification. Use fresh output directories and keep source SHA-256s, raw requests/replies, process/gate facts, owner/F1/L6/journal/witness readback and exact test commands/exit codes.

## Work product and stopping condition

Implement only in a **fresh isolated branch based on PR #43's pinned head**, preserving that draft and the stacked parents. Add focused tests/checks and a short report referencing the new evidence, source revision and WHAT-NOT-TESTED. No main merge, deployment, new provider operation or unrelated work. Stop when A1–A7 are demonstrated and a separate verifier can reproduce/check the claims, or on a concrete contradicted invariant with a smallest-possible decision request.

**Builder residual prompt:** “Implement the native pending-admission packet at this path against the pinned PR #43 head. Preserve all stated semantics; run the bounded native and parent regression histories and commit raw evidence. Return only source SHA, passed/failed case IDs, and any contradiction that needs a decision.”

**Independent verification handoff:** artifact/commit + claims A1–A7 + canonical relevant invariants and source revision, **without the builder's implementation rationale**. Same-family functional verification is useful but is not cross-family formal independent review.

## Source/authority receipt

Read/applied: current `skills/current/compact-prompt/SKILL.md` v1.1.1; `skills/current/compile-build/SKILL.md` v1.0.1; canonical `docs/methodology/ASES Bounded Project Build Method.md`; `docs/methodology/ASES Task-Scoped Information and Handoff Method.md`. Technical evidence: PR #43 `PACKET.md`, `REPORT.md`, `baseline_probe.py`, native owner/sink; current #35/#36/#38 and WNASES-4 context. The original research packet is **superseded for the seal claim only**; this document is a derived task packet, not new Kernel or project-wide policy. All conclusions are bounded to the cited experimental profile.
