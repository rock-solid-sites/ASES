---
title: When do authorized resource conversions conserve capacity?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Transferring-and-reclaiming-resource-allowances.md
  - docs/research/kernel-0/Budgeting-for-unresolved-external-attempts.md
  - docs/research/kernel-0/When-separate-checks-prove-one-legal-effect.md
last_updated: 2026-11-28
---

# When do authorized resource conversions conserve capacity?

Perfect isolation and ordering can still serially admit a set of resource conversions that creates capacity. Consider two conversion rules, one of which consumes one A to issue two B while the other consumes one B to issue one A. Starting with one A, those two authorized steps return the A and leave an extra B. There is no concurrent double spend in this example. Conservation is a separate property of the whole conversion policy. This matters when a Work Unit can reshape, split or reclaim rights measured in different units. [Transfer conservation for one declared resource](Transferring-and-reclaiming-resource-allowances.md)

## Exact existence criterion for this accounting certificate

Fix a finite list of resource types and a finite list of normalized conversion rules. Each rule atomically consumes a fixed nonnegative integer vector and produces another such vector. Let column dⱼ be produced minus consumed for rule j and let D contain those columns. Include every affected balance in the observation, including outstanding and quarantined credits if those can be redeemed. An independent authorized funding event can raise the starting bound and needs its own source and accounting.

A positive linear measure w proves a common upper capacity bound if wᵢ > 0 for every protected balance and dⱼ·w ≤ 0 for every conversion. Its total cannot increase along any finite sequence. In a nonnegative state whose initial weighted total was M, balance i is at most M/wᵢ. Strict positivity matters: a nonnegative measure that assigns zero to a mintable balance can hide unlimited growth in that balance. For lossless conversion a stronger requirement is dⱼ·w = 0. Here a transition may dispose of capacity.

For a finite rule matrix, such a positive nonincreasing measure exists exactly when there is **no nonnegative mixture of conversions whose total net change is componentwise nonnegative and nonzero**. One direction follows by taking the dot product with w. For the other, normalize w so that w ≥ 1 componentwise, write w = 1 + u, and solve

```
Dᵀu + z = −Dᵀ1,    u ≥ 0, z ≥ 0.
```

If this is infeasible, Farkas' alternative gives y with y ≥ 0, Dy ≥ 0, and −1ᵀDy < 0. Thus Dy is a nonzero gain vector. Conversely such y certifies that no positive linear measure meets the rules. For rational rule data the feasible systems can use rational witnesses. Scaling a rational y gives integer rule multiplicities. A weight vector or rule multiset is a compact, independently checkable output. [Farkas' alternative in equality form](https://people.csail.mit.edu/moitra/docs/6854lec11.pdf)

With the legitimate conversions A→2B and 2B→A, w=(2,1) gives lossless conversion. If the second rule is B→A instead, one use of each produces the witness Dy=(0,1). This is an algebraic discriminator for the actual unit and route map. Per-rule authority and an exact history of admissions supply different evidence.

## When the negative certificate predicts reachable growth

With no enabling condition beyond having enough inputs, any finite multiset of rules may be taken in any chosen order from a sufficiently large finite starting marking. For example a marking large enough to cover the sum of their input vectors suffices. If the sequence produces a componentwise nonnegative net gain, it can run again from its final marking and produce the same gain. This is a real counterhistory for sufficiently provisioned instances of the simple model.

It need not give a reachable counterhistory from a particular bounded genesis, under an additional live policy or when the listed rules cannot all be compatible in one configuration. Carry those guards in a reachable-state proof. A positive measure still bounds any execution whose actual effects correspond to the covered rules. Failing to find such a measure rules out this kind of certificate for that rule family. It does not rule out a different invariant, fixed-genesis bound, or stronger enabling policy.

The aggregate certificate also leaves a separate identity obligation. Suppose two one-unit balances are supposed to be backed by two distinct physical slots. Both balances can instead name the same slot, leaving the second slot unused. The count and weighted total remain unchanged, yet the ledger cannot give both holders the independently promised use. Where identity or extent matters, prove unique backing, check disjointness, or model the independently protected extents explicitly. A count invariant alone cannot prove it.

Further, a recovered ledger can omit an unobserved external charge or double represent a restored credit. A positive measure over planned or reported values says nothing about those effects unless issuance, consumption and redemption match the represented vector atomically at the relevant boundaries. Non-fungible real limits still need their own enforced rows. Choosing weights for a proof does not make cash, subscription credits and concurrent slots economically interchangeable. [Unresolved physical exposure](Budgeting-for-unresolved-external-attempts.md)

**Disposition.** A proposed primitive basis can encode conservation by constraining transitions and genesis. A sufficiency claim for a concrete resource profile still needs that invariant and the complete physical correspondence. The two possible certificates give a low-cost discriminating design check for a declared conversion policy. This argument is deductive and makes no experiment, real accounting or architectural adoption claim.
