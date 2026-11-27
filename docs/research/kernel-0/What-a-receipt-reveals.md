---
title: What a receipt reveals across Work Unit scopes
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# What a receipt reveals across Work Unit scopes

Run the same first append at P twice from equivalent P states. In one history Q is idle. In the other Q first commits one append of its own. The local owner's global receipt is 1 in the first history and 2 in the second. Every append was authorized, P can read only its own bytes, and the W5/W6 tests pass in both histories. Nevertheless P observes a difference caused by Q. One successful scoped read test cannot establish confidentiality of other scopes' activity. [Local owner crosswalk](Local-owner-admission-and-replay.md) · [Earlier confidentiality discriminator](../astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md)

This is a boundary between two possible contracts. If callers are entitled to globally consecutive insertion ordinals, the numbering is correct and reveals placement in the global sequence by design. If P is promised that hidden Q activity cannot affect the sequence of its terminal reply values, no owner can give P that global ordinal on both histories and meet the promise. This impossibility follows from the two required, distinct values alone. Serialization inside a shared owner can still implement the second contract when the global position is kept internal.

## A scope-relative projection

In the experimental alternative the owner retains its internal global row ID and returns the rank of the row among committed appends to the same W/P, across all its tenures. Both fresh acceptance and exact replay compute that rank. Rank stays fixed because the log is append-only. After replacement, a retry by X still identifies the exact original row, and a fresh request by Y obtains the next rank in P. Q's first receipt may have the same numeral as P's first. A consumer comparing receipts from different scopes would need to retain their scopes. The alternative assumes the promised identifier is scoped. Deletion or import of older rows would invalidate rank stability unless ordinals were separately preserved.

**Two-run argument.** Compare two owner states on P's selector, its grants and the ordered list of P's accepted (grant, nonce, resource, payload) records. Compare fresh credentials up to a consistent renaming, or couple their successful generation across the executions. Ignore physical row IDs. An ordinary successful Q step leaves that projection fixed. For any identical well-formed P request and equivalent P states, grant lookup and eligibility agree, nonce lookup finds the same scoped position and payload or finds none, and each reply depends only on the projection. An append extends the two projected sequences equally. A P replacement installs corresponding fresh grants and preserves the rows. Induction over matching P steps, allowing extra Q steps between them, gives equal terminal reply values and equal projected successor states. Conversely the global receipt test breaks the reply-equality step. Scope integrity is a property of each execution. Concealment of Q activity compares executions. [Clarkson and Schneider, *Hyperproperties*](https://www.cs.cornell.edu/fbs/publications/Hyperproperties.pdf)

## Executed checks

`python3 docs/research/kernel-0/receipt_observations.py` exercises the actual SQL request handler over fresh in-memory stores. It compares a fixed seven-operation P history with all interleavings of zero through three successful hidden Q appends. P appends, reads, changes tenure, retries the committed old request, attempts a fresh stale append, appends as successor, and reads the surviving contents. In global mode 155 of 165 histories have a different P transcript from the no-Q baseline. In scoped mode zero do. For global mode the ten unchanged histories are exactly the distributions of zero through three hidden appends across the two slots after P's final append. The counts are exhaustively enumerated cases for this workload. [Paired-history experiment](receipt_observations.py)

`python3 docs/research/kernel-0/local_handover_owner.py` also runs the queued, precommit kill and postcommit lost-reply histories in both modes through the separate owner process. All six passed. In the lost-reply case P's exact retry returns 2 in global mode and 1 in scoped mode. In each case Y sees X's bytes exactly once. This tests compatibility between the change in observation and the earlier local recovery contract. [Owner and process-loss controls](local_handover_owner.py)

**Limits.** The argument ranges over completed successful operation processing with independent scoped operations, no identifier exhaustion or collisions, and the same low inputs. Error timing, scheduling, resource contention, storage exhaustion, shared quotas, visibility of global audit logs, guessing or transferring other scopes' credentials and stronger information-flow policies require distinct arguments. No deployment supplies evidence here. The result changes how to test a proposed ISOLATE responsibility. If it includes hiding activity, CONNECT's admission checks and ORDER's legal serial histories leave a further two-run observation obligation.
