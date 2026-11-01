# Independent feasibility gate — requirements and acceptance criteria (2026-11-01)

## Architectural decision

**No schedule may be dispatched unless an independently implemented validator accepts it.** Feasibility validation is part of the ASES resource-control boundary, not an optional solver debugging feature. A solver's SAT/optimal result is not permission to execute.

Three independent layers:
1. **Input preflight**: validate the authoritative WorkGraph, environment snapshot, resource estimates, units, IDs, dependencies, capabilities, and policy constraints before solving. Reject cycles, duplicate IDs, negative/unknown resource estimates, impossible domains, inconsistent snapshot versions and integer overflow.
2. **Candidate acceptance**: validate a solver-produced plan using the authoritative input, not values supplied by the solver. Check all stages, precedence, start/end/duration, allowed environment and data class, CPU/RAM/slots at every change point, time-varying quotas/credits, hard budget, setup/transfer/cold-start, maintenance windows, secret boundaries, frozen/completed work, reservations, and artifact requirements. Recompute objective independently.
3. **Dispatch-time admission**: immediately before each launch, recheck real observed free RAM/CPU, current quotas, host health, in-flight reservations, credentials/capabilities and snapshot freshness. Atomically reserve resources or reject and replan. A previously valid plan may become infeasible because conditions changed.

## Critical distinctions

- **Estimated versus actual**: solver capacity checks apply to explicitly versioned *estimated* resource envelopes. No offline feasibility proof guarantees runtime memory usage. The dispatcher must use headroom, telemetry, runtime limits, and stop/replan controls.
- **Soundness versus completeness**: a validator can confirm that a proposed schedule satisfies encoded rules; it cannot prove that no other feasible schedule exists. Optimality requires a separate proof/bound/oracle, and model adequacy requires independent tests.
- **Uncertainty**: null historical resource measurements must not silently become zero. Unknown estimates require explicit synthetic assumptions or a fail-closed policy.
- **Identity**: bind schedule to hashes/versions of the WorkGraph, EnvironmentSnapshot, policy, estimate set and objective. Any mismatch invalidates acceptance.
- **Safety and language**: production gate should be implemented in memory-safe Rust with checked integer arithmetic and structured error codes. Python standard-library checker remains an independent prototype and cross-language oracle.
- **Trust separation**: avoid sharing solver constraint-generation functions with the validator; otherwise one translation bug could cause both to agree incorrectly.

## Required invariants

A. Every required stage scheduled exactly once; optional stages obey inclusion/exclusion dependencies; no unknown/duplicate stage IDs.
B. Acyclic dependencies and precedence, including artifact availability and transfer latency.
C. Start/end times and durations in integer ticks; no overflow, negative time, or illegal horizon.
D. Environment eligibility, capabilities, permitted data classes and secret boundaries.
E. Per-environment instantaneous RAM, CPU and concurrency capacity, plus other scarce resources where modeled.
F. Quota/credit consumption and reset windows, cost ceiling, pricing/expiry policy and hard deadlines.
G. Outages, availability windows, startup/shutdown, cache and data transfer constraints.
H. Frozen stages cannot move; running reservations count against capacity; failures cannot erase completed evidence.
I. Reported objective equals independently recomputed cash, makespan and churn scores.
J. Unknown, missing or stale input yields **reject** rather than a default permissive schedule.

## Verification matrix

- Positive and negative unit tests for every invariant.
- Boundary tests at exact resource capacity, equal timestamps, reset/expiry boundaries and zero-length tasks.
- Mutation and property-based tests generating invalid plans; differential tests against small exact oracle and independent implementation.
- Replay real TripN GitHub Actions execution trace; document-derived 18-stage graph with separate synthetic estimates.
- Concurrent admission race tests, stale-snapshot injection, host outage, quota exhaustion, solver timeout, maliciously understated resource demand and cancellation.
- Fault injection for partial dispatch, lost acknowledgements, retries, duplicate jobs and telemetry loss.
- Ensure errors are stable machine-readable reason codes, include stage/environment, policy revision and evidence reference.

## Implementation order

1. Upgrade Python reference validator to canonical integer units, authoritative demand lookup and structured error codes; complete schema and negative tests.
2. Add independent Rust validator, no Pumpkin dependency. Cross-language differential testing on identical fixtures.
3. Implement minimal Pumpkin scheduling adapter. Require Rust validator pass before any dispatch.
4. Implement atomic runtime reservation/admission control and event-sourced evidence of decisions.
5. Add quota, budget, credentials, cache, failure recovery and concurrent orchestration tests.

## Current status

A local Python v1 prototype passed 13 unit tests for a subset of requirements, but that local implementation is **not yet committed or production verified**. The committed earlier Python prototype was amended to reject resource demand mismatches where authoritative fixture values exist. Neither currently constitutes the full gate specified above. No Rust adapter or Rust validator has been compiled or benchmarked.

Upstream Pumpkin API: https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/ ; cumulative resource constraint: https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/fn.cumulative.html
