---
title: How much currentness evidence must survive a Work Unit rollback?
version: 0.2.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# How much currentness evidence must survive a Work Unit rollback?

Suppose two Work Units have each made zero or one protected update. There are four current version vectors. Validating a whole offered image can require only three trusted stamp values: keep the sum of the two current versions outside the rollback domain. If each offered version is authentic and no later than its actual current version, equality of the sum forces equality of both components. But if either Work Unit must be recovered *alone*, while the other version cannot be read, every one of the four vectors needs a different trusted value. The recovery interface changes the minimum amount of trustworthy information, even though the possible states and losses are identical. [September currentness impossibility, §5](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md)

## A general lower bound with side information

Let y be the true current state, x the recovery probe (including scope and candidate image), and R the feasible pairs (y,x). A decoder sees x and an external stamp e(y). It must produce a specified verdict for **every** feasible pair, including accepting a current candidate. Join two distinct states y,z by an edge when the same probe is feasible for both and calls for different verdicts. The minimum number of external stamp values is exactly the chromatic number of this graph. An equal stamp on an edge leaves indistinguishable inputs with incompatible answers. Conversely a proper coloring lets the decoder return the common verdict of every feasible state of that color for the observed x. Values on impossible inputs are outside the stated failure contract.

This is a one-shot zero-error side-information argument. It gives both proof techniques: a clique supplies a lower bound, and a proper coloring supplies a sufficient encoding. No cryptography or universal global ledger follows. If only safety is required and recovery may always refuse, the lower bound for exact validation no longer applies. [Witsenhausen, *The zero-error side information problem and chromatic numbers*](https://doi.org/10.1109/TIT.1976.1055607)

## Exact cost of whole, local and grouped validation

There are n components. A current version y_i ranges from 0 through k_i; every joint vector is possible. Each increment distinguishes an authoritative version, names are unique within the scope, and an offered version x_i is known to satisfy x_i≤y_i. Same-version divergent branches are excluded. The recovery observation asks whether all presented versions are current, without reconstructing the missing bytes. A fixed partition divides components into independently recoverable blocks. A probe supplies exactly one entire block, and the stamp may be shared across all blocks.

**The minimum stamp alphabet size is the product, over blocks B, of (1 + sum of k_i for i in B).**

For the upper bound store one total per block. Within B, nonnegative differences y_i−x_i sum to zero precisely when every difference is zero. For a matching lower bound select in each block a chain starting with all zeros and increasing a single coordinate by one until all coordinates reach their maxima. It has exactly the indicated number of elements. Take the Cartesian product of these chains across blocks. Any two distinct selected states differ in some block and those block projections are comparable in its chain. Probe that block with the smaller projection. The same candidate is feasible in both states, current in one and stale in the other. The product is therefore a clique of exactly the upper-bound size.

Consequently an all-component check needs 1+sum k_i values; independent singleton checks need the full product of (1+k_i) values. Four independently versioned components with bounds two need nine values for whole-cut validation and 81 for singleton validation. Two blocks of two need 25. These count values representable outside the failure projection, not database rows or simultaneous network round trips. An implementation may instead obtain trusted observations from other current holders, which changes what is included in the probe.

**Countercontract.** If any authentic whole vector can be substituted against any current vector, the conflict graph is complete. Probe one of each pair of distinct candidates and the verdicts differ. In particular (1,0) and (0,1) collide under summation. Authenticity of component labels alone does not establish the earlier-version premise; that needs trusted lineage, scope and fork assumptions. If histories differing in version are equivalent under all promised future observations, requiring version equality may itself be too strong. [Future-observable seal equivalence](How-much-seal-state-survives.md)

## Cross-check and trusted boundary

`python3 docs/research/kernel-0/recovery_anchor.py` constructs conflicts by enumerating *observable probes and verdicts*, independently of the chain proof. For every partition it checks that the proposed coloring separates every conflict, the chain-product clique contains every required edge, and both certificates have the predicted cardinality. It covers version bounds (1,1), (1,2,3), (1,1,1,1) and (2,2,2,2), with 37 partition instances. The full-substitution control separately produces a complete graph for each whole-vector case. [Executable certificates](recovery_anchor.py)

The theorem minimizes a trusted *observation alphabet*. It assumes the authoritative stamp actually tracks acknowledged changes across loss, is bound to the correct scope and is checked coherently with enabling service. Keeping one sum synchronized with independent commits can be more expensive than storing more per-owner metadata. A checksum of recovered data that rolls back with the candidate provides no such witness. Unbounded increments, bounded rollback distance, and partial recovery with correlated versions require their own confusability relations. Admission control, preservation of accepted content and escaped votes remain separate obligations. [Gate recovery model](Recovering-a-gate-with-votes-in-flight.md)

## Nested and overlapping recovery scopes

The partition theorem can be extended to two materially different recovery interfaces. Keep exact acceptance, independent version ranges and authentic coordinatewise-ancestral candidates. A query now selects one of an explicitly allowed family of scopes. Two states conflict precisely when their projections onto some allowed scope are unequal and componentwise comparable. In that case the smaller projection supplies the decisive shared probe. If two unequal projections are incomparable, neither current projection is a feasible old candidate at the other state, so that scope alone cannot distinguish them.

**Nested scopes.** Suppose the family covers the coordinates and is laminar: any two scopes are disjoint or one contains the other. For each scope take its residue after removing all its proper subscopes. Ignore empty residues. They partition the coordinates. Store one total for each residue. Any permitted scope is a union of residues, so its total is available without presenting its children separately. The partition formula applied to these residues is again the *exact* alphabet size, even when the residues themselves are not permitted queries. For the lower bound use the same product of residue chains. For two distinct selected states choose an inclusion-minimal scope whose own residue differs. Within its proper subscopes the projections are equal by minimality, while its own residue projections are comparable along their chain. Probing that entire scope distinguishes the states. Components that occur in no permitted scope are irrelevant for this verdict.

**Pair scopes.** Now let the only permitted scopes be the edges of a connected undirected graph on n≥2 components, with positive version bounds k_i. Put V=product of (k_i+1), the number of version vectors. The minimum stamp alphabet is

| Permitted pair graph | Minimum stamp values |
| --- | ---: |
| Contains an odd cycle | V |
| Bipartite | V − product of k_i |

For two distinct states to share a stamp, each queried edge must see either equal versions at both ends or changes in opposite strict directions. Starting from any changed vertex, every neighbor must change in the opposite direction. Connectivity propagates this sign throughout the graph. An odd cycle makes such a pair impossible; every pair of distinct versions conflicts.

For a bipartite graph choose sides and transform the version coordinates to z_i=y_i on one side and z_i=k_i−y_i on the other. Two distinct vectors can share a stamp exactly when all transformed coordinates strictly increase together in one direction. Color by z minus its minimum coordinate in every position: each color is a diagonal chain. Its starting vector has at least one zero, and every such starting vector occurs. Their count is V minus the number of vectors with all coordinates positive, namely V−product of k_i. Any two distinct zero-containing vectors are incompatible with simultaneous strict increase in either direction. They form a clique of this same size. A decoder can derive each queried pair's true version sum from the difference of its transformed coordinates and the known bound on the flipped endpoint. This gives a concrete verifier in addition to the coloring argument. For disconnected components each with at least one pair query, independent component colors give a product upper bound and independent component cliques give the matching lower bound.

A three-component example shows why storing every scope sum is not always optimal. Allow {A,B}, {A,C} and {A,B,C}, with binary versions. The two pair queries alone require seven colors: their graph is a bipartite star. The only merged states are (1,0,0) and (0,1,1). Their whole projections remain incomparable, so adding the whole query leaves seven sufficient. But the three numerical sums distinguish all eight states. A verifier can validate the whole probe without preserving its exact true sum. Similarly, in the odd-cycle case a publicly readable exact global stamp distinguishes every global version vector even if one caller may recover only a pair. An isolated verification service could keep that stamp internal. Confidentiality of update activity is an additional observation contract. [Cross-scope observation experiment](What-a-receipt-reveals.md)

`python3 docs/research/kernel-0/overlapping_recovery_scopes.py` independently builds the probe/verdict conflict graph and checks matched coloring and clique certificates. It covers all 45 laminar covering families on three components with bounds (1,2,1), all four connected labelled pair graphs on three components with bounds (1,2,3), and all 38 connected labelled pair graphs on four components with bounds (2,2,2,2). Half of the four-component graphs contain an odd cycle and require 81 values; the other half require 65. The pair-plus-whole example checks the seven-value optimum directly. [Executable certificates](overlapping_recovery_scopes.py)

These results use stable component identities and the exact set of permitted probes. Moving a Work Unit to a new recovery group can change the minimum currentness evidence, even when all component data remains unchanged. General overlapping hyperedges, changing scope membership and the cost of updating a crash-consistent external stamp remain open.
