---
id: SR-02
class: SR
kind: well-formed
title: Recover after interruption using persisted state and evidence
version: 0.1.0
---

# Brief SR-02 — Recover after interruption using persisted state and evidence

## Context

Work on `docs/architecture/decision-013-sharding.md` was interrupted mid-draft (agent crash, no conversation history). A fresh agent with **zero conversation history** but full artefact history must resume.

## Artefact under test

Recovery for `docs/architecture/decision-013-sharding.md`.

## Task

1. Starting with only artefact history (file + provenance + evidence, no conversation), reconstruct: what was done, what remains, and what decision was pending.
2. Use the persisted state and handoff artefact (if any) to resume — do not re-ask for information already in artefacts.
3. Complete the artefact to `Reviewed` (or record why it cannot be completed).
4. Record the recovery as a provenance entry: what was used to recover, what was inferred, and what was explicitly not available (WHAT-NOT-TESTED for recovery).

## Acceptance criteria

- [ ] AC1: Agent resumes using only artefact history (no conversation replay) and correctly identifies done/remaining/pending.
- [ ] AC2: Resumption does not re-request information already in artefacts (auditable).
- [ ] AC3: Artefact is completed to Reviewed or a specific block reason is recorded.
- [ ] AC4: Recovery provenance states what was used, what was inferred, and what was not available.

## Scoring

- 2 points per AC. Max 8.

## Notes

- Directly tests the artefact-recovery hypothesis (H2/H3). See `research/execution-engine-ui/reports/rq6-artefact-recovery.md` for the three-condition experiment design.
