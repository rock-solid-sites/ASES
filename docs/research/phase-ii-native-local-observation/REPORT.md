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

Pending execution. Required histories are frozen in `PACKET.md`; the raw
capture format is in `SCHEMA.md`.

## Reasoning and certainty

WHY: after successful journal fsync, the durable F4 event is authoritative
evidence of a local effect even if the subsequent owner sequence callback did
not run. Recovery must observe that exact event rather than invent or cancel
an outcome.

WHAT: the existing protected reservation, parsed F4 event and index, native
owner `record_local_effect` callback, writer guard, witness proof/CAS, and
settlement helper.

HOW CERTAIN: experimental until each actual gate history and bounded negative
control passes with source hashes pinned.

WHAT NOT TESTED: hostile same-UID/root, arbitrary rollback or power loss,
absence-based reservation cancellation, missing-witness repair, remote
exactly-once delivery, generalized F3 semantics, or automatic grant revival.
