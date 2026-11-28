---
title: What capacity must a Work Unit hold for unresolved external attempts?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Disconnected-resource-allowances.md
  - docs/research/kernel-0/Transferring-and-reclaiming-resource-allowances.md
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
last_updated: 2026-11-28
---

# What capacity must a Work Unit hold for unresolved external attempts?

Three timed-out dispatches can describe one logical request but remain three potentially billable attempts. Their common ID reduces exposure only if the downstream effect owner actually guarantees deduplication for the relevant scope and period. Conversely, counting all pending arms separately can needlessly block admission when independently checkable evidence excludes simultaneous charge. This question is about the safest usable upper bound under uncertainty, separate from reporting exact settled usage. [Resource Solver reconciliation](../Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) · [Original external-effect profile](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-External-Effects.md)

## Exact admission with a known exposure set

Fix one budget row, with limit C and known settled charge S. Separate amounts still possible from the settled amounts to avoid double counting. Let pending physical attempts have enforceable nonnegative exposure bounds wᵢ. Let E be the family of sets of pending attempts that can still contribute at the protected decision. Assume that for each set in E, all its fees can jointly attain their stated bounds or approach them arbitrarily closely. Assume a newly accepted commitment can add charge x independently of those possible old charges.

With these assumptions safe exact admission is possible if and only if

```text
S + x + max { sum(wᵢ for i in A) | A in E } ≤ C.
```

This follows by bounding every possible charge for sufficiency. If the bound is exceeded, use a maximizing set and jointly realizing history for necessity. A maximizer for one budget row need not maximize another. Multiple rows can be checked separately under this same realization premise on each row, with the use decision binding the complete vector of charges coherently. When per-attempt maxima cannot occur together, the exact input is instead the joint set of attainable charge vectors. Summing an impossible set of independent maxima gives a conservative bound or a spurious counterexample. An interval on final liability must include any live liability that can materialize after dispatch, regardless of whether a report is currently available. [Independent envelopes](Disconnected-resource-allowances.md)

No component can guarantee a real money or capacity cap against an effect owner allowed to charge without an enforceable bound. Recording an overrun and restricting later commitments may still be necessary. Those controls implement a different promise from bounding every realized external effect. A protected Work Unit hold says what was authorized and reserved. It does not itself constrain a provider.

## What verified exclusion buys

A partition into independent groups with an actual at-most-one effect contract within each group gives an exact sum of group maxima. For example three alternatives with charges 4, 6 and 7 require a hold of 7 if only one can be applied, or 17 if all can occur. To credit the smaller hold, bind the proof to downstream scope, actual account/meter contract, operation and durable deduplication lifetime. Equal local logical IDs, an SDK retry setting, and a timed-out response establish none of those facts on their own. Exact logical replay can still establish a stable user response while the physical outcome accounting remains unresolved.

More generally make a graph joining attempts when trustworthy evidence says they cannot both charge. If every independent set is attainable and each can attain its member bounds jointly, exact exposure is the maximum weight of an independent set. This also exhibits NP-hardness for an unrestricted supplied compatibility graph, without any scheduling complexity. If not every independent set is attainable, the graph remains a conservative relaxation. For example if any two of three attempts may charge, but all three cannot, pairwise evidence alone misses the higher-order limit.

For a cheap upper certificate, cover the attempts by cliques of this incompatibility graph. Sum the maximum weight in each clique. Each reachable set contributes at most one per clique, so the bound is sound, even if overlaps overcount. A partition makes accounting simpler. A lower certificate is an actual compatible history with observed or provably reachable charges, not a selected graph independent set absent the attainability proof. Where its cost is justified, tighter checking should be compared with the amount of useful admission it unlocks. These are model bounds, not measured scheduler performance.

## Clearing a hold is a consequential decision

An unreachable downstream owner leaves two possible histories after dispatch. One has no effect. The other has an effect whose reply was lost or whose charge is delayed. A local timeout or old worker's exit cannot by itself remove the second history. Before freeing capacity, use a trusted terminal observation covering the attempt's exact effect and charge, or an irrevocable exclusion plus complete prior outcome evidence. A cancellation receipt that only blocks future starts does not eliminate the already-started charge. A proof that usage cannot be billed may come from a different authority than process termination.

An older resource-control example already preserves both local cost and delayed reported totals when report coverage is unknown. Exposure can fall when trusted evidence establishes overlap or settles the exact bill. Keep authorization, observed settlement and the safe upper bound separately typed, so a conservative bound cannot be reported as an observed charge. A scheme can also learn enough to reduce one meter while another remains unresolved. Scope and period constraints are part of the computation. [Provider metering reconciliation](../Provider%20Registry%20Control%20Plane%20and%20Usage%20Reconciliation%202026-11-01.md) · [Allowance reclaim evidence](Transferring-and-reclaiming-resource-allowances.md)

**Disposition.** Reuse the earlier bounded accounting evidence for observed-versus-reserved distinctions. This argument supplies a conditional structural rule for uncertain external attempts, with an explanatory witness when a declared budget could be exceeded. Determining a real effect owner's exclusion and exposure envelope remains an integration obligation. An actual-provider or new synthetic accounting matrix would require its own admission. This research makes no external call or empirical cost claim.
