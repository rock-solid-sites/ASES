# T18/F4 recorded-trace correspondence

**Status:** bounded read-only correspondence, not an F2 fixture execution or host acceptance. The checker uses recorded events, journal representations, client results and fresh-reader observations; it ignores the producing harness's stored `assertions` and `pass` fields. The preregistration is `TRACE-CORRESPONDENCE-PREREGISTRATION.md` at `f59db0e24`. The F2 fixture file exactly matches commit `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`; the use-current case remains **prepared-only** in that file.

| Recorded case | Independent classification | Exact boundary of correspondence |
|---|---|---|
| Sink-ordered use-current | Supported analogue | Held old request seq 3, replacement seq 4, stale rejection seq 5; current v1/v2 requests accepted. The old request was initiated before replacement; the frozen F2 fixture sends after acknowledged revoke. A replacement is not automatically the same as its revoke. |
| Exact obligation | Supported analogue | Commit seq 2, replacement seq 4, matching obligation ID/payload/hash accepted seq 7. The separate client-send event is not logged. This is the selected decision-time profile, not use-current authority. |
| Detached-check mutant | Violation | Old permission read seq 1, replacement seq 3, old-version effect accepted under new authority seq 4. The violation is stale use-current admission. |
| F4 uninterrupted | Supported analogue | Client received 201 and fresh reader recovered one exact matching record. Raw output does not independently retain the gate events or the time of `fsync`. |
| F4 accepted-before-ACK | Unknown to caller; one committed effect recovered | No response was observed, while the recorded journal and independent reader contain one exact effect. Do not relabel this as a denial; no retry was tested. |
| F4 preaccept | Unknown to caller; no effect recovered | No reply and zero reader-reported effects. Missing journal and empty journal are indistinguishable in the original reader; this is not a general no-effect proof. |
| F4 early-ACK mutant | Violation | Client received 201, while the independently observed recovered effect set was empty, contrary to the selected success-after-acceptance contract. Missing and empty journal remain conflated by the original reader. |
| Recorded truncated control | Incomplete/refused | Reader returned an error and no successful empty recovery. |

In-memory corruption controls independently deleted a required T18 event, removed an F4 client observation, removed a T18 scenario, truncated a journal, and supplied malformed JSONL. All five produced `INCOMPLETE`; none was accepted as a successful history. These controls do not modify the preserved raw input files. Fixed recorded schedules only; no exhaustive event-order or fault search.

Commands from the repository root:

```sh
python3 -m py_compile research/phase-i-t18-sink-order-20261103/check_trace_correspondence.py
timeout 30 python3 research/phase-i-t18-sink-order-20261103/check_trace_correspondence.py > research/phase-i-t18-sink-order-20261103/trace-correspondence-raw.json
```

Both exited 0. Checker SHA-256 `76f2939998c09ec27649c7bd9def6a45f91764f3f0e3c1f7785941151d65f6d3`; output `254d2cd96b6020d89b3eda227ae2b17c908cc2c08fb114a1386266886834c6c1`. Pinned F2 fixture `bdc8cbeb5e917c10f23add99ab8dd88a9d2212d1d9f52be0a7e5c178e1eb6f65`; T18 raw `0f61e9b5a513c24a9f1d1c4f4089eafe990c3768ba0c4db7131416ecfe2522f1`; F4 raw `78a10b4b5e64f0e577102196149fb7cbfdb651e0dc7d5d986111b2e9784541ae`. T18 source at `b631bfae01faff1f32a8f81993386cdc3a36eb63` hashes to `d07e71da07638003c12852607c0662014e389a9d3b54499982f32fcdc509918f`; F4 source `run.py` hashes to `63d52186d3cd4cb64ad471b6b017a3406506930fb926be3e0da648e03de21b23`, matching its recorded source hash. Full specification hashes and checker results are in the output.

The recorded journal contains evidence of the local sink's accepted records and the fresh reader's results; it does not independently prove physical durability or ordering of the omitted F4 barrier and ACK events. The pinned T07 lost-reply fixture explicitly specifies **power loss**, whereas the concrete experiments kill only the sink process on a live host. T18 post-revocation initiation, source-to-real-sink correspondence, retained gate observations, missing-versus-empty recovery, power loss, real F3 routes and aggregate T01–T24 coverage remain unresolved. No F1/F2/F3/F4/F5 completion is claimed.

Resume cursor: independent conformance review of the checker and its input-to-profile mapping; separately, if authorized, obtain a recorded actual post-revocation initiated request with independently retained source/sink ordering, and distinguish missing from empty journal without changing frozen fixtures or treating process death as power loss.
