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

**Completed Phase 2 — A2**, selected decision-authorized obligation profile.
Governing evidence commit: `788c34ae267d4f274e06150610924deac24bf437`, pushed and remote SHA verified.
2,715 model states / 9,924 edges; six detected weakenings; seven pinned histories;
five source and two sink crash cuts plus revocation/overwrite tests. A sink effect
with lost acknowledgement is repeated by retry. This is permitted, not exactly-once.
The obligation survives producer revocation; sink-current authority and cancellation
remain unclaimed. Phase 1 reran successfully after adding the consumer extension.

**Completed Phase 3 — A3 (bounded model only).** Governing commit:
`018fc72daa9a5b902f1b6140fbf5e033aee85ac5`, pushed and remote SHA verified. 432 states / 17,280 edges;
48 unordered independent-step checks. Scoped evidence and local availability
compose; reservation/transfer requires a joint coherent view and compatible
recovery cut. A half-transfer recovers `(0,0)`, satisfying exclusion but losing
the whole declared effect. No physical multi-holder recovery implementation is
claimed. No new Kernel-0 primitive or canonical definition changed.

**Completed Phase 4 — conditional parametric arguments; no cutoff theorem.**
Governing commit `771af312a481c32520b6165cb1a5bb1af84b4048`, pushed and remote SHA verified. P1 non-resurrection,
P2 arbitrary-field whole-effect refinement, P3 complete acyclic dependency orders,
and P4 disjoint-footprint locality have explicit hand arguments. Their concrete
premises remain unproved. Negative families: label reuse, four-cycle invisible to
all triples, and naive one-hop delegation extension. 444 finite commutation sanity
checks do not substitute for the argument.

**Completed Phase 5 — bounded whole-history refinement evidence.**
Governing commit `ef1f49c0deee068c85cadc2c05ea76c15f1c5478`, pushed and remote SHA verified. Fifteen actual
concurrent/crash histories have coherent explanations; four inconsistent histories
are rejected; both old/new outcomes of an unanswered operation remain possible.
Algorithmic separation is not independent review. Unknown outcomes are scoped to
holder loss, not arbitrary network loss. SQLite I/O crash placement remains the
largest tractable substrate gap.

**Completed Phase 6 — no new Kernel-0 primitive justified.** Governing commit:
`9b325b617e633b73f8c150b858e290417194aa92`, pushed and remote SHA verified. The removal audit classifies all
retained distinctions/mechanisms as intrinsic, optional-profile, substrate or
realization. Stronger claims parameterize σ, guarded whole commitment, authority,
order, failure projection and mediation. Canonical semantics remain unchanged.

**Next: Phase 7.** First concrete action: assess the bounded discriminator of
killing the existing transactional holder at actual storage write/synchronization/
journal-removal calls, using test-only instrumentation and the same whole-state
oracle. If feasible, implement it; do not build a production storage engine or
claim power-loss/storage-fault proof from live-OS process termination.

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
