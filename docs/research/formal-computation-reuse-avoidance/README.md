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

## Planning sequence (operator confirmed 2026-11-26)

1. Reconcile existing research and current capabilities. [Scoped reconciliation in SOURCE-MAP](SOURCE-MAP.md#step-1--prior-research-reconciled-with-current-capabilities-2026-11-26); remaining provenance gaps explicit.
2. Identify and organize distinct areas of study.
3. Map relationships between research topics.
4. Identify unresolved questions and relevant literature.
5. Establish a coherent research programme.

The current phase is organization and planning. Prior suggested CodeGraph, Kernel-0, multi-donor composition, and graph-assisted-review comparisons are deferred research directions, not immediate experiments. Formal models and pilot designs may be considered after the planning phase and separate authorization. Do not rerun existing work or choose experiment cases now. 

No new test dispatch or implementation selection is implied by this charter. Preserve required durable intermediate records and evidence custody; do not eliminate them merely because fusion is possible.
