---
title: What changes when three usage reports may overlap?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Reconciling-partly-overlapping-usage-evidence.md
  - docs/research/kernel-0/Budgeting-for-unresolved-external-attempts.md
last_updated: 2026-11-28
---

# What changes when three usage reports may overlap?

A Work Unit may observe one meter through local instrumentation, a gateway, and an account report. Combining these sources can reduce double-counted consumption only when the records can describe the **same** metered units. Independent charges from different meters or liabilities stay separate even if the same activity generated them. With three normalized sources, even exact pairwise overlaps leave some usage unresolved. A two-source matching procedure also loses its general tractability once plausible origin groups link all three sources. [Two-source exact model](Reconciling-partly-overlapping-usage-evidence.md)

## Exact interval from three totals and three pair counts

Let A, B and C be finite unit sets under the same meter, scope and cut. Suppose each total a,b,c and every inclusive pairwise intersection pAB,pAC,pBC are known. Let t count units in all three. Each pair-only region contains pXY − t units, and the A-only region contains a − pAB − pAC + t. The other two single-source regions follow by exchange of labels. All seven regions are nonnegative exactly when

```
lower = max(0, pAB + pAC − a, pAB + pBC − b, pAC + pBC − c)
upper = min(pAB, pAC, pBC)
lower ≤ t ≤ upper.
```

Every integer in the interval has a realizing assignment. Create seven disjoint pools of the computed sizes and place each in the indicated source sets. The interval is empty precisely when these totals and overlaps cannot coexist in the model. For a feasible interval, exact observed union size is a+b+c−pAB−pAC−pBC+t. Its extrema use the two endpoints for t. Additional information about which concrete record must overlap with which can tighten these bounds or reject an assignment. The formula is exact for the stated **aggregate** evidence.

For three sources of size two and all pairwise counts equal to one, a witness with three units uses one distinct unit for each pair. A witness with four units uses a common unit in all three and a private unit in each source. Exact totals and exact pairs are the same. Conversely, with the same totals and pair counts 2,2,0, each pair can be realized in isolation but jointly they cannot. The first two overlaps would identify both of A's units in each of the other sources and force their intersection to have size two.

## Record-level planning with arbitrary candidate origins

Fix n distinct unit positions in each of three sources. A candidate report origin may group at most one position from each source, and the admissible triples are supplied in a finite list. Allow singletons and, if useful, all two-source restrictions of allowed triples. A reconciliation is a partition of all 3n positions into admissible groups. Its union size is its number of groups. To have at most n groups, every group must contain three positions, since each group accounts for at most three. Thus size n is reachable exactly when the supplied triples contain a perfect three-dimensional matching. Conversely any such matching supplies a valid reconciliation. Deciding the minimum threshold is NP-hard even though all counts are single units, and the explicit unit-position decision problem is in NP by verifying a proposed partition. The reduction uses actual triple eligibility, independently of whether that eligibility was conveyed as a route or provenance constraint. [Karp, 1972](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/Karp.pdf)

This differs from the tractable aggregate calculation above. Three named sources do not make every instance hard. A verified shared underlying ID fixes the grouping, or independent disjoint classes that can never represent the same unit can be solved separately and their intervals added when every combination is feasible. For a more general partial binding, a conservative interval can still support admission, while a consistency witness or a capacity bound can show which additional evidence would change the decision. The hardness result describes the unrestricted model and gives no latency estimate for actual datasets.

**Disposition.** For a three-report adapter, first ask whether the inputs describe one liability and whether the only evidence is totals, authenticated pair counts, or incidence of actual unit IDs. Use the corresponding proof and keep the interval separate from settled liability and pending exposure. No new provider activity, accounting implementation or synthetic matrix was run. The source-specific normalization and authenticity obligations remain open.

## Mechanized obligations

The [Lean proof](proofs/ThreeSourceOverlap.lean) checks the exact three-way count bounds, inclusion-exclusion, two distinct union sizes at identical pair measurements, and the contradictory three-source case. Run `lean docs/research/kernel-0/proofs/ThreeSourceOverlap.lean` on Lean 4.19.0. The check exited 0 using standard axioms. It formalizes the aggregate case. The perfect-matching reduction is deductive prose.
