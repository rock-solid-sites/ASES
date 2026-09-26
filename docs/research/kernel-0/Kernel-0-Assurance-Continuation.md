---
title: Kernel-0 Assurance Continuation
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
consumed_by:
  - Fresh Kernel-0 assurance sessions
---

# Restart cursor

Branch: `codex/kernel-0-reasoning-566`. Issue #567 (child of #566) covers the
operator-authorized seven-phase assurance program. Work only under this directory.
The original checkout on `main` contains unrelated operator changes; do not use it
for source changes. Current working checkout: `/tmp/ases-kernel0-preflight`;
the repository, not that temporary pathname, is the durable carrier.

## Governing baseline

- Accepted bounded executor-loss result: `e2e3bc110b1370f3505aa0838990713520bf3f7c`.
- Starting branch tip: `19a1860934a2467c29c3b1c0d52fcd203098e703`, verified against
  `git ls-remote origin refs/heads/codex/kernel-0-reasoning-566` on 2026-09-26.
- Fresh reasoning session read current specifications and experiment boundaries;
  no new independent reviewer has been launched. Prior result is accepted as the
  operator's bounded premise, not promoted to an unbounded proof.

## Current position

**Completed Phase 1 — A1**, bounded holder SIGKILL/restart recovery.
Governing evidence commit: `1149fb124d7306f834fb7e9383ccaf7c79c5b7fa`.
It was pushed and remote SHA verified on 2026-09-26 before Phase 2 work.
Sources/results: `Kernel-0-Crash-Recovery.md`, `kernel0_recovery_model.py`,
`kernel0_recovery_service.py`, `kernel0_recovery_check.py`, and the two generated
Crash-Recovery result JSON files. Finite: 7,502 states / 12,457 edges / 24 fixtures /
10 detected mutants. Concrete: 36 cut cases, 18 timed races, two successful
content-preserving recovery profiles, order/replay and startup attacks.

Strongest counterexample: restoring an old same-root image after acknowledged
revocation resurrects old authority. Disposition: confirmed negative against
freshness-by-root-ID; excluded by the explicit current-storage trust boundary.
No canonical semantics changed. Cold and continuing recovery have different
attachment obligations. Continuing mode trusts a surviving supervisor's immutable
producer/context mapping, never supervisor-supplied current rights.

Untested: SQLite I/O-path crash coverage, power loss, corruption, hostile rollback,
supervisor loss, unbounded contexts, physical source binding after new-evidence
transfer, progress, exactly-once, and independent review of these new artifacts.

**Next: Phase 2.** First concrete action: derive a selected external-effect profile
by separating current authority at durable decision from current authority at sink
acceptance; build the smallest finite sink model and test revocation/crash/retry.
Do not silently require exactly-once or revoke previously accepted obligations.
Frozen Phase 1 independent-review packet is indexed in `Kernel-0-Assurance-Review.md`.

## Required execution order

1. Authority-service crash/recovery: semantic derivation, finite model, concrete
   process kill/restart experiment; gate A1/B1/C1/D1.
2. Selected protected external-effect contract; A2/B2/C2/D2.
3. Two independent domains and an explicit coupled operation; A3/B3/C3/D3.
4. Narrow parametric arguments or explicit finite-only limits.
5. Additional formal/refinement assurance only against a concrete remaining gap.
6. Re-minimize: intrinsic distinction / optional profile / substrate / mechanism.
7. Stronger bounded realization direction or precise production-scope gate.

Before advancing, internally attack, document, commit, push, and verify the remote
SHA. Then record the governing evidence commit here and push this cursor update.
The operator explicitly authorized these phase pushes in this request. No merge,
reviewer/model launch, or production deployment follows from that authorization.
Do not wait for external reviewers; freeze a packet when useful and accurately
label self-review. Preserve counterexamples and source-hashed generated results.

WHY: interruption must not erase completed reasoning. WHAT: operator program and
current repository evidence. HOW CERTAIN: plan only. WHAT-NOT-TESTED: all stronger
profiles remain pending. Resume by reading this file and taking its next action.
