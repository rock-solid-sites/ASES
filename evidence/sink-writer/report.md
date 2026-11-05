# Sink writer exclusion check

**Result:** the original T18 ordered sink admits two cooperating-looking but unguarded processes against the same fresh journal. Both become ready before either append, both return HTTP 201 with sequence 1, and both records remain in the journal. A cold strict recovery refuses those duplicate sequences. A cooperative startup guard prevents the second guarded process from becoming ready before the first append and supports a killed-owner restart that continues the current journal at sequence 2. An unguarded participant bypasses that advisory guard and reproduces the collision.

This is a bounded same-host sink experiment. It supports a cooperative all-writer premise for the selected stable-root profile. It does not establish protection against a writer that ignores `flock`, authenticate the journal or root, establish host confinement, or test power loss. Strict recovery refusal did not erase the acknowledged contents: the captured journal bytes and digest were identical before and after refusal.

## Prediction and source basis

Before execution, [source-prediction.md](source-prediction.md) recorded the predicted case outcomes and SHA-256 hashes for the only four permitted source files. The execution used baseline tree `55aee5131141c82c9a6cd2e6418e02890a6291d8`. The recorded hashes were rechecked against the resulting raw capture. The supplied `check.py` was inspected as source, but the audit below was authored independently.

The source order explains the predictions. In `guarded_sink.py`, the process opens the lock file, takes nonblocking exclusive `flock`, and only then constructs `SinkState`; it keeps the file descriptor open through server lifetime. In `run.py`, each independent `SinkState` starts with `next_seq = 1`; a successful effect append is fsynced before its HTTP success response. Recovery validates strictly increasing sequence numbers and refuses duplicates. The lock is advisory, so an unguarded process does not join the exclusion protocol.

Phase-I Closure C6, C7, and C12 are used only as premise anchors: source-bound exclusion, current compatible recovery retaining accepted commitments, and acknowledgement after recoverable commitment. This check does not make a full closure or realization-conformance claim.

## Observations

The primary probe ran once. The two original unguarded processes shared a path and reported ready before the journal existed and before either request began. Each actual request received HTTP 201 with `event_seq: 1`; the journal contains both request IDs and payloads at sequence 1. Cold strict recovery exited 1 with `invalid durable sequence`. The post-refusal journal is byte-for-byte unchanged: SHA-256 `e088c4f40c641eca8911194b3debf0e85d241415ce48864d50c624f0a64efa87` (330 bytes).

In the guarded case, the second guarded startup exited 75 with `writer-guard-busy` before the journal was created. Across the first owner, blocked attempt, fresh-mode refusal, recovered owner, and final cold restart, the lock path, device, and inode stayed the same. The first owner returned HTTP 201/sequence 1 and was killed and reaped. Fresh mode then refused the existing journal without changing bytes. Recovery observed the same one-record current journal before becoming ready, restored the accepted effect, and accepted a second actual request at sequence 2. Final recovery exposed both effects in order at sequences 1 and 2.

The mixed-participation case showed the boundary: while a guarded owner held its lock, an unguarded process also became ready and appended a second actual HTTP 201/sequence-1 event. Two separate roots instead had different lock inodes and independently accepted and recovered their own sequence-1 events.

The read-only audit passed all these checks, including request ACK-to-payload correspondence, raw journal digest/records, startup precedence, guard identity, current-journal continuity, strict-refusal byte preservation, and distinct-root recovery. It inspected 15 owned child-process records in the raw capture.

## Reproduction and pins

From the repository root at the pinned baseline, run the primary probe exactly once:

```sh
python3 research/phase-i-t18-sink-order-20261103/writer-exclusion/probe.py > evidence/sink-writer/raw.json
```

Then run the independent, read-only audit against that captured file:

```sh
python3 evidence/sink-writer/audit.py evidence/sink-writer/raw.json > evidence/sink-writer/check.json
```

The probe capture records the execution SHA, Python version and executable digest, platform, resource bound, child processes, timestamps, startup frames, requests, and journal bytes. The captured execution pin is `55aee5131141c82c9a6cd2e6418e02890a6291d8`.

SHA-256 pins:

| File | SHA-256 |
|---|---|
| `research/phase-i-t18-sink-order-20261103/run.py` | `3dcb7f66f7e712778e275034e13cf21e845b0348a2c15fcd93bc465fd8823149` |
| `research/phase-i-t18-sink-order-20261103/writer-exclusion/guarded_sink.py` | `08cfe9d019631448f9570e418762d48326959bbedf89ac37fc41f380b2ef4133` |
| `research/phase-i-t18-sink-order-20261103/writer-exclusion/probe.py` | `d31473bcd0d70553351e18b927d96d4d842a890d6bd3cced7ac25e0c78f48f32` |
| `research/phase-i-t18-sink-order-20261103/writer-exclusion/check.py` | `586682823a8b487163ec8d756feb7b90f2e3b35a6d68c0df8af25b39c63615a1` |
| `evidence/sink-writer/source-prediction.md` | `6929735c5b124a69397affc981627124c802528fcc037d4cc8ff3fafeb6e35a9` |
| `evidence/sink-writer/raw.json` | `219cf7fdabac2522f5e9b82baaa5f44d6d2a3ee2591d1ebde18619827b8299de` |
| `evidence/sink-writer/audit.py` | `cb6abc87e5afac9bd26171585e0c73f5e2414c9750024352d188b61734833510` |
| `evidence/sink-writer/check.json` | `65580c6861166f67e18c0a8771d100ae2a9c4757b265012b1cab35eaa65f04a2` |

**WHY:** a startup exclusion primitive is relevant only if it is acquired before journal validation and held while the process can append; the overlap schedule and current-journal restart directly discriminate those conditions.

**WHAT:** one captured loopback process probe plus an independent read-only audit at the pinned tree.

**HOW CERTAIN:** evidence-based for this source version, filesystem/process profile, and schedule; not universal.

**WHAT-NOT-TESTED:** writers that ignore the advisory lock are shown to bypass it, but no adversarial root replacement, symlink/aliasing, cross-host/shared-filesystem, power-loss, payload authenticity, or aggregate F4/F1/cross-family check was performed.
