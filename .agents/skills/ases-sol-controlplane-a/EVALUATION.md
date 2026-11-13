---
title: "EVALUATION"
version: 0.2.0-experimental
status: experimental
authority: run-scoped
run_id: ASES-SOL-CTRL-A-20261113
supersedes_revision: eaf0d2c5092c1c1627e1ef79188378d1237f3e37
---

# Comparison protocol — treatment A versus earlier hands-on runs

**Treatment A:** fresh Codex Cloud session with explicit `ASES-SOL-CTRL-A-20261113`; parent orchestrates only, Luna handles complete tools/data plane. **Historical comparison B:** previous ASES-4 campaign on Nov 10–12, where parent directly executed many commands and validated some worker results. Operator reports Sol accounted for **~80–90%** of usage; this is user-observed analytics, not a connector-derived figure.

## Primary outcome

**Cost per useful separately verified engineering slice**, not raw PR counts. A slice is useful when it has a source-pinned executable change or decisive negative finding, relevant red/green neighboring cases, raw evidence, and a handoff that a separate model can assess. A builder's own green tests do not count as verification. A separate Luna verifier's independently authored falsifiers provide an intermediate gate, still qualified as same-family; ASES-6 CI and heterogeneous reviews are stronger, separate gates.

## Session metrics

Luna records, where reliably observable:
- Start/end timestamps, model usage **from actual product analytics where available**, separate parent and child consumption; don't invent unavailable token counts.
- Sol share of allowance and direct parent shell/file/search/API calls (strict target **zero**; count coordination calls separately).
- Slices by status: builder-only, separately Luna-verified, heterogeneous-reviewed, independent-CI-reproduced; unresolved regressions, erroneous acceptance claims and rolled-back work.
- Sol's verification plans predeclared before implementation, rejected builder claims, disputed observations, and decisions based on separate verifier packets.
- Subagent count, concurrency, command/test count and per-slice observed latency when available.
- Number of escalations requiring a Sol decision, and approximate length of each received decision packet.
- Work Notes and Git checkpoints; data lost at quota exhaustion, tool failure or session disappearance.
- Same-source integration correctness and any new negative counterexample.

A separate inexpensive observer should gather audit metadata/usage screenshots supplied by the operator and compile the comparison. The parent should not perform instrumentation personally.

## Comparability

Treat previous work as a **historical baseline**, not a controlled random trial: task difficulty, remaining defects, context age, host state and tooling differ. Compare similar slices within native ownership and Rust execution-engine tracks, normalize by scope, and identify confounders. A future matched A/B replication with fresh, equivalently sized tasks would provide stronger evidence.

## Interpretation

Direct parent calls at zero do not, by themselves, establish efficiency. Sol owns verification criteria and the acceptance verdict, with independent execution delegated. Report whether treatment A lowers Sol consumption **without sacrificing validated outcomes**. A mixed strategy may ultimately win if rare direct parent inspection truly avoids repeated delegated rounds. The experiment uses strict delegation now to measure that tradeoff; do not quietly loosen it partway through.
