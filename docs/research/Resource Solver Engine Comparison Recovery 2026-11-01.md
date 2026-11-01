---
title: Resource Solver Engine Comparison Recovery — 2026-11-01
program: EDASES
layer: Research
document_type: Benchmark and Decision Recovery
status: Provisional
authority: Prior conversation benchmark; awaiting original artifact reconciliation
last_updated: 2026-11-01
related_documents:
  - docs/research/VPS Selection Evolution and Resource Solver Decision Record 2026-11-01.md
---

# Resource solver engine comparison — recovered decision

The prior VPS/resource-solver conversation had already compared **four actual solver configurations**. Do not restart at an unimplemented synthetic-only solver as though this comparison had not occurred.

## Recovered results

| Engine | Reported optimal results | Runtime | Peak memory |
| --- | ---: | ---: | ---: |
| Small exact enumerator | 6 | 20 ms | 11.9 MB |
| OR-Tools CP-SAT | 8 | 292 ms | 112.9 MB |
| MiniZinc + Gecode | 8 | 106 ms | 21.0 MB |
| MiniZinc + Chuffed | 8 | 99 ms | 16.7 MB |

The prior conversation reported validation of schedules, infeasibility, and larger optima: a 12-stage case with 23-minute optimum and a 30-stage case with 52-minute optimum. The table preserves the original reported comparison; the exact meaning of the 'optimal results' count, hardware, model formulation, test corpus and repeat variance should be recovered from original benchmark artifacts before interpreting it as a general performance ranking.

## Provisional conclusion

**MiniZinc with an on-demand backend is the preliminary preferred direction**, with Chuffed and Gecode both viable. It is not a final engine or implementation-language selection. The small exact enumerator remains useful as an independent oracle for small cases; CP-SAT remains a comparator. The performance results are workload-specific and do not establish general dominance.

## Remaining acceptance gates

- Replanning with completed and running stages, retaining previous estimates and decision reasons.
- Quota balances, expiry and reset windows, including recurring vs one-time credits.
- Cash/credit versus makespan tradeoffs, multiple full-graph Pareto alternatives.
- Hard compatibility and security constraints; setup/cache/transfer overhead.
- Independent verification, repeatability, memory measurements and failure/teardown semantics.

No production integration, deployment or solver engine selection is authorized by this recovery record.

## Correction to November 1 decision record

The previous record's final paragraph proposed starting with a pure deterministic synthetic prototype. That should be read as **remaining validation work**, not as the first-ever engine comparison. This recovery record preserves the already completed comparison and its tentative MiniZinc direction. Reconcile original test source and outputs before promoting benchmark claims to independently verified evidence.
