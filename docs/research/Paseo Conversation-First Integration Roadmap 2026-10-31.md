---
title: Paseo Conversation-First Integration Roadmap — 2026-10-31
program: EDASES
layer: Research
document_type: Design Record
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md
  - docs/research/Paseo Role Capability Matrix.md
related_documents:
  - docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
  - docs/research/Paseo Integration Research Findings 2026-10-31.md
  - docs/methodology/Agent Model Launch Routes.md
  - docs/ORCHESTRATOR.md
last_updated: 2026-10-31
---

# Paseo integration roadmap: strategy conversations first

**Status:** Operator-directed proposed roadmap, not an implementation or proof of working integrations. Paseo is the selected interim management plane; aim to use existing native/plugin surfaces without a large fork. It does not replace the future ASES execution engine, Kernel-0, Work Unit, or Observer.

## Definitions and non-negotiable boundaries

- **Original strategy conversations:** live, authoritative ChatGPT and DeepSeek consumer conversations, at a higher level than ASES Orchestrator, Builder and Reviewer execution sessions. Multiple original conversations may serve one project. They must remain usable at their source, not be imported/copied and substituted as Paseo agent sessions.
- **Project membership:** many-to-many navigation metadata linking original conversations, repositories, decisions and agent sessions. This is organizational and must never imply task-delegation or data-access authority.
- **Execution session:** native Paseo coding-agent session or third-party cloud agent/task; does not become a strategy chat by association.
- **Work graph / stages / jobs:** planning objects for placement and timing. The **Work Unit** is an ASES execution-engine component and must not be redefined as a bounded stage.
- **Placement planner:** persistent advisory interface returning revisable alternative plans, not a global automatic router.

## Overall sequence and gates

| Phase | Desired capability | Observable acceptance gate | Prerequisites / risks |
| --- | --- | --- | --- |
| **0. Current integration foundations** | Finish VPS runbook and integrate existing agent CLIs/models, usage and profiles with Paseo | Reliable control/recovery; verified live model route, status, logs, stop/cancel and session lifecycle | **Both remain current blockers** for dependable execution |
| **1. Live strategy conversations** | Within Paseo Desktop, open, continue and group original ChatGPT/DeepSeek web chats by project | Two existing ChatGPT chats and one original DeepSeek chat can be revisited after reconnect and replies continue at source; no transcript substitution | Native desktop browser documented, provider-specific sign-in not yet verified |
| **1b. Safe discovery / grouping assistance** | Authorized assistant proposes membership/search links across source chats | Source-linked results, explicit authorization, scope and provenance | Source-history API not verified; browser tab access does not equal all-chat search |
| **2. Link discussions to execution** | Bidirectional navigation between project chats, decisions, Paseo agent sessions, external tasks and repo evidence | Project -> source chat -> two native agent sessions -> actual CI/commit evidence -> source chat | Existing sessions and project-link representation |
| **3. Advisory resource calculator** | Work graph with multiple feasible placement proposals, telemetry and replanning | Proposed whole-graph routes include cost/quota/latency/setup/cache and risks; after observed change unfinished stages replan without dispatch | Verified usage sources and resource baselines |
| **4. Provider adapters** | Selectively add managed agents, shell workspaces, batch and hourly cloud execution | Authorized stage starts and stops; evidence retained; cost and resource use recorded | Provider-specific permissions, lifecycle APIs and spending controls |

Phases are **user-visible priority order**, not permission to build a new subsystem while the runbook and current tool integration are incomplete. Targeted documentation research and cheapest compatibility checks may proceed in parallel. No other implementation activity is implied by this roadmap.

## Phase 0: finish the actual prerequisites

**VPS runbook.** Finalize SSH/recovery console reliability, authorized access, credentials isolation, service persistence, emergency stop, actual daemon memory/CPU and disk hotset, and contingency for an 8/12 GB host or smaller replacement. A full VPS image backup is not required by the operator.

**Paseo baseline.** Confirm the installed version, native/remote daemon connection, Windows desktop browser, model catalog, Codex/OpenCode agents, per-provider auth/permissions, subagent lifecycle, terminal/log views, user-facing usage reports and exact API/CLI contracts. Earlier experiments showed MCP fan-out can add measurable RAM; avoid default unnecessary MCP servers on the VPS. Read the current dated launch inventory: docs/methodology/Agent Model Launch Routes.md.

**Safety.** All compute environments, including the VPS, are potentially compromised. The runbook should provide a narrow authority boundary before connecting cloud account credentials.

## Phase 1: access original chats, not imports

Paseo Desktop documents authenticated browser tabs attached to workspaces; its plugin API offers Electron-only navigation.openBrowser to original source URLs. Initial design can be a small project conversation view holding source/provider identifiers and links plus project memberships; the original ChatGPT/DeepSeek websites own chat content, history, native features and continuation.

The first compatibility test must distinguish:
1. Does each original source website sign in and work interactively in the current Paseo desktop browser?
2. Does the exact existing thread continue in the same ChatGPT/DeepSeek account?
3. Does it survive returning to project grouping, closing/reopening a tab and restarting Paseo?
4. Does the plugin/desktop browser open in the correct window and workspace? Public Paseo issue #3223 reports routing/visibility failures.
5. Which native browser features are unsupported on mobile/web clients? Provide a truthful external link; do not force a second daemon-host Chromium browser without assessing RAM and cookies.

The **ChatGPT API** must not be mistaken for an API to all ChatGPT product conversations; a DeepSeek inference API likewise does not establish consumer history access. Reading a browser accessibility tree is not proof of account-wide search. An optional index of *links and user-authorized metadata* can assist discovery without becoming a copy of full private chats.

Assess the existing Workspace Spaces, Workboard and Project Notes plugins before writing a custom organizer; verify version and whether any support external source chats or many-to-many grouping.

## Phase 2: connect chats and execution sessions

Link graph (many-to-many):
- project ↔ original conversation source/provider/account/URL and optional user-approved decision pointer;
- decision/request ↔ proposed graph and stage;
- stage ↔ specific agent session/host/provider, GitHub branch/commit/issue/PR and CI evidence;
- session ↔ current state, permission scope, test/reviewer result and on-demand detailed diagnostics.

This does **not** put all chat transcripts into an orchestrator's context. Default is structured position, cheap-test evidence and concise reviewer verdict, preserving source links. Authorized humans/orchestrators can request and inspect *full logs, diffs, code or raw evidence* when useful. The expected assurance pattern is failing acceptance tests first (where testable), then passing tests on an identified commit with independent review; untestable claims explicitly carry residual risk.

Do not infer authority from membership or permit agents to search entire ChatGPT/DeepSeek accounts without an explicit scope and justified read mechanism.

## Phase 3: revisable, advisory resource planning

A work graph records dependencies/alternatives and resource requirements **for the entire plan**, not only its next step. The planner should make related-stage colocation vs moving work to another environment visible, including workspace warm state, cache locality, setup latency, data transfer, CPU/RAM/disk, model and host concurrency, downstream memory peaks, security and credit expiry.

Return several *feasible* plans for discussion with operator and selected orchestrator, e.g. lowest cash, fastest viable completion and lowest operational risk. State observed vs estimated vs stale usage, failure probability, provider policy constraints, model allowance resets and resource costs. Replan only unfinished stages when actual timing or utilization differs; preserve previous plan, reasons for the revision and immutable completed evidence.

**Models, harnesses, environments and storage are distinct.** OpenCode does not provide free compute merely because model calls are included. Managed coding agent services bundle model and host; separate CLI workers require a shell environment. Sol as orchestrator and MiMo as summarizer were merely examples; do not hardcode either. Use existing Paseo usage reporting and OpenCode token/TPS/cost plugins as prior art, rather than duplicate instrumentation.

The calculator never silently launches jobs. Kernel-0, Work Unit and Observer retain their separate architectural identities.

## Phase 4: provider adapters (after feasible plans)

- **Managed cloud agent:** Codex Cloud, Mistral Vibe Web and other viable future services; observe job status, result and PR through supported interface. A Google Jules API exists but its service is **sunsetting**, so do not add Jules as a new provider.
- **Shell workspaces:** GitHub Codespaces, Daytona, E2B, CodeSandbox, legitimate hourly VPS; CLI harnesses can run there when authentication/network/tool support is actually verified.
- **Batch compute:** GitHub Actions and Modal Functions; plan build/test matrices separately from coding-agent inference.
- **Persistent host:** resource-constrained Paseo daemon, small databases and coordination services on whichever VPS is selected, with desktop local browser rendering.
- **Provisioning tools:** DevPod and alternatives are adapters to *other people's compute*, not free extra cloud environments.

**Critical untested bridge:** Codex Cloud launching and supervising OpenCode children in the same hosted environment. Do not rely on this until a least-privilege test confirms installation/auth, process lifetime, communication and evidence.

Each adapter must expose lifecycle semantics including stop vs delete, provider billing continuation, limits, immutable output and security policy. No automatically dispatched workers or persistent paid VMs without a separately authorized controller.

## Gate discipline: claims and negative space

For every meaningful gate record WHY, WHAT, HOW CERTAIN and WHAT NOT TESTED. Prefer the cheapest discriminating tests before spending cloud credits or changing Paseo. Report refusal/unsupported behavior as evidence. Do not silently substitute an imported chat archive for live access, or a different paid provider for exhausted quotas.

## References

- Existing design decision: docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md
- Research summary: docs/research/Paseo Integration Research Findings 2026-10-31.md
- Provider inventory: docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
- Paseo browser: https://paseo.sh/docs/browser
- Paseo plugins: https://paseo.sh/docs/plugins/reference
- Paseo bug: https://github.com/getpaseo/paseo/issues/3223
