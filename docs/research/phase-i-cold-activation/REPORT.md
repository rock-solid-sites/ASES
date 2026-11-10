# Cold activation continuation probe — result

## Coverage correction (run-02)

The initial `run-01` covered old-token refusal after a replacement was replayed,
but it did **not** try `/activate` at that second cold start. It therefore did
not establish the packet's fresh-replacement requirement for this history.
`run-02` adds that native request and preserves `run-01` unchanged. It shows
that the immediately previous wrapper source (captured from commit
`b85fd935`) accepts `/activate` at retained version 2 after the intermediate
kill (HTTP 200), reproducing the gap. The current wrapper rejects the same
request with HTTP 409 `fresh-replacement-required` and no journal append; a new
replacement to version 3, activation, and fresh effect then succeed. The
run-02 checker also decodes and hashes captured journal bytes to verify the
pre-loss event and compares the actual witness cut to the sink's runtime cut.
For the intermediate-recovery claim, use `run-02`; `run-01` remains the initial
capture and does not prove this discriminator.

## WHY

The pinned F4 sink replays its journal's active state. This probe asks whether a
token issued before engine death can still authorize a new effect after actual
process reaping and cold recovery, and whether a local cold-sealed continuation
can require native replacement followed by native activation while retaining
already accepted bytes.

## WHAT

The comparison ran the receipt F4 process and a disposable subclass around its
real sink state, journal, HTTP routes, and published-cut witness. Each path
accepted a pre-loss effect, killed and reaped the sink, and recovered against
the same journal and witness. The initial raw evidence is in
`evidence/run-01/raw.json`; corrected follow-up evidence is in
`evidence/run-02/raw.json`. Captured source files and local journals are kept
beside each record. `check.py` reads raw evidence without importing
`cold_sink.py`.

The pinned original recovered with `active=true`; presenting version 1 after
the sink's `-9` exit was accepted (HTTP 201). The pre-loss effect's exact
embedded bytes remained in the journal. In the candidate, replay also retained
`active=true`, but its in-boot admission gate started sealed. The old token was
refused (409) without journal growth, and `/activate` alone was refused. Native
`/replace` advanced the version from 1 to 2 and deactivated authority; native
`/activate` then opened admission. A version-2 effect succeeded and version 1
remained refused.

The candidate also survived a kill after replacement and before activation.
Its next cold boot remained sealed, refused the old token, and refused direct
activation with `fresh-replacement-required`, with journal bytes unchanged. A
fresh native replacement reached version 3 before activation and a fresh
effect. The captured pre-fix wrapper accepted activation after the same
intermediate recovery, demonstrating the specific coverage gap that run-02
closes.
An injected lost replacement publication reply returned 503 with
`local_control_committed=true`; the local cut and witness current cut matched
exactly before activation continued successfully.

A separate bounded worker completed 500,000 integer operations while the sink
was dead; its effect attempt during that interval got a transport error. It
completed further bounded work while the recovered route was sealed, and its
mediated effect was refused. The same old worker was then deliberately given
the new version-2 bearer token and its effect succeeded. This demonstrates the
flat-token physical-source binding limit; it makes no physical identity claim.
Unknown routes, an extra profile field, and a mistyped submit token were
refused at runtime without journal append.

## CERTAINTY

**Evidence-based for this pinned local process profile.** The discriminator
uses real child processes, kill-and-wait reaping, the pinned append and
publication code, exact local journal bytes, and witness readback. The
independent raw checker passed. Five altered controls were rejected:
candidate starts unsealed, admission resurrects after the intermediate kill,
intermediate activation succeeds without a fresh replacement, and replacement
reply loss is misreported as denial, or captured pre-loss journal bytes change.
Journal checks re-decode native event
bytes and verify the SHA-256, exact pre-loss payload occurrence and embedded
content hash. Witness checks compare its raw current cut with the sink's
runtime cut and captured journal hash. This supports the narrow cold-sealing
hypothesis; it does not establish a general engine guarantee.

## NOT TESTED

No obligation endpoints, pending external effects, provider or model calls,
host/system configuration, production behavior, cross-platform process or
filesystem semantics, multi-manager contention, independent review, or CI were
tested. The worker is a bounded local CPU probe, not a scheduler or service.
The candidate is disposable research code and adds no independent durable
authority store. A bearer token remains transferable: physical producer
exclusion is explicitly unresolved.

## Reproduction and source identity

From the `ases-cold` checkout, use a new output directory and retain prior runs:

```sh
python3 -B docs/research/phase-i-cold-activation/run.py --out /tmp/ases-cold-followup
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-cold-followup/raw.json
```

The checker mutation controls can be reproduced with:

```sh
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-cold-followup/raw.json --mutant unsealed
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-cold-followup/raw.json --mutant resurrected
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-cold-followup/raw.json --mutant activation-hole
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-cold-followup/raw.json --mutant lost-reply-as-denial
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-cold-followup/raw.json --mutant preloss-bytes
```

Each altered-control command exits nonzero. The source capture was made from
receipt commit `9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9` with:

```sh
git archive 9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9 \
  research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py \
  research/phase-i-t18-sink-order-20261103/managed-revocation/managed_sink.py \
  research/phase-i-t18-sink-order-20261103/run.py
```

The prior candidate control was captured without modifying the live wrapper.
Its source identity can be independently checked with:

```sh
git show b85fd935:docs/research/phase-i-cold-activation/cold_sink.py | sha256sum
```

Captured source and helper SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `published-cut/cut_sink.py` | `5bd76e093f20acb264b1d7e5688c7353822f6a13686fd9d4c18af56e33c7c5ed` |
| `managed-revocation/managed_sink.py` | `7134618da4241942f2343748e44ae3d3e339e6d5f22c0681f539d404d0c8247f` |
| pinned F4 `run.py` | `6b1d759b87b13d32bdc7c5f31a64c15d5a63296d77bc2f16ecc6b0e7795a9d59` |
| reused `phase-i-sol-integration/native.py` | `3b2eecfe64701e0c852f43f239fb0518a98c2c0365d62a863193f8f94cb111a6` |
| pre-fix `cold_sink.py` from commit `b85fd935` | `6de876db0fd3273507cb99f48dce8c96e81a3313f6e94e2e42cac09224b8a07f` |
| current `cold_sink.py` | `f94f8d28c78e75c1446e09b4f6838775b916ebcb59cdb1e1d892067c66804cec` |
| follow-up `run.py` | `9cdbd605b1990574bed22703a45aa49e818c9d796731aace9b72ad19091f056b` |
| follow-up `check.py` | `74370013422ebd68d9cef23d2e423173ee0c528404e5b48ad788034c9ba9424b` |
| `worker.py` | `084f353b104419e43a5cc566a84c5ea74623894799bdef665d4ed66222792915` |

The exact pre-fix wrapper is retained as
`evidence/run-02/controls/prior_cold_sink.py`; pinned F4 sources and raw process
evidence are captured under `evidence/run-02/`.

The source hashes can be checked against the capture and current helpers with:

```sh
sha256sum docs/research/phase-i-cold-activation/evidence/run-02/pinned/research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py \
  docs/research/phase-i-cold-activation/evidence/run-02/pinned/research/phase-i-t18-sink-order-20261103/managed-revocation/managed_sink.py \
  docs/research/phase-i-cold-activation/evidence/run-02/pinned/research/phase-i-t18-sink-order-20261103/run.py \
  docs/research/phase-i-sol-integration/native.py \
  docs/research/phase-i-cold-activation/evidence/run-02/controls/prior_cold_sink.py \
  docs/research/phase-i-cold-activation/cold_sink.py \
  docs/research/phase-i-cold-activation/run.py \
  docs/research/phase-i-cold-activation/check.py \
  docs/research/phase-i-cold-activation/worker.py
```
