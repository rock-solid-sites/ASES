---
title: What must remain recoverable when an old admission path is closed?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Fencing-after-membership-rollback.md
  - docs/research/kernel-0/Surviving-content-at-handover.md
  - docs/research/kernel-0/Retaining-immutable-content-across-attempts.md
  - docs/research/kernel-0/glm-g4/Custody-after-a-forgotten-commit.md
last_updated: 2026-11-28
---

# What must remain recoverable when an old admission path is closed?

The selector can safely skip fencing a gate whose old enables all lie below its protected floor. It cannot skip the contents that gate accepted while it was open. The two obligations can require different responders, and a durable fence and a durable content copy can still attest different cuts. This is a deductive composition of the published admission and custody models. It adds no new execution evidence. [Admission closure](Fencing-after-membership-rollback.md) · [Forgotten-commit custody argument](glm-g4/Custody-after-a-forgotten-commit.md)

## The closure and snapshot order

Use a single Work Unit whose locally accepted appends are authenticated, ordered per source and uniquely named by scope, source incarnation and position. Suppose every whole append commits while its source is eligible and is serialized with any fence on that path. Let the recovery target be the vector of final old prefixes as of successor selection. The successor may therefore need evidence from a source retired before the latest known membership. The vector contract leaves the relative order of incomparable appends unspecified.

For each source, distinguish two things.

1. **A stable end to old admission.** A fence, permanently higher floor, or irreversible exclusion protects against later old appends. The proof must account for escaped enables and any already admitted operation still capable of adding bytes. An instantaneous status of closed has no such force.
2. **A final extent and custody certificate.** A trustworthy observation gives the source's exact final accepted prefix and binds it to bytes available under the declared failure model. The certificate can be derived from a durable admission journal outside the source. It can also be derived from a causal cut witness that already includes the last old acceptance. Authentication of a prefix and the physical survival of those bytes alone establish only that prefix.

Proof of finality must cover the last time a source could add to the promised cut. Suppose A has accepted prefix a and an independent holder attests and retains exactly a. Compare two continuations before A's successful fence. In one nothing happens. In the other A accepts one legitimate append x after the holder's observation and before the fence. If the fence attests only closure and the suffix evidence is unavailable, all observed receipts can be the same. One recovery must deliver a, the other a+x. An earlier authenticated transfer receipt cannot be upgraded to a final cut by pairing it with an unrelated fence. Obtaining a snapshot after the fence works under a protected no-rollback and full-observation contract. A stronger fence can instead return the bound final prefix at the very decision that closes admission. If a verified previous snapshot is extended by a complete authenticated suffix through the fence, no repeat full copy is needed.

A content certificate can be necessary even when a fence is unnecessary. Consider histories A and B with identical selector observations and B's floor strictly above its old enables. B is no longer required for admission closure. In one history it accepted x while still eligible, and in the other the same x was prepared but never accepted. Keep only a copy of the staged bytes and drop the outcome evidence. The two histories yield the same remaining observations. Recovery cannot decide whether x belongs in the continuing work. A trusted final zero extent or an authenticated journal covering B's earlier tenure would change the result. The fact that B has never been enabled since a *recent* membership or selector cut is insufficient if that cut does not already cover all of B's earlier work. [Staging versus commitment](Committing-to-a-surviving-cut.md) · [Prepared-cut ambiguity](Reconstructing-a-cut-from-prepared-updates.md)

## What the successor can certify

Under the stated assumptions, the following construction suffices.

- Establish durable closure for all old paths, possibly at different times. Stop old summary issuance as in the closure study. Serialize each path's final extent with its last opportunity to append.
- Obtain a complete, trustworthy extent for every source that may contribute beyond the last independently certified cut. Retain the named material and replay data through the allowed failures. A certified empty or fully included prefix needs no new contact with its original gate.
- Bind the vector of extents and the new configuration in the successor's authorized selection. Expose success only after the promised material and its verification evidence are available to the successor. Allow a prior holder to discard required material only after an independently safe successor placement has been established, according to the custody contract.

This vector exists without a simultaneous multi-gate snapshot because every source projection is stable after its own closure. At successor selection the product of these stable projections is the exact old cut. Pairs of projections require additional consistency rules if they overlap in identity, if one can overwrite another or if requests span several sources. An observer promised one global append order also needs an authenticated order or a proven canonical merge rule consistent with its prior replies. For two independent stores with snapshots (A1,B0) and (A0,B1), neither candidate is the maximum of the other. Per-source authenticated maxima give (A1,B1) only when the two components name compatible prefixes. The earlier phrase “take the maximal store cut” is sound for one append chain under the stated safety and custody premises. It needs this clarification for independent stores, and it does not license a merge of forks. [Storage-loss model](Surviving-content-at-handover.md) · [Repeated retention and release](Retaining-immutable-content-across-attempts.md)

## Exact availability at a fixed certified cut

One can express the two independent obligations without identifying voters with holders. Let R be the ready endpoints and let U be the old paths that still need a fence. In the simple direct-fencing contract, each i in U needs its own responsive endpoint. For each source j, let `ProofSets(j)` be the sets of endpoints whose **joint** response is sufficient to recover and verify that source's final prefix. Empty sets are allowed when a certificate is already held safely, including a certified zero contribution. A set can contain multiple endpoints, for example one attests extent and another supplies the bytes. Its members may be totally different from the original gate.

Given correct joint certificate semantics and fixed responses, the immediate handover criterion is

```text
U ⊆ R  AND  for every source j some P in ProofSets(j) satisfies P ⊆ R.
```

In a failure projection it must hold after each allowed endpoint loss, if successful handover despite every such loss is promised. This is exact relative to the complete certificate vocabulary and the assumption of no unmodeled dependency among simultaneous responses. Sufficiency follows by gathering the named inputs and constructing the cut above. Necessity holds for the stated interface when a missing proof means another compatible history has a different final prefix or required bytes are unavailable. Compatible histories, shared failure domains and costs can make any proposed roster of proof sets incomplete. The formula does not derive that roster from application state. It allows independent placement choices and illustrates why either a single voting quorum or a single replica count can misstate the availability guarantee.

## Research disposition

**REUSE** the existing fence and immutable retention proofs for their component claims. Their combination requires final-extent binding and complete source coverage. Existing local transfer data can illustrate the closed single-prefix case. An executable study of changing membership plus withheld final evidence is a separate experiment. The useful acceptance condition is recovery of *exact* named bytes and receipts at the honest cut, with a negative control that reuses a valid but pre-fence certificate. A correct fail-closed response to a missing extent is a safety result. Successful continuation requires additional evidence. Native composition, replicated witness semantics, physical failure and a complete global order remain open.
