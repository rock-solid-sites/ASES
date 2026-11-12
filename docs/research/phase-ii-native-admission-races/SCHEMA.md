---
title: Native Revocation versus Append Probe Schema
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

`probe.py` writes `evidence/run-06/raw.json` with schema identifier
`ases4-native-revocation-append-v1`. The probe captures the existing native F1,
F3, L5, L6, and F4 processes; it does not encode an alternate owner or
admission service.

The top-level `cases.append_first` and `cases.seal_first` records contain the
two histories. Each includes setup responses, F4 outer lifecycle and witness
initialization, initial native owner state, the F4 request/envelope, gate frame,
contender process request/reply, later owner transitions, denied requests,
and final F4 and owner captures.

Each direct owner capture (`owner_at_gate`, `owner_after_contender`,
`owner_after_append`, `owner_after_seal`, `owner_after_denial`, and
`owner_after_current_denial`, where present) is read from disk without a second
owner-process read. It includes:

* `current_raw_hex`, selected `selector`, immutable `record_raw_hex`,
  `record_sha256`, parsed `state`, and `native_owner`;
* `record_files`, the raw tree beneath the L5/L6 protected root;
* `f1_sqlite` and `l6_sqlite`, each a consistent read-only SQLite backup as
  `snapshot_raw_hex` plus its SHA-256, size, integrity result, and selected SQL
  rows;
* `l6_files`, the raw bytes, digest, size, inode, and mode for owned material.

F1 queries capture the kernel view, selected consumer observation, and retained
observations. L6 queries capture the unit live/sealed row and all dependency
catalog rows. The inventory object's owned bytes are captured independently.

Journal captures (`journal_at_gate`, `journal_after_contender`,
`journal_after_append`, `journal_after_denial`, and `journal_final`, as present)
include exact journal bytes and digest plus decoded event rows. `append_attempt`
contains the request, envelope, pre-request journal, and actual F4 gate frame.
`append_reply` retains the response and request-bound before/after journal
captures emitted by the reused native F4 helper. `f4_final_snapshot` retains
native sink status, witness status, calls, process frames, config, and journal.

In append-first, `historical_exact_retry_before` and
`historical_exact_retry_after` each contain journal bytes, sink `/status` with
the actual local cut, and witness `/status` with the published cut.
`historical_exact_retry` is the actual F4 `/submit` call using the original
request ID, payload, and outer authority version. Its call record includes
request, response, and before/after journal captures. `historical_status` is a
separate GET `/status` capture; it is not the exact-ID retry.

The checker derives append counts, authority selection, refusal invariants,
material stability, and post-move denial from these captured records. Summary
fields or admission certificates are not authority for those assertions.

Top-level `sources` retains the native-owner probe's ten frozen F1/F3/L5/L6/F4
source entries and adds hashes for the revocation probe, direct native helper,
and the executed F4 composition chain (continuation, composed sink, cold
factory, admission wrapper and guard, retry candidate, published-cut sink,
managed sink and base), plus the F1 bootstrap service. Each entry carries its
repository relative path and SHA-256.

The earlier `run-01` through `run-03` directories preserve instrumentation
failures; `run-04` is the successful capture before exact-ID retry coverage;
`run-05` captures the retry; `run-06` is the final capture with complete
executed-source provenance. Checkers should consume the path explicitly
supplied by the operator and should not merge runs.
