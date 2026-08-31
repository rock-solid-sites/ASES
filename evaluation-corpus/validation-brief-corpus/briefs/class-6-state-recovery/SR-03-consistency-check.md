---
id: SR-03
class: SR
kind: well-formed
title: Verify state consistency across artefacts after concurrent updates
version: 0.1.0
---

# Brief SR-03 — Verify state consistency across artefacts after concurrent updates

## Context

Two agents concurrently updated `docs/architecture/decision-014-api-gateway.md` and `docs/architecture/decision-015-auth-service.md`, both of which reference a shared artefact `docs/architecture/decision-005-auth.md`. Consistency must be verified.

## Artefact under test

Consistency across the three artefacts after concurrent edits.

## Task

1. Check for divergence: does the persisted state of each artefact match its frontmatter? Do the references to `decision-005` still resolve?
2. Run a consistency check that reports per-artefact status (consistent / divergent) and names any divergence.
3. If divergence is found, record the specific inconsistency (e.g., index says Active but file says Draft, or reference now dangling).
4. Record the check as an auditable artefact with who checked, when, and what was verified.

## Acceptance criteria

- [ ] AC1: Consistency check is performed across all three artefacts and reports per-artefact status.
- [ ] AC2: Any divergence is named specifically (not generic "inconsistent").
- [ ] AC3: References to shared artefact are verified (resolve or flagged as dangling).
- [ ] AC4: Check is recorded with who/when/what as an auditable artefact.

## Scoring

- 2 points per AC. Max 8.
