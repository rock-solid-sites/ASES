---
title: Changing the set of resource owners at handover
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Changing the set of resource owners at handover

An owner can owe a fence even if it has never served a request. Give A an enable certificate for phase 0 and delay its delivery. Remove A, complete a replacement, then deliver that genuine certificate. A can now accept a fresh append from the displaced tenure. Waiting for all *currently open* owners or for all owners common to the two configurations misses A. There is no need for a forged message, a concurrent append or a rollback in this history.

## Scope of the change

At a single serialized decision for a continuing W/P, move from tenure e with eligible owner identities M to e+1 with eligible identities N. Each enabled owner can independently perform a whole local append. The public contract permits deferral during reconfiguration or while enable delivery is delayed. A completed append must belong to the current tenure at a currently eligible owner. State belonging to removed owners remains protected. Reconfiguration here changes eligibility. Migrating accepted bytes or serving an atomic cross-owner snapshot would require additional transitions. This extends the fixed-membership construction and inherits its local effect and authority assumptions. [Fixed-membership proof](One-handover-across-resource-owners.md) · [Neutral requirements](Kernel-0-Evidence-Packet.md)

## A sufficient protocol

The selector durably orders configurations and issues authentic, scoped enable certificates to exactly the installed members at each decision. A gate begins closed with durable floor zero. It may open at h only on its own genuine enable for h ≥ floor. While open it admits only its issuing scope and installed tenure. Closed gates can defer calls. A prepare for the unique proposed successor makes each outgoing configuration member, **including retained members**, atomically close and raise its durable floor to e+1 before it sends its receipt. Old and duplicate prepares do not lower the floor. The selector commits N only on complete matching receipts from M. It can issue enables to N after commit. Newly added identities need no precommit vote under these premises. Every identity has a unique protected incarnation, or preserves its floor across absence and reuse. Initially no pre-existing enable can target a newly created identity.

A receipt binds the configuration instance, member, scope and transition. An authentic matching receipt proves a floor at least e+1 if floors are durable and never decrease. This permits delayed and duplicated receipt delivery. The abstract guard can therefore read these lower bounds. The selector runs at most one undecided proposal. Reusing a transition identity for a different proposal or selector rollback would need a separate argument.

**Induction for any finite execution.** Fix a gate i. Write f for its floor, h for its open generation (−1 when closed), and u for the greatest certified generation strictly before e at i (−1 if absent). At all times u < f. Also h is closed or i is a current member and h=e ≥ f. Initially both clauses hold. Prepare raises f and closes the gate. A delayed enable older than e has value at most u and cannot reopen i. Only a current member has an enable for e. At commit, if i was a member, its fence gives f>e and it was closed. Its new u is e. If i was absent its earlier u remains, and it was already closed. Both clauses carry through commit whatever the next membership. Changing another gate leaves the argument intact. Universal generalization proves admission safety for a changing population over arbitrarily many reconfigurations. An open gate that returns a definitive stale reply about an older grant also has the current generation to justify it.

The distinction between u and “latest certificate issued” matters for a gate rejoining after many absent rounds. Its floor can be less than the current generation while its new certificate is valid. Using u keeps the whole older prefix below the floor and allows this gap. The proof treats absence as protected closure. A writable alias outside the gate or reusing physical identity with a cleared floor violates that premise.

**Necessity under independent service.** If a still-deliverable old enable at i can open an independent path and no event visible on that path distinguishes the new decision, delay all further traffic to i. After commit, issue the same old append that would succeed if no replacement occurred. The path has identical inputs and must answer differently under the two contracts. A selector needs evidence excluding that possibility before it can promise removal. A durable fence at i suffices. An external mechanism that irrevocably disables the whole path could supply equivalent evidence. Incoming-only voting cannot establish the fact for an independent outgoing path. A failed outgoing member can consequently block the protocol, including a transition to the empty set.

## Checks

Run the scripts from the repository root.

- `python3 docs/research/kernel-0/membership_fences.py` enumerates every next subset of a fixed universe, including empty, unchanged, disjoint and rejoined sets. It retains every prior configuration so authentic enables remain deliverable indefinitely. One gate/four changes reaches 109 states, two gates/three changes 549, and three gates/two changes 979. Each full-length membership sequence admits a schedule reaching a fully activated final membership. This existential check says nothing about progress on an arbitrary schedule. Both incomplete-vote variants exhibit the four-event delayed-enable failure in the opening paragraph. Clearing the durable floor on recovery also produces an old append after a fully fenced commit. [Schedule search](membership_fences.py)
- `z3 docs/research/kernel-0/membership_induction.smt2` checks initialization, prepare, enable, commit, and the two incomplete-vote controls for an arbitrary member. Z3 4.13.3 returned four `unsat` and two `sat` answers. The executable search supplies reachable failures for both satisfiable induction controls. The symbolic proof models arbitrary older enables by an overapproximation that includes every nonnegative generation up to u. Its linkage to receipt verification and whole local effects is the protocol argument above. [Arithmetic obligations](membership_induction.smt2)

**Implication for the working triad.** ISOLATE would have to preserve the floor and accepted effects even after removal. CONNECT would have to bind each certificate and receipt to the right scope and identity. ORDER would have to place the local append, fence, and global configuration decision as specified. Under those contracts, separate admission by all joining gates before commit is unnecessary for safety. Omission of outgoing paths, false receipts, recycled identities without preserved floors, owner loss of accepted data, and an implementation's ability to enumerate every writable path remain distinct assurance obligations.
