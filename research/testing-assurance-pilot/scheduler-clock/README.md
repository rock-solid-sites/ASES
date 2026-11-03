# ASES scheduling delivery experiment (2026-11-02)

## Scope and test arms

This is a **nonproduction, non-alerting** ASES research experiment. GitHub Actions
`rock-solid-sites/ASES/.github/workflows/ases-schedule-probe.yml` has a
native GitHub schedule (`13 */3 * * *`; 8 slots/day) and a harmless manual
`workflow_dispatch` path. The Cloudflare Worker in this directory runs
`9,39 * * * *` (48 clock ticks/day) and writes each scheduled UTC timestamp,
actual execution time, duplicate count, and dispatch status to durable D1.

The Cloudflare Worker is deployed in the Rock Solid Sites Cloudflare account
with a dedicated D1 database. Its fetch handler always returns HTTP 404; it
has **no public ingestion endpoint**, no booking queries, no issue updates and
no access to Trip'n production.

Eight Cloudflare ticks/day (hours divisible by three, at minute 09) are
eligible to dispatch the harmless ASES GitHub workflow. **Dispatch is
disabled by default**. Enabling it requires TWO separately configured
secrets/settings: a fine-grained GitHub token with Actions:write scoped only
to public `rock-solid-sites/ASES`, stored in the Cloudflare secret binding
`GITHUB_ACTIONS_TOKEN` (never commit the value), and `DISPATCH_ENABLED=true`
on the Worker. No GitHub credential is available to this research worker
at initial deployment; until deliberately configured, no GitHub requests occur.

## Evidence and readback

Cloudflare D1 database: `ases-schedule-clock-20261102`
(`722b87f3-1570-466b-8565-dd77f650a241`). A controlled read query:

```sql
SELECT datetime(scheduled_ms / 1000, 'unixepoch') AS scheduled_utc,
       datetime(observed_ms / 1000, 'unixepoch') AS observed_utc,
       observed_ms - scheduled_ms AS delay_ms,
       dispatch_status, http_code, duplicate_count
FROM ticks
ORDER BY scheduled_ms DESC
LIMIT 100;
```

Compare the expected 48 Cloudflare slots/day, the recorded actual Worker
timestamps, the native GitHub run-creation times (8 nominal slots/day),
and — *only after explicit enabling* — accepted external dispatches,
corresponding GitHub workflow_dispatch run-creation/completion times.
GitHub workflow_dispatch HTTP 204 means GitHub accepted the request,
**not** that a run has started or succeeded. Missing Cloudflare rows are
identified by generating the expected UTC cron series, not by relying on
worker logs. The `slot_utc` workflow input propagates the external slot
into the GitHub run title and logs for correlation.

## Invariants, limitations, and stop conditions

- Independent provider clocks cannot prove GitHub's internal event queue.
- Cloudflare Cron has global propagation delay (potentially ~15 minutes);
  allow propagation before counting missed first ticks.
- Never run the Trip'n production invariant detector or `simulate_failure`
  as part of this experiment.
- D1 stores only timing/HTTP status; no tokens or response bodies.
- A Cloudflare duplicate is recorded, but must **not** dispatch twice.
- A D1 claim followed by a Worker crash can leave a `pending` row;
  treat it as unresolved rather than claiming dispatch succeeded.
- A failed D1 write leaves no row; inspect Worker logs if missing.
- Do not interpret relative counts as per-tick delivery without
  correlating UTC timing and possible rollover.
- The native GitHub workflow on a public repo has small free Actions
  usage; the Worker and D1 are deliberately low-volume.
- Source of truth: this folder; restart or disable via Cloudflare
  Worker Triggers. Do not put tokens in the repository or in chat.

## Acceptance after a full observation window

Check a seven-day window (56 expected native GitHub runs, 336 expected
Cloudflare clock ticks; 56 Cloudflare dispatch attempts if enabled).
Count lateness, misses, 4xx/5xx acceptance, duplicate slots, and GitHub
job-start latency separately. Test results should be retained permanently
in ASES evidence independent of GitHub log retention.

## Typed evidence classification (2026-11-02)

The initial analysis is now governed by [EVIDENCE-CLASSIFICATION.md](EVIDENCE-CLASSIFICATION.md)
(experiment-specific, **not** promoted global methodology). The independent
03:49 UTC read is retained as
[`snapshot-2026-11-02T0349Z.json`](snapshot-2026-11-02T0349Z.json),
its deterministic output as
[`classification-2026-11-02T0349Z.json`](classification-2026-11-02T0349Z.json),
and the reproducible classifier and eight tests as `classify.mjs` and
`classify.test.mjs`. Run `node --test classify.test.mjs` and
`node classify.mjs snapshot-2026-11-02T0349Z.json`.

The classifier distinguishes missing source observations, GitHub runs not
yet visible, permanently *unproven* missing deliveries, disabled dispatch,
claim confidence, and incomplete artifact retention. Never infer an exact
native GitHub cron slot from a run's creation timestamp when delays can
cross expected intervals. New observations must be append-only snapshots;
do not overwrite the initial evidence after late events arrive.

## Readback repair and live cross-provider qualification (2026-11-03)

The [repair investigation](REPAIR-2026-11-03.md) records two isolated
observation errors (unsupported workflow-specific GitHub connector route and
incorrectly calculated minimum lateness), plus GitLab activation uncertainty.
Use `readback-v2.mjs` for UTC slot generation, GitHub repository-wide run
pagination qualification, conservative lateness bounds, and GitLab configuration
checks. The original `classify.mjs` now consumes those functions.

Run `node --test classify.test.mjs readback-v2.test.mjs` to qualify the
classifier without touching any provider. The append-only
[`snapshot-2026-11-03T0340Z.json`](snapshot-2026-11-03T0340Z.json) is a
bounded cross-provider source read, not a claim of full native CI log archival.

Never infer a run's true cron slot from its creation time. For the observed
21:41 ASES run the latest *possible* preceding slot is 21:13 UTC, so the lower
bound is 28m32s, **not** 2h28m. GitLab's two planned native schedules remain
`CONFIGURATION_UNVERIFIED` until both are authoritatively inspected and their
activation boundary recorded. The Cloudflare-to-GitHub dispatch remains
disabled by design.
