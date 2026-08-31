---
id: MF-03
class: WV
kind: malformed
title: Enforce transition — truncated brief body
version: 0.1.0
---

# Brief MF-03 — Truncated brief body (malformed)

## Context

Artefact `docs/architecture/decision-003-cache-invalidation.md` is in `Draft`. The lifecycle forbids transitioning directly from `Draft` to `Active` without passing through `Revie

## Task

Attempt the invalid transition Draft→Active. The system must reject the transition and leave the artefact in `Draft`, with an error that names the allowed transitions (e.g., Draft→Reviewed). Record the rejected attempt

[TRUNCATED MID-SENTENCE — this brief is intentionally incomplete to test detection of truncated/malformed input. The acceptance criteria and scoring sections are missing.]

_expected_recovery: Flag as incomplete, request resubmission_
