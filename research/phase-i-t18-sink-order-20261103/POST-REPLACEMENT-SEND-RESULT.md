# Post-replacement request to the disposable sink

**Status:** one selected T18 use-current analogue, not execution of the frozen F2 fixture or F3 host acceptance. Preregistered in `POST-REPLACEMENT-SEND-PREREGISTRATION.md` at `744985792`. The previously recorded held-request result and its mismatch analysis remain intact.

Two sequential, separate local sink processes received the same four synchronous calls: current v1, version-1→2 replacement, stale v1, current v2. In both cases the replacement response was fully read before the stale HTTP helper was invoked; client-side monotonic intervals, request/response objects, four sink snapshots, complete server event sequence, journal bytes and hashes are retained in `post-replacement-send-raw.json`. The markers are invocation/response boundaries, not packet timestamps. Both sink processes were killed and reaped with exit -9.

| Sink | Before replacement | After replacement: stale v1 | After replacement: current v2 |
|---|---|---|---|
| Reference | 201; accepted | 409; rejected, no matching effect | 201; accepted |
| Disposable currentness-bypass mutant | 201; accepted | 201; accepted under current version 2 | 201; accepted |

For the reference, sink sequence 1 is the initial accepted effect, 2 is replacement, 3 is the stale rejection and 4 is the new current effect. The independent checker verifies snapshots as successive prefixes, all response and payload identities, version values and raw journal bytes. In the bypass mutant, event 3 is instead the stale accepted effect and is present in the journal. The mutant changes only the `/submit` current-version comparison in a temporary source copy; the checker reconstructs that exact change from the original and verifies its SHA-256. This is a direct currentness-bypass control, not the earlier pre-replacement detached-check mutation.

`check_post_replacement_send.py` reads the recorded trace and pinned F2 fixture, checks replacement-ACK completion before stale call initiation and the observed sink-side result, then reports `SUPPORTED_SELECTED_MAPPING` for the reference and `VIOLATION` for the bypass. Missing event, missing invocation time, and truncated-journal mutations each report `INCOMPLETE`. The pinned fixture still says `prepared-only` and is not modified. Its revoke/send order is matched under the **selected interpretation** that this local version replacement invalidates old use; its create/grant/activate bootstrap is not independently recorded here. No claim is made that arbitrary replacement and F2 revocation are universally identical.

Commands from repository root:

```sh
python3 -m py_compile research/phase-i-t18-sink-order-20261103/post_replacement_send.py research/phase-i-t18-sink-order-20261103/check_post_replacement_send.py
timeout 30 python3 research/phase-i-t18-sink-order-20261103/post_replacement_send.py > research/phase-i-t18-sink-order-20261103/post-replacement-send-raw.json
timeout 30 python3 research/phase-i-t18-sink-order-20261103/check_post_replacement_send.py > research/phase-i-t18-sink-order-20261103/post-replacement-send-check.json
```

All exited 0. Python 3.12.14, Linux 6.18.57. SHA-256: runner `58d7f6b9d6df85d2e9e9166e5816fcaa2779166d426c1854d930b3cd550c8d65`; raw `4ea421134ac56a604c771a980e0c6548dcbfbd277486759be7d57e111aaa7d38`; checker `d9798339a48286d9a2cd6b9743b72b48dbcfdd4451bf9f82533f949866f6f58a`; checker output `a9c50f1df32ee868555988c38db0a3b0064899bef7391f0b6b08f1bea86c141f`; original sink `63d52186d3cd4cb64ad471b6b017a3406506930fb926be3e0da648e03de21b23`; temporary mutant `c9569d7277793dfbbd704d1298cbb857c9f2b58b569dfaa3b41cdedc13b77a01`; frozen fixture `bdc8cbeb5e917c10f23add99ab8dd88a9d2212d1d9f52be0a7e5c178e1eb6f65`. Earlier T18/F4 raw hashes remain `0f61e9b5a513c24a9f1d1c4f4089eafe990c3768ba0c4db7131416ecfe2522f1` / `78a10b4b5e64f0e577102196149fb7cbfdb651e0dc7d5d986111b2e9784541ae`.

Two fixed schedules only. This tests the disposable loopback sink and currentness check; it does not prove a production sink, general host confinement, F3 route or aggregate F2 acceptance, all possible orders, or power-loss durability. The existing journal `fsync` contract remains a local assumption and no F4 crash experiment was rerun. Next: independent conformance review of both read-only adapters and the new event/source mapping; missing-versus-empty journal ambiguity and actual F2 bootstrap correspondence remain separately open.
