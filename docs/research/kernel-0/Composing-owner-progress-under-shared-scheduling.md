---
title: When does a shared scheduler preserve each owner's progress promise?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/When-recovery-must-make-progress.md
  - docs/research/kernel-0/Removing-state-while-preserving-progress.md
  - docs/research/kernel-0/Recovery-as-repeated-decisions.md
last_updated: 2026-11-28
---

# When does a shared scheduler preserve each owner's progress promise?

One owner can be able to finish recovery whenever its action is served, yet never receive that service when several owners share a scheduling boundary. A sound proof of locally correct reactions needs a separate link from global scheduling and eligibility to each local promise. This issue is independent of whether any two protected effects commute. [Finite-state progress check](When-recovery-must-make-progress.md) · [Input-level recovery composition](Recovery-as-repeated-decisions.md)

## Two small counterexamples

**Aggregate fairness.** Owners A and B both continuously have eligible work. Every global step serves an A action, because A always has more tasks. The union of A and B actions is continuously enabled and its scheduler takes an action from that union at every step. Weak fairness for that single class is met. B can nevertheless remain pending forever. Separate class or per-obligation fairness is a stronger premise. Giving each owner an occasional turn can still fail when the owner's required action competes with an endless stream of its other actions. [Action classes in Lynch and Tuttle, section 3.3](https://groups.csail.mit.edu/tds/papers/Lynch/I0Automata.pdf)

**Intermittent global opportunity.** A local check sees B as continuously eligible. The shared resource makes the global B action available only on alternate steps. The global scheduler can skip every opportunity and still satisfy weak fairness for B, since that action never becomes continuously enabled. Strong fairness for the globally intermittent action would rule out this run. Alternatively a grant that reserves the opportunity until B takes it changes the enabling premise. These are conditional alternatives. Neither follows from a separate B queue or a fast reactor.

## A projection certificate

Represent the local projection on the global step indices, allowing stutter when a step belongs to another owner. If a local proof drops stutter steps, establish that the resulting finite or infinite projection lies within its own trace and progress semantics. In particular a permanently absent owner cannot disappear merely because it has no more projected events.

A local fairness obligation is an implication from a trigger to recurrence of a local taken event. For weak fairness the trigger is eventual continuous enablement. For strong fairness it is infinitely frequent enablement. To inherit it from a declared global obligation, suffice to prove both conditions on every candidate composed run.

1. Whenever the local trigger holds on the projection, the corresponding global trigger holds on the run. The triggers may use different fairness strengths.
2. Every occurrence chosen by that global taken event witnesses an occurrence of the correct local action or service at the corresponding step.

Then the global implication gives recurrence of the local actions. This supplies the local progress premise alongside whatever environment, custody, and actual-step correspondence the owner's proof already needs. In a true interleaving product with independent enabledness and distinct owned labels both conditions are immediate. A global “some owner was served” event can fail the second condition. Intermittent shared eligibility can fail the first. Use a condition about the same pending request or an adequate local scheduling policy if a generic owner turn is insufficient.

These two implications give a sufficient certificate, not the weakest possible relationship. A finite graph allows direct falsification. Keep the actual global fairness conditions, then check for a run with the local trigger and eventually no local taken event. To negate local weak fairness, require the local enabled predicate and absence of local service continuously on the recurrent part. To negate local strong fairness, require recurrent local enablement and the same absence of local service. These are the state and edge restrictions of the earlier recurring-component procedure. A fair counterexample identifies the actual shared scheduling gap. [Recurring-component criterion](When-recovery-must-make-progress.md#a-finite-state-decision-procedure-for-one-outstanding-obligation)

## Joint completion is its own obligation

For a fixed finite set of owners or requests, if each eventually reaches a retained discharge fact, then all are discharged after the latest of those finite steps. A handover can use this argument only if the facts remain valid for the same attempt until the handover occurs. A supply of transient ready states that reset on another owner's turn need never be jointly ready. Per-request progress on an unbounded stream also gives no promise that all outstanding requests will ever be absent at once. A closure or intake boundary can turn the latter requirement into the finite fixed-set case, while leaving fencing, currentness and accepted-content custody to their own proofs.

**Disposition.** Require the scheduling premises at the scopes the Work Unit claim can observe. A shared process can implement independent scheduling obligations, while isolated processes can still share a single insufficient admission opportunity. A native progress check first needs the actual owner-authenticated transition and declared availability assumptions. No native or synthetic scheduler ran for this argument.

## Mechanized obligations

The [Lean proof](proofs/FairOwnerScheduling.lean) checks fairness transport from the trigger and taken-event implications, the continuously enabled but starved owner, and the alternate-step difference between weak and strong fairness. Run `lean docs/research/kernel-0/proofs/FairOwnerScheduling.lean` on Lean 4.19.0. The proof checked using standard axioms.
