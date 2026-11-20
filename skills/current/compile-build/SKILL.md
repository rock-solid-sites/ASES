---
name: compile-build
version: 1.0.1
description: Compile a bounded, sufficiently specified project slice into a verifiable Implementation Packet.
status: current
---

# Bounded project compilation

**If compiling a substantial bounded implementation packet, retrieve and read the full current canonical** `docs/methodology/ASES Bounded Project Build Method.md` **before declaring the packet ready**. A link to the method, a PR referring to it, or a prior summary is not equivalent to reading it. The Strategy-to-Builder derivation in `docs/research/` is non-normative; old `skills/prompt/SKILL.md` is not the active prompt-selection procedure. Do not compile trivial edits, exploratory architecture-dependent work, or assume an entire large project can be frozen. If the method cannot be read, emit only a preliminary packet with the exact missing source noted.

Determine the user-selected behavior and acceptance, inspect the existing code and reusable alternatives, eliminate unnecessary requirements/components, resolve interfaces and tests, and document only remaining live assumptions. Emit a minimal Implementation Packet: frozen behavior, constraints, relevant source, needed components, test evidence and stop conditions.

The builder integrates and verifies, rather than redesigning already settled decisions. Use `skills/current/compact-prompt/SKILL.md` for the residual task and `skills/current/agent-launch/SKILL.md` for actual model dispatch.
