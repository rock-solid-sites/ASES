# Comparison protocol — treatment A versus earlier hands-on runs

**Treatment A:** fresh Codex Cloud session with explicit `ASES-SOL-CTRL-A-20261113`; parent orchestrates only, Luna handles complete tools/data plane. **Historical comparison B:** previous ASES-4 campaign on Nov 10–12, where parent directly executed many commands and validated some worker results. Operator reports Sol accounted for **~80–90%** of usage; this is user-observed analytics, not a connector-derived figure.

## Primary outcome

**Cost per useful independently verified engineering slice**, not raw PR counts. A slice is useful when it has a source-pinned executable change or decisive negative finding, relevant red/green neighboring cases, raw evidence, and a handoff that a separate model can assess. Local same-family tests remain provisional pending ASES-6 independent checks.

## Session metrics

Luna records, where reliably observable:
- Start/end timestamps, model usage **from actual product analytics where available**, separate parent and child consumption; don't invent unavailable token counts.
- Sol share of allowance and direct parent shell/file/search/API calls (strict target **zero**; count coordination calls separately).
- Total useful engineering slices and their independent review status; unresolved regressions, erroneous acceptance claims and rolled-back work.
- Subagent count, concurrency, command/test count and per-slice observed latency when available.
- Number of escalations requiring a Sol decision, and approximate length of each received decision packet.
- Work Notes and Git checkpoints; data lost at quota exhaustion, tool failure or session disappearance.
- Same-source integration correctness and any new negative counterexample.

A separate inexpensive observer should gather audit metadata/usage screenshots supplied by the operator and compile the comparison. The parent should not perform instrumentation personally.

## Comparability

Treat previous work as a **historical baseline**, not a controlled random trial: task difficulty, remaining defects, context age, host state and tooling differ. Compare similar slices within native ownership and Rust execution-engine tracks, normalize by scope, and identify confounders. A future matched A/B replication with fresh, equivalently sized tasks would provide stronger evidence.

## Interpretation

Direct parent calls at zero do not, by themselves, establish efficiency. Report whether treatment A lowers Sol consumption **without sacrificing validated outcomes**. A mixed strategy may ultimately win if rare direct parent inspection truly avoids repeated delegated rounds. The experiment uses strict delegation now to measure that tradeoff; do not quietly loosen it partway through.
