# Bounded priority-list local search: 30-case comparison (2026-11-01)

## Decision
**Promote bounded local search to the next prototype candidate, not the final engine.** Retain the simple deterministic feasible scheduler as the always-available fallback. Keep Pumpkin and other solvers unselected pending representative heterogeneous, quota, and replan workloads.

## Experimental setup
- Identical 30 seeded synthetic DAGs and resource capacities as `Thirty Synthetic Solver Benchmarks 2026-11-01.md` (6/10/18/30/60 stages; six cases each; seeds 1101–1130).
- Deterministic priority-list scheduler, longest-ready-duration-first baseline.
- Local search: 400 iterations, deterministic seed `seed+99173`; 65% swap and 35% insertion proposals; accept nonworsening current solutions, periodic restart; reconstruct earliest-feasible schedule for each priority permutation.
- Every best-solution improvement checked by separate minute-by-minute resource/dependency validator; final solution validated again. Replay determinism tested across 15 additional combinations.
- Python local run; 30×401 candidate schedules; fixed iteration budget, **not a time or memory bound**. Timings include greedy plus local optimization and validation, not process startup. CPU/RSS not measured.
- Historical exact oracle results: 16 certified optima, two timeouts, 12 larger cases not exact solved. No new exact solver runs in this experiment.

## Results
- **30/30 feasible**; **24/30 improved**; none worsened; 146 total synthetic makespan ticks saved.
- Mean relative makespan reduction across all 30: **7.34%**.
- Mean baseline excess above certified optimum across 16 cases: **9.27%**; local-search excess: **0.34%**.
- Local search attained **15/16 certified optima**; remaining case 14: baseline 49, local 39, certified optimum 37.
- Total measured greedy+local-search execution across 30 cases: **19.22 seconds** (single local run; environment-specific).

| Jobs | Improved cases / 6 | Mean makespan reduction | Median runtime per case |
|---|---:|---:|---:|
| 6 | 1 | 1.11% | 14.8 ms |
| 10 | 6 | 12.18% | 50.4 ms |
| 18 | 6 | 8.69% | 177.8 ms |
| 30 | 6 | 9.69% | 412.4 ms |
| 60 | 5 | 5.02% | 2164.1 ms |

Full per-case local makespans, cases 1–30: 27,16,18,14,14,13,39,30,23,38,28,20,64,39,31,76,56,45,100,57,70,112,77,55,232,147,113,243,135,97.

## Consequences
- A specialized two-phase scheduler (feasible earliest-fit, then bounded local improvement) is credible and low-dependency.
- The current 400-iteration budget becomes seconds for 60-stage cases. Measure improvement-vs-evaluation curves and support wall-clock/CPU/RSS budgets and early stopping.
- **No evidence of optimality** for 14 cases without certificates. Lower-bound ratios must not be presented as proven optimality gaps.
- The 30-case corpus is synthetic, homogeneous, single-environment, and makespan-only. It does not yet validate ASES's heterogeneous VPS/Actions scheduling, quotas, monetary costs, failures, freezes, or real resource pressure.
- Use a Rust implementation with independent validator in a subsequent stage. Avoid choosing a large native solver until materially harder instances show a clear advantage.
- Reproduce results in GitHub CI from committed executable and JSON fixtures; local benchmark artifacts are not yet committed to the repository.

## Next gates
1. Commit executable local-search runner and JSON output, and add CI replay.
2. Measure 50/100/200/400 iterations, time-to-best, peak RSS and cold startup. Enforce interruption semantics.
3. Test 30 **heterogeneous** instances (VPS vs cloud, eligibility, quotas, outage, hard budget, critical paths), with validated outcomes.
4. Compare a bounded branch-and-bound or Rust solver on the same instances, report gains per CPU-second and per MiB.
