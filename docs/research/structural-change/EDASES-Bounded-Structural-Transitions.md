---
title: EDASES Bounded Structural Transitions
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: edases
crosslink_issue: 566
baseline_commit: 741abfb905a270a90cab62213cf74fcda257b223
baseline_branch: codex/work-unit-foundational-review
depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Kernel-0 Multi-Domain Composition
  - Kernel-0 Authority-Service Crash and Recovery
  - EDASES Currentness and Recovery Assurance
  - Work Unit-0 Foundational Reduction
  - Concept: Levels of Abstraction
related_documents:
  - EDASES Work Unit Component Design
  - Concepts and Topics Registry
  - Methodology to Requirements Mapping Specification
  - Execution Engine Vision
  - Orchestrator Instructions
consumed_by:
  - Structural-change architectural review
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Authors of consumer transition and recovery claims
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# EDASES Bounded Structural Transitions

## 1. Result and adoption decision

**F4 adds no semantic power to Kernel-0. Its required histories reduce to existing
guarded whole effects, current authority, coherent ordering, consumer invariants
and continuity, and the declared recovery/conformance profile.** Work Unit adds
real policy: durable confinement, containment attenuation, sealed recovery, and
disposition before boundary removal. Those policies must be instantiated; they
are not supplied by merely naming a guard.

The candidate survives as a **conditional derived verification pattern for changes
to authoritative structural dependencies**, stated in §3. It does not justify a
new project-wide structural-transition primitive or an additional independent
assurance requirement. Pure physical relocation reduces to existing conformance
and durability. Permission-preserving relocation and explicitly authorized
permission-changing transitions must remain distinguishable.

There are actual non-Work-Unit consumers of the underlying obligations: Kernel-0's
two-domain resource transfer and its authority-holder recovery profiles. However,
their contracts already explicitly cover the failure histories used to support
F4. The additional consumer search finds current-state/resumption claims whose
needed clarification is already captured by the settled currentness result. It
does **not** find another existing contract that needs Work Unit confinement,
single-parent containment, or its disposition policy. Keeping those provisions
Work Unit-local makes none of the identified non-Work-Unit claims incorrect.

**Recommendation:** retain this research explanation for reuse; narrow F4's
proposed propagation and use the bounded contract in §10 for consumer
formalization. Do not change Kernel-0, add ontology identities, or promulgate a
new general structural rule merely because several consumers instantiate existing
obligations. A shared verification reference is optional documentation reuse,
not a missing architectural guarantee. The incremental mandatory project-wide
propagation set from this review is empty (§9).

**WHY:** each candidate obligation has an existing semantic home and a removal
witness; both overgeneralization controls succeed without new machinery.
**WHAT:** the pinned contracts, reduction in §3, and counterhistories in §§5–8.
**HOW CERTAIN:** evidence-based reduction and scoped placement recommendation,
not a universal minimality proof. **WHAT-NOT-TESTED:** a new formal model, a Work
Unit realization, physical migration, distributed recovery, or independent review.

## 2. Evidence boundary and method

The remote head of `rock-solid-sites/ASES`, branch
`codex/work-unit-foundational-review`, was verified with `git ls-remote` on
2026-09-28 as `741abfb905a270a90cab62213cf74fcda257b223`. An isolated working
branch starts at that exact tree. An existing checkout had an additional local
commit; it is excluded from this review. All source references below mean this
pinned baseline, not a subsequent branch head.

| Ref | Source and use |
| --- | --- |
| F | [Work Unit-0 Foundational Reduction](../work-unit-0/Work-Unit-0-Foundational-Reduction.md), §6/F4, T5 and T7–T10: findings under investigation, not axioms. |
| W | [Work Unit Component Design](../../architecture/EDASES%20Work%20Unit%20Component%20Design.md), current A–L, especially C/E–K: consumer claims being tested. The preserved historical design does not reinstate primitives. |
| K | [Kernel-0 Abstract Semantics](../kernel-0/Kernel-0-Abstract-Semantics.md), Parameters, Resolved transition, Authority and order, Continuity and failure, External action: semantic reduction target. |
| V | [Kernel-0 Verification Obligations](../kernel-0/Kernel-0-Verification-Obligations.md), invariants 1–6, adequacy, traces, conformance and trust assumptions: existing proof obligations. |
| J | [Kernel-0 Composition](../kernel-0/Kernel-0-Composition.md), witness, removal attacks and What composes: actual non-Work-Unit consumer, whole transfer and independent domains. |
| C | [Kernel-0 Crash and Recovery](../kernel-0/Kernel-0-Crash-Recovery.md), What must survive, Two recovery claims and Result A1: whole current cut, accepted content and bearer reconstruction. |
| U | [Currentness and Recovery Assurance](../currentness/EDASES-Currentness-Recovery-Assurance.md), §§3, 7–8: settled claim-relative currentness and six-field recovery disclosure, reused without reopening. |
| R | [Concepts and Topics Registry](../registry/Concepts%20and%20Topics%20Registry.md), authority boundary and deferred checkpoint topic: discovery and lineage, not architectural specification. |

Expansion beyond these sources is limited to checking the actual State Management,
Validation, Traceability and Recoverability claims in the
[Requirements Mapping](../../requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md),
State Management in the [Execution Engine Vision](../../architecture/Execution%20Engine%20Vision.md),
and durable resumption in [ORCHESTRATOR](../../ORCHESTRATOR.md), “Orchestrator as
Single Integration Point.” Their relevance and exclusion from new propagation
are tested in §9. No general migration/storage architecture was sought. The
registry's named Minimal Execution Substrate documents were not located in the
baseline; its summaries cannot fill that evidentiary gap.

The cheapest discriminating test is a short history: remove one proposed rule,
identify the failed observation, then try to express the repair using K plus the
consumer's existing policy. The histories below are reasoned counterexamples,
not newly executed experiments. J reports bounded model evidence; C reports
bounded process-loss evidence and an outside-profile rollback attack. Those
results were read, not rerun, and do not establish physical Work Unit confinement
or split-holder atomicity.

## 3. Kernel-0 reduction before structural vocabulary

### 3.1 Scope, premises and strongest defensible wording

For this review a **semantic structural transition** changes a relationship or
authoritative representation on which a declared permission, protection,
accepted-state, or continuity observation depends. Examples are changing a
governing containment edge, transferring an exclusive entitlement, or activating
a restored image as current. This is an applicability test, not a new object
type. An operation can change several such relationships together.

“Bounded” here requires an identifiable protection/dependency scope in the consumer
claim. It does not imply a fixed number of bytes, a deadline, a universal parent
relation, or a globally finite system. Durability is always relative to named
failures. A surviving file with no required enclosing protection does not acquire
Work Unit confinement merely because it is durable.

The premises of the derived pattern are:

1. The consumer declares the relevant observations, protection/rights policy,
   continuity projection, and outcomes that must actually be possible. They are
   requirements, not properties inferred from a convenient implementation.
2. All relationships that can change those observations enter the authoritative
   view or its declared trusted dependencies. Include affected descendants and
   external holders where the claim actually depends on them.
3. Initial/current management authority and the authority for each proposed
   structural and permission effect are established under the existing trust
   contract. Structure, creator identity and physical possession do not supply
   that authority by themselves.
4. Whole-effect granularity, authoritative observations and admitted intermediate
   commitments are specified before their outcomes are claimed. The failure
   profile states which commitments/content must survive.
5. Concrete enforcement and recovery refine those claims. An abstract edge change
   is not evidence that an old handle stopped working or bytes remained protected.

Under these premises the strongest justified reusable wording is:

> A change to authoritative structural dependencies must be a currently admissible
> whole effect, or an explicitly admitted sequence of whole effects. Every
> authoritative observation and covered recovery outcome must satisfy the
> protection, rights and continuity obligations applicable at that stage to every
> surviving dependent. Any newly effective authority must be included in an effect
> authorized by current policy; changed structure alone is not authorization for
> widening. Recovery must preserve the declared committed effects and required
> continuity at their specified granularity, using the established currentness
> basis and a compatible cut wherever dependencies couple the recovered state.

“Applicable at that stage” permits authorized narrowing, transfer and legitimate
policy changes. It does not permit weakening an invariant after a torn result is
observed, or relabeling lost accepted content as intentional disposal. An earlier
promised whole transfer remains whole; any later authorized supersession is a
separate event. A safety obligation does not imply eventual completion. An
always-refuse realization still fails any advertised successful-transition claim.

### 3.2 Removal and expressibility audit

| Candidate extra obligation | Required history lost if omitted | Existing expression; does F4 add semantics? |
| --- | --- | --- |
| Include structural dependencies in the current view | Change parent while retaining a grant; admission overlooks the changed restriction (A1). | K's `σ` includes all facts determining current permission; V protected-meaning closure. No extra semantics. |
| Preserve required protection of survivors | Remove the only protective boundary and expose a surviving file (S1). | Consumer `I`/guard/effect and external conformance. Confinement is substantive W policy, not a universal K invariant. |
| Authorize a resulting widening | A latent write becomes effective solely through new parentage (A1). | Current `G` must cover the full semantic `E`, including authority changes. Existing settled explicit-widening obligation; not exact preservation of rights. |
| Resolve the promised whole effect | Split a promised transfer and retain neither owner (R1). | K's `E` and failure clauses; J already gives this very counterexample. Final invariant alone is insufficient, but K already says so. |
| Cover concurrent dependency creation | Empty check; child creation commits; stale removal commits (S3). | Current coherent `G`, V conflict ordering. No destruction lock or lifecycle primitive follows. |
| Preserve same work and required content | Rename the surviving entry but lose its bytes, or silently replace work with an old checkpoint (R3/R4). | Consumer continuity projection and K/V retained-content obligation, with U's currentness basis. Stable spelling is neither necessary nor sufficient. |
| Recover coupled state compatibly | Independently authentic source/destination fragments recover duplication or loss (R1). | C/J compatible whole cut and U field 6. No additional recovery mechanism. |
| Permit safe multi-step transitions | Requiring a giant transaction rejects bounded staging and recursive disposition (S4). | K explicitly permits allowed prefixes of separately committed changes. Stage policy belongs to the consumer. |
| Preserve semantics across representation/holder changes | Retire the only accepted-content holder while a reference survives (R3). | V realization abstraction, external dependencies, observation mapping and declared durability. No universal holder registry. |

Delete the label “structural transition” while retaining these instantiated
obligations: every required history remains expressible. Delete the obligations
themselves: the cited histories fail. Thus F4 is useful explanation and a policy
instantiation guide; it is not another semantic capability of Kernel-0.

**WHY:** the reduction assigns each necessary observation to a specific existing
parameter, rather than hiding it inside an unspecified guard. **WHAT:** K/V,
W.C/E–K, J/C/U and the removal witnesses above. **HOW CERTAIN:** evidence-based
expressibility argument for these claims. **WHAT-NOT-TESTED:** exhaustive
formalization, all future consumers, or correctness of any implementation.

## 4. Which changes matter, including identity

The distinctions below describe effects and dependencies. They do not mandate
separate APIs, lifecycle states, migration objects, or ontology entries.

| Change | What can change the guarantee? | Can identity remain unchanged; does that settle safety? |
| --- | --- | --- |
| Physical relocation of bytes | Under the clean control, neither authoritative relationships nor effective permissions change. Retention, integrity, observation equivalence and the selected failure coverage still must hold. | Yes. Same logical object at another location is possible. Identity alone does not prove successful copying or durability. |
| Containment | Governing protection path, aggregate resource constraints and affected descendants may change. Parentage is not automatically management. | Yes: W.J explicitly moves the same child. Safety follows from resulting obligations, not from retaining its ID. |
| Resource ownership | “Ownership” must specify the entitlement: exclusive allocation, duty to retain content, right to dispose, or another consumer meaning. Moving one need not move the others. | Usually possible under the declared identity model. If identity includes domain, explicit continuity correspondence may be required. No universal ownership meaning is justified. |
| Management authority | Who may administer, revoke or dispose changes; old evidence may have to cease being eligible. | Yes: authority can change around the same object. Identity/provenance cannot preserve the old manager's rights. |
| Effective permission through structural context | Unchanged local grants can yield different permitted effects, even with both endpoints temporarily inactive (A1). | Yes. This is a direct counterexample to identity plus unchanged grant records being enough. |
| Authoritative representation or holder | An encoding change can be observationally equivalent; selecting a different current source can change accepted meaning, trust, evidence binding and recovery dependencies. | Logical identity can survive either. A holder process may change identity while work continues. Competing holders must meet the advertised authority/consistency contract. |
| Checkpoint/restore | Copying historical material differs from installing it as current or activating its relationships; see §8. | A checkpoint can carry the original ID as historical data. Simultaneous current instances with that ID are not thereby authorized. Restore may continue the same work or explicitly create a branch/new object. |
| Transfer between domains | What moves must be named: bytes, containment, entitlement, management, or a combination. Exclusive transfer differs from copying or delegation. | Same-object transfer is possible; a new identifier with valid continuity mapping is also possible if the consumer permits it. Renaming cannot excuse loss or duplicate authority. |
| Destruction/removal of a containing boundary | Removal can invalidate protection/resource/continuity dependencies of survivors. Disposal guarantees differ from revocation of borrowed access. | The destroyed boundary does not remain an existing current object; provenance may retain its ID. Survivors can keep theirs. Reusing an identifier must not resurrect old authority. |

If a consumer defines identity using parentage, reparenting changes that identity;
the rule still applies to the continuing content/obligations through the declared
correspondence. W instead claims continuing Work Unit identity across relocation.
Neither scheme warrants a general immutable identity primitive. K already requires
non-confusable authority observations and the particular continuity observation.

**Material distinctions:** semantic change versus representation equivalence;
containment versus management; allocation/ownership versus actionable permission;
historical copy versus current activation; exclusive transfer versus copy; and
logical disposal versus physical erasure. Collapsing them fails A1, A2, S1 or
R1–R4. They are already expressible in the existing authoritative view and
consumer policy. No new ontology distinction is necessary to state them.

## 5. Rederiving confinement and ordering

### S1 — remove before disposition

Premise: P supplies a required restriction on surviving file F; F is not authorized
for general exposure. Remove P and leave F accessible through an unconstrained
host path. F's bytes and ID survive, and the remaining records may be individually
valid, but the required restriction no longer holds. The violated property is
surviving-content protection, not necessarily content durability or currentness.

Atomic removal of P alone would still be wrong. Whole-effect semantics cannot
choose the missing invariant for the consumer. W.I supplies the repair: transfer
each dependent to a valid bounded destination or dispose of it under the declared
storage guarantee before the boundary ceases. A composite disposition/removal
can be one whole effect, or disposition can precede final removal through valid
committed stages. Revoking a borrowed resource relationship does not destroy that
external resource.

Counterexample to “a parent can never disappear while anything formerly inside
survives”: F has been validly transferred, or an authorized structural change
leaves its independently sufficient protection intact under a consumer that
permits this result. P can disappear without a protection loss. The general
obligation concerns **required dependencies**, not retention of all old ancestors.
W's narrower two-disposition policy remains binding on Work Units; a general
consumer is not thereby required to implement it.

### S2 — split move, both orderings

Start with C protected through P. A promised whole move changes P to Q.

1. Commit removal from P before valid Q containment exists; then observe or crash.
   If no other effective protection bounds C, protection fails. If C remains
   independently sealed and protected, protection may hold, but the result still
   fails a promise that only the old or new whole endpoint is authoritative.
2. Establish Q first while P remains. If both are effective parents in a claimed
   single-parent model, the structural invariant fails. If either path grants
   access independently, the new path can also violate restrictions imposed by P.
   But two physical copies are not necessarily two authoritative parents. And a
   consumer explicitly permitting overlapping boundaries that jointly preserve
   all obligations can admit dual containment. Dual presence is not inherently
   an authority violation.

Preparation at Q that cannot change authoritative meaning can occur while P stays
authoritative. If preparation exposes protected bytes or creates actionable access,
that effect must already be authorized and confined; the word “candidate” does
not exempt it from the protected-effect claim. Alternatively an explicitly
admitted bounded staging state can be a whole committed result (§7). It cannot
be retroactively substituted for the torn midpoint of a promised atomic move.

### S3 — stale final-removal decision

The destroyer observes P empty. A valid create operation then commits child C in
P. Removal subsequently commits using the old empty observation. If create is
ordered first, removal's current guard is false. If removal is ordered first,
create cannot attach to the now-absent P under the declared containment policy.
Accepting both with a surviving dependency has no valid coherent order. Overlap
may choose either ordering, but each guard must see its relevant predecessors.

K/V capture the failure completely once the consumer includes the real dependent
set in the guard/conflict footprint. An incomplete enumeration or unmediated
creation route is a model/conformance error, not a missing ordering primitive.
A policy that stops new admissions during destruction can simplify the instance;
it is not a necessary universal lifecycle state or global lock.

### S4 — recursive destruction with accepted prefixes

Seal a boundary; disposition one durable child; disposition another; remove each
empty boundary; finally remove the root. If each committed prefix retains required
protection and accepted surviving content, recovery may retain that prefix. W.I
requires the interrupted remainder to stay bounded and sealed. No promise that
all prior children will reappear, no secure erasure of every physical backup,
and no completion deadline follows.

A crash before the first seal commits may leave the previous whole state. A
durably started destructive sequence cannot claim to have removed the boundary
while undispositioned dependents remain. If a different consumer promises atomic
subtree deletion, these separately visible partial results would violate that
stronger promise even though safe. The consumer's chosen granularity determines
which interpretation is allowed.

**WHY:** S1 needs substantive confinement policy, S2/S4 need effect and prefix
semantics, and S3 needs current conflict ordering. None defeats K's expressibility.
**WHAT:** W.I/J/K, F.T7–T10 and K/V/J. **HOW CERTAIN:** evidence-based conditional
counterhistories. **WHAT-NOT-TESTED:** real handles, containment enforcement,
recursive termination, external disposal, or multi-holder interruption.

## 6. Authority: forbid implicit widening, permit authorized change

### A1 — latent authority becomes effective

Use F.T5's exact premise: C has local read+write authority; P restricts effective
use to read; C is sealed; C moves to permissive Q with its local relationship
unchanged. Reactivation that merely lifts the temporary move seal enables write.
Destination compatibility and unchanged grant records both hold, yet the move
has introduced an effective authorization that was never explicitly authorized
as a widening. The dependency omitted from the move's effect was P's restriction.

Comparing the empty enabled-action sets of two sealed snapshots misses the
failure. Compare the retained policy's effective scope through permitted later
activation, disregarding only the move's temporary inactive condition. Do not
erase actual revocations, ancestor restrictions, resource conditions, or the
authority required for activation. The same analysis applies to affected
descendants. Where rights are conditional, compare semantic effects and conditions,
not strings or capability counts.

For a permission-preserving move, retain an equivalent restriction, reduce/revoke
the enabling relationship, or refuse that move if its required success conditions
cannot be met. A later activation that itself explicitly authorizes write is a
different valid history, not silent widening.

### A2 — explicitly authorized widening: counterexample to exact preservation

A current manager is eligible both to reparent C and to authorize write in Q.
The proposal expressly includes the new write permission; current guards admit
the complete structural and authority effect. A whole commit changes both. This
is allowed by K. A rule requiring rights to remain identical, or never increase,
would prohibit an otherwise valid required management operation.

Authority to move alone does not imply authority to widen. Conversely, explicit
authorization need not mean a fresh human click or a separate commitment: a
declared standing policy may authorize a specified move-and-widen effect, and a
policy-generated event is still a guarded proposal. The effective widening must
be within that policy's scope and represented in the admitted effect. Mere
destination permissiveness or requester intention is insufficient.

For W.J, the directly described path is sealed relocation followed by authorized
reactivation with different grants. This review does not amend that consumer's
operation set to require a combined move-and-widen operation. It establishes that
a general rule must allow the combined operation wherever the consumer permits it.

### A3 — narrowing: counterexample to preserving all old rights

A move intentionally drops write, or a current policy revokes a relationship as
a condition of transfer. This can preserve every required protection while
reducing usable authority. The change still needs its applicable current guard;
calling it “safer” does not grant an unauthorized actor permission to disrupt
another object. Required continuation or resource obligations must also hold;
dropping all rights is not automatically a successful transfer if useful
post-transfer continuation was promised.

“Structural change must not itself constitute an unrequested authorization
change” is therefore too imprecise as the final rule. Explicitly authorized policy
events may narrow rights without a contemporaneous requester, and one authorized
proposal may deliberately change both structure and rights. The sharper wording
is the authority clause in §3: **newly effective authority must be part of an
effect authorized by current policy; structural context alone is not that
authorization.** All other authority changes remain guarded as K already requires.

### A4 — equivalent authority, different representation

P's read-only attenuation is represented after the move by a destination policy
that permits the same reads and excludes the same writes on the same resources
under the same relevant conditions. Keeping P's policy bytes or its boundary
identity is unnecessary. Equivalence must include management, descendants,
resource restrictions and future required observations where those are claimed;
matching today's example read is insufficient. This refutes a universal demand
for an old-parent record or a second authority ledger.

### A5 — clean physical-relocation control

Move the bytes behind an accepted reference from one trusted physical location
to another. The authoritative object, relationships, effective rights and all
required future observations remain equivalent; the declared failure model
covers the relocation transparently. There is no new permission effect to
authorize. Concrete copying, access protection and retention still must satisfy
conformance, including any already-protected external actions. If the destination
exposes bytes, loses accepted contents on a covered crash, or changes governing
authority, it fails this control's premise and is analyzed under its actual effects.

**WHY:** A1 defeats destination-only checks; A2–A5 defeat exact-rights preservation,
mandatory separate authorization ceremonies and treating every byte move as a
permission transition. **WHAT:** settled explicit-widening requirement, K's
authority/whole-effect clauses and W.J/K.19. **HOW CERTAIN:** evidence-based rule
qualification. **WHAT-NOT-TESTED:** equivalence of any actual capability language,
standing policy, substrate route or attachment implementation.

## 7. Whole commitments and legitimately bounded intermediate states

An intermediate is legitimate when it is a **declared admissible committed state
with its own truthful observations**, preserving all applicable protection,
authority, resource and continuity obligations through the covered interruptions.
Its dependency scope, responsible protection and permitted uses are determined.
If continued processing is unavailable, it remains within those obligations;
“we will repair it soon” is not a safety argument. Bounded does not itself mean
time-limited. If a completion deadline is claimed it needs a separate progress
argument.

An invariant-valid intermediate can still be a torn promised effect. Three tests
distinguish them: was this prefix actually admitted by the operation contract;
what did an authoritative observer or acknowledgement promise had completed;
and does recovery preserve those commitments and required content? A client-facing
workflow may complete later than its individual stage commitments, but its
published meaning cannot pretend that a partial transfer is already whole.

| Proposed decomposition | Valid conditions | What would make it torn or unsafe? |
| --- | --- | --- |
| Prepare Q while P stays authoritative | Q is non-authoritative preparation; all protected access/copy effects are admitted; P continues to meet retention/protection duties. | Exposing Q as current, freeing P's only accepted bytes early, or creating an unguarded route to protected content. |
| Commit sealed bounded staging | Staging is a declared whole outcome with effective protection, retained content, current governing authority, defined permitted actions and a recovery meaning. | An orphan labeled “staged,” two zero enabled-action sets hiding later widening, or an atomic P→Q promise that admits no stage. |
| Transfer, then activate | Transfer fully establishes the destination's required relationships and continuity in an inactive state. Activation separately checks current authority and constraints. | Activation on a stale validation, or claiming transfer complete before its exclusive ownership/containment effect is complete. |
| Recursive destruction across durable commits | Each accepted disposition leaves survivors bounded; final removal sees no unmet dependent obligation; W's remainder is sealed. | A visible partial result under an atomic subtree-deletion promise, or a survivor's protection lost between disposals. |
| Relocation plus management transfer | Either both are one declared effect, or each stage explicitly says which manager remains eligible and which rights cease, while meeting all invariants. | A combined promise recovers the new location with the wrong manager; revoking old management before any permitted stage can govern the survivor. |
| Relocation without management transfer | Current management remains valid; equivalent restrictions and required content/continuity survive the move. | Treating the destination owner or physical holder as automatically authorized to manage. |

There is no universally correct “revoke first” or “grant first” protocol. Exclusive
transfer, delegation and staged suspension admit different histories. If the
consumer requires one whole effect, a realization must refine that effect or
decline the claim; it cannot silently weaken it into independent writes. If the
consumer permits several commitments, one giant transaction is unnecessary.

Two successful semantic witnesses prevent safety-only vacuity: move a sealed C
while retaining its read-only restriction, separately authorize activation, then
successfully read retained content while write remains denied; and disposition
two children across separate commits, recover the still-sealed remainder between
them, then finish final removal. A2 supplies a successful deliberate widening
witness. These show expressibility, not realized availability or termination.

## 8. Recovery, coupled state, and checkpoints

### 8.1 Five independent questions

| Question | What it establishes | What it does not establish alone |
| --- | --- | --- |
| Structural consistency | The recovered relationships satisfy the selected invariant, such as one valid governing path or at-most-one reservation. | That a promised transfer happened wholly, that bytes survived, or that this view is current. |
| Whole-effect continuity | Recovery corresponds to the operation's admitted history and retained commitments at the declared granularity. | Freshness against excluded rollback, usable content from a lost holder, or real protection enforcement. |
| Currentness | The recovered view supports the required present propositions under the declared preservation/reconstruction basis. | New permission, physical isolation, content availability, or completion progress. |
| Authority | The current effect or activation is eligible, with trustworthy evidence and ordered use. | That an authentic historical image was the latest committed work or that an old manager remains eligible. |
| Content durability | Required accepted content is retained or reconstructible under the stated failures. | Correct governing relationships, whole transfer, currentness or authority to use it. |

These are separable verification questions, not five new subsystems. A complete
authoritative view may include all of them; checking just one projection does not
certify the others.

### R1 — incompatible source/destination restoration

Let membership/entitlement indicators `(P,Q)` change by a declared whole transfer
from `(1,0)` to `(0,1)`. Restore old P with new Q: `(1,1)`, duplicate apparent
containment/ownership. Restore new P with old Q: `(0,0)`, missing containment or
entitlement. Each fragment can be authentic. The second result satisfies
`P+Q≤1` but violates the whole transfer and required resource continuity. Even
choosing the old whole endpoint after an acknowledged durable transfer is wrong
under the C/J profile; it is whole but obsolete, absent a later authorized reversal.

This is J's actual non-Work-Unit reservation counterexample, reapplied to F.T9.
It does not prove that every copy is a second owner: an explicitly non-authoritative
copy contributes no such membership. Nor may a checker erase a missing child to
make a no-orphan predicate true when that child was required to survive.

### R2 — compatible cut, without global synchronization

A compatible recovery cut is required when recovered facts are jointly needed
to interpret a whole commitment, an interacting order, or a shared invariant
and continuity/authority dependency. Physical separation is neither necessary
nor sufficient. The C/J profile retains completed and irrevocably committed
effects, including lost acknowledgements; interacting predecessors are respected,
and no whole composite is torn. Later legitimate supersession can replace values;
this is not a demand to replay or retain every historical byte.

U already requires this disclosure in its coupled-cut field. The recovery basis
must distinguish materially obsolete alternatives where the current claim needs
that distinction. A recovered old parent and a current destination cannot be
certified independently while ignoring their joint effect. A currentness check
that truly includes all those dependencies already covers the issue; no new
freshness mechanism is added here.

Counterexample to a global synchronized snapshot: J's independent local work
bits, with disjoint guard/effect/invariant and authority dependencies, can change
and recover independently; B-local work remains admissible while A is unavailable.
No required observation selects one shared wall-clock snapshot for them. Coupling
is determined by actual dependencies, not by co-residence or an author's assertion
that data are “local.” Transitive interactions must be included when material.

### R3 — holder change while retaining only a name

Accepted work references content held only at L. The reference/ownership label
is changed to M, L is retired, and recovery finds the name but no accepted bytes.
Structural checks may pass while required continuation fails. K/V's retained
content obligation already rejects the history. C's cold recovery also shows that
transient bearers may be discarded while work and rights distinctions survive;
reconstructing a current bearer from a caller's identity assertion is a separate
authority-binding failure. Neither issue requires a universal holder registry.

### R4 — restore into a different authority context

An authentic checkpoint records C with local read+write while P supplied a
read-only restriction. Restore under Q and activate by trusting only the recorded
local relationship. Write becomes effective without the authorized widening.
Conversely, restoring into a more restrictive context can invalidate previously
usable rights even if the checkpoint is perfectly current for its content.

Recovery must bind the candidate view and its claimed authority to the actual
current context and order activation with relevant changes. Historical validity
in P is not admission in Q. If current authority intentionally grants write in Q,
that new event can be valid (A2); it does not establish that the historical image
includes every accepted content change or superseding decision. This uses U's
existing currentness/binding result and K's current guard, not a new restore rule.

### 8.2 Checkpoint events are not interchangeable

| Event | Default semantic treatment, subject to the actual claim |
| --- | --- |
| Create checkpoint | Preserve historical material. Reading/copying protected content may need authority, but no current-owner or permission change follows merely from creating a snapshot. If a “whole checkpoint” is promised, its own capture consistency must satisfy that promise. |
| Restore bytes into a candidate location | Materialize candidate data under its protection contract. It is not current work simply because a restore command succeeded. Existing effects of copying/exposure remain governed. |
| Install/select restored state as authoritative | Changes accepted meaning even if execution remains inactive. Requires guarded admission, whole effect, content/continuity policy and U's currentness basis for the claim being made. |
| Activate restored relationships | Makes specified actions usable. Can be a later, separately guarded commitment; validates the actual current context and evidence. A verified image does not pre-authorize later activation. |
| Replace current state with an old checkpoint | If advertised as uninterrupted current-state recovery, must preserve the required current observations. An explicitly authorized reset/branch may deliberately select historical content under a different contract, without reviving invalid old authority or claiming that no intervening work occurred. |

One implementation operation can combine these effects, but its claim must say
which it includes. Even a sealed installation is already authoritative if readers
or future decisions treat it as current. Conversely, an archive, historical
evidence record or cache over specified immutable inputs is not a structural
restoration merely because it reuses bytes. Include currentness only when the
consumer claims current authoritative selection or required continuity.

**WHY:** R1 separates invariant validity from whole continuity; R2 bounds coupling;
R3 separates content from references; R4 separates historical authority from
current admission. **WHAT:** K/V/C/J and U §§3/8, applied to W.E/F/J.
**HOW CERTAIN:** evidence-based reduction using existing bounded results plus
constructed histories. **WHAT-NOT-TESTED:** any checkpoint framework, physical
replica recovery, storage failure beyond the source profiles, or live orchestration.

## 9. Generalization and architectural placement audit

### 9.1 Actual non-Work-Unit claims: necessity controls

| Candidate consumer and existing claim | Concrete failure if the obligation is omitted | Does leaving F4 Work Unit-local make this existing claim wrong or ambiguous? |
| --- | --- | --- |
| J's two-domain reservation/transfer: authority in both domains, one shared resource, whole `(1,0)→(0,1)`, compatible recovery; domains explicitly are not Work Unit primitives. | R1 admits duplication or invariant-valid loss if joint effect/cut obligations are omitted. | **No.** J already specifies and attacks both omissions. It is concrete reuse of K, not a missing general confinement rule. |
| C's authority-holder restart: retained current work/content, cold or continuing evidence binding under declared storage survival. | R3 loses accepted bytes or confuses a recovered bearer; R4's general shape applies if current context differs. | **No.** C already distinguishes whole state, currentness, content and bearer reconstruction. Renaming this “structural” supplies no extra guarantee. |
| Requirements Mapping, State Management/Validation/Traceability/Recoverability; Engine Vision, State Management. | Restore old promotion-ready state after an accepted withdrawal, then promote. A valid historical record has replaced required current meaning (U.H8). | **No additional structural gap demonstrated.** U already proposes the exact current-state recovery clarification. These sources do not promise cross-domain migration, Work Unit confinement, or a checkpoint framework. Do not count this again as evidence for stronger F4 propagation. |
| ORCHESTRATOR, durable resumption from last-known state; future durable orchestration through the engine requirements. | Resume from a restored ready position after a superseding stop/prerequisite change (U.H9). | **No additional structural gap demonstrated.** U's existing candidate-versus-current clarification applies. “Orchestration” alone does not establish exclusive holder transfer or bounded-object containment. |
| Checkpointing/stacked diffs in R. | R4 would fail a current-authoritative activation claim, if one were adopted. | **No independent substantive contract found.** Topic is deferred and tied to Work Unit recovery/integration. A hypothetical failure does not justify propagation to a nonexistent checkpoint service. |
| Coupled replicas or moving durable objects between bounded domains outside Work Units. | R1 would refute a promised whole exclusive transfer; A5 is a conforming physical relocation with no new authority event. | **Only J supplies an actual relevant contract in the inspected sources**, with physical realization expressly unproved. No new replicated-state or migration consumer is established by a potential use case. |

This is a bounded source audit, not a claim that no future EDASES consumer can
need the pattern. It finds multiple actual consumers of the *existing* semantics,
but no non-Work-Unit promise that becomes materially ambiguous merely because F4
stays local once those semantics and the settled U clarification are respected.
That difference is decisive for architectural propagation.

### 9.2 Narrowest justified placement and impact map

| Placement | Necessity result |
| --- | --- |
| Work Unit lifecycle/disposition policy | Necessary local instantiation. S1 and S4 fail W.I/K without it; A1 fails W.J/K.19 without semantic authority comparison. Preserve this policy locally. |
| Shared bounded-object verification rule | Useful derived pattern (§3/§10), conditional on declared claims. No new mandatory rule demonstrated: J/C already carry the non-Work-Unit obligations. May be referenced rather than duplicated. |
| General EDASES structural-transition assurance rule | Reject as a new independent requirement. It either restates K/U, or overreaches by exporting W confinement/exact authority preservation to consumers that do not claim it. A2/A5 are counterexamples to stronger wording. |
| Modification of Kernel-0 verification semantics | Unnecessary. V already requires adequate dependency state, current whole effects, covered failure traces and conformance. Repeated consumer instantiation is not a missing Kernel obligation. |
| Research finding with local clarification proposals | **Narrowest justified placement now.** Records the reduction, bounded contract, counterexamples and explicit lack of incremental shared necessity. |

Only the following existing documents warrant **new proposed clarification** from
this review; none is edited here:

| Existing concept/contract | Proposed local consequence | Necessity and propagation limit |
| --- | --- | --- |
| F, §6/F4 and §8 propagation recommendation | Replace the unqualified shared-preservation conclusion with this reduction and scope. Distinguish general existing assurance obligations from W-specific confinement/disposition. | S1 requires an actual protection claim; A2 permits explicit widening; A5 has no authority transition. The review found no incremental non-W necessity for F4 promotion. This is a correction to the research recommendation, not a Kernel change. |
| W.J and its formalization of K.19 | Explain that destination compatibility is insufficient for permission-preserving reparenting; include retained policy and affected descendants through later activation, with narrowing or explicit subsequent widening as permitted by W. | A1 is possible under the existing local read+write relationship plus parent attenuation. This clarifies an existing W prohibition. It need not propagate Work Unit policy to other consumers. |

**Incremental project-wide change proposed: none.** No new registry entry,
methodology provision, Kernel mechanism, orchestration ownership, storage contract
or common lifecycle is required by this review. U's previously justified shared
currentness propagation remains valid and separate; it is neither withdrawn nor
claimed as a new result. K/V/C/J can cite this explanation if useful, but no
existing promise becomes false through omission of that editorial reference.

### 9.3 Necessity classification of every surviving finding

| Finding | Classification | Counterexample or reason no stronger addition survives |
| --- | --- | --- |
| Semantic dependencies must enter the authoritative view and current guard | Existing Kernel-0 semantics already sufficient | A1/S3; K protected-meaning closure and common order express the repair. |
| Surviving W dependents retain confinement; destruction has explicit dispositions and sealed interrupted remainder | Work Unit-specific derived policy | S1/S4; K expresses the policy but does not independently invent it for every consumer. |
| W reparenting must account for latent effective authority through later activation | Existing concept needing clarification, local to W.J/F | A1; no new authority primitive. |
| Explicit authority changes may accompany structural changes; exact rights preservation is overstrong | Existing Kernel-0 semantics already sufficient; reuse settled authority assurance | A2/A3; move-only authority is not sufficient for widening. |
| Whole promised effects differ from invariant-valid states; declared staged workflows may recover prefixes | Existing Kernel-0 semantics already sufficient | S2/S4/R1; K already states both cases. |
| Compatible cuts follow actual coupled commitments/dependencies; currentness uses the declared basis | Existing Kernel-0/C/J semantics and settled reusable U assurance already sufficient | R1/R2/R4; independent J bits refute global snapshots. |
| Historical capture, current installation, activation and reset are different possible effects | Existing concepts needing clarification in a consumer that uses them | R4 and §8.2; no independent checkpoint contract found to amend. |
| Conditional structural contract in §3/§10 | Reusable derived explanation of existing obligations, **not a newly necessary EDASES assurance rule** | Cross-consumer value is trace organization; no missing non-W requirement survives §9.1. |
| Stable StructuralTransition, Ownership, Checkpoint, or lifecycle ontology entity | New ontology distinction not justified | Erase the proposed entity names while keeping `σ/G/E/I`, authority and continuity: all witnesses remain expressible. |
| Shared transaction/coordinator, migration service, ownership registry, authority ledger or storage architecture | Broader architectural change not justified | No required history defeats K plus policy. A5 and independent domains refute unconditional necessity. Physical realization difficulty does not prove a new primitive. |
| Actual confinement, holder durability, equivalence of permissions and split-holder recovery | Implementation-dependent / unresolved | Concrete evidence tasks in §11; an abstract reduction cannot certify them. |

**WHY:** propagation is tested against claim owners rather than similarity of
vocabulary. **WHAT:** the exact source clauses and witnesses in §9.1, and the local
impact map. **HOW CERTAIN:** evidence-based within the pinned source boundary.
**WHAT-NOT-TESTED:** unlocated contracts, a repository-wide implementation audit,
future claims, or adoption of the proposed local clarifications.

## 10. Bounded transition contract for downstream formalization

For each selected consumer operation, supply the following six answers using
existing K/V and U contracts by reference where possible. This is a review aid,
not a schema, persisted certificate, protocol, or requirement that all consumers
support every kind of move.

1. **Meaning and dependencies.** What changes: physical representation,
   containment, entitlement, management, effective permission, or authoritative
   selection? Which survivors and dependent observations are affected, and why
   are excluded domains independent? State identity/continuity correspondence.
2. **Current guard and semantic effect.** Supply the concrete policy for `G/E/I`.
   Include authority for each structural and permission change, the full relevant
   path/resource dependencies, and conflicts such as creation versus final
   removal. A move's name or manager identity is not its guard.
3. **Preservation and permitted change.** Name the required protection/content/
   continuity observations and rights that change intentionally. For a
   permission-preserving move, compare retained policy through activation.
   If widening is intended, show the current authorization covering it. Define
   disposal separately from revoking borrowed access and from physical erasure.
4. **Commitments and observations.** Declare the whole effect(s), permissible
   prefixes, authoritative reads/acknowledgements and any external authorization
   point. Each committed stage must satisfy its actual claim during interruption;
   preparation cannot acquire protected meaning unnoticed.
5. **Failure and recovery.** Apply U's six-field recovery assurance to these
   observations: losses/survivors, currentness basis, binding/ordered use,
   uncertainty behavior and actual coupled cut. Retain required content. Identify
   what success is promised, rather than inferring it from safe indefinite denial.
6. **Witnesses and conformance boundary.** Give one successful permitted transition
   and actual post-recovery use, plus the relevant negative histories below.
   State how concrete handles, holders and effects map to the declared view, and
   what remains untested. No abstract invariant alone proves that mapping.

The minimum bounded cases for W formalization are S1–S4, A1, the W-permitted form
of A2, A3/A4, and R1/R3/R4, plus an independent-object control from R2. The pure
physical control A5 must add no authority event solely because location changed.
For another consumer, select only cases that exercise its real contract; do not
import W's sealed/single-parent policy merely to reuse a test fixture.

Acceptance means each required effect has an existing semantic expression, each
committed/recovered observation satisfies its declared contract, intended successes
exist, and weakened variants fail for the intended reason. A generic “migration
works” result or a final invariant check alone is insufficient. No implementation
or formalization is performed in this review.

## 11. Questions requiring realization evidence

| Unresolved question | Cheapest discriminating evidence after a realization/profile is selected | What foundational reasoning already settles |
| --- | --- | --- |
| Does the real protection boundary survive interrupted move/removal, including old handles and inbound routes? | One survivor and one formerly valid access path; interrupt at loss of old protection and attempt the excluded access before and after recovery. | S1/S2 specify the forbidden observation; changing ownership metadata alone cannot establish exclusion. |
| Can the chosen capability representation preserve the old effective restriction at Q? | Use A1's read+write/read fixture; move sealed, then separately activate and test both permitted read and forbidden write, including a descendant. Also exercise intentional narrowing and explicitly authorized widening. | Exact old bytes/ancestor retention is unnecessary; semantic equivalence or permitted reduction must actually hold. |
| Does a selected split-holder realization preserve a promised whole transfer? | One exclusive transfer, asymmetric loss/restoration at its commitment boundary, and both `(1,1)` and invariant-valid `(0,0)` attacks; check lost acknowledgement and accepted-content use. | J's abstract result is not physical evidence. Narrow the claim if this cannot be demonstrated; no protocol is selected here. |
| Does a staged workflow remain safe and useful through its covered failures? | Interrupt after each declared stage, recover through the actual path, verify bounded survivors/current authority and continue from at least one advertised successful recovery state. | An unclaimed atomic endpoint cannot be replaced by a convenient midpoint. Safety alone does not prove progress. |
| Can restored state be installed and activated under a changed context without stale authority? | R4 with a completed intervening restriction/manager change; distinguish candidate inspection, installation, and activation. Keep test-oracle history out of recovery. | U already defines the currentness/binding obligation; a fresh grant cannot certify missing historical work. |
| Does logical disposal meet its selected persistence guarantee? | Dispose while an old reference remains; attempt access and each claimed recovery path. | No secure physical erasure or destruction of borrowed external resources follows. |

These are bounded conformance investigations, not authorization to build a
migration service, storage layer, checkpoint framework or lifecycle engine.
Failure coverage, completion promises and which operations are supported remain
explicit consumer decisions. More foundational abstraction cannot establish the
empirical trust, durability or enforcement properties of a selected realization.

## 12. Propagation boundary

- **Shared EDASES contracts, if adopted:** reuse §3/§10 only as a derived
  verification reference to existing K/V and U obligations. This review proposes
  no new mandatory project-wide guarantee; §9 found no concrete incremental
  non-Work-Unit necessity. Preserve the already-settled authority/currentness work.
- **Work Unit-specific:** confinement/attenuation, sealed discovery and interrupted
  destruction, valid disposition destinations, containment policy and W.J's
  reparenting interpretation. Clarify A1 and narrow F4's propagation recommendation.
- **Must not generalize:** every byte move into an authority transition; immutable
  rights or parent identity; single-parent containment; no dual copies; one giant
  transaction; global synchronized snapshots; automatic checkpoint activation;
  secure erasure; exactly-once behavior; or termination from safety alone.
- **Suitable for cheaper-model downstream work:** after adoption and a selected
  consumer contract, make the two local documentation clarifications, extract the
  six answers in §10, formalize the finite cases and permitted successes, audit
  dependencies/links, and test one chosen realization using §11. Preserve claim
  boundaries and negative evidence. No agents are launched or models selected here.
- **Frontier reasoning still needed:** none for the present reduction. Escalate
  only an actual required history that cannot be expressed with existing K plus
  declared consumer policy, or a concrete non-Work-Unit contract needing stronger
  shared obligations. Failed implementation protocols alone do not meet that bar.
