---
title: GitLab Chat-Operated Pipeline Schedule Control - Requirements and Realization Candidates
program: Tooling
layer: Architecture
document_type: Design Document
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - plugins/gitlab-schedule-control/README.md
  - plugins/gitlab-schedule-control/DIAGNOSIS.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - skills/custom-mcp-connector/SKILL.md
related_documents:
  - plugins/README.md
  - research/testing-assurance-pilot/scheduler-clock/EVIDENCE-CLASSIFICATION.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
consumed_by:
  - future bounded implementation packet
  - ChatGPT-to-GitLab integration assurance and acceptance
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-03
---

# Capability contract, options, and MCP rationale

`document_scope`: preimplementation selection artifact for AI builder/reviewer. No architecture selected; no token issued; no remote service or schedule changed. Avoid promoting an unproven mechanism to a guarantee.

## R-001 Required capability, independent of implementation

`user_goal`: an authorized agent operating from an **ordinary ChatGPT conversation** manages both one-off GitLab pipeline executions and persistent GitLab *schedule objects*. A routine GitLab dashboard session must not be part of task execution.

`operator_boundary`: agent performs technical steps (API, CI config, browser, SSH, log review); human approves consequential choices and performs only irreducible identity/consent once. Never request that the human paste secrets into the conversation.

`minimum tool behavior`:
1. Discover and list schedule objects for a specified project, including pagination and active/inactive status.
2. Get one schedule's ID, description, cron expression, timezone, target ref, owner, created/updated times, `active` and `next_run_at`; distinguish null/absent fields from failed observation.
3. Create schedule with explicit project/ref/cron/timezone/description and an explicit `active` choice; re-read the stored object.
4. Update schedule or toggle active state without silent collateral field changes; re-read and compare.
5. Stop/remove a schedule only after distinct explicit destructive authorization; verify durable state and capture baseline for recovery.
6. Optionally `play` a schedule or create a one-off pipeline; **label these differently** from a real scheduled trigger and preserve `source`.
7. Inspect resulting pipeline and job IDs, `source`, `created_at`, `started_at`, `finished_at`, status, SHA, branch, queue duration and artifact metadata when available.
8. Work from ChatGPT without an assumed Work-mode switch; if the plugin or transport works only in another product surface, treat ChatGPT acceptance as **FAIL** until proven.

`must_not`: create duplicate schedules by retry; infer activation from a `POST 201` alone; equate pipeline creation to job success; claim missing events on unverified slots; log tokens; grant arbitrary GitLab API proxy or shell authority; create schedule ownership changes without authorization.

`scope_seed`: GitLab project `88367140` (private) and research branch `refs/heads/research/scheduler-clock-gitlab-2026-11-02`; intended schedules `ases-clock-gitlab-A-17m-3h` (`17 */3 * * *` UTC) and `ases-clock-gitlab-B-47m-3h` (`47 */3 * * *` UTC). These are test fixtures, not a global GitLab management allowlist.

## R-002 Why an MCP might be needed

**MCP = Model Context Protocol**: a tool exposure/transport boundary through which an AI client discovers named, schema-constrained operations on an external system. A GitLab MCP server adapts ChatGPT tool calls to authenticated GitLab REST API calls and returns bounded typed results. It does *not* replace GitLab's scheduler; it provides the missing agent-accessible management interface.

`current_path`:
`ChatGPT -> connected GitLab integration -> exposed project/pipeline tools -> GitLab API`
: actual `create_pipeline` works for an immediate run; schedule-object operations absent from available tool inventory.

`proposed_MCP_path`:
`ChatGPT -> authorized plugin/MCP tool -> authenticated narrowly scoped server -> GitLab pipeline schedules REST API -> authoritative readback`.

The MCP is justified **if** the installed connection cannot be extended and a direct chat-callable management surface is required. It is not justified merely because "MCP" is fashionable, because GitLab already has REST endpoints, or because a website menu is inconvenient. Assess the actual connection and token custody. Successful standalone CLI calls do not prove that ChatGPT sees or can call the tools. A new MCP server introduces a new attack surface, deployment, transport and auth to maintain.

Potential MCP tool catalog (names illustrative, **not** claims about installed tools):
- `gitlab_schedule_list({project_id,scope?,page?,per_page?})`
- `gitlab_schedule_get({project_id,schedule_id})`
- `gitlab_schedule_create({project_id,description,ref,cron,cron_timezone,active})`
- `gitlab_schedule_update({project_id,schedule_id,expected_current?,patch})`
- `gitlab_schedule_set_active({project_id,schedule_id,active})`
- `gitlab_schedule_delete({project_id,schedule_id,confirmation})`
- `gitlab_schedule_play({project_id,schedule_id})`

Each tool must validate/normalize provider data at runtime, preserve raw error class and GitLab resource ID, use concrete bounded endpoints rather than arbitrary URL fetch, and record readback status separate from mutation acknowledgment. Do not expose schedule variables/secrets in generalized list responses.

## R-003 API surface confirmed by current GitLab docs

Base: `https://gitlab.com/api/v4`. API paths are relative to base:

| Action | Method and route | Consequence |
| --- | --- | --- |
| list schedules | `GET /projects/:id/pipeline_schedules` | read-only, paginated |
| get schedule | `GET /projects/:id/pipeline_schedules/:schedule_id` | read-only |
| list schedule-triggered pipelines | `GET /projects/:id/pipeline_schedules/:schedule_id/pipelines` | read-only, per schedule |
| create schedule | `POST /projects/:id/pipeline_schedules` | mutation, duplicate risk |
| update/pause/resume | `PUT /projects/:id/pipeline_schedules/:schedule_id` | mutation/rescheduling |
| delete schedule | `DELETE /projects/:id/pipeline_schedules/:schedule_id` | destructive |
| play schedule now | `POST /projects/:id/pipeline_schedules/:schedule_id/play` | creates run now; does not move next scheduled time |

Provider docs: [pipeline schedules API](https://docs.gitlab.com/api/pipeline_schedules/) and [job-token restrictions](https://docs.gitlab.com/ci/jobs/ci_job_token/). GitLab `CI_JOB_TOKEN` does **not** generally grant pipeline-schedule API operations. A pipeline bridge would require another authorized credential; even when the job inherits an Owner's role, endpoint allowlists apply.

GitLab API values, including short-vs-full `ref` support, pagination, timezone format, rate limits, owner eligibility, token type and minimum frequency, must be rechecked against the actually deployed provider version before implementation. The current account being Owner-equivalent for the project **does not yet prove** the connected credential has schedule endpoint scopes.

## R-004 Candidate realizations; not yet an architecture decision

| Candidate | What it eliminates | Added trust/operating boundary | Current decision |
| --- | --- | --- | --- |
| A. Existing installed GitLab integration gains schedule tools | New server and credential | Requires upstream connector/tool exposure; not presently in our control | **PREFERRED IF EXPOSED**, not currently available |
| B. Reuse an existing independently verifiable GitLab MCP with schedule support | New implementation code | Package audit, hosting/client connection, OAuth/token custody, tool allowlist, upstream lifecycle | **EVALUATE FIRST** via read-only canary |
| C. Bounded private MCP extension with only schedule-object endpoints | Broad unrelated GitLab tools | One small authenticated endpoint/service and associated credential/secret rotation | **CANDIDATE** if existing solution fails trust/feature gates |
| D. Protected management CI pipeline bridge, invoked through current `create_pipeline` | New MCP transport and ChatGPT plugin | API-capable secret in CI, script/branch protection, job execution cost and lag, GitLab pipeline as control plane for its own scheduler | **TACTICAL FALLBACK**, not automatically preferred for recurring operations |
| E. Routine GitLab dashboard navigation | No integration development | Repeated operator labor, wrong acceptance surface | **EXCLUDED** for normal use; permitted only as one-time diagnosis |

`B candidate to assess`: [jmrplens/gitlab-mcp-server](https://github.com/jmrplens/gitlab-mcp-server), independent MIT-licensed Go implementation, **not GitLab's official MCP server**. Its [published tool reference](https://jmrplens.github.io/gitlab-mcp-server/reference/tools/pipeline/) includes schedule list/get/create/update actions, and its repository advertises read-only/safe modes and HTTP/OAuth transport. **Documentation claim only**: no binaries, packages, credentials, endpoints, code, tool discovery or ChatGPT integration have been vetted in this ASES investigation. Do not send private GitLab tokens to a hosted demo. Audit source, scope, dependency supply chain, deployment and disclosure surface before deciding reuse.

The [official GitLab MCP server](https://docs.gitlab.com/user/model_context_protocol/mcp_server/) and [tool inventory](https://docs.gitlab.com/user/model_context_protocol/mcp_server_tools/) are a distinct possible route, not interchangeable with the connected ChatGPT GitLab integration or third-party servers. Do not infer schedule support from a generic `ci` toolset label; verify tool names/schemas on the current connection.

`D bridge authority model`: privileged protected CI job with a narrow schedule action parser and allowlisted project/refs, executing native REST calls; ChatGPT's current `create_pipeline` triggers the job with an allowlisted operation, then readback/CI artifacts report outcome. Minimum safeguards: protected default branch or equivalent immutable reviewed code, protected and masked scoped secret stored in GitLab settings (never in chat or repo), no untrusted MR execution of privileged job, strict action validation, nonce/idempotency and duplicate detection, no arbitrary shell/script/URL inputs, redacted audit, caps/timeouts, no broad token echo in traces. A pipeline may fail before calling the API; distinguish request never sent from API rejected and from schedule persisted. This bridge does not bypass API credential requirements or guarantee scheduling reliability. If CI itself is impaired, a pipeline bridge may make diagnosis harder.

`C custom MCP authority model`: use approved transport and real ChatGPT OAuth/tunnel capabilities, not a guessed one. Server-side GitLab token/oauth credential is isolated, projects and methods allowlisted, all write calls require explicit intent and effective ChatGPT permission gate, destructive tools separately gated, output bounded/redacted, request IDs logged safely, revocation and rollback possible. The user’s existing GitLab plugin OAuth session is **not automatically available** to a second MCP and cannot be exported or assumed reusable.

## R-005 Security, evidence and cost gates

Hard requirements; failing any one excludes the candidate even if it seems convenient.

- `SEC-01` Secret never appears in ChatGPT message, response, URL, source repository, tool error, CI log, artifact or trace. At rest it is held by an approved secret manager; rotation and revocation are tested. Do not silently broaden GitLab group ownership/token scope.
- `SEC-02` Project/resource authorization enforced at the provider boundary and, where possible, again by adapter allowlist. A caller cannot redirect a privileged GitLab token to arbitrary projects or hosts.
- `SEC-03` Distinguish permission denied `403`, unauthenticated `401`, absent schedule `404`, conflict/duplicate, invalid ref/cron, rate limit `429`, transport timeout, and uncertain persistence after timeout. No automatic unbounded retries or duplicate creation.
- `SEC-04` Writes must be attributable to a user-approved objective and logged with redacted request identity; pause/delete and ownership changes have distinct confirmation controls. Do not confuse an LLM suggestion with action approval.
- `EVD-01` Readback records schedule ID, source project, description, normalized full `ref`, `cron`, `cron_timezone`, `active`, owner, `created_at`, `updated_at`, `next_run_at`, provider response/observer quality and UTC source-query window. A null `next_run_at` on an inactive schedule is not automatically an error.
- `EVD-02` Native scheduled pipeline evidence retains `source=schedule` and provider IDs; `play` or `api` source is never counted as equivalent without provider evidence. The exact originating cron slot remains unresolved unless provider gives authoritative linkage.
- `EVD-03` API acknowledgment, durable schedule GET, next eligible cron window, created pipeline, started job and job success are independently classified. Persist bounded append-only evidence, hash important artifacts and disclose archive gaps.
- `OPS-01` Prefer no always-on VPS; assess free-tier cost, cold-start reliability, HTTP transport compatibility, secret management, and independent diagnostic reachability. A CI bridge should not consume substantial capacity for trivial schedule reads.
- `OPS-02` Any maintained plugin must follow [ASES realization/language selection](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md). Strict TypeScript or Go are bounded eligible options; do not select language from habit or claim the implementation is secure merely because it compiles.

## R-006 Test matrix: cheapest discriminating tests before deployment

| ID | Test | Falsifies / decision changed |
| --- | --- | --- |
| T0 | Inspect current tool discovery and upstream tool inventory | Determines whether A can be enabled without new service |
| T1 | Authoritative read-only list schedules for project `88367140` via permitted authenticated path | Distinguishes empty provider state from broken connector and auth |
| T2 | With no credentials committed or shared, inspect candidate MCP source/manifest and tool discoverability in an isolated test client | Excludes unsupported MCP tooling or broad unsafe exposure |
| T3 | Connect to ChatGPT and invoke an authenticated **read-only** schedule-list canary; correlate backend request | Proves client/registration/transport/auth/discovery/execution boundary |
| T4 | Under separately authorized disposable research project/branch, create exactly one inactive fixture, GET it, update it, pause/resume if appropriate, then delete and verify | Proves write semantics and persistence; no changes to the two target schedules without separate decision |
| T5 | Duplicate create request and response-loss/time-out injection with idempotency rule | Proves safe retries, no accidentally duplicated schedule |
| T6 | Invalid cron, ambiguous/nonexistent ref, missing project, wrong identity, no scope, and forbidden project | Proves errors/allowlists are distinct and fail closed |
| T7 | Once schedules explicitly activated, observe at least one verified eligible UTC slot and pipeline/job history | Tests real scheduler behavior, not only API CRUD |
| T8 | Revoke/rotate the integration credential, confirm requests fail, restore via authorized flow; inspect logs for leakage | Proves revocation and secret isolation |

A prototype passing T1/T2 but failing T3 does **not** satisfy the user’s in-chat requirement. T4 may be postponed until a safer fixture exists and mutation is approved. These are candidate acceptance tests, not claims they have already run.

## R-007 Decision procedure and pending choices

1. Preserve this document as **proposal**, do not set a canonical architecture yet.
2. Resolve T1 and the schedule-existence hypothesis before proposing a repair to GitLab Cron.
3. Compare A/B/C/D by observed user-client usability, privilege footprint, exposure of secrets, number of additional services, auditability, reversible state, cost and maintenance. Exclude any candidate that violates hard security/authority gates.
4. Prefer the smallest **verified** route: reuse provider capability if truly exposed; otherwise evaluate a vetted schedule-capable MCP; use custom narrow MCP or secured CI bridge only when their costs and risks are supported by tests.
5. When implementing, place canonical runtime integration and connector-record artifacts in [rss-tools/mcp](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp), preserving the ASES dossier as a reasoning and requirements source. Do not migrate historical old OpenCode/Claude plugin artifacts into an active tools repository.
6. Release only after real ChatGPT invocation and provider readback. Do not claim that installing or registering an MCP is functional acceptance.

## R-008 Status & certainty contract

`WHY`: prevent recurring manual GitLab console administration while making ASES scheduler experiments observable and eventually manageable.

`WHAT`: GitLab API and current connector capabilities; user-specified operational requirement; ASES empirical tests, repository policies and evidence classification.

`HOW CERTAIN`: required user outcome and missing current ChatGPT tool = confirmed; GitLab native REST API supports schedules = provider documentation; CI job-token schedule limitations = documented; best integration route = **UNDECIDED**; third-party MCP usability in ChatGPT = untested.

`WHAT-NOT-TESTED`: actual provider schedule GET for this identity, activation of two intended schedules, upstream GitLab connector extensibility, third-party MCP code security, plugin registration, GitLab OAuth scope mapping, any write/pause/delete path or token rotation. No current artifact here proves a working MCP or management bridge.

`authority`: this is a task-specific design proposal, not global ASES policy, deployment authority, or authorization to mutate GitLab schedules/credentials.
