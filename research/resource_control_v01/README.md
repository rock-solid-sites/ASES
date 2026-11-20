---
title: Resource Control v0.1 — Experimental Controlled-Launch Slice
program: ASES
layer: Implementation
document_type: Research Implementation Guide
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
related_documents:
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - docs/research/Independent Feasibility Gate Requirements 2026-11-01.md
implemented_by:
  - research/resource_control_v01/control.py
  - research/resource_control_v01/server.py
  - research/resource_control_v01/catalog.py
  - research/resource_control_v01/archive.py
last_updated: 2026-11-02
---

# Resource Control v0.1: bounded executable research implementation

**This implementation has not been authorized as a production resource gateway.** It executes **only a durable mock launcher**; it has no Codespaces/Modal/E2B/paid-provider credentials, performs no paid calls and does not pretend to enforce launch routes that bypass it. It is the full synthetic end-to-end *research slice* requested by the [reconciliation](../../docs/research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md), not the complete multi-provider Execution Engine.

## Implemented

- SQLite-backed account/product/period/unit buckets; distinct **CONSUMABLE** allowances and reusable **CONCURRENT** capacities.
- Durable server-issued quotes (claims and estimates cannot be modified afterward), account-bound and snapshot-revision-bound atomic multi-meter reservations, and bounded authorization tokens.
- Strictly separate **RESERVED**, **AUTHORIZED**, **LAUNCH_PENDING**, **RUNNING**, **INTERRUPTED**, **COMPLETED/FAILED/CANCELLED**, and **EXPIRED** states. No inferred successful launch based on an ACK.
- No permission to launch a job with no resource claim. Free-only jobs use a finite nonchargeable concurrent slot, rather than bypassing the gateway.
- SQLite WAL with synchronous FULL and cross-process write serialization. A mock external provider maintains a *separate* SQLite database; external attempt IDs are replay-safe.
- Safe recovery of uncertain external launch: look up the existing attempt at the provider; never create a replacement just because a local confirmation is missing.
- Expiry of **never-launched** reservations; do not release a launch-pending/running resource without evidence of termination.
- Lifecycle and agent-activity intervals, consumable usage, observed overrun, sticky frozen accounting on authorization violations, provider reports, evidenced overlap accounting, corrections and explicit privileged usage adjustments.
- **Provider usage is not blindly added to local usage or reduced to max(local,provider).** Reported overlap is excluded only with explicit matching evidence. Unknown overlap is conservatively counted twice for *availability protection*, and flagged; exact accounting remains unresolved until evidence arrives.
- Immutable zipped session/event evidence snapshots, per-file SHA-256, archive SHA-256, corruption detection and byte-level restoration. Source events and later interpretations are kept separate.
- Passive, independent model-catalog monitor with normalized adapter input, conditional fetch, historic diffs, TTLs and failure-safe behavior. Catalog listings do **not** prove inference capacity or a working credential.
- Loopback-only HTTP API with bearer token for operational requests and separate administrative token for provider facts and manual usage adjustments. No arbitrary command execution or real provider launch.

## Files and test commands

```sh
python3 -m compileall -q research/resource_control_v01
python3 -m unittest discover -s research/resource_control_v01 -p 'test_*.py' -v
python3 research/resource_control_v01/mutation_checks.py
```

The GitHub Actions workflow `.github/workflows/resource-control-v01.yml` runs Python 3.11 and 3.13, including multiprocessing, real subprocess SIGKILL checkpoints and four targeted mutations. Generated-history tests use 80 deterministic multi-job histories and 50 additional synthetic report-overlap cases; those are **fixture instances**, not 130 distinct unit-test methods.

### Running the mock-only HTTP control layer

```sh
export RESOURCE_CONTROL_TOKEN="$(python3 -c 'import secrets;print(secrets.token_hex(32))')"
export RESOURCE_CONTROL_ADMIN_TOKEN="$(python3 -c 'import secrets;print(secrets.token_hex(32))')"
python3 research/resource_control_v01/server.py \
  --db /tmp/ases-control.sqlite \
  --mock-db /tmp/ases-mock-provider.sqlite \
  --archive-directory /tmp/ases-evidence \
  --port 8765
```

The server binds **only to 127.0.0.1**. Use `Authorization: Bearer $RESOURCE_CONTROL_TOKEN` for ordinary calls and the admin token only for account/entitlement changes. Do not put either token, private account metadata or sensitive output in public repositories or logs. This research facade is not a remote multi-tenant authentication service.

The logical HTTP contract is:

| Route | Purpose |
| --- | --- |
| `GET /v1/resources?account=...` | Current account-scoped revision, allowances, reservations, freshness and cost fields |
| `POST /v1/quote` | Register estimates and proposed meter claims |
| `POST /v1/reserve` | Check immutable quote and atomically reserve |
| `POST /v1/acknowledge` | Bind acknowledgement and expiring launch token |
| `POST /v1/launch` | Launch only through deterministic mock provider |
| `GET /v1/jobs/{id}` / `GET /v1/events` | Compact current state and evidence |
| `POST /v1/observe` / `POST /v1/activity` | Cumulative usage and measured lifecycle interval |
| `POST /v1/interrupt` / `POST /v1/finalize` | Preserve unknown execution / finalize only with termination evidence where applicable |
| `POST /v1/recover` / `POST /v1/expire` | Reconcile uncertain mock launch; expire proven unlaunched claims |
| `POST /v1/provider-report` / `POST /v1/reconcile` | Account usage report and conservative availability |
| `POST /v1/register` / `POST /v1/bucket-refresh` | Privileged contract/entitlement maintenance |
| `POST /v1/correction` / `POST /v1/usage-adjustment` | Evidenced manual annotations and ledger adjustment; admin-only |
| `POST /v1/archive` | Snapshot and independently check locally retained session evidence |

The catalog monitor is a separate Python interface because provider-specific public API formats and authentication differ; its `refresh(source_id, fetcher, adapter)` call does not perform inference. Integrate each real provider **only after** confirming its data contract and allowed polling cadence.

## Evidence discipline and test sensitivity

The suite includes valid/invalid neighboring examples for multi-meter admission, account separation, stale snapshots, tampered quotes, token rejection/expiry, concurrent capacity reuse, overrun recognition, stop-evidence requirements, externally reported usage, stale and duplicate provider events, unknown overlaps, manual accounting corrections, archival tampering and the model-catalog failure path.

For crash recovery, children are killed with SIGKILL after specific checkpoints (RESERVED, AUTHORIZED, external launch before local confirmation); the parent opens the persisted authority/provider databases and verifies exact state without trusting the child's final report. These are bounded controlled checks, not a sudden power-loss or disk-corruption proof.

Mutation qualification deliberately modifies the reservation-capacity guard, free-only launch guard, overrun-freeze logic and quote-binding check in isolated copies. Correctly targeted tests must fail for those mutants. A full mutation score is **not** claimed.

Failures, instrumentation mistakes and the reason for a correction are part of the evidence record. A green CI run demonstrates only its tested properties, not real quota settlement or universal authorization.

## Safety / implementation limits to resolve before deployment

1. **No production launch or account access:** No account inventory migration, verified balances, real Codespaces/Modal/Codex/OpenCode adapter, real provider termination proof, or adapter-specific credential scoping. A free-text `stop_evidence` is a research marker, not an authenticated provider receipt.
2. **No complete orchestration engine:** The existing independent work-graph validator and portfolio optimizer are separate references, not yet invoked by this minimal HTTP control service. The future Work Unit and Observer remain distinct.
3. **No production authorization service:** Per-account principal authentication, billing consent, role-based permissions, audit-trusted actor identity, upstream network protection and launch credential isolation require implementation/verification. Admin bearer strings are insufficient for multi-tenant exposure.
4. **Incomplete provider semantics:** Clock-skew, settlement revisions, provider-specific billing periods/reset splits, prepaid and postpaid actual liability, aggregate-only reporting, provider unavailability, lifecycle resizing and provider-specific stop receipts need real adapters and tested policies. Observed external activity may remain unattributed.
5. **Observation provenance:** Local `observe`, `coverage_evidence`, `stop_evidence`, and `source` fields are caller-supplied. Only real signed/authorized provider adapters can make these authoritative.
6. **Evidence retention:** Archive hashing/restoration is implemented locally but remote durable off-host storage, independent backup, privacy classification, recovery cadence and comprehensive transcripts are not configured. Local ZIP hashes are not proof of independent durable retention.
7. **Implementation language:** Python is preserved as an **experimental reference**. Existing ASES policy prefers Rust for production safety-critical admission; no claim of approved production language or deployed enforcement is made.
8. **Provider state/routing:** Published model catalogs, account entitlements and real availability are distinct; the passive monitor has no mandatory external scheduler or configured OpenCode-specific adapter. No model-capability benchmarking occurs here.
9. **Operational maintenance:** Persistent DB schema migrations, failure/repair of corrupt SQLite, journal checkpoint policy and backup restore remain outside this research slice.

Do not merge or deploy this as an all-provider security gateway based solely on unit-test success. Next build stage: independent validation review, typed Rust contract/admission integration, authenticated provider adapter, off-host evidence archive and a bounded real-provider acceptance experiment with no paid-overage permission.
