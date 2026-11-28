---
title: What must the first fresh commit transfer, and from where?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-28
---

# What must the first fresh commit transfer, and from where?

A resumed selector can make its numbering safe by reading control evidence — gate floors and its outgoing spool. Can it also answer, at its first fresh commit, *what has been accepted so far*? The bounded model of the [selector rollback study](Selector-rollback-recovery.md) enumerates every genuine earlier image against the true history; in 3,572 of 6,769 one-gate restored images (1,358 of 4,219 with two gates) the true world committed a tenure beyond the one the image remembers — a *forgotten-commit window*. Each tenure that ever held authority may have admitted contents, since a tenure that can never write is not a tenure. The window is the majority case, not a corner. [D]

**Markers: [D] demonstrated, [C] conditional argument, [H] hypothesis, [O] open obligation.**

## The control plane cannot answer [C]

The selector's durable state after resumption — decisions, selected tenure, recorded bindings — plus every gate floor, vote and summary in the system is *control* evidence. None of it encodes the accepted sequence: whole appends are admitted at open gates without changing any control state, which is precisely why the rollback model could leave appends out entirely and still decide every authority question. Two histories with identical control state can therefore differ arbitrarily in what was accepted under the tenures of the forgotten window. No procedure keyed to the resumed selector's own record can reconstruct the accepted prefix; the record that regressed with the image is a lower bound that the true history has already passed.

## Two ways the regressed record harms [C]

*Truncation.* A successor that takes the resumed selector's record as the accepted prefix inherits a stale cut and treats accepted work as absent — re-doing it, or answering queries as if it never happened. The evidence packet requires that accepted authoritative changes persist and that replacing an executor never treats continuing work as new; a truncating transfer violates both in every forgotten-commit window.

*Destructive reclamation.* Worse, a resumed selector that acts on its record — releasing, compacting or reassigning the store regions beyond its cut, on the theory that they were never accepted — destroys accepted contents. This composes the retention studies' release race with rollback: the release directive is now issued by an authority that is wrong about the very fact (acceptedness) that makes release safe. Any reclamation procedure that trusts the regressed record has a witness history of data loss.

## The reconciliation rule [C]

Under any append-safe resumption from the first study — every gate opened only under a lineage-authorized tenure — no store can contain an item accepted under a tenure the true history never authorized. The stores' own cuts therefore *are* the authoritative accepted prefix at the moment of resumption, and the safe transfer at the first fresh commit is: **take the maximal store cut; treat the resumed selector's regressed record as, at most, a lower bound and never as an instruction to truncate or reclaim.** The placement principle this forces is asymmetric and, we claim, irreducible:

- resumption *authority* can be rebuilt from control evidence (floors and spool), because decisions and messages are all the control plane ever held;
- resumption *custody* cannot, because the control plane never held the contents.

The first fresh commit therefore transfers custody *from the content plane directly to the successor*, with the resumed selector contributing only fresh numbering and the commit's authorization — not the prefix. This sharpens the surviving-content study's separation of version custody from a checkable recovery certificate: after rollback the certificate must be obtainable without the selector's testimony. [Surviving contents](Surviving-content-at-handover.md)

## Evidence

The forgotten-commit window counts come from the same executable enumeration as the first study: `python3 docs/research/kernel-0/glm-g4/selector_rollback_recovery.py 1 3 4` prints `forgotten-commit windows: 3572 of 6769`; `2 2 4` prints 1,358 of 4,219; both assert the window is nonempty before the custody claims are usable. The model also counts direct append service: in 948 of 6,769 one-gate images (702 of 4,219 two-gate) some gate is open at the restore instant holding the true selected tenure, which the verified invariant identifies — so an append is *accepted right then* under a tenure beyond the image's record, with no rollback fiction needed. Stronger, under the repaired resumption itself — the rule that makes numbering safe — 1,134 of 6,769 one-gate runs (743 of 4,219 two-gate) visit states where an open gate keeps serving the forgotten true tenure until the first fresh commit fences it: the contents that accrue during this service window are real, they are accepted after the failure, and the resumed selector's record cannot enumerate them. The same runs confirm the reconciliation rule's premise from the other side: no open gate ever holds a tenure outside the lineage under any append-safe rule, so everything the stores accumulated is authoritative. [D]

**Boundary.** The reconciliation rule inherits every boundary of the first study's append-safe rules; if gates can open under forged tenures, stores may hold unauthorized items and the maximal cut is no longer authoritative — the two studies stand or fall together on that clause. The store cut needs its own checkable certificate under the surviving-content study's obligations, which this result does not re-prove. If the stores share the rolled-back storage domain, both custody and contents are lost together and nothing here applies [O]. Reclamation and compaction protocols under the reconciliation rule, multi-store cuts with partially available stores, and the interaction with changing membership remain open [O]. No realization, storage layout or production practice is selected by this argument.
