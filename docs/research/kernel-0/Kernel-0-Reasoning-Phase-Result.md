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

This record reports the open derivation, Sol reconciliation, Work Unit adequacy and verification tests, irreducibility review, and two falsification/reduction passes directed under Crosslink issue #566. The first Astra 6 Medium pass received only the [Evidence Packet](./Kernel-0-Evidence-Packet.md) and the task stated for that pass. Each Astra 6 High pass received a compact current candidate and an open challenge. No pass selected a realization. This record is a provisional research result, not a change to the Evidence Packet's established requirements.

The Evidence Packet is internally coherent enough for this derivation: its authority, continuity, minimality, and verification clauses can be interpreted together without selecting an implementation. Its references to source work were not independently audited in this bounded session. The packet deliberately leaves policy, failure coverage, continuity criteria, and the scope of external effects underdetermined.

## Retained candidate: a conditional authoritative transition

Kernel-0 is provisionally a **durable conditional transition boundary with revocable authority**. This is a semantic candidate, not a claim that one physical component or location is necessary.

The core retains the information necessary to distinguish future permission and continuity outcomes, accepts proposed effects only through a guarded whole commitment, and makes revoked authority unusable at commitment. Its authority order covers affected commitments, without requiring a global order or one physical arbiter. The model below states the exact abstract obligations. A concrete instantiation must supply policy, protected effects, critical invariants, and trusted assumptions; the generic relation alone proves none of them.

## Minimal testable semantic model

Let `Σ` be the combined retained state on which an assurance claim depends. It includes authoritative state and any declared trusted external state needed by that claim; where the facts reside physically is not fixed. Let `q` be a proposed authoritative effect, including an authority change. Let `f` be a relevant externally supplied fact only when admission depends on it. An occurrence with no authoritative effect can appear in a trace without becoming a kernel transition. An occurrence that changes authoritative state must pass through the same guarded relation as any other proposal.

`Step(σ, q, f, outcome, σ′)` describes a **resolved** proposal and has two outcomes:

- `commit`: the proposed effect, at its declared granularity, is applied as one authoritative change; its permission is valid at that commitment point and `σ′` satisfies the stated substrate invariants;
- `deny`: `q` causes no authoritative change (`σ′ = σ` in the ordered model), with no substitute or partial effect. Other independently committed requests may still change observable state before a denial is reported.

A proposal may remain pending without a resolved outcome; the packet does not promise eventual response or commitment. Denial is the semantic no-effect outcome when the boundary does resolve a request against it, not a requirement for a particular error message.

For a testable instantiation, `permission valid` must be defined from the current combined state, request authority evidence, and any explicitly trusted facts. `invariant` must be an actual predicate over reachable states. These predicates are obligations of the instantiation, not unexplained Kernel-0 oracles. Rejection, commitment, and acknowledgement are different observations; only the first two define authoritative state. A lost acknowledgement does not undo a commit or establish that a retry is safe.

Revocation is an authorized transition after which requests grounded only in the withdrawn authority fail. The transition need not be named `revoke` or represented by an epoch, list, or token. Where a replacement must proceed while a superseded execution is excluded, their submissions must carry **trustworthily distinguishable authority evidence** at admission, or pass through equivalent trusted mediation. Current permission for a shared principal is insufficient if both executions can present it. The superseded execution must be unable to exercise the replacement's authority. This is a necessary information and enforcement condition, not a Kernel-0 Execution primitive.

For any permission-changing commitment `a` and affected proposed commitment `c`, the model must resolve `a` and `c` in a common authority order. If `a` precedes `c`, `c` is judged from the post-`a` authority state; if `c` precedes `a`, it may commit under the pre-`a` state. An already completed authority change must precede a later initiated affected request. Overlapping operations may resolve in either order if the resulting authoritative history is coherent. No total order for unrelated operations, clock primitive, or single physical arbiter follows. This order can be derived from an adequate commitment trace; it need not be an independently stored object.

Executor death is an environmental trace event. It does not by itself erase `Σ` or create a new Work Unit. Automatic authority invalidation on death would require a trusted death signal and a guarded transition; neither is assumed. The established durability boundary is loss or replacement of the executor. Whether the authoritative substrate itself must survive its own restart or wider infrastructure failure remains a separate requirement question.

The state and interface are minimal only relative to required future behavior: two histories may collapse to the same `Σ` exactly when every required future permission and continuity observation remains equivalent. This criterion derives grant validity, work identity, and conflict distinctions from observations before introducing a named state component. It cannot yield a unique representation until those observations and the trusted boundary are fixed.

## Why these distinctions remain

| Distinction | Necessity argument | Smallest model challenge |
| --- | --- | --- |
| Proposal versus committed change | A caller's request or identity cannot itself change authoritative state. | A proposed but invalid change must leave no authoritative effect attributable to it. |
| Whole commitment versus partial mutation | Invalid changes must not silently become different or partial authoritative changes. | Attempt a change with one invalid part and check that none of its proposed authoritative effect commits. |
| Current versus superseded authority | Otherwise an old executor can act after replacement merely because it once had access. | Order replacement before an old request, then reverse the order; the permission outcome must be able to differ. |
| Distinguishable authority evidence versus a shared principal | If old and new executions are indistinguishable at admission, one cannot be denied while the other proceeds. | Give both executions the same authenticated principal and credential; replace one and attempt requests from both. |
| Relevant authority order versus an old observation | A truthful read made before revocation cannot authorize a later commitment. | Read authority, commit revocation, then attempt the earlier request. |
| Continuing work versus a new work identity | Replacement must preserve the same work and executor-facing position. | Replace an executor and recover the prior work and position without creating new work. |
| Retained state versus executor lifetime | Executor death must not erase work information or current authority needed for continuation. | Remove the executor and check that continuation can still refer to the same work. |
| Compatible versus incompatible commitments | Configuration must permit concurrency while excluding coexistence where exclusivity is required. | Commit two compatible requests; then attempt a pair whose resulting states are declared incompatible. |
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

For a **small falsifiable Work Unit instance**, let the consumer interpret `Σ` as three finite relations: `C`, a continuing work-to-position association; `A`, currently eligible authority evidence for each position; and `D`, the minimal retained work value. Use one work handle, one position, two distinct authority contexts, and two possible values. The following are consumer-level proposed effects, all resolved through the same guarded commitment relation:

| Proposed effect | Guard and authoritative result |
| --- | --- |
| `establish(w,p)` | Trusted initial management authority permits creation when `w,p` are unused; commit adds `C(w,p)` and initializes `D(w)`. |
| `authorize(p,a)` or `withdraw(p,a)` | Current management authority permits the change; commit updates `A` while preserving `C,D` and the configured exclusivity invariant. |
| `replace(p,a0,a1)` | Current management authority permits a whole update that withdraws `a0` and authorizes distinguishable `a1`, preserving `C,D`. Separate withdrawal and authorization are also possible if an interval with no executor is allowed. |
| `change(p,a,v)` | Commit changes `D(w)` only if `C(w,p)` holds, the request is trustworthily bound to currently eligible `a`, and the proposed value satisfies the stated work-state invariant; otherwise deny without changing `D`. |
| `lose-executor(e)` | Environmental event leaves `C,D` intact. It changes `A` only if a separately specified trusted observation triggers a guarded authority transition. |

This finite instance can enumerate both orders of `replace` and an old `change`, death followed by replacement, and compatible or incompatible authority configurations. For the whole-effect test, submit one composite proposal containing an admissible `D` change and an inadmissible `A` change; it must deny as a whole. The instance excludes the shared-credential counterexample only if the declared evidence-binding assumption is true; without that assumption it must fail the supersession test. The seeded management authority is an explicit initial-state assumption, not an unguarded exception for later authority changes. The instance is a falsification witness for the generic model, not proof of general Work Unit adequacy or a Kernel-0 ontology.

The safety candidate by itself can reject every request. The positive histories above exclude that vacuous result for a Work Unit instantiation. Eventual progress is not currently assigned to Kernel-0; any later progress claim needs explicit availability and scheduling assumptions.

### Guarantee-by-guarantee composition test

| Work Unit guarantee | Composition over the abstract model | Information the commitment boundary must reliably use |
| --- | --- | --- |
| Work continuity after executor death | A death event leaves the retained work reference and continuation data intact; a later authorized request can refer to the same work. | The continuing identity and required data must survive in `Σ` or a declared trusted store. The kernel need not parse a Work Unit type. |
| Attachment Point continuity | Keep a stable executor-facing position while its current execution association changes or is empty. | A distinction between that position and the temporary execution must be protected or supplied by a trusted component. |
| Replacement and revocation | Change the current authority association without replacing the work or position. Validate old and new requests in the common authority order. | Current authority, affected scope, and distinguishable authority evidence at commitment; no particular grant representation. |
| Stale execution exclusion | After replacement precedes an old request, deny it even if it retained an old representation. | A trustworthy distinction between superseded and current authority; an old representation cannot regain validity accidentally. |
| Sequential and concurrent executors | Use the same transition relation with one, successive, or multiple simultaneously valid authority associations. | A policy distinction between compatible and incompatible affected changes; no special execution mode. |
| Exclusivity where required | Prevent a second conflicting commitment from creating a forbidden coexistence state. | The conflict relation and enough ordering to evaluate the invariant for affected changes. |
| Bounded authority | Admit only requests whose scope and authority evidence satisfy current grants. | A reliable scope/evidence relation or equivalent trusted mediation; a shared actor identity alone is insufficient. |
| Idle work and restart | Retained work and position need no resident executor. A replacement executor can resume if required data and authority state survive. | Executor loss is covered. Substrate crash/restart coverage and storage durability beyond that boundary are not specified by the packet. |

This establishes **conditional composability**, not unconditional adequacy. In particular, an unmediated external effect is outside the protected transition, and a trusted store that holds continuity or authority facts is part of the assurance boundary. The smallest missing semantic decisions for stronger claims are the precise scope of protected effects, the positive Work Unit operations, and the intended failure/restart boundary.

## Falsification and correction

The Astra 6 High pass found a stale-observation trace against the candidate's unconstrained external-authority alternative: a request observes authority at generation 4; replacement becomes authoritative at generation 5; the request then commits using its truthful generation-4 observation. Rechecking only whether the observation was once valid does not prevent stale mutation. The retained candidate therefore requires the common ordering contract above for every permission-relevant authority change and affected commitment. This is a semantic requirement, not a choice of protocol or physical arbiter.

It also reduced the candidate's description: the essential boundary is a conditional authoritative transition with revocable authority. A single displayed relation does not prove a single physical kernel component is necessary. No further primitive follows from the current evidence.

A later open Astra 6 High challenge exposed **supersession without distinguishable authority**. If old and replacement executions share a principal and credential, current permission for that principal, valid request provenance, ordering, and atomic commitment can all hold while the old execution still mutates state. The minimal correction is the distinguishable authority-evidence condition above whenever policy requires the replacement to proceed while excluding the old execution. Kernel-0 can expose this as a generic admission condition; the Work Unit instantiation must demonstrate that the condition is actually supplied and enforced. The packet does not decide its representation or placement.

## Minimum verification target

### Model properties

The abstract model must define initial states, the guarded commitment relation, denial, authority updates, and the exact critical invariants for each claimed instantiation. The smallest useful property set is:

1. **Guarded whole effect:** every committed request was eligible under authority current at its commitment point and its declared whole effect preserves the invariants; a denied request has no attributable authoritative effect.
2. **Revocation safety:** after an authority-withdrawing change precedes an affected request in the common order, that request cannot commit by relying on the withdrawn authority. Re-granting authority cannot make a superseded execution eligible merely by reusing an indistinguishable representation.
3. **Exclusivity:** no reachable state contains a configured incompatible authoritative combination. Compatible commitments remain representable without a special mode.
4. **Continuity across executor loss:** losing an executor does not erase the retained work and position information needed for the declared continuation behavior. Replacement preserves the continuing identity.

The first two are generic boundary properties once eligibility and effect granularity are supplied. The latter two are parameterized by the consumer's conflict and continuity definitions. Successful creation, authorized change, replacement, and continuation traces are required to rule out an always-denying model. Eventual completion is not a safety invariant and needs separate availability/fairness assumptions if later claimed.

### Model adequacy and discriminating traces

Exploring every encoded transition is insufficient if the encoding omits a relevant state or order. At minimum, the model must distinguish:

| Trace | Expected observation |
| --- | --- |
| Authorized whole change; then a change with one invalid part | The first can commit; the second cannot produce a substitute or partial authoritative mutation. |
| Old request observes valid authority; authority is withdrawn; old request then attempts commitment | The truthful stale observation cannot authorize the later commitment. This is the explicit stale-authority regression. |
| Replacement and old request overlap, in both resolved orders | Commitment before supersession may stand; commitment after supersession is denied. The model must represent both orderings. |
| Old and replacement executions submit with the same principal and credential | If old must be denied while replacement proceeds, the instantiation must add trustworthy distinguishability or fail the adequacy claim. |
| Executor disappears; work and position remain; replacement continues | The same continuing work and position are recoverable without treating replacement as new work. |
| Compatible concurrent requests and configured incompatible requests | Compatible requests can commit; incompatible authoritative states never coexist. |
| Commitment succeeds but acknowledgement is lost | Authoritative state remains definite; no retry guarantee is inferred unless separately specified. |

If permission depends on an external fact, add the two orders in which that fact changes before or after commitment, plus the fact's trust/freshness assumption. If substrate restart or external-resource control is claimed, add failure and effect traces for that declared boundary. These are claim-specific additions, not universal Kernel-0 primitives.

### Realization correspondence

Any later realization needs a stated mapping from its retained concrete state and trusted external state to `Σ`, and from its observable operations to abstract outcomes. Every concrete authoritative commit must map to a permitted whole transition; denial must map to no attributable mutation; authority invalidation and affected commitments must obey the modeled order. Recovery must preserve the abstract distinctions promised by its failure boundary. Mechanisms that emit protected external effects need an equivalent mediation or ordering argument. Model verification alone establishes none of this correspondence.

### Trusted assumptions outside a proof

Claims must name the origin of initial authority, the trustworthiness of subsequent request authority evidence, the consistency and durability of any external state relied on, the boundary that identifies a commitment, relevant external facts, and the availability/fairness assumptions behind progress. A proof cannot imply safety for unmediated effects or failures below its declared boundary. Semantic correctness of research, code, design, and other work products is outside this target.

## Irreducibility review

The core can be written as an admissible-history relation or as `Σ`, proposals, and guarded resolved transitions. `Σ` can itself be understood as equivalence classes of histories: histories are equivalent only if every required future permission and continuity observation is the same. These are alternative mathematical presentations of one candidate, not evidence for different kernel architectures. Transition notation is retained because it exposes the tests above.

| Candidate element | Result of removal test |
| --- | --- |
| Retained authoritative distinctions `Σ` | Keep only as the minimal summary of behaviorally distinguishable histories. Without equivalent retained information, current authority or continuing work can be lost across executor replacement. No concrete state container follows. |
| Proposal and declared effect `q` | Keep as an abstract input. Without the proposed effect and its granularity, the boundary cannot distinguish an authorized change from an unsolicited or partial mutation. Separate request and event primitives are unnecessary. |
| Guarded commitment relation | Keep. Without it, a caller's action can become authoritative without a current permission and invariant check. |
| Revocable authority | Keep as a property of changing eligibility under the relation. A grant, capability, epoch, owner, or role object is not forced. |
| Authority-relevant order | Keep as a constraint on affected commitments and authority changes, derivable from the accepted history. A separately stored order, global clock, or universal total order is unnecessary. |
| Distinguishable authority evidence | Keep as a conditional interface obligation where one producer must remain eligible while a superseded producer is denied. Its representation and placement are not fixed. |
| External fact `f` | Make optional. It can be folded into a request or trusted state, but its truth, freshness, and ordering assumptions must remain explicit whenever permission depends on it. |
| Invariants and incompatibility | Keep as explicit, instantiation-supplied predicates to test claims. They do not force an intrinsic conflict object or Work Unit type. |
| Denial, acknowledgement, and pending | Denial is a no-effect resolved outcome; pending has no implied progress guarantee; acknowledgement is outside authoritative commitment. None requires a persistent kernel object. |
| Executor-loss event and durability | Keep the preservation obligation for required `Σ` information. Loss is an environmental trace event, not necessarily a state variable or automatic revocation. |

The resulting semantic minimum is therefore a **retained behavioral distinction, a proposed effect, and a guarded authoritative commitment**, with revocation and relevant ordering expressed as properties of that relation. This does not remove the obligation to specify policy, positive Work Unit behavior, or trusted composition before claiming adequacy. Local and external placement of retained authority facts remain semantically equivalent only if both satisfy the same observable contract; their different trusted assumptions matter in a later realization comparison.

## Realization-independent requirements

Any realization claiming the abstract guarantees must satisfy the following behavioral obligations. They do not select a software, hardware, storage, or proof mechanism.

| Requirement | Guarantee it serves |
| --- | --- |
| Retain and recover every behaviorally necessary authority and continuity distinction across executor loss; keep inactive work and positions without a resident executor. | Work and position continuity, stale-execution exclusion after replacement. |
| Give each resolved proposal a definite authoritative result at its declared effect granularity: the whole permitted effect or no effect attributable to the proposal. If admission evidence is unavailable, a commit is not justified; the request may remain pending or be denied. | No unauthorized, substitute, or partial authoritative mutation. |
| Make permission-changing commitments and affected requests obey one coherent authority order, including concurrent and delayed requests. Check eligibility at the commitment point, not merely when the request was first seen. | Revocation safety and the stale-observation regression. |
| Supply trustworthy, currently eligible authority evidence that can distinguish a replacement from a superseded producer when policy requires different outcomes; prevent the old producer from exercising the replacement's authority. | Replacement can proceed while stale execution is excluded. |
| Enforce declared conflict and critical-invariant predicates for configured operations while allowing compatible concurrency through the same semantic interface. | Exclusivity without a special single- or multi-executor mode. |
| Expose relevant outside facts to the admission model with their trust and freshness conditions. If an external effect is claimed as protected, mediate it or include an equivalent trusted enforcement contract. | No hidden nondeterminism or unsupported claim about unmediated resources. |
| Provide a correspondence argument mapping concrete retained state, commitments, denial, authority updates, and relevant failure behavior to the abstract model. State the trusted components and assumptions on which it depends. | Model verification can transfer only to behavior that conforms to the model. |

If authoritative-substrate crash or restart is added to the promised failure boundary, recovery must resolve interrupted changes to an abstractly permitted whole commitment or no attributable commitment, preserve the authority order, and restore the distinctions needed for continuation. Executor loss alone does not establish that broader durability promise. If eventual progress or safe retry is claimed, the realization needs additional outcome, availability, and scheduling conditions; neither follows from the safety model.

## Open alternatives and discriminating questions

| Alternative or gap | Smallest discriminating question |
| --- | --- |
| Authority state local to the boundary, in a trusted external component, or enforced by an equivalent fencing contract | Can a replacement and an old request be ordered so that no old request commits afterward, including delayed and concurrent requests? State the trusted assumptions for each arrangement. |
| Continuity information inside protected kernel state or in a trusted external store | Which exact future Work Unit behaviors must remain distinguishable after executor loss, and who guarantees the information survives? |
| Progress beyond positive Work Unit reachability | The present evidence supports safety-preserving, non-vacuous Work Unit operations but assigns no eventual scheduling/availability guarantee to Kernel-0. Specify one only if a later consumer requires it. |
| Authoritative state limited to internal records or extending to external resource effects | Which external actions must a stale executor be unable to perform, and where is their mediation contract? |
| Executor loss alone or authoritative-substrate restart as the failure boundary | Must work and authority survive the substrate's own interrupted commitment and restart, or only loss of a replaceable executor? |
| Work Unit continuity details | Which work and position observations must remain the same after executor replacement, beyond identity and the minimum continuation state? |
| Different minimal representations | The state-transition and admissible-history formulations are equivalent relative to fixed observations. Physical placement remains for realization comparison, with its trusted assumptions counted. |

The successful and forbidden histories above fix the minimum authority and continuity behavior for a falsifiable Work Unit witness. They do not settle the protected-effect scope, stronger failure boundary, or full meaning of work and position continuity. Those are requirements questions, not a reason to select a language, state-machine formalism, storage engine, or hardware realization.

## Decision gate

**State C — missing semantic requirement.** The guarded transition core and its conditional Work Unit witness are stable enough to state verification and realization obligations. They are not sufficient to choose or compare realizations fairly while the protected-effect scope, authoritative-substrate restart promise, and full Work Unit continuity observations remain unstated. Local versus external placement of authority is a realization partition under the same semantic contract, not evidence for competing Kernel-0 ontologies. No settled Work Unit guarantee has been shown impossible, so state D is not supported.

The smallest discriminating next input is a bounded set of required traces: (1) after supersession, identify whether an old executor's external resource action is within the forbidden effects; (2) during an interrupted authoritative-substrate restart, identify which work, position, and authority observations must survive; and (3) give one permitted post-replacement continuation using the same work and position. The first two determine the trust and failure boundary; the third fixes the minimum positive continuity claim. Until those are established, preserving the alternatives is more accurate than choosing a realization or enlarging Kernel-0 by preference.

## Claim boundary

**WHY:** The retained distinctions answer explicit packet requirements; the ordering correction follows from a stale-authority interleaving, and the positive histories prevent a vacuous always-rejecting instantiation.

**WHAT:** The Evidence Packet, one open Astra 6 Medium derivation, Sol reconciliation and Work Unit trace test, two Astra 6 High falsification/reduction passes, and a minimal semantic, adequacy, verification, and irreducibility review.

**HOW CERTAIN:** Evidence-based semantic candidate. The stale-observation and indistinguishable-replacement counterexamples are decisive for the unconstrained alternatives they attack. Unique minimality, full Work Unit adequacy, and realization conformance are not proven.

**WHAT-NOT-TESTED:** The finite abstract instance was specified but not machine-checked. No implementation correspondence, concrete authority protocol, storage or external-effect mediation, broader failure model, or liveness proof was tested. The packet's underlying source provenance was not re-audited in this bounded session.
