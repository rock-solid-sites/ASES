---
title: When may a continuing attachment reuse an authority identifier?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-25
---

# When may a continuing attachment reuse an authority identifier?

A replacement test that passes once can miss an unsafe implementation indefinitely if the test resets the owner between runs. Keep the same work and attachment alive, delay a fresh write, and replace the execution until its admission evidence repeats. At that point even a perfectly atomic comparison against the *current* owner record can accept the wrong write. This result constrains the owner interface; it supplies neither an owner implementation nor evidence of a defect in an existing stack.

## Evidence admitted

| Input | Established within its stated scope | Open obligation |
| --- | --- | --- |
| [Neutral requirements](Kernel-0-Evidence-Packet.md) and [September Work Unit reduction, especially T5–T10](https://github.com/rock-solid-sites/ASES/blob/741abfb905a270a90cab62213cf74fcda257b223/docs/research/work-unit-0/Work-Unit-0-Foundational-Reduction.md) | Durable bounded work, replaceable activity, surviving restrictions and currentness are requirements. The reduction gives counterexamples for recovery and transfer. | A recovered authentic old snapshot may still be obsolete. Determine which failures the owner covers. |
| [September guarded transition semantics](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-Abstract-Semantics.md) and [assurance record](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-Assurance-Continuation.md) | Distinguishability and whole, coherently ordered commitments were already derived. Bounded models and local realization experiments have explicit supervisor, storage and effect assumptions. | No general refinement for independent stores, arbitrary policies or hostile rollback. |
| [Round 2 comparison and critiques](../astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md) | Direct tenure grants and delegated lineage are distinct candidate constructions. A guard supplied by the caller may omit a dependency. | The public comparison identifies ISOLATE / CONNECT / ORDER but leaves their original definitions unverified. This paper uses the triad as a working hypothesis and states its interpretation below. |
| [Pinned W1–W6 evaluation](https://github.com/rock-solid-sites/ASES/blob/8de559c78272bf639a82d284572e218a14cc1269/docs/research/kernel-0/work-unit-adequacy-result-2026-11-24.md) and [review correction](../astra-followup-20261125/round25/WORK-UNIT-AUTHORITY-RUST-CUSTODY.md) | Historical W1–W4 show one-use launch, conservative unknown custody, exit-bound finalization and unlaunched cancellation. Native content registration has separate admission/epoch evidence. | Neither stack demonstrates an owner-authenticated continuing W/P with X→Y mutation fencing. No historical run repeated here. |

## A narrow refinement target

Fix one durable pair (W,P), a write to its protected contents, and owner-authorized replacements. A *tenure* is one grant interval at P. ISOLATE must keep the accepted contents and grant selection outside unilateral worker control. CONNECT must let an ingress bind each request to evidence of its actual grant, preserved through intermediaries. ORDER must serialize the replacement with the eligibility check **and whole append** at the owner. These are obligations placed on a candidate interpretation. The historical names alone entail none of them.

The reference state is (W,P,current tenure,accepted sequence). Replacement changes only current tenure. Delivering a fresh write appends once if its provenance equals the current tenure, otherwise it leaves the sequence unchanged. An observation of an already committed result is a read. A queued request in this experiment has never crossed the authoritative append point. Delivering a previously committed external obligation would exercise a different contract. An accepted write followed by replacement therefore remains in history, while reversing those owner events denies the same write. An executor loss with no owner transition leaves the durable projection unchanged. This is a specification argument about W5/W6. It assumes atomic persistence if restart of the owner is in scope.

## Lower bound and constructive escape

Let D be the number of distinct authenticated admission values possible for otherwise identical, individually permissible fresh writes to this pair. Suppose each tenure must be able to write, a still-deliverable old request may be delayed across arbitrarily many replacements, and admission has no other way to distinguish origin. Require progress through D replacements even when each prior tenure has left such a request pending. Among D+1 tenures two receive the same value. At the later tenure compare delivery of the earlier write with delivery of an identical current write from the same pre-state. All admission inputs match, but the specification requires opposite decisions. Even nondeterminism cannot guarantee both safety and current-write acceptance. An atomic counter modulo D therefore fails. Random identifiers give a probabilistic collision contract if the value space is finite. Counting hidden channel incarnations or protected receipt identifiers as additional evidence increases D.

The tight local condition for the tag-equality policy is **absence of any deliverable stale write matching the current tag**. Necessity follows by scheduling that delivery first. Sufficiency follows by induction if issuance authenticates the current tag, retired issuers can no longer mint requests, and replacement may reuse a tag only when no still-deliverable request carries it. Delivery removes a message and cannot introduce a collision. Replacement preserves the condition by its guard. This permits reuse even with unrelated pending traffic. A permanent delay can block a cyclic allocator. An allocator free to choose among tags can grant immediately if a free tag exists. If every tag is contaminated, changing allocator strategy cannot restore both guarantees.

The drain premise is an obligation on *all* ingress paths. Emptying a worker's local queue while a relay holds a copy fails in three stages: the relay retains X's request, P reuses its tag after a local empty observation, and the relay delivers it. Killing X also leaves that history possible. A trusted channel cut that discards all old deliveries, or a durable ingress decision invalidating those messages before tag reuse, can discharge the premise. A copied bearer still usable after the cut defeats it. No additional primitive follows unless the three proposed operations are specified tightly enough to rule out all such constructions.

## Reproduction and discriminating controls

Run `python3 docs/research/kernel-0/tenure_reuse.py` from the repository root. The model enumerates reachable schedules with one fixed pair, 1–5 tags, at most one fresh send per tenure, and at most D+1 replacements. Delivery may occur in any order. The observer knows the origin tenure; ordinary tag admission sees only its residue. The drain variant consults queued tags under an assumed closed transport. Memoization merges equal future states. Since the only write operation is a single append at delivery, an incorrect append decision is detected at the first differing event. History storage itself is outside the executable model.

| Admission rule | Shortest mismatch in the fresh run (events, by D = 1,2,3,4,5) |
| --- | --- |
| Eligibility cached at issuance | 3, 3, 3, 3, 3 |
| Atomic comparison with current cyclic tag | 3, 4, 5, 6, 7 |
| Atomic comparison plus collision-aware replacement guard | No mismatch in any of the five bounded searches |

For D=2 the shortest tag failure is send by X(0), replace with Y(1), replace with Z(0), deliver X. For D>1 the original two-tenure W6 race alone cannot produce the wraparound failure. Positive schedules include send/deliver before replacement and replace/send/deliver by the new tenure. Both guards allow indefinite reuse on a fully drained transport. The safety search allows a blocked replacement and proves no scheduling or recovery liveness.

## What would count as implementation evidence

For the owner crosswalk, identify the durable selector for (W,P), the actual issuer of trustworthy evidence at ingress, every queue and alias from which an old write can reach the protected sink, and the exact event that admits the append. Locate the durable outcome for replay after a lost reply. A launch ID or content epoch answers only part of that crosswalk. Verify each candidate transition projects to a permitted reference transition, preserves prior accepted results, and admits both W6 orders with owner-visible evidence. Exercise a delayed fresh write separately from a retry of an already accepted write. Force identifier reuse or verify the exhaustion/refusal boundary under the declared issuer and recovery assumptions. If multi-attachment or delegated writes are supported, verify all paths sharing that sink and their revocation dependencies. Local per-attachment proofs compose only when those dependencies are disjoint or coherently ordered.

**Confidence and limits.** The indistinguishability result is deductive under the stated finite-observation and progress premises. The executable result is a bounded self-check, with no independent replay or runtime conformance evidence. It assumes trusted issuance, complete mediation, immutable in-flight provenance and an atomic owner. It excludes delegated writes, crash/recovery, hostile transport, external effects, multiple attachments and revocation of fresh authority intentionally regranted to the same physical worker. ISOLATE / CONNECT / ORDER remains viable for this slice under those obligations. Its historical equivalence to guarded commitment, general adequacy and irreducibility remain open.
