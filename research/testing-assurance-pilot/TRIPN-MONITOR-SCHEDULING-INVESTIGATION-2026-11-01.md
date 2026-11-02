---
title: Trip'n Production Monitor Scheduling — Read-Only Root-Cause Assessment
program: ASES / EDASES
layer: Research
document_type: Investigation and Corrective-Action Recommendation
status: Read-only investigation complete; provider-internal cause and owner billing unverified
authority: Evidence-bound; no production change authorized
date: 2026-11-01
source_repository: TripN-Chill-Zone/tripn-astro (private)
source_branch: master
source_workflow: .github/workflows/production-invariant-check.yml
source_archive: private GitLab rock-solid-sites-group/rock-solid-sites-project
---

# Trip'n production monitor — scheduling investigation (2026-11-01)

## Decision

**The observed production monitor does not provide its intended 30-minute detection cadence.** Evidence strongly localizes the missing effective coverage to GitHub scheduled-event delivery/creation, not the detector, runner queue, workflow-level concurrency, or a historical cron edit. GitHub's exact internal mechanism (late creation, dropped schedule events, coalescing, throttling or another provider-side condition) remains **UNVERIFIED**. The repository owner's billing/budget information and workflow administration/audit records were not accessible with the GitHub connection. Do not represent those unknowns as disproved.

**Recommend a staged external-scheduler pilot**, using a Cloudflare Workers Cron Trigger to dispatch the existing, unmodified GitHub workflow, with durable slot/run reconciliation and a missing-heartbeat alert. Run the pilot against a harmless research-only workflow first, then compare delivery/latency and owner entitlement before production approval. Do not change production monitoring settings or simulate failures in the live workflow during this investigation.

## Evidence provenance and boundaries

- Primary workflow: https://github.com/TripN-Chill-Zone/tripn-astro/blob/master/.github/workflows/production-invariant-check.yml ; blob 7a7550bf2d3824381595c3ace5e37b2c73325b73.
- Detector: https://github.com/TripN-Chill-Zone/tripn-astro/blob/master/scripts/check-production-invariants.mjs ; blob a61b8b8df74863bbd87914cda1f5d63d0642e7cc. It uses Node node:https, independently bootstrapped DNS-over-HTTPS, TLS/SNI with resolved-IP requests, HTTP header/body checks, and exact content comparison. A direct port to Cloudflare Workers would need validation; the Node implementation is not a simple edge-fetch equivalent.
- Original workflow file commit 2026-09-24T15:16:53Z: https://github.com/TripN-Chill-Zone/tripn-astro/commit/d37a9fd3d9b56ff1d93410597cf3b6b7599f540c . File-specific history returned only its creation; all five distinct archived production head SHAs returned the identical workflow blob, with cron 7,37 * * * *.
- Private immutable-by-reference historical snapshot: https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/tree/main/evidence/tripn-production-invariant/2026-11-01 ; files run-history.json and manifest.json, plus nine selected raw job logs. The snapshot has 196 run metadata entries and is not a claim that all 196 logs were archived.
- ASES baseline preregistered plan and P2 results: research/testing-assurance-pilot/P2-PREREGISTERED-PLAN-2026-11-01.md and P2-RESULTS-2026-11-01.md at research/rust-haskell-admission-2026-11-01.
- Source endpoints consulted read-only through the connected GitHub and GitLab connectors; official GitHub and Cloudflare docs linked below. No workflow dispatch, issue write, DNS mutation, booking/payment action, or deployment performed.

## Discriminating tests (observation separated from inference)

| Cheapest test | Observation | Implication |
| --- | --- | --- |
| Repo default branch / live YAML | Private repo, default master; cron 7,37 * * * *; no job-level schedule filters; concurrency group production-invariant-check with cancel-in-progress false | Current cron expression and obvious cancellation directive are not the cause |
| Historical YAML and file commit history | No workflow-file changes after its Sep 24 creation; same blob on all five archived scheduled head SHAs | Historical cron edits do not explain the gaps |
| Archived run completeness | 196 unique IDs = 194 schedule + 2 dispatch; outcomes 189 success and 7 failure; first GitHub run_number=1, last run_number=196 | Strong evidence that 196 is complete recorded workflow history, not a paginated/partial list. No cancelled or queued conclusions in archived history |
| Sample queue vs run durations | Six jobs across Sep/Oct: created to started 2–4 seconds; execution 19–24 seconds; including after the longest observed gap | Runner-capacity waiting cannot explain multi-hour inter-run gaps in these samples |
| Other workflow groups | Other four current YAMLs have no competing concurrency group (deployment uses production-deploy); monitor is unique | Intra-repo concurrency collision unlikely |
| Independent scheduled-workflow control | Beds24 Token Keepalive cron 17 4 * * 1; same YAML blob c6a9814cd2fb00267b3c284fecf4a3989a3de20a at sampled Aug–Oct refs, single creation commit 2026-07-31. All 13 weekly runs 2026-08-03 through Oct 26 occurred **43 minutes to 7h49m after** the 04:17 UTC weekly tick; median about 5h42m. | Scheduling anomalies also affect a distinct low-frequency workflow, prior to monitor creation, arguing against monitor-specific implementation or frequency as the sole cause |
| Account and billing | Repo owner is TripN-Chill-Zone (GitHub User); linked rock-solid-sites principal has push but no admin. GitHub connector's permitted endpoints did not provide owner billing, workflow enablement metadata, or audit log | Plan, shared compute balance, stop-usage budgets, and historical manual enable/disable actions remain unknown |

**Paired provider control:** Keepalive recent instances: Oct 5 expected 04:17Z, created 11:35Z (+7h18m), https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/37303863486 ; Oct 12 12:06Z (+7h49m), https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/38246936196 ; Oct 19 09:59Z (+5h42m), https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/39234133492 ; Oct 26 10:13Z (+5h56m), https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/40305695314 . The complete repository schedule-event collection reported 207 runs: 194 monitor and 13 keepalive. Keepalive had run numbers 1–13 without weekly omissions. This independently favors *late event creation* for low-frequency scheduled work, but does not show whether high-frequency events are dropped, coalesced or delayed beyond observation.

**Sample monitor jobs:** Sep 24 run https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/36048451353 (3s queue, 23s execution); Oct 1 https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/36883867103 (4s, 22s); Oct 5 https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/37336621613 (2s, 22s); Oct 12 https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/38294351947 (2s, 19s); Oct 20 https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/39492369244 (2s, 24s); Nov 1 https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/41348658367 (2s, 20s).

## Measured observation coverage, NOT service uptime

Window: 194 recorded scheduled executions from 2026-09-24T19:29:04Z through 2026-11-01T20:47:31Z, 913.3075h; approximately 1,827 half-hour cron slots within this window. Recorded-run density is 194/1827 = **10.6%** of nominal slots. This is a *run-count ratio*, not a direct percentage of on-time cron deliveries (no scheduled-tick timestamp is emitted).

There are 193 measured inter-run intervals: minimum 2.1144h, median 4.8394h, 95th percentile 7.1216h, maximum 9.8803h; 41 are greater than six hours, three greater than eight, and zero shorter than two hours. October had 157 scheduled monitor executions (~5.06/day), compared with 48 scheduled opportunities per day. Persistent failures could remain undetected for nearly 9.88h under the worst observed gap, even if every available check correctly detects them. Short failures within gaps can be missed completely. **No finite future detection maximum is established.**

**Conditional empirical exposure model, not measured uptime or a service SLA:** Take a uniform random onset time within the observed inter-run intervals; assume a persistent fault that every actual check would correctly detect at execution. Then the interval-weighted mean time until the next sample is Σ(gap²)/(2Σgap) = **2.61 hours**; probability of a check within 30m is Σ min(gap,0.5h)/Σgap = **10.57%**; within 1h **21.13%**, within 2h **42.26%**. These results are conditional, retrospective timing estimates, not incident probabilities or independent reliability claims. Failures due to comparison-hostname DNS do not establish apex outages; raw log classifications are in P2.

## Hypotheses and rejected/remaining uncertainty

- **Rejected as explanation:** malformed cron; wrong default branch; workflow file changed during observation window; monitor-only test logic aborting *before run creation*; cancel-in-progress in monitor; >2h runner queue (six sampled jobs; 196 complete-run history); missing hundreds of runs due to archival pagination (workflow run numbers 1 through 196 and 196 distinct entries).
- **Strongly disfavored, not logically eliminated:** manual workflow disable/enable repeated throughout 39 days; periodic concurrency suppression by other current workflows; sustained billing hard-stop across whole month. Continued successful runs on every October date and second delayed weekly workflow weigh against these as principal explanations.
- **Provider-side scheduled-event non-delivery/delay: probable failure boundary, not precise provider mechanism.** GitHub docs acknowledge high-load delay/drop and default-branch restrictions. Only provider-side event logs/support could distinguish scheduling drops vs throttling/coalescing vs precreation backlog.
- **Not checked/unknown:** private repository owner's actual paid/free plan, included shared compute remaining, hard budgets, restrictions, organization/enterprise-level policies, historical workflow enabled state and audit log, any provider internal scheduler diagnostics. The current read-only connector denies administrative workflow and billing endpoints.
- **No conclusion about the seven failure runs as site uptime:** five comparison-hostname DNS issues, one isolated timeout, one deliberate manual synthetic test, per existing P2 evidence.

## Cost and smallest justified correction

GitHub current official billing: GitHub Free provides **$12/month shared included compute** (not guaranteed as 2,000 minutes if other eligible products consume it); standard ubuntu-latest Linux x64 at **$0.006 per rounded-up job-minute**. Repository OWNER pays for private runs. The short sampled monitor jobs would usually bill one minute each: Oct 157 runs ~157min / $0.94 usage-equivalent; if 30-day 48/day cadence actually ran, ~1,440min / **$8.64** usage-equivalent, consuming 72% of an otherwise unused Free included $12 compute allowance. This calculation is not an account-level billing statement; other jobs and compute products are unmeasured. Official references:
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/billing/reference/actions-runner-pricing
- https://docs.github.com/en/billing/reference/product-usage-included
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

**Candidate A — very small but NOT reliable correction:** adjust minute offsets, re-save cron or reduce schedule frequency. Low implementation cost, but likely fails the detection objective: 7/37 already avoids exact top-of-hour, and the weekly 04:17 control is repeatedly delayed. Do not adopt as a cure without comparative observations.

**Candidate B — preferred near-term minimal functional correction, subject to acceptance:** one Cloudflare Worker Cron Trigger every 30m to call GitHub workflow_dispatch of the current workflow WITHOUT simulate_failure, using a narrowly scoped secret with Actions write for this repo. Maintain a durable per-slot record with expected UTC time, Worker scheduledTime, actual dispatch time, API result, corresponding GitHub run ID, start time and outcome; include retries, duplicate protection and a separate stale-heartbeat alert. Initially use a *separate research-only non-alerting workflow* to test delivery and a one-week parallel observation window, without changing production monitoring. This preserves the current Node DNS/HTTPS/SNI checks and issue alert path, and avoids the GitHub native cron creation path; it does **not** remove GitHub runner/billing or GitHub API availability as dependencies. An extra 1,440 Cron events in 30 days is ~48/day and negligible relative to Cloudflare Workers Free's 100,000 requests/day, assuming Worker CPU <=10ms and normal subrequest quotas. Monitor actual CPU/elapsed latency before claiming capacity.

The connected Rock Solid Sites Cloudflare account, inspected read-only 2026-11-01, listed five Worker scripts and **zero Cron Triggers** across them; documentation permits five Cron Triggers/account on Workers Free. This demonstrates *available capacity in that connected account*, not that Trip'n currently belongs to it or that deployed cross-account monitoring is already operational. Source: https://developers.cloudflare.com/workers/platform/limits/ and https://developers.cloudflare.com/workers/configuration/cron-triggers/ .

**Candidate C — preferred long-term architecture if GitHub budget or scheduling remains a blocker:** move simple low-cost externally observable checks to a Cloudflare scheduled Worker and record each result to D1 or similar durable free storage, keeping existing GitHub Node detector as independent less-frequent cross-provider assurance. D1 Free lists 100k rows written/day and 5GB total stored; 48 sample records/day is negligible, but use bounded retention and export manifests, not cloud logs alone. A Worker-only port has important fidelity constraints: Node's raw resolved-IP HTTPS, SNI pinning and observable DNS independence cannot be treated as equivalent to Worker fetch without discriminating tests. A Cloudflare-hosted primary monitor shares provider failure modes with Cloudflare-hosted production, so retain an independent vantage for outage classification. Sources:
- https://developers.cloudflare.com/d1/platform/pricing/
- https://developers.cloudflare.com/workers/configuration/cron-triggers/

**Acceptance gate:** A research-only external dispatch must produce an auditable, persistent 30m cadence record, with missing-slot detection independent of the GitHub run it checks. Reconcile all intended vs actual slots for >=7 days; measure p50/p95/max dispatch, run-created, job-start, outcome delays; verify tokens, billing headroom and independent alert transport. Only then approve production trigger changes. Leave the native schedule in place as a fallback until the new path is proven, accounting for duplicates, issue side effects and extra billable runs. No production changes authorized by this report.

## Remaining provider/account actions

1. **Owner-only billing check (read-only):** TripN-Chill-Zone Settings > Billing & Licensing; verify plan, shared compute usage, spend budgets that stop usage, and per-workflow/other-repo consumption. The linked rock-solid-sites collaborator account is not a substitute for repo-owner billing.
2. **Owner/admin workflow state:** read GitHub workflow state metadata, repository Actions policies, and audit events for manual disable/re-enable; no assumption of uninterrupted enabled state without this evidence.
3. **Provider support request:** private issue with sample expected/actual timestamps, both schedule expressions, run IDs, creation SHA/blob, run-number continuity, queue durations, and confirmation that two unrelated workflows are affected. Ask whether nominal schedule events were dropped, delayed before creation, suppressed or coalesced, and why.
4. **External scheduler synthetic acceptance test** as described. No production dispatch or alert-writing test was performed here.

## ASES assurance status

Source-first, smallest discriminating tests, independent sibling-workflow control and separation of hypotheses from observations were applied. Existing P2 historical evidence is retained in private GitLab; this public ASES report stores aggregate findings and references, **not** sensitive job traces. Independent provider-internal root-cause confirmation, owner billing and longitudinal corrective validation remain **NOT DONE**.

---

## Follow-up 2026-11-02 — repository-owner GitHub access and third-workflow control

**Provenance:** User connected `TripN-Chill-Zone` GitHub account to GitHub MCP on 2026-11-02. Investigated read-only via that account and the Actions GET/list functions. No simulated failure, dispatch, production, or monitoring mutations.

### New owner-authorized observations

- Account identity **verified**: `TripN-Chill-Zone` (GitHub user ID 272279656); the repository is private, the account reports `admin: true` for `TripN-Chill-Zone/tripn-astro`.
- Direct workflow read **verified**: production-invariant workflow ID `366183226`, `state: active`, created and `updated_at` both 2026-09-24T15:20:01Z; sibling keepalive ID `324843349`, `state: active`, created and last updated 2026-08-01T00:32:15Z. The equal timestamps strengthen, but do not conclusively prove, uninterrupted enabled state; no historical audit log was available.
- The six *current* workflows in `tripn-astro` are active. The GitHub Actions API separately returns `disabled_inactivity` for a scheduled workflow in another repository; this distinguishes inactivity disablement from the current private monitor's active state.
- The linked owner account exposes three repositories, of which only `tripn-astro` is private. Read-only enumeration of this private repo's Actions history returned **316 total workflow runs** across June–November 1, 2026, of which **165 total in October** (157 monitor, four Beds24, two CI, two deployments); source names should be calculated from actual enumeration, not an assumed billing balance. Observed earlier `Pink Bubble` workflow had 43 `startup_failure` conclusions from June–August, *not* contemporaneous with the monitor's September–November intervals. Current recorded monitor executions remain 196, including 194 scheduled and two manual.
- Cross-check: `157 + 4 + 2 + 2 = 165` October workflow executions. Across the period the other public repos have independent runs but they are not billed as private-repository standard GitHub-hosted usage. The observed low number and short 19–24s monitor jobs make an exhausted 2,000-minute equivalent allowance *unlikely* to explain scheduling; owner billing usage and budgets remain **not verifiable** via available tools.
- Historical run usage GET returned `billable.UBUNTU.total_ms = 0` despite nonzero 23s/28s wall time on sampled private runs. **DO NOT interpret this as proof of zero billed usage**: GitHub deprecated/is closing the old workflow run usage endpoint; its result is not a trustworthy billing-account statement. Official notice: https://github.blog/changelog/2025-02-02-actions-get-workflow-usage-and-get-workflow-run-usage-endpoints-closing-down/ and https://github.blog/changelog/2025-09-26-product-specific-billing-apis-are-closing-down/ .
- `GitHub__fetch` with the *owner link* still rejects the administrative `/actions/workflows/{id}`, `/actions/permissions`, and `/actions/billing/usage` URLs at the connector's allowlist layer (HTTP 400), not because owner lacks repo administration. The separate GitHub Actions GET tool did return workflow `state` successfully. Owner **billing** and policy restrictions still require the official Billing & Licensing UI or a permitted consolidated billing connector/API; do not use deprecated usage values.

### Third independent scheduling control: different repository, near-perfect correlated delays

**New evidence materially strengthens the shared upstream scheduling hypothesis.**

In public `TripN-Chill-Zone/tripn-instagram-feed`, workflow `.github/workflows/refresh-instagram-tokens.yml`, ID `318641780`, is configured for Mondays at `0 4 * * 1` (04:00 UTC). In separate **private** `TripN-Chill-Zone/tripn-astro`, workflow `.github/workflows/keepalive.yml`, ID `324843349`, uses `17 4 * * 1` (04:17 UTC). Ten dates have schedule-created runs in both, with the following observed event times and UTC delays:

| Monday UTC | Instagram actual | Instagram lateness vs 04:00 | Beds24 actual | Beds24 lateness vs 04:17 |
| --- | --- | ---: | --- | ---: |
| Aug 03 | 07:23:49 | 3.397h | 07:50:32 | 3.559h |
| Aug 10 | 05:25:05 | 1.418h | 05:47:09 | 1.503h |
| Aug 17 | 04:40:33 | 0.676h | 05:00:38 | 0.727h |
| Aug 24 | 04:42:27 | 0.708h | 05:04:22 | 0.789h |
| Aug 31 | 10:34:49 | 6.580h | 10:55:02 | 6.634h |
| Sep 07 | 08:56:31 | 4.942h | 09:25:10 | 5.136h |
| Sep 14 | 09:35:20 | 5.589h | 09:56:14 | 5.654h |
| Sep 21 | 09:37:19 | 5.622h | 09:59:59 | 5.716h |
| Sep 28 | 10:36:33 | 6.609h | 10:59:15 | 6.704h |
| Oct 05 | 11:11:31 | 7.192h | 11:35:00 | 7.300h |

Pearson correlation of their ten per-date lateness values is **0.9998387**; actual creation timestamps differ by an average of **22.94 minutes** against the original 17-minute scheduled offset. The delays move together from week to week. There is therefore strong **cross-repository** evidence of a common scheduling effect. However, both repositories have the same owner and scheduled-actor `rock-solid-sites`, so this observation **cannot distinguish GitHub-platform-wide delay from shared account/actor-specific effects**. The timing alone does not reveal GitHub's internal event queue, coalescing, suppressions, or billing logic.

Primary references: [Instagram workflow](https://github.com/TripN-Chill-Zone/tripn-instagram-feed/blob/main/.github/workflows/refresh-instagram-tokens.yml), [Oct 5 Instagram workflow history](https://github.com/TripN-Chill-Zone/tripn-instagram-feed/actions/workflows/refresh-instagram-tokens.yml), [Oct 5 Beds24 run](https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/37303863486). Run timestamps above were retrieved from the two authenticated Actions workflow run lists.

**Separate operation risk:** Instagram refresh workflow state is `disabled_inactivity` with `updated_at=2026-10-05T11:11:31Z`. The last repository commit checked was 2026-08-06T01:27:48Z. GitHub docs confirm public scheduled workflows can auto-disable after 60 days without repository activity: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows . That disabled state concerns the Instagram token-refresh schedule, not the private production monitor, but merits its own operational review before refresh tokens expire. **Do not re-enable here without separate scope/approval.**

### Updated root-cause confidence and remaining tests

- **CONFIRMED:** the monitored workflow is currently active under the owner's account; its creation/update metadata has not changed; the private repository's October execution count is low; the published schedule remains twice-hourly, while actual run creation averages multi-hour intervals.
- **STRONGER SUPPORT THAN BEFORE:** common GitHub scheduled-event delivery/creation (or common account/actor scheduling policy) is implicated because *two independently coded weekly workflows in two repositories* show almost exactly matched multi-hour lateness, while the original monitor also misses most nominal slots.
- **EXCLUDED:** the public Instagram workflow's 60-day inactivity disablement as an explanation for the private monitor (it is active and private); the discrepancy is not solely a high-frequency-cron phenomenon.
- **UNVERIFIED:** owner's actual plan, monthly remaining compute, configured budgets/stop-usage and whether GitHub's internal scheduler delayed or dropped each nominal 30-minute event; provider audit/support would be required. The old per-run billable usage API's zero is **not** evidence.
- **RECOMMENDATION UNCHANGED:** test a low-cost external heartbeat/dispatcher on a safe nonproduction workflow, record *every intended slot* and distinguish dispatch success from GitHub run creation and completion before any production change. Current connection does not justify altering production cron.
