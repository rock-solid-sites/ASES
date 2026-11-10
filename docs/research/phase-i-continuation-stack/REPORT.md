# Integrated cold continuation stack — bounded result

## WHY

The integrated claim needs three distinct paths to coexist in one native
process history: new effects must pass current F4 cold activation and current
F1/L5/L6 admission; exact-ID history lookup may observe an already accepted
effect without becoming new authorization; and the outer composed outcome
wrapper must retain local commitment when publication is unresolved. The
decisive test is whether source change or sink restart can turn an old accepted
effect into new permission.

## WHAT

`cold_sink.py` now exports `state_type(original, recover)` and its original CLI
uses that factory. The existing F4 cold probe passed after the extraction. The
integrated CLI loads the frozen composed sink and sets the cold factory around
its replay-derived `RetryState` immediately before calling the existing
`admission.serve`. That preserves the full append hook, Denied mapping,
receipt-aware cut state, and composed outer `OutcomeState` return wrapper.
The additional strict L5 schema check is in the branch's existing
`phase-i-effect-admission/admission.py`; no second admission implementation is
retained.

The final native run is `evidence/run-02/raw.json`. Its five histories show:

- A's real publication reply was suppressed after witness publication. The
  sink was killed and reaped, recovered the same journal with active v1 while
  cold-sealed, and observed A by exact ID with HTTP 200, original event sequence
  and accepted v1. Activate-only and a new B were refused without adding an
  effect. Native replacement and activation advanced to v2; B then appended
  and published. A remained a v1 historical observation, while a new ID with
  old v1 was refused.
- After native L6 dispose and removal, the raw catalog changed from live `x`
  to disposed `x` and `unit.live=0`; the object disappeared. Cold recovery still
  observed A with a fresh exact witness cut. After F4 v2 replacement and
  activation, a new B was refused by current admission with no effect event.
- A recovery with active v1 refused activate-only. After replacement to v2 and
  another kill, recovery retained inactive v2 and again refused activate-only
  without journal change. A fresh replacement to v3, activation and a valid B
  succeeded; new use with stale v2 was refused.
- An actual witness publication rejection left one locally committed A. Its
  identical retry returned `retry-observation-unresolved` with the original
  sequence and `new_local_effect=false`. A known same-ID payload conflict was
  decided without a witness call. Cold startup refused the divergent local and
  witness cuts.
- A test-only malformed L5 current recovery image set `schema=2` and used its
  actual new record hash and selected generation in a new B request. The
  existing graph predicate returned true, but the branch-local strict schema
  check refused B after F4 v2 activation with no effect append. Historical A
  remained observable with its original accepted version. This image was
  written directly as a test fixture and is not a native authorized migration.

The independent checker reads captured bytes directly. It verifies journal
lengths and SHA-256 values, exact event IDs and payload digests, admission
certificates and versions, F1/L5/L6 source captures, actual SQLite L6 rows and
object presence, witness roots/nonces/cuts, and all 31 captured source hashes.
Four altered controls are rejected: cold-seal bypass, historical result
misreported as a new effect, fabricated current L6 source, and unsupported
schema bypass.

The first four attempts are retained under `evidence/initial-01` through
`evidence/initial-04`; the intermediate `evidence/run-01` remains as a
superseded capture. The failures record a pre-run missing checker reference,
expected refused-startup handling that assumed a port, an incomplete manual
admission wrapper that returned 400 for a source denial, and a checker
assumption that L6 remained live after removal. The final integrated CLI
delegates admission and outcome handling to the existing composed sink, and
the L6 checker verifies native `(live,sealed)=(0,1)` after removal.

## CERTAINTY

**Evidence-based for these pinned local processes and the stated trusted test
imports.** The probe uses real F1/L5/L6/F4 processes, real append/fsync and
witness publication, real sink reaping and replay, and captured local and remote
state. The factory extraction was separately exercised by the existing cold
probe. This establishes the bounded composition behavior in these histories;
it does not establish a universal native identity or custody mechanism.

## NOT TESTED

No production integration, external target, provider/model call, host
configuration, all-writer custody enforcement, hostile same-UID writer,
physical-source identity, remote cancellation, or external exactly-once
delivery was tested. The schema-2 source is a deliberately malformed local
recovery fixture. The native witness is an in-memory local process and its
durability/rollback resistance is outside this slice. No CI or independent
review was run.

## Reproduction and source identity

From the `ases-continuation` checkout, use a new empty output directory; the
probe refuses to overwrite an existing one:

```sh
python3 -B docs/research/phase-i-cold-activation/run.py --out /tmp/ases-continuation-cold-repro-20261110
python3 -B docs/research/phase-i-cold-activation/check.py /tmp/ases-continuation-cold-repro-20261110/raw.json
python3 -B docs/research/phase-i-continuation-stack/probe.py --out /tmp/ases-continuation-stack-repro-20261110
python3 -B docs/research/phase-i-continuation-stack/check.py /tmp/ases-continuation-stack-repro-20261110/raw.json
```

The four integrated checker mutations can be reproduced against that fresh
output; each exits nonzero:

```sh
python3 -B docs/research/phase-i-continuation-stack/check.py /tmp/ases-continuation-stack-repro-20261110/raw.json --mutant cold-seal-bypass
python3 -B docs/research/phase-i-continuation-stack/check.py /tmp/ases-continuation-stack-repro-20261110/raw.json --mutant history-as-new-effect
python3 -B docs/research/phase-i-continuation-stack/check.py /tmp/ases-continuation-stack-repro-20261110/raw.json --mutant fabricated-current-source
python3 -B docs/research/phase-i-continuation-stack/check.py /tmp/ases-continuation-stack-repro-20261110/raw.json --mutant schema-bypass
```

The run is pinned to the captured candidate commits: admission `671ecc09`, retry
`16e6460f`, composed sink `0e724a6c`, and cold activation `4485a834`. The exact
native source commit pins and all 31 file hashes are recorded in
`evidence/run-02/raw.json`. Key source hashes for the final run are:

| Source | SHA-256 |
| --- | --- |
| receipt `cut_sink.py` | `5bd76e093f20acb264b1d7e5688c7353822f6a13686fd9d4c18af56e33c7c5ed` |
| receipt `managed_sink.py` | `7134618da4241942f2343748e44ae3d3e339e6d5f22c0681f539d404d0c8247f` |
| L5 `l5_integrated.py` | `7216dbb401afa01c01ef5f72a5c45555d5525678799aa30164a7eafce4076fd8` |
| L6 `store.py` | `baddc9a72c33dd3cae55e49e37c422dde6ba8dfd97493dd3954c5e0adcb2249c` |
| F1 `c11_service.py` | `864e43153e069247c6c2557dc5cb2ce7c51795c612a20515c2be0cb82c9a2c28` |
| `cold_sink.py` factory | `e5dba0f4846331b68199a44e20f8b4b5f4c058ce37c1da89195d713ccb19d7e1` |
| existing admission `admission.py` | `3c950d3ba9481e0997aae52b91aa5ea77558f501c3c0d8b7224f5fc9e3f544c5` |
| `continuation_sink.py` | `9b0abcfe61ee05bbbda66e9e1adb63f28bc0cb5d23f0f3081eeafd754a841b42` |
| `probe.py` | `5f6e6b823845fdad22c802dd0bfc40261c1be17d34ad29e3ba02b30ca991e86e` |
| `check.py` | `e1eae2db6d7cf080419949db02bd491cb9c4fea4a555c54a01c906e095170433` |

Check the key current and captured hashes with:

```sh
sha256sum docs/research/phase-i-cold-activation/cold_sink.py \
  docs/research/phase-i-effect-admission/admission.py \
  docs/research/phase-i-continuation-stack/continuation_sink.py \
  docs/research/phase-i-continuation-stack/probe.py \
  docs/research/phase-i-continuation-stack/check.py \
  docs/research/phase-i-sol-integration/evidence/sources/receipt/research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py \
  docs/research/phase-i-sol-integration/evidence/sources/receipt/research/phase-i-t18-sink-order-20261103/managed-revocation/managed_sink.py \
  docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py \
  docs/research/phase-i-sol-integration/evidence/sources/l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/store.py \
  docs/research/phase-i-sol-integration/evidence/sources/f1/docs/research/phase-i-f1/c11-sqlite/c11_service.py
```
