---
title: Transferring the accepted prefix between local resource owners
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Transferring the accepted prefix between local resource owners

An outgoing owner has accepted two requests with different nonces and identical payloads. A successor can have exactly the right visible bytes and still be unable to answer which request committed. Conversely, a target that has copied the complete prefix may still lack authority to admit the successor. This experiment separates content readiness from eligibility with two storage-owner databases and a third selector database. All three use independent SQLite transactions. [Content recoverability](Surviving-content-at-handover.md) · [Local single-store admission](Local-owner-admission-and-replay.md)

## Construction and reference relation

Consider one continuing W/P and one move from X at store A to Y at store B. The authoritative content is an ordered sequence of (ordinal, issuing tenure, nonce, payload). The reference accepts a fresh current request, replays the ordinal of an exact committed request, and refuses conflicting nonce reuse. A gate between phases can defer. The experiment treats X and Y as already authenticated origin labels on a trusted local interface; it provides no credential authentication. It fixes one coordinator, one transfer attempt, and the two store identities.

1. Freeze A against all its appends in A's local transaction. Committed requests before that boundary are part of the prefix. A later attempt at frozen A defers.
2. Copy the frozen rows to private staging at B, permitting loss between any two copies. Recopy by ordinal idempotently. Compare all rows, in order, with the frozen source and mark B ready in its local transaction only on exact agreement. A mismatched row prevents publication. There is one writer for staged data and no authorized transition out of ready before selection.
3. Commit Y at the selector. This is the abstract replacement. Its premises are A's stable freeze and B's durable, reserved readiness. Activate B on the committed decision. A subsequent coordinator retry sees Y and uses B alone. It never overwrites newer appends with the old prefix.

Before selector publication A contains the reference sequence. Staging at B is invisible to admission. At publication B contains exactly the same sequence, so switching the content projection preserves all accepted effects and ordinal bindings. Neither side can admit X afterward. Until activation B may defer both old and new calls. After activation, B can append Y's fresh request and replay an old accepted X request without treating it as a new mutation. Induction over local transactions gives this safety statement for the stated monotone one-attempt model. No cross-file atomic filesystem transaction is required because equality and readiness cannot be withdrawn during the vulnerable interval. Neither repeated transfers, concurrent coordinators nor independent rollback have that premise automatically.

## Ten real process-loss cuts

Run `python3 docs/research/kernel-0/local_content_transfer.py`. Each case uses fresh files and a subprocess that terminates via an immediate process exit inside or after the indicated SQLite transaction. A new invocation reopens the durable state. The harness injects an X append after interruption, probes target admission where the selector is still X, completes the move and checks the full target sequence, conflicts and retries. If selection of Y survived the interruption, it makes A unavailable at its configured path before recovery. The ordinary database opener refuses to create a replacement for a missing store. [Executable experiment](local_content_transfer.py)

| Interruption point | Observable recovered state and distinguishing outcome |
| --- | --- |
| Immediately before the freeze transaction commits | The X selector and open A survive. The intervening X append is accepted as ordinal 3 and transferred; Y obtains ordinal 4. |
| After freeze, inside the first copy transaction, after one durable copy, immediately before the ready transaction commits | The X selector and frozen A survive. The intervening X call defers. B is in its initial staging mode and cannot admit Y. Recovery reconstructs the exact prefix. |
| After ready, immediately before the selector transaction commits | B has durable content and remains ineligible. Y is still deferred. The replacement can subsequently commit. |
| After selector commit, immediately before B activation commits | Y is durably selected and B is ready. With A's file unavailable, recovery activates B from its own content. |
| After activation | B is open for Y. A further transfer retry preserves the successor's newly appended row. |

All ten cuts passed on SQLite 3.53.1. Except in the pre-freeze case, Y obtains ordinal 3. In every case, exact X retries at B yield 1 and 2 for the distinct nonces holding identical bytes, conflicting reuse is refused, and a fresh X request cannot append. Repeating recovery after Y's own append preserves the full successor sequence.

Two controls use separate fresh stores. Changing only the copied nonce preserves every payload and its position. Full comparison refuses publication; a publisher accepting payload equality alone loses the original retry and replies stale after selection. In the other control the copied rows are exact but B is opened before the selector changes. B accepts a fresh Y append while the selector still reports X. These distinguish receipt-history equating, content readiness and execution authority.

**Trust and reach.** SQLite's local transaction guarantees, protected owner files, immutable staging after verification, stable selector, complete append/freeze mediation, and correct fixed scope are premises. The program uses a full equality scan and can block on A before selector commit. The post-commit tests establish process-restart continuation with A inaccessible at the configured path on one host. They do not simulate physical power loss, independent storage domains, source destruction, hostile rollback, or an engine deployment. Extending the procedure to abort and repeated moves requires binding readiness and release to the exact attempt so that a delayed release cannot destroy a later configuration's retained bytes.
