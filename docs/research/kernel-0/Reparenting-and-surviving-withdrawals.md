---
title: Which withdrawals must still work after a Work Unit moves?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Which withdrawals must still work after a Work Unit moves?

A sealed child moves from P to Q. Its one retained append currently passes through grant a under P. The proposed new path admits the same append through b under Q. At the instant of the move both grants are live. Both policies admit exactly the same operation, even when evaluated with the temporary move seal lifted. Later a is withdrawn while b stays live. If the issuer of a was promised continuing withdrawal power over that retained append, the move has broken the promise. If the transfer explicitly retires that dependency, the same trace can be legal.

September's T5 already shows that two sealed snapshots conceal scope widening and that a former parent need not permanently govern the child. The distinction here is which *future independently authorized withdrawals* a particular transfer promises to preserve. This is a stronger, optional interface. A transfer decision must identify the surviving dependencies before a checker can judge it. The archived Work Unit reasoning also distinguishes independent child grants from restrictions imposed by containment. The present result tests policies conditional on a local grant to perform the same defined effect. [September reduction, §6.1](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md) · [Competing direct and delegated models](../astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md)

## An exact comparison for retained effects

Fix one observable effect on one resource. Fix permanent, distinct names for the initially live grant incarnations whose withdrawals are in scope. A context X is the subset still live. Hold other policy inputs fixed, including any dependencies whose retirement was explicitly authorized. Every subset is reachable by withdrawing the complement. No new issuance occurs in this comparison. Let A(X) be the surviving ceiling derived from the pre-move policy, and B(X) the proposed effective policy after the move and reactivation. Both are monotone in liveness. Scope comparison must hold separately for every effect and affected descendant. Rights to different things with the same printed name are different effects.

For each policy keep its inclusion-minimal *supports*, the sets of live grants sufficient to enable the effect. The empty family denies everywhere. A family containing the empty support permits everywhere. The following three statements are equivalent.

1. No future withdrawal-only context allows B to exceed A.
2. Every minimal support b of B contains a minimal support a of A.
3. There is no distinguishing context obtained by keeping exactly one minimal support b of B live.

Indeed, if b contains no such a, taking X=b enables B and disables A. Conversely, whenever B(X) holds, finiteness supplies a minimal b inside X. Its contained a establishes A(X) by monotonicity. The checker only has to search the new supports against the old ones if the families are already known complete. Extracting them from a compact policy may itself be exponential. A witness b is a sufficient set to keep. Its complement need not be the *smallest* number of withdrawals exposing the difference.

A maximal repair retaining the bar on widening is A ∧ B. Its supports are the inclusion-minimal unions a ∪ b over both families. This implements both ceilings, and any policy below each is pointwise below their conjunction. A single live authenticated lineage path demonstrates an acceptance. It cannot establish that all alternative paths respect a withdrawal. A retained parent reference, a symbolic guard, or dropping the effect can be compared by this same test. Introducing an explicit widening decision changes the specification.

## Losing the ability to observe an old grant

Suppose the destination sees only live set V on a fixed visible subset of incarnations, and H ranges over hidden ones. Even an ideal destination-side decision function has only one answer per V. Its greatest safe grant under the two ceilings is

```text
D(V) = B(V) and (for every compatible H, A(V union H)).
```

Here B itself is observable. Necessity follows because D must hold under every hidden state producing that view. Sufficiency follows by substitution, making this the greatest safe policy available from that observation. If hidden withdrawals are independent and arbitrary, the empty hidden set is compatible and least. Monotonicity reduces the universal test to A(V), meaning A evaluated with all hidden grants withdrawn. On the support representation simply discard old supports requiring any hidden grant. Retain the others as alternatives. Thus loss of one observer need not seal everything. With A = (a AND h) OR c and hidden h, a surviving visible c still suffices. Treating formerly live h as eternally live silently preserves the first route after a withdrawal.

Exact decisions matching the full-information policy B ∧ A are possible precisely when it is constant on every set of full states with the same view. Otherwise one can preserve safety by reducing availability, or supply additional trusted evidence distinguishing those states. Correlated withdrawals can change the maximal safe policy. If a contract guarantees that at least one of two hidden grants stays live, their disjunction holds throughout that view even though evaluation at the empty set gives false. The universal formula still applies.

## Why testing one revocation at a time misses a defect

For any n ≥ 2, let A permit the effect if any of n initially live distinct grants survives. Let B permit it unconditionally. Every history that withdraws fewer than n distinct grants gives equal answers at every prefix. Withdrawing all n distinguishes them. Consequently there is no fixed bound on withdrawal count sufficient to test every such move. This does not require n unrelated rights, only n independent supports for a single right. Support comparison above exposes the empty new support immediately.

`python3 docs/research/kernel-0/reparent_policy.py` enumerates all 168 monotone policies on four grant incarnations and all ordered pairs. For 7,581 pairs B implies A. Of 20,643 widening pairs, 20,476 look identical with all four live. The support witness and conjunction repair agree with direct truth-table evaluation in every pair. For all policies, 16 visibility masks and 16 live subsets the reduced policy agrees with universal quantification over indistinguishable states. The script also exhausts all proper withdrawal subsets in the lower-bound family through n=11. [Executable comparison](reparent_policy.py)

**Boundary.** CONNECT must express exactly the dependencies promised for each retained effect and distinguish grant incarnations. ORDER must evaluate the policy against one coherent view at the effect point. ISOLATE must protect that view and mediate every path. The proof assumes these obligations. It excludes nonmonotone policy, quotas, new grants, concurrent relocation, joint effects across descendants and hidden correlations unless explicitly included in the model. No claim selects direct grants or autonomous delegation for all Work Units.
