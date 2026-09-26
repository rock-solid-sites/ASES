---
title: Kernel-0 Verification Obligations
program: EDASES
layer: Research
document_type: Provisional Verification Specification
status: Provisional
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
crosslink_issue: 566
---

# Kernel-0 Verification Obligations

This is the minimum verification target for the provisional [abstract semantics](./Kernel-0-Abstract-Semantics.md). A checked model proves only the properties and assumptions it represents. No proof tool or realization is selected.

## Model invariants

For a declared authoritative view `σ`, proposed whole effect `q`, guard `G`, effect relation `E`, and critical invariant `I`:

1. **Admissibility and whole effect:** every committed `q` satisfies `G(σ,q,f)`, `E(σ,q,σ′)`, and `I(σ′)` using one coherent current validation view. A denied `q` causes no authoritative effect; pending has no completion guarantee.
2. **Current authority:** an authority change is itself guarded. A request ordered after invalidation cannot commit using only the invalidated authority. An old authority representation cannot become eligible again by accidental reuse while old attempts remain possible.
3. **Acyclic conflict history:** all independently resolved commitments that can change one another's guard or invariant result admit one common acyclic order consistent with their validation views and completed-before-initiated precedence. Unrelated commitments need no stipulated order.
4. **Configured exclusivity and rights:** no reachable authoritative view violates the declared conflict or rights policy. Delegated rights are a subset of current delegable parent rights when that policy is claimed.
5. **Executor-loss continuity:** loss or replacement of an executor preserves the declared continuing work/position observation and all authoritative information needed for a later valid continuation. Current authority may change only through a guarded event.
6. **Protected-meaning closure:** every event that changes accepted authoritative meaning, including mutation of a live external dependency, is represented by a guarded commitment or excluded by an explicit trusted immutability/mediation assumption.

Old-grant exclusion is unconditional once that grant is invalidated. Exclusion of the old physical producer after it obtains a new valid grant is a separate, conditional source-binding claim. No general exactly-once, eventual progress, or independent authority-service restart property is inferred.

## Model-adequacy obligations

Before exhaustiveness is meaningful, the model must contain enough state to distinguish current from invalidated authority, old from replacement evidence when different outcomes are required, work from execution lifetime, position continuity, configured rights/conflicts, and every live external dependency that can change authoritative meaning. It must model relevant external facts with their trust and ordering assumptions. A caller-supplied assertion alone cannot satisfy an authority premise.

The event alphabet must allow proposal, commit, deny or pending, authority update, executor loss, replacement, compatible and conflicting work changes, and any external fact or protected effect the claim includes. It must represent materially different orders, including overlapping operations and conflict cycles. Non-vacuity requires at least successful establish, authorized change, replacement, and continuation histories. A model that only rejects is inadequate even if all its safety invariants hold.

## Trace properties

| Regression trace | Required result |
| --- | --- |
| Read authority; invalidate it; attempt commitment based on the old read | Deny the later commitment. |
| Race replacement with an old request in both orders | Before replacement may commit; after replacement cannot use old authority. |
| Reuse or replay old evidence after replacement | Old evidence remains invalid. If the old producer presents genuinely new valid evidence, physical exclusion needs the declared source-binding rule. |
| Two writes each validated against `(0,0)` but together violating `d1+d2≤1` | At most one independent proposal commits. |
| Three proposals with guard dependencies requiring `A<B<C<A` | All three cannot commit independently; pairwise consistency is insufficient. |
| Executor loss between validation and effect, or effect and durable record | The authoritative view after recovery corresponds to whole allowed commitments at declared granularity; no accepted invalid partial state. |
| A stale executor changes an accepted live external referent | Reject/prevent the change or fail the protected-meaning claim. Candidate material awaiting separate acceptance is a different case. |
| Conflicting grants/revocations and an over-broad delegated grant | Every accepted order preserves configured rights and exclusivity. |
| Authorization of an outside action before invalidation, with consequence afterward | Apply the declared authorization-point and cancellation contract; no universal outcome is inferred. |
| Commit followed by lost acknowledgement and replay | Authoritative outcome remains definite. A repeated authorized request may commit again; exactly-once behavior needs separate declared semantics. |

If independent authority-service restart, storage interruption, or corruption is claimed, add traces for the exact covered failure and recovery points. If external actions are in the protected set, include their effect-sink ordering and irreversible completion behavior. These are profile-specific additions.

## Realization-conformance obligations

A realization must define an abstraction from its concrete records, memory, external dependencies, and trusted services to `σ`. Every protected concrete effect must refine one permitted whole abstract commitment; a denial refines a no-effect outcome. Concrete validation and effect must behave as one coherent abstract transition across all relevant dependencies, including three-way conflicts and cross-component authority updates. Executor loss must preserve or reconstruct the declared authoritative view. If an external sink is protected, its authorization point and effect ordering must refine the abstract contract. An implementation cannot claim a smaller trusted boundary by placing an authoritative fact or mediator outside its named kernel component.

The mapping must also account for observations: a caller may not receive a commitment acknowledgement, and speculative external work cannot be treated as authoritative before guarded acceptance. Independent restart, safe retry, or progress need separate correspondence arguments if claimed.

## Trusted assumptions and claim boundary

State the origin of initial management authority; authenticity, freshness, non-confusability, and any physical-source binding of authority evidence; correctness of the supplied policy and conflict relation; integrity and availability of retained state across executor loss; trust/freshness of outside facts; immutability or mediation of live external dependencies; and any failure classes excluded beneath the retained-state boundary. Implementation-specific compiler, runtime, OS, storage, circuit, or hardware assumptions belong in a later realization claim.

**WHY:** Each obligation closes a specific false-confidence path: stale admission, indistinguishable authority, cyclic validation, hidden authoritative dependencies, invalid partial recovery, or model-to-realization mismatch.

**WHAT:** The Evidence Packet, the abstract semantics, the finite Work Unit adequacy attempt, and open Astra falsification of the candidate.

**HOW CERTAIN:** Evidence-based verification target. The stated counterexample traces logically invalidate models that admit them; adequacy and realization conformance remain to be demonstrated.

**WHAT-NOT-TESTED:** No model has been exhaustively checked, no concrete realization has been mapped to this specification, and no external sink, substrate restart, or liveness guarantee has been verified.
