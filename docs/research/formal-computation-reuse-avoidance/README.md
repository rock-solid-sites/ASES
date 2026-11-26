---
title: Formal Computation, Reuse and Avoidance
program: EDASES
layer: Research
document_type: Research Charter
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-26
---

# Formal Computation, Reuse and Avoidance

This research branch extends the earlier Universal Caching & Computation Reuse studies: minimize unnecessary computation, particularly local resource use, while preserving correctness, evidence, authority, recoverability and freshness. The operator identified recursion schemes, typed DSLs, lawful lenses and multi-donor composition as connected research directions. This is a research home, not an active architecture, universal cache, mandatory method or Git branch.

**Central question:** What representation and evidence can establish that a computation or verification step is necessary, unnecessary, reusable or incrementally repairable? Include the cost of establishing that judgment. Reasoning effort, time, memory, I/O, external calls, tokens and verification effort are distinct measurements.

## Research map

| Area | Research question | Initial objects |
| --- | --- | --- |
| Structural representation | Which identities, types, effect descriptions and invariants make invalid operations unrepresentable or observable? | Typed DSL/IR, typestate, multiple interpretations, Tidepool/ExoMonad leads, state-model method |
| Computation avoidance | Can we establish that a result is not demanded or a transformation/check is redundant? | Demand-driven evaluation, early cutoff, fold fusion |
| Reuse and validity | Under what scope and assumptions does an existing artifact or proof remain valid? | Content addressing, provenance, environment identity, cache composition |
| Incremental computation | What minimum dependency frontier must be recomputed? | Merkle structures, dependency graphs, CodeGraph, change propagation, memoization and fixed points |
| Compositional correctness | When do local guarantees imply a global guarantee, and what is missing? | Recursion schemes, structural induction, assume/guarantee contracts, Kernel-0, donor composition |
| Lawful transformations | What changes can move between representations without unnecessary reconstruction or inconsistency? | Lenses, bidirectional transformations, HMS views, Projektor projections |
| Verification efficiency | Which obligations can be proved statically, reused or selectively retested? | Model checking, evidence reuse, independent oracles, compositional verification |

## Organization and progress

- [SOURCE-MAP.md](SOURCE-MAP.md): earlier studies, qualified observations, candidate techniques, and outstanding reconciliation.
- [GRAPH-ASSISTED-REVIEW.md](GRAPH-ASSISTED-REVIEW.md): draft controlled comparison and evaluation rubric for source-only, graph-only and graph-assisted chat/review agents.
- Add topic-specific research documents and runnable experiments here when substantive work warrants them. Keep existing owner artifacts in place; link pinned originals rather than copy or move them. No empty placeholder directories or parallel test lab.
- Human research direction: Projektor ASES-25; topic graph node `ases-concept-formal-computation-reuse-avoidance`. Execution/reconciliation: WNASES-32. Public technical findings belong on main; private archive source locators remain in authorized records.
- Related: [comparative implementation research](../Comparative%20Implementation%20Research%20and%20Upstream%20Contribution%20Proposal%202026-11-25.md), [state-model applicability](../../methodology/State-Model%20Applicability%20and%20Reuse%20Method.md), [testing and assurance source map](../Testing%20and%20Assurance%20Source%20Map.md). Independent Rust Safety Foundations remains independently owned.

## Operational baseline versus open research

CodeGraph is already selected and used in our structural analysis workflow after comparison with alternatives, not merely a hypothetical research candidate. The [current operational skill](../../../skills/current/codegraph-actions-repository-research/SKILL.md) was reverified on 2026-11-26 (v1.2.2 at this review); GitHub Actions and B2 provide commit-scoped reusable indexes, with verified cache maintenance and approved exact-key deletion. The operator reports recent debugging of the live workflow. Continue using the established route when appropriate; its operational owner retains responsibility for maintenance. Research remains open on semantic and partial cross-revision reuse, dependency completeness, invalidation, retention decisions, query/evidence reuse, and end-to-end costs. Do not confuse adoption of a useful tool with proof or closure of these broader questions, or restart the tool selection exercise. Historical reconstruction is useful for extracting surviving ideas, not a prerequisite for using current evidence.

## Research sequence

1. Reconcile prior work by domain before proposing cross-domain primitives: build/compilation, verification, agent knowledge, execution, testing, dependencies/environment, inference, repository semantics and distributed computation. Distinguish original hypotheses from actual measurements and decisions.
2. Begin from the active CodeGraph workflow and its latest maintenance evidence; compare existing incremental results and clean-rebuild controls. Formulate the smallest reusable-validity question and identify the independent oracle and cost boundary.
3. Use Kernel-0's existing shared-handover result to examine compositional proof obligations; use actual multi-donor composition as a second, distinct experimental context. Do not rerun existing suites merely to demonstrate a mathematical pattern.
4. Investigate recursion schemes, typed specifications and lawful transformations with primary literature and minimal discriminating examples. Only claim a hylomorphism for a genuinely well-founded unfold/fold computation; shared/cyclic dependencies need appropriate graph/fixed-point treatment. Type-level checks cannot replace runtime authority; lens laws do not license effects or concurrent writes.
5. Compare alternatives at equivalent required guarantees and record negative cases, proof complexity, correctness and actual computational cost. Generalize only after cross-domain transfer evidence.

No new test dispatch or implementation selection is implied by this charter. Preserve required durable intermediate records and evidence custody; do not eliminate them merely because fusion is possible.
