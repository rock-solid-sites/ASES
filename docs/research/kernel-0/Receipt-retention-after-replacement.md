---
title: What must survive replacement to answer an old retry?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# What must survive replacement to answer an old retry?

The local owner can tell a delayed fresh X write from a retry of X's committed write after replacing X with Y. Both requests can carry an authentic retired grant. Its experiment retains all accepted request identities and receipts. How much of that history can a different owner discard while giving the same replies? [Local owner experiment](Local-owner-admission-and-replay.md)

## A lower bound with fixed application contents

Fix a single grant and N distinct possible request keys. Every request appends the same bytes to the same initially empty log. Accept k distinct keys in any order, numbering receipts 1 through k, then replace the grant. The application byte sequence, current tenure, total number accepted, and all submitted retry payloads are identical across the resulting histories. A probe of a previously accepted key must recover its original ordinal. A probe of any other key must report stale. There are N!/(N−k)! possible ordered selections. Any two differ on some key's answer, so exact service needs at least that many distinguishable recoverable states across these histories, or at least ceil(log2(N!/(N−k)!)) bits in a fixed-length encoding. A table mapping the selected keys to their original ordinals suffices for this restricted family. If only accepted versus stale is observable, the number of states drops to binomial(N,k). For k=N membership needs no extra information in this fixed family while ordinal replay still distinguishes N! permutations.

The bound counts information anywhere a recovery decision can consult. An existing application log containing ordered request identities, or a trustworthy external witness available for every retry, can carry it. A separate receipt table is optional. A caller who *lost* the reply cannot be presumed to have the receipt. A content digest with fewer possible values than required cannot support exact discrimination on this family, absent additional evidence. The argument fixes the application bytes to avoid counting a distinction the application already has to preserve. It is a lower bound for a stronger replay contract than fresh-write safety. [Finite-observation tenure argument](Tenure-reuse-and-delayed-admission.md)

## An explicit release contract admits bounded outstanding receipts

Consider a different interface for one authenticated stream, with positive integer keys that do not wrap. Its consumer may release a contiguous prefix once it no longer requires individual answers there. A completed release through f changes the answer to *every* subsequent call at key ≤f to “released”, with no effect. Prior accepted application contents remain durable. A delayed packet may still arrive after the release. A handler must have evidence of the floor even after deleting the individual outcomes. Other streams require their own binding and release authority.

A sufficient owner keeps the durable floor f and accepted outcomes above f. A fresh call is eligible only while the grant is current and f < key ≤ f+w. Exact retries above the floor still receive their saved ordinal and payload-conflict check after replacement. Release to t>f requires authorized consumer consent and outcomes for every key in (f,t]. Advance f and reclaim those individual bindings as one recoverable transition. The consumer acknowledges relinquishing exact answers over the whole prefix. Acknowledging just its greatest completed key carries different information. A consumer who cannot durably remember giving up those answers may lose its own recovery guarantee.

**Refinement.** Compare against an owner retaining the full append log and the same release floor. The compact records are precisely the accepted records above f, with original payloads and ordinals. Initially empty, a duplicate reads the same record, a fresh admitted key creates the same next record, and a released or denied call creates none. Release deletes exactly the records hidden by the new reference reply. A duplicated or delayed older release leaves the floor fixed. Retirement disables fresh admission while preserving the relation. Induction covers any finite interleaving. In the single-stream model with no other appends, next ordinal is f plus the number of outstanding records plus one, since all keys up to f have committed. Shared stores can instead retain a separate sequence allocator. The in-window admission rule bounds outstanding records by w even with arbitrary out-of-order calls. It can block if a prefix hole is never filled. The bounds exclude application bytes, payload sizes per outstanding record, and the growing bit length of nonwrapping integers.

The RIFL system provides an external comparison for collocating RPC metadata with affected objects and collecting it under a lease. The release proof here assumes explicit prefix consent and a durable floor. It uses neither a clock nor a lease-failure model. The receipt lower bound applies when the consumer keeps the original reply contract indefinitely. [Lee et al., *Implementing linearizability at large scale and low latency*](https://doi.org/10.1145/2815400.2815416)

## Executed controls

`python3 docs/research/kernel-0/receipt_retention.py` enumerates the exact retry vectors and their membership projections for every k at N=8. Both counts match the formula. A separate breadth-first comparison checks a compact owner against a full-history oracle, with two payloads per key, retries, conflicting reuse, arbitrary prefix releases and retirement. It explores 58, 726 and 9,290 paired states for (maximum key, window) equal to (3,1), (4,2) and (5,3). Neither owner models an external side effect. [Executable comparison](receipt_retention.py)

- Accept key 2, then request release through 2. A policy that checks only the maximum accepts despite the hole at 1. The reference refuses.
- Accept 1, release through 1, then deliver another copy of the same request while the tenure is still current. Ignoring the floor after deletion appends it a second time. Consent to forget receipt details cannot erase transport copies.

This establishes an interface trade-off and a conditional reference construction. The experimental SQLite owner still implements indefinite exact replay. Testing crash recovery of a reclamation implementation would require observing the durable floor and the retained bytes on both sides of its release commit.
