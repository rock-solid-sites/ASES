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
