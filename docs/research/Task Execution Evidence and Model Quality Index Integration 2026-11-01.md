---
title: Task Execution Evidence and Model Quality Index Integration — Research Handoff
program: EDASES
layer: Research
document_type: Research Framework
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
related_documents:
  - docs/research/Heterogeneous Synthetic Scheduler Comparison 2026-11-01.md
  - docs/research/registry/AI Capability Registry Specification.md
  - docs/research/registry/Model-Routing-Matrix.md
last_updated: 2026-11-01
---

# Task execution evidence, resource observations, and the Model Quality Index

## Purpose and scope

Capture the proposed **data-collection research track** separately from the resource-allocation algorithm investigation. This is a research handoff, not an approved canonical methodology, an implemented collector, or a claim that the existing Model Quality Index (MQI) has already adopted these fields.

ASES/EDASES already studies model capability and model feedback. Task execution evidence should be linked to that research so that model quality, verified engineering output, resource consumption, and prediction accuracy can be studied together. Accurate resource accounting should be independently valuable even if no dedicated optimizer is deployed.

## Connection to the allocation research

The allocation research seeks to distribute work across projects, accounts, agents, models, and execution environments. Resource constraints include CPU, peak RAM, disk, wall-clock and startup time, tool access, concurrency, inference tokens, credit balances, subscription quotas, and reset/expiry times. Accounts own resources; projects may have dedicated reservations or access to permitted shared/borrowed capacity. The VPS, Codex, OpenCode and MiMo are currently shared across projects; Rock Solid Sites account allowances currently serve ASES and HMS; mbd-record has potentially lendable idle allowances. Future independent project accounts should not require schema redesign.

A scheduler needs forecasts of task duration, success probability, memory, credits, and resource availability. Evidence collection supplies measured outcomes, calibration data, and historical baselines. It must not be coupled to one optimizer or imply that the optimizer is authoritative.

## Minimum linked records (proposed, not final schema)

1. **Task definition**: stable task ID, project ID, work category, requirements, dependencies, priority, due window, complexity estimate, and task-definition version.
2. **Execution attempt**: unique attempt ID (multiple attempts per task), timestamps for queued/provisioning/running/verification/completed, agent role/configuration, model/version, inference provider/account, execution environment/account, relevant tool availability and tool versions, code revision, and parent attempt/retry reason.
3. **Forecast snapshot**: prediction timestamp; estimator identity/version (human, model or algorithm); predicted runtime, CPU/RAM, tokens, credits, success likelihood and confidence/uncertainty; assumptions and available-information snapshot ID. Preserve forecasts **before** execution to avoid hindsight leakage.
4. **Observed consumption**: wall time, active compute time, startup/teardown time, peak and sampled RAM/CPU where measurable, tokens by type, quota units, provider-billed charges, allowance changes, and attribution to owning accounts. Record units, measurement windows, provenance and unknown/unavailable fields; do not equate modeled cost with actual billing.
5. **Verified outcome**: completion state, artifacts, tests/independent review results, correctness/quality assessments, regressions, retries, human correction time, and whether the work was useful and accepted. A successful API response is not a verified engineering outcome.
6. **Allocation decision**: candidate plan ID, planner type/model/version, authoritative resource/policy snapshot, competing alternatives, predicted outcomes, chosen plan, validator result, actual outcome and reasons for deviations. Record rejected or unselected proposals where feasible to support later comparisons.

Link records by stable IDs; retain historical model/provider configurations rather than overwriting them when capabilities change. A single task may involve multiple agents, models, attempts, and accounts. The data model must support that many-to-many structure.

## Relationship to the Model Quality Index (MQI)

The MQI concept should be informed by **observed, verified task performance**, not merely subjective model ratings or provider benchmark claims. Potential evidence dimensions include:
- task-type-specific correctness and independent verification rate;
- useful accepted work per unit of elapsed time, tokens, credits, and compute;
- retry, regression, and correction burden;
- reliability under tool and context limitations;
- calibration of predictions (time, resources, cost, success likelihood);
- performance variation by agent role, environment, project, and task difficulty.

These are **candidate inputs**, not a proposed universal single-number formula. Do not collapse different task types, risk profiles or resource currencies into one opaque rank. Separate capability/quality measurement from price and availability, then permit context-dependent routing and decision policies. Report sample sizes, confidence intervals where meaningful, provenance, selection bias, and missing data. Compare like-for-like tasks; account for task difficulty and the fact that stronger models may be assigned harder work. Avoid treating correlated reviewer/model judgments as independent verification.

The existing AI Capability Registry, Model-Routing-Matrix, and model-feedback entries are related research artifacts; this proposal should be reconciled with their actual schemas before implementation. The phrase MQI is a conceptual connection here, not a claim that a particular MQI specification was inspected or modified.

## Two independent consumers of the same evidence

**Model-based planning** may reason about upcoming work, shared reservations, expiring allowances, and opportunities to consolidate jobs on provisioned environments. It may propose options and explain tradeoffs.

**Calculation/optimization tools** should independently enforce eligibility, permissions, budgets, capacity, timing and other hard constraints, estimate outcomes, explore Pareto alternatives, and test model projections. Smaller models should have access to the same calculation functions. Neither model-generated claims nor optimizer output should override authoritative account snapshots or independent validation.

Keep raw measurements, derived estimates, predictions, human judgments, and verified facts distinct. Preserve source timestamps, stale-data markers, and uncertainty.

## Collection and privacy boundaries

Prefer event-based, append-only records plus versioned snapshots; keep raw provider responses or audit references where lawful and practical. Never collect secrets, prompts containing credentials, private code, or personal information merely to improve optimization. Minimize retained content; store structured measurements and references, with access controls by account/project and retention rules. Cross-account lending does not imply cross-account visibility of confidential task data. Provider terms and permission boundaries are hard eligibility constraints.

Collection itself has CPU/RAM/storage/token overhead. Measure overhead and allow lightweight or sampled instrumentation. A local SQLite prototype and exportable schema are possible implementation options, not requirements.

## Independent value before predictive optimization

Useful reporting includes per-project and per-account allowance use; expiring unused credits; cost of verified work by task category; startup and teardown overhead; repeated failure modes; prediction-versus-actual error; agent/model quality by task type; and resource waste from avoidable duplicate provisioning. Distinguish actual from estimated and synthetic values.

## Research and validation plan

1. Inventory the existing model-feedback/MQI and capability-registry concepts; map overlaps and gaps before introducing new canonical terms.
2. Define a minimal versioned event schema and authoritative identity/ownership references; test multi-attempt, multi-model, multi-account and shared/dedicated resource cases.
3. Instrument a small number of representative tasks with low overhead; capture forecast snapshots before dispatch and verified outcomes afterward.
4. Check event completeness, clock and unit consistency, account attribution, missing measurements, replay determinism and provenance; verify that telemetry cannot change scheduling eligibility.
5. Establish retrospective calibration baselines, then prospective blinded comparisons for model-only, algorithm-only and hybrid allocation proposals against the same independent validator.
6. Consider a dedicated execution-engine data service only after sufficient evidence demonstrates its usefulness and acceptable overhead.

## Explicit non-decisions

- No MQI formula, weights or threshold selected.
- No solver, model, database service or cloud provider selected by this document.
- No claim that all provider allowances are transferable, shareable, or even observable through APIs.
- No presumption that a task's measured resource usage generalizes to another environment without calibration.
- No automatic cross-account resource lending without explicit owner policy.

## Handoff

This evidence-collection/MQI track can proceed independently. The active scheduling research should continue investigating multi-project, multi-account, multi-mode, multiobjective, rolling-horizon resource allocation, setup-cost consolidation, and model-versus-algorithm decision quality. Both tracks should eventually share a versioned, provenance-aware data contract.
