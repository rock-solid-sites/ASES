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

**Checkpoint 1:** baseline and coupled failure boundary established. Continue
with information admission, targeted processorless falsification, a removal audit,
and exact downstream acceptance conditions. No runtime implementation is required
by this investigation.

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
| Engine/authority process stops while host protection and storage survive | Disable active routes; retain bounded objects and committed contents; recover cold and sealed before explicit activation. | A surviving/fail-closed protection mechanism is part of the TCB. Its realization must be tested, not inferred from a metadata flag. |
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
trusted exclusion of A from every protected ingress. A surviving host can supply
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

The baseline cannot implement sealed merely as "do not accept future results."
Work Unit H also disables active execution/outward use. A concrete engine-loss
claim must identify the trusted event that disables execution and the routes
whose use ends there. At a minimum, no new protected admission can occur through
a dead or superseded authority holder. Any process termination/fate-sharing
mechanism needed for the stronger execution-disable claim belongs in the TCB.

There is a real specification edge: process death, detection of death, termination
of another process, and disappearance of a host are different events. Work Unit
E/H does not specify their allowed interval. This investigation does **not**
quietly reinterpret it as indefinite computation inside an isolated object. The
prototype must either demonstrate a trusted joint disable boundary or explicitly
report this gap; the precise temporal claim is unresolved in §8. A heartbeat or
lease cannot prove instantaneous death detection. Pure in-flight computation,
new boundary use, and previously committed external consequences must be tested
separately.

**WHY:** a record-only model can satisfy every local invariant while a concrete
route violates the claimed effect or confinement. **WHAT:** H1/H2/H5/H6 and Work
Unit C/E/H/K. **HOW CERTAIN:** evidence-based realization constraints; platform
sufficiency is unverified. **WHAT-NOT-TESTED:** host isolation, descriptor revocation,
process fate sharing, actual path resolution, or a whole-effect implementation.

## 3. Durable information and recovery without a second state owner

Retain information exactly when deleting it makes two histories with different
required future observations indistinguishable. An alternative sufficient
representation is allowed; a fixed schema, full log, and every past value are not
required. The recovery implementation must not use a test oracle's hidden history.

| Information that must remain available | Why it survives deletion attempts | What may disappear/recompute |
| --- | --- | --- |
| Work Unit identity/genesis, created-by, project and other W.D observations | W.D expressly requires them even when they are not admission dependencies. Source provenance is not current authority. | Formatting, indexes and UI views. |
| Current governing relationships, restrictions, containment and any conserved quantities | Determine legal future transitions and protection of survivors. | Effective permissions and totals, recomputed from complete current inputs. |
| Accepted contents and required continuity/evidence | A reference to absent bytes cannot support continuation. Consumer-required decision/evidence records are accepted contents, not disposable caches. | Unaccepted scratch work and executor conversation unless separately accepted/required. |
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
session objects and continuing bearer reconstruction **only if every route carrying
old authority is actually excluded**. Pending messages at a mediator or sink are
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

**WHY:** deleting required information or its interpretation merges histories
whose permissions, contents or audit observations differ. **WHAT:** H3/H7–H9 and
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
| Lease/heartbeat | Not required for safety. Detection may trigger a replacement proposal; timeout alone grants nothing. Any claimed timed expiry needs trusted time and use-point enforcement. |
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
