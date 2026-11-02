# Scheduler investigation: typed evidence and bounded conclusions

**Status:** experiment-specific evidence contract, v0.1, 2026-11-02. This is **not** an adopted project-wide ASES policy or a new orchestration gate. It applies the reasoning categories in the draft [Testing and Assurance Method](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md) and [Debugging and Fault Isolation Method](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md) without promoting them. The proposals live on a separate review branch; nothing here promotes them to canonical policy.

## Distinct objects, not one status flag

| Dimension | Recorded meaning | Invalid shortcut |
| --- | --- | --- |
| Configuration | Workflow/Worker schedule, revision, active state, activation/propagation boundary | `schedule configured` → `event delivered` |
| Intended slot | Nominal UTC cron instant generated from a **verified eligible window** | `nominal slot` → `guaranteed execution` |
| Observer/source | Query identity, as-of time, permission, completeness, error, retained raw/normalized response | `API query failed` → `scheduler missed` |
| Provider dispatch | Event trigger or external HTTP dispatch, with acceptance status if measured | `204 accepted` → `run started` |
| Run creation | Provider-issued run ID and `created_at` | `no run yet` → `permanently dropped event` |
| Runner/job start | Job ID, start timestamp and evidence, distinct from workflow `run_started_at` | `run created` → `runner started` |
| Check execution | Executed check, result, fixtures, actual production surface; not run metadata alone | `job passed` → `site healthy` |
| Evidence archive | Separate manifest, hash, provider-independence, capture completeness, privacy scope | `native CI logs exist` → `durably archived` |
| Claim evaluation | `SUPPORTED_WITHIN_SCOPE`, `CONTRADICTED`, `UNRESOLVED`, `NOT_TESTED` | `execution recorded` → `causal diagnosis` |
| Acceptance / intervention | Authorized decision and reason, separate from the agent's interpretation | `green test` → `approved release` |

### Minimal state semantics

`EXECUTION_RECORD_OBSERVED` means a D1 record establishes that the Cloudflare handler reached the database. It does **not** independently prove delivery completeness, successful GitHub API dispatch, or production monitoring. D1 `scheduled_ms` is recorded as the provider's scheduled timestamp; compare it **separately** with the nominal cron minute and the handler's `observed_ms`.

`NO_ROW_VISIBLE_AS_OF_QUERY` means a configured clock slot lacks a D1 row in the read. Possible explanations include failed/omitted delivery, a handler or storage error, observer/query incompleteness, or delayed ingestion. **Root cause unresolved.** `OBSERVER_UNAVAILABLE` applies if the source query failed; that state must not be counted as an absent event.

`NO_RUN_VISIBLE_AS_OF_QUERY` means the GitHub run listing had no new run created since the experiment's first eligible slot at the read cutoff. **This is not an executed failing job.** `SLOT_ATTRIBUTION_UNRESOLVED` is used whenever new run IDs exist but GitHub's native `schedule` event does not expose their exact intended cron slot. Nearest-neighbor matching by create time could misattribute runs delayed longer than a cadence. Actual run creations are retained independently of inferred slots.

`NOT_RUN_BY_DESIGN` is the appropriate dispatch category while the Cloudflare-to-GitHub dispatch gate is disabled. A schedule-eligible Cloudflare row with `dispatch_status=disabled` is evidence the Worker deliberately did not send an API call, *not* evidence of a GitHub rejection. An HTTP 204 would prove only API acceptance, if/when enabled.

`PARTIALLY_QUALIFIED` describes the instrument/evidence quality here: Cloudflare D1 is queried directly and GitHub provides native run metadata, but we do not have independent clock event telemetry, full GitHub job/log archiving, or automated cross-provider snapshots. This is **not** an accusation that known observations are wrong; it limits their scope.

## Frozen baseline and assessment

The reproducible input `snapshot-2026-11-02T0349Z.json` records a bounded **normalized excerpt** of the live Cloudflare D1 and GitHub run-list results, not the full provider response bodies. Its `as_of_utc` is the exact time returned by the Cloudflare-side read (`2026-11-02T03:49:40.796Z`). GitHub API reads were in the same bounded sweep but individual GitHub response timestamps were not captured. Never claim millisecond-level GitHub observation precision.

Run `node --test classify.test.mjs` and `node classify.mjs snapshot-2026-11-02T0349Z.json` (Node 22 used for the first run). The derived `classification-2026-11-02T0349Z.json` includes the input's SHA-256; the source repository commit pins all three files and the tests. The classifier is **offline, read-only**, and intentionally cannot change any live service or CI workflow. Its `first_evaluable_utc` is explicitly supplied per arm, not inferred from a file creation time alone.

- **Cloudflare:** six rows observed (01:09 through 03:39 UTC, 30-minute spacing, no duplicates). The **01:09 observation is excluded from the completeness denominator** to allow Cron trigger propagation after the 00:58 UTC deployment; five of five later eligible ticks have recorded rows. Observed end-to-end delays from the configured minute are ~32 seconds. The scheduling delay consists of a ~31-second provider scheduled-time offset and roughly 0.6–1.5 additional seconds to D1 observation. Only the observed window is supported; sustained reliability is unresolved.
- **GitHub ASES research probe:** created/active, first expected slot 03:13 UTC, no run visible at the 03:49 UTC bounded read. Classification `NO_RUN_VISIBLE_AS_OF_QUERY`, **not** `FAILED` or `PERMANENTLY_DROPPED`.
- **GitHub Trip'n production monitor:** configured/active with new first expected slot 03:07 UTC, no run visible at the same bounded read; latest lifetime run was #197 at 00:36:11 UTC, before the cadence change. Classification likewise `NO_RUN_VISIBLE_AS_OF_QUERY`. No live production check was executed by this research test.
- **External dispatch:** disabled. `NOT_RUN_BY_DESIGN`; result unknown.
- **Claim decisions:** clock records support functionality *in the five-slot observed window*; native GitHub reliability after the cadence change, exact upstream scheduler failure mechanism, future event arrival, and Trip'n production health are `UNRESOLVED`/`NOT_TESTED`. No automatic acceptance decision was issued.

## Test quality and limitations

The classifier has eight bounded deterministic tests: successful rows, the nominal-minute versus provider-scheduled timestamp distinction, preactivation denominators, zero run creation versus a failed job, later unattributed run, unavailable observer, absent row, disabled dispatch, and duplicate counts. These qualify its **categorization behavior**, not the underlying external services. An external test of an intentionally faulty monitor's sensitivity, and real CI job/run log archival, remain unperformed.

Do not silently rewrite the 03:49 snapshot when later runs appear. Make a new time-scoped observation and link it to the preceding record, explicitly saying whether later arrivals revise the interpretation. Preserve both snapshots, not just the latest verdict.

## What to capture on the next observation

Read Cloudflare D1 `ticks` (including `scheduled_ms`, `observed_ms`, `duplicate_count`, dispatch status) and independently list `schedule` runs for ASES workflow `404004929` and Trip'n workflow `366183226`. Capture each source status and UTC query time independently where supported. Where runs exist, retain IDs, run event, creation time, workflow start time, completion state, job-level `started_at`/`completed_at` when independently inspected, exact run source revision, and the archival status of logs. Compare against expected UTC slot series **without equating run creation to specific nominal slots**. A first run delayed hours changes the earlier `NO_RUN_VISIBLE_AS_OF_QUERY` observation into a subsequently observed run, *not* an erased prior observation.

### Retention gap to fix separately

This pilot preserves bounded metadata snapshots in Git but does **not** yet automatically export complete GitHub CI logs/artifacts independent of GitHub or Cloudflare Worker logs independently of Cloudflare. Archive completeness is a **separate measurable claim**. Do not promote the proposed universal CI retention requirement based on this partial pilot.
