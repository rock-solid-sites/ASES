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
