# Real ASES Rust/SQLite property-engine comparison — first executed observation

Date (UTC): 2026-11-19 01:05–01:06. Status: **bounded property trials PASSED; framework advantage UNRESOLVED**.

## Object, independent claims, and versions

- Source is the actual `resource-control` crate from `research/phase-ii-native-identity-lifetime-cloud-20261112` at SHA `fbf5cea6a925419c2bd6774ab1ce659cab41ec10`. Experimental PR #59 head `93e97a1d2aa7a23017fc2c75460abd08f51bad52` adds test-only dependencies, shared oracle, two test runners and CI; **runtime implementation was unchanged**.
- The actual SQLite `Store` is used for every generated case, including readback after dropping and reopening the connection.
- Source-backed claims: reserve only available allowance under current catalog authority; rejected admission and stale versions do not create side effects; exact-ID replays do not allocate or append events again; state is durable across process-local Store lifetimes.
- Oracle: independent arithmetic `expected_used += amount` on successful admission with a 100-unit fixture budget. Explicit fixture preconditions include fresh account/environment/meter snapshots, 64 parallel slots, unique IDs, 1–80 units per claim, and at most 19 sequential proposals. That is an actual implementation test with bounded generated inputs, **not a production provider allowance reconciliation**.

## Execution

- Tested PR: https://github.com/rock-solid-sites/ASES/pull/59
- Dedicated GitHub CI run: https://github.com/rock-solid-sites/ASES/actions/runs/44434228368 — **success**.
- Artifact: https://github.com/rock-solid-sites/ASES/actions/runs/44434228368/artifacts/14487831571 — `ases-real-store-pilot.zip`, uploaded zip SHA-256 `96e63c105d3d65acef51a692cce530e6f2d84b800a6b05b8bf84ec9023fc66ba`, retention 30 days; contains before/after lockfiles, exact Cargo metadata, complete regression and test logs.
- Rust/Cargo: `rustc 1.100.0 (0ef1bc386 2026-11-09)`, `cargo 1.100.0 (3acc79c0c 2026-11-05)`.
- Exact top-level generator dependencies: `proptest 1.12.0`, `hegeltest 0.53.1`, with `hegeltest-c 0.52.0` resolved; full resolution currently retained in artifact, not yet committed to `resource-control/Cargo.lock`.
- Unchanged existing `cargo test --test control`: **48 passed, 0 failed**.
- `cargo test --test resource_property_proptest -- --nocapture`: **1 test function, 120 generated cases, passed**; test body finished in **2.77 s**.
- `cargo test --test resource_property_hegel -- --nocapture`: **1 test function, 120 generated cases, passed**; test body finished in **2.31 s**.
- Both runners use the same shared oracle. Each runner constructs real on-disk SQLite fixtures. The process durations are uncontrolled one-run measurements and are NOT a valid benchmark.
- The proptest log notes `FileFailurePersistence::SourceParallel set, but failed to find lib.rs or main.rs`; this is a failure-persistence configuration caveat, not a failed test. No failing example was generated, so shrink quality was **not** assessed in this run.

## Additional existing CI result (keep separate)

- ASES repository's existing `Resource control verification` workflow also ran on this PR; runs https://github.com/rock-solid-sites/ASES/actions/runs/44434229752 and https://github.com/rock-solid-sites/ASES/actions/runs/44434201535 each completed compilation and tests but **failed Clippy** with `-D warnings`. Reported errors include `clippy::derivable_impls` in `src/local.rs` and `clippy::type_complexity` in `src/lib.rs`. Both production files were **unchanged in this experimental PR**. The failures are not evidence that the property test assertions failed, and the PR should not be called all-green.
- Whether the upstream base already exhibits those warnings under the same Rust toolchain needs a separate pinned baseline run before labeling them pre-existing. The experiment intentionally did not change unrelated code.

## What the evidence does not establish

- No process launch, real provider billing, remote execution, crash/power failure, concurrent reservation race or end-to-end Work Unit guarantee was exercised.
- Generated histories intentionally restrict to one entitlement and sequential distinct IDs; some invariants were covered by the existing deterministic regression tests rather than new generated cases.
- A test pass does not imply a better shrinker. No faults were detected; there are no observed counterexamples to compare. Generator seeds are not currently pinned in both runners; a reproduced test invocation need not generate identical inputs.
- The two frameworks share an oracle, so correlated specification/model errors are possible.
- Kernel-0 semantics are not inferred from this resource-control prototype.

## Process feedback

- Reusing existing test setup and public interfaces worked; two runners used exactly one real implementation and one simple oracle.
- Record **separate** statuses for method execution, source baseline regression, Clippy, artifacts, and global PR checks.
- Before performance comparisons, pin generated data seeds, failure persistence paths and lockfile; run repeated trials with controlled caching. Before selecting a framework, test a harder state-history/property with controlled violating cases (without altering production), and inspect shrink results.
- Preserve null results, link sources, and keep method promotion distinct from prototype correctness. ASES process draft should consume this and the HMS pilot without creating a competing ASES skill or mandatory lifecycle.


## Follow-up — cancellation/replay lifecycle extension (2026-11-19 01:16 UTC)

The existing test oracle (not the runtime implementation) was extended at `resource-control/tests/support/resource_properties.rs` to keep admitted plan identities, reopen the actual SQLite store, then cancel each accepted RESERVED plan in reverse order. It checks one terminal event per cancellation, exact-ID cancellation replay with no new event, and restored available allowance/reservation totals after each step. No production code was modified.

- Source/test commit: [2520583cbfbc9d840d9e2ec205f652eba932efec](https://github.com/rock-solid-sites/ASES/commit/2520583cbfbc9d840d9e2ec205f652eba932efec).
- [Focused CI 44435444808](https://github.com/rock-solid-sites/ASES/actions/runs/44435444808) **passed**: proptest 120 bounded histories, 1.78s observed test time; Hegel 120 histories, 1.62s; existing control suite also executed in the same workflow.
- [Full evidence artifact 14489256371](https://github.com/rock-solid-sites/ASES/actions/runs/44435444808/artifacts/14489256371), ZIP SHA-256 `7ed09651b1723ad51466e636a59612114a0c3ed97960ce3492703fc0bb81763a`, 30-day retention.
- Status: **NO_DISCREPANCY** within this extended sequential history fixture; **not** a new proof about concurrent cancellation or user-visible execution termination. The performance ranking remains inconclusive; tests ran under different build caches and generators with different histories.
- Same separate resource-control Clippy failures on unchanged source persist in the repository-wide verification workflow. These do not invalidate the passed focused tests but prevent claiming an all-green PR.
