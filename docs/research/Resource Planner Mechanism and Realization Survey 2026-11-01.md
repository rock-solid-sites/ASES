---
title: Resource Planner Mechanism and Realization Survey — 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Resource Planner Requirements and Behavioral Model 2026-11-01.md
related_documents:
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - docs/research/Resource Planner Realization Selection Gate 2026-11-01.md
  - docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
  - docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md
last_updated: 2026-11-01
---

# Mechanism and realization survey (no implementation selected)

**Research objective (2026-11-01):** Find feasible means of producing, revising and explaining whole-graph resource-placement proposals with strict project/account isolation and low compute footprint. **Paseo is the current presentation/launch-harness context, not a constraint on future core language, data model or optimizer. Do not add compatibility machinery for a speculative future ASES UI.** This is the open-ended Level B ASES realization-selection research phase. New production implementation is blocked until requirements, exclusions and comparisons are validated.

## 1. Problem classification and implication

The computational core resembles **multi-mode resource-constrained project scheduling (MRCPSP)** with alternative machine/mode choices and resource capacities, plus **flexible project structures** (optional work and changing dependencies), nontrivial environment setup/transfer costs, budgets and multi-objective choices. It is not merely assignment, token-price ranking, or shortest path. Some variations are computationally hard; an algorithm that tries every possible placement but uses fixed topological scheduling can still miss optimal schedules. The 3-stage A/B/C counterexample is in the requirements file.

Research: an updated RCPSP variants survey https://www.sciencedirect.com/science/article/pii/S0377221721003982 and flexible structures paper https://www.sciencedirect.com/science/article/pii/S0377221724008269. These provide academic problem analogies, not proof that any library meets our unique model/account trust constraints.

## 2. Mechanism families after requirements, not a language shortlist

| Mechanism | Useful properties and likely fit | Important limits | Current classification |
| --- | --- | --- | --- |
| **Pure constraint/feasibility evaluator + small exact enumerator** | Very small on-demand TCB, transparent reasons, oracle for small test graphs | Exhaustion grows combinatorially; must enumerate actual schedule orders, not only environment assignments. | **UNRESOLVED** as maintained small-graph solution; v0 exact-claim **fails R05** |
| **Constraint programming / SAT hybrid with scheduling intervals (CP-SAT)** | Native precedence, optional execution modes, no-overlap, cumulative capacities, time limits, feasibility/optimal status; strong direct fit | Model time units as bounded integers; need correct setup/cache/transfer encoding, memory measurement and solver status handling. | **Promising, UNRESOLVED** |
| **Solver-independent constraint model + interchangeable backends** | Declarative model can test different CP/SAT/MIP solvers and compare optimality/performance without choosing core language upfront | Translating time-dependent credits and sequential setup can be complex; compiler + solver TCB and package footprint; portability isn't itself a reason to add a DSL. | **Promising, UNRESOLVED** |
| **Mixed-integer programming (MIP)** | Strict budgets, linearized fixed/variable costs and capacity; objective bounds and infeasibility diagnostics can be useful | Time-indexed/nonlinear scheduling, warm-cache and conditional transfer constraints may explode in binary variables; model and solve first. | **UNRESOLVED** |
| **SMT optimization / MaxSMT** | Rich logical hard constraints, multi-objective lexicographic/Pareto possibilities, counterexamples for authority/feasibility | Scheduling support and performance for realistic instances not yet demonstrated; needs separate benchmark. | **UNRESOLVED** |
| **Incremental local search / metaheuristics** | Dynamic graph changes, pinned work and fast revised proposals; objective explainability can be added | A found solution needn't be global optimum or even feasible if hard constraints/solver result unchecked; runtime cost of JVM or equivalent unknown. | **UNRESOLVED** |
| **Flow/assignment/graph algorithms** | Very efficient and simple for specialized cases: pure assignment, dependency reachability, maxflow | **Insufficient ALONE** for general whole-graph ordering, setup, precedence, multi-dimensional resource quotas. | **EXCLUDED as full planner**, retain as subroutines |
| **Rules/SQL-driven deterministic scoring** | Cheap validation, durable materialized observations, simple explainability; can avoid large optimizer for small queries | Database query order is not an optimizer of disjunctive resource scheduling; it needs a genuine search/schedule mechanism. | **UNRESOLVED for feasibility/ledger**, **EXCLUDED alone for claimed optimal scheduling** |
| **Cloud optimizer as external service** | Removes burst CPU/RAM from VPS; possibly useful if exact solving is expensive | Secrets/input exposure, dependency, external billing, persistent account policy and outage; not justified at current scale. | **UNRESOLVED; low priority** |
| **Ensemble: feasibility validator + bounded solver + fallback heuristic** | An independent validator can check any proposed schedule; fallback retains responsiveness with explicit quality limits | More components; needs proof that two algorithms are necessary for actual workloads. | **UNRESOLVED, avoid premature construction** |

No approach above is declared VIABLE for maintained deployment. Research should first compare smallest realizations satisfying the requirements; avoid selecting a popular stack by habit.

## 3. Specific implementation-ecosystem evidence (not selections)

### Google OR-Tools / CP-SAT

Docs: https://github.com/google/or-tools/blob/stable/ortools/sat/docs/scheduling.md ; https://developers.google.com/optimization/cp/cp_solver ; https://developers.google.com/optimization/cp/cp_tasks ; https://developers.google.com/optimization/install/

Official scheduling primitives include **optional intervals**, **no-overlap**, and **cumulative resource capacity**. The solver supports time limits and integer models. OR-Tools is implemented in C++ and officially wraps **Python, Java and C#** (C++ native also exposed). Per ASES rules this does **not** automatically forbid an established external C++ library/runtime, but its native dependency belongs to the trusted-base assessment; no new standalone C++ application code is permitted. Native binary/package size, worker RSS, install complexity and model fidelity remain **unmeasured**.

### MiniZinc and multiple solvers

Docs: https://docs.minizinc.org/en/stable/ ; https://www.minizinc.org/downloads/ ; https://www.minizinc.org/license/

MiniZinc is an established, open-source **solver-independent constraint-modeling language**. Official downloads include Gecode, Chuffed, OR-Tools CP-SAT, HiGHS and COIN-OR CBC. This may let us compare scheduling models independently of the program used for input decoding and on-demand invocation. The model compiler and backend binaries increase install size/TCB; **not** inherently lighter than a direct CP-SAT integration. GPL/MPL/Apache/MIT/EPL license obligations for bundled tools must be reviewed if distributing them. A modeling DSL is legitimate only if it reduces complexity/evidence burden after tests, not because hypothetical future systems need flexibility.

### Timefold Solver

Docs: https://docs.timefold.ai/timefold-solver/latest/ ; https://docs.timefold.ai/timefold-solver/latest/responding-to-change/real-time-planning ; https://docs.timefold.ai/timefold-solver/latest/constraints-and-score/overview ; https://timefold.ai/license

Community edition is open-source Apache-2.0 and runs on Java 21+; Kotlin is supported. Incremental scoring and \`ProblemChange\` with pinned work suit revised schedules, but solutions must be checked for feasibility, and a heuristic's "best" is not guaranteed globally optimal. The JVM/startup and resident footprint, packaging and ability to encode cost/quota reset nuance need benchmarking before a VPS-friendly recommendation. Daemon mode exists but an always-on solver is **not required by user**.

### HiGHS, Z3, Airbus discrete-optimization

- HiGHS: https://highs.dev/ — open-source MIT LP/MIP/QP solver, standalone executable and interfaces to several languages. Useful countercandidate for linearisable time/money constraints; runtime/variable explosion unmeasured.
- Z3: https://microsoft.github.io/z3guide/docs/optimization/intro/ and https://microsoft.github.io/z3guide/docs/optimization/combiningobjectives — supports lexicographic, Pareto and independent optimization goals. Its rich constraint expressiveness does not establish RCPSP execution efficiency.
- Airbus discrete-optimization: https://github.com/airbus/discrete-optimization and https://airbus.github.io/discrete-optimization/ — Python reference implementations of RCPSP variants and methods (greedy, local search, MILP, CP, hybrid, scenario/Pareto). Valuable for **research fixtures/reference algorithms**, but has broad dependencies and is not automatically a suitable always-on lightweight dependency.

### Persistence and revision history are a separate choice

SQLite WAL is documented to support concurrent readers with one writer on a single host: https://sqlite.org/wal.html . It is **not** a solution for live multi-host network-mounted WAL, nor does using SQLite automatically make any observation trustworthy. A tiny local transactional record or append-only event log may suffice; neither is selected. The original conversations and evidence remain authoritative at their source; planner provenance references must not become a second writable authority for project decisions.

## 4. Realization and language discipline

No existing design instruction authorizes choosing Node.js/TypeScript as a default for the core. A **thin Paseo-specific UI/plugin adapter** can reasonably use strict TS as an integration-specific boundary, subject to tests; it does not determine the maintained planner's language. For the core, different realizations may favor a low-footprint single executable, an on-demand solver process, a managed-language solver library, a declarative model invoked through CLI, or even a no-daemon library coupled to minimal state. **Do not rank Rust/Go/Java/Kotlin/Python/C#/Haskell/OCaml/etc by preference alone**; assess the actual mechanism + runtime + packaging + TCB against the same functional and measurement tests, applying the canonical unsafe-language exclusions to new standalone code.

Current important trade-offs **to benchmark** rather than assume:
- baseline idle RSS and CPU on an 8/12 GB VPS; on-demand peak memory and startup/compile sizes;
- scheduler optimality or bounded gap on 3/12/30-stage workload families, feasibility verification, and deadline/time-limit behavior;
- complexity of supporting variable mode choice, cache/colocation and explicit data transfers;
- number of process/runtime dependencies, vulnerabilities and maintenance effort; 
- stable tested input validation, deterministic evidence generation, and security of data ingress/egress;
- integration with **currently verified** Paseo command/plugin capabilities, not a future system.

**No full language shortlist is selected at this stage**. The next discovery can use constrained technical probes to eliminate concrete realizations rather than ideation by familiarity.

## 5. Cheapest discriminating research programme

**First, create solver-neutral behavior fixtures and expected verdicts.** Share identical inputs and outcomes across experiments, including deliberately infeasible and unknown cases:

| Fixture | Claim tested | Pass condition |
| --- | --- | --- |
| F01: A/B/C, 2 machines | Non-greedy schedule ordering | Feasible 32-minute schedule returned; label optimal only with sound bound or exact proof |
| F02: 3 domains, cheaper alien quota | Identity/account isolation | Reject alien account despite lower cost |
| F03: independent review | Builder/reviewer separation | No placement on same prohibited workspace |
| F04: downstream 32 GiB gate | Full-graph lookahead | Upstream choice accounts for expensive final-stage transfer/setup |
| F05: warm workspace vs cold server | Colocation and startup | Correctly compare new setup and cache/transfer savings |
| F06: exhausted/cross-reset quota | Units and time windows | No false unlimited model/CPU capacity; explicit unknowns |
| F07: completed-and-running stages | Replanning | Preserve observed/pinned work; revise only legally movable stages |
| F08: incompatible/retired provider | Hard feasibility | Reject, explain reasons, don't silently substitute paid route |
| F09: untrusted malformed JSON/provider telemetry | Boundary validation | No bypass, crash/ambiguity reported, state unchanged |
| F10: solver timeout/partial solution | Honesty of guarantee | Separate feasible but unproven, proven optimal, infeasible, and unknown statuses |

**Second, perform three *small* mechanism probes, not a product rewrite:** 
1. A solver-independent MiniZinc model run under two included backends on F01–F06; inspect binary size, CPU, memory and model complexity.
2. A direct CP-SAT model in its simplest supported interface for the same fixtures, bounded runtime and output classification.
3. A minimal exact schedule-order enumeration for F01–F05 as an independent oracle and to measure when the no-general-solver option becomes impractical.

**Third**, compare outcome quality, packaging, trust footprint and implementation effort with current machine measurements. Only if these three fail important criteria should we invest in MIP/HiGHS, SMT/Z3, or Timefold's incremental replanning as follow-up probes. This test order is a *cost-saving research sequence*, not a preapproved production shortlist.

**Fourth**, choose the smallest realization that satisfies the validated needs and current Paseo access. If a simple on-demand procedure with a local data snapshot suffices, **do not build an always-on daemon, multi-provider plugin framework or generic future ASES compatibility API**.

## 6. Why no final selection yet

- Neither actual memory/time measurements nor reproducible 12/30-stage workload distributions are available.
- No scheduling engine has been installed/tested in the current sandbox or final VPS.
- No live Paseo/OpenCode/account telemetry paths or per-provider units have been validated.
- The exact extent of durable state and concurrency is not yet established.
- Solver completeness and optimality status must be demonstrated by real tests, not inferred from library feature lists.

**Decision status:** all promising realization families are **UNRESOLVED**, except the demonstrated insufficiency of assignment-only/fixed-order scheduling (EXCLUDED as a globally optimal planner) and pure shortest-path/min-cost-flow as a full solution. No measured surviving implementation is yet VIABLE under the canonical ASES selection process.

## Evidence classification

WHY: real whole-workflow planning, resource and credit costs, and identity isolation need accurate alternatives; optimizing an assignment instead of a schedule already failed.
WHAT: the dated ASES canonical realization selection method; documented official solver APIs/licenses; research papers; synthetic counterexample against the existing v0.
HOW CERTAIN: high that solver families are relevant and v0 scheduling insufficient; medium that CP-SAT/MiniZinc will express our requirements economically; low regarding fit on actual VPS and maintained runtime choice.
WHAT-NOT-TESTED: benchmarked memory/CPU, full API model/host separation, static/dynamic quota reconciliation, trusted account integrations, security of native solver dependencies, actual worker scheduling across providers, open-ended novelty beyond mechanisms surfaced by this first sweep.
