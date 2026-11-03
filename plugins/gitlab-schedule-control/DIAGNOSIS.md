---
title: GitLab Pipeline Schedule Connector Gap - Bounded Diagnosis
program: Tooling
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - AGENTS.md
  - research/testing-assurance-pilot/scheduler-clock/EVIDENCE-CLASSIFICATION.md
related_documents:
  - plugins/gitlab-schedule-control/README.md
  - plugins/gitlab-schedule-control/CAPABILITY-AND-OPTIONS.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
consumed_by:
  - GitLab schedule management realization selection and troubleshooting
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-03
---

# GitLab scheduled-pipeline management: discrepancy and evidence

## D-001 Original acceptance surface

`target`: a user requests in an ordinary ChatGPT strategy conversation to list, create, inspect, update, activate/deactivate, optionally manually run, and delete GitLab *pipeline schedule objects*; an agent performs authorized GitLab actions and verifies actual persistence without routine operator dashboard navigation.

`observed_deviation`: the connected GitLab integration supports ordinary project/branch/CI pipeline reads and immediate `create_pipeline` calls but does not advertise schedule-object management tools. Attempting to observe schedules through the available `list_pipelines(source="schedule")` only lists pipelines *already created by the scheduler*. It cannot establish whether schedule definitions exist, are active, point at the right branch, or have a valid `next_run_at`.

`impact`: two nonproduction comparative scheduler research arms cannot establish their eligible observation windows. The absence of native scheduled runs must not be classified as permanently missed events. Longer-term ChatGPT automation of GitLab schedule management is blocked.

`scope`: current connected GitLab app as surfaced in this ChatGPT conversation, project `88367140`, `rock-solid-sites-group/rock-solid-sites-project`. Do not generalize from this observation to every GitLab MCP server, GitLab edition, OAuth client, plugin, or user account.

## D-002 Verified boundaries (observed in connected tool responses, 2026-11-03)

| ID | Boundary/probe | Result | Entitled conclusion |
| --- | --- | --- | --- |
| E01 | Connected GitLab current user | `rocksolidsites`, user ID `43975579`, active | Authentication works for exposed operations |
| E02 | `get_project(88367140)` | Project exists; private; group `access_level=50`; jobs enabled | GitLab project access with Owner-equivalent role in the returned model |
| E03 | `get_branch` | `research/scheduler-clock-gitlab-2026-11-02` exists, unprotected | Target ref exists; no branch-not-found explanation |
| E04 | `get_repository_file_raw(.gitlab-ci.yml, ref=research/...)` | `scheduler_clock` job and `CI_PIPELINE_SOURCE == "schedule"` rule present | CI configuration is capable of selecting a schedule-sourced job |
| E05 | `list_pipelines(source="api")` and `create_pipeline` prior controlled probes | Successful API-sourced pipelines; jobs executed | GitLab pipeline API and runners work for **API-triggered** execution; not a native schedule test |
| E06 | `list_pipelines(source="schedule")` | 0 returned | **NO_SCHEDULED_PIPELINES_VISIBLE_AS_OF_QUERY**; not proof that schedule objects do not exist |
| E07 | Current connector action inventory | 128 GitLab actions inspected; no schedule-list, schedule-create, schedule-update, schedule-delete or schedule-play action; no general raw REST-request action | **CONNECTOR_TOOL_NOT_EXPOSED** in this ChatGPT connection |
| E08 | Official GitLab REST API | Documented `GET/POST /projects/:id/pipeline_schedules` and item GET/PUT/DELETE and play actions | The provider has an API for this feature; this does not imply the current connector exposes it |
| E09 | ASES scheduler `readback-v2` / PR #6 | 25/25 tests passed independently, including GitLab `CONFIGURATION_UNVERIFIED` handling | Classifier behavior qualified; schedule existence still unverified |

`query_precision`: no exact GitLab server-side UTC query timestamp was returned by the connector. Event dates and source-created timestamps must not be presented as source-read timestamps. The frozen [03:40Z experiment snapshot](../../research/testing-assurance-pilot/scheduler-clock/snapshot-2026-11-03T0340Z.json) remains a bounded historical source observation, not fresh authority over current schedule state.

## D-003 Fault boundaries and falsifiable hypotheses

| Hypothesis | Present state | Cheapest distinguishing test and interpretation |
| --- | --- | --- |
| H1. ChatGPT-connected GitLab integration simply lacks schedule-object tools | **SUPPORTED at tool-discovery boundary** | Compare exposed schemas to documented provider API; no attempt to synthesize a missing tool name |
| H2. Schedule-list endpoint itself denies this GitLab identity (401/403) | **NOT TESTED** | Authenticated GET to the *actual endpoint* through an approved direct API route; compare 200 vs 401/403. Owner-looking project metadata is not this test |
| H3. Two intended schedule objects were never created | **OPEN** | Successful schedule-list endpoint returns empty collection, with project ID and pagination confirmed |
| H4. Schedules exist but are inactive, invalid, owner-ineligible, or mis-targeted | **OPEN** | Schedule GET/list yields IDs, `active`, `cron`, `cron_timezone`, `ref`, `owner`, `next_run_at` |
| H5. Scheduler misses eligible events despite active valid schedules | **NOT YET EVALUABLE** | First establish source-confirmed activation and a later eligible window; compare native `source=schedule` runs without equating `created_at` to a unique intended slot |
| H6. GitLab globally cannot create pipelines | **WEAKENED/CONTRADICTED for API-triggered path** | Existing successful API-sourced pipelines, including [3016894193](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/pipelines/3016894193); no inference about schedule path |
| H7. Reconnecting GitLab would surface the missing tool | **UNSUPPORTED SPECULATION** | Require a changed advertised capability/toolset before spending effort on reconnecting or increasing token scope |

`epistemic_warning`: `tool unavailable` != `API rejects request` != `schedule missing` != `schedule eligible but no run visible` != `trigger permanently dropped` != `created run failed`. Do not collapse these entities under `GitLab is broken`.

## D-004 Specific planned comparative research arms

- `project_id`: `88367140`; `ref`: `refs/heads/research/scheduler-clock-gitlab-2026-11-02` (short ref accepted if unambiguous).
- `A`: description `ases-clock-gitlab-A-17m-3h`; cron `17 */3 * * *`; timezone `UTC`.
- `B`: description `ases-clock-gitlab-B-47m-3h`; cron `47 */3 * * *`; timezone `UTC`.
- `verified_schedule_ids`: **NONE**.
- `verified_activation_utc`: **UNKNOWN**.
- `verified_next_run_at`: **UNKNOWN**.
- `native_schedule_pipeline_count_at_last_check`: zero; *not* an established denominator for missed triggers.
- `non-schedule control`: API-triggered pipeline and push-triggered pipeline succeeded on this branch, demonstrating the branch-level CI job is executable. A CI smoke test cannot substitute for the missing scheduling boundary.
- `production_and_external_controls`: Cloudflare-to-GitHub dispatch disabled; Trip'n production monitor must remain untouched.

## D-005 Cheapest next discriminating tests (stop if decision resolved)

1. **Tool capability control (already done):** action inventory + official GitLab API endpoint documentation. Do **not** repeat to justify a reconstruction.
2. **Missing provider state read:** once authorized, inspect `GET https://gitlab.com/api/v4/projects/88367140/pipeline_schedules` via a suitable authenticated API caller. An agent-controlled call is preferred; one-time GitLab UI inspection is an allowed specific diagnostic when a suitable caller is unavailable. Neither path is the permanent operator workflow.
3. Interpret provider response explicitly: `200 []` => no visible schedule objects under this identity and query; `200 [items]` => inspect matching object IDs and fields; `401` => authentication defect; `403` => authority/scoping defect; `404` => distinguish wrong project/route from resource masking; transport/timeout => observer fault, not no-schedules conclusion.
4. If both schedules exist/active, freeze evidence before counting first eligible slots. If absent, a separately authorized, idempotent create + authoritative readback is required. Do not silently create as a troubleshooting side-effect.
5. Once a candidate integration exists, complete a real **ChatGPT-originated** read/list canary (and later authorized write); verify upstream readback and provenance. Shell/API success alone is not end-to-end acceptance.

## D-006 Claim ledger (ASES reasoning discipline)

- **WHY**: cannot reliably administer or evaluate GitLab native schedule arms from the actual user conversation.
- **WHAT**: supported identity/project/branch/pipeline calls; missing schedule-management tools; successful API-sourced controls; zero observed `source=schedule` results; documented GitLab schedule endpoints.
- **HOW CERTAIN**: missing schedule tools in *current connection* = high/direct; schedules absent on GitLab = unknown; provider schedule-delivery failure = not established; role-based authorization for missing endpoint = untested.
- **WHAT-NOT-TESTED**: authenticated schedule REST GET/POST; live UI schedule list; token scopes and OAuth grants for schedule endpoint; native schedule activation; existing third-party MCP connection; real ChatGPT invocation of proposed extension.

## D-007 Sources, provenance and amendment rule

- [ASES experiment contract](../../research/testing-assurance-pilot/scheduler-clock/EVIDENCE-CLASSIFICATION.md)
- [ASES fault-isolation proposal](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md) — explicitly a **proposal**, not global adopted policy.
- [GitLab pipeline-schedules REST reference](https://docs.gitlab.com/api/pipeline_schedules/).
- [Official GitLab MCP tool reference](https://docs.gitlab.com/user/model_context_protocol/mcp_server_tools/).
- [ASES scheduler repair PR #6](https://github.com/rock-solid-sites/ASES/pull/6).

On subsequent observations append date + source + result + changed hypothesis to this record or linked evidence. Do not rewrite historical `NO_RUN_VISIBLE_AS_OF_QUERY` as false merely because a delayed run appeared later.
