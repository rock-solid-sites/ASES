---
id: WV-03
class: WV
kind: well-formed
title: Manage parallel workflow branches with dependency tracking
version: 0.1.0
---

# Brief WV-03 — Manage parallel workflow branches with dependency tracking

## Context

Two artefacts `docs/architecture/decision-005-auth.md` and `docs/architecture/decision-006-authz.md` are being developed in parallel. `decision-006` depends on `decision-005` (authz builds on auth). Both are in `Draft`.

## Artefact under test

Parallel workflow and dependency management.

## Task

1. Record the dependency explicitly (e.g., `depends_on: [docs/architecture/decision-005-auth.md]` in `decision-006` frontmatter).
2. Allow parallel work: both artefacts can be in `Draft` simultaneously, but `decision-006` must not be promotable to `Reviewed` until `decision-005` is at least `Reviewed`.
3. Attempt to promote `decision-006` before `decision-005` is reviewed — the system must block or warn with the dependency reason.
4. After promoting `decision-005` to `Reviewed`, verify that `decision-006` can then be promoted.

## Acceptance criteria

- [ ] AC1: Dependency is recorded explicitly and machine-readable (frontmatter or index).
- [ ] AC2: Parallel Draft state is allowed (no spurious block on independent Draft).
- [ ] AC3: Promotion of dependent artefact is blocked with dependency reason when prerequisite not met.
- [ ] AC4: Promotion succeeds after prerequisite is satisfied, with dependency resolution recorded.

## Scoring

- 2 points per AC. Max 8.
