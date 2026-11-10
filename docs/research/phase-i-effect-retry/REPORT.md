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
  - check_mutations.py
  - evidence/final/raw.json
---

# Result

The isolated candidate enforces at-most-once local `effect_accepted` journal
acceptance per request ID for the tested flat C/p `/submit` path. Exact retries
are observations of the original local event only after the pinned receipt-aware
wrapper freshly verifies the complete current local cut at the witness. A
same-ID payload conflict returns 409 without appending. This does not deliver an
external effect or claim exactly-once delivery.

`/commit-obligation` and `/deliver-obligation` return 403
`unsupported-in-retry-candidate` before the pinned handler runs. Both histories
leave journal bytes unchanged. Obligation commit or delivery therefore gains no
retry contract or identity semantics in this experiment.

# Native evidence

The candidate and probe execute the frozen receipt extension source capture
`9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9`. The exact `published-cut/cut_sink.py`
SHA-256 is `5bd76e093f20acb264b1d7e5688c7353822f6a13686fd9d4c18af56e33c7c5ed`;
the checker pins this digest and also pins the receipt capture's managed sink
and run source hashes. No pinned source capture was edited.

The lost receipt uses the receipt source's own `drop_publish_reply_once`
instrument. It is armed at the real witness, which commits `/publish`, records
`reply_suppressed: true`, then closes the connection before sending its reply.
There is no relay or proxy in this final run. The baseline returns 503 with
`local_control_committed=true`; its retry returns 201 and creates a second row.
The candidate returns 503 for the first attempt and 200 `already-accepted` on
retry, preserving the original event sequence and accepted authority version.
Same-process and cold-recovery retries each keep one row for that ID.

The native probe and independent raw-evidence checker passed 11 histories:

- Lost receipt baseline and candidate retry; payload conflict; a new ID; stale
  authority; and observation after revoke.
- Real SIGKILL before append, after local fsync but before publication, and after
  publication but before the client reply.
- Explicit remote publication rejection, refusal after divergent local commit,
  and cold restart with a fresh empty witness.
- Refusal of both obligation routes without journal change.
- A journal capacity failure on both the initial request and exact retry. Both
  return the underlying 503 error, append no row, and carry no no-effect outcome.
- Rejection of a legacy journal containing a duplicate request ID.

The independent checker reads raw journal bytes, verifies their digests and
sequences, validates payload hashes, replays the tested authority transitions,
checks fresh witness observations and original receipt fields, and checks
process exits and stderr. `check_mutations.py` also passed three negative
controls: a duplicate effect row with its journal bytes and digest recalculated,
a false original event sequence, and a mismatched verified journal receipt were
all rejected.

Reproduce the native run and checks with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/research/phase-i-effect-retry/probe.py --out docs/research/phase-i-effect-retry/evidence/<new-run>
PYTHONDONTWRITEBYTECODE=1 python3 docs/research/phase-i-effect-retry/check.py docs/research/phase-i-effect-retry/evidence/<new-run>/raw.json
PYTHONDONTWRITEBYTECODE=1 python3 docs/research/phase-i-effect-retry/check_mutations.py docs/research/phase-i-effect-retry/evidence/<new-run>/raw.json
```

The final retained artifacts are [raw.json](evidence/final/raw.json) and
[check.json](evidence/final/check.json). This is finite local evidence under
the pinned source, local process and trusted-root premises; it is not a
production assurance result.

# Boundary and remaining assumptions

WHY: request identity must be reconstructed from the durable accepted-event
journal after restart; an in-memory cache would permit a second local acceptance.
An equal-ID retry is safe to report only after the live witness verifies the
complete current local cut. WHAT: real witness-side receipt suppression after
commit, raw journal readback, process-kill gates, remote rejection, cold replay,
obligation refusal, a failed append, and independent raw-evidence mutation
controls. HOW CERTAIN: evidence-based for the finite tested `/submit` histories
in flat C/p using the pinned receipt extension. WHAT-NOT-TESTED:

- Trusted root custody, all external management entrypoints, and exclusion of
  an unguarded same-UID writer. The inherited advisory lock is cooperative.
- Witness durability, rollback detection, broader authentication, or continued
  witness availability. An empty witness restart was tested to refuse; durable
  witness recovery was not added.
- Partial/torn writes or arbitrary storage faults. The observed capacity error
  does not append; other storage faults remain native recovery failures and are
  not reclassified as successful or no-effect retries.
- External side-effect execution or delivery. One journal acceptance says
  nothing about an external system carrying out the effect.
- A production policy for reading accepted results after revoke. The local
  management boundary can observe retained results; broader access policy is
  absent.
- Other roots, units, positions, obligation workflows, unguarded concurrent
  mutation, storage migration, or broader history bounds.

A local append followed by explicit remote rejection remains locally committed
and remotely unresolved. The candidate exposes that distinction, does not
append a second effect, and refuses cold recovery against the divergent cut. A
fresh witness without retained state refuses rather than resetting genesis. No
production migration or ASES-wide contract change follows from this experiment.
