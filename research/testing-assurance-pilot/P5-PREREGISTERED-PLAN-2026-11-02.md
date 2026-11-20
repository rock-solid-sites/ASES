---
title: EDASES P5 — Comparative Crash-Recovery Assurance
program: EDASES
document_type: Preregistered Experiment Plan
status: Frozen Before New Test Code and CI Execution
date: 2026-11-02
authority: Experimental
---
# P5: compare conventional restart testing with qualified crash-boundary testing

**Methodology status:** DRAFT. This is a narrow, testable comparison of techniques, not a universal testing gate or language-selection decision. Use a new local append-only journal toy engine in Rust and Haskell. No production system, third-party provider, actual payment account, Trip'n booking, cloud infrastructure mutation or shared server stress is authorized.

## Claims and exact persistence boundaries

Each executable accepts a bounded reservation ID, requested units and charge, validates remaining capacity / spend cap / paid opt-in, appends a complete transaction record and performs an explicit file sync before acknowledging a successful commit. Recovery replays *complete* records, with no duplicate IDs in a correct engine. Every invocation is a separate child process; tests use one at a time to avoid claiming cross-process locking.

- **C1:** After a successful acknowledgement and program exit, a new process recovers exactly one reservation and charge. Retrying the same ID must not add a charge.
- **C2:** A child **SIGKILL before journal append** must leave no durable committed reservation; a retry may then commit once.
- **C3:** A child **SIGKILL after the append and successful fsync but before acknowledgement** must recover exactly one committed reservation, and a retry must not charge twice. The client did not receive an acknowledgment: retry must be idempotent.
- **C4:** If an ACK has been observed and the child is terminated immediately at the ACK pause, the acknowledged transaction must survive restart. An ACK is a claim of persistence.
- **C5:** The test harness must prove it actually reached the stated milestone, sent SIGKILL to the exact child, observed signal termination, then recovered state from the on-disk journal in a separately executed process.
- **C6:** Full CI artifacts and their hashes are independently retrievable, and independent-review ability is recorded honestly.

**Boundary caveat:** SIGKILL is a **process interruption**, *not* a power-loss, disk-cache-loss or sudden-host-failure simulation. File `fsync` returning successfully is the testable durability boundary, but disk/hardware guarantees are not established.

## Frozen conventional and qualified methods

**Approach A, credible conventional tests:** On a fresh journal, commit a normal authorized transaction, start a new process to inspect recovered state, retry the same ID (expect DUPLICATE/no additional charge), deny an unapproved paid request, and reject a request that would exceed capacity or the spend cap. On successful normal program exit inspect state again. Run on every original and faulty implementation.

**Approach B, A plus qualified crash checkpoints:** Repeat the same A checks, then run five independent repetitions of each of three kill points using new journal files:

1. **PREPARED** (after validation, before append): upon marker, send SIGKILL, verify exit `-9`, restart inspect (0 committed), retry one authorized request and recover one.
2. **DURABLE** (after complete append + fsync, before ACK): upon marker, SIGKILL, recover one; retry returns DUPLICATE and does not charge twice.
3. **ACK** (ACK marker, child explicitly held at a barrier): upon marker, SIGKILL, recover one without needing retry to establish durability.

No random-time kill is accepted as proof of targeted crash position. An unobserved marker, failed kill, unexpected exit, malformed log, no synchronization or fixture setup error is **INSTRUMENT_ERROR**, not a detected product fault. Preserve both successes and failures for each approach. Bound child process time and number of journal files.

## Fault candidates, frozen hypotheses, and falsifiers

Both languages have three **separate** research modes:

- `correct`: validate, append, fsync, ACK in that order; suppress duplicate IDs.
- `duplicate`: deliberately omit the duplicate-ID check. **Prediction:** both A and B detect duplicate charging on retry.
- `early_ack`: issue an ACK **before** journal append/fsync. For ordinary no-hook invocation, finish append/fsync before process exit. **Prediction:** A's ordinary completed-transaction/retry checks pass while B's ACK-kill case detects an acknowledged but missing commit. If A detects it, preserve that result rather than forcing a contrived advantage.
  
Additional hypothesis: B produces richer evidence but consumes more execution time and storage. Measure actual seconds, case count, error classifications, artifact bytes and any reviewer reconstruction effort. A comparison cannot establish relative developer productivity or reliability with only two planted defects.

**Controls:** A and B must pass every case for `correct` engines; all three checkpoint controls must verify the actual interruption and journal state. False-rejecting a compliant transaction counts against correctness. No language earns credit for a compiler error.

## Evidence and limitations

Run A and B sequentially on both languages/modes in one isolated GitLab CI job, using identical input parameters. Preserve the detailed per-operation transcripts, exit codes, checkpoint markers, source and toolchain versions, journal fingerprints (without sensitive data), elapsed wall times, failures and completed cases. The harness should *not* abort on an intentional behavioral violation: capture approach-level detections, but fail the CI job if the correct implementation fails, the instrument cannot be qualified, a faulty implementation is not detected as predicted, or evidence is missing.

Archive original raw provider artifacts outside GitLab's retention, with a digest match, or explicitly state NOT_VERIFIED. The pre-execution plan remains unchanged; report deviations in a separate results file. An independent reviewer has **not** participated unless an actual separate reviewer executes a blind reconstruction packet. **Do not** declare the testing method adopted on this result.
