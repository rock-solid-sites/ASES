---
title: How much shared headroom can a Work Unit keep private?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Disconnected-resource-allowances.md
  - docs/research/kernel-0/What-a-receipt-reveals.md
related_documents:
  - docs/research/kernel-0/How-much-currentness-must-survive.md
last_updated: 2026-11-28
---

# How much shared headroom can a Work Unit keep private?

The same authorized request can receive different terminal replies solely because another Work Unit has occupied a shared resource. This holds with one correct serial owner, scope-relative receipts and no observable timing. An isolation contract that conceals the other unit's usage must qualify the admission guarantee itself. The disconnected-allowance result assumes independent choices from fixed envelopes. Here the owner may see exact global usage and communicate with every participant. The question is what it can safely promise while making only a specified amount of that usage observable. [Disconnected allowances](Disconnected-resource-allowances.md) · [Scoped receipt experiment](What-a-receipt-reveals.md)

## Exact admissions disclose frozen headroom

Fix integer capacity C and a caller P with no initial usage. Another scope holds h units, leaving r = C − h, and keeps its usage unchanged throughout the observation. P may request a positive integer amount. Safe admission forbids granting more than r. Exact admission requires a completed success whenever the otherwise eligible request fits. For two possible residuals r < s, the request for r+1 must fail at r and succeed at s. Returning a generic failure code, using a dispatcher, or placing the resource behind an independent owner cannot equalize these terminal outcomes. With guaranteed release or a read-only feasibility query, adaptive threshold queries recover r in at most ceil(log2(C+1)) replies. A different observer issuing one-unit allocations without releasing can recover r by counting successes until the first failure, or stopping after C successes. These arguments fix P's other grants and inputs, require completed outcomes, and use quiescent hidden usage. The one-request distinction does not need release, adaptivity, or a measurement of response time.

This is a resource-policy conflict, independent of the mechanism that enforces the bound. A Work Unit may instead receive an explicit local allowance, or the contract may allow a chosen public disclosure of shared headroom. Completion is load-bearing here. A permanent wait can conceal the answer by withholding service, while a distinguishable timeout adds an observation to the contract. The distinctions concern what P learns about the total hidden usage. Identifying which other Work Unit consumed it needs more information. [Clarkson and Schneider, *Hyperproperties*](https://www.cs.cornell.edu/fbs/publications/Hyperproperties.pdf)

## Tight disclosure for bounded underuse

Let H be a finite set of possible remaining capacity vectors in nonnegative integers, for separately bounded resource dimensions. The values in H may be correlated. Fix an integer tolerance vector Δ ≥ 0. At an allocation boundary an authorized policy publishes a signal. The signal promises an allowance q. P may subsequently use and return any vector bounded coordinatewise by q, with completed replies depending on P's own charges and the public allowance. The policy must keep q backed throughout this interval. For example, the other units' uses can remain fixed, or a conserving reservation can prevent later consumption of P's promised allowance. Require for every possible r that q ≤ r and r − q ≤ Δ, both coordinatewise. The first inequality is safe and the second bounds forgone headroom.

For a set S of residual vectors mapped to one observable signal, there is a common allowance **exactly when**

```text
max(r_i over S) − min(r_i over S) ≤ Δ_i   for every resource i.
```

For necessity, all r ∈ S require r_i − Δ_i ≤ q_i ≤ r_i. For sufficiency choose q_i = min(r_i over S). A reservation of q can then be managed by the scope under a local charge invariant, and hidden changes that preserve the backing and public signal need not affect its completed replies. Conditions on the backing are separate from the algebraic existence of q.

**Exact finite optimization.** Make a graph on H joining two vectors if some coordinate differs by more than its tolerance. A signal's preimage must be independent. A proper coloring conversely supplies common allowances by taking the coordinate minima of each color class. The minimum number of possible public signal values is therefore the chromatic number. Equivalently it is the smallest number of integer boxes [q, q+Δ] covering H. The condition is pairwise because each coordinate's extrema are attained by two members of S. This bound assumes deterministic, zero-error outcomes at the stated allocation boundary. It counts distinct signal values and gives a fixed-length encoding bound in bits. It does not measure distribution-dependent or repeated disclosure. Distinct colors that induce an identical q can be merged, so encoding separate hidden distinctions with equal allowances is unnecessary.

**Independent ranges.** If H = ∏ᵢ {0,…,Cᵢ}, the exact alphabet size is ∏ᵢ ceil((Cᵢ+1)/(Δᵢ+1)). For an upper bound publish coordinatewise rounded-down multiples of Δᵢ+1. For a lower bound take all grid points on those multiples. Every pair differs by at least Δᵢ+1 in some coordinate, so this grid is a clique of exactly the claimed size. With scalar capacity 15, exact fitting requires 16 distinct signals, tolerance three requires four, and hiding all headroom requires accepting a worst-case slack of 15 in an unreserved pool. A prior exclusive reservation changes H. For a correlated example, H = {(0,0),(1,1),(2,2)} with Δ=(1,1) needs two signals, whereas the enclosing independent box needs four. This does not extend the disconnected-allowance theorem to resource substitutions or arbitrary coupled admission rules. [Related observation-alphabet method](How-much-currentness-must-survive.md)

## Architectural consequences and checks

- Sharing resource capacity across branches of the Work Unit tree does not by itself define what a caller may learn about the other branches. Per-scope receipts and protected data addresses can coexist with this channel. A scope boundary can hide raw charges and expose a coarser backed allowance, with a checkable bound on forgone capacity.
- A shared allocator may still redistribute unspent capacity at deliberate allocation boundaries. An implementation must either publish allowed differences there or preserve the caller-visible allowance. A quota that quietly borrows against hidden free units with exact acceptance has reintroduced the distinguishing reply. Escrow is a mechanism for protecting promises about available rights. The disclosure rule needs its own specification. [Balegas et al., *Extending Eventually Consistent Cloud Databases for Enforcing Numeric Invariants*](https://arxiv.org/abs/1503.09052)
- An adequacy test can fix caller inputs and public allocations, vary only another scope's usage, then compare terminal transcripts. Separately vary the public signal and test that promised local charges remain backed and meet the tolerance. A safe but always-refusing owner fails the second check whenever the promise is positive.

Run `python3 docs/research/kernel-0/capacity_disclosure.py`. Independently computed conflict-graph colorings and feasible allowance covers agreed on all 4,599 instances formed from the nonempty subsets of a 3×3 residual grid and tolerances zero, one and two per dimension. The script also checked 81 full-grid formula instances and recovered the residual in all 8,385 scalar threshold cases with capacities up to 128. [Executable experiment](capacity_disclosure.py) This is a research model. Implementation conformance, scheduling and timing, random or probabilistic disclosure, dynamic renewal, and composition of repeated public signals remain open.
