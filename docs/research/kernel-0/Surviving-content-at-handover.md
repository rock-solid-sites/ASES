---
title: What evidence shows that accepted contents survive handover?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# What evidence shows that accepted contents survive handover?

A selector can collect a vote from every outgoing gate, fence every old append, install the successor, and still lose the only readable copy of X's last accepted bytes. The gate proof concerns permission to append. A successor's right to resume also refers to particular information at a particular cut. This study isolates one recoverability obligation that a selector or a reviewer can check independently. [Membership and handover](Abortable-handover-and-catch-up.md) · [Local continuation and exact replay](Local-owner-admission-and-replay.md)

## Specify what the successor must reconstruct

Fix a finite frozen content version x, represented for this experiment as a vector of bits. The consumer requires Lx, for a public binary matrix L. For exact bytes take L to be the identity; a deliberately weaker consumer may require only a projection. When exact retry is promised, the information defining historical outcomes must also remain available. Equal application bytes can accompany different required receipt histories. [Receipt distinguishability](Receipt-retention-after-replacement.md)

In failure domain i the surviving record holds A_i x, with each row denoting XOR over specified input bits. The matrices and domain identities are known. For the mathematical result these fragments are all the content-dependent information available to the decoder. A manifest that provides extra content bits, a digest usable for exhaustive reconstruction, or a separate trusted historical log changes the decoder's observations. It must be accounted for if used. Authentication and agreement on the version are separate premises.

For a set of lost domains F, stack the surviving rows into A. **Exact reconstruction of the required observation for all x is possible iff every row of L belongs to the row space of A.** If so, an untrusted party can supply a decoder matrix D with DA=L. Matrix multiplication validates the certificate; D(Ax) yields the required answer. If the inclusion fails, there is a difference z in the kernel of A with Lz nonzero, by the orthogonal-complement relation between row space and kernel. The two words 0 and z yield identical surviving fragments and different required observations. This furnishes a reproducible failure witness. The criterion may hold for a declared projection even if the original bytes cannot be recovered. Changing the consumer promise requires checking the new L.

## Which failure domain sets matter?

For a content difference z define its support as the set of domains i for which A_i z is nonzero. Among differences with Lz nonzero, let d be the minimum size of this support. For nonconstant required observations, d is the minimum number of whole domains whose erasure can make recovery ambiguous. Indeed two words become indistinguishable if every domain on which they differ is lost. Thus every set of at most f domain losses is tolerable exactly when d>f. More generally, no allowed loss set may contain the whole support of a required difference. A realizable counterexample includes both the lost domains and the two confused content versions.

If up to b surviving domains may supply arbitrary undetected block values and up to e domains are known missing, the corresponding condition is d>2b+e. Given a putatively ambiguous observation, two explanations differ on at most the e missing and the two sets of at most b altered blocks. Conversely erase up to e differing blocks of a closest pair and split the remaining differences into two groups of size at most b. Taking blocks from opposite originals on those groups yields a common observation. This is the classical distance argument applied to domain blocks and differences that affect L. It addresses unique decodability, without promising an efficient decoder for arbitrary matrices. [Hamming, *Error detecting and error correcting codes*](https://doi.org/10.1002/j.1538-7305.1950.tb00463.x)

With two original bits, storing x, y and x XOR y on three independent domains tolerates any one loss. Put both originals in one domain and parity in another and a single loss can be fatal. Three signed storage receipts can describe either placement. With two copies of x and neither copy of y, the x-only projection survives either single-copy loss, while whole-content recovery already fails before any loss. Domain independence, qualified version binding and the required projection each change the answer.

## Composition with a handover

For a candidate cross-owner realization, first identify which frozen prefix at each gate includes every accepted append. Only fragments of those prefixes count. Even two independent systematic rows can decode a word belonging to neither authoritative version: taking the first bit of 00 and the second of 11 yields 01. A full-rank matrix cannot compensate for selecting different commits. The holder must bind its receipt to the correct immutable material and maintain the promised readability through the relevant transfer and loss interval.

There is a useful reduction for discarding old copies. Once every *new* retained fragment is durable and reserved through the change, further independent deletion of a designated set of old copies only removes rows. If the required observation is reconstructible after **all** those deletions and each allowed fault, any intermediate subset of deletions is safe for this observation because it has at least the final rows. Checking separate deletions against a shared initial snapshot is insufficient. With two replicas each deletion in isolation preserves the bytes and deleting both loses them. A selector must authorize the joint retirement set or maintain equivalent exclusive retention obligations. Progress accepting new appends, content confidentiality and preventing premature release of a promised fragment are different obligations.

## Checks and limits

`python3 docs/research/kernel-0/surviving_contents.py` compares row-span inclusion with direct grouping of all eight possible three-bit words by their surviving observations. It tests every choice of four distinct rows from eight possible rows in increasing binary order, two fixed domain groupings, three required projections, and every whole-domain loss mask. Of 5,040 cases, 1,421 permit exact reconstruction and 3,619 admit ambiguity. The minimum support calculation agrees with the smallest fatal loss set throughout. Two small codes also compare the error/erasure threshold with exhaustive received-word ambiguity. [Executable cross-check](surviving_contents.py)

This is a conditional certificate for bounded linear encodings, not a proposal to require erasure coding in Kernel-0. ISOLATE must protect the contents and promised storage domain, CONNECT must authenticate the material and future access, and ORDER must relate the frozen version, reservation and release. The calculation alone establishes none of those facts. Physical persistence, retrieval latency, nonlinear compression, unmodelled correlated failures and custody of encryption keys remain separate parts of the realization claim.
