---
title: Which state reductions preserve a Work Unit progress proof?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/When-recovery-must-make-progress.md
  - docs/research/kernel-0/State-elimination-under-partial-contracts.md
last_updated: 2026-11-28
---

# Which state reductions preserve a Work Unit progress proof?

A state reduction for public replies can discard exactly the distinction that keeps an internal recovery loop from recurring. An exact finite-state progress check needs either a reduction with path correspondence or a clear statement of which way the reduction approximates actual behavior. This is distinct from finding a smaller device for a partial input/output contract. [Progress obligations and fairness](When-recovery-must-make-progress.md) · [Partial input/output state reduction](State-elimination-under-partial-contracts.md)

## A merged state that can wait forever

Consider a finite concrete graph. Staging advances internally to selected. Selected answers the particular pending request. Answered can remain answered. From any concrete state the request is answered within two graph steps. Both the staged and selected states have the same public pending view.

Put an edge between two views whenever some concrete edge connects representatives. The quotient has an internal pending self-loop, witnessed by staged to selected, and a pending to answered edge. It can wait forever by taking the quotient self-loop. The self-loop cannot be lifted from the actual selected stage. No trusted external availability assumption or unfair scheduler is needed for this counterexample. Forward projection is sound for excluding paths if all the relevant labels are preserved, but a bad quotient path need not explain an actual failure. The infinite bad path can be spurious even before any action is hidden or compressed.

There is a dual labeling error. Suppose selected is the only representative where the answering action is enabled, and a pending staged representative genuinely can loop indefinitely. Marking the whole class continuously enabled because *one* member enables the action lets weak fairness discard the real staged bad run. Forward inclusion of edges carries no guarantee when the fairness premise itself is changed by projection.

## Checkable path correspondence

Use a state map q and edge labels recording the obligation and fairness events. Keep the pending monitor and all relevant enabled predicates constant on each q-class. Require both clauses.

1. Every labelled concrete step projects to a labelled quotient step.
2. For every concrete state s and every labelled quotient step from q(s) to a class v, there is a concrete successor from **s** with that label and class v.

The first clause projects any concrete path. The second inductively lifts every quotient path starting at any prescribed concrete representative of its initial class. It must find a successor from the representative already chosen, including after earlier non-visible steps. For an infinite quotient path, recursively choosing each successor produces an infinite lift. Marking starts, substantive discharge, enabled predicates, and taken events identically preserves the progress monitor and each weak or strong fairness condition at every position. With corresponding initial states this proves equivalence of a bad-run query and of the availability of a fair continuation after each matched prefix. In a finite graph, the second clause is equivalent to equal sets of labelled target classes across all members of a class. The observations and the labels determine how to refine a failing partition.

This is a sufficient equivalence check. A coarser abstraction may preserve a single chosen progress property. A one-way overapproximation with correctness of label projection can still prove absence of bad paths even when it cannot produce reliable negative examples.

## Hiding a whole finite sequence of internal steps

A different reduction replaces finite segments by edges between retained boundaries. To preserve the fairness interpretation, each reduced edge can record, for each action, whether the segment contains any enabled state, any disabled state, and any taken event. Count each state and edge in at least one segment and at most finitely many, with every segment finite. Under an infinite sequence of such segments, an event or state predicate occurs infinitely often exactly when its mark occurs on infinitely many segments. Apply this both to enablement for strong fairness and to *disablement* for weak fairness, since persistent enablement means that disablement happens only finitely often. For the same argument, eventual continuous environment facts need a mark for any violation. An internal discharge must also be recorded if the selected contract counts it.

Adjacent reduced edges must be liftable from the same concrete boundary representatives, or the preceding seam counterexample applies again. A concrete execution can also take infinitely many hidden steps without reaching another retained boundary. Either represent that behavior or prove it impossible under the checked environment contract. A well-founded decrease on every hidden edge suffices for the latter. It proves no relationship between graph steps and elapsed time.

**Disposition.** A classifier of staged and selected material can be irrelevant to the next public reply yet essential to a progress claim. A proposed elimination can identify the monitor and fairness facts it preserves, provide a lift or a one-sided explanation, and justify every hidden infinite suffix. The disposition concerns reduction of the proof graph. Native scheduler correspondence remains open.

## Mechanized obligations

The [Lean proof](proofs/FairQuotient.lean) checks per-position transport of weak and strong fairness, construction of the forward projection and infinite path lift, and the spurious pending loop against the concrete two-step bound. Run `lean docs/research/kernel-0/proofs/FairQuotient.lean` on Lean 4.19.0. The check exited 0. Only the general lift uses classical choice. Finite-segment compression and a native model's matching clauses remain separate obligations.
