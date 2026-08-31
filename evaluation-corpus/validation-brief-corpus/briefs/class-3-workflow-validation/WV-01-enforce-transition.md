---
id: WV-01
class: WV
kind: well-formed
title: Attempt an invalid state transition and expect rejection
version: 0.1.0
---

# Brief WV-01 — Attempt an invalid state transition and expect rejection

## Context

Artefact `docs/architecture/decision-003-cache-invalidation.md` is in `Draft`. The lifecycle forbids transitioning directly from `Draft` to `Active` without passing through `Reviewed`. A request to promote Draft→Active should be rejected mechanically.

## Artefact under test

State transition enforcement for `docs/architecture/decision-003-cache-invalidation.md`.

## Task

1. Attempt the invalid transition Draft→Active (e.g., via a promotion script, statechart, or manual frontmatter edit).
2. The system must **reject** the transition and leave the artefact in `Draft`, with an error that names the allowed transitions (e.g., Draft→Reviewed).
3. Record the rejected attempt in an audit trail (log, comment, or transition history) with actor, timestamp, and reason.
4. Verify that a valid transition Draft→Reviewed would succeed (or, if not performing it, document the valid path).

## Acceptance criteria

- [ ] AC1: Invalid transition is rejected and artefact remains in Draft.
- [ ] AC2: Error message names the allowed transitions / required intermediate state.
- [ ] AC3: Rejected attempt is recorded with actor, timestamp, and reason.
- [ ] AC4: Valid transition path is documented (what would succeed).

## Scoring

- 2 points per AC. Max 8.

## Notes

- Tests mechanical enforcement, not just documentation. A system that silently allows Draft→Active fails.
