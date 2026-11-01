---
title: Portfolio Harness Validation Strengthening — 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
related_documents:
  - docs/research/Portfolio Allocation Harness v0 2026-11-01.md
  - docs/research/Portfolio Harness First Executed Baseline 2026-11-01.md
last_updated: 2026-11-01
---

# Portfolio harness strengthening: independent admission

## Changes committed

- `portfolio_oracle_v1.py`: separate, standard-library, fail-closed admission oracle; does not import the scheduler.
- `test_portfolio_oracle_v1.py`: 11 test methods including 60 seeded mutation cases, malformed inputs, duplicate tasks, account permissions, protected credit budgets, reset boundaries, capacity and mode-specific resource demand/duration.
- `portfolio_harness_v0.py`: planner candidate generation and final run now require **both** the original validator and the new oracle to accept a plan.

## Execution evidence

The GitHub-committed source was reproduced in a separate Python environment, with the oracle and harness integrated. The **existing seven regression tests passed** (7/7, 0.302s), and the harness executed successfully with both validators enabled. Greedy: 5 tasks, 37 on-time value, 7 synthetic credit ticks; beam100: 5 tasks, 37 on-time value, 4 credit ticks. A manually executed set of 15 oracle checks passed 15/15, covering both planners and selected negative cases. The newly committed `test_portfolio_oracle_v1.py` test file **has not yet been executed as a full unittest suite** in this run. These distinctions must not be collapsed into a claim that all committed tests passed.

A Python subprocess emitted an unrelated spreadsheet runtime warmup traceback on stderr; unittest and the harness returned exit code 0.

## Remaining limitations and next gates

1. Validate the complete committed oracle test suite in CI and run mutation/property testing at larger scale.
2. Strengthen snapshot schema checks before planning, including account budgets even when unused, dependency cycles, malformed project identities and all eligible mode definitions.
3. Support partial task completion semantics, frozen in-flight tasks, and consistent accounting for credit-consuming modes.
4. Model reset/expiry as actual timeline transitions. Current oracle rejects a single job crossing a reset boundary rather than splitting usage; this is a conservative provisional rule, not a general provider policy.
5. Introduce multiple distinct shared allowance pools and billing currencies; current accounting assumes each environment charges one owning account.
6. Add deterministic seeded scenario generation with realistic task variability, and separate optimization quality from validator correctness.
7. Keep environment placement undecided; benchmark planner CPU, wall-clock and memory separately.

All quotas, costs, project workloads and mode profiles remain synthetic. No live cloud resources were allocated or consumed.
