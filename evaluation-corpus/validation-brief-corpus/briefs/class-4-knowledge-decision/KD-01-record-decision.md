---
id: KD-01
class: KD
kind: well-formed
title: Record a decision with alternatives, trade-offs, and rationale
version: 0.1.0
---

# Brief KD-01 — Record a decision with alternatives, trade-offs, and rationale

## Context

A decision is needed on caching strategy for the execution engine. The decision must be traceable, with alternatives and trade-offs explicit.

## Artefact under test

`decisions/cache-strategy-001.md` (new).

## Task

1. Create the decision artefact with frontmatter: `title`, `program: EDASES`, `layer: Architecture`, `document_type: Decision`, `status: Draft`, `decided_by`, `decided_at`.
2. Body must contain:
   - **Decision** (single sentence)
   - **Alternatives** (≥2, each with brief description)
   - **Trade-offs** (what is gained/lost per alternative)
   - **Rationale** (why this alternative was chosen)
   - **Consequences** (what follows from the decision)
3. Link the decision to at least one supporting finding or evidence item.
4. Ensure the decision is distinguishable from a finding (it records a choice, not an observation).

## Acceptance criteria

- [ ] AC1: Frontmatter has all required fields with correct values; body has all five sections (decision, alternatives ≥2, trade-offs, rationale, consequences).
- [ ] AC2: Alternatives and trade-offs are specific (not placeholder "Option A/B").
- [ ] AC3: Decision is linked to at least one finding/evidence with explicit relationship.
- [ ] AC4: Artefact is typed as Decision (not Finding or Observation) and is auditable (decided_by/at present).

## Scoring

- 2 points per AC. Max 8.
