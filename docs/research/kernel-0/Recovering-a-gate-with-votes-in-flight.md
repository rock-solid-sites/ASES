---
title: When is an earlier gate snapshot safe to resume?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# When is an earlier gate snapshot safe to resume?

A selector and recovering gate can have identical durable images in two executions that require different recovery decisions. Begin attempt 1 with tenure 0 still active. In one execution the gate has never prepared. In the other it prepared, sent an authentic vote, then lost its new state and restored its initially open image. The selector has received no vote in either execution. In the second the in-flight vote can complete a replacement without closing the restored gate. In the first the gate must close before it can contribute the vote. Comparing the two stores cannot distinguish these histories.

The abortable membership proof used durable nondecreasing floors as a sufficient premise. This investigation characterizes exactly which earlier *genuine* images preserve admission under a narrower failure model. Keep the selector at its true latest state, all other gates healthy, all old authentic summaries replayable, and every emitted vote potentially deliverable. Fix the same gate identity before and after restore. Freeze application access during restore. Only the gate's control record rolls back. Preserving previously accepted bytes is a separate obligation. [Abortable membership model](Abortable-handover-and-catch-up.md)

## Exact condition

Let t be the floor in the image being restored. Let u be the greatest **decision number** of a historical summary that includes this gate with a binding obsolete at the current selector (−1 if none). If there is a pending attempt q for which this gate has emitted a usable vote, let a=q; otherwise let a=0. Then resuming the gate preserves finite-prefix admission safety for every continuation precisely when

```text
t ≥ max(u + 1, a).
```

The target is authority to append under the proper current tenure and membership. The owner may defer while closed. The equivalence assumes that the remaining participants can take their ordinary successful steps on some schedule, allowing a pending move to commit. Each image is from the actual earlier history of this gate and obeyed the original control protocol there. Arbitrary corruption could pair a high floor with an unrelated open binding and needs additional checks.

**Why each term is necessary.** If t≤u, deliver the summary at u. The gate opens with an obsolete binding and can accept an old append. If a=q and t<q, finish the current commit using the escaped vote and matching votes from the other outgoing gates. The restored gate need take no step in that interval. The immediately preceding summary at d=q−1 names it eligible because it belonged to the outgoing configuration. Deliver that summary after commit. Since t≤d, the gate can open under the displaced tenure. Both are permitted schedules under the replay assumption.

**Why it suffices.** With t>u, no obsolete eligible summary can reopen the gate. In a genuine open image, the gate's binding was installed by an eligible summary at its own t (including the initial configuration at zero). If the binding were obsolete that summary would contradict t>u. A genuine image has t no larger than the highest issued attempt, and an image with t=q for a still-undecided q must be closed. If a pending vote exists, the second bound therefore preserves exactly the frozen state relied on by the selector. For the earlier arbitrary-member induction, retain as proof state only votes that can match the current pending attempt. All votes for decided attempts can be discarded from this proof state, since attempts never repeat. The retained vote bound is at most t, even if an obsolete historical vote used a higher number than the recovered image. The original prepare, commit, abort and summary cases now apply to all future steps. This replaces a full-history monotonicity premise by a cut-specific safety condition.

**Recovery consequence.** A selector's empty receipt inbox cannot establish a=0. If the channel may retain a copy, a recovery procedure can conservatively include q for a possibly voting member. A different sufficient procedure is to keep the gate unavailable, establish a quiescent authoritative cut at the selector (including durably aborting a still-undecided attempt where authorized), and install its current summary before resuming. Hold that recovery cut against a racing decision until installation, or prove the corresponding concurrency protocol. At a quiescent cut the latest summary has floor d≥u+1 whenever u exists, since the summary at d itself cannot be obsolete; d≥0 covers the empty case. No pending vote can then count towards a new attempt. Other protocols can invalidate the old message incarnation, but must establish that old votes really cease to be creditable. None of these procedures restores lost payloads or repairs rollback of the selector itself.

## Executable comparison

`python3 docs/research/kernel-0/gate_snapshot_recovery.py` first computes earlier gate images reachable along an actual path to each healthy state of the dynamic protocol. It restores gate zero while preserving the vote evidence that escaped it. A separate oracle enumerates subsequent message deliveries, prepares and decisions, then follows transitions backward from externally incorrect append states. This classifies candidate restored states by existence of a harmful continuation without using the threshold formula. The controls allow delayed prepares to issue an older vote without erasing a previously escaped higher vote. [Recovery search](gate_snapshot_recovery.py) · [Protocol transitions](abortable_handover.py)

| Bounded experiment | Distinct restored protocol states | Safe | Unsafe | Safe source/image pairs with a strictly lower floor |
| --- | ---: | ---: | ---: | ---: |
| One gate, up to three attempts | 443 | 239 | 204 | 178 |
| Two gates, up to two attempts | 696 | 447 | 249 | 247 |

The threshold agreed with the oracle throughout. The last column counts pairs before deduplicating equivalent restored states. In the two-gate run there were 20 restored states in which only replay of an obsolete summary failed the three direct checks (open mode, summary, escaped vote), and 100 in which only reliance on a pending vote failed. No genuine open image failed the immediate mode check alone, as predicted by the proof.

This result specifies the trusted evidence recovery would need. It does not imply that a local gate can observe u or the absence of in-flight votes. The two-store indistinguishability example explains why an implementable recovery test may intentionally be more conservative. If effects or the selector share the rollback domain, extra evidence outside that domain is still necessary for their own guarantees.
