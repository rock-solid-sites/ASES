---
title: Astra follow-up — review disposition and remaining work
version: 0.1.1
program: ASES
layer: Research
document_type: Experimental Research Handoff
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-25
---

# Astra follow-up

This is a coordination checkpoint, not a Kernel design decision or an implementation packet.

## Verified state

- **Round 25 evidence record:** [Work Unit authority, native admission and custody evidence](round25/README.md), merged in main commit `eb6c78e230967a7aabc1024dc0f8416188ed26d5`. The cross-family-reviewed decision packet keeps the authority owner unresolved and W5–W6 NOT REPRESENTED. The fixed-head #98 test-only follow-up was independently accepted for its narrow gate-time result (head `2358354c86a2b15e6ddbe81480d4c783a46e5a56`); it does not establish generalized seal denial or W5/W6. A7 (#35/#36) was not rerun, and #98 remains draft. The #85 custody preflight remains blocked on the exact image; the original DeepSeek #84 Step Summary report remains unretrieved.

- [PR #84](https://github.com/rock-solid-sites/ASES/pull/84), head `bfabf1d95a1f51052679ff4855a2ccc147b97584`, base `e91fb4b14875487dee9c19cc764e72655ba534c0`: A1–A7 and parent regressions passed independent operational replay and [hosted CI](https://github.com/rock-solid-sites/ASES/actions/runs/45326641417). [Evidence preserved in B2](https://github.com/rock-solid-sites/ASES/pull/84#issuecomment-7148415116).
- MiMo [raw report](https://github.com/rock-solid-sites/ASES/pull/84#issuecomment-7142524796) and [coordinator source triage](https://github.com/rock-solid-sites/ASES/pull/84#issuecomment-7148494828): no confirmed #84 regression; duplicate eventless A is existing unresolved reservation, not a fresh-ID denial. Remaining tests concern real exception reachability, coverage of same-A eventless retry, and simultaneous lifecycle/admission ordering.
- DeepSeek [run summary](https://github.com/rock-solid-sites/ases-plugins/actions/runs/45408696041): delivered, full report not retrieved by coordinator; findings NOT TRIAGED. Keep #84 assurance gate open. Do not repeat just to recover the existing report.
- [PR #83](https://github.com/rock-solid-sites/ASES/pull/83), head `8de559c78272bf639a82d284572e218a14cc1269`: W1–W4 prior evidence checked (not rerun); W5–W6 NOT REPRESENTED. [Owner-identity decision evidence](https://github.com/rock-solid-sites/ASES/pull/83#issuecomment-7122210041).
- [PR #85](https://github.com/rock-solid-sites/ASES/pull/85), head `7cb443821659ad7606b906ba601952afde028d66`: syntax checked, runtime blocked on exact #38 image; no equivalent custody test established.
- [Reviewer working recipe](https://github.com/rock-solid-sites/ases-plugins/blob/d4d4ba5462a97950fa7b34082054372675759081/docs/INDEPENDENT-REVIEWER-WORKING-RECIPE.md): connector-readable job log report, byte/hash verification, durable PR comment; summary secondary. [ASES B2 helper](https://github.com/rock-solid-sites/ASES/blob/cb6f37fd10ddb3d93937996627deb84dddf24873/.github/scripts/archive-artifact-b2.sh) is tested on actual evidence. Bulk artifact migration deferred; billing caps not independently verified.

## Next autonomous round

Parent orchestrates only; delegate all inspection, experiments, engineering and record updates to isolated workers. Run separable work units in parallel.

**Worker routing (operator direction, 2026-11-25):** Make OpenCode agents the default execution pool for research, code inspection, test design, implementation, debugging and independent verification; actively use the remaining OpenCode Go subscription allowance and verified zero-price OpenCode models. As coordinator, establish exact approved model IDs, available execution hosts, current eligibility and bounded allocations before dispatch using `agent-launch` v1.0.7. Prior Go DeepSeek/MiMo success is route evidence, not a current quota/availability measurement. Prefer the latest supported harness with verified working routes; parallelize independent bounded tasks, not indiscriminate invocations. Use Codex Luna through its subscription only for work where it adds distinct value or required capability; preserve independent family separation and the orchestrator-only role. No automatic fallback, unapproved metered spending or model selection by task recipients. Record actual routes and failures; continue other independent work if a route is blocked. No requirement to exhaust every available quota.

1. Native admission: apply coordinator triage on #84. Verify prior same-A raw evidence, extend maintained replay only where a meaningful gap exists, test concrete reachable post-reservation failure and concurrent admission/lifecycle ordering if justified. Do not change deliberate eventless uncertainty or widen exception handling without falsifying evidence. Pin base/head; separate inherited limitations from regressions. Existing behavior must remain intact.
2. Work Unit adequacy: produce a small decision packet for the operator, not a positive implementation. Identify the authority-owner home for durable Work Unit/Attachment Point/current Execution eligibility and the trusted path by which the owner verifies execution identity. Evaluate existing native owner and Rust custody seam without equating job/launch IDs, content epoch, physical sink binding or F4 authority with continuity. Specify W5/W6 histories and minimal unresolved design choices. W5: same W/P, X replaced by Y, stale X denied and historical results retained. W6: concurrent X mutation/replacement serializes with owner authority, with Y eligible afterward. Workers request-only. No self-asserted epoch or execution identity.
3. Custody: one bounded preflight for exact #38 image `sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335` and required UID-separated environment. If available run #85; if unavailable retain blocker, do not pull/build/substitute or use same UID as evidence. Sequential two-worker test is not concurrent fencing proof.

Use existing pinned packets and source, current compact-prompt v1.2.0, workflow-orchestration v1.0.4 and Task-Scoped Information and Handoff Method v1.1.2 (read 2026-11-25 via public raw main; moving URLs, exact skill commit not verified). Apply compile-build plus canonical bounded-build methodology only before substantial bounded implementations. No unreviewed production activation/merge. Preserve useful experimental results on main in classified research locations; isolated branches are disposable only after durable checkpoint verified. Push development-agent checkpoints at roughly five minutes/meaningful transitions. Update Work Notes WNASES-4/WNASES-6 and Projektor ASES-8 with exact source, run, evidence, outcome, remaining blocker. Use no unapproved provider spending/fallback; coordinator owns launch routing. This record is a preparation for operator dispatch, not a launched run.
