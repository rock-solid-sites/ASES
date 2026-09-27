---
title: EDASES Currentness and Recovery Assurance
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 566
baseline_commit: 052658f46d154b549df33d99535b868f6f28f1dc
baseline_branch: codex/work-unit-foundational-review
foundational_reduction_baseline: 6596931136f8276ae573041c2ade25a6f5ad0c64
depends_on:
  - Work Unit-0 Foundational Reduction
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Kernel-0 Authority-Service Crash and Recovery
  - Kernel-0 Multi-Domain Composition
  - Concept: Levels of Abstraction
related_documents:
  - Kernel-0 Assurance Continuation
  - Kernel-0 Re-Minimization After Stronger Profiles
  - Concepts and Topics Registry
  - EDASES Work Unit Component Design
  - Methodology to Requirements Mapping Specification
  - Execution Engine Vision
  - Workflow Topology Design and Reasoning Record
  - Crosslink DB Rollback Incident
consumed_by:
  - EDASES recovery assurance documentation review
  - Work Unit Formal Specification
  - Work Unit Prototype Testing
  - Recovery claim authors and reviewers
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-27
---

# EDASES Currentness and Recovery Assurance

## 1. Decision and scope

**The currentness result survives as a reusable derived assurance obligation for
claims that recovered information represents current permission, accepted state,
or required continuity under a declared failure model.** It is not a requirement
for every persistent object, every cache hit, or every historical record.

Kernel-0 already expresses the necessary distinctions and trust dependencies.
No new Kernel primitive, stable ontology entity, or broader runtime architecture
is justified. The justified addition is an explicit, reusable way to discharge
existing recovery claims: identify the materially different histories the claim
must exclude, and explain how the declared surviving information or preservation
premise excludes them. Where that cannot be done, bound the recovery claim or
withhold the affected outcome.

This is more than a Work Unit-local issue because existing requirements promise
recoverable **current methodological state**, and orchestration promises resumption
from durable tracker state. Their consumers need the same distinction without
having to adopt Work Unit containment. Their exact propagation tasks are in §7.
No wider propagation is inferred from the mere presence of storage.

The important narrowing of Work Unit-0 F3/T6 is that **different permitted
outcomes do not necessarily require different recovery behavior**. Denial,
restricted operation, or a genuinely new authorization may be valid in both
histories. That can preserve safety without establishing which historical state
is current. Non-vacuity somewhere in a system is also weaker than successful
continuation from the particular ambiguous recovery observation.

This document proposes documentation changes; it does not adopt policy or modify
canonical contracts. It implements no service, recovery mechanism, persistence
layer, or Work Unit.

**WHY:** the indistinguishability proof in §3 and removal witnesses in §4 apply to
specific existing non-Work-Unit claims in §7. **WHAT:** the pinned repository
contracts and bounded evidence below. **HOW CERTAIN:** proven conditional
information limit; evidence-based placement and propagation recommendation.
**WHAT-NOT-TESTED:** a new realization, current Crosslink behavior, a Work Unit
implementation, or an independent adversarial review of this result.

## 2. Evidence boundary

The review starts at branch head
`052658f46d154b549df33d99535b868f6f28f1dc`, verified against the remote branch on
2026-09-27. This includes the foundational reduction and its confinement follow-up.
The reduction itself used `6596931136f8276ae573041c2ade25a6f5ad0c64`; that earlier
commit is lineage, not the source snapshot for this review. All source references
below refer to the review baseline. Unrelated working-tree changes are excluded.

| Ref | Source and precise use |
| --- | --- |
| F | [Work Unit-0 Foundational Reduction](../work-unit-0/Work-Unit-0-Foundational-Reduction.md), §2 (premises 4–5) and §5/F3/T6: proposition under investigation, not an axiom. |
| K | [Kernel-0 Abstract Semantics](../kernel-0/Kernel-0-Abstract-Semantics.md), Parameters and meaning; Authority and order; Continuity and failure: current view, observational equivalence, trustworthy distinction, coherent order, selected failure boundary. |
| V | [Kernel-0 Verification Obligations](../kernel-0/Kernel-0-Verification-Obligations.md), Model adequacy; Trace properties; Trusted assumptions and claim boundary: freshness, successful witnesses, profile-specific recovery and refinement. |
| C | [Kernel-0 Crash and Recovery](../kernel-0/Kernel-0-Crash-Recovery.md), What must survive; Two recovery claims; Result A1: current cut, cold/continuing recovery, executed same-root rollback. |
| A | [Kernel-0 Assurance Continuation](../kernel-0/Kernel-0-Assurance-Continuation.md), completed gates and strongest counterexample: bounds of the cumulative positive and negative evidence. |
| J | [Kernel-0 Composition](../kernel-0/Kernel-0-Composition.md), Removal attacks; What composes: whole effects and compatible joint recovery. |
| R | [Concepts and Topics Registry](../registry/Concepts%20and%20Topics%20Registry.md), authority boundary; deterministic reuse, checkpointing, Work Unit baseline: identities and discovery of candidate consumers, not substantive authority. |
| M | [Kernel-0 Re-Minimization](../kernel-0/Kernel-0-Re-Minimization.md), Removal audit: checks that the proposed rule does not introduce an already-rejected primitive. |

Expansion is restricted to actual claim owners: Work Unit A–L, requirements state
management/recoverability/evidence management, engine state management, workflow
resumption and durable positions, and the Crosslink rollback incident. Their links
are in §7. **W** below denotes the current A–L sections of the Work Unit Component
Design, not its preserved historical design. The registry names *EDASES Minimal Execution Substrate Architecture*
and its *Design and Reasoning Record*, but those titled documents were not located
in this baseline. Processor summaries therefore support discovery only; this
review does not invent their missing substantive contract or infer one from the
superseded Work Unit design.

C's existing [experiment result](../kernel-0/Kernel-0-Crash-Recovery-experiment-results.json)
records `outside_profile_same_root_rollback`: save image, acknowledge revocation,
kill, restore old same-root image, restart, old authority commits. This review
inspected that recorded trace; it did not rerun it. A's 90 storage-call process
cuts and 12 partial-write experiments retain the current-storage premise and do
not establish resistance to that rollback. J is bounded model evidence, not a
physical multi-holder recovery demonstration.

The histories below are semantic witnesses constructed for this review, except
where an existing result is expressly identified. They are not new experimental
measurements. Lower-layer documents supply claims to test, not axioms from which
the information limit is derived.

## 3. Strongest defensible formulation

### 3.1 Currentness is relative to a claim and an observation point

For this review, **currentness** means that recovered information is adequate to
represent the required present authoritative meaning at the declared recovery or
use point, given the permitted histories and failures. It need not be the newest
byte image, preserve every old value, or identify one wall-clock instant. A
coherent current cut can have several concrete representations.

Let `F` declare allowed histories, losses, rollbacks, survivors and trust
assumptions; `Q` declare the permission, accepted-state and continuity observations
promised by the consumer. Histories `h0 ≈Q h1` are equivalent only when no required
future observation under Q distinguishes them. Audit/history observations count
if the claim includes them. A diagnostic timestamp does not count if Q excludes
it and it has no effect on future required behavior.

Let `o` include **all** recovery-available information used to make the claim:
retained data, configured policy, trusted survivors and any permitted exchanges.
Define `H_F(o)` as the allowed histories compatible with that information. Equal
disk bytes alone do not imply indistinguishability if a surviving authority,
content holder or other trusted source distinguishes the histories. For an
interactive recovery procedure, the argument requires an indistinguishable
observation transcript through the decision, including replies to adaptive
queries. Unread oracle history available only to a test harness is not evidence.

### 3.2 Information limit and behavior limit

> If two histories admitted by F yield indistinguishable information at a
> recovery claim's decision point, but disagree on a currentness proposition
> required by Q, a procedure using only that information cannot soundly determine
> that proposition in both histories. In particular, it cannot certify an exact
> current Q-equivalence class when `H_F(o)` spans distinguishable classes.

**Proof:** the same observations and declared assumptions give the procedure the
same basis for an assertion in both histories. If the required answer differs,
one such assertion is false. Adaptive queries do not help while their transcripts
remain indistinguishable. Randomness independent of the history provides no
evidence identifying it: the output distribution is the same. For a binary answer
with no abstention, one of the two histories has error probability at least one
half. A probabilistic claim with a supplied prior is a different, qualified
assurance claim, not certainty about which history occurred.

There is a related but narrower operational impossibility. If `B_Q(h)` is the set
of acceptable continuation strategies for h, a procedure unable to distinguish
the histories must choose a strategy acceptable for **every** member of `H_F(o)`.
If their intersection is empty, no such procedure meets that continuation claim.
For a single resolved outcome, the same test uses allowed outcome sets. Different
sets alone are insufficient: they may share denial, waiting or a useful restricted
action. For a family of histories, pairwise overlap also does not ensure a common
strategy across the entire family.

These statements require neither reconstruction of the full past nor knowledge
of all future events. Later authority changes must be ordered with later use,
as K already requires. A recovery observation does not permanently freeze rights.

### 3.3 Exact premises and escape conditions

1. Both histories are admitted by the **same** declared trust/failure contract.
   If current surviving storage excludes rollback, the rollback history cannot
   refute that narrower contract. The preservation premise still needs evidence
   in a realization claiming to satisfy it.
2. The hidden difference changes a required proposition or continuation outcome.
   Physical age, different encodings or irrelevant lost events are insufficient.
3. The procedure has no trustworthy discriminating observation before the claimed
   decision. A surviving fact must differ in the relevant way; mere independent
   location or a stable root identity is insufficient.
4. The claim is sound determination of current state, or satisfaction of the
   specified continuation obligations. A guess, historical interpretation,
   abstention, or explicitly weaker recovery is not that claim.
5. A new authorized transition may change future requirements. That is a new
   event, not retrospective proof that the recovered historical image was current.

The result is an information limitation on a specified claim. It proves neither
that all rollback is harmful nor that a universal external freshness source is
necessary. Distinguishing every Q-class is sufficient to remove this particular
information obstacle; it does not prove policy correctness, content availability,
confinement, implementation refinement or recovery progress.

## 4. Counterhistories and attempted falsifications

### H1 — authentic revocation rollback, and the missing success premise

There is one grant g and one affected action a. Save valid image S with g enabled.
In history 0, lose the holder and recover S. In history 1, revoke g, acknowledge
completion, lose the holder, and restore every recovery-visible fact to S.
Request a after recovery. Signatures, origin, root, recorded version and provenance
inside S agree; current permission differs. This is F.T6 and the semantic form of
C's executed attack.

A claim to establish whether g remains current fails. A promise to successfully
continue g in history 0 while excluding it in history 1 also fails without a
survivor or narrower failure premise. But K's bare safety rule only makes commit
conditional on eligibility; it does not require every eligible request to commit.
**Denying both is safe under that weaker rule.** Successful recovery elsewhere
does not establish success for this ambiguous observation. The failure must be
reported as lost permission knowledge or unsupported continuation, not simply
"all recovery is impossible."

### H2 — byte-different but behaviorally equivalent

S0 and S1 encode the same retained content, rights and containment with different
field ordering or an irrelevant diagnostic timestamp. All Q-observations agree.
Requiring evidence that selects S1 rather than S0 adds no promised guarantee.
If a timestamp later determines expiry, or its history is a required audit
observation, the premise changes and the states cease to be equivalent for Q.
This defeats "recover the latest bytes" and universal event replay requirements.

### H3 — identical recovered bytes, different required continuity

Save S containing accepted content x. In history 0, no replacement is accepted.
In history 1, accept y in place of x and acknowledge it; then lose/roll back every
visible record to S, with no surviving y holder. Recovery sees identical bytes,
but the promised accepted content differs. Even disabling every old bearer cannot
make x the current accepted content in history 1. A fresh manager granting access
to S does not reconstruct y. The two *actual authoritative histories* cannot map
to the same abstract σ under K; the indistinguishable concrete recovery evidence
is precisely an inadequate representation under this failure model.

### H4 — common safe progress, and immutable useful facts

Extend H1 with a separately preserved immutable document d whose read permission
is unchanged by the revocation. Recovery can allow the shared read of d while
withholding a. This is useful progress without identifying g's current status;
sealing every unrelated domain would be an unnecessary restriction.

Alternatively, let a work item be terminal and immutable by the declared policy,
with no permitted later transition affecting Q. An authentic, correctly bound
terminal image determines its required state even if it is old. An immutable
accepted fact can also remain true while unrelated fields evolve. Thus "immutable
state cannot establish anything useful" and "every old image needs an external
freshness source" are false. If later revocation or supersession is permitted,
immutability of the saved bytes alone does not remove H1/H3.

### H5 — new authority and deliberate reset

A currently authorized recovery manager issues a genuinely new grant after H1.
Both histories may now permit a under that new event, provided its preconditions
do not depend on the unresolved historical difference. The manager's present
authority is a separate trusted premise; restoring its old credentials is not
enough. This does not establish old g, old parentage, or H3's missing accepted y.

If policy permits an explicit destructive reset to S, an authorized reset can
make S the new valid state. It has changed the continuity promise through a new
guarded event. Calling that reset "recovery of the previously current state"
would conceal information loss. Bootstrap, reset and recovery must not be
silently substituted for one another.

### H6 — surviving but irrelevant evidence, and detached validation

Keep root r outside the rollback domain. Both H1 histories have r: recovery still
cannot distinguish them. Similarly, authentic current evidence for domain B
cannot certify an old image of A. A history-sensitive surviving attestation helps
only if it applies to the particular recovered view, domain and relevant policy.

Now supply relevant evidence that g is current, complete revocation, then activate
g using the earlier check. Recovery's evidence was truthful when read; use is
wrong because validation and activation lack K's coherent ordering. This is
authority revocation during use, not loss of disk durability. A contract must
cover both the recovery claim point and subsequent protected use.

### H7 — individually authentic pieces do not form a whole recovery

A joint transfer changes `(A=1,B=0)` to `(A=0,B=1)`. Recover A before and B after
to obtain `(1,1)`, violating exclusivity. Recover A after and B before to obtain
`(0,0)`: exclusivity holds, but the transfer's whole effect and resource continuity
fail. J reports both failure shapes in its removal attacks. Checks against each
piece's own local history cannot certify the joint commitment.

This does not refute genuinely complete currentness checks whose dependency
scope already includes the joint effect. It refutes treating separate local
checks as a sufficient joint check. Two disjoint work bits with independent
authority and no coupled effect can recover independently; no universal total
order or synchronized snapshot is justified.

### H8 — accepted methodological state versus preserved evidence

S records that validation v supports promotion of artefact a. A later accepted
decision invalidates v's applicability or withdraws promotion readiness. An
interruption restores S and hides that decision. An authentic historical v still
supports "this validation was performed on that input"; it does not support
"promotion is currently permitted." If restored state authorizes promotion, the
current-state/validation claim fails. An archive answering a historical query
about v remains correct. This separates evidence preservation from restoration
of the current epistemic relationships used for action.

### H9 — last-known orchestration state and a durable but obsolete tracker

S contains a last-known ready position for work t. In history 0, it remains valid.
In history 1, a completed stop, changed prerequisite or recorded disposition
supersedes it; recovery presents S and loses that change. Reporting readiness or
resuming an affected action on S alone is unjustified. Reading S as a recovery
hint, then obtaining current task authority and reconciling its dependencies,
does not make that claim and can be correct.

The [Crosslink rollback incident](../crosslink-db-rollback-incident.md), Root cause
evidence and Impact, records a concrete related failure: hydration from an old
hub checkpoint lost local-only issue registrations and closure while structural
integrity checks passed. This establishes that a consistent dataset need not
preserve the required work state. It does **not** establish total information loss
in that incident: Git/hub artefacts survived, so reconstruction could use additional
evidence. Nor is it evidence that the current Crosslink binary still has the bug.

### H10 — cache applicability, then rollback of its authoritative inputs

For a pure deterministic function f, a retained result `f(x)` remains applicable
to the same complete immutable inputs and computation semantics. Evicting it and
recomputing changes cost, not authoritative state. No extra freshness duty arises
merely because it is old or durable.

If the current input changes from x to y while the cache still serves `f(x)` as
`f(y)`, this is ordinary invalidation/applicability failure. Recomputing from known
current y repairs it. If recovery instead rolls both the input selector and its
invalidation record back to x while the accepted current input must remain y,
recomputing `f(x)` cannot repair the lost authoritative distinction. The currentness
obligation attaches to the recovered input/acceptance claim, not to memoization
as a new kind of authority. Correct provenance for `f(x)` does not make x current.

### H11 — a reference does not preserve content

Accept a digest of y, retain the digest, then lose the only bytes of y with the
executor. The digest may be authentic and demonstrably current. Continuation
requiring y still fails. V already includes this trace. Currentness is necessary
for some recovery claims, not a replacement for availability, complete content
or declared trusted holders.

### H12 — replicas and liveness are not interchangeable with currentness

After acknowledged revocation, a lagging replica can return the old authentic
grant. If the contract allows historical reads, that read need not be wrong.
If it authorizes a new action that requires current permission, H1 applies even
without a crash. Replication and distributed ordering determine which observations
are allowed; recovery still needs those assumptions to survive its failures.
Several replicas that roll back together add no discriminating information.

A heartbeat from just before a crash can likewise be authentic and recent while
its producer is dead. Conversely, a process may be live while its tracker view
lags. Age thresholds can trigger investigation; they do not establish missing
revocations, the current recovery cut, or present process liveness. Existing
startup checks remain their own operational obligation.

**WHY:** each history removes a premise or isolates a different promise, so it can
falsify an overbroad formulation before mechanisms are designed. **WHAT:** H1–H12,
with C/J/V and the incident explicitly identified where reused. **HOW CERTAIN:**
proven failures or non-failures under the stated toy histories; evidence-based
connection to actual contracts. **WHAT-NOT-TESTED:** executed new traces, exhaustive
consumer policies, current tracker hydration, distributed recovery or storage.

## 5. Minimum conceptual distinctions

These are distinctions in claims, not a proposed collection of runtime records.

| Existing notion | What it answers | Relationship to currentness |
| --- | --- | --- |
| Identity/genesis | Which object/work/domain is this, and what trusted establishment does it descend from? | Excludes wrong-object/bootstrap confusion. The right object can still be an obsolete image (H1/H6). |
| Authenticity/integrity | Is the information from the claimed source and intact under its integrity contract? | Necessary where relied on, but an authentic old record remains authentic. A checksum alone need not establish origin. Neither property excludes supersession. |
| Provenance | What derivation, creator, input or accepted history explains this material? | Establishes lineage within its evidence scope. Completeness through the required cut is an additional premise; a valid prefix can omit a later event (H8/H10). |
| Current authoritative relationships | Which grants, restrictions, parentage or accepted relationships govern now? | This is part of the meaning to be recovered, not proof that the recovered representation has that meaning. Source and governing authority can differ. |
| Continuity | What same work, accepted content and future use must survive the selected interruption? | Determines the observations for which currentness matters. Also requires content and compatible whole effects (H3/H7/H11). It need not preserve concrete bearers or every old value. |
| Durability | Which commitments/information survive which failures? | A strong durability contract preserving the current whole view can discharge currentness without another mechanism. Mere persistence of some authentic bytes cannot (H1/H9). |
| Recovery hints | Where to look, what the last recorded topology was, or what may have happened? | Useful candidate evidence; not permission to reactivate or represent the hint as current (H9). |
| Freshness/currentness | Is the information adequate for this required present-state proposition/use? | A scoped property of information under a history/failure contract. Wall-clock recency is one possible observation, not its definition or a universal sufficient test. |
| Authority to create a new valid state | Who may perform a particular new transition under current policy? | Can authorize a new grant or explicit reset without proving the recovered past current. Its own authority and state-dependent preconditions need support (H5). |

The word **currentness** is useful because "durable", "authentic", "created by",
"same root" and "last known" recur at interfaces that consumers may mistake for
present authority. H1, H8 and H9 make that ambiguity consequential. But removing
the word while keeping K's current authoritative view, trustworthy observations,
failure projection and continuity contract loses no expressive power. The
distinction is already present in C and V.

**Reduction:** clarify an existing claim property and give it a reusable assurance
rule. Do not add `concept:currentness`, a Freshness object, or a new lifecycle
owner. R already records the relevant boundary-record and recovery relationships;
no new independent identity or graph relationship is demonstrated here. An
editorial reference to this finding is sufficient if adopted.

The neighboring problems remain separate:

- **Rollback currentness:** recovery hides a completed distinction that Q still
  requires. H1/H3 are direct witnesses.
- **Ordinary cache invalidation:** derived output does not apply to known current
  inputs. H10's first failure needs applicability checking, not historical-state
  reconstruction.
- **Dependency staleness:** a relationship or result no longer applies after a
  dependency changes. This can occur without any failure. It becomes a recovery
  currentness problem only when restoration loses the required change/selector.
- **Provenance:** origin/derivation may be correct while current applicability is
  false. Archival truth and current acceptance are distinct (H8).
- **Distributed consistency:** concurrent holders' observations and commitments
  must meet the chosen ordering/visibility contract. It is not solved by merely
  preventing rollback; conversely, replica agreement on one old view is not
  evidence that no completed revocation was lost (H7/H12).
- **Authority revocation:** defines which later actions must be excluded. Recovery
  currentness is one obligation necessary to preserve that rule across a selected
  failure; H6 also shows an ordinary ordering failure without rollback.

## 6. Architectural placement test

| Candidate placement | What fails if the proposed addition is absent? | Decision |
| --- | --- | --- |
| New Kernel-0 semantic primitive | Nothing in H1–H12 requires a distinction beyond K's authoritative view, trust, current eligibility, order, whole effect and continuity/failure parameters. Omitting those existing semantics would fail H1/H3/H7, but adding another primitive is unnecessary. | **Existing semantics already sufficient.** Do not change K. |
| Kernel verification obligations | V already requires freshness assumptions, sufficient distinguishing state, covered recovery traces and realization correspondence. A verifier ignoring these would admit H1/H3, but that is nonconformance to existing obligations. | Add at most a derived recovery-profile checklist/reference to make discharge explicit; do not expand the base executor-loss guarantee. |
| Shared EDASES recovery/assurance rule | A Work Unit-only note leaves the current-state promise in the requirements mapping and the durable-resumption promise in orchestration susceptible to H8/H9. Those claims do not depend on a Work Unit boundary record. | **Narrowest useful reusable placement:** a conditional assurance rule for authors/consumers of current-state recovery claims. Initially this research result; promotion requires explicit adoption. |
| Work Unit-specific requirement | Removing currentness from W.E/F permits H1/H3 for grants, contents and containment. But making the entire rule local leaves H8/H9 unresolved. | Retain Work Unit's concrete sealed-recovery policy and continuity projection locally; reference the shared rule. |
| Research finding only, with no proposed contract propagation | The theorem remains correct, but recoverable-current-state and last-known-state wording remain underspecified at actual consumer interfaces. H8/H9 justify a bounded clarification now. | Keep this artefact non-normative, but recommend the specific propagation below. No open-ended architecture programme is needed. |

The reusable obligation is about **substantiating an existing guarantee**, not
silently making every consumer resist a larger failure class. A contract that
explicitly excludes storage rollback may retain that exclusion. A historical
archive need not become a current authority service. Generic safety may permit
withholding only the affected action, whereas Work Unit recovery specifically
requires preserving its sealed boundary.

## 7. Impact map and bounded propagation

### 7.1 Existing claims and their actual reach

| Area and existing source claim | Discriminating case | Required consequence and classification |
| --- | --- | --- |
| **Kernel authority/recovery.** K's current eligibility and failure clauses; V's freshness and conformance obligations; C's current whole cut and cold/continuing profiles. | H1/H3/H6. | Already sufficient semantics. Preserve the current-storage premise and profile bounds. Optional verification clarification P1 below, not a new authority-record type. |
| **Work Unit boundary record/restart.** [Component Design](../../architecture/EDASES%20Work%20Unit%20Component%20Design.md), D–F and K.9/K.20, requires discoverable identity, current authority/currentness and declared continuity. | H1–H6/H11. | Existing concept needs clarification: qualify E's candidate principle using §3; supply a concrete recovery claim before implementation. Sealed confinement, contents and containment remain Work Unit-specific. |
| **Checkpoints/restored execution.** R's `topic:checkpointing-and-stacked-diffs` is deferred; W.C/F promises work continuity without requiring live processes to survive. | H2/H3/H5. | Existing semantics sufficient for Work Unit recovery. No generic checkpoint service contract exists here to amend. A historical checkpoint may remain a candidate; promoting it to current work invokes the rule. A deliberate branch/reset may have a different continuity contract. |
| **Processor/deterministic reuse.** R identifies applicability checks, provenance, invalidation and recomputation; substantive named source documents were not located. | H10, including the valid immutable-input reuse case. | No blanket propagation to caches, no new Processor responsibility. Conditional implementation-dependent question only if a later design treats restored inputs/results as current authoritative meaning. Do not use R's summary as a missing specification. |
| **Reasoning/evidence stores and promotion state.** [Requirements Mapping](../../requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md), Evidence Management preserves supporting evidence; State Management requires current recoverable methodological state, and Validation checks promotion readiness. | H8/H11. | Existing concept needs clarification P2. Preserve historical evidence as such; any recovered current acceptance/invalidation relationships used by validation need the scoped assurance contract. No evidence ontology change. |
| **Crosslink/durable work state.** [ORCHESTRATOR](../../ORCHESTRATOR.md), Orchestrator as Single Integration Point promises resumption from last-known durable state; Crosslink Stewardship requires accurate current project state. [Workflow Topology](../Workflow%20Topology%20Design%20and%20Reasoning%20Record.md), §5.1/5.4, makes the same dependency explicit. | H9 and the recorded rollback incident. | Existing concept needs clarification P3 at the consumer claim. Current storage or reconciled surviving evidence must support present-state assertions. An obsolete tracker may still provide hints. This review does not diagnose a live Crosslink defect. |
| **Replicas/distributed holders.** J's whole joint transfer and compatible-cut obligation is the concrete existing contract; its physical realization is expressly unproved. | H7/H12. | Existing semantics sufficient; a realization claiming split-holder recovery must evidence the declared cut. No global synchronization rule for independent domains. Implementation-dependent evidence gap, not a new consensus requirement. |
| **Authority records.** K treats authority changes as guarded events; C distinguishes stored current relationships from concrete bearer reconstruction; W.D separates creator provenance from current management. | H1/H5/H6. | Existing semantics sufficient. Authenticate and bind the recovered relationship under the selected failure model; new grants do not certify historical content. No separate authority service is forced. |
| **Future durable orchestration.** [Execution Engine Vision](../../architecture/Execution%20Engine%20Vision.md), Methodology Execution and State Management, promises current methodological state and resumption from state. | H8/H9. | Consume P2's clarification through the existing requirements dependency. No new execution-engine component, lifecycle ownership, or universal loss tolerance follows. |

The [Session Recovery After VPS Crash](../session-recovery-after-crash.md), Key
Lessons, reports survival of Crosslink and Git records after a particular session
failure. That remains useful bounded evidence. It is not evidence that any
authentic restored database is current under arbitrary rollback. No revision of
that historical observation is necessary.

### 7.2 Every proposed shared change, its witness, and why it cannot stay local

Only the following shared documentation propagation is justified. These are
proposals for a later authorized edit, not changes performed by this review.

| ID / target | Exact proposed change | Claim lost if omitted; why Work Unit-local wording is insufficient |
| --- | --- | --- |
| **P1 — V, profile-specific recovery assurance guidance.** | Reference the scoped result in §3 and use §8's six fields when a realization claims restored current state. Note that uncertainty can permit safe common behavior without establishing full currentness, and that successful witnesses must match the advertised recovery scope. | H1 distinguishes safety-only denial from the stronger continuation claim; H6/H7 expose omitted binding/cut assumptions. V is shared by Kernel consumers, including consumers with no Work Unit; a boundary-record note does not discharge their conformance argument. This makes existing obligations explicit, not stronger. |
| **P2 — Requirements Mapping, State Management and Recoverability.** | Qualify recovered *current* methodological state by a declared interruption/failure boundary and preservation or reconstruction basis, with a defined response when required current relationships cannot be established. Keep historical Evidence Management distinct. Use this shared rule by reference rather than duplicate the proof. | H8 restores promotion readiness after accepted withdrawal. Requirements already promise current state and valid transitions to all implementations; repairing only Work Unit metadata would leave other evidence/workflow stores able to satisfy a weaker, merely historical reading. H11 keeps content preservation separate. |
| **P3 — ORCHESTRATOR resumption/current-state claim and its Workflow Topology rationale.** | Clarify that a last-known position is candidate resumption information unless the declared recovery assumptions preserve its required current meaning. Before asserting current task state or taking affected action, reconcile relevant changes and current authority; otherwise hold that claim/action. Reference the existing safe source-selection guidance, without rewriting launch or approval policy. | H9 loses a stop/prerequisite/disposition; the incident demonstrates consistent-but-obsolete state. Orchestration consumes trackers directly, without depending on Work Unit semantics. Its operational contract and research rationale must agree about what durable positions establish. |

P1 is a **reusable derived assurance rule**; P2/P3 are **existing concepts needing
clarification**. Existing [playbook §6.5](../../../.crosslink/knowledge/agent-orchestration-playbook.md)
already distinguishes hub agent output from a stale hydrated cache and records a
historical fix. P3 should reference that boundary rather than prescribe another
sync procedure or claim the fix is absent. The playbook's named source is itself
trusted only within its declared preservation/visibility scope. A live audit of
that implementation is outside this review.

The common reusable text proposed for these references is:

> A recovery claim that presents retained or reconstructed information as current
> for permission, accepted state or continuity must identify the covered failures,
> required observations, and trusted basis excluding materially obsolete
> alternatives at the claimed point of use. Unresolved alternatives must not be
> asserted away: withhold the affected outcome or explicitly provide the weaker
> recovery that policy permits. Include a compatible whole recovery cut where
> commitments couple the recovered domains.

Local follow-up is narrower: W.E/F and F.§5 should replace the unqualified
"every recovery claim" reading with this applicability test and distinguish
permitted from promised successful continuation. R's candidate quotation can
link to the narrowed finding without adding a concept ID or changing its
identity/lineage authority. The engine vision can reference clarified requirements;
it does not need a separate architectural rule. No change to canonical terminology,
the general methodology, storage architecture, or every registry entry is justified.

**WHY:** P1–P3 each name an existing consumer promise and a concrete failure, with
a reason Work Unit-local wording cannot protect that consumer. **WHAT:** the
source sections in the map and H1/H6–H9/H11. **HOW CERTAIN:** evidence-based impact
analysis; currentness is already expressible in the existing concepts.
**WHAT-NOT-TESTED:** all repository consumers, missing substrate documents, live
tracker behavior, or adoption of these proposals. No project-wide runtime change
is proposed.

## 8. Minimum assurance contract

For an affected claim, record the following information. Existing contract
clauses may supply it by reference; this is not a mandatory schema or stored
certificate. A claim only about archival recovery or pure deterministic reuse
can state that scope and avoid asserting current authoritative meaning.

| Field | Minimum content | Removal test |
| --- | --- | --- |
| **1. Required observations and alternatives** | What permission, accepted state or continuity is promised; at which recovery/use point; what counts as observationally equivalent; which success/availability outcomes are actually required. Identify historical alternatives whose difference matters. | H2 overconstrains bytes if equivalence is omitted; H1 confuses permission with required success; H3 misses content continuity. |
| **2. Failure projection** | What may disappear, roll back or become mutually inconsistent together; what remains trusted; which failures are excluded. Include all authoritative dependencies even when they live outside the named component. | H1/H10 hide correlated rollback; moving a record elsewhere does not remove it from the failure projection. |
| **3. Exclusion or preservation basis** | Why compatible surviving observations cannot hide an alternative that falsifies the claim: a justified preservation premise or sufficient trusted evidence/reconstruction. Do not use "this is current" as its own evidence. | H1's authentic image and H6's invariant root satisfy integrity but do not exclude obsolete alternatives. Trusted current surviving storage can supply this field for the process-loss profile. |
| **4. Binding and ordered use** | How the basis applies to this work/domain, policy and recovered view, including required content/relationships, and how changes between validation and protected use are ordered. Initial/recovery management authority has its own trust basis. | H5/H6 admit wrong-domain evidence, resurrected management authority or detached activation; an external fact without this binding is insufficient. |
| **5. Uncertainty and successful recovery boundary** | Which assertions/actions are withheld, what candidate/history access remains valid, and whether recovery waits, fails, offers restricted operation or makes an explicit authorized reset. Provide successful witnesses for each advertised recovery mode; state conditions under which success is unavailable. | H1 defeats an always-deny claim of successful continuation; H4 defeats universal freezing; H5 exposes a reset mislabeled as continuity. Unknown is not a fabricated denial of an already committed outcome. |
| **6. Coupled recovery cut, when applicable** | Which cross-domain dependencies or whole commitments must be preserved together; how recovered observations form a compatible cut respecting required committed effects and order. For independent domains, state why no joint cut is required. | H7 loses a whole transfer even when a local invariant passes. Independent bits supply the counterexample to mandatory global coordination. |

For the C/J profile, a compatible cut preserves completed commitments and
irrevocably committed effects with lost acknowledgements, respects predecessors
of interacting commitments and includes each declared whole effect without
tearing it. A later legitimate supersession need not retain every old value.
Other recovery claims must state their own observation/commitment boundary rather
than silently inherit stronger durability. In particular, lack of a reply does
not prove noncommit and currentness does not imply exactly-once effects.

Three bounded applications check that this contract does not prescribe mechanisms:

- **Existing process-loss recovery:** the holder's volatile state is lost, the
  trusted whole current store survives, relevant accepted content is retained,
  and configured root/policy plus continuing-mode source binding are explicit.
  Exclude hostile rollback and power loss as C does. The currentness premise is
  supplied by surviving storage, without a new external freshness service.
- **Same profile expanded to include total indistinguishable rollback:** H1/H3
  show field 3 cannot be discharged for the old exact-currentness promise.
  Narrow the claim, preserve discriminating information under an explicitly
  stronger trust boundary, or withhold the affected recovery. Writing more
  metadata inside the same loss projection cannot satisfy the promise.
- **Pure cached computation over specified immutable inputs:** promise the result
  for those inputs, not the latest accepted input selection. H10's first case
  has no competing current-state alternatives. Applicability, integrity and
  availability remain relevant; rollback resistance is not added to that cache.

These fields are necessary assurance content, not a sufficient correctness proof.
Authors must substantiate preservation assumptions, model required histories and
provide realization correspondence. Successful witnesses show non-vacuity only
within their declared conditions; they do not prove eventual recovery for every
failure. Consumers can audit presence, relevance and stated exclusions without
rerunning the producer's verification, consistent with AGENTS' certainty rule.

## 9. Necessity audit and remaining evidence questions

| Proposed consequence | Classification | What fails on removal, or why no addition survives |
| --- | --- | --- |
| Distinguish current meaning from authentic historical material | Existing semantics already sufficient; clarify usage | H1/H8 fail if removed. K/C already express it. |
| Scope recovery by observations, failure projection, trust and order | Reusable derived assurance rule (P1) | H1–H7 expose each omitted premise. Existing K/V parameters express the rule without a new API. |
| Qualify non-Work-Unit current-state/resumption claims | Existing concept needs clarification (P2/P3) | H8/H9 fail the actual named promises; local Work Unit edits cannot cover their consumers. |
| Add a stable currentness ontology entity | New ontology distinction **not justified** | No required reasoning becomes inexpressible after removing the proposed entity while retaining the existing property and assurance rule. |
| Add a shared freshness service, universal counter, authority subsystem or global recovery coordinator | Broader architectural change **not justified** | Process-loss preservation, H2/H4/H10 and independent domains are counterexamples to necessity. No counterexample defeats the more abstract six-field obligation. |
| Select actual survivors, storage/reconstruction, binding or distributed cut mechanisms | Implementation-dependent / unresolved | H1/H3/H6/H7 identify exactly what each selected realization would have to defeat; foundational reasoning alone cannot establish its survival properties. |

Only the following questions need further evidence. Each has a concrete witness
and a bounded next test; none requires designing a freshness architecture now.

| Question | Why reasoning alone does not settle it | Cheapest discriminating next evidence |
| --- | --- | --- |
| Does a proposed Work Unit recovery profile preserve accepted content and relationship changes across engine/holder loss? | H1/H3/H11; no Work Unit realization was tested. | Declare the loss projection; accept content and complete a grant/containment change, interrupt at the claimed boundary, then demonstrate correct denial and actual retained-content use. Keep any test oracle out of recovery. |
| Does a proposed survivor discriminate relevant histories and bind to the recovered view? | H6; independent location or identity can survive without distinguishing anything. | Construct the paired histories first. Compare all recovery observations, then attempt wrong-domain/view substitution and a change between check and use. If observations coincide, stop before building the expensive mechanism. |
| Does the current Crosslink recovery/source-selection path preserve acknowledged work and superseding state under its actual contract? | H9; the incident is historical and the playbook records a later fix. The acknowledgement and hub-publication boundary matters. | In a disposable fixture, record a later issue change, retain an older checkpoint, exercise only the claimed recovery path, and compare required state with declared surviving sources. Do not reproduce it against live work. |
| Can physically separate holders preserve a required joint recovery cut? | H7; J assumes the compatible cut and excludes physical split-holder failures. | Use one coupled transfer and asymmetric loss/restoration at its commitment boundary. Test both `(1,1)` and invariant-valid `(0,0)` as forbidden recovered outcomes for that whole-effect claim. |
| Would a future Processor own any current-state selector, or only recomputable derived outputs? | H10; the substantive Processor contract is not present in this baseline. | First obtain/declare the authoritative dependency contract. Only if it includes a recovered current selector, test jointly rolling back selector and invalidation evidence; otherwise test ordinary applicability separately. |

The unsettled failure coverage and availability tradeoffs are design decisions to
be made explicitly, not missing axioms. If a later proposal promises useful
continuation despite total loss of every distinction that continuation requires,
H1/H3 already reject that promise. Escalate foundational reasoning only if an
actual proposed contract appears to escape the premises while retaining the same
guarantees, or cannot define observational equivalence/whole effect consistently.

**WHY:** the remaining unknowns concern concrete preservation and correspondence,
not a missing semantic distinction. **WHAT:** existing exclusions in A/C/J and
the paired histories above. **HOW CERTAIN:** evidence-based research boundary;
no general architectural change has a demonstrated necessity. **WHAT-NOT-TESTED:**
the proposed future tests, any mechanism choice, or all possible future contracts.

## 10. Propagation boundary

- **Shared/canonical incorporation proposed:** adopt the conditional assurance
  wording and six-field disclosure by reference through P1; clarify only the
  already-promised current-state and durable-resumption claims in P2/P3. Keep
  Kernel-0 semantics and failure coverage unchanged. This document remains a
  research recommendation until explicitly adopted.
- **Work Unit-specific:** sealed confinement during discovery/uncertainty,
  containment/grant reconstruction, accepted contents, engine mediation and the
  particular continuation modes. Qualify W.E/F and F3/T6; a registry reference
  suffices without a new stable concept.
- **Do not generalize:** age into obsolescence, provenance into current authority,
  timestamps into rollback protection, new grants into historical recovery,
  safety-only denial into promised success, or persistence/cache reuse into an
  automatic need for an external service. Require joint cuts only for actual
  coupled dependencies.
- **Suitable for cheaper-model downstream work:** after adoption, bounded
  documentation edits P1–P3 and the local qualification/reference updates; source
  and link audits; extracting a six-field contract from a selected design; and
  constructing the specific fixture tests in §9. Require the stated exclusions
  and acceptance criteria. This review launches no agents and selects no models.
- **Frontier reasoning still required:** none for the information limit or its
  present placement. Escalate only a concrete new semantic counterexample of the
  kind identified in §9. Storage, trust-binding and split-holder claims need
  implementation evidence, not further open-ended foundational generalization.
