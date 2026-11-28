---
title: Which resource owners must a recovered selector fence?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Abortable-handover-and-catch-up.md
  - docs/research/kernel-0/glm-g4/Selector-rollback-recovery.md
  - docs/research/kernel-0/Changing-the-set-of-resource-owners.md
last_updated: 2026-11-28
---

# Which resource owners must a recovered selector fence?

A selector rolls back across a successful membership change. Reading a fresh attempt number and one currently open owner's tenure does not tell it which other owners can still serve. There is a precise recovery alternative to reconstructing exact membership: fence every owner that can still admit under an older authorization. That alternative permits a fresh replacement when an unavailable selected member has never obtained an enable and cannot obtain one from old messages. It requires a separate, explicit recovery permission to fence and replace on evidence of admission closure. [Prior rollback frontier](glm-g4/RUN-LOG.md) · [Changing-membership protocol](Abortable-handover-and-catch-up.md#joint-refinement-with-changing-membership)

## An observation lower bound

Two independent gates A and B have protected, nondecreasing control floors. A is initially the sole member. In both histories begin attempt 1, obtain A's prepare and commit. One attempt proposes and installs {A}. The other proposes and installs {A,B}. A can have the same local state (floor 1, open tenure 1) in both histories after receiving the appropriate summary. In the second history issue the summary including B. It can still reach B, even if B is closed and initially did not receive it. Restore the genuine initial selector image in both histories. Throughout recovery B does not answer management queries. A returns only its local floor and open tenure, and will return the same fresh-attempt fence receipt in both histories. The observer has a trustworthy attempt horizon and may even know the actual current tenure number. It has no surviving observations of the differing summary payload or the changed outgoing membership. A's receipt proves A's fence and contains no information about B.

Any policy promising eventual replacement when all actual outgoing members respond must finish in the first history under fair delivery to A. The same finite observations and the same choices can be scheduled in the second history until the policy returns success. B can then consume the old summary and append under the displaced tenure. A policy that waits for B in both histories forgoes that availability guarantee. The adversary can withhold B's recovery replies while admitting or delaying independently addressed workload messages. An owner that cannot possibly serve when it is unreachable to recovery falls under a different premise. With zero-error safety, randomization cannot justify a positive-probability commit on the indistinguishable prefix in the second history.

The proof isolates membership uncertainty from attempt reuse. The previously reported witness B starts from a pending image with target {A,B} and then passes {A} to its replayed commit. The helper accepts this deviation from the rule fixing a proposal for one attempt. That particular trace is therefore insufficient as a reachability proof for the published protocol. Here both pre-rollback targets are fixed from start through decision. Recovery uses a genuinely fresh attempt and its own fixed target. The stale admission still follows. The prior witness A supports re-decision of an identical attempt in its fixture. It is unnecessary for this argument. [Prior executable witnesses](glm-g4/membership_rollback_witness.py)

## Sufficient evidence of admission closure

Fix one scope with a finite, complete inventory of gate identities. Assume an exclusive recovery selector can stop any new issuance under older decisions, authenticate recovery fences, and select a fresh number q above all prior issued or decided control, including delayed prepares and summaries. It has permission to propose one new configuration. The model assumes gates retain their floors across selector loss, check authority at each whole append, and cannot be bypassed. It also assumes the recovered selector cannot issue an old binding from stale memory. A new abort summary based on stale state would break this last condition.

For each gate i, let mᵢ be the highest number of any *issued* summary that can enable i, with −1 if there was none. Count the initial enable too. Use an upper bound on mᵢ if actual old messages may have been dropped or the issuance record deliberately over-approximates. Let fᵢ be a verified lower bound on the gate's nondecreasing control floor. Then:

- If **mᵢ < fᵢ**, the gate is closed and all eligible old summaries are below its floor. An open gate would have a floor equal to the number of an eligible summary it accepted. Only a new eligible summary could raise that floor while leaving it open.
- If the inequality is unproved, a current fence at q supplies both closure and a floor above every old summary. A trusted, irreversible exclusion of the real admission path can supply equivalent effect-side evidence. A management timeout supplies neither.
- A selector can commit the replacement once every gate is covered. Delayed old prepares can only close a gate and raise its floor. Delayed absent summaries cannot open it. A fence and a local append serialize at the actual effect boundary. After the fresh commit, only the new selected members get the new enable.

With exact floors and all issued summaries still deliverable, the criterion is exact. If mᵢ ≥ fᵢ, immediate delivery of an eligible summary with number mᵢ can open the gate. Conversely strict inequality excludes that path and immediate service. In particular a closed gate alone proves too little, and an upper bound equal to the certified floor still allows opening.

This yields two constructions with different availability. A full census can fence every gate without retaining old membership, given every path is enumerable and responsive. A complete issuance journal and trustworthy floor evidence can skip an absent or never-enabled path. Such a journal can retain a per-gate eligible-summary ceiling instead of a sequence of memberships. It must reflect each enable before it escapes. A conservative overclaim may needlessly block on an absent gate. A protected exact membership record is another way to preserve the original requirement to obtain votes from the current members. The alternative recovery rule weakens that **participation requirement** to effect closure. If owners themselves have approval rights, or new membership depends on an unobserved decision, data-path closure alone cannot authorize the replacement. General reconfiguration systems also separate configuration authority from data handling; their mechanisms do not settle which ASES contract applies. [Lamport, Malkhi and Zhou, *Vertical Paxos and Primary-Backup Replication*](https://lamport.azurewebsites.net/pubs/vertical-paxos.pdf)

## Minimum evidence for exact availability

Suppose a compact checkpoint is the only distinguishing information besides the set R of gates that can be fenced. Let E be the exact set of old admission paths, fixed for this question. Success is possible exactly when E ⊆ R, under the admission-closure contract and with all other prerequisites available. If every R is possible, distinct exposure sets need distinct checkpoint values: choose a gate in the symmetric difference and make it the only unavailable one. The two sets then require opposite answers. A bitmap of E suffices. If k gate identities can be independently exposed or unexposed, the minimum alphabet is 2^k. For restricted failure sets the equivalence is coarser: merge exposure sets exactly when all allowed R give the same answer. The proof concerns a frozen recovery observation. It does not imply that the exact bitmap is cheaply maintainable under in-flight issuance or cross-domain crashes. Live floor attestations or other new observations can change the required checkpoint.

## Executed evidence and open obligations

Run `python3 docs/research/kernel-0/recovery_membership_exposure.py`. The model independently enumerates changing proposals, aborts, durable fences, issued summaries and delayed delivery before rolling the selector's view back to the initial image. From each decided state, a continuation oracle tests immediate and delayed old admission, before and after fencing every possible set of responders. The journal predicate is checked against that oracle.

| Gates, attempts | Reachable states | State and fence-set checks | Blind observation classes conflicting on progress | Safe journal cases with an unavailable selected gate |
| --- | ---: | ---: | ---: | ---: |
| 2, 3 | 6,353 | 16,484 | 51 | 317 |
| 3, 2 | 3,195 | 16,088 | 129 | 400 |

The model finds a matching pair with A closed at floor 1 after preparing both fixed proposals and preserves the genuine, delayed summary only in the exposed continuation. It tests all 256 exposure-set availability signatures for eight variable gates. Separately, a new run of the earlier unchanged fixed-membership selector model reproduced the reported 6,769 one-gate and 4,219 two-gate restores per rule, including the zero harmful continuations under the repaired rule in both bounds. That replay does not turn the old model into a changing-membership proof. [New exploration](recovery_membership_exposure.py) · [Earlier fixed-membership model](glm-g4/selector_rollback_recovery.py)

**Outstanding.** The experiment restores a fixed initial image after a decided state, with at most one recovery cut, a complete fixed identity inventory and no publication from stale decisions. It does not model arbitrary selector images or pending attempts at the restore, surviving management acknowledgments, content preservation or destruction, selector failover, or implementing a crash-consistent journal. Publication must still bind the new configuration to its actual authorization. The exact availability lower bound and the sufficient fencing rule concern admission. In particular a gate can contain accepted work even if every admission path from it is closed. Losing or skipping that gate can still violate custody. [Custody boundary](glm-g4/Custody-after-a-forgotten-commit.md)
