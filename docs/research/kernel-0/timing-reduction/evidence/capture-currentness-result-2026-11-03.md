# Coherent capture does not establish later currentness

Preregistered at `e4b739577`. All 20 schedules and 40 oracle serial candidates completed. Both modes use identical whole snapshot capture and monotonic version validation. Five of ten schedules per mode validate and five withhold the write because revocation falls between version samples.

| Resolution rule | Validated before revoke | Validated after revoke | Withheld | Unwitnessed |
| --- | ---: | ---: | ---: | ---: |
| Resolve against current state | 1 | 4 | 5 | 0 |
| Resolve against validated snapshot | 1 | 4 | 5 | 1 |

The sole unwitnessed case captures and validates the entire pre-revocation state, then revocation commits and a whole-state monitor observes it, and finally the stale snapshot authorizes a write. Serializing the write before revoke would change the monitor; serializing afterward denies it. The current-resolution control denies the stale-authority write and has a witness. This separates coherence at capture from freshness at resolution in one bounded fixture, without claiming a particular implementation mechanism is required. Shared oracle semantics, one fixed request pair, logical whole-state events, and an unbounded version are explicit limits; the withheld attempts do not test retry or progress.

The run counts 20 cases, 140 per-case cuts, 120 events, caps 20/140, wall 10 s and 1 GiB; elapsed Python 0.00274 s, peak RSS 12,672 KiB. Case-cap-3 and cut-cap-15 controls exit 2 with next exact schedule. Replay: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/capture_currentness_scan.py'`.

SHA-256 script `c13775646f467c4683d7a6f6eabf8cac3b47a760b8985eaf27f25cad13eacf59`; full log `999601c50fb02bcb531b80d8fd636ae237f73064757597914cf128508dd39921`; case truncation `f7cf57ccd06558d635eb6ceb3a0be63e109dabad2bac1956b06e548da9668036`; cut truncation `ae62d267b6d20920181ad6ec4c37a10ab38092633aa9b6bf5f9c058229346b56`.

Next cursor: inspect frozen RTL/correspondence premises and find the smallest feasible concrete-to-abstract discriminator; do not infer RTL behavior from this event abstraction.
