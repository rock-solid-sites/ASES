# Cold gateway-loss evidence

## Scope

This report records the disjoint native history in `resource-control/tests/native_local_cold.rs`. It exercises an actual `resource-gateway` Unix socket and a single harmless worker selected by a test-only trusted profile. The gateway is killed through its test-owned `std::process::Child`; the worker is never signalled by a saved PID. It exits when the test writes its release file, and its own timeout bounds an interrupted run.

The history retains raw request/reply pairs, SQLite `Store::event_log` snapshots, worker launch counter and process identity, plus source hashes under `evidence/cold/` when run with the evidence environment variable described below.

## Required observations

The captured history must show:

- one worker marker after launch and no increase after exact `local_launch` replay through the cold gateway;
- after gateway death, compact resume reports `unknown` and the worker remains independently bounded;
- a cold `local_stop` persists its launch-bound request but does not signal the now-unowned worker;
- `local_finalize` remains blocked and the reservation remains held without exact exit evidence;
- wrong selectors and caller-supplied command/PID/process/observation fields are rejected with unchanged durable event snapshots;
- the actual Unix peer configured only as a viewer is denied local administrator operations, with unchanged event snapshots.

## Run and evidence

The focused integration target passed 2/2 tests (one bounded worker helper and one history) on the adapter commit recorded in `evidence/cold/manifest.json`. The actual history confirms one cold worker launch despite exact replay, `unknown` liveness after restart, an effect-free blocked finalization with capacity retained, and a second independent path where hot stop/wait records exact exit evidence that survives restart and permits explicit cold finalization. The manifest records the exact command, test count, commit, and source hashes. The JSON history is primary evidence; prose interpretation is limited to what those records establish.

WHY: a controller restart destroys in-memory `Child` ownership, so a persisted launch intent must remain unknown and must not cause redispatch, signaling, or release of reserved capacity. WHAT: actual Unix gateway requests, test-owned gateway termination, durable event reads and the fixed worker's own marker/release/timeout. HOW CERTAIN: experimental evidence when the focused native history passes and retained records agree. WHAT NOT TESTED: whole-host power loss, hostile same-UID code, arbitrary programs, remote providers, generalized process containment, or automatic cancellation after authority/catalog changes.
