---
title: Kernel-0 / Work Unit adequacy — bounded evidence packet
version: 0.1.1
program: ASES
layer: Research
document_type: Evidence and Test Packet
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-23
---

# Kernel-0 / Work Unit — bounded adequacy test packet

**Operation:** bounded source crosswalk and falsifying local tests; **not yet** a frozen implementation. **Human owner:** Projektor ASES-8; related native/engine work WNASES-4. **Inputs:** canonical requirements `docs/research/kernel-0/Kernel-0-Evidence-Packet.md` on ASES main `a02df749b4b3da88d3f88c1712623cec6ad5d963`; experimental native Rust `resource-control` at [PR #42](https://github.com/rock-solid-sites/ASES/pull/42), head `27bcc552cecb8bbb456b9db3a0a77da1513b31ab` (stacked on #41/#40/#39). Source baseline and associated reports inspected; new runtime cases below **not executed** in this preparation pass.

## Correct question and invariant boundary

The settled consumer relationship is **Work Unit → Attachment Point → Execution**.

A Work Unit is durable independent of any executor; an Attachment Point is a durable executor-facing continuity position; an Execution is disposable and replaceable. Superseded Executions cannot mutate current authoritative state; executor loss does not destroy work; replacement is continuation of the same Work Unit. Authority is external to the executor. Single/sequential/concurrent executors and shared/isolated/hybrid arrangements are configurations, not separate Kernel modes.

**Do not assume** these three are intrinsic Kernel-0 objects, or that Rust `job_id` already equals Work Unit, `launch_id` equals Attachment Point, or a local child equals an authorized Execution. The requirement is the externally observable guarantee, not a preferred representation. Kernel-0's primitive vocabulary, transition relation, persistence implementation, and realization language remain open in the canonical evidence packet.

## Exact implementation facts already supported

| Existing experimental mechanism | What source supports | What it does NOT establish |
| --- | --- | --- |
| `resource-control/src/lib.rs` `Proposal.job_id`, `Store` jobs/events and `resume_view(job_id)` | SQLite-retained job identity, bounded evidence pointers, interpretable job state; current process liveness intentionally `unknown` in a read-only projection | Durable Work Unit semantics, attachment continuity, or work-product persistence |
| `Store.begin_launch(job,launch_id,...)` (approximately lines 773–808) | SQLite `BEGIN IMMEDIATE`, one dispatch grant from AUTHORIZED, same launch ID replays observation, different ID refused in LAUNCHING/RUNNING; no blind second dispatch | Permission to replace an Execution for the same continuing work; it currently **refuses** a second launch identity under active intent |
| `LocalSupervisor.children` and `LocalSupervisor.resume` in `resource-control/src/local.rs` | In-memory custody of exact child + launch; lost custody yields `unknown` and does not adopt an arbitrary PID | Persistent Attachment Point granting/revoking a replacement execution |
| `LaunchExitObservation`, `observe_launch_exit`, `finalize` | Exact started process/launch-bound exit observation is required before intent-backed capacity release | Executor fencing / invariant-preserving replacement when work is still active |
| `resource-session`, `resource-gateway` and tests `native_local_cold`, `resume_view`, `native_unlaunched_cancel` | Fixed local Unix gateway/role boundary, observable cold history, exact denial and idempotent unlaunched cancellation | General hostile-host exclusion, distributed execution, arbitrary provider outcomes or complete Kernel/Work Unit adequacy |

The native F3/F4 owner branch PR #43 is **another experimental stack**, not already integrated with Rust `resource-control`. Neither stack's passing tests prove end-to-end Work Unit replacement authority.

## Cheapest source-to-requirement crosswalk (deliverable 1)

Against the two pinned source references, classify each requirement as **demonstrated in actual tests**, **represented but untested**, **not represented**, or **unknown because source/evidence is insufficient**. For every classification cite exact file/function/commit and the shortest evidence/test path. Distinguish:

- stable work identity versus durable *job* identity;
- durable attachment position versus launch intent/receipt;
- temporary execution identity versus a process PID;
- who issues, revokes and checks execution authority;
- stale executor write/append/management exclusion;
- continuation after losing the original process/controller;
- unknown outcome retained without duplicate dispatch;
- identity-preserving replacement after an old execution becomes ineligible;
- ability to express single/sequential/concurrent cases under the same authority model;
- trusted host, Store, worker, gateway and observer assumptions.

Do not search the entire historical conversation archive unless a particular requirement remains ambiguous. Existing canonical evidence and current code come first.

## Evidence-first bounded falsifiers (deliverable 2)

**Do not spend a worker round rerunning existing, source-pinned W1–W4 tests by default.** The experimental PR #42 stack already includes direct histories for those distinctions. First cite the precise checked source/test and prior raw evidence. Re-run a focused existing test only when its prior evidence is incomplete, the source changed or an actual interface dependency makes a new result necessary. Use only fixed-worker disposable fixtures and existing source APIs; capture precise commands/exit codes and event/state/balance readbacks for anything new.

Existing checks at pinned PR #42:

- **W1:** `resource-control/tests/control.rs`: `launch_intent_is_one_use_durable_and_observations_are_idempotent`, `independent_begin_launch_contenders_receive_one_dispatch_capability`; `resource-control/src/lib.rs::Store.begin_launch`.
- **W2–W3:** `resource-control/tests/native_local_cold.rs`: `actual_gateway_loss_preserves_unknown_and_capacity` and its `cold_finalize_after_hot_exit` helper; `resource-control/src/local.rs::LocalSupervisor.resume`; `resource-control/tests/resume_view.rs` checks read-only interpretation.
- **W4:** `resource-control/tests/native_unlaunched_cancel.rs`: `preflight_failure_cancel_replay_and_later_launch_denial`, `actual_client_loses_committed_cancel_reply_then_exact_retry_replays`, `reserved_unlaunched_job_can_be_canceled_and_replayed`, and `launched_live_exited_and_closed_jobs_refuse_unlaunched_cancel_unchanged`; historical PR #42 report records 78 selected tests passing, **not** a fresh test in this packet.

These prove only their specific local/ledger claims, not Work Unit replacement or fencing.

| ID | History | What counts as evidence |
| --- | --- | --- |
| W1 | AUTHORIZED job starts one genuine native launch; call `begin_launch` again with same ID and a different launch ID | Same ID observes rather than dispatches. Different ID cannot obtain a second dispatch grant or a new intent while original active; retained job remains intact |
| W2 | Real local gateway/Child custody disappears while an owned worker may still run; reopen Store and inspect resume | Liveness remains `unknown`; no unjustified PID adoption, capacity release, automatic relaunch or fabricated exit |
| W3 | Genuine started-process and matching exit evidence recorded; interrupted/restarted gateway then exact finalization | Finalization remains possible only against matching retained evidence. Mismatch/missing exit leaves capacity held; no inferred completion |
| W4 | AUTHORIZED or RESERVED job with no launch history follows atomic `cancel-unlaunched`; replay and attempt later launch | One terminal cancellation, exact replay and no new dispatch; already launched job refuses this route |
| W5 | Attempt **same Work Unit W, same Attachment Point P, Execution X superseded by Y**: an authority change invalidates X; Y may act on continuing W/P; historical X evidence remains readable | Require a demonstrated authoritative check that accepts Y while denying *all* new X mutations after the supersession decision. If APIs cannot express it, report **NOT REPRESENTED**, not a passing test. A new job ID, an untrusted execution-supplied epoch, a process kill, or a read-only resume view alone cannot prove replacement authority |
| W6 | X attempts a mutation concurrently with the authoritative X→Y supersession; Y attempts a mutation afterward | Define two allowed serializations: (1) X mutation commits *before* supersession and then X loses authority, or (2) supersession commits first and X is refused without mutation. Y may act only after obtaining current authority. Show atomic ordering from the owner, not from transcript timestamps. Run only if a genuine authority seam exists; otherwise report missing atomic check |

A red result in W5/W6 is valuable evidence; this is an **adequacy test**, not a requirement to retrofit replacement semantics inside the local resource ledger.

## Required interpretation and next decision

Produce a small crosswalk and **evidence pointers** for already-covered W1–W4, with selective new raw proof only when necessary. For W5/W6 either show a genuinely existing native authority transition and run a bounded case, or identify the **smallest missing state distinction and atomic authorization check** needed to enforce the requirement. Do not select new Kernel primitives, a language, store, event bus, identity registry or distributed protocol by preference.

Consider at least these competing interpretations without silently choosing one:

1. `resource-control` is only a cost/launch custody component; Work Unit authority belongs in a different existing or proposed owner.
2. An already present authoritative owner can expose just the minimal attachment/execution eligibility transition.
3. There is a genuinely missing Kernel-0 semantic distinction; raise it as a falsifiable decision and state which required property fails without it.

The expected result is **a justified next minimal vertical test**, not a blanket recommendation to merge independent prototypes. If source inspection establishes sufficient semantics, compile a separate bounded Implementation Packet using the current build method before coding; do not mislabel this exploratory evidence packet as a frozen build.

## Completion and restrictions

Stop when the crosswalk and verified W1–W4 evidence references (or precise gaps) exist, W5/W6 are shown with evidence or classified **NOT REPRESENTED/UNRESOLVED** with a discriminating next test, and a concise `PASS / FAIL / UNKNOWN / WHAT-NOT-TESTED` handoff is committed.

Work on a fresh isolated branch of the relevant **PR #42 pinned source** when runtime tests or additional evidence are needed. Preserve existing stacked PRs and evidence; no main merge, deployment, authority redesign or provider operation. Follow the project's documented fixed-worker cleanups.

**Worker residual prompt:** “Evaluate the Work Unit adequacy packet at this path against the pinned Kernel-0 evidence and Rust PR #42 head. Run only the specified discriminating local checks, distinguish implemented safeguards from actual Work Unit replacement authority, and commit the crosswalk/evidence. Return source revision, result per W1–W6 and the smallest remaining decision.”

## Source/authority receipt

Read/applied: current `skills/current/compact-prompt/SKILL.md` v1.1.1; `docs/methodology/ASES Task-Scoped Information and Handoff Method.md`; relevant source in `resource-control`; current Kernel-0 evidence. The `compile-build` skill and canonical bounded-build methodology were read **for the separate native implementation packet**, but this packet explicitly remains **bounded reconnaissance/adequacy**, not a frozen implementation. PR #42's reported tests are historical source evidence; fresh independent reruns have not occurred. An existing job is not presumed to be a Work Unit.
