# ASES scheduler-clock preliminary observation — 2026-11-02 ~02:48 UTC

## Read-only sources

- Cloudflare D1 `ases-schedule-clock-20261102`, `ticks` rows via D1 REST API, queried in the 2026-11-02T02:48Z preliminary check.
- GitHub Actions workflow run listing for `rock-solid-sites/ASES` workflow ID `404004929`, and `TripN-Chill-Zone/tripn-astro` workflow ID `366183226`.
- Both workflows independently reported `state=active`.

## Cloudflare scheduled events

| Configured tick (UTC) | D1 scheduled_at | D1 observed_at | observed - scheduled (ms) | Duplicates | Status |
| --- | --- | --- | ---: | ---: | --- |
| 01:09 | 01:09:31 | 01:09:31 | 596 | 0 | `not_dispatch_slot` |
| 01:39 | 01:39:31 | 01:39:32 | 831 | 0 | `not_dispatch_slot` |
| 02:09 | 02:09:31 | 02:09:32 | 1132 | 0 | `not_dispatch_slot` |
| 02:39 | 02:39:31 | 02:39:32 | 828 | 0 | `not_dispatch_slot` |

- Four out of four **observable expected ticks** recorded after deployment, with no duplicate events.
- Scheduled-time timestamps were already **31 seconds after the UTC cron minute**; actual handler execution followed within approximately 1 second. Do **not** mislabel the latter as end-to-end cron latency.
- External GitHub dispatch is still disabled; these events are all heartbeat-only by design, and none falls on a dispatch-eligible 3h slot.

## GitHub observations and boundaries

- ASES research probe: active; **0 workflow runs yet**. This is **expected**, because the control was created at 2026-11-02T00:54:52Z, after the 00:13 UTC nominal slot. First eligible `13 */3 * * *` run is 03:13 UTC, *future as of query*. The empty history is **not** evidence of a miss.
- Trip'n production invariant monitor: active, **197 lifetime runs**. Latest `schedule` run #197 created at 2026-11-02T00:36:11Z, completed successfully: https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/41368023717. This predates the cadence change around 01:00 UTC. The first new `7 */3 * * *` slot is 03:07 UTC, *future as of query*. Therefore no new-cadence reliability claim is yet justified.
- Cron states and counts were read-only; no workflow runs manually dispatched, no booking checks or alert issue mutations. No premature missed-slot assertions.

## Immediate next discrimination

After 03:13 UTC, check Cloudflare D1 for 03:09 heartbeat (`dispatch_status=disabled` by design), GitHub ASES probe for 03:13 nominal native run creation, and Trip'n for 03:07 nominal production run creation; preserve run creation and job start separately. A missing GitHub run at 03:13 does not immediately prove permanent loss, since delayed creation is the observed failure mode. Repeat at 06:07/06:13 and after 24h.
