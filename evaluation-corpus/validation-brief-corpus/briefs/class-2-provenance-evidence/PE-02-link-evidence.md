---
id: PE-02
class: PE
kind: well-formed
title: Link evidence to a finding with explicit relationship
version: 0.1.0
---

# Brief PE-02 — Link evidence to a finding with explicit relationship

## Context

A finding `findings/retry-backoff-finding.md` states that exponential backoff reduces retry storms. This finding must be traceable to its evidence.

## Artefact under test

`findings/retry-backoff-finding.md` and its evidence links.

## Task

1. Create the finding artefact with frontmatter that includes an `evidence:` array, each entry with `source`, `content`, and `relationship` (e.g., `supports`, `contradicts`, `derives-from`).
2. Provide at least two evidence items: one observation log and one benchmark result.
3. Ensure each evidence item is itself an artefact or has a stable reference (path or ID) — not a transient inline quote without provenance.
4. Include a "Traceability" section that makes the finding→evidence graph explicit for audit.

## Acceptance criteria

- [ ] AC1: Finding has structured `evidence:` array with source, content, and typed relationship per item.
- [ ] AC2: At least two evidence items of different types (observation + benchmark or log + measurement).
- [ ] AC3: Each evidence item has a stable reference (path/ID) and is not ephemeral.
- [ ] AC4: Traceability section explicitly maps finding to evidence (auditable).

## Scoring

- 2 points per AC. Max 8.
