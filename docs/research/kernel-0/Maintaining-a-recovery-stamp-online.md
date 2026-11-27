---
title: Can an online owner maintain the minimum recovery stamp?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Can an online owner maintain the minimum recovery stamp?

For n independently updated binary components, n+1 trusted values suffice for a one-shot whole-cut validation under the ancestral-candidate premise. An online owner processing authenticated announcements that can repeat needs **2^n distinguishable states** under the interface below, even if its only public operation validates that same whole cut. Saving space in the value read by recovery can move the full information cost into the mechanism that maintains it. [Minimum one-shot stamps](How-much-currentness-must-survive.md)

## A machine with replayable inputs

Component i starts at zero and can reach k_i. A trusted updater receives set-version(i,h), meaning that i has reached *at least* h. The reference applies y_i := max(y_i,h). Notifications may be duplicated or delivered out of order; h is within the declared bounds. Updates acknowledge identically. At any subsequent cut a recovery probe offers coordinatewise ancestral versions for one allowed scope B and requires an exact current/stale verdict. This model takes the updater's delivered prefix as authoritative. If acknowledgment by some other owner precedes delivery to the updater, an additional ordering protocol is needed. The updater has only its own persistent state and the input; it cannot consult an external authoritative previous value or an independent deduplication oracle.

For two different current vectors y,z and an allowed scope B, count p coordinates of B with y_i<z_i and m with y_i>z_i. If p+m>0, the **shortest common notification suffix after which a probe on B can distinguish the histories** has length min(p,m).

A distinguishing common ancestral probe exists exactly when the projected vectors are unequal and comparable. One notification can erase a sign difference at one coordinate by advancing both values to the larger, and cannot reverse a sign. As long as both signs remain, neither projected state can be a feasible current candidate at the other. Thus at least min(p,m) notifications are necessary. Saturate the coordinates of the less numerous sign, or either sign on a tie; the surviving sign gives the required unequal comparable pair. Offer the smaller projection. This attains the bound. A scope on which the vectors agree cannot later distinguish them under identical inputs.

Minimize that length over allowed scopes on which the histories differ. Whenever the allowed scopes cover all coordinates, **every pair of version vectors is distinguishable by a common continuation**. If an online deterministic implementation merged them, identical future messages would preserve identical machine state through the decisive query. The minimum state count is therefore the full product of (k_i+1). Keeping per-component maxima and validating the offered block attains it. If some coordinates appear in no scope and cannot affect covered coordinates, their counts drop out. The proof counts the owner's total accessible reliable state. A compact public stamp and a larger protected maintenance table are consistent with it.

For binary components and whole-only recovery, a balanced pair with opposite discrepancies can need floor(n/2) announcements before a common probe separates it. A local test that compares only the instant of recovery may see the optimal one-shot compression but miss the future update that disproves its use as an online state quotient. A small example has true states (1,0) and (0,1), both with sum one. Deliver set-version(A,1) to both. The sums now need to be one and two respectively. Candidate (1,0) is feasible in both and current in only the first.

## Where the information can move

With exactly-once, authenticated +1 deltas and a guarantee against boundary overflow, a whole-cut stamp can add one per delivered increment; it does not need to classify a repeated cumulative announcement. Establishing exactly-once delivery or deduplicating those deltas is a separate obligation. Another interface gives each protected producer exclusive responsibility for a disjoint group and lets it report a cumulative group total. The combiner can use per-producer maxima and sum them. It relies on the producers to prevent double counting inside each group and on immutable assignment. This is the componentwise-maximum principle used in a grow-only counter. A cryptographic commitment with update proofs supplied from outside the owner offers still different observations and computational assumptions. None contradicts the indistinguishability result for identical replayable inputs. [Shapiro et al., *A comprehensive study of Convergent and Commutative Replicated Data Types*](https://inria.hal.science/inria-00555588/document)

## Checks

`python3 docs/research/kernel-0/online_recovery_stamp.py` starts with conflicts obtained by enumerating actual ancestral probe verdicts and propagates distinguishability backward over paired transitions with identical updates. It compares all shortest distances against the sign-count formula. For four components with bounds two there are 3,240 unordered pairs. With whole-only queries 1,215 separate immediately, 1,782 after one announcement and 243 after two. With pair queries on a four-vertex path 3,159 separate immediately and 81 require one more input. In both cases all 81 states are necessary online, although the one-shot optimum is nine and 65, respectively. The search also checks heterogeneous bounds, uncovered components and binary whole-cut queries. [Executable comparison](online_recovery_stamp.py)

This establishes an interface-dependent maintenance lower bound and an exact shortest discriminator. Nonreplayed ordered events, externally maintained evidence, bounded replay windows, probabilistic summaries, fail-closed recovery, concurrent publication and actual crash-consistent witness placement require their own analysis. A validator and its upstream producer must both be included in a trusted-state or computation-reduction claim.
