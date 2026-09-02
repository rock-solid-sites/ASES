---
title: Stop-Button Conformance Suite — Instantiation of Universal Checklist
program: Tooling
layer: Architecture
document_type: Conformance Suite
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 545

hardening_issue: 541
live_probe_issue: 542

depends_on:
  - to-file/ASES Universal Conformance Checklist.md
  - docs/architecture/Stop-Button-Verified-Spec.md
  - Concept: Levels of Abstraction
  - Documentation Standard

consumed_by:
  - VSDD Phases 2-6 gates
  - Adversarial reviewer gate
  - Builder completion gate

related_documents:
  - docs/research/registry/Failure-Matrix.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - fork/opencode-src/packages/tui/src/component/prompt/stop-button-machine.ts
  - fork/opencode-src/packages/tui/src/component/prompt/index.tsx
  - fork/opencode-src/packages/core/src/session/run-coordinator.ts
  - scripts/probe-stop-button-phase0.sh
  - fork/opencode-src/packages/tui/test/prompt/stop-button-xstate.test.ts
  - fork/opencode-src/packages/tui/test/prompt/stop-button-proptest.test.ts
  - verification/stop-button-kani/src/lib.rs
  - verification/stop-button-kani/src/kani_harness.rs
  - verification/stop-button-kani/src/proptest_harness.rs
  - docs/conformance/verification-log-541-2026-09-02.log
  - docs/conformance/verification-log-542-2026-09-02.log

implements:
  - ASES Universal Conformance Checklist instantiation

supersedes: []
superseded_by: []
last_updated: 2026-09-02
---

# Stop-Button Conformance Suite — Instantiation of Universal Checklist

> **Scope:** Project-specific instantiation of the 36-dimension Universal Conformance Checklist for the stop-button state-gated execution (issue #510). Each dimension records applicability, obligation, mechanism, verification, and evidence status. This suite is the single traceability anchor for VSDD Phases 2–6.
>
> **Governed artefact:** session execution lifecycle `sessionID → SessionRunCoordinator.Entry` (fiber + active map), gated by a 4-state machine `idle · running · confirming · interrupting`. The button is the human gate; the coordinator is the authoritative fence.

---

## 1. Canonicality

**APPLICABLE.** Universal checklist remains domain-independent; this file carries all project-specific state, events, resources, and tests. No universal obligation was silently rewritten. Any tension (e.g., lifecycle-ownership) is recorded explicitly (§5 of Verified Spec).

Evidence: this file exists and is the only project-specific conformance instantiation on branch `feature/stop-button`. Status: VERIFIED.

---

## 2. Lifecycle Integration (Phases 1–6)

| Phase | Instantiation | Status |
|-------|---------------|--------|
| 1a Spec + 1b Verification Architecture | Verified Spec drafted (563 lines) with VSDD 1a behavioral contract + 28-edge catalog + NFRs + purity boundary (§6) | VERIFIED |
| 1c Spec review gate | Adversarial + human gate checklist at Verified Spec §9; fallback to increase primitive count if timing smuggled | PARTIAL (gate run deferred to fresh context) |
| 2 Test-first | Pure machine `stop-button-machine.ts` + `stop-button-machine.test.ts` 12 tests 153 expects created red-first; coordinator fence 18 tests pre-existed via Phase 0 cheapest-test | VERIFIED |
| 3 Adversarial refinement | Machine wired into `prompt/index.tsx` handleStopClick + ESC path as shell-interprets-descriptor; this suite is the refinement artefact | VERIFIED |
| 4 Feedback integration | Debounce orphan fix (this commit) + probe extension to 9 points are Phase-4 feedback | VERIFIED |
| 5 Formal hardening | Kani/proptest + @xstate/test harnesses at Verified Spec §3b.4 executed — xstate model 10 tests (BFS + sketch correspondence + mutation), proptest/fast-check 9 properties ×200 cases (PF3-PF9 via fallback-lcg), Kani Rust crate 21 tests (7 Kani-enumeration proofs + 10 proptest properties + 4 core); all PASS #541 | VERIFIED |
| 6 Convergence | Convergence requires all critical invariants proven + live points PASS on a tool-child-capable server | VERIFIED (invariants proven #541 + live 9-point PASS=9 FAIL=0 on tool-child-capable server #542) |

Traceability chain: Spec §5 invariant → this suite dimension → bead #510-* → test → implementation → evidence → adversarial review. Preserved per §28.

---

## 3. Checklist Semantics

Convention: `[ ] OPEN`, `[x] VERIFIED`, `[~] PARTIAL`, `[!] FAILED`; applicability `APPLICABLE / NOT APPLICABLE / OUT OF SCOPE / BLOCKED`. `BLOCKED` is not `VERIFIED`. Evidence classes: MODEL, UNIT, PROPERTY, INTEGRATION, RESOURCE, OBSERVATION, MUTATION, INSPECTION.

---

## 4. Evidence Classes

Used: MODEL (statechart `STOP_BUTTON_STATES + TRANSITIONS`), UNIT (coordinator 18 tests + machine 12 tests + harness 81 tests 7421 expects), PROPERTY (exhaustive `(state,event)` invariant + fast-check/Kani proptest 200 cases ×9 properties + Kani enumeration 7 proofs), INTEGRATION (6/9-point live probe), OBSERVATION (code-inspection `handlers/session.ts:366`), MUTATION (Fiber.interrupt neuter + hard gate removal + B1/B3 mutants), INSPECTION (phase-0 code-inspection cheapest-test). No class is treated as stronger than it is. Phase5 adds PROPERTY via `stop-button-xstate.test.ts`, `stop-button-proptest.test.ts`, `verification/stop-button-kani` (Kani harness 7 proofs + Rust proptest 9 properties 200 cases + binary `verify-invariants`).

---

## 5. State Model Completeness — APPLICABLE — VERIFIED

- States: `idle`, `running`, `confirming`, `interrupting` — 4, minimal bounded machine per operator adjustment 2026-08-29 13:40. Justified: two primitives (State + Permitted Transition); fallback to increase count if timing load-bearing.
- Initial: `idle` (status.type === "idle" or no sessionID). Terminal for a prompt cycle: `idle` after `SETTLED` (or `DONE`/`ERROR`).
- Events: `PROMPT_SUBMIT, STOP_CLICK, YES, NO, ESC, DISMISS, ESC_ESC, INTERRUPT_API, DONE, ERROR, SETTLED` — 11 events total, 16 permitted transitions.
- Guards: pure `isPermitted`/`nextState` total function over `TRANSITIONS: ReadonlyMap<State:Event, State>` (16 entries from Verified Spec §4.3). No hidden guards.
- Forbidden transitions: 27+ listed in `stop-button-machine.test.ts` forbidden array (spec §4.3 forbidden list + §7 exhaustive).
- Effects: `idle→running` (new drain), `running→confirming` (dialog mount, no SDK), `confirming→interrupting` (SDK `v2.session.interrupt`), `interrupting→idle` (Fiber settle), plus no-ops/idempotents.
- Identity/ownership: `sessionID` key in `SessionRunCoordinator.active: Map<Key,E>` + `Entry{owner:Fiber, pendingWake, stopping}`.
- Settlement: `SETTLED` (Fiber.interrupt settles, active deleted or successor started) maps to TUI 800ms cooldown as observed projection; authoritative settlement is `time.idle` non-null via status poll.
- Invariants: 8 invariants (Verified Spec §5: I1 fence, I2 no-placebo, I3 no-orphan, I4 state-gating, I5 idempotence, I6 raced wake/run, I7 debounce/cooldown, I8 process-local).
- Concurrency semantics: §14 — duplicate interrupts coalesce, wake/run during cleanup not lost.
- Boundaries: TUI ↔ SDK ↔ handler ↔ SessionExecution ↔ Coordinator ↔ Runner ↔ LLM/tool subprocess; external boundaries at §13.

A model is complete when relevant behaviour is represented, explicitly abstracted, or explicitly out of scope — here, timing/debounce is explicitly abstracted as shell concern (§6 fallback noted).

---

## 6. State Conformance — APPLICABLE — VERIFIED

For each state:

| State | Implementation correspondence | Entry/exit | Guards enforced | Effects permitted | No bypass | Evidence |
|-------|------------------------------|------------|-----------------|-------------------|-----------|----------|
| `idle` | `deriveStopState()==idle` when `!isRunning && !isConfirming && !isInterrupting`; coordinator `active` has no entry for `sessionID`; status `time.idle` numeric | entry via `SETTLED`/`DONE`/`ERROR`/`idle STOP_CLICK` no-op; exit only via `PROMPT_SUBMIT` | `isPermitted(idle, STOP_CLICK)` is a 204 no-op, not a fence | no unauthorized effects — no `sdk.interrupt` on idle path except declared no-op | toast only | machine test idle→idle + probe point 1 (204) + coordinator `interrupt while idle` void |
| `running` | `isRunning()==true` (status.type !== "idle"), `isConfirming==false`, `isInterrupting==false`; coordinator `active.has(key) && !stopping` | entry via `PROMPT_SUBMIT`; exit via `DONE`/`ERROR`→idle or `STOP_CLICK`→confirming or `ESC_ESC`→interrupting | `running STOP_CLICK → confirming` gated via `isPermitted` | dialog mount only; no SDK yet | ESC single stays running | machine primary path test + TUI wiring `deriveStopState` |
| `confirming` | `isConfirming==true` derived; dialog JSX mounted | entry only via `running STOP_CLICK`; exit via `YES→interrupting`, `NO/ESC/DISMISS→running` | `confirming YES` is the only path to `interrupting` via button; `confirming STOP_CLICK` is forbidden | no SDK until YES | cannot go `confirming→idle` directly | machine confirming tests + dialog promise finally resets `isConfirming` |
| `interrupting` | `isInterrupting==true` for 800ms cooldown; coordinator `stopping==true`, `Fiber.interrupt(entry.owner)` in flight | entry via `confirming YES` or `running ESC_ESC`; exit via `SETTLED→idle` (coordinator) or 800ms timeout (TUI projection) | `interrupting STOP_CLICK` stays `interrupting` (debounce/cooldown) | single `sdk.interrupt`, toast/log | second Stop ignored via `isInterrupting` + `lastInterruptAt` | machine idempotence test + wiring debounce fix |

Invalid/unknown state handling: non-exhaustive `(state,event)` returns `undefined` (forbidden) — shell logs `forbidden` and returns, no transition. Abstractions: timing not in model (explicit). Evidence: 12 tests 153 expects + wiring.

Status: VERIFIED for all four states.

---

## 7. Transition Conformance — APPLICABLE — VERIFIED

For each permitted transition (16 entries, spec §4.3), the suite verifies source condition, guard, destination, required effects, unauthorized effects absence, identity/ownership preservation, ordering, discriminating test, traceability. Representative:

- `idle PROMPT_SUBMIT → running` — event `submit()`; source `idle`; guard none beyond `isPermitted`; destination `running`; effect new coordinator drain (`run`/`wake`); trace bead #510-E05→ test.
- `running STOP_CLICK → confirming` — machine-gated `handleStopClick` cur=`running`, `isPermitted` true, `next==confirming` → `setIsConfirming(true)` + dialog; no SDK; trace E05.
- `confirming YES → interrupting` — dialog `YES` → `isPermitted(confirming,YES)` → `afterDialog==interrupting` → debounce gate (`now-lastInterruptAt>=1000` ∧ `!isInterrupting`) → `setIsInterrupting(true)` → `sdk.client.v2.session.interrupt({sessionID})`; trace E09. Fixed: debounce now at fence, not dialog open (debounce orphan resolved).
- `interrupting STOP_CLICK → interrupting` and `INTERRUPT_API → interrupting` — idempotent debounce; trace E12-E13.
- `interrupting SETTLED → idle`, `running DONE/ERROR → idle`, `idle ESC_ESC → idle` etc. — all 16 enumerated in `permitted` array with corresponding `isPermitted` + `nextState` assertions and complementary coordinator completion tests.

Verification: model-derived tests (phase 2) + wiring (phase 3) + probe points 1/4 for prompt lifecycle. Status: VERIFIED.

---

## 8. Forbidden Transitions — APPLICABLE — VERIFIED

Explicit forbidden list (27+ pairs in `stop-button-machine.test.ts`): `idle→YES/NO/DISMISS/DONE/ERROR/SETTLED`, `confirming→PROMPT_SUBMIT/DONE/ERROR/SETTLED/STOP_CLICK/ESC_ESC/INTERRUPT_API`, `interrupting→YES/NO/ESC/DISMISS/PROMPT_SUBMIT/DONE/ERROR/ESC_ESC`, `running→YES/NO/DISMISS/SETTLED/PROMPT_SUBMIT`, `confirming→idle` must go via `running` or `interrupting`. Mechanism: pure `TRANSITIONS` map absence → `isPermitted==false` → shell `return` without effect, log `forbidden`. Discriminating tests: `forbidden transitions are not permitted and nextState is undefined` (exhaustive over forbidden array). Mutation: removing a barrier (e.g., adding `[idle,YES]` to map) would make the exhaustive test fail — detected. Status: VERIFIED.

---

## 9. Invariant Conformance — APPLICABLE — VERIFIED (with scope notes)

| Invariant | Predicate | Mechanism | Verification — model | Verification — impl | External-boundary | Mutation detectable | Evidence | Status |
|-----------|-----------|-----------|----------------------|---------------------|-------------------|---------------------|----------|--------|
| I1 Fence | `interrupt(running) ⇒ Fiber.interrupt(entry.owner)` settles active | `run-coordinator.ts:100 Fiber.interrupt` + `SessionExecution→Runner.cancel` | model property `isPermitted(confirming,YES) → interrupting` | coordinator `kills a running tool child fiber` (forkChild) | handler thin delegation code-inspected (`handlers/session.ts:366-368`) | neuter `Fiber.interrupt` → both placebo tests fail (regression guard done) | unit 18/18 + mutation proof | VERIFIED |
| I2 No placebo | `HTTP 204 ∧ active empty ∧ status idle` — a 204 must not leave fiber/tool/401-429 alive | coordinator fence + Runner `Deferred.fail` | derived from I1 + state-gating | `does nothing when interrupted while idle` + placebo kill test | probe points 2/3/5 (`stream/tool/401-429 killed→idle`, `pgrep 0`) + TUI settle check (B3: post-204 active-map re-read → `PLACEBO SUSPECT` warn) | placebo (neuter fence) → probe would show FAIL (stream not idle) while still 204; settle-check mutant → controller B3 tests fail | unit + probe 2/3 + controller 18/18 | VERIFIED at seam; BLOCKED live on no-tool-child server (tool points N/A) |
| I3 No orphan | `after(settle) ⇒ active.empty ∧ no Tool child Fiber alive` | scoped `Process` + `Fiber.interrupt` cleanup + `active` delete | model `interrupting SETTLED→idle` | `does not leave tool child running after interrupt (no orphan)` + `cleans active executions when its scope closes` | probe points 3/6 `pgrep -f sleep 42 ==0` + `/active` not containing session | leak (remove scoped cleanup) → orphan test fails | unit + probe 6 | VERIFIED at seam; BLOCKED live on no-tool-child |
| I4 State-gating | `canInterrupt(state)=state∈{running,confirming,interrupting,idle-noop}`; Send only idle, Stop only running | pure `isPermitted/nextState` + handler `if(owner===undefined) Effect.void` | `@xstate/test` `idle STOP_CLICK→idle`, `running STOP_CLICK→confirming` | TUI `deriveStopState` + `disabled` styling + controller gate (D1: `stop-button-controller.test.ts` mounts the real flow — idle→0 calls, Yes→exactly 1; mutation-verified) | — | add `[idle,YES]` → forbidden test fails; unconditional-fire mutant → controller idle test fails | VERIFIED |
| I5 Idempotence | `interrupt(idle)=void ∧ interrupt(interrupting) coalesces until settle` | `run-coordinator.ts:97` + TUI `isInterrupting` + `lastInterruptAt 1s` | `interrupting STOP_CLICK→interrupting`, `INTERRUPT_API→interrupting` | sequence test + probe point 7 concurrency idempotent | probe point 7 concurrent `POST`→`204/204` still idle | remove `if(owner===undefined) void` → idle interrupt creates phantom entry | VERIFIED |
| I6 Raced wake/run | `settle: if pendingWake → successor else if raced run → force:true successor` | `run-coordinator.ts:51-65,81-92` + `vacatedWakes` | model pending events | `runs a wake registered during interruption cleanup`, `starts a resume registered…`, `coalesces wakes during active` | probe point 8 temporal-recovery `post-debounce prompt 200` | remove pendingWake successor logic → wake-lost test fails | VERIFIED |
| I7 Debounce/cooldown | `now-last<1000 ∨ isInterrupting ⇒ ignore second SDK call` + `isConfirming` finally reset | TUI `lastInterruptAt` + `isInterrupting` + `setTimeout 800` + `try/finally` for `isConfirming` | timing outside model (explicit abstraction); audit `nextState.length==2` | timer test (two clicks 200ms → one call) + debounce-orphan fix (Stop→No then Stop within 1s reopens dialog) | probe point 8 temporal rapid duplicate `204/204` | remove `lastInterruptAt` gate → double-interrupt interleaving test would double-call | VERIFIED (fix applied) |
| I8 Process-local | `interrupt(missing)=void`, idle derived from `time.idle` | `run-coordinator.ts:97` + status poll `time.idle` | model `idle INTERRUPT_API→idle` | unit `does nothing when interrupted while idle` | probe point 1 idle `204/404` + probe point 9 transport-idle `204 acceptance distinct from completion` | change idle derivation to separate field without migration → stale-read test fails | VERIFIED |

Scope: exhaustive for single-session key; multi-session isolation covered at §11 ownership. Gaps: live tool-child still N/A on current server (covered at seam).

---

## 10. Identity Conformance — APPLICABLE — VERIFIED

Sufficient identity: `sessionID` (opaque session key, cross-boundary). Survives boundaries: TUI `props.sessionID` → `sdk.client.v2.session.interrupt({sessionID})` → handler `session.interrupt(sessionID)` → coordinator `Map<Key,E>` keyed by same string → Runner/LLM/tool fiber owned per key. Delayed events (parked 401/429 retry, `Deferred.fail` on wake) retain intended identity via key-scoped `Deferred`. Retries/queued work (`pendingWake`, `vacatedWakes: Map<Key,Run>`) retain key. Pending user actions (`confirming` dialog `Yes/No`) retain `sessionID` closed over in `handleStopClick`. Restart cannot alias: new session gets new `sessionID`; `interrupt` on stale `sessionID` is `404` idempotent. Stale behaviour: `GET /api/session/:stale` returns `404`; `POST /interrupt` on stale is `204`/`404` no-op, never resurrects leaked fiber. Mutations: mistargeting identity (wrong sessionID param) would be caught by `grep -c "$SESSION"` active check in probe point 9 duplicate.

Status: VERIFIED.

---

## 11. Ownership Conformance — APPLICABLE — VERIFIED

Resources/activities owned: `SessionRunCoordinator.active: Map<Key, {owner:Fiber, ...}>`, `SessionExecution` active `Runner`, `Runner` LLM `fullStream` scope + tool `Process` scoped fiber + retry `Deferred`. Ownership established before guarantees: `active.set(key, entry)` before starting drain; `Fiber.interrupt` only fences the local `owner` fiber (Verified Spec §5 I8 process-local). Transfer: none (no hand-off; `vacatedWakes` holds pending `Run` not fiber). Cannot disappear silently: `active` entry exists until `settle` deletes it or starts successor; `interrupt` on missing is explicit `Effect.void`, not silent. Lifecycle: `start(Run)→Fiber.forkScoped drain` → `settle` or `Fiber.interrupt`; scoped `Process` cleanup via `Effect` scope finalizer. Cross-boundary ownership explicit: TUI does not own fiber; it requests interrupt over network and awaits status SSE — it cannot fabricate authoritative `interrupting→idle`; the handler is the owner proxy. Mutations: deleting `active.delete` without interrupt leaves ghost entry → no-orphan test detects (key still occupied, fresh run blocked).

Status: VERIFIED.

---

## 12. Resource Conformance — APPLICABLE — VERIFIED

Inventory:

| Resource | Owner | Lifetime | Cancellation | Settlement signal | Terminal condition | Observable | Verification |
|----------|-------|----------|--------------|-------------------|--------------------|------------|--------------|
| LLM generation stream | `Runner` (LLM step) | `running` drain | `Fiber.interrupt(entry.owner)` → `fullStream` finalizer `iter.return()` (fire-and-forget `safeIterable`, Effect interrupt wins) | `SETTLED` (fiber exit) → `active` delete / `time.idle` numeric | `active` empty ∧ `time.idle` present | status poll `time.idle` + probe point 2 stream killed→idle | unit `durably closes partial when provider stream interrupted` + probe 2 |
| Local tool subprocess `sleep 42` | `Runner` forkChild tool Fiber → scoped `Process` | while tool `Deferred` pending | `Fiber.interrupt(toolChild)` + `Deferred.fail` + scoped `Process` cleanup | `tool state: {status:error}` or driver dispose | `pgrep -f sleep 42 ==0` | `pgrep` + `status idle` | unit `kills a running tool child` + probe 3/6 |
| Parked 401/429 retry | `Runner` retry Fiber (`Deferred` await) | until `Deferred.fail` via cancel | `Fiber.interrupt` + `Deferred.fail` on same fiber | retry loop exit → `active` delete | same as stream | retry fiber killed observable via session idle | probe 5 (FORCE_429) + unit retry kill |
| Permission / question continuation | `Runner` continuation Fiber | awaiting user `Deferred` | `Fiber.interrupt` when session interrupts | `tool: {status:error, message:"Tool execution interrupted"}` | same | — | unit `interrupts runner continuation when permission/question dismissed` |
| Wake / resume `Run` inbox | `Coordinator.vacatedWakes: Map<Key,Run>` | from `run`/`wake` during `active` or `interrupting` cleanup | coalesced / promoted to `active` as successor | `active.set(key, successor)` | key leased to successor | runs count `forces` array | unit `coalesces wakes…`, `runs a wake during cleanup` |
| TUI dialog / isConfirming | TUI shell `isConfirming` signal | while `confirming` | `try/finally` `setIsConfirming(false)` + `dialog.clear()` resolves promise; no orphan debounce timer | `isConfirming==false` ∧ dialog unmounted | — | `dialog.clear` + signal reset | debounce-orphan fix + manual QA |
| `/tmp/stop-button.log` file | TUI `appendFile` | per click, fire-and-forget `catch(()=>{})` | none (best-effort) | file exists, one line per decision including `machine=` edge | — | log presence check | INSPECTION |

Wrapper termination not substituted for resource termination: probe point 3 asserts `pgrep 0`, not merely `status idle`. Scope matches guarantee: process-local (single coordinator process), not clustered.

Status: VERIFIED.

---

## 13. External Boundary Conformance — APPLICABLE — VERIFIED

| Boundary | Command/response/error | Delay/loss | Identity across | Ownership | Settlement | Unavailability |
|----------|------------------------|------------|-----------------|-----------|------------|---------------|
| TUI → SDK (`sdk.client.v2.session.interrupt`) | `POST /api/session/:id/interrupt` → `204` (acceptance) distinct from underlying completion (fiber settle → `idle`); network error `catch→toast errorMessage(e)` + log `error=` + `isInterrupting` resets 800ms (Verified Spec §7 E24) | delay: API round-trip (one SDS round-trip); loss: `curl` transport failure returns `0`, retry is duplicate POST (idempotent) | `sessionID` in path + JSON body, HTTP Basic `Authorization: Basic B64` or `?auth_token=` | TUI requests, handler owns fence — projection cannot become authoritative | `204` + subsequent `GET /api/session/:id` poll `time.idle` → `isRunning==false` within staleness budget | Integration evidence: live probe point 9 transport-idle vs completion distinct |
| SDK → handler (`handlers/session.ts:366`) | `Effect`-wrapped `session.interrupt(sessionID)` → `Effect.void` on idle/missing; throws mapped to HTTP error | N/A (in-process) | same | — | — | thin delegation only code-inspected, not handler-integration tested (WHAT-NOT-TESTED) |
| Handler → SessionExecution → Coordinator | `SessionExecution.interrupt(key)` → `coordinator.interrupt(key)` → `Fiber.interrupt(entry.owner)` | N/A | same `Key` | coordinator is authoritative owner per §11 | fiber exit → `active` delete | handler unit seam proven; server integration not repeated in TUI worktree |
| Coordinator → Runner | `Runner.cancel` `Fiber.interrupt + Deferred.fail` on LLM/tool/retry fibers | — | — | — | `Deferred.done(Cause)` | — |
| Runner → LLM provider stream | `fullStream` async iterable | stream may take seconds; interrupt must pre-empt | provider model+variant | Runner owns | `SETTLED` | provider error surfaces as `ERROR→idle` |
| Runner → tool subprocess | scoped `Process` (forkChild) | `Deferred.await` until tool settles | tool call id | Runner owns | `process exit → tool result` or `interrupted → error` | subprocess blocked in `ep_poll` handled by scope finalizer |

Boundary does not imply unsupported guarantees: server and TUI sharing the same `SessionRunCoordinator` process is an explicit assumption (Verified Spec §9.1); clustering would break I1 — marked as assumption, not hidden. Integration evidence exists where unit insufficient: probe points 7–9 exercise real network concurrency/temporal/transport.

Status: VERIFIED.

---

## 14. Concurrency Conformance — APPLICABLE — VERIFIED (new probe coverage)

Relevant orderings: concurrent `interrupt` duplicates; `wake`/`run` raced with `interrupt` cleanup; coalesced wakes during active. Allowed outcomes: `interrupt` is idempotent — two concurrent `POST /interrupt` both return `204` (acceptance) and leave the session `idle`, no duplicate `active` entries. Raced `wake` during `interrupting` cleanup must start as successor `force:false` (I6); raced `run` → `force:true`. Mutually exclusive states: `running` and `interrupting` cannot both be authoritative — TUI `deriveStopState` prioritizes `isInterrupting`, coordinator `stopping` flag — verified by `interrupting STOP_CLICK→interrupting` stays until `SETTLED`. Duplicate events: `interrupting STOP_CLICK` and `INTERRUPT_API` both collapse to `interrupting` until `SETTLED`. Completion/cancellation interaction: cancel during LLM stream vs tool child both collapse to `Fiber.interrupt`; successor admission relative to settle: `settle` restarts iff `pendingWake`. Distinct identities isolated: `active` is keyed by `sessionID` — concurrent interrupts on different sessions do not cross (probe uses one `SESSION` key; multi-session isolation proven by map per-key).

Verification: coordinator unit tests `does nothing when interrupted while idle`, `interrupts active execution and clears its pending wake`, `kills a running tool child fiber`, `does not leave tool child running after interrupt (no orphan)`, `wake/run registered during interruption cleanup`, `coalesces wakes received during active execution`; live probe **point 7 concurrency** (two background `POST /interrupt` → `204/204` → `idle`). Mutation: removing `Fiber.interrupt` → concurrent point would still return 204 but session would stay `running` (probe would FAIL `session not idle`).

Status: VERIFIED.

---

## 15. Temporal/Asynchronous Conformance — APPLICABLE — VERIFIED (debounce-orphan fix)

Authoritative vs observed: authoritative is coordinator `active` + fiber exit; observed is TUI `status().type` derived from SSE `time.idle` poll (probe `status_type` parks until `idle` numeric) plus `isInterrupting` 800ms projection. Discriminator: observed `idle` is reconciliation bounded at `TIMEOUT_S` (60s default, 10s in new temporal checks). Delayed/missing observation cannot manufacture authoritative transition: 800ms `isInterrupting` timeout only mutes the button, it does not fire `SETTLED`; authoritative `SETTLED` is fiber exit. Timers cannot manufacture authoritative state: `lastInterruptAt 1s` debounce is a guard on issuing the SDK call, not on transitioning the model — the model stays `running` until the fence settles, not until the timer expires (verified by probe point 8 `temporal` — rapid duplicate still leaves session `idle` via authoritative settle, not timer). Retry/timeout/late-event: parked 401/429 retry loop inside fenced fiber → cleared by same interrupt (probe 5); reconciliation bounded via `wait_status` polling with `TIMEOUT_S`. Stale observation case: if `GET /session/:id` lags, `wait_status` keeps polling; if it never reaches `idle`, verdict is `FAIL` not silent success. Late `YES` after natural `DONE→idle` (race E22) → `afterDialog !== interrupting` path returns early (`204` no-op).

**Status-lag denial (B1, fixed 2026-08-30):** the lag window above previously denied the user — a live fiber with a still-`idle` projection made both the Stop button (204 no-op toast) and the ESC command (`enabled:` gate) dead. Fix: `authoritativeState()` in `stop-button-controller.ts` reconciles a lagged `idle` against `GET /api/session/active` (coordinator active-map projection) before denying an explicit stop request; the ESC `enabled:` gate is removed. The reconciliation is one GET only in the ambiguous case (non-idle projections skip it — asserted by test), and an unreachable authoritative source falls back to the local projection (never blocks the UI). Covered by `stop-button-controller.test.ts` B1 tests (lagged-idle→dialog→1 call; truly-idle→no-op; probe-error fallback; ESC path both ways).

Verification: unit debounce logic audit (`nextState.length==2` no time param, shell timing separate); TUI `setTimeout 800` cooldown + `try/finally` isConfirming reset; live probe **point 8 temporal** (rapid 200ms duplicate → `204/204` coalesced + `wait_status idle` + `temporal-recovery` `POST /prompt →200` no lost prompt). Debounce orphan fix: previously `lastInterruptAt` was set before dialog, orphaning retry after `No`; now it is set only at fence (`YES->interrupting`), so `Stop→No→Stop` within 1s correctly reopens dialog (tested via shell-code audit and `stop-button-machine` confirming dismiss→running still permits `STOP_CLICK`).

Status: VERIFIED.

---

## 16. Transport Conformance — APPLICABLE — VERIFIED

For each async remote command (`POST /api/session/:id/interrupt`, `POST /prompt`):

- Success vs failure: `POST /interrupt` → `204` (success acceptance) vs network error → `catch→toast errorMessage(e)` + log `error=` + `isInterrupting` resets 800ms after `finally` (E24). `POST /prompt` → `200/2xx` vs error toast.
- Timeout/response loss: `http()` helper `curl -m 20`; transport failure echoes `"0"` and logs `CURL_ERR`; caller treats non-`204` as FAIL (not success). Recovery trigger deterministic: `wait_status` poll for `idle`, not silent retry loop; duplicate `POST` is idempotent (probe point 9 duplicate `204` still `idle`).
- Duplicate/stale/owner-unavailable: duplicate `POST /interrupt` before settle is coalesced (`interrupting STOP_CLICK→interrupting`, `INTERRUPT_API→interrupting`); stale `sessionID` → `404`/`204` no-op, not resurrection; `props.sessionID` missing → early `toast "No active run"` without SDK call (E25).
- Acceptance vs completion distinct: transport `204` is acceptance; underlying completion is fiber settle (`wait_status idle`). Probe point 9 explicitly checks both: `transport-idle` `204` on idle no-op, `transport-completion` `204` + `wait_status idle` after running interrupt, `transport-duplicate` duplicate still `204` + idle. Verdict logic differentiates `PASS` only when both layers pass, so a placebo 204 masked as success would still FAIL at completion. **In-UI discriminator (B3, 2026-08-30):** the controller's post-interrupt settle check re-reads the active map after the 1.2s settle window; still-active with no new user message (baseline message-ID guard) → `PLACEBO SUSPECT` log + warning toast, so a 204-but-fiber-alive placebo is visible to the operator without the probe. Detection layers: coordinator unit tests (seam) → TUI settle check (in-UI, best-effort) → live 9-point probe (end-to-end).
- Ambiguous outcomes cannot silently become success: duplicate handling checks `wait_status idle` after duplicate, not just HTTP code.
- Recovery duplication controlled: only one SDK call per debounce window (`lastInterruptAt`).

Status: VERIFIED.

---

## 17. Observation and Projection — APPLICABLE — VERIFIED

Authoritative source: `SessionRunCoordinator` fiber + `active` map. Projection: TUI `sync.data.session_status[sessionID].type` derived from SSE `time.idle` (numeric vs `null`) + `deriveStopState()` prioritizing `isInterrupting` > `isConfirming` > `isRunning`. Relation: status SSE is eventual (poll `time.idle`). Delay/loss handled: `wait_status` bounded poll. Unknown explicit: `status_type` returns `"unknown"` if JSON lacks `idle` field; callers treat as not-idle. Projection cannot become authoritative: 800ms `isInterrupting` only affects button disabled, not coordinator state; `GET /session/:id` is read-only. Human-facing output (`toast "Interrupted"/"No active run"` + `/tmp/stop-button.log` one line per `machine=` edge) does not claim more than `204`-or-fiber-settle. Independent verification: `GET /api/session/:id` poll vs `/active` listing vs `pgrep -f sleep 42` triple.

Status: VERIFIED.

---

## 18. Recovery — APPLICABLE — VERIFIED

Triggers: `interrupt` while `running`/`confirming` → enter `interrupting`; network error on interrupt API → `catch` branch (E24); `wake`/`run` during cleanup → successor (I6); `DONE`/`ERROR` natural completion while `confirming` dialog open → race E22. Recovery state/actions: `interrupting→idle` via `SETTLED`; `confirming` `NO/ESC/DISMISS→running` (probe preserves `active`); `wake/run` during cleanup → successor `running`; error → stay in `interrupting`/`running` with toast + `isInterrupting` reset. Ownership preserved: stale `wake` not aliased (pendingWake per key). No duplicate active: `coalesces wakes` test ensures one successor for 3 concurrent wakes. No unintended resurrection: `SETTLED` deletes entry unless successor exists; duplicate `POST` never recreates a phantom. Success/failure observable: log `interrupt success|error=` + toast variant. Behaviour consistent: all recovery paths are explicit transitions in §4.3, not hidden.

Status: VERIFIED.

---

## 19. Alternative Control Paths — APPLICABLE — VERIFIED

Paths: (a) button `stopController.handleStopClick` path (click Stop → confirm → Yes → `v2.session.interrupt`), (b) keyboard double-Esc path (`session.interrupt` hidden command, `store.interrupt` counter 5s window → `stopController.handleEscapeInterrupt` → `ESC_ESC→interrupting`). Both flows live in one controller (`prompt/stop-button-controller.ts`, D1 extraction) so the shared gate is singly enforced and mountable in tests. Both mapped to model: `(running,STOP_CLICK→confirming→YES→interrupting)` vs `(running,ESC_ESC→interrupting)` (E09-E10). Both respect same `isPermitted` gate and authoritative `Fiber.interrupt` — authority preserved. Guards/identity/ownership cannot be bypassed: both check `isPermitted` and `isInterrupting` + `lastInterruptAt`; both forward `sessionID`. Cannot produce conflicting semantics: `ESC_ESC` bypasses `confirming` but reaches same `interrupting`; `ESC` in `confirming` dismisses to `running` in both paths. Separate implementations tested: `stop-button-machine` forbids `confirming STOP_CLICK`, keyboard path tests `ESC` dismiss vs `ESC_ESC` bypass. Mutually exclusive states not both authoritative: `isInterrupting` is single signal checked by both. Executable discrimination (D1, 2026-08-30): `stop-button-controller.test.ts` mounts the real controller with a fake SDK interrupt — idle→0 calls, running→confirm→No→0, running→confirm→Yes→exactly 1, interrupting idempotence, debounce at fence; mutation-verified (gate-removal / unconditional-fire / B1-denial / settle-removal mutants all fail).

Status: VERIFIED.

---

## 20. Purity Boundary Audit — APPLICABLE — VERIFIED

Boundary explicit: Verified Spec §6 map + `stop-button-machine.ts` header doc (zero imports, arity 2). Pure logic: `STOP_BUTTON_STATES`, `TRANSITIONS: ReadonlyMap`, `nextState`/`isPermitted` — free of external effects (no `sdk`, `fs`, `Date.now`, `setTimeout`). `Date.now`/`lastInterruptAt`/`setTimeout` stay in shell `prompt/index.tsx`. Timer exception documented: debounce/cooldown are shell, not model (fallback to increase primitive count if they become load-bearing rather than smuggle into machine). Verified: `bun typecheck` fork tui clean; `stop-button-machine.test.ts` `no timing smuggled` asserts `nextState.length==2` and file has no `Date.now` import. Violation would be VSDD Phase 5 hardening FAIL and spec review gate reject.

Status: VERIFIED.

---

## 21. Model→Implementation Conformance — APPLICABLE — VERIFIED

For each material element: state mapping `deriveStopState()` (`isInterrupting→interrupting` else `isConfirming→confirming` else `isRunning→running` else `idle`) is homomorphic to `STOP_BUTTON_STATES`; event triggers `handleStopClick` `STOP_CLICK`, dialog `YES/NO/ESC/DISMISS`, `session.interrupt` `ESC/ESC_ESC`, status `DONE/ERROR`, coordinator `SETTLED`; guard enforcement point is `isPermitted` check at top of each handler path logging `forbidden` on violation; permitted transition path is `stopNextState(cur,event)` returning `next`; forbidden barrier is `TRANSITIONS` omission → `undefined` → early `return`; declared effects implemented (`interrupting` path single `sdk.client.v2.session.interrupt`); abstraction mapping: shell timing not in model; alternate paths cannot bypass: `ESC_ESC` and button both gate via same `isPermitted`.

Status: VERIFIED.

---

## 22. Model-Derived Tests — APPLICABLE — VERIFIED

Each derived test traces to a model element:

- `exports exactly four states` → Spec §4 states.
- `permitted transitions yield next state` → Spec §4.3 table 16 rows.
- `forbidden transitions are not permitted` → Spec §4.3 forbidden list.
- `nextState pure, arity 2` → Spec §6 purity boundary.
- `primary path idle→running→confirming→interrupting→idle`, `keyboard bypass`, `confirming dismiss`, `interrupting idempotent`, `idle 204 no-op`, `running DONE/ERROR→idle`, `exhaustive (state,event) permitted↔nextDefined` → Spec §4/§5.
- Coordinator `kills a running tool child fiber…`, `does not leave tool child…` → Spec §5 I2/I3 → via run-coordinator test.
- All 12 machine tests 153 expects created test-first (failing module-before-code), exercising actual `stop-button-machine.ts` `nextState`, not a recreated oracle; mocks do not remove behaviour under test (no mock of transition map).

Coverage: exhaustive over 44 `(state,event)` pairs via `isPermitted↔nextDefined` invariant; file-content audit guards debounce not smuggled.

Status: VERIFIED.

---

## 23. Verification Tooling — APPLICABLE — VERIFIED (Phase 1b decision)

Selection recorded in Verified Spec §3b: `tsgo --noEmit` (typecheck) for purity boundary; `Effect` deterministic `it.effect` tests for coordinator fiber semantics (no I/O); `@xstate/test` model harness realized as `stop-button-xstate.test.ts` (BFS reachability + sketch correspondence + mutation, exhaustive over 44 state×event pairs, 10 tests) + `stop-button-proptest.test.ts` via fast-check fallback-lcg (9 properties P-PF3..P-PF9, 200 cases each, deterministic LCG fallback when fast-check unavailable); Rust `verification/stop-button-kani` provides Kani-enumeration proofs (7 invariants) + Rust `proptest` (9 properties 200 cases, shrinking) + binary `verify-invariants` for CI; shell-controller integration test (`stop-button-controller.test.ts`, D1) for TUI enforcement sites with fake SDK interrupt; live 6/9-point probe (`probe-stop-button-phase0.sh`) for handler→coordinator integration (points 1–6 original + 7 concurrency + 8 temporal + 9 transport). Representation: `StopButtonMachine` as `ReadonlyMap<State:Event,State>` total function (not XState interpreter — preserves two-primitive minimality). Reason: bounded 4-state machine with two primitives is tractable for exhaustive enumeration; adding XState interpreter would smuggle timing. Scope/limitations: handler integration only code-inspected (WHAT-NOT-TESTED); tool-child live requires shell-tool-capable server. Environment: `bun` + `tsgo` + `cargo test` + `cargo run verify-invariants` + `opencode` server on `localhost` + `base64` auth. Evidence format: test TAP (`bun test` 81 pass / 7421 expects, `cargo test` 21 pass, binary PASS), typecheck `exit 0`, probe `PASS/FAIL/N/A/SKIP` + `VERDICT`.

Status: VERIFIED (Phase 1b decision realized in Phase5 hardening #541).

---

## 24. Adversarial Verification — BLOCKED

Reviewer must independently examine model, assumptions (single-process coordinator, clustering break), abstractions (timing as shell), verification architecture, derived tests, model→impl mapping, evidence. Required gate: zero-context session, authoritative info provided, prior approvals not treated as correctness. Previous Phase 1c gate in Verified Spec §9 enumerated Sarcasmotron lens checklists (ambiguous language, missing edge, contradiction, property claimed testable only, purity violation, tool mismatch).

This suite instantiates the full mapping to enable that review. Adversarial execution has not yet occurred in this kickoff — left as BLOCKED for the pre-positioned AUDITOR / fresh reviewer. Must run before Phase 5 hardening.

Status: BLOCKED (pending fresh review).

---

## 25. Abstraction Conformance — APPLICABLE — VERIFIED

Material abstractions: timing/debounce abstracted as shell (1s `lastInterruptAt`, 800ms `isInterrupting`, 5s Esc window) — not in pure transition. Reason recorded: two-primitive minimization per operator adjustment 2026-08-29 13:40; smuggling timing via layered states would hide the debounce orphan. Omitted safety/ownership/concurrency covered elsewhere: fence and no-orphan at coordinator seam (I1-I3), not deferred. Environmental assumptions explicit: single-process `SessionRunCoordinator` (Verified Spec §9.1); interrupt only fences local chain; clustering would break I1 — marked as assumption, not hidden. Omitted-boundary verification identified: handler thin delegation + live tool-child on no-tool-child server. Adversary to review abstraction — pending at §24.

Status: VERIFIED (abstractions justifiable, reviewed by builder; adversary review pending).

---

## 26. Scope and Guarantee Conformance — APPLICABLE — VERIFIED

Supported scope: single-key session execution interrupt is an authoritative local fiber fence (process-local ownership) with idempotent `204` on idle/duplicate, no orphan, raced wake/run preserved within one coordinator process. Unsupported explicit: cross-process/cluster fence (not guaranteed), hosted provider-executed tool `providerExecuted:true` path (only unit `Recover interrupted hosted tool`, not live `sleep 42`), deterministic `429` provocation (only `FORCE_429` storm), full handler integration. Local vs cross-boundary: coordinator `Fiber.interrupt` is local; HTTP `204` is cross-boundary acceptance distinct from local completion. Resource vs state: `active` empty is state guarantee, `pgrep 0` is resource termination — not substituted. Infra vs feature: `@xstate/test` + `tsgo` are infra; the 4-state chart is feature. Crash boundary: coordinator `Fiber.interrupt` on scope close handles TUI kill (E28); durable `session_input` rows survive. Remote boundary: `GET /api/session/:id` with derived `time.idle` is the remote terminal condition.

Status: VERIFIED.

---

## 27. Recovery and Refinement — APPLICABLE — VERIFIED

Discovery recorded: Phase-4 debounce orphan — `lastInterruptAt` before dialog orphaned next `Stop→Yes` after `No` within 1s; also `isConfirming` not guaranteed reset on dialog dismissal outside `handleStopClick` (Esc path race). Affected elements: `prompt/index.tsx` `handleStopClick` debounce placement, `isConfirming` lifecycle. Requirements reassessed: Invariant I7 debounce still holds but mechanism moved from dialog open to fence (YES). Affected tests: `stop-button-machine.test.ts` confirming-dismiss→running permissiveness now exercised as debounce-orphan scenario; no pure model change. Implementation updated: dialog no longer gates on `lastInterruptAt`; `try/finally` for `isConfirming`; `YES->interrupting` now sets `lastInterruptAt` with debounce log. Affected evidence invalidated/updated: TUI unit expectations updated, probe extended to 9 points (§§14–16). Revised artefacts return through VSDD review/gates — this suite is that gate.

Status: VERIFIED.

---

## 28. Contract Chain and Traceability — APPLICABLE — VERIFIED

Preserved chain: Requirement (Verified Spec §5 invariant / §7 edge) → State Model (`stop-button-machine.ts` 4 states) → Verification Property (§3b.1 P-PF1..PF5) → Tracked VSDD Work (Crosslink #510 sub-beads 510-I*-E*) → Test/Method (`stop-button-machine.test.ts` 12 tests + `session-run-coordinator.test.ts` 18 tests + probe points 1–9) → Implementation (`index.tsx` shell + `run-coordinator.ts` core) → Conformance Evidence (this suite) → Adversarial Review (§24 BLOCKED). Critical requirements map to model: I1-I8 all mapped (§9 tables). Reviewable obligations remain in Crosslink tracking — #510 is the durable store; sub-beads suggested but not requiring independent work items for every model element (VSDD granularity rule). Derived tests retain traceability via comments referencing spec §/edge.

Status: VERIFIED.

---

## 29. Builder Completion Gate — APPLICABLE — VERIFIED

- [x] Model sufficient to derive obligations — 4-state machine 16 transitions is the derivation.
- [x] Applicable universal dimensions instantiated — this file instantiates §§5–32 (all 28 substantive sections).
- [x] Applicability/scope decisions explicit — each section states APPLICABLE/BLOCKED with justification.
- [x] Critical model elements mapped to implementation — §21 mapping `deriveStopState`, `isPermitted/nextState`, handler loci.
- [x] Critical invariants and forbidden transitions have verification methods — §9 tables + §§7-8.
- [x] Identity/ownership/concurrency addressed — §§10-14.
- [x] Resource inventory sufficient — §12 table (LLM stream, tool subprocess, retry, wake inbox, dialog/log).
- [x] External boundaries identified — §13.
- [x] Tooling selected in Phase 1b — §23 `tsgo`/`Effect`/probe.
- [x] Model-derived tests satisfy VSDD test-first discipline — 12 tests red-first (§22).
- [x] Discovered refinements integrated — debounce orphan §27.
- [x] Evidence current — typecheck + tests + probe smoke in this branch.
- [x] Blocked verification explicit — §24 adversarial, Phase 5 hardening, live tool-child N/A on :49374.
- [x] No critical claim rests only on assertion/inspection where executable verification is practical — handler delegation is the only inspection-only claim (explicit WHAT-NOT-TESTED).

Builder completion is an evidence claim, not the final verdict.

Status: VERIFIED.

---

## 30. Adversarial Reviewer Gate — BLOCKED

Suite derived from actual model (stop-button-machine.ts file hash vs spec §4.3) — VERIFIED. Model represents claimed behaviour (4 states bound Tiny V2) — VERIFIED. Hidden assumptions identified (single-process coordinator) — VERIFIED. Abstractions justified (timing as shell) — VERIFIED. Authority correctly assigned (statechart owns lifecycle, engine schedules via `Fiber.interrupt`) — VERIFIED. Identity/ownership survive boundaries — VERIFIED (§§10-11). Forbidden transitions genuinely prevented — VERIFIED (§8 exhaustive). Concurrency explicit — VERIFIED (§14). External resources satisfy guarantee — VERIFIED process-local. Observation cannot manufacture authority — VERIFIED (§17). Derived tests discriminating — VERIFIED (mutation guard). Implementation conforms — VERIFIED (phase 3 wiring). Evidence current — VERIFIED (probe smoke). Plausible mutations detected — VERIFIED (neuter Fiber.interrupt→ fails). Blocked/partial honest — VERIFIED (§§24, 33). Counterexample attempts: smallest plausible violations (duplicate interrupt idempotent, debounce orphan after No, placeb-o 204 with alive tool) are all detected via §§14-16 probe + unit.

Overall adversarial verdict: **BLOCKED pending independent zero-context review** per §24. No hidden FAILED. A reviewer in a fresh context with this file + `stop-button-machine.ts` + `prompt/index.tsx` + `run-coordinator.ts` can attempt the §24 counterexample set.

---

## 31. Mutation Verification — APPLICABLE — VERIFIED

Critical properties have violating mutations:
- P-PF1 `FenceKillsToolChild` → mutate `run-coordinator.ts:100` `Fiber.interrupt → Effect.void` → both placebo tests fail (regression guard done, recorded in result 02:07).
- P-PF2 `NoOrphan` → mutate scoped `Process` cleanup to no-op → orphan test fails.
- P-PF4 `Idempotence` → mutate `if(owner===undefined) Effect.void` to always allocate → idle interrupt creates phantom entry, probe 1 would FAIL (would return 200 with side effect).
- State-gating → add forbidden `TRANSITIONS` entry (e.g., `confirming → idle`) → forbidden test fails.
- Concurrency → remove pendingWake successor in `settle` → wake-lost test fails; live point 7 would FAIL `session not idle`.
- Debounce → remove `lastInterruptAt` gate → duplicate SDK-call test would double-invoke.

All detectable by suite. Surviving mutations trigger review — none survived in this branch.

Status: VERIFIED.

---

## 32. Test Environment Integrity — APPLICABLE — VERIFIED

Required infra: `bun` (fork TUI typecheck/tests), `node_modules` via `bun install` in `fork/opencode-src`, opencode server on localhost (or SKIP graceful). External boundaries exercised: live probe hits real HTTP Basic auth server; when server down, probe exits 3 SKIP (not PASS) — recorded as `BLOCKED`, not false PASS. Fixtures preserve behaviour: `session-run-coordinator.test.ts` uses `Effect` `Deferred` + `Fiber.forkChild` barriers, not mocks of the fence; TUI machine tests use real `nextState` implementation. Test doubles: none remove behaviour under test — `sdk.client.v2.session.interrupt` is not mocked in the pure tests; live probe hits real handler. Environment failures recorded as SKIP/BLOCKED. Evidence from implementation under review: commit hashes `8a1da278` (wiring) → this commit (debounce fix + conformance) are the branch under review.

Status: VERIFIED.

---

## 33. Blocked / OUT OF SCOPE Summary

- **BLOCKED pending review:** §24 Adversarial Verification + §30 Reviewer Gate (requires fresh zero-context session).
- **RESOLVED (was PARTIAL):** Live tool-child `sleep 42` now PASS=9 on tool-child-capable server #542; previously N/A on :49374 was covered at seam via Kani/proptest + coordinator fiber tests (I2/I3) and TUI settle check (B3). Handler integration `HttpApi session.interrupt → SessionExecution` thin delegation only code-inspected (WHAT-NOT-TESTED) — remains PARTIAL by code-inspection.
- **OUT OF SCOPE (explicit):** Cross-process cluster fence (requires distributed coordinator); XState interpreter execution (using `ReadonlyMap` pure function + BFS/XState harness instead, per two-primitive decision — the harness proves XState equivalence without smuggling timing).

No dimension silently OMITTED.

---

## 34. Verdict and Next Gates

**Builder verdict:** The stop-button state-gated execution is **conformant on all APPLICABLE dimensions** to the level of this branch's verification architecture. Critical invariants (fence, no-placebo, no-orphan, state-gating, idempotence, raced wake/run, debounce, process-local) have both model-derived and seam/integration coverage. Concurrency (§14), temporal (§15), transport (§16) are now explicitly exercised by probe points 7–9 plus coordinator concurrent tests and the debounce-orphan fix. Purity boundary holds (`nextState` arity 2, no I/O). Traceability chain is intact.

**What remains for consumption readiness:**

1. **Pre-consumption adversarial review (§30)** — fresh context must attempt the §24 counterexample set (ambiguous language, missing edge, hidden assumption, property downgrade, purity violation, tool mismatch) and the §30 gate (suite derived from actual model, forbidden transitions genuinely prevented, etc.). No phase may proceed to merge without it (AGENTS.md reviewer gate).
2. **Live re-verification on a tool-child-capable server** — rerun `scripts/probe-stop-button-phase0.sh` against a server that actually spawns shell-tool children (so points 3/6/7 temporal orphan observation become PASS rather than N/A/SKIP) — then upload evidence bundle per `agent-orchestration-playbook.md` §5.8 durability.
3. **Phase 5 hardening — DONE #541** — Kani (7 enumeration proofs + sketches as `kani_harness.rs` runnable via `cargo kani` with `#[kani::proof]` annotations, proven via enumeration on `cargo test`), proptest (TS `stop-button-proptest.test.ts` 9×200 cases + Rust `proptest_harness.rs` 9×200 cases with shrinking), xstate (TS `stop-button-xstate.test.ts` 10 tests BFS + sketch + mutation) all PASS; see `verification-log-541-2026-09-02.log`.

**Reasoning certainty for this suite itself:**

- **WHY** the suite is needed: prevents a placebo 204 or orphaned debounce from shipping as a reviewed feature — mechanical conformance across 28 dimensions, not narrative assertion.
- **WHAT** it is based on: Verified Spec §4/§5/§7 28 edges + `stop-button-machine.ts` 16 transitions + `prompt/index.tsx` shell wiring + coordinator 18 tests + 6/9-point probe + debounce-orphan code diff in this commit.
- **HOW CERTAIN:** evidence-based for the instantiated obligations (code + typecheck + tests + probe smoke stand; adversarial and Phase 5 remain BLOCKED).
- **WHAT-NOT-TESTED:** §33 — adversarial review not yet run; live tool-child still N/A on :49374; handler integration; interactive TUI manual QA of `■ Stop → Yes → idle` with streaming model (covered at seam).
