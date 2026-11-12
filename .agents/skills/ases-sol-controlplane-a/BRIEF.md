# Current engineering queue — delegated reconnaissance required

**Run:** ASES-SOL-CTRL-A-20261113. **Repo:** `rock-solid-sites/ASES`. **Work Notes:** `ASES-4` is the inherited engineering thread; earlier `ASES-2` contains the baseline. This page is a **source index**, not an instruction to trust stale PR summaries.

## First worker job: state reconnaissance

One Luna agent must inspect latest GitHub PRs and Work Notes to determine which promises are demonstrated and what is still unfinished. It should return an ordered, tiny decision packet with exact current source SHA, material counterexamples and one recommended next experiment. Parent does not fetch the repository itself.

Starting evidence as of 2026-11-13:
- [#30 native ownership](https://github.com/rock-solid-sites/ASES/pull/30): actual F1→F3 selected registration, L6 material, F4 current effect admission and bounded lifecycle.
- [#35](https://github.com/rock-solid-sites/ASES/pull/35) / [#36](https://github.com/rock-solid-sites/ASES/pull/36): exact witness reconciliation and post-journal-fsync missing local owner observation.
- [#38](https://github.com/rock-solid-sites/ASES/pull/38): restricted owner-only recovery through the UID-separated native route.
- [#43 unresolved reservation admission](https://github.com/rock-solid-sites/ASES/pull/43): **in progress at last check**. First reproduce whether an interrupted pre-append reservation permits subsequent new IDs, then decide a minimal conservative admission bound if demonstrated. Do not turn a hypothesized defect into a claim before a red baseline.
- [#29](https://github.com/rock-solid-sites/ASES/pull/29), [#31](https://github.com/rock-solid-sites/ASES/pull/31)–[#33](https://github.com/rock-solid-sites/ASES/pull/33), [#39](https://github.com/rock-solid-sites/ASES/pull/39)–[#42](https://github.com/rock-solid-sites/ASES/pull/42): Rust durable launch, exact exit, local execution API, cancellation and recovery.
- CI discrepancy on #42: [failing runner](https://github.com/rock-solid-sites/ASES/actions/runs/43293464260/job/131445439283) observed `exit_observed` when a test expected `running`; **separate OpenCode assignment ASES-6**, not Sol work. Do not assert it is merely flaky.

## Priorities after current state check

1. Resolve the highest-value actual native admission/ownership problem, currently #43's pending-effect/reservation accumulation hypothesis.
2. Converge native acceptance, local outcome observation, publication reconciliation and UID-separated custody into a single defensible owner-controlled path. No new universal registry without an unavoidable concrete counterexample.
3. Converge execution-engine local launch/stop/finalize with recorded unknown outcomes and session recovery without false liveness; use existing source.
4. When these are complete or independently blocked, select the next most consequential existing ASES engine gap from actual results. Continue until the session's usage resource is exhausted, not until one PR is green.

Separate inexpensive OpenCode issues: ASES-5 PR dependency matrix, ASES-6 independent CI/replay, ASES-7 evidence-recovery audit. Parent must not duplicate them. No production action or merge.

Never start by sending the parent the entire runbook, source tree or previous transcripts. A compact source-pinned *delta* from current state is enough.
