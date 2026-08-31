---
id: OO-04
class: OO
kind: well-formed
title: Escalate a blocked artefact through the defined escalation path
version: 0.1.0
---

# Brief OO-04 — Escalate a blocked artefact through the defined escalation path

## Context

Artefact `docs/architecture/decision-011-concurrency-model.md` is blocked: two reviewers gave conflicting verdicts (one approve, one reject). The methodology defines an escalation path: divergent reviews → synthesis → human orchestrator decision.

## Artefact under test

Escalation handling for `docs/architecture/decision-011-concurrency-model.md`.

## Task

1. Detect the divergence (conflicting verdicts) and record it as a `blocked` state with reason.
2. Escalate via the defined path: create a synthesis artefact that preserves both original verdicts (does not overwrite) and states the conflict.
3. Route to the human orchestrator for decision — record the escalation (`escalated_to`, `escalated_at`, `reason`).
4. The artefact must remain blocked (not silently promoted or rejected) until the orchestrator resolves.

## Acceptance criteria

- [ ] AC1: Divergence is detected and artefact is marked blocked with specific reason (conflicting verdicts named).
- [ ] AC2: Synthesis preserves both original verdicts (additive, not overwriting) and states the conflict.
- [ ] AC3: Escalation is recorded with to/at/reason and targets the orchestrator.
- [ ] AC4: Artefact remains blocked until orchestrator decision (no auto-promote/reject).

## Scoring

- 2 points per AC. Max 8.
