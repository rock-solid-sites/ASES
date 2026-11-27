---
title: How much independent seal state must a Work Unit retain?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# How much independent seal state must a Work Unit retain?

A parent restricts outward activity and a child separately suspends the same effect. Both histories can appear simply “sealed.” Now release the parent's restriction. Whether the effect can proceed depends on whether the child's restriction was also present. Does this require retaining every reason for sealing? For a fixed interface the exact answer depends on **which authorized releases can distinguish the reasons in future**. A current eligibility bit can be too small; one durable record per syntactic reason can also be redundant.

The Work Unit reduction distinguishes an independently restricted child, ancestor bounds and explicit management authority. It also permits replacing a data representation if all required future permission and continuity observations survive. Here one effect, its local grant, its identity, its bytes and all other eligibility conditions are fixed. Each asserted veto blocks the effect. The result concerns part of the state required for management of that effect. [Work Unit reduction, §§2–4](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md) · [Which observations survive a move?](Reparenting-and-surviving-withdrawals.md)

## Interface and exact quotient

There are n independently assertable veto causes. Management commands have authenticated authority established outside this model. Assert(i) idempotently sets cause i. Each available release command g clears its fixed subset of causes, regardless of which other causes are present. All these commands acknowledge identically. A query permits the effect exactly when there are no outstanding causes. Repeated assertions, releases and queries are allowed in any order. The subject cannot change its own restrictions by asserting that a manager approved.

For each cause i let E_i be the set of release commands that can clear it. For a current veto set Z form the inclusion-minimal distinct sets among {E_i : i in Z}. Call that antichain M(Z). The empty antichain means no veto. A family containing the empty set reduces to the single empty clause and means a veto no available command can clear.

**Theorem.** Two states yield the same complete future query and acknowledgment behavior exactly when they have the same antichain.

- After a sequence of releases with command set H, the initial vetoes have all cleared exactly when H intersects every E_i in Z. A smaller clause subsumes a larger one. Assert(i) on the summary adds E_i and minimizes again. Release(g) deletes every clause containing g. This operation needs no reconstruction of discarded supersets: if a smaller clause is removed, so are all its supersets; if it remains, those supersets remain redundant. The summary therefore reproduces every interleaving, including new assertions.
- If two minimal families differ, in one direction there is a clause e on the first side containing no clause of the second. Otherwise each family's upward closure would contain the other, giving the same minimal elements. Issue all releases outside e and then query. The first state retains e. Every clause on the second side meets the issued set, so that state permits the effect. The argument includes the two empty cases. This constructs a distinguishing continuation without trusting a state-minimization routine.

Since every veto subset is reachable by assertions, the exact minimum number of deterministic observable states is the number of antichains of the distinct signatures E_i ordered by inclusion. Each antichain is representable by asserting one cause of each signature. A solver or stored representation may encode these states differently. To support exact service after a loss, sufficient distinguishing information must survive somewhere trusted in the declared recovery system.

## Three different state costs from the same present-tense guard

If each cause has its own exclusive release, its signature is a distinct singleton and there are 2^n classes. For the states “all asserted” and “all except i asserted,” one needs at least n−1 releases and a query to see the difference. Every other cause must be cleared before a reply can differ, and releasing i would erase the difference. A suite testing only one release after a sealed observation misses this family for n>2.

If all causes share exactly one release command, there are only two classes for any n≥1. For h distinct strictly nested signatures there are h+1 classes, one per most restrictive outstanding signature plus the empty case. A single eligibility bit computes the same instantaneous query in all three designs. It has radically different adequacy for future management actions.

**Configuration changes matter.** Initially causes A and B can both be cleared only by g. Histories in which just A or just B is asserted then have the same summary. Add a new release h clearing A alone, issue h, and query. The histories now require opposite replies. An owner that discarded the distinction cannot implement that new contract exactly from its prior summary. An unchanged configuration identifier or a new encoding for the same two summary states cannot restore the missing information. Retaining attributable evidence, constraining how policy may evolve, or defining a conservative migration changes the premises. A promise to audit which cause was asserted would already distinguish the two original states.

## Checks and implications

`python3 docs/research/kernel-0/independent_seals.py` explores all 512 mappings of three causes to three release commands, including empty release signatures. It computes observable equivalence by ordinary transition-system partition refinement, independently compares all state pairs with the antichain representation, replays the distinguishing continuations for unequal pairs, and checks the two update rules. The numbers of mappings with 2, 3, 4, 5, 6 and 8 minimum states are respectively 8, 114, 162, 144, 72 and 12. The independent versus group-release cases were also checked through eight causes, and the reconfiguration counterhistory was executed. [Executable minimization](independent_seals.py)

This result tests a representation-level hypothesis about the Work Unit envelope. It rules out erasing independently releasable restrictions merely because they currently deny the same effect. It also gives conditions under which CONNECT and ORDER can maintain a smaller summary while preserving every advertised reply. The argument assumes idempotent causes, fixed release authority, serial authoritative commands and no observation of causal attribution. Counted leases, individual revocation receipts, descendant-sensitive changes, timing, protected data loss and unauthorized management access need their own proofs. It supplies no universal count of Kernel-0 primitives.
