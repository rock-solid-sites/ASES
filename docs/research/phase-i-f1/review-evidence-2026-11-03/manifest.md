# Preserved review evidence

This directory contains exact copies of the first-verdict record, the bounded review inputs, and the stdout/stderr artifacts captured during the review. Files were copied from `/tmp/f1-bridge-review/` without rerunning the original scenarios. The first verdict remains byte-identical to its original record.

## Provenance and commands

- Target revision: `89db5e03380b9420d0e54c0e11e459fd079b3329`; comparison base: `651a740be`.
- First verdict time: `2026-11-03T20:08:50Z`; initial run outputs were captured around `20:09Z`, independent harness output around `20:10Z`.
- Runtime recorded during review: Python 3.12.14, SQLite 3.53.1.
- Original bounded commands from the disposable copy: `timeout 30s python3 sqlite_capacity_competition.py`; `timeout 15s python3 active_capacity_reassignment.py`; `timeout 15s python3 stale_disposition_recovery.py`.
- Independent bridge command: `timeout 15s python3 independent_bridge.py`.
- The scripts' output JSON records child PIDs, outcomes, ACKs, and child exit codes. The independent output includes the separate read-only SQL observations taken before ACK.
- Stderr captures are preserved as zero-byte files (SHA-256 is the empty-file hash).
- The original command wrapper's numeric top-level exit code was not captured as a separate file. The original shell used `&&`, and execution continued to the subsequent output-size and runtime-version commands; this establishes successful completion but is not represented here as a raw numeric exit record. Child exit codes remain present in the original stdout JSON.
- The independent bridge script writes its SQL observations to stdout JSON. No separate SQLite database file survived its `TemporaryDirectory` cleanup; the exact SQL observation output is preserved verbatim.

## SHA-256

### Inputs

- `first-verdict.md`: `d20ec3a3e3229623e02fd0ab5767712d99de279b292a0ca838e0f418ef931eba`
- `source/sqlite_capacity_competition.py`: `34e60b2c6a291fb1f2ec3cfdf2d9512fca931970cb7e78cab3d518fef42402df`
- `source/active_capacity_reassignment.py`: `cd2a4b57ea5454d85fce553990854c6c8a76f9d6858491b3d5c6ed1e489278ba`
- `source/stale_disposition_recovery.py`: `871b2f03f7ff2b470070523abac9d60250adaa3c7eb5cd5385bf3bf59dee4560`
- `source/phase_i_f1_model.py`: `b0240c9aa1326f9a41d76e0ffe457bc3828b513b921f3c83ca41965958e07518`
- `source/independent_bridge.py`: `bf192c3733afac1b2d32f7ccc745a0c3ef99d29955b68f40b58b2d4b19e40bfa`

### Captured outputs

- `runs/sqlite-capacity.stdout.json`: `957c50e3db63288c18502ea41e95d8732f7f0c286ccebd00499bf3dcf1fe0cd7`
- `runs/sqlite-capacity.stderr`: empty, `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `runs/active-reassignment.stdout.json`: `1b9cccf75952688b19d34705901c5df389a69b1681692c09604f981c93641679`
- `runs/active-reassignment.stderr`: empty, `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `runs/stale-disposition.stdout.json`: `9fa5cf3858885247cefaf93b79bdea3dbd6b1379defb22ca143915d010fbbe78`
- `runs/stale-disposition.stderr`: empty, `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `runs/independent-bridge.stdout.json`: `0ee67c1040b73e196c7c9a62989a93673525ae389d82c43b7120f766880e5c8a`
- `runs/independent-bridge.stderr`: empty, `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
