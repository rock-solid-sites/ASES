# Independent fixed-claim check: journal short writes

**Assessment:** Supported for the bounded API-return scenario exercised here. **Certainty:** evidence-based. The original sink can send HTTP 201 after the selected journal write physically appends only part of a record; the repaired sink counts successive returned bytes and does not send success after a zero return.

## Evidence

The review was pinned to `43ddd00633ecf4d909021a47f89052f1dca1cfcf` (`research/autonomy-20261104-f4-write-count`). The reviewed `run.py` SHA-256 is `516b48d81012207f1d736304ba12ac4fdf5595e927e359a3ae5b5c9d0332f702`; `probe.py` is `f8c5f012b5ead80edaf838cdafe663a8289478dafdf84c6abc7a968d18e61bed`.

The baseline raw record uses source revision `589cee004b0c60d07fcdbc1b6ff2c96e60909b44`, whose source hash is `63d52186d3cd4cb64ad471b6b017a3406506930fb926be3e0da648e03de21b23`. Its normal control received 201 and cold-read as `VALID`. Under the short-return case, the scoped shim asked the real `os.write` to write 350 bytes, it wrote and returned 175, and the original one-call sink still returned 201. The retained journal ended mid-record; the independent reader exited 2 with `REFUSED: truncated final record`.

On the repaired source, the short-return trace records ten actual partial `os.write` calls (requested/returned counts: 356/178, 178/89, 89/44, 45/22, 23/11, 12/6, 6/3, 3/1, 2/1, 1/1). The client received 201. The cold reader exited 0 with `VALID`, and recovered the exact payload bytes `73686f72742d77726974652d6566666563742dcf800a696d6d757461626c65` and matching payload digest. The zero-return case made one shim call returning zero, raised `OSError: journal write made no progress`, left an empty journal that the cold reader classified `EMPTY`, and gave the client a connection close without an HTTP success response. The server traceback is the expected injected failure path.

The repaired raw's source hash matches the reviewed `run.py`, but its `source_revision` field says `d1c411e6731e818c1cc0a9e0c26f928262268b6a`; that commit contains the baseline source hash, not the repaired source. The runner reads source from the working tree but records only `git rev-parse HEAD`, so this field records checkout HEAD rather than binding the executed source bytes to a commit. Treat the raw's source hash plus this review's pinned commit as the identity of the repaired bytes. This is a harness provenance defect; it does not invalidate the retained write counts, journal bytes, client response, or reader result.

The separate `postsend-regression.raw.json` (SHA-256 `11bb6c1c963c84a6075c7a6f8c4caeb9c30091366219c7c1697c52532c0c93f1`) records a currentness/submit schedule check. It is not evidence for the short-write repair. The baseline and fixed raw SHA-256 values are respectively `d9be95a1e1aae5b6ec3197e1121bf509ceaf8b5e42bf3fd87a7a2857fe2bf103` and `30bc7d8520a8503297e9c489f15edcdf88bcd09858df5d4277f3ea2f9a8f821d`.

## Injection fidelity and controls

The probe makes a disposable source copy and replaces only the selected `os.write` expression with `shim_write`. For short returns, that shim calls real `os.write` with a shortened buffer and returns its actual count; therefore the partial journal bytes are real writes through the file descriptor. This is source-level API-boundary injection, not an OS-level fault injector. The zero case returns zero without calling `os.write`, modeling a zero-return API outcome.

Controls discriminate the claimed behavior: the baseline normal case establishes successful exact-record operation; the baseline short case shows premature success over partial bytes; the repaired short case shows continued writes and exact recovery; and the repaired zero case shows no success after zero progress. The fixed payload serialization is larger than the baseline serialization because the repaired source adds UTF-8 hex metadata, so the byte counts are not a same-length comparison. Both exercise the same logical payload and short-return rule.

Recorded commands (from the retained run record, each bounded by a 30-second timeout) were:

```text
python3 research/phase-i-t18-sink-order-20261103/short-write/probe.py baseline > research/phase-i-t18-sink-order-20261103/short-write/baseline.raw.json
python3 research/phase-i-t18-sink-order-20261103/short-write/probe.py fixed > research/phase-i-t18-sink-order-20261103/short-write/fixed.raw.json
```

The recorded wrapper exit was 0 for both phases; the owned sink processes were killed and reaped with exit `-9`. No additional harness rerun was needed for this check.

## Limits

This supports only the sink's response to the injected write-return values for this small local journal record. It does not test spontaneous kernel/filesystem short writes, exceptions after a partial write, `fsync` failure, physical power loss, directory persistence, rollback, or broader F4 gates. On failure, the in-memory event list is appended before the journal operation; the evidence supports absence of durable bytes and absence of HTTP success in the zero-return case, not transactional rollback of every in-memory side effect.
