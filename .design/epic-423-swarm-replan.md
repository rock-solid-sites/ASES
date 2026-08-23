---
title: EPIC 423 Remainder - Swarm Re-plan
program: EDASES
layer: Implementation
document_type: Design
status: Proposed
authority: Derived
parent_epic: "#423"
consumed_by: crosslink swarm init --doc
---

# Purpose

Execute EPIC #423 remainder as a gated swarm. Ordering principle established by
operator 2026-08-23: documentation-integrity infrastructure precedes all phases,
because every downstream agent consumes documents and stale docs would reproduce
the 2026-08-23 failure classes at swarm scale.

# Surfaces (classification axis)

S1 = OpenCode 2 TUI (opencode2, @opencode-ai/cli beta)
S2 = pp3g fork CLI 1.18.13 (opencode wrapper target)
S3 = crosslink-fork CLI (coordination layer)

# Phase DIS - Documentation Integrity System (gates all other phases)

Objective: mechanical defense against the four staleness classes observed
2026-08-23: phantom file targets, phantom section citations, self-declared-stale
snapshots, surface-divergent claims.

D0a Spike: auto-extract a doc-graph from existing frontmatter conventions
(authority, dependencies, downstream consumers) plus a citation scan across
docs/, .crosslink/knowledge/, wrapper scripts and configs. ACCEPTANCE TEST: the
extracted graph must flag all four known-broken instances from 2026-08-23 -
the missing .crosslink/knowledge/opencode-fork.md target cited by the opencode
wrapper, the unverifiable playbook section citations reported by issue #429
researcher, the permissions.md self-declared staleness, and the stale git claim
in auditor kickoff text. Failure to catch all four = redesign, not proceed.

D0b Existence validator (V1): every cited path/section resolves.
D0c Freshness + propagation (V3): last-verified stamps; editing a source node
marks dependent nodes stale (update-pushes-out semantics).
D0d Consult-gate (#387): before dispatch / config change / merge, orchestrator
must reference current doc versions; hook pattern per auto-export plan v7.
D0e Authority-trace validator (V2): Derived claims chain to Canonical parents;
may trail if frontmatter coverage incomplete.

Exit criteria: V1+V3 live with the four acceptance cases passing; V4 designed
with implementation ticket. Gate G1: reviewer verdict on DIS artifacts.

# Track M - Server Migration Readiness (parallel-account build to jork)

Not an in-place rename: lower-risk parallel environment + cutover. Path updates
handled systematically by projects/server/migration-handoff-summary.md runbook.

M1 path-dependence checklist - GATED ON R1 output (hardcoded-path column).
M2 signing/identity continuity - verifies issues #22-#25 chain survives jork.
M3 opencode-state migration annex - DB/caches/tmux-boundary notes for runbook;
   informed by R0d storage-semantics findings.
M4 cutover timing recommendation - gated on wave completion + R0d.

# Phase R0 - Foundation Probes and Inventories

R0a Tools-repo inventory and drift check vs TOOLING.md; map items to {current |
future | orphan}; feeds consolidation analysis (#354); locate or schedule
reconstruction of fork-restoration runbook.
R0b Crosslink-v2 interop probe - can coordination layer drive v2 binaries
headlessly? Gates ALL retirement logic.
R0c Credential/config sharing map between binaries; conflict risk.
R0d Storage retention and growth semantics per binary; informs #419-A timing.
R0e Fork-runbook reconstruction via session archaeology under EPIC #396 method
(union tool indexes both stores; precedent issue #261 verbatim extraction);
deliverable recreates .crosslink/knowledge/opencode-fork.md and fixes the
wrapper pointer.

Gate G2: foundation findings posted with claim discipline; unknowns routed to
R2 tickets.

# Phase R1 - Tooling Inventory and Classification

R1a Classify every custom tool x {S1,S2,S3} x {working|suspect|broken|
superseded} with hardcoded-path column (feeds M1).
R1b Open-issue relevance map: every OPEN issue x {S1|S2|S3|multi|none} x
{blocks-retirement|unaffected|accelerates-retirement|orthogonal} plus
close-candidate identification. Early partial execution already delivered via
issue #432; consume and extend rather than redo. Input: W2 staleness baseline
(issue #420) when available.

Exit criteria: matrix committed; UNKNOWN cells routed to R2. Gate G3: reviewer
verdict; orchestrator resolves unknowns into probe tickets.

# Phase R2 - Regression Probe Suite

P0 series (fork-delta parity vs v2, behavioral probes from #427 matrix):
P0a turn-level idle guard equivalence [D2]; P0b consumption-deadlock pattern
[D3]; P0c non-SSE body deadline [D1]; P0d bounded-retry semantics [D4].
Results land as {v2-equivalent-present|absent|partial} directly into #427 rows.
P1 timeout-schema survival on S1 under provider schema redesign.
P2 S1 write-path exposure given guard absence (execute-sandbox boundary).
P3 project-level markdown-agent discovery in v2.
P4 hot-reload scope for definitions/registry (permissions already confirmed live).
P5 db-path override existence either binary (#419-C precondition).
P6 catalog-source parity (models.dev vs Zen API vs S1 picker).
P7 DIS validators V4 implementation + integration across dispatch surfaces.

Standards: probes scripted under tools/probes/; paths passed as arguments (no
hardcoding - migration-safe); results carry claim discipline; scratch under
/tmp/opencode/ only.

Gate G4: reviewer verdict; failures triaged into fix tickets with tiered
verification assignments per docs/ORCHESTRATOR.md.

# Phase R3 - Fork-Necessity Verdict Closeout

Consume R2 parity results + #427 matrix -> verdict per delta {retire | keep |
conditional}; produce retirement runbook replacing missing opencode-fork.md if
retirement viable; else keep-decision with dated re-evaluation triggers; resolve
#419-A merge strategy (freeze-then-merge vs periodic schedule).

Gate G5: post-hoc audit over outcome AND process (Phase-2 style).

# Swarm Parameters

Budget window: 6h total guide. Phases strictly sequential; parallelism within
phases only. Models: selected at dispatch time per Mandatory Rule 5 (never
assume; ask operator) - no pins in this document. Auditing: pre-positioned
auditor per phase with nudge-authority via comment channel; stop/intervene stays
orchestrator-only. All work references EPIC #423 and sub-issues; commits cite
issue ids.
