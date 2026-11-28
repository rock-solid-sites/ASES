---
title: When can Work Unit containment express managerial authority?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Authority-in-mixed-containment-trees.md
  - docs/research/kernel-0/How-much-seal-state-survives.md
last_updated: 2026-11-28
---

# When can Work Unit containment express managerial authority?

Suppose manager A can pause writes to resources {a,b} and manager B can pause writes to {b,c}. Both pauses must persist across replacement of the executor, and releasing one pause cannot overrule the other. No tree of unique resource identities can express both scopes as one subtree each. A flat policy over the same durable resources can express both. This challenges containment as the source of authority under a precise contract, independently of earlier findings about preserving an already chosen policy during moves. [Mixed containment](Authority-in-mixed-containment-trees.md) · [Independent seal semantics](How-much-seal-state-survives.md)

## The representation test

Consider n resources, one unique leaf per authoritative identity. For every manager take the nonempty set of leaves over which it must have an independently exercisable veto. The tree-only candidate assigns exactly one node to each distinct scope, giving it authority over all that node's descendant leaves. It has no aliases, independent labels or exceptions. Identical scopes can share a node while retaining independent veto state.

**The candidate can realize exactly the laminar families.** Two subtree leaf sets are disjoint when the subtrees are incomparable and nested otherwise. For sufficiency, add the whole resource set and all singletons to the family. Connect each proper set to its smallest strict superset. All supersets of a nonempty set are nested, so the parent is unique. Each resulting node has precisely its set of singleton descendants. This is both a representation and a linear-size explanation of any rejection: two crossing scopes and a resource in each of their intersection and two differences suffice.

A pure containment arrangement can still be adequate if the actual policy is laminar or the observations do not require independent cross-cutting control. The three-leaf fixture is a discriminator for a stronger observation contract. It does not assert that current ASES policy requires these particular managers or resources.

## If each scope can use several subtrees

In a fixed tree, assign a scope the maximal subtrees entirely contained in it. Their leaves are disjoint and exhaust the scope. Any other covering subtree lies inside one of those maxima. Thus the number of maximal contained subtrees is the exact minimum number of subtree declarations for that scope. This cost counts declarations. If several declarations assert one logical veto, the realization still needs a shared authoritative state or an admissible publication protocol for changing that veto. Independent per-node changes do not automatically supply that behavior.

There is an exact small-instance solver for choosing the hierarchy itself. Put w(S) = the number of scopes containing all of leaf set S. For each nonroot node its contribution to total cover size is w(S) − w(parent). The root contributes w(root). It suffices to consider binary trees: refining a node with more than two children adds possible cover roots without invalidating any prior cover. On a binary tree, summing the differences gives

```text
total declarations = Σ w(singleton leaf) − Σ w(internal node).
V({leaf}) = 0
V(S) = w(S) + max[V(A) + V(S \ A)], for nonempty proper A ⊂ S.
```

The decomposition is exact since the subtrees meet only at S and the leaf contribution is fixed. Subset dynamic programming takes O(3^n) time after the weights are computed. It gives a baseline for testing the structural cost of a proposed placement, without claiming this cost predicts runtime or authority graph size.

Two families clarify the cost.

- If every distinct pair of leaves is a separate scope, a pair gets one declaration only if its leaves are siblings. Such pairs are disjoint. The optimum is 2·binom(n,2) − floor(n/2), achieved by building floor(n/2) sibling pairs and connecting them. This counts declarations under the positive-subtree representation.
- If the scopes are all n complements of individual leaves, the complement of leaf i has one maximal contained subtree for each sibling on i's root path in a binary tree. Its declaration count equals its depth. When n=2^h the optimum is exactly n·h. The sum of 2^(−depth) over leaves is one, so their mean depth is at least log₂ n by convexity. A perfect depth-h tree attains the bound. A uniform policy allowing manager i to veto all leaves except i instead uses one excluded identity per manager and one shared rule. This is a representational gap for this family, without a claim about every possible policy language.

## A comparison architecture

Keep stable resource identities and a protected relationship from each manager to the leaves its veto covers. Keep the current execution grant and the asserted vetoes independent. At a write's authoritative decision, check the current grant and reject if any applicable veto is asserted. When manager A withdraws its own veto, the shared resource b remains closed if B still asserts its veto. Replacing an execution changes its tenure only, preserving both vetoes and accepted work. No authoritative parent link is needed to define these behaviors. A tree can still organize the user's navigation or groups of work. The underlying policy relation needs a distinct authority to change its extent. The exact realization must serialize a write with any live grant or applicable veto change relevant to it.

This is a finite constructive compatibility witness for current scoped admission and durable continuation in one Work Unit. It leaves autonomous delegation, grant composition, changes to scope membership, authenticated role administration and atomic changes across independent effect owners unproved. It also leaves open which authority patterns the real programme needs. The comparison makes the Work Unit tree testable as an architectural choice without inferring optional kernel object types from architectural nouns.

## Executed evidence

Run `python3 docs/research/kernel-0/containment_scope_covers.py`. For all 128 families of nonempty scopes over three leaves, explicit cover minimization matched the recurrence and exactly the laminar families used one subtree per extent. For 160 reproducibly sampled families on five leaves, the recurrence agreed with direct enumeration of all 105 labelled binary trees. The pair and complement calculations agreed with the recurrence through nine leaves. A separate direct-policy history checked the two vetoes, a stale append at an otherwise unblocked resource after replacement, current-tenure continuation and the accepted content sequence. [Executable comparison](containment_scope_covers.py)
