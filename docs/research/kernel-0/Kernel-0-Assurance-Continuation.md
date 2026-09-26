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

No stronger phase is complete. Phase 1A/1B are internally checked: 7,502 states,
12,457 edges across 24 fixture closures; ten intended weakened variants fail.
Governing source/evidence checkpoint: `15d6f48722eec238f1d928b00a75237496abf5d7`.
Initial derivation checkpoint: `5d5ff7e1b220d348e0a0d2e9f6244ed6dbbc9509`. Phase 1C real process experiment is
running. First concrete action: inspect its result, challenge adequacy and
conformance, then freeze A1/B1/C1/D1. No Phase 2 work has begun.

Unresolved: recovery evidence must distinguish the current whole commitment from
an authentic but obsolete image; continuing recovery additionally needs authentic
producer-to-authority association. Physical-producer exclusion after transfer of
new evidence, power failure, media corruption, progress, and exactly-once remain
unclaimed.

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
