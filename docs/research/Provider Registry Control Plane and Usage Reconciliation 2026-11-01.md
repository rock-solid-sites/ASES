# Provider registry as authoritative control plane — provisional architecture

Date: 2026-11-01
Status: Provisional research decision; implementation and provider-specific access require verification.

## Principle

The provider registry is a safety-critical source of verified capabilities, account entitlements, pricing rules, quota meters, and provider-specific lifecycle semantics. Scheduler admission must fail closed when a hard constraint is unknown or stale. Do not turn estimates into provider facts.

## Three evidence planes

1. **Published provider contract:** product SKUs, supported hardware configurations, model availability, invocation/task limits, billing and reset rules, API semantics. Store source URLs, retrieval timestamps, content digests, effective dates, parser version and independently reviewed revisions.
2. **Account and entitlement observations:** account tier, current model access, remaining quotas, provider-reported usage, active environments, balances and restrictions. Record API source, scopes, observed-at, effective period and freshness TTL. Treat absent API data as unknown.
3. **Runtime telemetry:** Paseo session IDs, job start/stop, environment identity, selected model route, token counters when available, CPU/RAM measurements, retries, interrupts and locally estimated costs. Distinguish measured, provider-reported, inferred and manually corrected values.

Each fact should have provenance, validity window, revision, and confidence class. Conflicting evidence must be surfaced, not silently overwritten.

## Continuous monitoring and change control

- Poll supported official usage/billing/entitlement APIs at provider-appropriate intervals; respect rate limits and avoid unnecessary calls.
- Track documentation and product changelogs with conditional fetches or content hashes; distinguish cosmetic changes from meaningful contract changes.
- Trigger immediate revalidation on failed admission, provider errors, model unavailable responses, quota exhaustion, unexpected billing, new SKU, and catalog version change.
- Maintain an append-only event history and diff; require review before newly discovered paid capabilities or unverified allowances become usable.
- Stale or conflicting safety-critical information blocks new paid commitments; active work follows an explicit drain/cancel policy.
- Verify webhook signatures where offered; polling remains reconciliation fallback. Use backoff and jitter, avoid treating missing reports as zero usage.

## Usage accounting

Represent every usage event with execution/session/job IDs, provider account, product, model route if applicable, meter, unit, period, amount, source, provider event ID if available, and deduplication key. Preserve gross observed usage, settled provider usage, pending estimates, adjustments and disputed discrepancies as separate records.

A single job can debit multiple meters: Codespaces machine runtime and storage, external model tokens or requests, GitHub Actions runner minutes and artifacts, Cloudflare Worker requests and CPU milliseconds, Pages builds and related Worker invocations. Meter definitions are non-fungible. Provider receipts outrank local estimates for billed amounts, but retain both to detect discrepancies.

Use idempotent ingestion, monotonic cursors/watermarks where available, and replay-safe reconciliation. Some providers expose only delayed or aggregate billing data: never claim exact per-job cost without matching evidence. Attribute unassigned usage explicitly instead of silently distributing it.

## Paseo integration

Use Paseo as the preferred launch/control point with a stable execution correlation ID. Record preflight admission, provider/environment/model selection, start, progress, pause, stop, outcome, and post-run usage reconciliation. A session started elsewhere can be imported or manually attributed without inventing missing telemetry. Design provider adapters independently of Paseo so changing launch tools does not break accounting.

## Manual correction

Allow a human to append corrections with reason, evidence reference, author, timestamp, affected events and revision. Corrections must not delete original provider observations. Reconciliation should distinguish provider adjustments, manual attribution, disputed charges and forecasts. Require approval for corrections that increase spending permission or override a safety block.

## Registry lifecycle

Candidate -> documented -> account-verified -> active -> degraded -> draining -> retired. Preserve historical IDs and balances. Provider removal disables new scheduling while preserving committed work and audit records. Re-onboarding creates a new verified capability revision. Add provider-specific contract tests before activation.

## Implementation order

1. Versioned typed provider manifests with explicit unknowns, provenance, and a strict schema validator.
2. Provider adapters for documentation discovery, entitlement snapshots, and usage retrieval; begin with read-only APIs.
3. Event ledger and reconciliation with idempotent provider event ingestion and manual correction records.
4. Paseo correlation and session telemetry, including tasks started elsewhere.
5. Atomic SQLite admission against catalog revisions, observed balances, account policy, and multi-meter claims.
6. Change-detection monitoring, stale-data blocking, drift alerts, failure injection and mutation tests.

## Open decisions

Define provider-specific refresh SLAs, observation TTLs, cost of polling, manual approval roles, model-route discovery, historical price effective dates, and how to handle aggregate-only usage feeds. No claim of automatic fine-grained tracking where the provider does not expose it.

## Verification gate

Red-green-mutation tests for stale entitlement, wrong billing period, duplicate events, out-of-order updates, missing usage, unknown price, changing model availability, provider API outage, restart, concurrent ingestion, manual adjustment replay, and provider retirement. Use real provider documentation as fixtures and separately validate live account-specific observations.
