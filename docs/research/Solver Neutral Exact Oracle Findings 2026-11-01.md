# Solver-neutral exact-oracle comparison — 2026-11-01

## Decision status

**No engine selected.** Pumpkin, Chuffed, Gecode, OR-Tools and MILP remain comparators. Exact small-instance benchmarks establish an optimization gap but do not justify a general-purpose solver for ASES.

## Provenance and method

- Source graph: `docs/research/fixtures/tripn-beds24-document-derived-v0.json` (D-tier dependencies, not actual execution chronology).
- Resource/duration envelope: `docs/research/fixtures/tripn-synthetic-s0.json` (S-tier invented, not observed).
- Baseline: deterministic longest-duration-ready-first, earliest resource-feasible placement.
- Reference: time-indexed binary mixed-integer program using SciPy/HiGHS; binary stage start, exactly one start per stage, precedence, per-tick RAM/CPU/slots, makespan minimization. Status 0 and gap 0 are necessary for claiming a proven optimum.
- Independent checks: stage coverage, exact duration, dependencies, and per-minute RAM/CPU/slots. This is **not** production runtime admission control.
- Local reference run: Python with SciPy installed, 2026-11-01. Upstream solver implementation is native code; this is a benchmark oracle, not a proposed Rust dependency.

## Results

| Closed subset | Capacity (MiB / millicores / slots) | Greedy makespan | Certified optimum | Excess | Exact runtime |
|---|---|---:|---:|---:|---:|
| 6 stages | 4096 / 2000 / 2 | 86 | 86 | 0 | 0.902s |
| 6 stages | 8192 / 4000 / 4 | 49 | 49 | 0 | 0.350s |
| 8 stages | 4096 / 2000 / 2 | 87 | 83 | 4 min (4.82%) | 1.343s |
| 8 stages | 8192 / 4000 / 4 | 65 | 65 | 0 | 0.238s |
| 10 stages | 4096 / 2000 / 2 | 103 | 99 | 4 min (4.04%) | 3.368s |
| 10 stages | 8192 / 4000 / 4 | 81 | 81 | 0 | 0.697s |

Every MILP run reported status 0 and zero optimality gap. Each solution was separately checked. These results were obtained from the local benchmark prototype. The repository version of the reference script was committed afterward and **has not yet been rerun in CI**.

## 18-stage heuristic smoke benchmark

| Capacity | Feasible synthetic makespan |
|---|---:|
| 4096 MiB / 2000 millicores / 2 slots | 187 min |
| 8192 MiB / 4000 millicores / 4 slots | 95 min |
| 4096 MiB / 2000 millicores / 2 slots; outage [0,15) | 202 min |

These are feasible schedules only, **not optimality results**. No valid 18-stage optimality gap has yet been established.

## Risks and methodological limitations

1. Six instances from one synthetic family are insufficient for engine selection; workload topology and resource demand distributions must vary independently.
2. Small-subset selection and the synthetic demand values may favor the baseline; report exact subsets and seeds.
3. Current `heuristic_v0.py` tests resource demand by summing all jobs that overlap the *candidate interval*. Such jobs may not overlap each other. This is conservative and can reject feasible placements; replace with event-point checks and a red/green regression before interpreting baseline quality.
4. The reference MILP uses minute ticks and an all-serial upper bound. Increasing horizon or stage count can dramatically increase variables and solve time; benchmark memory, termination, lower bounds, and timeout behavior.
5. Independent feasibility checks establish feasibility under the model, not the correctness of resource estimates or model completeness. Do not equate zero solver gap with independently verified optimality proof.
6. Current `validator_v1.py` requires an independently supplied environment snapshot, but schema, trust freshness, quotas, budget, typed units and runtime admission are intentionally incomplete.
7. Baseline objective is makespan only. ASES ultimately needs cash, resource pressure, quotas and disruption/replan churn.
8. The 8 GiB synthetic case must not be interpreted as 8 GiB actually free on the VPS.

## Next evidence gates

- Reproduce all tests from committed repository files in CI, including expected-failure tests and actual process peak RSS.
- Fix conservative overlap bug red-to-green, then rerun comparisons; baseline results may improve.
- Add independent exhaustive oracle for 3–6 jobs and property-based differential testing; do not depend exclusively on HiGHS as an oracle.
- Benchmark at least 30 distinct instances across 6/12/18/30/60 stages, with seeded topologies, resource distributions, deadlines and outages. Report best feasible objective, proven lower bound, gap, cold runtime and peak RSS.
- Compare Rust specialized heuristic and bounded local improvement first; introduce Pumpkin and other engines only if baseline gaps justify integration costs.
