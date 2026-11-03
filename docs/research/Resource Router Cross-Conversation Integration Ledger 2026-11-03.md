---
title: Resource Router Cross-Conversation Integration Ledger — Codespaces Pilot
program: ASES
layer: Research
document_type: Integration Ledger
status: Experimental / reconciliation required
authority: Research; no new canonical policy
date: 2026-11-03
related:
  - docs/research/Resource Solver Specification Reconciliation 2026-11-02.md
  - docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md
  - research/provider-registry/known_accounts_v1.json
  - research/provider-registry/potential_offers_v1.json
  - research/provider-registry/candidate_inventory_v0.json
  - docs/proposals/2026-11-02-testing-debugging-ontology/ases-account-enumeration-chat-2026-11-02.md
---

# Resource-router integration ledger: Codespaces first provider

**Purpose:** Collect decisions and source boundaries from the November 1–3 ASES Account Enumeration, Resource Solver, VPS selection, provider registry, Paseo, resource-control and Codespaces launcher discussions into a reviewable project map. This is a provisional synthesis, **not** an adopted Engine specification, account entitlement, scheduler launch permission or claim that a live provider integration works.

Companion machine-readable traceability file: `research/provider-registry/resource-router-integration-map-2026-11-03.json`.

## Existing evidence and branch status

1. **Main:** `docs/research/Resource Solver Specification Reconciliation 2026-11-02.md` explicitly separates (a) account/provider discovery, (b) advisory planning, (c) independent admission and controlled launch, (d) usage and evidence; the Observer and full Execution Engine do not exist. `docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md` defines published contracts, account-specific observations and runtime telemetry as distinct evidence planes.
2. **Main:** `research/provider-registry/known_accounts_v1.json` contains previously enumerated accounts and unknown usage; `potential_offers_v1.json` contains unredeemed offer *claims*, not awards. The prior generic `candidate_inventory_v0.json` is separate again. The files are public-safe snapshots and cannot substitute for restricted account-specific credentials or fresh billing evidence. The November 3 JSON migration commit is `f361c62be6c3af3036341f751a723c8c8ea8a946`.
3. **Unmerged development:** `feature/resource-control-v01-2026-11-02` contains early resource-control research; `feature/resource-control-runtime-2026-11-02` contains experimental Rust/SQLite controller code, scoped meter accounting, bounded reservations, mock launch, lifecycle records, restricted Unix-socket gateway and evidence export. The runtime branch README **explicitly** says no real provider account adapters, authenticated remote transport or hard external spending-limit termination are implemented. Do not infer code on these branches exists on main or is production accepted.
4. **Proposal only:** `docs/proposals/2026-11-02-testing-debugging-ontology/ases-account-enumeration-chat-2026-11-02.md` provides assurance/evidence corrections. Proposed ontology reviewer roles are not an automatic per-launch gate; mandatory admission is a separate mechanical safety check.
5. **Discussion / not yet fully committed:** November 3 Codespaces-launcher design, routing-VPS and remote-compute experiments; further November 1–2 account-enumeration discussions about future Engine role boundaries, deterministic Observer, and ontology design/conformance roles. Their full conversation histories are not reconstituted in this document. Treat summaries here as retrieval pointers needing source-level reconciliation.

## Proposed responsibility boundaries

| Layer | Owns | Specifically does **not** own |
| --- | --- | --- |
| Provider / opportunity catalog | Public capabilities, hardware SKU definitions, published offers, source, validity, pricing | A user's rights to an offer, actual balance |
| Account registry | Identifiers scoped to actual account/payer/project, approved credential route, entitlement and source history | Free capacity inferred from marketing material |
| Account-specific observations | Signed/official responses, effective period, billing owner, limits and actual usage; TTL | Arbitrary permission to spend |
| Advisor / resource solver | Placement choices, predicted memory/CPU contention, latency/cost and alternatives | Authorization or automatic execution |
| Resource-control admission | Independent checks, reservations across distinct meters, rev-bound bounded permission and audit | Provider actions outside approved adapters |
| Codespaces provider adapter | Machine discovery; create/start/stop/status; reconcile provider resources and reports | A second independent planner, alternative entitlement ledger or user-policy decision |
| Paseo / ChatGPT integration | User requests, coordination and correlated session identity | Credentials with unrestricted GitHub ownership rights, bypassing admission |
| Current collectors / evidence | Actual start/stop/usage, provider discrepancies, archives and recovery proof | Pretend the future Observer already exists |
| Future Execution Engine | Eventually consumes these contracts; Work Unit is durable Engine identity | Redefining today's provider jobs as Work Units |

The current resource-control runtime uses a local trusted-controller CLI and peer-authenticated Unix-socket gateway. ChatGPT access requires **another authenticated, authorized and audited transport**, not exposing the Unix socket or giving a third-party plugin direct SQLite access.

## JSON account inventory -> Codespaces adapter integration

**Never turn the existing `github` record's published personal Free claim into a schedulable balance.** The account inventory's `id=github`, claims, `usage.status=unknown` and null meters are a discovery anchor only. The adapter must distinguish:
- account login, exact billing owner, repository owner, authenticated principal, token permission, and authorized project scope;
- the published machine catalog (core count, RAM, supported region/availability, image);
- account-specific eligible plan, current compute limit, storage allocation and used amounts with `observed_at`/TTL;
- actual Codespace ID, machine type, repository/ref, creation time, execution state, changed lifecycle timestamps and storage footprint;
- projected **core-hours** (machine cores × expected running duration) distinct from storage **GB-hours/GB-month** and any external model-token quota;
- current local reservations and running Codespaces *including those started outside the router*, outstanding billable storage on stopped instances, provider aggregation/reporting lag, overages and refunds/adjustments;
- read-only credential checks and explicit spending authorization; no assumed unused free credit.

Proposed adapter transformations:
`public catalog + account observations -> typed provider catalog/entitlement revision -> independent quote and multi-meter reservation -> one-use launch request -> external Codespaces lifecycle -> locally observed usage + provider billing report -> reconciliation`.

The current public inventory should retain redaction and **not** be overwritten with real private account snapshots. The operational ledger is access-controlled and versioned separately, with symbolic public references.

## First bounded vertical slice

1. **Reconcile actual schemas:** inspect `known_accounts_v1.json`, `inventory_schema_v1.json`, `manifest_v0.py`, `resource-control/src/lib.rs`, gateway access policy and branch state. Produce explicit key-by-key mappings; preserve null/unknown, units and source timestamps.
2. **Read-only Codespaces access:** authenticated account/billing identity, list existing Codespaces, available machine types, states, plan eligibility, metered usage and source/freshness. If a provider API has only aggregate or delayed billing, return an explicit gap instead of inventing per-job amounts.
3. **Synthetic fixtures before real account mutations:** external-launch uncertainty, authorization expiry, restart/replay, stale quota, wrong payer, external usage, compute versus stored-data billing, and repeated stop; record red/green/mutation evidence.
4. **Bounded real experiment:** quote 1 × eligible 2-core/8GB Codespace, verify spending and ownership constraints, require approval for actual launch, record provider resource ID, use a short explicit deadline, verify independent stop and retained-data charge, reconcile actual provider report later.
5. **Only after read-only and stop tests:** expose a scoped launcher interface to ChatGPT and Paseo; route both through the *same* admission and ledger. No unscoped shell execution and no auto-creation of environments after unknown launch outcomes.
6. **Broaden providers later:** Modal and Daytona sandboxes, GitHub Actions where appropriate, then paid hourly VMs. Each requires separate meter semantics; do not assume Codespaces billable units generalize.

### Minimal first interface
`list_accounts`, `list_environments`, `quote`, `request_launch`, `status`, `request_stop`, `usage`. Provider delete and high-liability actions are separate explicit authorization paths. A user interface may expose fewer methods.

## Known integration gaps / risks (not an exhaustive audit)

- **Data-model mismatch:** public `known_accounts_v1.json` stores descriptive snapshots, not authorized account-specific entitlement observations; existing Rust `Meter` requires an integer `limit` and fresh `observed_at`/TTL. Unknown must fail closed; don't coerce null to 0, default plan quota or a fabricated integer.
- **Resource model mismatch:** the Rust experimental `Environment` describes concurrency but does not by itself describe all Codespaces machine variants, time-based billing, storage persistence and lifecycle transitions. Add explicit product-specific capability semantics through the provider layer.
- **Launch ambiguity:** network timeout after create/start may mean success; reconcile provider resource IDs before retry. Exactly-once effects cannot be assumed from a one-use local token alone.
- **Hard stop and funds exposure:** a local reservation does not enforce an external cost cap or stop a Codespace after the caller disconnects. An independently persistent reconciler/watchdog and tested provider stop behavior are required.
- **Reporting lag:** local running-time estimates, external executions and provider billing reports can disagree. Preserve original observations, correction and provider settlement separately.
- **Access transport:** GitHub plugin presently exposes repository/CI operations but no Codespaces lifecycle actions; plugin availability is not the same as API availability. Need appropriate GitHub Codespaces permission and restricted chat-facing adapter.
- **Testing and assurance:** historical green mock tests do not prove safe real billing; retain result provenance and execute real provider contract tests. Future deterministic Observer must not be conflated with Auditor or reasoning agents.
- **Related work:** VPS and Paseo orchestration are separate deployment choices. A Codespaces adapter should work from a small routing VPS without requiring a full development server.

## Relationship to long-term roadmap

**Now (research / provisional):** provider catalogs and JSON inventories; Rust prototype safety gate; synthetic benchmarking; independent capability harness and optimizer research.

**Codespaces pilot:** bridge registry to live account observation and a single provider lifecycle; verify partial usage accounting, one bounded launch, stop and reconcile; usable through one trusted launcher.

**Multi-provider resource router:** more provider adapters, account capability refresh and shared ledger, correlated sessions in Paseo, project-scoped authorizations and real-world placement data.

**Later Engine integration:** reuse deterministic resource admission, lifecycle and accounting, with eventual Work Unit mappings and Observer data streams; update ontology/Engine roadmap through its own design-review process before changing those roles. Do not assume such Engine modules currently exist.

## Next reconciliation work

Build a source matrix for *each* relevant conversation and branch, storing `source_identifier`, date/commit, authority, status, decisions, contradictory statements, implemented_by, tested_by, and open gaps. Specifically retrieve full contents of recent resource-control branch specifications and proposals; inspect model-routing and launcher discussions; determine whether ASES Resource Solver and Account Enumeration have uncommitted outputs; preserve source history rather than replacing it with a single summary.

This document deliberately makes no purchase, creates no Codespace, does not alter authority or the public account JSON values, and authorizes no paid work.
