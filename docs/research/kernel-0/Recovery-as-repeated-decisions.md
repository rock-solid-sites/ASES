---
title: When does a safe recovery choice preserve future progress?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Recovery-with-several-legal-outcomes.md
  - docs/research/kernel-0/Recoverable-owner-selection.md
  - docs/research/kernel-0/Minimum-revalidation-at-commit.md
last_updated: 2026-11-28
---

# When does a safe recovery choice preserve future progress?

A recovery controller may have an answer that is safe for all currently possible histories, yet choosing it can make the next required answer impossible. The missing input is how the choice changes the evidence or obligations that survive. A one-shot test is complete for the decision it models. It is insufficient for a recovery policy with required future reactions. [One-shot common outcomes](Recovery-with-several-legal-outcomes.md)

## A two-stage discriminator

Two hidden authoritative histories differ in the outcome of an old request. In both, a caller can ask the controller to finish a recovery step. Two replies are allowed and both finish that step. One reply also releases the last owner that can prove the old outcome. The other holds the owner long enough to obtain that proof. If the next request asks for the old outcome and requires an exact answer, the first choice can reach a view in which no correct answer exists. The second can succeed. Both choices had the same immediate legality.

This is a counterexample about an authority contract, not a claim that the native model exposes a release of this form. It motivates checking a retirement or compaction step against the old observations that future requests can still require. If the contract allows retiring that old answer explicitly, the counterexample's second request changes. If the controller can preserve independent outcome evidence before release, the adverse branch changes.

## Exact model for finite, repeated must-answer requests

Let S be a finite set of true states, with a small command set, action set and observation set. The controller's belief B is exactly the nonempty set of states compatible with its observed history. For an observed input i, discard worlds where i could not occur. Call the result Bᵢ. A response a is available for this input exactly if it satisfies the per-state requirements in every state in Bᵢ. An admitted response has at least one possible successor for each compatible state. By a supplied transition relation, each permitted hidden transition produces an observation o. The next belief is

```text
Post(Bᵢ,i,a,o) = {s' | some s in Bᵢ can take (i,a,o) to s'}.
```

Possible observations are exactly those with nonempty Post. A completion promise means that every admissible input requires a response from the declared action set. The model allows explicit terminal states with no legal further input. It does not infer eventual response from a safety predicate permitting perpetual deferral.

For a region W of possible beliefs, let F(W) contain B if for every input with Bᵢ nonempty there exists a common permitted response whose every possible successor belief belongs to W. F is monotone. Starting with all nonempty beliefs, repeatedly replace W by F(W) until it stabilizes. There are at most 2^|S|−1 beliefs. The sequence is decreasing and terminates after at most that many strict removal rounds.

**Necessity and sufficiency.** In the stable region choose an allowed response witnessing F for each belief and input. Induction gives a response on every valid finite play and keeps the belief inside the region. Conversely, the set of beliefs from which any strategy can meet the same promise is postfixed under F: its first response is allowed, and each possible observation leaves a continuation strategy. This holds even if that strategy remembers the complete input/output history. Thus it lies in the computed greatest region. Belief plus current input suffices in this model. A controller that knows only a coarser observation must either improve its state estimate or demonstrate a strategy for the resulting weaker interface.

A removed belief has a finite explanation. At its first removal round there is an input such that every response is already wrong in some compatible world or leads under some possible observation to a belief removed at an earlier round. Follow the removal ranks to build a finite adversarial tree. A branch through that tree can be realized by a coherent hidden history: the exact nonempty successor sets justify choosing its underlying hidden predecessors backwards. Approximating reachable beliefs can prove safe policies when conservative, but a claimed lower bound from an overapproximation still needs a reachable witness. This is the standard knowledge-game structure applied to recovery decisions and retained evidence. [Imperfect-information games, Chatterjee et al.](https://lsv.ens-paris-saclay.fr/~doyen/papers/Algorithms_for_Omega-regular_Games_of_Imperfect_Information.pdf)

## A usable composition boundary

For two truly independent owners, let the possible state be a product B₁×B₂. Every input acts on just one owner. Its conditions, observations and transitions mention only that owner. The other owner stutters and contributes no new shared information. The owners retain their own outcomes. Then combining strategies from the two local winning regions is a winning joint strategy. Product beliefs are preserved by every tagged local projection. Conversely an environment can address just one owner, so a local losing region cannot be repaired by the product under these conditions. A shared buffer, budget, release rule or correlated fault can invalidate the premises. The test is about **independence of future obligations and observations**, not merely the existence of separate current stores.

**Disposition.** A one-shot common output permits the next recovery step. Required future outcomes justify checking closure under the resulting belief update. This narrows the native eventless-design branch: specify whether exact older outcomes must still be answerable after cancellation and which of the supporting observations survive. An executable implementation comparison awaits a stated contract and its own admission. The abstract proof remains valid without choosing native storage, authentication or timing mechanisms.

## Mechanized obligations

The [Lean proof](proofs/RecoveryDecisions.lean) shows that the union of postfixed belief regions is itself the greatest fixed point, that finite-horizon regions decrease, and that any stabilized finite horizon gives exactly the viable region. It constructs a policy keyed only by belief and input and verifies the two-stage release counterexample. Run `lean docs/research/kernel-0/proofs/RecoveryDecisions.lean` on Lean 4.19.0. The check exited 0. Fixed-point and stabilization theorems report no axioms. The positional decision construction uses standard classical foundations. The finite bound on the number of beliefs and the accuracy of a native belief update are separate from those mechanized obligations.
