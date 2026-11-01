# Funding, billing liability, and language-policy correction — 2026-11-01

Status: binding research direction, implementation not yet complete.

## Financial model

Never classify an entire provider as simply free or paid. Funding belongs to a specific account/product/meter and effective billing period. Each meter needs a funding source, allowance unit, reset/expiry rules, overage behavior, settlement method, balance observation, and spend authorization.

Distinct cases:
- Free recurring allowance: remaining free quota, reset time, and whether overage is blocked, throttled or charged.
- Trial or promotional credit: finite credit, expiry, eligibility, and behavior after exhaustion; never treat as recurring.
- Prepaid wallet / PAYG upfront: available funded balance, minimum required reserve, top-up rules, immediate or delayed debits.
- Postpaid PAYG: liability accrues with execution, invoicing and settlement later; require explicit spending cap, expected maximum liability and uncertainty margin.
- Fixed subscription: recurring fee with included quotas, possible overages, account sharing and billing period.
- Free/unmetered local capacity: opportunity cost, hardware occupancy and external dependency costs can still matter.

Billing frequency, payment timing, allowance reset and charge accrual are independent dimensions. "PAYG" alone does not determine prepaid versus postpaid. Usage attribution may be delayed or aggregated. Preserve both estimated and settled usage.

## Opportunity cost and scheduling

A free Codespace that is already running can have a low incremental monetary cost while another task completes, but consumes finite core-hour allowance, storage and time before idle shutdown or maximum lifetime. It may also consume model allowances separately. An already-paid VPS lease may have zero incremental cost until the next billing boundary; a metered VPS or postpaid cloud VM can accrue liability for every additional minute. Compare marginal cost and scarce allowance consumption over the *actual next decision interval*, not a provider-wide free/paid flag.

Admission must simulate cost across free-quota exhaustion, billing boundaries, idle time, retries and unknown provider reporting lag. If a free quota can spill into paid usage, disallow spill without explicit spend permission. Track the ability to stop, suspend, resize and cancel charges separately.

## Accounting and safety invariants

1. No implicit paid overage; opt-in per account/meter.
2. Do not mistake included allowance for unlimited free runtime.
3. Do not mistake prepaid credit for a postpaid spending ceiling.
4. Keep actual incurred liability separate from paid invoices, remaining wallet, estimated future cost and available free allowance.
5. A running environment may incur cost while idle; an ephemeral event runtime may not.
6. If billing mode or pricing is unknown, do not authorize new financial commitments.
7. Source account-specific balances from official provider APIs when available; stale observations trigger conservative behavior.
8. Record every assumption with provenance, effective time and revision.

## Language selection policy

The committed Python files (`research/provider-registry/manifest_v0.py`, `registry_v0.py`, and their tests) are research prototypes, **not** approved production implementation. ASES prefers memory-safe, type-safe implementation for production; Rust is the default recommendation for the authoritative registry, typed ledger and admission logic. TypeScript is acceptable for provider integrations with runtime validation and bounded permissions. Keep Python prototypes as explicitly superseded research evidence rather than silently presenting them as policy-compliant production code.

## Required next implementation

Implement a typed Rust funding contract with an extensible provider-meter envelope. Include distinct funding source, charge accrual, settlement and overage policy; add red/green tests for free Codespaces vs metered VPS, free-to-paid boundary, prepaid depletion, postpaid liability, subscription inclusion, provider reporting lag and cross-product model allowance. Then integrate it with versioned provider manifests and SQLite transaction semantics. Do not activate scheduling from Python research code.
