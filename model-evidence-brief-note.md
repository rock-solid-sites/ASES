---
title: "Model Evidence Brief — Status Note for Next Orchestrator"
tags: ["evidence", "model"]
sources: []
contributors: ["OL2r"]
created: 2026-08-27
updated: 2026-08-27
---

# Model Evidence Brief — Status Note

Doc exists: docs/research/registry/model-evidence-brief.md — v0 instrumentation for live model/capability/failure evidence (append-oriented, machine-readable, raw evidence preserved, taxonomy/scoring deferred).

Read this before re-learning: Much of the brief is ALREADY SOLVED in v1.1 as built — do not rebuild as new work.

Already solved / in main:
- Separation (Capability Registry vs Failure Matrix vs Routing Matrix — distinct, not collapsed) — implemented per brief Separation.
- Model identity as provider+version/revision/endpoint — implemented in Observer evidence bundles.
- Evidence record schema — implemented as Observer bundle manifest + manager-state.json hot-backup off /tmp (fixes F24 ephemerality, now durable).
- Failure observations retain class/symptom + attribution (model|agent|orchestrator|engine|tool_provider|environment|policy_permission|coordination|mixed|unknown) — implemented via convergent-evidence gate and earlyoom attribution (journalctl -u earlyoom) in Observer.
- Orchestrator notes bounded mechanism — implemented as hub position store + durable queue.

Still deferred per brief Scope — do NOT build in v1.1:
- Final taxonomy/sophisticated scoring, automatic routing, capability-based authority, prose Registry generation, historical corpus mining, final scoring.

Next orchestrator: Read the brief as v0 spec, treat the solved items above as DONE, and only build the deferred items when the swarm explicitly calls for them. References: #477 synthesis, observer-swarm-v1.1-resilience.md, server-memory-management.
