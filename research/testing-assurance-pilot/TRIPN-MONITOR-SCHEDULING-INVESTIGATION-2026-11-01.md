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

---

## Follow-up 2026-11-02 — cheapest discriminating tests: upstream scheduler regression

**Result:** Read-only evidence now strongly supports a **broad GitHub Actions `schedule` event-creation/delivery degradation**, with a sharp observed onset **2026-08-27** in an unchanged cross-account control and ongoing effects as late as October 2026. This is a provider-side **failure boundary**; without GitHub's internal scheduler traces, do **not** claim a specific internal root-cause mechanism or that the August 26 incident caused all subsequent missed events.

### Hypotheses preregistered for the follow-up and minimal tests

| Hypothesis | Cheap discriminating test | Evidence-bound verdict |
| --- | --- | --- |
| The issue is confined to TripN's private repo, owner allowance or cron syntax | Historical independent public `rock-solid-sites/100percentaiart` `0 */4 * * *` schedule and unrelated `kort0881` public cron | **REJECTED** as a sole explanation: independent owners, actors, and public repos also show missed slots and severe delays |
| The cross-repository synchronization is caused by common GitHub scheduled actor `rock-solid-sites` | Read-only independent actor `kort0881` with current October schedules and stable YAML | **REJECTED** as sole explanation: `kort0881` workflows exhibit October under-delivery |
| Workflow code/configuration regression caused the change | Compare exact workflow **blob SHA** at commits before/after 2026-08-27, compare daily run counts | **REJECTED** for the `100percentaiart` control: identical `hourly-post.yml` blob `ed86f7ae199c538a014c9436a14e1167a715b191`, cron `0 */4 * * *`, on Aug 25 and Aug 28; head SHA unchanged `e6a281a3ce4faa40b9c6ae8cb2737f521f41a181` through August transition |
| Late runs are runner-queue bottlenecks | Compare GitHub job creation vs start in pre/post control and unrelated actor | **REJECTED in the samples**: Aug 25 Go bot created 20:17:56Z and job started 20:17:59Z (3s); Aug 27 created 18:38:49Z and started 18:38:52Z (3s); Oct 27 unrelated actor created 18:31:21Z, started 18:31:24Z (3s) |
| The problem began on/around a GitHub infrastructure event | Before/after control and official incident report, independent public incident reports | **TEMPORALLY CONSISTENT**, not proven causal: an August 26, 2026 GitHub Actions incident affected run starts / inbound event processing; public community reports describe prolonged cron event-creation failures after Aug 26. Official incident report describes a queued-run/runner assignment failure, which is **not itself** proof of our later precreation scheduler failure |
| New synthetic workflow necessary to distinguish application vs GitHub | Evaluate read-only controls above | **NO:** controls discriminate sufficiently for an operational correction; new production workflow runs risk issue writes and consume capacity, while a harmless fresh workflow cannot expose GitHub internal queue state without longitudinal observation |

### Primary controlled before/after: separate owner, stable source

Workflow: `rock-solid-sites/100percentaiart/.github/workflows/hourly-post.yml`; schedule at historical head: `0 */4 * * *` (6/day), same workflow file blob before and after regression. GitHub Actions recorded **448 scheduled runs** 2026-06-21T21:06:05Z through 2026-09-08T19:08:47Z, enumerated across five pages and independently counted.

- **Pre-period:** Aug 1–25, 25 full UTC days, **149 recorded run creations vs 150 nominal** (99.3% count ratio); 24 days had six run creations and one day five. Consecutive-interval mean ~4.02h, just one >6h, none >8h. `run 385`: https://github.com/rock-solid-sites/100percentaiart/actions/runs/32894531570 at 2026-08-25T20:17:56Z, job queued 3s.
- **Transition:** Aug 26 still **6** recorded run creations, including 2026-08-26T22:36:04Z for the last daily creation. Aug 27 only **2**, created at 05:54:15Z and 18:38:48Z. Aug 28 only **2**, at 03:55:31Z and 15:48:56Z. Gap Aug 27 05:54 to 18:38 was **12.7425h**. `run 393`: https://github.com/rock-solid-sites/100percentaiart/actions/runs/33104515512; job started 3s after creation.
- **Post-period:** Aug 27–Sep 7, 12 full UTC days, **53 recorded run creations vs 72 nominal** (73.6% count ratio); one day had six, 11 had fewer. Consecutive-interval mean ~5.39h, 21 gaps >6h, 7 >8h.
- **Caveat:** The ratios count run **creation dates**, not individual matched intended slots, because GitHub does not expose the original intended tick time and delayed events can cross UTC date boundaries. The abrupt large change and persistent gaps remain regardless of exact slot assignment. This natural before/after sample establishes severity in another repo and another repository owner, not the name of the faulty internal component.

The same Mondays Aug 3, 10, 17, 24, 31 and Sep 7 exhibited broad clusters between Go bot's run creations, Chill Zone's Instagram refresh and Beds24 keepalive; bot is owned by `rock-solid-sites`, but its scheduling actor is also `rock-solid-sites`. It therefore tests a **second owner**, not a second actor.

### Strong independent-actor control in October: `kort0881`

From GitHub public REST run history and historical workflow blobs (not just anecdotal community posts):

- `kort0881/facts-telegram-generator`, `.github/workflows/facts.yml`, `0 5,9,13,17,21 * * *` (nominal 5/day). Same workflow blob SHA `49bbc4576f85d2f50c69ed41b411ede02ad523cd` on Oct 23, Oct 31 and Nov 2 run heads. **29 recorded scheduled run creations** in Oct 23–31 (9 days), against **45 nominal opportunities**. Actor `kort0881`. [2026-10-27 sampled run](https://github.com/kort0881/facts-telegram-generator/actions/runs/40560753284) created 18:31:21Z, job started 18:31:24Z (3s).
- `kort0881/No-code-protection`, `.github/workflows/kibersos.yml`, `0 6,12,15,18 * * *` (4/day). Same workflow blob SHA `9ae2ee0af9ad2540c01e7ac3e779ee29609fe5b5` on Oct 23, Oct 31 and Nov 1 run heads. **25 recorded scheduled run creations** in Oct 23–31, against **36 nominal opportunities**. Actor `kort0881`.
- **Caveat:** Date-window run counts are not exact per-tick matched slot counts when delayed creations cross midnight; there may be timing/cross-boundary error. They nonetheless demonstrate substantial under-delivery by a distinct GitHub actor/owner.

This rejects the narrow account/actor-only hypothesis and supports a cross-GitHub `schedule` problem extending into October. **Do not presume every schedule or every region is affected identically**.

### External corroboration and chronology

- **Official GitHub schedule limitation:** GitHub documents that scheduled events can be delayed and some may be dropped: https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
- **Official August 26 incident RCA:** GitHub reports inbound Actions event volume, shared database saturation, manual throttling and runner assignment impacts, beginning 2026-08-26 at 15:11 UTC. Its RCA concerns runner starts / event-processing pressure, not a confirmed persistent cron-specific scheduler defect: https://github.blog/news-insights/company-news/github-availability-report-august-2026/
- **Independent report Aug 27 onward:** https://github.com/orgs/community/discussions/206019 (public workflows missing events, manual dispatch starts promptly; off-hour cron shifts ineffective).
- **Independent report Sep 9, following Aug 26 onset:** https://github.com/orgs/community/discussions/207346 (private repo, dropped/late run creations despite resets, workflow active).
- **Independent contemporary report Oct 27:** https://github.com/orgs/community/discussions/211421 (4–7h late run creations October 13–27).
- These community posts are *third-party reports*, not GitHub engineering acknowledgement of the exact scheduler root cause. They corroborate independent observations across unrelated accounts.

### Consequences and remaining unknowns

**Root-cause assessment updated:** Very high confidence that TripN's missing coverage is caused predominantly by failed or late `schedule` **event delivery/run creation** on GitHub rather than a TripN monitor defect. The `rock-solid-sites` pre/post abrupt degradation and unrelated `kort0881` October controls strongly support a **broad provider-side regression**. We cannot distinguish event drops, coalescing, scheduler throttling, replay windows, or queue TTLs without provider-internal logs. Nor can we prove the August 26 incident caused a persistent scheduler defect; the evidence establishes a matching onset.

**Next smallest useful action:** Given strong observational discrimination, **stop adding YAML tweaks or synthetic live failures**. Preserve the existing workflow and run history, create a provider support incident with this evidence packet, and prototype a **separate harmless external scheduler and heartbeat**, only then decide whether GitHub native `schedule` should remain a backup. A near-term external Cloudflare Cron → GitHub `workflow_dispatch` path avoids the failure boundary while preserving Node/SNI/DoH detector behavior. Validate the new trigger without production probes or issue writes, with a missing-slot watchdog and measured run completeness. Actual GitHub owner's billing and account-specific budgets still remain **NOT VERIFIED**, though cross-account under-delivery rules them out as a general root cause.

**Evidence integrity:** No GitHub Actions production dispatch, production DNS/HTTPS checks, booking/payment interactions, live issue writes, workflow changes, or Cloudflare resource mutations occurred. All tests were historical read-only API queries and public documentation verification. Keep private TripN logs in original private GitLab evidence location. 

---

## 2026-11-02 operational experiment launched

**User-approved scope:** lower Trip'n production monitor from 30min to 3h; keep 100% AI Art at zero scheduled runs; launch an independent, non-alerting Cloudflare Cron vs GitHub native scheduling control. **No manual production monitor run, no synthetic production failures, no alert-issue mutations.**

### Recorded production and source changes

- **Trip'n live schedule updated and read back:** `TripN-Chill-Zone/tripn-astro`, `master`, `.github/workflows/production-invariant-check.yml`; commit `1ae87b0541d429fe75277e2e06c51bdf9d3841ec`. Original `7,37 * * * *` (48 nominal/day) changed to `7 */3 * * *` (8 nominal/day, 00:07/03:07/...21:07 UTC). Only cron and its explanatory comment changed; detector, issues/alert and recovery logic are unchanged. This is a workload and frequency experiment, **not** a known workaround or latency guarantee. Coverage is intentionally reduced; a persistent failure can take >=3h to be observed under perfect scheduling, and longer if an event is missed.
- **100% AI Art no-op verified:** `rock-solid-sites/100percentaiart`, default `main`, `.github/workflows/hourly-post.yml`, blob `b497f982216778f50ff3bf74dfffad6a7df13688`, declares `workflow_dispatch` only. Zero configured scheduled executions; no production or repo edit needed.
- **Research-only GitHub control activated on public ASES main:** `.github/workflows/ases-schedule-probe.yml`, commit `0fd989ec5c545c6be65d3d3e28c459a35c4a68ab`, workflow ID `404004929`, state `active`. Native cron `13 */3 * * *`, 8 nominal runs/day. One harmless job logs event, run ID and UTC time; `contents: read` only; no fetch of production or GH issue mutation. It has optional `workflow_dispatch` `slot_utc` input for future external comparison.
- **Cloudflare Worker and canonical source deployed:** `rock-solid-sites/ASES` `main` commit `e3a33bf5d8389c63d490f378664a1c579bd69e7d`, folder `research/testing-assurance-pilot/scheduler-clock/` contains `worker.mjs`, `schema.sql`, `wrangler.jsonc`, `README.md`. Worker `ases-schedule-clock-20261102`, Cloudflare account `bdfa7b03c77a00402ac0fa3541b229be`; deployment ID `86f94ed444c0493ea49bd793deb4a7c2`. Cron trigger PUT and GET both verified `9,39 * * * *` (48 clock slots/day). 30min clock is deliberately cheap Worker + D1, distinct from GitHub Actions compute.
- **Cloudflare D1 schema created successfully:** DB `ases-schedule-clock-20261102` id `722b87f3-1570-466b-8565-dd77f650a241`, table `ticks` keyed by `scheduled_ms`; records scheduled/observed timestamps, duplicates, dispatch status. Worker is D1 bound, `DISPATCH_ENABLED=false` by default. HTTP fetch responds 404. No public event ingestion or direct booking/production probe.
- **External `workflow_dispatch` deliberately not live:** GitHub-to-Cloudflare scoped Actions-write token is not available through installed connectors without explicit provision. The Worker requires **both** `DISPATCH_ENABLED=true` and a securely provisioned `GITHUB_ACTIONS_TOKEN` before making GitHub API requests; neither is supplied in the deployed Worker. No token is in docs/source/chat. Cloudflare clock and native GitHub control are already valid independent experimental arms. External dispatch correlation is a **pending later test**; do not claim it was exercised.
- **Observation window:** UTC hourly and 3-hour rhythms, starting after Cloudflare Cron trigger propagation (~15m) and ASES workflow registration, through at least seven full UTC days. Compare 48 expected Cloudflare rows/day against D1 (including delay and duplicate count), 8 expected native ASES schedule runs/day, and 8 nominal Trip'n production monitor schedule events/day. Distinguish GitHub run *creation*, runner start, detector result, and no-row slots; preserve run IDs and UTC evidence. Native ASES control and production Trip'n are both GitHub schedules and thus not independent triggers.
- **Reversibility:** To return Trip'n to the former cadence, restore solely the YAML cron line `7,37 * * * *` on master; reassess budget/scheduling evidence and alert latency. To stop the research clock, remove Cron Trigger from `ases-schedule-clock-20261102` (retain D1 evidence). To stop research GitHub cron, remove the `schedule` stanza, keeping manual dispatch for debugging.
- **Safety/coverage note:** Lowering frequency increases worst-case outage detection exposure even if provider delivery improves. Until the experiment proves coverage adequate, do not promise an SLA or continuous external monitoring. Auto-evaluation is *not* configured; the recorded evidence can be reconciled on a follow-up inspection.
