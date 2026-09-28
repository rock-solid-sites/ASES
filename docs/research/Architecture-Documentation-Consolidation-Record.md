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


### Stage 2B.3b — Crosslink dormant-capability audit

**Status: moved as research evidence.**

Primary-source findings:

- `.design/crosslink-dormant-capability-audit.md` identifies itself as “ASES / EDASES Research,” is dated 2026-08-28, and records a deployed/source audit rather than proposing project architecture;
- its evidence is explicitly tied to deployed Crosslink `0.9.0-beta.1+37789b51-dirty` and the then-current source tree, making it a dated Research Record rather than a durable implementation specification;
- repository code search found no exact-basename reference to the file;
- commit `96694b17ec49` on 2026-08-29 is titled `feat(#517): activate dormant crosslink features per audit #505` and directly cites audit #505 in the resulting implementation comments, establishing the audit as upstream research evidence consumed by later implementation.

Moved byte-for-byte:

- `.design/crosslink-dormant-capability-audit.md` → `docs/research/crosslink-dormant-capability-audit.md`

No claim, recommendation, version string, or historical source citation inside the audit was rewritten.


### Stage 2B.3c — tooling/guard family closeout

**Status: batch complete.**

Remaining family findings:

#### `.design/rtk-guard.md`

- The document is an Implementation/Execution design for `.opencode/plugins/rtk-guard.ts`.
- The implementation file still exists at `.opencode/plugins/rtk-guard.ts` and the active `.opencode/opencode.json` explicitly loads `./plugins/rtk-guard.ts` alongside the orchestrator and Crosslink guards.
- Git history shows the design and plugin entered the repository together in the 2026-07-17 pre-consolidation snapshot; no later document supersedes the design by exact path/basename search.

**Disposition:** current-use Implementation design/evidence, not Research and not justified as Historical. No move performed. Its eventual filing depends on establishing a repository home for active Implementation-layer designs.

#### `.design/v2-guard-rewrite-design.md`

- Metadata declares `layer: Implementation`, `document_type: Design`, `status: Draft`, `authority: Derived`, issue `#504`, and branch `feature/v2-guard-rewrite`.
- The file was introduced on 2026-08-28 specifically as the V2 guard rewrite design for #504.
- Current `crosslink-guard.ts` remains active, but its history contains multiple later semantic changes after the design snapshot, including #517, #525, #527/#528/#529-related guard fixes through 2026-08-31.
- No exact-path or basename reference to the design was found in indexed repository code.

The design is therefore a dated Draft/Derived Implementation record whose embedded “current” source observations are no longer safe to treat as current runtime truth. However, no primary source available in this bounded check proves #504 was closed, abandoned, or fully superseded by a specific successor document or implementation.

**Disposition:** leave in place for now; flag as a retrieval hazard, but do not promote, rewrite, or archive without stronger lifecycle evidence. It belongs with the later decision about the home/lifecycle rules for Implementation-layer design records.

#### `.design/rpc-enforcement-prototype.md`

Disposition remains as recorded in Stage 2B.3a: Experimental/Implementation design; move deferred pending historical-status evidence or an established Implementation-layer home.

### Batch result

- **Moved to Research:** 1 file — `crosslink-dormant-capability-audit.md`.
- **Retained pending Implementation-layer filing decision:** 3 files — `rpc-enforcement-prototype.md`, `rtk-guard.md`, `v2-guard-rewrite-design.md`.
- **Semantic rewrites:** none.
- **Unsupported historical promotions:** none.

This batch also establishes a broader filing issue for Stage 2: the Documentation Standard recognizes `Implementation` as an abstraction layer, but this repository currently has no `docs/implementation/` subtree. That structural question should be resolved once enough Implementation-layer records have been classified to justify a repository-level filing decision rather than creating a directory opportunistically for a single document.


## Stage 2B.4 — standalone research/review material batch

**Status: in progress. Recovery checkpoint.**

Batch scope:

- `.design/adversarial-reviewers-analysis.md`
- `.design/architectural-brief-documentation-process.md`
- `.design/capability-schema-validation.md`
- `.design/chatgpt-execution-classification.md`
- `.design/prior-art-brief.md`
- `.design/research-git-notes.md`
- `.design/tool-to-engine-gap-matrix.md`

Goal: determine which are Research Records, Syntheses, Research Designs, External Reviews, or Historical research evidence; move only where the primary-source role is clear. Preserve contents byte-for-byte unless a separate metadata correction is independently justified.


### Stage 2B.4a — clear standalone research/review moves

**Status: completed for six clear files.**

Repository code search found no exact-path/basename references to any file in this sub-batch.

Moved byte-for-byte:

- `.design/adversarial-reviewers-analysis.md` → `docs/research/syntheses/adversarial-reviewers-analysis.md`. Its own header identifies it as ASES Research, type “Analysis, Synthesis,” status Complete.
- `.design/architectural-brief-documentation-process.md` → `docs/historical/decisional-provenance/architectural-brief-documentation-process.md`. Its body is a fresh-reviewer brief for the same documentation/decisional-provenance architecture sequence already archived in Stage 2B.1.
- `.design/capability-schema-validation.md` → `docs/research/capability-schema-validation.md`. Its metadata declares `layer: Research`; its body calls itself a Research Design Document and explicitly says it is not an engine implementation or architecture redesign.
- `.design/chatgpt-execution-classification.md` → `docs/research/review-inbox/chatgpt-execution-classification.md`. Its metadata declares `status: External-Unverified`, `authority: External`, and provenance as an independent ChatGPT review whose source claims require verification. The review-inbox location preserves that authority boundary even though the historical metadata says `layer: Implementation`.
- `.design/research-git-notes.md` → `docs/research/research-git-notes.md`. It is explicitly a web-grounded research record on Git Notes and their decisional-provenance suitability.
- `.design/tool-to-engine-gap-matrix.md` → `docs/research/tool-to-engine-gap-matrix.md`. Its metadata declares `layer: Research`, `document_type: Advisory`, `status: Draft`, and `authority: Derived`; the body explicitly says it is advisory only and does not make the build-vs-buy decision.

No internal content or metadata was rewritten in this substep. Metadata contradictions preserved in historical/external material remain visible rather than being silently normalized.


### Stage 2B.4b — EPIC #423 prior-art brief classification correction

**Status: completed.**

`.design/prior-art-brief.md` contained an internal classification contradiction:

- title: “Prior Art Brief - EPIC 423 Support Systems”;
- `document_type: Research Brief`;
- purpose: “Operator-conducted external prior-art scan”;
- body: “This brief exists so the OPERATOR can check existing tools before we build”;
- introduction commit `7f41a08ea477` is titled `docs(design): prior-art research brief for EPIC 423 support systems - operator-conducted external scan [#423][#441]`;
- but metadata declared `layer: Implementation`.

Under the canonical Documentation Taxonomy, a prior-art investigation that gathers external evidence before implementation is Research-layer material. No primary source found in this check supports the Implementation-layer classification.

Action:

- moved `.design/prior-art-brief.md` → `docs/research/prior-art-brief.md`;
- corrected only the contradictory metadata field from `layer: Implementation` to `layer: Research`;
- preserved all research content, status, authority, parent-epic, and purpose fields unchanged.

### Stage 2B.4 batch result

- **Moved to Research / Research Synthesis / Review Inbox:** 6 files.
- **Moved to Historical decisional-provenance lineage:** 1 file.
- **Metadata correction:** 1 field in `prior-art-brief.md` (`Implementation` → `Research`), directly supported by its title, document type, purpose, body, commit provenance, and the Documentation Taxonomy.
- **Files left unresolved in this batch:** none.

The standalone research/review family is complete.


## Stage 2B.5 — remaining implementation/operational design batch

**Status: in progress. Recovery checkpoint.**

Current `.design/` contains exactly seven files:

- `.design/epic-423-swarm-plan.md`
- `.design/epic-423-swarm-replan.md`
- `.design/lifecycle-manager-design.md`
- `.design/observer-swarm-v1.1-resilience.md`
- `.design/rpc-enforcement-prototype.md`
- `.design/rtk-guard.md`
- `.design/v2-guard-rewrite-design.md`

Five already have recorded dispositions or deferrals from Stages 2B.2–2B.3. This batch therefore focuses first on the two unclassified records:

- `.design/lifecycle-manager-design.md`
- `.design/observer-swarm-v1.1-resilience.md`

After those are resolved, the batch will decide whether enough evidence now exists to establish a common home/lifecycle rule for the remaining active or unresolved Implementation-layer records without guessing.


### Stage 2B.5a — lifecycle-manager supersession filing

**Status: completed.**

Primary-source lineage:

- `.design/lifecycle-manager-design.md` is a Proposed/Derived Implementation design introduced for EPIC #423 on 2026-08-24.
- `.design/observer-swarm-v1.1-resilience.md` (2026-08-27) explicitly lists the lifecycle-manager design under `supersedes` as **partially superseded**, retaining only the lifecycle-state semantics, post-transition action-table shape, and SC1–SC5 validation intent while replacing its resilience, filing, and traceability assumptions.
- `specifications/observer-conformance-suite.md` (2026-08-30) independently repeats that status: the lifecycle-manager design is “superseded in part; lifecycle-semantics baseline,” while the Observer v1.1 design is the behavioural contract and `scripts/observer/observer.sh` the implementation.

Action:

- moved `.design/lifecycle-manager-design.md` byte-for-byte to `docs/historical/lifecycle-manager-design.md`;
- updated the four verified path references in the current Observer v1.1 behavioural contract to the historical location;
- updated the verified path reference in the Observer conformance suite to the historical location.

The GitHub connector provides default-branch code search only, not branch-scoped search. These reference repairs therefore cover the branch-local primary consumers directly verified in this consolidation; the move is not represented as an exhaustive branch-wide grep.

No historical content was rewritten.

### Observer v1.1 disposition

`.design/observer-swarm-v1.1-resilience.md` remains a Draft/Derived Implementation design rather than a historical record. The 2026-08-30 conformance suite explicitly treats it as the behavioural contract, records `scripts/observer/observer.sh` as the implementation, and grades portions of the design as implemented/verified and other portions as still open. No later superseding primary source was found in this bounded check.

Its filing therefore remains coupled to the unresolved repository-home question for active Implementation-layer designs; no move is performed here.


### Stage 2B.5b — branch-local reference scan checkpoint 1

**Status: 30 live documentation files scanned.**

Completed exact-path checks across:

- all 10 files under `docs/architecture/` and `docs/architecture/core-substrate/`;
- 20 current top-level Research documents under `docs/research/`.

Targets checked:

- `.design/epic-423-swarm-plan.md`
- `.design/epic-423-swarm-replan.md`
- `.design/observer-swarm-v1.1-resilience.md`
- `.design/rpc-enforcement-prototype.md`
- `.design/rtk-guard.md`
- `.design/v2-guard-rewrite-design.md`

Result:

- one branch-local reference found: `docs/research/capability-schema-validation.md` → `.design/observer-swarm-v1.1-resilience.md`;
- no references to the other five targets were found in these 30 files.

Two earlier oversized scan attempts exceeded the connector's per-call tool limit and are explicitly excluded from evidence. The reliable scan unit is now 10 files per call.


### Stage 2B.5c — branch-local reference scan checkpoint 2

**Status: 20 additional files scanned; 50 total in reliable scan.**

This tranche covered:

- `specifications/observer-conformance-suite.md` and the other files under `specifications/`;
- the main research registry documents and ten model-feedback registry records.

Result:

- `specifications/observer-conformance-suite.md` references `.design/observer-swarm-v1.1-resilience.md` as its behavioural contract;
- no references to the other five remaining target paths were found in this tranche.

Cumulative reliable scan results after 50 files:

- Observer v1.1 has two confirmed live consumers so far: `docs/research/capability-schema-validation.md` and `specifications/observer-conformance-suite.md`;
- no branch-local exact-path reference has yet been found for the EPIC #423 plan/replan pair, RPC enforcement prototype, RTK guard design, or V2 guard rewrite design.


### Stage 2B.5d — branch-local reference scan checkpoint 3

**Status: 26 additional operational/canonical files scanned; 76 total in reliable scan.**

This tranche covered every textual file under:

- `.crosslink/knowledge/`;
- root-level `docs/`;
- `docs/methodology/`;
- `docs/requirements/`;
- `docs/roles/`;
- `docs/standards/`.

Result: no additional exact-path references to any of the six remaining `.design/` targets.

Cumulative confirmed references remain:

- `docs/research/capability-schema-validation.md` → `.design/observer-swarm-v1.1-resilience.md`;
- `specifications/observer-conformance-suite.md` → `.design/observer-swarm-v1.1-resilience.md`.

No confirmed branch-local references have been found for the EPIC #423 plan/replan pair, RPC enforcement prototype, RTK guard design, or V2 guard rewrite design in the 76 reliably scanned live documentation/knowledge files.


### Stage 2B.5e — branch-local reference scan checkpoint 4

**Status: 50 additional high-value research/proposal documents scanned; 126 total in reliable scan.**

This tranche covered:

- 10 capability-schema-validation research reports/READMEs;
- 20 execution-engine UI reports and the synthesis;
- 20 execution-engine proposal/review/research-classification documents under `to-file/`.

Generated measurement JSON, schemas, and corpus fixtures were excluded because they are data artifacts rather than documentation consumers; this exclusion is explicit rather than treated as a successful scan.

Result: no additional exact-path references to any of the six remaining `.design/` targets.

Cumulative confirmed references remain limited to the two Observer v1.1 consumers already recorded.


### Stage 2B.5f — implementation/configuration reference scan checkpoint

**Status: 21 implementation/configuration files scanned; 147 total files in reliable exact-path scan.**

This tranche covered:

- `.opencode/` agent/configuration/plugin/design files relevant to guards;
- `.crosslink/hook-config.json`, sandbox/wrapper support files;
- liveness and Observer scripts/tests;
- `tools/kickoff-notify.py`.

Result: no exact-path references to any of the six remaining `.design/` targets.

Additional filing evidence discovered during the tranche:

- `.opencode/design/rtk-guard-plugin-design.md` declares **Canonical Location: `.opencode/design/rtk-guard-plugin-design.md`** and targets `.opencode/plugins/rtk-guard.ts`;
- `.opencode/design/rtk-guard-final-synthesis.md` declares itself **Canonical — to be implemented** and targets the same plugin;
- therefore `.design/rtk-guard.md` must be evaluated as a possible duplicate/superseded implementation design rather than automatically moved into a new generic Implementation directory.

The archived `docs/research/Proposed Implementation Layer - Decision Record.md` was also inspected. Its own status note says issue #341 superseded its conclusion, so it is not used as authority for creating a new `docs/implementation/` subtree.


### Stage 2B.5g — RTK guard duplicate/supersession resolution

**Status: completed.**

`.design/rtk-guard.md` is not the current RTK implementation design:

- `.opencode/design/rtk-guard-plugin-design.md` existed in the same 2026-07-17 snapshot and explicitly declares its canonical location as `.opencode/design/rtk-guard-plugin-design.md`, targeting `.opencode/plugins/rtk-guard.ts`;
- `.opencode/design/rtk-guard-final-synthesis.md` likewise existed in that snapshot, declares `Status: Canonical — to be implemented`, and targets the same plugin;
- the generic `.design/rtk-guard.md` remained `Status: Proposed` and materially conflicts with the final synthesis by recommending a static-pattern fallback;
- the implemented `.opencode/plugins/rtk-guard.ts` follows the final synthesis instead: live `rtk rewrite`, a validated v1 allowlist, a 15 ms latency gate, and fail-to-`no-op` behavior;
- commit `c66fd8beaa3b` in August did not promote or re-author the generic design; it only repaired its companion research-analysis path during the harness-evaluation relocation;
- the completed reliable exact-path scan found no consumer of `.design/rtk-guard.md` in the 147 live documentation/configuration/implementation files checked.

Action:

- moved `.design/rtk-guard.md` byte-for-byte to `docs/historical/rtk-guard.md`;
- retained the canonical RTK design/synthesis beside the implementation under `.opencode/design/`;
- no live references required repair.

This removes a conflicting Proposed design from the active-looking generic `.design/` surface without rewriting its historical content.


### Stage 2B.5h — remaining `.design/` disposition

**Status: remaining design batch complete.**

The canonical Documentation Standard recognizes `Implementation` as an abstraction layer but explicitly states that repository location should not determine document identity. Neither the Standard nor the Taxonomy mandates a `docs/implementation/` directory. Creating one solely to empty `.design/` would therefore be an aesthetic repository reorganization rather than a source-backed filing correction.

After the completed lineage checks and a reliable exact-path scan of 147 live documentation/configuration/implementation files, `.design/` contains five records:

1. `epic-423-swarm-plan.md` — operational Implementation plan. Historical/closed status not established; retained.
2. `epic-423-swarm-replan.md` — Proposed/Derived Implementation replan paired with the plan. Historical/closed status not established; retained.
3. `observer-swarm-v1.1-resilience.md` — Draft/Derived Implementation design. A later conformance suite explicitly treats it as the behavioural contract and records mixed implemented/open status; retained as active design evidence.
4. `rpc-enforcement-prototype.md` — Proposed/Derived Experimental Implementation design. Explicitly not an architectural commitment; completion/abandonment/supersession not established; retained.
5. `v2-guard-rewrite-design.md` — Draft/Derived Implementation design. Later guard implementation changed after its snapshot, making it a retrieval hazard, but no primary source establishes closure or a specific superseding design; retained with that warning.

Files removed from the active-looking `.design/` surface during this stage were only those with positive evidence for another classification/home: historical decisional-provenance lineage, Research records/syntheses/reviews, the superseded lifecycle-manager design, and the superseded generic RTK proposal.

**No new `docs/implementation/` subtree is created.** The five retained files are intentional exceptions pending lifecycle evidence or a future canonical filing rule for implementation design records.

This closes the `.design/` portion of Stage 2. Stage 2 itself remains open because the previously inventoried root-level `docs/` drift family still requires disposition.


## Stage 2C.1 — root-level completed records

**Status: completed.**

The Documentation Taxonomy restricts top-level repository documents to repository entry/navigation roles. Three root-level `docs/` files are instead bounded records of completed past work:

- `mirror-sync-259-tripn-astro.md` — one-off mirror/staging correction record dated 2026-08-08;
- `project-completion-report-crosslink-model-agnostic.md` — completion report for the 2026-07-11 Crosslink model-agnostic implementation session;
- `sentinel-model-triage-scope.md` — implementation scope marked “Implemented (2026-07-11),” with history limited to the model-agnostic feature landing/update.

Indexed repository search found no exact-path or basename consumers for any of the three.

Moved byte-for-byte:

- `docs/mirror-sync-259-tripn-astro.md` → `docs/historical/mirror-sync-259-tripn-astro.md`
- `docs/project-completion-report-crosslink-model-agnostic.md` → `docs/historical/project-completion-report-crosslink-model-agnostic.md`
- `docs/sentinel-model-triage-scope.md` → `docs/historical/sentinel-model-triage-scope.md`

No content was modernized or rewritten.


## Stage 2C.2 — current root utilities disposition

**Status: classified for deeper review; no unsafe path moves.**

Five non-entry documents remain at root `docs/` after the completed-record archival:

- `docs/ORCHESTRATOR.md`
- `docs/SESSION-END.md`
- `docs/crosslink-adversarial-review.md`
- `docs/crosslink-subagent-orchestration.md`
- `docs/final-report-template.md`

The Taxonomy says top-level repository documents are entry/navigation documents, so these paths are not ideal. However, the canonical Documentation Standard also says location does not determine identity, and Stage 2 forbids opportunistic semantic rewrites or unsourced directory schemes.

Disposition by file:

1. **`ORCHESTRATOR.md` — retained.** Current operational role/permission contract, but it mixes role semantics with OpenCode/Crosslink deployment detail and its name collides with the architectural Orchestrator concept. Moving or reclassifying it safely requires a full consumer/reference rewrite and likely a semantic split between role doctrine and tooling realization.
2. **`SESSION-END.md` — retained.** Existing metadata (`layer: Research`, `document_type: Standard`, `authority: Derived`) conflicts with its body, which describes an operational routing convention and provisional Crosslink mechanism. Correcting this is a semantic classification task, not a path-only cleanup.
3. **`crosslink-adversarial-review.md` — retained.** Explicitly a Crosslink workflow/review guide. It contains tool/version/model-specific operational claims whose currentness must be checked before declaring a durable guide home.
4. **`crosslink-subagent-orchestration.md` — retained.** Explicitly a Crosslink workflow/orchestration guide. It likewise contains deployment-specific CLI/default-model/permission claims that require currentness validation before refiling.
5. **`final-report-template.md` — retained.** Reusable template rather than repository entry point, but the current canonical Taxonomy does not define a Template category or repository home. Creating `docs/templates/` solely for this file would be an unsourced structural decision.

### Search limitation confirmed

GitHub indexed code search returned zero results for all five files, including `docs/ORCHESTRATOR.md`. That result is known false-negative evidence because `docs/research/capability-schema-validation.md` on this branch directly references `docs/ORCHESTRATOR.md`. Indexed search is therefore not used to justify moves for this family.

These five files are passed into Stage 3 as **retrieval/currentness hazards requiring deeper semantic/reference investigation**, rather than being moved speculatively.

## Stage 2 completion

**Stage 2 is complete.**

Completed outcomes include:

- historical decisional-provenance review and authored-design lineage separated from active design surfaces;
- research, synthesis, external-review, and advisory records moved from `.design/` into Research-appropriate homes;
- completed/superseded implementation records archived only where primary-source evidence established that status;
- the generic RTK proposal removed from active surfaces after canonical RTK design/synthesis plus implementation evidence established supersession;
- root-level completed operation/implementation records moved to Historical;
- unresolved active Implementation designs retained rather than forced into an invented `docs/implementation/` scheme;
- current root utilities explicitly classified as Stage 3 hazards rather than silently rewritten.

Stage 3 now begins from a bounded hazard set plus the deeper-search categories already defined above: misplaced design records outside obvious folders, current research under historical/addenda locations, architecture claims in operational notes, canonical-looking prose without metadata, duplicate homes, broken canonical references, abstraction conflicts, historical upstream dependencies, orphaned syntheses/reviews, generated truth masquerading as maintained truth, and repository-level documents redefining canonical concepts.


## Stage 3.1 — historical-upstream dependency search

**Status: in progress. Recovery checkpoint 1.**

Stage 3 begins with the highest-risk latent retrieval error defined by the Taxonomy: historical documents acting as upstream dependencies.

Inventory:

- `docs/historical/` currently contains 28 Markdown records, including decisional-provenance review/design lineage, superseded implementation designs, completed operation/project records, and legacy skills.

Completed first scan tranche:

- all 10 current architecture/core-substrate documents;
- current methodology, requirements, role, standards documents, plus `docs/ORCHESTRATOR.md` (10 files).

Search condition: exact occurrence of `docs/historical/` in current document content/frontmatter.

Result: **0 historical-path references in 20 high-level current documents.** No forbidden Historical → current upstream dependency was found in this tranche.

This is a bounded string-level dependency check; it does not yet rule out references by bare title/basename or copied historical content without a path. Those are later Stage 3 checks.


### Stage 3.1 checkpoint 2 — current Research/conformance

**Status: 20 additional current documents scanned; 40 total in Stage 3.1.**

Result:

- 19 documents contain no `docs/historical/` path reference;
- `specifications/observer-conformance-suite.md` contains one historical path: `docs/historical/lifecycle-manager-design.md`.

That reference is **not an upstream dependency**. It appears under `related_documents`, not `depends_on`, and is explicitly annotated `superseded in part; lifecycle-semantics baseline`. This is an intentional historical lineage citation and does not violate the Taxonomy rule that Historical documents must not become upstream dependencies.

No forbidden historical upstream dependency has been found in the first 40 current high-value documents checked.


### Stage 3.1 checkpoint 3 — registries/currentness/evaluation material

**Status: 30 additional documents scanned; 70 total in Stage 3.1.**

This tranche covered currentness, evaluation-framework/harness-evaluation material, read-only/methodology research, registry documents, model-feedback records, and the AI Evaluation Protocol.

One historical citation was found:

- `docs/research/registry/Failure-Matrix.md` cites `docs/historical/` under **Secondary Evidence (Historical)** as evidence of earlier role-boundary/fallback/context-corruption patterns.

This is not an upstream dependency. The file's frontmatter `depends_on` contains only the current AI Capability Registry Specification and Agent Orchestration Playbook; historical material is explicitly evidence provenance in the body.

Result: **no forbidden Historical → current upstream dependency found in 70 current documents checked so far.**


### Stage 3.1 checkpoint 4 — maintained research subtrees

**Status: 37 additional maintained Research documents scanned; 107 total in Stage 3.1.**

Covered in full:

- `docs/research/crosslink-gates/`
- `docs/research/pre-build-compilation/`
- `docs/research/prompting/`
- maintained retrospective phase/topic documents
- `docs/research/review-inbox/`
- `docs/research/sections/`
- `docs/research/selection-rationale/`
- `docs/research/structural-change/`
- `docs/research/syntheses/`
- `docs/research/work-unit-0/`

Result: **0 occurrences of `docs/historical/` in all 37 documents.**

Cumulative Stage 3.1 result remains: no forbidden Historical → current upstream dependency found. The only historical citations found so far are explicit lineage/evidence references, not `depends_on` relationships.


### Stage 3.1 checkpoint 5 — Kernel-0 anchor documents

**Status: 3 additional current documents scanned; 110 total in Stage 3.1.**

Checked:

- `docs/research/kernel-0/README.md`
- `docs/research/kernel-0/Kernel-0-Evidence-Packet.md`
- `docs/research/kernel-0/Kernel-0-Reasoning-Phase-Result.md`

Search condition: exact occurrence of `docs/historical/`.

Result: **0 historical-path references in all three documents.**

Cumulative Stage 3.1 result remains unchanged: no forbidden Historical → current upstream dependency found. Existing historical citations discovered in earlier checkpoints are explicit lineage/evidence references, not `depends_on` relationships.


### Stage 3.1 checkpoint 6 — remaining Kernel-0 reasoning documents

**Status: 16 additional current documents scanned; 126 total in Stage 3.1.**

Covered all remaining non-review Markdown documents directly under `docs/research/kernel-0/`.

Search condition: exact occurrence of `docs/historical/`.

Result: **0 historical-path references in all 16 documents.**

Cumulative Stage 3.1 result remains unchanged: no forbidden Historical → current upstream dependency has been found. The only historical references found in the 126 current documents checked are explicit lineage/evidence citations, not `depends_on` relationships.


## Stage 3.2 — canonical-looking prose without complete metadata

### Stage 3.2 checkpoint 1 — high-level current-document inventory

**Status: 29 high-level current documents inspected. No edits performed.**

Method: inspect the opening 80 lines of each file for YAML frontmatter and the field names required by the canonical Documentation Standard. This is an inventory pass only: a missing field-name result is a retrieval hazard to inspect, not automatic authority to synthesize metadata.

Coverage:

- all 10 current Architecture/core-substrate documents;
- methodology, requirements, role, and Standards documents;
- the five retained root-level `docs/` utilities;
- all three files under `specifications/`.

#### Files with no YAML frontmatter at the document start

Seven high-level documents currently present authoritative-looking prose without a metadata header:

- `docs/standards/Documentation Standard.md`
- `docs/ORCHESTRATOR.md`
- `docs/crosslink-adversarial-review.md`
- `docs/crosslink-subagent-orchestration.md`
- `docs/final-report-template.md`
- `specifications/Adverarial Test Suite Reviews:.md`
- `specifications/Hospitality Management Suite Specification.md`

The Documentation Standard itself is therefore part of the metadata-conformance hazard set; field names appearing in its explanatory body must not be mistaken for document metadata.

#### Frontmatter present but required-field names incomplete in the opening metadata region

Notable cases:

- `docs/architecture/Execution Engine Vision.md` — lacks field names for `consumed_by`, `implements`, `implemented_by`, and `superseded_by` in the inspected header region.
- older methodology/core-prompt documents generally lack some combination of `implements`, `implemented_by`, `supersedes`, and/or `superseded_by`.
- `docs/roles/Ontology-Reviewer.md` has frontmatter but lacks most of the canonical identity/relationship fields, including `program`, `layer`, `document_type`, `canonical_repository`, and dependency/consumer/relationship fields.
- `docs/standards/Canonical Terminology.md`, `Concept - Levels of Abstraction.md`, and `Documentation Taxonomy.md` lack several relationship fields and `last_updated` in the inspected header region.
- `docs/SESSION-END.md` lacks several implementation/supersession relationship fields.
- `specifications/observer-conformance-suite.md` is nearly complete but lacks an `implemented_by` field name in the inspected header region.

By contrast, the newer EDASES architecture/core-substrate documents are largely fully populated under the current metadata schema.

### Interpretation

This confirms a Stage 3 retrieval hazard rather than a blanket repair instruction: metadata completeness correlates strongly with document generation era, while some high-authority older documents predate the current schema entirely. The next step should distinguish:

1. documents that should receive mechanically obvious metadata completion;
2. documents whose classification/authority must be resolved before metadata can be authored safely;
3. templates/specifications that may need a taxonomy/home decision rather than fabricated canonical metadata.

No metadata was invented or normalized in this checkpoint.

### Turn workload note

This turn inspected **45 documents total**: 16 Stage 3.1 Kernel-0 documents plus 29 Stage 3.2 high-level documents. It completed without the oversized scan pattern used in the prior failed turn.


### Stage 3.2 checkpoint 2 — current Research metadata inventory

**Status: 45 additional current Research documents inspected. No source-document edits performed.**

Method: inspect the opening metadata region for YAML frontmatter and the field names required by the canonical Documentation Standard. Missing field names are inventory signals only; this pass does not infer empty relationships or fabricate metadata.

#### Broad pattern

Most current Research documents in this tranche already have coherent identity metadata (`title`, `program`, `layer`, `document_type`, `status`, `authority`) and are missing mainly relationship fields such as `implements`, `implemented_by`, and sometimes `supersedes` / `superseded_by`. This strongly suggests schema-era drift rather than wholesale classification failure for the majority of the Research tree.

#### No YAML frontmatter at document start

Five inspected Research documents have no metadata header at all:

- `docs/research/ases-stage3-crossref.md`
- `docs/research/harness-evaluations/Microsoft-AutoGen.md.trace.md`
- `docs/research/harness-evaluations/_template.md`
- `docs/research/hms-postmortem-claims-assessment.md`
- `docs/research/other-stage3-crossref.md`
- `docs/research/research-git-notes.md`

(There are six files in this list; the classification is based on the actual inspected results, not the heading count.)

These require document-purpose classification before metadata can be authored safely. In particular, the trace file and template may not belong to the same metadata contract as maintained Research records.

#### Materially incomplete identity/relationship metadata

Notable cases requiring deeper inspection rather than mechanical empty-field insertion:

- `docs/research/pre-build-compilation/Strategy-to-Builder Integration Packet Method - Derivation.md` — identity metadata exists, but all dependency/consumer/implementation/supersession relationships are absent.
- `docs/research/prior-art-brief.md` — after its corrected Research-layer classification, it still lacks most repository/dependency/consumer/relationship fields and `last_updated`.
- `docs/research/prompting/Ontological Connection to Review Skill.md` — identity present, relationship graph largely absent.
- `docs/research/sections/source-3-atlas.md` — has frontmatter delimiters but lacks almost all canonical identity and relationship fields; this is effectively a metadata-empty source record.
- `docs/research/sections/source-5-paper-28802.md` — identity is partial and most relationship fields are absent.

#### Mostly relationship-only gaps

The following families are generally classified and only lack some current-schema relationship fields:

- `docs/research/crosslink-gates/`
- failure/handoff analyses
- maintained harness evaluations
- read-only methodology research
- regression/epistemic-validation research
- retrospective phase/topic documents
- several source-section and selection-rationale records

The repeated absence of `implements` / `implemented_by` across Research material may be semantically appropriate for some documents, but the Standard currently requires the fields. Whether the correct representation is an explicit empty value, `none`, or omission-by-document-type must be resolved from the Standard/taxonomy contract rather than guessed file-by-file.

### Stage 3.2 cumulative position

The metadata hazard is now clearly two problems:

1. **classification/identity gaps** — a minority of documents need semantic review before any metadata is written;
2. **schema-conformance gaps** — a much larger set appears correctly classified but predates or incompletely implements the current relationship-field schema.

The next useful step is therefore to inspect the Documentation Standard's required-field semantics and existing fully compliant documents to determine whether mechanically adding explicit empty relationship values is permitted. If so, a large safe normalization batch becomes possible; if not, the Standard itself needs clarification before repository-wide repair.

### Turn workload

This turn inspected **45 Research documents** and completed without streaming/tool-limit failure.


### Stage 3.2 checkpoint 3 — metadata contract resolution

**Status: one mechanically safe normalization class established.**

Primary-source basis:

- the canonical Documentation Standard's metadata example includes explicit relationship fields even when empty;
- the Standard defines `implements` as an Implementation-document relationship and states: **“Research documents should normally leave this empty”**;
- the Standard defines `implemented_by` for Methodology and Requirements documents;
- current fully populated Derived/Research and Derived/Architecture exemplars encode non-applicable relationships as empty arrays, e.g. `implements: []` and `implemented_by: []`.

Safe normalization rule for this stage:

> For a document that already has structured frontmatter and explicitly declares `layer: Research`, a missing `implements` and/or `implemented_by` field may be added as an explicit empty array without inventing a relationship.

This rule does **not** authorize inference of `depends_on`, `consumed_by`, `related_documents`, `supersedes`, `superseded_by`, identity, status, authority, or classification. Those remain evidence-dependent.

The Standard's wording (“Every canonical document should begin with structured metadata”) is narrower than a universal all-document mandate. Therefore this consolidation will not automatically force complete canonical metadata onto External/Generated/trace/template records merely because they live under `docs/`.


### Stage 3.2 checkpoint 4a — safe Research normalization, Crosslink-gates/failure tranche

**Status: 6 documents normalized.**

Applied only the checkpoint-3 rule: existing `layer: Research` frontmatter received missing `implements: []` and/or `implemented_by: []`. No other metadata or body content changed.

- `docs/research/crosslink-gates/evidence-based-gates.md`
- `docs/research/crosslink-gates/gates-issues.md`
- `docs/research/crosslink-gates/gates-verified-facts.md`
- `docs/research/crosslink-gates/server-crash-postmortem.md`
- `docs/research/crosslink-gates/updated-evidence-based-gates.md`
- `docs/research/failed-conversation.md`


### Stage 3.2 checkpoint 4b — safe Research normalization, evaluation/method tranche

**Status: 9 documents normalized; 0 skipped.**

Applied only the checkpoint-3 empty `implements` / `implemented_by` rule to existing `layer: Research` frontmatter.

Edited:
- `docs/research/frameworks/Evaluation Framework.md`
- `docs/research/handoff-failure-analysis.md`
- `docs/research/harness-evaluations/2026-07-12-rtk-opencode-gap-analysis.md`
- `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`
- `docs/research/harness-evaluations/Microsoft-AutoGen.md`
- `docs/research/pre-build-compilation/Strategy-to-Builder Integration Packet Method - Derivation.md`
- `docs/research/prior-art-brief.md`
- `docs/research/prompting/Ontological Connection to Review Skill.md`
- `docs/research/protocols/AI Evaluation Protocol.md`

Skipped (not eligible or already complete):



### Stage 3.2 checkpoint 4c — safe Research normalization, read-only/retrospective tranche

**Status: 9 documents normalized; 0 skipped.**

Applied only the checkpoint-3 empty `implements` / `implemented_by` rule.

Edited:
- `docs/research/read-only-boundary-as-methodology.md`
- `docs/research/read-only-role-crosslink-allowlist.md`
- `docs/research/regression-testing-orchestrator-compliance.md`
- `docs/research/research-addendum-epistemic-validation.md`
- `docs/research/retrospectives/phases/Phase 1.md`
- `docs/research/retrospectives/phases/Phase 2.md`
- `docs/research/retrospectives/phases/Phase 3.md`
- `docs/research/retrospectives/phases/Phase 4.md`
- `docs/research/retrospectives/phases/Phase 5.md`

Skipped:



### Stage 3.2 checkpoint 4d — safe Research normalization, retrospective-topic tranche

**Status: 9 documents normalized; 0 skipped.**

Applied only the checkpoint-3 empty `implements` / `implemented_by` rule.

Edited:
- `docs/research/retrospectives/topics/EDASES-topic-Containers-and-Environment.md`
- `docs/research/retrospectives/topics/EDASES-topic-Git-Based-Engineering-Systems.md`
- `docs/research/retrospectives/topics/EDASES-topic-Harness-Evaluation.md`
- `docs/research/retrospectives/topics/EDASES-topic-Memory-Research.md`
- `docs/research/retrospectives/topics/EDASES-topic-Methodology-Research.md`
- `docs/research/retrospectives/topics/EDASES-topic-Model-Capability-16-Review-Wave.md`
- `docs/research/retrospectives/topics/EDASES-topic-UI-design.md`
- `docs/research/retrospectives/topics/EDASES-topic-microVMs.md`
- `docs/research/selection-rationale/2026-06-22-microsoft-autogen.md`

Skipped:



### Stage 3.2 checkpoint 4e — safe Research normalization, session/audit tranche

**Status: 3 documents normalized; 6 skipped.**

Applied only the checkpoint-3 empty `implements` / `implemented_by` rule.

Edited:
- `docs/research/selection-rationale/2026-06-23-microsoft-agent-framework.md`
- `docs/research/session-audit-plan.md`
- `docs/research/session-recovery-after-crash.md`

Skipped:
- `docs/research/selection-rationale/_template.md`
- `docs/research/session-audit-stage2-summary.md`
- `docs/research/session-audit-stage3-summary.md`
- `docs/research/session-audit-stage4-summary.md`
- `docs/research/stage4-orphaned-audit.md`
- `docs/research/stage4-partial-audit.md`
