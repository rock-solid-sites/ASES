---
title: Kernel-0 Machine Realization Family Reduction
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Derived
canonical_repository: ASES
crosslink_issue: 573
baseline_commit: 09d7d3854d2210fb668b30feae102a0ea25ee1b3
depends_on:
  - Kernel-0 Machine Realization Investigation
  - Kernel-0 Machine Realization Evidence Record
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
consumed_by:
  - Kernel machine realization formalization and experiments
related_documents:
  - Kernel-0 Machine-Adjacent Realization Input Packet
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Kernel-0 machine realization family reduction

## Continuation boundary

This continuation attacks the classification before T0–T6 begins. It starts from `09d7d3854d2210fb668b30feae102a0ea25ee1b3`: [investigation](./Kernel-0-Machine-Realization-Investigation.md), blob `81aefad8cee1c3be4158c1bcccc8976333762025`; [evidence record](./Kernel-0-Machine-Realization-Evidence.md), blob `3f09a5bf7a84f46acdbb1873f315fcee1b39bdbb`. The packet, selected semantic/profile sources, recorded expansions and provisional-delta conditions remain exactly those pinned by that investigation. No additional repository or external source is needed for this classification attack. No downstream prototype, model or independent review has been launched.

## Working reduction

The three labels are not an irreducible partition. F1 describes confinement of untrusted behavior, F2 describes instruction-based execution and protection, and F3 combines a digital implementation with a deeper verification boundary. They can describe the same physical realization. The continuation will separate assumption-preserving regrouping from a new physical implementation or a newly discharged proof obligation; neither follows merely because every candidate is digital.

WHY: a family should survive only through a necessary difference in trust/refinement structure. WHAT: the original F1–F3 definitions and the unchanged contextual effect/loss contract. HOW CERTAIN: evidence-based reduction in progress. WHAT-NOT-TESTED: complete reductions, dominance conditions and revised downstream handoff are not yet finalized.
