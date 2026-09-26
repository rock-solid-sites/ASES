---
title: Kernel-0 Reasoning Phase Result
program: EDASES
layer: Research
document_type: Reasoning Record
status: Provisional
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
crosslink_issue: 566
---

# Kernel-0 Reasoning Phase Result

## Scope and evidence

This record reports the open derivation, Sol reconciliation, Work Unit adequacy test, and one falsification/reduction pass directed under Crosslink issue #566. The first Astra 6 Medium pass received only the [Evidence Packet](./Kernel-0-Evidence-Packet.md) and the task stated for that pass. The later Astra 6 High pass received the reconciled candidate and an open request to falsify, reduce, or expose missing assumptions. Neither pass selected a realization. This record is a research result, not a change to the Evidence Packet's established requirements.

The Evidence Packet is internally coherent enough for this derivation: its authority, continuity, minimality, and verification clauses can be interpreted together without selecting an implementation. Its references to source work were not independently audited in this bounded session. The packet deliberately leaves policy, failure coverage, continuity criteria, and the scope of external effects underdetermined.

## Retained candidate: a conditional authoritative transition

Kernel-0 is provisionally a **durable conditional transition boundary with revocable authority**. This is a semantic candidate, not a claim that one physical component or location is necessary.

Let `s` denote retained authoritative distinctions, `q` a proposed change, and `x` explicit external inputs on which permission depends. A commitment relation permits `s --(q,x)--> s'` only when the request is authorized by conditions current at commitment, the resulting state preserves substrate-critical invariants, and the whole proposed authoritative change takes effect. Otherwise the request is rejected with no authoritative mutation attributable to it. Authority-changing requests use the same guarded boundary. An accepted commitment need not imply that its caller received an acknowledgement.

The admission rule cannot be an unexplained oracle. Each instantiation must state its authority policy, protected state, critical invariants, external-input assumptions, and the granularity of a proposed change. The boundary must retain, either directly or through a declared trusted component, every distinction needed for future admission and required continuity. Histories requiring different future permission or continuation behavior cannot be collapsed into the same combined trusted state.

This parametric relation is a specification frame, not a proof by itself. A model claiming assurance must represent successful and forbidden transitions, relevant orderings, and external inputs before exploration or exhaustiveness can establish anything. A later realization must separately establish correspondence with that model.

Conflicting authority changes and affected commitments require a **common ordering contract**: a commitment cannot use authority superseded before that commitment. A truthful earlier read of authority is insufficient. Independent changes need no stipulated global order. This contract may be realized by local state, coordinated external state, fencing, or another mechanism with equivalent semantics; the candidate selects none.

Durability here covers executor loss and replacement. No claim is made about arbitrary storage, network, machine, or site failure. External actions are covered only when the stated authoritative boundary mediates them or a trusted component enforces an equivalent contract.

## Minimal testable semantic model

Let `Σ` be the combined retained state on which an assurance claim depends. It includes authoritative state and any declared trusted external state needed by that claim; where the facts reside physically is not fixed. Let `q` be a proposed authoritative effect, including an authority change. Let `f` be a relevant externally supplied fact only when admission depends on it. An occurrence with no authoritative effect can appear in a trace without becoming a kernel transition. An occurrence that changes authoritative state must pass through the same guarded relation as any other proposal.

`Step(σ, q, f, outcome, σ′)` has two outcomes:

- `commit`: the proposed effect, at its declared granularity, is applied as one authoritative change; its permission is valid at that commitment point and `σ′` satisfies the stated substrate invariants;
- `deny`: `q` causes no authoritative change (`σ′ = σ` in the ordered model), with no substitute or partial effect. Other independently committed requests may still change observable state before a denial is reported.

For a testable instantiation, `permission valid` must be defined from the current combined state, request provenance, and any explicitly trusted facts. `invariant` must be an actual predicate over reachable states. These predicates are obligations of the instantiation, not unexplained Kernel-0 oracles. Rejection, commitment, and acknowledgement are different observations; only the first two define authoritative state. A lost acknowledgement does not undo a commit or establish that a retry is safe.

Revocation is an authorized transition after which requests grounded only in the withdrawn authority fail. The transition need not be named `revoke` or represented by an epoch, list, or token. The model must nevertheless distinguish an old request from a newly authorized one, including their trustworthy request provenance or an equivalent mediation assumption. Reusing a grant representation in a way that makes a superseded request appear current would violate the guarantee.

For any permission-changing commitment `a` and affected proposed commitment `c`, the model must resolve `a` and `c` in a common authority order. If `a` precedes `c`, `c` is judged from the post-`a` authority state; if `c` precedes `a`, it may commit under the pre-`a` state. An already completed authority change must precede a later initiated affected request. Overlapping operations may resolve in either order if the resulting authoritative history is coherent. No total order for unrelated operations, clock primitive, or single physical arbiter follows. This order can be derived from an adequate commitment trace; it need not be an independently stored object.

Executor death is an environmental trace event. It does not by itself erase `Σ` or create a new Work Unit. Automatic authority invalidation on death would require a trusted death signal and a guarded transition; neither is assumed. The established durability boundary is loss or replacement of the executor. Whether the authoritative substrate itself must survive its own restart or wider infrastructure failure remains a separate requirement question.

The state and interface are minimal only relative to required future behavior: two histories may collapse to the same `Σ` exactly when every required future permission and continuity observation remains equivalent. This criterion derives grant validity, work identity, and conflict distinctions from observations before introducing a named state component. It cannot yield a unique representation until those observations and the trusted boundary are fixed.

## Why these distinctions remain

| Distinction | Necessity argument | Smallest model challenge |
| --- | --- | --- |
| Proposal versus committed change | A caller's request or identity cannot itself change authoritative state. | A proposed but invalid change must leave no authoritative effect attributable to it. |
| Whole commitment versus partial mutation | Invalid changes must not silently become different or partial authoritative changes. | Attempt a change with one invalid part and check that none of its proposed authoritative effect commits. |
| Current versus superseded authority | Otherwise an old executor can act after replacement merely because it once had access. | Order replacement before an old request, then reverse the order; the permission outcome must be able to differ. |
| Trustworthy request provenance versus an actor's assertion | Without a reliable association to the current grant, an old executor can present or reuse a representation that appears current. | Present an old request after a new grant and test whether its asserted identity alone is accepted. |
| Relevant authority order versus an old observation | A truthful read made before revocation cannot authorize a later commitment. | Read authority, commit revocation, then attempt the earlier request. |
| Continuing work versus a new work identity | Replacement must preserve the same work and executor-facing position. | Replace an executor and recover the prior work and position without creating new work. |
| Retained state versus executor lifetime | Executor death must not erase work information or current authority needed for continuation. | Remove the executor and check that continuation can still refer to the same work. |
| Compatible versus incompatible commitments | Configuration must permit concurrency while excluding coexistence where exclusivity is required. | Commit two compatible requests; then attempt a pair whose resulting states are declared incompatible. |
| Commitment versus acknowledgement | An executor may lose contact after an authoritative commit. | Drop the acknowledgement and check that authoritative state remains definite. |
| External assertion versus trusted decision input | An outside fact may affect permission but its truth and freshness do not follow from its appearance in a request. | Vary the fact or its ordering against a commitment and state the assumption under which admission is sound. |

These are necessary semantic distinctions in the combined trusted system. They are not arguments for kernel object types named Work Unit, Attachment Point, Execution, grant, epoch, resource, clock, or scheduler. The exact minimal state representation remains underdetermined until the required interaction vocabulary and observations are fixed.

## Work Unit adequacy

The Work Unit / Attachment Point / Execution architecture is a consumer of the candidate. A proposed instantiation passes only if it can express and enforce these histories under one substrate with different configurations:

1. Establish work and an executor-facing position that remain identifiable while no executor runs.
2. Permit an authorized execution to change protected work state.
3. Replace that execution while preserving work and position continuity. An old request committed before supersession may stand; one committed after supersession must fail.
4. Permit compatible concurrent executions while preventing any incompatible authoritative states from coexisting.
5. Preserve information needed for continuation after executor loss, and make a permitted continuation possible when the declared availability and scheduling assumptions hold.

Generic protected state and policy can express these histories without promoting the three architectural concepts to Kernel-0 primitives. That is an **adequacy sketch**, not a proof of a concrete Work Unit design: the Evidence Packet does not fully define work continuity, attachment continuity, resource enforcement, or the positive operations an instantiation must provide. If continuity data or authority lives outside the kernel, its holder joins the trusted composition for the corresponding guarantee. Merely calling that holder external does not reduce the trusted obligation.

As a witness at the Work Unit layer, interpret protected information as a continuing `work–position` association, current `position–execution` authority, and the work state needed for continuation. Replacement changes current authority while retaining the association and work state; the old and new requests are then judged against the ordered authority change. These names describe the consumer's interpretation of generic protected information, not Kernel-0 object types.

The safety candidate by itself can reject every request. The positive histories above exclude that vacuous result for a Work Unit instantiation. Whether conditional progress belongs to Kernel-0 itself or to its instantiation remains open. Any progress claim needs explicit availability and scheduling assumptions.

### Guarantee-by-guarantee composition test

| Work Unit guarantee | Composition over the abstract model | Information the commitment boundary must reliably use |
| --- | --- | --- |
| Work continuity after executor death | A death event leaves the retained work reference and continuation data intact; a later authorized request can refer to the same work. | The continuing identity and required data must survive in `Σ` or a declared trusted store. The kernel need not parse a Work Unit type. |
| Attachment Point continuity | Keep a stable executor-facing position while its current execution association changes or is empty. | A distinction between that position and the temporary execution must be protected or supplied by a trusted component. |
| Replacement and revocation | Change the current authority association without replacing the work or position. Validate old and new requests in the common authority order. | Current authority, affected scope, and request provenance at commitment; no particular grant representation. |
| Stale execution exclusion | After replacement precedes an old request, deny it even if it retained an old representation. | A trustworthy distinction between superseded and current authority; an old representation cannot regain validity accidentally. |
| Sequential and concurrent executors | Use the same transition relation with one, successive, or multiple simultaneously valid authority associations. | A policy distinction between compatible and incompatible affected changes; no special execution mode. |
| Exclusivity where required | Prevent a second conflicting commitment from creating a forbidden coexistence state. | The conflict relation and enough ordering to evaluate the invariant for affected changes. |
| Bounded authority | Admit only requests whose scope and provenance satisfy current grants. | A reliable scope/provenance relation or equivalent trusted mediation; actor identity alone is insufficient. |
| Idle work and restart | Retained work and position need no resident executor. A replacement executor can resume if required data and authority state survive. | Executor loss is covered. Substrate crash/restart coverage and storage durability beyond that boundary are not specified by the packet. |

This establishes **conditional composability**, not unconditional adequacy. In particular, an unmediated external effect is outside the protected transition, and a trusted store that holds continuity or authority facts is part of the assurance boundary. The smallest missing semantic decisions for stronger claims are the precise scope of protected effects, the positive Work Unit operations, and the intended failure/restart boundary.

## Falsification and correction

The Astra 6 High pass found a stale-observation trace against the candidate's unconstrained external-authority alternative: a request observes authority at generation 4; replacement becomes authoritative at generation 5; the request then commits using its truthful generation-4 observation. Rechecking only whether the observation was once valid does not prevent stale mutation. The retained candidate therefore requires the common ordering contract above for every permission-relevant authority change and affected commitment. This is a semantic requirement, not a choice of protocol or physical arbiter.

It also reduced the candidate's description: the essential boundary is a conditional authoritative transition with revocable authority. A single displayed relation does not prove a single physical kernel component is necessary. No further primitive follows from the current evidence.

## Open alternatives and discriminating questions

| Alternative or gap | Smallest discriminating question |
| --- | --- |
| Authority state local to the boundary, in a trusted external component, or enforced by an equivalent fencing contract | Can a replacement and an old request be ordered so that no old request commits afterward, including delayed and concurrent requests? State the trusted assumptions for each arrangement. |
| Continuity information inside protected kernel state or in a trusted external store | Which exact future Work Unit behaviors must remain distinguishable after executor loss, and who guarantees the information survives? |
| Progress as a Kernel-0 obligation or as a Work Unit instantiation obligation | Is the kernel required to permit eventual authorized continuation, or only to make safety-preserving continuation expressible? Under what availability assumptions? |
| Authoritative state limited to internal records or extending to external resource effects | Which external actions must a stale executor be unable to perform, and where is their mediation contract? |
| Different minimal representations | Define required successful and forbidden interaction histories, then compare representations by the retained distinctions and trusted assumptions they require. |

The next narrow reasoning step is to define a small set of mandatory successful and forbidden histories for Work Unit continuity and authority replacement. Those histories can discriminate among the alternatives without choosing a language, state-machine formalism, storage engine, or hardware realization.

## Claim boundary

**WHY:** The retained distinctions answer explicit packet requirements; the ordering correction follows from a stale-authority interleaving, and the positive histories prevent a vacuous always-rejecting instantiation.

**WHAT:** The Evidence Packet, one open Astra 6 Medium derivation, Sol reconciliation and Work Unit trace test, and one Astra 6 High falsification/reduction pass.

**HOW CERTAIN:** Evidence-based semantic candidate. The stale-observation counterexample is decisive for the unconstrained external-authority alternative. Minimality and full Work Unit adequacy are not proven.

**WHAT-NOT-TESTED:** No formal model, implementation correspondence, concrete authority protocol, storage or external-effect mediation, broader failure model, or liveness proof was tested. The packet's underlying source provenance was not re-audited in this bounded session.
