---
id: PE-04
class: PE
kind: well-formed
title: Audit an artefact for evidence completeness before promotion
version: 0.1.0
---

# Brief PE-04 — Audit an artefact for evidence completeness before promotion

## Context

`docs/architecture/decision-002-retry-policy.md` is ready for promotion, but promotion requires evidence completeness. The task is to perform the audit, not just claim it.

## Artefact under test

Audit report for `docs/architecture/decision-002-retry-policy.md`.

## Task

1. Create an audit artefact at `findings/decision-002-audit.md` that checks:
   - Every finding cited by the decision has linked evidence.
   - Every evidence item has a stable reference and relationship type.
   - The WHAT-NOT-TESTED clause is present and specific (not generic "more testing needed").
2. The audit must state a verdict: `pass` or `fail` with justification per check.
3. If any check fails, the artefact must **not** be promoted — record the block and required remediation.
4. The audit itself must have provenance (who audited, when, what was checked).

## Acceptance criteria

- [ ] AC1: Audit checks all three items (evidence linked, stable refs, WHAT-NOT-TESTED specificity) and records pass/fail per item.
- [ ] AC2: Audit states an overall verdict (pass/fail) with justification.
- [ ] AC3: Promotion is blocked if any check fails (auditable decision not to promote).
- [ ] AC4: Audit has its own provenance (auditor, timestamp, checks performed).

## Scoring

- 2 points per AC. Max 8.
