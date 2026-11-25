---
title: Matched reasoning task — Work Unit authority and replacement
version: 0.1.0
status: Experimental
authority: Derived
last_updated: 2026-11-25
---

# Work Unit authority and replacement

## Question

Determine the minimum semantic and trusted-interface distinctions necessary to support Work Unit continuity and execution replacement, and whether the existing experimental mechanisms can supply them. Give a justified architectural disposition and the smallest decisive experiment. This is reasoning, not implementation. Do not seek or read previous reviewers' or comparison participants' conclusions.

## Established requirements

- Authoritative state changes must satisfy the substrate's invariants; execution authority is external to the executor. Prompt instructions do not confer authority.
- A Work Unit is durable independently of execution. An Attachment Point supplies durable executor-facing continuity. An Execution is temporary and replaceable. Loss of an executor must not destroy work, and replacement must not create new work.
- Superseded execution cannot make new authoritative mutations merely because it retains old access. Where exclusivity is required, incompatible authority states cannot coexist.
- Single/sequential/concurrent operation and shared/isolated/hybrid resources are configurations, not distinct kernel modes. Work Unit, Attachment Point and Execution are adequacy constraints, not presumed intrinsic Kernel-0 objects. Do not assume any language, store, IPC, capability representation or new primitive.
- Kernel responsibility is limited to authoritative state and permitted change; semantic work judgment, orchestration, resource budgeting and observation are separate concerns.
- W5: same W/P, X superseded by Y; Y can mutate continuing work, new X mutations are denied and historical X outcomes remain readable.
- W6: X mutation races with replacement. Either X commits before replacement and subsequently becomes ineligible, or replacement commits first and X is denied without mutation. Y acts only after current eligibility is granted. Ordering comes from authority, not transcript timestamps.

## Experimental evidence (not a merged architecture)

1. Rust resource-control at PR #42: a job has one durable launch intent, same launch ID observes, different launch ID is refused while active; actual child custody is in memory. Cold loss yields unknown, no blind PID adoption, relaunch or capacity release. Exact matching exit observation is required before finalization. Unlaunched cancellation is atomic and replayable but is not replacement. Historical W1-W4 evidence supports narrow local ledger/custody claims; no fresh rerun this round. Neither job/launch identity nor PID implements durable W/P or X/Y eligibility. W5/W6 not represented.
2. Native owner at PR #38: selected protected CURRENT records ownership, registrations, selected content, epoch, lifecycle, pending effects; Session.commit publishes a new CURRENT. Owner.locked obtains F1 BEGIN IMMEDIATE, L5 writer flock, L6 BEGIN IMMEDIATE; native effect guard checks current registration, selector, material and path, reserves before journal append. These are native content/lifecycle mechanisms, not demonstrated Work Unit attachment or execution identity. The UID-2000 manager derives a current envelope from a fresh owner read and a request ID; worker route carries only {"op":"write","payload":request_id}. ControllerProxy forwards requests without a trusted per-execution identity receipt. No current owner-visible X/Y proof. Two-worker UID custody probe #85 blocked on exact image, no runtime result.
3. Native admission PR #84 adds pending-effect exclusion for fresh request IDs under the existing owner guard. Eventless A can remain durably reserved after guarded EOF; journal/witness unchanged; fresh B/C are denied ordinarily. Exact journaled A can be reconciled with validated journal/witness and historical replay does not append. Distinct owners can progress. Seal remains allowed after reservation, disposal denied while pending. A1-A7 passed earlier fixed-head CI. Test-only PR #98: stale-selector same-A retry denied 409; refreshed same-A retry returns reconciliation-required 503, one unresolved reservation, no new journal event. One simultaneous seal attempt refused while the guard was held, not generalized seal denial. A7 not rerun in #98. No cancellation/timeout rule for eventless A. No demonstrated execution replacement or full integration of the stacks.

## Deliverable

Using only the supplied evidence, give:
- A minimal realization-neutral authority/continuity model and trust boundary; identify necessary versus derived distinctions and why.
- A concrete counterexample to any weaker design you reject, including a stale request racing with supersession and an in-flight effect with unresolved publication/settlement.
- Whether an existing owner is a plausible experimental seam, what it would need to verify and which guarantees remain unsupported; distinguish authorization, custody, history and external effects.
- A recommendation and cheapest discriminating acceptance histories, including what would falsify the recommendation. Separate known facts, inferences and unresolved choices.

Return one concise reasoning report. No edits, tests, agent launches or additional retrieval. A missing fact should be stated as an uncertainty, not invented. Do not choose a production implementation or add a new Kernel primitive without showing necessity.

## Evidence provenance (coordinator receipt; no additional retrieval required)

- Kernel-0 Evidence Packet at a02df749b4b3da88d3f88c1712623cec6ad5d963, docs/research/kernel-0/Kernel-0-Evidence-Packet.md.
- Adequacy packet at 38a61d2c28c68bb6bc43c3d0d42d2b76a575a50f, docs/research/astra-prelaunch-20261123/WORK-UNIT-ADEQUACY-TEST-PACKET.md.
- W1-W6 result at 8de559c78272bf639a82d284572e218a14cc1269, docs/research/kernel-0/work-unit-adequacy-result-2026-11-24.md; Rust #42 27bcc552cecb8bbb456b9db3a0a77da1513b31ab.
- #38 0bd51a34700164a5eb77efe98158fa37d1a74e23: native_owner.py Owner.locked/Session.commit/reserve_effect; native_sink.py NativeAdmission.guard; phase-ii-native-recovery-uid/fixture/driver.py ControllerProxy and owner_controller.py NativeManager.current_write.
- #84 bfabf1d95a1f51052679ff4855a2ccc147b97584; #98 2358354c86a2b15e6ddbe81480d4c783a46e5a56; published research record at bb66ef80881cbcb430354c72c5c36c19ef8aaabd, docs/research/astra-followup-20261125/round25/README.md.
