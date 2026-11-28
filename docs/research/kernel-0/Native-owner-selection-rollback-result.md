---
title: Native owner selection rollback — recovery result
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Native-owner-selection-rollback-registration.md
  - docs/research/kernel-0/Native-acceptance-and-recovery-boundaries.md
last_updated: 2026-11-28
---

# Native owner selection rollback — recovery result

The native API can return HTTP 200 and `already-accepted` even when the selected owner record has lost the effect's settlement. In the admitted three-case matrix, the same API repaired a selected record that still named the effect and its local sequence. It left the owner unresolved when the selected record preceded reservation. In every case the exact F4 effect survived once and the F4 witness stayed unchanged. [Source crosswalk](Native-acceptance-and-recovery-boundaries.md)

## Observed cases

Each case originated one confirmed F4 effect and owner settlement before the controlled interruption. It stopped the native sink and closed all owner CLI processes. The fixture retained the live witness, journal, F1 and inventory files, immutable owner records and directory identities. Only the selected owner pointer changed in R1 and R2. The subsequent owner open and ordinary cold sink startup used the pinned native code. The retry reused the original request bytes through the existing F4 client.

| Case | Selected owner before retry | Exact F4 reply | Selected owner after retry |
| --- | --- | --- | --- |
| R0, current settlement | Record 7, `published` | HTTP 200, `already-accepted`, owner `published` with `replayed=true` | Same record 7 |
| R1, local event selected | Record 6, `local`, sequence 4 | HTTP 200, `already-accepted`, owner `published` with `replayed=false` | Fresh record 8, `published`, sequence 4 |
| R2, pre-reservation selected | Record 4, no effect entry | HTTP 200, `already-accepted`, owner `unresolved` with `native-effect-reservation-mismatch` | Same record 4, no effect entry |

All three cold sinks became ready. The retry left the full journal byte-for-byte identical within each case, with one `effect_accepted` at sequence 4, matching the original payload. The live witness remained at revision 5 with its original cut. Originally retained files remained unchanged. The only added protected file in the three replays was the record selecting the repaired R1 outcome. The originally published record 7 still existed as an immutable file in R2. The current recovery path did not select it. Thus this result identifies a recovery capability boundary even when the earlier records physically survive. [Raw three-case receipt](evidence/native-owner-selection-rollback/raw.json)

## Evidence and admission

The operator approved the exact frozen three-case matrix in WNASES-36 as a low-risk local run under the current admission method. The [frozen registration](https://github.com/rock-solid-sites/ASES/blob/b2031b71ed0dc791a6d5240d790cc289720785a2/docs/research/kernel-0/Native-owner-selection-rollback-registration.md) has SHA-256 `e32b8306f3c8d7c41c26ebecfb96432642b35528144b77cc02fd802f171e3187`. Execution used the [harness](native_owner_selection_rollback.py) with SHA-256 `385a851789e16a3dcd431e67e292b5df58226a2f3c649a7e6d692b01288c350f` and the unchanged native PR #38 checkout `0bd51a34700164a5eb77efe98158fa37d1a74e23`. Three cases ran once each, with no retry. Harness exit was 0. The recorded aggregate case time was 3.457 seconds and the output tree occupied 432 KiB. Python 3.12.14, SQLite 3.53.1 and an unprivileged Linux test user ran the fixed local fixture using private Unix sockets. The raw receipt SHA-256 is `930fd8037601d3150dca212ad153442173a621ae05a8dc6b9b2436657ed3f4d3`.

Reproduce within the admitted envelope using a detached clean checkout of the native pin and a fresh empty local output directory. The harness takes those two absolute paths:

```bash
timeout --kill-after=5s 295s python3 -B docs/research/kernel-0/native_owner_selection_rollback.py \
  /workspace/ASES-kernel-native-evidence /tmp/fresh-empty-output
```

## What the result changes

**REUSE** the native retry path for historical F4 observation where its published journal and witness both survive. **REUSE** owner re-settlement from an authentic selected `local` record under the R1 premises. A consumer that needs confirmed owner settlement must inspect `owner_effect` or an equivalent authoritative field. A consumer that infers current owner settlement from HTTP status or the F4 outcome alone has a concrete counterexample.

R2 rules out recovery of the missing selected entry *through the exercised retry*. It does not rule out a qualified recovery procedure using surviving historical records. A highest-numbered immutable owner record, by itself, is insufficient: `publish` writes the record before installing `CURRENT`, so a record can survive without having been selected. A historical F4 witness also does not attest later F3-only authority changes. An outcome-only repair could attempt to prove a specific historical event and restore an observational index without claiming the restored owner graph is current. Enabling prospective mutations or release of custody would still require independent currentness and final-extent evidence. This is a conditional design route. [Record selection and owner-side changes](Native-acceptance-and-recovery-boundaries.md) · [Final-extent obligation](Custody-at-an-admission-closed-cut.md)

**Open scope.** The fixture deliberately keeps one genuine owner directory, surviving immutable records and live F4 witness. It covers a targeted rollback of the selected pointer and subsequent native retry, with one local concurrency profile. Physical-loss durability, witness-process loss, general rollback of the material and inventory, cross-owner atomicity, safe disposal during recovery and W5/W6 remain open. The experimental source was unchanged.
