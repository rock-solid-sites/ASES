---
id: WV-02
class: WV
kind: well-formed
title: Enforce validation gate before promotion
version: 0.1.0
---

# Brief WV-02 — Enforce validation gate before promotion

## Context

Artefact `docs/architecture/decision-004-api-versioning.md` is in `Reviewed` and ready to promote to `Active`, but promotion requires a validation gate: all findings must have evidence, and all assumptions must be challenged or accepted.

## Artefact under test

Promotion gate for `docs/architecture/decision-004-api-versioning.md`.

## Task

1. Run the validation gate (or simulate it) that checks:
   - Every finding linked to the artefact has evidence with stable refs.
   - Every assumption has a recorded challenge or acceptance.
2. If the gate **passes**, promote the artefact to `Active` and record the validation outcome.
3. If the gate **fails**, block promotion and list the specific missing items (not a generic "validation failed").
4. Record the gate result as an auditable artefact (validation report) with provenance.

## Acceptance criteria

- [ ] AC1: Gate checks both conditions (evidence completeness + assumption disposition) and reports per-item results.
- [ ] AC2: Promotion occurs only if gate passes; otherwise blocked with specific missing items.
- [ ] AC3: Promotion (if it occurred) is recorded with validation outcome and timestamp.
- [ ] AC4: Validation report is auditable (who validated, when, what was checked, verdict).

## Scoring

- 2 points per AC. Max 8.
