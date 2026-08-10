---
title: Session End Conventions
program: EDASES
layer: Research
document_type: Standard
status: Active
authority: Derived
canonical_repository: edases
depends_on:
- Documentation Standard
consumed_by:
- Future agent sessions
- Orchestrators
related_documents:
- SESSION-START.md
- agent-orchestration-playbook.md
last_updated: 2026-08-04
---

# SESSION-END

Routing entry point for how a session ends and hands off. Read before ending any session. Mirrors SESSION-START.md (the in-router); this is the out-router. SESSION-START should reference this document.

## Purpose

A handoff is a ROUTING document, not a state dump. It must let a fresh orchestrator bootstrap with minimal context and prevent context bloat. Durable detail lives in the tools we already have (issues, knowledge pages, git refs, hub); the handoff only POINTS there, to be checked on demand.

## Who writes

By convention, the ORCHESTRATOR writes the durable handoff (most insight over what happened). Agents end their own sessions with 'crosslink session end --notes' (machine-readable). The structured, durable handoff is orchestrator-produced at session boundaries.

## Mechanism (provisional)

The orchestrator has NO filesystem write (edit denied; orchestrator-guard blocks write tools for non-Builder). Per the repo's handoff mechanism decision, provisional option A: the orchestrator writes markdown through CROSSLINK surfaces (crosslink knowledge add/edit, crosslink issue comment, crosslink session end --notes). If this proves insufficient (e.g. dated repo-file notes needed), revisit option B ('crosslink note' command) — part of the project's continual learning. See the repo's knowledge pages for the decision trail.

## Structure (thin — about one screen, skimmable)

| Section | Content | Rule |
|---|---|---|
| State | Done (to closed issues), Open (to open issues/Epics), Blocked (to blocked-by edges) | pointers only, never restate |
| Known gotchas | Pointers to knowledge pages/issues documenting them (e.g. hydration issues, lock staleness, agent drift, flags lie) | never re-document here |
| Next actions | Recommended next Epic/issue (to issue ready) | one line |
| Reference map | topic to issue / knowledge page / file | the index |

## Anti-bloat rules

1. Never duplicate issue content — reference it.
2. Never embed a retrospective — point to where it lives (e.g. a research doc referenced from its issue or knowledge page).
3. Longer info lives elsewhere (issues, knowledge, docs) and is pulled only if needed.
4. The handoff itself stays small — if it grows, the detail belongs in a knowledge page or issue, not the handoff.

## Ending procedure (ordered)

1. Post --kind result comments on any issues worked (minimum plan + result).
2. Record 'crosslink session action' breadcrumbs for context compression.
3. Run 'crosslink session end --notes' with the handoff summary (machine-readable).
4. Produce the durable thin handoff per the structure above (orchestrator; via the repo's handoff mechanism surfaces).
5. Model evidence: if models were used this session, record their performance (strengths, weaknesses, failure modes, token cost) into the Model Capability Registry (knowledge page: model-routing-matrix / docs/research/registry/Model-Routing-Matrix.md + docs/model-feedback-*.md). This is how the registry stays current.
6. Run 'crosslink kickoff cleanup' after each dispatch wave (assess STALE with --dry-run --force, preserve work before removing).

## Conventions

Operator git commands must use `--no-edit` so no interactive editor opens.

## Evolution

Sections are a living list, updated as we learn what a fresh session actually trips on. First real test: next session — does the handoff let a fresh orchestrator pick up the active Epic without this conversation?

## Decision trail

The series of decisions that led to this convention (see the repo's knowledge
pages for the issue trail):
- Tooling/methodology boundary (2026-08-03) — tooling work stays tooling, but tooling observations are research evidence.
- Retrospective intake (2026-08-04) — sparked 'the orchestrator is often best-placed for retrospectives/handoffs/housekeeping markdown, but has no filesystem write'.
- Handoff mechanism design (2026-08-04) — option A (existing crosslink surfaces, zero code) provisionally adopted; B (crosslink note command) if insufficient; C (scoped *.md filesystem write) rejected as riskier.
- This document (2026-08-04) — convention codified on the option-A assumption.
- Earlier evidence shaping the convention: thin-orchestrator principle (bounded signals); crash-recovery lesson (committed work survives, conversational state may not — see the repo's research docs); handoff examples in the repo's session-handoff archives.
