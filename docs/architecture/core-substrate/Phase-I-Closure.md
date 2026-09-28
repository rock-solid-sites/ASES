---
title: EDASES Phase I Core Substrate Closure
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 4e800957a673c8bd07eeea3c3c909349cdae76ac
depends_on:
  - EDASES Execution Engine Roadmap
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Work Unit-0 Foundational Reduction
  - EDASES Work Unit Component Design
  - EDASES Currentness and Recovery Assurance
  - EDASES Bounded Structural Transitions
consumed_by:
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Phase I architectural closure review
related_documents:
  - Phase I Processorless Core Falsification
  - Phase I Core Substrate Verification Work
  - Phase I Revocation Verification and Q1 Reduction
  - Phase I Concurrent Realization Proposal
  - Kernel-0 Assurance Continuation
  - Kernel-0 Re-Minimization After Stronger Profiles
  - Kernel-0 Protected External Effects
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Phase I — core substrate closure

## Investigation boundary and restart point

This investigation addresses [roadmap Phase I](../EDASES-Execution-Engine-Roadmap.md)
on `codex/execution-engine-roadmap`. The initial evidence tree is the exact
baseline above. Crosslink #571 is the active investigation under #566. New
histories here are reasoned counterexamples, not executed experiments. Earlier
model counts and crash experiments are inherited evidence within their original
bounds; this investigation does not reclassify them as Work Unit implementation
assurance. Canonical Work Unit A–L controls substantive Work Unit requirements.
The obsolete design beneath A–L does not restore Execution or Attachment Point
primitives.

This is a derived architectural candidate, not a canonical methodology revision.
The intended freeze concerns what downstream builders must implement or verify
for this candidate. It is not a declaration that a deployed core already exists.

**Result:** a scoped Kernel + Work Unit core survives the attacks without a new
primitive or persistent Processor. Trusted guard computation remains necessary.
The former Q1 ambiguity is resolved by the canonical Work Unit clarification:
engine loss disables protected capability use but does not itself require interior
computation using still-valid resources to stop. Bounded quiescence is a stronger,
optional profile rather than a baseline correctness obligation. The
[synthesis](#9-concise-synthesis-and-handoff) states the conclusion and limits;
the [falsification record](./Phase-I-Processorless-Falsification.md) preserves
fifteen Processor attacks; the [verification plan](./Phase-I-Verification.md)
assigns the remaining bounded formalization, implementation and hostile testing.

**Restart cursor:** the architectural investigation is complete at the semantic
level; start downstream work at verification F1/F3. No prototype, new model check or
independent review has been completed. Concurrent commits `76a38fb7`/`8bebb403`
introduced an alternative realization argument into the same file; its preserved
[proposal](./Phase-I-Closure-Realization-Boundary.md) and the [disposition](#10-disposition-of-the-concurrent-realization-proposal)
keep that contribution recoverable without mixing contradictory contracts.

## Evidence used and why

| Evidence | Question it constrains |
| --- | --- |
| [Kernel semantics](../../research/kernel-0/Kernel-0-Abstract-Semantics.md) and [verification obligations](../../research/kernel-0/Kernel-0-Verification-Obligations.md) | What counts as an admissible whole commitment, current authority, continuity, and a sufficient realization? |
| [Work Unit A–L](../EDASES%20Work%20Unit%20Component%20Design.md) and [foundational reduction](../../research/work-unit-0/Work-Unit-0-Foundational-Reduction.md) | Which confinement, metadata, containment, loss, and disposition guarantees actually have to survive? |
| [Assurance continuation](../../research/kernel-0/Kernel-0-Assurance-Continuation.md), [re-minimization](../../research/kernel-0/Kernel-0-Re-Minimization.md), and [crash/recovery](../../research/kernel-0/Kernel-0-Crash-Recovery.md) | Which mechanisms already have bounded evidence, and where does it stop? |
| [Currentness assurance](../../research/currentness/EDASES-Currentness-Recovery-Assurance.md), especially §3 | Which indistinguishable histories require withholding a claim, and which still permit common safe continuation? |
| [Protected external effects](../../research/kernel-0/Kernel-0-External-Effects.md) | Why decision, irreversible acceptance, later visibility, and knowledge of outcome must be distinguished. |
| [Bounded structural transitions](../../research/structural-change/EDASES-Bounded-Structural-Transitions.md) | Whole disposition, no latent widening, and compatible recovery cuts already reduce to the existing semantics. |

The roadmap names *EDASES Boundary-Composed Authority*, but no separately titled
file was found in this tree. The substantive boundary rule is available in the
foundational reduction §4. No missing separate document is treated as evidence.
The earlier UI synthesis was consulted as required by AGENTS.md; its graph,
statechart, and scheduling proposals do not decide any Phase I mechanism here.

## 1. A concrete baseline without a new primitive

Retain Kernel-0's six semantic distinctions, with Work Unit's particular policy:
authoritative meaning versus candidates; proposal versus whole commitment;
current versus past permission; trustworthy discrimination between attempts that
require different outcomes; a coherent view/common acyclic order for interacting
commitments; and continuing information independent of executor lifetime.

The least demanding useful realization target is one **logical authoritative
commitment boundary**, retained accepted contents, and completely mediated
selected attachments. A single serialized holder is a sufficient comparator;
multiple holders are not needed to demonstrate the core. This is not a
requirement for one physical process, a database product, or one global clock.
Storage, protection and external mediators actually relied upon count in the
trusted boundary wherever placed.

The baseline supports finite, explicitly represented Work Units, a well-founded
containment forest, explicit local grants plus full-path restrictions, bounded
resource quantities, immutable accepted content, cold recovery, and explicit
replacement. It must admit useful create/grant/accept/replace/recover/continue
histories, not merely an empty object and universal denial. A finite-capacity
implementation may refuse new work before exceeding its declared limits; it
cannot erase required accepted work to make room.

### 1.1 Failure profile to implement first

| Event | Required result in this candidate | Assumption or boundary |
| --- | --- | --- |
| Executor or attachment process disappears | Preserve the Work Unit, accepted contents, and current authoritative relationships; replacement is a guarded event. | Neither executor-local bytes nor executor assertions are a trusted continuation store. |
| Engine mediation process stops while host protection and storage survive | Prevent new protected admission and protected capability use through the lost mediator; retain bounded objects and committed contents; preserve surviving resource grants where valid; recover cold and sealed before fresh capability activation. Interior computation may continue using surviving resources. | A surviving/fail-closed protection mechanism must make capability loss real at the effect boundary. Its realization must be tested, not inferred from a metadata flag. |
| Loss during commitment, including lost reply | Recover a permitted whole endpoint; preserve irrevocably committed effects even if unacknowledged. | Current retained storage supplies a coherent recoverable cut. No automatic retry or exactly-once promise follows. |
| Transient loss of contact with authority | Withhold affected new commitments; an isolated executor cannot confer authority on itself. | No partitioned multi-writer availability guarantee, timeout election, or takeover by suspicion. |
| Missing, unreadable, or detected-inconsistent recovery material | Keep affected objects bounded and inactive; do not silently bootstrap an empty replacement. | Preservation/availability may be lost. Refusal is not successful recovery. |
| Machine restart, power loss, failed writes, rollback, media corruption | Do not inherit a positive recovery guarantee from the process-loss experiments. | A stronger profile needs its own storage/protection evidence. Silent rollback or corruption cannot be promised detectable under the baseline. |

These are *selected assurance bounds*, not permission to weaken Work Unit's
abstraction. Engine loss cannot release its contents. Power-loss durability,
rollback-resistant successful recovery, and physical erasure remain explicit
stronger claims. An implementation must disclose which failures its evidence
covers; unsupported failures cannot be reported as passing this profile.

### 1.2 First coupled removal tests

**H1 — a seal bit does not revoke a route.** Grant an executor a direct handle to
accepted bytes. Replace it or lose the engine. The old process writes through the
handle while a record says sealed. Kernel records remain valid; authoritative
meaning and confinement do not. Required repair: the concrete route must be
mediated at its claimed authorization event, revoked by a trusted substrate, or
restricted to candidate/private material whose mutation changes no accepted
meaning. Adding a durable Execution record, heartbeat or Processor does not close
the route. This sharpens realization, not Kernel semantics.

**H2 — a new engine is not a new authority by assertion.** Engine A loses contact
with storage but remains alive. B loads a saved grant table and serves replacement
execution; A resumes with old handles. A shared root or generation label does not
prevent both from acting unless the actual acceptance boundary discriminates
current authority. The single-holder baseline permits B to activate only after
trusted exclusion of A from every ingress that can admit new protected effects. A surviving host can supply
that exclusion; distributed takeover would require additional realization
assumptions. No lease or election is introduced to hide a missing exclusion proof.

**H3 — cold recovery fixes bearers, not missing work.** Accept x, then accept y;
restore an authentic image containing x and drop all old endpoints. New endpoints
cannot reconstruct y. The currentness obligation covers accepted contents and
coupled relationships as well as authority. Cold recovery reduces bearer
reconstruction requirements but does not remove current-storage trust.

**H4 — already-authorized consequence.** Commit a precise external obligation;
replace its producer; the sink accepts it afterward. This is valid only under an
explicit decision-authorized obligation whose authorization survives replacement.
It violates a different promise requiring current producer authority at sink
acceptance. A raw network capability is not an immutable exact obligation. The
profile must identify the authorization event and cancellation behavior before
such an attachment can be granted. A later denial or compensation cannot undo an
unauthorized irreversible consequence.

**WHY:** H1–H4 distinguish actual failure behavior from valid-looking records.
**WHAT:** Work Unit C/E–K, Kernel's effect/failure parameters, and the existing
external-effect/currentness counterexamples. **HOW CERTAIN:** evidence-based
architectural constraints; the two-history information limit is conditional logic.
**WHAT-NOT-TESTED:** a Work Unit confinement substrate, engine-death teardown,
partitioned takeover, host restart, or arbitrary external sinks.

## 2. Trusted realization: enforce effects, not component names

The following are trusted **functions**, not a compulsory service decomposition.
They may share one implementation. Moving a function into an adapter does not
remove it from the assurance boundary.

| Trusted function | Smallest obligation | Removal witness |
| --- | --- | --- |
| Admission and interpretation | Evaluate the supported policy against the actual current dependencies; interpret operations and their exact whole effects consistently. | A correct transition store running the wrong policy authorizes forbidden work. |
| Complete mediation and confinement | Every claimed actionable crossing and mutation of accepted meaning passes an authorized route; inactive objects retain protection. | H1, including inbound attachment creation and retained descriptors. |
| Recoverable commitment and content retention | Acknowledged/irrevocable commitments and required bytes survive the selected loss together, or through a declared equivalent retained representation. | H3; reference survives but bytes do not; metadata and contents from different cuts. |
| Authority ingress and engine activation | Establish bootstrap/current management, bind request evidence to its permitted origin/scope where required, and exclude superseded holders. | H2; an old caller claims the replacement's position. |
| Attachment conformance | Map the proposed resource, destination, quantity and operation to the concrete effect and its authorization event. | A granted read is translated into a write, or a path is retargeted after validation. |
| Observation/derivation validation, when used | Establish exactly the premises a guard relies on, bound to current inputs and declared semantics. | A signed but false or stale computed result passes admission. |

The supporting host/OS, runtime/compiler, storage, access-control configuration,
trusted manager and any selected sink contract remain explicit assumptions. The
baseline does not resist a malicious host, compromised manager, arbitrary hardware
fault, covert channel, or all information-flow leakage. Work Unit's physical trust
boundary is not a proof of those properties.

### Effect correspondence rules

1. A candidate executor may compute and edit private scratch material through its
   granted resources. That does not modify accepted contents. Acceptance pins the
   **actual bytes/meaning consumed**, not merely a name, mutable path or supplied
   digest. It establishes their protection and retention before authoritative
   publication. Immutable references require trusted immutable retained referents.
2. An operation descriptor must have a supported semantic meaning at every
   relevant boundary. Unsupported restrictions, ambiguous resource resolution,
   or inability to enforce a requested narrowing mean refusal. A generic shell
   or network attachment cannot advertise finer confinement than it enforces.
3. The affected validation view and committed whole effect must have a common
   order including relevant ancestor changes, accepted-content changes and
   resource use. A serialized holder may enforce a stronger total order. A
   requester-supplied dependency list cannot omit a relevant boundary.
4. Concrete preparation is permissible before commitment only while it has no
   protected effect attributed to the proposed change, remains properly bounded,
   and cannot be mistaken for accepted state. If preparation itself exposes
   protected data or consumes a governed external resource, that action needs its
   own authorization. Calling an effect preparation does not exempt it.
5. If one promised whole effect cannot be implemented atomically across actual
   sinks, refuse that promise. Use separate commitments only when their bounded
   intermediate states are expressly part of the operation contract. Do not
   redefine a torn transfer after observing the failure.
6. Reports distinguish committed, denied-with-no-effect, and unresolved knowledge.
   A failure after irreversible commitment is not a denial. A final success reply
   cannot precede the profile's recoverable commitment point.
7. **Access-control policy is an authoritative resource.** A concrete policy
   change alters what already-running authorized work may do. It is ordered with
   the Kernel's authority change on the same footing as a sink acceptance point,
   it fails closed on partial or rejected application, and the realization
   discloses which policy changes are inside the trust boundary. A host
   administrator able to broaden policy can otherwise restore access the Kernel
   records as revoked. See [AC](./Phase-I-Revocation-and-Q1.md) Part A.

**H5 — verified object, substituted object.** Validate candidate x through path p;
the executor replaces p with y; acceptance records "x validated" but retains y.
A digest label, a Processor cache, and a new generation all leave the mismatch.
The minimum repair is binding validation, retained content and accepted meaning
to the same stable input. A trusted copy followed by validation of that copy, or
a pinned immutable holder, suffices. No general content-addressing subsystem is
forced. Mutable accepted content would need separately guarded mutations.

**H6 — support lost during use.** Check a read permission, then revoke the ancestor,
then issue a new read through an open session. Checking only when the session was
created fails a per-read promise. Either order each protected read with revocation
or declare a genuinely bounded, previously committed read/export obligation.
Already delivered bytes cannot be made unknown to a recipient by revocation.
Neither "no later acceptance" nor "no later visibility" follows from deleting a
local attachment record.

### Engine death and the meaning of sealed

The canonical Work Unit definition now resolves the earlier wording ambiguity.
A sealed Work Unit remains bounded and cannot exercise protected outward capability
attachments, but internal computation may continue using still-valid granted
resources unless a separate policy pauses, terminates, or revokes those resources.

For the baseline Phase I profile, engine loss therefore requires two things:

1. **admission/effect closure** — no new protected admission or protected capability
   use may be accepted through the lost or stale engine mediator; and
2. **route closure** — previously exposed capability paths must become unusable at
   the actual effect boundary, including retained handles or credentials within the
   declared realization scope.

It does **not** require general process quiescence. A bounded quiescence window after
engine loss is a stronger optional profile and may require an engine-independent
enforcement point, trusted liveness detection, and timing machinery. That question
remains useful for realization research but is no longer part of baseline Work Unit
conformance.

The important separation is now:

```text
engine loss
    ├─ capability attachments: inactive / fail closed
    ├─ protected effects: unavailable
    └─ still-valid resources: may continue to support internal computation
```

Pure internal computation, new boundary use, and previously committed external
consequences must still be tested separately.

**WHY:** the Work Unit canonical source now distinguishes resource grants from
capability attachments at failure time. **WHAT:** H1/H2/H5/H6 plus Work Unit
B/C/E/H/K. **HOW CERTAIN:** canonical semantic clarification; platform sufficiency
remains unverified. **WHAT-NOT-TESTED:** host isolation, descriptor revocation,
credential invalidation, actual path mediation, or any optional quiescence bound.

## 3. Durable information and recovery without a second state owner

Retain information exactly when deleting it makes two histories with different
required future observations indistinguishable. An alternative sufficient
representation is allowed; a fixed schema, full log, and every past value are not
required. The recovery implementation must not use a test oracle's hidden history.

| Information that must remain available | Why it survives deletion attempts | What may disappear/recompute |
| --- | --- | --- |
| Work Unit identity/genesis, created-by, project and other W.D observations | W.D expressly requires them even when they are not admission dependencies. Source provenance is not current authority. | Formatting, indexes and UI views. |
| Current governing relationships, restrictions, containment and any conserved quantities | Determine legal future transitions and protection of survivors. | Effective permissions and totals, recomputed from complete current inputs. |
| Accepted contents and required continuity/evidence | A reference to absent bytes cannot support continuation. Consumer-required decision/evidence records are accepted contents, not disposable caches. | Unaccepted scratch work and executor conversation unless separately accepted/required; any surviving durable candidate still needs confinement and valid disposition. |
| Sufficient meaning of the policy and representation | The same bytes interpreted under changed rules can authorize a different action. | A policy version label if a fixed, trusted compatible interpreter already supplies the distinction. |
| Enough authority distinctions to reject still-possible stale use | Reuse of a representation must not revive invalidated authority. | Bearers and endpoint instances in cold recovery; old distinction records only after no admissible old observation can collide. |
| Any committed obligation whose outstanding status changes required continuation | An accepted external consequence cannot silently cease to be owed, or be retried as though never accepted under a stronger retry contract. | Pending proposals; acknowledgements/delivery history when the chosen contract does not depend on them. |
| A trustworthy whole current cut, or information reconstructing an equivalent cut | Genuine but incompatible fragments fail whole effect and continuity. | Complete event replay when the remaining representation already meets all observations. |

This is not an obligatory collection of extra records. For example, retention
can be inline, or supplied by a trusted holder whose lifetime and integrity cover
the selected failures. A snapshot can incorporate current values and accepted
provenance without preserving an engine event log. Conversely, the higher-level
[requirements for evidence and traceability](../../requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md)
forbid discarding the evidence those consumers need merely because the core's
permission predicate no longer reads it. Phase I supports those records as
protected accepted content; it does not design their ontology.

### Recovery procedure and its evidence

Establish current management and exclude unauthorized authority holders before
activation. Discover/interpret boundary records without executing interiors;
validate the current whole cut and required content under the declared profile;
reconstruct containment and grants while inactive; then activate only explicitly
authorized fresh routes. Any changes to eligibility during recovery are themselves
guarded, ordered changes. A historical read is not a perpetual activation permit.

Cold recovery deliberately discards all old channels. This can eliminate durable
session objects and continuing bearer reconstruction **only if every route capable of admitting new effects on old authority is actually
excluded**. A previously committed exact obligation may still complete under its
own declared policy; it is not a fresh exercise of the lost producer grant. Pending messages at a mediator or sink are
routes too. The baseline does not promise that a client will learn an operation's
pre-crash result. Repeated recovery must not bootstrap new authority or repeat a
protected effect simply because the previous recovery lost its reply.

Recovery of interacting components needs a compatible whole cut. Unrelated objects
can recover separately when no promised effect, ancestor restriction, conserved
quantity or accepted dependency couples them. A global freshness service and a
global snapshot are therefore unnecessary as semantic requirements. The one-holder
prototype simplifies this obligation without proving distributed recovery.

### Retention, compaction, and interpretation attacks

**H7 — policy drift.** A record with permission value r meant read-only under P0;
a restarted binary interprets r as read/write under P1. Storage is current and all
signatures pass. This is still a change of authority. Recovery must use a compatible
interpretation or remain sealed; a semantic migration needs a guarded transition
and its own conformance argument. A stored version without the corresponding
meaning does not repair it. The initial prototype can pin one supported policy
and refuse incompatible images. A migration subsystem is not required.

**H8 — deletion of the only distinguishing evidence.** A grant is revoked, or
accepted evidence is withdrawn. Compact away the revocation/current selector and
retain the earlier valid record; a delayed message now succeeds. Compaction is
safe only if retained information and interpretation exclude every required stale
continuation. Keeping a current folded result, cutting off all old ingress, or
retaining the relevant fact can supply that distinction. Blind tombstone expiry
by elapsed time cannot. No universal tombstone, log or infinite history is forced.

**H9 — destructive recovery fallback.** A required content holder is unavailable;
recovery substitutes an empty object and calls it successfully recovered. This
fails continuity even if no stale grant activates. Preserve the object as
unresolved and protected; a separately authorized reset changes the promise and
must be reported as reset, not recovered acceptance. This keeps safety and
successful recovery distinct.

### H14 — an unaccepted durable candidate is still a confined thing

An executor writes candidate z to durable storage inside W, never accepts it, and
dies. The authoritative accepted-content list is empty. Removing W's boundary on
that basis exposes z in a host namespace. This violates Work Unit I even though
accepted-work continuity is untouched. Durable-content disposition covers every
dependent durable thing, not just accepted artefacts or registered children.

A private scratch area may be explicitly ephemeral, or be logically disposed of
under the storage guarantee. Until disposition, surviving bytes remain bounded.
A trusted complete inventory or enclosing storage mechanism can discharge this;
a Processor-produced list with unproven completeness cannot. This is an additional
completeness obligation on the realization of H13/C8, not a new primitive.
**WHY:** non-authoritative does not mean unconfined. **WHAT:** Work Unit A/I/K and
the described history. **HOW CERTAIN:** evidence-based semantic counterexample.
**WHAT-NOT-TESTED:** scratch-storage teardown and concrete durable-object inventory.

**WHY:** deleting required information or its interpretation merges histories
whose permissions, contents or audit observations differ. **WHAT:** H3/H7–H9/H14 and
the existing currentness/composition arguments. **HOW CERTAIN:** evidence-based
minimum semantic information; not a minimal-byte representation proof.
**WHAT-NOT-TESTED:** compaction, policy migration, repeated crash recovery, media
fault handling, or a Work Unit content-retention implementation.

## 4. Replaceable execution and external outcomes

The durable Work Unit does not need a durable Execution object. A current
relationship plus trustworthy request ingress must distinguish old and replacement
attempts wherever policy demands different answers. A caller-provided generation,
a process ID, or shared principal name is not that trustworthy distinction.

Replacement is a guarded whole change of the relevant authority relationship(s).
It preserves required accepted content and bounded identity. A pre-replacement
proposal may commit only if its actual commitment orders before replacement. A
pre-replacement *read of permission* cannot justify a later commitment. Concurrent
requests may order either way; completed replacement precedes later initiated use.

| Mechanism candidate | What the baseline actually needs |
| --- | --- |
| Generation/counter/nonce/token | Any non-confusable current authority representation. No particular numeric identity is required. Finite exhaustion must refuse safely, not wrap into a reachable old identity. |
| Source binding | Required if old physical participants must be excluded even when they acquire current evidence. The prototype should use trusted, non-transferable ingress associations and test impersonation. If relying on bearer secrecy instead, state the weaker physical-exclusion claim. |
| Durable issued-token set | Only if otherwise an old usable representation can collide after a covered failure. Cold recovery plus proven elimination of old routes can remove this representation, not the non-resurrection obligation. |
| Lease/heartbeat | Not required for baseline safety or replacement. Detection may trigger a replacement proposal; a timeout that only proposes grants nothing. A lease/heartbeat-class mechanism becomes relevant only for an explicitly stronger claim such as bounded quiescence after engine loss or timed authority expiry. Those claims require their own trusted liveness/time and enforcement assumptions. See [Part B](./Phase-I-Revocation-and-Q1.md) for the historical reduction that exposed this distinction. |
| Sink fencing | A semantic requirement only for a profile that needs current authority at that sink; an integer is one possible realization. Every affected sink must enforce the same relevant authority order. |
| Request identity/deduplication | Required only when a promised result/retry/at-most-once observation depends on distinguishing repeats. Not inferred from disposable execution. |
| Durable retry queue | Not needed for baseline safety. A retained accepted obligation plus explicit invocation can be sufficient; no automatic delivery or scheduling guarantee is claimed. |

Three external-effect contracts must stay distinct:

- **At a mediated use:** check current authority at the concrete protected
  acceptance event. Revocation must order with that event. A sink accepting new
  uses on an old unchecked handle is incompatible.
- **A committed exact obligation:** check authority when the exact bounded effect
  is committed. Its later completion is governed by the obligation's own declared
  policy. In the existing Kernel experiment it is not cancelled by producer
  revocation and duplicates are allowed. That is useful bounded evidence, not a
  safe default for arbitrary effects or an unlimited capability.
- **A stronger cancellation/retry promise:** no post-revocation sink acceptance,
  at-most-once acceptance, or exactly-once eventual delivery requires the relevant
  sink order/outcome contract. The core must refuse an unsupported promise.
  Compensation is a subsequent effect and does not make a forbidden history valid.

**H10 — two indistinguishable lost replies.** In history a, the sink accepts effect
q and the reply disappears. In history b, q never reaches the sink. The source's
remaining observations are identical. Retrying can duplicate a; never retrying
can fail required delivery in b. A local Processor, durable source request ID,
clock or higher confidence cannot distinguish them. A trusted outcome query,
sink deduplication/idempotence contract, or weaker explicitly selected guarantee
is necessary. Source-side persistence alone cannot promise both eventual delivery
and at-most-once effect. No such stronger promise is smuggled into the baseline.

For local state, lost replies have the same knowledge distinction. Read back
current accepted state and formulate a fresh, currently guarded proposal. Do not
infer from no reply that the earlier transition was denied. Comparing present
values is adequate only if the requested observation does not require identifying
which historical request produced them.

**WHY:** authority and outcome are properties of the relevant accepted event, not
of an executor's apparent liveness or memory. **WHAT:** H2/H4/H6/H8/H10 and Kernel's
current-authority/order/external-action clauses. **HOW CERTAIN:** evidence-based
contract reduction; H10 is a conditional indistinguishability argument.
**WHAT-NOT-TESTED:** distributed fencing, at-most-once sinks, timed revocation,
physical-source exclusion, or a concrete replacement implementation.

## 5. Authoritative information is a use contract

An information category is not an authority rank. An accepted statement that a
model reported confidence 0.99 can be authoritative **as a record of that report**
without making its proposition true. Conversely, a transient calculation may
legitimately supply a guard premise if its truth and applicability are established
within the current commitment. Do not implement promotion-to-authority by a label,
a confidence threshold, a signature alone, or persistence alone.

| Information | Permitted participation in a guard | Required limitation |
| --- | --- | --- |
| Current authoritative state | Direct input under the declared policy and coherent view. | Recovered/cached copies need the same currentness and interpretation basis. |
| Trusted observation | Input for exactly the proposition its source and acquisition contract establish. | Authenticate source/scope, bind subject and observation event, establish timing/order and the limitations of the observation. |
| Deterministic derived fact | Input after trusted evaluation or sound verification for the actual inputs and semantics used at commitment. | Deterministic does not mean correctly computed, complete, current, or relevant. |
| Candidate proposal | Requests a transition or offers evidence. | Never supplies its own permission or proves its own preconditions by assertion. |
| Evidence and provenance | Supports the claim its content, provenance and accepted applicability justify. | Historical validation is not current permission; provenance does not prove truth or completeness. |
| Bounded probabilistic judgment | May meet an explicitly declared policy condition such as an authorized review/decision record. | The enforced claim is that the qualified judgment/approval occurred and applies, not certainty of the underlying semantic proposition. |
| Open semantic reasoning | May produce proposals, challenges, explanations and requests for authorized decisions. | No implicit power to amend policy or bypass unknown premises. |
| Unknown/unresolved | Prevents a positive claim that needs the missing proposition. May allow an action safe under every relevant alternative. | Absence of evidence, elapsed time, silence, and numerical confidence do not resolve it. |

### Minimum admission rule for a fact

For every fact on which the guard relies, identify (in the semantics, not
necessarily in a record with these field names): the proposition; subject and
scope; source/derivation and trust; input/policy interpretation; applicable
observation or commitment point; and the changes that could invalidate it.
Then discharge **both** correctness of the fact and applicability to this use.
A trusted source can be wrong outside its scope; a correct old result can be
inapplicable now. The relevant observation can be carried by a request, retained
accepted evidence, or a trusted synchronous computation. No general fact store
is forced.

For stable facts about retained immutable inputs, validity can survive unrelated
state changes. For mutable predicates, checking a result and later committing
must not permit an intervening invalidating event. A coarse complete-state
comparison is a sufficient first comparator. Dependency tracking may later avoid
unnecessary retries, but correctness never relies on a requester's incomplete
list of dependencies. Semantic input binding includes policy/algorithm meaning,
configuration and any external facts used, not merely the bytes of one file.

**H11 — stale derivation with genuine provenance.** Compute allowed(C, write) from
a valid child grant and permissive ancestor. Revoke the ancestor. Submit the exact
old inputs, result and valid provenance. They establish a historical calculation,
not current permission. Recompute the relevant guard or validate a sound witness
against a coherent current view. A persistent invalidation registry is unnecessary
when current admission performs this check; an asynchronous invalidation message
is insufficient when admission does not.

**H12 — an authentic observation of the wrong proposition.** A test service
reports that immutable candidate x passed suite t at time u. That can establish
the trusted test outcome for x/t under its contract. It does not establish that x
is now selected, that suite t proves a requested safety property, that no later
withdrawal exists, or that the service's external world is unchanged. Those are
separate premises. An external property required *at sink use* needs use-point
ordering/control or an explicitly weaker observation-based policy. Constant
monitoring cannot repair an uncontrolled check/use gap by itself.

**H13 — false negative by omission.** A worker supplies a dependency graph missing
one child and derives "no dependents remain." Every included edge is correct.
Destroying the boundary releases the omitted child. No proof over the supplied
subset establishes completeness. The prototype evaluates absence over its own
complete finite current containment domain; an external proof must be bound to
an equally complete trusted domain. This requires a sound negative-fact check,
not a persistent graph-building subsystem.

### Unknown is a constraint on assertions and actions

Let H(o) be the histories compatible with the trusted observations and selected
failure contract. A fact may be asserted only if justified across the remaining
relevant alternatives. An action/continuation must be permitted across all of
them; choosing a new authority event must itself have supported preconditions.
This is the currentness record's intersection-of-acceptable-strategies rule.
Implementations need not enumerate H(o): a sound conservative predicate can
establish the required permission. Failure to establish it yields pending,
refusal, restricted operation or an authorized reconciliation proposal.

For example, an uncertain delivery of an irreversible effect blocks blind retry
under an at-most-once contract, but can leave a separate immutable read usable.
An uncertain ancestor restriction blocks the descendants and effects that depend
on it, not automatically every Work Unit. Where object-wide current authority
cannot be established, Work Unit recovery remains sealed. Later evidence must
be validated; escalation to a human does not itself create missing truth.

Do not invent a required Unknown object or persist every uncertain request. A
knowledge distinction needs durable representation only if losing it would allow
a forbidden future claim or action, or would lose a promised continuation. A
client-side timeout alone may leave the authority holder's state perfectly definite.

**WHY:** H11–H13 allow false admission despite authentic provenance or deterministic
computation. **WHAT:** Kernel's f/G/current-view semantics and the scoped
currentness rule, applied to derived and semantic information. **HOW CERTAIN:**
evidence-based admission contract. **WHAT-NOT-TESTED:** a proof verifier, observation
service, semantic-review policy, external-world freshness, or an implementation
of unknown-state handling.

## 6. Processorless result

The [targeted falsification record](./Phase-I-Processorless-Falsification.md)
contains the reduction and strongest counterhistories. The surviving claim is:

> For the declared finite Work Unit policy and failure/effect profile, persistent
> derivation state and a separately authoritative Processor lifecycle are not
> necessary. Trusted guard evaluation/verification, retained authoritative inputs
> and accepted contents, and concrete enforcement remain necessary.

This is not a claim that all deterministic computation can be untrusted or kept
outside the TCB. Nor is it a universal theorem for arbitrary consumer programs,
real-time workloads, or all future EDASES semantics. Those stronger claims are
unsupported. No attempted history in the record requires a new Kernel primitive.

## 7. Frozen semantic target for downstream work

This section fixes the **candidate's implementation/verification target**. It does
not promote this derived record to canonical policy. Builders may select a
representation but must not silently alter these observations, effects or limits.
The [verification plan](./Phase-I-Verification.md) assigns the remaining bounded
work and acceptance conditions.

### Required operations and policy

All operations use current, explicitly authorized management or execution ingress,
relevant containment boundaries and resource constraints. Being creator, parent,
project member, a process, or a holder of candidate bytes grants no implicit right.
Initial management is a declared trusted initialization premise; ordinary recovery
is not bootstrap. The supported policy/encoding is fixed for the first prototype.

| Operation | Whole semantic result and additional guard |
| --- | --- |
| Establish an empty Work Unit | A bounded, inactive object with the W.D boundary observations; no inherited grants or authority. Its identity cannot be confused with a still-reachable prior object. |
| Grant/expose a relationship | Only currently governing authority may establish the explicitly scoped relationship. Supporting allocations do not become callable interfaces merely by existing. Attachments are the exposed subset. Every actual use remains subject to its declared effect contract. |
| Narrow/revoke/seal | An authorized whole restriction with concrete route exclusion at the specified event. Preserve accepted contents and all dependent confinement. Ancestor restrictions constrain descendants; a child's own restriction need not disable its ancestors. Sealed/revoked/destroyed remain distinct. |
| Accept content or evidence | Accept the exact validated/proposed meaning under the applicable acceptance policy, with required bytes and provenance retained and bounded. Content acceptance alone is not publication or proof of semantic truth. |
| Replace execution ingress | Invalidate the old relationship and establish the authorized new one at one declared whole commitment when replacement promises both. Preserve work identity and accepted content. No stale request can commit after this using old evidence. |
| Recover | Establish an equivalent current whole view and present authority; reject stale bearers; recover bounded and sealed before activation. Include all coupled commitments and required contents. Unsupported/ambiguous recovery does not become a new empty Work Unit. |
| Move a sealed child | Validate both containment contexts and governing permissions; avoid cycles/dangling relations; retain bounded contents and descendant protection; preserve or narrow the child's latent permissible authority under the changed path. Move cannot grant new rights. Drop unsupported grants in the whole move or deny it. |
| Activate | A separate current authorized event creates only supported, currently allowed routes. Recompute full-path constraints after a move/recovery. Historical grants, old observations or a permissive destination are insufficient. |
| Dispose accepted contents | An explicit authorized disposition under the declared logical-storage guarantee. Revoke actionable access as required; preserve other survivors. No secure physical erasure is implied. |
| Remove a Work Unit | Current complete dependency check establishes all durable dependents safely dispositioned and no surviving object loses protection. Concurrent creation/acceptance must order with removal. Recursive disposal may have separately accepted bounded prefixes; final removal cannot tear a promised whole move. |
| Use a protected external attachment | Apply the selected authorization event, exact-effect correspondence, trust and outcome policy in §4. Unsupported cancellation, atomicity or retry guarantees must be refused before the effect. |

For moves, comparing **currently enabled** actions of two sealed states is
insufficient: both sets are empty. Compare the retained restrictions and permitted
activation/use they would allow, including descendants, applicable resources and
management dependencies. A child whose write was blocked only by its old parent
must not gain write when later activated under a permissive parent. If a supported
policy cannot represent the old restriction at the new location, narrow the grant
or refuse the move; a second persistent authority system is unnecessary.

### Exact invariant and trace target

The formal target includes Kernel verification invariants 1–6 unchanged and the
following Work Unit/profile instantiation. These are predicates/trace properties,
not mandatory records or individually deployed components.

| ID | Required invariant or history property |
| --- | --- |
| C1 | Every protected concrete effect is explained by a currently admissible whole commitment with the exact promised meaning; denial has no protected effect attributable to that proposal. |
| C2 | One coherent view and one common acyclic order explain all interacting commitments, including completed-before-initiated precedence and negative/range dependencies. Invariant validity alone does not establish whole-effect fidelity. |
| C3 | Boundary crossings require explicit current local authorization plus every relevant enclosing restriction and resource constraint. Management does not follow from containment; resource allocation alone is not exposure. |
| C4 | All existing Work Units, including empty/inactive ones, have interpretable trusted boundary observations; containment is well-founded and non-dangling; authoritative metadata agrees with the committed relationships. |
| C5 | Required contents and every survivor remain bounded across executor loss, engine loss, partial disposition and covered recovery. Sealing/revocation does not delete, export or unbound them. The execution-disable timing is subject to Q1 below, not silently omitted. |
| C6 | Replacement/invalidation excludes old authority at the specified event; representation reuse, restart and reparenting cannot resurrect it. Physical-producer exclusion additionally meets the declared source-binding premise. |
| C7 | A covered recovery retains all required accepted/irrevocable commitments and contents through an observationally equivalent current compatible cut; no torn coupling, fictitious bootstrap or historical image asserted as current. |
| C8 | Reparenting does not silently widen latent authority, including descendants and later activation. Final destruction has a current complete disposition precondition and never weakens surviving protection. |
| C9 | Every guard premise has adequate truth/authority and current applicability for its stated proposition. Unknown cannot satisfy a required positive premise. A model judgment remains qualified by what policy actually authorizes it to establish. |
| C10 | Every external effect obeys its declared decision/use/acceptance/visibility and failure contract. Replacement does not silently cancel a committed obligation or retrospectively authorize an invalid effect. |
| C11 | Required identity, provenance, project and retained consumer evidence remain observable across covered loss, even where not needed for current admission. Derived views may be rebuilt; required observations may not disappear. |
| C12 | Successful acknowledgements/publications follow recoverable commitment. Lost replies preserve uncertainty about an otherwise definite local outcome; they do not undo effects or authorize retries. |
| C13 | Any concrete access-control policy that governs what already-running work may do is ordered with the Kernel's authority change, fails closed on partial application, and is disclosed as inside or outside the trusted boundary. A revocation the Kernel records is not treated as an exclusion unless the enforcing policy is itself in the boundary (AC). |

A no-effect denial can itself have separately declared diagnostic/audit consequences
under policy, but must not partially execute the denied protected proposal. A
resource whose consumption is governed cannot be consumed secretly in a "failed"
preparation step. The model must make such auxiliary effects explicit if included.

### Non-vacuity and bounded progress

Under a healthy declared substrate, valid finite inputs, available supported
resources, no competing invalidation and execution of the invoked handler, the
prototype must complete its supported successful operations. No request can be
left forever unknown merely to avoid implementing a required guard. This is a
bounded test acceptance condition; no autonomous scheduler, availability under
partition, hard deadline, or fairness of an external service is inferred.

At least one successful witness must cross each of these boundaries: acceptance
**before** loss followed by actual use **after** recovery; replacement followed by
continued accepted work; sealed restricted relocation followed by valid use and
continued denial of the old forbidden action; partial disposition/recovery followed
by completion; and a chosen external effect consistent with its explicit contract.
These witnesses accompany hostile tests. Passing deny-all tests is insufficient.

## 8. Remaining architectural uncertainty and review propositions

The repeated reduction has reached a useful stopping boundary: the known required
histories specify a finite policy/realization contract. More general model building,
implementation, fault injection and product comparisons should not consume further
frontier reasoning without a failed obligation. The surviving uncertainty is small
and concrete; broader unselected guarantees are not mislabeled unfinished Phase I.

### Q1 — resolved: engine loss does not require baseline quiescence

The earlier Q1 existed because Work Unit E/H could be read as requiring both
capability closure and cessation of interior execution. The canonical Work Unit
glossary has now been clarified: **sealed** means that protected outward capability
use is disabled while the durable bounded object remains. Internal computation may
continue using still-valid resource grants unless a separate policy requires
quiescence.

The previous D1/D2/D3 decomposition remains useful as analysis:

- **D1 — admission disabled:** required by the baseline.
- **D2 — protected effect/capability use disabled:** required by the baseline.
- **D3 — interior execution stopped:** not a baseline requirement.

D3 is now an explicitly stronger profile. If a product or deployment wants
bounded or immediate quiescence after engine loss, it must name and test the
engine-independent enforcement and liveness/timing mechanism that supplies that
guarantee. No new Kernel primitive follows automatically.

The historical derivation and the source-level revocation correction are retained
in [Phase I Revocation Verification and Q1 Reduction](./Phase-I-Revocation-and-Q1.md).
Its former "canonical wording decision" residual is closed by the Work Unit
clarification made during the documentation consolidation pass.

### Unselected stronger profiles, not hidden architecture tasks

Rollback-resistant successful recovery, machine/power-loss durability, physical
secure erasure, distributed available takeover, continuing bearer recovery,
at-most-once arbitrary sinks, irreversible multi-sink atomicity and real-time
computation deadlines have no unconditional Phase I promise here. They have
specific discrimination tests in the verification plan if selected. Refusing to
claim them is not evidence that a later subsystem solves them. A requirement
making one mandatory must first identify its permitted histories and success
condition; then reopen only the affected trust/failure/effect contract.

### Propositions for independent cross-family review

No independent review was launched in this task. Reviewers should form their own
judgment from the pinned source contracts and histories, not from model consensus.
The highest-value challenges are:

1. **Processor elimination is not relabeling.** Attack P1/P6/P8/P9: find required
   independent deterministic state/machinery that cannot be reduced to the finite
   guard and retained authoritative information without changing an observation.
2. **The failure target is non-vacuous and adequate.** Challenge whether engine-loss
   confinement and Work Unit E/H can actually be met by the declared surviving TCB,
   especially Q1, retained handles and delayed pre-crash requests.
3. **Fact admission includes completeness.** Challenge H11–H13/P3/P4 with omitted
   dependencies, negative facts, changed policy, mutable external facts and races
   between proof checking and use. A correct proof about the wrong domain fails.
4. **No authority hides in a mediator.** Challenge H2/H4/H6/H10: find a concrete
   route or effect event that escapes the declared commitment/authority order,
   including recovery of the mediator and reuse of ingress identities.
5. **Persistence is sufficient without indiscriminate history.** Challenge H3/H7–H9
   and C7/C11 using required provenance, unacknowledged commitments, rollback or
   coupled restoration. Distinguish unsupported failures from violations within
   the selected profile.
6. **AC is correctly scoped and sufficient.** Added after independent source
   verification. Challenge rule 7 and C13: is treating the concrete access-control
   policy as an authoritative resource complete, or does it smuggle in a
   requirement the specifications do not make? Specifically, try to find a route by
   which a correctly recorded Kernel revocation is defeated by policy that the
   Kernel does not control, and try to find a legitimate revocation that AC's
   ordering and fail-closed clauses would wrongly forbid.
7. **Capability closure is correctly separated from optional quiescence.** Try to
   find a required protected effect that can still occur after the capability
   attachment is inactive, including retained handles, credentials, asynchronous
   completion, or mediator recovery. Separately test that permitting CPU-only
   interior computation after engine loss does not itself create a protected
   effect. Bounded quiescence is reviewed only when that stronger profile is
   explicitly claimed.

## 9. Concise synthesis and handoff

**Surviving core:** Kernel's existing guarded current whole transitions and
continuity, instantiated with Work Unit's bounded-object/containment/disposition
policy; retained accepted information; trusted complete mediation and authority
ingress; compatible current recovery; and trusted evaluation/verification of
actual guard premises. None requires a new named Kernel primitive, persistent
Execution object, independent Processor, Observer, tracker or scheduler, nor does
Kernel correctness require an Orchestrator agent. The intended product model may
still use an Orchestrator as the normal user-facing agent. A logical single-holder
prototype is sufficient to test this candidate.

**Trust/failure assumptions:** known initial/current management; correct supported
policy and interpretation; a host/protection boundary that survives or fails
closed through the claimed process loss; current complete retained storage and
contents; non-confusable request ingress; and explicitly scoped observations/sink
contracts. No host-compromise, silent rollback/corruption, power-loss, partitioned
availability, or arbitrary exactly-once guarantee is inferred.

**Semantic changes:** none to Kernel-0. Work Unit A–L is retained. Required profile
clarifications concern exact effect events, recovered-current meaning, policy/input
binding and lost-outcome behavior; they instantiate existing parameters. Q1 needs
an explicit Work Unit temporal clarification before a full sealed-execution claim.
Canonical documents are not silently rewritten by this derived investigation.

**Processorless outcome:** survives fifteen targeted attempts for the finite
profile. The stronger claim that no trusted deterministic guard computation is
needed is false. Complete inputs, interpretation, accepted historical information
and exact content retention are necessary; persistent derivation management is
not justified by the histories tested.

**Remaining work:** formalize the finite target and its observation/refinement
relation; execute positive/hostile traces and removal mutations; implement and
fault-test one real mediated boundary and cold recovery; verify content/metadata
coupling and stale-ingress exclusion; obtain AC/C13 conformance evidence for the
chosen access-control policy, including whether a given administrative revocation
actually invalidates already-open access; make the canonical decision on Q1's
strong reading and measure the quiescence window; and seek the independent review
above. [Acceptance conditions](./Phase-I-Verification.md) bound each task. Two
narrow primary-source checks were needed: to assess the concurrent host-limit claim
(§10) and to verify the counterexample that rejects it
([Part A](./Phase-I-Revocation-and-Q1.md)). No broad literature survey,
live-model experiment, runtime implementation or new formal proof was performed in
this investigation.

**Completion status:** architectural investigation complete enough for bounded
downstream work. Q1 was subsequently reduced from an open core contract to a named
disclosure, a named enforcement point, one canonical wording decision and one
measurement, with no new primitive. Roadmap Phase I's implementation/formal/
hostile-test exit evidence is **not yet complete**. Further frontier work is gated
on a concrete failed invariant/required history, on the canonical decision that
Q1's strong reading is intended, or on a new selected failure/effect profile — not
on another broad survey or restatement of the current design.

**WHY:** all surviving additions have a removal witness; known attacks reduce to
existing semantic parameters or an explicitly unsupported stronger claim.
**WHAT:** pinned baseline, H1–H14, P1–P15, C1–C12 and the downstream acceptance plan.
**HOW CERTAIN:** evidence-based scoped architectural closure, not universal
minimality, full realization conformance or independent consensus.
**WHAT-NOT-TESTED:** all new model/realization obligations in that plan, Q1's timing,
and independent review; inherited Kernel evidence keeps its original bounds.

## 10. Disposition of the concurrent realization proposal

While this investigation was writing its final target, commits `76a38fb7` and
`8bebb403` replaced earlier sections with another argument and preserved that
argument in a [separate file](./Phase-I-Closure-Realization-Boundary.md). The
contribution is kept as an unadopted proposal. It is not an independent review
commissioned by this task, and its presence in Git is not architectural approval.
The live record restores the information/persistence/effect sections that the
replacement removed and evaluates the substantive challenge here.

**Useful finding retained:** distinguishing valid admission from actual exclusion
of a previously usable route is necessary. An orphaned child process holding an
old descriptor is a concrete variant of H1/T05. Add child creation, descriptor
inheritance/passing and pending messages to the route inventory and hostile tests.
A connection object or peer credential is a realization candidate, not an automatic
proof of exclusion of every old physical producer.

**Rejected inference L1:** limitations of capabilities/Landlock/seccomp do not
establish that all mainstream-host revocation requires terminating the holder,
or that exactly two realization families exist. A narrow countermechanism is in
Linux v6.12's `selinux_file_permission`: its fast path depends on unchanged
subject, object and policy sequence, and otherwise revalidates permission for an
already-open file. This defeats the claim that host access enforcement is
universally fixed at open/creation time. It does not prove complete revocation
for mappings, all sinks or this host. [Pinned Linux source](https://github.com/torvalds/linux/blob/v6.12/security/selinux/hooks.c#L3418-L3436).

**Independent verification (added later).** The pinned source was read directly and
the rejection is **confirmed**: `selinux_file_permission` returns early only when
the subject context, the inode context and `avc_policy_seqno()` all match what was
recorded at `file_open`, and otherwise calls `selinux_revalidate_file_permission`,
which re-evaluates the inode permission at the moment of use. An already-open
descriptor is therefore re-checked whenever the policy sequence number changes.
L1 was wrong in its universal form. Two limits on the correction are recorded
rather than assumed: it does not establish that a given administrative revocation
actually increments the policy sequence number, and the hook does not govern
already-mapped memory, device `ioctl` or asynchronous completion. Because the
counterexample relocates rather than removes the obligation, it yields the
stricter requirement recorded as rule 7 in §2 and invariant C13: concrete
access-control policy is an authoritative resource whose change must be ordered
with the Kernel's authority change, fail closed, and be disclosed as inside or
outside the trust boundary. Detail in [Phase I Revocation Verification and Q1
Reduction](./Phase-I-Revocation-and-Q1.md) Part A.

Landlock's documented self-restriction and descriptor limits support the narrower
warning that applying a new rule cannot be assumed to revoke existing handles.
They are not a lower bound on every host security mechanism. The documentation
also explicitly composes Landlock with other system controls. [Linux Landlock
documentation, descriptor rights and policy layers](https://docs.kernel.org/userspace-api/landlock.html#rights-associated-with-file-descriptors).
The seccomp notification manual likewise supports its specific warning against
using the notification mechanism as the security-policy decision boundary, not
an impossibility theorem about all mediation. [Linux seccomp notification manual](https://man7.org/linux/man-pages/man2/seccomp_unotify.2.html).

Further concrete reductions reject the claimed forced semantic change:

| Proposal claim | Disposition and discriminating reason |
| --- | --- |
| A failing direct-handle realization forces narrowing Work Unit B/K.5. | H1 already rejects that realization. A trusted mediator or an actually enforceable substrate route remains allowed. Unsupported attachments must be refused; weakening the canonical promise to fit the chosen host is unjustified. Q1 remains a different unresolved timing question. |
| Route exclusion must act on the holder itself. | Refusal at a trusted sink/mediator can make new use ineffective without changing the holder. The obligation is exclusion at the declared effect event across all routes, not one mandatory physical location of enforcement. |
| Every route dies when the engine owns it. | A previously sent request, buffered message or sink-accepted consequence can survive engine death. H4/H10 require the chosen effect contract even in an all-mediated design. Ownership does not erase in-flight effects. |
| Currentness must hold for every later consequence of a route. | A committed exact obligation can remain valid after producer revocation. The proposal's universal CP would exclude the supplied Kernel effect profile unless separately qualified by the authorization event. Retain §4's distinction. |
| Admission must prevent the old producer ever acquiring genuinely new authority. | Kernel expressly distinguishes invalid old grants from a genuinely new authorized grant. Physical exclusion is an additional claim; forbidding all future grants changes policy rather than implementing ordinary replacement. |
| Connection-time credentials prove every future message's physical source. | `SO_PEERCRED` describes connection-time credentials, and descriptors can be passed. A connection must have a proven non-transfer condition or appropriate per-use trusted source binding if physical-source exclusion is claimed. A peer label alone does not establish it. [Linux Unix-socket manual](https://man7.org/linux/man-pages/man7/unix.7.html). |
| Fencing is only non-reissuance of an identity. | A unique label ignored by a stale sink cannot fence anything. The affected acceptance boundary must enforce the authority order; §4 already makes that profile-specific obligation explicit. |

The original process-loss table was a **required result under an explicit
surviving/fail-closed protection assumption**, not a report that an arbitrary
engine already supplies it. Its wording is sharpened above to separate new
admission, execution disable/Q1 and previously committed consequences. No tested
host capability establishes full confinement here. R-A/R-B remain possible
implementation sketches with gaps; neither is selected or treated as exhaustive.

**WHY:** specific host limitations do not justify universal impossibility or
weakening accepted semantics; the counterhistories already discriminate the
necessary use-point guarantee. **WHAT:** concurrent proposal, supplied Kernel/
Work Unit contracts, and the narrowly retrieved primary sources on 2026-09-28.
**HOW CERTAIN:** evidence-based rejection of the universal inference; source-level
countermechanism, not an executed host conformance result. **WHAT-NOT-TESTED:**
SELinux availability/configuration on this machine, live policy revocation,
mappings/async I/O coverage, physical-source binding or either proposed family.
