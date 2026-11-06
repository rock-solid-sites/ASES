---
title: Resource Console v0.1 — Design and Contracts
program: Tooling
layer: Architecture
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/requirements/Resource Console v0.1 Requirements.md
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
consumed_by:
  - docs/research/resource-console/verification-matrix.md
  - docs/research/resource-console/implementation-packet.md
related_documents:
  - research/provider-registry/README.md
  - research/provider-registry/resource-router-integration-map-2026-11-03.json
  - docs/research/Resource Router Cross-Conversation Integration Ledger 2026-11-03.md
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
implements:
  - docs/requirements/Resource Console v0.1 Requirements.md
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-06
---

# Resource Console v0.1 — Design and Contracts

Status: **candidate architecture, not an implemented or kernel-authoritative design**. Freeze behavior where settled; verify realization/host details before freezing mechanisms.

## Boundaries and data flow

1. **Existing private static ingress** serves an Astro build with React islands. A page GET loads no telemetry and does not touch a protected collector API.
2. Explicit Start invokes an authenticated control route, waking an on-demand local backend. Candidate mechanism: systemd socket activation behind existing ingress, with the backend itself not resident when inactive.
3. A session manager grants revocable, short-lived browser leases and activates local read-only collectors only while >=1 valid session exists. A local collector may use /proc, cgroup v2 and systemd read interfaces without elevated process-control rights.
4. Read-only provider adapters retrieve allowed usage/entitlement observations. They operate only on request or TTL while a monitoring session exists; their external reporting latency is metadata, not a freshness guarantee.
5. An isolated, restricted local **projection SQLite** store retains safe snapshots, source references, session events, and identity associations. It is not the account entitlement ledger, resource-controller database, or an authoritative Kernel/Engine store.
6. Both browser and agent clients consume the same sanitized, versioned query representation. The agent interface may also read the latest cached snapshot when no dashboard session is active without waking continuous monitoring.
7. No connection from UI to the unmerged resource controller's write/admission API. Later read-only integration requires a distinct reviewed adapter.

The implementation must not create an always-on API process merely to serve static assets. Existing ingress/tunnel capabilities should be inspected before selecting any deployment model; there is no assumption that a systemd service directly receives Cloudflare tunnel connections.

## Reuse / source mapping

| Existing artifact | Fields or role to reuse | Boundary / incompatibility |
|---|---|---|
| `research/provider-registry/known_accounts_v1.json` | `records[].id`, `provider`, `account_evidence`, `claims[]`, `usage.status`, `usage.meters[]`, `verification_next` | Reported registrations and historical claims, **not** fresh authenticated balances. Private identifiers stay outside public repo. |
| `research/provider-registry/inventory_schema_v1.json` | Schema of known-account / potential-offer source material | Do not replace or silently broaden its truth states. Mapping into view schema is explicit/versioned. |
| `research/provider-registry/manifest_v0.py` | Experimental capabilities, meters, facts, source/status/revision model | Research validator only; do not require Python runtime in maintained console or treat its `active` enum as live admission authority. |
| `research/provider-registry/resource-router-integration-map-2026-11-03.json` | Responsibility boundaries, source authority and known gaps | Identifies incomplete/unmerged components, not a working runtime. |
| `data/compute-credits/registry.json` | Provider discovery, offers, billed/stopped semantics, candidate credit opportunities | Separate from verified account entitlements; some balances and provider access are unknown. |
| `docs/research/Resource Solver Specification Reconciliation 2026-11-02.md` | Account/payer/product/meter scope, observation TTL, event and billing distinctions | Advice, reservation and controlled execution are out of console scope. |
| `feature/resource-control-runtime-2026-11-02/resource-control/` | Future candidate read-only event/usage integration and identity mapping | Unmerged, mock only, not current UI authority or production adapter. |
| `docs/architecture/Execution Engine Vision.md`, Kernel-0 evidence packet | Conceptual exclusions and downward dependency boundaries | Console does not define Work Units, Observer, Kernel primitives or methodological transitions. |

**Identity rule:** provider, product, account, payer, agent session, job/attempt, environment and meter each retain distinct IDs. A source lacking one reports the missing identity or unattributed usage; no synthetic join becomes a fact.

## Read representation: proposed v1 projection, not a canonical registry schema

All numeric quantities use explicit unit and period; timestamps are UTC ISO-8601; query responses expose projection revision, source revision and observation time independently. Example shape, with **synthetic** data:

```json
{
  "schema_version": 1,
  "snapshot_id": "sample-001",
  "generated_at": "2026-11-06T00:00:00Z",
  "resources": [{
    "resource_id": "github/codespaces",
    "provider_id": "github",
    "product_id": "codespaces",
    "account_ref": "symbolic-account",
    "capabilities": ["remote_build"],
    "access_routes": [{"kind": "provider_api", "operations": ["list"], "verification": "unverified"}],
    "meters": [{
      "meter_id": "compute",
      "unit": "core_hours",
      "period": "billing_cycle",
      "remaining": null,
      "evidence_kind": "unknown",
      "freshness": "unknown",
      "dispute_status": "unknown",
      "observed_at": null,
      "source_ref": "known_accounts_v1.json"
    }]
  }]
}
```

Per-metric `evidence_kind` distinguishes runtime measurements, provider reports, user reports, published claims, estimates and unknowns; orthogonal `freshness` and `dispute_status` fields retain staleness/conflict without overwriting provenance. Provenance also includes original evidence category, collector identity, retrieved/observed timestamps, effective period, applicable account/payer, TTL and source reference when available. A provider-reported charge is **not** the same as settled billing; inference is never automatically promoted to verification. If source fields are insufficient, preserve null and expose a reason.

Provide a changed-since cursor plus immutable snapshot IDs to avoid converting delayed observations into a continuous but false real-time balance. UI history is an observation record, not reconstructed Kernel history.

## Initial API surface and privileges

| Method / route (candidate) | Purpose | Effect |
|---|---|---|
| `GET /v1/resources` | Filtered read projection with evidence kind, freshness and dispute status | Read-only |
| `GET /v1/observations?cursor=…` | Incremental metric/event projection | Read-only |
| `GET /v1/history?resource_id=…` | Historical observations | Read-only |
| `POST /v1/monitor/sessions` | Explicit Start: create one authenticated monitor lease; idempotency key | Transient local session only |
| `PUT /v1/monitor/sessions/{lease}/heartbeat` | Extend current lease | Transient local session only |
| `DELETE /v1/monitor/sessions/{lease}` | Explicit Stop and revoke lease | Transient local session only |

No generic `POST /execute`, `/shell`, `/provider`, `/kernel`, `/reserve`, or `/approve` capability is exposed. Authorization, rate limiting, method scoping, caller identity and anti-CSRF/origin checking apply even behind private ingress; no bearer credentials in URL parameters or browser bundles.

## Dashboard session model (SUPPLEMENTARY state modeling)

States `inactive`, `starting`, `active`, `stopping`, `expired`, `failed`; these are **UI/monitor lifecycle states, not authoritative Engine/Kernel states**. Each tab has a separately identified renewable lease; the server tracks a generation counter and last heartbeat, and can discard stale callbacks. Additional tabs extend collection only through their own explicit Start. On final stop/expiry, the backend terminates owned collector process group, closes DB cleanly, and exits. Stopping this group **must never stop an observed service**.

Normal browser disconnect should request immediate lease cancellation. Lost connectivity cannot be reliably distinguished from a temporary pause; a 30-second fail-safe expiry is a test target. If WebSocket/SSE is selected, the heartbeat and lease semantics remain independently necessary; `beforeunload` is not a correctness mechanism. Browser visibility suspension should be tested on mobile.

When the dashboard is inactive, source snapshots may be stale. Static resources and cached historical reads may be served without starting collectors, but an explicit human action is required to initiate new polling. If API startup itself triggers a process, its idle lifetime must be bounded; only Start should activate collectors.

## Presentation

Four panes in one responsive app: **VPS** (CPU/RAM/process/service trends), **Providers** (accounts/capacity with freshness and source), **Activity** (known sessions/jobs with measured vs inferred usage), **History** (snapshots and anomalies). Initial view: inert shell with Start button; no automatic provider refresh, auto-start or background service worker. Accessible tabular alternatives to charts; mobile/laptop layouts; no arbitrary credentials, command lines or PII.

## Open realization gates

- Existing VPS private ingress, socket activation route and unit privileges have **not** been inspected live; test before selecting binding/port strategy.
- Astro + React are operator-proposed frontend candidates, not a decision on backend language or Engine realization.
- The server backend implementation is not selected; compare a minimal native/static path against a maintained process framework on measured idle and active overhead, lifecycle safety, integration and assurance.
- SQLite is the likely **projection store**; confirm path permissions, crash recovery, retention and contention before making it binding.
- Live provider quota read APIs, credentials and polling costs remain unverified; v0.1 must work with static inventory and synthetic usage events before claiming live provider coverage.
