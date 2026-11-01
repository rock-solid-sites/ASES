---
title: Portfolio Harness Expanded Test Results 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-01
---

# Expanded portfolio harness tests

## Execution and result

The source of the committed portfolio harness and independent oracle was reproduced in an isolated local Python environment, updated to match this round's source changes, and executed with:

```sh
PYTHONPATH=/mnt/data/ases_portfolio_test python -m unittest discover -s /mnt/data/ases_portfolio_test -p 'test_portfolio*.py' -q
```

**36 tests passed in 6.130 seconds** (Python 3.13.5). This is not a GitHub Actions CI run. The final tests were executed in the local container against matching source, not pulled as a complete repository checkout. The test names and source are committed for CI reproduction.

## Test coverage

- Original seven regression tests.
- Independent-oracle eleven tests, including 60 seeded invalid-plan mutations.
- Nine additional stress tests: shared-account spending, exact budget boundary, nonoverlapping endpoints, permutation invariance (25 seeds), monotonic CPU/RAM/slot increases (30 seeds), monotonic allowance increases (30 seeds), 40 seeded portfolio variations evaluated by both greedy and beam, 100 seeded malformed-plan mutations, and a two-task exhaustive optimum reference.
- Nine whole-snapshot preflight cases: malformed unused account budgets, unused environment capacities, unknown account owner, invalid task duration/dependencies/modes, boolean CPU demand and invalid allowance period.

The 36 figure is the number of unittest methods, **not** the number of subcases or generated scenarios.

## Defects found and fixed

1. **False-negative test setup**: the original shared-credit overspend test set RSS credits to 5 and reserve to 3, allowing 2 units, while the fixture consumed exactly 2. The test was corrected to credits 4, reserve 3, making the consumption exceed the permitted 1.
2. **Incomplete snapshot preflight**: the independent oracle previously checked budgets and environment capacities only when used. It now rejects invalid unused accounts, environment capacities, account owners and basic task definitions before admission.

## Current limits and unverified properties

- All resource quantities, allowances, project values and deadlines are synthetic.
- This is one fixed five-task portfolio with seeded variations, not 40 independently generated task graphs.
- The oracle currently supports only single-period charging for tasks wholly within one account period. It rejects jobs crossing reset boundaries rather than allocating charges across periods.
- The planner's legacy validator still assumes task duration and demands are independent of execution mode. Therefore mode-specific scheduling and charging are **not** yet correctly implemented end-to-end; only the independent oracle's rejection checks cover mode overrides.
- Snapshot freshness/version binding, task graph cycle detection, stale policy races, frozen tasks, expiry/credit reset semantics, concurrent admission and actual provider billing remain incomplete.
- Greedy and beam are heuristics; the exhaustive reference covers only a tiny instance, not the five-task fixture.
- A clean CI checkout and test run is still needed.

## Next gates

1. Repair the planner/oracle mismatch for mode-specific durations, CPU/RAM and credit costs; make all scheduling candidates use the same authoritative mode interpretation.
2. Add schema/versioned snapshot identity, dependency cycle detection and mutation/replay tests for policy changes.
3. Add multiple generated DAG families, larger stress sizes, true rolling-horizon resets and expired allowance scenarios.
4. Build an independent brute-force oracle for several small instances to quantify solution quality and missed alternatives.
5. Record wall time, CPU and peak memory for each algorithm and scenario, with identical input data.
