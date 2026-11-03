# L5 management current-record conformance

**Status: bounded single-holder policy conformance; no concurrency or host-confinement claim.** Preregistered before implementation in `MANAGEMENT-CONFORMANCE-PREREGISTRATION.md`. The prior stress probe remains preserved at `management-currentness-raw.json`; the conformance result is `management-conformance-raw.json`.

## Patch

`manager_roundtrip` now authenticates first, then loads the selected `CURRENT` record and rejects a caller-supplied state that differs from that published state. Under the declared single-holder/no-concurrent-writer assumption, this prevents the stale-state replay previously observed from replacing an active record. The compare and commit are not atomic against concurrent writers.

Activation now requires a valid current record with no current ingress, all units inactive and sealed, and C under the supported P or Q parent. Both the positive C-under-P activation and post-move C-under-Q activation in `run_case` use the manager handler. This removes the old direct positive-control field mutation and direct commit.

## Results

- Fresh authorized move committed `record-000002.json`, SHA-256 `b5100b89e554d99c6c58613e362f10613d8dd9faf85f4c4e2543674f775e337b`.
- Fresh authorized activation through the handler committed `record-000003.json`, SHA-256 `fc899329c71de4108f871dcfbbec0a338de9ab9010444182dd00084910fd23c4`.
- Replaying the authentic stale bootstrap state denied with `management-state-not-current`; selector and all files in the disposable protected store were byte-identical before/after.
- Wrong credential denied with `management-authorization-required`; selector and store remained byte-identical.
- An inactive but unsealed current activation fixture denied with `activation-requires-current-inactive-sealed-state`; selector and store remained byte-identical. This malformed current record was directly published by the test fixture and is not a manager-reachable history.
- Existing ancestor-use pure policy controls continue to pass.

Reproduce from this directory with `python3 -m py_compile l5_integrated.py test_management_conformance.py test_ancestor_use_policy.py`, `python3 test_management_conformance.py`, and `python3 test_ancestor_use_policy.py`.

## Remaining evidence gap

The existing safe moved path now exercises activation through the handler, and the former positive control does too. The test still uses a local socketpair/helper rather than a live trusted manager process. The single-holder assumption supplies serialization and current in-memory ownership; the code does not establish concurrent check-and-commit safety. Landlock is unavailable in this environment, so the integrated worker path was not run. This is not host L5 acceptance, F3 acceptance, or a production security claim.
