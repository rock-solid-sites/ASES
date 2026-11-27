---
title: What authority becomes visible during a batch of Work Unit moves?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# What authority becomes visible during a batch of Work Unit moves?

A Work Unit can acquire a right in an intermediate placement even if every possible placement is a tree and both endpoint policies deny the right. In fact there are batches of n moves for which *every* nonempty proper subset widens authority. Reordering those moves cannot fix such a batch. The previous structural result guaranteed a tree-preserving serial order for every pair of valid trees. Its conclusion does not extend to policy-preserving serial orders. [Structural result](Concurrent-moves-of-sealed-Work-Units.md) · [Withdrawal-preserving relocation](Reparenting-and-surviving-withdrawals.md)

## Exact analysis without enumerating mixed trees

Use the fixed identity universe and independent old/new parent choices of the structural result. Assume their union is acyclic. During the batch each boundary v has a fixed predicate B_v for admitting one particular defined effect under the current grant context. An actionable crossing also needs an explicit local grant at the subject, held fixed. A containment path admits the effect only if every boundary on it permits it. Test possible reactivation at each intermediate cut unless the contract establishes that reactivation there is impossible. Predicates used here ignore only the temporary move seal under test. Other restrictions are preserved. A permanently sealed subject that cannot be exposed at any intermediate cut has a different contract.

Write P(v) for whether **some** mixture permits that effect through v's path. Set P(root)=B_root. In a parent-before-child traversal of the union compute

```text
P(v) = B_v AND (P(old_parent(v)) OR P(new_parent(v))).
```

An actual path establishes the corresponding disjunct inductively. Conversely, a true disjunct provides a permitted path from that parent to the root. Acyclicity ensures v is absent from the rest of the path. Each vertex on the extended path chooses exactly one of its parents, and those choices extend to a full mixture by filling the other choices arbitrarily. This proves exactness for a single subject/effect/context. Remembering the chosen true predecessor reconstructs the path and a concrete set of installations causing it. Thus to protect a retained ceiling A at v, check that its local grant together with P(v) implies A in every admitted context. With concrete policy bits the propagation takes linear work in the union size per bit. Symbolic implication across many grant contexts is an additional cost. A true path under an overapproximation of reachable placement choices needs a scheduling witness.

A bitset can represent several effects or contexts in parallel. Different true bits can come from *different* mixtures. The result is exact for a safety requirement quantified separately over effects. A single mixture simultaneously permitting several named effects needs shared placement choices across them. Claims about consumable quantities, jointly observed multi-object effects, new grants, or changing local policies require different models.

## An arbitrary lower bound on publication width

Build a path with n independent parent choices. At choice i the selector unit points either to an old filter or a new filter; both fixed filters point to the next selector. The last filter leads to the root. Thus even the union is acyclic. Give the subject a local grant for n named effects r_i and grant nothing locally to the intermediate units. All filters pass all effects except one. The old filter at i blocks r_i. The new filter at i blocks r_(i−1), subscripts modulo n. No filter's policy changes during the batch.

Effect r_i survives exactly when choice i is new and choice i+1 is old. At both endpoints no effect survives. In any nonconstant circular sequence of choices there is a new choice followed by an old one. Hence some effect survives in every mixed placement. This uses positive permits and intersection along one containment path. Negation in an authority language, multiple parents in an installed configuration, or a structurally invalid tree are unnecessary.

If a consumer can reactivate or exercise the retained grant after any visible cut, and the only available edits are the given old-to-new pointers, all n changes must become visible together to preserve the empty ceiling. There is no universal bounded batch size for this interface. The lower bound concerns *observable* change. A durable seal covering all affected subjects and recovery paths can instead hide intermediate placements; switching a versioned root can publish a prepared full configuration. Both alternatives introduce an explicit correspondence obligation and can change availability. A request to move a sealed child does not by itself prove that a later observer cannot reopen it from a partial configuration.

## Evidence

`python3 docs/research/kernel-0/mixed_placement_authority.py` compares propagation with direct evaluation on every mixture for all acyclic-union pairs of rooted trees through four nonroot units. Each subject is considered as a possible local grantee and every assignment of one permission bit to each nonroot boundary is tested. With four nonroot units, among 5,941 structurally compatible tree pairs there are 3,096 (pair, subject, permission assignment) cases permitting an effect in a mixture that both endpoints deny. With three nonroot units there are already 12. The script independently constructs the circular filter family, enumerates every subset through n=12 and checks exactly which effects survive. [Executable comparison](mixed_placement_authority.py)

The result puts a specific limit on separating the three proposed responsibilities. ISOLATE can preserve the same fixed filters and CONNECT can expose only authentic parent choices, yet independent publication can create an unauthorized path. ORDER can discharge this obligation by restricting observable cuts or by checking that every allowed cut is safe. Proving that an actual owner controls *all* routes to reactivation and that its recovered selector chooses one permissible cut remains a separate verification task.
