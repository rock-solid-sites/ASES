---
title: Resource Console v0.1 — Bounded Implementation Packet
program: Tooling
layer: Implementation
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/requirements/Resource Console v0.1 Requirements.md
  - docs/architecture/Resource Console v0.1 Design and Contracts.md
  - docs/research/resource-console/verification-matrix.md
  - docs/methodology/ASES Bounded Project Build Method.md
related_documents:
  - research/provider-registry/README.md
  - docs/research/Resource Router Cross-Conversation Integration Ledger 2026-11-03.md
consumed_by: []
implements:
  - docs/requirements/Resource Console v0.1 Requirements.md
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-06
---

# Resource Console v0.1 — Bounded Implementation Packet

## Compilation status

**Frozen behavioral slice; conditional implementation mechanisms.** This is a reduced builder packet for the first bounded slice, not a claim that on-host ingress, security and process-stop assumptions have been verified or that a whole production application is ready for deployment.

### Objective and freeze

Build a useful single-VPS dashboard showing local resource usage and recorded provider/account facts, with reusable read-only API for agents. The initial page stays inert until explicit Start. While active it updates live local metrics; when the last session ends or expires it terminates all dashboard-owned collector processes, retaining safe historical snapshots. Charts and lists label provider data freshness and unknowns. Under no condition does the console gain provider execution, agent stop, kernel/Engine, or resource solver admission authority.

Accept the behavior and test obligations in:
- `docs/requirements/Resource Console v0.1 Requirements.md`
- `docs/architecture/Resource Console v0.1 Design and Contracts.md`
- `docs/research/resource-console/verification-matrix.md`

Avoid duplicating their normative content in implementation notes.

### Minimum source/reuse map

Preserve `research/provider-registry/known_accounts_v1.json`, `inventory_schema_v1.json`, `resource-router-integration-map-2026-11-03.json`, `data/compute-credits/registry.json`, and historical research unchanged. Use an explicit read-only adapter for each source, with unknown/null preserved; do not merge opportunity records into account grants. The Rust controller under `feature/resource-control-runtime-2026-11-02` is experimental and **not** merged or live-connected; do not fork its mutable ledger for v0.1.

### Proposed minimal vertical slice

1. **Source contract**: validate the new snapshot schema and synthetic fixture; create deterministic mapping from at least the existing known-account source plus local host metric records. Keep provenance and account scope.
2. **Static UI**: small Astro shell, React islands for responsive charts/tabular provider inventory and Start/Stop. No API invocation automatically on load and no auto-start in browser lifecycle.
3. **Local collector**: read only /proc, cgroup v2 and systemd; emit typed observations, bounded rate, redact process secrets. Keep observer target processes outside monitor process group.
4. **Session boundary**: implement local authenticated Start/heartbeat/Stop and single last-lease shutdown, crash/disconnect recovery and multi-tab policy; no unauthenticated start endpoint.
5. **History**: SQLite for derived safe observations with append-oriented writes, stable event IDs, digest/source revision and restart recovery. No dashboard write path to any registry/controller/kernel authority.
6. **Read interface**: GET resources/observations/history with versioned shape shared by UI and agent clients.
7. **Adapter extension**: after provenance tests, add one low-risk provider read-only API, if verified credentials are available without copying them to UI or repo.

### Candidate realization; NOT selected until discriminating live checks

- Frontend: static Astro + strictly typed React islands; check bundle/runtime cost and compatibility.
- Host ingress: existing private route; inspect before changes. A systemd socket-activated collector service is a plausible no-resident-process mechanism; test static-first-load, race and shutdown behavior.
- Storage: SQLite projection in protected local directory; measure and test durability, contention, recovery.
- Backend language: **unselected**. Evaluate the smallest memory-safe or managed implementation consistent with existing ASES language policy and actual deployment support. Do not infer a Kernel or Engine language from this choice.
- Provider polling: mock/fixtures first; actual intervals and permissions per provider. No universal "real-time" promise for delayed billing.

### Highest-risk live assumptions

- Can the existing ingress forward authenticated Start requests to a socket-activated collector without leaving another console daemon running?
- Does current private access actually authenticate all HTTP routes and origin/session-mutating requests from phone and laptop?
- Can this VPS query relevant process/cgroup/systemd metrics without adding privileged access or new permanent services?
- Does ending the final client lease reliably terminate only owned monitoring processes under abrupt network loss, restart, race and multiple clients?
- What is the baseline and additional PSS/CPU cost on the target VPS, measured rather than estimated?

If a candidate mechanism fails, keep the required behavior and find the smallest alternative; **do not** silently weaken the security, session lifetime, or zero-resident-process requirement.

### Narrow implementation gates

**Gate A:** Contract/schema and fixtures pass static validation; browser has inert static shell; no real provider credentials. **Gate B:** Isolated on-host lazy activation and process cancellation pass V01–V06 plus privilege check, with recorded evidence. **Gate C:** Derived snapshots, real local metrics, provider freshness and UI/agent consistency pass V07–V16. Only then describe v0.1 as live-ready. No automated production deployment solely because code compiles.

### Builder residual task (compact)

```text
Operation: implement a bounded Resource Console v0.1 vertical slice on an isolated branch.
Target: ASES project specifications in docs/requirements/Resource Console v0.1 Requirements.md, docs/architecture/Resource Console v0.1 Design and Contracts.md, and docs/research/resource-console/verification-matrix.md.
Preserve provider-registry source evidence kinds and freshness states and current VPS private ingress; inspect that ingress before selecting activation and backend realization. Implement the smallest static Astro/React dashboard with explicit Start/Stop, real read-only local metrics and derived provider snapshots, SQLite history, and a matching read-only agent API. No producer authority, provider actions or Kernel/Engine implementation.
First run the narrow discriminating tests for lazy launch, multi-session shutdown, abrupt-loss fallback, authentication, process isolation and resource overhead. If an assumption fails, return the measured incompatibility and smallest safe alternative. Validate all v0.1 acceptance cases; preserve evidence and list blocked live checks. Stop at an isolated working slice and PR; do not deploy to production without verified private ingress and permission boundaries.
```

### Stopping condition

A tested branch/PR demonstrates the requirements with identified live gates, reproducer artifacts and no unauthorized operational changes. If the host is inaccessible from the builder route, complete source/fixture tests and explicitly mark on-VPS claims **NOT TESTED** rather than treating synthetic or local-host outcomes as confirmation.
