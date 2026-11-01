# SQLite full-schedule gate: red–green adversarial test, 2026-11-01

Status: experimental local implementation, source archive supplied in conversation; **not yet committed to repository**.

## Repository write diagnostic

GitHub read access and a short new-file write both succeeded. Diagnostic commit: 2acca67ecc5fc2facaf02a5c305bd59c9e700102. The previous long audit tool calls were blocked by a tool safety check, not an observed GitHub permission failure. Root cause of the tool block is unknown.

## Expanded integration

A local ScheduleGate prototype now validates DAG dependencies, timing, execution-mode durations and resource demands, project/account authorization, CPU/RAM/slot capacities, explicit account/provider/product/period/unit identities, and allowance charges. It stores a policy digest and revision in SQLite and performs admission inside BEGIN IMMEDIATE transactions.

**Critical RED defect:** Two separate plans both reserved the same local machine slot, because per-plan feasibility was checked but machine capacity was not reserved globally. The focused test failed (second admission incorrectly succeeded). **GREEN fix:** Added persistent per-plan, per-environment, per-tick CPU/RAM/slot reservations, checked against existing active reservations in the same SQLite transaction as allowance admission. Release now frees both machine and unspent allowance reservations. The focused test passed afterward.

**Mutation evidence:** Deliberately disabling the shared-machine-capacity guard caused the regression test to fail. Restoring the guard returned the complete suite to green.

**Final local result:** 60/60 unittest methods passed with ResourceWarning treated as an error. Includes 12-process contention, stale revisions, tampering, DAG cycles, dependency ordering, authorization, budget limits, zero-credit local jobs, machine reservation release and non-overlapping time slots. One earlier insufficient-budget test initially had an incorrect expectation (3+2 fits a budget of 5); its fixture was corrected to demand 3+3 before recording green.

## Remaining serious gaps

- Existing reservations are checked using the *current* environment definition. Changing machine capacities or time-slot semantics while reservations exist needs an explicit migration/revalidation policy.
- Scheduling uses abstract integer ticks; real clocks, reset calendars, time zones, preemption and billing period boundaries remain unimplemented.
- The gate does not yet bind scheduler output to execution dispatch, agent identity, provider observations, or immutable task payload hashes.
- No global fairness, deadlines, optimality guarantees, running-work revocation policy, disk-full/corruption recovery, or multi-host support.
- The full-schedule prototype is not integrated into the existing portfolio planner or a clean-checkout CI workflow.
- SQLite WAL assumes a local filesystem and is not evidence of distributed safety.

Next gates: capacity changes with active reservations, crash/restart while a machine slot is reserved, mutation testing of authorization and resource arithmetic, randomized multi-plan state-machine comparisons, and full planner-to-gate integration.
