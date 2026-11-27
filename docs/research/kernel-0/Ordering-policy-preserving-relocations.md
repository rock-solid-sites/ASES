---
title: How hard is it to find a safe order for Work Unit moves?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# How hard is it to find a safe order for Work Unit moves?

Suppose two endpoint configurations are safe, each proposed pointer edit costs one step, and every intermediate state can be observed. The Work Unit topology question admits a constructive order whenever both endpoints are trees. Adding fixed boundary filters makes the corresponding *admission-policy* scheduling problem NP-complete, even when every mixture is a tree and a single subject must retain an empty effect set. A useful one-sided class still admits a greedy solver and a checkable explanation when it blocks. [Structural ordering lemma](Concurrent-moves-of-sealed-Work-Units.md) · [Authority in mixed trees](Authority-in-mixed-containment-trees.md)

## Compiling forbidden placements into real boundary filters

Represent the set of already installed edits by S. A forbidden pattern (N,O) holds when every switch in N is new and every switch in O is old. Use nonempty disjoint sets N and O, so both complete endpoints avoid the pattern. Arrange the choices along the chain from the mixed-tree construction. Give one effect to each forbidden pattern. At switch i the old filter blocks this effect if i belongs to N. The new filter blocks it if i belongs to O. All other filters pass it. The effect reaches the root from the subject exactly in the forbidden pattern. Each installed configuration has one parent per unit and every boundary filter is fixed before the first edit.

This compilation realizes a conjunction of clauses on the visible edits with only a linear chain of switches and two filters per switch. The explicit permit table is polynomial in the number of switches and patterns. A candidate order is a certificate: follow the actual parent path and check the finite effect set at every prefix. For this explicit finite input, membership in NP follows immediately. This says nothing about the complexity of establishing that a real owner's filter table or containing path is complete.

## A reduction from Betweenness

Given a finite set of items and triples (a,b,c), Betweenness asks for a total order in which b lies strictly between a and c for every specified triple. Create one switch per item and two patterns per triple.

| N (must be new) | O (must be old) | What a forbidden prefix would show |
| --- | --- | --- |
| {b} | {a,c} | b occurred before both endpoints |
| {a,c} | {b} | b occurred after both endpoints |

A permutation of edits keeps both effects disabled at every prefix precisely when b lies between a and c. The same equivalence holds for all triples simultaneously. The polynomial compilation therefore reduces the NP-complete Betweenness decision problem to existence of a safe single-edit schedule. Only three choices matter to each effect. No ancestor cycle or runtime policy mutation is used. This is a lower bound on *finding* an order under a specified visibility requirement; checking a proposed order remains polynomial. Universal testing of all mixtures in the single-effect path analysis can be easier than finding one whole safe schedule for all effects. [Opatrný, *Total Ordering Problem*](https://doi.org/10.1137/0208008)

## A tractable class and its dual

When every pattern has exactly one new switch i, each pattern says “do not install i until at least one member of O has been installed.” A switch may have several such requirements. Start empty and repeatedly install any switch for which all its requirements are satisfied. Its installation cannot invalidate an already satisfied prerequisite. If a solution existed before that step, moving the chosen switch earlier and leaving the other switches in their former relative order still satisfies all prerequisites. Induction proves greedy completeness.

If the process stops early, give the remaining set R and, for each i in R, one requirement whose entire nonempty O lies in R. No element of R can be first in any successful total order, even after all outsiders are installed. This is a negative certificate independently checkable from the input. A reverse-time argument handles the opposite class in which every pattern has exactly one old switch. With the two types combined, the Betweenness construction already applies. The number of named prerequisites per condition alone is therefore a poor proxy for verification cost.

## Reproduction and implications

`python3 docs/research/kernel-0/relocation_order.py` constructs the filters, walks the installed containment path at every subset, and searches legal single-edit transitions. For four switches all 4,096 subsets of the twelve possible betweenness constraints were compared with an independent permutation oracle. Both methods admit 127 and reject 3,969. For three switches, all 512 families of single-new-switch patterns were checked against subset search. Greedy admits 121 and rejects 391, and every failure supplies the stated internally blocked set. [Executable reduction](relocation_order.py)

The result concerns direct single-edit publication. An owner that can atomically change the observable configuration, or keep every affected subject durably sealed throughout, offers a different set of transitions. The proof identifies when an untrusted scheduler can submit an inexpensive certificate and where an efficient *complete* scheduler would require an additional restriction or a complexity breakthrough. It does not impose general transactions on the kernel or establish a deployment time bound.
