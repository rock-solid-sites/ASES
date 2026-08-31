---
id: OO-01
class: OO
kind: well-formed
title: Assign functional roles and enforce read-only boundary
version: 0.1.0
---

# Brief OO-01 — Assign functional roles and enforce read-only boundary

## Context

An artefact `docs/architecture/decision-008-event-bus.md` is under review. The methodology requires independent reasoning: reviewers must be read-only and must not influence each other before completing their own analysis.

## Artefact under test

Role assignment and enforcement for the review of `docs/architecture/decision-008-event-bus.md`.

## Task

1. Assign at least two reviewers with distinct roles (e.g., `reviewer: hy3` and `reviewer: luna`) in isolated contexts (isolated sub-issues or worktrees, per `agent-orchestration-playbook.md` §5.6).
2. Enforce that reviewers have **no write access** to the artefact under review — they can comment on their isolated sub-issue but not edit the artefact.
3. Ensure reviews are independent: each reviewer's verdict is recorded before any synthesis, and synthesis does not overwrite individual verdicts.
4. Record the assignment in an auditable manifest (who was assigned, when, with what scope).

## Acceptance criteria

- [ ] AC1: At least two reviewers assigned with isolated contexts and distinct roles.
- [ ] AC2: Reviewers are read-only on the artefact (no edit/write to the artefact itself).
- [ ] AC3: Individual verdicts are preserved before synthesis; synthesis is additive, not overwriting.
- [ ] AC4: Assignment manifest exists with who/when/scope.

## Scoring

- 2 points per AC. Max 8.
