# SQLite adversarial verification — 2026-11-01

Status: local prototype and test evidence; implementation not yet merged into repository.

## Verified RED → GREEN

1. Two malformed plan-ID cases (settle and release) initially raised uncaught sqlite3.ProgrammingError. Two tests failed on the previous implementation. Explicit string validation corrected both; suite green.
2. A budget exceeding signed 64-bit SQLite integer range raised an uncaught OverflowError on initialization. A focused test failed, then passed after rejecting limits above 2**63 - 1.

## Expanded regression and state-machine tests

**43/43** local unittest methods passed, approximately **3.05 seconds**, with ResourceWarning treated as an error. The suite includes the original 30 tests, 12 adversarial/boundary tests, and one independent seeded model test executing **5,000 state transitions**. Every transition compares SQLite version, available quota, reserved quota and irreversible spent quota with an independently maintained in-memory model. The model also exercises reopen/reinitialize behavior.

Additional checks cover settlement-event uniqueness across plans, budget reinitialization immutability, period isolation, oversized and duplicate claims, stale revisions and release without refunding spent units.

## Remaining production blockers

- **Critical:** authorization policy and planning snapshot are not stored/checked in the same SQLite transaction as reservations. Multi-process stale-policy races are therefore **not solved** by this prototype.
- **Critical:** billing periods are caller-supplied strings; need timestamp-to-provider-period mapping, especially for crossing reset boundaries.
- **Critical:** reconcile local settlement events with actual provider usage and durable idempotency identifiers.
- Test local disk-full, corruption, interrupted migrations, crash timing and WAL checkpoint recovery.
- Do not infer clean-checkout CI, multi-host correctness, NFS safety, or production readiness from these local tests.

Next step: commit the complete SQLite implementation and tests after review, then implement a transactionally bound policy/snapshot admission gate using the same SQLite database and red–green/mutation testing.
