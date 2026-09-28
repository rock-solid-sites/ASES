---
title: Phase I Core Substrate Verification Work
program: EDASES
layer: Architecture
document_type: Verification Plan
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 4e800957a673c8bd07eeea3c3c909349cdae76ac
depends_on:
  - EDASES Phase I Core Substrate Closure
  - Phase I Processorless Core Falsification
  - Kernel-0 Verification Obligations
  - EDASES Work Unit Component Design
consumed_by:
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Phase I architectural closure review
related_documents:
  - Kernel-0 Assurance Continuation
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Work remaining after architectural closure

The [closure record](./Phase-I-Closure.md) fixes the candidate, its C1–C12 target,
profile, Q1 and claim limits. The [Processor falsification](./Phase-I-Processorless-Falsification.md)
fixes the finite comparator. This plan specifies downstream work; none of the new
checks below has been executed in this investigation. Existing Kernel experiments
are reusable evidence/fixtures within their bounds, not completed Work Unit checks.

## 1. Dispatch boundary

Perform F1–F5 with deterministic tools and ordinary implementation/test work.
Escalate architectural reasoning only when a required history violates the frozen
contract, a proposed implementation cannot discharge a trust assumption without
new semantics, or Q1's concrete evidence requires a contract decision. A failed
implementation is not automatically a new primitive. Try the simplest correction
within the existing guard/effect/currentness contract first.

No agent launch, model choice or push is authorized by this plan. Follow the
repository's operational approval rules when downstream work actually starts.
This task did not run an independent cross-family review; its propositions are
listed in closure §8 rather than presented as agreement already obtained.

## 2. F1 — formalize the policy and observation relation

**Deliverables:** a finite transition model; a readable mapping of each state
variable/event to C1–C12 and Work Unit K.1–20; trusted/failure premises; positive
witnesses; and an abstraction/observation definition. Language and proof tool are
implementation choices. Do not promote model variables into ontology by naming them.

Use enough state to expose the following distinctions. A family of explicit small
fixtures is acceptable; report exactly which products were explored.

- Two possible parent Work Units P/Q, child C, a descendant D and sibling S.
  Exercise old and new paths, independent restriction, a cycle attempt, and
  capacity competition. Include an empty sealed Work Unit.
- Supported use effects read/write over at least two distinguishable content
  atoms x/y; local grants and parent ceilings vary independently. Created-by,
  project and management have separate meanings, even if encoded compactly.
- One conserved reservation supplied by P to C or S, with capacity one. Define
  allocation versus consumption explicitly for this fixture; do not accidentally
  count a child's allocation both as a parent reservation and new global usage.
- Old and replacement request ingress; current management M; an unauthorized
  parent-interior requester. At least one authority representation is reusable
  in a deliberately weakened fixture to expose resurrection.
- At least three concurrent pending proposals for the existing cyclic-validation
  attack, plus a disjoint transition for the independence control. The original
  Kernel three-way dependency fixture may be reused with its mapping stated.
- Distinct preparation, recoverable commitment, response, loss, discovery,
  currentness validation and activation events. Two successive recovery losses
  suffice for the first bounded fixture; do not imply an unbounded cutoff.
- An optional selected sink with request in flight, irreversible acceptance and
  lost response distinguished. Include both dropped and surviving in-flight
  messages. A source crash must not erase a possible message by model fiat.

The ordinary recovered model never reads ghost committed history. The checker may
retain it separately as an oracle. Recovery sees only declared survivors and
permitted exchanges. Failure injections include correct current storage and
explicitly outside-profile obsolete/corrupt material so claim boundaries remain
visible; the latter must not be counted as successful covered recovery.

**Acceptance:** all C1–C12 properties within the represented profile, all Work Unit
observations, and successful witnesses are checked. Report state/transition bounds,
search completeness within those bounds, excluded combinations, and every trusted
premise. At least one accepted x must be used after losing the activity and authority
process that first accepted it. Checking x accepted only after restart is invalid.
Q1 must be represented as an explicit parameter/event relation and left unproved
where its temporal contract remains unresolved.

A finite result is not an unbounded proof. Supply separate inductive obligations:
initial invariants; preservation under each admitted transition; preservation and
whole-effect interpretation under the covered failure/recovery relation;
non-resurrection for any still-reachable old evidence; acyclic conflict order;
and observational equivalence of recomputed versus retained derivations. State
what structural induction over a containment forest would require. Do not spend
frontier effort constructing proof scripts once these obligations are clear.

## 3. F2 — pin hostile histories and destructive controls

Each row requires a named initial state, exact event sequence, promised observation,
and expected result. Preserve failing mutations and counterexample traces. A
mutation rejected before reaching its intended fault is not a valid discriminator.

| Trace | Required acceptance condition |
| --- | --- |
| T01 — explicit grant/path conjunction | Parent admits with no child grant: deny. Child grant with ancestor denial: deny. Both grant and full path valid: successful use. |
| T02 — replacement race and replay | Old request may commit before replacement; it must fail afterward. Completed replacement precedes later initiated old use. New valid ingress successfully continues x. |
| T03 — source impersonation and reuse | Old producer claiming new position/generation fails. Reuse of a still-reachable old representation fails. Record whether the physical-source binding or bearer-secrecy claim was tested. |
| T04 — conflicting capacity and three-way guards | At most one of two unit-capacity reservations succeeds. No three separately validated commitments with cyclic required order all succeed. An independent change remains possible. |
| T05 — engine loss with retained routes | Kill authority while old activity retains file/socket/process references. No new protected use succeeds; accepted contents stay bounded. Separately measure execution disable for Q1. A sealed flag alone is not an oracle. |
| T06 — exact content | Swap candidate path/content after validation; accept only the exact checked retained bytes or reject. Lose candidate producer after acceptance; required bytes still usable from the trusted holder. |
| T07 — whole commitment and no early success | Interrupt before/after preparation, commitment and response. Only permitted whole endpoints recover. Every acknowledged/irrevocably committed value survives. No-reply is not forced to mean no-commit. |
| T08 — current versus historical recovery | Restore an old authentic image after accepted y/revocation. The baseline must label this outside its current-storage premise; a claimed rollback-resistant extension must distinguish/refuse it. Fresh credentials alone may not label old x current. |
| T09 — wrong root, missing content, changed interpretation | Reject/quarantine activation of wrong/incomplete/incompatible images. No empty bootstrap, invented y, or permission widening via reinterpretation. Protection of discovered contents persists. |
| T10 — repeated recovery | Lose recovery between discovery, validation and activation, then recover again. No duplicate authority/effect, unbounded exposure, lost accepted content, or revival of old channels. |
| T11 — sealed move with latent restriction | C has local read/write but P restricts to read. Move sealed C under Q allowing both. After activation, read succeeds and write still fails unless a separate authorized grant explicitly changes it. Include D. |
| T12 — structural race and coupled recovery | Empty check races child creation; final removal cannot strand it. Coupled move recovers old or new whole relation, never double placement or missing confinement. Invariant-valid half-effects still fail. |
| T13 — interrupted disposition | Dispose one dependent, fail, recover the remaining contents bounded/sealed, then finish. Boundary disappears only once every durable dependent is safely dispositioned. Retained old references cannot expose logically disposed material under the claimed guarantee. |
| T14 — old derived result | Compute allowed before revocation, then submit true with authentic provenance. Deny after revocation. Recompute on an unchanged healthy state and successfully admit; no mandatory cache/invalidation service. |
| T15 — negative facts and phantom | Omitted child graph cannot prove emptiness. Correct enumeration followed by new child cannot authorize stale removal. A complete current empty state permits authorized removal. |
| T16 — observation scope and semantic judgment | A result for x/t does not validate y or a stronger property. A model confidence claim cannot supply permission; an expressly authorized qualified decision is recorded with its actual scope. |
| T17 — unknown and restricted progress | Unknown irreversible sink outcome cannot authorize unsafe retry. A separately supported immutable read can proceed. Missing current authority keeps the affected Work Unit sealed. |
| T18 — external events and replacement | For the chosen exact-obligation profile, later delivery remains allowed after producer replacement. For a claimed use-current profile, post-revocation sink acceptance is excluded by actual sink ordering, not a detached read. |
| T19 — lost sink reply | Distinguish committed and uncommitted histories with identical source observations. Demonstrate duplicate possibility under the existing permissive profile; forbid an exactly-once claim without an added sound sink contract. |
| T20 — engine overlap | Isolate holder A, attempt B activation, then resume A with old requests. No two eligible authority holders can cause conflicting protected acceptance. Refuse takeover if exclusion cannot be established. |
| T21 — derivation restart and deletion | Delete all optional caches and kill a half-completed derivation. Recompute guard from retained state; no partial output becomes authoritative; accepted historical output/evidence remains available. |
| T22 — boundary metadata and information flow | Interior edits cannot alter identity/parent/grants or create an exposed route. Completion alone cannot export x. Created-by/project do not confer management; parent code cannot administer C solely by containment. |
| T23 — unaccepted durable contents | Leave durable candidate z unaccepted, then request final boundary removal. Retain its confinement until valid disposition; checking only the accepted-content list must fail the completeness obligation. Test declared ephemeral scratch teardown separately. |

**Destructive controls:** independently weaken current-view checking, ancestor
checking, source binding, recoverable-before-ack ordering, content retention,
whole-effect recovery, complete-domain checking, latent-rights preservation and
concrete route mediation. Each weakening must produce its intended failing trace.
Do not count one bug with multiple names as multiple independent obligations.

**Acceptance:** the strong model/implementation rejects every forbidden history
within its declared profile, accepts the listed useful controls, and detects all
intended weakened variants. Coverage is by histories and guarantee distinctions,
not merely line count or aggregate test count.

## 4. F3 — realize one complete protected boundary

Before constructing a broad runtime, choose one useful mediated attachment and
its full effect/failure claim. Build the smallest host-protected Work Unit with
retained accepted bytes, authoritative boundary records, a replaceable activity,
and cold recovery. Use one logical commitment holder. Reuse prior Kernel code only
after checking that its trust assumptions match this claim; previous supervisor
survival or descriptor ownership is not proof of general Work Unit confinement.

**First cheapest test:** give old activity the actual route, revoke its ancestor
or stop the engine, then attempt use through retained handles and fresh aliases.
If it bypasses the claim, fix the route or narrow the supported attachment before
building a scheduler, Observer, Processor, general API or UI.

Deliver a concrete inventory of every actionable route in the selected profile:
filesystem names and open handles (including descriptor passing), process/child
creation and inherited authority,
network/external-service ingress, credentials, shared resources and inbound
attachments. State which are absent/disabled, completely mediated, or outside the
physical trust assumptions. Include a bypass attempt for every enabled route.
Never infer resource isolation merely from a record limiting its nominal capacity.
A trusted adapter carrying credentials must enforce its own current scope and
cannot let the untrusted interior obtain reusable ambient credentials.

For every concrete state/effect, supply a mapping to the authoritative view, the
point that establishes its whole recoverable commitment, and which concrete
transitions are private preparation/stuttering. Show how physical confinement
continues during holder loss and how current management excludes an old holder
before activation. Define parser/decoder behavior for untrusted boundary records
without executing the interior. Pin compatible policy meaning for the prototype;
refuse unsupported interpretation rather than implementing a speculative migration
framework.

**Acceptance:** execute the relevant T01–T23 traces plus a live successful sequence:
create empty P/C; explicitly grant supported read/write with attenuation; accept x;
replace activity and use x; kill authority; recover x cold and sealed; activate a
fresh authorized route; accept y; move C sealed to Q without latent widening;
activate and read; dispose dependents and remove the empty boundary. Preserve
independent observations of confinement and actual retained bytes throughout.
A useful external effect must have an explicit profile and its positive/negative
witnesses; arbitrary external correctness is not required.

No full Work Unit sealed-execution claim passes until Q1 is resolved or the actual
realization demonstrates the stronger joint disable interpretation. Report the
narrower verified facts without presenting that gap as an implementation success.

## 5. F4 — failure injection and whole-history refinement

Use the selected realization's actual interruption boundaries, not only mock
API returns. Cover termination during preparation, storage commitment, publication,
replacement, grant revocation, recovery/activation, transfer and disposition. Cover
lost messages, pending old requests and sink response loss when that attachment
exists. Retain observations of storage call boundaries where the claim relies on
them; process termination evidence alone does not prove power-loss durability.

Compare **entire histories** to the formal target, including invocations, replies,
accepted content, external effects and crashes. Require one common acyclic order
and compatible recovered cut. Do not choose incompatible abstract explanations
for different prefixes or components. Permit ambiguity of unacknowledged operations
only where concrete observations actually permit it. The test oracle must remain
outside recovery, not silently restore its remembered state into the implementation.

Check acknowledged old/new values as well as invariants: `(0,0)` after an exclusive
whole transfer can satisfy a capacity invariant while losing the promised transfer.
Inject the no-content, mixed-cut, early-success and replay mutations deliberately.
A corrupted/rolled-back fixture excluded by the baseline illustrates the boundary;
it is not evidence of safe successful recovery within a stronger profile.

**Acceptance:** every recorded concrete history has a single permitted whole-history
explanation satisfying all included observations; known inconsistent histories are
rejected. Publish source revision, commands, profile, bounds, traces, pass/fail and
untested surfaces. This is strong bounded evidence, not proof of OS/runtime/storage
correctness or arbitrary failure schedules.

## 6. F5 — independent review and evidence disposition

Give an independent reviewer the source contracts, pinned implementation/model,
assumptions, raw counterexamples and acceptance criteria. Ask for its own verdict
before it consumes the synthesis's conclusions. Review should specifically attack
closure §8's five propositions and Q1. Cross-family agreement is evidence, not
canonical authority. Do not assert review happened until a delivered result exists.

**Acceptance:** each finding has a required history or explicit missing assumption,
its smallest proposed repair, and a disposition: implementation defect, model
adequacy defect, missing profile evidence, consumer-policy clarification, or new
architectural counterexample. Only the last class, or Q1, reopens frontier work.
A new primitive needs a failed reduction to existing semantics, not reviewer
preference. Preserve disagreement and what was not tested.

## 7. Stronger profiles only when requested by a real requirement

| Proposed extension | Cheapest discriminator before implementation | Condition for claiming success |
| --- | --- | --- |
| Machine/power-loss durability | Interrupt an accepted coupled change at the platform's actual durability boundary and restart with volatile host state gone. | Storage/protection contract and tests cover that failure; acknowledged work and confinement survive. Process-kill evidence alone fails. |
| Rollback-resistant successful recovery | Paired histories with/without acknowledged revocation or y, presenting the same restored image. | A trusted observation/preservation premise actually distinguishes all relevant alternatives; demonstrate wrong-domain and correlated rollback resistance within the claim. |
| Available multi-holder takeover | Partition A; activate B; resume A against every affected sink/store. | Real acceptance boundaries exclude stale A and maintain required ordering/cut; availability assumptions are explicit. A lease label alone fails. |
| At-most-once plus eventual sink delivery | Accept at sink, lose reply, retry; also lose request before acceptance. | Selected sink identity/outcome semantics distinguish/suppress duplicates and progress assumptions support delivery. No local-only assertion suffices. |
| Sink-current cancellation | Delay pre-revocation request, complete revocation, deliver it. | Sink acceptance orders with revocation or a proven equivalent exclusion; any allowed later visibility is stated separately. |
| Time-bounded safe continuation | Identify required deadline, supported workload and a lower bound that defeats recomputation. | Measured/proven bound and failure assumptions meet the deadline. Only then assess necessary persistent precomputation. |
| Physical erasure | Retain covered backup/snapshot/reference, logically dispose object, attempt recovery. | Erasure claim names covered media/copies and establishes removal under that scope. Logical disposal alone fails. |

No automatic adoption of these extensions follows from this table.

## 8. Evidence status at handoff

| Roadmap exit aspect | This investigation establishes | Evidence still owed |
| --- | --- | --- |
| Frozen abstract core | Operations, C1–C12, information admission and removal results. | Formal model/induction and independent review. |
| Explicit trusted/failure boundary | Process-loss/current-storage comparator; concrete-effect and route obligations. | Actual TCB/attachment conformance and Q1. |
| Mechanical replacement | Exact old/new authority and pending-effect contract. | Real ingress/route exclusion under loss and replay. |
| Authoritative information | Truth versus applicability, scoped judgments, completeness and unknown behavior. | Implemented evaluator/verifier and tests. |
| Processorless sufficiency | Finite comparator and fifteen targeted attempts; conditional elimination. | Model/realization refinement and independent falsification. |
| Hostile-testable prototype | Defined positive traces, destructive controls and fault/refinement criteria. | Build and execute F1–F4. |
| No hidden later subsystem | No required Observer/Processor/Orchestrator/tracker/scheduler dependency identified. | Reopen only on concrete contrary evidence. |

**WHY:** implementation agents need fixed observables and pass/fail conditions,
not architectural choices disguised as test tasks. **WHAT:** closure C1–C12,
H1–H14, Processor P1–P15 and Work Unit A–L. **HOW CERTAIN:** evidence-based work
specification, not completed verification. **WHAT-NOT-TESTED:** all F1–F5 work and
stronger-profile extensions; no new runtime/model tests were run in this session.
