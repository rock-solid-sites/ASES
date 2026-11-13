---
title: "Account and promotional compute inventories"
version: 0.3.0-research
status: research-active
authority: registry-evidence
last_updated: 2026-11-13
supersedes_revision: 9a122c6c840c39dbe0cefbfc3cf2970b3d0a5a2f
---

# Account & promotional compute inventories

Machine-readable canonical sources:
- [known_accounts_v1.json](known_accounts_v1.json): **29** recorded provider accounts (28 historical plus the 2026-11-13 Northflank update), claimed resource entitlements, unknown current consumption, and verification checklist.
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

## Operator account and onboarding update (2026-11-13)

The operator now confirms an existing **Northflank** account, **OpenRouter** with **$5 in reported monthly credits**, and possession of an **NVIDIA NIM API key**. The account registry records these facts without logging tokens, private IDs or credentials. The $5 is a **claimed recurring allowance**, not a provider-observed current balance; `usage`, awarded this billing period, consumed and remaining are still unknown. API-key possession does not demonstrate usable models, token quotas, or valid permissions.

**Provider selection must not impose an existing-account-only filter.** The operator reports that signing up for eligible free services through GitHub or Google SSO typically takes only minutes. Thus **potential easy free SSO signup** has low onboarding friction relative to conventional account acquisition and can compete with existing but unverified accounts. For each provider the assistant must still verify that the *specific product* permits GitHub/Google sign-in, an actual usable free tier, no unexpected payment-card requirement, network/API access and limits before suggesting signup or starting a job. Never invent already-held accounts merely because signup is easy. Operator action is required for authentication or signup; a free signup is not an automatic authorization for billable provisioning.

Selection should distinguish three separable properties: `account_evidence` (existing versus possible low-friction signup), `product_entitlement` (actual quota, API permissions and billing), and `live_route` (tested invocation, cleanup and receipts). Discovery candidate entries remain unverified until product-specific facts are observed. Existing executable evidence (e.g. an ASES GitHub Actions run) is a useful baseline, **not** a global ranking over other accessible providers.

## Cross-family reviewer inference screen (2026-11-13)

[reviewer-inference-screen-2026-11-13.md](reviewer-inference-screen-2026-11-13.md) versions the task-specific account/candidate screen. The catalogue contains **60 discovery providers**, including six newly researched, **unowned/unverified** inference API candidates (Groq, Cohere, Z.ai, Cerebras, SambaNova, Ollama). The 29-account inventory still identifies only accounts actually reported or observed; new candidate additions are **not** treated as new user-owned accounts. Since model-only reviews generally need neither an OpenCode sandbox nor remote CPU, the first preflight is already owned OpenCode Go/Console and OpenRouter, with Groq/Z.ai as plausible no-card alternatives. Private-source data handling and actual credits/keys are separate gates. No external API or account signup was performed for this screen.

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


## Per-account attribution across programs and providers (draft, 2026-11-12)

- [account_attribution_v1.json](account_attribution_v1.json) describes **workstreams** (who benefits) separately from **provider accounts** (which actual identity is used), **API actors**, **repository owners** and **billing accounts**. It retains the existing Rock Solid Sites-owned ASES/HMS repositories and the separately connected MbD and Trip'n GitHub identities. ASES/HMS-specific future accounts are marked `planned` with no invented handles.
- [account_attribution_v1.py](account_attribution_v1.py) and [test_account_attribution_v1.py](test_account_attribution_v1.py) enforce account references, planned-versus-observed identities, workstream/repository ownership, missing billing attribution and no committed credential values. These are **structural checks**, not authorization or billing verification. This file is part of the existing provider registry, not a new operational database.
- For each execution, record `workstream_id`, `execution_account_id`, `api_actor_account_id`, `repository_owner_account_id`, `billing_account_id`, `product_id`, `meter_id`, `billing_period`, `amount`, `unit`, `correlation_id`, source and time. A single agent job can create **multiple meter events**: GitHub Actions minutes and OpenCode inference usage may be charged to different accounts. Preserve both the benefiting workstream and the actual payer.
- `billing_account_id: null` means **unallocated/unknown**, not free use and not permission to launch. GitHub Codespaces can be user- or organization-billed depending on verified organization policy. Do not automatically assign bills based on repository owner, actor or business grouping.
- Account transitions, repository transfers and reassignments have effective dates and new revisions. Historical usage remains attributed to the account that actually incurred it. New ASES/HMS accounts must be observed before promotion from `planned`.
- The provider's **public product catalogue** remains shared; account-specific quotas, credentials, balances, usage and spending limits remain private, keyed by the stable provider-account ID. Never publish credential material, billing PII or private account identifiers. Independent admission must validate the specific account, payer, quota, credentials and product's rules before a paid or quota-consuming launch.

The [resource-router integration map](resource-router-integration-map-2026-11-03.json) references this account-identity layer while retaining its existing experimental/non-operational status. No usage records have been fabricated and no active billing observer was deployed.

