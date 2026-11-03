# Return precedence rules out an apparent serial witness

Preregistered at `376ee9e62`. All 10 cases and 20 oracle serial candidates completed. `revoke_return` precedes `write_invoke` in every case. The cache may be populated in any of five positions before resolution; two are before revocation commits and three after.

| Mode and cache timing | Cases | Final-state witness | Final + outcome witness | Witness also respecting return precedence |
| --- | ---: | ---: | ---: | ---: |
| Current resolution, before/after revocation | 5 | 5 | 5 | 5 |
| Stale cache before revocation | 2 | 2 | 2 | 0 |
| Stale cache after revocation | 3 | 3 | 3 | 3 |

For the two unsafe cases, the cached pre-revocation authority permits the later-invoked write. The final whole state and both `commit` outcomes agree with serial write-then-revoke, but that order violates the completed revocation's return-before-write-invocation edge. Revoke-then-write denies the write. Thus final state and outcome serial equivalence alone cannot establish the observed real-time order here. This is a deliberately stale pre-invocation cache mutation, not evidence that an actual implementation uses it. Event and serial traces are retained; executor and serial replayer share the frozen oracle, though their control flow is separate.

The 10 cases count 80 per-case state cuts and 70 steps. Bounds 10/80, wall 10 s, 1 GiB; elapsed Python 0.00087 s, peak RSS 12,416 KiB. Case-cap-3 and cut-cap-17 controls exit 2 and give the exact next schedule. Replay: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/return_precedence_scan.py'`.

SHA-256 script `c105b3d5a2e14ca1e470e6ac8aa58099cf01d3a3f01bd1aeb2d15ce298a2e246`; full log `d3b6654c2c8ef1916fd85f1f06d87762a0be9973290d49b355d87a0e33fbfc4d`; case truncation `381b9192207d648a8fc18b3de75727f95771d37e2a442d34de8aa0856a868a42`; cut truncation `c910a732712c5881c777ae5b1ab04347d6a0cc5f21226b119191cb7d9c53ec2e`. These finite schedules are not a global linearizability proof or physical realization.

Next cursor: measure and preregister a bounded combined product of coherent field observation and revocation/currentness, retaining separate positive and unsafe controls and real-time edges. The present result does not test that combined interface.
