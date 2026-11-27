---
title: Which holders may release immutable Work Unit contents after a handover?
version: 0.2.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Which holders may release immutable Work Unit contents after a handover?

The three-store experiment keeps the outgoing store frozen and uses one transfer. In a repeated transfer, an old “you may delete” message can arrive after a holder has become responsible for the same immutable version again. If the holder applies it, *every* party can have signed the correct handover while the last physical copy disappears. The problem is the lifetime of the storage promise, even with identical bytes and correct authentication. [Single transfer experiment](Transferring-the-accepted-prefix.md) · [Failure-domain criterion](Surviving-content-at-handover.md)

## Baseline protocol with an explicit storage promise

Fix one W/P and one immutable, already validated content version. A selector durably records its required nonempty holder set M. A member must physically retain the specified material. Extra copies at other authorized storage sites are permitted. The fault model here admits message delay, duplication and process suspension; each holder's pledged bytes and control state survive them. It excludes independent disk loss. A higher-level loss contract can use domain-qualified fragments and the recoverability test above to qualify M. Version identity, completeness and rightful access by a successor are separate obligations.

As in the abortable admission model let d be the last decided attempt, c the last commit, and q=d+1 the sole possible pending attempt. A target N may overlap M, be disjoint or equal it. At a holder, t is the greatest processed attempt and held means the bytes are actually pinned. Initially members have the content and t=0. There are three relevant steps.

1. An authentic hold request r>t requires the holder to obtain and validate the correct bytes. It pins them and durably sets t=r before sending its scoped storage receipt. Supplying the number r or a positive acknowledgment alone cannot set held. A holder prepared at q can retransmit its receipt while the move remains pending.
2. Abort leaves M and its promises intact. The baseline commits N only after receiving a matching storage receipt for q from every member of N. The decision is durable and unique. For this storage invariant no outgoing deletion acknowledgment is needed.
3. A holder can act on an authentic decided summary r only if r≥t. It advances t to r. When that summary excludes the holder, it may release its copy. When included, it preserves an existing copy. Reading a summary never recreates absent bytes. In a quiescent configuration, the latest summary suffices to reclaim extra copies even if earlier aborts or removals were missed.

**Arbitrary-member argument.** Keep t≤d+(one if pending) and v≤t where v is the greatest emitted hold vote. When t>d the bytes are pinned. A current holder has held and t≥c. Initialization, prepare, start and abort preserve these facts. At commit a target holder's receipt gives t=q>d, hence held, and the new c=q. At a current member, an applicable summary has r≥t≥c. Its membership equals today's because there has been no later commit. Hence it cannot delete the required copy. A stale hold that arrives at a nonmember can consume space, but the latest summary can reclaim it. These arguments apply to any finite population and history. “Pinned” assumes every deletion path and recovery procedure respects the promise.

The direction of the receipt matters. Admission fences close every independently effective **old** path before selecting a successor. Storage readiness must cover the **future** content promise before old holders may release. A compound acknowledgment from an overlapping member must establish both facts if both are required. A storage receipt by itself says nothing about stale appends. This is a conditional composition for immutable data. Copying a still-changing source must first establish the frozen prefix or another valid cut. [Admission proof](Abortable-handover-and-catch-up.md)

## Checks and controls

`python3 docs/research/kernel-0/retention_handover.py` tracks actual possession as well as votes and history. A copy can be acquired only while some source bytes exist. The schedule search overapproximates delayed holds by allowing them for every historical attempt regardless of whether the aborted proposal named that holder. This adds harmless extra pins in the safety model. It permits every old genuine decision summary to be delivered again. With two holders/three attempts, three/two and four/two, it found 1,081, 2,994 and 42,654 reachable states, respectively. Every required member retained its bytes. At quiescence the latest summary alone can leave each member with exactly its required retention state.

- With only old/new overlap receipts, moving from A alone to B alone can commit with no copy at B. A's valid release then removes the last bytes.
- With all target receipts but no summary floor check, first prepare B and commit it as sole holder. A can now correctly release its copy. Deliver the initial authentic summary to B: it names only A. B releases the remaining copy.

Both are reachable schedule results. `z3 docs/research/kernel-0/retention_induction.smt2` and `cvc5 --incremental docs/research/kernel-0/retention_induction.smt2` also check initialization, start, pin, abort, commit, summary and the two weakened obligations. Z3 4.13.3 and cvc5 1.4.2 both returned six `unsat`, then two `sat`. Independent solvers check the same arithmetic model. Authentic summaries, correct acquisition and surviving physical bytes remain premises. [Schedule search](retention_handover.py) · [Symbolic obligations](retention_induction.smt2)

This proof is sufficient for the baseline. The next section tests whether already-established pins at continuously required holders need renewal. Prompt erasure of old copies, destructive same-identity reuse, changing the immutable version, concurrent scopes sharing physical storage, and authenticated repair after actual disk loss require different contracts.

## A continuously required holder can remain silent

The baseline vote requirement can be reduced for an unchanged immutable version. At a commit from M to N collect fresh durable holds only from **N minus M**. Carry forward the existing pin at every retained member. In particular a change of execution tenure that leaves the version and required holders unchanged needs zero new *storage* votes. The earlier proof's t≥c premise is now too strong: a retained member can span many commits without processing a message.

For an arbitrary holder define a as the latest **decision number** whose summary excluded it, initially −1 if it has always been required. If the holder is currently absent, a=d. A required holder must have actual pinned bytes and t>a. As before, t is bounded above by the last issued attempt, a vote cannot exceed t, and t>d implies pinned bytes. This puts the threshold at the last potentially destructive message instead of the last change of execution tenure.

A target joiner was previously absent with a=d. Its receipt raises t to q=d+1 and pins the bytes. A retained member already has held and t>a, and the new summary includes it, leaving a unchanged. A removal sets a=q with no duty to retain. Abort similarly advances a only at absent holders. An authentic exclusion at r satisfies r≤a; at any required holder it therefore fails r≥t. An applicable inclusion keeps the pin. These cases re-establish the induction for an arbitrary number of holders and changes. Quiescent catch-up still uses a single summary per holder. For h consecutive commits retaining the same m holders, the baseline requires h×m renewed receipts; the reduced protocol needs none from those m for this storage claim. Initial acquisition, later joins, admission fences, and auditing damaged storage have their own costs.

**A join cannot inherit a mere observation of bytes.** Prepare B for attempt 1, then abort. Its bytes are present while the current configuration still requires only A. Begin attempt 2 with B as the sole target. If the selector counts B's present bytes in place of the attempt-2 promise, it can commit and A can release. The delayed abort-1 summary still excludes B and matches B's floor. It can now delete the last copy. The latest absence summary is why continuity of the *obligation* matters, even when the physical bytes have never moved. An independently irrevocable pin covering the new decision would change this premise.

The [schedule search](retention_handover.py) now checks both protocols. The reduced-vote searches reached 1,769, 4,857 and 82,895 states at the same respective bounds, with all required pins present. The seven-event loss trace above was found using only actually addressed prepares. The [reduced arithmetic obligations](retention_reuse.smt2) returned six `unsat`, then two `sat` in Z3 4.13.3 and cvc5 1.4.2. The last cases expose the point-in-time possession error and demonstrate that a retained gate's floor can safely lag the new commit. This resolves receipt reuse for fixed immutable contents under persistent storage promises. A new content version or a temporary gap in membership invalidates the inheritance argument.
