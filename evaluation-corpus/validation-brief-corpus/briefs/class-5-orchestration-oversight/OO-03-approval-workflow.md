---
id: OO-03
class: OO
kind: well-formed
title: Require human approval before promotion and record attribution
version: 0.1.0
---

# Brief OO-03 — Require human approval before promotion and record attribution

## Context

Artefact `docs/architecture/decision-010-data-retention.md` is ready to promote from `Reviewed` to `Active`. Per Human Oversight, promotion requires explicit human approval — automation must not self-approve.

## Artefact under test

Approval workflow for `docs/architecture/decision-010-data-retention.md`.

## Task

1. Request human approval via a durable mechanism (e.g., `crosslink issue comment --kind approval` or an approval artefact) — not an in-memory flag.
2. The artefact must **not** be promoted until approval is recorded. An attempt to promote without approval must be blocked with "requires human approval".
3. Upon approval, record: `approved_by`, `approved_at`, and `approval_ref` (comment or artefact ID).
4. Promote the artefact and link the promotion to its approval (traceable).

## Acceptance criteria

- [ ] AC1: Approval is requested via a durable, auditable mechanism (not transient).
- [ ] AC2: Promotion without approval is blocked with a specific error.
- [ ] AC3: Approval is recorded with by/at/ref, and is human-attributable (not agent self-approval).
- [ ] AC4: Promotion is linked to its approval (traceable via frontmatter or log).

## Scoring

- 2 points per AC. Max 8.
