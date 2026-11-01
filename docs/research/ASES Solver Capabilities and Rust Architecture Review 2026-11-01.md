# ASES solver capability and memory-safe architecture review — 2026-11-01

Decision: **defer stripped C/C++ binaries and any wholesale rewrite**. First benchmark existing Rust engines and identify ASES-specific missing features. Historical MiniZinc/Chuffed/Gecode results remain reference measurements, not a mandate to adopt their implementation languages.

## Capability inventory

| Capability | Chuffed | Gecode | ASES need |
| --- | --- | --- | --- |
| Constraint engine | Lazy clause generation: finite-domain propagation, SAT nogood learning and explanations | Extensible propagators, branching and search engines | Search, conflict detection, optimality |
| Variables | Integer bounds/domains and Boolean SAT literals | Integer, Boolean, set, float | Mostly integer time/cost/CPU/RAM and Boolean assignment |
| Scheduling | Cumulative, disjunctive, difference | Scheduling, bin packing, graph and other global constraints | Precedence, non-overlap, time-varying resource capacity |
| Search | Conflict learning and assumptions | Search heuristics, restarts, parallel search | Bounded optimization, warm starts/replans |
| Explanations | Assumption nogoods, potentially nonminimal | Failure/branching instrumentation; no equivalent core assumed | Auditable infeasibility and allocation decisions |
| Runtime | Native C++ | Native C++ | Neither preferred for new ASES production code |

Sources: https://github.com/chuffed/chuffed ; https://www.gecode.org/ ; https://www.gecode.dev/documentation/

## Rust candidate: Pumpkin

https://github.com/consol-lab/pumpkin ; https://docs.rs/pumpkin-solver/latest/pumpkin_solver/

Pure-Rust lazy clause generation engine. As of crate 0.5.0 (2026-08-05), documented cumulative/disjunctive, element, linear arithmetic, integer operations and clausal constraints. Modular crates include core, propagators, constraints, conflict resolvers and checking. Its proof certificates and independent checking are particularly relevant to ASES evidence requirements. Check actual API completeness, incremental assumptions, objective support, propagation correctness and benchmark performance. A dependency on a build-time C compiler is not equivalent to C/C++ solver logic; audit transitive build scripts and runtime dependencies.

## Rust candidate: unifier

https://casoon.github.io/unifier/docs/

Early 0.5.x Rust CSP/COP framework with scheduling primitives, cumulative/no-overlap, several search algorithms, lexicographic hard/soft objectives and incremental feasibility checks. Especially aligned to project scheduling, but docs explicitly note no general unsat cores, no serde serialization, and no independent production-scale verification. Research comparator, not presumed production-ready.

## ASES minimal constraint vocabulary (candidate)

1. Boolean `assign(stage, environment)`; exactly one permitted assignment per active stage.
2. Integer `start`, `end`, `duration` with dependency precedence and optional stages.
3. Cumulative resource constraints by time for CPU, RAM, environment concurrency and quota windows.
4. Budget and credits with time-sensitive resets/expiry; transfer/cache/startup costs and setup jobs.
5. Immutable completed/running stages and artifact/security eligibility gates.
6. Multiobjective optimization: feasible first, then policy-specified lexicographic or Pareto cash/makespan/replan churn.
7. Explain infeasible hard constraints, verify every output independently and retain evidence/proof where available.

Not required initially: arbitrary real arithmetic, general set/graph constraints, full MiniZinc syntax, generic modeling IDE, advanced global constraints unrelated to scheduling.

## Architecture recommendation

- Define a versioned **Rust WorkGraph + EnvironmentSnapshot** model independent of any solver.
- Compile this model into Pumpkin first; compare with MiniZinc/Chuffed/Gecode reference and exact small-instance oracle.
- Implement an independent Rust plan validator, not a shared solver-specific feasibility checker.
- If Pumpkin lacks a critical constraint, first build a narrow, tested Rust propagator or transform it into existing supported constraints. Avoid cloning Chuffed/Gecode.
- Keep a separate domain-specific scheduling heuristic for rapid feasible fallback, especially for very small jobs and solver timeout.
- Benchmark cold/warm RSS, build footprint, runtime, quality, proof/checking cost, timeout and replanning. No production engine selection before equivalent 18/30/60-stage tests.

## Rewrite decision gates

A wholesale rewrite of Chuffed or Gecode should require: (a) demonstrated missing capabilities in existing memory-safe solvers; (b) a minimal specification and independent oracle; (c) explicit correctness/performance acceptance targets; (d) maintenance, licensing and security review. ASES-specific scheduling functionality is more likely to be worth implementing than a generic CP engine.

## Evidence and uncertainty

This is a capability review based on upstream public documentation, **not** an audited implementation or executed benchmark. The earlier 18-stage TripN fixture and measured CI trace remain separate. Any synthetic durations/resource values must be independently labeled.
