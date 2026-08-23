# EPIC 423 Swarm Plan

Coordination layer drives fork CLI (S2) today and must be verified against OpenCode 2 beta (S1) before any retirement decision. Context document: .design/epic-423-swarm-replan.md

## Requirements

### Phase 1: Documentation Integrity System (sequential)

- REQ-DIS1: Build doc-graph extractor over existing frontmatter conventions plus citation scan across docs, .crosslink/knowledge, wrapper scripts and configs. Acceptance: graph flags four verified current instances - missing .crosslink/knowledge/opencode-fork.md target cited by opencode wrapper, permissions.md self-declared staleness, stale git claim in auditor kickoff text, and knowledge page crosslink-subagent-orchestration.md documenting H2 phase headers while installed fork parser empirically requires H3 groups nested under an H2 Requirements section. Additionally the graph must model temporal citation healing: playbook section citations in docs/research/registry/Failure-Matrix.md were phantom-at-write on 2026-08-18 but self-healed when the playbook landed - distinguish phantom-now from phantom-at-write.
- REQ-DIS2: V1 existence validator live - every cited path or section reference resolves against the repository.
- REQ-DIS3: V3 freshness propagation live - last-verified stamps on documents; editing a source node marks dependent documents stale via reverse edges.
- REQ-DIS4: V4 consult-gate design and implementation ticket for issue #387 - require doc consultation before dispatch, config change, merge; hook pattern per auto-export plan v7.
- REQ-DIS5: V2 authority-trace validator - Derived claims chain to Canonical parents via declared dependencies.

### Phase 2: Foundation Probes (sequential)

- REQ-F1: Tools repo inventory and drift check versus TOOLING.md; map every item to current-use, future-need, or orphan; feeds consolidation analysis issue #354.
- REQ-F2: Crosslink-v2 interop probe - verify coordination layer can drive opencode2 beta binaries headlessly; verdict gates all retirement logic.
- REQ-F3: Credential and config sharing map across both binaries with conflict risk assessment.
- REQ-F4: Storage retention and growth semantics per binary; informs issue #419 option A merge timing.
- REQ-F5: Fork-runbook reconstruction via session archaeology per EPIC #396 method using scripts/session-union.py as index; recreates .crosslink/knowledge/opencode-fork.md and fixes the wrapper pointer.

### Phase 3: Tooling Inventory and Relevance Map (parallel)

- REQ-R11: Classify every custom tool x S1/S2/S3 x working/suspect/broken/superseded including a hardcoded-path column feeding migration checklist M1.
- REQ-R12: Open-issue relevance map covering every open issue: surface applicability plus fork-retirement sensitivity blocks/unaffected/accelerates/orthogonal plus close-candidates with evidence; consume issue #432 categorization and issue #420 W2 findings rather than redoing them.

### Phase 4a: Parity Probes - Fork Deltas (parallel)

- REQ-P0A: Behavioral probe of turn-level idle guard equivalence in v2 (matrix delta D2).
- REQ-P0B: Behavioral probe of consumption-deadlock pattern in v2 (delta D3).
- REQ-P0C: Behavioral probe of non-SSE body deadline in v2 (delta D1).
- REQ-P0D: Bounded-retry semantics parity check (delta D4 remainder).

### Phase 4b: Surface Probes (parallel)

- REQ-P1: Timeout provider-option survival on S1 under redesigned schema.
- REQ-P2: S1 write-path exposure at the execute-sandbox boundary given guard absence.
- REQ-P3: Project-level markdown-agent discovery support in v2.
- REQ-P4: Hot-reload scope for definitions and registry; permissions already confirmed hot-reloading.
- REQ-P5: db-path override existence for either binary; issue #419 option C precondition.
- REQ-P6: Catalog-source parity - models.dev versus Zen API versus S1 picker ordering.
- REQ-P7: V4 consult-gate implementation across dispatch surfaces per issue #387.

### Phase 5: Fork Verdict Closeout (sequential)

- REQ-V1: Final per-delta verdict table retire/keep/conditional merging issue #427 matrix with Phase 4a parity results.
- REQ-V2: Retirement runbook written if retirement viable replacing missing opencode-fork.md; otherwise keep-decision with dated re-evaluation triggers.
- REQ-V3: Issue #419 option A merge strategy resolved freeze-then-merge versus periodic schedule with multi-verifier plan per tiered-verification doctrine.
