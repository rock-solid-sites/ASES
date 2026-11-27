---
title: When can sealed Work Units change parents independently?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# When can sealed Work Units change parents independently?

Let A and B be children of the root, and C a child of B. Three approved moves would place A under C, B under A, and C under the root. Each move in isolation leaves a tree, and the full destination is a tree. Apply only the first two and the parent pointers form A→C→B→A. No move edited another mover's parent field. A recovered mix of individually genuine parent records can have the same defect.

The September reduction requires a current well-founded containing path and a whole, non-widening move. Here we isolate one part of that requirement. Which *sets* of already specified moves can become visible independently while preserving well-founded containment? This is a structural check. The [withdrawal-preserving policy check](Reparenting-and-surviving-withdrawals.md) addresses a different condition on what a surviving placement may authorize. [September Work Unit reduction](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md)

## An exact criterion for all intermediate placements

Use a finite universe of durable Work Unit identities and a fixed root (a virtual root can represent several top-level units). Initially every other unit has exactly one parent and reaches the root. A batch offers at most one new parent per moved unit. All endpoints exist and the full target also reaches the root. Each local installation changes one pointer atomically and the choices of which installations are visible are independent. There are no simultaneous creates, deletes, or other topology changes.

Form the directed union of every old and proposed child→parent edge, treating the root as terminal. **Every mixture is well founded exactly when this union is acyclic.** Every mixed graph is a subgraph of the union. Conversely, on a simple directed cycle in the union choose its one outgoing edge at each cycle vertex. Distinct vertices choose independently. Keep all other units anywhere permitted. That mixture realizes the cycle. Finiteness and existing endpoints ensure that the absence of a cycle takes each unit to the root. A ranking decreasing along every union edge is a reusable certificate allowing the tested moves in any order. It remains valid for the specific edge sets and ranks checked.

Only changed sources can create new cycles. From each old or proposed parent of a changed source, follow the unique unchanged-parent chain to the first changed source or root. Replace that path by one edge. The resulting graph has at most k+1 vertices and 2k outgoing choices in total for k changed sources. Contracting a union cycle produces a closed walk here; expanding a compressed closed walk produces a closed walk in the union. Either closed walk contains a directed cycle. Memoizing common unchanged tails avoids repeated parent queries. Establishing those tails still requires a trusted common topology. In particular, treating an unverified missing parent as root can falsely prove safety. The tiny checker uses repeated topological elimination for readability; ordinary linear-time cycle detection also applies.

## What ordering buys when the union fails

For a given cycle C in the union, let N be its edges available only in the new configuration and O those available only in the old one, identifying each by its child. Common edges need no choice. Both N and O are nonempty since both endpoint configurations are trees. A prefix installing the subset S realizes C exactly if N is contained in S and S is disjoint from O. Thus a serial schedule has to break at least one old-only edge before the last required new-only edge is installed. There can be many cycles, and a certified schedule can avoid enumerating them.

**Constructive scheduling lemma.** If both endpoints are rooted trees, installing moved pointers in order of increasing *final* depth always keeps a tree. When installing v→p, every changed pointer along p's final path to the root is already installed. Unchanged pointers along it agree with their final values. That path excludes v. Therefore the new edge cannot make a cycle. This supplies at least one valid serial realization for any legal finite target. It also permits a move that would be invalid at the initial cut once its intended parent has been moved. If the consumer promises an indivisible batch observation, or retained grants and resource dispositions depend on the intermediate ancestors, this structural schedule alone is insufficient.

**No constant test width.** Start with units 1 through n immediately below the root and a bridge child of 1. Move each i<n under i+1, move n under the bridge, and move the bridge under the root. A mixed placement is cyclic exactly when all the first n moves take effect and the bridge move has not. Every batch with fewer than n applied moves, the source tree, and the full target tree all pass. A system can therefore pass every bounded-width mixture test and still violate containment. The union check exposes the full cycle directly. This family uses genuine parent moves on an otherwise fixed universe.

## Evidence and adequacy

`python3 docs/research/kernel-0/concurrent_reparenting.py` generates all pairs of rooted labelled trees on the same fixed root and one through four other units. It checks every mixed placement by following its parent pointers, compares against cycle elimination on the compressed graph, and executes the constructive serial schedule for every pair. Among 15,625 endpoint pairs with four nonroot units, 5,941 permitted every mixture and 9,684 had a cyclic mixture. Of those failures, 780 passed every single-move check as well as both endpoint checks. The corresponding three-unit counts were 142, 114 and 6. A separate control checks every subset in the long-cycle family through nine required new edges. [Executable comparison](concurrent_reparenting.py)

This distinguishes independent publication, ordered publication, and indivisible batch visibility in one Work Unit operation. ISOLATE must preserve identity and prevent topology edits outside the certified set. CONNECT must distinguish containment from grant, management and other links. ORDER may rely on a certified compatible batch for this invariant, or preserve dependencies of a safe schedule. The proof does not decide which of those visibility contracts the architecture promises. A real move also owes authorization, preservation of descendant restrictions and continued confinement of accepted contents.
