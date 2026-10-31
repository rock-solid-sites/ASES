---
title: Paseo Live Conversation Management and Resource Planning — 2026-10-31
program: EDASES
layer: Research
document_type: Design Record
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Paseo Role Capability Matrix.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
related_documents:
  - docs/ORCHESTRATOR.md
  - docs/methodology/Agent Model Launch Routes.md
  - docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md
  - docs/research/Paseo Integration Research Findings 2026-10-31.md
  - docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
last_updated: 2026-10-31
---

# Paseo: live strategy conversations, linked sessions and resource planning

## Status and priority

This is an **operator-directed design record**, not an implementation claim or a change to canonical ASES methodology. The first user-facing outcome is access to **original, live conversations from this ChatGPT account inside Paseo**, with a compatible approach to DeepSeek conversations. **Do not substitute imported transcript copies or exported archives for this requirement.**

A long-running project (ASES, VPS runbook, HMS, ATProto) can involve multiple separate ChatGPT/DeepSeek strategy conversations and many downstream coding-agent sessions. A conversation can belong to more than one project. The conversations are at a different level from coding-agent Orchestrator, Builder, Reviewer and Auditor sessions; project grouping is not the same as execution authority.

**Order of work:** 1. access and organize original live strategy chats through Paseo; 2. associate chats and decisions with native Paseo and other active agent sessions; 3. prototype advisory resource planning and revisable work-graph proposals; 4. selectively verify cross-environment launch adapters. Current infrastructure blockers are the in-progress VPS runbook and initial integration of existing tools/models with Paseo.

## 1. Original conversations remain authoritative (FIRST)

### User requirement

The **same conversations** available in the ChatGPT application must also be available **through Paseo**, rather than being copied, re-created as Paseo coding sessions or replaced by summaries. Maintain normal history, source account identity, provider-native features and continued conversation where supported. Apply equivalent principles to DeepSeek.

Paseo should allow a human to group live conversations by **project/initiative**, including multiple chats for one project and cross-project membership. It should make it easy to navigate related original conversations and, if possible, let a read-only agent search across them and propose groups. Group metadata and links may be stored in Paseo; the actual source conversations stay in their original applications.

### Technical distinctions and unknowns

- **Live UI access:** Test Paseo's existing desktop browser with signed-in original ChatGPT and DeepSeek conversation URLs and continuity after restart. A browser tab is potentially an immediate no-fork way to use the live service; it is **not evidence** of native Paseo conversation support or automatic cross-chat search.
- **Embedding/native integration:** Investigate whether browser views can be placed alongside workspace views, and whether browser restrictions, login sessions, site frame policies or UI layouts prevent useful integration. Do not imply iframe embedding works without testing.
- **Account-wide discovery and search:** No officially supported ChatGPT personal chat-history API or DeepSeek web-history API has yet been verified for this use. A ChatGPT API conversation endpoint is not necessarily access to ChatGPT product history. Do not invent provider API contracts or rely on scraping account cookies.
- **Links and grouping:** When supported, store source conversation URL/ID, provider, project memberships, user tags, optional user-selected excerpt or decision pointer, last-verified time, provenance and permissions. Indexing or cached summaries are **optional discovery aids**, never the authoritative conversation or an implicit copy of full private chats.
- **Agent access:** Search across all chats is an additional permissioned integration problem. If live provider access is unavailable, state the gap clearly; do not silently implement an import-based workaround.

### Acceptance gate

From within Paseo, a user can open and continue **two existing ChatGPT conversations** relevant to one project, return to their group, and open one DeepSeek conversation under the same project when supported. Verify links work after restart, and distinguish provider-native conversation features from Paseo's navigation features. Cross-conversation **agent search** is a separate gate requiring verified access to the original content; until then, report it unsupported.

### Candidate minimal design

A trusted Paseo **project conversation view** storing links and grouping metadata, using its existing browser/navigation surfaces to open real ChatGPT/DeepSeek conversations. Prefer plugin hooks or native workspace tabs over a large Paseo fork. Explore stronger live integration only after browser-based continuity is proven or rejected.

## 2. Link high-level chats to active execution sessions (SECOND)

- Create typed relationships: project ↔ original conversation; conversation/message/decision ↔ plan; plan/stage ↔ Paseo host/agent session, provider cloud task, GitHub issue/PR, commit and CI job.
- Links are many-to-many and never infer authority from topic similarity. Human strategic discussions remain separate from agent coding-session transcripts.
- Paseo should show agent session state and references from a project group while keeping the ChatGPT/DeepSeek conversation usable in its original form.
- Human users and authorized orchestrators can inspect detailed logs, diffs, code, web results and test evidence **on demand**. Defaults are compact structured summaries with citations to independently stored evidence.
- Red-before-green tests, reproducible revision identifiers and independent reviewers are the assurance model; orchestration need not consume raw diffs by default.

**Acceptance gate:** Navigate bidirectionally between two live strategic chats and at least two related Paseo agent sessions. Summaries must cite actual test evidence, source conversation links and repository revisions. Provider session types that Paseo cannot natively display are represented as external links until integration is verified.

## 3. Advisory, revisable resource planning (THIRD)

The calculator is **not an autonomous router**. A human or selected orchestrator queries it to discuss several proposed full-graph execution plans. ASES terminology: **Work Unit is a named execution-engine component, not a generic bounded job**. Use *work graph*, *stage*, *job*, *execution plan* and *agent session* for planning.

Separate three dimensions:
1. Models and provider allowance windows (Codex/ChatGPT, OpenCode-accessible model allowances, MiMo, DeepSeek, Mistral and others).
2. Harnesses (Paseo providers, Codex CLI, OpenCode CLI, Mistral Vibe, etc.). OpenCode is **not** CPU/RAM; it runs on a host.
3. Execution environments (VPS, Codex Cloud, Mistral cloud, Jules, Codespaces, GitHub Actions, Modal, Daytona, E2B, hourly VPS, etc.).

A work graph records stage prerequisites, alternatives, parallelism, required memory/CPU/disk, data and cache transfer, model and host concurrency, expected verification, security boundaries, resource windows and downstream capacity needs. Placement must optimize the **whole graph**, not greedily the next stage. Related jobs may be cheaper in one already-prepared workspace.

Give the operator/orchestrator a few fully feasible alternative plans (e.g. quota-first, earliest finish, most conservative compatibility), their expected credits/cash/time, uncertainties and evidence. As actual results differ, recompute **unfinished** stages while preserving completed results, previous estimates, and why assignments changed. Use Paseo usage surfaces and established OpenCode usage/TPS plugins as prior art, not a new redundant telemetry stack.

No default model or role is hardcoded: Sol as orchestrator and MiMo as summarizer are **examples**, not requirements. Codex as summary-only orchestrator has been effective in prior ASES trials: it normally receives compact subagent results without reading raw artifacts, but can inspect them on demand. Codex Cloud launching external OpenCode agents remains **untested**.

## 4. Optional cross-environment execution (FOURTH)

Paseo is the **management plane**, not a replacement for Kernel-0, Work Unit or Observer. Retain an affordable persistent Linux VPS for Paseo, necessary services, reference experiments and recoverability. Offload expensive builds, Rust compilation, browser tests and other bursts to suitable cloud environments when supported by real quotas. Provider adapters must distinguish hosted agent tasks, shell workspaces and batch compute; not every job needs a Paseo daemon.

Environments, including the VPS, are **not fully trusted**. Minimize secrets, assign least privilege, retain evidence independently, restrict source access, and validate stop/deletion outcomes. Railway's October 2026 incident motivates treating provider secret storage and cloud control planes as potential compromise boundaries.

The current, dated environment inventory is maintained in `docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md`. It includes Codex Cloud, Mistral Vibe Web, GitHub Codespaces/Actions, Modal (confirmed recurring $30 compute credit), Daytona/E2B (one-time credits), Vercel Sandbox (Hobby commercial-use restrictions), and hourly VPS options. **Correction as of 2026-10-31:** Google Jules announced its shutdown on October 29; it is historical, NOT a future execution adapter. Ona/Gitpod Cloud and Codeanywhere are similarly discontinued. DevPod is provisioning tooling, not an additional compute allocation.

Do not introduce an always-on automatic dispatcher or rebuild the ASES execution engine as a Paseo plugin.

## Dependencies and validation questions

**Active prerequisites:** VPS hardening/recovery runbook; integrate current agent harnesses, accounts, models, usage reporting, profiles and permissions in Paseo. These remain current blockers for dependable coordination.

**Critical initial questions:**
- Can Paseo open and preserve authentication/continuation for original ChatGPT and DeepSeek web conversations?
- Can Paseo represent project groupings and link those live conversations without copying transcripts?
- Can an authorized agent search original ChatGPT/DeepSeek histories through a supported mechanism, or is that part unavailable?
- Can existing Paseo hosts/sessions and linked external cloud jobs be navigated from a shared project view?
- What provider/plugin/CLI behavior is *actually* present rather than merely documented?
- Can Codex Cloud launch and supervise external OpenCode agents under the proposed trust constraints?

**Non-goals until evidence changes:** chat export/import as a replacement for live access; unsupported account scraping; auto-promoting AI-generated summaries to canonical project decisions; large Paseo fork; untested execution claims.

## Evidence and rationale

Operator decisions in the 2026-10-31 strategy discussion govern priority and scope. This is a plan, **not** proof the implementation exists. Before development, compare current Paseo plugin/browser/workspace capabilities with direct hands-on tests; maintain an explicit capability matrix with statuses *observed, documented, unverified, unsupported*. See `docs/research/Paseo Role Capability Matrix.md` and the active cross-environment model launch routes.

**Key reasoning:** project strategy and agent execution occupy different scopes. Preserving original conversations prevents provenance loss; linking them to agent sessions improves coordination; only after that does resource planning connect the strategy, evidence and execution layers usefully. 


## Research and roadmap follow-up (2026-10-31)

This initial design record is supplemented, not superseded, by:

- [Paseo Conversation-First Integration Roadmap](Paseo%20Conversation-First%20Integration%20Roadmap%202026-10-31.md): ordered phases, active runbook/tool blockers and acceptance gates; original live chats first, session linkage second, advisory planning third.
- [Paseo Integration Research Findings](Paseo%20Integration%20Research%20Findings%202026-10-31.md): sourced Paseo browser/plugin capabilities and known issue #3223, account-history/search gaps, observability prior art, current provider corrections.
- [Paseo Cloud Execution Environment Registry](Paseo%20Cloud%20Execution%20Environment%20Registry%202026-10-31.md): comprehensive categorized integration targets, documented quotas, one-time vs recurring credits, untrusted-cloud boundaries, exclusions and storage.

**Evidence correction:** live original ChatGPT/DeepSeek web conversations must not be replaced with imports; existing Paseo desktop browser support is **documented**, but actual current-account continuation and cross-chat agent search have **not** been verified. The plan remains a proposal until its specified discriminating tests pass. OpenCode is a harness, not compute; Sol and MiMo are examples, not default model pins. The Work Unit name retains its specific ASES engine meaning.
