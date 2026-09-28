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

**Initial checkpoint:** provenance verified; investigation in progress. No A/B
completion verdict is asserted by this checkpoint.

The frozen architecture basis is the following exact eleven-document set at
`8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. The manifest was read at
`d310a08de512aa7864b283e3964173e64358a4ff`, which changes only
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
  research file, live platform claim, or implementation experiment has yet been
  introduced. References within the frozen packet are inherited claims unless
  separately listed here; their linked sources were not silently imported.
- Operational guidance read from the starting checkout: AGENTS.md, ORIENTATION.md,
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
