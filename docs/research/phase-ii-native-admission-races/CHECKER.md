---
title: Native revocation versus F4 append raw-evidence checker
program: EDASES
layer: Research
document_type: Assurance Record
status: Active
authority: Derived
dependencies:
  - PACKET.md
  - ../phase-ii-native-ownership/native_owner.py (frozen at parent commit f7b16ddbf34034ce1a0967c37cd92d5869f7e399)
downstream_consumers:
  - REPORT.md
---

# Purpose

`check.py` evaluates the two ASES-4 histories in the raw capture. It derives
claims from the selected owner records, consistent SQLite snapshots, actual
owned bytes, F4 journal bytes, and witness publication state. It does not use
a probe summary flag or admission certificate as the authority for a PASS.

Run the checker against the completed capture:

```sh
python3 -B docs/research/phase-ii-native-admission-races/check.py docs/research/phase-ii-native-admission-races/evidence/run-04/raw.json
```

This reads the capture and compares each listed parent input with its bytes at
frozen commit `f7b16ddbf34034ce1a0967c37cd92d5869f7e399`. It does not rerun the
probe or the earlier twelve native-ownership histories.

# Evidence checked

The checker verifies both append-first and seal-first histories:

- It decodes each direct `CURRENT` value, verifies its selected immutable
  record bytes and digest, and matches those bytes to the captured owner tree.
- It validates F1 and L6 SQLite snapshot hashes and integrity results. It
  reconstructs the selected F1 pair from query rows, requires the selected
  observation to remain retained, and binds each live L6 inventory row to
  captured owned bytes.
- It derives D permissions from its actual L5 ancestry. The initial path must
  grant read and write. Following the native seal, real move to Q, and
  activation, a freshly selected D path must be read-only.
- In append-first, the guarded F4 request must have an owner reservation before
  the gate. A separate owner's refused seal must report a busy/locked result,
  leave CURRENT, material, and F1 unchanged, and leave journal bytes unchanged.
  The actual F4 journal must then contain exactly one accepted effect bound to
  the submitted envelope and selected native owner. Owner publication sequence,
  witness cut, and the historical request-index record must identify that same
  row. The post-move new-ID denial must leave the journal and effect history
  unchanged.
- In seal-first, the before-admission request must have no reservation. The
  separate owner process commits the seal and advances native authority. The
  stale request and a fresh sealed request must both be denied without journal
  mutation or reservation. The journal must contain zero accepted effects.
- In both histories, the outer F4 authority remains active at version 1, so the
  denials are attributable to native owner state rather than a cold or stale
  outer gate.
- It makes two in-memory altered-evidence copies and requires rejection. One
  adds a self-consistent invented `effect_accepted` event after revocation.
  The other changes CURRENT during the append-first refused contender to a
  different retained owner record while updating the direct record bytes.

# Limits

The retained historical result is checked through the actual post-move F4
`/status` response: the original request ID remains indexed to its one journal
sequence, and the published cut matches the raw journal. The capture does not
issue a second exact-ID `/submit` after revocation, so the checker does not claim
that a post-revocation retry request was exercised.

These checks concern the captured local process and SQLite histories. They do
not establish behavior under same-UID or root compromise, arbitrary power loss,
remote delivery retries, or rollback. The two generated controls test that
these particular raw-evidence assertions reject those mutations; they are not
a general adversarial test of the checker implementation.
