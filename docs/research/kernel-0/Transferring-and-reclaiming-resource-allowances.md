---
title: When can a transferred Work Unit allowance be reclaimed?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Disconnected-resource-allowances.md
  - docs/research/kernel-0/Fencing-after-membership-rollback.md
  - docs/research/kernel-0/Receipt-retention-after-replacement.md
last_updated: 2026-11-28
---

# When can a transferred Work Unit allowance be reclaimed?

Conserving a shared allowance does not require a central decision for each use. It does require an authoritative transfer of the right to use it. Once a sender has issued a transferable debit, silence from the receiver cannot justify reclaiming it. A receiver may already have made or used the corresponding credit. A durable receiver-side refusal can make cancellation safe, at a cost in availability when that evidence is missing. [Fixed independent allowances](Disconnected-resource-allowances.md)

## A conserving transfer

For each declared additive budget row, mint protected rights in that row's units up to its available bound. For example a request that uses X or Y may consume one right from the common X+Y row. An operation touching several rows must reserve its entire charge vector at one local effect boundary. A resource release returns only the rights corresponding to the actual released charge. Cumulative budgets such as spent credits require their own nonreturnable rows. The positive result assumes nonnegative charge vectors, no omitted use paths, no unauthorized mint, and a trustworthy initial allocation.

Each scope keeps free rights and outstanding charges. For an individual transfer, choose a fresh identity binding the issuing scope and incarnation, destination, budget-row interpretation and exact nonnegative vector. Use these steps:

1. Under the source's protected accounting decision, remove the entire vector from its free balance and record a unique outstanding debit. Only the committed debit can yield a transferable certificate.
2. At the destination, decide once whether to redeem the authenticated debit or to retire it without credit. Redeeming moves the vector to its free balance. Retiring creates a permanent refusal for this identity, including for delayed delivery of the original debit. The two outcomes compete at the same destination decision.
3. A source can reclaim only from an authenticated destination refusal in step 2. Returning the balance and marking the source debit reclaimed are one source decision. Repeated copies of the refusal add nothing. Once the destination redeems, a return of unused allowance requires a separate reverse transfer from the destination's actual free balance.

Certificates must bind the row definition or a compatibility proof. Reusing a nominal budget key after changing what the row measures can create dissimilar material charges from the same debit. Authorization to move rights and the feasibility of the destination's requested action are separate checks. Selecting a new executor must not copy available rights out of an earlier owner's incarnation without proof the old incarnation can no longer use them.

**Invariant for every budget row.** Total free rights plus total outstanding charges plus the vector value of issued debits neither credited at their destination nor reclaimed at their source equals the original authorized amount. A source debit moves value from free to the in-flight term. Destination redemption moves it from in-flight to destination free. Durable refusal keeps it in-flight until source reclamation, then it moves back to source free. The mutually exclusive receiver decisions ensure neither transition can double-count it. Local charges move rights from free to charged. Release reverses that transfer. Duplicates and delayed messages have no other effect. The algebra holds componentwise. No observation of a remote owner enters an ordinary local use that is already backed by sufficient rights. This is an abstract two-owner escrow protocol. It assumes trustworthy local transactions and durable non-forking accounting state. Bounded counters supply prior art for safe decentralized numeric rights; this argument isolates the cancellation and owner-recovery conditions needed for the Work Unit contract. [Balegas et al.](https://arxiv.org/abs/1503.09052)

## The exact cancellation uncertainty

Start with total capacity one and one authentic in-flight debit. In one history the destination received nothing. In another it made the grant decision and consumed the unit, but all replies are delayed. The source sees the same committed debit and no replies. Reclaiming and spending at the source would allow two units of outstanding charge in the second history. Deeming the destination merely idle or imposing a local cancellation timeout cannot make that evidence differ. The converse direction is also important. A receiver that merely sees a removal request and replies without durably refusing future redemption has a history where the delayed original certificate can still be consumed after reclamation.

Under the stated messaging contract, before supplying spendable headroom the source must know that destination redemption cannot already have occurred and cannot later occur. A destination refusal is one sufficient witness. A trusted fence known to prevent all credit uses, together with complete destination outcome evidence, can serve the same role. The source never needs to prove physical packet deletion. If the destination is unreachable and may already have redeemed, the admitted outcome can remain unknown while availability is tied up. A system with a stronger proof of bounded message or grant lifetime can change the decision surface. A timeout by itself does not establish that proof. [Admission closure from surviving evidence](Fencing-after-membership-rollback.md)

## Which state must survive replacement?

A source that restores a pre-debit image while the original certificate survives can spend both its restored rights and the destination's later credit. A destination that restores a pre-redemption image can redeem the same debit again, including after a previously credited use or reverse transfer survives elsewhere. A destination that loses a permanent refusal can redeem a certificate whose source has already reclaimed. The whole accounting invariant depends on both sides retaining the decisive debit and terminal classification, or reconstructing equivalent evidence before service. The issue is independent of whether usage receipts are returned.

A small free-balance record cannot in general replace the retained classification. Suppose n individually redeemable unit debits are fully staged, any k can have been redeemed, and the destination's only aggregate status reports k. Two different k-subsets give the same numeric state while an exact replay of an identity in their symmetric difference requires different behavior. With no other distinguishing observation, exact duplicate handling needs at least binom(n,k) additional values at that count. If the contract forces one immutable redemption prefix, its rank can identify the settled subset. Such a restriction adds a progress dependency because an individual later transfer might then wait for earlier IDs. Outcome compaction therefore needs a defined safe-retirement contract, not only a conserved total. [Prepared-cut counting](Reconstructing-a-cut-from-prepared-updates.md) · [Retry release](Receipt-retention-after-replacement.md)

**Disposition.** Local spending against a fixed allowance can reuse the existing envelope proof. Dynamic transfer requires a verified debit, a unique destination decision and a reclaim witness before old capacity is reused. The budget semantics, receipt retention policy and desired availability during lost destination replies remain architecture choices. A future native discriminator would compare delayed first redemption against successful refusal-before-redemption, and include rollback before each side's decision while messages survive. No new allocator or rollover runtime has been admitted or executed.
