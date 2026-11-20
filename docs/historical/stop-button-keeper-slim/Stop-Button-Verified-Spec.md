---
title: Stop-Button Verified Spec — State-Gated Execution
program: Tooling
layer: Architecture
document_type: Verified Spec
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 510

depends_on:
  - Concept: Levels of Abstraction
  - Documentation Standard
  - Execution Engine Vision
  - Methodology to Requirements Mapping Specification
  - AI Orchestration Guide
  - to-file/VSDD.md

consumed_by:
  - fork/opencode-src/packages/tui/src/component/prompt/index.tsx
  - fork/opencode-src/packages/core/src/session/run-coordinator.ts
  - fork/opencode-src/packages/core/src/session/execution.ts
  - fork/opencode-src/packages/server/src/handlers/session.ts
  - scripts/probe-stop-button-phase0.sh
  - fork/opencode-src/packages/core/test/session-run-coordinator.test.ts

related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/research/registry/Failure-Matrix.md
  - research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md
  - docs/research/retrospectives/topics/EDASES-topic-UI-design.md
  - findings/vsdd-archaeology-report.md

implements:
  - Execution Engine Vision Mechanical Enforcement
  - Methodology to Requirements Mapping State Management
  - ASES State-Gated Execution

implemented_by:
  - fork/opencode-src/packages/tui/src/component/prompt/index.tsx
  - fork/opencode-src/packages/core/src/session/run-coordinator.ts

supersedes: []
superseded_by: []
last_updated: 2026-08-29
---

# Stop-Button Verified Spec — State-Gated Execution

> **VSDD Phase 1 Spec Crystallization** (Step 1a Behavioral Specification + Step 1b Verification Architecture + Step 1c Spec Review Gate) for Crosslink #510.
>
> **Scope:** The Tiny V2 Stop-button as a **state-gated execution** primitive: toggle `Send ↔ ■ Stop` right of prompt + confirm `Yes/No` → authoritative `ctx.session.interrupt(sessionID)` / `POST /api/session/:id/interrupt` per VSDD phases 1a-1c and Execution Engine hypotheses H1-H4.
>
> **Source fidelity:** This spec does not invent methodology. It operationalizes the Execution Engine Vision's "preventing invalid state transitions / identifying orphaned reasoning" and the Methodology-to-Requirements Mapping's "State transitions should only occur when permitted" for one concrete artefact: the **session execution lifecycle** owned by `SessionRunCoordinator` + `SessionExecution` + `Runner`.

---

## 1. Purpose, Authority, and Reasoning Certainty

### 1.1 What this spec is

This is the **Verified Spec** for the stop-button feature on branch `feature/stop-button` (issue #510). It is the single source of truth for:

* the 4-state lifecycle: `idle` · `running` · `confirming` · `interrupting`;
* the permitted transitions and the gates on each transition;
* the invariants that separate an authoritative fence from a placebo 204;
* the purity boundary that makes the lifecycle provable;
* the exhaustive edge catalog that every implementation and test must satisfy.

### 1.2 Why state-gated (WHY)

WHY: The prior `session.interrupt → Esc` path returned "accepted" but left the `SessionRunCoordinator` fiber, the LLM stream, the bash/tool child, and the 401/429 parked-retry loop alive. The TUI showed `idle/stopped` while the server kept running — a **placebo worse than no button** because the operator trusts the UI and abandons a live fiber that orphans, wastes budget, and collides with the next prompt (Failure-Matrix row "Uncancellable / placebo interrupt", confidence High, 2026-08-27). Mechanical enforcement via an explicit state machine is the corrective: the button is only enabled in `running`, the fence is only invoked from a state that owns a fiber, and idle interrupt is a typed no-op.

### 1.3 Basis (WHAT)

WHAT: Evidence →

* Code-inspection (cheapest test, run before UI wiring): `packages/server/src/handlers/session.ts:366` `session.interrupt(sessionID)` → `SessionExecution.interrupt` → `SessionRunCoordinator.interrupt(key)` → `Fiber.interrupt(entry.owner)` (run-coordinator.ts:94-101) fences the process-local ownership chain. `Runner.cancel` does `Fiber.interrupt + Deferred.fail` on in-flight tool/retry promises. Idle/missing is `Effect.void` (204 no-op). Parked retries live inside the same fenced fiber.
* Unit fence proof: `fork/opencode-src/packages/core/test/session-run-coordinator.test.ts` — 18/18 pass including two #510 placebo tests ("kills a running tool child fiber when interrupted", "does not leave the tool child running after interrupt (no orphan)"); regression guard by neutering `Fiber.interrupt` → both fail as expected.
* Live discriminating test: `scripts/probe-stop-button-phase0.sh` 9-point probe (idle 204/no-op, stream killed→idle, tool `sleep 42` killed, new prompt 200, 401/429 cleared, no orphan after UI restart, plus concurrency idempotence, temporal debounce/reconciliation, transport acceptance vs completion); live run against `opencode :49374` after auth fix: PASS on 2 testable points (idle 204, post-interrupt 200), 4 N/A due to server that spawns no shell-tool children (points 7-9 SKIP when server down).
* TUI state threading: `fork/opencode-src/packages/tui/src/component/prompt/index.tsx:215-298` — `isRunning = status.type !== "idle"`, `isInterrupting` signal, `handleStopClick` with 1s debounce + 800ms cooldown, `Yes/No` dialog, `sdk.client.v2.session.interrupt({sessionID})`, `appendFile("/tmp/stop-button.log")`, `toast`; plus legacy double-Esc path at `:475-504` now migrated to the same `v2.session.interrupt`.

### 1.4 Certainty and Negative Space (HOW CERTAIN / WHAT-NOT-TESTED)

* **HOW CERTAIN:** evidence-based for the fence (code + unit tests prove `Fiber.interrupt` propagates to forkChild tool fibers); evidence-based for idle no-op and post-interrupt admission (live probe PASS); **not proven** by live 9-point for stream/tool/429/orphan on a server that does not spawn shell-tool children — unit tests cover that class at the coordinator seam instead (thin delegation from handler to coordinator is only code-inspected, not handler-integration-tested).

* **WHAT-NOT-TESTED (negative-space disclosure):**

  * Full server handler round-trip `HttpApi session.interrupt → SessionExecution → coordinator.interrupt` is not exercised by the coordinator unit tests; it is a thin delegation proven only by code-inspection of `handlers/session.ts:368`.
  * Full fork `bun typecheck` / `bun test --workspace` (requires `bun install` + `node_modules`) was proven clean on prior phase (`d8cd1535`, `78a02a8b #510`) but is not re-run in this spec-draft pass — only file-presence + `tsc --noEmit` shape.
  * Live stream-kill / tool-kill / 401-429-parked / no-orphan-after-restart remain N/A on the `:49374` server that completes generations in <2s; they require either a server that runs shell-tool children (so `sleep 42` is observable) or an integration harness.
  * Cross-worktree UI manual QA (click `■ Stop` → dialog → `Yes` → `idle` with real streaming model) not re-executed in this session; prior `90458364` TUI was manually inspected and type-checked.

---

## 2. VSDD Phase 1a — Behavioral Specification

### 2a.1 Behavioral Contract

**Governing rule (from Execution Engine Vision § Mechanical Enforcement):** the engine must "prevent invalid state transitions" and "identify orphaned reasoning." For the stop-button, the governed artefact is the **session execution** (`sessionID` key in `SessionRunCoordinator`), not the button pixels. The button is the human-facing gate on that artefact's lifecycle.

#### Preconditions

| # | Precondition | Enforced by |
|---|--------------|-------------|
| P1 | A `sessionID` exists and the TUI holds it in `props.sessionID`. | TUI guard (handleStopClick) + server route param |
| P2 | `sync.data.session_status[sessionID]` is the single source of derived status (`type: "idle"` vs non-idle). | `useSync` subscription (server SSE) |
| P3 | The server process that owns the `SessionRunCoordinator` entry for `sessionID` is the same process that receives `POST /api/session/:id/interrupt`. | Process-local `SessionExecution` constraint (V2 AGENTS.md note) |
| P4 | The drain (`options.drain(key, force)`) owns all work for that session (LLM stream + tool forkChild fibers + parked retry Deferreds) inside `entry.owner`. | `run-coordinator.ts:37-46` ownership |

#### Postconditions

| # | Postcondition | Observable |
|---|---------------|------------|
| Q1 | After `interrupt(key)` settles, `coordinator.active` no longer contains `key` and the owner `Fiber` is done with `Cause.interrupt`. | `Fiber.await` returns interrupted; `active` set empty |
| Q2 | After `interrupting → idle`, the session accepts a new prompt (`200`) and starts a fresh drain. | probe point 4: `POST /api/session/:id/prompt` 200 |
| Q3 | Idle interrupt is `204` no-op with no side effect, no error, no new drain. | probe point 1 |
| Q4 | The TUI reflects exactly `sync.data.session_status`: `isRunning = type !== "idle"`; `Send` ↔ `■ Stop` toggle; `■ Stop` disabled when `idle` or `isInterrupting`. | visual + `isRunning` memo |

#### Invariants (see §5 for full list)

* **Fence:** interrupting must `Fiber.interrupt(entry.owner)` — the whole drain, not just the wrapper — so child tool fibers and parked retries die with it (I1).
* **No placebo:** UI `idle` must imply coordinator `active` empty and no tool child alive (I2).
* **No orphan:** no tool child or retry may survive `Fiber.interrupt` after the fiber settles (I3).
* **State-gating:** `Send` and `interrupt` are only legal in their owning states (I4).
* **Idempotence:** duplicate `interrupt` while `idle` or `interrupting` is a safe no-op (I5).

### 2a.2 Interface Definition

**No new server endpoint.** The spec binds the existing authoritative surface:

| Layer | Interface | Contract | Source |
|-------|-----------|----------|--------|
| **TUI (effectful shell)** | `stopController.handleStopClick()` | Machine-gated flow: `authoritativeState()` → `isPermitted(cur,"STOP_CLICK")` → idle no-op toast / confirming dialog → on `Yes` `requestInterrupt` → `interrupting` until cooldown; debounce 1s at the fence, cooldown 800ms, log `/tmp/stop-button.log`, toast. Extracted from `prompt/index.tsx` into a mountable controller (issue #510 D1) | `prompt/stop-button-controller.ts`, wired at `prompt/index.tsx` |
| **TUI (keyboard)** | `promptCommands: "session.interrupt"` | `Esc Esc` within 5s → `stopController.handleEscapeInterrupt()` (machine-gated `ESC_ESC` + B1 reconciliation → fence). **No `enabled:` gate on the TUI-local status projection** — a lagged "idle" must not deny ESC (issue #510 B1); single `Esc` only increments `store.interrupt` counter | `prompt/index.tsx` command registry |
| **TUI (authoritative probe)** | `GET /api/session/active` via `sdk.client.v2.session.active()` | Coordinator active-map HTTP projection: `{data: {[sessionID]: {type:"running"}}}`. Consulted once when the local projection says `idle` and the user explicitly requests a stop (B1) and once after each 204 (B3 settle check); any non-idle projection skips the probe | `protocol/src/groups/session.ts:146`, `server/src/handlers/session.ts:81-89` |
| **SDK (generated)** | `sdk.client.v2.session.interrupt({sessionID})` | `POST /api/session/{id}/interrupt` → `204` (idle no-op or success) else error; `Session3` on `v2`, not legacy `Session2` | `fork/opencode-src/packages/sdk/js/src/generated/client.ts:5782` `Session3.interrupt`, getter `sdk.gen.ts:7007` |
| **Server handler** | `session.interrupt(sessionID)` in `handlers/session.ts:366-368` | Delegates to `SessionExecution.interrupt(sessionID)`; idle/missing is no-op (204) | `handlers/session.ts:366-368` |
| **Execution seam** | `SessionExecution.interrupt(sessionID)` | Process-local `LocationServiceMap.get(session.location)` only at drain start; interruption targets the active process-local ownership chain for that `sessionID` | V2 Session Core AGENTS.md note |
| **Coordinator fence** | `SessionRunCoordinator.interrupt(key)` | `if (entry?.owner) { entry.stopping=true; entry.pendingWake=false; return Fiber.interrupt(entry.owner) } else Effect.void` | `run-coordinator.ts:94-101` |
| **Status subscription** | `sync.data.session_status[sessionID]` | SSE `SyncMessage` stream → `type: "idle" \| "running" \| "tool-executing" \| ...` — TUI derives `isRunning`; no separate status field on `GET /api/session/:id` (idle inferred from `time.idle`) | `useSync` context |

**Type correctness gate:** `v2.session.interrupt` lives on `Session3` (generated SDK); `sdk.client.session.interrupt` does not exist (`Session2` lacks `interrupt`) — prior `TS2339` fixed at `d8cd1535`.

### 2a.3 Edge Case Catalog (summary — full catalog at §7)

Enumerated per VSDD "explicitly enumerated boundary conditions" (Phase 1a: Behavioral Specification). Each edge lists expected behavior, cheapest discriminating test, and evidence carrier. Summary classes:

* **Idle edges:** idle + Stop click, idle + API interrupt, missing sessionID, idle + double-Esc
* **Running edges:** running + Stop → confirming, running + Esc Esc → interrupting without dialog
* **Confirming edges:** Yes → interrupting, No / Esc / outside-click / auto-dismiss / 5s timeout → running
* **Interrupting edges:** second Stop ignored (debounce/cooldown), wake arriving during interrupt, run arriving during interrupt, failure vs success settle, defect settle
* **Fence edges:** stream kill, tool `sleep 42` kill, local vs hosted tool, blocked tool awaiting settlement, 401/429 parked retry kill, permission-pending, question-dismissed, no orphan after UI kill/restart
* **Concurrency edges:** different keys concurrent, same key join, coalesced wakes, trampolines 20k self-wakes
* **Infrastructure edges:** network error from `interrupt`, auth 401 on interrupt, server down / SKIP path, log write failure

Full exhaustive list: 28 edges at §7.

### 2a.4 Non-Functional Requirements

| # | NFR | Spec | Rationale |
|---|-----|------|-----------|
| NF1 | **Debounce** | `lastInterruptAt` 1s gate + `isInterrupting` 800ms cooldown; `store.interrupt` 5s window for double-Esc. | Prevents accidental double-interrupt storms; protects the 9-point probe from retry races |
| NF2 | **Latency** | State transition `running → confirming` is instant (dialog mount); `confirming → interrupting` is one SDK round-trip (`POST /interrupt`); `interrupting → idle` awaits `Fiber.interrupt` settle (bounded, no polling). | User perceives Stop as immediate; the cheap staleness trigger (§5 Workflow Topology) detects a stuck `interrupting` via position store |
| NF3 | **Feedback** | Every terminal outcome toasts: `Interrupted` (success 204), `No active run` (idle), error text on catch; every decision appends `/tmp/stop-button.log` (timestamp + sessionID + status/error). | Operator gets a durable trace for the Failure-Matrix 9-point probe without instrumenting the server |
| NF4 | **Accessibility** | `Yes` is `theme.error` background, `No` is `backgroundElement`; `esc` hint; both boxes are `onMouseUp` targets; dialog is `dialog.replace` with `onClose → resolve(false)` so `Esc`/outside dismiss = No. | Keyboard-op dispatch must still reach the fence |
| NF5 | **TUI file discipline** | Stop-button shell logic lives in `prompt/stop-button-controller.ts` (machine gate + fence + timing, effects injected); `prompt/index.tsx` keeps only context wiring, dialog JSX and the ESC counter. Supersedes the original single-file constraint from `90458364`: the extraction is what makes the real gate code mountable in tests (issue #510 D1 — the enforcement sites previously had no executable discriminating test). | Reviewer D1 finding 2026-08-30; machine purity boundary (§6) unchanged |

---

## 3. VSDD Phase 1b — Verification Architecture

> "What properties must be mathematically provable, and what architectural constraints does that impose?" — VSDD Phase 1b.
> The answer for stop-button is: the **statechart** and the **fence** must be provable; the network/dialog/toast must be observed.

### 3b.1 Provable Properties Catalog

Which invariants (from §5) are **critical-path and must be proven** vs where test coverage suffices:

| Property | Class | Why provable vs testable | Formal carrier |
|----------|-------|--------------------------|----------------|
| P-PF1 `FenceKillsToolChild` — `Fiber.interrupt(entry.owner)` terminates every `forkChild` tool fiber spawned inside the drain, and the tool's `Exit` is an interruption | **must be proven** (critical path, placebo risk) | Pure `Effect` fiber algebra, no I/O; unit test already proves it deterministically; property-based harness can assert over arbitrary drain shapes | unit test `kills a running tool child fiber when interrupted` + Kani-style harness sketch below |
| P-PF2 `NoOrphan` — after `interrupt` settles, `active` is empty and a fresh `run(key)` starts (no leaked child holds the key) | **must be proven** | Leak-freedom is ownership reasoning; deterministic with `Deferred` barriers | unit test `does not leave tool child running after interrupt (no orphan)` |
| P-PF3 `StateGating` — `interrupt` is only invoked when `status.type !== "idle"` (or is idempotent no-op when idle); `Send` disabled when running; `Stop` disabled when idle/`interrupting` | **must be proven** at the pure transition level | Pure statechart predicate `(state, event) → state` is a total function with no side effects | XState v5 model + `@xstate/test` model-based test |
| P-PF4 `Idempotence` — `interrupt(idle) == 204 no-op`; `interrupt(interrupting)` coalesces (second call ignored until settle) | **must be proven** | `run-coordinator.ts:97` `if (entry?.owner === undefined) Effect.void` + TUI debounce | property test: random sequence of duplicate interrupts yields same terminal state |
| P-PF5 `CoalescedWakes` — wakes received during active execution coalesce to exactly one successor drain | proven via existing `coalesces wakes received during active execution` | runner correctness (not placebo) | existing test (3 concurrent wakes → 2 runs) |
| P-NF1 `Debounce` (1s + 800ms + 5s Esc window) | test coverage sufficient | Timing, shell | unit timer test |
| P-NF2 `Toast/Log` delivery | test coverage sufficient | Effectful shell | probe log inspection |

**Distinction (high confidence):** properties marked "must be proven" are those where a placebo (UI says stopped, server still running) is the Failure-Matrix's "worse than no button" class. They belong in the **pure core** and are reachable by Kani/TS proof harnesses *and* by deterministic `Effect` tests without mocking the universe.

### 3b.2 Purity Boundary Map

The most consequential VSDD 1b decision: where the **deterministic, side-effect-free core** ends and the **effectful shell** begins. This boundary dictates module decomposition, dependency direction, and how verification tools can operate.

```
                              Purity Boundary
  ┌─────────────────────────────────┐         ┌──────────────────────────────┐
  │          Pure Core              │         │      Effectful Shell          │
  │  (verification can reason       │◄────────│  (verification can only       │
  │   without mocking I/O)          │  calls  │   observe via tests/probes)   │
  ├─────────────────────────────────┤         ├──────────────────────────────┤
  │ • StopButtonMachine (XState v5) │         │ • sdk.client.v2.session.      │
  │   states + transitions + guards │         │   interrupt network call      │
  │   (idle/running/confirming/     │         │ • Fiber.interrupt effect      │
  │    interrupting, Fig at §4)     │         │   execution (Effect runtime)  │
  │ • Guard predicates:             │         │ • Server SSE status stream    │
  │   isRunning(status)             │         │ • Dialog mount / onMouseUp    │
  │   isInterrupting flag           │         │ • Toast                       │
  │   shouldDebounce(now)           │         │ • appendFile log              │
  │ • Invariant predicates I1-I8    │         │ • SessionExecution delegation │
  │   (see §5) as pure boolean fns  │         │ • Runner LLM stream + tool    │
  │ • Debounce math (pure time)     │         │   subprocess (scoped child    │
  │ • Transition function:          │         │   process, Deferred.fail)     │
  │   next(State, Event) -> State   │         │ • 401/429 retry Deferred      │
  └─────────────────────────────────┘         └──────────────────────────────┘
                 ▲                                      │
                 │  pure core tests drive              │  shell tests
                 │  the shell should be                │  assert via
                  │  minimal glue                       │  9-point probe
```

**Boundary rationale:**

* The statechart is pure: given `(state, event, guards)` it deterministically produces `nextState` and a declarative effect descriptor (`invokeInterrupt` | `openDialog` | `toast`). No `sdk`, no `appendFile`, no `Fiber` inside the pure function — those are interpreted by the shell.
* This is the same "reversed composition" tension the execution-engine-ui synthesis flagged as High confidence ("lifecycle-ownership: execution engines claim state that EDASES reserves for statecharts"): the fix is explicit — **statechart owns lifecycle**, engine (coordinator/execution/runner) only **schedules** the Fiber. The coordinator's `active` map is the runtime mirror of `State=running|interrupting`; the chart is authoritative for *what may happen*, the engine for *whether the Fiber actually died*.
* Because the pure core has no I/O, a model checker can reason about it without mocking the server, and `@xstate/test` can generate exhaustive paths (every state × every event) without flake.

### 3b.3 Verification Tooling Selection

Chosen **now** (Phase 1), not after coding, because tool constraints are architectural constraints — exactly as VSDD 1b prescribes.

| Tool | Scope | Constraint it imposes | Proven here? |
|------|-------|-----------------------|--------------|
| **tsgo / bun typecheck** (`bun typecheck` in `fork/opencode-src/packages/tui`) | TUI surface + SDK binding | Forces correct `v2.session.interrupt` path (Session3 vs Session2); catches `TS2339` at spec time | Yes — gate on `d8cd1535`; re-run required for any TUI edit |
| **Bun + Effect test** (`session-run-coordinator.test.ts`) | Fence + state gating | Test must be deterministic (no `setTimeout` races); tool expectations: `Deferred` barriers, `Fiber.forkChild`, `Cause.hasInterruptsOnly`; no shell-tool children needed | Yes — 18/18 pass |
| **Bun test — shell controller** (`test/prompt/stop-button-controller.test.ts`) | TUI gate enforcement (D1) + B1 reconciliation + B3 settle check | Mounts the REAL `createStopController` flow with a fake `sdk.client.v2.session.interrupt`; asserts idle→0 calls, running→confirm→No→0 calls, running→confirm→Yes→exactly 1 call, interrupting idempotence, debounce at the fence. Mutation-verified: gate-removal and unconditional-fire mutants fail 4 tests each; B1-denial and settle-removal mutants fail 3 each | Yes — 18/18 pass (2026-08-30) |
| **Live 9-point shell probe** (`scripts/probe-stop-button-phase0.sh`) | End-to-end placebo detection (network + server): 1-6 functional, 7 concurrency, 8 temporal, 9 transport | Server must be running; probe must use `sleep 42` not `sleep 30` (avoids `pgrep -f "sleep 300"` collision with kickoff watchers); probe creates its own session (`PROBE_SESSION`) so it never touches operator sessions | Partial — code path verified; live verdict N/A on no-tool-child server |
| **TUI post-interrupt settle check** (B3, in `stop-button-controller.ts`) | In-UI placebo detection: after a 204, re-reads the active map after the settle window (1.2s); still-active + no new user message → `PLACEBO SUSPECT` log + warning toast | Best-effort by design (server unreachable → logged, never thrown); the live probe remains the end-to-end discriminator; false-positive guard = baseline user-message ID | Yes — controller tests cover suspect / new-prompt / settled / unavailable branches |
| **XState v5** | Pure statechart | Chart definition is executable spec; `@xstate/test` generates all-state/event paths; persistence + inspection per execution-engine-ui synthesis (XState v5 can model independent artefact lifecycles, High confidence) | Chart sketch below; implementation deferred to Phase 2 |
| **Kani (Rust) / property harness (TS)** | Hardening (Phase 5) | Pure transition function + invariant predicates are declared as harnesses (see §3b.4) before coding | Harness sketches below; execution at Phase 5 |
| **Manual probe log + toast** | Human oversight | `/tmp/stop-button.log` is rotated-free append; human checks that `stop-button interrupt success` appears only when coordinator settled | Operational |

**Tool-boundary note:** Kani selection is aspirational — the pure core is TypeScript `next(State,Event)`; the equivalent TS harness is a `proptest`/`fast-check` property that asserts invariants across random event sequences. Either harness satisfies VSDD's "property specifications drafted alongside the behavioral spec" requirement.

### 3b.4 Property Specifications (harnesses drafted alongside this spec)

Per VSDD 1b: the formal property definitions are drafted now, as a second mathematically precise encoding of the requirements, before implementation hardens.

**Harness H1 — `FenceKillsToolChild` (critical):**

```ts
// Pure sketch: for any drain that forks a never-ending tool child,
// interrupting the owner must interrupt the child and empty active.
import { Deferred, Effect, Fiber, Exit, Cause } from "effect"
import { SessionRunCoordinator } from "@opencode-ai/core/session/run-coordinator"
import { expect } from "bun:test"

// Property: forall drains of shape "forkChild(never)", interrupt => child Exit is interrupt-only
forAll(drainShapes, async (shape) => {
  const toolExit = await runCoordinatorWithDrain(shape).then((c) => interruptAndCaptureToolExit(c))
  invariant(Cause.hasInterruptsOnly((toolExit as Exit.Failure).cause))
  invariant((await c.active)().size === 0)
})
```

Concrete existing carrier: the two #510 tests at `fork/opencode-src/packages/core/test/session-run-coordinator.test.ts:248-334` — they are the executable form of this harness.

**Harness H2 — `StateGating` (XState model test):**

```ts
import { createMachine } from "xstate"
import { createModel } from "@xstate/test"

const stopMachine = createMachine({
  id: "stopButton",
  initial: "idle",
  states: {
    idle:       { on: { PROMPT: "running", STOP_CLICK: { actions: "toastNoRun" }, INTERRUPT_API: { actions: "noop204" } } },
    running:    { on: { STOP_CLICK: "confirming", ESC_ESC: "interrupting", DONE: "idle", ERROR: "idle" } },
    confirming: { on: { YES: "interrupting", NO: "running", ESC: "running", DISMISS: "running" } },
    interrupting:{ on: { SETTLED: "idle", STOP_CLICK: { actions: "debounceIgnore" }, INTERRUPT_API: { actions: "idempotentNoop" } } },
  },
})
// model-based test generates every state×event path:
const model = createModel(stopMachine).withEvents(/* ... */)
model.testAllStates() // asserts no transition violates guards
```

**Harness H3 — `NoPlacebo` (shell probe):**

```sh
# Shell-level property: POST /interrupt while status!=idle must eventually yield status=idle and no tool child
assert_probe_point 2 "stream killed"   # GET /api/session/:id/status eventually idle
assert_probe_point 3 "tool killed"     # pgrep -f "sleep 42" gone within TIMEOUT_S
assert_probe_point 6 "no orphan after restart"  # pgrep after UI kill still gone
# Probe is the harness: scripts/probe-stop-button-phase0.sh already implements this
```

All three harnesses are **specified now**, executed at Phase 2 (tests green) and Phase 5 (hardening). A harness that fails indicates either a bug or a spec property needing refinement — both feed back through Phase 4 (VSDD §IV).

---

## 4. States and Transitions (Statechart)

### 4.1 States

| State | Meaning | TUI | Coordinator | Status SSE |
|-------|---------|-----|-------------|------------|
| **`idle`** | No active drain for this `sessionID`; `coordinator.active` does not contain key; session may accept a new prompt immediately. | `isRunning=false`, `Send` enabled (↑), `■ Stop` muted/disabled, `isInterrupting=false` | `active.get(key) === undefined` | `type: "idle"` (`time.idle` present) |
| **`running`** | A drain owns the session: LLM streaming, tool executing, permission pending, or retry parked inside the same fiber. | `isRunning=true`, `Send` hidden/secondary, `■ Stop` red/error enabled, `isInterrupting=false` | `active` contains key, `entry.owner` is live Fiber | `type !== "idle"` (running / tool-executing / pending) |
| **`confirming`** | User clicked `■ Stop` while `running`; confirmation dialog is mounted awaiting `Yes/No`. No server call yet sent. | Dialog visible: "Stop agent? / Stop the current agent? This will interrupt the model and running tools." + `[No]` `[Yes]` + `esc` hint; backdrop `onClose → No` | still `running` (no coordinator change yet) | still non-idle |
| **`interrupting`** | `Yes` confirmed (or `Esc Esc` path); `sdk.client.v2.session.interrupt` in flight or `Fiber.interrupt` settling; TUI debounced. | `isInterrupting=true`, `■ Stop` disabled/muted for 800ms cooldown, 1s `lastInterruptAt` gate; toast pending | `entry.stopping=true`, `pendingWake=false`, `Fiber.interrupt(entry.owner)` running; `active` still contains key until `onExit → settle` | non-idle until settle, then `idle` |

**Derived states (not new states, but sub-modes of `running` captured in `status.type`):** `tool-executing`, `permission-pending`, `waiting-for-provider` (401/429 park), `question-dismissed` — all are `running` for the Stop-Button's purposes; interrupt kills them all because they live inside the same fenced fiber (Failure-Matrix § "parked 401/429 retry loops live inside the same fiber").

### 4.2 Statechart (XState v5 sketch)

```
         PROMPT / wake(idle)
  ┌─────────────────────────────────┐
  │         idle                    │◄───────────────────────────┐
  │  Send: enabled                  │                            │
  │  Stop: muted → toast "No run"   │   DONE / ERROR / SETTLED   │
  └──────────┬──────────────────────┘                            │
             │                                                   │
             │ DONE/ERROR (natural completion)                   │
             ▼                                                   │
  ┌─────────────────────────────────┐      YES / ESC_ESC         │
  │        running                   │──────────────────────────┐  │
  │  Send: disabled                  │                          │  │
  │  Stop: red enabled               │    ┌─────────────────┐   │  │
  │  Esc Esc ─────────────────────►  │    │  confirming     │   │  │
  │  Stop Click ──────────────────►  │    │  dialog open    │   │  │
  └────────────────┬────────────────┘    │  No/Esc/Dismiss  │   │  │
                   │                      │  ──► running     │   │  │
                   │                      │  Yes ────────────┼───┘  │
                   │                      └─────────────────┘        │
                   │                                    ▲           │
                   │  YES (from dialog)                 │           │
                   ▼                                    │           │
  ┌─────────────────────────────────┐                   │           │
  │      interrupting               │                   │           │
  │  isInterrupting=true (800ms)    │                   │           │
  │  debounce 1s                    │───────────────────┘           │
  │  Stop Click → debounceIgnore     │     SETTLED → idle            │
  └─────────────────────────────────┘                               │
             ▲                                                      │
             │  Fiber.interrupt(entry.owner)                        │
             └──────────────────────────────────────────────────────┘
```

**Machine definition (executable, see §3b.4 H2):** `idle --PROMPT→ running --STOP_CLICK→ confirming --YES→ interrupting --SETTLED→ idle` is the primary path. `running --ESC_ESC→ interrupting` bypasses `confirming` (keyboard authority). `running --DONE/ERROR→ idle` is the non-stop completion.

### 4.3 Permitted Transitions (table-level contract)

| From | Event | Guard | Action (effectful shell) | To | Note |
|------|-------|-------|--------------------------|----|------|
| `idle` | `PROMPT_SUBMIT` / `wake(key)` / `run(key)` | — | `coordinator.run(key)` / `wake(key)`; drain starts | `running` | Per `SessionExecution.wake` |
| `idle` | `STOP_CLICK` | `props.sessionID` present but `status.type=="idle"` | `toast "No active run"` + log | `idle` | no-op, 204 equivalent |
| `idle` | `INTERRUPT_API` | — | server returns `204 no-op` (`Effect.void`) | `idle` | probe point 1 |
| `running` | `STOP_CLICK` | `!isInterrupting && now-lastInterruptAt>=1000` | `openDialog(confirming)` | `confirming` | |
| `running` | `ESC_ESC` | `status.type!=="idle"` && second Esc within 5s | `sdk.client.v2.session.interrupt` | `interrupting` | legacy path, no dialog |
| `running` | `DONE` / `ERROR` / `drain settles success/fail/defect` | — | clear `active` | `idle` | natural end |
| `confirming` | `YES` | `!isInterrupting` | `setIsInterrupting(true)`; `appendStopLog interrupt request`; `sdk.client.v2.session.interrupt` | `interrupting` | fence invoked |
| `confirming` | `NO` / `ESC` / `DISMISS` / `outside click` / `5s timeout` | — | `appendStopLog cancelled`; `dialog.clear` | `running` | fiber untouched |
| `interrupting` | `STOP_CLICK` | — | `debounceIgnore` (guard blocks) | `interrupting` | idempotent |
| `interrupting` | `INTERRUPT_API` (second) | — | `Effect.void` / `204` | `interrupting` | idempotent |
| `interrupting` | `SETTLED` (Fiber.interrupt done, `onExit→settle`) | `settled(key, entry, exit)` | `active.delete(key)` or successor start; `toast Interrupted`; `setTimeout 800ms → isInterrupting=false` | `idle` | may also go to `running` if a `wake` raced (see §5 I6) |

**Forbidden transitions (must be rejected by the pure transition function):** `idle → confirming`, `idle → interrupting` (except the typed idle no-op which stays `idle`), `confirming → idle` (must go through `running` or `interrupting`), `interrupting → confirming`, `interrupting → running` except via raced `wake`/`run` (§5 I6).

---

## 5. Invariants

Mechanical enforcement belongs here (Execution Engine Vision: "preventing invalid state transitions" + "detecting orphaned reasoning"). Each invariant states the pure predicate, the enforcement locus, and the cheapest discriminating test.

| # | Invariant | Pure predicate | Locus | Cheapest test (falsifying) | Probe point |
|---|-----------|----------------|-------|----------------------------|-------------|
| I1 | **Authoritative fence** — `interrupt(key)` must `Fiber.interrupt(entry.owner)` for the live key, killing the entire drain (LLM stream + every `forkChild` tool fiber + `Deferred.fail` on parked retry/tool promises). | `interrupt(key) ⇒ Fiber.interrupt(owner) ∧ entry.stopping ∧ ¬pendingWake` | `run-coordinator.ts:94-101` | unit: `kills a running tool child fiber when interrupted` — fork a `never` tool child via `forkChild`, interrupt, assert `Cause.hasInterruptsOnly` on both owner and child | probe 2,3,5 |
| I2 | **No placebo** — UI shows `running` iff coordinator `active` contains key; UI shows `idle` iff no fiber or tool child remains alive. | `isRunning()==true ⇔ key∈active ⇔ ∃ live owner Fiber` | TUI `isRunning` memo + sync | falsify by asserting `status.idle` but `pgrep -f "sleep 42"` still alive within 1s → probe FAIL | probe 2,3,6 |
| I3 | **No orphan** — after `interrupt` settles, no tool child process survives the interrupt; the key is free so a fresh drain can start. | `after(interrupt settles) ⇒ active.empty ∧ no Tool child Fiber alive ∧ pgrep 0` | coordinator `settle` + scoped child process `Fiber.interrupt` cleanup | unit: `does not leave tool child running after interrupt (no orphan)` + live `pgrep -f "sleep 42"` after interrupt | probe 3,6 |
| I4 | **State-gating** — `interrupt` is legal only when `running` or `confirming` (→ `interrupting`) or `interrupting` (idempotent) or `idle` (204 no-op); `Send` only when `idle`; `■ Stop` only when `running` (and not `interrupting`). | `canInterrupt(state) = state∈{running,confirming,interrupting,idle-noop}` | pure machine `can(state,event)` predicate → TUI `disabled` + handler `if (owner===undefined) Effect.void` | @xstate/test model test generates `idle/STOP_CLICK` → stays `idle`; `running/STOP_CLICK → confirming` | probe 1,4 |
| I5 | **Idempotence** — `interrupt(idle)` is `204 no-op` with no side effect; `interrupt(interrupting)` is coalesced (second call ignored until `settled`). | `interrupt(idle)=Effect.void ∧ interrupt(interrupting)=Effect.void until settle` | `run-coordinator.ts:97` + TUI `isInterrupting` guard + 1s `lastInterruptAt` | sequence test: `interrupt(idle); interrupt(idle); assert runs==0`; `interrupt(running); interrupt(running) before settle; assert runs==1` | probe 1 |
| I6 | **Raced wake/run safety** — a `wake(key)` or `run(key)` that arrives while `interrupting` cleanup is settling must not be lost: if `pendingWake` was set during interrupt, `settle` starts a successor; a `run` registered during cleanup results in `force:true` successor. | `settle: if entry.pendingWake → start(successor, force:false)`; `if interrupt sees pendingWake && run raced → force:true` | `run-coordinator.ts:51-65,81-92` + tests `runs a wake registered during interruption cleanup`, `starts a resume registered during interruption cleanup` | concurrent test: `interrupt.fork; wake during cleanup; await; assert runs==2` | — |
| I7 | **Debounce + cooldown** — rapid duplicate `Stop` clicks do not issue duplicate SDK calls. | `now-lastInterruptAt < 1000 ⇒ ignore ∧ isInterrupting ⇒ ignore` | TUI `lastInterruptAt` + `isInterrupting` + `setTimeout 800ms` | timer test: two clicks 200ms apart → one `sdk.interrupt` call + one log line | — |
| I8 | **Process-local ownership** — interrupt only fences the **local** coordinator entry; idle/missing interruption is no-op (not error); `GET /api/session/:id` has no status field — idle is derived from `time.idle`. | `interrupt(missing key)=void` | `run-coordinator.ts:97` | unit: `does nothing when interrupted while idle` — `await coordinator.interrupt("missing")` resolves | probe 1 |

---

## 6. Purity Boundary (detailed)

See §3b.2 for the architectural map. This section names the exact files and the direction of dependency.

### 6.1 Pure core (must remain free of I/O)

| Artifact | File / locus | Purity | Verification reachable? |
|----------|--------------|--------|-------------------------|
| `StopButtonMachine` definition (states, events, transitions, guards) | **to be created** `fork/session-ui/src/v2/components/prompt-input/machine.ts` (or `prompt/index.tsx` extracted `createStopMachine`) | pure — `(State, Event, Guards) → State` + effect descriptor | Yes — `@xstate/test`, Kani/proptest harnesses |
| Guard predicates `isRunning`, `canInterrupt`, `shouldDebounce`, `isConfirming` | `prompt/index.tsx:215-216` `isRunning` memo + extracted pure helpers | pure boolean fns of `(status, isInterrupting, lastInterruptAt)` | Yes |
| Invariant predicates I1-I8 as assertions | this spec §5 (formal predicates) | pure — predicate over `(state, active, fiberExit, pgrep)` | Yes — property tests |
| Transition function `next(State, Event) → State` | extracted from machine | pure total function | Yes |
| `SessionRunCoordinator` ownership logic (active map, `start`, `settle`, `run`, `wake`) | `run-coordinator.ts` | pure `Effect` algebra, no network/disk per se — but `Effect` runtime is the interpreter | Yes via `Effect` deterministic tests (no I/O) |

### 6.2 Effectful shell (must remain thin glue)

| Shell | Locus | Effect | How tested |
|-------|-------|--------|------------|
| `sdk.client.v2.session.interrupt({sessionID})` network call | `prompt/index.tsx:289` `handleStopClick` + `:498` double-Esc | HTTP `POST /api/session/:id/interrupt` → `204` | live probe (real server) |
| `SessionExecution.interrupt` delegation + `Runner.cancel` (`Fiber.interrupt + Deferred.fail`) | `packages/core/src/session/execution.ts` + `runner/llm.ts` | cancels LLM `fullStream` + tool subprocess `Process` scoped fiber | coordinator tests + process.test.ts |
| `Fiber.interrupt(entry.owner)` execution | `run-coordinator.ts:100` | actually kills the fiber | unit (forkChild) proof |
| `appendFile("/tmp/stop-button.log")` | `prompt/index.tsx:219-222` | fire-and-forget, `catch(()=>{})` | log presence check |
| `toast.show` | `prompt/index.tsx:291,293` | UI feedback | visual / snapshot |
| `dialog.replace(confirming JSX)`, `onMouseUp` handlers | `prompt/index.tsx:239-280` | mount/unmount | interaction test |
| `sync.data.session_status` SSE subscription | `useSync()` | server-driven status | status polling |

**Dependency rule (VSDD 1b):** shell may call core; core never imports shell. Concretely, `prompt/index.tsx` may import the pure `StopButtonMachine`; the machine never imports `sdk` or `fs/promises`. This is the "pure core, effectful shell" that VSDD warns misplacing makes verification unrecoverable (AGENTS.md abstraction boundaries: Research must not depend on Implementation).

**If the boundary is violated later** (e.g., `Effect` runtime details leak into the chart, or `appendFile` moves into the transition function), the spec's §3b.1 provable properties become unreachable and the VSDD Phase 5 hardening fails — the spec review gate (§8) must reject the change.

---

## 7. Edge Catalog (exhaustive)

Each edge states the **event**, the **state before**, the **expected next state + observable**, and the **cheapest discriminating test** (per AGENTS.md Cheapest-Test-First). The list is exhaustive for the 4-state machine with the two entry paths (button + Esc Esc).

| # | State before | Event | Expected next state + observable | Cheapest test (falsifying) | Carrier |
|---|--------------|-------|----------------------------------|----------------------------|---------|
| E01 | `idle` | `STOP_CLICK` (no `sessionID`) | stay `idle`; `toast "No active run"`; log `no sessionID` | TUI: mount prompt without sessionID, click Stop, assert `isRunning==false` + toast | TUI unit |
| E02 | `idle` | `STOP_CLICK` (`sessionID` set, status `idle`) | stay `idle`; `toast "No active run"`; log `no active run` | click Stop while idle, assert no `sdk.interrupt` call | TUI unit |
| E03 | `idle` | `INTERRUPT_API` (`POST /interrupt` while idle) | `204` no-op; `active` empty; still `idle`; no toast from server | `coordinator.interrupt("missing") → Effect.void`; probe point 1 `http 204` | unit + probe |
| E04 | `idle` | `ESC` single / `ESC_ESC` (idle) | stay `idle`; no dialog; `store.interrupt` increments then resets after 5s | single Esc in idle → assert `status.type=="idle"` | TUI unit |
| E05 | `running` | `STOP_CLICK` (first, not debounced) | `confirming`; dialog mounted; no SDK call yet | click Stop while running (`status.type!="idle"`) → assert dialog visible | TUI unit |
| E06 | `running` | `STOP_CLICK` + `NO` | `confirming → running`; dialog closes; fiber alive; `active` contains key | click Stop → No → assert `isRunning==true` + `active.size==1` | TUI + unit |
| E07 | `running` | `STOP_CLICK` + `ESC` (dismiss) | same as No (`running`) | Esc while dialog open → assert back to running | TUI unit |
| E08 | `running` | `STOP_CLICK` + `DISMISS` (outside click / `onClose`) | same as No (`running`) | click outside dialog → `resolve(false)` → running | TUI unit |
| E09 | `running` | `STOP_CLICK` + `YES` | `confirming → interrupting`; `appendStopLog interrupt request`; `sdk.client.v2.session.interrupt` invoked once; `isInterrupting=true` | Yes → assert `sdk.interrupt` called once + `isInterrupting==true` + `isRunning==true` until settle | TUI unit |
| E10 | `running` | `ESC_ESC` (double Esc within 5s) | `running → interrupting` directly (no dialog); same SDK path as E09 | double Esc while running → assert `sdk.interrupt` called without dialog | TUI unit |
| E11 | `running` | `ESC` single only | stay `running`; `store.interrupt=1`; auto-reset after 5s | single Esc → assert `store.interrupt==1` | TUI unit |
| E12 | `interrupting` | `STOP_CLICK` (second click within 1s / while `isInterrupting`) | stay `interrupting`; second `sdk.interrupt` suppressed (`lastInterruptAt` / `isInterrupting` guard) | click Stop, immediately click again → assert `sdk.interrupt` call count 1 | TUI unit |
| E13 | `interrupting` | `INTERRUPT_API` second call (concurrent API) | idempotent `Effect.void`; still `interrupting` until settle | `interrupt(running); interrupt(running) concurrent → await settle → runs==1` | unit |
| E14 | `interrupting` | `wake(key)` arrives during cleanup (`cleanupStarted → Deferred.await(cleanupGate)`) | `pendingWake=true`; `settle` starts successor with `force:false`; eventually `running` then `idle` | test `runs a wake registered during interruption cleanup` | unit |
| E15 | `interrupting` | `run(key)` arrives during cleanup | successor with `force:true` (see §5 I6) | test `starts a resume registered during interruption cleanup` → `forces==[false,true]` | unit |
| E16 | `running` | `interrupt` while LLM streaming | stream fiber interrupted (`llm.ts` `fullStream` scope finalizer `iter.return()` is fire-and-forget `safeIterable`; `Effect` interrupt wins) | probe point 2: start `Write a 3000-word essay…`, interrupt within 1s, assert `status` eventually `idle` | probe + unit `durably closes partial when provider stream interrupted` |
| E17 | `running` | `interrupt` while local tool `sleep 42` (forkChild) | tool child `Fiber` interrupted; scoped child process `Process` cleaned; `tool state: {status:error}` | probe point 3: `sleep 42` via tool input, interrupt, assert `pgrep -f "sleep 42" == 0` + `status idle` | probe + unit `kills a running tool child fiber` |
| E18 | `running` | `interrupt` while hosted (provider-executed) tool | `providerExecuted:true` tool result is error; same interrupt path but provider metadata preserved | unit `Recover interrupted hosted tool` | unit |
| E19 | `running` | `interrupt` while 401/429 park (retry Deferred) | parked `Deferred.fail` + `Fiber.interrupt` clears the retry loop; `active` empty | probe point 5: provoke 429 (FORCE_429) then interrupt → assert cleared; unit: retry fiber killed | probe + unit |
| E20 | `running` | `interrupt` while `permission-pending` (Awaiting approval) | runner continuation interrupted; `tool: {status:error, message:"Tool execution interrupted"}` | unit `interrupts runner continuation when permission approval is declined` | unit |
| E21 | `running` | `interrupt` while `question-dismissed` | same as permission: continuation interrupted | unit `interrupts runner continuation when a question is dismissed` | unit |
| E22 | `running` | natural `DONE` / `ERROR` before confirm Yes race | `running → idle` via `settle`; later `YES` arrives against `idle` → `204 no-op` (not error) | race test: `Deferred.await(gate)` drain, `gate succeed`, immediate interrupt → assert idle + interrupt no-op | unit + probe race |
| E23 | `interrupting` | `SETTLED` success/failure/defect | `interrupting → idle` (delete `active` or successor if `pendingWake`); `Deferred.done` with exit | unit `cleans active executions after failure and defect`; `settles` with interrupt Cause | unit |
| E24 | any | `interrupt` network error (HTTP ≠204, exception) | stay in current state; `catch` → `appendStopLog error=…` + `toast errorMessage(e)` + `isInterrupting` resets after 800ms | mock `sdk.client.v2.session.interrupt` throws → assert toast error + `isInterrupting==false` after timeout | TUI unit |
| E25 | any | `sessionID` missing/undefined at call | `toast "No active run"`; no SDK call; stay in state | `props.sessionID===undefined` → `handleStopClick` early return | TUI unit |
| E26 | `running` | `coalesced wakes` (3 wakes concurrent during active) | exactly one successor drain (runs==2) | unit `coalesces wakes received during active execution` | unit |
| E27 | any | `GET /api/session/:id` poll after interrupt (UI derives idle from `time.idle`) | `time.idle` present → `isRunning==false` within staleness budget | probe point 6 + status poll `time.idle` | probe |
| E28 | after UI restart | orphan check (`pgrep` after TUI kill) | no tool child survives UI process death (scoped fiber cleanup via `Fiber.interrupt` on scope close) | test `cleans active executions when its scope closes` + probe point 6 after `kill $TUI_PID` | unit + probe |

**Count:** 28 edges; exhaustive for `(4 states) × (events: STOP_CLICK, NO, YES, ESC, ESC_ESC, DISMISS, INTERRUPT_API, PROMPT, DONE, ERROR, SETTLED, WAKE, RUN)` plus shell errors (E24-25) and infrastructure (E27-28). Any missing edge discovered in Phase 3 adversarial refinement must be added to this catalog per VSDD Phase 4 feedback loop.

---

## 8. Execution Engine Hypotheses H1-H4 — Traceability

The Execution Engine is an ASES methodology execution system, not a project-management app (Execution Engine Vision § Core Principle). The stop-button is the smallest state-gated execution that makes that vision observable. This spec traces each of the four UIRD hypotheses (EDASES-topic-UI-design §24) to a concrete stop-button obligation:

| Hypothesis | Statement | Stop-Button obligation in this spec | How verified |
|------------|-----------|-------------------------------------|--------------|
| **H1 Artefact abstraction** — Engineering artefacts are a more useful primary abstraction than repositories. | The governed artefact is **session execution** (`sessionID` key + `SessionRunCoordinator.Entry`), not the repository or the button widget. The button is a gate on artefact state. | Artefact is explicit: `Coordinator<Key,E>` with `active`, `run`, `wake`, `interrupt`; states `idle/running/confirming/interrupting` are artefact lifecycle, not widget animation. | `run-coordinator.ts` is the artefact authority; `@xstate/test` paths assert artefact state |
| **H2 Context reduction** — Versioned artefacts and explicit provenance reduce context for zero-context agents. | A zero-context agent must be able to answer "can I interrupt?" from `status.type` alone, without rereading the conversation. | Derived status `sync.data.session_status[sessionID].type` is the single source; `idle` is derived from `time.idle` (no separate field to drift); the statechart's `canInterrupt(state)` is a pure function of that status. | TUI `isRunning` memo + probe log `/tmp/stop-button.log` (one line per decision, not a transcript) |
| **H3 Interruption recovery** — Explicit provenance improves an agent's ability to resume interrupted work. | After `interrupting → idle`, the session must accept a new prompt immediately (no lost prompt, no orphaned drain). | §5 I6: raced `wake`/`run` during interrupt cleanup are not lost; `POST /api/session/:id/prompt` after interrupt is `200` and starts a fresh drain (probe point 4). | unit `wake/run registered during interruption cleanup` + probe point 4 |
| **H4 Unified representation** — A shared graph can represent execution, reasoning, evidence, and version history without becoming unusable. | One underlying information model backs four views: Execution (`active` map), State (`idle/running/…`), Evidence (`/tmp/stop-button.log` + `Cause` + `tool state error`), Version history (`session_input` durable rows, no `no-orphan` leak). | Same `sessionID` key anchors execution (coordinator), state (status SSE), evidence (log + Exit cause), version (durable `session_input` + `promptInput` inbox) — per Execution Engine Vision §§ State/ Knowledge Model. | log + `session_input` row + `active` map all keyed by `sessionID` |

**H1/H3 tension note (per execution-engine-ui synthesis §5: lifecycle-ownership):** the synthesis warned that "reversed composition (statechart owns lifecycle, engine only schedules) is unevidenced." This spec makes the position explicit: the **statechart owns lifecycle** (authoritative transitions at §4.3), the **engine owns scheduling** (Fiber ownership, §6). The evidence status is experimental — the live probe provides the discriminating test that will confirm or falsify the ownership claim.

---

## 9. VSDD Phase 1c — Spec Review Gate

Per VSDD Phase 1c, the complete spec — behavioral contracts *and* verification architecture — must be reviewed by both the human and the Adversary before any tests are written beyond the Phase 0 cheap fence (the fence tests already exist; this gate qualifies them).

### 9.1 Adversary checklist (Sarcasmotron lens — zero tolerance)

The Adversary should pronounce on each, with file:line citations:

* [ ] Ambiguous language: any transition phrasing that admits two readings (e.g., "eventually idle" needs a timing bound).
* [ ] Missing edge: any `(state, event)` pair not in §4.3 / §7.
* [ ] Implicit assumption not stated: e.g., "server and TUI share the same `SessionRunCoordinator` process" (V2 Session Core: interrupt only fences the process-local chain; clustering would break I1 — mark as assumption).
* [ ] Contradiction between spec sections (e.g., §4.2 chart vs §4.3 table).
* [ ] Property claimed "testable only" that should be provable: push back on §3b.1 if any `must be proven` was downgraded to "test coverage sufficient" lazily.
* [ ] Purity boundary violation: any logic in §6.1 that actually depends on external state (e.g., `shouldDebounce` that reads `Date.now()` must be `(now, last)` pure).
* [ ] Verification tool mismatch: Kani/proptest/@xstate/test cannot actually prove `FenceKillsToolChild` as stated, or harness sketch at §3b.4 is not executable.

### 9.2 Human operator gate

* [ ] Spec Crystallization (§2) matches operator intent: "Tiny V2" (toggle + confirm, no surge of new files, no new endpoint).
* [ ] Verification Architecture (§3) is not over-ceremony for the host: XState v5 + Effect tests + live probe is lite-VSDD (observer-swarm Appendix A), not full formal proof.
* [ ] H1-H4 traceability (§8) is honest: lifecycle-ownership tension acknowledged, not hidden.

### 9.3 Exit criterion for Phase 1c

Per VSDD §II "Convergence" four-dimensional check: the spec is considered **1c-pass** when:

1. Adversary spec critiques are nitpicks about wording, not about missing behavior, ambiguity, or verification gaps;
2. No edge in §7 is found missing by independent re-derivation (hy3-style source re-check);
3. The purity boundary at §6 survives an audit that the transition function indeed has no I/O imports.

Only then may Phase 2 proceed (translate §2 into failing tests) — though in this branch the fence tests pre-existed via Phase 0 cheapest-test; Phase 2 now adds the XState model test and the edge-catalog harness per §3b.4.

---

## 10. Traceability: Spec → Bead → Test → Proof

Per VSDD §III Contract Chain, every artifact links back:

```
Spec Requirement (§5 invariant / §7 edge)
  → Bead (Crosslink #510 sub-issue — to be decomposed per contract item)
  → Test Case (run-coordinator.test.ts harness or probe assertion)
  → Implementation (run-coordinator.ts / prompt/index.tsx)
  → Adversarial Review (Phase 3 roast of spec+tests+implementation)
  → Formal Proof / Hardening (Phase 5: @xstate/test paths + Kani/proptest harness)
```

| Spec item | Bead (suggested) | Test case | Implementation | Review |
|-----------|------------------|-----------|----------------|--------|
| I1 Fence | #510-I1-fence | `kills a running tool child fiber when interrupted` | `run-coordinator.ts:100 Fiber.interrupt` | Phase 3 |
| I2 No Placebo | #510-I2-no-placebo | `pgrep -f "sleep 42"` after interrupt | `prompt/index.tsx` `isRunning` + status SSE | probe 2,3 |
| I3 No Orphan | #510-I3-no-orphan | `does not leave tool child running after interrupt` | scoped `Process` cleanup | probe 6 |
| I4 State-Gating | #510-I4-gating | `@xstate/test` model (every state×event) | StopButtonMachine guards | Phase 1c |
| I5 Idempotence | #510-I5-idempotent | `does nothing when interrupted while idle` + debounce test | `run-coordinator.ts:97 Effect.void` + `lastInterruptAt` | — |
| I6 Raced wake/run | #510-I6-raced-wake-run | `runs a wake registered during interruption cleanup` + `starts a resume registered…` | `run-coordinator.ts:51-65` settle successor | — |
| E01-E28 | #510-E* | per §7 Carrier column | per §7 | Phase 3 |

---

## 11. Decisions and Open Items

### 11.1 Decisions recorded in this spec

* **D1 — Statechart owns lifecycle, engine schedules** (§6): the chart is authoritative for which transitions are legal; the coordinator is authoritative for whether the Fiber actually died. This resolves the lifecycle-ownership tension by making it explicit, at the cost of requiring the chart and the `active` map to stay coherent (enforced by SSE status subscription).
* **D2 — No new server endpoint:** bind the existing `POST /api/session/:id/interrupt` (Session3 / `v2`). Correctness is at the fence, not the route — avoids protocol sprawl.
* **D3 — Lite-VSDD:** XState v5 + Effect deterministic tests + live 9-point probe + tsgo is the verification stack (not Kani on the whole TUI). Per observer-swarm Appendix A, full formal proof of the effectful shell is deferred; the pure core is the only Kani-harness target.
* **D4 — `sleep 42` discipline:** probe `TOOL_CMD` defaults to `sleep 42` (not `sleep 30`) to avoid collision with `sleep 300` kickoff watchers (`pgrep -f "sleep 30"` false positives observed 2026-08-29). This is a test-id hygiene rule, not a product rule.
* **D5 — Status-lag denial closed by authoritative reconciliation, not documented window** (issue #510 B1, 2026-08-30): the TUI-local `status().type` projection can lag the coordinator (fiber live, projection still `idle`), which denied both the Stop button (204 no-op toast) and the ESC command (`enabled:` gate). Chosen fix: when the projection says `idle` and the user explicitly requests a stop, reconcile once against `GET /api/session/active` (the coordinator active-map HTTP projection) and treat presence as `running`; the ESC `enabled:` gate is removed entirely (the machine gate + reconciliation handle idle). Rejected alternative: documenting the lag window as accepted — rejected because it leaves the user unable to stop a live fiber, the exact denial class the button exists to prevent. Cost: one extra GET only in the ambiguous case; unreachable server falls back to the local projection.
* **D6 — Shell gate extracted into a mountable controller** (issue #510 D1, 2026-08-30): the reviewer found the gate's two enforcement sites (`handleStopClick`, `session.interrupt` ESC_ESC) had no executable discriminating test — a mutation deleting the gate passed every test in the repo. Fix: extract the flow into `prompt/stop-button-controller.ts` with injected effects and gate it with the same pure machine; the integration test mounts the real controller and is mutation-verified (gate-removal and unconditional-fire mutants fail). Supersedes the NF5 single-file constraint (see §2a.4).
* **D7 — Placebo detection is layered; the TUI now participates** (issue #510 B3, 2026-08-30): placebo (204-but-fiber-alive) was previously detectable only by the live probe (which SKIPs without a server) and the coordinator seam tests. The controller now runs a post-interrupt settle check: after the 1.2s settle window it re-reads the active map; still-active with no new user message → `PLACEBO SUSPECT` log + warning toast. Detection matrix: coordinator unit tests (seam, deterministic) → controller settle check (in-UI, best-effort) → live 9-point probe (end-to-end, requires tool-child-capable server).

### 11.2 Open items (deliberately unresolved, not silently settled)

* **O1 — Clustering:** V2 Session Core notes "Keep local Session drains process-local until clustering is implemented." If sessions become cluster-placed, the process-local fence (I1) no longer covers a remote owner — a placement-aware interrupt is an explicit future design, not in this spec.
* **O2 — `@xstate/test` machine file locus:** `machine.ts` extraction vs inline in `prompt/index.tsx` — decision at Phase 2 implementation; either is compliant as long as purity boundary (§6) holds.
* **O3 — Probe server capability:** live proof of E17 (tool kill) needs a server/agent that runs shell-tool children (`sleep 42` observable). The `:49374` opencode server does not expose that; O3 is closed by the coordinator unit test at the fence seam, not by live shell kill — track as evidence gap.
* **O4 — `GET /api/session/:id` status field:** no status field exists; `idle` is derived from `time.idle`. If a future server adds explicit status, §4.1 and `isRunning` derivation must be re-reviewed for drift.

---

## 12. Relationship to Other Documents

* **Execution Engine Vision** (§§ Methodology Execution, Mechanical Enforcement, State Management) — this spec is the smallest executable instance of that vision: methodology (state-gating) made executable via explicit state + coordinator ownership + mechanical guards.
* **Methodology to Requirements Mapping** (§§ State Management, Traceability) — derives "State transitions should only occur when permitted" → this spec's §5 invariants + §4 transitions.
* **AI Orchestration Guide** (§ Independent Reasoning, Constructive Adversarial Review) — Phase 1c review gate + Phase 3 roast are instances of that workflow.
* **Workflow Topology Design** (§§ Position-emitting agents, Cheap staleness trigger, AUDITOR as divergence verifier) — the Verified Spec itself is the durable position stream for the stop-button; the live probe's staleness (2× expected interval without `idle`) is the cheap trigger; the Reviewer at §9.1 is the read-only divergence checker.
* **Failure-Matrix** rows 18-20 (placebo interrupt, Task vs kickoff divergence, plugin load) — this spec is the hook implementation that would prevent the first row.

---

*End of spec. Next step per VSDD: Adversarial review of this spec (Phase 1c) — fresh context, hastily claimed gaps are the adversary's product.*

