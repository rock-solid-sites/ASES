# ASES solver-mechanism experiments (2026-11-01)

**Research-only.** These files exercise a restricted, synthetic scheduling model; they do not select an implementation language, authorize paid compute, access credentials, reproduce real provider quotas, or launch a Paseo worker. They are independent of the experimental Node/TypeScript planner and its implementation assumptions.

## Shared model

Fixtures use a fixed integer-minute horizon, account-scoped resources, a bounded price in *synthetic cents*, single-task-per-machine constraints, per-machine minute quotas, alternative execution modes, dependency-induced transfer minutes, and builder/reviewer resource separation. All duration/price data are hypothetical. The scenarios are deliberately narrow: per-provider quota reset, GB-hours, token-cost windows, dynamic cache state, multi-stage resource occupancy, concurrent writes, running stage pinning, and real trust boundaries **are not modeled**. `F05-co-location` tests a conditional move cost, not a full persistent-warm-workspace cost model. F07 (running/completed-stage replanning) is unimplemented in this comparative suite; do not count it as passing.

All candidate outputs are checked against a separate `common.check_plan` verifier. Statuses differentiate proven optimum, proven infeasibility, feasible without proof, unknown and process failure. Independent hard feasibility verification is necessary but does not establish that the model faithfully represents cloud provider terms.

## Mechanisms under test

- `exact.py`: disposable pure-Python oracle that enumerates eligible modes and all ready-task orders, inserting jobs at earliest non-overlap gaps. For deliberately small no-preemption/no-calendar scenarios, this provides a reference result; search bounded at 50,000 nodes and skipped on 12+/30-stage fixtures. No claim about general RCPSP optimality.
- `cpsat.py`: direct Google OR-Tools CP-SAT model (fixed/alternative interval constraints, no-overlap, quotas, budget, conditional inter-host transfer and exclusion), one search worker, 3-second timeout.
- `scheduling.mzn` + `minizinc_run.py`: one MiniZinc declarative model, run separately with Gecode and Chuffed under the same 3-second per-fixture limit. Its modeling/compiler overhead is deliberately visible.

All use the same JSON fixtures under `fixtures/`, with any ineligible resource removed by a shared preflight layer. As a result the comparison tests **solving mechanisms on common admissible inputs**, not separate independent security-domain implementations. That preflight is research code, **not an approved production security guard**.

## Reproduction

Research host environment: Python 3.12, `ortools==9.14.6206`, MiniZinc bundled CLI 2.10.0 with Gecode and Chuffed; `/usr/bin/time` for peak RSS. GitHub Actions workflow `resource-planner-research.yml` runs only on the research feature branch, with no credentials and `permissions: contents: read`.

From this directory:

```sh
python3 make_fixtures.py
python3 research_run.py
```

Results are printed and written to `results.json` (GitHub Actions artifact), including host/platform, solver versions, time, peak RSS, objective and the returned schedule. Do not compare process RSS from different machines as if they were identical. The MiniZinc bundle is a separate process/runtime; OS cold start, library cache and solver versions matter. Measurements are comparative only for this specific GitHub runner, not the target VPS.

## Acceptance and research scope

F01–F06 and F08 are executable finite scheduling fixtures; F09 tests malformed-data rejection. F11 and F12 measure 12- and 30-stage instances with solver time limits. F07 and F10 are specified in the requirements research but *not* fully tested; unknown/time limit classification is partially exercised where solvers hit limits. F06 verifies machine-minute caps, not distinct real-world account quotas with resets.

Critical research question: does a serious solver correct the known F01 52-minute result to the proven 32-minute optimum, while keeping resource and identity eligibility sound and providing low enough on-demand memory/process overhead?

No architecture decision should be made from one synthetic benchmark. Next add adversarially constructed provider-unit profiles and actual Paseo/OpenCode telemetry after integration reaches the required trust boundaries.
