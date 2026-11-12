---
title: Native Acceptance and Producer Overlap Histories
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
# Native acceptance and producer overlap

## Result

The final bounded capture is
[`evidence/run-03/raw.json`](evidence/run-03/raw.json). It uses two isolated
fixtures: duplicate C acceptance, and an F1 C-to-D producer overlap while the
owner is preparing C. The raw evidence records process frames, direct immutable
owner selections, consistent F1/L6 snapshots, material bytes, and F4 journal
and witness state. See [SCHEMA.md](SCHEMA.md) for field details.

### Duplicate C acceptance

The fixture established and accepted native A, activated D, sealed the owner,
and had the actual F1 producer select world C with the same content bytes while
retaining A. Two owner processes were ready before the first C acceptance
entered the existing `material-prepared` gate. While that gate held the actual
F1 and L6 guards, the other process attempted `accept`. It returned `DENY`
with `OperationalError: database is locked`; its response reported no owner
selection or durable phase change. Direct snapshots before and after show no
second registration, selected record change, or extra material preparation
beyond the one candidate prepared by the gated operation.

Releasing the first owner committed one C registration, selecting its C pair
and `objectb`. The second owner then retried `accept` and returned the exact
selected registration with `duplicate: true`. Registration count, selected
ID, epoch, L6 rows, and owned bytes remained unchanged. The earlier A
registration and `objecta` remained present and accounted for.

### F1 producer D overlap and current use

In the separate fixture, the actual F1 producer service was ready before the
owner entered the C `material-prepared` gate. Its actual D accept request began
while the gate remained held. The request was pending at release; direct F1
snapshots immediately before release still selected C, and the prepared C
registration bound C. The first owner was released and committed C; the
producer operation then completed with its actual `commit` response for D.
This is one finite scheduler observation, not a liveness or fairness claim.

The native owner remained selected on C while F1 selected D. The actual D
descendant was activated on its original write-granting P/C path. A fresh C
envelope was denied specifically with
`native-f1-selected-retained-mismatch`; the owner had no effect reservation and
the F4 journal gained no effect. The outer F4 authority stayed active at
version 1.

The owner then sealed, accepted current F1 world D as a distinct native
registration, and activated D. A fresh current D envelope succeeded once as
published F4 event sequence 4, with the witness publishing the matching
journal cut. The final owner retains distinct A, C, and D issuer registrations
over equal content bytes, with all three objects present in L6 and bound by
their catalog rows.

## Evidence and limits

**WHY:** These histories test native acceptance serialization and the behavior
of an accepted native world when the real F1 producer changes worlds during
physical preparation.

**WHAT:** The evidence uses actual F1 producer processes, independent owner
processes, existing L5/L6/Owner transitions, and the composed F4 path, including
their selected records, database snapshots, bytes, requests, responses, and
publication frames.

**HOW CERTAIN:** Experimental. Run 03 proves one bounded overlap: the actual
producer call starts before release, F1 remains C at the pre-release snapshot,
and the D response completes after release. It does not establish universal
scheduler behavior.

**WHAT NOT TESTED:** Hostile same-UID or root actors, arbitrary rollback or
whole-host power loss, remote exactly-once delivery, fairness, or generalized
F3 confinement.

Runs 01 and 02 are preserved as successful but incomplete scheduling captures:
their actual producer service/request startup did not establish a request
overlap before release. They are not used as the final overlap evidence.
Production sources were not modified.
