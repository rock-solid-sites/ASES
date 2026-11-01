---
title: Portfolio Allocation Harness v0 — Scope and Execution
program: EDASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
related_documents:
  - docs/research/Heterogeneous Synthetic Scheduler Comparison 2026-11-01.md
  - docs/research/Task Execution Evidence and Model Quality Index Integration 2026-11-01.md
last_updated: 2026-11-01
---

# Portfolio allocation harness v0

## Runnable files

- `research/resource-solver/portfolio_harness_v0.py`: synthetic scenario, standalone validator, greedy and bounded beam-search planner, metrics, JSON output.
- `research/resource-solver/test_portfolio_harness_v0.py`: unit tests.

Run from repository root:

```sh
python3 research/resource-solver/portfolio_harness_v0.py
python3 -m unittest discover -s research/resource-solver -p 'test_portfolio_harness_v0.py' -v
```

No third-party packages required. These commands have **not yet been executed against the committed version**; do not treat the presence of tests as a passing test report.

## Scope and caveats

This is a small *synthetic* first common harness, not a production optimizer, verified account inventory, exact solver comparison, or multiweek forecast implementation. Seven discrete day-sized ticks are used as a deliberately coarse horizon. Credits are synthetic duration ticks, not actual cloud or inference billing units. Account credit resets and expiry are recorded as fixture metadata but are **not yet implemented as time-varying constraints**. Model quality, task failures, inference allowance coupling, dynamic arrival, probabilistic forecasts, frozen running tasks, storage quotas, provider-specific instance lifecycle, and independent external admission are not yet modeled.

The burst environment's startup units appear in the reporting metric only; they do not delay task start or consume a monetary budget. A single startup charge per environment is a simplification; actual lifecycle events, reuse gaps and billing granularity require separate modeling. The baseline objective prioritizes on-time value, not a complete Pareto frontier. The beam search is heuristic and not a mathematical proof of optimality. It can omit tasks, and beam width does not guarantee finding the best plan.

The existing `validator_v1.py` remains a separate validator for the older stage-based fixture; the new harness uses its own small portfolio validation function. An independent portfolio-policy oracle remains necessary.

## Immediate next gates

1. Execute and record tests and deterministic JSON output; fix any failures.
2. Add property tests for duplicate tasks, malformed snapshots, overcommit, budget double spend, owner reclaim, expiry/reset, partial plans, and policy changes.
3. Model task modes with different durations, model quality and token/credit costs; account for multiple concurrent billing currencies.
4. Model environment provisioning, idle retention, startup latency, teardown and capacity interference.
5. Compare greedy/beam against CP-SAT, MILP and bounded local search on the same instances and with identical independent feasibility checks.
6. Add rolling seven- and thirty-day forecasts, surprise arrivals and replan stability; report Pareto alternatives rather than only one scalar score.
7. Benchmark planning runtime, peak RAM and remote execution overhead independently from workload resource consumption.

## Optimizer placement: not VPS-bound

The optimizer should be a portable pure function of an authoritative resource/policy snapshot, task portfolio, planning horizon and bounded compute budget. It should emit candidate plans, explanations and provenance. An independent admission gate checks proposals before any execution.

A Cloudflare Worker is a candidate execution target for lightweight heuristics, small WASM solvers, and plan validation. Larger CP-SAT/MILP instances may require a different remote compute service, asynchronous execution or decomposition. Do not assume a Worker supports arbitrary native binaries, unrestricted CPU time or sufficient memory. Verify the current plan-specific Worker CPU, memory, request-duration, subrequest, WASM and storage limits before choosing deployment. A Worker-hosted optimizer avoids competing for VPS CPU/RAM but still consumes Worker allowances and incurs data-transfer, latency and potential privacy costs. A remote solver should not receive secrets or unnecessary private task content.

Keep optimizer location a *resource allocation decision* in its own right; compare local, Worker, and other cloud execution on total cost and reliability rather than treating VPS capacity as the default.
