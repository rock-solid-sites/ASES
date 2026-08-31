---
id: PE-01
class: PE
kind: well-formed
title: Capture provenance for an artefact transition (WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED)
version: 0.1.0
---

# Brief PE-01 — Capture provenance for an artefact transition

## Context

An artefact `docs/architecture/decision-002-retry-policy.md` is being promoted from Draft to Active. Per AGENTS.md Reasoning Certainty, every cross-role claim must state WHY, WHAT, HOW-CERTAIN, and WHAT-NOT-TESTED.

## Artefact under test

`docs/architecture/decision-002-retry-policy.md` — transition evidence.

## Task

1. Create or update the artefact with a promotion record that includes all four certainty clauses:
   - **WHY** — reasoning behind the decision (1–2 sentences)
   - **WHAT** — basis (observations, data, or prior artefact)
   - **HOW CERTAIN** — one of `guess` / `evidence-based` / `proven`
   - **WHAT-NOT-TESTED** — explicit negative-space disclosure (what was not tested)
2. Link the claim to its supporting evidence (at least one evidence item with source and content).
3. Record the transition in the artefact's provenance: who promoted, when, and the validation that was performed.
4. Ensure the provenance is stored as a typed relationship (not just free-text), e.g., frontmatter `provenance:` block or a sidecar evidence file.

## Acceptance criteria

- [ ] AC1: All four clauses present and non-empty, with HOW-CERTAIN being one of the three allowed values.
- [ ] AC2: At least one evidence item linked (source + content) and relationship is typed/explicit.
- [ ] AC3: Transition record includes actor, timestamp, and validation performed.
- [ ] AC4: Provenance is machine-readable (structured frontmatter or sidecar), not only prose.

## Scoring

- 2 points per AC. Max 8.
