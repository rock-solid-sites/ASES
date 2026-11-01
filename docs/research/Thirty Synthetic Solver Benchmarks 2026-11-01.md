# Thirty synthetic scheduling benchmarks — 2026-11-01

## Status

30/30 deterministic earliest-fit schedules passed independent per-tick dependency and CPU/RAM feasibility checks. 18 exact SciPy/HiGHS reference runs were attempted (5-second limit each): **16 certified optima**, **2 timeouts**. The remaining 12 cases (30/60 stages) were NOT run through exact MILP; only an analytical lower bound was computed. This is **not** a comparison of 30 optimization engines or 30 real ASES executions.

These are **new seeded synthetic random DAGs**, not the document-derived TripN 18-stage graph. Cases have 6, 10, 18, 30 or 60 jobs; six seeds per size; capacities 2/3/4 units for both CPU and RAM. Job durations are random 2–8 ticks; CPU/RAM demand 1 or 2 units. Seeds 1101–1130. Baseline is longest-ready-duration-first with earliest-fit placement. The exact oracle uses time-indexed binary MILP and HiGHS. This experiment measures makespan only. It does not model heterogeneous machines, quotas, credits, cash cost, startup, security or frozen replanning.

## Results

| Size | Cases | Baseline makespans, six seeds | Certified optima / attempted |
|---|---|---|---|
| 6 | 1–6 | 27,16,18,14,15,13 | 6/6 |
| 10 | 7–12 | 49,36,24,46,31,21 | 6/6 |
| 18 | 13–18 | 69,49,36,80,58,46 | 4/6 |
| 30 | 19–24 | 106,65,83,114,90,60 | not attempted |
| 60 | 25–30 | 232,156,125,248,145,103 | not attempted |

Certified optimum results: case 1 27; 2 16; 3 18; 4 14; 5 14; 6 13; 7 39; 8 30; 9 23; 10 38; 11 28; 12 20; 14 37; 15 31; 17 56; 18 45.

Among these 16 certified cases the **mean per-case relative baseline excess** was 9.265% (unweighted). Do not extrapolate this to real ASES work.

Timeout cases: 13 (incumbent 86, bound 38, while independently verified greedy schedule 69), 16 (no returned incumbent or bound). An incumbent worse than the known greedy schedule is not evidence that the greedy schedule is invalid; the reference model did not receive the greedy incumbent as a warm start.

For 30/60-stage cases, analytic lower bound = max(critical path, ceil(total CPU work/capacity), ceil(total RAM work/capacity)); these are **lower bounds, not optima**. Case: (baseline, bound): 19 (106,88), 20 (65,55), 21 (83,66), 22 (114,96), 23 (90,74), 24 (60,54), 25 (232,209), 26 (156,146), 27 (125,106), 28 (248,211), 29 (145,128), 30 (103,93).

## Interpretation

- Feasibility was easy for this simplistic, homogeneous resource model; finding a **provably optimal** plan became substantially harder.
- The baseline is materially suboptimal on some certified cases (e.g. case 7: 49 vs 39; case 14: 49 vs 37).
- The reference MILP is unsuitable as an unbounded default on constrained machines without a strict time/memory budget and a feasible incumbent.
- These results justify comparing **bounded local improvements and specialized Rust scheduling** against general-purpose engines, but do not select an engine.

## Methodological limitations

1. Homogeneous CPU/RAM, integer units, fixed duration, no deadlines, quotas, price, transfer, failures or multiple environments.
2. 30 generated cases, only 16 proven optima. 12 large instances were not exact-solved.
3. The generator and baseline used Python; process startup, RSS and CPU usage were not separately profiled. In-process scheduling measurements are not end-to-end wall time.
4. Random DAG generator uses preceding-index dependencies, with at most two predecessors; may not represent actual ASES workload structure.
5. Feasibility check is separate code but in the same benchmark file, not a cross-language proof or production gate.
6. The source and complete 30-case JSON results were generated locally; they must be attached or committed before claiming reproducible GitHub CI.
7. Analytic lower bounds can be weak; baseline-to-bound ratio is not an established optimality gap.

## Decision

**Keep engine selection open.** Next test bounded swap/insertion/local search against this same corpus, validate each result independently, and then introduce heterogeneous resource/credit constraints. Evaluate whether the quality gains outweigh runtime and memory overhead. Preserve the fixed resource-snapshot trust boundary.
