---
title: Projektor Mobile Project Workspace — Project-Local Trial Plan
program: ASES / EDASES
layer: Implementation / Research Feedback
document_type: Project-Local Experimental Plan
status: Draft
authority: Experimental; not adopted ASES policy
date: 2026-11-05
depends_on:
  - docs/proposals/2026-11-02-testing-debugging-ontology/README.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/upstream-change-awareness-addendum-2026-11-02.md
---

# Projektor mobile project workspace — bounded trial

## Local reconciliation: workspace trial and subsequent evidence (2026-11-26)

The November 5 plan remains the preregistered project-local trial, not current operational guidance or an adoption of the draft ontology. Subsequent use of Projektor and Work Notes established a more precise separation: Projektor for human planning, priorities, dependencies and decisions; Work Notes for agent operational state and recoverability; Git repositories for durable technical artifacts and evidence. Apply the [current task-scoped method](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md), not the old Crosslink-dependent implementation or a universal project lifecycle. The method governs ASES, not unrelated projects by inheritance. The human and agent trackers are distinct products/record authorities even when they use similar technology or names.

| Original trial criterion | Later evidence and outstanding boundary |
| --- | --- |
| Actual hosted use and authenticated data access | Projektor owner record ASES-4 reports deployment and authenticated reads, creation of a weekly status wiki page and 13 issues followed by independent relisting on November 15. Subsequent ordinary project coordination also retrieves and updates existing records with readback. This supports actual API use, not the entire original paired phone/browser/API acceptance or permission matrix. UI search/activity, cross-session OAuth and specific mobile workflows remain unqualified in that record. |
| Workspace identity and authorization | PJDEV-10 diagnosed duplicate project slugs across distinct workspaces: the workspace-qualified API correctly refused the foreign project ID; the frontend discarded context. Its tracker is Done, but the retained body says diagnosis/API tests only, no code patch or deployment. Do not promote that status to a verified navigation fix. A restricted-member test remains absent from the November 10 relationship sample. PJDEV-22 tracks recurrent OAuth prompts; a presently working connector does not establish the root cause or durable session behavior. |
| Mobile workspace, graph and timeline | Local Graph/Timeline prototypes and user acceptance feedback are documented in the November 13 assessment and PJDEV records. Native app-shell/navigation, mobile controls, hierarchy and lifecycle-event semantics remain separately tracked; the static/mock browser-test scope is not authenticated live acceptance. No verified latest deployment or source-level portability conclusion follows. |
| Data preservation and upgrade | PJDEV-26 remains todo: the dated deployed v0.9.1 / upstream v0.11.1–0.11.2 observations, Worker MCP-anchor and Graph/Timeline shell failures, and clean rebuild/import proposal are historical. No independently verified clean-store restore, schema-compatible import, rollback or current deployed version was recovered in this review. The [customization method](../../methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md) governs proportionate upstream compatibility, not an automatic upgrade. |
| Cost and infrastructure | The original November 5 account inventory, Workers/R2 conditions and zero-additional-cost target are dated preflight inputs. Actual use is not measured free-tier headroom, current entitlement, invoice reconciliation or a controlled VPS-outage test. Do not refresh billing or provision infrastructure merely for this documentation check. |
| Selective knowledge and conversation references | PJDEV-6's seven-entry source-linked topic sample, three separately addressable draft topic pages and the PJDEV-2 read-only relationship traversal establish bounded useful navigation. The source scratchpad is not canonical topic registry authority. The conversation corpus and archived classification work are distinct from lossless automatic source acquisition (ASES-1). No full semantic graph, mass import, automatic sync, independent restricted-user authorization or complete topic-registration acceptance follows. |

The retained November 10 relationship baseline observed direction inversion, cross-project issue links, wiki-ref attachments and backlinks within the authorized workspace, without testing a second permission-limited identity. Preserve the exact source relationship and treat views as derived; no new generic edge table is required merely to publish a topic pointer. The [early research topic disposition](../../../future-research-topics/README.md) and optional ASES-5 relationship projection retain their separate scope. The current Work Notes Reassessment aligns Chat entrypoints and per-turn material-change routing with the canonical method; it does not establish mechanical enforcement or replace project-specific rules.

**Disposition:** the trial has progressed to actual use and bounded read/write/navigation evidence; the full P0–P6 acceptance was not demonstrated. Preserve the plan as history and reuse its outstanding discriminators only in their actual owner tasks. Projektor Development owns product/upstream/deployment and UI acceptance; ASES owns its own source authority and optional retrieval/relationship research. Do not create another work tracker, require a universal project graph, copy private conversation sources, restore Crosslink, or run old trial steps automatically. The existing upstream assessment and owner records are the basis for further decisions. Source evidence: ASES-4, PJDEV-2/6/9/10/14/19–22/26 and the November 10 baseline, topic sample and November 15 status review. The owner fork/deployment repository was not located in the bounded connected GitHub searches; current source/production identity remains unverified. Source cutoff [58088846](https://github.com/rock-solid-sites/ASES/tree/58088846b397ad052134bfed92592884ad1f9830). No new tests, deployment, upstream survey, billing check or Actions.

## Authority and scope

This is a **project-local experiment plan**, not an ASES-wide adoption of the draft testing, debugging or ontology roles. The November 2 method bundle is proposal-only. No Projektor installation, Cloudflare deployment, permission change, provider billing activation, Crosslink migration or global methodology promotion is established by this document.

**Original operator goal:** a **$0 additional-cost**, reliable, self-hosted/open-source, iPhone-usable project workspace for updating project knowledge, plans, milestones, scheduling, funding applications and cross-project conversation references, independent of the development VPS. FlareMo remains the separately planned small two-person shared notes app. Existing Git repositories and Crosslink remain authoritative for engineering artifacts and execution.

**Candidate:** [TAJD/projektor](https://github.com/TAJD/projektor), a MIT-licensed Cloudflare Workers project/issue tracker and wiki with REST and MCP surfaces. Deployment model: a pinned public release in a private **config-only** deployment repository, Cloudflare Workers and isolated D1/KV/R2 resources, with Cloudflare Access.

## System-of-record boundaries — do not silently collapse

| Concept | Initial authority | Projektor use |
| --- | --- | --- |
| Canonical ASES methods, source code, verification evidence | Git repositories and retained original artifacts | Links and human-readable summaries; edits upstream only through existing review/push workflow |
| Engineering work-unit execution, agent lifecycle, agent sessions | Crosslink / work-unit implementation / resource solver, as applicable | Portfolio-level plans, dependencies and milestones; do **not** claim issue status equals actual execution or settlement |
| Accounts, quotas, allowances, estimated and measured spend | Existing JSON resource/account registry and solver | Links to resource records; avoid a second authoritative balance |
| Funding opportunities and applications | Trial Projektor workspace record while evaluated | Candidate tracker with program, track (ASES vs HMS), eligibility, deadline, last verification, application round, requested award, actual award, next action |
| Conversations | Original archived chat JSON/export where available | Stable references, summaries, decisions and many-to-many project/topic associations; do not duplicate raw archives by project |
| Everyday shared notes | FlareMo candidate, independently tested | Not included in Projektor trial |
| Hosted project state | Isolated Projektor D1, KV and R2 if provisioned | Disposable until export/restore acceptance is demonstrated |

Research provenance must distinguish user-supplied fact, source inspection, test observation, interpretation, recommendation and authorized decision.

## Upstream reconnaissance and cost preflight

Before editing source or deploying, record:
- the actual pinned Projektor release/tag, release archive digest, latest upstream release, mainline commit and relevant known issues; avoid automatic upgrades;
- the release's actual `wrangler` template, migrations, bound resources, D1/KV/R2/DO requirements, API/MCP parity tests, access configuration and script versions;
- Cloudflare's actual account plan and product entitlements; current account read-only inventory (2026-11-05) had one existing ASES D1 database, six Worker scripts, **zero KV namespaces and zero R2 buckets**. Never reuse the ASES scheduler database;
- **R2 requires a subscription checkout even for included free usage**. Having zero buckets does not establish whether the subscription is active. Do not activate usage-based billing or a paid plan under the $0 requirement without an explicit separate decision;
- Workers Free CPU budget (10 ms per HTTP invocation) and other per-product free-tier constraints. Treat free-tier fit as unverified until the actual pinned release runs and usage is measured;
- the newer `scripts/release-assets/wrangler.example.toml` includes two KV namespaces, a rate-limiter SQLite Durable Object, and a separate optional realtime DO. Current CF docs say SQLite DO works on Workers Free; older Projektor docs may say the optional WebSocket feature is paid-only. Verify the pinned artifact, not prose alone.

If R2 is not activated and checkout is required, stop before billing enrollment; evaluate whether an upstream-supported attachment-free deployment exists or whether a narrow optional-R2 adaptation could be justified. Do not casually fork the entire application.

## Trial phases and evidence gates

### P0. Preregister the minimum acceptance and competing hypotheses

Acceptance:
1. iPhone Safari / Home Screen PWA can view and edit a project plan, wiki section, milestone/issue, funding deadline; data persists after reload and a separate session.
2. Agent via REST/MCP reads the same project record changed on phone and can update a permitted section without erasing adjacent content.
3. At least one archived conversation is indexed *once* and referenced from two distinct projects; original source and any summary remain distinct.
4. Protected app/API cannot be read or edited by an unauthorized identity or via an alternate publicly accessible hostname.
5. A backup can be exported and independently restored into clean storage.
6. No extra paid plan or charge; metrics remain in relevant free-tier limits; VPS outage does not affect operation.

Candidate explanations for failures should include wrong client surface, Access/OAuth discovery, Worker CPU limit, D1 schema/migration, KV/DO binding, R2 subscription, app logic, stale client state, MCP role/permission and broken test fixture. Do not assume a code defect.

### P1. Baseline and lowest-cost local checks

Use upstream release documentation and existing tests first. Test import/build or artifact validation in an isolated development environment; no production mutation. Identify one working / one deliberately invalid API case, expected output before execution, and the independent oracle. Preserve commit/tag, test command and raw output where possible. No giant generic test suite required before the primary premise is checked.

### P2. Isolated staging deployment — gated on free-tier preflight

Use unique resource names, separate D1, KV, OAuth KV and R2 if truly available under the accepted account conditions. Pin release; secure hostname with Cloudflare Access, and verify alternate URLs do not bypass the gate. OAuth discovery metadata may require narrow carve-outs, but protected app data and token issuance must not be exposed. Start with a single owner and synthetic projects; enable only required functions. Do not turn on automatic upstream release adoption.

### P3. App, persistence and MCP parity

Produce paired browser/API tests:
- valid project and issue create/update/reload versus unauthorized/wrong-workspace edit rejection;
- wiki section edit preserves unrelated sections;
- issue status change does not pretend Crosslink execution occurred;
- same object fetched via UI and MCP/REST returns the expected persisted state after fresh reads;
- failed authentication versus wrong route versus D1 migration error are recorded distinctly;
- client acknowledges a change **and** fresh D1-backed read observes it.

### P4. Mobile and knowledge model

On real iPhone, verify touch editing, Home Screen launch, keyboard behavior, legibility, back-navigation, search, date editing, failure indicators and reconnect/reload. Do not assume offline editing support unless verified. Seed only six representative records: ASES kernel, ASES resource solver, HMS, funding application, shared infrastructure, and one cross-project conversation. Check whether a conversation can link to multiple projects without duplicate copies and without a false claim of canonical authority.

### P5. Data preservation and release rollback

Export current staging data to a separate copy, check hash / readability, restore to a clean D1 instance and compare selected record IDs, issue state and wiki revisions. Distinguish capture attempted, upload succeeded, hash checked and **recoverability demonstrated**. Test a harmless pinned-release rollback in staging and verify database compatibility; code rollback does not automatically roll back D1 migrations. Store substantial artifacts outside native CI; a GitHub Actions job URL alone is not a durable archive. Prefer the available external off-site backup mechanism subject to $0 and credentials constraints.

### P6. Decision and selective hardening

Adopt unchanged if P0 acceptance is met within $0 limits. If only a small, isolated defect remains, use the debugging loop to identify the cheapest boundary test, record the hypothesis and intervention, and verify the original iPhone workflow after correction. If the core architectural assumption fails, reject or defer rather than invent a rewrite merely to keep Projektor. Do not run independent ontology-review agents mechanically; use a targeted conceptual review only if the system-of-record and identity/authority distinctions prove ambiguous.

## Trial evidence record

Use a compact, append-oriented record: claim ID, frozen baseline/expected falsifier, tested account/client/hostname, exact release/commit and environment, paired valid/invalid controls, test instrument state, raw observation, execution status, evidence quality, archive state, interpretation, WHAT-NOT-TESTED, decision and next action. Keep actual CF usage metrics separate from estimated usage or any provider-billed settlement. Do not record secrets in test artifacts.

## Minimum rollout / non-goals

**Trial:** one pinned upstream release, isolated private app, a few synthetic records, browser/MCP tests, export/restore, measured free-tier usage. **Not in trial:** replace Crosslink, move canonical ASES specs into the wiki, import the whole conversation corpus, migrate provider balances, build a new ontology registry, enable a full multi-agent fleet or automate funding submissions.

After successful acceptance, gradually import project summaries and application tracking, then explore a one-way mapping from Crosslink milestones. Require a demonstrated benefit before building bidirectional synchronization or a custom Projektor fork.

## References

- [Proposal bundle](https://github.com/rock-solid-sites/ASES/tree/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology)
- [Testing and assurance proposal](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md)
- [Debugging and fault isolation proposal](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md)
- [Upstream-change awareness addendum](https://github.com/rock-solid-sites/ASES/blob/main/docs/proposals/2026-11-02-testing-debugging-ontology/upstream-change-awareness-addendum-2026-11-02.md)
- [Projektor deployment instructions](https://tajd.github.io/projektor/guides/deploying/)
- [Projektor source](https://github.com/TAJD/projektor)
- [Cloudflare R2 subscription requirement](https://developers.cloudflare.com/r2/get-started/)
- [Cloudflare Workers Free limits](https://developers.cloudflare.com/workers/platform/limits/)
