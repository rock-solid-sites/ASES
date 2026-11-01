# Heterogeneous synthetic scheduler comparison — 2026-11-01

## Decision

Bounded local search remains the preferred **prototype improvement layer** over a deterministic feasible fallback, not a selected final engine. This test covers 30 synthetic workloads and demonstrates feasibility and improved modeled objective, **not** optimality or verified provider entitlements.

## Provenance and limits

- VPS observations from earlier IT3812 inventory: Ubuntu 22.04, four vCPU, ~7.9 GiB physical RAM, concurrency deliberately capped at two following historical OOM events. **5.5 GiB allocatable** is a conservative *synthetic assumption*, not a measured free-memory reading.
- `actions` runner: 4 vCPU, 7 GiB RAM, one slot, 180 synthetic duration-tick quota, cost rate 1. **Not verified as the user's Actions entitlement or billing.**
- `burst` runner: 8 vCPU, 12 GiB RAM, one slot, 75 synthetic duration-tick quota, cost rate 5. **Hypothetical capacity, not an established provider account.**
- VPS rate 0 is incremental scheduling cost only, not zero actual hosting cost.
- No resource or allowance sharing across identity domains; private work stays on the VPS in this experiment.
- Fixed independently supplied environment envelopes. No live discovery, account authentication, quota synchronization or runtime admission attempted.
- Random DAGs, 10/18/30/60/90 stages, seeds 2101–2130; duration 3–18 ticks, CPU 0.5–3 vCPU, RAM 0.5–4 GiB; build/test/review/deploy capability restrictions; ~22% private, plus private deploys.
- Five scenario families, six instances each: VPS-only; normal external availability; restricted external quotas; VPS outage [15,40); tight VPS memory and external quotas.
- Each scenario uses deterministic priority-based earliest fit, then 100 swap/insertion attempts with best-only acceptance; candidate evaluated against independent authoritative job and environment data. The local search cannot make the result worse on its specified objective.
- Combined score = makespan + 0.08 × synthetic execution charge; a demonstrative scalarization, not actual money or user-approved tradeoff.
- Resource quota modeled as total allocated job-duration ticks, not actual GitHub Actions billed minutes or provider subscription quota.
- These are all synthetic; no external jobs were launched.

## Measured results

**30/30** cases produced feasible plans; **30/30** improved combined score; mean relative score improvement **7.95%**. **28/30** shortened makespan; nine reduced modeled external charge, ten increased it, and eleven did not change it. Mean score improvement by scenario:

| Scenario | Instances | Mean score gain | Mean makespan gain |
|---|---:|---:|---:|
| VPS only | 6 | 6.08% | 6.08% |
| External runners | 6 | 9.88% | 12.86% |
| Restricted quotas | 6 | 8.27% | 9.09% |
| VPS outage | 6 | 6.45% | 8.34% |
| Tight memory/budget | 6 | 9.05% | 9.54% |

Total measured 30-case benchmark runtime ~8.99s, including 100 local-search evaluations per case; Python, local container, not VPS hardware. Runtime excludes Python startup and does not establish peak RSS. The benchmark was checked by 10 local unit tests including data eligibility, dependencies, CPU capacity, outage, quota, budget, determinism and non-regression.

## Important caveats

1. No exact solver comparison was performed on these heterogeneous cases. The local-search improvements do **not** demonstrate closeness to the optimum.
2. The benchmark's candidate validator and scheduler are separate functions in the same Python module, not a fully independent implementation or Rust production validator.
3. Current search chooses a greedy feasible placement for each priority ordering; it does not optimize assignments and priority jointly or preserve actual work already in progress.
4. The scalar objective may increase cost while reducing time; hard user budgets and preference sensitivity must be tested separately.
5. This is a stylized homogeneous unit-tick workload; no model tokens, provider context windows, per-model shared allowances, Codex Cloud session constraints, Codespaces free-hour quotas, runner boot time or data-transfer overhead are represented.
6. No claims about real Actions, Codex Cloud, Codespaces, OpenCode Go, Mistral or MiMo entitlements should be inferred. Actual quotas remain unverified.
7. Python `assert` is used for prototype validation; a production validator must use explicit checks that cannot be disabled with optimized Python execution.

## Next gate

Use verified account limits where available, keep unverified ones explicitly scenario-based; run sensitivity over objective weights and quotas; introduce a second independently implemented feasibility oracle; compare a bounded branch-and-bound or CP engine on the same 30 instances and record wall-clock, peak RSS, and objective bounds. Only then make the engine selection.
