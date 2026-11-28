---
title: Which verification observations distinguish the remaining explanations?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Method
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Native-owner-selection-rollback-result.md
  - docs/research/kernel-0/Recovery-with-several-legal-outcomes.md
  - docs/research/Resource Solver Red Green Mutation Verification 2026-11-01.md
last_updated: 2026-11-28
---

# Which verification observations distinguish the remaining explanations?

One way to avoid repeating a passed experiment is to name two explanations still compatible with it and write down exactly what evidence the next check could distinguish. A test can exercise code absent from a prior test and still be unable to distinguish the open claims. Conversely a new check can reuse a retained capture without performing a second trial. This argument gives a selection rule relative to a named hypothesis set, including when tests in a batch have to share a history. [Native retained evidence](Native-owner-selection-rollback-result.md) · [Targeted mutation precedent](../Resource%20Solver%20Red%20Green%20Mutation%20Verification%202026-11-01.md)

## Exact criterion for selecting a fixed suite

For each hypothesis h about the implementation or evidence pipeline, let Hₕ(Q) be the joint observations feasible under a fixed suite Q. Observations include the captured values, source revision, relevant ordering and relevant outcomes rather than only a checker pass marker. Use the suite's actual resets and correlation rules. Under the declared exhaustiveness assumptions a suite guarantees discrimination between h and g exactly when their joint observation sets are disjoint. If they overlap, the same possible result supports both. If disjoint, every observed feasible answer for one excludes the other. A result outside both sets challenges the model, expected outcomes or capture assumptions.

For deterministic probes on independently restored inputs, mark the unordered hypothesis pairs separated by each probe. A suite that distinguishes all relevant pairs is exactly a set cover of those pairs. Costs can include proposed runs, setup, a missing monitor, and review, with shared costs kept explicit. A single known target versus a catalog of named defects reduces to covering target–defect pairs. Other differences between defects need not be observed merely to falsify them. The resulting guarantees depend on the hypothesis set, complete observable predictions and trustworthy expectations. Identifying a named guard omission gives no coverage claim over omitted routes or an oracle that shares the mistaken policy.

For nondeterministic probes there is an important qualification. If Hₕ(Q) is exactly the product of the per-probe possibilities for h and the same is true under g, they separate exactly when at least one probe's own possibilities are disjoint. Otherwise leave the joint sets intact. For example, two reports may each be zero or one under both explanations. An implementation that always reports equal bits differs from one that always reports opposite bits **only** when the pair is read under its stated common history. Independently resetting between probes can destroy the distinguishing observation. Conversely combining separately feasible reports without a joint witness can fabricate a failure. Track what fixes correlation: the cut, selected identity, store state, repeated query or other shared source.

## When adaptivity saves one run

For deterministic scenarios, split the remaining hypotheses according to the next available probe's expected output. A worst-case cost bound for a decision tree is the selected probe's cost plus the highest bound among its possible successor classes. Take the minimum over probes that strictly split the current class. A terminal class has no relevant unresolved pair, and a class without such a split is unresolvable through this menu. This is exact by induction for a finite fixed menu with independent deterministic probes and additive costs. If tests change eligibility or remaining resources, the recurrence needs actual remaining actions and state. For correlated nondeterminism, restrictions of the joint observation histories must be carried forward. Marginal possibilities alone can be misleading.

For four distinct hypotheses there can be one probe splitting them into two pairs and two probes each separating just one of the pairs. For example, the three binary questions ask whether the index is in {1,2}, whether it is 2, and whether it is 4. Any fixed two questions leave a collision. Starting with the split and then asking the question for the returned pair identifies the hypothesis in two steps. The example is a planning bound. Permission to deviate from an admitted experiment is a separate question. An adaptive schedule, if sought, has to fit the experiment admission's stated branches and limits.

## Applying the rule to owner rollback evidence

The retained R0, R1 and R2 cases all return the exact F4 reply `already-accepted` with the same journal event count and within-case unchanged bytes. A suite that observes only those fields cannot discriminate an observer that conflates F4 with F3 settlement from the two-plane interpretation. Observing the owner settlement distinguishes R2 from R0/R1. Observing the selected record before and after the retry distinguishes R0's replay from R1's repair. Compare the fields to the claim about recovery; the first check's apparent positive control is an opportunity to reuse the existing recorder and evidence without replaying the native run.

A competing “strict historical restoration” proposal and “new authorized cancellation” proposal can still produce the same initial stale-effect denial and the same unchanged journal. Once their preconditions are defined, distinguish them through the selected continuation result under a known eventless cut, whether an old outstanding obligation survives or is explicitly released, and whether a fresh currently authorized operation succeeds after the premises hold. A failed readiness check alone need not distinguish either policy. These are predicted differences between prospective contracts. The R0–R2 archive does not decide the eventless-reservation policy or the owner-authenticated W5/W6 interface. [Conditional owner recovery contracts](Recoverable-owner-selection.md)

**Disposition.** A proposed next controlled run earns its place by naming the unresolved pair it can separate and the fields that do the separating. A hypothetical mutation is informative only when its projected observation differs from the reference in the intended scope. Preserve joint observation assumptions and source versions. No native trial or new mutations were run for this argument.

## Mechanized obligations

The [Lean proof](proofs/DiscriminatingChecks.lean) checks both directions of the product criterion and the two observations whose marginals always overlap despite disjoint joint values. Run `lean docs/research/kernel-0/proofs/DiscriminatingChecks.lean` on Lean 4.19.0. The check exited 0. Only the product converse requires classical choice.
