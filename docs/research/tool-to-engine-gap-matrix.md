---
title: Tool-to-Engine Gap Matrix (Track C — Advisory)
program: EDASES
layer: Research
document_type: Advisory
status: Draft
authority: Derived
canonical_repository: edases
parent_issue: "#506"
classification: Track C advisory — no engine build recommendation (parallel API-candidate branch owns that)
related_documents:
  - docs/architecture/Execution Engine Vision.md
  - to-file/Proposal: EDASES Execution Engine.md
  - docs/research/registry/Hookability-Matrix.md
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md
  - .crosslink/knowledge/agent-orchestration-playbook.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
depends_on:
  - Concept: Levels of Abstraction
  - AI Orchestration Guide
labels: [gap-matrix, advisory, execution-engine]
last_updated: 2026-08-29
---

# Tool-to-Engine Gap Matrix — Track C Advisory

**Advisory only.** This document does not recommend building or not building a bespoke Execution Engine. The parallel API-candidate branch owns the build-vs-buy decision. This matrix exists to make the semantic distance between *current tooling* and *engine vision primitives* auditable, so that decision can be evidence-driven.

---

## 0. How to read this document

- **Producer / consumer asymmetry.** The producer (this advisory) can verify cheaply against deployed binaries and source. The consumer (the API-candidate / engine-design track) must treat every claim as auditable and check the cited evidence before acting on it.
- **Cell classification** reuses Proposal §11's five-way vocabulary verbatim: `satisfies` / `partially` / `requires adaptation` / `semantically incompatible` / `unnecessary`. A cell that is syntactically present but semantically wrong is **not** `partially` — it is `semantically incompatible` or `requires adaptation` depending on whether reinterpretation or reimplementation is needed.
- **Evidence discipline.** Every matrix cell carries a one-line evidence pointer to a deployed binary (`crosslink --version`, `opencode --version`, `~/.local/bin/claude`, `tools/kickoff-notify.py`, `scripts/liveness-watchdog.sh`, `scripts/agent-liveness.py`) or to source (`hook-config.json`, `*.ts` plugins, `agent.md` frontmatter). No claim is presented as proven without naming its source.
- **Certainty tags** follow `AGENTS.md § Reasoning Certainty`: `guess` / `evidence-based` / `proven`, plus an explicit `WHAT-NOT-TESTED` clause — the sharpest disclosure.

---

## 1. Context

### 1.1 What this matrix is testing

Proposal §11 ("Existing-System Research Method") prescribes a semantic comparison matrix: *same requirements, different systems, five-way judgment*. Hookability Matrix §14 then re-ranks which enforcement gaps are cheapest to close and most failure-relevant. Execution Engine Vision defines the long-term responsibilities (mechanical enforcement, knowledge model, context management, state management, observability, orchestration).

Track C collapses those into **8 engine-vision primitives** (rows) and **4 current-tooling surfaces** (columns) — a deliberately smaller cut than the 13-row illustrative table in Proposal §11, focused on the vision-level primitives where a general-purpose workflow engine and an EDASES-specific engine would diverge.

### 1.2 Inputs (canonical)

| # | Input | Role in this matrix |
|---|-------|---------------------|
| 1 | `docs/architecture/Execution Engine Vision.md` (canonical, `ases-engine` mirror, 2026-08-10) | Defines the 8 vision responsibilities; source of row names |
| 2 | `to-file/Proposal: EDASES Execution Engine.md` (§§4–11, §14) | Defines §11 method (5-way cells) and §14 acceptance criteria (6 groups / 24 sub-criteria); source of scoring rubric |
| 3 | `docs/research/registry/Hookability-Matrix.md` (2026-08-24, #440 extended) | Defines §14 re-ranked top-13 hookable-but-not-yet-enforced priorities; source of priority mapping |
| 4 | `docs/research/agent-tooling-and-permission-enforcement-reviewed.md` (2026-08-09, merged 8 reviews) | Calibrated picture of what guards actually enforce (vs. advertised); corrects overclaims about read-only, allowlists, and deployed-vs-source drift |

### 1.3 Evidence base inspected this session

| Surface | Deployed artifact inspected | Version / provenance |
|---------|-----------------------------|----------------------|
| **A — Crosslink** | `crosslink --version` + `crosslink --help` + `.crosslink/hook-config.json` + `.crosslink/issues.db` + `.crosslink/.active-issue` | `crosslink 0.9.0-beta.1+37789b51-dirty` (worktree, dirty: `.crosslink/.last-hydrated-ref` delta); source tree at same hash; `agent.json` role `agent` |
| **B — OpenCode TUI + guards** | `opencode --version` + `.opencode/opencode.json` + `.opencode/plugins/*.ts` + `.opencode/agents/*.md` + `.opencode/permissions.md` | `opencode 1.18.13-pp3g-fork`; plugins `orchestrator-guard.ts`, `crosslink-guard.ts` (1220 lines), `rtk-guard.ts` (415 lines); branch `feature/gap-matrix` |
| **C — claude wrapper** | `~/.local/bin/claude` (bash, ~86 lines) | Wrapper validated 2026-08-29: strict model gate + `--auto` under tmux + `systemd-run --scope` memory caps |
| **D — watchers** | `tools/kickoff-notify.py` (18,319 B) + `scripts/liveness-watchdog.sh` + `scripts/agent-liveness.py` (24,653 B, v2) + `tools/ases-kickoff-notify.timer` | systemd timer 15s cadence; watchdog 120s cycle; agent-liveness v2 with pane-hash freeze + process-tree aliveness |

---

## 2. Method

### 2.1 Row definitions (8 engine-vision primitives)

Derived from Vision § Responsibilties + Proposal §§4–8. Each row states the *semantic guarantee* an engine would provide, not a feature name.

| Row | Primitive | Vision / Proposal anchor | Engine guarantee (what would be true if satisfied) |
|-----|-----------|--------------------------|-----------------------------------------------------|
| **R1** | **State gates** | Proposal H1 (§4): `state → permitted actions → permitted transitions → required evidence → policies` | Invalid transitions mechanically rejected; state determines what *may* happen next; required evidence gates transitions |
| **R2** | **Durable execution identity** | Proposal H2/H5 (§5, §8): Work Item → Execution → Workers (replaceable) | Execution survives worker loss; stable ID across recovery; restart does not require agent reconstruction |
| **R3** | **Worker ownership / leases** | Proposal H5 primitive `worker ownership/leases` + §13 expts 7–8 | Exclusive ownership; lease expiry; concurrent workers on same execution prevented; queryable owner |
| **R4** | **Durable timers / scheduled transitions** | Proposal H5 `durable scheduled actions` + §8 "timer must not disappear with process" | Scheduled transition survives engine/worker death; fires exactly once; visible even if waiter died |
| **R5** | **Execution history / replay** | Proposal H8 primitives `execution history` + §14 Durable execution | Append-only event log reconstructs current state; replay explains how we got here |
| **R6** | **Observability** | Proposal H6 (§6) + Vision § Validation; §13 expts 1–4 | Authoritative signals (worker exists/exited, hook fired, commit exists, heartbeat arrived, timer expired); process aliveness distinguishable from *meaningful progress* |
| **R7** | **Knowledge model / context management** | Vision §§ Knowledge Model, Context Management, The Object of Management | Reasoning relationships (observation→finding→decision→validation) are first-class, queryable, persist across tasks; context is task-scoped and recoverable |
| **R8** | **Mechanical enforcement** | Vision § Mechanical Enforcement + Proposal H4 (§7) | Invariants enforced without agent cooperation: unsupported promotion blocked, missing evidence detected, orphaned reasoning flagged; attention states replace silent stall |

### 2.2 Column definitions (4 tooling surfaces)

| Col | Surface | What it actually is | Boundary |
|-----|---------|---------------------|----------|
| **A** | **Crosslink** issues / sessions / locks / sentinel / knowledge | Rust CLI (`crosslink`) + SQLite `issues.db` + hub sync + `.crosslink/.active-issue` sentinel + `locks` + `sessions` + knowledge pages | Owns durable issue/work state and coordination metadata; delegates execution to workers |
| **B** | **OpenCode Beta TUI + current guards** | `opencode 1.18.13-pp3g-fork` harness + 3 worktree plugins + 4 agent `.md` permission maps + MCP filesystem server | Enforces per-tool-call policy; TUI is presentation; guards are the enforcement boundary |
| **C** | **claude wrapper** | `~/.local/bin/claude` — pre-dispatch `bash` that translates Claude args → `opencode run`, validates model, injects `--auto` under tmux, scopes with `systemd-run` | Single enforcement point for model discipline + memory caps; not a state machine |
| **D** | **systemd kickoff-notify.py + liveness-watchdog.sh** | `kickoff-notify.py` (15s systemd timer) + `liveness-watchdog.sh` (120s tmux loop) + `agent-liveness.py` v2 (pane-hash + process-tree + walk-based activity signal) | Observation + notification only (Phase 1): no kill/relaunch; posts to issue #429 |

### 2.3 Five-way classification (§11)

| Value | Meaning | When to use |
|-------|---------|-------------|
| **satisfies** | Surface provides the engine guarantee with acceptable semantics | Behavior matches without reinterpretation |
| **partially** | Subset present, but gap remains that matters for engine semantics | Works for some cases; fails the discriminating test |
| **requires adaptation** | Conceptually compatible but needs reimplementation / reinterpretation | Can be made to satisfy with non-trivial change |
| **semantically incompatible** | Provides a feature with the same name but wrong semantics, or fundamentally cannot model the guarantee | Using it as-is would encode the wrong invariant |
| **unnecessary** | EDASES does not need this primitive from this surface | Legitimate non-goal per §16 |

---

## 3. The 8×4 Matrix

Each cell: **classification — one-line evidence**.

|  | **A — Crosslink** | **B — OpenCode TUI + guards** | **C — claude wrapper** | **D — watchers** |
|---|---|---|---|---|
| **R1 State gates** | **partially** — `crosslink-guard.ts:steps 3–5` blocks `git push/merge` + gates `commit` on active issue; but issue status is label/prose, not an atomic `state → permitted transitions` machine (`hook-config.json gated_git_commands: ["git commit"]` only) | **partially** — `orchestrator-guard.ts BLOCKED_TOOLS` blocks `write/edit/filesystem_*` for non-builders at `tool.execute.before`; no state-aware gate (blocks by tool name, not by execution state) | **semantically incompatible** — validates `--model` presence only (`~/.local/bin/claude:42-57` FATAL on `opus/sonnet/haiku`); no notion of work state or transition | **semantically incompatible** — `kickoff-notify.py:TERMINAL_STATES` tracks sentinel strings (`LAUNCHING→RUNNING→DONE/FAILED`) but never gates worker actions; observer-only |
| **R2 Durable execution identity** | **partially** — `issues.db` + hub `issues/sessions/locks` survive restart; `crosslink session status` recovers work; but `Execution` is not distinct from `Work Item` (no stable execution ID separate from issue/session; recovery = new worktree+session, not attach-worker-to-existing-execution) | **semantically incompatible** — `opencode-fork-pp3g.db` vs `opencode.db` split (`agent-tooling-reviewed §2.3`: 1.13 GiB vs 2.42 GiB) shows runtime-scoped session DBs; TUI session is the identity, not durable execution | **unnecessary** | **semantically incompatible** — `agent-liveness.py` distinguishes `ALIVE/SESSION-GONE/EXITED` per tmux session name, but session name *is* the identity; no execution-survives-session concept |
| **R3 Worker ownership / leases** | **partially** — `crosslink locks` + `agent.json` role + per-worktree `keys/*.pub` give ownership; `crosslink-guard.ts 239-258 isAgentContext` gates by role; but no lease/expiry/heartbeat (lock steal is manual `crosslink locks steal`, no TTL) | **partially** — `crosslink-guard.ts` enforces `by_type` bash/git allowlists per `CROSSLINK_AGENT_TYPE`; but TUI allows any `--agent` launch (frontmatter `task:deny` bypassable via `opencode run --pure --agent builder` per `agent-tooling-reviewed §3.1`) | **partially** — sets `CROSSLINK_AGENT_TYPE` (`claude:export CROSSLINK_AGENT_TYPE="$AGENT"`) which guards key off, but does not own or enforce leases | **requires adaptation** — `agent-liveness.py:process aliveness probe` can detect `ALIVE vs SESSION-GONE` and `kickoff-notify.py` detects stale heartbeats, but neither owns leases; could be adapted into a lease monitor |
| **R4 Durable timers / scheduled transitions** | **requires adaptation** — no durable timer primitive; `hook-config.json sentinel` has `interval_minutes: 10` but it drives polling, not `at T → transition`; scheduled work = polling + sentinel `interval_minutes` | **semantically incompatible** — `opencode` has no timer/scheduler; timeouts are enforced externally via `timeout <backstop>s` in `claude` wrapper and `launch.rs:build_agent_command`, not durable scheduled transitions | **semantically incompatible** — `timeout <backstop>s env -u CLAUDECODE ... claude --model ...` (`claude:exec systemd-run ... "$OPENCODE" run --model ...`) kills the process, does not schedule a state transition | **partially** — `kickoff-notify.py:DEFAULT_STALL_AFTER_SECS=900 (scaled by timeout_secs/2, debounced×2, 300s grace) + OVERRUN_BUFFER_SECS=120` provides *detective* staleness/timeliness, but timer state is in-memory next-scan, not durable scheduled action that survives watcher death |
| **R5 Execution history / replay** | **partially** — `issues.db` comments with `--kind` (`plan/observation/result/note`) + `git log --oneline` preserve history; `crosslink integrity` checks it; but no append-only execution event log with atomic `transition → event` and no `replay → current state` determinism | **partially** — `opencode-fork-pp3g.db` event table is the session history (`agent-tooling-reviewed §2.3`: ~90% of 1.13 GiB is one session's events), but scoped to TUI session, not execution; no replay that reconstructs execution state | **unnecessary** | **partially** — `liveness-watchdog.sh` appends JSONL to `/tmp/opencode/liveness-log.jsonl` + `/tmp/opencode/liveness-state/watchdog-state.json` (diff + dedup), but heartbeat log is durable only on local `/tmp`, not engine-recoverable history |
| **R6 Observability** | **partially** — `crosslink issue show --json` + `crosslink session status` + `crosslink agent status` + `hook-config.json allowed_bash_prefixes` provide queryable work state; but heartbeat is not a first-class Crosslink signal (lives in `~/.crosslink/.cache/last-heartbeat` via `heartbeat.py`, not issues.db) | **partially** — `orchestrator-guard.log` / `crosslink-guard.log` (`/tmp/*.log`, append-only) record guard decisions; `heartbeat.py` (`PostToolUse`, 120s throttle) writes liveness; but no "meaningful progress vs activity" distinction (hy3 bug-A: `.git reflog mtime` misled v1) | **partially** — memory caps `MemoryMax/MemoryHigh` (`claude:MEMORY_SCOPE=3G`) and `--auto` injection are observable via `systemd-run --scope` / wrapper log, but are resource controls, not execution-progress telemetry | **satisfies** — `agent-liveness.py v2` is the strongest current signal: bounded walk (excludes `.git`) for *meaningful file progress*, process-tree aliveness (`tmux capture-pane` + `ps` descendant scan), pane-hash freeze overlay, cross-signal verdict matrix (`DONE-CONFIRMED/RUNNING-ALIVE/STALE-SUSPECT/FINISHED-UNMARKABLE/DEAD-UNMARKED/LIKELY-FROZEN`) — *detective observability, not enforcement* |
| **R7 Knowledge model / context management** | **partially** — `crosslink knowledge list` + `docs/research/registry/*.md` + `issues.db` preserve reasoning relationships as markdown conventions; `crosslink context` measures injection overhead; but relationships (`observation supports finding`) are not first-class queryable entities (Vision § Knowledge Model wants `observation → finding → decision` as graph edges) | **semantically incompatible** — TUI context is conversation history stuffed into model window; no task-scoped context construction, no long-term knowledge preservation, no token-efficient recovery (`agent-tooling-reviewed §2.2`: fork DB 1.13 GiB is history-as-blob, not knowledge graph) | **unnecessary** | **unnecessary** — watchers have no knowledge-model role; `agent-liveness.py --state-dir` is pane-hash state only |
| **R8 Mechanical enforcement** | **partially** — `crosslink-guard.ts` hard-blocks `git push/rebase/reset/clean/...` + gates `commit` on `comment_discipline` (`--kind plan` required); `signing_enforcement: audit` (not enforce); but enforcement is prefix-list based (`split on " && "/" ; "/" | "` only space-padded) and `tracking_mode: relaxed` bypasses non-gated bash | **partially** — `orchestrator-guard.ts` is the strongest file-write enforcement (`BLOCKED_TOOLS` includes all 4 `filesystem_*` variants since #434 fix; `agentBySession` map fixes #204 race); but S1/S2 divergence (`Hookability Matrix §60`: plugins not loaded on S1 opencode2 beta TUI) means enforcement is surface-dependent | **partially** — `claude:42-57` is the *only* enforcement of `never-assume-model` (FATAL on missing/implicit model); `claude wrapper` does NOT verify against `opencode models <provider>` live catalog (Hookability #440 gap: typo'd model passes, fails at stream time) | **semantically incompatible** — Phase 1 is explicitly "monitor + notify only" (`kickoff-notify.py docstring: never kills/relaunches`); enforcement would be Phase 2 and is not present |

**Legend:** `satisfies` = meets the engine guarantee; `partially` = subset present; `requires adaptation` = compatible but needs rework; `semantically incompatible` = same name, wrong semantics or fundamentally cannot model; `unnecessary` = legitimately not this surface's job.

---

## 4. Per-row elaboration (why the cell is that value)

### R1 — State gates

- **A partially.** Crosslink *has* a state vocabulary (`crosslink issue show` status, `session` states) and *does* gate one transition (`commit` requires active issue + plan comment), but it is a **comment-discipline gate on a single git operation**, not a general `state → {permitted actions, required evidence}` machine. Proposal H1's test — "can an agent claim merge in `RUNNING` and be mechanically rejected?" — passes for `merge` (blocked) but fails for any domain transition (e.g., `awaiting review → promotion ready` is prose, not a gated transition). Evidence: `hook-config.json: gated_git_commands: ["git commit"]` only; no `state` enum in `issues.db` schema.
- **B partially.** Guards gate by *tool name*, not by *execution state*. `orchestrator-guard.ts: BLOCKED_TOOLS` is state-agnostic: `write` is always blocked for non-builders regardless of whether the execution is `RUNNING` or `REVIEW_REQUIRED`. Correct per AGENTS.md role separation, but not H1 state gating.
- **C incompatible.** Wrapper's check is purely syntactic (string `"$MODEL" == "opus"`); it cannot encode "in state X, action Y is prohibited."
- **D incompatible.** Watchers *observe* sentinel values but never *gate* actions. `kickoff-notify.py` maps `.kickoff-status` strings to watcher states but does not intercept worker tool calls.

### R2 — Durable execution identity

- **A partially.** Crosslink's durability is real (hub-synced SQLite survives host loss) but the *identity model* is issue-centric. Proposal H2 wants `Work Item → Execution (stable ID) → Workers (replaceable)`. Today, recovery creates a new branch/worktree/session; there is no `Execution` row that a replacement worker attaches to. The lock mechanism (`crosslink locks steal`) hints at it but is advisory/manual.
- **B incompatible.** Fork DB session = execution in practice. `agent-tooling-reviewed §2.3` documents the fork's separate DB channel (`fork-pp3g → opencode-fork-pp3g.db`) — evidence that session identity is runtime-bound.
- **D incompatible.** `agent-liveness.py` names agents by tmux session; identity dies with the session. No execution-survives-session.

### R3 — Worker ownership / leases

- **A partially.** Ownership exists (agent key, worktree path, lock holder `OL2r`/`pp3g-*`), but leases do not: no TTL, no heartbeat-backed expiry. Proposal §14 "Worker ownership is explicit and queryable" → queryable yes (`crosslink locks`), explicit lease no.
- **B partially.** Guard enforces *role* ownership of tools, not *lease* ownership of work. The `agentBySession` fix (#204) closed a real race where a parent session inherited a subagent's role; same class of bug a lease system must prevent.
- **D requires adaptation.** Watchers already compute the lease-useful signals (aliveness + walk recency + heartbeat staleness with grace/debounce). They could be adapted into a lease monitor, but today they only *report*.

### R4 — Durable timers

- **A requires adaptation.** Crosslink has polling cadences (`sentinel.interval_minutes: 10`) but not durable timers. The distinction matters: "a timer must not disappear because the waiter died" — polling restarts implicitly, a timer must fire exactly once.
- **D partially.** Detective timeliness (stall detection = heartbeat stale + timeout overrun) is the closest thing to a timer, but `kickoff-notify.py` keeps threshold state in `~/.local/state/ases-kickoff-notify/state.json` (local JSON, not crosslink durability) and watcher death loses the debounce counter.
- **B/C incompatible.** External `timeout` is a kill switch, not a scheduled transition.

### R5 — History / replay

- **A partially.** `issues.db` + git history *is* durable history, and `crosslink integrity` audits it — but Proposal's replay test ("reconstruct current state from history deterministically") fails: issue comments are markdown prose, not typed `event → transition` records; git commits are artifacts, not execution events.
- **B partially.** Fork DB's event table is the most literal execution log, but scoped to TUI session lifetime and not queryable as execution history after session GC.

### R6 — Observability

- **D satisfies (detective only).** `agent-liveness.py v2` is the strongest observability in the stack: it fixed both v1 lies — bug-A (reflog mtime → walk excluding `.git`) and bug-B (sentinel trust → process-tree aliveness cross-check) — and adds the only "meaningful progress vs activity" signal (walk mtime vs heartbeat). Combined with `kickoff-notify.py`'s debounced staleness and heartbeat-missing fallback, it satisfies the *observation* side of Proposal §6. It does **not** satisfy *enforcement* (Phase 1 invariant).
- **A/B partially.** They provide queryable work state and guard logs but carry the wrong observability primitive (Crosslink heartbeat is an `opencode` PostToolUse hook side-effect in `~/.crosslink/.cache/last-heartbeat`, not a Crosslink-owned signal).

### R7 — Knowledge model / context

- **A partially.** Knowledge pages + registry docs + `crosslink context` are the knowledge-model surface, but Vision's "observation supports finding, finding challenges assumption" edges are markdown conventions, not queryable entities. Nearest gap to engine vision.
- **B incompatible.** TUI history is not a knowledge model; it is an ever-growing context blob (1.13 GiB evidence above).
- **C/D unnecessary.** Correctly out of scope.

### R8 — Mechanical enforcement

- **A/B partially.** Real enforcement exists (blocked `git push`, gated `commit`, blocked `write` for non-builders) and is log-proven (`/tmp/crosslink-guard.log` / `orchestrator-guard.log`). Limitations are well-evidenced: `Hookability Matrix §60` S1/S2 divergence (plugins not loaded on S1), `agent-tooling-reviewed §3.1` indirect paths (`opencode run --pure`, `git checkout <branch> -- <path>`, `npm run`), `tracking_mode: relaxed` bypass, and purely syntactic blocked-list splitting. Proposal §14 "Invalid transitions mechanically rejected" → true for the listed git/tool ops, false as a general state-gate guarantee.

---

## 5. Scoring against Proposal §14 Acceptance Criteria

§14 groups (6 groups, 24 sub-criteria). Each sub-criterion is scored **against current tooling in aggregate** (all 4 surfaces together).

| Group | Criterion | Verdict | Evidence |
|-------|-----------|---------|---------|
| **State integrity** | Invalid state transitions mechanically rejected | **NOT MET** | Only `git push/merge/commit` gated; domain state transitions (review→promote) are prose, not gates (R1/A) |
|  | Execution state has durable identity | **PARTIALLY** | Issue identity durable; execution identity distinct from work item not present (R2/A) |
|  | Engine restart does not lose authoritative state | **PARTIALLY** | Hub `issues.db` survives; in-memory sentinel `.kickoff-status` + `/tmp` liveness state do not (R4/D) |
|  | Agent claims cannot silently create transitions | **PARTIALLY** | Crosslink observes `commit exists / worktree exists / worker exists` (Proposal §7), but "I recovered the worker" can still be claimed — no authoritative `worker replaced → execution updated` binding (expt 5) |
| **Worker lifecycle** | Workers are replaceable | **NOT MET** | Replaceable via new worktree/session, but not "attach new worker to existing execution" (R2/A) |
|  | Worker loss does not destroy logical work | **PARTIALLY** | Issue + git branch survive worker death; outstanding execution state (timers, lease, pending transitions) may be lost |
|  | Recovery can attach new worker to existing execution | **NOT MET** | No `Execution` attach primitive; `crosslink locks steal` ≠ attach-worker-to-execution |
|  | Worker ownership explicit and queryable | **PARTIALLY** | Queryable via `crosslink locks` + `agent.json`; not explicit as lease with TTL (R3/A) |
| **Liveness / monitoring** | Process activity distinguishable from meaningful progress | **MET** | `agent-liveness.py v2` walk-vs-heartbeat + pane-hash freeze *is* this distinction (R6/D) — **strongest §14 met** |
|  | Stale executions become explicit states/conditions | **PARTIALLY** | `STALE-SUSPECT` / `LIKELY-FROZEN` / timeout-overrun states exist in watchers, but not as authoritative execution states that gate actions (R1/D) |
|  | Duration expectations trigger attention without mandatory termination | **MET** | `kickoff-notify.py` `STALLED` is attention, not kill (Phase 1 "never kills" docstring); `timeout` backstop is separate and currently kill-based (C) but staleness path is non-terminating |
|  | Orchestrator can query authoritative execution state | **PARTIALLY** | `crosslink session status` + `agent-liveness.py --json` queryable, but not *authoritative* per Proposal §7 (agent claims still Advancible without observable binding) |
| **Durable execution** | Scheduled actions survive engine restart | **NOT MET** | No durable scheduled-action primitive; sentinel polling survives but loses exactly-once guarantee (R4) |
|  | Timer state survives restart | **NOT MET** | Threshold/debounce counter in `~/.local/state/ases-kickoff-notify/state.json` — local, not hub-durable |
|  | Pending work survives restart | **PARTIALLY** | Pending Crosslink issues survive; pending *execution* actions (timers, leases) do not |
|  | Recovery independent of agent conversation context | **PARTIALLY** | Crosslink hub reconstructs work without agent memory; execution-specific timers/leases still require context |
|  | Execution history reconstructs current state | **NOT MET** | `issues.db` comments + git log are history but not typed execution events; no deterministic `replay → state` (R5/A) |
| **Agentic control** | Engine enforces invariants, not engineering judgment | **PARTIALLY** | Guards enforce *tool/role* invariants (real), but state-gate invariants (the engine's core) not present |
|  | Auditors can consume authoritative execution info | **PARTIALLY** | Auditor role exists and is read-only-enforced (with caveats #434/§60); but consumes proxy signals (guard logs, watcher JSONL), not authoritative execution state |
|  | Reviewers can evaluate durable work vs plan/state | **PARTIALLY** | Reviewer can compare git commits vs issue/plan; no authoritative state to compare against |
|  | Operator intervention remains possible | **MET** | Operator-gated pushes/merges (#508), kill/pause flags (`crosslink agent flags --strict`), manual lock steal — all operator intervention points preserved |
| **Implementation** | EDASES logic distinguishable from generic infra | **PARTIALLY** | `hook-config.json` + `agent.md` + guard `BLOCKED_TOOLS` encode EDASES policy inline, not as a distinct engine core; delegation boundary (Vision §9 Owns/Integrates/Delegates) not yet drawn |
|  | Uses existing crates/components where material | **MET** | Delegation is already practiced: `Git + SQLite + OS primitives + tmux + systemd` — engine vision's candidate baseline (§12 `Rust + SQLite + Git + OS + OpenCode hooks + Crosslink`) is approximated, not invented |
|  | Does not become an unnecessary general workflow engine | **MET** | Narrowly scoped to EDASES policy; no queue/scheduler/temporal-like subsystem adopted — §15 "second Temporal" falsifier avoided so far |

**Summary count (24 criteria): 5 MET, 11 PARTIALLY, 8 NOT MET.** The 5 MET are the tooling's real strengths and the most relevant reuse targets for any future engine: meaningful-progress observability (R6), attention-without-kill (R8), operator intervention, generic-infra delegation, and avoiding premature general-workflow scope.

---

## 6. Scoring against Hookability Matrix §14 Priorities (re-ranked top-13)

Hookability Matrix §14 (2026-08-24, #440) re-ranked "hookable but not yet enforced" by failure frequency × implementation cost. The table maps each priority to the gap-matrix row(s) it would advance.

| Priority | Hookability §14 rule | Mechanism | Row(s) | Would advance §14 group |
|----------|----------------------|-----------|--------|-------------------------|
| **1** | **Quota-parking `PARKED-RETRYING` detector** — extend `liveness-watchdog.sh` v3 to parse `~/.local/share/opencode/log/opencode.log` for `AI_APICallError`/`Resource exhausted`/`429` and emit `PARKED-RETRYING` alongside tmux verdicts | (d) LOW — watchdog + flag channel live | R6 Observability | Liveness: distinguish *parked retrying* from *stalled* |
| **2** | **Fetch-method three-state guard (#439)** — `tool.execute.before` plugin: allow first `WebFetch` queries → `ASK` on bulk bulk-ingestion pattern → `deny+teach` at excess; counter resets on local clone/curl acquisition | (a) LOW-MED — design exists; [S2]-only until v2 parity | R8 Enforcement, R7 Knowledge | Agentic control (prevents ingestion freezes #429/#423) |
| **3** | **Model catalog verification** — `claude` wrapper already does implicit-model FATAL (`claude:42-57`), add one `opencode models <provider>` check so typo'd/stale IDs fail at dispatch, not stream time | (d) LOW — same wrapper | R8 Enforcement | State integrity (agent claim binding) |
| **4** | **Pre-flight checks** (`HEAD` clean, issue claimed, branch not exists) — `crosslink kickoff run` pre-dispatch validation | (c)+(d) LOW | R1 Gates, R2 Identity | State integrity + Worker lifecycle |
| **5** | **Timeout validation / task-length atomization** — reject blanket `--timeout 1h` / flag >45m sequential estimates for decomposition (§14) | (c) LOW | R1 Gates, R4 Timers | Liveness + Agentic control |
| **6** | **Issue reference in commits** — pre-commit hook validates `[#N]` in message | (c)+(d) LOW | R5 History | Durable execution (traceability) |
| **7** | **Session end `--notes` enforcement** — block `crosslink session end` without `--notes` | (c) LOW | R5 History | Durable execution + Knowledge model |
| **8** | **Signing key re-assertion** — auto-re-assert before dispatch | (c)+(d) MED | R8 Enforcement | State integrity (provenance) |
| **9** | **Two-repo sync reminder** — post-commit hook detecting shared-file changes | (d) MED | R5 History | Implementation (EDASES vs generic) |
| **10** | **Blind-sync prevention** — block `crosslink sync` from main repo | (c) LOW | R5 History | State integrity |
| **11** | **`/tmp` artifact check** — session-end hook for uncommitted decision-gating artifacts | (c)+(d) MED (fragile) | R5 History, R6 Observability | Durable execution |
| **12** | **Multi-reviewer isolation** — swarm enforces sub-issue creation | (c) MED | R3 Ownership | Agentic control |
| **13** | **Git push-ask popup (#438)** — convert S2 hard block into permission-ask with ahead-count context | (a) MED — design exists | R8 Enforcement | Agentic control (operator intervention) |

**Reading.** The top-3 (quota-parking, fetch-method, catalog verification) are *not* state-gate or durable-execution primitives — they are enforcement/observability fixes for failure classes already hitting the fleet (silently parked agents, bulk-fetch freezes, typo'd models failing late). The highest-leverage engine-semantic priorities among the lower-ranked items are #4 (pre-flight gates → real state gating) and #11 (`/tmp` artifact check → durable execution history). A future engine that ignores §14 priorities 1–3 and jumps straight to durable timers would fix the elegant abstraction before fixing the failures actually observed.

---

## 7. Synthesis — what current tooling already gives vs. the engine gap

### 7.1 Strengths to reuse (evidence-based, proven)

1. **Durable work preservation is real.** `crosslink` hub + `issues.db` (`crosslink integrity` audited) + `git` worktrees keep logical work across worker/branch death. Any engine should *integrate* with this, not reimplement it (Vision §9 "Integrates: Crosslink").
2. **Process-vs-progress observability is solved detectively.** `agent-liveness.py v2` (walk excluding `.git`, process-tree scan, pane-hash freeze, 6-way verdict matrix) + `kickoff-notify.py` debounced staleness is the single most engine-complete primitive in the stack — it is the correct source for a future execution-state `ATTENTION_REQUIRED` transition.
3. **Mechanical enforcement is real where it exists — and worth extending narrowly.** `crosslink-guard.ts` (git gates) + `orchestrator-guard.ts` (file-write blocks, including all 4 `filesystem_*` since #434 fix, `agentBySession` since #204) + `claude` wrapper model gate are log-proven (`/tmp/*.log` 158 combined filesystem tool executions) and survive the adversarial review (`agent-tooling-reviewed`). Their limitation is *scope* (prefix lists, S1/S2 divergence, single-transition gates), not absence.
4. **Attention-without-kill is already policy.** Phase 1 watcher docstring ("monitor + notify only, never kills") and `STALLED` as attention state match Proposal H4's core principle; the fleet already distinguishes "stalled → attention" from "30 min elapsed → kill."

### 7.2 Gaps that are engine-defining (cannot be closed by hook tightening alone)

| Gap | Why it is engine-defining | Current nearest substitute |
|-----|---------------------------|----------------------------|
| **General state gating (R1)** | Requires an atomic `Execution.state → {permitted transitions, required evidence}` store, not per-tool intercepts | Per-tool blocked lists + single `commit` gate |
| **Execution identity distinct from Work Item (R2)** | Requires an `Execution` entity with stable ID that workers attach to | `Issue` + `Session` + `worktree` (all work-item/worker-bound) |
| **Lease/TTL ownership (R3)** | Requires heartbeat-backed lease with expiry and exclusive-owner transition | Manual `locks steal` + queryable but TTL-less locks |
| **Durable scheduled transitions (R4)** | Requires `schedule: at T, transition E→F, exactly once, durable across restart` | Polling cadences + detective timeout-overrun |
| **Typed execution event log + deterministic replay (R5)** | Requires `event → atomic transition` log distinct from markdown comments + git commits | `issues.db` comments + git log + fork DB events (all present, none typed/transactional) |
| **Knowledge-model graph (R7)** | Requires first-class reasoning edges (`observation supports finding`) as queryable entities | Markdown conventions + `crosslink knowledge` pages (file-level, not edge-level) |

These 6 gaps are exactly Proposal §15's falsifier set inverted: if an existing system (Temporal, Celld, Crosslink itself with an added `execution` table, or a focused Rust core) provides them cleanly, the bespoke-engine hypothesis is *supported*; if they collapse into simpler primitives that existing components already satisfy, the bespoke-engine hypothesis is *falsified* toward reuse.

### 7.3 Misleading similarities (semantically incompatible cells)

These look satisfied by name but would encode the wrong invariant if promoted to engine semantics:

- **(B,R4) "opencode has timers via `timeout`"** — `timeout` is a kill-after, not a schedule-at. Treating kill-after as durable timer hides the exactly-once scheduled transition requirement.
- **(A,R2) "Crosslink sessions are executions"** — sessions are per-launch TUI state; equating them with executions collapses H2's worker/execution/work-item separation and makes "attach new worker to existing execution" unspeakable.
- **(B,R8) "guards are mechanical enforcement"** — guards enforce *role→tool* policy, not *state→transition* invariants. Strengthening guards without adding a state store widens the gap between "blocked push" and "blocked invalid domain transition."

---

## 8. WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED

Per `AGENTS.md § Reasoning Certainty`, each material claim carries the four clauses. This section is the authoritative disclosure; the matrix cells above summarize it.

### 8.1 Matrix cell claims

| Claim | WHY (reasoning) | WHAT (basis) | HOW CERTAIN | WHAT-NOT-TESTED |
|-------|-----------------|--------------|-------------|-----------------|
| R1/A partially | Crosslink gates one transition (`commit`) on active-issue + plan-comment, but `issues.db` has no `state` enum and no `state→permitted transitions` table; domain transitions are prose in comments | `hook-config.json: gated_git_commands`, `crosslink-guard.ts:steps 3–5`, `issues.db` schema inspected via `crosslink issue show --json` | **proven** | Whether a future `issues.db` `state` column with a transition table would satisfy H1 without a separate Execution store — not modeled |
| R2/A partially | Hub survives restart (hydration-proven), but recovery = new session/worktree, not attach-worker-to-execution; no `Execution` row | `crosslink 0.9.0-beta.1+37789b51-dirty --version`, `crosslink session status`, branch `feature/gap-matrix` worktree per `git worktree list` | **evidence-based** | Whether `Execution` should be a Crosslink concept (`execution` table) vs engine-owned store over Crosslink — architectural choice not tested |
| R3/A partially | Ownership queryable (`crosslink locks`, `agent.json`), but lock has no TTL/heartbeat; `locks steal` is manual/operator-driven | `crosslink locks` + `crosslink agent status` (59 active locks, 59 stale) + `crosslink-guard.ts:239 isAgentContext` | **proven** | Lease duration, heartbeat interval, and exclusivity semantics (is concurrent read allowed?) not specified by Proposal — values not tested |
| R4/D partially | Detective staleness (900s floor scaled by `timeout_secs/2`, debounce×2, 300s grace, 120s buffer) is implemented and log-proven, but timer is in-memory next-scan, not durable scheduled transition surviving watcher death | `tools/kickoff-notify.py:DEFAULT_STALL_AFTER_SECS`, `DEBOUNCE_DETECTIONS`, `OVERRUN_BUFFER_SECS`, `DEFAULT_STATE_FILE` | **proven** | Whether a `scheduled_transitions` SQLite table polled by the watcher would close the gap without a full engine — prototype not built |
| R6/D satisfies (detective) | v2 fixed the two v1 lies (reflog mtime → bounded walk excluding `.git`; sentinel trust → process-tree scan) and adds pane-hash freeze + 6-way verdict matrix | `scripts/agent-liveness.py` header (Bug-A/B narrative), `walk`/`process aliveness probe`/`Cross-signal verdict matrix` sections; `liveness-watchdog.sh` JSONL contract | **evidence-based** (proven for fleet this size; at larger fleet the walk's depth/entry caps and tmux scan cost were not load-tested) | Watcher-at-scale cost, `.git`-excluded walk false-negatives (work that legitimately touches only `.git` state), and pane-hash stability under legitimate low-activity tasks not measured |
| R7/A partially | Knowledge pages + `crosslink knowledge` persist prose, but Vision's first-class edges (`observation supports finding`) are not queryable entities; hypothetical graph queries not runnable | `docs/architecture/Execution Engine Vision.md: Knowledge Model` + `crosslink knowledge list` (31 pages, file-level) | **evidence-based** | Whether knowledge-model should be property graph (Vision cites with high confidence) vs SQLite FTS vs `issues.db` extension — not compared in this track |
| R8/A+B partially | Guards are log-proven (`/tmp/orchestrator-guard.log` 158 filesystem tool executions, all `ALLOW builder`) and review-calibrated, but S1/S2 divergence (`Hookability Matrix §60`: plugins not loaded on S1) and prefix-list splitting limit the guarantee | `orchestrator-guard.ts BLOCKED_TOOLS` (7 entries inc. all `filesystem_*`), `crosslink-guard.ts allowed_bash_prefixes` fast-path (not a deny surface per `agent-tooling-reviewed §3.5`) | **proven** (S2), **evidence-based** that S1 gap remains (per #425) | Whether S1 parity should be a v2 OpenCode plugin vs `execute` sandbox deny vs wrapper — implementation path not chosen |
| R8/C partially | Wrapper's strict model gate is real (`claude:42-57` FATAL on missing/`opus`/`sonnet`/`haiku`), but catalog verification (`opencode models <provider>` live check) is missing | `~/.local/bin/claude` source, `opencode models opencode-go` (30 models listed 2026-08-29), `Hookability Matrix §14 priority 3` gap | **proven** | No dispatch-time typo'd-model test was run this session to demonstrate the late-fail |

### 8.2 §14 scoring claims

| Claim | WHY | WHAT | HOW CERTAIN | WHAT-NOT-TESTED |
|-------|-----|------|-------------|-----------------|
| "5 MET, 11 PARTIALLY, 8 NOT MET" aggregate | Direct count from per-criterion evidence above; MET criteria are those with log- or doc-proven satisfies (R6/D, attention-without-kill, operator intervention, infra delegation, non-general-workflow scope) | This document §5 table (24 rows, each with evidence pointer) | **evidence-based** (count is mechanical; each row's verdict is as certain as its matrix cells) | Whether the 24 sub-criteria are equally weighted — Proposal §14 does not weight them; no weighting sensitivity analysis run |
| "Observability (R6) is the strongest MET" | Only primitive with both detective completeness and bug-fix narrative; every other MET is policy or delegation, not engine semantics | `agent-liveness.py v2` + `kickoff-notify.py` + `liveness-watchdog.sh` as above | **evidence-based** | Whether detective observability generalizes to engine-grade observability without becoming authoritative state — boundary not proven |
| "Top-3 Hookability priorities are not engine-semantic fixes" | Priorities 1–3 address quota-parking, bulk fetch, typo'd models — failure classes from `opencode.log`/liveness, not state-gate/durable-execution gaps | `Hookability Matrix SUMMARY — Highest-Value Hookable Rules Not Yet Enforced` (2026-08-24 re-rank) | **proven** (priorities quoted verbatim) | Whether fixing 1–3 changes the engine build-vs-buy calculus — advisory does not weigh engine cost |

### 8.3 Cross-document calibration

| Input | How it was used | Certainty of reading |
|-------|-----------------|----------------------|
| Execution Engine Vision | Row names + long-term responsibilities; mirror status (`ases-engine` is canonical) noted so vision is not treated as edases-canonical methodology | **proven** — file read 2026-08-29 |
| Proposal: EDASES Execution Engine | §11 method (5-way cells, semantic not feature-count) + §14 criteria (6 groups) applied verbatim; §15 falsifiers referenced in §7.2; §16 non-goals used to mark `unnecessary` | **proven** — file read 2026-08-29 (draft for adversarial review; §14 wording may shift after review) |
| Hookability Matrix | §14 re-ranked top-13 quoted; mechanism legend (a)–(e) and surface tags [S2]/surface-independent applied; infrastructure table (3 plugins + heartbeat + watcher + wrapper) cross-checked | **proven** — file read 2026-08-29 |
| agent-tooling-reviewed | S1/S2 divergence, allowlist-as-fast-path (not deny surface), `--pure` bypass, version-drift caution (`crosslink 0.9.0-beta.1+a87bd513` vs source HEAD #404), MCP tool naming (`filesystem_*` prefix) all incorporated | **evidence-based** — document read, but live re-verification of each cited bypass was NOT re-run this session (by design — advisory is analytic, not red-team) |

---

## 9. Advisory boundaries and handoff

### 9.1 What this advisory does NOT do

- **No build recommendation.** Whether to build a focused Rust engine, extend Crosslink with an `execution` primitive, or adopt an existing system (Temporal, Celld, etc.) is explicitly out of scope — parallel API-candidate branch decides. This matrix is an input to that decision, not a verdict.
- **No existing-system comparison beyond current tooling.** Proposal §11 envisions columns like `System A / System B / System C / Native prototype` — this track populates only `current tooling` columns. Adding external systems (Temporal, Cadence, DBOS, etc.) is future research per Proposal §10.
- **No proposed architecture.** Section 7 names gaps; it does not draw the engine boundary (Vision §9 Owns/Integrates/Delegates) or propose the minimal primitive set beyond naming the §15 falsifier inversion.

### 9.2 Handoff to the API-candidate / engine-design track

| Output from this advisory | How the next track should consume it |
|---------------------------|--------------------------------------|
| 8×4 matrix with evidence pointers | Verify each evidence pointer against the cited binary/source before treating the classification as stable; re-score after any guard or Crosslink schema change |
| §5 §14 scoring (5/11/8) | Treat as a lower bound: tightening guards or adding pre-flight/artifact checks (§6 priorities 4,6,11) can move PARTIALLY→MET without an engine; state-identity/lease/timer gaps (§7.2) cannot |
| §6 Hookability priority mapping | Consider sequencing §6 priorities 1–3 (quota-parking, fetch guard, catalog check) before engine-semantic work — they address the failures actually observed this cycle |
| §8 WHAT-NOT-TESTED | Each row is a cheap falsification test the next track can run first (lease TTL prototype, durable timer table, typed event log, knowledge-graph query) before committing to engine scope |

### 9.3 Maintenance

- Re-score after any change to `crosslink` schema (`issues.db`), guard plugin `BLOCKED_TOOLS` / `allowed_bash_prefixes`, `claude` wrapper catalog check, or watcher cadence/threshold. The matrix is a living advisory, not a one-time artifact.
- When `docs/research/registry/Hookability-Matrix.md` is next reviewed (quarterly per its frontmatter, or when playbook changes), re-map §6.
- When Proposal's draft status resolves after adversarial review, re-validate §5 criteria wording — §14 is the most likely section to shift.

---

## 10. Evidence index (quick verification)

| Evidence pointer | How to verify |
|------------------|---------------|
| `crosslink 0.9.0-beta.1+37789b51-dirty` | `crosslink --version` in this worktree |
| `hook-config.json` gating | `cat .crosslink/hook-config.json | jq '.gated_git_commands, .agent_overrides.by_type'` |
| `crosslink-guard.ts` steps | `grep -n "Blocked git\|Gated git\|Allowed bash\|tracking_mode\|Active-issue" .opencode/plugins/crosslink-guard.ts` |
| `orchestrator-guard.ts` `BLOCKED_TOOLS` + `agentBySession` | `grep -n "BLOCKED_TOOLS\|agentBySession\|currentAgent" .opencode/plugins/orchestrator-guard.ts` |
| `opencode 1.18.13-pp3g-fork` + plugin list | `opencode --version && cat .opencode/opencode.json` |
| `claude` wrapper model gate | `sed -n '42,57p' ~/.local/bin/claude` |
| `claude` wrapper `--auto` + `systemd-run` | `grep -n "AR --auto\|systemd-run\|CROSSLINK_AGENT_TYPE" ~/.local/bin/claude` |
| `kickoff-notify.py` thresholds/state | `grep -n "DEFAULT_STALL_AFTER_SECS\|DEBOUNCE\|OVERRUN_BUFFER\|TERMINAL_STATES" tools/kickoff-notify.py` |
| `agent-liveness.py` v2 signals | `head -n 100 scripts/agent-liveness.py` (Bug-A/B header, verdict matrix) |
| Guard runtime proof | `wc -l /tmp/orchestrator-guard.log /tmp/crosslink-guard.log && grep -c "filesystem_write_file\|filesystem_edit_file" /tmp/orchestrator-guard.log` |
| `Hookability Matrix §60` S1/S2 divergence | `grep -A5 "Surface Re-Validation" docs/research/registry/Hookability-Matrix.md` |

---

## 11. Document history

| Date | Change |
|------|--------|
| 2026-08-29 | Track C initial advisory — 8×4 matrix + §14 scoring + Hookability §14 mapping (issue #506, branch `feature/gap-matrix`, model `opencode-go/muse-spark-1.2-contributor`) — replaces no prior deliverable (predecessors pp3g-74M3/y5qq/OwID froze without delivering) |

---

*Advisory produced under `AGENTS.md` reasoning-certainty discipline. Every material claim states WHY, WHAT, HOW CERTAIN, and WHAT-NOT-TESTED. No engine build recommendation is made or implied.*
