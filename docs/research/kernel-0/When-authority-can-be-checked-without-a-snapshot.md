---
title: When can authority be checked without a common snapshot?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Minimum-revalidation-at-commit.md
  - docs/research/kernel-0/Grounding-delegated-authority.md
  - docs/research/kernel-0/When-a-lease-can-replace-a-fence.md
last_updated: 2026-11-28
---

# When can authority be checked without a common snapshot?

Reading two live authority bits from different times can manufacture a permit that no coherent state granted. A different contract, where each read establishes a **bound that still holds at the effect**, can admit a positive decision without a single snapshot. The distinction is between authentic historical observations and continuing evidence. It gives a way to eliminate some fresh lookups without eliminating currentness at the actual effect. [Existing revalidation result](Minimum-revalidation-at-commit.md) · [Committed-obligation profile](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-External-Effects.md)

## Exact bounds for a monotone guard

Let S be a set of scope-bound positive facts and let the actual live set at effect time be X⊆S. The effect guard P is monotone: if it permits X, it permits every superset. The available evidence establishes L⊆X⊆U, with L⊆U. The facts in L are guaranteed true at the decision and facts outside U are guaranteed false. The guarantees may come from different times or components, provided each one holds at the same effect.

- If P(L), permission is certain for every compatible X.
- If ¬P(U), refusal is certain for every compatible X.
- When all intermediate sets are genuinely possible, these are exact. If P(L) is false, L itself is a possible denial. If P(U) is true, U itself is a possible permit. In the remaining mixed case a definitive response needs more evidence or a weaker contract.

If instead physical or logical correlations eliminate some intermediate sets, the extremal conclusions remain sufficient. They need not be necessary. For example the contract “at least one of x and y always live” establishes P(x∨y) without putting either fact individually in L. A jointly authenticated correlation can be cheaper than acquiring one more field. Conditional feasibility must be verified before presenting the computed rectangle as an exact lower bound.

Possible one-sided temporal evidence includes:

| Observed fact and contract | Bound it can still establish |
| --- | --- |
| A commitment is durably accepted and the exact immutable historical observation remains available | That historical fact belongs to L despite executor replacement |
| An incarnation is irreversibly revoked and its identity cannot be reused in this scope | That incarnation stays outside U |
| A live fact was read before a later independently authorized withdrawal could occur | No continuing positive bound on that fact |
| An authenticated issuer holds a fact true through a stated interval | That fact belongs to L if the whole effect lies within the protected interval, with valid clock and recovery assumptions |

The resulting argument justifies only the predicate it covers. A mutable balance can still be overspent if two permitted uses do not reserve it indivisibly. A commitment can still be wrongly attributed if the observation names the wrong effect or incarnation. Combining immutable facts does not replace validation of material references, negative dependencies or authenticity. [Lease bounds](When-a-lease-can-replace-a-fence.md) · [Conserved resource claims](Transferring-and-reclaiming-resource-allowances.md)

## Smallest per-decision certificates

For a finite monotone P define a support as an inclusion-minimal true set. Treat already proved stable facts as constants in the remaining guard. Under independent unknown facts, a positive decision can be certified by authenticating any one live support, and every set of authenticated positives that suffices contains a live support. The necessity is the lower-corner argument above. With distinct read costs, choose a minimum-cost available support. A negative decision is certified by authenticating false facts hitting every support. Otherwise there is a support in the upper corner U, so some permitted world remains. The same proof yields exact positive and negative certificate complexity for a fixed actual input and the given fact vocabulary.

| Guard over n independent facts | Smallest positive certificate | Smallest negative certificate |
| --- | ---: | ---: |
| All n must hold | n | 1 |
| At least one must hold | 1 | n |
| At least k must hold, 1≤k≤n | k | n−k+1 |

These are certificate sizes. An evaluator trying to discover which facts hold by querying them may need more reads than a producer who supplies a correct witness. Every supplied witness still has to be interpreted by a trusted verifier. Even finding the smallest positive certificate can be NP-hard when all roots are live: for a monotone guard in conjunctive normal form, a selected fact covers every clause containing it. Finding the smallest set meeting all clauses is set cover. A proof tree that duplicates a fact used by two clauses can overcount the true verification cost. Alternative supports can reduce cost, but processing them cannot silently change the effect or accepted scope. [Grounded conjunctive and disjunctive rules](Grounding-delegated-authority.md)

## Applying the criterion to a gate

Specify one canonical proposed effect and the authority predicate actually used. Identify the trusted atom vocabulary and which positive or negative claims remain stable across the interval from observation to effect. A support is sufficient when every required claim remains valid at the effect, even if the claims were acquired separately. Under independent unconstrained expiry, each required claim's interval must cover that event. If intervals overlap only earlier, cache reuse is unsound unless an irreversible obligation was already accepted in that overlap under the declared profile.

**Disposition.** A coherent snapshot is a sufficient realization for the volatile cases, while stable one-sided observations can discharge some of its obligations. The theorem neither chooses the present ASES gate predicate nor proves completeness of a native effect footprint. A candidate conformance proof should name its monotonicity assumptions and include a distinguishable non-monotone or changing-balance control. A new verification benchmark or runtime optimization remains a separate decision.

## Mechanized obligations

The [Lean proof](proofs/MonotoneEvidence.lean) checks both exact rectangle rules, necessity of a positive support, and both directions of the negative hitting condition. Run `lean docs/research/kernel-0/proofs/MonotoneEvidence.lean` with Lean 4.19.0. The check exited 0. The extremal guard theorems and the positive certificate result report no logical axioms. The general negative support existence statement uses standard classical foundations. Trusted fact interpretation and evidence freshness remain premises.
