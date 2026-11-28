---
title: When do separate owner proofs establish one recovered cut?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Restoring-history-without-restoring-authority.md
  - docs/research/kernel-0/When-separate-checks-prove-one-legal-effect.md
  - docs/research/kernel-0/When-recovery-must-make-progress.md
last_updated: 2026-11-28
---

# When do separate owner proofs establish one recovered cut?

An owner proof may use evidence from a sink while the sink proof uses owner authorization. This is sound if the facts concerned have an independently grounded order in the actual history. Reasoning about each component's own latest surviving checkpoint can substitute a previously true fact for a current one. Reasoning that assumes the other component's current conclusion can also prove two implications without establishing either conclusion. Neither is repaired by inspecting the implementation in a different proof language. [Historical and current owner evidence](Restoring-history-without-restoring-authority.md) · [Machine realization assurance boundary](https://github.com/rock-solid-sites/ASES/blob/d30679c3aaeb0a57f7ca160140a7c3174496ff04/docs/research/kernel-0/Kernel-0-Machine-Realization-Family-Reduction.md#6-common-assumptions-additional-assumptions-and-dominance)

## A local proof rule for one coherent successor

Let Pᵢ describe the guarantee supplied by each component or proof obligation at a coherent cut of the actual system. Prove all Pᵢ at the initial cut. For every actual transition from cut s to t, including failure and restoration, provide an order for the current-cut dependencies. To establish Pᵢ(t), a local proof may assume any Pⱼ(s) and only those Pⱼ(t) whose rank is strictly lower than i's in this transition. Include the actual enabledness and assumptions about trusted effects used to justify the transition outside this rule.

Induction on concrete transitions establishes every preceding-cut premise. Induction on rank within a transition then establishes every current-cut guarantee. A rank can be a topological position for the finite current-dependency graph. It may depend on which transition occurs. For example accepting a new authorized append may derive publication from a prior validated selection. Reading a recovery certificate may establish a later owner settlement from already established publication. A static graph that merges every event and uses no time index could appear cyclic when every actual proof follows a grounded order. Conversely the transition-local order proves no graph progress when required guards never enable. [Time-indexed compositional reasoning, McMillan](https://mcmil.net/pubs/CAV98.pdf) · [Progress assumptions](When-recovery-must-make-progress.md)

A genuine same-cut cycle cannot be handled by this rank rule as separate steps. For purely conditional claims, setting both conclusions to false satisfies “A if B” and “B if A.” One way forward is to prove the conjunction for that strongly connected group directly from prior-cut results and external facts. Another is to use previously established evidence whose guarantee actually survives to the point of use. A proof that adds a delay to break the cycle must justify that the delayed evidence still supports the required current claim. The direction of an arrow in a component diagram is insufficient.

## Restoration is an actual transition

For example two claims may refer to equality of the selected cut at an owner and at a sink. Both copies were coherent at a cut with value zero and then at a cut with value one. Restoring the owner's old authenticated image restores zero locally while the sink still exposes one. Each underlying image once participated in a legal cut. Their mixture violates equality. If the proof treats the local old cut as the global predecessor, invoking its invariant silently changes the system history. A recovery certificate must instead establish a common selected cut, repair one side from authenticated evidence, or explicitly keep the unresolved view non-authoritative until a qualified action.

The actual F3/F4 source has separate selection and publication meanings. The R2 case observed F4 historical success with unresolved F3 owner settlement; it does not demonstrate circular implementation logic. A proposed common-cut bridge introduces a new proof obligation. For each step identify whether it uses (a) old valid evidence about a historical event, (b) the currently authorized decision from the protected boundary, or (c) a new conformance conclusion. Prove that no currentness claim relies on another claim about the same cut unless the latter already has an independent proof or both are proved together. Where restoration cannot prove continuity of a dependency, authority should remain undecided in the proof graph until the contract establishes its disposition. [Native R2 result](Native-owner-selection-rollback-result.md) · [Actual source boundaries](Native-acceptance-and-recovery-boundaries.md)

## An audit reusable across kernel candidates

For each necessary guarantee record the subject, scope, cut or tenure, and the exact dependencies. Label edges by whether they come from the same coherent cut, an earlier cut, or a declared external premise. Check that each recovery and normal transition preserves the dependency meaning and is covered by an actual proof. A local theorem can be stronger than this scheme, for example by proving a jointly recovered invariant directly. The audit's useful failure output is a concrete transition with a missing predecessor, an ungrounded same-cut group, or an unproved external boundary. It does not imply a specific kernel partition or require separate proof components.

**Disposition.** The proof method closes a specific composition gap without importing a physical synchronization mechanism. Native application needs exact recovery transitions, a chosen currentness/reservation contract and evidence that every pertinent read and effect belongs to the stated cut. The current argument neither replaces that work nor proposes another native trial.

## Mechanized obligations

The [Lean proof](proofs/GroundedAssurance.lean) proves transition-local ranking and reachable preservation with transition-dependent ranks, the false mutual-implication example, and an incoherent mix of earlier coherent cuts. Run `lean docs/research/kernel-0/proofs/GroundedAssurance.lean` on Lean 4.19.0. All four exported obligations checked without axioms.
