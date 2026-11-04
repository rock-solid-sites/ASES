# Short-return API injection exposes early success; bounded write-all repair

Preregistered589cee0; failing baseline committed d1c411e before repair. Separate continuation branch preserves unchanged November3 cross-layer source at5d45805. No canonical/runtime promotion.

Original normal positive returns201 and fresh strict reader validates exact record. Scoped short-return shim actually writes half the provided record and returns that count to the sink. Original sink ignores count, fsyncs partial bytes, returns201; fresh reader REFUSED truncated journal. This is a controlled API-boundary fault counterexample, not a spontaneous OS/storage failure. It shows a single successful syscall return is insufficient without checking count.

Minimal correction in this branch's run.py advances offset until all payload bytes have been written and rejects zero progress before fsync/success. Identical short-return shim on repaired source makes multiple actual writes, then returns201 with one exact complete fresh-readable record. Zero-return control invokes once, raises OSError journal write made no progress, client receives no HTTP success, extant zero-byte journal is EMPTY. Expected server exception traceback retained in raw sink_stderr; this is intended failure-path evidence, not a test harness crash. All owned sinks SIGKILL/reaped -9, wrapper exit0, wrapper stderr empty. No retry after uncertain outcome, partial-exception rollback or fsync-error atomicity guarantee.

Commands, each with timeout30, from repository root:

```
python3 research/phase-i-t18-sink-order-20261103/short-write/probe.py baseline > research/phase-i-t18-sink-order-20261103/short-write/baseline.raw.json
python3 research/phase-i-t18-sink-order-20261103/short-write/probe.py fixed > research/phase-i-t18-sink-order-20261103/short-write/fixed.raw.json
```

Baseline source is retrieved at frozen589cee0 for reproducibility even after repair; exact source/shim/runner/executable hashes, actual write request/return counts, payload bytes, response, raw journal/hash and independent reader outputs retained. API shim changes only selected write call in disposable copy; real os.write is given a shortened buffer, so its returned partial count is genuine for that shim. It does not establish frequency or possibility for a particular filesystem under the original tiny request.

Old provenance checker pins original sink and will correctly reject modified source here; historical gate/currentness evidence must be replayed at its recorded pins on original branch. Correction changes byte accounting only; selected post-replacement schedule regression checked separately without overwriting earlier raw. This is bounded local process/storage-interface assurance, not full F4, physical power-loss, directory fsync, corruption recovery, rollback resistance, native enforcement or arbitrary sink proof. Sink in-memory event list is still appended before journal operation; do not treat an event alone as durable acceptance on a failed path. Next: independent check of fault fidelity/repair and cold remote restoration.
