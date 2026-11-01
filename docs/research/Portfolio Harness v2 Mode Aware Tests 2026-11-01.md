---
title: Portfolio Harness v2 — Mode-aware scheduling and generated DAGs
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-01
---

# Portfolio harness v2

## Changes

A separate mode-aware planner, `research/resource-solver/portfolio_harness_v2.py`, avoids altering the v0 baseline. Candidate durations and credit costs now come from the selected execution mode, and every candidate is checked by the independent `portfolio_oracle_v1.validate` gate. Task ordering is topological, and cycles raise an error. Both greedy and bounded beam-search are deterministic for a fixed snapshot.

`test_portfolio_v2.py` includes ten targeted checks for scheduling, reset boundaries, mode demand, dependencies, invalid inputs, determinism, immutability and credit limits.

`portfolio_scenarios_v2.py` generates independent seeded DAGs across three projects and two execution environments, with variable durations, resources, deadlines, values, modes and dependencies. Its default evaluation compares 20 eight-task scenarios for both planners; this generated suite is committed but **has not yet been executed**.

## Execution evidence

The v2 planner, its ten tests, and the previously committed oracle source were reproduced locally in a Python environment. Command:

```sh
cd /mnt/data/ases_round
python3 -m unittest discover -p 'test_portfolio_v2.py' -v
```

Result: **10/10 tests passed in 0.007 seconds**. This is not a GitHub Actions run or an execution of a clean GitHub checkout. No general performance claim is justified.

To reproduce from a repository checkout:

```sh
python3 -m unittest discover -s research/resource-solver -p 'test_portfolio_v2.py' -v
python3 research/resource-solver/portfolio_scenarios_v2.py
```

## Important outstanding correctness issues

1. The independent oracle does not yet bind a candidate to an immutable snapshot ID/version or enforce atomic admission against concurrent updates. Stale snapshots and account races remain unsafe.
2. A task spanning a credit-reset boundary is rejected rather than split into per-period charges; this is a deliberate v1 limitation, not full reset support.
3. The oracle does not preflight all nested mode overrides, does not detect arbitrary cycles in an unused DAG, and does not enforce frozen running work. Additional malformed-input tests and explicit graph preflight are needed.
4. The generated DAG evaluator has not been run, and no exact optimum or independent reference has been established for those instances.
5. The v2 planner's ranking is heuristic. Beam width is a search bound, not an optimality certificate. Late work may be admitted and consume capacity.
6. The model does not yet include credit expiry, startup/teardown delay, account owner reclaim, inference quotas, multi-currency budgets or dynamic arrivals.
7. Runtime placement remains out of scope; measure solver runtime and peak memory separately.

## Next gates

Run the generated suite, independently cross-check small DAGs with exhaustive enumeration, and add mutation/property tests that specifically expose stale snapshots, nested mode errors, account race conditions and frozen-task changes. Do not use the oracle for production admission until these are implemented.
