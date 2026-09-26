---
title: Kernel-0 Abstract Semantics
program: EDASES
layer: Research
document_type: Provisional Specification
status: Provisional
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
crosslink_issue: 566
---

# Kernel-0 Abstract Semantics

This is a realization-neutral candidate contract. It defines the smallest presently justified authoritative boundary, not a physical component, data schema, proof tool, or canonical Work Unit ontology. The [reasoning record](./Kernel-0-Reasoning-Phase-Result.md) gives its evidence and unresolved questions.

## Parameters and meaning

An instantiation declares:

- an **authoritative view** `σ`: all distinctions whose current meaning determines accepted work, current permission, or a critical invariant. If an accepted fact depends on live external data, changes to that data belong to this view unless the dependency is made immutable or a later guarded acceptance is the only event that can change authoritative meaning;
- a set of **proposed effects** `q`, each with a declared effect granularity, affected domain, and authority evidence. A policy-generated event that changes authority is also a proposal. A caller's identity or assertion is not itself permission;
- a current **admissibility predicate** `G(σ,q,f)`, where `f` is an optional external fact with an explicit source, freshness, and ordering assumption;
- a proposed whole-effect relation `E(σ,q,σ′)` and critical invariant `I(σ)`;
- a declared failure boundary and, for any protected external action beyond a change in `σ`, its authorization point and meaning under later invalidation.

`σ` is the combined state of whatever trusted components the claim actually relies on. Locating a distinction outside one proposed kernel component does not remove it from the trusted assurance boundary. Two histories may share the same abstract `σ` only if every required future permission and continuity observation is equivalent.

## Resolved transition relation

For an initial state, `I(σ₀)` holds. A resolved proposal has one of these outcomes:

```text
commit:  σ --q/commit--> σ′  only if  G(σ,q,f) ∧ E(σ,q,σ′) ∧ I(σ′)
deny:    σ --q/deny--> σ    with no authoritative effect attributable to q
```

The first line describes a permitted commitment; it does not authorize an arbitrary successor merely because an unspecified predicate is named `G`. Each instantiation must supply enough policy and state to evaluate `G`, `E`, and `I`. The `σ` used for admission and the whole effect is one coherent current view at that commitment point. Validation against an earlier snapshot cannot be detached from the effect if another commitment could change its validity. A proposed effect cannot silently become a different or partial authoritative effect. A request may remain pending without a resolved transition; no eventual response or progress follows. Commitment and the caller's knowledge of commitment are distinct.

Every event that changes the authoritative view must be represented as a guarded proposal, including an externally triggered or policy-generated event. Its triggering fact has a declared trust boundary. A mutable external location that changes an accepted live reference is therefore protected even if no nominal kernel record changes. An external candidate that cannot alter authoritative meaning before a separate guarded acceptance can be changed speculatively outside this boundary. External visibility and reversibility alone do not decide whether an effect is protected.

## Authority and order

Authority is the state-dependent eligibility of a proposed effect, not a privileged property of the proposing actor. An authority grant, restriction, transfer, or invalidation is itself subject to the resolved transition relation. The source of initial management authority is an explicit trusted initial-state assumption.

For any two proposed commitments whose effects can change one another's admission or invariant result, the accepted history supplies a coherent relative order or an equivalent atomic validity constraint. This includes authority changes and affected requests, and conflicting changes to work state. Each request is judged against the relevant current view at its commitment point. A completed relevant change precedes a later initiated affected request. Overlapping operations may resolve either way if the resulting history is coherent. A truthful read made before invalidation cannot justify a commitment ordered afterward. Unrelated commitments need no universal total order, clock, or stored sequence number.

If one producer must remain eligible while a superseded producer is denied, their attempts must differ in a trustworthy admission observation or pass through a trusted mediator that distinguishes them. Current permission for a principal shared by both is insufficient. The old producer must not be able to exercise the replacement's authority; reusing visible authority evidence while old attempts remain possible violates that condition. This requires a non-confusable current authority relationship, not a primitive Execution identity, generation number, token type, or lineage record.

## Continuity and failure

An executor-loss event does not itself erase the authoritative view, end the continuing work, or require a resident executor for inactive work. An instantiation supplies a continuity projection identifying the same work and executor-facing position and the authoritative information needed to continue. Replacement may change current authority while preserving that projection. Work Unit, Attachment Point, and Execution are consumer interpretations, not required kernel object types.

The minimum claimed failure class is loss or replacement of an executor, including any authoritative information improperly co-located with it. If an executor is lost during a proposed protected change, the post-loss authoritative state must still correspond to whole committed effects at the declared granularity; the caller may remain uncertain which outcome occurred. A sequence of separately committed changes may leave an allowed prefix. Independent failure and restart of an authority service, loss of trusted persistent state, corruption below the trusted boundary, and a recovery deadline are not established by the evidence. An instantiation that claims those failures must state stronger recovery obligations.

## Boundary of external action claims

An outside action is necessarily protected when its occurrence changes the authoritative view. Other external actions are protected only when an instantiation expressly claims that their occurrence exercises substrate-governed authority. Such a claim must identify the event at which authority is required, the trusted mediation or conformance contract, and whether invalidation cancels an action authorized earlier but completed later. Exclusion of stale authority at an earlier authorization point does not imply that no previously authorized consequence becomes visible after replacement; that stronger claim requires a coherently ordered boundary at the effect sink or an equivalent cancellation contract. An irreversible protected consequence cannot be made valid by a later denial or compensation. No general transaction system follows from this contract.

## Necessity and limits

| Retained distinction | Why it cannot be removed for the stated claim |
| --- | --- |
| Authoritative view versus unaccepted candidate material | Otherwise a stale external write can change an accepted fact without crossing the guard. |
| Proposal versus whole commitment | Otherwise a caller's action or a valid subpart can silently become an unauthorized authoritative change. |
| Current eligibility versus past permission | Otherwise a superseded executor can reuse old authority. |
| Trustworthy distinction among attempts requiring different outcomes | Otherwise old and replacement executions that look identical to admission cannot be treated differently. |
| Coherent validity view for affected commitments | Otherwise a stale observation can authorize a later invalid commitment, or two separately validated changes can jointly violate an invariant. |
| Continuing information versus executor lifetime | Otherwise executor loss can destroy the same work or position needed for continuation. |

The model does not select a representation for any of these distinctions. A Work Unit instantiation must still provide non-vacuous successful histories and its own continuity, exclusivity, and authority policy. Arbitrary work-product correctness, general scheduling, and unclaimed external effects remain outside Kernel-0.
