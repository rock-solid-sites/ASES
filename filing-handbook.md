---
title: "Filing Handbook — routing + conventions for document-filing sessions"
tags: ["filing", "documentation", "routing"]
sources: []
contributors: ["OL2r", "pp3g-Mdur-execute-the-operator-approved-filing-plan-on-issue"]
created: 2026-08-10
updated: 2026-08-10
---


Thin handbook for document-filing sessions. Pointer-only: deeper docs live elsewhere and are read on demand. If you were pointed here via 'read the filing handbook', also read SESSION-START.md first.

## Purpose
Route a filing session: classify new/staged documents, author frontmatter per the Documentation Standard, place them in canonical homes, and close out. Do not re-derive the conventions from scratch — this page points at them.

## The two-category model (from the 10 retrospectives, filed 2026-08-10)
- PHASE / HISTORICAL docs -> docs/research/retrospectives/phases/, status: Archived, document_type: Research Record, supersedes/superseded_by chained through the sequence.
- TOPIC / ACTIVE docs -> docs/research/retrospectives/topics/, status: Active, document_type: Research Record, cross-linked (related_documents/consumed_by) to the downstream structures they feed (ASES methodology, execution-engine research, capability-mapping, knowledge architecture).
Worked example: the filed set at docs/research/retrospectives/ (read a phase + a topic doc for the shape).

## Filing procedure (condensed)
1. Classify: category (phase/topic), layer (Research / Methodology / Requirements / Architecture / Implementation), document_type (per Documentation Taxonomy).
2. Author frontmatter per docs/standards/Documentation Standard.md: title, program, layer, document_type, status, authority, canonical_repository, depends_on, consumed_by, related_documents, supersedes, superseded_by, last_updated. Normalise programme->program; American spelling; last_updated (not last_update).
3. Place in the canonical home (docs/<layer>/). git mv preserves history.
4. Reference sweep folded into the SAME commit: old path AND title strings in depends_on/consumed_by/related_documents across CHANGELOG, .design/, research-addenda/, .crosslink/knowledge/, scripts/, ORIENTATION.md, ARCHITECTURE.md, SESSION-START/END, docs/. Exclude docs/historical/ (frozen archive).
5. Commit with [#issue] ref, post plan + result comments, sync.

## Canonical homes (current layout)
- docs/methodology/ — AI Orchestration Guide, Clean Room Execution Guide, core-system-prompts/
- docs/requirements/ — Methodology to Requirements Mapping Specification
- docs/architecture/ — Execution Engine Vision
- docs/research/ — canonical research docs, retrospectives/, review-inbox/, frameworks/, protocols/
- docs/research/registry/ — AI Capability Registry (Specification + instance: Harness-Capability-Matrix, Model-Routing-Matrix, model-feedback-*)
- docs/standards/ — Documentation Standard, Documentation Taxonomy, Canonical Terminology, Concept: Levels of Abstraction

## Staging / backlog

to-file/ — holds only CLUSTER D (reviews-1/2/3.md), HELD per operator decision on #351 (waiting for checklist subjects). All other staging items filed to canonical homes per #351: crosslink-gates/ (5) -> docs/research/crosslink-gates/ (Archived, superseded by crosslink impl #13/#22-#27); failed-conversation.md, handoff-failure-analysis.md, research-addendum-epistemic-validation.md, assumption-register-candidate.md -> docs/research/ (Active Research Records); regression-testing.md -> docs/research/regression-testing-orchestrator-compliance.md; EDASES-topic-methodology-research.md + EDASES-topic-Git-Based-Engineering-Systems.md -> docs/research/retrospectives/topics/; EDASES-methodology-enforcement.md -> docs/research/EDASES-Methodology-Feedback-and-Enforcement.md.

## Deeper docs (read on demand)
- docs/standards/Documentation Standard.md — frontmatter rules, permitted layer values, authority rules
- docs/standards/Documentation Taxonomy.md — document categories
- knowledge page session-handoff-2026-08-10-341 — the previous filing session, worked example
- knowledge page model-routing-matrix — model selection when dispatching agents

## Gotchas
- Orchestrator bash: pipe chains and compound commands (; &&) are DENIED — single commands only; use rtk read/diff or the Read tool.
- Stale duplicate issues exist (e.g. #225/#223 'file the main project document') — already superseded by merged docs; do not re-do.
- to-file/ items need classification decisions first (historical vs research vs active) — never auto-file.
- New untracked docs need an active crosslink issue before commit (git commit gated on active issue).
- Pre-positioned auditor / read-only roles cannot write .kickoff-status — completion signal is the synced verdict comment.
- crosslink kickoff cleanup is all-or-nothing; --force touches other sessions' live-tmux worktrees — gated kill-by-ID is being scoped (#349/#350).
