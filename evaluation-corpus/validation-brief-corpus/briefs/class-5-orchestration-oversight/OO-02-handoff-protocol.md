---
id: OO-02
class: OO
kind: well-formed
title: Execute a handoff with context preservation and acknowledgement
version: 0.1.0
---

# Brief OO-02 — Execute a handoff with context preservation and acknowledgement

## Context

An orchestrator is handing off work on `docs/architecture/decision-009-state-machine.md` from one agent to another. The handoff must preserve context without relying on transient conversation history (per `SESSION-END.md`).

## Artefact under test

Handoff record for `docs/architecture/decision-009-state-machine.md`.

## Task

1. Create a handoff artefact at `session-handoffs/decision-009-handoff.md` (or equivalent durable store) containing: decisions made, pending tasks, blockers, and explicit state (what is done / what remains).
2. The handoff must be **durable** — stored in git, not only in `opencode.log` or memory. It must survive a crash and be readable by a zero-context agent.
3. The receiving agent must acknowledge the handoff (record `acknowledged_by` and `acknowledged_at`) before proceeding.
4. Verify that the receiving agent can resume without re-asking for information already in the handoff.

## Acceptance criteria

- [ ] AC1: Handoff artefact exists in a durable location (git-tracked) with decisions, pending, blockers, and state — all non-empty.
- [ ] AC2: Handoff is not solely in transient memory/log; it is file-based and git-trackable.
- [ ] AC3: Acknowledgement is recorded (by/at) before resumption.
- [ ] AC4: Resumption does not re-request handoff-contained information (auditable via logs or comments).

## Scoring

- 2 points per AC. Max 8.
