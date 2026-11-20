# Phase I reproducible assurance runner (experimental, 2026-11-05)

## Purpose and authority
Run independently repeatable, bounded Phase I tests in GitHub Actions without consuming Sol's model allowance. This is an **experimental runner**, not proof of Phase I correctness or authorization to merge experimental branches. Evidence from a green job proves only the specified observation on the recorded source, runtime, and assumptions.

## Source selection
The runner checks out **explicit full commit SHAs**, not moving research branch names, for each independent case. Every case is run in a fresh job. Each result records the tested SHA, workflow SHA, runner OS, Python version, command, exit codes, stdout/stderr, and source hash. Never combine evidence from different commit revisions without an explicit comparison.

Initial cases:
- F1 C11 SQLite accepted observation coupling: `29ec3960c4c6` (resolve to full SHA before enabling).
- F1 native resource COMMIT failure: `ff4ea8ba87f3`.
- F4 sink writer exclusion: `55aee5131141`.
- F4 published cut: `26db6db361be`.
- F4 publication receipt loss: `9226cd4b8cd1`.
- F3 L5 move death cuts: `51b34aface93`.
- F3 L6 inventory phantom: `0f348fda050e`.
- Kernel-0 mapped induction: `ea3f20cd13cf` (requires separate pinned Yosys image/toolchain; do not mark skipped as passed).

## Assurance contract
1. Baseline positive and adversarial controls both execute; an expected counterexample is **not** a failed test if its independent oracle detects it.
2. Independently validate checker failure on missing observation (INCOMPLETE), contradictory evidence (VIOLATION), and a known semantic mutation; checker exit zero alone is insufficient.
3. Distinguish original implementation from deliberately weakened mutants; preserve both results.
4. Re-run with fixed seeds and different seeds where applicable, then vary scheduling and process interleavings; record number of attempts, overlap and termination.
5. Verify process reap/EOF, exact bytes, fresh-process recovery and durable ACK provenance where claimed.
6. Classify each obligation as EXECUTED, INDEPENDENTLY_REPRODUCED, SOURCE_REVIEWED, PREREGISTERED, BLOCKED, TIMED_OUT, or FALSIFIED. A timeout is not a passing negative test.
7. Retain raw observations and their SHA-256 manifests. GitHub artifacts expire; copy important evidence to durable, separately indexed storage before expiry. No secrets in artifacts.
8. No main merges, no production credentials, no external writes, no privileged runner use. Use read-only GitHub token, explicit timeouts and per-job resource limits.
9. A passing suite is **bounded evidence**, not a universal proof. Formal claims must state theorem, model, assumptions, proof engine/version, source/netlist identity, proof logs, and uncovered physical/host boundaries.

## Initial CI implementation
The accompanying workflow uses explicit SHA-pinned experimental sources, clean Ubuntu runners, no secrets, a bounded 20-minute job timeout, and a read-only token. Each job reruns a source-specific `probe.py` then `check.py` against the newly captured output. Upload raw output, checker output, stderr, and machine metadata even on failure.

The first CI objective is **reproducibility**, not maximal load. Once the first four jobs are confirmed to execute, add an independent oracle and mutation suite; then scale to randomized schedules, multi-version/toolchain matrices, sanitizers, RTL model checking, cross-component integration, and cross-host comparisons. Prefer incremental assurance obligations over indiscriminate repetition.

## Formal proof roadmap
Maintain a traceability ledger: requirement -> invariant -> abstraction boundary -> proof obligation -> tool/model -> evidence hash -> independent reviewer -> limitations. Use SMT/SAT/induction for finite-state obligations, property-based testing and controlled mutation for implementation alignment, and integration/fault injection to test assumptions about external effects. Require a refinement argument connecting abstract proofs to the executed implementation. Neither extensive fuzzing nor successful bounded testing establishes proof by itself.

## Operations
Open a draft PR from `research/phase-i-ci-assurance-20261105` to `main` to keep review isolated. Inspect workflow runs, jobs, logs and artifacts after each change. Do not retry failing runs blindly; isolate runner/setup/harness/product faults with a minimal discriminating test. Never replace or rewrite Sol's original evidence; this suite is an independent replay and audit.

## Proposal-methodology reconciliation (2026-11-05; experimental)

The relevant candidate sources are on `proposal/testing-and-assurance-method-2026-11-01`, under `docs/proposals/2026-11-02-testing-debugging-ontology/`: `testing-and-assurance-method.md`, `debugging-and-fault-isolation-method.md`, `ontology-conformance-reviewer.md`, `integration-plan.md`, and `cross-conversation-reconciliation-2026-11-02.md`. They are **proposal-only**, not adopted global policy. This CI branch is a pilot and does not promote them.

The proposal requires separate axes for execution (PASS/FAIL/ERROR/INCONCLUSIVE/BLOCKED/CANCELLED/SKIPPED/NOT_RUN), claim evaluation (SUPPORTED_WITHIN_SCOPE/CONTRADICTED/UNRESOLVED/NOT_TESTABLE_AS_STATED), evidence quality (QUALIFIED/PARTIALLY_QUALIFIED/UNQUALIFIED), and authorized acceptance (ACCEPT/REVISE/DEFER/REJECT/ESCALATE). A CI job's success is not operator acceptance. Off-provider archive completeness is a separate boolean, not inferred from GitHub artifact upload.

The accompanying `evidence_contract.py` is a deliberately **conservative experimental pilot**: SHA-256 manifest generation and a claim classifier with positive and adversarial self-tests. It cannot claim qualified evidence without independently checked oracle and both negative and valid-neighbor controls. The existing six replay jobs currently run original probes and original checkers; these are **reproducibility checks, not independent-oracle qualification**. They do not yet produce the full portable manifest, frozen pre-run rationale, off-provider archive, or independently qualified claim. Do not treat their green status as a completed assurance case.

### Next pilot acceptance criteria
- Generate a common structured manifest for each case and route, with source/spec/harness revision, environment, seeds, exact command, outcome, artifacts and hashes, claim ID, before-run falsifier, and explicit WHAT-NOT-TESTED.
- Add independent-oracle controls: known invalid evidence rejected, legitimate neighbor accepted, and an intentionally broken checker detected; preserve original raw records.
- Demonstrate that archive failure is independently visible. Select project-owned off-provider storage only after deciding access, retention, expected volume, capacity, backup, and integrity checks. Never call a GitHub artifact durable off-provider archival.
- Compare a second CI route only after the common manifest can be consumed without rewriting the claim; cross-provider replay is reproducibility, not oracle independence.
- Preserve raw successes and failures, and append corrections/supersessions instead of overwriting original reasoning. Capture reviewer provenance and potential common-mode bias.
- Apply the debugging proposal's smallest-discriminating-test loop to every failure, distinguishing target defect, checker defect, runner failure, and archive failure.
- Evaluate the *methodology itself* with planted broken tests, valid controls, missing archive, no-new-test justification, and cross-provider portability. Record time, storage, false positives/negatives, and added assurance value.

### Baseline execution
GitHub Actions run [42034883130](https://github.com/rock-solid-sites/ASES/actions/runs/42034883130) completed six source-specific replay jobs successfully (F1 C11, F3 L5, F3 L6, F4 writer exclusion, F4 published cut, F4 receipt loss). The result is bounded replay success only; independent oracle and external archive remain outstanding.
