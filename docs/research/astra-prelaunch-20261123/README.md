---
title: ASES prelaunch engineering packet index — 2026-11-23
version: 0.1.0
program: ASES
layer: Research
document_type: Task Packet Index
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-23
---

# ASES engineering campaign — prepared task boundary

These two packets were compiled in Chat before an autonomous engineering run. They are **source-backed task instructions, not evidence of a new code fix or a successful Work Unit integration**.

- [Native pending-effect admission implementation packet](NATIVE-PENDING-ADMISSION-IMPLEMENTATION-PACKET.md) — bounded and sufficiently specified for a builder, grounded in draft PR #43 baseline. Corrects the contradicted original *seal-blocked* expectation. Target source `e91fb4b14875487dee9c19cc764e72655ba534c0`.
- [Kernel-0 / Work Unit adequacy test packet](WORK-UNIT-ADEQUACY-TEST-PACKET.md) — bounded source/evidence reconnaissance, **not** a frozen new-Kernel implementation. Canonical Kernel-0 evidence on `a02df749b4b3da88d3f88c1712623cec6ad5d963`; Rust prototype PR #42 `27bcc552cecb8bbb456b9db3a0a77da1513b31ab`.

**Parent orchestration-only task delta:**

> Coordinate completion of the two ASES engineering packets linked here. Delegate source work, implementation and tests to workers; review their concise evidence, settle real engineering decisions and commission separated verification. Preserve commits and actual test evidence, then advance to the next justified task without repeating settled research.

No caller-side model identity, quota forecast, provider details or self-verification requests belong in the receiving task text. Those are not engineering decisions in these packets.

**Verification at preparation:** Current ASES prompt/build/handoff methods read; exact target code and reported experimental baseline read at the pinned refs; original baseline and prior Rust regression reports inspected. **Not executed:** a revised native admission test, a fresh independent Rust test, a real Work Unit replacement-fencing test or an autonomous agent launch. Do not classify these as passing on the basis of documentation.

**Authority:** these are isolated experimental handoffs, not changes to main, project-wide design, or the canonical Kernel. PR #45's old Sol control-plane package is superseded; it is not a dependency.
