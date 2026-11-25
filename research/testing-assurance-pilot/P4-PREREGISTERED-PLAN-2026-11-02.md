---
title: EDASES P4 — Stateful Reservations Under Environmental Perturbation
program: EDASES
status: Frozen Before P4 Implementation and Execution
document_type: Preregistered Experiment Plan
date_frozen: 2026-11-02
authority: Experimental
---
# P4 — Scheduling perturbation and isolated bounded CPU contention

**Test substrate:** new research-only, *in-memory* concurrent reservation toy implementations in Rust and Haskell, using the same JSON inputs. This is a new stateful prototype, **not** the earlier one-shot solver, the ASES funded-resource solver, or production reservations. No external payment or provider requests.

**Primary invariant:** atomic admission must never reserve more units than available, charge more than the authorized spending cap, accept an unapproved positive charge, or commit the same request ID more than once. Rejected transactions leave state unchanged. Correctly designed implementations may slow down but must not violate these constraints when scheduling changes.

## Frozen cases and required outcomes

All transaction checks and commits are required to occur atomically against current state.

1. `capacity-race`: capacity 1, cap 100 cents, competing IDs A and B, each reserving 1 unit costing 60 cents with explicit paid opt-in. **Exactly 1** admitted, 1 reserved, total charge 60.
2. `spend-race`: capacity 2, cap 100 cents, requests A/B each reserving 1 unit and charging 60 cents with opt-in. **Exactly 1** admitted, total charge 60.
3. `authorization`: capacity 2, cap 100 cents, requests A (positive charge 40, no opt-in) and B (40, opt-in). **Exactly 1** admitted, 40 cents.
4. `duplicate-id`: capacity 2, cap 100 cents, two concurrent requests sharing ID A, each 1 unit and charge 40 cents with opt-in. **Exactly 1** committed, total charge 40 and 1 unique committed ID.

Each program emits final state and measured actual critical-section pause. The independent harness checks the specific expected counts and the full observable invariant, not merely program exit status. Which worker wins when two requests are eligible is not prescribed.

## Prospective treatments and hypotheses

- **T0 unperturbed:** two workers each read and attempt to commit concurrent requests with a release barrier, and no intentional delay. Both languages expected to preserve all four invariants. Barrier reached by both workers is measured.
- **T1 deterministic scheduling delay:** insert a 3,000 microsecond delay **inside** the atomic critical section, verified by a monotonic measured pause of at least 2,500 microseconds per request. Same four final-state expectations. Any invariant change is a defect, not expected degradation.
- **T2 known faulty candidate:** deliberately split read/check from write using a barrier, making competing requests use an old snapshot before commits. This fault is experimental, not production code. Expect the `capacity-race` and `spend-race` controls to expose excessive allocation or charge, and `duplicate-id` to expose duplicate admission in both languages. An instrument that fails to detect it is not qualified.
- **T3 optional CPU contention:** bind one test process and one bounded spinner to a *single permitted CPU* for at most 1.5 seconds, using a bounded test-only process and no host-wide pressure. Verify the spinner actually used CPU and report the workload's measured delay. If affinity, isolation or pressure observation is unavailable, classify `NOT_TESTED` or `PERTURBATION_INEFFECTIVE` and do not claim resilience. Do **not** make the main suite fail merely because a shared runner lacks requested affinity controls.

## Falsifiers

Any safe variant admits more than one in the four cases, allocates over capacity, exceeds spend cap, bills an unapproved request, or duplicates a committed ID. Any faulty variant fails to expose any of the anticipated three race faults. Any delay treatment fails to establish that a delay happened. Any compiler, runner, dependency or measurement error counts as **ERROR**, not a behavioral red test. A failed CPU treatment does not imply failed business invariants.

## Isolation, cost and evidence

Use GitLab's existing shared Linux/amd64 CI for compilation and bounded probes. CPU contention uses at most one assigned core for no more than 1.5 seconds and does not intentionally stress RAM, disks or external networks. Run repeated trials (at least five) to verify consistency; retain each complete trial's results, wall times, tool versions, source SHA, and resource observations. Separate the native build/dependency overhead from test overhead. Do not run any production monitoring, Cloudflare, bookings or provider billing.

Record CI outcomes and the native 90-day artifacts. Transfer structured trace-observed outputs independently to ASES; mark complete full archive `NOT_VERIFIED` unless actually exported and hash-checked. Do not infer real crash recovery or durable journal behavior from in-memory tests.

**P4 decision:** A successful pilot qualifies this chosen perturbation technique only for the scoped concurrency invariants. It does not authorize method adoption, language choice or deployment. The separate ASES testing-and-assurance proposal remains draft.
