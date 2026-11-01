---
title: Resource Planner Requirements and Behavioral Model — 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
related_documents:
  - docs/research/Resource Planner Realization Selection Gate 2026-11-01.md
  - docs/research/Resource Planner Mechanism and Realization Survey 2026-11-01.md
  - docs/research/Paseo Resource Planner Parallel Track and Identity Domains 2026-11-01.md
last_updated: 2026-11-01
---

# Requirements-first definition and behavioral model

## Operator instruction and scope boundary

The operator directed (2026-11-01) that a resource-planner mechanism be researched **now**, with current Paseo interoperability necessary but **speculative compatibility with a future non-Paseo system NOT an architecture selection factor**. Do not build a generalized "future ASES engine" adapter, plugin architecture, separate service or always-on process without a demonstrated immediate requirement. ASES Work Unit, Kernel-0 and Observer retain their separate meanings. This planner **proposes** candidate full-graph work plans for operator/orchestrator discussion; it never authorizes or launches jobs.

This file freezes the *purpose and hard invariants* for research; numerical performance limits, cost units and input sizes are provisional and must be measured before a maintained realization is selected. The initial TypeScript/Node experiment is **evidence, not preferred implementation**.

## 1. Inputs, outputs and minimum current interface

**Input:** user-selected project identity, source commit/requirements/evidence pointers, directed acyclic work graph of *stages* (not ASES Work Units), each stage's alternatives and resource needs; account-scoped provider/resource profiles with capability, location, quota units and reset windows, remaining credits, host RAM/CPU/concurrency, trust/permissions, restrictions, setup/cache state, data-transfer assumptions, and observed completed/running work. Raw provider data may be stale or untrusted.

**Output:** a small set of human-comprehensible feasible alternatives showing each stage's suggested environment, optional harness/model route, estimated start/end, cash and quota costs, transfer/setup and workspace-reuse economics, warnings/uncertainty, rejected constraints, and evidence/provenance. Alternatives differ on meaningful trade-offs (e.g. minimum spend, shortest finish, least uncertainty/operational risk), not cosmetic names.

**Paseo now:** one on-demand request/response route through an existing supported CLI, plugin navigation surface or other verified local interface. It is legitimate to use JSON for that *current exchange* if observed Paseo capabilities make it easiest, but **do not choose core language, solver, storage or architecture for a hypothetical later UI**. No permanent network API is necessary until a real current user requires one.

**Persistent capability, not necessarily a daemon:** provider observations and plan history must survive process restarts; the solver may run only when asked or when verified observations change. No requirement yet for a continuously resident planner process.

## 2. Non-negotiable candidate invariants and proof obligations

| ID | Property | Concrete falsifying trace / acceptance evidence | Status |
| --- | --- | --- | --- |
| R01 | Project identity separation | An ASES stage may not consume HMS or Trip'n provider/model quotas, storage, repository permissions, or secrets merely because they share UI/VPS. Existing Trip'n production GitHub owner is \`tripn-chill-zone\`; HMS remains separate. | Required; v0 synthetic unit tests, no live enforcement |
| R02 | No implicit grants | Cross-domain sharing is absent unless explicit scoped, authorized, revocable and provider-permitted; no inferred duplicate free-account allowance. | Required; intentional sharing out of current scope |
| R03 | No planning side effects | Read-only proposal may not launch, stop, merge, deploy, reserve billed resources, mutate GitHub or move credentials. A later authorized controller is separate. | Required; negative capability audit pending |
| R04 | Hard feasibility first | No plan breaks dependency order, machine capacity, region/terms, model/harness compatibility, policy, secret/data-class allowance or declared remaining account quota. Reject/label \`unknown\` without inventing verified availability. | Required; full cross-provider observations not yet collected |
| R05 | Whole-graph scheduling | Make not only placement but **stage start/end order** decisions considering dependencies, concurrency, setup, warm cache, transfers and downstream resources. Do not claim optimality for a topological-order heuristic. | **Existing v0 fails** counterexample (section 3) |
| R06 | Multi-dimensional units | Never equate a free model-token allowance, API credit, 1 GB-hour, 1 core-hour, a cloud-agent task, a machine-minute and cash. Record units, resets, paid overage and confidence explicitly. | Required; v0 single-minute abstraction is insufficient |
| R07 | Alternative plan integrity | Return feasible, genuinely distinct options and meaningful trade-offs; never label a heuristic result optimal without proof/bound, and report when search stops or evidence is insufficient. | Required; optimization/completeness untested |
| R08 | Replanning | Completed stages keep pinned source, provider, duration, cost and evidence; running stages are immutable or explicitly controlled; replan unfinished work when observation changes and retain reason for change. | Required; v0 tests only completed-state case |
| R09 | Deterministic explanation | Given the same versioned snapshot and policy, return stable feasibility verdicts, failure reasons and objective values; if search is nondeterministic, report solver seed/version/bounds and preserve result evidence. | Required; future solver check |
| R10 | Runtime input validation | Unknown/invalid fields, negative, NaN, malformed credits, unit conflicts, impossible model route, untrusted API claims or duplicate identity keys cannot pass hard gates. Types alone are insufficient. | Required; v0 JSON decoding incomplete |
| R11 | Low current-host footprint | Bench idle RSS/CPU, short query peak RSS, time-to-first feasible plan, and p95 plan generation on actual representative graphs on target VPS/desktop; avoid always-on heavy service unless benefit is measured. | **Thresholds UNRESOLVED** pending current Paseo/VPS baseline |
| R12 | Loss/restart recovery | Proposals reference revisioned snapshot; crash or stale quota update does not silently corrupt accepted evidence or spending estimates. Concurrent observations reconcile with provenance. | Required; persistent mechanism unselected |
| R13 | Safe failure and cancellation | Solver time budget exhaustion reports feasible-but-unproven vs infeasible vs unknown appropriately; provider lifecycle claims do not imply actual shutdown/billing settlement. | Required; future solver + adapter tests |
| R14 | Provenance and least-context | Support concise plan summaries and explicit references to raw logs, diffs, tests, model usage and evidence on demand; no automatic dump of full agent contexts. | Required; current data links unverified |
| R15 | Cheap development and operating cost | No recurring commercial optimizer subscription by default; no persistent extra resource used solely for a read-only plan without measured need. | Required; sourcing and license tests |

Financial, storage and performance thresholds must not be fabricated. Proposed **initial test scales**, not frozen user requirements: (i) 3 stages/2 resources counterexample, (ii) 12 stages/5-8 resource offers, (iii) 30 stages/10-20 resource offers, (iv) simultaneous accounts for 3 identities. Measure on representative 8 GB and 12 GB VPS candidates and current Windows desktop. A small-workload solver that stops at a cap may be acceptable **only if it discloses its limits**.

## 3. Reproducible adversarial finding in existing v0

A local Node 22 execution of the previously built \`tools/resource-planner/dist/planner.js\` with completely synthetic data produced the following **observed** output:

- Stage A: 30-minute independent task available only on machine R1.
- Stage B: 2-minute independent task available only on R1.
- Stage C: 20-minute task available only on R2, depends on B.
- Two resources available; zero startup, transfer and money costs; adequate memory and credits; ordered stage input [A,B,C].
- **v0 returned:** A on R1 at 0–30; B on R1 at 30–32; C on R2 at 32–52. Reported makespan = **52 minutes**.
- **Explicit feasible improvement:** B on R1 at 0–2; C on R2 at 2–22; A on R1 at 2–32. Makespan = **32 minutes**. Dependencies and one-stage-per-resource exclusivity are satisfied.

This proves that exhaustive **resource assignment** enumeration plus fixed topological stage scheduling does **not** optimize whole-graph completion even when assignments are forced and graph size is three. The currently claimed "fastest" proposal is **not demonstrably fastest**. Preserve the example as a regression and require an improved candidate to return the 32-minute schedule (or disclose inability to prove/select it). This is not evidence about any actual cloud-provider performance.

Local test source can be reconstructed from \`tools/resource-planner/planner.ts\` using the three-stage graph; no live services or auth were accessed.

## 4. Correct abstraction: feasible graph and schedule, then objectives

A scenario is a proposed selection of permitted execution modes (model + harness + environment), start times and shared resources. Hard predicates check identity, provider-terms, capabilities, CPU/RAM/disk/concurrency, precedence, isolation, quota, privacy and budget ceilings. If no feasible solution can be shown, return \`NO_FEASIBLE_PLAN\` / \`INSUFFICIENT_EVIDENCE\` / \`SEARCH_BUDGET_EXHAUSTED\` separately, not a plausible-looking impossible plan.

Within valid plans compare cash expenditure, latency/makespan, quota opportunity cost, risk/uncertainty (as provenance-rich evidence, NOT an arbitrary safety score), transfer/cache/setup effects, stability of unfinished assignments after replanning, and cost of failure/teardown. Maintain multiple nondominated options or explicitly chosen lexicographic objectives. A plan dominated in every dimension may still be shown as a **rejected reference** with explanation, not labeled a preferred option.

Observe that a managed cloud coding agent bundles model+compute and may prevent custom model selection, whereas OpenCode/Codex CLI harness plus model accounts plus shell compute are separate dimensions.

## 5. State-model applicability: scope each state boundary

- **Pure DAG/feasibility calculations:** **NOT APPLICABLE** for a separate authoritative state machine; deterministic invariants and mathematical constraints are more direct.
- **Proposal, accepted reference, revision/supersession, observations:** **SUPPLEMENTARY**. Versioned snapshots/evidence and forbidden rewrites should be explicitly specified; a plain append-only observation history could be enough.
- **Provider credits/grants/authority:** **SUPPLEMENTARY or UNRESOLVED**; the advisor currently has no authority to reserve/consume, so do not model pretend authoritative reservations. If later introduced, derive guards and revocation semantics independently.
- **Actual job execution / stop / settlement:** OUT OF SCOPE for the read-only planner. Provider status reported by a launcher must not be mistaken for a verified physical stop or billing cessation.

Smallest forbidden traces: stale quota after a reset, retroactive alteration of a completed stage, unapproved cross-domain grant, reviewer sharing builder workspace against an explicit independence requirement, and a provider disappearing mid-plan. Model tests should challenge those as data/invariants before selecting a statechart library.

## 6. Trust architecture / current Paseo integration limit

Treat all execution environments and provider measurements as untrusted, including the VPS. Keep raw tokens and production GitHub secrets out of the read-only solver; external telemetry collectors should provide scoped observations (source/time/unit/confidence) through a separately reviewed authority boundary. **A clean plan is not permission to execute it.**

For now the user may talk to an orchestrator over Paseo; that controller can call an *on-demand* planner and show candidate plans. No direct cloud launches, no credential-bearing plugin, no future ASES engine integration work and no need to make one language fit both the UI and solver.

## Evidence and WHAT NOT TESTED

WHY: Whole-graph optimization, data isolation and no extra VPS burden are the user's current requirements; existing v0 demonstrated a scheduling failure.
WHAT: canonical ASES language and state selection documents; v0 code; synthetic 3-task counterexample; verified solver docs in the companion survey.
HOW CERTAIN: high on requirement direction, identity boundaries, and the demonstrated v0 counterexample; medium on solver suitability; low/UNRESOLVED on performance, current Paseo data access, optimal scalability and actual provider limits.
NOT TESTED: current provider API balances, installed Paseo plugin behavior, credential boundaries, quota reset reconciliation, runbook host benchmarks, any full scheduling solver on the representative graph, stochastic estimate accuracy, live execution correctness.

## References

- \`docs/research/Resource Planner Realization Selection Gate 2026-11-01.md\`
- \`tools/resource-planner/planner.ts\`
- OR-Tools scheduling: https://developers.google.com/optimization/scheduling/job_shop
- University/industry solver survey is linked in companion document.
