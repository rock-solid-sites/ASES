---
title: Which capacity promises can disconnected Work Units honor together?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Which capacity promises can disconnected Work Units honor together?

September's two-domain reservation test shows the danger of independently claiming the last unit of a shared resource. Does every grant of capacity therefore need a shared runtime decision? For independent local promises and additive resource accounting, a verifier can decide exactly which promises fit together ahead of time. The result also identifies which refusal an isolated owner may truthfully return. [Two-domain reservation counterexample](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-Composition.md) · [Work Unit reduction, shared allocation](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md)

## Exact boundary

At disconnection, let c be committed base usage and E_i the nonempty finite set of incremental usage vectors reachable at *any prefix* of the calls owner i promises to serve locally. Include the idle vector. Components name the same physical units across owners. Each local charge/return and its promised local outcome is mediated durably. During this interval grants are fixed, remote owners receive no messages, local choices can occur independently, and global usage is c plus the sum of the local vectors. Unique charging and absence of shared mutable inputs have to be established at the chosen resource boundary. An envelope omitting a real transient peak is unsound.

The global safety region is given by explicit budget rows a with limits b_a, so a·usage ≤ b_a for each row. For each owner and each row compute h_i(a) = max over x in E_i of a·x. Then all promised local prefixes are jointly safe **if and only if**, for each row,

```text
a·c + sum_i h_i(a) ≤ b_a.
```

Sufficiency bounds every joint prefix row by row. For necessity pick a failed row. At each owner take a prefix attaining that row's maximum. Independence allows all those prefixes to occur together, giving a concrete violating tuple. Different rows may use different tuples. No common maximizer across rows is needed. With only an outer approximation to the actual E_i, passing is sufficient, while a failed row needs realizability evidence for its tuple. Resource bounds are distinct from other Work Unit policies governing which caller may access the resource.

Several consequences follow.

- A subtree of independent owners can export just the sum of their profiles for the declared rows. Regrouping the same children preserves the sum. Changing a budget coefficient or introducing a new row can require reopening the underlying envelopes. With known profiles the integration check costs O(owners × rows). Presenting a claimed maximum with one attaining prefix proves attainability only. Assurance also needs an upper bound covering *all* local prefixes.
- For one new owner, its greatest individually compatible set of usage vectors is the intersection of the residual inequalities a·x ≤ b_a − a·c − sum of all *other* owners' h_i(a). Two owners cannot independently install their respective unilateral expansions from one stale allocation snapshot. With capacity one and two initially idle-only allocations, each can independently compute one unit of room. Installing both promises recreates September's counterexample. Reallocation must conserve capacity across the whole change or establish an equivalent decomposition into exclusive rights.
- There is no fixed bound on the number of owners required to witness an unsafe set of allowances. Give n owners one unit each against a cap of n−1. Every proper subset fits and all n can exceed the cap. A single violated inequality is nevertheless a short *kind* of certificate with one local contribution per relevant owner. The two-endpoint result for ordered handovers depends on a different invariant. [Repeated-handover checker](Repeated-handover-histories.md)

## Preserving freedom of local choice

Suppose each of 32 owners may consume one unit of either resource X or Y. The shared budget is X+Y ≤ 32. Each owner has three reachable usages (idle, X, Y). Every joint history respects the bound. Taking each coordinate's independent maximum and then adding both reports 64 and can reject a safe allocation. A profile in the actual budget direction X+Y yields 32, exactly. The check represents 3^32 joint choices with 32 local maxima for that row. This counts avoided combinations and assumes the local envelopes have already been established. It gives no runtime performance measurement.

For a monotone global budget and nonnegative usage, a definitive “the global resource is exhausted for this request” needs additional observation. Suppose the owner has used nothing and has exhausted its *local allowance* of zero. Compare two silent remote histories with capacity one. In one the sole entitled peer is idle, in the other it has spent one. The same one-unit request is globally feasible in the first and infeasible in the second. A refusal reporting local allowance exhaustion is truthful in both. A refusal claiming a current global fact cannot be correct in both. Nor can an owner safely take its peer's unused unit opportunistically while promising the disconnected peer will still serve its own caller. The semantics of the reply and the durability of the other promise both matter.

Escrow-based bounded counters directly address decentralized numeric invariants. Invariant confluence gives a broader framework for reasoning about coordination and application invariants. The result here specializes the question to advertised sets of local Work Unit prefixes, explicit linear resource budgets and terminal reply meanings. It supplies no dynamic escrow transfer or consensus implementation. [Balegas et al., *Extending Eventually Consistent Cloud Databases for Enforcing Numeric Invariants*](https://arxiv.org/abs/1503.09052) · [Bailis et al., *Coordination Avoidance in Database Systems*](https://arxiv.org/abs/1402.2237)

## Reproduction and interpretation

Run `python3 docs/research/kernel-0/disconnected_allowances.py`. For three owners each with eight candidate envelopes on two binary resource coordinates, it checks all 512 ordered envelope choices against 112 cap vectors on X, Y and X+Y. The profile test agreed with Cartesian enumeration on all 57,344 cases, including 6,056 safe cases. Every failing profile produced an actual tuple violating its reported row. Independent controls exercise the 32-owner alternative-resource example and the population witness through n=19. [Executable experiment](disconnected_allowances.py)

This gives a conditional way to shift ORDER from every individual admission to allocation and reallocation boundaries. ISOLATE must protect assigned local allowances against cloning or rollback. CONNECT must bind each use to the right owner, unit and grant. Local decisions still need ordering where they spend the same allowance. Revocation during disconnection, transfer of consumable rights, correlated workloads, nonadditive resources and cross-owner observation of a single serial log require additional arguments. The result concerns adequacy for a resource contract, without selecting a kernel vocabulary or realization.
