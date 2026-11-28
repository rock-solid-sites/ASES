---
title: When do separate checks prove one legal effect?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Minimum-revalidation-at-commit.md
  - docs/research/kernel-0/How-independent-are-authority-checks.md
last_updated: 2026-11-28
---

# When do separate checks prove one legal effect?

The September abstract semantics casts a resolved commitment as a current guard, the declared whole effect and a post-state invariant. It describes these as a decomposition of one admissible relation. If components really have separate observations, a collection of individually accurate checks can accept a transition that none of the successful reference histories permits. Establishing a coherent cut is necessary for many such designs. It cannot by itself repair an omitted relation between facts that are all current. [September guarded relation](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-Abstract-Semantics.md#resolved-transition-relation) · [Commit-time revalidation](Minimum-revalidation-at-commit.md)

## Exact criterion with required positive cases

Fix a set D of candidate effect instances and the legal subset L. Each instance includes the relevant pre-state, request, actual whole effect, outcome and applicable external facts. Let P be the subset of legal instances the implementation is required to permit under this profile. Model check i by its trustworthy observation oᵢ(d) of an instance. Its verdict may depend on precisely that observation. Assume that the physical boundary permits the instance exactly when every check accepts. Facts established by prior actual prevention can be reflected in D, with the prevention proof retained separately.

For each i retain the set of observations occurring in P. A candidate is forced through any collection of conjunctive checks that accepts all P precisely when its observation belongs to these retained sets for **every** i. In particular, safe checks that allow all P exist if and only if

```
for each d in D minus L:
    some i has no p in P with oᵢ(p) = oᵢ(d).
```

Necessity follows because every check must accept the observation of each required positive. If an illegal candidate projects into every such set, each check is forced to accept it. Sufficiency follows by choosing each check to accept exactly its retained observations. No check can reject an allowed observation on the grounds that another component's view might be wrong. It may instead consume a trustworthy shared value, certify a suitable dependency or operate with a stricter upstream restriction proved about D.

For a failed factorization the counterexample consists of one candidate forbidden transition and, for every check, a required legal transition with the same observation. The witnesses are allowed to differ across checks. This is a relative version of lossless relational joining. It supports optional safe denial by taking P smaller than L, and allows dependencies supplied by an independently proven candidate domain. If P equals L, the test concerns exact enforcement. Existence of a filter is a set-theoretic result. It does not establish cheap computation, terminal response, durable authority, or a sufficiently fine real effect model. [Relational join dependencies, Maier, chapter 7](https://web.cecs.pdx.edu/~maier/TheoryBook/MAIER/C07.pdf)

## A binding counterexample

The same outward Work Unit operation may be valid on either of two actual provider routes. In required positive cases the current grant is for route zero and the effect is on zero, or the grant is for route one and the effect is on one. The first check sees only which route is granted. The second sees only which route actually receives the effect. A third confirms that total usage remains within the allowed row, which can be true for equal charges in all four cases. The mixed candidate grant-zero/effect-one passes every check that accepts both positives. A coherent snapshot of the separate facts leaves this witness intact.

A joint check that the grant route equals the actual route suffices for this relation. A shared authenticated operation binding can also do it, provided independent path constraints ensure that the effect is on the bound route and the grant authorizes that same bound route. A mutable display label, planned route or account alias may appear equal in both reports while still leaving the mixed actual effect indistinguishable. The right fix depends on what the implementation can bind, where it binds it, and what a downstream effect owner can guarantee.

There can be irreducibly higher-order observations. Let three binary facts have even parity in every required legal candidate. All possible observations of every pair appear in the positive set. Any actual odd candidate then has a positive witness for each pairwise check, even if all overlapping views agree on the shared facts. This is a formal discriminator for a proposed view decomposition, not a suggested authorization policy. In contrast, for a genuine conjunction of independently grounded boundary vetoes, their individual truth values already suffice for that specific policy.

## Comparing primitive proposals

With a fully observed unrestricted transition relation, any safe relation is expressible as a single predicate. One can also choose a vacuous factor and put all work in the other. Consequently vocabulary size or the ability to encode a proposed transition is weak evidence of an enforcement reduction. Compare concrete candidate mechanisms by fixing D, L and the required positives, then spelling out what each observer actually receives at the effect boundary. The route example removes one claimed independence without needing a special route primitive or a universal central authority. If the domain and positive set are finite, a failing choice can be diagnosed directly, and proposed extra observations can be compared by the set of forbidden instances they separate.

**Disposition.** Treat guard/effect/invariant as a candidate proof decomposition. An implementation that splits observation or authority still needs either a factorization proof, a verified candidate-domain restriction, or additional binding. The November public comparison does not pin a final ISOLATE/CONNECT/ORDER contract. Exact historical passages are available for further provenance reconciliation. The distinction between the exploratory definitions and a reviewed normative specification still matters. Neither the guarded source nor these factorization results establishes a correspondence with the historical triad. [Historical comparison and source gap](../astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md#relation-to-previous-kernel-research)

## Mechanized obligations

The [Lean proof](proofs/FactoredAcceptance.lean) checks the exact existence criterion with arbitrary typed observations, the mixed-route counterexample, and sufficiency of the paired view for equality. Run `lean docs/research/kernel-0/proofs/FactoredAcceptance.lean` on Lean 4.19.0. All five exported components checked without axioms. It does not prove any concrete observer, binding, or provider contract.
