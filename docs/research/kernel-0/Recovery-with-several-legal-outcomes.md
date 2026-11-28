---
title: How much recovery evidence is needed when several outcomes are legal?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/How-much-currentness-must-survive.md
  - docs/research/kernel-0/Recoverable-owner-selection.md
  - docs/research/kernel-0/Custody-at-an-admission-closed-cut.md
last_updated: 2026-11-28
---

# How much recovery evidence is needed when several outcomes are legal?

The exact currentness study assigns a fixed answer to each recoverable probe and true history. A looser contract may permit completing or abandoning an undecided attempt, or selecting one of several safe recovery paths. Pairwise agreement no longer suffices. There can be a safe answer for every pair of histories and none that works for all histories sharing a recovery view. There is an exact extension of the earlier evidence bound, and an important class where pairwise checking remains complete. [Exact-answer bound](How-much-currentness-must-survive.md) · [Cancellation option](Recoverable-owner-selection.md)

## The exact one-shot test

Let H be a finite set of possible true authoritative histories. A feasible probe p reveals the post-loss side information available to recovery. For each feasible pair (h,p) let A(h,p) be the nonempty set of terminal outcomes allowed by the contract. An outcome includes any authoritative changes or claims that the caller is entitled to observe. When successful recovery is required, unchecked refusal and indefinite waiting do not belong to A. A protected observation e(h) can distinguish histories before the decoder must choose. The choice may depend on p.

**A set S of histories can share one evidence value exactly when, for every probe, the intersection of A(h,p) over feasible h in S is nonempty.** A decoder with a shared evidence value must choose the same allowed outcome for all histories in this intersection. Conversely choose one element of every nonempty intersection and define the decoder on all reachable pairs of evidence value and probe. Pairs with no compatible history do not require an answer. This uses a trusted encoder or equivalent available observation. The bound says nothing yet about maintaining it through repeated crashes.

Make an edge for every inclusion-minimal group of histories whose outcome sets for some common feasible probe have empty intersection. This produces a hypergraph, a family of sets rather than only pairs. Its minimum coloring with no monochromatic edge is the exact minimum evidence alphabet. Every valid evidence assignment colors the hypergraph in this way. Conversely any such coloring gives feasible groups and hence a decoder. Single-valued allowed sets recover the earlier ordinary conflict graph. A probe with incompatible singleton history would make the original contract impossible even with full evidence and has been excluded here. [Zero-error side information for exact decoding, Witsenhausen](https://ieeexplore.ieee.org/document/1055607/)

There is no universal fixed number of compatible histories sufficient to validate a group. For n candidate decisions, let history i prohibit decision i and permit every other decision, all under the same probe. Any proper subset of histories shares at least one decision. All n prohibit every choice. At n=3 this defeats pair checks. In the other direction, the edge model has no hidden representational restriction: to realize a chosen finite family of minimal edges, introduce a different probe for every edge, feasible exactly on that edge. For a probe of edge E use E's members as decision labels and let history i prohibit label i. This introduces that edge without adding any proper subgroup conflict for that probe.

For one common probe, the optimization is exactly a set-cover problem on histories: each outcome covers the histories allowing it. Any evidence partition of size k decodes to at most k outcomes, which cover H. From a cover by k outcomes, encode each history by one covering outcome and use that outcome directly. This observation explains why explicit recovery policy alternatives can make the one-shot question computationally costly even before state maintenance or message protocols matter.

## When pairs are enough

Suppose the promised output is the set K of requests the owner will preserve. History h requires keeping every request in Lₕ and permits keeping only requests in Uₕ, with Lₕ⊆Uₕ. Within those limits individual choices are independent. For a common probe, any group S can share an answer exactly when

```text
union(Lₕ for h in S) ⊆ intersection(Uₕ for h in S).
```

If it holds, the union itself works. If it fails, a request belongs to Lₐ and is excluded by Uᵦ for some two histories a and b, so those two already have no common answer. This covers a recovery contract with independent mandatory preserve, mandatory retire and explicitly optional classifications. The same endpoint argument works for intervals of admissible recovery cut ranks on one established chain, by comparing the greatest lower bound in the family with the least upper bound. The independent form is load-bearing. A constraint such as selecting exactly one repair route can yield the n-way example even though each route choice alone appears harmless. The interval case is the one-dimensional instance of the general Helly distinction between pairwise and higher-order intersection. [Danzer, Grünbaum and Klee, *Helly's Theorem and Its Relatives*](https://users.fmf.uni-lj.si/lavric/Danzer%2C%20Gruenbaum%2C%20Klee%20-%20Helly%27s%20theorem%20and%20its%20relatives.pdf)

There is a related error when the recovery result has two components. A controller might choose an independently safe gate disposition and an independently safe custody plan from the marginal projections of its possible worlds. Those choices need not form a safe pair. For example one hidden history allows precisely matching binary choices and another allows only mismatching choices. Both components can independently choose either value in each history, yet no joint pair works for both. Factoring robust feasibility into two independent checks is valid if the joint allowed set is actually the product of those two constraints in every compatible history. Otherwise certify a joint outcome, such as custody for the exact cut named by the chosen fence.

## Effect on the native frontier

If the native contract allows abandoning some effectless reservations, reconstructing the exact transient reservation set can be unnecessary. A proof must still identify which outcomes remain legal for **all** compatible histories, including escaped old effects, accepted request keys and outstanding charge. Durable evidence sufficient to recover all settled outcomes can be insufficient for a joint prospective recovery plan whose prerequisites couple scopes. Conversely a uniformly safe cancellation outcome would collapse distinctions that an exact-history contract requires. Apply this test to the recovery policy before choosing its authority record or proposing a replay. Native implementation, continued online evidence maintenance and a successful proof of closure for its eventless reservations remain open.
