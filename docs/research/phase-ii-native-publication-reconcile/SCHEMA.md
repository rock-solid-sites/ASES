---
title: Native pending-publication reconciliation evidence schema
program: EDASES
layer: Research
document_type: Evidence Schema
status: Experimental
authority: Derived
dependencies:
  - PACKET.md
  - ../phase-ii-native-ownership/PACKET.md
downstream_consumers:
  - REPORT.md
---
# Evidence schema

`evidence/run-*/raw.json` is the unnormalized record emitted by `probe.py`.
It keeps process frames, exact JSONL bytes, owner protected-record bytes,
witness request and response records, F1 state, and test-gate observations in
one capture. Binary data is represented by the shared native helper's record
(`raw_hex`, SHA-256, size, device, inode); textual JSON frames retain their raw
line alongside the parsed value.

Top-level fields are:

| Field | Meaning |
|---|---|
| `schema` | Fixed probe schema identifier. |
| `started_ns`, `finished_ns` | Monotonic capture boundaries. |
| `sources` | Absolute path and SHA-256 for each source used by the probe. |
| `cases` | Actual isolated histories and bounded controls. |
| `processes` | Child process argv, pid, frames, exit state, and stderr. |
| `status` | `PASS` only after all mandatory assertions complete; otherwise `PROBE_FAILED`. |
| `failure` | Exception and traceback retained when capture execution fails. |

No normalized evidence overwrites `raw.json`. The report may interpret a
record, but the interpretation must point back to its case and concrete raw
fields. A missing case, source hash, process record, or raw state field is an
incomplete capture, not a pass.
