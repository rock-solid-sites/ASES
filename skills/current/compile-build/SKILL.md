---
name: compile-build
version: 1.0.0
description: Compile a bounded, sufficiently specified project slice into a verifiable Implementation Packet.
status: current
---

# Bounded project compilation

Read the canonical `docs/methodology/ASES Bounded Project Build Method.md` when compilation is materially useful. Do not compile trivial edits or assume an entire large project can be frozen.

Determine the user-selected behavior and acceptance, inspect the existing code and reusable alternatives, eliminate unnecessary requirements/components, resolve interfaces and tests, and document only remaining live assumptions. Emit a minimal Implementation Packet: frozen behavior, constraints, relevant source, needed components, test evidence and stop conditions.

The builder integrates and verifies, rather than redesigning already settled decisions. Use `skills/current/compact-prompt/SKILL.md` for the residual task and `skills/current/agent-launch/SKILL.md` for actual model dispatch.
