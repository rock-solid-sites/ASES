# ASES Resource Control v0.1

**Status: experimental integration implementation; not a live-provider production gateway.**

Rust + transactional SQLite reference implementation of the proposed Resource Solver
control boundary. The code builds independently of Paseo, the future Execution Engine,
Observer and model capability harness.

## Boundaries

- Account/product/period/unit-scoped discrete meters and physical environment slots.
- Immutable pre-run proposals, quotes, durable reservations, bounded acknowledgement,
  one-use authorized mock launch, lifecycle events, idempotent usage deltas, and provider
  aggregate usage reconciliation. Real usage is never rejected merely for exceeding an
  authorized reservation; overruns reduce availability and are reported.
- SQLite `BEGIN IMMEDIATE` transactions serialize independent CLI processes.
- Catalog and account observations have provenance, freshness and explicit unknowns.
- Compressed JSONL session/event export with digest and read-back validation.
- The CLI is a **local trusted-controller interface**, not a multi-tenant service.
  Run as a dedicated OS identity; never give untrusted orchestrators direct database
  write access. A thin authenticated transport and credential-isolated provider
  launch adapters must be verified before real workloads can be controlled.
- No real provider account keys, balances, payment actions or environments are used.

## Quick start

```bash
cargo test --all-targets
cargo run -- /tmp/ases-control.db init
cargo run -- /tmp/ases-control.db request '{"op":"register_meter","meter":{"id":"codespace-cores","account":"account-a","provider":"github","product":"codespaces","period":"2026-11","unit":"core_minutes","limit":7200,"guard":0,"observed_at":0,"ttl_seconds":0,"source":"synthetic"}}'
```

`observed_at=0` is stale by design and cannot authorize admission. Use a current
Unix timestamp and a positive TTL for fixtures. Actual calls are JSON request/
response; see `src/main.rs` and integration tests for schema examples.

## Safety and operational gaps

Provider catalog polling, remote B2 archival, real inference/compute launch adapters,
authenticated callers and hard expense-limit termination are not yet implemented.
The mock launch path does not claim to enforce external spend caps. Failed external
launch or unknown outcome must be reconciled by a provider adapter before retry;
replaying an uncertain launch must not create a second resource.

The `provider_report` operation accepts an explicit `complete_through` watermark
only if the provider guarantees inclusion of all usage through that point. If no such
guarantee exists, reported cumulative usage is added conservatively to local
observations rather than silently double-counting it as a verified match.
Reductions in cumulative provider totals require a new period or an authorized
adjustment, not an unverified lower snapshot.

## Research relationship

Based on `docs/research/Resource Solver Specification Reconciliation 2026-11-02.md`.
The tested implementation is deliberately narrower than the full multi-provider
specification. Retain older Python research and P1-P7 experiments as evidence; a
local successful test does not establish real-provider billing, credential isolation,
archive durability outside this host or future Engine control.
