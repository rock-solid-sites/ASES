---
title: Kernel-0 / Work Unit adequacy result — 2026-11-24
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-24
---

# Kernel-0 / Work Unit adequacy result

**Scope:** source crosswalk and bounded evaluation of W1–W6 from the task packet at PR #77 head `38a61d2c28c68bb6bc43c3d0d42d2b76a575a50f`. Canonical requirement pin: Kernel-0 evidence packet at `a02df749b4b3da88d3f88c1712623cec6ad5d963`. Rust source pin: PR #42 head `27bcc552cecb8bbb456b9db3a0a77da1513b31ab`, checked out unchanged for this evaluation. This report does not claim a fresh test run.

## Result

| Case | Result | Claim supported by pinned source / prior evidence | Limit |
|---|---|---|---|
| W1 | **PASS, bounded ledger claim** | `Store::begin_launch` serializes AUTHORIZED→LAUNCHING in an SQLite immediate transaction. `launch_intent_is_one_use_durable_and_observations_are_idempotent` checks first dispatch, same-ID observation replay, different-ID conflict and retained reservation; `independent_begin_launch_contenders_receive_one_dispatch_capability` yields one grant among independent contenders (`resource-control/tests/control.rs:278,366`). | One-use job launch intent is not Work Unit replacement authority. No identity-preserving replacement is available. |
| W2 | **PASS, bounded custody claim** | `actual_gateway_loss_preserves_unknown_and_capacity` creates a real worker, kills its gateway, then cold reopens the ledger. Resume reports unknown; no arbitrary PID adoption, relaunch, exit fabrication or capacity release (`resource-control/tests/native_local_cold.rs:265`; prior raw history `docs/research/phase-ii-local-execution/evidence/cold/cold-history.json`). | This demonstrates conservative local process custody, not durable Attachment Point continuity or executor replacement. |
| W3 | **PASS, bounded exit/finalization claim** | `cold_finalize_after_hot_exit` and native termination histories require exact started-process exit observation, retain capacity until explicit finalization, and refuse mismatch/missing evidence (`resource-control/tests/native_local_cold.rs:178,363`; `resource-control/tests/native_termination.rs:263,426`; raw integrated histories under `docs/research/phase-i-termination-evidence/evidence/integrated-01/`; summary `docs/research/phase-i-termination-evidence/REPORT.md`). | No X→Y authority transition or stale-X fencing is exercised. Trusted adapter truth remains an assumption. |
| W4 | **PASS, bounded unlaunched-cancel claim** | Native cancellation histories cover atomic cancel/replay after preflight failure, committed-cancel reply loss with exact retry, reserved cancellation and refusal for launched/live/exited/closed jobs (`resource-control/tests/native_unlaunched_cancel.rs:319,383,444,471`; prior pass logs `docs/research/phase-ii-native-unlaunched-cancel/evidence/cargo-native-regressions-pass1.txt` and `...pass2.txt`). | Cancellation is not replacement. A terminal cancelled job cannot continue as the same Work Unit through a replacement Execution. |
| W5 | **NOT REPRESENTED** | The Store's durable key is `job_id`; its single `launch_id` is a dispatch-intent selector and exact replay key. No durable Attachment Point identity, current-Execution eligibility state, revocation transition, or authority check accepting Y while rejecting X exists in this stack. `LocalSupervisor.children` is in-memory custody; `resume_view` is read-only and cannot authorize a mutation. | No meaningful W5 runtime test can be expressed through existing APIs. A second job would be new work, and a second launch ID on one active job is refused. |
| W6 | **NOT REPRESENTED** | Mutations use per-operation SQLite transactions, but there is no authoritative X→Y supersession operation to serialize against X or Y mutations. Atomic `begin_launch` only grants the first launch intent for one job; it cannot stand in for an execution-eligibility check. | The required race has no valid authority seam. A synthetic epoch supplied by an execution, process kill, or transcript ordering would not establish authority. |

## Crosswalk and smallest next decision

The canonical requirement is durable work independent of executors, durable continuity at an Attachment Point, replaceable temporary Executions, and exclusion of stale Executions from current authoritative mutation. `resource-control` is presently a resource admission and local launch/custody ledger. Its `job_id` and `launch_id` do not implement those architecture identities. Existing checks establish useful local safety properties but do not show Work Unit adequacy.

Current evidence best fits interpretation 1 in the packet: `resource-control` is a cost/launch custody component; Work Unit authority must be owned elsewhere or remain an explicit future design boundary. Do not retrofit replacement semantics into this ledger based on the evidence here. No implementation experiment was justified because there is no current authoritative supersession transition to exercise.

Smallest missing distinction for a future vertical test: an authority owner must distinguish the continuing work/attachment from the currently eligible execution and atomically decide whether each attempted mutation is authorized against current eligibility. The discriminating test should exercise X mutation concurrent with X→Y supersession and establish either (a) X commits before supersession and is then ineligible, or (b) supersession commits first and X is refused without mutation; Y may mutate only after current authority grants it. The owner and interface for this transition remain a decision; no new Kernel primitive or storage design is selected here.

## Verification and provenance

- **Source inspection:** `27bcc552cecb8bbb456b9db3a0a77da1513b31ab`; no Rust files modified.
- **W1–W4:** cited source tests and historical captured runs only; no reruns in this task.
- **W5–W6:** source/API inspection; no tests added or run because the needed authority transition is absent.
- **WHAT-NOT-TESTED:** no end-to-end Work Unit runtime, attachment persistence, X→Y replacement, stale-execution write fencing, multi-host authority, hostile host, or independent verification. Rust PR #42 and native PR #43 are separate experimental stacks; integration is not established.
- **Current task method:** read and applied `ASES Task-Scoped Information and Handoff Method` v1.0.0 from canonical pin `a02df749b4b3da88d3f88c1712623cec6ad5d963`; current `compact-prompt` skill from that pin. Canonical Kernel-0 evidence and experimental packet were treated as distinct authority levels.
