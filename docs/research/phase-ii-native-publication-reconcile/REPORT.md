---
title: Native pending-publication reconciliation experiment
program: EDASES
layer: Research
document_type: Experimental Report
status: Experimental
authority: Derived
dependencies:
  - PACKET.md
  - SCHEMA.md
  - ../phase-ii-native-ownership/PACKET.md
downstream_consumers:
  - ASES methodology review
---
# Native pending-publication reconciliation

## Question

Can one privileged F4 reconciliation action publish and settle the exact final
locally admitted native effect after the real after-append EOF history, while
the ordinary cold mismatch refusal remains intact?

## Evidence boundary

The probe imports `setup_native_f3`, the actual F1/F3 owner, the existing F4
sink and private Unix witness process helpers from
`phase-ii-native-ownership/probe.py`. It invokes the isolated reconciliation
command against those native stores. It does not synthesize owner state,
journal parsing, or witness state. Source versions are pinned by SHA-256 in
each raw capture.

`probe.py` writes the detailed evidence to `evidence/run-*/raw.json`. The
capture is authoritative for process exits, exact journal and owner bytes,
nonce exchanges, witness records, and the retained F1 observation. This report
will summarize only completed histories and will not treat an incomplete
capture as a successful experiment.

## Results

`evidence/run-10/raw.json` is the final complete `PASS` capture. It pins
`reconcile.py` at SHA-256
`0e51253d600665c784dcd80af4870765134e2c82b814d6d361d9d334d9c87f9b` and the
executed probe at SHA-256
`66c1d0d7119e39bbfcba5d1462f71ff6cf9c4bf2a81aa27bc46ecb68df2967f7`.
Earlier runs remain as raw failed or superseded attempts; run-10 is the final
bounded evidence set.

The primary history reproduced a complete local event at sequence 4 followed
by EOF at the actual post-append gate. It retained one effect and unchanged
journal bytes. Ordinary cold start refused the mismatch with
`published-cut-unavailable`. While the original sink held the writer guard,
reconciliation returned `refused-writer-guard-busy` without changes. After the
sink stopped, reconciliation used one CAS from the exact preceding cut,
confirmed the full target with a distinct nonce, and settled the actual owner
reservation. No effect append occurred. A second reconciliation observed the
matching full cut, performed no CAS, and left owner records and journal bytes
unchanged.

Cold recovery accepted the reconciled cut while retaining its cold gate. After
the actual F4 replacement/activation, the probe sealed and moved the native
source, then observed the original ID's `already-accepted` result with the same
single effect sequence. A fresh ID used current F4 authority version 2 and the
current native epoch/selector; it reached the native admission guard and was
denied with `native-current-path-denied`. Pending child disposal was refused
before settlement. Normal child and content disposal completed after
settlement. F1 integrity and retained observations remained unchanged.

The additional actual histories distinguished:

| History | Observed result |
|---|---|
| Kill reconciler after witness confirmation, before owner settlement | Owner remained `local`; retry settled the same event with `cas_count: 0` and unchanged journal/revision. |
| EOF at the same gate | Structured `unresolved-settlement`; publication was confirmed while owner settlement remained unknown/local. |
| Lost witness `/publish` reply | One CAS attempt, transport loss recorded, fresh `/check` confirmed the target, and owner settlement completed. |
| Actual witness 503 CAS rejection | `unresolved-publication`; reply loss was false, one CAS only, witness remained at prefix, and owner/journal stayed pending and unchanged. |
| Non-prefix witness cut | Refused as `witness-cut-not-exact-target-or-preceding-cut`, with local owner and journal unchanged. |
| Corrupt journal tail | Existing parser refused; exact corrupt bytes and owner state remained unchanged. |
| Changed Unix attachment parent | Replaced the bound path with a new directory identity; refused with `native-witness-parent-identity-changed`, leaving the journal unchanged. |
| Reserved-only owner record | Refused without settling the reservation or changing journal/owner state. |

These observations support only the exact native profile and histories tested.
The evidence does not establish universal repair or cross-store atomicity.

## Reasoning and certainty

WHY: reconciliation must close a narrow pending-publication gap without
turning a historical effect into current D permission or dropping a complete
local effect.

WHAT: the actual native owner, journal parser, exclusive F4 writer guard,
bound Unix witness compare-and-swap, fresh proof, and owner settlement helper.

HOW CERTAIN: experimental until every required actual history and bounded
negative control passes with stable source hashes.

WHAT NOT TESTED: hostile same-UID/root, missing-witness recovery, arbitrary
rollback or power loss, remote exactly-once delivery, universal repair, and
new Kernel/F3 disposal semantics.
