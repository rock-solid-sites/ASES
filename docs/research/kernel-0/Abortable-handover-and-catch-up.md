---
title: Aborting a handover without reviving obsolete votes
version: 0.2.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Aborting a handover without reviving obsolete votes

A selector may need to abandon a replacement when one resource owner is unreachable. It must then preserve the *original* tenure. Installing a new grant on every attempted replacement would invalidate that contract. Conversely, if two attempts use the same target identifier because the first aborted, a genuine vote from the abandoned attempt can arrive after its gate has reopened. Counting it in the next attempt can leave the old tenure able to append after a successful replacement. The fixed-membership construction previously excluded abort. [Fixed-membership proof](One-handover-across-resource-owners.md)

## A protocol in which missed aborts need no replay

Fix one W/P, a nonempty finite set of independent whole-append gates, one durable selector and an initial tenure 0. Each initiated attempt gets a nonreused increasing number. The selector stores d, the last decided attempt, and c, the attempt that last *committed* (or 0). It can have one pending attempt q=d+1. Successful replacement selects a fresh grant identified by q. Abort leaves the prior grant current. Each gate durably stores t, its largest processed control number, and either an open tenure h or closed status. Initially d=c=t=h=0. Messages bind W/P, member or membership as appropriate, and selector identity.

| Event | Effect |
| --- | --- |
| Start | Durably initiate q and permit authenticated prepares for q. |
| Gate prepares r | On a genuine prepare with r>t, atomically close the gate and store t=r before issuing a receipt bound to this attempt and member. A delayed prepare from an already aborted attempt can briefly close a lagging gate. |
| Abort q | The selector can durably decide abort without any vote. Set d=q, retain c. Acknowledgment promises that the previously selected tenure remains selected. |
| Commit q | Require a genuine prepare receipt for q from every distinct gate. Set d=c=q and authorize the successor. The selector can produce only one terminal decision for an attempt. |
| Gate catches up | On an authentic summary (r,b) of a decided prefix, where b was its selected tenure, apply only if r≥t. Atomically set t=r and open for b. A gate may request the latest summary. |
| Append | An open gate checks the scoped issuing tenure against h at the whole append. Closed gates defer definitive decisions. |

The authority can retransmit the latest durable (d,c) and the corresponding current grant binding. It need not retain or send the intervening list of aborts *for gate catch-up*. Acknowledging old management-request outcomes by request ID would be a different retention contract. Within a pending attempt a prepared gate must be able to retransmit its vote after a lost reply; its durable state and the bound pending identity suffice. Suppressing duplicate vote-delivery steps is safe for the model below because it tests existence of a matching receipt.

**Arbitrary-member proof.** Choose one gate and let v be the greatest attempt for which it ever voted, initially zero. Maintain c≤t≤d+1 with t≤d when there is no pending attempt, v≤t, and an open gate has h=c and t≤d. A prepare strictly raises t and closes the gate, preserving the bounds. Abort increases d without changing c, so an open gate stays legal. Start only relaxes the bound. At commit the matching vote proves v≥q, hence t=q. The gate must be closed because q>d. After commit c=d=q, preserving the invariant. This reasoning applies to every gate before the selector returns success.

For any genuine summary (r,b), r≤d. Whenever r≥c, the selected tenure at r equals today's c, because no later commit could have occurred without increasing c above r. An applicable summary has r≥t≥c, so opening for b is safe. An old summary received by a gate that voted for a still-pending q cannot reopen it because r≤d<q=t. Delayed messages and locally remembered votes therefore pose no safety problem under the explicit durability and authentication assumptions. This proof allows arbitrarily many aborts between two commits.

**Progress with limits.** With no pending attempt, t≤d at every gate. A single delivery of the latest summary per lagging gate therefore restores the whole open configuration. Catch-up traffic per gate can be independent of the number of missed aborts. To commit a new uncontended attempt, deliver its prepare, collect and deliver all matching receipts, commit, and deliver the new summary. Each gate can freeze even if it missed earlier summaries. These are finite successful schedules. Eventual progress requires a live selector, suitable retransmission and delivery, and for commit a responsive full membership. Aborting can finish without the unavailable member. It cannot guarantee immediate service at a disconnected gate already frozen. If the selector itself is unavailable after collecting votes, a gate cannot infer whether commit occurred. Unilateral timed reopen would need a different contract.

## Evidence

`python3 docs/research/kernel-0/abortable_handover.py` enumerates every commit/abort choice and every useful delivery of every issued prepare or summary. The oracle retains all decisions so even an obsolete authentic summary can arrive. Reachability visited 515 states for one gate/five attempts, 1,862 for two/four, and 5,093 for three/three. At every decided quiescent selector state each lagging gate can apply the latest summary directly. Allowing votes from any attempt since the last commit produced a reachable stale append after abort and a new commit. Allowing an older summary to reopen a gate produced a stale append even in the first attempt. Printed paths are shortest for those admission mismatches in this event alphabet. [Schedule search](abortable_handover.py)

`z3 docs/research/kernel-0/abortable_induction.smt2` checks initialization, start, prepare, abort, commit and catch-up for the arbitrary-member invariant and both negative controls. Z3 4.13.3 returned six `unsat`, then two `sat`. The mathematical prefix argument supplies the summary axiom in the formula. The proof also relies on complete membership, durable monotonic state, authentic scope and atomic binding of the terminal decision. No selector failover, storage rollback or distributed implementation was tested. [Arithmetic obligations](abortable_induction.smt2)

The new distinction is between an *attempt number* and the *selected tenure*. A single increasing sequence supplies both identifiers if a grant is selected only on successful attempts. CONNECT must bind receipts to the attempt even when the current grant survives abort. ORDER must preserve the unique decision and the gate's control floor. ISOLATE must preserve the evidence across reopen and recovery. The next section tests whether that proof survives changes to membership.

## Joint refinement with changing membership

A direct conjunction of the two earlier proofs fails. Start with an empty membership and commit the addition of gate i. The outgoing set owes no votes. Before i receives its enable it can have t=0 while the selector has c=1. The fixed-membership invariant c≤t is false in this reachable, safe state. Conversely, blindly applying a new summary that only names a tenure can open a removed member. The summary now needs to establish whether i belongs to its decided configuration. [Changing-membership proof without abort](Changing-the-set-of-resource-owners.md)

For each pending attempt freeze one proposed membership N. On abort keep (c,M), where M is the current membership. On commit require receipts from every member of M, then install (q,N). Empty memberships, repeated memberships, and disjoint memberships are permitted. Issue prepares to the outgoing membership. In an authenticated decided summary, bind the attempt, selected tenure and membership to one decision. A gate accepting a summary with r≥t opens only when that summary includes it. Otherwise it advances t and stays closed. A closed gate defers any final eligibility decision. The remaining rules are as above. Unique identities and protected nondecreasing t survive removal and rejoin.

Here is the missing induction variable. For the chosen gate let u be the **latest decision number** whose summary included that gate with a binding now obsolete, or −1 if none exists. The number is the summary's decision number, even if it represents an abort that repeated a much earlier selected tenure. Maintain u<t, v≤t≤d+(one if pending), and an open gate is a current member with h=c and c≤t≤d. There is no lower bound c≤t on closed gates.

- Initially the old-summary set is empty. Prepare raises t and closes. Abort retains membership and selected tenure, so its new summary introduces no obsolete binding and u is unchanged.
- At commit, if i belonged to M, the matching vote implies t=q and closure. The summary at the immediately preceding decision d included i. All previously current eligible summaries become obsolete, and the latest such summary is now d. Set u=d<t. If i was absent, it was closed and every earlier eligible summary for i was already obsolete. Keep u. Either case allows arbitrary new membership N.
- If an accepted summary includes i with an obsolete binding, then r≤u<t, contradicting the acceptance guard. Thus every accepted eligible summary carries precisely the current binding. Every accepted absent summary closes the gate. Other gates' steps preserve these conclusions. With no pending attempt each gate has t≤d, so the latest summary can directly bring each to the correct open or closed state.

The obsolete-summary bound is proof state. An owner implementing the protocol stores t and its mode/binding, while the selector supplies a trustworthy current snapshot. This shows one catch-up delivery per gate suffices after arbitrarily many membership changes and aborts when the selector is quiescent. The size of a complete configuration can grow with membership. A compact membership representation needs its own evidence.

The schedule script now additionally enumerates every proposed membership subset in its bounded dynamic runs, including all abort choices and delayed old prepares and summaries. Starting with the last identity absent, it reached 708 states for one gate/four attempts, 2,235 for two/three, and 2,220 for three/two. The fixed-membership counts remain reproducible. Waiting only for the intersection of old and proposed memberships allowed a removed open gate to append immediately after commit. The [joint SMT obligations](abortable_membership.smt2) returned six `unsat`, then two `sat` with Z3 4.13.3. The final queries respectively weaken the voter set and permit a lagging gate at an absent-to-present transition. The latter illustrates a failed proof premise, not a protocol failure.

This resolves the joint admission and catch-up question for fixed identity semantics, single-scope serialized proposals, complete outgoing membership and deferred answers at closed gates. A strong promise that a removed gate immediately returns a definitive nonmembership answer changes the observation contract. Transfer of accepted contents, selector failover, unknown membership, compaction across identity recycling and progress with unavailable required members remain open.
