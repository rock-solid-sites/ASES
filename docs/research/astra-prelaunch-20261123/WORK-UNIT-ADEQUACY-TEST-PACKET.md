---
title: Kernel-0 / Work Unit adequacy — bounded evidence packet
version: 0.1.0
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

## Bounded local falsifiers (deliverable 2)

Use only existing fixed-worker, disposable test fixtures and existing source APIs. Prefer existing regression targets before creating a new harness. Capture exact source pin, commands/exit codes and event/state/balance readbacks.

| ID | History | What counts as evidence |
| --- | --- | --- |
| W1 | AUTHORIZED job starts one genuine native launch; call `begin_launch` again with same ID and a different launch ID | Same ID observes rather than dispatches. Different ID cannot obtain a second dispatch grant or a new intent while original active; retained job remains intact |
| W2 | Real local gateway/Child custody disappears while an owned worker may still run; reopen Store and inspect resume | Liveness remains `unknown`; no unjustified PID adoption, capacity release, automatic relaunch or fabricated exit |
| W3 | Genuine started-process and matching exit evidence recorded; interrupted/restarted gateway then exact finalization | Finalization remains possible only against matching retained evidence. Mismatch/missing exit leaves capacity held; no inferred completion |
| W4 | AUTHORIZED or RESERVED job with no launch history follows atomic `cancel-unlaunched`; replay and attempt later launch | One terminal cancellation, exact replay and no new dispatch; already launched job refuses this route |
| W5 | Attempt to model **same Work Unit, same Attachment Point, Execution X replaced by Y** with authoritative exclusion of stale X | If existing public mechanisms cannot express both *authorized Y* and *denied stale X* while preserving the same work, report **NOT REPRESENTED**, not a passing replacement test. Never fake it by treating a new job as continuation or by killing X and assuming stale authority is revoked |
| W6 | Two would-be executors race a mutation/authorization around a replacement boundary | Specify the expected permitted ordering and stale refusal. Run only if an actual relevant authority seam exists; otherwise document the minimal missing atomic check as an architectural decision |

A red result in W5/W6 is valuable evidence; this is an **adequacy test**, not a requirement to retrofit replacement semantics inside the local resource ledger.

## Required interpretation and next decision

Produce a small crosswalk plus raw proof/negative evidence for W1–W4. For W5/W6 either show a genuinely existing native authority transition and run a bounded case, or identify the **smallest missing state distinction and atomic authorization check** needed to enforce the requirement. Do not select new Kernel primitives, a language, store, event bus, identity registry or distributed protocol by preference.

Consider at least these competing interpretations without silently choosing one:

1. `resource-control` is only a cost/launch custody component; Work Unit authority belongs in a different existing or proposed owner.
2. An already present authoritative owner can expose just the minimal attachment/execution eligibility transition.
3. There is a genuinely missing Kernel-0 semantic distinction; raise it as a falsifiable decision and state which required property fails without it.

The expected result is **a justified next minimal vertical test**, not a blanket recommendation to merge independent prototypes. If source inspection establishes sufficient semantics, compile a separate bounded Implementation Packet using the current build method before coding; do not mislabel this exploratory evidence packet as a frozen build.

## Completion and restrictions

Stop when the crosswalk and W1–W4 test records (or explicit environment/test blockers) exist, W5/W6 are shown with evidence or classified **NOT REPRESENTED/UNRESOLVED** with a discriminating next test, and a concise `PASS / FAIL / UNKNOWN / WHAT-NOT-TESTED` handoff is committed.

Work on a fresh isolated branch of the relevant **PR #42 pinned source** when runtime tests or additional evidence are needed. Preserve existing stacked PRs and evidence; no main merge, deployment, authority redesign or provider operation. Follow the project's documented fixed-worker cleanups.

**Worker residual prompt:** “Evaluate the Work Unit adequacy packet at this path against the pinned Kernel-0 evidence and Rust PR #42 head. Run only the specified discriminating local checks, distinguish implemented safeguards from actual Work Unit replacement authority, and commit the crosswalk/evidence. Return source revision, result per W1–W6 and the smallest remaining decision.”

## Source/authority receipt

Read/applied: current `skills/current/compact-prompt/SKILL.md` v1.1.1; `docs/methodology/ASES Task-Scoped Information and Handoff Method.md`; relevant source in `resource-control`; current Kernel-0 evidence. The `compile-build` skill and canonical bounded-build methodology were read **for the separate native implementation packet**, but this packet explicitly remains **bounded reconnaissance/adequacy**, not a frozen implementation. PR #42's reported tests are historical source evidence; fresh independent reruns have not occurred. An existing job is not presumed to be a Work Unit.
