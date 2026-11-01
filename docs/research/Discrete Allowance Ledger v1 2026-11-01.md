---
title: Discrete Allowance Ledger v1 — Atomic Admission Prototype
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-01
---

# Discrete allowance admission

The new `research/resource-solver/allowance_ledger_v1.py` is a standalone, process-local experimental ledger. Each allowance bucket has five identity dimensions: **account, provider, product, period, unit**. No implicit conversion or borrowing is allowed. An explicit cross-account borrowing authorization is a separate policy concern; an allowance does not become fungible merely because borrowing is permitted.

Admission requires an exact expected ledger version, a unique plan ID, and a nonempty collection of positive integer claims. Claims against the same bucket are aggregated before checking limits. A reservation either succeeds for every bucket or leaves all buckets unchanged. A successful reservation increments the version. Release also requires the latest version.

## Execution evidence

Locally executed `python3 -m unittest discover -s /mnt/data/ases_allowance -v` against the source reproduced in the local container: **16/16 tests passed in 0.013 seconds**. Cases cover account/provider/period separation, exact budget limits, duplicate claims, all-or-nothing rollback, stale versions, duplicate IDs, release, invalid amounts, unknown buckets and two concurrent thread scenarios. In 100 simultaneous attempts with the same version and a fully consuming claim, exactly one admission succeeded.

The repository files were committed after the local run; a clean-checkout CI run is still required.

## Explicit limitations

- **Not production safe**: the lock and version exist only within one Python process. Two replicas or a restart can double-allocate. Distributed admission requires durable transactional compare-and-swap or an equivalent single authoritative serialization mechanism.
- The ledger currently tracks *reserved allowance*, not measured provider consumption. Releasing reservations after real usage would incorrectly restore spent credits. Implement separate reserved/consumed/settled states before connecting to live providers.
- No automatic billing-period rollover, expiration, subscription allowance reset, or credit reconciliation.
- No immutable snapshot signature, account ownership proof, capability authorization, provider terms checks, or persisted audit log.
- **Not yet wired to the v2 scheduler**. Its existing portfolio oracle still uses a simplified account-level synthetic credit budget. A plan-to-bucket claim adapter and end-to-end atomic admission tests are required before the ledger protects actual scheduler proposals.
- The five-dimensional identity deliberately excludes conversion: units must be provider-defined and canonicalized before budget ingestion. Do not silently equate different quota units.
- Test fixtures are synthetic, not actual account balances or entitlements.

## Next gates

1. Integrate an explicit plan-to-bucket mapping and test that every chargeable execution mode produces exactly the right claims.
2. Define durable admission transactions, unique plan idempotency and account-policy revision checks.
3. Distinguish reservation, settlement, consumption, refund and expiry.
4. Test multiple simultaneous scheduler proposals and simulated worker crashes/retries.
5. Reconcile snapshot budget versions against actual provider observations before live admission.
