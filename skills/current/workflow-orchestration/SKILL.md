---
name: workflow-orchestration
version: 1.0.0
description: Select the smallest evidence-driven recon, review, test, build or synthesis loop with isolated work.
status: current
---

# ASES workflow orchestration

Inspect current evidence and identify the smallest unresolved question. Choose targeted recon when the mechanism is unknown; independent parallel tests for separable hypotheses; synthesis for conflicts; implementation when requirements are sufficiently settled; and verification against observable claims. Do not require a ritual sequence or create agents to increase agent count.

Choose execution environment according to task: bounded GitHub Actions work units, Codespaces/Modal for longer exploratory work when available and authorized. Separate shared mutable state and provider quotas. Persist commits, verified test evidence and work-unit position; investigate stale progress with corroborating signals rather than killing a healthy worker solely for unchanged terminal text.

Before launching use `skills/current/agent-launch/SKILL.md`; for independent reviews use `skills/current/review-launch/SKILL.md`. Keep current decisions in the work issue and canonical repo; don't reconstruct settled meaning from obsolete Crosslink/VPS runbooks. End with a verified result or a specific blocker.
