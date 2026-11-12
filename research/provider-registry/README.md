# Account & promotional compute inventories

Machine-readable canonical sources:
- [known_accounts_v1.json](known_accounts_v1.json): **28** previously enumerated provider accounts, claimed resource entitlements, unknown current consumption, and verification checklist.
- [potential_offers_v1.json](potential_offers_v1.json): **26** individually addressable offers/comparators, with credit terms and illustrative rather than provider-quoted compute value.
- [inventory_schema_v1.json](inventory_schema_v1.json): JSON Schema Draft 2020-12 contract.
- [test_inventory_v1.py](test_inventory_v1.py): stdlib static tests, including negative/mutation checks. Run with `python -m unittest discover -s research/provider-registry -p 'test_inventory_v1.py'`. Optionally validate schema with Python `jsonschema` or another JSON Schema 2020-12 implementation.

## Scope and admission
The snapshots were transcribed from the Nov 2, 2026 inventory documents; account existence came from prior user reports and tool observations, *not* live API polling. No paid resource or credit is pre-authorized for the scheduling solver. The existing `candidate_inventory_v0.json` remains a distinct discovery-only provider list.

- `claims` are previously reported hardware / public plan figures, *not* current account grants.
- `usage.meters[].granted|consumed|remaining = null` represents unknown account-specific usage, never zero.
- `credit.advertised_usd` is a promotion headline. `credit.awarded_usd = null` means no award has been verified and must not be converted into available balance.
- `compute_equivalent_scenario` uses hypothetical $0.10–$0.20/hour 8GB x86 VM costs and assumes neither particular provider SKU pricing nor actual eligibility. Special-product IBM credits and Arm Always Free allowances must not be valued as generic x86 credits.
- `source_status=previous_research_not_revalidated` makes freshness explicit; no current offer availability was checked during this formatting migration.
- `account_evidence.status` is evidence about **account existence**, not usage or entitlement.

Future agents should append read-only provider observations or maintain an account-scoped private ledger with exact timestamps, meters, billing periods and provenance. Do **not** commit credentials, account identifiers, billing PII or sensitive usage details to this public repository. For architecture see `docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md`.

## Cloud agent execution discovery (research, 2026-11-12)
The existing `candidate_inventory_v0.json` now retains all earlier candidates and adds
new cloud execution providers. Individual `documented_execution_routes` identify
a product's official launch/trigger documentation, not account availability or
operational readiness. Every documented route is explicitly
`account_access: unverified`, `adapter_state: not_implemented`,
`launch_test: not_run`. A published API must never bypass the independent
Resource Solver admission gate.

- The public catalogue is **discovery-only**; it is not the account inventory
  (`known_accounts_v1.json`) or the credit ledger (`potential_offers_v1.json`).
  It does not store keys, billing identities, actual balances, instance costs or
  executable dispatch instructions.
- `test_execution_discovery_v1.py` validates uniqueness, references, baseline
  preservation and the prohibition on promoting documents into launch authority.
- `probe_execution_sources_v1.py` performs read-only HTTPS HEAD checks of
  public source URLs and records HTTP/ETag metadata. Transport failures or 403/405
  responses are not evidence that a provider or product is unavailable.
- `.github/workflows/provider-registry-observations.yml` runs structural
  tests for repository changes and archives read-only source observations daily
  **once the workflow is present on the default branch**. Until then it is a
  proposed workflow, not an active scheduled monitor. GitHub artifacts expire;
  they are not the authoritative provider state ledger.

### Activation boundary
A route becomes schedulable only when an authorized adapter actually passes
launch/status/stop/recovery tests, account-specific entitlements and usage
are observed with freshness, prices/quotas are verified, secrets are provisioned
outside the public repository, and the deterministic Resource Solver independently
authorizes a bounded one-use launch. No account signups, payments, credits,
provisioning, credentials or live launches were performed in this survey.

