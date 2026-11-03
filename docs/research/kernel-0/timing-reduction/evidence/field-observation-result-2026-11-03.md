# Two-field observation: publication alone does not make a multi-read coherent

Preregistered at `f8d41bf50`. The predicted positive control failed: publishing the successor as one whole event does not by itself make a reader's separately timed field reads a coherent observation. The original assertion failure and its exact source are preserved in `field-observation-prediction-failure.log` and `field_observation_scan_v1.py`. The final script removes only that incorrect assertion; it reports the full partition instead of suppressing the counterexamples.

| Publication mode | Cases | Coherent interval cut | No coherent cut |
| --- | ---: | ---: | ---: |
| Whole successor at first publication event | 24 | 16 | 8 |
| Each field separately; abstract commit at second event | 24 | 12 | 12 |

For example, in whole mode a read of field 0 before commit and field 1 after commit can assemble `(0,0)`, although the only coherent whole values are `(0,1)` and `(1,0)`. A whole publication event still requires the read interface to establish a coherent snapshot, retry, or equivalent behavior; this fixture does not establish any particular mechanism as necessary. The split mode also exposes torn tuples. Every incoherent tuple here is `(0,0)` or `(1,1)`; the preregistered possibility of a matching value outside the interval did not occur in this binary two-state fixture. Full schedules, snapshots, interval cut candidates and observations are retained in the raw log. The algorithm explicitly enumerates cuts between the first and last read, including the state immediately before the first read; it is independent of the frozen Kernel-0 oracle and tests only this two-value abstraction.

All 48 parameterized cases completed, counting 240 per-case cuts and 192 event steps; elapsed Python time 0.00044 s, peak RSS 8,960 KiB. The schedule-cap-3 and state-cap-11 runs both exit 2 with the next exact case; the cap counts whole cases and includes the root cut. Bounds were 48 cases, 250 cuts, 10 s and 1 GiB. `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/field_observation_scan.py'` replays the full run.

SHA-256: final script `cb0bb1269f2335c5e2238b67a1077a091a3b3cf15994ba8e2baba24543d5faec`; complete log `228a94e904ec513de1a9cff68c992620b9c1181d22f1e770cadc4e974c48ba47`; prediction failure `d6457a4f0e69ddfcee614b13d4b383adb19f193cc764d608bad50aadc08c3553`; schedule truncation `07f2e5753ff64d9df40bc962ad47af5db0fe63092df2548a4124b57b01f779cb`; state truncation `d57c55f1b7d92b4bb9ddc9d785a91e08a053ea20648004af82bbc3ab0b58a6c2`.

This is finite, one-reader/one-writer abstract evidence, not a physical implementation or unbounded proof. Next: test a coherent-read control and an explicit retry/validation control under the same event schedules before combining observation and stale-currentness products.
