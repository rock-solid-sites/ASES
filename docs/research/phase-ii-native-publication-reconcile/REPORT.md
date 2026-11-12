---
title: Native pending-publication reconciliation experiment
program: EDASES
layer: Research
document_type: Experimental Report
status: In Progress
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

Pending execution. Required histories are specified in `PACKET.md` and the
raw capture contract is in `SCHEMA.md`.

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
