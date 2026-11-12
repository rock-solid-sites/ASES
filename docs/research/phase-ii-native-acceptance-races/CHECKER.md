---
title: Native acceptance races raw-evidence checker
program: EDASES
layer: Research
document_type: Assurance Record
status: Active
authority: Derived
dependencies:
  - PACKET.md
  - SCHEMA.md
  - ../phase-ii-native-ownership/native_owner.py (frozen at parent commit f7b16ddbf34034ce1a0967c37cd92d5869f7e399)
downstream_consumers:
  - REPORT.md
---

# Purpose

`check.py` checks the two captured ASES-4 histories from their raw selected
owner records, serialized F1/L6 SQLite backups, owned material, process frames,
and actual F4 journal and witness cuts. It does not treat the probe's `PASS`
field or an admission certificate as the authority for a claim.

Run it against the final capture:

```sh
python3 -B docs/research/phase-ii-native-acceptance-races/check.py docs/research/phase-ii-native-acceptance-races/evidence/run-03/raw.json
```

The checker requires the frozen essential F1/F3/L5/L6/F4 sources and verifies
every listed parent path against its bytes at commit
`f7b16ddbf34034ce1a0967c37cd92d5869f7e399`. It checks the actual race-probe
hash against the repository file. It does not rerun the probe or the earlier
twelve native-ownership histories.

# Evidence checked

The checker deserializes the captured SQLite images, runs the fixed F1 and L6
queries against those images, and compares the results with the captured query
rows. It verifies owner `CURRENT` bytes against the selected immutable record
and owner tree. Every live L6 inventory row must bind captured object bytes by
name, digest, and size.

For duplicate C acceptance, it requires:

- The real first owner reaches the `material-prepared` gate with F1 C selected,
  while native selection is still A.
- The second owner is a distinct prestarted process. Its accept request occurs
  while the gate is held and returns the captured busy refusal. Direct selected
  owner state, F1 snapshot, L6 catalog, and object bytes remain unchanged by
  that refusal.
- Releasing the first owner adds exactly one C registration and one C object.
  C binds the selected F1 pair; the earlier A registration and object remain
  present and accounted for.
- The second owner retry returns the exact selected C registration as a
  duplicate. `CURRENT`, epoch, registration state, L6 inventory, object bytes,
  and F1 current/retained evidence remain unchanged.

For producer overlap and use, it requires:

- The actual F1 Holder is ready before the owner gate, and its actual D accept
  operation starts before release. The direct F1 snapshot immediately before
  release still selects C. The checker accepts the captured busy or pending
  disposition; the run-03 observation is pending at release and commits D only
  after the native C acceptance commits.
- The selected native C registration remains current while F1 selects D. The
  worlds have equal accepted bytes and distinct required fields, with A, C, and
  D all retained.
- The native D unit is active on its original write-granting path. A fresh
  current-selector envelope for native C is denied with the exact reason
  `native-f1-selected-retained-mismatch`. The selected owner state and F1/L6
  evidence do not change, no effect reservation appears, and journal bytes do
  not change. Outer F4 authority remains active at version 1.
- The owner seals C, accepts current F1 D as a distinct native registration,
  and activates D. A fresh current D envelope produces exactly one accepted
  F4 event. Its raw payload, request ID, admission binding, owner publication
  sequence, sink cut, and witness cut all match the D envelope and final
  journal bytes.

The checker creates two in-memory altered-evidence controls and requires
rejection. The first adds a hash-consistent second C registration and a matching
L6 catalog/object entry. The second injects a rehashed accepted event for the C
envelope while direct F1 still selects D.

# Limits

Run 03 demonstrates one bounded producer overlap: the actual F1 call began
before release, C remained selected at the pre-release snapshot, and the D
response completed after release. It does not establish universal scheduling,
fairness, or liveness behavior. Runs 01 and 02 are incomplete scheduling
captures and are excluded from the final checker invocation.

These local histories do not establish behavior under same-UID or root
compromise, arbitrary rollback or host power loss, remote exactly-once delivery,
or generalized F3 confinement. The two mutations check these specific
assertions; they are not a general adversarial proof of the checker.
