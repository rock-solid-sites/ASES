# ASES resource-planner prototype (v0, read-only)

**Status:** Experimental prototype for a future Paseo integration, not part of the ASES Work Unit, Kernel-0 or Observer execution engine. No cloud APIs, credentials, sessions, payments, resources or production repositories are accessed or modified. The included example is **synthetic**: its `verified` resource state indicates eligibility *inside the fixture*, **not real provider availability**.

The planner accepts a resource inventory, an identity domain, and a dependency graph of development stages. It enumerates placements for small graphs, rejects unavailable/ineligible resources and cross-domain account usage, then returns up to three distinct plan proposals: lowest estimated incremental cash expense, earliest estimated completion, and lowest modeled exposure. Model and environment selection remain separate; a `harness` field prevents assigning jobs to resources incapable of executing that harness. Actual model routing and token/quota telemetry are intentionally not integrated yet.

## Realization selection gate — NOT APPROVED FOR MAINTAINED USE

**Language/runtime choice remains UNRESOLVED.** This TypeScript/Node implementation was written before the required canonical ASES realization-selection review. It is retained **only as a disposable, offline behavioral experiment**, not the chosen resource-planner architecture or a supported implementation. It must not be deployed, wired into real account credentials, or expanded into a production integration until the full requirements-first, exclusion-based selection process is completed. Passing the local regression tests does not establish that TypeScript/Node is appropriate. See [`Resource Planner Realization Selection Gate 2026-11-01.md`](../../docs/research/Resource%20Planner%20Realization%20Selection%20Gate%202026-11-01.md) and the canonical [`Implementation Realization and Assurance Selection Method`](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md).

The current code has strict TypeScript checking and some runtime invariants, but it has **not** been independently validated for arbitrary JSON input, complex quota units, performance, account authority or persistent state. The final planner may use another realization; a thin Paseo JavaScript/TypeScript adapter is a separate choice.

## Identity boundaries: user-confirmed 2026-11-01

| Domain | GitHub identity | Current state |
| --- | --- | --- |
| `ases` | Future dedicated GitHub identity | **Planned**. Current development repo is under `rock-solid-sites`; the new identity name is not chosen. |
| `hms` | Future dedicated GitHub identity | **Planned**, independent of Trip'n. |
| `tripn` | `tripn-chill-zone` | **Existing production account**. No migration or production changes are authorized by this prototype. |

The operator plans separate platform accounts for each domain where supported and allowed. Platform quotas are never implicitly pooled. The v0 solver **only** considers provider accounts explicitly owned by the task's identity domain; intentional cross-domain sharing/grants are not implemented and must require a separate, explicit scoped policy. Recording a project in a common Paseo UI grants no execution rights.

Production data can only be assigned to resources that explicitly declare production eligibility within the same domain; that flag is **configuration**, not proof that an environment is secure. All cloud hosts, the VPS included, are treated as untrusted for secrets and sensitive code unless a separate security assessment authorizes access.

## Quick test (no provider accounts required)

Requires Node.js 22+ and npm. From this directory (one pinned TypeScript development dependency):

```sh
npm install --ignore-scripts --no-audit --no-fund
npm test
node cli.mjs fixtures/example-ases.json
```

Run the tests before using the sample CLI. The CLI reads a local JSON fixture and returns a planning proposal; it never launches a process on any remote host.

## Existing features

- Distinguishes domain, provider account, host resource, harness, stage and observation.
- Requires explicitly eligible resource kind, CPU, RAM, data class and harness, plus a verified availability label.
- Treats included compute minutes and cash limits as separate account-specific resources.
- Uses the entire small DAG, including transfer costs, sequential reuse of a workspace, warm-start avoidance and dependent stage requirements, rather than greedily choosing each stage in isolation.
- Checks stage independence where requested (e.g. reviewer must not reuse builder's workspace).
- Handles observed completed stages as immutable, and replans remaining stages using new estimates.
- Fails closed on missing dependencies, cycles, account ownership violations, unsupported tasks, exceeded budgets and excessive search size.
- Returns structured plans suitable for a future Paseo panel / CLI integration.

## Deliberate limits and next implementation work

This is **not** a production optimizer. The solver enumerates host assignments but schedules independent stages in deterministic topological order, not all possible intra-host permutations. It assumes one stage per resource at a time; global provider concurrency, multi-stage parallel use of available cores, occupancy from other projects and scheduling windows are not yet modeled. Work estimates are point values; risk scoring uses configured relative numbers, not measured safety. The credit model uses included **compute minutes**; real providers may offer dollars, GB-hours, core-hours, monthly resets or task quotas, which must be modeled without false conversion. It does not currently select model routes, infer token price, retrieve usage, authorize cross-domain grants, or compare existing model account balances.

Those deficiencies should be addressed using the actual Paseo and OpenCode usage/plugin APIs after the parallel tool integration work. Before deployment, add account-specific adapter permissions, provider terms and expiry, account-local storage/artifact boundaries, atomic quota reservations, a measured telemetry layer, better scheduling, adversarial verification and explicit authority/control contracts. Neither a hypothetical resource in a fixture nor a green unit test is proof that a real provider account is accessible.

## Related design documents

- `docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md`
- `docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md`
- `docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md`

The project-level UX priority remains original live strategy conversations and their association with agent sessions. **Development of this independent calculator can proceed in parallel**, with no dependencies on completing Paseo's UI integration or the VPS runbook.