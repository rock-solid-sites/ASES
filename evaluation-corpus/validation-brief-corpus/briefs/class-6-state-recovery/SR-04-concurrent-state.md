---
id: SR-04
class: SR
kind: well-formed
title: Handle concurrent state updates with conflict detection
version: 0.1.0
---

# Brief SR-04 — Handle concurrent state updates with conflict detection

## Context

Two agents attempt to promote `docs/architecture/decision-016-rate-limit.md` from `Reviewed` to `Active` simultaneously. The system must detect the race and ensure exactly one promotion succeeds.

## Artefact under test

Concurrent promotion handling for `docs/architecture/decision-016-rate-limit.md`.

## Task

1. Simulate concurrent promotion attempts (or document the expected handling) — the second attempt must detect that the artefact is already `Active` and not create a duplicate transition.
2. Use an atomic or idempotent mechanism (e.g., compare-and-swap on state, or a lock) to serialize the promotion.
3. Record both attempts in the transition history: one success, one detected conflict.
4. Verify the final state is `Active` (not `Active` twice or corrupted) and the history is linearizable.

## Acceptance criteria

- [ ] AC1: Concurrent attempts are serialized — exactly one promotion succeeds.
- [ ] AC2: Second attempt detects the conflict and is recorded as such (not silent duplicate).
- [ ] AC3: Mechanism is atomic/idempotent (CAS, lock, or equivalent) and documented.
- [ ] AC4: Final state is Active and history is linearizable (not duplicated or corrupted).

## Scoring

- 2 points per AC. Max 8.
