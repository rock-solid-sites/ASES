---
id: AL-04
class: AL
kind: well-formed
title: Archive an artefact with retention policy
version: 0.1.0
---

# Brief AL-04 — Archive an artefact with retention policy

## Context

`docs/architecture/decision-001-circuit-breaker.md` (v1, superseded) is now historical. Per the data-retention knowledge page, superseded artefacts should be archived, not deleted, with an explicit retention record.

## Artefact under test

Archive handling for `docs/architecture/decision-001-circuit-breaker.md`.

## Task

1. Move or mark the superseded artefact as archived according to the project's retention policy (if no explicit archive dir exists, add a `status: Archived` and `archived_at: 2026-08-31` to its frontmatter and ensure it remains discoverable).
2. Record the archival in an audit trail: what was archived, why, retention period, and who authorized.
3. Ensure the artefact remains readable via history/provenance (not removed from graph or index).
4. Verify that the supersession chain (v1 → v2 → synthesis) still resolves after archival.

## Acceptance criteria

- [ ] AC1: Artefact is marked archived (either moved to archive location or frontmatter `status: Archived` with `archived_at`).
- [ ] AC2: Audit record exists (comment, log, or archival manifest) with what/why/retention/authorization.
- [ ] AC3: Artefact remains readable via history (not deleted).
- [ ] AC4: Supersession chain still resolves (synthesis → v2 → v1) after archival.

## Scoring

- 2 points per AC. Max 8.
