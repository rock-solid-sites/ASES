---
title: Paseo Integration Research Findings — 2026-10-31
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md
related_documents:
  - docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md
  - docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
  - docs/research/Paseo Role Capability Matrix.md
  - docs/methodology/Agent Model Launch Routes.md
last_updated: 2026-10-31
---

# Research findings: live original conversations, Paseo and cloud environments

**Evidence scope.** Dated source/doc/public-issue review as of 2026-10-31, plus earlier ASES/Paseo studies. This research did **not** test the current Paseo desktop installation, authenticate to ChatGPT/DeepSeek through Paseo, attach a cloud worker or measure the user's current quota balances. A vendor's public API/feature page is **documented**, not **observed in the user's account**. Unavailable services remain in the registry for audit history but not in eligible routing capacity.

## Main findings

**1. The initial live-conversation objective is plausibly already supportable without major Paseo changes.** Paseo Desktop provides a native browser tab tied to workspace/project context, retains signed-in browser state, and allows a permissioned agent to inspect/interact with desktop browser tabs. Its daemon brokers requests; actual browser rendering is on the desktop, not the VPS. Paseo plugin screens can use navigation.openBrowser to open the original web conversation URL inside a workspace on Electron.

**Limitation:** No evidence yet establishes that current ChatGPT/DeepSeek consumer sites work in this particular installation for authenticated continuation and persistent history. Importing/exporting/copying chats is not a substitute for original live access.

**2. The source browser is not an account-wide chat-history API.** A browser snapshot exposes a loaded tab, not automatically all previous ChatGPT or DeepSeek conversations. ChatGPT API conversations and DeepSeek inference API conversations are distinct from the respective consumer websites' histories. Native account-wide discovery and cross-provider agent indexing remain **unverified**, especially regarding permissions and privacy. The first milestone can still provide manual project grouping and live links.

**3. There is substantial organization prior art.** Paseo Workspace Spaces groups workspaces/agent sessions in sidebar spaces; Workboard and Project Notes offer project tasks, linked agents and notes. Paseo plugin navigation can open agent/workspace screens and Electron browser tabs. None has been shown to supply full live ChatGPT + DeepSeek project grouping; first examine source/version compatibility before a custom plugin.

**4. Browser-host routing is a real known defect.** Paseo public issue #3223 reports new agent-created browser tabs landing in another desktop window/host, including reproductions in October 2026. A ChatGPT tab was also reported opened through UI but not visible to an agent in the same workspace in a September reproduction. Human visual availability and agent browser-list access are **different acceptance checks**. The issue is not evidence that ChatGPT can't be displayed; it affects orchestration and search.

**5. Native browser vs Shared Browser:** the native browser puts login cookies in the desktop webview; Paseo community Shared Browser runs persistent Chromium on the daemon host, serves multiple clients and stores authenticated profiles on that host. Shared Browser may provide mobile shared-view functionality, but increases VPS RAM/CPU and exposure of account cookies. Do not default to it.

**6. Existing ASES role work already defines the integration boundary.** `docs/research/Paseo Role Capability Matrix.md` inspects Paseo native provider/role enforcement at a pinned October 3 baseline and explicitly treats it as an interim harness, not the future execution engine. `docs/methodology/Agent Model Launch Routes.md` is the October 31 dated launch-route inventory. Their claims and live install state must not be conflated. Earlier ChatGPT-to-Paseo control MCP tests reportedly passed 14/14 in an isolated integration, but this is **not** proof of a deployed end-to-end daemon/tunnel session.

**7. Models, harnesses and compute remain separate resource dimensions.** OpenCode Go includes access to models, not compute hosts. Codex Cloud, Mistral Vibe Web and other managed cloud agents include a hosted environment with restrictions. GitHub Codespaces, Modal, Daytona and E2B provide compute where arbitrary CLIs may or may not install and authenticate. The calculator must keep account/model allowance and CPU-hour storage billing distinct.

**8. The planner is a revisable work-graph advisor, not an automatic dispatcher.** A cheap stage A may be expensive overall when stage B requires 32 GB RAM and many gigabytes of transferred caches. The proposal must compare colocating related stages, setup/warmth, model consumption, network transfer, downstream requirements and provider expiry. Preserve completed work and replan unfinished stages using observed data. Orchestrator and summarizer model choice is runtime-specific; Sol/MiMo are examples only. Normal context is succinct structured status/test evidence, with logs, code and diffs available to authorized orchestrators on request. Red-before-green tests and independent review remain the evidence gates. **Work Unit is an ASES execution-engine component, not a generic bounded job.**

## Capability and certainty table

| Feature | Status | WHAT verified / WHAT NOT TESTED |
| --- | --- | --- |
| Native desktop browser + stored login | **Vendor documented** | Real tabs, desktop host, session state; ChatGPT/DeepSeek account-specific login and continuity **not tested** |
| Browser tool access for authorized agents | **Vendor documented** | Opt-in tools and desktop relay; reliability across child sessions and several windows **not verified** |
| ChatGPT tab visible in Paseo | **Public issue report** | Tab created through UI; source account-wide history and agent tab enumeration **not established** |
| Desktop plugin opens original web link in workspace | **Vendor documented** | Electron navigation.openBrowser; undefined on web/mobile |
| Project/session plugins | **Vendor documented** | Workspace Spaces, Workboard, Project Notes; external-source grouping is a **design candidate** |
| Official all-chat ChatGPT/DeepSeek live API | **Not verified** | Do not invent access, scrape session cookies or silently replace with imports |
| ChatGPT -> Paseo control adapter | **Prior test report only** | Early connector tests passed; production VPS auth, recovery and live routes remain blocked |
| Codex Cloud -> OpenCode child | **Untested** | Check shell, network, installation, authentication, process lifecycle and evidence under least privilege |
| OpenCode token/TPS/cost plugin telemetry | **Community prior art** | Schema, quotas and export lifecycle require actual version/installed test |
| VPS memory savings through eliminating unused MCP fan-out | **Previous audit observation** | Earlier memory/latency measurements were on a specific environment; retest after current tool installation |

## Cloud environment research corrections (material)

| Finding | Evidence and implication |
| --- | --- |
| **Google Jules is being retired** | Its API and 15 free daily tasks/3 concurrent tasks are documented, but **official Oct 29, 2026 turndown**: finish sessions by Nov 11; read-only afterwards; Dec 31 shutdown. Remove Jules from future integration shortlist. https://jules.google/docs/changelog/2026-10-29 |
| **Ona (formerly Gitpod) Cloud closing** | Official shutdown on **Oct 31, 2026**; promotional approved-maintainer credits are historical, not free capacity. https://ona.com/stories/ona-core-shutdown |
| **Codeanywhere already closed** | Official July 1, 2026 shutdown supersedes stale comparisons claiming free hours. https://codeanywhere.com/blog/codeanywhere-is-sunsetting/ |
| **Google Antigravity mentioned as successor** | The Jules turndown points to Antigravity; no price, quota or integration verified. **Research target only**, not available capacity. |
| **GitHub Codespaces** | GitHub Free personal: 120 core-hours/month, 15 GB-month storage; separate from organizational budgets. https://docs.github.com/en/billing/reference/product-usage-included |
| **GitHub Actions** | October GitHub documentation describes $12/month included compute for eligible Free billing accounts; standard public-repo workflow billing differs. Do not rely on old private Actions minute tables. https://docs.github.com/en/billing/reference/product-usage-included |
| **Modal Starter** | $30/month recurring credits for Functions/Sandboxes, not Shared Endpoint inference. https://modal.com/pricing |
| **Daytona / E2B** | $200 / $100 **one-time** sandbox compute credits respectively; finite session durations. https://www.daytona.com/pricing ; https://e2b.dev/pricing |
| **CodeSandbox free Build** | SDK and 4-vCPU/8-GB VM class listed; recurring included VM credit amount not established. https://codesandbox.io/pricing |
| **Vercel Sandbox** | Hobby published 5 active CPU-hours and 420 GB-hours/month; plan has noncommercial restrictions. https://vercel.com/pricing |
| **Google Cloud Shell** | 50-hour weekly interactive quota, 5-GB home and forced noninteractive/session termination. Not a generic unattended build pool. https://docs.cloud.google.com/shell/docs/quotas-limits |
| **Railway incident** | On Oct 21 attacker accessed internal systems and decrypted environment variables in subset of workspaces; vendor report notes AI API keys targeted. Treat provider secret storage as a potential compromise boundary, including on the VPS. https://blog.railway.com/p/preliminary-report-october-security-incident |

The accompanying **Paseo Cloud Execution Environment Registry 2026-10-31.md** enumerates the remaining permanent VPS vendors, hourly instances, managed agent services, sandboxes, batch CI, provisioning tools, excluded products and archival/storage services with their economic and security differences.

## Architecture constraints retained

- User chooses/discusses plans with an authorized orchestrator. Calculator produces competing proposals and stays read-only/advisory.
- The orchestration model and summarization model are selectable per task, not baked into Paseo.
- Native client and daemon are separate; keep browser rendering on desktop when appropriate, rather than paying for extra server Chromium.
- Every execution environment is untrusted to some degree. Scope repo access, credentials, network and stop/deletion; Railway is a concrete threat example.
- Work graph placement must account for late-stage resources and replan after unexpected durations or costs. Environment reuse may be cheaper than splitting work.
- Test quality should be demonstrated by red-to-green outcomes on pinned revisions plus reviewer/auditor review; raw data available for inspection but not sent wholesale by default.
- Keep evidence and indispensable configuration independently; no full VPS image backup requirement.
- Avoid broad MCP enablement on the VPS and don't duplicate Paseo/OpenCode observability mechanisms without measuring gaps.

## Open validation items and cheapest next research actions

1. Wait for / coordinate with current VPS runbook and Paseo current-tool/model integration; verify installed version and actual tools.
2. Test two original ChatGPT conversations plus one DeepSeek live conversation in the native desktop browser for sign-in, continuation and restart; do **not** import.
3. Check Workspace Spaces/Workboard/Project Notes and plugin API for external source URL link grouping.
4. Separately test browser agent visibility and source-site chat search with explicit scoped authorization.
5. Link real chat references to two coding agent sessions and evidence objects in one project; preserve roles and read boundaries.
6. Only then test resource planner with actual usage/quota observations and provider-specific cloud lifecycle adapters.

## Primary public sources

- Paseo native browser: https://paseo.sh/docs/browser
- Plugin screens/navigation: https://paseo.sh/docs/plugins/reference
- Browser host issue: https://github.com/getpaseo/paseo/issues/3223
- Workspace Spaces: https://paseo.sh/plugins/hieppp/workspace-spaces
- Workboard: https://paseo.sh/plugins/fxbing/workboard
- Project Notes: https://paseo.sh/plugins/zhjiang22/project-notes
- Shared Browser plugin: https://paseo.sh/plugins/omercnet/shared-browser
- Paseo docs/CLI: https://paseo.sh/docs
- Google Jules shutdown: https://jules.google/docs/changelog/2026-10-29
- Ona shutdown: https://ona.com/stories/ona-core-shutdown
- Railway preliminary report: https://blog.railway.com/p/preliminary-report-october-security-incident
