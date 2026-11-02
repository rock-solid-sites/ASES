# Known accounts and resource entitlements — reconciliation snapshot
Date: 2026-11-02. **Status: user-reported account existence; live billing/usage verification incomplete.** Public-safe version: no email addresses, account IDs, tokens, billing identifiers or other secrets.

This is a distinct layer from `candidate_inventory_v0.json`: a user-reported account is not proof a product, quota, credit, or access credential is active. "Unknown" is **not zero**. Do not admit paid workloads on the basis of this snapshot. Follow `docs/research/Provider Registry Control Plane and Usage Reconciliation 2026-11-01.md`.

## Known accounts

| Provider/account | Claimed offering (public plan, not necessarily this account's entitlement) | Actual account/product verification | Current usage / remaining entitlement | Next read-only evidence |
|---|---|---|---|---|
| HOSTKEY | User-reported VPS: 8 GB RAM, 4 shared vCPU, 120 GB NVMe, Italy, ~$61.91/year | User-confirmed active; hardware from user account history, not refreshed API | RAM/disk/CPU actual utilization unknown; billing term/renewal unknown | VPS panel + guest `free -h`, `df -h`, CPU contention; contract |
| GitHub | Repositories, Actions, Codespaces; personal Free advertises 120 core-hours and 15 GB-month for Codespaces; 2-core hours count as 2 core-hours | Connected GitHub operations observed; precise billing owner, plan and runner usage unknown | Actions minutes, Codespaces core-hours, storage, artifacts: **unknown** | Billing usage/entitlement pages by owner; Actions job logs; Codespaces usage |
| GitLab | Repos, CI pipeline runners, potential workspaces | User-reported account and CI scheduling experiment; quotas unverified | Pipeline minutes / storage / runner consumption **unknown** | Project CI usage and plan panel |
| Cloudflare | Pages, Workers, D1, R2, etc.; Pages Free published 500 builds/month; Workers Free 100k requests/day (10ms CPU per request per Nov 1 documentation) | User-confirmed account and deployed projects; per-product plan unknown | Pages builds, Worker requests/CPU, D1 rows/storage, R2 storage/egress and bills **unknown** | Account-specific analytics + billing; distinguish product meters |
| Modal | Sandboxes, functions, GPU/CPU jobs; Starter historically advertised $30/month included usage | Account and local CLI reported functional; production execution/remaining allowance unverified | Actual spend / monthly available / active apps **unknown** | Billing credits, usage dashboard, plan and CPU sandbox quotas |
| E2B | Agent sandboxes and usage allowance | Account user-reported only | All quotas, minutes, balance **unknown** | E2B billing/limits page |
| Daytona | On-demand developer workspaces/sandboxes | Account user-reported only | Compute credits, usage and concurrency **unknown** | Organization plan and usage |
| Vercel | Projects; Sandbox and standard deployment products subject to distinct meters | Account user-reported | Credits, sandbox usage, build counts **unknown** | Vercel dashboard usage + specific Sandbox entitlement |
| Google / Drive / AI Studio | Google Drive consumer storage commonly 15 GB shared; AI Studio free-tier model/API limitations vary; Cloud Shell is separate product | User-reported account; no proof Google Cloud billing project exists | Drive total/used **unknown** (15 GB not verified account quota); API tokens, quotas **unknown** | Google One/Drive storage usage, AI Studio usage, separate Cloud Billing account check |
| Backblaze | B2 object storage; paid/free allowance depends on plan | Account user-reported | B2 storage, transaction/egress, accrued bill **unknown** | B2 buckets + billing usage |
| IDrive | e2 object storage, IDrive personal/mini distinct contracts | Account user-reported | Allocation and consumed bytes **unknown** | Account plan + used storage by product |
| Box | Cloud files; plan-specific storage | Account user-reported | Total/used **unknown** | Box Account Settings/Storage |
| MEGA | Cloud storage; plan-specific transfer/storage | Account user-reported | Storage and transfer **unknown** | Storage manager / transfer allowance |
| pCloud | Cloud storage; plan-specific | Account user-reported | Total/used **unknown** | Storage dashboard |
| TeraBox | Cloud storage; plan-specific | Account user-reported | Total/used **unknown** | Storage dashboard |
| iCloud / Apple | Storage and sign-in identity | Account user-reported | Total/used **unknown** | iCloud storage settings |
| Tailscale | Tailnet connectivity / device membership, not compute | User-reported Apple sign-in and previously tested connectivity; current policy needs refresh | Devices and active users versus plan limits **unknown** | Admin usage/access controls |
| Mistral | API, developer tools; free-tier constraints and credits change | User-confirmed signup | API requests/remaining allowance **unknown** | Console billing and quotas |
| OpenRouter | Model API aggregator; balances and free model limits vary | Account user-reported | Remaining credit/requests **unknown** | Keys/credits dashboard (do not publish secrets) |
| NVIDIA | Developer APIs or NIM trials, subject to program eligibility | Account user-reported; actual product unknown | All credit/usage values **unknown** | NVIDIA console |
| DeepSeek | Prepaid model API credits; PAYG, not general-purpose compute VM | User-reported account, product use in development | Current balance/spend **unknown** | API billing account |
| Xiaomi/MiMo | Model inference account; token plans and API billing separate | User-reported account, subscription/credits history | Balance/remaining tokens **unknown** | Developer console |
| Phoenix Grove | Inference subscription / plan allowance, not VM | Account user-reported | Remaining shared allocation **unknown** | Subscription meter |
| OpenCode | Go/Zen models, potentially paid plans/credits | User-reported subscription and $5 credit in Oct 2026 | $5 was reported at that time; **not verified as current**; remaining allowance unknown | OpenCode billing + credit wallet |
| Firecrawl | Web research/scrape credits; plan-specific | Account user-reported; API/plugin usage observed | Remaining credits **unknown** | Billing and usage meters |
| Hugging Face | Spaces, inference, hosted services; account-specific quotas | Account user-reported | Compute/storage/credits **unknown** | Account billing and running Spaces |
| Typesafe | Developer account; precise product and entitlements unresolved | Account user-reported | **Unknown** | Identify product and plan |
| ChatGPT / OpenAI | ChatGPT Plus, Codex Cloud, separate API if enrolled; separate quotas | Plus and Codex Cloud environments ASES/HMS user-reported; limits shared/plan-specific | Remaining Codex task/model limits, API balance **unknown** | ChatGPT usage/Codex settings and API billing if account exists |

### Interpretation
- Existence confidence: **user-reported**, not independently audited, unless noted. Connected GitHub is tool-observed. HOSTKEY and some products have additional prior user evidence, not a fresh snapshot.
- Provider advertised entitlement, account-awarded quota, provisioned resources, provider-measured consumption and locally measured runtime are **five different facts**. Do not derive remaining balance without same-unit, same-period values: `remaining = granted + adjustments - provider_settled_use - valid_reservations`.
- A single provider may have distinct product meters (e.g., GitHub Actions vs Codespaces; Cloudflare Pages vs Workers; Google Drive vs Google Cloud; API credits vs VM-hour credits).
- Future revisions should record source URL, retrieved/observed timestamp, period/reset date, owner domain, verification status (claimed / provider-reported / runtime-measured), confidence and observation TTL. Do not commit account-level sensitive billing data to this public repository.

## Immediate evidence checklist
1. Get account-specific read-only billing/usage snapshots for GitHub, GitLab, Cloudflare, Modal, E2B, Daytona and Vercel.
2. Get storage usage snapshots for Backblaze B2, IDrive e2 and Drive; distinguish provisioned storage from free-tier headline totals.
3. Get VM metrics for HOSTKEY, and current subscription/API credit balances for model providers.
4. Audit billing owner and eligible new-customer status separately for HMS and ASES; never assume one program's credit can fund the other's workloads.

Sources: user account enumeration on 2026-11-01, existing ASES provider registry design and source docs, linked provider references therein.