# F4 bounded Codex check — 2026-11-04

## First verdict

**Supported within the selected process-loss fixture; checker provenance is incomplete.** The retained raw observations and an independent two-case run distinguish acceptance before ACK from early ACK: after `SIGKILL`, accepted-before-ACK has one exact live/cold-readable journal record and no HTTP response; early-ACK returned 201 before the kill and has a missing journal. The retained controls separately classify missing (exit 3), empty (exit 0), malformed (exit 2), and truncated (exit 2). The detached-mode raw observation shows a stale request initiated after replacement is denied (409), with the replacement event preceding its permission read.

This supports only the selected **process-death** schedule. It provides no power-loss, storage-failure, or broad sink guarantee.

## Scope and provenance

- Review worktree: branch `review/autonomy-20261104-f4-check`, checkout `407a3453a5e69c0babc9e109cebe14c02a9e96e1`.
- Governing instructions read from `origin/main`: `AGENTS.md` and `ORIENTATION.md`.
- Scoped source hashes (SHA-256):
  - `run.py`: `63d52186d3cd4cb64ad471b6b017a3406506930fb926be3e0da648e03de21b23`
  - `f4_gate_qualification.py`: `28a6862ef073b52e276858d1b392fb7f2509d9c86866c841dc375b61644d6016`
  - `check_f4_gates.py`: `88f8c39270a23fac07c73f498561abe0d83fce86b56970cd34db766920ec71db`
  - `round2-f4-gates.raw.json`: `55dddea4e7a767d6e2f0d896c9ada17034e7ff8e7045ebc7d9bb833b133a1488`
  - `round2_detached.py`: `b5c89d2b33a1f28125ad6b0aa3bce8aee9faa9840676a3cd601a6080ef5551`
  - `round2-detached.raw.json`: `535083716112dff67e2e420335f666f1a86a375c378e871169cd5c69ff462740`
- F4 raw record identifies experiment source revision `962785f926345d7909eb690f5e81d72a1c65f5d0`; its recorded hashes for `run.py` and `f4_gate_qualification.py` match the scoped source files above. The checker does not enforce that binding.

## Commands and outcomes

Commands were run from `/workspace/ases-f4-check`. No retained raw file was modified.

1. `python3 research/phase-i-t18-sink-order-20261103/check_f4_gates.py` — exit 0. Baseline: `SUPPORTED_SELECTED_PROCESS_LOSS_MAPPING`; all four built-in mutations returned `INCOMPLETE_OR_INCONSISTENT`.
2. In-memory checker sensitivity probe: changed only `source_revision`, then only `hashes['run.py']`; both still returned `SUPPORTED_SELECTED_PROCESS_LOSS_MAPPING` (probe exit 0). This is a checker defect: raw/source provenance is not validated by the checker.
3. Independent temp-path reproduction, calling the existing `run_case` helper for only `accepted` and `early_ack`—exit 0:
   - `accepted`: sink exit `-9`; client exit 0, HTTP status absent; events `effect_accepted`, `accepted_waiting_before_ack`; live and cold readers `VALID`; journal exists.
   - `early_ack`: sink exit `-9`; client exit 0, HTTP 201; event `early_ack_waiting_before_accept`; live and cold readers `MISSING`; journal absent.
4. Initial import-only reproduction attempt—exit 1 (`ModuleNotFoundError: run`) because the experiment directory was not on `sys.path`; rerun with that directory added succeeded. This was a reproduction setup issue, not a sink failure.

## Findings separated by layer

**Sink observations:** the acceptance path appends and fsyncs `effect_accepted` before the held ACK; the early-ACK branch sends 201 before waiting and before writing any effect. The selected run's process kill leaves the corresponding distinct journal states. The detached schedule in the raw record invokes stale `/submit` only after `/replace` has completed; it observes version 2, rejects version 1 with 409, and records no stale effect.

**Harness/checker defects or limits:** `check_f4_gates.py` validates selected raw fields and built-in structural mutations but ignores `source_revision` and `hashes`; provenance must be independently checked. Its status is therefore a structural consistency result, not proof that the observations came from the claimed source. The independent import attempt needed the experiment directory on `sys.path`; after fixing that setup, the bounded reproduction passed. The retained checker controls do not exercise every malformed JSONL shape or journal race.

**Missing evidence:** no machine power cut, storage/cache fault, filesystem crash consistency, or arbitrary sink was tested. This check does not aggregate F2/F3 findings or establish broader durability.
