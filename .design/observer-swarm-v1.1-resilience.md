---
title: Observer Swarm v1.1 — Resilience Hardening
program: EDASES
layer: Implementation
document_type: Design Document
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - docs/architecture/Execution Engine Vision.md
  - .crosslink/knowledge/agent-orchestration-playbook.md
  - .crosslink/knowledge/server-memory-management.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - issue #473 — Observer freeze-detection misfire + OOM death class
  - issue #462 — Execution Boundary D1-D4, Secrets Handling, Startup Verification
  - to-file/VSDD.md — Verified Spec-Driven Development (lite adoption, see Appendix A)
  - to-file/messaging.md — EDASES Observer v1.1 Minimal Agent-to-Orchestrator Communication (integrated into Phase 2)
consumed_by:
  - Swarm launch (observer v1.1 phases)
  - docs/ORCHESTRATOR.md
  - .crosslink/knowledge/agent-orchestration-playbook.md (next revision)
related_documents:
  - .design/lifecycle-manager-design.md
  - .design/epic-423-swarm-plan.md
  - issue #460
  - issue #483
  - issue #484
  - issue #485
  - issue #486
  - issue #487
  - issue #489
  - issue #488 — swarm design for execution-engine vision (#460-lineage)
  - issue #490 — EPIC Observer Centralized Operator Reports (Hybrid F)
supersedes:
  - .design/lifecycle-manager-design.md (partially — lifecycle semantics retained, resilience + filing + traceability added)
  - prior observer swarm assumptions that treated launch as infallible and filing as per-issue comments only
  - to-file/messaging.md as standalone draft — superseded as integrated Phase 2 expansion (no new broker/MCP; watermark watcher + blocking semantics + 10 acceptance tests now live in this design)
  - prior assumption that Builder->Orchestrator questions required a new protocol — replaced by Crosslink agent-communication convention forwarded via existing Observer->Orchestrator path (see Phase 2 §2e)
last_updated: 2026-08-27
---

# Observer Swarm v1.1 — Resilience Hardening

## Purpose

Define a three-phase swarm that hardens the Observer supervision pipeline against
the failure classes proven in August 2026. The design is **vision-driven**: the
Execution Engine Vision requires mechanical enforcement of methodology, explicit
state, and auditable reasoning — this swarm makes those properties survive
memory-pressure kills, operator-surface drift, and scattered filing.

The swarm does not redesign Observer's core verdict matrix or state machine
(completed/failed/killed/parked/frozen). It closes the **resilience, filing,
and traceability gaps** around that core so the engine can operate as a
methodology operating system rather than a fragile monitor.

## Relationship to Execution Engine Vision

| Vision clause | How v1.1 serves it |
|---|---|
| *Methodology execution — understand awaiting-validation / blocked / promotion-ready state* | Phase 1 mechanical launch gate and Phase 3 evidence durability ensure the engine never promotes or kills on stale/missing evidence. Phase 2 messaging makes WAITING_FOR_ORCHESTRATOR an explicit, auditable methodology state rather than a silent stall. |
| *Mechanical enforcement — prevent unsupported promotion, detect missing evidence* | Phase 3 makes evidence-at-transition and earlyoom attribution mandatory before any destructive action; Phase 1 makes memory-headroom a gate, not guidance. |
| *Knowledge model — explicit relationships between observation/finding/decision/validation* | Phase 2 centralizes operator-facing findings under one parent epic with machine-queryable labels, so relationships are durable, not scattered comments. Agent-communication records carry the same durable relationships (agent + issue + blocking + message) via Crosslink. |
| *Orchestration — coordinate heterogeneous capabilities* | Phase 2 sentinel triage and Phase 1 admission checks route capability selection through explicit, auditable gates. The Observer watermark watcher adds a second coordination surface without a new broker. |
| *Human interaction — augment, not reduce, human understanding* | Execution Boundary D1-D4 and Secrets Handling (Phase 1) keep the operator surface to decisions/approvals/review, never shell execution. VSDD-lite (Appendix A) keeps specs living and reviewable, not frozen proofs. |
| *State management — explicit, recoverable, auditable, consistent* | Phase 3 durable git-tracked backlog (`knowledge/execution-engine-backlog.md`) plus per-transition evidence bundles. Crosslink is the durable source of truth for agent communication (survives Observer/Orchestrator restarts). |
| *Long-term — methodology operating system that improves through evidence* | Every phase emits evidence that feeds the knowledge pages it depends on (bidirectional hardening). Live probes (server-memory-management, earlyoom) replace exhaustive edge-case catalogs. |

## Dependencies

### Canonical (read before implementing)

1. **`.crosslink/knowledge/server-memory-management.md`** — single source for
   three-layer defense (systemd Scope MemoryMax=3G, earlyoom 10% RAM+swap SIGTERM
   biggest consumer, zram 3.9G), `free -m` headroom rule (>=1GB over ~1.9GB base
   stack + fleet footprint), forensic trap (`journalctl -u earlyoom` not
   `journalctl -k`), mitigation knobs (`-m`/`-s` percent, `--prefer`/`--avoid`
   regex, `-r` cadence), VACUUM and cleanup rules.

2. **`.crosslink/knowledge/agent-orchestration-playbook.md`** — operator profile
   D1-D4, Secrets Handling, Startup Verification (launch -> sleep 30s ->
   opencode.log tail + `.kickoff-status` check), task-matched timeouts,
   progress-feedback contract, heartbeat + stall trigger (§5.8), Decision-Gating
   Artifacts Before Session End (§5.9).

3. **`docs/architecture/Execution Engine Vision.md`** — architecture principles
   (explicit state, composable services, traceable reasoning) and the
   EDASES -> ASES -> Execution Engine layering that this design must not invert.

4. **Issue #473** — research finding: pane-hash freeze false-positive on
   self-throttling collectors, earlyoom SIGTERM masquerading as agent death,
   commit-age and positive-progress signals needed, fleet-size admission
   implication, FAILED/KILLED discrimination requirement.

5. **Issue #462 doctrine** — D1-D4 binding, Secrets Handling, Startup
   Verification interim procedure (operator decisions 2026-08-24/25).

6. **`to-file/VSDD.md` — Verified Spec-Driven Development** — full VSDD pipeline
   (Spec Crystallization + Verification Architecture + TDD + Adversarial
   Refinement + Formal Hardening + Convergence). This design adopts **VSDD-lite**
   (Appendix A): spec supremacy as living specs, harness assertions not formal
   proofs, live probes, reviewer/auditor adversarial review, no exhaustive
   edge-case catalog. See Appendix A for the lite mapping.

7. **`to-file/messaging.md` — Minimal Agent-to-Orchestrator Communication** —
   v1.1 contract integrated into Phase 2 (§2e): Builder writes Crosslink
   `agent-communication` with `type/blocking/message`; Observer watermark watcher
   on new changes only; `blocking=true` => WAITING_FOR_ORCHESTRATOR (not stalled);
   forward via existing Observer->Orchestrator path; no broker/MCP; 10 acceptance
   tests; deferred sandbox hook as optimization only.

### Informational

- `.design/lifecycle-manager-design.md` (superseded in part, retained as
  lifecycle-semantics baseline; see Supersessions)
- `docs/research/Workflow Topology Design and Reasoning Record.md` (position
  store, staleness trigger, AUDITOR two-phase)
- Issues #483-#487, #489 (filing territory — consumed, not duplicated)
- Issues #488, #490 (swarm design intent and Hybrid F epic — this doc is their
  consolidated deliverable, committed referencing both)

## Supersessions

| Superseded / Partially Superseded | What changes | What is retained |
|---|---|---|
| `.design/lifecycle-manager-design.md` | Treated launch as infallible; filing as per-issue comments; no earlyoom attribution; no D1-D4/Secrets/Startup-Verification wiring | Agent lifecycle states (LAUNCHED->RUNNING->COMPLETED|FAILED|KILLED|PARKED|FROZEN), post-transition action table shape, SC1-SC5 validation intent |
| Any prior assumption that `journalctl -k` suffices for OOM forensics | Replaced by `journalctl -u earlyoom --since <window>` (may require sudo) per server-memory-management | — |
| Scattered operator-report filing (ad-hoc comments across issues) | Replaced by Hybrid F centralized epic + dual labels + sentinel sweep (§ Phase 2) | Per-transition evidence emission still originates at the Builder/Observer; only the durable index is centralized |
| `to-file/messaging.md` as a standalone draft requiring a new protocol | Integrated as Phase 2 §2e: Crosslink convention (`type: agent-communication`, `blocking`, `message`) + watermark watcher + existing notification path; no broker/MCP; deferred sandbox hook documented as future optimization only | Semantic contract (blocking vs non-blocking), Builder convention, 10 acceptance tests (preserved verbatim as P2-MSG1..10), failure/recovery requirements |
| Prior assumption that VSDD requires formal proofs / exhaustive edge-case catalog on this host | Replaced by VSDD-lite (Appendix A): harness assertions, live probes, reviewer/auditor review, living specs | Spec supremacy principle, behavioral contract + interface definition, Chainlink/Crosslink bead traceability |

This document is the **single swarm entry point** for #460-lineage hardening;
per-issue specs (#483-#487, #489) remain as work items but defer to this design
for acceptance criteria. It is also the **final project piece** consolidating
`to-file/messaging.md` and `to-file/VSDD.md` (lite) per #495 — downstream
consumers read this design, not the to-file drafts in isolation.

---

## Overview — Three Phases, One Swarm

```
Phase 1: LAUNCH RESILIENCE  (mechanical gate, blocks Phase 2 & 3 if unmet)
   |
Phase 2: HYBRID F FILING    (centralized operator surface + sentinel triage + agent-communication)
   |
Phase 3: DURABILITY & TRACEABILITY (#473 — evidence-at-transition + earlyoom discrimination)
```

Dispatch shape: **swarm** (`crosslink swarm init --doc .design/observer-swarm-v1.1-resilience.md`),
three sequential phases with gates. Each phase carries its own acceptance
criteria below — a phase gate fails if ANY criterion is unmet. The swarm is a
**prove-serially-then-fan-out** shape: Phase 1's gate is proven before Phase 2
fans handling paths; no phase parallelizes an unproven pattern.

Model routing: per `.crosslink/knowledge/model-discipline.md`; no model pins
in this doc — the orchestrator resolves at runtime and records provenance
(#441 M3).

---

## Phase: Launch Resilience - Mechanical Gate

- Pre-launch memory-headroom check (free -m available RAM+swap vs 10% earlyoom trigger + 1GB/fleet floor) with launch-deferred-memory event (P1-AC1)
- Earlyoom SIGTERM biggest-consumer model (RAM+swap <10%, stock Debian defaults, 3.4G/3.9G swap kills) documented in gate (P1-AC2)
- Forensic attribution path via journalctl -u earlyoom --since <window> (not journalctl -k) for SIGTERM deaths (P1-AC3)
- Mitigation knobs -m/-s/--prefer/--avoid/-r documented as tunable reserves without silent tuning (P1-AC4)
- Execution Boundary D1-D4 enforced as mechanical pre-launch rejection (P1-AC5)
- Secrets Handling enforced with named secret-placement location (path or env var), no secret in chat (P1-AC6)
- Startup Verification launch -> sleep 30s -> opencode.log tail + .kickoff-status check as post-launch health gate (P1-AC7)

### Problem (evidence-based)

Stock Debian earlyoom on the host SIGTERMs the biggest consumer when **both
RAM and swap fall below 10%** (defaults: no `-m`/`-s` overrides, no prefer/
avoid lists, only `-r 3600`). The host has 8GB RAM, ~1.9GB base stack, ~3GB
per session with subagents, and 3.9GB zram swap. Two concurrent sessions
exhausted swap at 3.4G/3.9G and killed the pp3g-qlIC collector at 05:58 UTC
2026-08-25 (issue #473). The earlier OBSERVER freeze-misfire at 05:41 under
swap exhaustion killed a healthy continuation builder when the pane-hash
heuristic matched identical hashes across two scans (~4.5 min apart) on a
self-throttling collector, wiping pre-commit work (no multi-signal
re-verification on the pane-hash path).

The July-13 crash postmortem shows the fleet headroom rule is not procedure
but survival: keep >=1GB headroom over base + expected fleet, defer/stagger
when available RAM+swap approaches the earlyoom trigger.

### Design

#### 1a. Pre-launch memory-headroom check (blocking gate)

Before any dispatch (orchestrator `crosslink kickoff run` / `crosslink swarm
launch`), the orchestrator or Observer admission surface runs:

```
free -m  →  read available column (RAM) + swap free
```

Gate: **defer or stagger when available RAM+swap headroom approaches the
10-percent earlyoom trigger**. Operationalization per server-memory-management:

- Compute `headroom = available_RAM + available_swap` (from `free -m`).
- Keep `headroom >= max(1GB, 10% * (RAM+swap))` plus expected fleet footprint
  (1.9GB base + 3GB per planned concurrent session is the default model; heavy
  collectors/scrapers scheduled in low-fleet windows or given their own ceiling).
- On gate FAIL: enqueue with delay, warn on the working issue, emit a
  `launch-deferred-memory` event — do not launch and starve the fleet.

This is a **mechanical gate, not advisory text**. It renders as a launch-time
refusal with evidence (the `free -m` snapshot attached to the deferral comment)
and is auditable in `events.jsonl`.

References: `server-memory-management.md` § "PRE-LAUNCH CHECK" + Three-Layer
Defense table.

#### 1b. earlyoom behavior inside the gate (what the gate guards against)

Hard-coded defaults on this host (operator-confirmed):

- Threshold: RAM <10% **AND** swap <10% → SIGTERM biggest consumer.
- No overrides in use; no prefer/avoid lists.
- Self-report cadence `-r 3600`.

The gate's 10-percent calculation mirrors earlyoom's own trigger so the
orchestrator stays ahead of the killer rather than racing it. The gate does not
re-implement earlyoom; it avoids waking it.

#### 1c. Forensic attribution path (non-blocking, post-incident)

Any process that dies with SIGTERM/Terminated **without** a kernel OOM line in
`journalctl -k` must NOT be attributed to the kernel. Check:

```
journalctl -u earlyoom --since <death-window>   # may require sudo
# empty == not logged to kernel ring (earlyoom is userspace)
```

Finding #473 upgraded from guess to evidence-based-strong only after this
distinction was made; the earlier empty `journalctl -k` was a forensics trap.
The discrimination logic (Phase 3) consumes this path.

#### 1d. Mitigation knobs (tunable, not default-tuned now)

Documented for future tuning, not enabled at gate time:

- `-m PERCENT`, `-s PERCENT` — move RAM/swap thresholds.
- `--prefer REGEX`, `--avoid REGEX` — protect opencode TUI / target fleet patterns.
- `-r SECONDS` — self-report cadence.

Rationale for leaving defaults intact in v1.1: the gate strategy is admission
control (fewer concurrent heavy sessions), not earlyoom re-tuning; knobs are
reserved for post-measurement tuning when live fleet data shows a safer curve.
Any future change records its `-m`/`-s` values in the design and the knowledge
page together (§5.5 two-repo sync if touched).

#### 1e. Playbook propagation — Execution Boundary D1-D4, Secrets Handling, Startup Verification

These three addenda to `agent-orchestration-playbook.md` (from #462 doctrine)
become **mechanical checks** inside Phase 1, not prose:

**Execution Boundary D1-D4 (binding):**

- D1 — Any shell/config/admin-UI/SSH action is agent work by default; operator never performs it.
- D2 — Operator surface = decisions/priorities/approvals/review + at most ONE irreducible human-identity action presented as a single step.
- D3 — >1 such action mid-task = workflow wrong → stop, re-plan for delegation.
- D4 — Multi-step terminal sequences, menu navigation, port flags, config-file edits are never given to the operator, even as copy-paste blocks.

Mechanical enforcement: dispatch specs are rejected if they delegate >1 human
click, or if they hand the operator a shell command, admin console, or SSH
step. The orchestrator's prompt builder enforces this; the Builder never asks
the operator for execution help.

**Secrets Handling (binding, #462 addendum 2026-08-25):**

- Agents NEVER ask the operator for codes/keys/tokens inside chat.
- Operator places secrets ON THE MACHINE themselves (file under
  `/tmp/opencode/secrets/` or env var they set); agents learn only WHERE to
  find it (path/var name), never its value.
- Every dispatch spec that needs external credentials names a secret-placement
  location explicitly.

Mechanical enforcement: a dispatch missing that location field is rejected at
the gate (same admission surface as 1a).

**Startup Verification — launch -> sleep 30s -> opencode.log tail + .kickoff-status check (interim, until Observer F2 fast-path is live):**

- Evidence 2026-08-24 forensics: death signatures appear within seconds
  (consent-gate fatal ~6s; rate-limit parking within one cycle). Staleness
  thresholds (45-90 min) are SUPERSEDED for launch-window checks.

Mandatory sequence per launch, before reporting healthy:

1. launch
2. sleep 30s
3. check `opencode.log` tail for the session — creation line present, no
   `AI_APICallError` / `retry-after` / `consent-gate` signature, tracking
   heartbeats advancing — AND check `.kickoff-status`
4. only then report status

Mechanical enforcement: the orchestrator's post-launch verifier runs this
sequence; a missing creation line or a consent-gate/retry-after signature
fails the health check and triggers relaunch-with-backup-model before any work
is entrusted to the agent (prevents the #462 "reported healthy at t=0 while
dead" class).

These three are **playbook updates that Phase 1 codifies as mechanical gates**.
They are not deferred to later phases; they are part of the launch-resilience
gate that blocks swarm progression.

### Phase 1 Acceptance Criteria

| ID | Criterion | Evidence |
|---|---|---|
| P1-AC1 | Every dispatch consults `free -m` available column and a computed RAM+swap headroom against the 10% earlyoom trigger + 1GB / fleet-footprint floor before launch; launches that would breach are deferred with a `launch-deferred-memory` event and a comment carrying the `free -m` snapshot | Deferral comment + events.jsonl entry + code call site that runs `free -m` |
| P1-AC2 | Earlyoom kill model (SIGTERM biggest consumer when RAM and swap <10%; stock Debian defaults; observed kills of opencode + pp3g-qlIC at 3.4G/3.9G swap) documented in the gate's comments/code, matching `server-memory-management.md` | Knowledge-page citation + in-code comment citing defaults |
| P1-AC3 | Forensic path for SIGTERM deaths uses `journalctl -u earlyoom --since <window>` (with sudo note), NOT `journalctl -k`; the trap is documented where attribution logic lives | Grep finds no `journalctl -k` in new attribution code; comment cites earlyoom unit journal |
| P1-AC4 | Mitigation knobs `-m`/`-s`/`--prefer`/`--avoid`/`-r` are documented as tunable reserves with current values (unconfigured) stated; no silent tuning | Doc string / design parity check passes |
| P1-AC5 | Execution Boundary D1-D4 enforced as a mechanical pre-launch check: dispatch specs delegating shell/admin/SSH steps or >1 human action are rejected | Rejection test: dispatch with 2 human clicks refused |
| P1-AC6 | Secrets Handling enforced: dispatch specs requiring external credentials without a named secret-placement location (path or env var) are rejected; no secret value enters chat | Rejection test + chat log contains no secret values |
| P1-AC7 | Startup Verification sequence (launch -> sleep 30s -> opencode.log tail + .kickoff-status check) implemented as post-launch health gate; staleness thresholds not used for launch-window verdict | Log evidence: health check runs sleep 30s, tails opencode.log for creation + absence of AI_APICallError/retry-after/consent-gate, checks .kickoff-status before reporting healthy |
| P1-GATE | All P1-AC1 through P1-AC7 pass | Phase 2 does not open until this gate is green |

---

## Phase: Centralized Filing - Hybrid F

- Filing via crosslink quick with BOTH labels observer + operator-report (P2-AC1)
- Parent epic Observer Operator Reports as human triage queue (epic labeled epic, observer, operator-report) (P2-AC2)
- Sentinel poll watcher triage loop polling open observer+operator-report issues (P2-AC3)
- Observer sweep from same label pair into knowledge/execution-engine-backlog.md idempotent and incremental (P2-AC4)
- Backlog page follows Documentation Standard and mirrors #483-#487 (P2-AC5)
- Sync mechanisms explicit: SESSION-END.md handoff today vs auto-export timer #487 future (P2-AC6)
- Workflow topology preserved: central epic = human index, label poll = machine surface, Observer sweep = durability (P2-AC7)
- Builder agent-communication convention `type: agent-communication` + `blocking` + `message` on Crosslink (P2-MSG1..2 — §2e)
- Observer Crosslink watcher on new changes only with watermark/cursor; no full history scan (P2-MSG5..6)
- Blocking semantics: `blocking=true` => WAITING_FOR_ORCHESTRATOR (not stalled); `blocking=false` => continue with normal liveness (P2-MSG2,8,9)
- Forwarding via existing Observer->Orchestrator notification path; no new broker/MCP (P2-MSG3..4, P2-NO-BROKER)
- 10 messaging acceptance tests (P2-MSG1..10) plus deferred sandbox hook documented as future optimization only (P2-DEFERRED)

### Problem

Observer findings were scattered (per-issue comments with no operator index, no
machine-queryable surface, no durable git-tracked backlog). The operator
needed one place to triage; agents needed one label to file under; the
knowledge base needed one durable file that mirrors the live issue state.

A second gap surfaced in `to-file/messaging.md`: Builders that hit an
ambiguous spec or a blocking question had no reliable, inspectable path to the
Orchestrator. Ad-hoc comments did not carry machine-readable blocking semantics,
so the Observer's liveness model could not distinguish intentional waiting from
a stall, and the Orchestrator had no canonical place to respond without a new
protocol.

### Design — Hybrid F (chosen)

Hybrid F is the filing topology proven in issues #489 / #441-territory:

1. **Labels — `observer` + `operator-report` (both required).**
   Filing = one `crosslink quick` (or swarm-filed equivalent) with BOTH labels.
   Single-label issues are not operator reports. The dual-label requirement is
   mechanical (gate checks for both).

2. **Parent epic — `Observer Operator Reports` (canonical index for humans).**
   Every filed report sets its `parent` to the epic. The epic's issue list IS
   the human triage queue; closing the epic is forbidden until all children are
   resolved or explicitly moved. The epic carries `labels: epic, observer,
   operator-report`.

3. **Sentinel poll watcher — machine surface.**
   A sentinel (long-running poll loop, per `crosslink-subagent-orchestration.md`
   sentinel shape) polls the hub on cadence:
   ```
   crosslink issue list --label observer --label operator-report --state open
   ```
   On each sweep it triages: new reports get an inbox marker, stalled reports
   get a staleness nudge, close-ready reports surface to the orchestrator.
   The watcher owns no destructive action (read + flag only — execution is
   delegated to builders).

4. **Observer sweep — durable git-tracked file.**
   Observer monitors the same Crosslink label pair (`observer` + `operator-report`)
   and on cadence sweeps issues into the durable file
   `knowledge/execution-engine-backlog.md` (per the every-issue->knowledge-page
   rule discussed in #489). The sweep preserves evidence per the workflow
   topology (position/claim/every issue retains its evidence chain; the backlog
   is an index + summary, not a replacement). Incremental append, idempotent on
   re-sweep. Upstream: live issues are source of truth; the file is a
   git-tracked mirror so reasoning survives hub compaction and offline reads.

5. **Sync today vs future.**
   - Today: sync via `docs/SESSION-END.md` handoff (thin pointer) + manual
     or swarm-driven sweep. Issues #483-#487 already mirror into the backlog
     in this mode.
   - Future (issue #487): auto-export timer pushes epics/issues to git on
     cadence (`crosslink knowledge add/edit` or `ases-tools` export verb),
     making the backlog continuously fresh without a manual handoff.

6. **Hybrid F invariant.**
   Filing = `crosslink quick` with two labels + parent epic. Central epic view
   = index for humans. Label poll = machine surface. Observer sweep = evidence
   preservation to git. Violation of any one is a defect (e.g., filing without
   the epic loses the human queue; filing without labels loses the machine
   surface).

Territory note: #483 (launch-resilience doc), #484 (guard path-allowlist),
#485 (engine-backlog close gate), #486 (preflight doc check), #487
(auto-export timer) live in the same filing/sync territory and already mirror
to `knowledge/execution-engine-backlog.md` via the Hybrid F path — this design
does not duplicate them; it makes Hybrid F the contract they all satisfy.

### Design — Agent-to-Orchestrator Communication (messaging.md v1.1, §2e)

This subsection integrates `to-file/messaging.md` (EDASES Observer v1.1: Minimal
Agent-to-Orchestrator Communication) as a **small extension to the existing
Observer**, not a new subsystem. The invariant is asymmetry: upward uses the
existing durable coordination workflow; downward uses the existing
sandbox prompt/control path; the Observer connects the two by attention routing.

```
Builder
   │  structured Crosslink communication
   ▼
Crosslink  (durable, local-first SQLite + hub sync, typed comments, agent identity)
   │  new/changed state
   ▼
Observer  (existing continuous loop — no new daemon)
   │  existing supervisory notification
   ▼
Orchestrator
   │  existing sandbox prompt/control API
   ▼
Builder
```

No new broker, MCP, A2A, or message database is introduced in v1.1. Knowledge
pages are not the communication channel (coordination events, not durable
knowledge).

#### 2e.1 Communication record — Builder convention

When a Builder needs the Orchestrator's attention it creates a Crosslink
communication record using the **existing** Crosslink machinery (issue/session
comment with a narrow convention — no schema extension in v1.1 unless testing
proves `blocking` must become first-class queryable data).

Semantic payload — three fields:

```yaml
type: agent-communication
blocking: true | false
message: <agent's message>
```

Conceptual example:

```yaml
type: agent-communication
blocking: true
message: >
  The API contract conflicts with the issue specification.
  I need a decision before proceeding with the implementation.
```

Required semantics:

- `blocking: true` — Builder cannot or should not continue until the Orchestrator
  responds.
- `blocking: false` — Builder is informing the Orchestrator but can continue
  working without a response.

The existing Crosslink issue/session context supplies identity and coordination
context (agent id, issue/work item, timestamp/change id). The Builder does not
need to know how the Observer works — only: write the communication to Crosslink
and continue or wait according to `blocking`.

Crosslink is the durable source of truth, so the communication survives
Observer/Orchestrator/Builder restarts (see Tests 5 and 10).

#### 2e.2 Observer watcher — new changes only, watermark, no full scan

Add a Crosslink watcher/check to the **existing** Observer loop — do not create
a new daemon or event service:

```
Observer loop
├── process/liveness checks
├── heartbeat checks
├── lifecycle checks
├── rate-limit checks
├── Crosslink change detection
│   └── agent-communication detection  ← new, §2e
└── other existing checks
```

Requirements for the watcher:

- Process **new changes only**, maintaining a cursor/watermark (or whatever
  change-detection mechanism Crosslink already provides — e.g., `events.jsonl`
  offset, comment sequence, or hub `events.log` cursor). Do **not** repeatedly
  scan the entire database or full history on each tick.
- Consume the existing Crosslink local state + hydration/sync, not a new sync
  mechanism.
- Extract on detection: originating agent, associated issue/work item, `blocking`,
  `message`, timestamp/change id, plus standard agent metadata the Observer
  already includes in its other notifications.
- Emit through the **existing Observer → Orchestrator notification mechanism**
  with normal Observer metadata. Example shape:

```
AGENT COMMUNICATION

agent: builder-17
issue: #123
blocking: true

The API contract conflicts with the issue specification.
I need a decision before proceeding.
```

- Must not understand or answer the substantive question; must not become a
  conversational agent; must preserve the existing loop and failure handling.

Normalization note: the Observer normalizes the detected change into an internal
`AgentCommunication { agent, issue, blocking, message, timestamp }` event so a
future direct sandbox hook can converge on the same event without a second
architecture (see §2e.5).

#### 2e.3 Blocking semantics and liveness integration

`blocking` is not a convenience flag — it integrates directly with the
Observer's liveness model (playbook §5.8 cheap staleness trigger):

- `blocking: true` — Builder is logically `WAITING_FOR_ORCHESTRATOR`. The
  Observer **must not** classify the resulting inactivity as a stall. The
  Orchestrator is responsible for responding; the Builder resumes after the
  response arrives via the existing sandbox API.

```
Builder working → writes blocking question → WAITING_FOR_ORCHESTRATOR
  → Observer notifies Orchestrator → Orchestrator responds → Builder resumes → WORKING
```

- `blocking: false` — Builder remains in ordinary working state. Observer
  informs the Orchestrator, but liveness monitoring continues normally; no stall
  suppression.

```
Builder working → writes non-blocking message → Observer notifies Orchestrator
  └────────────────────────► Builder continues (no stall suppression)
```

This distinction is the reason `blocking` exists: it prevents false stall
signals while preserving stall detection for genuinely stuck Builders. The
implementation must not create a separate "communication state machine" — the
existing execution/liveness state gains meaning from the Crosslink communication
state.

#### 2e.4 Forwarding and response path — no new broker

- Forwarding uses the **existing** Observer → Orchestrator notification path.
  No new broker, MCP, A2A, or persistent communication subsystem.
- Orchestrator response uses the **existing** sandbox prompt/control mechanism
  (kill/pause/resume/reprioritise + queued prompt injection). If the Builder is
  waiting, the response resumes it; if still working, the response queues to
  the existing injection point. Crosslink is not a bidirectional real-time
  transport — the loop is intentionally asymmetric (Builder → Crosslink →
  Observer → Orchestrator → sandbox API → Builder).
- Diagnostic chain remains inspectable with existing infrastructure: Builder →
  Crosslink record → Observer detection → Orchestrator notification → sandbox
  delivery → Builder. Every step has an existing artifact (Crosslink comment,
  Observer log, Orchestrator prompt).

#### 2e.5 Deferred sandbox hook — optimization, not prerequisite

Do **not** implement a dedicated sandbox → Observer communication API in v1.1
unless testing demonstrates a concrete need. The future low-latency hook is:

```
Sandbox API ──► AgentCommunication ──► Observer notification
                     ▲
Builder ──► Crosslink (durable record always written)
```

When/if added, both paths converge on the same internal `AgentCommunication`
event and Crosslink remains the durable record:

```
                    ┌──► Observer ──► Orchestrator
Builder ──► Sandbox ┤
                    └──► Crosslink
```

This gives low-latency attention **and** durable recovery/audit. The hook is
therefore an optimization of the existing architecture, not a foundation. Do
not preemptively implement: no first-class `blocking` schema field, no richer
communication types, no explicit request/response IDs unless real usage
demonstrates they are necessary.

### Phase 2 Acceptance Criteria

**Hybrid F filing (P2-AC1..7) and messaging (P2-MSG1..10) are one Phase 2 gate.
All must pass before Phase 3 opens. Messaging tests map verbatim from
`to-file/messaging.md` § Acceptance Tests.**

| ID | Criterion | Evidence |
|---|---|---|
| P2-AC1 | A filed operator report is created via `crosslink quick` (or swarm equivalent) with BOTH labels `observer` and `operator-report`; filing without both is rejected or flagged | Live `crosslink issue show <new>` shows both labels; negative test: single-label issue not treated as report |
| P2-AC2 | Every filed report has `parent: Observer Operator Reports` epic (epic itself labeled `epic, observer, operator-report`); the epic's open-children list is the operator triage queue | Epic `crosslink issue show <epic>` lists children; operator can triage from one view |
| P2-AC3 | Sentinel poll watcher implements the triage loop: polls open `observer+operator-report` issues on cadence, marks new/stalled/close-ready, flags without mutating issues destructively | Poll loop log + issue comment markers on a test report |
| P2-AC4 | Observer sweep from the same label pair into `knowledge/execution-engine-backlog.md` is idempotent and incremental; re-sweeping does not duplicate rows; new issues appear on next sweep | Two consecutive sweeps: second is no-op; new issue appears after third sweep |
| P2-AC5 | Backlog page follows Documentation Standard metadata (`program: EDASES, layer: Implementation`) and contains a table mirroring #483-#487: id, title, parent #441, status, one-line description, sync mechanism note | `knowledge/execution-engine-backlog.md` renders and passes doc existence checks |
| P2-AC6 | Sync mechanisms are explicit: today's path via `SESSION-END.md` handoff vs future auto-export timer (#487); neither path loses evidence on hub compaction | Design cites both paths; manual sweep test shows no loss after compaction |
| P2-AC7 | Workflow topology preserved: central epic view = human index, label poll = machine surface, Observer sweep = evidence durability — each is cited in the implementation | Code comments cite all three surfaces |
| P2-MSG1 | **Test 1 — Basic question (non-blocking):** Builder creates `type: agent-communication, blocking=false` communication. Crosslink contains the durable record, Observer detects it, Orchestrator receives it via existing notification path, Builder continues working | Crosslink comment present; Observer log shows detection; Orchestrator notification present; Builder hub position advances after write |
| P2-MSG2 | **Test 2 — Blocking question:** Builder creates `type: agent-communication, blocking=true` communication. Crosslink contains record, Observer detects it, Orchestrator receives it, Builder is represented as `WAITING_FOR_ORCHESTRATOR` rather than stalled | Crosslink comment present; Observer notification includes `blocking: true`; liveness state is WAITING_FOR_ORCHESTRATOR; no stall flag for >2× idle floor |
| P2-MSG3 | **Test 3 — Response (blocking resume):** Orchestrator responds through existing sandbox prompt/control API. Builder receives response, resumes, waiting state clears | Sandbox delivery receipt; Builder hub position advances with response ref; WAITING state transitions to WORKING |
| P2-MSG4 | **Test 4 — Active Builder response (queued):** Orchestrator responds while Builder is still working (non-blocking case). Response is queued through existing prompt mechanism, delivered at existing injection point; no new transport required | Queued-prompt log; Builder continues until injection point; no broker/MCP artifact |
| P2-MSG5 | **Test 5 — Observer restart durability:** Create a communication, restart the Observer, verify detection afterward (Crosslink as durable source of truth) | Communication written before restart; post-restart Observer log shows detection of same record via watermark recovery |
| P2-MSG6 | **Test 6 — Duplicate prevention:** Cause the same Crosslink state to be observed more than once; exactly one Orchestrator notification is emitted (watermark/cursor prevents re-delivery) | Two observation cycles over same DB state produce one notification; second cycle is no-op |
| P2-MSG7 | **Test 7 — Multiple Builders:** Multiple Builders submit communications concurrently; all are independently delivered with correct agent identity and issue context, without overwriting | Concurrent writes from builder-A/B/C; three distinct AgentCommunication events with correct agent+issue; Orchestrator receives all three |
| P2-MSG8 | **Test 8 — Continued work (non-blocking no false stall):** Submit non-blocking communication and have Builder continue meaningful work (commits/checkpoint cadence). No false stall while working | Non-blocking write + subsequent builder commits/checkpoints; liveness remains WORKING; no stall trigger |
| P2-MSG9 | **Test 9 — Waiting (blocking no false stall):** Submit blocking communication and intentionally stop Builder's normal work while awaiting Orchestrator. No false stall while in WAITING_FOR_ORCHESTRATOR | Blocking write + Builder idle; Observer classifies as WAITING_FOR_ORCHESTRATOR; cheap staleness trigger (>2× interval) does not fire |
| P2-MSG10 | **Test 10 — Recovery (cross-restart):** Terminate/restart components at different points in the communication path (Builder, Observer, Orchestrator) and verify durable Crosslink state prevents silent loss; communication remains discoverable if Orchestrator was unavailable at detection | Restart matrix (Builder before/after write; Orchestrator unavailable window); Crosslink record remains queryable; no silent loss |
| P2-NO-BROKER | No new broker/MCP/A2A/message-database is introduced; implementation reuses Crosslink durable substrate + existing Observer loop + existing Orchestrator notification + existing sandbox prompt path; grep finds no new broker config/service | Code search: no broker/MCP/A2A dependency; architecture diagram in §2e matches implementation |
| P2-DEFERRED | Deferred sandbox hook (direct Sandbox → Observer) is documented as a future optimization only, not implemented in v1.1; design states it converges on same AgentCommunication event and Crosslink remains durable record | Design §2e.5 present; no sandbox API code path in v1.1; decision log records deferral |
| P2-GATE | All P2-AC1 through P2-AC7 **and** P2-MSG1 through P2-MSG10 plus P2-NO-BROKER and P2-DEFERRED pass | Phase 3 does not open until this gate is green |

**Failure and recovery invariants (implicit in P2-MSG5..10, explicit as design constraints):**

- Communication written before Observer restart must still be detected afterward.
- Communication detected while Orchestrator is unavailable must remain discoverable (no silent loss).
- Builder that wrote a blocking question and then terminated must leave durable state for the Orchestrator.
- Duplicate observation must not spam the Orchestrator (watermark required).
- Multiple Builders' communications must not overwrite each other.
- Crosslink-read failure degrades the communication watcher only; it must not take down the entire Observer loop.

---

## Phase: Evidence Durability - Earlyoom Traceability

- Terminal verdict evidence bundle (opencode.log tail sha256 + pane tail + git status/diffstat + verdict timeline + hub position ref) synchronous at detection (P3-AC1)
- SIGTERM attribution via journalctl -u earlyoom --since <window> with machine field attribution: earlyoom | observer | failed | unknown (P3-AC2)
- Explicit negative earlyoom check record when journal empty for window (P3-AC3)
- FROZEN kills require multi-signal re-verification (pane-hash AND commit-age stale AND log-quiet AND hub-position static) (P3-AC4)
- Park-expiry re-verifies log tail before kill (P3-AC5)
- Self-throttling collectors not classified FROZEN on pane-hash alone; use PARKED/positive-progress and ~5m checkpoint cadence (P3-AC6)
- Fleet-size admission implication honored via Phase 1 gate + commit-age signal preventing concurrent exhaustion (P3-AC7)
- Durable store hub-ground-truth: bundle loss from /tmp without hub emission is defect (P3-AC8)

### Problem (from #473, evidence-graded)

- Pane-hash freeze heuristic false-positives on self-throttling collectors
  (sleep-and-wait loops produce identical hashes across ~4.5 min — proven).
- The failed kill at 05:41 was lucky (no-work destruction by accident — bug
  family, not design); the 06:41 retry succeeded and destroyed pre-commit work
  (proof the pane-hash path had no multi-signal re-verification).
- Collector death at 05:58 had NO kernel OOM line; attribution remained
  guess-level until earlyoom's userspace SIGTERM path was identified (swap
  3.4G/3.9G, stock earlyoom, hourly report only).
- Fleet-size exhaustion is an admission-policy problem, not a detector problem.
- Research/read-only roles need positive-progress signals, not non-quiet panes.

### Design

#### 3a. Evidence durability (already proven in Observer F1, now hardened)

Every terminal verdict (COMPLETED/FAILED/KILLED/PARKED-expiry/FROZEN) emits at
detection time, not archaeology time:

- attributed `opencode.log` tail (sha256)
- pane tail
- worktree `git status` / `diffstat`
- verdict timeline
- last hub position ref (`refs/heads/crosslink/agents/<id>/events.log`)

Composition is synchronous with detection (seconds, not minutes). Bundles live
under `/tmp/opencode/observer-state/evidence/<agent-id>/<ts>-<verdict>/` and
are referenced from the hub comment. The durable store rule (§5.8, AGENTS.md)
applies: the hub is the ground truth; the bundle is the evidence artifact.
Loss of `/tmp` without hub emission is a defect (caught by P3-AC1).

#### 3b. earlyoom traceability — FAILED/KILLED discrimination

When a builder dies with SIGTERM/Terminated or `exit 143`:

1. Run `journalctl -u earlyoom --since <window>` (window = death ±5 min;
   may require sudo — note that in the check).
2. If a matching earlyoom line is found → attribute `KILLED-BY-EARLYOOM`,
   emit a dedicated `earlyoom-kill` event (victim PID, journal line, swap %
   at time, available RAM+swap headroom from last `free -m` snapshot).
3. If no line is found → attribute `FAILED` (or `KILLED-BY-OBSERVER` if the
   Observer issued the kill), with the negative check recorded
   ("`journalctl -u earlyoom` empty for window <W>" — so a later reader knows
   the check ran).
4. The FAILED/KILLED discrimination is a **machine field** on the observation
   (`attribution: earlyoom | observer | failed | unknown`), not free-text
   inference, so downstream gates (e.g., #485 engine-backlog gate, staleness
   logic) can branch on it.

This consumes the 1c forensic trap and makes Finding 2's upgrade path
(guess -> evidence-based-strong) mechanical.

#### 3c. Multi-signal re-verification (extends FROZEN path)

The pane-hash-only path that caused the 06:41 destructive kill is gated
behind a multi-signal requirement:

- pane-hash AND commit-age stale AND log-quiet AND hub-position static

The park-expiry re-verification (log tail re-scan before any kill) and the
commit-age signal already landed in Observer v1 fix-pass (commits fb12f59,
1a23ab4). Phase 3 makes the multi-signal gate a **phase-gate invariant** —
any FROZEN kill emitted without all four signals is flagged as a policy
violation, even if the verdict was correct. This directly addresses #473's
"[FAILED/KILLED discrimination should consult journalctl -u earlyoom]" and
"guardrail gap vs spiral-authority spec" findings.

#### 3d. Positive-progress signals for research/read-only roles

Collectors and auditors emit periodic checkpoint posts (`--kind observation`,
`state=working`) plus incremental commits (builders) at ~5 min cadence per
`agent-orchestration-playbook.md` §5.4. Silence beyond `>2x` the idle floor is
the staleness trigger that causes the pre-positioned AUDITOR to act (not to be
summoned). Self-throttling loops are never classified as FROZEN on pane-hash
alone — they satisfy the park/rate-limit path instead.

### Phase 3 Acceptance Criteria

| ID | Criterion | Evidence |
|---|---|---|
| P3-AC1 | Every terminal verdict emits an evidence bundle (opencode.log tail sha256 + pane tail + worktree git status/diffstat + verdict timeline + hub position ref) synchronously at detection, referenced from the hub comment; no post-hoc archaeology needed | Bundle dir exists per-verdict; hub comment contains bundle ref + sha256; test kill shows bundle within seconds |
| P3-AC2 | Any SIGTERM/Terminated death without kernel OOM is attributed via `journalctl -u earlyoom --since <window>` (with sudo note recorded); attribution is a machine field `attribution: earlyoom \| observer \| failed \| unknown` | Grep finds no `journalctl -k` in attribution code; attribution field present on observation; earlyoom-positive case shows journal line in event |
| P3-AC3 | Negative earlyoom check is explicit: when the journal is empty for the window, the observation records "`journalctl -u earlyoom` empty for window <W>" — a later reader can distinguish "checked and absent" from "not checked" | Test death with empty journal shows the explicit negative record |
| P3-AC4 | FROZEN kills require multi-signal re-verification (pane-hash AND commit-age stale AND log-quiet AND hub-position static); a kill lacking any signal is flagged as a policy violation | Attempted pane-hash-only kill is refused/flagged; test harness covers the refusal |
| P3-AC5 | Park-expiry re-verifies log tail before any kill (fresh rate-limit signature extends park; kill only on expiry AND clean tail) — verified by the existing fb12f59 path | Suite covers extension + grace-floor + clean-tail kill |
| P3-AC6 | Self-throttling collectors (long sleep-and-wait loops) are not classified FROZEN on pane-hash alone; they route through PARKED/positive-progress instead; research/read-only checkpoint cadence (~5 min) is the liveness signal | Self-throttle fixture stays non-frozen; checkpoint comments advance hub position |
| P3-AC7 | Fleet-size admission implication honored: Phase 1 gate + commit-age signal together prevent concurrent heavy-session exhaustion that triggers earlyoom | Two heavy sessions at 3.4G/3.9G swap trigger a deferral, not a kill |
| P3-AC8 | All durable stores are hub-ground-truth (per §6.5); bundles lost from `/tmp` without hub emission are a defect | Test: /tmp wipe still leaves hub comment + bundle ref recoverable |
| P3-GATE | All P3-AC1 through P3-AC8 pass | Swarm complete — ready for shakedown live n=1 |

---

## Configurability — Every Knob Documented Now, Formalized Later via Thin API

All user-configurable values that affect the swarm's resilience, liveness, and
durability are documented here as they exist today. The swarm does not take an
opinion on any single value — e.g., whether a knob is `off` versus `3s`, or
`10%` versus `12%`, is a calibration choice left to the operator and the live
fleet data it produces. This section is the **single inventory**; future work
formalizes it via a thin `ask-menu` API (operator surface unchanged — see
Execution Boundary D1-D4 — but knobs become queryable/settable without code
changes).

Per `server-memory-management.md` and `agent-orchestration-playbook.md`, no
silent tuning is permitted: any change to these values is recorded in the
design and the knowledge page together (§5.5 two-repo sync).

### Knob inventory

| Knob | Where documented / default (today) | What it controls | Notes |
|---|---|---|---|
| **Observer poll interval** | `tools/kickoff-notify.py` + `ases-kickoff-notify.timer` (15s cadence in Phase 1 monitor); `server-memory-management` knowledge page | How often the Observer/watcher scans for lifecycle transitions and agent-communication changes | Phase 1 watcher is monitor+notify only; Phase 2 sentinel poll for Hybrid F triage uses same cadence family; change requires updating timer unit + doc together |
| **Observer backup cadence** | Observer evidence sweep cadence (on each poll) + commit cadence per §5.4 (~5 min incremental commits for builders; ~5 min checkpoint+sync for read-only roles) | How often evidence bundles and hub positions are emitted to durable store | Loss-tolerance budget is ~5 min — floor MUST be <= budget; see playbook §5.8.1 validated cadence |
| **earlyoom `-m` (RAM threshold)** | `server-memory-management.md` § earlyoom; default **10%** (stock Debian, no override in use) | Available RAM percent below which earlyoom SIGTERMs biggest consumer (AND with `-s`) | Documented as tunable reserve; no silent tuning in v1.1 — gate mirrors this value |
| **earlyoom `-s` (swap threshold)** | Same; default **10%** (no override) | Available swap percent (AND with `-m`) | Same as `-m` — admission gate uses both |
| **earlyoom `--prefer` / `--avoid` regex** | Same; default **none** in use | Which process names earlyoom prefers/avoid killing | Reserved for protecting opencode TUI vs fleet patterns; any future list recorded in design + knowledge page |
| **earlyoom `-r` report cadence** | Same; default **3600s** (hourly) | Self-report cadence for earlyoom | Observed hourly report only during #473 window |
| **`free -m` headroom floor** | `server-memory-management.md` § PRE-LAUNCH CHECK; Phase 1 gate §1a: `headroom >= max(1GB, 10%*(RAM+swap)) + fleet footprint` | Admission gate threshold that defers launches when headroom approaches earlyoom trigger | Fleet footprint default: 1.9GB base + 3GB per planned session; heavy collectors scheduled in low-fleet windows |
| **Startup Verification sleep** | `agent-orchestration-playbook.md` §1 / Phase 1 §1e; **sleep 30s** (interim, until Observer F2 fast-path is live) | How long after launch the post-launch verifier waits before tailing `opencode.log` + `.kickoff-status` | Staleness thresholds (45-90 min) SUPERSEDED for launch-window; 30s is not tunable to `off` without a documented F2 replacement |
| **Swarm `budget-window`** | `docs/ORCHESTRATOR.md` + `agent-orchestration-playbook.md` §5.2; launch-time recommendation per `crosslink swarm config --budget-window` (e.g., `2h` in examples); NOT a runtime hard limit | Estimation + launch-time gate (`launch_budget_aware`: Block/Split) for swarm dispatch; no runtime termination — agents exceeding window are NOT killed | Set realistic windows and enforce through gates + checkpoints, not hard kills |
| **Sentinel poll cadence** | `crosslink-subagent-orchestration.md` sentinel shape + Phase 2 Hybrid F §2 (sentinel poll watcher); polls `observer+operator-report` open issues on cadence | How often the sentinel triages new/stalled/close-ready operator reports (read+flag only) | Same watermark discipline as Observer watcher — new-changes-only, cursor, not full DB scan |
| **Auto-export cadence** | Issue #487 design; Phase 2 § Hybrid F sync §5: future timer pushes epics/issues to git via `crosslink knowledge add/edit` or `ases-tools` export | How often the durable mirror `knowledge/execution-engine-backlog.md` would be auto-refreshed if #487 lands | Today: `SESSION-END.md` handoff + manual/swarm sweep; future: timer cadence documented alongside this knob |

### Formalization path (thin API ask-menu, later)

V1.1 deliberately keeps knobs as **documented values with code-located defaults**
rather than a formal configuration subsystem. The next step, when justified by
live fleet evidence, is a thin `ask-menu` API that makes these knobs
queryable/settable without code edits — e.g., `crosslink swarm config --ask`
or `crosslink knowledge edit` surfacing the table above as a menu. Until then,
any knob change follows the two-repo sync rule (§5.5) and is recorded in both
the design and `server-memory-management.md` together. No opinion is offered
here on whether any knob should be `off` versus `3s` (or `10%` versus any other
percent) — that is a deliberate non-position; calibration follows measurement.

---

## Cross-Cutting Requirements

### Documentation Standard compliance

- This file carries full frontmatter per `docs/standards/Documentation Standard.md`
  (`title`, `program`, `layer`, `document_type`, `status`, `authority`,
  `canonical_repository`, `depends_on`, `consumed_by`, `related_documents`,
  `supersedes`, `last_updated`). All downstream patches (playbook edits,
  knowledge page updates, `knowledge/execution-engine-backlog.md`) carry theirs.
- `depends_on` now includes `to-file/VSDD.md` and `to-file/messaging.md` as the
  integrated final pieces; `supersedes` notes the messaging draft integration
  and the VSDD-lite calibration (see Appendix A).

### Two-repo sync (§5.5)

Any edit to `agent-orchestration-playbook.md` operator profile (§1) or to the
KICKOFF template `Progress Check-Ins` that lands for Phase 1 must be mirrored
to the sibling repo in the same process (never in a follow-up issue).

### Claim discipline

All producer claims that cross a role boundary state WHY / WHAT / HOW CERTAIN /
WHAT-NOT-TESTED. Cheapest discriminating test runs before expensive work
(positive-progress checkpoint + journalctl attribution before any FROZEN kill).
Messaging `blocking` claims carry the liveness disclosure (WAITING vs stalled).

### What is explicitly NOT in scope for v1.1

- Earlyoom re-tuning (`-m`/`-s` value changes) — documented as reserves only.
- Off-server rclone remote wiring beyond explicit pending-flag behavior
  (remotes exist but unwired — #462 parked state).
- New top-level scripts/plugins (consolidation discipline: single
  `scripts/observer/` directory, policy states its layer home).
- New broker/MCP/A2A messaging subsystem — Phase 2 §2e explicitly forbids it;
  the deferred sandbox hook is optimization only (P2-DEFERRED).
- Exhaustive edge-case catalog — VSDD-lite (Appendix A) replaces it with live
  probes + adversarial review (see there for rationale).

---

## Appendix A — VSDD-lite: Verified Spec-Driven Development, Lite Adoption

**Source:** `to-file/VSDD.md` (VDD × TDD × SDD fusion: Spec → Tests → Verification
→ Adversarial Refinement → Formal Hardening → Convergence with Four-Dimensional
Hallucination-based termination).

This appendix records **how v1.1 adopts VSDD in lite form** — what we take, what
we deliberately thin, and why the thinning is correct for this host and this
swarm. The full VSDD remains the aspirational pipeline; v1.1 is its
evidence-gated, operations-grounded subset.

### A.1 What VSDD-lite takes

| VSDD principle | Lite adoption in v1.1 |
|---|---|
| **Spec supremacy** — specs are the highest authority below the human; tests serve specs; code serves tests | Adopted, but **living specs**: `to-file/VSDD.md` § Spec Crystallization is respected — behavioral contracts, interface definitions, and edge cases are enumerated per-phase (see P1-AC*, P2-*, P3-*), but specs are not frozen artifacts. They evolve via measured evidence (memory forensics #473, watcher cadence calibration) and each change re-enters the spec → test → review loop. This design itself is a living spec. |
| **Verification Architecture (Purity Boundary Map, Provable Properties Catalog, Tooling Selection)** | Thinned to **verification architecture lite**: instead of formal proof harnesses (Kani/CBMC/Dafny/TLA+), v1.1 requires **testable harness assertions** — harness assertions that run in CI or the live probe suite, not mathematical proofs. The purity boundary is pragmatic: the deterministic, inspectable core (admission gate calculation, watermark cursor, attribution field) is isolated from the effectful shell (systemd scope, journalctl I/O, hub writes) so harnesses can reason about it without mocking the universe. |
| **Test-first (Red → Green → Refactor)** | Adopted as **test-first via live probes**, per `agent-orchestration-playbook.md` §5.8 cheap staleness trigger. The "tests" that gate decisions are live probes against the real host: `free -m` headroom checks, `journalctl -u earlyoom --since <window>` attribution, five-minute checkpoint liveness, swarm gate live n=1 shakedowns — not offline unit tests of mocked memory pressure. Live probes are the cheapest discriminating test for the failure classes we actually hit. |
| **Adversarial review** | Adopted via the existing **reviewer/auditor** roles: reviewer = pre-consumption readiness audit (testability + evidence + certainty labels); auditor = one-role/two-phase in-flight divergence verifier (Phase 1 monitor alongside builder + Phase 2 post-hoc, per playbook §5.8). Added-theory Adversary (different model family) and fresh-window entropy-resistance are honored where model routing permits. |
| **Traceability — Spec → Bead → Test → Implementation → Review → Proof** | Adopted as Crosslink bead traceability: every P1/P2/P3 acceptance criterion maps to a Crosslink bead/issue and is referenced in hub comments and bundle refs. The "proof" column is the harness + live-probe evidence chain, not a formal proof artifact. |

### A.2 What VSDD-lite deliberately does NOT take (and why)

| Full VSDD element | Why v1.1 defers it |
|---|---|
| Formal proof harnesses (Kani proof harnesses, Dafny contracts, TLA+ invariants) and proof-execution gate | The pure core here is small (gate arithmetic, watermark, attribution field) and its correctness is validated by live forensics (swap 3.4/3.9G, `journalctl -u earlyoom`, 05:41 freeze misfire) more cheaply than by a model checker. Formal tooling constraints would dictate module boundaries that the host's systemd/earlyoom/host reality already dictates. Revisit when the pure core grows to a scope where proofs gate promotion. |
| Exhaustive Edge Case Catalog ("What happens when input is null/empty/max/negative/unicode/concurrent?") | Replaced by **live-probe edge cases**: the edges that actually killed agents (self-throttling collector hash collisions, swap exhaustion at 3.4G, consent-gate ~6s death, rate-limit parking within one cycle). An exhaustive catalog for a supervision system whose edges are host-resource edges is not the cheapest discriminating set — the forensics are. |
| Mutation testing (mutmut/Stryker), structured fuzzing (AFL++/cargo-fuzz/libFuzzer), Wycheproof/Semgrep as mandatory CI gates | Valuable where the codebase is a crypto/parser/arithmetic core; overkill for a swarm whose dominant failure mode is admission + attribution + filing durability. Harnesses + live shakedowns + reviewer/auditor cover the current risk. |
| Hallucination-based termination ("Adversary forced to invent flaws") across four dimensions | Replaced by **gate-based termination**: P1-GATE, P2-GATE, P3-GATE as the convergence signals. A phase gate that fails on any AC is the operational equivalent of "Adversary still finds a legitimate hole." |

### A.3 Why lite is the correct calibration here

VSDD is high-ceremony by design and worth it when correctness is
non-negotiable and the codebase is a pure computational core. The Observer
swarm is a **host-coupled supervision system**: its correctness is dominated by
systemd scopes, earlyoom userspace kills, `free -m` accounting, hub durability,
and poll cadences — not by a provable arithmetic invariant. Forcing formal
hardening onto that substrate would make verification architecture dictate host
architecture rather than the reverse — exactly the inversion VSDD warns against
when purity boundaries are drawn late. Lite therefore applies VSDD's sharpest
lever — spec supremacy with living specs and adversarial review — and leaves
the heavyweight tooling for a subsystem that actually has a deterministic pure
core to prove.

---

## References

- `docs/architecture/Execution Engine Vision.md` — canonical vision.
- `.crosslink/knowledge/server-memory-management.md` (2026-08-25) — earlyoom
  defaults, forensic trap, pre-launch `free -m` rule, mitigation knobs.
- `.crosslink/knowledge/agent-orchestration-playbook.md` (2026-08-25) — D1-D4
  operator profile, Secrets Handling, Startup Verification, durability cadence,
  staleness trigger, review-before-consume / AUDITOR topology.
- Issue #473 — research findings that drive Phase 3 (including verbatim
  forensic timeline 05:41-05:58 UTC 2026-08-25).
- Issue #462 doctrine — binding D1-D4, Secrets Handling, Startup Verification
  decisions (operator 2026-08-24/25 with propagation commits 31415244 etc.).
- Issue #489 / #441 territory — Hybrid F filing + `knowledge/execution-engine-backlog.md`
  + auto-export timer #487.
- `to-file/VSDD.md` — Verified Spec-Driven Development (VDD×TDD×SDD fusion);
  lite adoption documented in Appendix A: spec supremacy as living specs,
  verification lite via harness assertions, test-first via live probes per
  playbook cheap staleness trigger, adversarial review via reviewer/auditor, no
  exhaustive edge-case catalog.
- `to-file/messaging.md` — Minimal Agent-to-Orchestrator Communication (v1.1);
  integrated in Phase 2 §2e: `type: agent-communication` / `blocking` / `message`
  convention, watermark watcher on new changes only, `blocking=true` →
  WAITING_FOR_ORCHESTRATOR, forward via existing Observer→Orchestrator path, no
  broker/MCP, 10 acceptance tests (P2-MSG1..10), deferred sandbox hook.
- Issues #488 and #490 — swarm design deliverable refs (this commit references
  both as the consolidated final piece per #495).

