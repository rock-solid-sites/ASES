---
title: Architecture Documentation Consolidation Record
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - Documentation Standard
  - Documentation Taxonomy
  - Concepts and Topics Registry

consumed_by:
  - EDASES architecture maintenance
  - Astra reasoning input preparation

related_documents:
  - Astra Reasoning Input Provenance
  - EDASES Execution Engine Roadmap
  - EDASES Authority Ontology
  - EDASES Efficiency Architecture

implements: []
implemented_by: []
supersedes: []
superseded_by: []

last_updated: 2026-09-28
---

# Architecture Documentation Consolidation Record

## Purpose

This record tracks the staged cleanup of EDASES documentation after the Kernel, Work Unit, Phase I, authority, and efficiency discussions materially outpaced the repository's older document graph.

The consolidation is a documentation-graph repair, not a license to rewrite historical reasoning or prematurely promote provisional conclusions to Canonical authority.

## Stage 1 — current project-level working set for Astra

**Status: completed for the first pass.**

Goals:

- make the small project-level architecture set internally coherent enough for frontier reasoning;
- preserve exact versions used by earlier Astra work;
- keep project-critical but unsettled documents explicitly non-authoritative;
- correct active retrieval hazards that would feed Astra obsolete ontology.

Actions completed:

- recorded the original Astra Phase I baseline, output lineage, later branch work, and the exact next Astra packet in `Astra-Reasoning-Input-Provenance.md`;
- clarified Work Unit sealing so engine loss disables affected outward capability use without inherently stopping resource-backed internal computation;
- clarified crash recovery so last-recorded capability attachments remain historical context and require fresh authorized reassessment before reattachment;
- clarified the Orchestrator as the expected primary user-facing LLM role whose authority is exactly what the user currently delegates, while keeping Kernel correctness independent of an active Orchestrator agent;
- reconciled Phase I closure and verification work with the resolved Q1 semantics while preserving the pre-resolution Q1 investigation as a reasoning record;
- created `EDASES Efficiency Architecture` as an Experimental/Derived consolidation of the current efficiency baseline;
- repaired active Concepts Registry entries that pointed at the nonexistent `EDASES Minimal Execution Substrate Architecture` substantive home.

Stage 1 does **not** promote the Authority Ontology, Efficiency Architecture, Phase I closure, or Kernel-0 provisional specifications to Canonical authority.

## Stage 2 — wider filing and drift correction

**Status: pending.**

Scope:

- inspect the broader documentation tree for known current documents filed in the wrong layer or directory;
- reconcile metadata classification with the Documentation Taxonomy;
- correct stale `depends_on`, `consumed_by`, `related_documents`, `supersedes`, and `superseded_by` relationships;
- move documents only when their current purpose is clear;
- preserve Git history and add redirects or lineage metadata where retrieval would otherwise break;
- identify older active-looking documents that should be Deprecated, Archived, Historical, Experimental, or Derived;
- avoid semantic rewriting of historical research records.

Output should be a bounded move/reclassification ledger rather than an opportunistic repository reorganization.

## Stage 3 — deep search for misfiled or miscategorized documentation

**Status: pending.**

This stage is broader than inspecting obvious architecture folders.

Search targets include:

- design records outside the documentation taxonomy;
- current research embedded in historical/addenda locations;
- architecture claims inside operational guides or implementation notes;
- canonical-looking prose without required metadata;
- duplicate substantive homes;
- broken or nonexistent canonical-home references;
- documents whose declared abstraction layer conflicts with what they actually define;
- historical documents that remain upstream dependencies;
- orphaned syntheses, decision records, and review packets;
- generated/compiled material presented as hand-maintained truth;
- repository-level documents that silently redefine canonical concepts.

The goal is to find **latent retrieval errors**, not merely tidy filenames.

## Consolidation rules

1. Preserve historical reasoning as evidence; do not silently modernize it.
2. Distinguish movement from semantic change.
3. Prefer an existing substantive home over creating a new document when the taxonomy permits.
4. Use Canonical authority only for sufficiently stable primary sources of truth.
5. Draft, Experimental, and Derived documents may be project-critical and may be intentionally supplied to Astra.
6. Record exact document versions for frontier reasoning runs.
7. Fix active retrieval hazards before aesthetic filing issues.
8. Do not let repository path alone determine document identity.
9. Treat unresolved contradictions as research questions, not cleanup opportunities.
10. Run mechanical relationship/reference checks after each consolidation stage where tooling permits.


## Stage 2A — obvious root-level `docs/` filing drift

**Status: inventory complete; no moves performed in this substep.**

This pass inspected only files directly under `docs/`. It intentionally did not inspect or move the larger `.design/` corpus.

| Current path | Current apparent role | Candidate classification / destination | Confidence | Reason |
| --- | --- | --- | --- | --- |
| `docs/ORCHESTRATOR.md` | Project-specific operating contract for the Orchestrator and specialist roles | Role/operational guide; likely `docs/roles/` after reconciliation with the current Authority Ontology and orchestration playbook | High that root placement is wrong; medium on exact final form | It defines an operational role contract, contains current deployment details, and currently lacks standard metadata. It should not be confused with the architectural Orchestrator ontology. |
| `docs/SESSION-END.md` | Session handoff procedure/router | Guide or operational convention rather than a Derived “Standard”; candidate relocation with other workflow guides after checking its paired `SESSION-START.md` source | High on classification mismatch; medium on destination | Its body is instructional and task-oriented. The Documentation Taxonomy describes this as Guide-like, while current metadata says `document_type: Standard` and `authority: Derived`. |
| `docs/crosslink-adversarial-review.md` | Crosslink workflow/knowledge guide | Tooling/workflow Guide; should live with Crosslink operational knowledge rather than project-root docs | High | It explicitly identifies itself as a Crosslink knowledge page and documents use of a concrete workflow. |
| `docs/crosslink-subagent-orchestration.md` | Crosslink CLI/workflow guide | Tooling/workflow Guide; should live with Crosslink operational knowledge rather than project-root docs | High | It is an instructional description of kickoff/swarm/sentinel/Task behavior, not project architecture. |
| `docs/final-report-template.md` | Reusable project-completion template | Template/reference support document; candidate dedicated templates location or methodology support location | High that root placement is poor; medium on exact destination | It is neither a substantive project finding nor architecture. A dedicated template category/path may be warranted if other templates exist. |
| `docs/mirror-sync-259-tripn-astro.md` | Historical operational synchronization record for another repo | Historical/implementation record; candidate `docs/historical/` or a scoped historical operations subdirectory | High | It records a completed dated mirror operation and explicitly describes staged state in `tripn-astro`; it should not appear as current project-level guidance. |
| `docs/project-completion-report-crosslink-model-agnostic.md` | Completed project report / retrospective evidence | Research Record or Historical project report; candidate historical/research project-record location | High | It is a dated completion report with findings, model evaluation, and retrospective material. It is useful evidence, not a current root-level specification. |
| `docs/sentinel-model-triage-scope.md` | Completed Crosslink implementation scope/design record | Implementation or Historical implementation record, probably grouped with Crosslink records | High | It documents concrete Rust files/line numbers and an already implemented Sentinel change. It is implementation evidence rather than current project architecture. |

### Root-level hazards identified

1. **Role-name collision:** `docs/ORCHESTRATOR.md` can be retrieved as though it defines the architectural Orchestrator, but it is actually a project-specific operational contract and predates the clarified authority ontology.
2. **Classification mismatch:** `SESSION-END.md` is structurally a guide but declares itself a Derived Standard.
3. **Tooling leakage into project root:** two Crosslink workflow guides and one Sentinel implementation record occupy the same root namespace as project-level documentation.
4. **Historical records look current:** the TripN mirror-sync record and completed Crosslink project report have no path-level indication that they are historical evidence.
5. **Template ambiguity:** the final-report template has no dedicated classification/home.

### Stage 2A disposition

No file has been moved or semantically rewritten yet.

The next bounded operation for these eight files should be a **move/reclassification batch only after dependency/reference checks**. In particular, `ORCHESTRATOR.md` must be reconciled against the current Authority Ontology before it is retained as a current operational role guide; it must not silently redefine Orchestrator authority.


## Stage 2A.2 — `.design/` filing inventory

**Status: inventory complete; no moves performed in this substep.**

This pass inspected every current file directly under `.design/`. The directory is not a single documentation class. It mixes research evidence, raw model review transcripts, historical architecture proposals, implementation designs, swarm plans, experiments, and operational audits.

The classification below is therefore a filing proposal, not a semantic promotion.

### A. Research, review, and evidence records

| Current path | Candidate classification / destination | Confidence | Notes |
| --- | --- | --- | --- |
| `.design/adversarial-reviewers-analysis.md` | Research Synthesis / model-evaluation evidence under `docs/research/` or a model-evaluation subdirectory | High | Completed 2026-06-24 synthesis of reviewer behavior; historical evidence rather than current architecture. |
| `.design/architectural-brief-documentation-process.md` | Historical Research Brief under `docs/research/` or `docs/historical/` | High | Snapshot of an earlier decisional-provenance problem space; useful lineage, not current specification. |
| `.design/architectural-reviews-synthesis.md` | Research Synthesis under `docs/research/syntheses/` | High | Synthesizes multiple adversarial reviews and competing architectures. |
| `.design/capability-schema-validation.md` | Research/Experiment Design under `docs/research/` | High | Already declares `layer: Research`; `.design/` location conflicts with its metadata. |
| `.design/chatgpt-execution-classification.md` | External Review / Research Record under `docs/research/review-inbox/` or dedicated external-review location | High | Declares external, unverified provenance; should not sit beside authoritative designs. |
| `.design/crosslink-dormant-capability-audit.md` | Research Audit / Tooling Evaluation under `docs/research/` | High | Evidence-heavy deployed/source audit of Crosslink capabilities; not a design document. |
| `.design/prior-art-brief.md` | Research Brief under `docs/research/` | High | Already calls itself a prior-art research brief despite `layer: Implementation`; metadata itself likely needs correction. |
| `.design/research-git-notes.md` | Research Record under `docs/research/` | High | Explicit external/prior-art research. |
| `.design/research-hybrid-cache.md` | Research Record / Architecture Research under `docs/research/` | High | Investigates CQRS/event-sourcing pattern and prior art; not implementation design. |
| `.design/tool-to-engine-gap-matrix.md` | Research Advisory under `docs/research/` | High | Already declares `layer: Research`; evaluates current tooling against engine concepts. |

### B. Raw model-review lineage

These files are mostly review payloads/responses rather than maintained specifications. They should remain preserved, but under a review/evidence location rather than `.design/`.

| Current path | Candidate classification / destination | Confidence |
| --- | --- | --- |
| `.design/reframe-chatgpt.md` | Historical external model review / `docs/research/review-inbox/` or historical review archive | High |
| `.design/reframe-claude.md` | Historical external model review / review archive | High |
| `.design/reframe-deepseekpro.md` | Historical external model review / review archive | High |
| `.design/reframe-glm52.md` | Historical external model review / review archive | High |
| `.design/reframe-redirect.md` | Multi-model review/recommendation record / review archive | High |
| `.design/reviews-2.md` | Historical adversarial review bundle / review archive | High |
| `.design/reviews-3.md` | Historical adversarial review bundle / review archive | High |
| `.design/reviews-4.md` | Historical adversarial review bundle / review archive | High |
| `.design/reviews-5-gemini.md` | Historical adversarial review / review archive | High |
| `.design/reviews-5.md` | Historical multi-model review bundle / review archive | High |
| `.design/reviews-6.md` | Historical adversarial review / review archive | High |
| `.design/reviews-7-synthesis-gemini.md` | Historical adversarial review / review archive | High |
| `.design/v7-reviews.md` | Historical adversarial review bundle / review archive | High |

The numbered/reframe files form a recognizable **decisional-provenance architecture review lineage**. They should likely move as one preserved set so chronology is not lost.

### C. Implementation designs, experiments, and execution plans

| Current path | Candidate classification / destination | Confidence | Notes |
| --- | --- | --- | --- |
| `.design/documentation-process-refactor.md` | Historical Implementation Design or Design Record | High | “Final audited” design for a superseded documentation/telemetry architecture; should not appear current merely because it says final. |
| `.design/dual-architecture-orchestration-spec.md` | Historical Architecture/Design Record | High | Explicitly says adversarial-review phase and not ready for selection; belongs with its review lineage. |
| `.design/epic-423-swarm-plan.md` | Historical/Operational Execution Plan | High | Ticket-specific swarm execution plan, not durable architecture. |
| `.design/epic-423-swarm-replan.md` | Historical/Operational Implementation Design | High | Declares `layer: Implementation`; tied to EPIC #423 and its companion plan. |
| `.design/lifecycle-manager-design.md` | Historical or Experimental Implementation Design | High | Concrete agent lifecycle design; depends on old session tooling and predates current Work Unit/authority consolidation. |
| `.design/observer-swarm-v1.1-resilience.md` | Historical/Experimental Implementation Design | High | Swarm hardening design tied to older Observer implementation assumptions; not the current Phase II Observer architecture. |
| `.design/rpc-enforcement-prototype.md` | Experiment Design under `docs/research/` or `docs/implementation/` if that location is introduced | High | Explicitly says it is an experiment, not an architectural commitment. |
| `.design/rtk-guard.md` | Tooling Implementation Design | High | Concrete OpenCode plugin design; useful implementation record and efficiency evidence, not EDASES architecture. |
| `.design/sqlite-native-refactor-proposal.md` | Historical Architecture Proposal | High | Earlier proposal whose guarantees were subsequently attacked by the adjacent review lineage. |
| `.design/v2-guard-rewrite-design.md` | Tooling Implementation Design | High | Concrete guard rewrite for a particular OpenCode/Crosslink generation. |

### Retrieval hazards identified in `.design/`

1. **“Final” and “watertight” historical proposals look current.** In particular, `documentation-process-refactor.md` and the SQLite/provenance proposals can be retrieved as settled architecture even though their own review lineage later falsified major claims.
2. **Raw model reviews are mixed with authored specifications.** A search can return one model's adversarial opinion beside a project design without an obvious authority distinction.
3. **Metadata/path disagreement is common.** Several documents declare `layer: Research` or `layer: Implementation` while living in the generic `.design/` bucket.
4. **Old Execution Engine ontology remains discoverable.** `lifecycle-manager-design.md`, `observer-swarm-v1.1-resilience.md`, `rpc-enforcement-prototype.md`, and `tool-to-engine-gap-matrix.md` encode pre-Kernel-0/Work-Unit-0 assumptions. They remain useful evidence but should not silently define current primitives.
5. **The old decisional-provenance program is overrepresented in search.** More than a dozen files are successive proposals/reviews of the same historical architecture problem. Preserving them as a grouped lineage will reduce retrieval noise without deleting evidence.
6. **Operational plans are mixed with durable knowledge.** EPIC-specific swarm plans should not have the same retrieval status as architecture/research findings.
7. **Useful guard evidence should be retained but re-scoped.** The RTK, V2 guard, Crosslink capability audit, and RPC prototype remain valuable evidence for capability mediation and fail-open/fail-closed distinctions, but are implementation/tooling artifacts rather than authority definitions.

### Stage 2A.2 disposition

No `.design/` file has been moved, renamed, or semantically rewritten.

The safest move sequence is not alphabetical. The next move/reclassification work should proceed in small dependency-checked families:

1. **historical decisional-provenance review lineage** — proposals + numbered/reframe reviews;
2. **EPIC #423 operational designs/plans**;
3. **current-use tooling/guard evidence**;
4. **standalone research briefs/audits**.

Each family should first receive a repository-wide reference check so moves do not create broken dependencies.


## Stage 2B.1a — raw decisional-provenance review archive move

**Status: completed.**

The first move family consists only of raw or near-raw model-review records from the historical decisional-provenance architecture sequence.

Repository code search found no current references by exact filename or `.design/reframe-*` / `.design/reviews-*` path pattern. This check uses GitHub code search and therefore is strongest for the indexed/default branch; no branch-local reference was identified in the inspected current documentation. Because the moved files are preserved byte-for-byte and are historical evidence rather than current dependencies, this family is low risk.

Moved without semantic edits:

- `.design/reframe-chatgpt.md`
- `.design/reframe-claude.md`
- `.design/reframe-deepseekpro.md`
- `.design/reframe-glm52.md`
- `.design/reframe-redirect.md`
- `.design/reviews-2.md`
- `.design/reviews-3.md`
- `.design/reviews-4.md`
- `.design/reviews-5-gemini.md`
- `.design/reviews-5.md`
- `.design/reviews-6.md`
- `.design/reviews-7-synthesis-gemini.md`
- `.design/v7-reviews.md`

Destination:

`docs/historical/decisional-provenance-reviews/`

The historical filenames are retained unchanged so chronology and existing human references remain recognizable.

No authored synthesis, proposal, research brief, implementation design, or current-use tooling record was moved in this substep.


## Stage 2B.1b — authored decisional-provenance lineage archive move

**Status: completed.**

This substep covers the authored synthesis, proposals, and supporting research material that accompanied the raw review sequence archived in Stage 2B.1a.

Primary-source classification check:

- `.design/architectural-reviews-synthesis.md` identifies itself as a synthesis of the historical decisional-provenance architecture review sequence and says it is ready for further review or selection rather than settled project architecture.
- `.design/documentation-process-refactor.md` is an authored implementation/design plan from the earlier decisional-provenance program. Its “Final Production Version” wording is preserved as historical evidence, but the current Documentation Taxonomy does not make that wording Canonical authority.
- `.design/dual-architecture-orchestration-spec.md` explicitly states that it is in adversarial review and “NOT ready for Swarm Selection.”
- `.design/sqlite-native-refactor-proposal.md` explicitly identifies itself as a draft proposal pending review.
- `.design/research-hybrid-cache.md` is supporting architecture research into the Git/event-sourcing/SQLite hybrid used by the same historical design sequence.

Repository code search found no exact-path or exact-basename references to any of these five files in the indexed repository. As in Stage 2B.1a, this is strongest for the indexed/default branch; the continuation tree itself was also inspected before the move. None of the five is a current upstream dependency recorded by the active documentation graph inspected for this consolidation.

Moved without semantic edits:

- `.design/architectural-reviews-synthesis.md`
- `.design/documentation-process-refactor.md`
- `.design/dual-architecture-orchestration-spec.md`
- `.design/sqlite-native-refactor-proposal.md`
- `.design/research-hybrid-cache.md`

Destination:

`docs/historical/decisional-provenance/`

The files are preserved byte-for-byte. No internal status wording, architectural claim, benchmark statement, or historical recommendation was modernized. Their historical classification is established by repository placement and this consolidation ledger, not by rewriting the evidence itself.

This move does not promote any conclusion from the historical decisional-provenance program into current EDASES architecture.


## Stage 2B.2a — EPIC #423 operational plan reference check

**Status: deferred; no move performed.**

Files checked:

- `.design/epic-423-swarm-plan.md`
- `.design/epic-423-swarm-replan.md`

Primary-source findings:

- the plan is explicitly an executable swarm plan for EPIC #423;
- the re-plan declares `layer: Implementation`, `document_type: Design`, `status: Proposed`, and `authority: Derived`, and identifies the plan as its executable companion;
- the pair cross-reference one another and are operational/ticket-scoped rather than project-level architecture;
- repository code search found no exact-basename references to either file in the indexed repository.

The consolidation inventory classified these files as likely Historical/Operational records, but that classification requires evidence that EPIC #423 is no longer active or that the plans were superseded. The GitHub issue endpoint for #423 was unavailable through the current connector, and no accessible closeout or superseding primary source was found in this bounded check.

Therefore no historical move is justified in this substep. The pair remains in place until project-state evidence establishes whether it is active implementation planning or historical execution evidence.


## Stage 2B.3a — RPC enforcement prototype classification

**Status: classified; move deferred.**

File checked:

- `.design/rpc-enforcement-prototype.md`

Primary-source findings:

- metadata declares `layer: Implementation`, `document_type: Experiment Design`, `status: Proposed`, and `authority: Derived`;
- the body explicitly states: “This is an experiment, not an architectural commitment”;
- its success criterion says a successful result would establish only a viable execution-authority substrate, not the final EDASES architecture;
- Git history shows one introduction commit, `f0453d9e4fe2` (2026-08-24), whose commit message identifies it as the “RPC enforcement prototype - v2-integration successor to ases-tools thin CLI [#441]”;
- repository code search found no exact-path, basename, title, or `parent_epic: "#441"` references elsewhere in the indexed repository.

Disposition:

The file is an **experimental Implementation-layer design**, not current architecture and not Canonical authority. However, no primary source found in this bounded check establishes that experiment #441 was completed, abandoned, or superseded, so classifying it as Historical would be unsupported.

The repository currently has no `docs/implementation/` home. Creating a new implementation subtree solely for this file would exceed this atomic filing step and would violate the consolidation rule against opportunistic repository reorganization. Therefore the file remains in `.design/` pending either:

1. evidence establishing historical/superseded status; or
2. a later bounded decision establishing the repository home for active Implementation-layer experiment/design records.

No semantic edit or move was performed.


## Stage 2B.3 — current-use tooling/guard evidence batch

**Status: in progress. Recovery checkpoint.**

Batch scope:

- `.design/rpc-enforcement-prototype.md`
- `.design/rtk-guard.md`
- `.design/v2-guard-rewrite-design.md`
- `.design/crosslink-dormant-capability-audit.md`

The RPC prototype was classified in Stage 2B.3a as an Experimental/Implementation design whose move remains deferred pending either historical-status evidence or an established Implementation-layer home.

This checkpoint records the remaining family before further reference/dependency checks so interrupted work can resume from the exact bounded set without reconstructing scope.
