---
title: Paseo Cloud Execution Environment Registry — 2026-10-31
program: EDASES
layer: Research
document_type: Registry
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md
related_documents:
  - docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md
  - docs/research/Paseo Integration Research Findings 2026-10-31.md
  - docs/research/Paseo Resource Planner Parallel Track and Identity Domains 2026-11-01.md
  - docs/methodology/Agent Model Launch Routes.md
last_updated: 2026-10-31
---

# Cloud execution, toolchain and storage candidates for Paseo/ASES

**Scope:** Complete working inventory of cloud environments and associated infrastructure considered in the October 2026 discussions, including confirmed accounts, low-cost possibilities, historical/deprecated options and *non-compute* adjacent tools. This is a research registry **not** a declaration of available balance, supported integration or provider approval. Last public verification: 2026-10-31. Check per-account dashboards, live order pages and current terms before including anything in a plan.

## Status, accounting and placement schema

- **User-confirmed:** user has the account/host; does *not* establish current available capacity or working API integration.
- **Published:** provider documents the capability; not yet tested in our environment.
- **Candidate:** attractive but price, access, permission or setup unverified.
- **Restricted:** technically possible, but contractual/resource/security constraints may disallow intended use.
- **Discontinued / excluded:** historical research only; cannot be chosen by router.
- **Recurring free:** refresh each known billing/quota period. **Intro credit:** one-time and must not be projected into future months. **Included with subscription:** finite model/task allowance; does not imply free shell compute. **PAYG:** requires hard spending/teardown limits.
- **Managed agent:** provider supplies model plus cloud computer; cannot assume custom OpenCode model/harness can run. **Workspace:** Linux session where separate coding CLI may run. **Batch:** noninteractive CI/serverless jobs. **Persistent:** daemon-coordination host. **Provisioner:** controls someone else's compute; provides no free machine itself.

Any adapter needs these fields: service + account; capability class; plan/terms/expiry; memory/CPU/disk/architecture/region; price basis; quota balance+reset+confidence; initialization/cache/transfer costs; allowed workload and data sensitivity; launch/status/logs/results/cancel/delete availability; origin/provenance; evidence retention. Record whether the metric is observed, provider-documented, inferred or user-entered.

## A. Existing or primary candidate execution environments

| Environment | Type | Economic/technical position | Status and integration note |
| --- | --- | --- | --- |
| **HOSTKEY IT3812 Italy** | Persistent VPS | Existing 4 shared vCPU, 8 GB RAM, ~120 GB NVMe; annual renewal $61.91 around Nov 11; restrictive sustained CPU/IO rules | **User-confirmed** baseline. VPS runbook/recovery problems unresolved. |
| **TNA Hosting Hybrid-8 / Hybrid-12, Chicago** | Persistent VPS | 8 GB / 3 vCPU / 300 GB cached HDD; 12 GB / 4 vCPU / 500 GB cached HDD; Halloween recurring 10% coupon yields anticipated $45 / ~$58.50 yearly, subject to checkout | **Candidate** replacement. Older Xeon, US latency, HDD random IO; SolusVM VNC/rescue to test; provider impact-based CPU explanation. |
| **GitHub Codespaces** | Interactive workspace | GitHub Free **personal**: 120 core-hours/month, 15 GB-month storage; 4-core workspace consumes 4 core-hours each hour | **Documented; user has GitHub.** No equivalent free organization Codespaces allocation; verify permissions, billing, image/toolchain/stop lifecycle. |
| **GitHub Actions** | Batch CI | Eligible standard public repo workflows free under GitHub terms; current GitHub Free private/internal included compute **$12/month** per eligible billing account, not a universal pool of 2,000 private minutes | **Documented; user already uses.** Use for genuine repo CI/testing; don't build a disguised generic unlimited compute farm. |
| **Codex Cloud (ChatGPT plan)** | Managed agent + cloud VM | Included use is plan/window-limited, not unlimited; candidate to coordinate and/or run bounded agents on its hosted Linux instance | **Account accessible; orchestration/delegation reported useful.** Launching OpenCode CLI children from Cloud still **unverified**. |
| **Mistral Vibe Code Web** | Managed cloud coding agent | Free cloud sessions previously reported (2/day, subject to plan/region/current controls); distinct from Mistral API and local Vibe CLI | **User signed up; provisional.** Obtain account-specific limits and external lifecycle/automation support. |
| **Modal Starter — Functions/Sandboxes** | Batch and interactive sandbox | **User-confirmed $30 recurring compute credit per month**; covers Functions and Sandboxes; limits/preemption/session storage differ; Shared Endpoints inference token billing excluded | **Primary candidate.** Burst Rust compile, test, browser jobs; protect against accidental overrun and persisting sandbox. |
| **Daytona Starter** | Cloud sandbox / CLI workspace | **$200 one-time introductory compute credit**, not monthly; one-hour Starter sessions, programmatic snapshots and lifecycle | **Candidate**, first portable OpenCode worker test; store results before expiration. |
| **E2B Hobby** | Cloud sandbox / CLI workspace | **$100 one-time credits**, 1-hour sessions, 20 concurrent sandboxes and default modest CPU/RAM | **Candidate**, second independent portable worker runtime. |
| **CodeSandbox Build / SDK** | Cloud VM sandbox | Free Build tier has SDK lite and up to 4 vCPU/8 GiB per sandbox; exact recurring free VM runtime credit **not confirmed** | **Candidate** pending dashboard check. Free plan existence is not proof of free recurring machine-hours. |
| **Vercel Sandbox, Hobby** | Cloud sandbox | Public pricing: 5 active CPU-hours + 420 GB-hours memory/month, separate quotas; **Hobby noncommercial use restriction** | **Restricted** for agency/client work; assess only personally eligible workloads. |
| **Railway Free / SSH dev box** | Small cloud services / development shell | Public Free plan/limited credits and short-lived interactive environment | **Restricted/deprioritized.** October 21-22, 2026 breach of internal systems and some environment variables; do not store broad AI credentials. |
| **Google Cloud Shell** | Temporary interactive shell | Free interactive utility, up to 50 h/week, 5 GB persistent home; noninteractive jobs terminated, 12-hour session cap | **Auxiliary only.** Policy/design are not for unattended ASES execution, and cached work has strict limitations. |
| **Google Antigravity** | Agent-first Google platform | Mentioned by Google as successor direction in Jules shutdown notice | **Research candidate only**; no free quota, usable API or permission tested. |

Primary official source links: 
- https://docs.github.com/en/billing/reference/product-usage-included
- https://docs.github.com/en/billing/concepts/product-billing/github-codespaces
- https://modal.com/pricing
- https://www.daytona.com/pricing
- https://e2b.dev/pricing
- https://codesandbox.io/pricing
- https://vercel.com/pricing
- https://docs.cloud.google.com/shell/docs/quotas-limits
- https://blog.railway.com/p/preliminary-report-october-security-incident
- https://jules.google/docs/changelog/2026-10-29

## B. Hourly / annual server capacity to investigate

| Provider or offer | Nature | Policy and status |
| --- | --- | --- |
| **OVHcloud hourly VPS/compute** | Disposable high-memory burst VM (previous example 32 GB hourly) | **Candidate PAYG**; model actual hourly + disk/IP charges, delete proof. Shelving/snapshot behavior differs from deletion. |
| **Hetzner Cloud CX/CPX** | PAYG cloud VPS, Germany/Europe/US choices | **Candidate**; previously attractive CPU price but desired sizes out of stock at last check; stopping does not necessarily stop charges; recheck availability. |
| **VM6 UK EPYC E8 / seasonal offer** | 8 GB / 4 vCPU / 120 GB NVMe annual promotional VPS | **Candidate**, pre-order/checkout and sustained-CPU-policy verification required. |
| **HostBrr (8, 12, 16 GB options)** | European shared-CPU VPS | **Candidate**; impact-based resource policy, advertised rescue/VNC; price/stock/check-out verification remains. |
| **ServerHost 8 GB seasonal** | 8 GB / 4 Xeon vCPU / 120 GB NVMe, ~$59.99/year promoted | **Candidate**, investigate region, CPU behavior and recovery before migration. |
| **SolidVPS Halloween** | 8 GB/80 GB SSD and 16 GB/120 GB NVMe seasonal offers | **Candidate**, limits and renewal changes; currently not stronger than known baseline on all dimensions. |
| **HostDZire seasonal** | Published India 12 GB / 8 vCPU / 120 GB NVMe promo and other offers | **High-risk candidate**; past incident and fair-use policy; pricing and fit unverified. |
| **NolimitHost October Budget** | Frankfurt EPYC 8 GB/80 GB, 12 GB/120 GB monthly offers | **Candidate**, substantially above annual bargain targets at published monthly prices. |
| **ForgeHost Spooky** | NL EPYC 8 GB/50 GB at €5.99/month, larger tiers | **Candidate but weak fit**; advertised RAM at reduced CPU/disk, check live availability. |
| **Hostishere Halloween** | Frankfurt Ryzen 7950X3D, 8 GB/5 vCPU/80 GB at €11.99/month | **Candidate for burst-performance economics**, not cheapest persistent 8 GB. |
| **HyperHost Solutions UK Halloween** | 8 GB/4 vCPU/80 GB advertised £59.35/year | **Candidate**, not below HOSTKEY; CPU type, rescue and renewal check. |
| **TNA other Hybrid/SSD tiers** | Different RAM, storage and billing cycles | **Candidate**; compare whole plan; Hybrid-4 may suffice only after measured Paseo footprint. |
| **ComputeBox promotion** | Previously attractive low-cost VM | **Excluded until reconfirmed**: prior price found stale; no current checkout evidence. |
| **Oracle Always Free** | General-purpose free VM | **Excluded** after user's unsuccessful attempt; do not present as a reliable fallback. |
| **HOSTKEY renewal** | Known cost/control baseline | **Real option** even if not ideal; compare migration time, CPU/IO policy and reliable rescue against nominal savings. |

Promotional provider offers are **snapshots, not buyable inventory**. They do not become available compute until location, stock, tax, checkout, renewal and active-resource rules are verified. Include region latency, CPU share, IOPS, rescue/console and refund/delete policy in comparisons.

## C. Orchestration, provisioning and related tools — not free compute

| Technology | Role | Status |
| --- | --- | --- |
| **Paseo (desktop, daemon, CLI, plugin system)** | Management plane; wraps existing agent CLIs, workspaces, browsers and session tools | **Selected**, no large fork. Native desktop browser and plugin navigation promising; real model/tool integration in progress. |
| **Codex CLI** | Harness / authorized orchestrator or specialist, may run on VPS/other Linux host | **Existing**; model quota and host compute are distinct. |
| **OpenCode CLI / OpenCode Go** | Harness + model access plans | **Existing**; consumes compute on whatever host runs it. Do not count model access as cloud machine-hours. |
| **Mistral Vibe CLI** | Local agent harness / API use | **Existing access**, distinct from Vibe cloud sessions. |
| **DevPod (Loft)** | Open-source portable devcontainer provisioning through SSH/cloud providers | **Potential launcher**, not a new capacity pool. |
| **Coder Community** | Self-hosted workspace lifecycle platform | **Optional comparative research**; likely duplicate Paseo operations and add running cost. |
| **Bunnyshell** | Managed ephemeral dev-environment platform atop bring-your-own cloud | **Low priority**: platform fees plus underlying infrastructure; not equivalent to free compute. |
| **Eclipse Che** | Kubernetes-oriented workspaces | **Excluded for current small-VPS/no-Kubernetes design**. |
| **Devbox** | Reproducible toolchains | **Useful setup optimization**, not compute provider. |
| **Paseo Workspace Spaces / Workboard / Project Notes** | Project and session organization plugin prior art | **Evaluate compatibility** before writing a custom project-chats panel. |
| **OpenCode usage/token/TPS plugins** | Existing per-model/session telemetry prior art | **Reuse measured signals**, not a full new observability stack. |

References: https://paseo.sh/docs ; https://paseo.sh/docs/browser ; https://paseo.sh/docs/plugins/reference ; https://devpod.sh/ ; https://coder.com/ ; https://www.bunnyshell.com/comparisons/github-codespaces-alternative/ .

## D. Research-history entries that must NOT be routed

| Environment | Historical appeal | Current exclusion |
| --- | --- | --- |
| **Google Jules** | 15 free tasks/24h, 3 concurrent, REST API; excellent on paper | **Official October 29, 2026 shutdown announcement:** finish active work by **November 11**, read-only after, shut down **December 31**. Not a future integration target. https://jules.google/docs/changelog/2026-10-29 |
| **Ona / former Gitpod Cloud** | Cloud workspaces and advertised up to $200/month for approved OSS maintainers | **Shuts down October 31, 2026; new signups closed.** Historical, not available. https://ona.com/stories/ona-core-shutdown |
| **Codeanywhere** | Comparisons still advertise free IDE hours | **Shut down July 1, 2026.** https://codeanywhere.com/blog/codeanywhere-is-sunsetting/ |
| **Firebase Studio** | Cloud IDE / Firebase workspaces | New workspace creation reportedly disabled in June 2026; **recheck official transition** before any revival; not an active assumed capacity pool. |
| **Hugging Face free CPU Basic Spaces** | Small free hosted CPU deployments | Prior free compute offering reportedly withdrawn for new CPU Spaces; **recheck current account eligibility**. Deployment hosting also not necessarily interactive CLI. |
| **Cloudflare Containers** | Container execution adjacent to existing Workers/Pages | Requires Workers Paid in previous research; **not counted as a $0 execution pool**. Cloudflare Workers/Pages remain viable lightweight endpoints/hosting, not general interactive development VMs. |

## E. Storage and control-plane services, not execution environments

| Provider | Possible role | Caution |
| --- | --- | --- |
| **IDrive Personal TechRadar promotion** | 10 TB first-year backup/archive for $4.98, $99.50 subsequent year advertised | **Not S3 object store**, auto renewal and possible server-backup add-on; original live checkout page was inspected Oct 31. Optional cold archive, not critical Work Unit exchange bus. |
| **IDrive Mini** | Consumer backup (100/500 GB plans) | Verify platform/backup licensing and renewal. |
| **IDrive e2** | S3-compatible independent object storage, 1 TB annual special previously noted | Cost/renewal require checkout; suitable immutable artifacts if API works. |
| **Backblaze B2** | S3-compatible small durable backup/evidence bucket | Separate operations/egress and lifecycle considerations. |
| **Cloudflare R2** | S3-compatible programmable artifact/evidence bucket | Free allowances and request billing; existing Cloudflare ecosystem fit. |
| **Hetzner Storage Box** | Remote rsync/SFTP/restic-like archive and backup | Not S3 and not low-latency filesystem. |
| **Google One / Google Drive** | Consumer sync/sharing and free account storage | Not remote execution, not S3; account limits apply. |
| **Microsoft OneDrive** | Consumer sync/sharing and free account storage | Not remote execution, not S3; account limits apply. |
| **Box, MEGA, pCloud** | Existing/free consumer file/archive options | Usable for export and handoffs where sanctioned; no presumed programmatic cross-worker access. |
| **GitHub repositories, Releases, artifacts and Cloudflare Pages** | Durable source / deploy / limited artifacts | Do not store secrets or treat CI artifacts as permanent without retention checks. |

**Storage policy:** large IDrive capacity plus available free accounts is ample for archival needs. Whole-VPS images are explicitly **not necessary**. Keep irreplaceable source, session handoffs, reference decisions, configs and measured evidence; reproducible build caches can expire. Favor server-local active working storage, independent remote evidence for disposable workers and inexpensive archive storage only when useful.

## F. Adapter priorities and termination rules

1. Native Paseo/VPS + ChatGPT/DeepSeek *live browser links* and project grouping first (not execution-provider adapters).
2. GitHub Actions, Codespaces and Modal are the first existing compute integrations worth measuring; they have documented recurring/plan-included capacity.
3. Codex Cloud, Mistral Vibe cloud, Daytona and E2B are different adapter classes; test only after permissions and lifecycle are understood. Codex Cloud -> OpenCode child remains unverified.
4. Provider scores must include setup/warmth, dependency graph, partial-stage replan, security, cancellation and evidence persistence. No default Sol/MiMo model pins.
5. Exclude discontinued products and stale seasonal discounts from feasibility calculations, while retaining them in this research history.

**Provider-trust rule:** the VPS and all cloud environments may expose source code, logs, secrets or provider session credentials. Minimize scopes and assume the environment can be compromised; the Railway October 2026 security incident is concrete evidence, not a justification to blacklist every host without analysis.

## Maintenance

Recheck active-provider status and pricing when a plan is requested, record last-observed balances and resets, and keep account capacity distinct from published plan maximum. The planner must never invent remaining credits, guaranteed stock, VM performance, safe secret storage or APIs. Promote a provider to **observed** only after a real user-account test with retained evidence.


## G. Identity-domain scope and account multiplicity (operator correction 2026-11-01)

Three **separate** identity domains are required: `ases` (dedicated future GitHub identity planned; current research repo is under `rock-solid-sites`), `hms` (dedicated future identity planned), and `tripn` (**existing GitHub account `tripn-chill-zone` with the production site**). HMS is **not** Trip'n's owning identity. Do not move, mutate or assume control of Trip'n production in research/prototype stages.

Register a **provider-account record per domain and service**; resources, subscription/model allowances, quotas and access tokens bind to that account. A common Paseo project view is not authority to pool allowances, move source code, reuse credentials or charge another project. The prototype fails closed on cross-domain account routing; shared resources would require a separate explicit scoped grant and legitimate provider permissions. Not every provider permits multiple personal/free accounts or duplicated promotional credits; account provisioning and free-allowance eligibility must be verified service by service, and organization/subaccount structures used where appropriate. This table is an inventory of possible providers, **not a combined balance across identities**. See `tools/resource-planner/README.md` and the parallel-track identity-domain design record.
