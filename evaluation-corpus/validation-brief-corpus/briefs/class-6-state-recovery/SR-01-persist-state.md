---
id: SR-01
class: SR
kind: well-formed
title: Persist artefact state explicitly and verify recoverability
version: 0.1.0
---

# Brief SR-01 — Persist artefact state explicitly and verify recoverability

## Context

Artefact `docs/architecture/decision-012-persistence.md` is in `Active`. State must be explicit (not inferred from file existence) and recoverable.

## Artefact under test

State persistence for `docs/architecture/decision-012-persistence.md`.

## Task

1. Persist the artefact's state explicitly in a durable store (e.g., frontmatter `state: Active`, a state manifest, or a statechart snapshot) — not just "file exists".
2. Record the state transition with provenance: what was persisted, when, and by whom.
3. Verify recoverability: after persistence, simulate a read from the durable store (not from memory) and confirm the artefact's state and content are intact.
4. Ensure state is consistent — the persisted state matches the artefact's frontmatter and any index.

## Acceptance criteria

- [ ] AC1: State is persisted explicitly in a durable, file-based store (not memory-only).
- [ ] AC2: Transition is recorded with what/when/by.
- [ ] AC3: Recoverability is verified by reading from the durable store (not memory) and confirming state + content.
- [ ] AC4: Persisted state is consistent with frontmatter and any index (no divergence).

## Scoring

- 2 points per AC. Max 8.
