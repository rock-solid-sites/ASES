---
title: How much usage can partly overlapping reports establish?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Budgeting-for-unresolved-external-attempts.md
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
last_updated: 2026-11-28
---

# How much usage can partly overlapping reports establish?

The Resource Solver reconciliation preserves two controls. A provider report of 15 units known to cover 10 local units, with another five units outside that coverage, establishes 20 observed units. With an unknown overlap, two reports of 10 and 15 protect availability using an upper bound of 25. The upper bound may improve even when exact coverage is unknown. The question is how to derive both endpoints and check the evidence for each. [Source controls and their limitations](../Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md#accounting-and-monitoring-evidence)

## Exact bounds for two internally disjoint sources

Fix an account, meter, period, unit and evidence cut. Each source reports a collection of internally disjoint batches. A unit in one local batch can agree with at most one unit in a provider batch. Batches contain fungible, integral units at the granularity at which agreement is defined. A trusted relation gives possible pairs of batches. A bound on a pair, row or column may also establish how many units actually agree. Such a lower bound is an overlap claim, which is stronger than membership in the same time window. The model assumes that arbitrary assignments satisfying these constraints are realizable, with unpaired units distinct across both sources. This excludes unrepresented dependency, joint occurrence constraints, repeated cumulative reports treated as distinct batches, and unsplittable operation charges.

Write L and P for the total units reported by the local and provider sources. Let xᵢⱼ count agreements between local batch i and provider batch j. Put edge capacities and optional lower bounds on xᵢⱼ. Require each row total to fall within its certified lower bound and its batch size, and impose the analogous constraint for each column. If the constraints are feasible, then the exact least and greatest distinct observed usage are

```
least    = L + P − max Σ xᵢⱼ
greatest = L + P − min Σ xᵢⱼ
```

Each physical interpretation counts the same unit twice precisely once per agreement, so its union has that size. Conversely, for a feasible integer allocation partition each local and provider batch into matched fragments of sizes xᵢⱼ and an unmatched residue. Identify the paired fragments one-to-one and give the residues fresh distinct names. This is a witness for every feasible allocation under the stated model. In particular, merely allowing a possible overlap leaves the largest union at L + P if the all-zero allocation remains feasible.

Represent the bounds as a network with arcs from source to local rows, rows to provider columns, and columns to sink. Arc lower and upper capacities are the corresponding constraints. A return arc from sink to source, with lower bound zero and capacity min(L,P), makes flow conservation equivalent to an allocation. For feasibility, subtract each arc's lower bound and route the resulting imbalances with an auxiliary source and sink. A saturating auxiliary flow provides a feasible circulation. A cut with capacity below the required total rejects the reported combination. Given any feasible circulation, set aside the return arc and use a residual network: a forward residual arc can increase a value up to its upper bound and a reverse one can decrease it down to its lower bound. Paths from source to sink increase overlap and paths in the other direction decrease it. If a more extreme value were feasible, subtracting the current flow from it would yield residual flow in that direction, which decomposes into paths and cycles and therefore contains a path. Thus an allocation and a reachability cut for the appropriate residual network certify each endpoint. Integral capacities give integral augmentations. Augmenting one unit at a time between the endpoints also shows that every intervening integer is possible. Standard flow algorithms can avoid taking one step per unit.

## Cases that change an admission decision

Suppose two local batches contain four units of account activity each. A provider report contains six units. It certainly includes at least three units from the first batch, can include up to its four units, and cannot include the second batch. The exact union lies between 10 and 11. Treating all coverage as unknown protects 14 units. Treating possible coverage of the full first batch as certain only protects 10. For a ceiling of 12, a new additional unit is safe on these observation assumptions and two units cannot be guaranteed safe. This example still requires a separate bound on all unobserved liability and atomic admission at the actual effect boundary.

Obligations certified separately can conflict. If two four-unit local batches are each fully covered by one six-unit provider aggregate, the aggregate cannot satisfy both. Selecting a favorable assertion on arrival order hides this discrepancy. A cut can expose the conflicting capacity and a trusted correction can remove or replace an assertion. The arithmetic does not choose the more authoritative source.

Meter granularity matters. If three indivisible local charges of two units can each match either of two provider batches of three units, the flow relaxation assigns all six units of overlap by splitting one charge. Whole-item assignment can overlap at most four. More generally, take an instance of PARTITION with total 2B and make two provider batches of capacity B. Each local item may wholly agree with either batch or remain unmatched. Full overlap exists exactly when the items partition into two sets of sum B. Thus the splittability distinction changes both exactness and worst-case computational cost. Under the same constraints but with extra indivisibility, the flow interval remains an outer bound on feasible union sizes, subject to the original granularity and source assumptions.

## What a Work Unit can act on

Duplicate or cumulative reports must first be normalized into trustworthy disjoint batches, or kept in a model with explicit same-source overlap. If two allegedly distinct local records can describe the same unit, the source total itself has no direct union meaning. Account, scope, meter, and period are proof inputs, and corrected reports need a versioned consistency policy. With authenticated evidence at a fixed cut, adding a consistent coverage constraint shrinks the feasible allocation set. One can update the two endpoints without treating the least possible charge as settled or releasing an unresolved commitment on the strength of a report alone. A late charge, revised statement, overlapping cash and usage entitlements, or a new debit outside the observed set require separate obligations. [External exposure](Budgeting-for-unresolved-external-attempts.md)

**Disposition.** The argument derives exact endpoints and checkable certificates for two normalized, divisible sources and identifies when their relaxation is one-sided. It reuses the existing ledger contract rather than adding a new provider identity or settlement service. The first source-specific continuation is to document which normalizations and positive overlap claims a particular adapter can authenticate. A new replay or provider trial requires its own admission. The derivation uses the definition and residual characterization of capacitated flow. It does not report performance or verify actual provider settlement.
