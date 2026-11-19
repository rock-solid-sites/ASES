---
title: Generated Property and Stateful Testing — Cross-Project Pilot
program: ASES
layer: Research
document_type: Experimental Method Candidate
status: Draft
authority: Experimental
canonical_repository: ASES
depends_on:
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
last_updated: 2026-11-19
---

# Generated property and stateful testing — cross-project pilot

**This document develops a candidate reusable ASES assurance procedure; it is not an adopted universal ASES workflow or another skill.** It does not override VSDD, the existing testing/assurance proposal, the state-model applicability method, or project-specific policies. No new required phase or gate is established. The point is to learn when generated histories over *real implemented code* produce distinct, reliable evidence at justifiable cost.

## Why we are studying this

A prior experiment compared Hegel and proptest against a deliberately synthetic Kernel-0 stale-execution witness (ASES [PR #58](https://github.com/rock-solid-sites/ASES/pull/58)). It established that the generators compiled and could detect three inserted violations, but did not validate a deployed kernel or a substantial implementation. The operator requested application to real modules in HMS and ASES, with the resulting experience feeding one reusable method rather than multiple duplicative project-specific skills.

Existing research already supplies **object → attributable claim → evidence question → selected technique → executed evidence → bounded conclusion**, including the legitimacy of zero findings. Our pilots are intended to operationalize that principle, not replace it.

## First bounded cross-project observations

| Object and source | Executed independent claims | Engine and evidence | Result / limitation |
| --- | --- | --- | --- |
| [HMS TypeScript reservation/reconciliation/occupancy domain, draft PR #20](https://github.com/rock-solid-sites/HMS/pull/20) | Scoped newest-update preservation across delivery order; failed-refresh atomicity; assignment and per-day occupancy accounting against half-open interval arithmetic | fast-check 4.10.2, 3 × 400 generated cases, independent simple oracles, seed 20261119, one newest-update-loss control; [CI 44433622360](https://github.com/rock-solid-sites/HMS/actions/runs/44433622360) | No discrepancies in 1,200 sampled cases; 4 test methods pass, controlled negative case detected. Artifact upload **BLOCKED by quota**; scoped Git report in HMS branch. No real Beds24 auth/provider contract tested |
| [ASES Rust SQLite resource-control, draft PR #59](https://github.com/rock-solid-sites/ASES/pull/59) | Real `Store::reserve` admission bounds, rejected-state atomicity, replay idempotency, stale catalog rejection, SQLite reopen, then reverse-order cancellation and terminal-event replay conservation | proptest 1.12.0 and Hegel 0.53.1, 120 histories each; existing 48-test `control` suite; [CI 44434228368](https://github.com/rock-solid-sites/ASES/actions/runs/44434228368) | Both generators pass; extended cancellation/replay history also passes in [CI 44435444808](https://github.com/rock-solid-sites/ASES/actions/runs/44435444808). No meaningful performance or shrinking conclusion. [Initial artifact 14487831571](https://github.com/rock-solid-sites/ASES/actions/runs/44434228368/artifacts/14487831571) uploaded with 30-day retention; separate resource-control workflow has Clippy failures in unmodified source |

Both are real code tests with **generated test inputs**; the data fixtures themselves are synthetic and appropriately labeled. Testing the real implementation does not establish correctness of provider inputs or live deployments. The first synthetic Kernel-0 fixture remains a testing-engine *canary*, never a production assurance result.

## Candidate reuse loop (project-independent; no mandatory new lifecycle)

### 1. Select object and authority before a generator

Identify the exact module, source repository, commit/branch, user-facing consequence, authoritative upstream system and relevant trust boundary. Record current implementation state: real production, prototype with real code, mock adapter, or design only. If no executable relevant implementation exists, do not describe a fabricated test double as its verification. Begin with one high-consequence claim whose failure would change a product decision.

### 2. Freeze each attributable, testable claim

For each claim record identifier, exact source/commit and conditions, expected allowed/forbidden behavior, validity assumptions, observable API and exclusions. Explicitly classify TESTABLE, UNTESTABLE or INCONCLUSIVE. Do not silently invent a tie-breaking rule, billing semantics, identity model, provider guarantees, concurrency ordering or approval policy to make a test convenient. Distinguish real source claims from desired future requirements. Resolve ambiguities through a separate decision, not a passing test.

### 3. Choose the least expensive discriminating observation

Prefer an existing unit/regression test or read-only observation when it can answer the question. Use generated data when input combinations are broad; use stateful histories when transitions, retries, ordering, cancellations, updates or recovery interact; use concurrent or fault-injection tests only for boundaries where they can actually occur. Model-based/property-based tests are complements to live adapter and end-to-end tests, not universal replacements.

### 4. Build an independently checkable oracle

Keep the property checker simpler and meaningfully distinct from the implementation being verified. Examples: integer budget conservation for resource admission; a half-open interval model for bed nights; separately computed newest source revision per scoped reservation key. Record shared assumptions and sources of common-mode mistakes. Check accepted requests **and** rejection immutability. Where a primitive has no independent behavioral oracle, say so rather than comparing a function to itself.

### 5. Qualify the test instrument and its generator

Pair a known-valid neighbor with an intentionally violating control where feasible. Control mutations belong in isolated test implementations, never production or a live provider. Verify that failure is for the intended claim, not compilation, environment or an unrelated downstream check. Examine generated data distributions and semantic branch coverage; number of cases alone is not coverage. For stateful generators distinguish valid histories, invalid operations, stale inputs, missing evidence, and external errors. Preserve failed seeds, minimized traces and exact replay instructions; prove that replay actually reproduces failures.

### 6. Run against the actual object, with bounded risk

Separate test harness/dependencies from production code where possible; avoid implicit toolchain upgrades and unapproved external side effects. Pin exact source revision, dependencies/lock, runner, generator settings and budget. Use isolated ephemeral DBs, read-only remote adapters or explicit dry runs. Progress in layers: pure domain → actual persistence → actual API → controlled end-to-end/provider. Crossing a trust boundary demands new evidence, not extrapolation from a green unit test.

### 7. Preserve machine evidence and classify outcomes precisely

Minimum record: project/module, claim ID/source, code SHA, tools/versions/resolved lock, generator parameters and seed (or explicit non-pinning), test command and exit status, runner OS/environment, counts, detected/rejected controls, minimal counterexample and replay command when any, CI run/job URL, key raw logs and hashes, artifact retention, costs/resources when known, assumptions and WHAT-NOT-TESTED. Separate source verification, new property tests, legacy regression, formatting/Clippy, deployment, and evidence archival. The following are different outcomes:

- **NO_DISCREPANCY:** valid executed claims observed no violations within tested scope.
- **CONFIRMED_DISCREPANCY:** minimized and independently reproduced violation of approved claim.
- **INCONCLUSIVE:** harness, oracle, coverage or observation does not justify a claim.
- **BLOCKED:** required authority, interface, environment or evidence unavailable.

A failing artifact upload is an **archival defect**, not proof the tests failed. A green property runner does not erase a failing unrelated CI job. A CI run created is not a run verified. Zero defects found may be the correct result.

### 8. Review and decide separately

A builder/test author should not revise the frozen criterion in response to unexpected behavior. An independent reviewer checks source-to-property fidelity, oracle independence, meaningful boundaries, negative controls, replay and whether reported evidence supports the conclusion. Report model validity separately from implementation conformance and operational assurance. Adopt or refine a testing technique based on repeatable validity, risk coverage and cost—not on the number of bugs or assertions.

## Which parts can be reusable?

**Reusable ASES machinery:** a small claim-to-evidence manifest, generator/seed/replay conventions, negative-control contract, an engine-neutral result schema, CI job/retention guidelines, scoped assurance report format, and independent-review rubric. These can be implemented as libraries or optional CI templates after evidence justifies them.

**Project-owned material:** real domain functions, source contracts, authoritative provider mapping, domain oracles, fixture rules, permission decisions, and financial/booking/work-unit state transitions. Never centralize domain authority into a generic ASES testing engine.

**Tooling choice:** select tools to match actual implementation, not vice versa. HMS TypeScript can use fast-check; ASES Rust can use proptest/Hegel; Python prototypes can use Hypothesis/Hegel. Adding an engine is justified only when it supplies distinctive valid coverage or reduces cost. Do not install another overlapping ASES skill while the existing workflow package is being stabilized.

## Findings and repair queue after two pilots

1. **Real implementation first works:** both projects allowed generated histories to execute public domain interfaces without modifying runtime sources. The shared testing approach spans TypeScript and Rust, but the sample size and invariant diversity are still limited.
2. **Evidence storage needs an independent fallback:** HMS Actions hit artifact quota; its CI log remained accessible at the time of observation and a scoped account was committed to HMS Git. The original complete uploaded zip was **not** preserved. ASES artifact succeeded but expires after 30 days. Future runs should ensure full log/lock/seed artifacts survive GitHub retention and quota limitations (via approved repository records or durable external storage).
3. **Pin actual generated corpus identity:** HMS recorded seed, but the ephemeral installed lockfile was not committed. Rust recorded pinned direct dependencies and uploaded full post-resolution Cargo.lock, but the test runners did not pin both generator seeds and proptest warned about a persistence path. Fix these before comparing performance, shrinking or exact corpus reproduction.
4. **Do not hide global CI results:** resource-control's established Clippy job fails on unchanged files even when focused and existing regression tests pass. A pinned same-toolchain baseline comparison is required before attributing the failure.
5. **Instrument sensitivity still needs depth:** HMS checked one deliberate newest-update-loss case; the ASES real-Store run passed without a controlled mutation of production-adjacent admission logic. A future test should validate another genuine failure mode through an isolated mutant while preserving the real unchanged binary for the main run.
6. **No framework winner:** ASES test execution yielded one proptest run of 2.77 s and one Hegel run of 2.31 s. One cold/warm nonrandomized comparison is not benchmarking evidence; both shrunk nothing in this real-code run.
7. **Next discriminating targets:** The ASES Store's reserve → reopen → cancel/replay phase has now passed a second bounded real-code run, but interleaved concurrent reserve/authorize/launch/exit/recover state histories remain untested. HMS full multi-event reconciliation with valid cancellations, same-timestamp ambiguity explicitly excluded pending source contract; HMS actual guest/finance transactional persistence (not merely session-local ledger) and guest-session SQLite state; ASES reserve/acknowledge/begin/exit/reopen histories with intentional interruptions and independent bound checks. Trip'N quote/count contract should retain its known hardcoded four-adult regression first, then add generated count, stay-length and price-basis combinations. Keep live writes disabled.

## Third application: HMS guest finance and snapshot repository (2026-11-19)

A third bounded object was exercised in [HMS draft PR #21](https://github.com/rock-solid-sites/HMS/pull/21), continuing the same test harness in TypeScript. The [scoped evidence record](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-hms-20261119/research/property-testing/OBSERVATION-FINANCE-2026-11-19.md) preserves provenance and classifications.

- **Real objects:** guest payment and refund preparation, per-guest/currency ledger balance, frozen rational FX conversion, source/received cash-currency projection, and the synchronous `createRepository` snapshot commit port. The associated records are *session-only prototype objects*, not processor settlements or D1 persistent transactions.
- **New generated scope:** 300 payment/refund histories, 250 revision/write-failure/reset histories and 350 FX inputs (900 new cases), all with seed `20261119`, `fast-check@4.10.2`, Node `24.22.2`. The inherited 1,200 reservation/occupancy generated cases also passed in the final suite.
- **Initial finding:** [CI 44440078585](https://github.com/rock-solid-sites/HMS/actions/runs/44440078585) failed FX sign symmetry. A minimized counterexample after nine shrinking steps was 1 minor unit at a frozen rate 1/3. The *test oracle* expected signed `-0` while the implementation returned `0`. This was an **invalid test expectation**, not an implementation bug. Exact seed `20261119`, shrink path `75:0:1:0:0:0:0:0:0:1` and unmodified failure log are retained in HMS Git.
- **Repair and replay:** Isolated test-only correction to normalize zero was followed by [passing CI 44440191933](https://github.com/rock-solid-sites/HMS/actions/runs/44440191933), still with the same seed. No HMS domain implementation files changed.
- **Semantic coverage qualification:** [Final CI 44440558161](https://github.com/rock-solid-sites/HMS/actions/runs/44440558161) passed 7/7 methods after adding explicit non-vacuity assertions. Observed operation counts include 221 accepted refunds, 259 over-refund attempts, 247 wrong-property attempts, 249 payment replays, 106 refund replays; repository 232 stale-revision attempts, 204 duplicated IDs, 182 injected storage failures and 221 resets; FX had 7 zero-rounded cases. These counts show paths were exercised; they are not state-space completeness metrics.
- **Evidence storage:** HMS Actions artifact quota still prevented uploading a ZIP. Complete runner job logs from initial failure, subsequent correction and coverage run were instead committed to a separate experiment branch in the HMS repository. The ephemeral npm-generated lockfile remains unretained (only its SHA-256 and exact direct dependency version are recorded).

### Method adjustments derived from this incident

1. **Classify counterexamples before source changes.** A minimized failure can expose invalid oracle assumptions or a harmless representation difference. Preserve the original failed case and assert the source-backed domain equivalence (monetary zero) explicitly, rather than silently changing the test or claiming a product defect.
2. **Prevent vacuous green tests.** Record semantic categories (accepted, rejected, replayed, wrong-tenant, stale, failed-save, recovery) and assert nonzero exercise of required categories. Emit counters as machine-readable evidence alongside seed and shrink data. Numeric count alone is not coverage; add explicit branch/transition coverage expectations tied to the claim.
3. **Do not promote assurance across storage boundaries.** Prepared payment/refund records, isolated ledger snapshots and an injected synchronous storage port are separate from real transactional persistence of a receipt plus its evidence. Test DB/D1 atomicity and failure recovery as a distinct future object.
4. **Treat reproducibility as an independent acceptance dimension.** Committed full CI logs mitigated artifact quota; without the resolved dependency lockfile, byte-for-byte environment replay remains incomplete. The next pilot should commit a pinned isolated lock and use `npm ci` or otherwise preserve the complete generated lock.

**Scoped outcome:** No discrepancies found in HMS domain behavior for exercised histories; one independently classified test-instrument problem found and corrected. No production guarantee, framework preference, or canonical ASES procedure is implied.

## Promotion and consumption boundary

This is an **experimental research record**, not an ASES-wide gate. Before proposing a canonical adaptation, require an independent review of the cross-project pilot and finance evidence reports, a stronger stateful history that finds or soundly rejects a known controlled violation, repeatable evidence archival, and a clear cost/coverage comparison to existing deterministic suites. If retained, update the *existing* ASES Testing and Assurance Method and documentation index rather than creating a competing standalone methodology or skill. Consumers such as HMS, Trip'N and Projektor then inherit a **small optional contract**, while domain rules and test evidence remain in their own repositories.

Open questions: best durable artifact backend under current quotas; data structure for claim-to-test manifest; how to record generator coverage distributions; how to report flaky concurrent histories without confusing input determinism with schedule determinism; and the minimum assurance budget that is meaningful for each class of effect.
