---
title: Can a progress stamp reconstruct which prepared Work Unit updates committed?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Can a progress stamp reconstruct which prepared Work Unit updates committed?

A validation experiment established that the sum of component versions can certify a whole *ancestral candidate* as current. A recovery procedure may instead encounter both old and proposed data for several components and have to choose the acknowledged cut. Here the same sum can be insufficient. The distinction is visible in two process histories with byte-identical recovered files and different acknowledged updates. [Whole-cut validation theorem](How-much-currentness-must-survive.md)

## Two concrete histories

Prepare A's proposed value “alpha” and B's proposed value “beta” in a local database; both initial values are empty. The separate trusted database holds only the number of published updates, initially zero. A publisher receives its chosen unit, checks the proposal exists, increments and commits the trusted number, and acknowledges that named update before exiting. In one run the acknowledged update is A's, in the other it is B's. Discard publisher memory. The recovery interface receives the prepared and trusted databases; the harness separately retains the reply as the specification oracle.

Both files in the first run were byte-for-byte equal to their respective files in the second, checked by direct comparison of the complete files in the executable fixture. They contain the same candidate values and a trusted count of one. Recovering exactly {A} and exactly {B} requires opposite decisions about A's bytes. Neither trying both candidates against the sum nor using the prepared database's authenticity chooses the correct one. This is a deliberately insufficient publisher in a disposable experiment. No production owner was evaluated. The earlier positive validation theorem required offered coordinates to be no later than the true coordinates. Here a proposed-but-unpublished component can be later.

## Exact residual information given a durable precedence relation

Let P be a finite set of distinguishable prepared updates with a known, immutable precedence relation. Every execution publishes a prefix of a linear extension of P. Assume all such prefixes are possible, each distinct committed set has a different required recovery observation, every update is published at most once, and the candidate store supplies identical data and precedence across the competing histories. A feasible committed set is an *order ideal*: including an update requires including all its predecessors. Conversely an ideal can appear first in a linear extension by sorting it internally, then sorting the remainder.

At trusted count k the exact number of remaining possibilities is the number I_k of ideals of size k. Recovery needs **at least I_k distinct additional evidence values** at that count. Two ideals sharing all evidence would require different reconstructed sets. Numbering the ideals of size k and retaining the actual number is sufficient under the assumptions. A fixed additional alphabet usable at every count needs max_k I_k values since different counts can reuse codes. This is an information bound; enumerating the ideals or atomically maintaining their encodings can be expensive.

A count suffices at every rank exactly when the precedence order is a chain. A chain has one ideal at every rank. If a and b are incomparable, take the union of their strict predecessor sets. It is an ideal containing neither. Adding a alone or b alone yields two different ideals of equal size. Thus one pair of incomparable prepared events, with both publication orders permitted, already requires surviving branch information at some cut.

For N independent updates I_k is binomial(N,k). For independent chains of lengths l_j it is the coefficient of X^k in the product of (1 + X + ... + X^l_j). With three chains of four at k=6 there are 19 possibilities. More generally, for any known chain decomposition an ideal intersects each chain in a prefix. Store prefix lengths for all but one chain; the trusted total determines the last. Cross-chain constraints can make some count tuples infeasible and allow further compression. If a decision promises an observable order among otherwise incomparable accepted updates, the committed set may itself omit necessary information. [Ordinal replay lower bound](Receipt-retention-after-replacement.md)

## What the storage and order assumptions buy

A genuinely single immutable publication order, established in advance and recoverable in the same trusted context, lets a rank select a unique prepared prefix. A recovered count cannot retroactively create that order. A selector that atomically names the selected content manifest supplies a different witness. Per-owner commit records, a recoverable external acknowledgment, or a constrained publication protocol can change the number of alternatives. Sequentializing independent commits to save witness bits can cost availability and throughput. The result places that trade-off at the interface between ORDER and the evidence that must survive loss.

`python3 docs/research/kernel-0/prepared_cut_recovery.py` computes ideals directly and compares them with prefixes of all valid publication orders for all forward-edge subsets on three through five labelled updates. On five updates 960 of 1,024 graphs have an ambiguous count. Counts of 6/8 and 56/64 occur for three and four updates. Different graphs can encode the same transitive order. The script also checks the chain-count example and executes both local publisher histories. [Runnable proof checks and database witness](prepared_cut_recovery.py)

The construction assumes complete prepared data, correct and stable precedence, a current external count, and a requirement to reconstruct every acknowledged update exactly. Partial recovery, loss of the precedence evidence itself, crashed unacknowledged operations that may be completed either way, and external irreversible effects have different admissible observations. A lookup that can refuse all ambiguous cases provides safety but cannot satisfy an unconditional successful-recovery promise.
