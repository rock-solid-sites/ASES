---
id: AL-03
class: AL
kind: well-formed
title: Supersede an artefact and preserve history
version: 0.1.0
---

# Brief AL-03 — Supersede an artefact and preserve history

## Context

Two artefacts exist: `docs/architecture/decision-001-circuit-breaker.md` (v1) and `docs/architecture/decision-001-circuit-breaker-v2.md` (v2, supersedes v1). A new cross-cutting finding invalidates both; a new synthesis is needed.

## Artefact under test

`docs/architecture/decision-001-synthesis.md` — supersedes both prior versions.

## Task

1. Create `docs/architecture/decision-001-synthesis.md` with frontmatter `supersedes: [docs/architecture/decision-001-circuit-breaker.md, docs/architecture/decision-001-circuit-breaker-v2.md]`.
2. Include a "Supersession rationale" section that explains why both priors are superseded (not merely versioned).
3. Ensure the artefact history remains navigable: an index or provenance graph should allow tracing from synthesis back through v2 to v1.
4. Do not delete the superseded files — they remain as historical record with status `Superseded`.

## Acceptance criteria

- [ ] AC1: Synthesis file exists with array `supersedes` listing both priors.
- [ ] AC2: Synthesis contains supersession rationale (why, not just what).
- [ ] AC3: History is navigable — superseded files still exist and are marked `Superseded` or index reflects the chain.
- [ ] AC4: No deletion or silent overwrite of historical artefacts.

## Scoring

- 2 points per AC. Max 8.
