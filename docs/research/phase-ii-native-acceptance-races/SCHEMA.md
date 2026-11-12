---
title: Native Acceptance Concurrency Probe Schema
program: EDASES
layer: Research
document_type: Evidence Schema
status: Active
authority: Derived
dependencies:
  - PACKET.md
  - ../phase-ii-native-ownership/probe.py
downstream_consumers:
  - check.py
---
# Raw evidence schema

`probe.py` writes `evidence/run-03/raw.json` with schema identifier
`ases4-native-acceptance-races-v1`. It keeps the two eligibility histories
separate in `cases.duplicate_acceptance` and `cases.producer_overlap`.

Both histories start from actual F1 world A and a real native F3 registration
for A, activate the native path, seal it, then use the actual F1 producer to
select same-byte world C. They record the real owner acceptance gate
`material-prepared`, the owner requests and process frames, and direct selected
state without relying on a second owner read while guards are held.

`direct_owner_snapshot` records `CURRENT` bytes and selected immutable record
bytes/digest, parsed selected state, the protected record tree, a consistent
read-only F1 SQLite backup and selected/retained rows, a consistent L6 catalog
backup and rows, and raw owned material. F1 snapshots include the kernel view,
selected observation, retained observations, SQLite image, and integrity
result. L6 snapshots include the unit and full dependency inventory; each live
material byte record carries its digest and size.

The duplicate fixture records `owner_before_guard`, `owner_at_gate`,
`owner_after_contender`, `owner_after_first_accept`, and snapshots around the
contender's duplicate retry. It retains both A and C registration/material
state, exact responses, and owner process frames.

The producer fixture records `f1_before_producer`, `f1_at_gate_before_release`,
and `f1_after_producer`; the producer operation includes start, release, and
response timestamps and distinguishes a refusal from a result pending at
release. Its real F1 producer process is ready before the owner gate, and the
actual F1 operation frame records when the `accept` request was sent. If the
observed operation is refused, its real retry occurs after the C acceptance
commits. The fixture then records C-current/F1-D native denial,
actual D acceptance and activation, and one published D-world F4 effect. F4
captures include journal bytes/events, witness and sink cuts/status, and the
actual request/reply.

Top-level `sources` contains the frozen native ownership source manifest plus
the directly executed F4 composition sources. The checker derives expected
state and append counts from raw records/bytes and those pinned sources.

`producer_operation.producer_process_ready_ns` records the prestarted F1
producer; `producer_operation.first_attempt.result.operation` contains the
actual F1 request and response frames with their start/end timestamps.
`disposition_at_release` reports whether the request was already complete or
still pending at release; `observed_outcome` reports what the actual response
did after that boundary. The run-03 capture establishes readiness and actual
F1 call before release, C still selected immediately before release, and D
response after release.

The final `sources` manifest contains 24 entries: the parent native ownership
manifest and the direct F1 Holder plus executed F4 composition sources.
`run-01` and `run-02` preserve earlier successful but incomplete scheduling
captures; `run-03` is the final bounded capture with a producer request proven
to overlap the actual owner gate.
