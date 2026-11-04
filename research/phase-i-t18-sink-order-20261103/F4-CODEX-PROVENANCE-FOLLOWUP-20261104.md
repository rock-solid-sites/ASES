# F4 provenance checker follow-up — 2026-11-04

This is a post-fix check of cross-layer commit `5d45805764a42a7464e0963d1715ae009dccac57`, performed in disposable detached worktree `/tmp/ases-f4-provenance-followup`. It does not replace or revise the initial independent verdict in `F4-CODEX-CHECK-20261104.md`.

The diff from `407a345` pins the expected `source_revision`, checks the recorded hashes for local `run.py` and `f4_gate_qualification.py`, and adds negative controls for wrong base revision, sink hash, and runner hash.

Commands and results from the disposable checkout:

- `python3 research/phase-i-t18-sink-order-20261103/check_f4_gates.py` — exit 0; baseline `SUPPORTED_SELECTED_PROCESS_LOSS_MAPPING`; all seven controls, including the three provenance controls, returned `INCOMPLETE_OR_INCONSISTENT`.
- In-memory direct probe of the baseline and the three provenance mutations — exit 0; baseline remained `SUPPORTED_SELECTED_PROCESS_LOSS_MAPPING`; wrong `source_revision`, wrong `hashes['run.py']`, and wrong `hashes['f4_gate_qualification.py']` each returned `INCOMPLETE_OR_INCONSISTENT`.

**Result:** the original wrong-base and wrong-sink-hash counterexamples now reject while the unmodified baseline remains supported. The added runner-hash control also rejects. This follow-up validates the checker change only; no sink cases were run.
