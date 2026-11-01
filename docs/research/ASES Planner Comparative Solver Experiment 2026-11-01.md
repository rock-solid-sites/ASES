---
title: ASES Planner Comparative Solver Experiment — 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Resource Planner Requirements and Behavioral Model 2026-11-01.md
  - docs/research/Resource Planner Mechanism and Realization Survey 2026-11-01.md
related_documents:
  - docs/research/Resource Planner Realization Selection Gate 2026-11-01.md
  - docs/research/Paseo Resource Planner Parallel Track and Identity Domains 2026-11-01.md
last_updated: 2026-11-01
---

# Comparative solver experiment: exact scheduling, direct CP-SAT and MiniZinc

**Status:** completed *narrow research experiment*, NOT a maintained implementation selection or proof of production scheduling, authorization, financial accounting or untrusted-provider security. All data is synthetic; source changes remain on the feature branch, not main.

## Execution evidence

- **Accepted GitHub Actions run:** https://github.com/rock-solid-sites/ASES/actions/runs/41261372360
- **Tested revision:** `607c61bcfb088fe4ed693a2e7d2bfb8d96c2d1b5` on `feature/paseo-resource-planner-identity-scopes`
- **Run result:** `success`; `results.json` reports `allPass: true` for **38 recorded result rows** (different backend/fixture combinations, not 38 independent requirements).
- **Artifact:** `ases-solver-synthetic-comparison`, ID `13065082848`, under the run; retained through approximately November 15, 2026 (workflow retention 14 days).
- **Source:** `tools/resource-planner-research/`; reference fixtures `fixtures/*.json`, common validator `common.py`, independent enumerator `exact.py`, direct solver `cpsat.py`, MiniZinc model `scheduling.mzn`, runner `minizinc_run.py`, harness `research_run.py`.
- **Environment:** GitHub-hosted Ubuntu 24.04 / Linux 7.0.0-1017-azure x86_64; 4 reported CPUs; Python 3.12.15; OR-Tools Python package 9.14.6206; MiniZinc 2.10.0 with Gecode 6.4.0 and Chuffed 0.14.0.
- **Process measures:** GNU `/usr/bin/time` peak RSS, Python `time.perf_counter()` subprocess wall time. Warm/cold library caches, OS scheduling, Python start and solver CLI startup affect comparisons; **not measurements on HOSTKEY/TNA or representative ongoing workloads**.

## Results, exactly as established

| Mechanism | Status counts in final run | Median full-process wall time | Median peak RSS | 12-stage / 30-stage makespan |
| --- | --- | ---: | ---: | --- |
| Pure-Python small-graph exact search | 6 OPTIMAL, 1 INFEASIBLE, 2 SKIPPED_TOO_LARGE | 20.1 ms | 12,160 KB | intentionally not run with full search |
| OR-Tools CP-SAT, direct Python model | 8 OPTIMAL, 1 INFEASIBLE | 292.3 ms | 115,564 KB | 23 / 52 min, both OPTIMAL |
| MiniZinc + Gecode | 8 OPTIMAL, 1 INFEASIBLE | 106.1 ms | 21,520 KB | 23 / 52 min, both OPTIMAL |
| MiniZinc + Chuffed | 8 OPTIMAL, 1 INFEASIBLE | 98.8 ms | 17,148 KB | 23 / 52 min, both OPTIMAL |
| Shared preflight invalid-input case | 1 REJECTED_INVALID_INPUT | n/a | n/a | n/a |
| Exact-search forced node-budget case | 1 UNKNOWN | 20.1 ms | 12,160 KB | n/a |

Measured medians include the applicable timed infeasibility case and are **not** solver-only iteration times. A Python OR-Tools process has a different import/native-library footprint than a MiniZinc binary; a smaller measured process does not prove Gecode/Chuffed use less memory for a more complex model, nor that MiniZinc is the smallest overall distributable dependency.

Individual 30-stage figures: CP-SAT 341.86 ms / 116,328 KB; Gecode 149.16 ms / 24,444 KB; Chuffed 348.31 ms / 21,584 KB. Chuffed has the fastest aggregate median on these fixtures but **not** the fastest 30-stage run. On the 3-stage F01 counterexample, all returned the proven **32-minute** optimum versus the **52-minute** placement from v0.

### Scope of validation

- **F01** task-order counterexample; **F02** project-domain eligibility; **F03** reviewer vs builder workspace independence; **F04** dependency-dependent inter-host transfer; **F05** simple co-location transfer; **F06** machine-minute quota; **F08** retired-resource infeasibility; **F09** malformed negative duration; **F10** forced exact-search `UNKNOWN`; **F11/F12** 12- and 30-stage examples.
- **Expected optimum is now a hard assertion** on each applicable verified test, rather than passing if a solver merely returns an unproven feasible status. For 12/30 stages the expected fixture values 23/52 were established from tested solver results and retained as regression values, not from an independent mathematical lower-bound proof.
- The shared `common.check_plan` function independently verifies the returned schedule's dependency/order, mode duration, resource no-overlap, simplified quota, independence and budget. The solver implementations therefore differ while **input eligibility and output checking are shared**. This is not independent proof of account isolation.
- Every external solver agreed on all finite numerical fixtures. The original exact enumeration independently proves the 32-minute F01 optimum by exhausting orders and matching the machine workload lower bound. For 12/30 stages, optimality is the solver-reported status for the simplified model, not a full formal audit of backend internals.

### Actual failure and repair

Run https://github.com/rock-solid-sites/ASES/actions/runs/41261098790 initially installed MiniZinc but Gecode could not start: `libEGL.so.1` was absent on the Ubuntu runner. The run was **failed**, despite CP-SAT and Chuffed returning valid outputs. Installing Ubuntu `libegl1` in the isolated workflow corrected the runtime dependency; a later run was successful. This demonstrates the difference between published binary availability and actual deployment dependencies. The MiniZinc bundle archive download was approximately **77.5 MiB**; its installed-size, packaging and overall trusted-base analysis remain open.

## What the experiment DOES NOT establish

The simplified model has **one task occupying a resource at a time**, integer-minute durations, per-machine quota limits, synthetic price ceilings, fixed dependency-transfer penalties, alternate execution mode choices and shared input prefiltering. It does not handle real-world account-level subscriptions and multiple owned resources; cross-reset model-token/API windows; distinct GB-hours/core-hours/API credits; dynamic cost of warm reusable workspaces; concurrent sharing of machine cores/RAM; stages already running/pinned; event history and atomic updates; uncertain duration distributions; cost-vs-speed Pareto-front proposals; untrusted account API data; signed source attestations; or cryptographic isolation of credentials.

**F07 pinned completed/running-stage replanning remains untested.** **F10 only proves the exact enumerator labels a one-node-budget exhaustion UNKNOWN**; it is not a full timed cancellation or recovery test of all backends. The current C++-based third-party solver libraries remain within the *trusted-base assessment*, but this experiment did not select a prohibited new standalone implementation language under ASES policy.

The shared input validator is a research preflight, not a verified authorization boundary. No providers, credentials, cloud API quotas, native Paseo sessions, agent/model routes or GitHub production repositories were accessed or changed by the solver code.

## Selection implications and next discriminating tests

1. The original **assignment-only fixed-order scheduler fails** the demonstrable F01 whole-graph requirement. Retain it only as historical behavioral evidence; do not patch it into production by assuming TypeScript/Node is selected.
2. For this **small, on-demand scope**, **MiniZinc invoked through its CLI is now a high-priority realization candidate**: two independent bundled backend solvers, smaller measured process footprint, reasonable startup and no resident optimizer. A declarative solver model may also keep logic independent of UI code without requiring a bespoke general future-compatibility layer. This is an experimental preference, not a decision.
3. Direct CP-SAT remains a serious candidate: it has first-class optional intervals/cumulative scheduling, reports solve bounds and may behave better on richer tasks; the measured 115 MB includes Python package/runtime imports. The exact enumerator is useful as a small-graph behavioral oracle/fallback but fails to prove optimality after a practical node cap for larger graphs.
4. **Before selection:** add F07 pinned/replanning behavior, quota windows with account-level rather than machine-level capacities, and real alternative-plan objectives; measure resource model expression complexity and memory on the chosen VPS after the runbook, and independently review data validation/authority boundaries.
5. **Paseo presently:** only a narrow on-demand input/output adapter is required once actual installed CLI/plugin facilities are verified. Do not shape the core around a hypothetical future management UI or write an always-on daemon absent current necessity.

**Research decision status remains UNRESOLVED for maintained production realization.** Report this result to operator/orchestrator as observed experimental evidence with its limited guarantees, not implementation approval.

## Source documentation

- https://developers.google.com/optimization/cp/cp_solver
- https://github.com/google/or-tools/blob/stable/ortools/sat/docs/scheduling.md
- https://docs.minizinc.dev/en/2.10.0/installation.html
- https://www.minizinc.org/license/
- Existing ASES realization selection method: `docs/methodology/Implementation Realization and Assurance Selection Method.md`
