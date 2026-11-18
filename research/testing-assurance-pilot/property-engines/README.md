# Rust property-engine comparison — exploratory pilot

Status: experimental. This is a deliberately small synthetic witness, NOT an implementation,
an executable definition, or a verification of Kernel-0. No kernel code is changed.

## Source and question

- Source: docs/research/kernel-0/Kernel-0-Evidence-Packet.md, Bounded authority and Durable work and disposable execution.
- Source: docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md (object-first, valid null results, controlled red/green cases).
- Claim selected: a stale or superseded Execution must not mutate current authoritative state.
- Question: on the same synthetic operation traces and oracle, do Rust proptest and Hegel detect three violating mutants, shrink them, and replay them reliably?

## Synthetic fixture (explicit assumptions, not Kernel-0 decisions)

An original execution has lease epoch 0 and actor 0. Replacing it creates a new execution with a new epoch. Code 0 replaces with the same actor; 1 replaces with actor 1; 2 requests a write from original execution; 3 requests a write from the current execution. The independent simple reference model rejects writes from the original lease after any replacement.

Controlled mutants: accept-any ignores revocation; actor-only confuses actor identity with execution authority; partial-side-effect rejects unauthorized write but still changes durable state. The identical Rust reference computation and candidate implementation are called by both frameworks. This intentionally controls for model differences but does not provide an independent real-system oracle.

## Execution

On pull_request, a dedicated GitHub Actions workflow compiles the two test runners using Rust stable, runs an explicit compliant control and the three mutants for each engine (8 arms), captures full logs and JSONL summaries, and uploads temporary CI artifacts. The scripts never mutate the real ASES system. This experiment only runs for changes to this folder or its workflow.

To run locally from this folder: bash run_matrix.sh. Tests deliberately fail for mutants; the runner treats a failure as expected only when the test output contains the COUNTEREXAMPLE marker. The GitHub job passes only if both baselines pass and all six mutant arms produce observed assertion failures.

## Evidence limitations

- Detection on deliberately seeded controls is not proof of detecting unknown bugs.
- Both engines use the same synthetic fixture; this does not establish production implementation conformance or independent oracle correctness.
- Counts and shrunk traces are in logs; do not infer relative engine quality from a single sample or compare elapsed times as if they excluded process startup.
- Cargo.lock is captured in CI artifacts; artifacts expire. Retain any reviewed final findings in Git, with run URL, commit, exact resolved dependency versions, traces, and test scope.
- No canonical kernel primitive, state machine, execution technology, or guarantee is decided by this experiment.

References: https://docs.rs/hegeltest/latest/hegel/ and https://docs.rs/crate/proptest/latest.