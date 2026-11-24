---
name: workflow-orchestration
version: 1.0.2
description: Select the smallest evidence-driven recon, review, test, build or synthesis loop with isolated work.
status: current
---

# ASES workflow orchestration

Inspect current evidence and identify the smallest unresolved question. Choose targeted recon when the mechanism is unknown; independent parallel tests for separable hypotheses; synthesis for conflicts; implementation when requirements are sufficiently settled; and verification against observable claims. Do not require a ritual sequence or create agents to increase agent count.

Choose execution environment according to task: bounded GitHub Actions work units, Codespaces/Modal for longer exploratory work when available and authorized. Separate shared mutable state and provider quotas. Apply the [canonical destination-first handoff method](../../../docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md#destination-first-execution-and-recovery): establish final artifact home/status and disposable workspace before work, push and verify short recoverable checkpoints during execution, and verify final delivery separately from branch progress. Persist verified test evidence and work-unit position; investigate stale progress with corroborating signals rather than killing a healthy worker solely for unchanged terminal text.

**When drafting an autonomous-run or multi-agent launch brief, read `skills/current/compact-prompt/SKILL.md` first and apply its source-admission gate.** An orchestration assignment is not automatically a frozen build packet: when a delegated work unit is a substantial bounded implementation, additionally read `skills/current/compile-build/SKILL.md` and the active canonical `docs/methodology/ASES Bounded Project Build Method.md` for that work unit. Do not load superseded prompt skills merely because an older PR cites them. Before actual model dispatch use `skills/current/agent-launch/SKILL.md`; for independent reviews use `skills/current/review-launch/SKILL.md`. Keep current decisions in the work issue and canonical repo; don't reconstruct settled meaning from obsolete Crosslink/VPS runbooks. End with a verified result or a specific blocker.
