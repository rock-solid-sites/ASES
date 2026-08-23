# EPIC 423 Swarm Plan

Derived from: .design/epic-423-swarm-replan.md (context, rationale, Track M)

## Phase 1 - Documentation Integrity System

- AC-DIS-1: Spike - build doc-graph extractor over existing frontmatter conventions plus citation scan across docs/, .crosslink/knowledge/, wrapper scripts and configs; acceptance test = graph flags all four known-broken 2026-08-23 instances (missing opencode-fork.md target cited by wrapper, unverifiable playbook section citations reported on #429, permissions.md self-declared staleness, stale git claim in auditor kickoff text); failure to catch all four blocks the phase
- AC-DIS-2: V1 existence validator live - every cited path or section reference resolves against the repo
- AC-DIS-3: V3 freshness propagation live - last-verified stamps on docs; editing a source node marks dependent docs stale via reverse edges
- AC-DIS-4: V4 consult-gate design ticket for issue #387 - pre-dispatch/config-change/merge doc consultation requirement, hook pattern per auto-export v7
- AC-DIS-5: V2 authority-trace validator - Derived claims chain to Canonical parents via declared dependencies

## Phase 2 - Foundation Probes

- AC-F1: Tools-repo inventory and drift check versus its TOOLING.md catalog; every item mapped to current-use, future-need, or orphan; feeds consolidation analysis #354
- AC-F2: Crosslink-v2 interop probe - verify coordination layer can drive opencode2 beta binaries headlessly; verdict gates all retirement logic
- AC-F3: Credential and config sharing map across both binaries; conflict risk assessment
- AC-F4: Storage retention and growth semantics per binary; informs #419-A merge timing
- AC-F5: Fork-runbook reconstruction via session archaeology per EPIC #396 method using scripts/session-union.py as index; recreates .crosslink/knowledge/opencode-fork.md and fixes the wrapper pointer

## Phase 3 - Tooling Inventory and Relevance Map

- AC-R1-1: Classify every custom tool x S1/S2/S3 x working/suspect/broken/superseded, including a hardcoded-path column feeding migration checklist M1
- AC-R1-2: Open-issue relevance map covering every open issue: surface applicability plus fork-retirement sensitivity {blocks, unaffected, accelerates, orthogonal} plus close-candidates with evidence; consume and extend issue #432 output and issue #420 W2 findings rather than redoing them

## Phase 4 - Regression Probe Suite

- AC-P0a: Behavioral probe - turn-level idle guard equivalence in v2 (matrix delta D2)
- AC-P0b: Behavioral probe - consumption-deadlock pattern in v2 (delta D3)
- AC-P0c: Behavioral probe - non-SSE body deadline in v2 (delta D1)
- AC-P0d: Bounded-retry semantics parity (delta D4 remainder)
- AC-P1: Timeout provider-option survival on S1 under redesigned schema
- AC-P2: S1 write-path exposure at the execute-sandbox boundary given guard absence
- AC-P3: Project-level markdown-agent discovery support in v2
- AC-P4: Hot-reload scope for definitions and registry (permissions already confirmed live)
- AC-P5: db-path override existence for either binary (#419 option C precondition)
- AC-P6: Catalog-source parity - models.dev versus Zen API versus S1 picker ordering
- AC-P7: V4 consult-gate implementation across dispatch surfaces per #387

## Phase 5 - Fork-Necessity Verdict Closeout

- AC-V1: Final per-delta verdict table {retire | keep | conditional} merging #427 matrix with Phase 4 parity results
- AC-V2: Retirement runbook written if retirement viable, replacing missing opencode-fork.md; otherwise keep-decision with dated re-evaluation triggers
- AC-V3: #419-A merge strategy resolved (freeze-then-merge versus periodic schedule) with multi-verifier plan per tiered-verification doctrine
