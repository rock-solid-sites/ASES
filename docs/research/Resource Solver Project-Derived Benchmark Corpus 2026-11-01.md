# Project-derived solver benchmark corpus v0.1 — 2026-11-01

Status: **proposed test fixtures**, not historical measurements or validated schedules. Follow the prior engine comparison in `docs/research/Resource Solver Engine Comparison Recovery 2026-11-01.md`. MiniZinc/Gecode, MiniZinc/Chuffed and OR-Tools CP-SAT must be evaluated on the **same normalized input and constraints**; the exact enumerator acts as oracle on reduced instances.

## Evidence tiers

- **H (historical verified):** source issue/PR/commit/CI job and measured start/end, CPU/RAM or billing data. Do not claim this tier without a link.
- **D (document-derived):** real project stages/dependencies reconstructed from specs, handoffs and repository history, with unknown durations.
- **S (synthetic):** estimated durations, resource demands, credits, failure rates and alternatives, explicitly marked. Never blend these into historical metrics.

Every fixture records `project`, `scenario`, `stage_id`, `dependencies`, `alternatives`, `required_capabilities`, `estimated_duration_minutes`, `peak_ram_gib`, `cpu_cores`, `harness`, `model_allowance`, `data_class`, `artifacts`, `verification_gate`, `evidence_tier`, `source_ref` and `assumption_id`. A separate environment snapshot records price, quotas/reset, startup, warm-cache, concurrency, memory, eligibility, teardown and evidence confidence.

## Four benchmark families

### HMS — multi-module rollout (D/S)

Derived from `specifications/Hospitality Management Suite Specification.md`: Rust/SQLite single-node platform, shared authentication/authorization, reservation and occupancy, guest ledger, staff/volunteer scheduling, communications, knowledge base, reporting, admin and staged rollout. Do not conflate this broader v1 spec with the separately narrowed prototype.

Synthetic DAG seed (12 stages): `requirements -> data_model -> auth -> {reservation_sync,guest_ledger,staff_scheduling,volunteer_management,communications,knowledge_base} -> integration -> reporting -> validation -> rollout`. Treat braces as parallel candidates, and ensure volunteer management depends on scheduling if the fixture assumes shared shift models. For larger cases split modules into build/test/review and add deployment stages. Critical test: shared DB migration and integration gates block apparently parallel work.

### ASES — parallel agent/review cycles (D/S)

Synthetic DAG seed: `scope -> architecture -> {kernel_experiment,observer_experiment,tooling_experiment} -> {independent_review_A,independent_review_B} -> synthesis -> remediation -> verification -> evidence_archive`. Model distinct builder/reviewer harnesses, reviewer independence, memory contention on a single 8GB VPS, and repeated remediation. Critical test: no review begins before relevant immutable candidate revision; evidence must persist when disposable workers end.

### Plugin portfolio — shared setup and independent releases (D/S)

Seed: `shared_contracts -> {github_plugin,atproto_reader,beds24_module} -> per_plugin_tests -> per_plugin_reviews -> integration_matrix -> release_gates`. Do not assert these are the actual current implementation stages without repo checks. Use shared toolchain/cache and API credential boundaries; compare colocated warm workers against independent fresh workers. Critical test: cheapest per-stage environment may lose globally due to repeated setup and transfers.

### TripN Astro + Beds24 — historical reconstruction (D, H when sourced)

Seed: `shared_design -> shared_astro_components -> {landing_site,property_1,property_2,property_3,property_4} -> multi_site_regression -> booking_widget -> beds24_integration -> credit_card_configuration -> booking_validation -> production_deploy -> postdeploy_verification`. The actual historical order may differ; reconstruct it from commits and handoffs before calling it historical. Preserve the known booking-heading mismatch and per-room credit-card configuration issue as candidate regression/rework branches, not invented time series. Critical test: integration regression discovered after deploy forces partial replan, while finished site builds remain frozen.

## Test matrix

For each family run: (A) baseline feasible DAG; (B) constrained 8GB VPS with limited concurrency; (C) one unavailable cloud environment; (D) quota exhaustion followed by reset; (E) one-time credits expiring; (F) warm-cache reuse versus cold-start transfer; (G) mid-execution failure and new remediation stage; (H) cash ceiling versus earliest completion; (I) incompatibility/secret boundary; (J) cancellation and evidence-retention requirement. Scale 12/30/60/120 stages, with project-specific meaningful edges rather than random disconnected jobs.

## Acceptance and measurements

- Validate every output independently: dependencies, resource concurrency, quotas over time, eligibility, trust boundaries, budget, artifact preservation and frozen completed stages.
- Compare identical feasible sets and objective definitions. A solver returning fewer results or a different objective must not be compared as a faster equivalent.
- Record objective value, feasibility/optimality proof or bound, wall time, peak RSS, model-build time, solution time, setup/transfer charges and deterministic seed. Repeat runs and report median/p95 and timeout count.
- Compare **plan quality** (cash, elapsed time, credits, replan churn, robustness) separately from **solver performance** (runtime, memory, optimality gap).
- Use a small exact enumerator as an independent oracle; preserve infeasible cases and counterexamples as regression fixtures.
- At least one deliberately infeasible case per family must return an explanation tied to a hard constraint.
- Replanning must preserve completed-stage placement and evidence, and log the old assignment, new assignment and reason.

## Immediate evidence collection

1. Recover original MiniZinc/CP-SAT benchmark source, model files, versions, fixtures and raw output; do not silently regenerate the old numbers.
2. Extract HMS spec and latest prototype handoff; ASES issues/reviews; plugin project manifests; TripN Astro and Beds24 commits, PRs and CI timestamps.
3. Build a source-backed stage/dependency table first, with unknown resource values explicitly null.
4. Add a **separate** synthetic estimates layer for executable solver inputs.
5. Run all engines with equivalent constraints; only then decide whether MiniZinc remains preferred.

## Decision status

No engine is selected for production. MiniZinc/Chuffed or Gecode is provisionally preferred based on earlier small tests. The purpose of this corpus is to try to falsify that preference under realistic scheduling, quotas and replanning, rather than reconfirm it.
