---
title: Native local observation recovery experiment
program: EDASES
layer: Research
document_type: Experimental Report
status: Experimental
authority: Derived
dependencies:
  - PACKET.md
  - SCHEMA.md
  - ../phase-ii-native-publication-reconcile/REPORT.md
downstream_consumers:
  - ASES methodology review
---
# Observe a durable native effect before owner sequence selection

## Question

Can the system recover the real F4 journal-fsync / native-owner-callback gap by
observing an already durable effect, while keeping strict reconciliation
refusal for a reserved record without a matching journal effect?

## Evidence boundary

The gate wrapper imports and runs the actual native F4 sink. It pauses only in
`NativeAdmission.after_append`, after the parent `emit_locked` has returned
from its append and fsync, and immediately before the original callback records
the owner-local sequence. After the gate is released it calls the unmodified
callback. The test kills the process at that boundary; it does not install
owner state, synthesize an event, or write the journal.

The probe uses the actual F1 and F3 setup helpers from
`phase-ii-native-ownership/probe.py`, the actual RetryState journal parser and
request index, the private Unix witness, owner CLI, and native settlement
helper. `evidence/run-*/raw.json` captures source hashes, raw owner/F1/L6/F4
state, process frames, gate frames, witness exchanges, and before/after byte
records.

## Results

`evidence/run-03/raw.json` is the full `PASS` capture. It records the final
implementation source hashes: `observe_local.py`
`dff70e2bb866c46d01d9a6c6840ce81579d4724ccc6bce019e05dff11f6e2207`, strict
`reconcile.py`
`588d502c72c674c4d8655d3ecdcab7919d09e2aae0cf831c2b656c4af5fe8bba`. The full
probe used hash
`6960db8146486fae5cf2a602da20b31c15d380efeb49824555a164c3be4dcb1b`. It ran
the prior full publication reconciliation probe once, which also reports
`PASS`.

`evidence/run-04/raw.json` is a focused reordered `LOCAL_CASES_PASS` capture
from a probe-only change (probe SHA-256
`53bee518ff3048bb2f5908ec94bcf9a88cd8fd5e4b1c06fc39692d82fb19c26f`). It
uses the same observer and strict-reconciler hashes as run-03, so the parent
regression result applies to the unchanged implementation. Run-04 changes the
history order to accept F1 world C, register C, and seal/move/activate the
source before observing the old world-A effect. It does not repeat the parent
regression.

The test wrapper paused after the real `emit_locked` append/fsync had returned
and immediately before the original `NativeAdmission.after_append` callback.
The retained process was killed there. The pinned `RetryState` parser found a
complete final effect at sequence 4 and indexed one effect; the protected
owner record remained `reserved` with no sequence, and the witness remained at
the exact preceding journal cut. Strict reconciliation refused this mismatch
without changing the owner, journal, or witness. The opt-in observer selected
the sequence from the actual parsed event, called the existing local-record
callback, performed the one required publication CAS and settlement, and left
journal bytes and the one-effect count unchanged.

After observation, an explicit test gate was killed before publication. The
owner retained the same local sequence while the witness remained at the
prefix. Strict reconciliation then published and settled that event without a
second observation or append. A real guarded pre-append kill left a reserved
owner record with no matching journal event; both strict and opt-in commands
refused and retained it. A mismatched protected reservation payload hash also
refused without further owner or journal mutation.

In run-04, the owner was already at epoch 4 with the world-C registration
selected when the observer consumed the world-A event. The observer changed
the old reservation to `published` at sequence 4 while preserving epoch 4 and
the selected world-C registration, without appending. The probe used the same
content bytes in F1 worlds A and C, retained the old registration, and recorded
both retained observations. The old exact request ID still returned
`already-accepted` for event 4 without changing the effect journal. A fresh
current-world request used the current F4 version and native owner
epoch/selector, reached the native guard, and was denied with
`native-current-path-denied`. F1 integrity and retained observations remained
intact.

These findings cover the tested native profile and crash boundaries only. They
do not claim cross-store atomicity or automatic cancellation of a reservation
when no matching event is present.

## Reasoning and certainty

WHY: after successful journal fsync, the durable F4 event is authoritative
evidence of a local effect even if the subsequent owner sequence callback did
not run. Recovery must observe that exact event rather than invent or cancel
an outcome.

WHAT: the existing protected reservation, parsed F4 event and index, native
owner `record_local_effect` callback, writer guard, witness proof/CAS, and
settlement helper.

HOW CERTAIN: experimentally demonstrated in the captured bounded native
histories and controls, with implementation source hashes pinned. The result
does not generalize beyond the stated native profile or prove cross-store
atomicity.

WHAT NOT TESTED: hostile same-UID/root, arbitrary rollback or power loss,
absence-based reservation cancellation, missing-witness repair, remote
exactly-once delivery, generalized F3 semantics, or automatic grant revival.
