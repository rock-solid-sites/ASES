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
