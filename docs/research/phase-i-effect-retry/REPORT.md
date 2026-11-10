---
title: F4 durable request identity and retry observation
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - PACKET.md
  - docs/research/phase-i-sol-integration/PLAN.md
  - docs/research/phase-i-sol-integration/REPORT.md
related_documents:
  - candidate.py
  - probe.py
  - check.py
  - evidence/final/raw.json
---

# Result

The isolated candidate enforces one durable local `effect_accepted` event per
request ID in the selected flat C/p profile. An exact retry is returned as an
observation of the original event only after the existing receipt-aware wrapper
freshly verifies that the live witness holds the complete current local cut. A
same-ID/different-payload request returns conflict without appending bytes. A
new ID still follows the pinned authority check and original append/publication
path.

This is **at-most-once local acceptance per ID** in the tested boundary. It is
not exactly-once delivery to an external system, and it does not add a durable
outbox or an automatic reconciliation path.

# Native evidence

The [frozen packet](PACKET.md) was implemented as a separate subclass and
probe. The candidate reuses the pinned `cut_sink.py`, managed state, writer
lock, append+fsync, live witness CAS, receipt handling, HTTP service and cold
recovery. No pinned source capture was edited. An independent standard-library
checker validates the raw journal bytes and digests, event sequence and
payload hashes, a separate replay of the tested C/p authority transitions,
witness/check replies, and the expected process and HTTP outcomes. It does not
import [candidate.py](candidate.py).

The fresh baseline reproduces the incident: the real witness commits a
publication, the relay drops only its reply, and the sink returns 503 with
`local_control_committed=true`. Retrying the same ID and exact payload returns
201 and adds a second `effect_accepted` row. The raw journal contains both IDs
and payload bytes.

With the candidate, the same real lost-reply sequence returns 503 for the first
attempt, then 200 `already-accepted` on retry. The observation carries the
original event sequence and accepted authority version, plus the current
verified journal hash and witness revision. Same-process and cold-recovery
histories each retain exactly one effect row. The checker also confirms:

- A same-ID payload that differs in exact UTF-8 bytes, including a composed vs
decomposed Unicode spelling, returns 409 and leaves the journal digest
unchanged.
- A new ID still succeeds under current authority. A new ID with stale
  authority is denied without journal bytes. An empty ID returns 400.
- An effect accepted before native revoke remains observable with its original
authority version after revoke, after a new live check of the current cut.
- A real SIGKILL before append leaves the effect absent; cold recovery admits a
  valid retry. A real SIGKILL after fsync but before publication preserves the
  local event and cold startup refuses the divergent witness cut. A real
  SIGKILL after publication but before the client reply allows cold recovery
  and an observation retry without another append.
- An explicit witness rejection is distinguished from lost reply. The first
  response is 503 `cut-publication-rejected` with
  `local_control_committed=true`. Under unresolved divergence, an existing
  same-ID conflicting payload still returns 409 before witness checking; an
  exact retry returns 503 `retry-observation-unresolved` with the original
  local event sequence and committed flag. A fresh ID adds no bytes, and cold
  recovery refuses the mismatch.
- Restarting the in-memory witness without retained state makes sink recovery
  refuse readiness. A valid legacy journal with two actual baseline rows for
  one ID is rejected by candidate recovery instead of selecting either row.

The parent receipt source pin is
`9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9`. Pinned source file hashes and the
complete raw process, gate, HTTP, witness, and journal capture are in
[evidence/final/raw.json](evidence/final/raw.json); the independent verdict is
also retained at [evidence/final/check.json](evidence/final/check.json). It is
reproduced with:

```sh
python3 docs/research/phase-i-effect-retry/probe.py --out docs/research/phase-i-effect-retry/evidence/<new-run>
python3 docs/research/phase-i-effect-retry/check.py docs/research/phase-i-effect-retry/evidence/final/raw.json
```

The recorded final run passed all nine histories. It used actual local sink and
witness processes, a disposable in-process HTTP relay for the dropped reply,
and process gates at before-append, after-fsync/before-publication, and
after-publication/before-client-reply. The checker returned PASS for all nine
cases.

# Boundary and remaining assumptions

WHY: request identity belongs in the validated durable effect journal so a
restart can reconstruct it; an in-memory cache would permit a duplicate after
crash. An equal-ID retry is safe to report only when the live witness freshly
confirms the exact current local cut. WHAT: baseline duplicate reproduction,
actual dropped witness reply, exact journal readback, three process-kill gates,
remote rejection, cold replay, invalid controls and independent raw checking.
HOW CERTAIN: evidence-based for the finite local C/p histories under the pinned
single-writer and trusted-root premises. WHAT-NOT-TESTED:

- Trusted root custody, all external management entrypoints, and exclusion of
  an unguarded same-UID writer. The inherited advisory writer lock remains
  cooperative; see the separate custody boundary finding.
- Witness durability, rollback detection, authentication beyond the existing
  loopback nonce/root checks, or continued witness availability. Empty witness
  restart was tested to refuse; durable witness recovery was not added.
- Partial/torn writes and arbitrary storage faults. A torn journal remains a
  native recovery failure; it is not converted to an accepted retry.
- External side-effect execution or delivery. One journal acceptance is not a
  claim that a remote effect occurred exactly once.
- A production authorization policy for reading old accepted results after
  revoke. The selected trusted local management boundary can observe retained
  results; broader information-access policy remains absent.
- Other roots, units, positions, obligation workflows, concurrent unguarded
  mutation, storage migration, or broader history bounds.

A local append followed by explicit remote rejection remains committed locally
and unresolved remotely. The candidate labels that state; it does not roll back
the event, append a second effect, or guess that publication succeeded. A fresh
witness with no retained state also refuses rather than resetting genesis. No
production migration or ASES-wide contract change follows from this experiment.
