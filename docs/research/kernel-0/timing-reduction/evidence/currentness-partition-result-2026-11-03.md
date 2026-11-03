# Partitioned currentness and monitor experiment

Preregistered at `1ff3f51aa`, using frozen Kernel-0 oracle/catalog and the existing `merge_effect` stale mutation. The inherited `flight_explore` changes authoritative state as a whole at resolution, so it cannot independently exercise torn publication. This standalone partition separates worker read/preparation, revocation preparation/commit, and monitor observation; internal candidate preparation is not made atomic with publication. It still explicitly treats each *logical authoritative commit* as a whole oracle event. Therefore this is not an exhaustive torn-field or physical atomicity test.

All 10 event orders consistent with the preregistered two chains were visited for each resolution rule; `write_resolve` is after the monitor. Replaying all three permitted serial orders independently per run gives:

| Rule and read position | Schedules | Serial witnesses | No witness |
| --- | ---: | ---: | ---: |
| Current resolution, read before revocation | 7 | 7 | 0 |
| Current resolution, read after revocation | 3 | 3 | 0 |
| Stale view, read before revocation | 7 | 0 | 7 |
| Stale view, read after revocation | 3 | 3 | 0 |

In each unwitnessed schedule the worker observes pre-revocation authority, revocation commits, and the authoritative monitor observes the revoked state before the stale worker publishes a write. Serializing the write before revocation would make the monitor see the write; serializing it afterward would deny the write. The separate serial replay checks complete outcome, whole monitored state, final state, and `revoke < monitor`, but shares the oracle implementation with the event executor. This extends the earlier bounded stale-view fixture with an explicit authoritative observation and an exact exhaustive schedule partition; it does not establish currentness in other request combinations, coherent multi-field reads under torn publication, or a global timing contract.

The run examined 20 schedule/rule cases, 120 executed event steps, 140 per-schedule state cuts (not distinct global states), and 60 serial-order candidates. The state ceiling applies to these counted per-schedule cuts; fixed schedule ceiling was 20, wall 10 s, address space 1 GiB. Elapsed Python time was 0.0052 s and peak RSS 12,544 KiB. The schedule-cap-3 run stopped incomplete after 3 cases/21 cuts with the next exact schedule; the state-cap-14 run stopped after 2 cases/14 cuts with its next schedule. Both retained exit 2 and raw cursors. These bounds include root cuts and do not silently label a truncated run complete.

Replay: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/currentness_partition_scan.py --state-cap 1000 --schedule-cap 20'`. Script SHA-256 `85cd885d0f3b69621bce699da7006403156a6b5c73ec4be42fec580760a0a7fc`; complete output `25951ae9f798bf946f73bb6ef74854ed2f211ebeaceef8854ea8773fe775cba6`; schedule truncation `26f280b7101a5e7d1a931a768427e4483a0561052fb76e084727a7f802ed7f3e`; state truncation `a840fc4c994b7fa093713112e2c3545e9851b56c2ce4fa585cfd80cf6d4cdc1b`.

Next discriminator: a separate bounded two-field observation model that explicitly exposes split authoritative publication and tracks the read's individual field times, with oracle comparison against every coherent whole-state cut. Combine with the currentness partition only after measuring its product size; the existing 10-order result cannot alone establish coherent reads across a split commit.
