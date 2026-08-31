---
id: MF-09
class: WV
kind: malformed
title: Enforce transition — conflicting instructions (malformed)
version: 0.1.0
---

# Brief MF-09 — Conflicting instructions

## Context

Artefact `docs/architecture/decision-003-cache-invalidation.md` is in `Draft`.

## Task

Do the following:

1. Promote the artefact from `Draft` to `Active` directly (skip `Reviewed`).
2. **Do not** promote the artefact from `Draft` to `Active` directly — you must go through `Reviewed` first.

These two instructions contradict each other intentionally. A conforming implementation must **flag the conflict** and request clarification, not arbitrarily choose one.

_expected_recovery: Flag conflict, request clarification_

_why_malformed: Conflicting instructions make the brief non-deterministic; the system must not silently choose._
