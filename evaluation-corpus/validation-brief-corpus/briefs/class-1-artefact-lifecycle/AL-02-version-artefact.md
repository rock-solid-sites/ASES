---
id: AL-02
class: AL
kind: well-formed
title: Create a new version of an existing artefact with supersession link
version: 0.1.0
---

# Brief AL-02 — Create a new version of an existing artefact with supersession link

## Context

`docs/architecture/decision-001-circuit-breaker.md` exists as version 1 (from AL-01). New evidence has emerged that changes the decision.

## Artefact under test

`docs/architecture/decision-001-circuit-breaker-v2.md` — new version.

## Task

1. Create the new artefact at `docs/architecture/decision-001-circuit-breaker-v2.md` with frontmatter that includes `supersedes: docs/architecture/decision-001-circuit-breaker.md` and `version: 2`.
2. Preserve the original decision's rationale in a "Prior decision" section, then state the revised decision.
3. Add a supersession notice to the **original** file (if the system supports in-place updates) or, if the original is immutable, ensure the index records the supersession relationship. Do not mutate the original's body beyond adding a notice; preserve its history.
4. Document provenance for the revision: what new evidence triggered it, how certain the new decision is.

## Acceptance criteria

- [ ] AC1: New file exists with correct frontmatter including `supersedes` pointing to original and `version: 2`.
- [ ] AC2: New file contains prior decision summary + revised decision (both present).
- [ ] AC3: Supersession relationship is recorded bidirectionally or in an index — original is marked as superseded, new is marked as successor.
- [ ] AC4: Provenance is explicit: states the evidence that triggered the revision and certainty level.

## Scoring

- 2 points per AC. Max 8.

## Notes

- Tests versioning and supersession — a core EDASES lifecycle primitive. Checks that history is preserved, not overwritten.
