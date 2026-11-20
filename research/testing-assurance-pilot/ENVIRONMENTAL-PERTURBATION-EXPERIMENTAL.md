# Environmental Perturbation Testing — experimental ASES technique

**Status:** Proposed selectable verification technique, **not** a global gate or an adopted methodology.

Perturbation changes an execution environment deliberately to reveal missing assumptions. Choose it when it provides a cheaper or more discriminating test of a stated system guarantee than ordinary functional examples, model checking or real-world experimentation.

## Selection and subtypes

- **Controlled scheduling:** barriers, deliberate interleavings and bounded delays around critical operations. Prefer deterministic scheduling when proving a race; random contention alone is insufficient.
- **Bounded resource contention:** constrained CPU, memory, I/O or concurrent workloads. Measure *applied* pressure; requested pressure is not proof that the application experienced it.
- **Fault/interruption injection:** dependency failures, network loss, process termination and restart, storage failures. Test recovery state, not merely whether the process exits.

Each dimension requires a stated claim and falsifier, baseline, expected permitted degradation, invariant(s), injected-condition telemetry, actual outcome and resource/cost measurement. Run in isolated CI or a similarly constrained environment, protecting shared infrastructure and never touching production unless separately authorized.

## Assurance-specific interpretation

Record these states separately: `INVARIANT_PRESERVED`, `INVARIANT_VIOLATED`, `PERTURBATION_INEFFECTIVE`, `INSTRUMENT_ERROR`, `INFRASTRUCTURE_ERROR`, `EXPECTED_DEGRADATION`, `NOT_TESTED`. Do not turn failed setup or ineffective load into a passing resilience result.

**Instrument qualification:** demonstrate the perturbation occurred (e.g. a measured pause, CPU usage and affinity, an actually terminated child). Include a positive neighbor. Where economical, inject a known fault that the method must expose; a test green under a faulty implementation is not sufficient.

## Marginal value and portability

Before extending the test dimensions, ask whether the environmental perturbation detected a violation that the baseline and other methods missed, how reliably it reproduces it, and what runner seconds / memory / storage / reviewer work it costs. Avoid applying every possible perturbation to every change.

Retain the frozen plan, unperturbed and perturbed observations, applied measurements, source/toolchain versions, exact seeds/barriers, failed setups, and artifact hashes independently of provider-retention limits. Report incomplete archive export separately from test results.

**Initial pilot:** [P4 preregistration](P4-PREREGISTERED-PLAN-2026-11-02.md). This begins with a minimal two-language stateful reservation experiment and deliberately bounded scheduling contention. Stateful crash recovery, disk/network failure and production integration are later **unverified** topics.
