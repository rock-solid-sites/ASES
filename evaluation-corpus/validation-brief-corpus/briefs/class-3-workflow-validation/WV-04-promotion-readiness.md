---
id: WV-04
class: WV
kind: well-formed
title: Determine promotion readiness via required relationships
version: 0.1.0
---

# Brief WV-04 — Determine promotion readiness via required relationships

## Context

Artefact `docs/architecture/decision-007-observability.md` is in `Reviewed`. Promotion to `Active` requires: at least one linked decision, at least one evidence item per finding, and explicit human approval.

## Artefact under test

Promotion readiness check.

## Task

1. Create or ensure the artefact has:
   - A `decisions:` frontmatter entry or decision record linked.
   - Findings with evidence links.
   - A `human_approval: pending` or equivalent marker.
2. Run a readiness check that evaluates each requirement and reports missing items.
3. If any requirement is missing, report the specific missing requirement (not generic) and block promotion.
4. After adding the missing items and recording human approval, re-run the check and promote, recording the final readiness report.

## Acceptance criteria

- [ ] AC1: Readiness check evaluates all three requirements and reports per-requirement status.
- [ ] AC2: Missing items are reported specifically; promotion is blocked until resolved.
- [ ] AC3: Human approval is required and recorded (who approved, when).
- [ ] AC4: Final promotion is recorded with the readiness report as provenance.

## Scoring

- 2 points per AC. Max 8.
