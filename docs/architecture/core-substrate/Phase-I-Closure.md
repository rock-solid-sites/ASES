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
