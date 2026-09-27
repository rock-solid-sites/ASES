---
title: Work Unit-0 Foundational Reduction
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 566
baseline_commit: 6596931136f8276ae573041c2ade25a6f5ad0c64
baseline_branch: codex/kernel-0-reasoning-566
depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Kernel-0 Assurance Continuation
  - Kernel-0 Re-Minimization After Stronger Profiles
  - Concepts and Topics Registry
  - Concept: Levels of Abstraction
related_documents:
  - EDASES Work Unit Component Design
  - Kernel-0 Authority-Service Crash and Recovery
  - Kernel-0 Protected External Effects
  - Kernel-0 Multi-Domain Composition
consumed_by:
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Kernel and EDASES authority and recovery contract review
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-27
---

# Work Unit-0 Foundational Reduction

## 1. Result and authority of this review

**No new Kernel-0 primitive is justified by the current Work Unit requirements.**
Work Unit-0 adds a particular durable-confinement policy, containment and exposure
relationships, a continuity observation, and a stronger recovery profile. These
are substantive requirements: merely naming an arbitrary guard does not supply
them. They can, however, be expressed through Kernel-0's existing authoritative
view, guarded whole commitment, current authority, coherent ordering, and declared
failure and external-effect boundaries.

Three consequences merit reuse beyond Work Unit: composition of boundary
restrictions, a qualified currentness impossibility result, and preservation of
surviving objects' confinement during containment changes. Each is a **scoped
consumer/assurance rule**, with a counterexample below; none adds an authority
system, universal transaction mechanism, or required runtime object to Kernel-0.

| Foundational question | Outcome | Consequence before building |
| --- | --- | --- |
| Q1: New primitive? | Reducible to existing Kernel-0 semantics plus Work Unit-specific derived semantics. | Supply the concrete semantic obligations in §3; do not infer that the existing Kernel experiments already implement confinement. |
| Q2: Nested authority composition? | A broader EDASES boundary-composition rule is justified by T1–T4. Its enforcement reduces to the existing current guard and coherent order. | Use explicit local authorization **and** admission by all relevant boundaries. Define resource and effect meanings, rather than intersecting unrelated capability names. |
| Q3: Rollback/currentness? | A broader, conditional recovery rule is justified by T6. It is already expressible in Kernel-0's trust/failure contract. | Separate identification/authenticity from currentness; declare what excludes obsolete recovery. No mandatory freshness service or new authority primitive follows. |
| Q4: Destruction/transfer/reparenting? | Ordinary guarded compositions, with Work Unit-specific disposition policy. The general preservation rule is supported by T5 and T7–T10. | Preserve bounded survivors and whole coupled effects at every accepted/recovered step. Destination compatibility alone is insufficient to prevent widening. |

This is a research result proposed for review, not a modification of canonical
policy. The Work Unit specification's **A–L, dated 2026-09-27**, controls substantive
meaning. Its historical design is not used to reinstate old primitives. The
registry controls identities, lineage and relationships, not substantive meaning.
No canonical source was changed. No Work Unit model, tests or realization was
implemented in this task.

### Sources and scope

All repository evidence is read at the baseline commit above. The named baseline
branch's existing local checkout was behind that commit; this artifact is prepared
in an isolated branch starting at the exact commit, without changing that checkout.

| Reference | Source and use |
| --- | --- |
| W | [Work Unit specification](../../architecture/EDASES%20Work%20Unit%20Component%20Design.md), A–L: requirements being reduced. Its architectural choices are objects of investigation, not new research axioms. |
| R | [Concepts and Topics Registry](../registry/Concepts%20and%20Topics%20Registry.md), authority boundary and provisional Work Unit baseline: identity and lineage only. |
| K | [Kernel-0 Abstract Semantics](../kernel-0/Kernel-0-Abstract-Semantics.md): transition, authority, order, continuity, external-action contract. |
| V | [Kernel-0 Verification Obligations](../kernel-0/Kernel-0-Verification-Obligations.md): adequacy, non-vacuity and conformance obligations. |
| A | [Assurance Continuation](../kernel-0/Kernel-0-Assurance-Continuation.md): strongest completed bounded assurance and its exclusions. |
| M | [Re-Minimization](../kernel-0/Kernel-0-Re-Minimization.md): removal audit and existing-parameter reduction. |
| C | [Crash and Recovery](../kernel-0/Kernel-0-Crash-Recovery.md), derivation, recovery claims and strongest counterexample: followed to resolve whether authenticity can establish freshness. |
| X | [Protected External Effects](../kernel-0/Kernel-0-External-Effects.md), selected profile and negative results: followed to resolve the timing of revocation versus external effects. |
| J | [Multi-Domain Composition](../kernel-0/Kernel-0-Composition.md), removal attacks and recovery cut: followed to resolve whole transfer versus merely invariant-valid fragments. |
| S | [Stronger Realization](../kernel-0/Kernel-0-Stronger-Realization.md), final storage-cut result: followed to bound the strongest recovery evidence. |

The published evidence is not rerun here. T1–T10 below are short semantic
counterhistories constructed in this review, except where explicitly identified
as an adaptation of a previously executed experiment. They are not claimed as
new model-checker or realization results. No conversation history is used as
design authority.

## 2. Assumptions and reduction method

For each proposed distinction, remove it or express it through K, then ask which
required observation becomes impossible. This is the cheapest discriminating
test for this review: a short failure history before any new mechanism is built.
A counterexample to an insufficient policy is not automatically a counterexample
to Kernel-0's ability to express the sufficient policy.

The reduction makes these premises explicit:

1. Initial management authority and the trusted mediation/substrate boundary are
   declared, as K requires. A Work Unit, process, creator or recovered record
   cannot establish its own governing authority merely by assertion.
2. Containment denotes the current, well-founded enclosing path used by W.G.
   A move must not create a cycle or a dangling parent. Other grants and management
   links are not implicitly additional parents. General multiple-parent
   containment is not needed to reduce this model.
3. Confinement applies to the declared actionable effects and resources under the
   computer/physical trust assumptions in W.A. An abstract guard does not establish
   physical isolation, absence of covert channels, or control over arbitrary
   external systems.
4. Recovery correctness means a current whole authoritative view, or a view
   observationally equivalent for all required future permission and continuity
   observations. Byte equality, complete historical replay and a global clock are
   not the requirement.
5. Safety does not imply termination. A sealed object may remain sealed when
   authority, a valid destination, or sufficient recovery evidence is unavailable.
   A realization still needs successful histories; permanent denial is not an
   adequate implementation of the Work Unit claim.

**WHY:** these premises expose where a reduction could otherwise conceal missing
authority, trust or liveness assumptions. **WHAT:** K's parameters and necessity
table, V's adequacy rules, W.A/E/G/I/J. **HOW CERTAIN:** evidence-based premises for
this reduction. **WHAT-NOT-TESTED:** any concrete mediator, containment substrate,
or Work Unit recovery implementation.

## 3. Q1 — the smallest semantic delta

### 3.1 What Kernel-0 supplies, and what Work Unit must supply

K supplies the **form of the obligation**, not a ready-made Work Unit policy:

| Existing Kernel-0 distinction | Work Unit interpretation |
| --- | --- |
| Authoritative meaning versus candidate material | Current bounded identity, containment, grants, disposition and accepted contents determine permission/continuity. An interior claim to be a grant or a recovered image awaiting validation is not authority. |
| Guarded whole commitment | Creation, relationship changes, acceptance, sealing, authority change, transfer and final removal have declared whole effects and current guards. |
| Current eligibility and non-confusable evidence | Revoked grants and old attachment evidence cannot regain validity by identity reuse, restart or relocation. Management changes are guarded too. |
| Coherent current view and common acyclic order | A child action interacts with relevant ancestor restrictions, allocation changes and reparenting, even when its last write is local. |
| Continuity independent of executor lifetime | Work Unit identity, required accepted contents and relationships outlive disposable activity. The continuity projection need not contain a distinct Attachment Point or Execution object. |
| Explicit failure/external-action contract | Engine-loss recovery and confinement of external effects strengthen the selected profile. They are not inferred from executor-loss safety alone. |

The minimum additional **meaning** is:

- **A bounded object observation:** the same Work Unit can exist empty, inactive
  and without grants. Its identity and boundary are independent of a live actor.
- **A confinement policy:** every actionable crossing is Kernel-authorized;
  supporting allocation does not itself create an internally usable crossing.
  This includes any inbound action that creates actionable access, not only
  outgoing changes to an accepted work record.
- **Containment policy:** explicit child authorization, attenuation through the
  current enclosing path, independent restriction, resource constraints and
  management authority distinct from containment (§4).
- **Continuity and safe disposition:** preserve required contents and boundaries
  across the declared losses; remove a boundary only after dependent durable
  contents have valid dispositions; relocation must not silently widen authority
  (§6).
- **Recovery interpretation:** discover without executing the interior, establish
  current authority/currentness, recover sealed, and activate only currently
  authorized relationships (§5).

These requirements do not select a data representation. W.D additionally requires
identity/genesis, created-by provenance, project, current parent, resources,
capabilities, optional agent association and interpretable boundary state. Those
informational obligations remain part of the specification even where they are
not necessary to the security reduction.

### 3.2 A non-vacuous instantiation, without a schema

The authoritative view must distinguish the bounded objects that exist; their
current containment and exposure/authority restrictions; any resource quantities
whose change affects admissibility; required accepted content or trusted holders;
and the facts needed to determine recovery and disposition. This is a list of
semantic dependencies, not prescribed records or a class decomposition. A fact
cannot be dropped merely because it resides outside the component named Kernel.

The Work Unit guard checks current authority for the proposed action, relevant
boundary permissions, aggregate resource constraints, and the operation's
preconditions. For a content acceptance it also checks that required content will
remain bounded and recoverable under the selected failure profile. Management
actions require their own current eligibility; an interior attachment does not
implicitly supply it.

The whole effect specifies the promised change: for example, create an empty
bounded object; change one admitted relationship; move a sealed child together
with necessary restrictions; or remove an empty/dispositioned boundary. The
invariant includes surviving-content confinement, valid containment, configured
rights/resources, and agreement between authoritative relationships and any
boundary metadata presented as current. Denial leaves no protected effect.

There are successful histories under this policy: create an empty sealed Work
Unit; explicitly grant a supported capability and activate it; accept required
content; lose its transient actor; recover the same bounded content under current
authority; attach a replacement through a new valid relationship and continue.
An independently restricted child can coexist with an active parent. A sealed
child can move to a compatible destination, allowing its emptied old parent to
be destroyed. These are semantic witnesses of expressibility, not executed tests.

**Removal result:** erase the names `Grant`, `Resource`, `Attachment`, `Execution`
and `Boundary Record`, but retain their required observations as guarded
relationships and projections, and these histories and distinctions remain
expressible. Erase confinement, exposure, currentness, or whole disposition
instead, and the counterhistories below fail a required property. Thus the
semantic obligations survive; the named object decomposition is not forced.

**Finding F1 — no new primitive. WHY:** each requirement has a stated dependency,
guard/effect/invariant or failure-profile interpretation, with successful histories.
**WHAT:** W.A–L mapped to K/V and M's removal audit. **HOW CERTAIN:** evidence-based
reduction, not a uniqueness or universal minimality proof. **WHAT-NOT-TESTED:** a
formal Work Unit model, exhaustive transitions, or any concrete confinement and
recovery realization. No existing Kernel test count is a Work Unit test count.

## 4. Q2 — containment composes restrictions, not authority grants

### 4.1 The sufficient reading of the proposed rule

The proposed “every relevant boundary admits the action” rule is correct as a
**necessary condition**. By itself it does not create a child's permission: every
boundary could be permissive while the child has never received a grant. Within
K, the sufficient authority rule is the conjunction of:

1. an explicit, currently valid Kernel-authorized relationship enabling that
   originating activity to request the particular effect;
2. admission of that effect by every relevant boundary on the current containment
   path; and
3. all other current guard/invariant requirements, including joint resource use
   and the declared external authorization event.

For illustration only, the authority part of the guard can be written
`LocalCurrent(σ,W,a) ∧ ∧ Admit(σ,b,a|b)` over the relevant boundaries `b`.
`a|b` means the same proposed semantic effect as constrained at that boundary,
including its destination, quantity and scope. It is not a common token spelling
or a new primitive. Path selection and all predicates are evaluated in one
coherent current view. “Relevant” is determined by actual effect and containment
dependencies, never selected by the requester to omit an inconvenient ancestor.

For an action reaching outside the outermost container, all enclosing boundaries
constrain it. A relationship to something inside an ancestor still obeys that
ancestor's applicable internal-resource/containment policy; it is not an excuse
to acquire an ungranted route to the world. Mediation that translates one callable
operation into another must preserve the relevant effect constraints. A syscall
name at one boundary and a service capability at another cannot be compared as
untyped set elements.

### 4.2 Discriminating histories

**T1 — no inherited permission; no bypass of an ancestor.** There are one parent
P, one child C and one external action `send`. With P admitting `send` but no
child grant, allowing C to send invents inheritance. With an explicit C grant but
P denying `send`, allowing C to send bypasses containment. Local authorization
and boundary attenuation are both necessary. Neither can replace the other.

**T2 — joint resource limits.** P supplies one simultaneously usable unit. C1 and
C2 each request one unit. Checking only “each child request ≤ parent's capacity”
admits both and consumes two units. P's current predicate must include the
coupled allocation/consumption invariant. If the requests race, their validation
and commitment must admit a coherent order; detached checks against the same
unused unit fail. The quantities may concern different resources, with distinct
predicates: no universal scalar or allocation algorithm is forced. This is the
same failure shape as J's double reservation, not a new accounting primitive.

**T3 — completed ancestor revocation.** C observes a valid child grant and an
admitting P. P's revocation completes. C then starts an affected action using the
old observation. Checking only C's stored grant admits a forbidden action. The
current path predicate denies it. The historical observation cannot be ordered
before the already completed revocation to justify this later request.

**T4 — containment is not management.** P contains C; activity in P has no grant
to administer C. If containment alone authorizes that activity to delete C or
change C's grants, the management restriction has disappeared. Conversely, an
external current manager may have explicit authority to restrict C while P is
sealed. A rule that requires this manager to exercise P's interior attachments
would incorrectly deny the permitted management action. Management authority
and effect-origin/containment are different dependencies within the same K view.

### 4.3 Coverage and temporal limit

| Required case | Reduction |
| --- | --- |
| Attenuation without inheritance | T1: explicit local relationship plus all applicable restrictions. A parent's own callable attachments and its permission to support child effects are not interchangeable sets. |
| Heterogeneous capabilities/resources | Interpret the semantic effect at each boundary and enforce relevant coupled quantities (T2). No conversion between unlike capability labels is assumed. |
| Independent child restriction | Changing C's own restriction denies C even while P remains permissive. No parent revocation is necessary. |
| Ancestor revocation | All affected descendants lose effective use through that boundary (T3). Derived loss of effective authority need not rewrite every descendant grant. |
| Descendant administration | Explicit Kernel authority can target a descendant; mere ancestry cannot (T4). The manager remains subject to restrictions that actually govern its own authority. |
| Reparenting | The old path, new path, affected descendants, resource obligations and management rights enter the relocation guard and whole effect. See T5 and §6. |

Revocation must be interpreted at the **declared authorization event**. X proves
that decision-time authorization can allow later sink acceptance under its
selected irrevocable-obligation profile. That is not evidence that Work Unit
sealing automatically stops every in-flight consequence.

If an action was only proposed/queued before sealing and is authorized afterward,
it must pass the then-current full path. If it was irrevocably authorized before
sealing, later completion or observation has the declared external-effect
semantics. A claim of no sink acceptance after sealing requires ordering or
cancellation at the sink; a claim of no later visibility is stronger still. W.H
does not supply a universal mechanism for either. Builders must not silently
inherit X's permissive completion policy or advertise stronger cancellation than
their selected attachment contract supports.

**Finding F2 — generalize the composition obligation, not the object vocabulary.**
Proposed EDASES rule: wherever nested boundaries claim to constrain effects,
explicit originating authority is limited by every applicable current boundary
restriction at the claimed authorization event. Joint resource dependencies are
included in that admission. **WHY:** T1–T4 lose required properties when any part
is removed. **WHAT:** W.B/G/H/J, K's authority/order/external clauses, V and J.
**HOW CERTAIN:** evidence-based semantic reduction; the counterhistories establish
necessity for the stated claims. **WHAT-NOT-TESTED:** actual heterogeneous mediators,
resource enforcement, arbitrary nesting or sink cancellation. Placement: a shared
authority-composition/verification rule for bounded consumers, not a new K
primitive and not a mandate that every Kernel consumer have containment.

## 5. Q3 — currentness is a trust obligation, not boundary metadata

### 5.1 What the strongest Kernel result establishes

A/S report recovery at 90 observed storage-call process cuts and 12 deliberately
partial writes, with the OS/storage remaining live. C reports the more decisive
negative: restore an authentic old same-root store after acknowledged revocation,
restart, and old authority can act. The positive storage-cut result **does not
repair that failure**. Trusted current surviving storage remains a premise. J's
joint recovery result is model-only; these results do not establish arbitrary
Work Unit storage, power-loss durability or physically split holder recovery.

**T6 — indistinguishable recovery histories.**

- H0: a whole image S records grant g as current; the holder is lost; recovery
  sees S. Successful continuation using g is permitted by the selected profile.
- H1: start at S; revoke g and acknowledge completion; lose the holder; roll back
  every recovery-visible fact in the declared domain to S. Recovery again sees S.
  Old g must now be denied.

If all available information is identical, recovery cannot reliably distinguish
the required outcomes. An identity, version, signature, root record, provenance
chain or “outside-of-the-box” label included in the rollback is identical too.
Random selection cannot establish which history occurred. This is the semantic
form of C's executed same-root attack; no Work Unit rollback experiment was run.

The qualified general result is:

> If the failure model permits histories requiring different current permission
> or continuity outcomes to yield identical recovery-visible information, no
> procedure using only that information can establish the required current state.

This is a conditional indistinguishability argument. The shorter candidate in W.E
needs these premises: a genuinely obsolete but observationally indistinguishable
state is possible, and the claim requires discriminating it. It is not a claim
that every immutable state is unverifiable or that byte-identical states must be
distinguished when all required future observations are equivalent. Rejecting
both histories prevents stale use but does not establish non-vacuous recovery.

### 5.2 Five kinds of information that must not be conflated

| Information | What it can establish | What it cannot establish by itself |
| --- | --- | --- |
| Intrinsic boundary information | Identity/genesis and interpretation/discovery without trusting the interior, under its integrity assumptions. | That recorded grants or parentage remain current after rollback. |
| Current authoritative relationship state | Governing rights, containment and permitted actions, **once its currentness is established under the declared profile**. | Its own freshness just by describing itself as authoritative. |
| Provenance | Who created something, or which accepted history an authentic record belongs to. | Present management authority or absence of a later revocation. |
| Recovery hints | Candidate locations, last-known topology and attachment descriptions to investigate while sealed. | Permission to activate what is found. |
| Freshness/currentness evidence or assumption | Exclusion of obsolete alternatives that would change required observations, when trustworthy, relevant and coherently bound to the recovered view. | A universal guarantee merely because the evidence is stored elsewhere. |

“Outside the rollback domain” means outside the **failure projection**, not outside
the Work Unit's interior or in another process. An independently located replica
rolled back with the original is still inside that domain. A surviving root ID
that has not changed across H0/H1 also does not discriminate them. The surviving
fact must be bound to this domain and distinguish the relevant histories; checking
it and later enabling effects cannot be separated by an unaccounted authority
change. Interacting domains must recover a compatible whole cut, not merely pass
independent freshness checks.

### 5.3 Minimum architectural consequence

Every recovery claim should explicitly state:

- what state/facts may be lost or rolled back together;
- what trusted preservation premise or surviving evidence excludes obsolete
  authoritative alternatives, including completed revocations and whole effects;
- how that evidence is associated with the recovered domain/view and the current
  authority to mediate it; and
- that unresolved currentness leaves the object bounded and inactive.

For the supported process-loss profile, the premise can remain **current surviving
storage**. No external freshness mechanism is required for a failure excluded by
that claim. If rollback is included and successful current recovery is promised,
some discriminating trusted information must escape the rollback, or recovery
must refuse the unsupported claim. An outside fact that also rolls back merely
moves the unresolved trust boundary.

A genuinely new management authorization can establish a new permission; it
does not prove that recovered contents, parentage or dispositions are current.
Nor can cold recovery's rejection of old bearers recover lost accepted content.
The current cut and the engine's present authority are both needed for W.E/F.

**Finding F3 — make currentness explicit across EDASES recovery contracts. WHY:**
T6 shows that intrinsic authenticity cannot supply the required discrimination.
**WHAT:** W.D–F, K's trustworthy-observation and failure parameters, C's actual
same-root counterexample, A/M/S and J. **HOW CERTAIN:** the impossibility is proven
under the stated indistinguishability premises; the proposed architectural
placement is evidence-based. **WHAT-NOT-TESTED:** a rollback-resistant Work Unit
realization, a particular freshness source, power loss, simultaneous loss of all
trust anchors, or availability of successful recovery. Required concept: an
explicit currentness/trust dependency in a claim. No new authority system,
mandatory service, clock, stored version type or stable registry entity is forced.

## 6. Q4 — safe disposition and relocation are guarded compositions

### 6.1 No silent widening during reparenting

**T5 — a permissive destination is not sufficient.** C has a locally granted
relationship allowing read and write, but parent P limits its effective use to
read. The broad local relationship cannot bypass P and therefore does not violate
the current effective-capability rule. Seal C, move it under Q, which permits both
read and write, and retain C's relationship. Destination compatibility holds.
Reactivating solely by toggling C's inactive condition now enables write, without
an explicit decision to widen permission.

This is why W.J's “destination supports every retained grant” is necessary but
not by itself sufficient for W.J/K.19's no-silent-widening requirement. The same
problem occurs for any broad local scope constrained by an old ancestor. A model
that forbids such latent breadth must actually preserve that restriction; it
cannot assume it away while permitting the history above.

The relocation effect must retain a restriction sufficient to prevent the move
alone from enlarging the child's authorized effect scope, or reduce/revoke the
relationships responsible, or deny that relocation. This comparison concerns the
permission policy of retained relationships, not just the empty enabled-action
sets of two sealed snapshots. Ignore only the child's temporary move-related
inactive condition when assessing that policy; do not erase authority withdrawals
or other ancestor restrictions. Apply the same obligation to affected descendants.
Any later widening requires an explicit current Kernel authorization for that
widening, as allowed by W.J's subsequent reactivation with different grants.

The old parent need not be retained forever as a governing authority. Its relevant
restriction can be expressed by the resulting Kernel-governed relationships;
alternatively the move can drop grants. No migration token, second authority
ledger or permanently stored “old effective rights” object follows. If a chosen
capability language cannot express or establish the required restriction, safe
reduction/revocation or refusal is valid; syntactic label matching is insufficient.

### 6.2 Whole changes and safe intermediate states

For each durable object surviving a change, its required containment must remain
effective throughout authoritative observation and recovery. W.I supplies two
dispositions: transfer to a valid bounded destination, or logical disposal within
the declared storage boundary. Revoking access to a merely borrowed external
resource does not destroy that resource. Moving a child changes containment;
moving governing authority is a different guarded effect. If both are promised
as one operation, both belong to its whole effect.

An admissible destructive progression is: commit sealing/disablement; disposition
contents through separately authorized whole changes while the boundary persists;
then remove the boundary only after no surviving durable object depends on it.
Recursive destruction applies the same obligation to each nested child. Each
accepted prefix remains bounded. The entire potentially long workflow need not
be one atomic transaction, and no new transaction primitive follows.

Once destruction has **durably begun**, interruption leaves its surviving objects
bounded and sealed. Loss before its initial seal commitment may leave the previous
whole state: an uncommitted proposal is not proof destruction began. Recovery
must not activate an ambiguous remainder. No progress deadline is implied.

Final removal's guard includes all surviving dependents and conflicts with any
proposal that could create a new dependency. A simple Work Unit policy can deny
new contents/grants while disposition is in progress, but a required new named
lifecycle state is not the foundation. Coherent admission and safe accepted
prefixes are. The guard must cover real containment dependencies, not just a
possibly stale enumeration of directory entries or child records.

**T7 — remove before disposition.** W contains a durable file F. Remove W's
boundary while F survives, and let F become generally accessible. No authority
record need be malformed; the confinement property is nevertheless lost. Retain
the boundary until F is transferred or disposed. A boundary may cease only when
no surviving dependent needs it.

**T8 — a split move.** P bounds C. Commit removal of C's old containment; crash
before establishing its new valid containment in Q. C is now orphaned/unbounded,
contrary to the promised whole move. Reversing the order may instead expose C
through two effective contexts or violate the single-parent claim. A whole
reparenting transition has the permitted old or new endpoint, including required
restrictions. Preparation can remain candidate material while old containment
persists. A separately committed bounded intermediate is also possible if it is
explicitly a different allowed sequence, not mislabeled as the one whole move.

**T9 — individually authentic recovery fragments.** A move from P to Q has
committed. Recover P's pre-move ownership and Q's post-move ownership: C appears
in both. Recover the opposite fragments: C appears in neither. Neither is the
promised whole endpoint. This is J's already evidenced incompatible-cut/
half-transfer failure applied to containment. The combined current view and
compatible recovery cut cover all coupled effects, even across physical holders.

**T10 — stale final-removal check.** A destroyer observes W empty. Before removal,
another authorized operation commits a new durable child C in W. The destroyer
then removes W using its earlier observation. C loses required containment.
Completed-before-initiated precedence and coherent guards prevent treating the
old emptiness check as permission for the later removal. This uses K's ordinary
conflict ordering; it does not require globally ordering unrelated Work Units.

The whole-effect obligation is stronger than checking a final invariant: J's
split transfer recovers `(0,0)`, which still satisfies “at most one reservation”
while losing the transferred resource. Likewise, declaring a vanished child
“absent” may satisfy a no-orphan predicate while losing required content. Check
the promised effect and continuity as well as surviving-state invariants.

External disposition must also refine the declared effect. Updating an ownership
label does not revoke an old usable handle or move protected bytes by itself.
If an irreversible protected external effect occurs before its authority is
established, later denial or compensation cannot repair that unauthorized event.
An unsupported sink may force refusal or a weaker explicitly selected claim;
there is no semantic promise of a transaction across arbitrary systems.

Logical deletion does not establish secure erasure from backups or media. A
disposed object must not regain actionable existence through supported recovery;
obsolete copies beneath an excluded rollback boundary remain subject to §5's
explicit limitation. Neither physical erasure nor deleting all historical
provenance follows from Work Unit destruction.

**Finding F4 — general preservation rule, ordinary Kernel composition.** Proposed
rule for any consumer claiming durable bounded objects: a containment change must
preserve effective confinement of every surviving dependent, must not silently
widen its authority, and must recover whole effects at its declared granularity.
**WHY:** T5 and T7–T10 fail those properties without needing a Work Unit-specific
execution object. **WHAT:** W.H–K, K's G/E/I, order and failure clauses, J's removal
attacks and M. **HOW CERTAIN:** evidence-based reduction; concrete whole-cut
evidence is bounded and composition is model-only. **WHAT-NOT-TESTED:** multi-holder
relocation, physical confinement through interruption, recursive-destruction
termination, arbitrary storage disposal or cancellation. Placement: shared
bounded-object consumer obligations, instantiated by Work Unit; no general
transaction service or core containment object type is justified.

## 7. Ontology consequences forced by the reduction

This is not a terminology redesign. R's identities remain unchanged, including
historical/superseded identities. The consequences proposed for later review are:

| Current concept | Necessary meaning and resulting placement |
| --- | --- |
| Work Unit | Remains the bounded continuing consumer object. Empty existence and durable confinement are meaningful observations; no resident executor is necessary. It is not a new Kernel-0 primitive. |
| Grant | A Kernel-authorized relationship/change with current eligibility. A separate Grant authority engine is unnecessary. Removing the name is harmless only if explicit authorization and non-resurrection remain. |
| Resource / Attachment | Supporting allocation versus internally actionable exposure remains necessary policy. Two disjoint primitive object classes do not. An allocation becoming callable requires a guarded change; changing labels cannot create access. |
| Boundary Record | Intrinsic protected information/projection associated with W, not necessarily an independently stored aggregate. It must reflect authoritative changes coherently; a mutable interior copy cannot govern. “Outside the interior” does not mean outside rollback. W.D's informational fields remain required; project and creator do not become permissions. |
| Execution | Descriptive activity; no required durable Execution identity. Distinguishable old/current authority attempts still matter even when their activity has no Execution object. |
| Containment | Current dependency path for confinement and attenuation, distinct from management, provenance and organization. General composition can be shared without renaming R's Work Unit Containment identity. |
| Sealed / revoked / destroyed | Preserve different facts, not necessarily an exclusive state enum. Partial revocation need not seal everything; an empty unactivated unit can be sealed without prior revocation; destruction is loss of the object after disposition. Collapsing these facts loses required histories. |
| Transfer / delegation / reparenting | Delegation can retain the delegator's rights; authority transfer removes the transferred entitlement from old evidence; reparenting changes containment and may change constraints. None implies the others. One whole proposal may combine them explicitly. |
| Currentness | A required distinction/dependency in recovery assurance when histories must be distinguished, not a new source of permission. No mandatory stable concept ID or runtime service is established by this review. |

**WHY:** only distinctions whose removal changes required histories are retained
as semantic obligations. **WHAT:** F1–F4, W.B–K and R's provisional/historical
statuses. **HOW CERTAIN:** evidence-based ontology consequences. **WHAT-NOT-TESTED:**
ergonomics or performance of alternative representations. No canonical identity,
summary, lifecycle spelling or required metadata field is changed here.

## 8. Propagation and remaining evidence boundary

### Proposed consequences for review

| Destination | Consequence | Counterexample / existing basis |
| --- | --- | --- |
| Kernel-0 | Retain the current primitives and semantics. Work Unit verification must instantiate real policy/dependencies and the stronger failure/external profile. | F1; K/V/M. |
| Shared EDASES authority contracts | Record explicit local permission plus coherent boundary attenuation, including joint resource dependencies. Scope it to consumers claiming such boundaries. | T1–T4; F2. |
| Shared EDASES recovery contracts | Record the qualified currentness result and the required trust dependency. Intrinsic metadata is not a freshness witness merely by construction. | T6; F3 and C's executed rollback attack. |
| Shared bounded-object verification obligations | Preserve surviving confinement and prevent silent authority widening during containment changes; state whole recovery obligations. | T5, T7–T10; F4 and J. |
| Work Unit specification/formalization | Make the reparenting no-widening obligation explicit beyond destination compatibility; instantiate the existing A–L invariants rather than adding historical machinery. | T5; W.J/K.19. |
| Engine and attachment/substrate boundary | Restarted engines need current mediation authority and a validated recovery view. Attachments need explicit authorization/cancellation timing and actual confinement enforcement. | T3/T6/T8; W.E/F/H, K and X. |
| Registry | Preserve present IDs and lineage. Reflect reviewed relationship/placement consequences later if adopted; do not create primitive identities to match convenient implementation objects. | §7; R's authority boundary. |

These are the findings that must be carried into the build contract before
implementation choices are treated as settled. They do not require canonical
edits as part of this task. Acceptance of the proposed general wording is a human
architectural review decision; no missing primitive is being reserved for a
builder to invent.

### Questions reasoning alone cannot settle

| Open realization question | Cheapest discriminating evidence required | Safe boundary meanwhile |
| --- | --- | --- |
| Does actual mediation cover every claimed crossing, including retained handles after ancestor revocation? | One selected attachment: establish access, revoke an ancestor, then attempt new use through the previously valid route. | No blanket confinement claim from a passing abstract guard. |
| Does the chosen recovery substrate supply the declared current whole cut and required contents? | Interrupt one accepted coupled change at a real persistence boundary and recover normally; replay old evidence. Include a rollback discriminator if rollback resistance is claimed. | Current surviving storage remains an explicit assumption; unresolved objects stay sealed. |
| Can a chosen destination preserve real confinement and attenuation through a move? | One sealed child with a restriction supplied by its old parent; relocate under a less restrictive parent, interrupt at the ownership boundary, and attempt the formerly excluded effect. | Drop unsupported grants or deny the move; do not infer safety from a new parent label. |
| Can physically separate holders recover a coupled move? | A single cross-holder transfer with failures producing incompatible local cuts. | J remains model-only. A simpler declared shared failure boundary may be selected without claiming distributed recovery. |
| Does logical disposal prevent surviving actionable access under the selected storage guarantee? | Dispose one durable object while a previously valid reference remains, then attempt access and covered recovery. | Retain the containing boundary until disposition is established; no secure-erasure claim. |

These are evidence targets, not a build plan. Selecting the promised external
authorization/cancellation event and failure class is a contract decision, not a
question experiments can decide for the operator. Once selected, the empirical
questions above are appropriate for implementation/test work. Unselected stronger
claims do not block building the bounded model with explicit exclusions.

## 9. Final build boundary

**Sufficiently settled for cheaper implementation/test models:** instantiate the
existing Kernel semantics with empty durable bounded objects, explicit exposure
relationships, full-path attenuation and coupled resource constraints, independent
management authority, executor-independent content, sealed recovery, safe
disposition, and reparenting that cannot activate latent permissions. Preserve
W.D's metadata observations without granting them self-certifying freshness.
Supply non-vacuous successful histories and counterhistories T1–T10; state the
chosen recovery and external-effect contracts before claiming conformance.

**Reserved for frontier reasoning:** no unresolved foundational primitive is
currently identified. Return for foundational review only if a concrete required
history cannot be represented by these existing semantics, or new evidence
invalidates one of the declared trust/composition premises. Stronger rollback,
sink-cancellation or physically split recovery promises need an explicit claim
and discriminating evidence, not speculative new ontology. Adoption of the three
broader rules remains an architectural review decision.

**WHY:** the four foundational questions have explicit outcomes and their remaining
uncertainties concern selected contracts or realization conformance. **WHAT:**
F1–F4, T1–T10, the source map and declared exclusions. **HOW CERTAIN:** evidence-based
readiness for bounded formalization and testing; not proof of a built Work Unit.
**WHAT-NOT-TESTED:** no Work Unit code, model, schema, API, physical isolation,
storage implementation or independent adversarial review was produced in this task.
