---
title: Stage-1 Authority and Recovery Reconciliation
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 8d158e3e82d5811e420c80cc6c9664d3ae4a6088
depends_on:
  - Astra Reasoning Input Provenance
  - EDASES Work Unit Component Design
  - EDASES Authority Ontology
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Phase I Core Substrate Closure
consumed_by:
  - Phase I formalization
  - Phase I realization
  - Phase I architectural closure review
related_documents:
  - Phase I Processorless Core Falsification
  - Phase I Revocation Verification and Q1 Reduction
  - Phase I Core Substrate Verification Work
  - EDASES Execution Engine Roadmap
  - EDASES Efficiency Architecture
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Stage-1 authority and recovery reconciliation

## 1. Run boundary and exact evidence

This is the operator-requested reconciliation of the Stage-1 authority/recovery
semantic delta against the existing Kernel + Work Unit candidate. It is not a
rerun of Phase I, a canonical change, implementation, or formal verification.
New counterhistories below are constructed reasoning, not executed traces.

**Current result:** completion state A; see §12. Earlier local checkpoints
preserve the in-progress evidence and derivation. All conclusions remain
Draft/Derived, with realization and formal assurance explicitly outstanding.

The frozen architecture basis is the following exact eleven-document set at
`8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. The manifest was read at
`d310a08de512aa7864b283e3964173e64358a4ff` (manifest blob
`89af38131465ee37fc780b7fb867860f51492f6e`), which changes only
`docs/research/Astra-Reasoning-Input-Provenance.md` relative to that head. This run
branches from that manifest commit as `codex/stage1-authority-recovery`.
The branch base is not permission to consume other files as architecture inputs.

Manifest: [Astra Reasoning Input Provenance](../../research/Astra-Reasoning-Input-Provenance.md).
For each row, `git rev-parse <frozen-head>:<path>` and the checkout's
`git hash-object <path>` both matched the recorded blob. All eleven passed.

| Frozen path | Git blob |
| --- | --- |
| `docs/architecture/EDASES Work Unit Component Design.md` | `22c98dbabdaed7f41d656209a6ce96269dde8390` |
| `docs/architecture/EDASES-Authority-Ontology.md` | `170016e0d8cfcb72bbe51f5cad230bf53192aa02` |
| `docs/architecture/EDASES-Efficiency-Architecture.md` | `349eee3b51171a9365201eff5d2bd10d8cbfa719` |
| `docs/architecture/EDASES-Execution-Engine-Roadmap.md` | `a82d8a3fc54fd075fd6a20cf9e64ce560313f87c` |
| `docs/architecture/core-substrate/Phase-I-Closure.md` | `a82482b1718a652a39a5a2bb179797f92908380d` |
| `docs/architecture/core-substrate/Phase-I-Processorless-Falsification.md` | `33ff65100cbb10c107337e0f325d1db023e8ffe1` |
| `docs/architecture/core-substrate/Phase-I-Revocation-and-Q1.md` | `4103042649e07b7fd4d6bb1c0f4cf30a01bcc9a9` |
| `docs/architecture/core-substrate/Phase-I-Verification.md` | `ca378a16e31128d6ed11d5472d83253340802253` |
| `docs/research/kernel-0/Kernel-0-Abstract-Semantics.md` | `fd2a485dba3805884fc394b093a61daa60719072` |
| `docs/research/kernel-0/Kernel-0-Verification-Obligations.md` | `7c1d9b198b34c360dd6e8d7d4795704811cfdfa3` |
| `docs/research/registry/Concepts and Topics Registry.md` | `6b7ddf737c14a3853e9be2e64b4417c013ee9c96` |

The original Phase-I output checkpoint remains
`cff5f57c2855c1a251d5b2d4b2f7058be12a3b07`. The reconciled closure and Q1
records in this packet include later work; their wording is not attributed
retroactively to that original run. Work Unit A–L controls current semantics;
the historical design below A–L and Q1's pre-disposition arguments are historical
evidence, not revived requirements. Registry use is navigation/lineage only.

### Additional evidence and operational reads

- The attached operator request supplies the objective, semantic delta, stop rule
  and two completion states. Its SHA-256 is `69cd86c4487860c37b2f9a3d41b8ffc594f5b8d9c387c114fb5ed957972378cd`.
- No outside architecture source, later architecture revision, linked historical
  research file, live platform claim, or implementation experiment was
  introduced in this run. References within the frozen packet are inherited claims unless
  separately listed here; their linked sources were not silently imported.
- Operational guidance read at starting head
  `3d4308b4b` (verified byte-identical in the manifest base): AGENTS.md, ORIENTATION.md,
  Documentation Standard and Concept: Levels of Abstraction. These govern work
  and document structure, not architecture conclusions. Crosslink issue/session
  state and Git/worktree metadata were inspected for task coordination only.
  Shared AGENTS hygiene reported current. The active corresponding issue is #571.
- The main checkout has unrelated changes and is preserved. This investigation
  uses `/home/claude-code/.codex/worktrees/authority-recovery/ASES`.

## 2. Initial discriminators

1. Does user-rooted authority require a new primitive, or does it instantiate
   Kernel-0's explicit initial management premise and guarded delegation?
2. Can fresh reassessment be distinguished from automatic historical replay without
   assuming an Orchestrator, an intent oracle, or a second authority owner?
3. Does continued sealed computation mutate accepted meaning, create protected
   effects, or race safe disposition? A seal alone cannot establish quiescence.
4. Can the existing coherent-view, effect-contract and currentness distinctions
   separate those histories without hiding a new subsystem inside an unspecified
   guard?

**WHY:** these are immediate consequences of the supplied semantic delta, with
cheap counterhistories capable of defeating superficially compatible records.
**WHAT:** the exact packet above, especially Work Unit E–J, Authority Ontology
§§4–13, Kernel-0's view/order/failure contract and closure H1/H4/H14/C1–C13.
**HOW CERTAIN:** evidence-based investigation targets; no reconciliation result yet.
**WHAT-NOT-TESTED:** all model/realization obligations, independent review, and
whether the candidate survives the remaining reasoning.

## 3. State distinctions exposed by the delta

The following are semantic distinctions, not proposed object types, database
columns or separately deployed services. A representation may combine them only
when all required future observations remain equivalent. Section references here
and below refer to the frozen packet in §1.

| Distinction | Smallest history that prevents collapse | Existing home |
| --- | --- | --- |
| User source / current engine mediation / delegated management / capability use | A valid engine serves a request from an Orchestrator whose management grant was revoked. Engine validity cannot authorize that request. | Kernel initial management premise and G; Ontology §§2–7. |
| Authority to install a right / authority to exercise that right | The user lets O attach repository-write to W without permitting O to write that repository itself. Conversely, W's write capability does not let W grant write to another object. | Guarded management effects versus use effects; closure C3. |
| Issuance provenance / continuing validity support | O validly installs a grant, then loses its own role. Whether the installed grant survives depends on its declared validity, not merely who issued it or whether O is running. | Ontology §5 validity conditions; Kernel effect versus later eligibility. |
| Remembered attachment / presently eligible proposal / active current relationship | After loss, the remembered set is authentic and still within user policy, but has not been reassessed/activated. It cannot yet be used. | Current versus past permission and proposal versus commitment. |
| Relationship unavailable / administratively revoked / resource allocation ended | Engine loss disables an attachment while a separately valid CPU allocation survives. These need not be the same event or have the same scope. | Grants and their declared validity; Work Unit E/H. |
| Sealed / computationally quiet / no remaining protection dependency | Sealed W still computes and creates private durable z; even a quiet W can already contain z. Neither seal nor quietness establishes safe boundary removal. | Work Unit H/I, closure H14/C8. |
| Accepted bytes / mutable candidate bytes / containment dependency | Private z need not be accepted, but cannot escape on destruction; accepted x cannot silently change when z evolves. | Kernel authoritative meaning, closure H1/H5/H14. |
| Reassessment / successful reattachment / knowledge of the outcome | A current assessment is followed by revocation, or activation commits and its reply is lost. The assessment is no perpetual permit; no reply is no proof of denial. | Coherent commitment and C12. |
| Pending use / exact committed obligation / later physical visibility | A request queued before loss is not necessarily committed; a validly accepted consequence can become visible later. | Kernel external-action parameters and closure §4. |
| Management lineage / containment path | Reparenting changes enclosing restrictions, not the source of management permission. Revoking management is not the same operation as deleting an ancestor. | Work Unit G/J and closure C3/C8. |

A single `active`/`inactive` field cannot represent all these observations. This is
not evidence for a durable Execution primitive: the missing distinctions concern
relationships, accepted information, effect commitments and protection, not a
required persistent identity for each computation.

## 4. User-rooted authority and bounded decision roles

### R1 — current mediation does not create management authority

**History.** U authorizes O to install read attachments on W. O proposes write.
Alternatively, O reads a broad envelope, U narrows it to read, and O submits the
old broad decision. A current engine accepts because O is the named Orchestrator,
or because the engine considers write useful.

**Failure:** either variant lets a model/role or mediator originate authority.
The Stage-1 root-source and Orchestrator-bound invariants fail even if containment
and storage are perfect.

**Smallest repair:** the grant-changing proposal carries trustworthy evidence of
user-originating authority or current delegated management authority for this
exact operation, target, scope and conditions. The guard checks it in the same
coherent view as the effect. A use capability is not implicitly delegable; an
ability to install someone else's use capability need not include personal use.
An authenticated actor is still checked for the requested operation.

**Positive discriminator:** U expressly delegates installation of read on W;
O installs it while that delegation is current; W reads; O cannot read merely
because it installed W's attachment. Removing O afterward does not disable the
Kernel's ability to admit a direct, authenticated U proposal.

**Reduction:** Kernel-0 already requires the origin of initial management to be
stated, all authority changes to be guarded, and rights/exclusivity policy to be
instantiated. Stage 1 binds that origin to U and rejects any inherited interpretation
of a trusted manager as an independently sovereign agent. Checking the bounded
management predicate belongs in the TCB; deciding what useful work to propose can
remain outside. Management is a required operation/scope distinction, not a new
primitive proven necessary by this history.

### R2 — provenance is not a complete revocation dependency

**Paired histories.** In A, U grants O authority to create a grant whose ongoing
validity expressly depends on O's continuing delegation. In B, U authorizes O to
install a specified standing allocation to W whose validity does not depend on O's
continued role. O installs the grant, then U revokes only O's management envelope.

A later affected use must fail in A. In B, that revocation by itself does not undo
the already-authorized installed relationship; its own conditions still decide
use. An engine that stores only “created by O” cannot implement both promises.
An engine that silently turns all issued grants into independent grants permits
A; one that silently cascades every management revocation contradicts B's scope.

**Required contract:** identify which source authorizes installation and which
conditions must continue to hold during use. Provenance and continuing support
may coincide, but must not be assumed identical. A continuously delegated right
cannot outlive or exceed its current support. A relationship deliberately installed
under a user's standing authorization remains user-derived; it is not authority
originating in O. The root may explicitly revoke the installed relationship too.
If the authorization does not establish a survival condition, recovery cannot
invent one from history or a role label.

These are conditional examples of express authorization scopes, not a declaration
that the canonical model has chosen a universal cascade policy. No cascade default
is needed to test the candidate: the bounded downstream fixture must represent
one continuously dependent grant and one expressly independent standing resource
grant, with the validity conditions stated in its input policy. Generic permissions
without a defined validity interpretation are unsupported inputs.

**Reduction:** existing G reads the complete current support facts. Its result can
be recomputed over finite supported dependencies. Installation is one guarded
effect; withdrawal/expiry/support changes are further events. Historical issuance
must be retained where required for provenance, but need not be a permanent graph
of every past grant. Containment restrictions remain an independent conjunction.
This exposes policy information previously easy to omit; it does not require a
second authority owner or separately persistent derivation state.

### R3 — an Orchestrator cannot bootstrap its own recovery permission

**History.** Engine mediation is lost; O's model/tool/management interfaces are
inactive. A restarted engine says only O can reassess attachments. O needs a model
or management attachment to act, and reattaches that interface using its old role
label. This is either a deadlock or unauthorized self-reactivation.

**Smallest repair:** establish current user-rooted management ingress independently
of the historical Work Unit attachment being reassessed. The existing trusted
initial/current-management assumption must name a supported control path. The user
can reassess directly through it. A standing user authorization can also permit a
bounded recovery action when its present preconditions are established; it cannot
be inferred from the need to make progress. O may subsequently operate through
freshly authorized relationships within its current envelope.

**Positive discriminator:** with no O agent active, recover W sealed, accept a
direct U assessment and activate a bounded route. Then separately show that a
fresh O proposal within a standing delegation succeeds. Neither path needs an
agent-role exception inside G. If U is unavailable and no standing authority
covers recovery, remaining sealed is the correct lack of availability; this is
not successful recovery-and-reactivation.

**Reduction:** authority ingress is already a trusted function in closure §2.
The delta makes its root and independence obligation explicit. This is not a new
ambient backdoor: root authentication, authority-domain binding and currentness
belong to that ingress's realization proof. A design placing every possible
recovery controller behind the very disabled attachment it must restore fails
non-vacuity; “add Orchestrator” does not repair it.

### R4 — current user intent is not an omniscience requirement

**Indistinguishable pair.** All recorded instructions, grants and observations are
the same. In A the user still wants network enabled; in B the user privately
changes their mind without communicating it. No reassessor or Kernel can distinguish
A from B from those observations. An Orchestrator's confidence adds no evidence.

**Contract clarification:** “reassess against current user intent” must mean the
applicable communicated instructions, current user policy/standing grants, and
any qualified semantic judgment explicitly authorized by that policy. An unknown
required fact cannot be asserted current. A new communicated restriction that can
change admission must enter the coherent authoritative view before a later
operation can rely on the old one. The system must identify the point at which
it accepts that restriction; merely displaying a message is not proof of enforcement.

This does not demote intent to irrelevance. It separates desired behavior from
the observable authorization guarantee, as Ontology §3 already does. Reassessment
may require a fresh user choice when standing authority is insufficient; correctness
does not require inferring that choice. A protected external-world precondition
also needs its own fact/currentness contract, not merely a current conversation.

**Reduction:** closure H12/C9 already bounds what a qualified judgment establishes.
A new intent oracle, permanent semantic Processor, or trusted autonomous
Orchestrator cannot be justified by this impossible stronger reading. No claim
that natural-language understanding is mechanically correct is made here.

**Claim disclosure — R1–R4.** WHY: collapsing source, ingress, management,
installation or observations permits the explicit false admissions above or
blocks the required no-Orchestrator control path. WHAT: Ontology §§2–10/12,
Kernel management/order/fact parameters, closure §2/§5/C3/C9 and the constructed
histories. HOW CERTAIN: evidence-based conditional semantic reduction; not a
proof of an authentication or delegation implementation. WHAT-NOT-TESTED: root
identity binding, semantic instruction interpretation, multi-user authority,
real delegation enforcement, or any recovery ingress.

## 5. Recovery means fresh eligibility, not historical replay

### R5 — authentic and still allowed does not mean reattached

**History.** W has attachment a and resources r. Its required mediation relationship
is lost. The stored boundary record truthfully remembers a. Recovery establishes
current storage and user policy still permits the same scope. The engine recreates
a and admits use solely because it appears in that record.

**Failure:** this skips the Stage-1 authorized reassessment and treats a historical
attachment as current. Neither authenticity nor unchanged policy is the activation
event. Conversely, requiring a different scope or new natural-language wording
would be unnecessarily strong: a fresh authorized decision may select exactly
the same capability description.

**Required recovery contract:**

1. Establish the current mediator and exclude conflicting stale mediation for the
   affected authority domain, under the existing recovery assumptions.
2. Recover a compatible current cut of required accepted contents, boundary state,
   policy and authority support. Do not confuse fresh channels with fresh data.
3. Reconstruct the affected attachment descriptions as historical candidates with
   no exercisable authority. Separately determine surviving resource validity;
   don't revoke every resource or call still-running computation newly resumed.
4. A currently authorized decision-maker supplies a reassessment for the proposed
   new relationship, with the relevant current intent/policy, Work Unit state,
   containment and external-fact premises. This can be a direct user action, an
   authorized bounded rule, or O's qualified choice within its delegation.
5. At actual reattachment, validate that assessment's authority and applicability
   in the coherent current view, then commit exactly the permitted new relationship.
   The historical description alone cannot satisfy this guard.
6. Keep every still-invalid, unknown, omitted or out-of-scope relationship inactive.
   Preserve the original historical information needed for recovery/provenance.

These are logical dependencies, not a prescribed number of API calls. A supported
whole transition may perform assessment and activation together. A decision
computed earlier may remain applicable if all relevant premises remain established;
“fresh” means a current authorized decision for this activation, not repeated
model inference or repeated human consent regardless of standing grants.

**Positive discriminator:** the recovered state remembers {a,b}; a current bounded
assessment selects the same scope for a and omits b; a' works, b and old a do not.
A copied old assessment without present applicability fails. No numeric generation
or fresh random token is assumed: the realization owes trustworthy discrimination
between old use and the freshly authorized relationship.

### R6 — reassessment itself can go stale or be lost

**History.** O reassesses W for write under parent P. Before reattachment, U narrows
O, P loses write, or W moves under a read-only parent. Alternatively W's relevant
purpose/state or the external predicate used by the assessment changes. Activating
from the earlier assessment violates at least one current premise.

**Required result:** revalidate all material premises at activation or deny/leave
pending. The assessment's exact subject, effect and decision scope must be bound;
an authentic decision for W is not one for a substituted W'. Unrelated private
computation does not invalidate an assessment unless its result/state was actually
a premise. No complete freeze of W is inferred.

**Loss variant.** Activation commits, its reply is lost, and recovery runs again.
A second loss of required mediation makes even that newly installed relationship
historical for the next recovery. Without a second loss, uncertainty about the
reply does not itself revoke the committed relationship or justify blind duplicate
activation. Read the actual current state and follow the declared outcome contract.

**Reduction:** current eligibility, exact-effect binding, non-confusable ingress,
C7/C12 and repeated-recovery ordering already express these outcomes. Any accepted
reassessment decision that affects required future observation is retained as
accepted information. Unfinished semantic reasoning is replaceable candidate work.
A general durable “Reassessment” workflow object is not required for correctness.

### R7 — no loss, execution loss and mediation loss are different histories

**Distinction test.** (A) The optional O process stops but an independent Kernel
mediator remains valid. (B) A worker computation stops; mediation remains valid.
(C) The required capability mediation relationship becomes unavailable while W's
local CPU/memory allocation and computation survive. A role/process liveness flag
that seals all three cases identically hides this distinction.

The delta directly requires affected attachment disable in C. A and B change
eligibility only according to the relationships actually lost; a deployment may
couple them to C, but must demonstrate that coupling rather than infer it from a
component name. In C, even a retained socket or credential must not bypass the
lost relationship. Loss of one domain need not disable an independent domain.

A safe implementation may over-restrict while knowledge is incomplete, but cannot
claim successful recovery by indefinite deny-all behavior. The scoped baseline
still requires useful post-recovery continuation and a no-O control witness.

**Claim disclosure — R5–R7.** WHY: current source data, historical attachments,
new activation and process liveness permit different future actions. WHAT:
Ontology §§6/11–13, Work Unit E/F/H, Kernel currentness and closure H2/H3/C6/C7/C12.
HOW CERTAIN: evidence-based refinement obligations with explicit counterhistories.
WHAT-NOT-TESTED: crash detection, attachment teardown, stale-route exclusion,
repeated recovery or reassessment persistence in a concrete realization.

## 6. Live sealed computation: follow the consequences to their boundary

### R8 — private progress cannot mutate accepted meaning

**History.** W accepts x through a reference to mutable interior bytes. Mediation
is lost; W is sealed but its computation continues and overwrites those bytes
with y. The engine later recovers the same reference and calls y the accepted x.
No new attachment was used. D1/D2 flags alone therefore fail Kernel protected-meaning
closure and accepted-work continuity.

**Required result:** accepted meaning is fixed to protected retained bytes, or
its mutation is itself a supported guarded effect. A live private candidate may
evolve from x to y, but the change is not an accepted update. Reassessment can
inspect only the exact stable candidate state it actually assessed; a content
selection or copy must bind inspection, validation and later acceptance. Continued
private computation is allowed while such a stable observation is retained.

**Positive discriminator:** accept x, lose mediation, compute private y, recover
and read accepted x, then separately authorize acceptance of y through a fresh
route. This tests useful surviving computation and retained accepted work together.
No need to preserve or replay every speculative computational step follows.

The old H1/H5 already prohibit aliases that mutate accepted meaning. Stage 1 makes
this a baseline live-computation case, rather than a test accidentally passed by
terminating every actor. An Orchestrator's reassessment does not sanitize aliased
storage. A per-computation durable Execution identity would not protect the bytes.

### R9 — sealing is not a stable destruction precondition

**Minimal history.** W is sealed with surviving private writable storage and
computation. A destruction handler correctly finds no durable dependent at t1.
At t2 the computation creates private durable z. At t3 the handler removes W's
boundary using the t1 inventory; z becomes exposed or loses its only protection.
There is no new capability activation in this history. Even if z is never
accepted, Work Unit I and closure H14/C8 fail.

**Necessary property:** final removal must establish both (a) valid disposition
of every existing dependent and (b) exclusion of a later dependent appearing
under the removed boundary. A negative inventory is not stable merely because
attachments are disabled. Every concrete producer that could defeat that property
must either lose that avenue before removal, or remain under an independently
valid bounded destination with the relevant continuing activity/resources covered.

This does not require the Kernel to enumerate every private byte or syscall. A
trusted enclosing allocation can itself be the dependent to transfer or logically
dispose as a whole. Private writes inside that still-bounded allocation can then
be abstract stuttering without changing the complete set of owned allocations.
Alternatively a realization can order each relevant creation with disposition.
The abstraction must prove its choice; an untrusted worker's object list is
insufficient. Accepted-content disposition obligations also continue to apply.

**Minimum successful path:** seal; keep the bounding allocation intact while
private activity continues; perform authorized disposition that closes its future
write/creation avenue and disposes its dependent contents under the declared
storage guarantee; only then remove the now-unneeded boundary. If activity is to
continue after removal, explicitly retain/reassign every protection dependency
it still needs. Refuse removal if neither can be established.

Quiescing a particular writer can be a realization's way of closing that avenue;
it is not a newly mandatory global D3 guarantee on every engine loss. Stopping
all computation alone is also insufficient: pre-existing z still needs disposition.
Conversely the seal itself need not stop computation when an enclosing allocation
continues to protect everything. This rejects both “sealed implies empty/safe to
destroy” and “safe destruction always requires globally inert Work Units.”

**Reduction:** Work Unit I's no-weaker-containment precondition and Kernel's
coherent whole effect already cover this history. Closure H13/H14, P4 and removal
ordering remain valid, but the downstream event alphabet must include relevant
private creation, not only explicit Kernel child creation/acceptance. A model
that omits this concrete producer can falsely pass. No independent scheduler,
execution lifecycle, or persistent dependency Processor is forced. Complete
protection at the disposition event is trusted; inventory display and progress
reporting can remain derived.

### R10 — inactive attachments do not release surviving capacity

**History.** Capacity is one. W holds a reservation of one and computes using it.
Mediation is lost. Recovery marks W's attachments inactive and treats all its
resource reservations as zero. It then grants one to V while W still uses its
surviving allocation. The promised capacity invariant is broken without any
forbidden outward capability use by W.

**Required result:** account for the actual surviving allocation under its own
validity and resource contract. An inactive attachment is not evidence of release.
A reservation may be released only when the protected allocation/reclamation
transition has the promised effect. Missing evidence of release cannot justify
new allocation that would exceed the bound in a compatible surviving history.
The healthy positive control releases or safely transfers W's reservation and
then admits V; indefinite refusal is not its expected result.

The unit-capacity example concerns reservations, not a claim about measured CPU
usage, energy, or exact spend. A resource with expiry or a cumulative consumption
budget needs enforcement for that separately declared condition even while engine
mediation is unavailable. It is not a “surviving valid resource” if its own condition
has failed. No trusted clock/meter is required for a fixed reservation merely
because a timed budget is possible; conversely declaring a timed budget would
not make its enforcement an optional optimization.

**Reduction:** closure C2/C3, P14 and Verification F1 already require conserved
quantities and allocation/consumption separation. Stage 1 requires the model to
retain this state through engine loss while attachments become inactive.
Computed totals can be rebuilt from complete current allocations. A resource
manager chosen in a realization is part of the TCB for its claimed enforcement,
not proof that a first-class Processor is needed.

### R11 — a resource label cannot hide a callable escape route

**History.** A provider session, shared writable mapping, or filesystem handle is
called a “resource.” It survives engine loss and activity uses it to perform a
new protected external operation or change accepted state. The system claims only
attachments needed disabling.

**Required result:** classify by the relationship's actual effects across the
logical Work Unit boundary, not a physical object's name or location. Passive
support/allocation and a callable cross-boundary route may coexist in one physical
realization but have distinct permissions and loss conditions. Shared accepted
bytes are not private scratch. A remote API call is not automatically exempt just
because it supplies computation. A separately committed bounded remote operation
must instead meet its explicit obligation/effect contract in R12.

A local computation may mutate private memory/storage within a granted bounded
allocation without each internal instruction becoming an attachment operation.
That is compatible only while it changes no accepted meaning, exceeds no enforced
resource condition and defeats no protection/disposition obligation. Baseline
physical trust and excluded covert-channel/information-flow claims are unchanged;
“no influence on the outside” does not here become a newly claimed absence of
all timing, heat or shared-hardware effects.

**Reduction:** Work Unit B calls resource/attachment an operational distinction
within grants. The delta requires different validity treatment, not disjoint new
ontological primitives. Effect correspondence and protected-meaning closure are
the discriminator. A route that cannot satisfy the attachment promise is unsupported,
not repaired by relabeling it as a resource.

**Claim disclosure — R8–R11.** WHY: the constructed histories violate accepted
meaning, safe destruction or capacity while the simplistic seal flag is true.
WHAT: Work Unit B/E/H/I/K, Kernel protected-meaning/order semantics, closure
H1/H5/H13/H14/C3/C5/C8 and Processor P4/P14. HOW CERTAIN: evidence-based necessity
of the distinctions, with a conditional reduction to existing policy/effects.
WHAT-NOT-TESTED: snapshot isolation, live private-storage disposition, memory/handle
revocation, capacity enforcement, resource metering/expiry, host or remote-provider
behavior. These are not empirical counterexamples to a running implementation.

## 7. In-flight effects, containment and scope of loss

### R12 — loss cannot reclassify a pending request as a committed obligation

Use three distinct events: authoritative decision D, irreversible sink acceptance
S, and later visibility V. A selected attachment must say at which event authority
is required and which invalidations cancel or preserve an exact prior obligation.

| History | Required interpretation |
| --- | --- |
| Propose q; lose required mediation; deliver old pending q | Historical queue membership is not authority. No new use can be admitted through the invalid relationship. |
| Commit a specific bounded obligation q under a declared decision-authorized, loss-surviving contract; lose producer mediation; complete q later | May be allowed by that contract. It does not resurrect the general capability or permit q' substituted by a live old computation. |
| Check permission; lose mediation; sink accepts under a promise requiring current permission at S | Forbidden without an admissible current authorization at S. An earlier read or a local “committed” label does not satisfy this different contract. |
| Sink irrevocably accepts q while authorized; lose mediation; consequence becomes visible later | Later visibility alone is not a fresh exercise of the inactive attachment. Revocation cannot be represented as undoing the irreversible acceptance. |

A surviving exact obligation must be retained with its precise meaning and
validity/outcome contract. It is not the historical attachment set. If further
protected dispatch is needed, its actual route must satisfy that contract; the
old producer's invalid general-purpose channel cannot do it. An in-flight message
already irrevocably committed can complete under the declared profile. A dispatch
needing unavailable mediation must wait for authorized recovery. No universal
right to continue all buffered commands, automatic cancellation, or exactly-once
retry follows.

This is a clarification required where Stage-1 summaries say “protected outward
effects disabled.” Read that as excluding affected new use at the contract's
protected event; reading it as “no later physical consequence of any earlier
commitment” contradicts Kernel-0 and closure H4/C10. The packet already distinguishes
these cases. No effect profile is silently changed here. The first mediated-use
fixture should test the first/third rows; a separate exact-obligation fixture
must test the second/fourth, including substitution and lost replies.

### R13 — sealing and moving must preserve latent restrictions

**History.** P restricts child C to read; C remembers a broader historical attachment
set and has surviving computation. After loss, C is moved sealed under permissive
Q. A reassessor restores C's historical set using Q's permissiveness. C gains write
without any specifically authorized widening. D1/D2 held throughout the move but
the later activation violates no-accidental-widening.

**Required result:** the whole move preserves or narrows the relevant retained
restriction on C and its descendants, and reattachment checks that resulting
state plus present management authority. A fresh assessment is not automatically
authority to widen. A separately authorized root/delegate widening is a different
allowed event, not an accident to prohibit. Surviving resource reservations must
also be accounted for under the new supply/containment contract; relabeling parentage
cannot produce more capacity or leave protection assigned to neither parent.

**Positive discriminator:** move sealed read-only C with private computation and
accepted x; reattach current read; read x succeeds and write remains denied;
then a separately authorized widening can allow write. Test one descendant and
an unaffected sibling to avoid both a one-object abstraction and gratuitous
system-wide sealing.

**Reduction:** closure §7 already tests latent authority, including resources
and management dependencies. Stage 1 strengthens the recovery fixture: remembered
attachments are candidates, and active private computation is not mistaken for
active external permission. This is C3/C8 plus R5/R10, not a new transfer primitive.

### R14 — stale mediation survives a process label change

**History.** A loses contact with the authoritative domain but can still reach a
sink; B restarts and passes a user-root authentication check. B reassesses W and
creates fresh attachments, while A continues using its old ones.

**Required result:** B's genuine user-derived mandate is not sufficient evidence
that A has lost effective access. The realization must exclude stale A at every
affected protected event before conflicting B activity is admitted. If it cannot,
activation remains unavailable. Unaffected domains may proceed when independence
is established. The conceptual persistence of user sovereignty supplies neither
failure detection nor a second current view.

**Reduction:** H2/C6/C13 already require exclusion and policy ordering. The delta
removes a misleading “transfer of sovereignty” story without removing any concrete
currentness obligation. No generation, lease, election, clock, or process identity
is thereby selected. A genuinely new authorized grant to the old physical producer
is a separate event; permanent exclusion of that producer needs the additional
source-binding policy already distinguished by Kernel-0.

**Claim disclosure — R12–R14.** WHY: a blanket loss rule either revives pending
capabilities or rejects permitted prior consequences; fresh approval or new
parentage alone cannot exclude stale routes or authorize widening. WHAT: Kernel
external-action/order clauses, Work Unit G/J, Ontology §§9/12/13 and closure
H2/H4/H6/C6/C8/C10/C13. HOW CERTAIN: evidence-based contract reconciliation, not
universal cancellation or takeover assurance. WHAT-NOT-TESTED: actual sinks,
pending-message exclusion, overlapping mediators, coupled moves or physical-source
binding.

## 8. Reduction test: no new primitive demonstrated

The claim is deliberately scoped to the finite Phase-I comparator. It is not made
true by allowing an unspecified guard to hide arbitrary new services. Extend its
explicit retained policy/state only with the information exercised above:

- trusted user-root ingress and current bounded management permissions, including
  operation/target scope and declared continuing support;
- current authoritative Work Unit forest, restrictions and conserved allocations;
- exact accepted bytes/decisions/required provenance and retained historical
  attachment descriptions;
- usable versus unavailable current mediation/attachment relationships, with
  non-confusable old/new admission observations;
- any selected exact obligations and their required continuation/outcome information;
- protection dependencies sufficient for safe disposition, represented either
  individually or by a trusted enclosing allocation.

The finite evaluator checks root/delegated scope, current declared support,
whole-path restrictions, capacity, exact input/effect applicability, absence of
unaccounted protection dependencies, and invariant-preserving whole effects.
Recovery additionally establishes the declared current cut and disabled old routes
before admitting current reattachment. These are explicit checks over supported
finite state and trusted predicates, not an arbitrary policy-language interpreter,
semantic truth solver, autonomous planner or derivation lifecycle.

Private evolution may be abstract stuttering only while it preserves all required
permission/continuity/protection observations. R8/R9 show the proof obligation for
that assertion. Loss that changes attachment eligibility is a represented event;
the surviving enforcement that makes it true is part of the declared realization,
not a guard evaluating a fictitious always-correct liveness bit.

| Proposed addition/distinction | Required guarantee and delta exposure | Existing representation / trusted placement | Necessity verdict and discriminator |
| --- | --- | --- | --- |
| User-origin and bounded management scope | Prevent O/engine self-authorization; Stage 1 fixes the source explicitly. | Initial-state premise plus guarded authority changes; ingress and evaluator trusted, semantic planner outside. | Correctness distinction, no new primitive; R1. |
| Issuance versus continuing support | Do not guess what management revocation invalidates; exposed by treating O as delegate. | Supported grant validity in current state/G, provenance retained separately where required. | Correctness information, no mandatory lineage service; R2 paired histories. |
| Current recovery reassessment | No automatic reactivation of remembered capabilities; direct Stage-1 requirement. | Ordinary current management proposal/commit with scoped assessment evidence. | Correctness event, no mandatory agent or durable reassessment workflow; R3/R5/R6. |
| Separate resource validity and capability activity | Preserve/limit continued allocations while losing outward authority. | Existing grants plus distinct predicates and quantity accounting; enforcement trusted. | Correctness distinction, not two new grant primitives; R10/R11. |
| Protection against live candidate mutation/creation | Accepted meaning and safe disposition despite continued computation. | Protected accepted bytes, whole disposition of complete domain/enclosing allocation; concrete protection trusted. | Correctness, not global freeze or Execution object; R8/R9. |
| Reassessment input/interpretation binding | A current decision cannot authorize substituted or changed state. | Existing scoped fact/decision admission and current-view order. | Correctness; R4/R6, with unchanged-input positive control. |
| Loss-surviving exact obligations | Preserve contracted effects without reopening general capability. | Existing declared effect semantics and retained accepted obligation state. | Required only for selected profile, not a generic queue; R12. |
| Latent rights and allocation preservation on move | Prevent recovery from widening or double-supplying rights/resources. | Existing whole move and activation guards. | Correctness; R13. |
| Independent Processor, Observer, Orchestrator, scheduler | None of these histories demands a separate authoritative lifecycle. | Bounded evaluation, explicit invocation and retained inputs/accepted choices suffice conditionally. | Not established as necessary; remove optional subsystems and run the successful histories in §10. |

**Processor challenge followed through.** Fresh reassessment might appear to
require replaying an unavailable semantic decision, maintaining a persistent
invalidation graph, or running an always-present Orchestrator. None follows.
A prior accepted decision whose scope still matters is retained information,
not a disposable derived value. A new qualified decision can be supplied through
a current authorized ingress. Applicability of either can be checked from retained
current premises; missing semantic permission leaves the affected proposal pending
without inventing truth. Finite current support/path checks can be recomputed.
If a required premise is an external fact, its trusted observation contract remains
necessary; naming its supplier Observer does not eliminate that obligation.

The Phase-I conditional elimination argument still applies to genuinely derived
values. It does not license deletion of the newly explicit authority decisions,
resource allocations or protection facts. No mandatory response deadline or
irreproducible required computation lifecycle has appeared in the Stage-1 delta.
Efficiency's event-driven/demand-driven preference remains subordinate to actual
fail-closed mediation; delayed invalidation notifications alone cannot authorize
use. A separate cache or view can remain outside the TCB only if its loss or error
cannot change protected admissions without trusted checking.

**WHY:** every retained distinction has a failing collapse history and a bounded
instantiation using existing semantic parameters; no tested requirement demands
a second authoritative lifecycle. **WHAT:** R1–R14 and the frozen Processor
comparator/elimination premises. **HOW CERTAIN:** evidence-based scoped survival,
not an exhaustive proof of all architectures or a demonstrated host realization.
**WHAT-NOT-TESTED:** formal product/induction, concrete refinement, timing bounds,
arbitrary grant languages, arbitrary semantic correctness, independent review.

### Loss is not an unguarded grant-changing escape hatch

One final adequacy challenge concerns Kernel-0's rule that changes of authoritative
meaning are guarded events: how can attachment eligibility change when the engine
that normally performs those checks has stopped?

The reconciliation does not require the dead process to execute a revocation
command. A relationship whose declared validity requires available mediation is
already conditional on that fact. The abstract failure/event relation must expose
its loss and the resulting disabled eligibility, consistently with the pre-existing
policy. The concrete route must actually stop admitting the affected use. This
is an instance of Kernel-0's externally triggered/policy-generated events plus
the explicitly stronger Phase-I failure profile; it is not permission for an
arbitrary external event to install or widen grants.

A use that must pass through unavailable mediation can fail closed without a
separate scheduler first deciding that a process is dead. A retained autonomous
route, however, cannot be declared disabled merely by that reasoning: its use-point
exclusion still needs a conformance argument. A model's loss event is not evidence
that a real host observes/enforces that event. R7/R14 and C13 keep this gap visible.
The source of the fact and the entire enforcing boundary count in the TCB;
neither a mandatory Observer nor a mandatory timeout follows. This challenges
the failure relation's adequacy without introducing a new unconditional primitive.

## 9. Disposition of prior claims and terminology

This section is a proposed downstream contract supplement. It preserves the
frozen texts as historical evidence rather than silently rewriting them. “Revised”
below means the indicated reading is rejected by this reconciliation; it does not
promote this Draft/Derived record to Canonical authority.

| Prior claim or location | Disposition in this pass | Downstream meaning |
| --- | --- | --- |
| Kernel-0's six distinctions and model invariants 1–6 | Confirmed for the scoped candidate. | No new primitive or transition calculus is demonstrated necessary. Supply the explicit authority/failure/policy parameters above. |
| Closure §2/§7: trusted manager / initial management | Clarified by Stage 1 and R1/R3. | Trusted user-rooted ingress and enforcement are not sovereign agents; O's proposals still need current delegated scope. |
| Roadmap §2: Kernel “owns” authoritative transitions/enforcement | Clarified, not deleted. | Owns responsibility for representation/enforcement, not the root right to authorize. |
| Ontology §§5–8: grants and attenuation | Refined by R1/R2/R10/R11. | Installation permission, use permission, current validity, issuance provenance and resource reservation cannot be collapsed. No universal grant lifetime/cascade rule is invented. |
| Work Unit F: register sealed/inactive; resume execution through explicit relationships | Clarified by R5/R7/R8. | Outward relationships are inactive. Surviving internal computation and valid allocations need not be restarted; a new exposed relationship does require current authorization. |
| Closure §3/§7: recover then explicitly activate | Confirmed and made more discriminating by R5/R6. | Current cut plus historical attachment descriptions is insufficient; activation needs present authorized reassessment and applicable premises. |
| Q1 Part B: D1 means no new work admitted or started | Historical broad reading superseded by the Stage-1 disposition. | D1 concerns affected capability admission/use. Work within surviving resource bounds is not prohibited merely because it is new private computation. |
| Q1 Part B: D2 means nothing egresses | Qualified by Kernel effect contracts; R12. | No affected new protected use at the declared event. Do not retroactively cancel valid exact commitments or forbid their later visibility by definition. |
| Q1's D3 requirement and automatic stopping language | Baseline requirement already superseded by Stage 1; confirmed here. | Global engine-loss quiescence remains optional. Specific resource reclamation/destruction may still require excluding a live writer; R9 is not a global D3 promise. |
| Historical Q1 assertions that D1/D2 are “always” achievable, or that a named timer is universally necessary for D3 | Not inherited as realization evidence or mechanism necessity. | Abstract obligations do not prove a host route closes. Optional timing profiles need their own justified enforcement/timing assumptions; this pass selects none. |
| Closure C5/C8 and destruction H13/H14/P4 | Confirmed, with expanded adequacy fixture. | Include live private creation and protection of whole allocations; do not assume sealed means an inventory cannot change. |
| Closure §7 / F1 conserved resource quantities | Confirmed, with loss-state refinement. | Inactive attachments must not zero surviving reservations. Define allocation, release and consumption distinctly. |
| Processorless closure and Efficiency §§5–6 | Confirmed conditionally. | Retain authority decisions/allocations/required information; recompute genuine derived values. No persistent derivation lifecycle is forced by the delta. |
| Work Unit C/L: Execution is activity, not a required durable object | Confirmed. | Add relevant activity/protection events to models without canonizing a durable Execution primitive. |
| F1/F3 as next architectural steps; later roadmap phases remain deferred | Confirmed with the supplement below. | Still formalize and realize the finite candidate; first cover these distinctions. No new multi-phase redesign or broad research programme follows. |

## 10. Downstream obligations reduced to explicit checks

These supplement C1–C13 and T01–T24; they do not replace their existing whole-effect,
continuity, content-retention or trust assumptions. They are specifications of
future checks. No formal verification or implementation was started in this run.

### Semantic invariants to carry into F1

| ID | Checkable obligation | Trace basis |
| --- | --- | --- |
| S1 | Every admitted grant-changing effect has a current, scope-correct authorization grounded in the user; authenticated role/identity, useful judgment and engine process identity alone are insufficient. | R1/R3/R14. |
| S2 | Current use satisfies all declared continuing support, containment and resource conditions. Issuance provenance is neither sufficient current support nor an implicit revocation dependency. | R2/R10/R13. |
| S3 | Loss of required mediation disables the affected attachment. Remembered pre-loss attachment descriptions cannot authorize use or activation; a current authorized reassessment and whole activation establish any new relationship. Old evidence remains invalid even if the new description is identical. | R5/R6/R7. |
| S4 | Reassessment scope and all required mutable premises are applicable at actual activation. Unknown required intent/fact/currentness cannot be silently supplied by O, a historical decision or user silence. | R4/R6. |
| S5 | Private computation under surviving valid resources cannot alter accepted meaning, exceed claimed resource bounds, create unmediated protected crossings or weaken protection. Sealed does not assert private-state immutability or zero resource consumption. | R8/R10/R11. |
| S6 | Final boundary removal has a complete current disposition basis and excludes future dependent creation under that removed protection; all surviving protected activity/content remains bounded. Quietness or a prior empty inventory alone is insufficient. | R9. |
| S7 | Each pending/committed external effect follows its declared decision/use/acceptance/visibility and failure contract. Inactivity of the old attachment neither grants pending work permission nor silently cancels an independent valid obligation. | R12. |
| S8 | Restart/reparenting/role replacement does not widen authority, lose accepted work, free unreleased capacity or permit stale conflicting mediation. A separately authorized change is distinguishable from resurrection. | R6/R10/R13/R14. |
| S9 | Removing the active O agent or optional derived subsystems leaves a supported direct-user or explicitly standing-authorized path for useful operation/recovery under healthy declared premises. | R3 and §8. |

### Hostile fixtures and positive controls

Reuse the frozen verification plan's fixtures; add only states/events required to
make the Stage-1 alternatives distinguishable. U/O identity and management scope,
current versus historical attachments, a live internal computation, one surviving
unit-capacity allocation, accepted x/private y/z, and a destruction-in-progress
observation are sufficient new dimensions for the first finite fixtures. The
existing P/Q/C/D containment and old/new ingress cases remain relevant. Bound the
supported validity conditions and effect vocabulary explicitly; don't turn this
into an arbitrary authority-language implementation.

| Supplement | Exact discriminator and expected result | Existing work it extends |
| --- | --- | --- |
| V1 | O has authority to install read but neither install write nor personally read. Read installation succeeds; the two unauthorized actions fail. Narrow O between assessment and commitment; old wider proposal fails. | T01/T16/T22; R1. |
| V2 | Install one expressly continuously dependent grant and one expressly standing resource allocation. Revoke only O's management envelope. The first loses eligibility; the second follows its own validity and remains accounted for. | T01/T04; R2/R10. |
| V3 | Remove O. With healthy root ingress/current storage, U recovers W sealed and authorizes read. Read succeeds. A role-only self-bootstrap request fails. | F1 non-vacuity, T09/T10; R3. |
| V4 | Recover authentic historical {a,b}; with no current assessment, neither activates. A current scoped decision selects only a; a' works, b and attempts based only on old a fail. The same capability description is allowed in a genuinely new grant. | T02/T03/T08/T10; R5. |
| V5 | Reassess, then independently change O's envelope, relevant parent restriction, assessed state or required external premise before activation. Each relevant invalidation blocks stale activation; an unrelated private change does not force reassessment. | T11/T14/T16; R6. |
| V6 | Crash after assessment/before activation; then after activation/before reply; then lose mediation during recovery again. Recover only permitted whole states; no replay restores old channels. A no-crash lost-reply control retains the actual definite commitment. | T07/T10; R6. |
| V7 | Keep private CPU activity running after mediation loss; old capability use fails, accepted x is unchanged, private y can evolve. After authorized recovery, read x then separately accept exact y. Mutating the accepted referent is a failing variant. | T05/T06/T21; R7/R8. |
| V8 | With W sealed and computing, enumerate empty, create private durable z, then attempt final removal. It must not expose z. Close/dispose the complete enclosing allocation or preserve a valid new boundary, then successful removal is possible. Stop-only with undisposed z also fails. | T12/T13/T15/T23; R9. |
| V9 | Capacity one remains allocated to W through engine loss. Granting one to V fails until W's allocation is actually released/transferred under the resource contract; then valid allocation succeeds. | T04/T05/T10; R10. |
| V10 | Label an actionable retained handle “resource”; attempt a protected effect after loss. The use still fails. Private mutation inside a valid bounded allocation remains allowed. | T05/T22/T24; R11. |
| V11 | Delay an uncommitted request across loss: reject old-authority use. Separately delay an exact committed obligation under a loss-surviving profile: permit only its precise promised consequence, never substituted q'. An acceptance-current profile has its own contrary expected outcome. | T18/T19; R12. |
| V12 | Move sealed C and D with live private computation under a permissive parent; fresh read works, old forbidden write does not. Surviving allocations remain conserved. A separately authorized widening is a positive control. | T11/T12; R13. |
| V13 | B has authentic current U authorization; A retains a stale route. B's activation cannot authorize conflicting effects until actual exclusion is established. Also remove only O while mediation remains healthy and confirm no fictitious Kernel-loss event. | T20/T24; R7/R14. |
| V14 | Present identical observations with an uncommunicated change of user intention in only one history. Do not claim the system detects the difference. Then admit a communicated restriction and confirm later affected use cannot rely on the old view. | T16/T17; R4. |

Each failing variant must reach the targeted fault. A fixture that kills every
writer at engine loss cannot count as evidence for V7/V8; one that deletes all
old routes by test setup cannot establish V4/V13; one with no successful activation
cannot establish non-resurrection together with useful recovery. These are
adequacy checks, not instructions to weaken a deployed guard.

### Realization/refinement obligations for F3/F4

1. **Name the actual root ingress and its protection.** Demonstrate scope checks
   with and without O. Show when communicated authorization/revocation becomes a
   committed fact and what success acknowledgment means. A semantic interpretation
   service, if trusted for a premise, must disclose exactly what it establishes.
2. **First route discriminator:** retain a real usable route and live private
   computation, lose required mediation, and attempt old use. Establish actual
   use-point refusal, not only a metadata change. Inventory aliases, inherited
   handles, queued work and access-policy changes per T05/T24. Accepted bytes must
   survive and remain protected while private activity continues.
3. **Prove the recovery mapping:** distinguish survived allocations, historical
   attachments, current decisions and fresh active relationships. Record the
   currentness/exclusion assumptions and interrupt each activation boundary.
   Recovered state must retain the compatible cut; renewed authority cannot repair
   missing accepted work or establish that a rolled-back image is current.
4. **Prove private-step abstraction:** identify which concrete steps preserve all
   authoritative/protection observations and may stutter. Use R8/R9 to challenge
   this. Define how ownership of an enclosing allocation makes private bytes safe
   without per-byte Kernel records; final removal must exclude later invalid writes
   and surviving unbounded activity. Refuse unsupported disposal/transfer promises.
5. **Conserve resources across loss and movement:** connect the abstract reservation
   to actual allocation and release. State fixed-reservation versus measured-use
   semantics and the failure boundary; add clocks/meters only if a selected validity
   condition requires them. Partial release cannot be reported as complete reclamation.
6. **Map effects as whole histories:** state the protected event for every enabled
   attachment and exact obligation. Account for old pending messages, lost replies,
   independently surviving consequences and repeated recovery. The abstraction
   cannot explain one prefix using decision-current authority and a conflicting
   suffix using acceptance-current authority.
7. **Repeat the optional-subsystem removal control:** no O agent, cache, Processor,
   tracker or general scheduler is present in the minimal successful sequence.
   Trusted ingress, finite checking, retained information, protection and explicitly
   invoked recovery remain. Their absence would be a different, unsupported claim.

**Successful sequence required:** U establishes empty W; delegates a bounded choice
to O; current selection grants a supported attachment/resource; accept x; lose
mediation with private computation surviving; old use fails and private y evolves;
recover x/current resource accounting with remembered attachments inactive; directly
U (no O) reassesses and activates read; read x; separately accept y; move a sealed
restricted child and activate without widening; dispose all dependencies safely,
including live producers, and remove the unneeded boundary. Independent observations
must check actual bytes, routes and resource/protection state.

This sequence is a downstream target, not a purported execution result. Failure
of one host mechanism first falsifies that realization. Reopen the architectural
candidate only if the required behavior cannot be represented or discharged by
any supported existing contract, or if a presently assumed property itself proves
incoherent for the accepted profile.

## 11. Assumptions, remaining questions and reopening conditions

No unresolved choice of a new core primitive or mandatory subsystem remains in
this scoped reconciliation. The following unknowns are explicit proof/realization
obligations or input-policy parameters, not claims settled by prose.

| Assumption / question | What evidence must settle it | What failure would change |
| --- | --- | --- |
| A trustworthy current user-root ingress and initial authority domain can be established. | An explicit realization/authentication mapping and V1/V3/V13. | If no supported control path exists, recovery non-vacuity fails; adding an assumed agent cannot repair it. Multiple competing root users remain a separate unselected policy. |
| Every granted relationship has a supported, unambiguous validity/effect interpretation. | Declare and check installation/use scope, continuing support and invalidation for the finite fixture; V2/V4/V11. | An unrepresentable mandatory policy may require a richer policy instantiation; first try existing parameters rather than declaring a new primitive. No implicit grant survival/cascade default is established here. |
| Required mediation/protection survives or fails closed for the selected process loss. | Retained-route, stale-mediator and concrete policy tests, with the actual TCB disclosed. | A bypass invalidates that realization's D1/D2 claim. If the required guarantee is unattainable under the selected trust/failure assumptions, stop and reopen the profile rather than weaken it silently. |
| Accepted contents, current allocations, decisions and compatible authority state survive the covered failure. | F4 loss/coupling tests with independent observations and no recovery oracle. | Missing information defeats continuity/currentness. Fresh authorization cannot recover missing work; rollback resistance remains unselected. |
| Live private computation remains confined and accepted meaning protected; disposition can close all future dependencies. | V7–V10 and an actual abstraction for private mutation/enclosing allocations. | An uncontrolled producer falsifies the realization/refinement. If safe useful removal requires an unrepresented guarantee, reopen the disposition contract. |
| Reassessment requires observable premises or expressly authorized judgments, not uncommunicated intent or arbitrary semantic truth. | V5/V14; declare the source/meaning/currentness of every consumed fact. | A requirement for truth unavailable from any permitted observation is an information-boundary pivot, not an occasion for stronger model confidence. |
| Finite supported checks terminate; no correctness deadline requires irreproducible autonomous derivation state. | F1 mapping and the processorless removal control. | A new required deadline/lower bound or independent necessary lifecycle reopens Processor elimination under its original conditional test. |
| External effects obey their selected contract; no arbitrary cancellation, at-most-once delivery, secure erasure or host-compromise resistance is promised. | Profile-specific sink/storage/confinement evidence if selected. | Selecting a stronger guarantee reopens only its affected failure/effect boundary, not all Phase I. |

Representation choices—storage format, grants schema, source binding, revocation
mechanism, immutable-byte custody and protection teardown—remain for realization.
They must be compared against the above properties. This pass does not pick leases,
generations, databases, logs, replication, a process model or a host mechanism.
Neither does it require the operator to decide abstract facts that the next bounded
tests can discriminate.

## 12. Completion decision and continuation cursor

**Completion state A — reconciliation succeeds for the declared Phase-I candidate.**
The supplied Stage-1 changes are coherent with the surviving Kernel + Work Unit
semantics after the explicit contract clarifications above. Fourteen concrete
histories, their contrasting successful cases, and the failure-event adequacy
challenge reduce to existing guarded authority/effect/currentness/continuity
semantics with explicit Work Unit policy and trusted realization obligations.
No material pivot was established. No claim of complete formal or implemented
Phase-I assurance follows.

The consequential reductions are: user-rooted management without agent sovereignty;
current reassessment distinct from historical replay; separate surviving allocation
and capability eligibility; live private evolution distinct from accepted state;
safe removal distinct from sealing; and precise treatment of committed consequences.
The no-Orchestrator and processorless correctness claims survive within their
original bounds. F1/F3 remain the next steps, with §10 as a required candidate
supplement; later optional-subsystem design remains deferred.

**Why stop here:** the materially different histories exposed by the delta have
specific invariants, successful/hostile witnesses and refinement discriminators.
Remaining uncertainty needs model or concrete realization evidence, or a newly
selected requirement. Continuing into a general authority language, recovery
framework, scheduler or subsystem design would expand the task without a failed
architectural obligation.

**Continuation:** read this record together with the exact §1 packet; instantiate
S1–S9/V1–V14 alongside C1–C13/T01–T24, preserving the stated policy and failure bounds.
Begin with the retained-route/live-computation discriminator and root/reattachment
scope fixtures. If an architectural pivot emerges, preserve its smallest history,
affected prior claims and dependencies, then stop for the next explicit decision.
Do not treat a failed host mechanism, preferred alternative design, or unselected
stronger guarantee alone as evidence that the core needs a new primitive.

**WHY:** every required distinction introduced by this reconciliation has a concrete
failure witness and an explicit smaller representation inside the existing finite
candidate; the successful witnesses exclude pure deny-all reasoning. **WHAT:** the
verified eleven-blob packet, the supplied semantic delta, R1–R14, the failure-event
challenge, and the removal/obligation mapping. **HOW CERTAIN:** evidence-based
architectural reconciliation and conditional reduction; not machine-checked proof,
independent consensus, or demonstrated realization conformance. **WHAT-NOT-TESTED:**
F1–F5, actual user authentication, natural-language interpretation, host enforcement,
resource retention/reclamation, real recovery, sink behavior and all unselected
stronger profiles. No subagents, formal verifier or production implementation ran.
