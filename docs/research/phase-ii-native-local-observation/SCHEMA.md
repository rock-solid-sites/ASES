---
title: Native local observation evidence schema
program: EDASES
layer: Research
document_type: Evidence Schema
status: Experimental
authority: Derived
dependencies:
  - PACKET.md
downstream_consumers:
  - REPORT.md
---
# Evidence schema

`evidence/run-*/raw.json` is the unnormalized capture from `probe.py`. It
records each actor's exact argv, process ID, raw stdout frames, exit state and
stderr; hashes and raw bytes for journal and protected owner/F1/L6 records;
the parsed event/index view; witness request/response records and revisions;
and snapshots at each crash or gate boundary.

Expected cases in a full capture:

| Case | Required evidence |
|---|---|
| `fsync-gap` | Actual sink gate after journal append/fsync, seq 4 in parsed journal, owner status reserved without sequence, and witness at prefix. |
| `strict-refusal` | Strict reconciler refusal with exact owner/journal/witness state unchanged. |
| `observed-and-settled` | Observer derives the event sequence, records local, publishes/settles without appending; journal effect count remains one. |
| `changed-world` | Same-content F1 world change, both retained worlds and owner registrations, source move/seal/activation, exact historical lookup, and current new-ID denial. |
| `observer-kill-retry` | Local selection before publication, killed observer, then strict completion without another observation or append. |
| `reserved-only` | Genuine guarded pre-append gate, no matching journal effect, strict and opt-in refusal with pending reservation unchanged. |
| `mismatched-payload` | Actual protected reservation / journal payload mismatch and exact refusal with unchanged files after the control mutation. |
| `parent-regression` | One full run of the prior publication reconciliation probe against the same source revision. |

Top-level `status` is `PASS` only after the case assertions and parent
regression pass. Probe-only follow-up captures may use
`LOCAL_CASES_PASS_REGRESSION_NOT_RUN` when a prior full capture has already
passed the parent regression and implementation hashes are unchanged. In this
task, run-03 is the full capture; run-04 reorders the world-change history and
omits only the parent regression. Failures are written to `failure` with
traceback and do not replace earlier attempt directories. The source manifest
pins every source used by the probe and wrapper.
