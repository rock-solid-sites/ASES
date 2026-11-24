---
title: ASES Documentation Navigation and Authority Index
version: 1.0.1
program: ASES
layer: Methodology
document_type: Guide
status: Active
authority: Derived
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
related_documents:
  - docs/architecture/Task-Scoped Information Architecture Decision 2026-11-21.md
last_updated: 2026-11-24
---

# ASES documentation: current sources, history and status

**Use this page as a human navigation index, not as an instruction to load every document.** ASES tasks select information at the point of use, as defined by the [canonical Task-Scoped Information and Handoff Method](methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md). Source authority is established by current metadata, owner and decisions, **not** by a filename, repository location, discoverability, or a generated graph.

## Current governing sources

| Scope | Source | Governs |
| --- | --- | --- |
| Documentation metadata | [Documentation Standard](standards/Documentation%20Standard.md) and [Documentation Taxonomy](standards/Documentation%20Taxonomy.md) | Authority, classification, relationship metadata |
| ASES coordination | [Task-Scoped Information and Handoff Method](methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) | Current source admission, effective task views, evidence/provenance |
| Architecture decision | [Accepted Task-Scoped Information ADR](architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md) | Agreed format-independent choices and non-goals |
| Bounded builds | [ASES Bounded Project Build Method](methodology/ASES%20Bounded%20Project%20Build%20Method.md) | Applied only when an Implementation Packet is genuinely compiled |
| Implementation choice | [Realization and Assurance Selection Method](methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md) | Requirements-first selection, language constraints, bounded upstream-reuse exception |
| State modeling | [State-Model Applicability and Reuse Method](methodology/State-Model%20Applicability%20and%20Reuse%20Method.md) | Task-specific model suitability; verify separately adopted VSDD sources |
| Upstream customization | [Software Customization and Upstream Compatibility Method](methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md) | Preserve upstream compatibility, use the smallest supported local difference |
| Operational agent tasks | [Current skills index](../skills/current/README.md) | Selectively retrieved task-specific prompting, orchestration, launch and review instructions |
| Execution authorization | [Current agent-launch skill](../skills/current/agent-launch/SKILL.md) | Exact provider/model/account/funding route; no unauthorized fallback |
| Research evidence | [Agent information topology research](../research/agent-information-topology/greenfield-task-context/README.md) | Accepted decision's evidence; remains non-normative |

Other documents under `docs/methodology/`, `docs/standards/`, `docs/requirements/`, `docs/architecture/`, `docs/research/`, `research/` and other repository-owned paths are **not automatically retired or endorsed** by this shortlist. Inspect their own metadata and current owner before applying them.

## Full document inventory and reconciliation

- [Generated current-document index](CURRENT-DOCUMENTS-INDEX.md) lists every **declared-active/current** repository-owned Markdown/MDX document found by the read-only scanner, with observed authority, version and diagnostics.
- [Complete machine inventory](current-documents.json) records in-scope source paths, observed frontmatter, missing explicit versions, duplicate declared-active canonical identities and broken relative links. File metadata is **not automatically corrected**.
- [Inventory source and regression tests](../scripts/docs_audit/inventory.py) define the coverage; [GitHub Actions](../.github/workflows/docs-status-inventory.yml) publishes a fresh diagnostic artifact and summary after relevant changes.
- **Tracking:** Work Notes WNASES-9 owns the exhaustive metadata/version/collision audit and limited repairs. Projektor ASES-5 owns any *derived* documentation/relationship projection, not a new canonical store. Newly found material conflicts remain open until verified, not quietly downgraded by an index script.

An entry reading `Active` in a historical file is **not a certificate of current runtime correctness**. Unversioned, invalid-identity or cross-repository-mirrored documents must be explicitly reviewed; do not assign fabricated past versions or treat a generated source digest as approval.

**First explicit reviewed revisions:** The four ASES-owned methods for bounded builds, realization selection, state-model applicability and upstream customization have dated document revisions `2026-11-24.1`. These are newly declared versions of the reviewed documents, not reconstructed historical release numbers or new validation of every referenced research claim. The state-model method explicitly separates current applicability guidance from unresolved adoption of the historical derived VSDD artifacts.

**Remaining authority conflict:** The EDASES Core System Prompt v1 and v2 both declare Active/Canonical, but v2 declares supersession of v1 and both retain old `AGENTS.md` consumer references. Their shared-source ownership and supersession require reconciliation; neither is a mandatory ASES startup prompt. This local navigation notice does not silently change the EDASES source metadata.

## Legacy and supersession

The old root `AGENTS.md` is now a **thin compatibility adapter** with active current links. Mandatory `SESSION-START.md`, `docs/SESSION-END.md`, and `docs/ORCHESTRATOR.md` have been retired as operational instructions. The dated `docs/methodology/Agent Model Launch Routes.md` is a deprecated redirect to the current launch skill.

These paths remain stable for inbound links, but do **not** authorize old Crosslink commands, IT3812/VPS routes, paid model substitutions or mandatory session rituals. Historical text is preserved at pinned Git revisions in each redirect. Runtime auto-loading of any file is separately measurable; neither this index nor the architecture decision asserts it has been tested.

## Ownership of decisions and state

GitHub retains the canonical technical source, versioned decisions and reproductions; Work Notes retains agent work packets/verified positions; Projektor retains human decisions and planning. A derived index can help discover relationships without becoming a fourth authoritative system or copying private material into public ASES.
