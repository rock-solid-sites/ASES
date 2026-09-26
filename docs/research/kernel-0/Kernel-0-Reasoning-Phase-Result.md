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

The current [abstract semantics](./Kernel-0-Abstract-Semantics.md) incorporates the protected-effect, authority-distinguishability, and executor-loss boundaries derived in this cycle. The schematic model below records the reasoning path and must be read with that later specification.

The core retains the information necessary to distinguish future permission and continuity outcomes, accepts proposed effects only through a guarded whole commitment, and makes revoked authority unusable at commitment. Every dependency relevant to admission or an invariant is evaluated from a coherent current view for that commitment; unrelated changes need no global order or one physical arbiter. The model below states the exact abstract obligations. A concrete instantiation must supply policy, protected effects, critical invariants, and trusted assumptions; the generic relation alone proves none of them.

## Minimal testable semantic model

Let `Σ` be the combined retained state on which an assurance claim depends. It includes authoritative state and any declared trusted external state needed by that claim; where the facts reside physically is not fixed. Let `q` be a proposed authoritative effect, including an authority change. Let `f` be a relevant externally supplied fact only when admission depends on it. An occurrence with no authoritative effect can appear in a trace without becoming a kernel transition. An occurrence that changes authoritative state must pass through the same guarded relation as any other proposal.

`Step(σ, q, f, outcome, σ′)` describes a **resolved** proposal and has two outcomes:

- `commit`: the proposed effect, at its declared granularity, is applied as one authoritative change; its permission is valid at that commitment point and `σ′` satisfies the stated substrate invariants;
- `deny`: `q` causes no authoritative change (`σ′ = σ` in the ordered model), with no substitute or partial effect. Other independently committed requests may still change observable state before a denial is reported.

A proposal may remain pending without a resolved outcome; the packet does not promise eventual response or commitment. Denial is the semantic no-effect outcome when the boundary does resolve a request against it, not a requirement for a particular error message.

For a testable instantiation, `permission valid` must be defined from the current combined state, request authority evidence, and any explicitly trusted facts. `invariant` must be an actual predicate over reachable states. These predicates are obligations of the instantiation, not unexplained Kernel-0 oracles. Rejection, commitment, and acknowledgement are different observations; only the first two define authoritative state. A lost acknowledgement does not undo a commit or establish that a retry is safe.

Revocation is an authorized transition after which requests grounded only in the withdrawn authority fail. The transition need not be named `revoke` or represented by an epoch, list, or token. Where a replacement must proceed while a superseded execution is excluded, their submissions must carry **trustworthily distinguishable authority evidence** at admission, or pass through equivalent trusted mediation. Current permission for a shared principal is insufficient if both executions can present it. The superseded execution must be unable to exercise the replacement's authority. This is a necessary information and enforcement condition, not a Kernel-0 Execution primitive.

Independently resolved commitments that can change one another's permission or invariant result must admit one acyclic order across the interacting set, consistent with their validation views. If an authority change `a` precedes an affected request `c`, `c` is judged from the post-`a` state; the reverse order may permit it. The guard and whole effect use the same current view at commitment. An already completed relevant change precedes a later initiated affected request. A declared composite proposal can have one whole-effect transition, but independent proposals cannot silently share one old validation snapshot. No total order for unrelated operations, clock primitive, or single physical arbiter follows. The relevant order is derived from an adequate commitment trace, not necessarily stored separately.

Executor death is an environmental trace event. It does not by itself erase `Σ` or create a new Work Unit. Automatic authority invalidation on death would require a trusted death signal and a guarded transition; neither is assumed. The established durability boundary is loss or replacement of the executor. Whether the authoritative substrate itself must survive its own restart or wider infrastructure failure remains a separate requirement question.

The state and interface are minimal only relative to required future behavior: two histories may collapse to the same `Σ` exactly when every required future permission and continuity observation remains equivalent. This criterion derives grant validity, work identity, and conflict distinctions from observations before introducing a named state component. It cannot yield a unique representation until those observations and the trusted boundary are fixed.

## Resolved minimum boundaries

**Protected effect.** The mandatory boundary follows authoritative meaning rather than storage location or external visibility. A protected effect is any occurrence that changes a distinction on which accepted authoritative facts or future admission depend. If an accepted record says its result is the live contents at external location `L`, a stale executor's overwrite of `L` changes authoritative meaning even though the record is untouched; that overwrite must be guarded or made impossible under a declared trusted assumption. If `L` holds only candidate material and a distinct current-authority acceptance determines what becomes authoritative, the candidate write need not be protected. An irreversible action that is itself declared an exercise of substrate authority also needs a guarded, ordered authorization boundary before its protected consequence occurs; arbitrary external actions are not automatically in scope. The contract must say whether a prior committed authorization remains valid for delayed consequences after supersession. Reversibility alone does not make an effect unprotected if observers can already rely on it as authoritative.

**Failure boundary.** The evidence establishes survival of executor loss or replacement, including loss of any authoritative information co-located with that executor. It does not explicitly establish survival of an independently failing authority service, storage corruption, or infrastructure loss. A proposal interrupted by executor death may remain pending, but no invalid partial mutation may be exposed as an accepted result at its declared effect granularity. A separately claimed substrate-restart profile must preserve committed authoritative meaning, current authority distinctions, and continuity on recovery; it must resolve interrupted protected commitments to an allowed state. This is a conditional stronger promise, not an intrinsic storage technology.

**Continuity and supersession.** The minimum enduring information is a relation identifying the continuing work and executor-facing position, the authoritative information needed to continue them, and a current eligibility relation for attempts affecting them. Work identity, position identity, and execution identity need not be separate kernel objects. Old and replacement attempts requiring different outcomes must differ in something admission can trust. A fresh authority relationship can supply that difference without a separate Execution identity; trustworthy execution attribution is another formulation. Reusing old visible authority evidence while the old execution can still submit recreates its access. A generation, epoch, token, lineage, or channel may prevent this, but none is semantically mandatory. Exclusion of the old physical producer after it obtains new current evidence is a stronger claim requiring source binding or non-transfer; a new authorized grant to it is not survival of old authority.

## Why these distinctions remain

| Distinction | Necessity argument | Smallest model challenge |
| --- | --- | --- |
| Proposal versus committed change | A caller's request or identity cannot itself change authoritative state. | A proposed but invalid change must leave no authoritative effect attributable to it. |
| Whole commitment versus partial mutation | Invalid changes must not silently become different or partial authoritative changes. | Attempt a change with one invalid part and check that none of its proposed authoritative effect commits. |
| Current versus superseded authority | Otherwise an old executor can act after replacement merely because it once had access. | Order replacement before an old request, then reverse the order; the permission outcome must be able to differ. |
| Distinguishable authority evidence versus a shared principal | If old and new executions are indistinguishable at admission, one cannot be denied while the other proceeds. | Give both executions the same authenticated principal and credential; replace one and attempt requests from both. |
| Coherent commitment view versus independent stale validation | A truthful old authority read or two individually valid work updates cannot justify a later invalid combined state. | Race a revocation with a request, and separately race two invariant-conflicting updates validated from the same old state. |
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

### Stronger finite adequacy proof attempt

The earlier one-position witness checks the basic replacement case. For a nontrivial consumer instance, take one continuing work identity `w`, two stable positions `p1,p2`, successive execution contexts `e0,e1,e2` and another concurrent context `e3`, with distinct authority contexts `a0,a1,a2,a3`. Consumer state interprets the abstract authoritative view as `C: position → work`, `D=(d1,d2)` for two independently changeable work fields, and `V` for current authority by position, effect class, and rights. A proof-only issued-context set `U` records the no-reuse assumption; a trusted freshness service could discharge the same obligation without storing `U` in Kernel-0. Initially `C(p1)=C(p2)=w`, `D=(0,0)`, and only `a0` is valid for `p1`. Initial management authority is declared.

The consumer offers guarded operations `replace(p,a_old,a_new)`, `authorize(p,a,rights)`, `withdraw(p,a)`, `delegate(a_parent,a_child,rights)`, and `change(p,a,field,value)`. Replacement withdraws old authority and admits fresh, non-confusable authority while preserving `C,D`; delegation admits only a rights subset of the parent's current delegable rights when that policy applies. Changes to `d1` and `d2` can be compatible; conflicting changes or grants are rejected under the configured invariant. Executor loss is an environmental event with no erasure of `C,D,V` or the effective no-reuse fact. Every operation that changes authoritative meaning uses the same guarded commitment; a composite proposal has one declared whole effect.

| Guarantee | Boundary information and higher-level interpretation | Trace or invariant; necessary trust condition |
| --- | --- | --- |
| Work survival and Attachment Point continuity | The boundary must preserve the authoritative view; `C` and `D` are Work Unit interpretations, not kernel object types. | `lose(e0); replace(p1,a0,a1)` leaves `C(p1),C(p2),D` unchanged. Executor-loss recovery must preserve them, including any live external dependencies of `D`. |
| Replacement and sequential continuation | Admission must resolve the same affected scope and current authority. The consumer interprets `p1` as the same position in `w`. | `a0→a1→a2` changes `V` but not `C`; `change` under each current context can update `D`. New contexts must not be confusable with withdrawn ones. |
| Superseded and replayed attempt exclusion | Current eligibility and trustworthy authority evidence are required at commitment; Execution identity can remain higher-level. | After `replace(a0,a1)`, a delayed or replayed `a0` change is denied. If the claim also excludes physical `e0` after it obtains `a1`, non-transfer or trustworthy execution attribution is an additional premise. |
| Revocation and stale observation | The boundary orders affected authority changes and commitments. | A read of `V(a0)` before withdrawal cannot justify a `change(a0)` committed after withdrawal. The reverse commitment order may allow the change. |
| Bounded authority and attenuation | The boundary checks effect scope and rights; role/profile meaning remains higher-level. | A delegated `a_child` has no right outside the parent's current delegable set. A management grant from an independent authority is a distinct case, not automatic parent amplification. |
| Compatible concurrency and required exclusivity | The boundary evaluates all relevant guard and invariant dependencies from one coherent current view for each commitment. | Under independent-field policy, `p1` changes `d1` while `p2` changes `d2` and both commit. Under `d1+d2≤1`, proposals setting each field to `1` from `(0,0)` cannot both commit, even if each validated first against `(0,0)`. |
| Failed or denied request | The boundary knows the declared whole effect; the consumer supplies the requested state change. | A composite request with a valid `D` update and invalid `V` update leaves both unchanged if denied. A lost acknowledgement changes no authoritative result. |
| Restart inside the claimed boundary | The boundary and trusted state holders retain the distinctions above; Work Unit semantics remain consumer-level. | Restart of the executor, including loss of its co-located volatile state, preserves `C,D,V` and effective no-reuse. Independent authority-service restart is an optional stronger profile, not established here. |
| Protected external dependency | The boundary's authoritative view includes every live dependency that changes accepted meaning. | If `D` points to live `L`, an old executor's overwrite of `L` must be guarded or prevented by a trusted assumption. If `L` is candidate material, only its later acceptance is protected. |

For this instance, invariants follow by induction on committed operations in one acyclic relevant order: establishment creates a valid `C,D`; authority changes preserve `C,D` and check `V`; work changes preserve `C,V` and check rights and the resulting `D` invariant against the current view; denial stutters; executor loss preserves the required view. Freshness, evidence binding, and coherent atomic validity are premises, not consequences of this induction. This is **adequate under explicit minimal assumptions** for the settled continuity, replacement, bounded-authority, and exclusivity guarantees. It is an informal proof attempt, not a machine-checked proof or a claim about unspecified Work Unit content and external actions.

## Falsification and correction

The Astra 6 High pass found a stale-observation trace against the candidate's unconstrained external-authority alternative: a request observes authority at generation 4; replacement becomes authoritative at generation 5; the request then commits using its truthful generation-4 observation. Rechecking only whether the observation was once valid does not prevent stale mutation. The retained candidate therefore requires the common ordering contract above for every permission-relevant authority change and affected commitment. This is a semantic requirement, not a choice of protocol or physical arbiter.

It also reduced the candidate's description: the essential boundary is a conditional authoritative transition with revocable authority. A single displayed relation does not prove a single physical kernel component is necessary. No further primitive follows from the current evidence.

A later open Astra 6 High challenge exposed **supersession without distinguishable authority**. If old and replacement executions share a principal and credential, current permission for that principal, valid request provenance, ordering, and atomic commitment can all hold while the old execution still mutates state. The minimal correction is the distinguishable authority-evidence condition above whenever policy requires the replacement to proceed while excluding the old execution. Kernel-0 can expose this as a generic admission condition; the Work Unit instantiation must demonstrate that the condition is actually supplied and enforced. The packet does not decide its representation or placement.

A fresh Astra 6 High pass exposed **independent stale validation**: two proposals can each pass against `(d1,d2)=(0,0)` and together commit `(1,1)` despite invariant `d1+d2≤1`. The repaired model requires a coherent current view for every dependency relevant to admission and invariants at commitment, not only for authority changes. This strengthens the semantic commitment contract without requiring a global order or a particular atomicity mechanism. The pass also clarified that exclusion of an old external action is relative to the declared authorization point; forbidding a previously authorized consequence from appearing after replacement is a stronger sink-ordering claim.

An additional Astra 6 High pass sharpened “coherent”: three independently validated requests can form a cycle of required precedence even when each pair can be ordered. Independently resolved commitments must therefore admit one acyclic order across their interacting set; a same-snapshot batch is valid only if explicitly declared as one composite proposal and checked as a whole. It also reduced the generic authority premise from physical non-transferability to non-confusable current eligibility. Physical-producer exclusion after acquisition of new authority evidence needs its own source-binding premise.

## Minimum verification target

### Model properties

The abstract model must define initial states, the guarded commitment relation, denial, authority updates, and the exact critical invariants for each claimed instantiation. The smallest useful property set is:

1. **Guarded whole effect:** every committed request was eligible under a coherent current view of all permission and invariant dependencies at its commitment point; its declared whole effect preserves the invariants. A denied request has no attributable authoritative effect.
2. **Revocation safety:** after an authority-withdrawing change precedes an affected request in the common order, that request cannot commit by relying on the withdrawn authority. Re-granting authority cannot make a superseded execution eligible merely by reusing an indistinguishable representation.
3. **Exclusivity:** no reachable state contains a configured incompatible authoritative combination. Compatible commitments remain representable without a special mode.
4. **Continuity across executor loss:** losing an executor does not erase the retained work and position information needed for the declared continuation behavior. Replacement preserves the continuing identity.

The first two are generic boundary properties once eligibility and effect granularity are supplied. The latter two are parameterized by the consumer's conflict and continuity definitions. Successful creation, authorized change, replacement, and continuation traces are required to rule out an always-denying model. Eventual completion is not a safety invariant and needs separate availability/fairness assumptions if later claimed.

### Model adequacy and discriminating traces

Exploring every encoded transition is insufficient if the encoding omits a relevant state or order. The compact regression set below separates missing semantics from implementation correspondence and claims the packet does not make:

| Adversarial trace | Required result or classification |
| --- | --- |
| Read valid authority; withdraw it; then attempt the old commitment | Deny. A truthful stale observation is insufficient; relevant authority order is a **model distinction**. |
| Race replacement with an old request in both resolved orders | Before supersession the old change may commit; afterward it must deny. Both orders must be represented. |
| Validate `d1:=1` and `d2:=1` separately against `(0,0)` under `d1+d2≤1`; then attempt both commitments | At most one commits. A model or realization that retains both old validations lacks a coherent **invariant-relevant commitment view**. |
| From `x=y=z=0`: A requires `y=0` and sets `x=1`; B requires `z=0` and sets `y=1`; C requires `x=0` and sets `z=1` | All three cannot commit as independent requests: their validation views require cyclic precedence `A<B<C<A`. A common acyclic order is necessary across the full conflict set. |
| Old and replacement executions present identical trusted evidence, or an old authority label is reused | If one must proceed and the other fail, the model is **inadequate** without non-confusable evidence or trusted source attribution. |
| Lose an executor; restart another with the same work and position; replay old evidence | Continuity survives and old authority is denied after replacement. Losing co-located authority state would be a **conformance failure**. |
| Validate, then lose the executor or revoke authority before the effect | A later protected commit needs current permission. An interrupted request may remain pending; no invalid partial effect is accepted. |
| Apply a protected effect, then lose the executor before its durable record | The authoritative view must still correspond to a whole allowed commitment or no effect at the declared granularity. A split effect/record is a **conformance failure** within the claimed failure class. |
| Accept a live reference to external `L`; a stale execution overwrites `L` | The overwrite changes authoritative meaning and is a **protected effect** unless trusted immutability or separate current-authority acceptance prevents it. |
| Authorize an external action, revoke authority, then observe its delayed consequence | The result depends on the declared authorization point and whether revocation cancels outstanding authority. This is an **optional external-action contract**, not an automatic kernel primitive. |
| Race conflicting grants, revocations, and work changes; attempt an over-broad delegated grant | The configured conflict and attenuation predicates must hold in every resolved order. Parent-revocation effects on a child grant require explicit policy. |
| Change an external fact used by admission without representing its source or timing | A model that assumes the old fact remains valid is **inadequate**; fact trust and ordering must be exposed. |
| Commit, lose the acknowledgement, and replay while the same authority is still valid | Authoritative outcome remains definite, but exactly-once behavior is **not established**; request identity or deduplication is required only if later claimed. |

Independent authority-service restart and storage corruption require additional traces only if included in the declared failure profile. The listed cases do not justify a new Kernel-0 object merely because a concrete protocol must handle them.

### Realization correspondence

Any later realization needs a stated mapping from its retained concrete state and trusted external state to `Σ`, and from its observable operations to abstract outcomes. Every concrete authoritative commit must map to a permitted whole transition; denial must map to no attributable mutation; all guard- or invariant-conflicting commitments must use a coherent current view and obey the modeled relative order. Recovery must preserve the abstract distinctions promised by its failure boundary. Mechanisms that emit protected external effects need an equivalent mediation or ordering argument. Model verification alone establishes none of this correspondence.

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
| Acyclic relevant commitment order and coherent validity view | Keep as a constraint on changes that affect one another's guard or invariant, derivable from accepted history. Pairwise orders may form a cycle; a separately stored order, global clock, or universal total order is unnecessary. |
| Distinguishable current authority evidence | Keep as a conditional interface obligation where an old grant must be invalid while a replacement grant is usable. Physical-source binding is needed only if exclusion is claimed even when the old producer obtains new evidence. Representation and placement are open. |
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
| Make all guard- or invariant-conflicting commitments obey a coherent current-view contract, including concurrent and delayed requests. Check eligibility and the whole resulting effect at commitment, not merely when the request was first seen. | Revocation safety, stale-observation exclusion, and prevention of jointly invalid state changes. |
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
