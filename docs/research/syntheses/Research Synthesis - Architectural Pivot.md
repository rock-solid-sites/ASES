---
title: Research Synthesis: Provenance Deadlock and the Epistemic Architectural Pivot
program: EDASES
layer: Research
document_type: Synthesis
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - Synthesis of Adversarial Reviews: Decisional Provenance Architecture
  - reframe-chatgpt.md
  - reframe-deepseekpro.md
  - reframe-glm52.md
  - Concept: Levels of Abstraction

consumed_by:
  - ARCHITECTURE.md
  - Methodology to Requirements Mapping
  - AGENTS.md
  - Execution Engine Vision

supersedes: []
last_updated: 2026-06-29
---

# Research Synthesis: Provenance Deadlock and the Epistemic Architectural Pivot

> **Current interpretation (2026-11-24, local reconciliation):** This EDASES research synthesis remains the historical rationale for treating engineering reasoning, not commits or storage mechanics, as the object of interest. The abstraction hierarchy and the need for evidence-backed reasoning continuity remain applicable. The pinned June synthesis preserves the original reviewers' conclusions; claims that a dedicated validation layer is necessary or that particular causes are proven are historical interpretations, not current architectural requirements. EDASES upstream revision is unverified.

## Where the investigation led

The governing ASES decision is the [Task-Scoped Information Architecture ADR](../../architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md), with operational meaning in the [Task-Scoped Information and Handoff Method](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md). These preserve meaningful reasoning, evidence, decisions and provenance at existing authorized durable destinations; source selection, applicability, uncertainty and verification matter more than a particular representation. A task-specific view can be ordinary prose or a structured packet. Neither a dedicated epistemic-validation layer, persistent graph, database, central registry, nor generated bootstrap is required. The [Execution Engine Vision](../../architecture/Execution%20Engine%20Vision.md) and [Methodology-to-Requirements Mapping](../../requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md) govern actual current engine boundaries and intended requirements, not this earlier design debate.

### Evidence and the development of the idea

| Source | What it preserves | Current interpretation |
| --- | --- | --- |
| [Phase-1 draft 1](../../../knowledge-architecture-research/Knowledge%20Architecture%20Research%20Phase-1%20draft%201.md), [review C](../../../knowledge-architecture-research/Knowledge%20Architecture%20Research%20Phase-1%20draft%20response%20C.md), [review G](../../../knowledge-architecture-research/Knowledge%20Architecture%20Research%20Phase-1%20draft%20response%20G.md) | Initial exploratory survey, critique of an unspecified research domain, unbounded scope and different human/agent retrieval needs | Historical research design and rejected premature infrastructure assumptions |
| [Phase-1 draft 2](../../../knowledge-architecture-research/Knowledge%20Architecture%20Research%20Phase-1%20draft%202.md), [response 2](../../../knowledge-architecture-research/Knowledge%20Architecture%20Research%20Phase-1%20draft%20response%202.md), [draft 3](../../../knowledge-architecture-research/Knowledge%20Architecture%20Research%20Phase-1%20draft%203.md) | Refinement toward actual long-duration project problems, representative source corpus and measurable evaluation | Historical iterations, not outstanding survey assignments or competing governing plans |
| Assumption registers [v1](../../../assumption-registers/Assumption%20Register%20v1.md), [v2](../../../assumption-registers/Assumption%20Register%20v2.md), [v3](../../../assumption-registers/Assumption%20Register%20v3.md), [v4](../../../assumption-registers/Assumption%20Register%20v4.md) | Evolving hypotheses, confidence judgments and validation priorities | Dated research snapshots, not four current registers. Preserve unresolved research questions and evidence; do not infer that every assumption is either adopted or disproven. |
| [Fresh-agent reconstruction failure](../handoff-failure-analysis.md), [challenged assumption](../assumption-register-candidate.md), [epistemic validation addendum](../research-addendum-epistemic-validation.md) and [raw historical transcript](../failed-conversation.md) | Plausible but semantically imprecise reconstruction, overconfidence and subsequent output failure; candidate explanation and distinct later context-corruption hypothesis | Reconstruction and readiness validation are separate epistemic questions. Neither this incident nor a successful retrieval proves a common runtime cause or the necessity of a dedicated software layer. |
| [Levels of Abstraction](../../standards/Concept%20-%20Levels%20of%20Abstraction.md), [Canonical Terminology](../../standards/Canonical%20Terminology.md), [Conceptual Architecture](../../../ARCHITECTURE.md) | Conceptual boundaries, shared meanings and direction of authority/evidence | Preserve current conceptual guidance independently of physical storage or execution architecture. |
| [November information-topology comparison](../../../research/agent-information-topology/greenfield-task-context/comparison/RESULTS-2026-11-20.md) and [field trial](../../../research/agent-information-topology/greenfield-task-context/field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md) | Equivalent static manual/structured/graph-derived checks; actual source-selection miss | Supported task-scoped architecture and corrected operational source selection, not a comparative live-agent performance result. |

### Distinguish three kinds of information work

- **Canonical source and current position:** GitHub retains substantive technical sources, evidence and material historical reasoning; Work Notes tracks operational position and Projektor human decisions. The [current document inventory](../../CURRENT-DOCUMENTS-INDEX.md) reports metadata and diagnostic observations, not source authority or semantic truth.
- **Historical preservation and research:** The earlier drafts and registers above preserve how ideas changed. They do not impose a mandatory schema or require re-running their old projects. Archive completeness and conversation retrieval remain separate from current operational authority.
- **Optional derived retrieval:** The [knowledge-index prototype](../../../scripts/knowledge_index/README.md) was merged as research via [PR #61](https://github.com/rock-solid-sites/ASES/pull/61), not as a maintained service. Its 49-test baseline and repaired importer defects qualify bounded prototype behavior; candidate graph edges are not validated facts. The proposed [minimal schema](../Cross-Project%20Knowledge%20Index%20-%20Minimal%20Schema%20and%20Integration%20Boundaries.md) and [pilot charter](../../proposals/knowledge-index/Experimental%20Pilot%20Charter%20and%20Handoff%202026-11-19.md) remain experimental. WNASES-16's comparative retrieval benchmark has not started at this reconciliation cutoff; ASES-19 owns the subsequent retain/revise/discard decision. It is not a prerequisite to the accepted task-scoped method or the execution engine. No private ingestion, deployment or graph authority is implied.

## Preserved original June synthesis

[Original local source](https://github.com/rock-solid-sites/ASES/blob/aa34b51f8f89cffb42ac307d5ae4ed33802c9e33/docs/research/syntheses/Research%20Synthesis%20-%20Architectural%20Pivot.md) preserves the complete June synthesis, exact source identities, reviewer attribution, and original metadata. Its historical next steps and architectural claims are not current requirements.
