---
id: AL-01
class: AL
kind: well-formed
title: Create a versioned artefact with required frontmatter
version: 0.1.0
---

# Brief AL-01 — Create a versioned artefact with required frontmatter

## Context

You are operating in an EDASES execution workspace that enforces artefact lifecycle via the Documentation Standard and the Levels of Abstraction. A new design decision needs to be recorded as a versioned artefact.

## Artefact under test

`docs/architecture/decision-001-circuit-breaker.md` — does not yet exist.

## Task

Create the artefact at the path above with the following requirements:

1. Include valid Documentation Standard frontmatter with: `title`, `program: EDASES`, `layer: Architecture`, `document_type: Decision`, `status: Draft`, `authority: Derived`, `canonical_repository: edases`, and `last_updated: 2026-08-31`.
2. Body must contain: decision statement, alternatives considered (at least 2), and trade-off analysis.
3. The file must be created as **version 1** — no supersession link needed, but the artefact must be registered in the artefact index (if one exists) or be discoverable via `docs/architecture/` listing.

## Acceptance criteria

- [ ] AC1: File exists at the exact path with valid YAML frontmatter (all required fields present, correct values).
- [ ] AC2: Body contains decision, ≥2 alternatives, and trade-off analysis (each non-empty).
- [ ] AC3: No duplicate artefact with same title exists; creation is idempotent-safe (second run would detect existing file).
- [ ] AC4: Reasoning is explicit: the decision states WHY (reasoning behind the claim) and WHAT (basis), per AGENTS.md Reasoning Certainty.

## Scoring

- 2 points per AC (0 = fail, 1 = partial, 2 = full). Max 8.

## Notes for harness

- Validate frontmatter via YAML parse; check `document_type` is `Decision` and `layer` is `Architecture`.
- Body checks are substring-based ( presence of "Alternative" or "Option" headings).
