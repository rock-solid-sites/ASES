---
title: Observer Conformance Suite — Instantiation of the Universal Conformance Checklist against Observer Swarm v1.1
program: EDASES
layer: Implementation
document_type: Conformance Suite
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 523

depends_on:
  - to-file/ASES Universal Conformance Checklist.md (2026-08-29)
  - .design/observer-swarm-v1.1-resilience.md @3fc3c60a
  - to-file/VSDD Adaptation Profile.md
  - to-file/VSDD.md (lite adoption per design Appendix A)
  - .crosslink/knowledge/agent-orchestration-playbook.md (§5.4, §5.8, §5.8.1)
  - server-memory-management knowledge page (2026-08-25 revision)
  - docs/standards/Documentation Standard.md

consumed_by:
  - Observer Swarm v1.1 phase gates (P1-GATE, P2-GATE, P3-GATE)
  - VSDD Phases 2–6 gates (lite adoption)
  - Adversarial reviewer gate (pedantic frontier review, issue #523 purpose)
  - Builder completion gate

related_documents:
  - scripts/observer/observer.sh
  - scripts/observer/tests/run-tests.sh
  - .design/lifecycle-manager-design.md (superseded in part; lifecycle-semantics baseline)
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/conformance/Stop-Button-Conformance-Suite.md (sibling instantiation, format precedent)

implements:
  - ASES Universal Conformance Checklist instantiation (§§1–36)

supersedes: []
superseded_by: []
last_updated: 2026-08-30
---

# Observer Conformance Suite — Universal Checklist §§1–36 vs Observer Swarm v1.1

> **Scope:** Project-specific instantiation of the 36-dimension ASES Universal
> Conformance Checklist for the Observer Swarm v1.1 resilience hardening
> (issue #523). Each dimension records applicability, the instantiated
> obligation, mechanism, verification, evidence pointers, and status. This
> suite is the single traceability anchor for the swarm's VSDD-lite Phases 2–6
> and is written explicitly for **pedantic frontier adversarial review**: every
> invariant is stated, every forbidden transition is enumerated, every status
> is graded against evidence that actually exists in the repository, and every
> discrepancy between design and implementation is disclosed rather than
> smoothed over.
>
> **Governed artefact:** the Observer Swarm v1.1 state model — three nested
> layers, defined in §5 below. The design document
> (`.design/observer-swarm-v1.1-resilience.md` @3fc3c60a) is the behavioural
> contract; `scripts/observer/observer.sh` is the implementation; T1–T27 of
> `scripts/observer/tests/run-tests.sh` are the model-derived tests.

---

## 0. Reading Guide and Evidence-Grading Discipline

**Status vocabulary** (Checklist §3): `[ ] OPEN`, `[x] VERIFIED`, `[~] PARTIAL`,
`[!] FAILED`. **Applicability vocabulary**: `APPLICABLE`,
`NOT APPLICABLE`, `OUT OF SCOPE`, `BLOCKED`. `BLOCKED` is not `VERIFIED`.

**Evidence classes** (Checklist §4 / Profile §15): MODEL, CONFORMANCE, UNIT,
PROPERTY, MODEL-BASED, INTEGRATION, RESOURCE, OBSERVATION, MUTATION,
INSPECTION, OPERATIONAL. No class is treated as stronger than it is. In
particular, throughout this suite:

- **MODEL** = the design document's prose/tables (a claim about intended
  behaviour, not evidence that behaviour exists).
- **UNIT** = a T-test in `run-tests.sh` executed under `OBSERVER_DRY_RUN=1`
  against the real `observer.sh` (hermetic, no real mutations).
- **INSPECTION** = direct code reading (function/line pointers in this suite).
- **OBSERVATION** = live-host forensic history cited by the design (#473
  timeline, #460 shakedown). Historical observation is not reproducible
  on demand and is labelled as such.
- **OPERATIONAL** = the harness itself running green (see §32 for its limits).

**Honesty rules enforced in this suite:**

1. A dimension whose only evidence is the design document is graded at best
   `PARTIAL` (design exists, implementation unproven), and `OPEN` where the
   obligation requires implementation to mean anything.
2. Every design-vs-implementation divergence found during instantiation is
   recorded in the Discrepancy Register (§37) and reflected in the affected
   dimension's status — not buried in prose.
3. The issue that commissioned this suite (#523) names `run-tests.sh
   T28-T33` as an evidence pointer. **No such tests exist on any branch**;
   the harness ends at T27. This is treated as a stale pointer and recorded
   (§37 D1); evidence pointers in this suite cite the tests that actually
   exist.

---

## 1. Canonicality — APPLICABLE — VERIFIED

The Universal Checklist remains domain-independent; this file carries all
project-specific states, events, resources, tests, and assumptions. No
universal obligation has been silently rewritten. Where the swarm's VSDD-lite
adoption (design Appendix A) deliberately thins a universal obligation
(e.g. no formal proof harnesses, no exhaustive edge-case catalog, no
mandatory mutation-testing CI gate), the thinning is **declared in §35
adaptations** with the design's rationale, not smuggled in.

Evidence: this file exists; the Universal Checklist is quoted by dimension
number throughout; adaptations are itemised in §35. Status: VERIFIED.

---

## 2. Lifecycle Integration (VSDD Phases 1–6) — APPLICABLE — PARTIAL

| Phase | Instantiation in this swarm | Status |
|-------|------------------------------|--------|
| 1a Specification | Design doc @3fc3c60a: three phases, per-phase acceptance criteria P1-AC1..7, P2-AC1..7 + P2-MSG1..10 + P2-NO-BROKER + P2-DEFERRED, P3-AC1..8; knob inventory; explicit not-in-scope list | VERIFIED (MODEL) |
| 1b Verification architecture | VSDD-lite (design App. A): harness assertions + live probes + reviewer/auditor adversarial review; no formal proofs; recorded in §23 here | VERIFIED (MODEL) |
| 1c Spec review gate | Design review happened via swarm-design review passes (#488/#490 lineage); formal 1c checklist gate not recorded for this design | PARTIAL |
| 2 Test-first | T1–T27 exist and exercise the implemented core (verdict transitions, gates, authority, mode). Red-gate discipline (tests created before corresponding implementation accepted) is **not evidenced** per-test — commit history shows test+implementation landing in the same commits (e.g. 2e690049, 1050447c, 2fa5a189, c5eb6e72) | PARTIAL |
| 3 Adversarial refinement | This suite is the refinement artefact; the pedantic adversarial review it is written for has **not yet run** | OPEN |
| 4 Feedback integration | Shakedown-driven fixes integrated and re-tested: silent breaker-deny → loud (#460, T20a/T20b), park-expiry re-verification (fb12f590, T5), instance lockfile (51ed928f, T19), watermark hold on sync failure (5cbfbc86), fail-closed mode/owner/gate pass (2e690049, 1050447c, 2fa5a189, c5eb6e72) | VERIFIED |
| 5 Formal hardening | Per VSDD-lite: harness + live probes are the hardening; executed for the implemented core (T1–T27 green); Phase 1/2 obligations have nothing to harden yet | PARTIAL |
| 6 Convergence | Requires P1-GATE, P2-GATE, P3-GATE green. P3 core is test-green; P1 and P2 are unimplemented; earlyoom attribution (P3-AC2/3) missing | OPEN |

Traceability chain (Checklist §28 / Profile §8) is instantiated per-dimension
in this file and summarised in the chain table at §28.

---

## 3. Checklist Semantics — APPLICABLE — VERIFIED

Convention adopted verbatim: `[ ] OPEN`, `[x] VERIFIED`, `[~] PARTIAL`,
`[!] FAILED`; applicability `APPLICABLE / NOT APPLICABLE / OUT OF SCOPE /
BLOCKED`; `BLOCKED` is not `VERIFIED`. Every dimension below carries both an
applicability and a status. No dimension is left unstated.

---

## 4. Evidence Classes — APPLICABLE — VERIFIED

Classes used in this suite, with their actual sources:

| Class | Source in this project |
|-------|------------------------|
| MODEL | `.design/observer-swarm-v1.1-resilience.md` @3fc3c60a (phases, ACs, invariants, knob inventory) |
| UNIT | `scripts/observer/tests/run-tests.sh` T1–T27 (hermetic, `OBSERVER_DRY_RUN=1`, isolated state dirs, fixture git repos) |
| PROPERTY | The convergent-gate and fail-closed-mode properties exercised exhaustively-by-construction in T21–T26 (see §9 for scope limits — these are bounded property checks, not exhaustive model exploration) |
| INTEGRATION | Not yet available: no test runs the Observer against a live hub/tmux fleet (the harness is hermetic by design; live n=1 shakedown is a post-P3-GATE step per design) |
| RESOURCE | T1 (worktree cleanup), T15 (dual-store backup with integrity checks), T18 (worktree preservation) |
| OBSERVATION | #473 forensic timeline (05:41 freeze misfire, 05:58 earlyoom SIGTERM at 3.4G/3.9G swap); #460 shakedown (05:26–05:54 breaker-deny archaeology) — historical, not reproducible on demand |
| MUTATION | Mutation-*detection* properties embedded in tests (T25 gate-held under repeated pane silence; T21 garbage-mode → observe; T22/T23 owner downgrades); systematic mutation testing is deferred per VSDD-lite A.2 (declared §35) |
| INSPECTION | Function-level code pointers in this suite (all `observer.sh` line numbers cited at @68750f28 working tree) |
| OPERATIONAL | Harness execution itself — fresh run during this suite's production: `RESULT: 181 passed, 0 failed` (T1–T27 incl. sub-checks, 2026-08-30, log retained at `/tmp/opencode/observer-tests-run.log`); see §32 for why a green harness is weaker evidence than it looks |

---

## 5. State Model Completeness — APPLICABLE — PARTIAL

The governed artefact is a **three-layer state model**. Completeness is
assessed per layer.

### 5.1 Layer A — Swarm phase gates (design-level; NOT implemented)

- **States:** `Phase 1 LAUNCH RESILIENCE` → `Phase 2 HYBRID F FILING` →
  `Phase 3 DURABILITY & TRACEABILITY`, each closed by a gate
  (`P1-GATE`, `P2-GATE`, `P3-GATE`).
- **Initial:** Phase 1. **Terminal:** Phase 3 gate green ("swarm complete —
  ready for shakedown live n=1").
- **Events:** gate evaluation (all ACs of a phase pass / any fails).
- **Guards:** a phase gate fails if ANY criterion is unmet (design, Overview).
- **Permitted transitions:** Phase N → Phase N+1 only on gate green.
- **Forbidden transitions:** opening Phase 2 with P1-GATE unmet; opening
  Phase 3 with P2-GATE unmet.
- **Effects:** phase opening authorises the next phase's work.
- **Identity/ownership:** swarm-level; per-phase work items are Crosslink
  issues (#483–#487, #489 territory; #488/#490 design deliverables).
- **Settlement:** gate-green recorded in issue comments (no mechanical gate
  artefact exists).
- **Invariants:** prove-serially-then-fan-out (no phase parallelises an
  unproven pattern).
- **Concurrency:** phases are strictly sequential.
- **Boundaries:** the swarm dispatches into the host (tmux, crosslink hub,
  opencode runtime).

**Status: PARTIAL.** The model is complete *as design* (MODEL evidence), but
Phase 1 and Phase 2 have **no implementation** — no `free -m` gate call site,
no `launch-deferred-memory` event emitter, no D1-D4/secrets dispatch
rejection, no startup-verification gate, no Hybrid F filing/sentinel/sweep,
no agent-communication watcher (verified by repo-wide search: zero hits for
`free -m` / `launch-deferred-memory` / `agent-communication` /
`operator-report` / `execution-engine-backlog` in `scripts/` and `tools/`;
no `knowledge/execution-engine-backlog.md` exists). Layer A obligations are
therefore **unverifiable**, not merely unverified: there is nothing to test.

### 5.2 Layer B — Observer six-class verdict matrix (implemented)

- **States (verdicts):** `COMPLETED` (DONE-CONFIRMED), `FINISHED-UNMARKABLE`,
  `FAILED`, `KILLED`, `PARKED`, `FROZEN` — the six-class taxonomy, declared
  UNCHANGED by v1.1 (design Supersessions; observer.sh header lines 38–45).
- **Derived/interim states:** `STALE-SUSPECT` (one warning cycle, then
  escalation), fast-path classes `PARKED-RETRYING`, `CONSENT-GATE-FATAL`,
  `RETRY-EXHAUSTED-DEAD`, `UNKNOWN` (observer.sh lines 74–79, 2241–2255).
- **Events:** liveness-scan verdict per cycle; fast-path log-line
  classification per cycle; park expiry; commit-age threshold crossing.
- **Guards:** deep probes only for candidate agents; once-per-episode dedup
  per (agent, verdict); circuit breaker on mutating actions.
- **Permitted transitions:** see transition table §7.
- **Forbidden transitions:** see §8.
- **Effects:** per-verdict action table (observer.sh lines 16–45):
  cleanup+deliverable-check+evidence-row (COMPLETED); findings-check+
  force-sweep flag (FINISHED-UNMARKABLE); worktree preservation+failure
  alert (FAILED); cleanup+orphan-check+termination record (KILLED);
  park+resume_at, never kill (PARKED); evidence bundle+auto-kill+cleanup+
  termination record (FROZEN, gated).
- **Identity/ownership:** agent slug identity; `.owner-orchestrator` stamp;
  session IDs recovered from attributed log sections (lines 56–60, 1814–1823).
- **Settlement:** terminal verdicts settle into `handled` map per
  (agent, verdict) with timestamp (line 1714).
- **Invariants:** see §9 (I1–I13).
- **Concurrency:** circuit breaker, single-instance lock, dedup windows
  (§14).
- **Boundaries:** opencode.log, tmux panes, git worktrees, crosslink hub,
  sqlite stores, rclone (§13).

**Status: VERIFIED** for the implemented matrix (UNIT T1–T8, T11–T14, T18,
T25–T27 + INSPECTION). The taxonomy is unchanged from the pre-v1.1 Observer,
which the design declares as a deliberate non-goal to redesign.

### 5.3 Layer C — Per-agent lifecycle phases (implemented, manager-state)

- **States:** `active` → {`parked`, `stale-suspect`} → terminal
  {`completed`, `finished-unmarkable`, `failed`, `killed`, `frozen-handled`};
  `parked` → `active` (recovery on RUNNING-ALIVE) or → `frozen-handled`
  (expiry + clean tail, via the gate).
- **Initial:** `active` (fresh_rec, line 1787). **Terminal:** the five
  terminal phases; a terminal phase suppresses re-entry to `active` for the
  same episode (line 1875 condition).
- **Events:** verdict per cycle; park expiry; fresh activity.
- **Guards:** park resolution precedes verdict dispatch (line 1826);
  terminal-phase check gates re-activation (line 1875).
- **Effects:** phase transitions recorded in `rec` and persisted atomically
  in manager-state.json.
- **Settlement:** `handled` map; `parked-recovered` / `parked-expired` /
  `parked-extended` events.

**Status: VERIFIED** (UNIT T1–T7, T11; INSPECTION lines 1796–1900).

### 5.4 Layer D — Execution-authority model (implemented, v1.1 C1–C4)

- **States:** `MODE ∈ {observe, act}` (resolved fail-closed, lines 444–461);
  per-action authorization state {allowed, downgraded(reason, owner)};
  convergent-gate state {allow, signals[], log_quiet, tail_changed}.
- **Initial:** observe (default; garbage → observe; DRY_RUN alias wins).
- **Guards:** act requires OBSERVER_ORCHESTRATOR_ID at startup (loud fatal,
  lines 463–475); authorization precedes breaker which precedes execution
  (lines 1147–1176, 1192–1209); gate sits on the termination path before any
  destructive capability (lines 1676–1702).
- **Invariants:** I1–I4 in §9.
- **Forbidden transitions:** see §8 rows F1–F7.

**Status: VERIFIED** (UNIT T21–T24, T27; INSPECTION).

**Completeness verdict (Checklist §5 closing rule):** relevant behaviour is
represented for Layers B/C/D; Layer A is represented in design only and is
**explicitly flagged as unimplemented** rather than abstracted; timing
calibration (knob values) is explicitly out of the model's opinion per design
("deliberate non-position"). Model is complete for what it claims; the claim
itself is narrower than the design's full three-phase scope — recorded as
discrepancy D2 (§37).

---

## 6. State Conformance — APPLICABLE — PARTIAL

For each implemented state: implementation correspondence, entry/exit
conditions, guards, effects, bypass absence, invalid-state handling.

| State | Implementation correspondence | Entry / exit | Guards | No-bypass evidence |
|-------|-------------------------------|--------------|--------|--------------------|
| `observe` mode | `OBSERVER_MODE_RESOLVED` (lines 444–461); `MODE`/`ACT` in embedded program (lines 547–550) | entry: default/unset/garbage/DRY_RUN; exit: none (process-lifetime) | every destructive function checks `ACT` first (lines 1134, 1181) | T21 (garbage → observe, zero mutations); T24 (act without ID refused) |
| `act` mode | same resolution point | entry: `OBSERVER_MODE=act` AND `OBSERVER_ORCHESTRATOR_ID` set | startup fatal otherwise (lines 469–475) | T24 |
| `COMPLETED` | `act_completed` (line 1318) | entry: verdict DONE-CONFIRMED; exit: phase=completed | deliverable gate: UNVERIFIED deliverable → NO cleanup, worktree preserved | T1 (gate passes → cleanup fires); T18 (UNVERIFIED → no cleanup, preservation note) |
| `FINISHED-UNMARKABLE` | `act_finished_unmarkable` (line 1432) | entry: read-only role finished without DONE marker | findings-presence check; force-sweep flag | T2 (sweep flag + reason + staging row) |
| `FAILED` | `act_failed` (line 1497) | entry: error exit / DEAD-UNMARKED | worktree NEVER auto-cleaned (conservative preservation) | T3 (preservation note in events) |
| `KILLED` | `act_killed` (line 1529) | entry: orchestrator stop signatures (SIGTERM/SIGKILL pane exit) | cleanup + orphan check + termination record | T4 (real tmux pane exit statuses discriminate KILLED vs FAILED) |
| `PARKED` | `act_parked` (line 1761) | entry: rate-limit signature in attributed tail (or fast-path PARKED-RETRYING); exit: recovery (RUNNING-ALIVE) or expiry→gate | kill SUPPRESSED by design; resume_at parsed from retry-after or default window | T5 (signature + retry-after parse + expiry); T25b context (live tail vetoes) |
| `FROZEN` → `frozen-handled` | `act_frozen` (line 1673) via convergent gate (line 1613) | entry: LIKELY-FROZEN ≥2 cycles, STALE escalation, or park expiry; exit: termination ONLY on gate allow | gate: ≥1 authoritative P1 signal AND log-quiet; denial → notification-only for the cycle | T26 (convergence fires when signals align); T25 (pane-hash alone NEVER terminates); T25b (advancing log vetoes despite P1) |
| `STALE-SUSPECT` | stale_streak logic (lines 1873–1940 region) | entry: quiet cycles; exit: escalation after OBSERVER_STALE_ESCALATE_CYCLES with commit-age F3 acceleration/grace | commit-overdue dedup; grace cycle on fresh commit | T7 (warning cycle then escalation); T14 (overdue event, accelerated + graced escalation) |

Invalid/unknown state handling: unrecognized `OBSERVER_MODE` → observe
(fail-closed, T21); unknown verdict classes from the fast path → `UNKNOWN`
flagged for review, no action (lines 78–79); unknown owner → downgrade
(T23). Abstractions: pane-hash is an observation heuristic, not a state
(declared in gate comments, lines 1596–1605).

**Status: PARTIAL** — all *implemented* states conform with discriminating
tests; the design's Phase 1/2 states (launch-deferred, WAITING_FOR_ORCHESTRATOR)
have no implementation correspondence to verify. `WAITING_FOR_ORCHESTRATOR`
is design-only (P2-MSG2/9 unimplemented).

---

## 7. Transition Conformance — APPLICABLE — PARTIAL

Permitted transitions of Layer C/D with their verification. (Layer A
transitions are design-only; see §5.1 status.)

| Transition | Event | Guard | Effects | Discriminating test | Traceability |
|------------|-------|-------|---------|--------------------|--------------|
| active → completed | DONE-CONFIRMED | deliverable check | cleanup + evidence row + digest comment | T1, T18 (negative) | P3-AC1; #460 F1 |
| active → finished-unmarkable | finished, no marker | findings check | sweep flag + staging row | T2 | #460 action table |
| active → failed | error exit / DEAD-UNMARKED | — | preservation + alert + bundle | T3, T27a | P3-AC1 |
| active → killed | stop-signature pane exit | — | cleanup + orphan check + record | T4 | #460 action table |
| active → parked | rate-limit signature | — | resume_at set; kill suppressed | T5 | #466 F1 |
| parked → active | RUNNING-ALIVE | — | resume_at cleared; parked-recovered event | T5 (recovery path) | #466 F1 |
| parked → frozen-handled | resume_at expiry AND clean tail | convergent gate + fresh-signature re-scan | parked-extended OR expired→act_frozen | T5 (expiry), T26 (convergence) | #466 F1 (fb12f590); P3-AC5 |
| active → stale-suspect → escalated | quiet cycles | commit-age F3 | warning then escalation; accelerated/graced | T7, T14 | #460 F3 |
| (any) → frozen-handled | LIKELY-FROZEN confirmed | **convergent gate** | bundle + stop + cleanup + record; denial → notification-only | T25, T25b, T26 | v1.1 C3; P3-AC4 |
| observe-mode any-transition | — | `ACT` false | intent recorded (dry-run event), no mutation | T1 (cleanup-dry-run), T21 | v1.1 C1 |
| act-mode destructive | — | authorization → breaker | stop/cleanup via crosslink CLI | T22/T23 (downgrades), T20a (breaker) | v1.1 C2 |

Ordering/linearization: authorization precedes breaker precedes execution
(lines 1147–1153, 1192–1200) — verified by inspection and by T20a's loud-deny
semantics. Identity preserved across transitions: agent slug is the key
throughout; owner stamp immutable per execution. VSDD traceability: AC IDs
cited per row.

**Status: PARTIAL** — implemented transitions verified; design-only
transitions (Phase 1 deferral event, messaging WAITING transitions) have no
implementation to conform.

---

## 8. Forbidden Transitions — APPLICABLE — PARTIAL

Explicit forbidden-transition register. "Barrier" = the authoritative
mechanism that prevents the transition; "Test" = the discriminating
verification that the barrier holds.

| ID | Forbidden transition | Barrier | Test | Status |
|----|---------------------|---------|------|--------|
| F1 | garbage/unset mode → lethal capability | fail-closed resolution (lines 444–461) | T21 | VERIFIED |
| F2 | DRY_RUN set + MODE=act → act | alias wins (lines 459–461) | T21 (DRY_RUN honoured) | VERIFIED |
| F3 | MODE=act without orchestrator identity → observer starts | loud fatal pre-lock (lines 463–475) | T24 | VERIFIED |
| F4 | owner=unknown OR owner-mismatch → destructive execution | `authorize_destructive` downgrade (C2; lines 1147–1152, 1192–1196) | T22 (cross-owner), T23 (unknown), T27 (authority facts in bundle) | VERIFIED |
| F5 | pane-hash silence alone → termination | convergent gate: silence contributes nothing, vetoes nothing (lines 1625–1627, 1668) | T25 (repeated confirmation never terminates) | VERIFIED |
| F6 | first tail sighting OR changed tail line → termination | undecidable-held / veto (lines 1632–1635, 1668) | T25b (advancing log vetoes despite P1) | VERIFIED |
| F7 | park expiry + live rate-limit signature → kill | fresh-signature park extension with grace floor (lines 1840–1865) | T5 (extension path) | VERIFIED |
| F8 | breaker-saturated window → silent mutation | loud deny events (lines 1153–1169) | T20a | VERIFIED |
| F9 | second Observer instance → concurrent mutation | instance lockfile + stale-PID recovery (lines 3185–3236) | T19 | VERIFIED |
| F10 | consecutive scan failures → destructive loop | halt-not-loop cap (lines 3165–3180) | T10 | VERIFIED |
| F11 | P1-GATE unmet → Phase 2 opens | **design-only; no mechanical gate exists** | none possible | OPEN (no implementation) |
| F12 | P2-GATE unmet → Phase 3 opens | **design-only** | none possible | OPEN (no implementation) |
| F13 | single-label filing → operator report | design-only (dual-label gate, P2-AC1) | none possible | OPEN |
| F14 | duplicate observation → duplicate Orchestrator notification | design-only watermark (P2-MSG6) | none possible | OPEN |
| F15 | blocking=true → classified stalled | design-only liveness integration (P2-MSG9) | none possible | OPEN |
| F16 | epic closed with unresolved children | design-only (P2-AC2) | none possible | OPEN |

**Status: PARTIAL** — F1–F10 verified with discriminating tests (this is the
implemented core's forbidden-transition surface); F11–F16 are design-level
forbidden transitions with no barrier to test. A pedantic reviewer should
note the asymmetry: the *implemented* Observer's forbidden transitions are
well-barriered; the *swarm's* phase-gate forbidden transitions exist only as
prose.

---

## 9. Invariant Conformance — APPLICABLE — PARTIAL

Critical invariants, precisely stated, with mechanism, verification method
(VSDD-lite Phase 1b selection), scope, and evidence.

| ID | Invariant (precise statement) | Mechanism | Verification | Scope / limits | Evidence | Status |
|----|-------------------------------|-----------|--------------|----------------|----------|--------|
| I1 | Resolved mode is `observe` unless the operator explicitly and correctly sets `act`; no input path (unset, empty, typo, garbage, DRY_RUN alias) yields lethality | mode resolution case-block (lines 444–461) | UNIT T21; INSPECTION | process-lifetime; per-invocation | T21 | VERIFIED |
| I2 | `act` mode exists only with an orchestrator identity; without one the process refuses to start (loud, pre-lock) | startup fatal (lines 463–475) | UNIT T24 | startup only | T24 | VERIFIED |
| I3 | No destructive action executes unless the target worktree's owner stamp equals this Observer's orchestrator ID; unknown/mismatched ownership downgrades to notification naming the facts | `authorize_destructive` + `.owner-orchestrator` stamp (C2) | UNIT T22, T23, T27 | stamp is trusted as written by launcher; stamp forgery out of scope (host-trust boundary) | T22/T23/T27 | VERIFIED |
| I4 | Observer-initiated termination requires ≥1 authoritative non-progress signal (hub-position-static, commit-stale, process-exit, resume-contract-expired) AND log-quiet; absence/silence alone never triggers; first tail sighting undecidable; changed tail vetoes | `convergent_gate` (lines 1613–1671) on the termination path (line 1681) | UNIT T25, T25b, T26; PROPERTY-by-construction over the gate's boolean structure | bounded: signal set is fixed (4 P1 signals + quiet veto); no exhaustive interleaving exploration | T25/T25b/T26 | VERIFIED (within declared scope) |
| I5 | Park expiry alone (weakest evidence) never kills: fresh rate-limit signature at expiry extends the park with a grace floor | expiry re-scan (lines 1840–1865) | UNIT T5 | — | T5 | VERIFIED |
| I6 | Every terminal verdict composes a full evidence bundle synchronously at detection (log tail + pane tail + git status/diffstat + verdict timeline + hub position ref), sha256-manifested, digest posted to the working issue | `compose_transition_evidence` (lines 928–1050) | UNIT T3, T12, T27 (bundle + authority.json present); INSPECTION | bundle lives under state dir (tmp-backed) — durability rule I12 applies | T3/T12/T27 | VERIFIED |
| I7 | Mutating actions are capped per rolling hour; every denial is loud and evidenced (no silent early-return) | `breaker_allow` (line 681) + explicit deny events (lines 1153–1169) | UNIT T9, T20a | — | T9/T20a | VERIFIED |
| I8 | Consecutive cycle failures halt the loop rather than looping destructively | error cap (lines 3165–3180) | UNIT T10 | — | T10 | VERIFIED |
| I9 | At most one Observer instance mutates; stale locks are recovered, live locks refuse | lockfile (lines 3185–3236) | UNIT T19 | PID-liveness based | T19 | VERIFIED |
| I10 | The Observer never touches live agent processes or worktrees directly; every mutation goes through crosslink CLI surfaces | `kickoff_stop`/`kickoff_cleanup` run `crosslink kickoff …` (lines 1170–1209) | INSPECTION + T1/T4 dry-run/real records | — | code + tests | VERIFIED |
| I11 | The backup pass never opens live databases for writing; watermark advances only on GREEN read-back AND (GREEN sync OR explicitly acknowledged local mode); sync RED holds every watermark | backup subsystem (lines 93–120, F4) | UNIT T15 | — | T15 | VERIFIED |
| I12 | The hub is ground truth for durable stores; loss of `/tmp` bundles without hub emission is a defect | hub-comment refs in every terminal path (I6); design P3-AC8 | design-only test (P3-AC8 "/tmp wipe" test) — **not implemented in harness** | — | MODEL only | OPEN |
| I13 | Observation cannot manufacture authority: projections (pane, log tail, hub-position signature) are evidence inputs only; the gate decides; and (design) `blocking=true` reclassifies inactivity as WAITING_FOR_ORCHESTRATOR rather than stall | gate precedence (C3); design §2e.3 | UNIT T25/T25b (projection cannot kill); design-only for messaging half | — | T25/T25b + MODEL | PARTIAL |

Invariants I1–I11 are verified within declared scope (bounded property
checks, not exhaustive exploration — per Checklist §9's "state bounded/sampled
scope otherwise"). I12, I13(messaging half) rest on design only.

---

## 10. Identity Conformance — APPLICABLE — PARTIAL

Independently evolving entities: agents (slug), sessions (opencode session
IDs), orchestrator instances (owner stamps / OBSERVER_ORCHESTRATOR_ID),
Observer instances (lockfile holder).

- **Sufficient identity defined:** agent slug is the primary key through
  scans, state, events, and actions (INSPECTION: `process_agent`, events).
  Session IDs recovered per-agent from the attributed log section via the
  `cwd=…worktrees/<agent-slug>` marker (lines 56–60, 1814–1823).
- **Identity survives relevant boundaries:** agent identity survives the
  log→state→action path; session identity is re-derived each deep probe and
  accumulated in `rec["session_ids"]` (line 1819).
- **Delayed events cannot retarget another entity:** actions are keyed by
  agent slug resolved in the same cycle as the verdict; no cross-agent
  action queue exists (INSPECTION).
- **Retries/queued work retain identity:** dry-run intent records carry
  agent + owner (lines 1141–1145, 1186–1190).
- **Restart cannot alias old identity to new entity:** owner stamp is
  immutable per execution — "a retry is a new execution with a new stamp"
  (lines 172–175); vanished-agent reconciliation handles tracked-then-absent
  agents (T11).
- **Stale identity behaviour defined:** vanished agents reconciled (T11);
  wave-anomaly all-agents-vanish emits platform-restart signature, deduped
  per episode, re-arms on reappearance (T17).
- **Critical identity mutations detected:** owner-stamp mismatch detected
  and downgraded (T22); session-id changes accumulate rather than overwrite.

**Not covered (honest gaps):** design-level messaging identity (agent +
issue + blocking + message as a durable record surviving restarts,
P2-MSG5/7/10) is unimplemented — no Crosslink agent-communication records
are read or written by any code in this repository. Status: PARTIAL.

---

## 11. Ownership Conformance — APPLICABLE — VERIFIED

For the relevant resources (agent worktrees, tmux panes, agent processes):

- **Owner identified:** `.owner-orchestrator` stamp written at dispatch by
  the launcher; opaque id; immutable per execution (lines 172–183).
- **Ownership established before guarantees apply:** authorization is read
  before ANY destructive action (lines 1147–1152, 1192–1196); observe-mode
  intent records still carry the ownership fact (lines 1129–1145).
- **Transfer defined:** none — ownership does not transfer; a retry is a new
  execution with a new stamp (declared, line 174).
- **Ownership cannot silently disappear:** unreadable/missing stamp →
  `owner=unknown` → downgrade (fail-closed), never treated as "mine"
  (T23, T27a).
- **Lifecycle/release mechanism:** cleanup via `crosslink kickoff cleanup
  --only <agent> --yes`; orphan worktrees flagged for force-sweep, never
  silently removed (lines 1710–1712; T1, T4, T18).
- **Resources cannot outlive ownership unnoticed:** orphan check after
  cleanup (line 1710); force-sweep flag file (line 1211).
- **Uncontrolled resources classified:** pre-stamp legacy worktrees are
  exactly the `owner=unknown` class — downgraded, flagged, surfaced to the
  operator (T23).
- **Cross-boundary ownership explicit:** cross-domain protection — a
  misconfigured Observer can never kill a sibling domain's agents (#472/#473,
  lines 180–183; T22).
- **Ownership mutations detected:** stamp is read per action; mismatch
  downgrades and names the actual owner in the notification and bundle
  (T27b).

Status: VERIFIED (UNIT T22, T23, T27a/b; INSPECTION). This is the strongest
dimension in the suite — the C2 pass was built directly against the #472/#473
cross-domain kill class.

---

## 12. Resource Conformance — APPLICABLE — PARTIAL

Resource inventory (Checklist §12 requires a maintained inventory):

| Resource | Owner | Lifetime | Cancellation/termination | Settlement signal | Terminal condition | Observable | Verification |
|----------|-------|----------|--------------------------|-------------------|--------------------|-----------|--------------|
| Agent worktree | owner stamp (orchestrator) | dispatch → cleanup | `kickoff cleanup --only` | cleanup rc + orphan check | worktree absent or force-sweep flagged | git + filesystem | T1, T4, T18 |
| tmux pane / agent process | launcher | dispatch → exit | `kickoff stop --force` (act, authorized) | pane_status dead | pane gone | `pane_status` (line 825) | T4 |
| Evidence bundle | Observer | detection → hub ref | none (append-only) | sha256 manifest + hub digest | hub comment posted (`notified` rc) | events.jsonl + bundle dir | T3, T12, T27 |
| Backup hot copies | Observer | pass interval | generation pruning after verified newer copy (OBSERVER_BACKUP_KEEP) | PRAGMA integrity_check + sha256 + read-back GREEN/RED log | verification.log entry | archive dir | T15 |
| Export watermark | Observer | per (store, table) | held on RED sync | watermark file | advanced only on GREEN | state dir | T15 (F2 5cbfbc86) |
| Park window | Observer | resume_at → expiry | extension on fresh signature | parked-extended / parked-expired events | expiry+clean tail → gate | manager-state | T5 |
| Observer instance | lockfile holder | process lifetime | stale-PID recovery | instance-lock events | process exit | lock file | T19 |

- **Wrapper termination is not used as a substitute for resource
  termination:** `kickoff stop` targets the agent process via crosslink;
  cleanup separately targets the worktree; orphan check catches the gap
  (T4, T18). The #473 class (kill without evidence) is additionally barred
  by the gate (I4).
- **Scope matches declared guarantee:** observe mode guarantees *zero*
  mutations and its records say so (`cleanup-dry-run`, `stop-dry-run`).

**Status: PARTIAL** — inventory above is complete for implemented resources;
design-level resources (agent-communication records, backlog file, launch
deferral queue) have no implementation to inventory.

---

## 13. External Boundary Conformance — APPLICABLE — PARTIAL

Boundary inventory and semantics:

| Boundary | Command/response/error semantics | Delay/loss | Identity across | Ownership across | Settlement | Unavailability semantics | Evidence |
|----------|----------------------------------|-----------|-----------------|------------------|-----------|--------------------------|----------|
| crosslink CLI (stop/cleanup/comment) | rc captured; out/err logged truncated (lines 1170–1176, 1201–1206); `notified` rc on comments (line 1756) | synchronous subprocess with timeout (90s/180s) | agent slug + issue | owner stamp | rc==0 | rc!=0 recorded; breaker still counts | T1–T4, T20a |
| opencode.log (shared log) | byte-offset cursor, rotation/truncation/partial-line safe (F2, lines 71–82) | tail attribution by cwd marker | session.id per line | — | classification per line | missing log → empty sections (undecidable → gate holds) | T13, T25b |
| tmux panes | pane_status dead/alive; exit codes via real pane drives (T4) | poll cadence (OBSERVER_INTERVAL) | agent slug = pane name | launcher-owned | pane exit | vanished pane → DEAD-UNMARKED → FAILED (conservative) | T4, T11 |
| git worktrees / repos | commit age via `git log -1 %ct` (line 886); status/diffstat in bundles | — | branch name = agent branch | owner stamp file | commit timestamps | missing repo → age None (undecidable, not stale — line 1648) | T14, T26 |
| sqlite session stores | hot-copy via `sqlite3 .backup`; never write live (I11) | daily interval | (store, session_id) keys | Observer (copies only) | integrity_check + sha256 | failure → deduped loud alert + retry backoff (lines 278–280) | T15 |
| rclone remote | sync GREEN/RED; unconfigured remote → explicit sync-pending local mode (lines 107–110) | per-pass | archive keys | — | verification.log | RED holds watermark, queues retry backlog | T15 |
| earlyoom / kernel (host) | **design-only**: attribution via `journalctl -u earlyoom --since <window>`; forensic trap documented (design §1c; server-memory-management lines 92–96) | — | victim PID | — | journal line present/absent | **NOT IMPLEMENTED**: zero `journalctl` references in observer.sh; P3-AC2/AC3 attribution field absent | MODEL only — OPEN |
| Crosslink hub (durable store) | hub position ref = latest comment stamp/kind (line 964); comments posted via CLI | hydration/sync cadence | issue number | — | comment posted | flag-issue unresolvable → fails fast hermetically (C1, lines 75–80 of harness) | T27, harness C1 |

- **Boundary does not imply unsupported guarantees:** the suite's §26 covers
  the scope statements; notably the Observer does NOT claim earlyoom
  attribution it cannot perform (the missing implementation is recorded as
  a gap, not claimed).
- **Integration evidence where unit evidence is insufficient:** none yet —
  the harness is hermetic by design; live n=1 shakedown is the designated
  integration step post-P3-GATE (design P3-GATE evidence column). This is a
  declared evidence gap, not a claim of integration coverage.

**Status: PARTIAL.**

---

## 14. Concurrency Conformance — APPLICABLE — PARTIAL

Where events may race:

- **Relevant orderings identified:** authorization → breaker → execution
  (I-ordering, §7); park-resolution before verdict dispatch (line 1826);
  gate before any destructive capability (line 1681).
- **Allowed outcomes defined:** breaker deny (loud), authorization downgrade,
  gate hold (notification-only for the cycle, baselines persist so next
  cycle can converge — lines 1676–1702).
- **Linearization semantics for critical transitions:** single-instance
  lockfile linearizes Observer cycles (I9, T19); within a cycle, per-agent
  processing is sequential (INSPECTION).
- **Arbitration mode:** circuit breaker caps mutating actions per rolling
  hour (24 default); once-per-episode dedup per (agent, verdict);
  fast-path dedup per (class, session) within OBSERVER_FASTPATH_DEDUP_SECS
  (lines 80–82).
- **Mutually exclusive states cannot be simultaneously authoritative:**
  observe/act is process-lifetime exclusive (I1); terminal phases suppress
  re-activation (line 1875).
- **Duplicate events defined:** repeated LIKELY-FROZEN confirmations are
  absorbed by the gate (T25); duplicate park events deduped via
  `first`/`prev_resume` comparison (lines 1768–1781).
- **Completion/cancellation interaction:** park recovery on RUNNING-ALIVE
  clears resume_at (lines 1827–1833).
- **Successor admission relative to predecessor settlement:** relaunch is a
  *recommendation* to the orchestrator, never an Observer action (action
  table lines 27, 45) — admission authority stays upstream (Phase 1 gate,
  design).
- **Distinct identities remain isolated:** per-agent rec state; per-agent
  breaker keys (`stop:<agent>`, `cleanup:<agent>`).
- **Representative interleavings tested:** T25 (repeated silence), T25b
  (signal-then-veto), T26 (convergence), T9/T20a (breaker saturation),
  T19 (double-run).
- **Exhaustive exploration:** NOT used — the gate's boolean structure is
  small and property-checked by construction in tests, but no exhaustive
  (signal × quiet) exploration harness exists. Declared scope limit (I4).
- **Concurrency mutations detected where practical:** T19 (double-run),
  T20a (cap bypass attempt surfaces as loud deny).

**Design-level concurrency (unimplemented):** multiple Builders submitting
communications concurrently must not overwrite (P2-MSG7); watermark prevents
duplicate notification (P2-MSG6). No implementation → OPEN.

**Status: PARTIAL.**

---

## 15. Temporal/Asynchronous Conformance — APPLICABLE — PARTIAL

- **Authoritative vs observed distinguished:** explicitly, in the gate's
  precedence docstring (lines 1596–1605): authoritative/contractual signals
  (commit age from git, process exit, hub position, resume contract)
  OUTRANK corroborating inference (pane hash); log-quiet is a veto gate.
  The liveness verdict itself is a *projection* consumed as a candidate,
  not authority.
- **Requested vs settled state distinguished:** park `resume_at` is a
  *requested* contract; settlement is fresh activity (parked-recovered) or
  expiry+clean-tail through the gate. `notified` true/false distinguishes
  comment acceptance from outcome.
- **Delayed/missing observation cannot manufacture authoritative
  transitions:** missing tail → silence-class (contributes nothing, vetoes
  nothing — lines 1625–1627); missing repo → age None = undecidable, not
  stale (line 1648 comment); first sighting undecidable (T25b).
- **Timers cannot manufacture authoritative state unless assigned
  authority:** the only timer-granted authority is park expiry
  (resume-contract-expired is a P1 signal) — and even it is double-gated by
  the fresh-signature re-scan (I5) and the gate's log-quiet veto. Pane-age
  and staleness timers alone escalate to *candidates*, never directly to
  kills.
- **Retry/timeout/late-event semantics defined:** backup retry backoff
  (lines 278–280); fast-path dedup window; park extension grace floor.
- **Reconciliation exists where state may become stale:** vanished-agent
  reconciliation (T11); wave-anomaly platform-restart signature (T17);
  watermark hold on sync RED (T15).
- **Reconciliation is bounded and controlled:** dedup fingerprints prevent
  alert loops (gate-held alert fingerprint, lines 1683–1701); episode
  re-arm conditions explicit (T17).

**Status: PARTIAL** — implemented temporal semantics verified; design-level
messaging temporal semantics (watermark cursor over Crosslink changes,
WAITING_FOR_ORCHESTRATOR suppression of stall classification) unimplemented.

---

## 16. Transport Conformance — APPLICABLE — PARTIAL

For asynchronous/remote commands (crosslink CLI invocations, hub comments,
rclone sync, and — design-only — the agent→orchestrator messaging path):

- **Success/failure/timeout/response-loss semantics:** subprocess rc + out/err
  captured and logged for stop/cleanup (lines 1170–1176, 1201–1206);
  timeouts 90s/180s; comment delivery recorded as `notified` rc on terminal
  events (line 1756; T27a pattern asserts it).
- **Duplicate semantics:** breaker + dedup keys bound duplicate mutations;
  duplicate *comments* are bounded by fingerprint dedup (gate-held) and
  once-per-episode handling.
- **Stale semantics:** watermark cursor for log reads (rotation-safe,
  line 73); export watermark held on sync failure (5cbfbc86, T15).
- **Transport acceptance distinguished from underlying completion:** comment
  post rc (acceptance) is recorded separately from the action outcome
  (`cleanup_executed`, `auto_kill` fields in the chain, lines 1721–1735) —
  the bundle records both, so acceptance≠completion is inspectable.
- **Ambiguous outcomes cannot silently become success:** every early-return
  path emits an explicit denial/deny event (the #460 shakedown fix; T20a);
  `auto_kill` field is three-valued: executed / dry-run / FAILED
  (line 1726).
- **Recovery/reconciliation has a deterministic trigger:** backup retry
  backoff; watermark hold; stale-lock recovery.
- **Reconciliation duplication controlled:** dedup fingerprints + breaker.

**Design-only (unimplemented):** the messaging transport contract — success,
failure, timeout, response loss, duplicate, stale, owner-unavailable
semantics for agent→orchestrator communications (P2-MSG1..10); transport
acceptance (Crosslink write) vs completion (Orchestrator response) — exists
only as MODEL. **Status: PARTIAL.**

---

## 17. Observation and Projection — APPLICABLE — PARTIAL

Projections in this system: pane status/hash, opencode.log tail, hub-position
signature, liveness verdict, manager-state `rec` (durable but derived),
force-sweep flag file, backlog mirror (design).

- **Authoritative source identified:** git commit history (commit age),
  process exit status, hub Crosslink state, and the manager-state rec are
  authoritative inputs; pane hash and log tails are corroborating
  projections (gate docstring, lines 1596–1605).
- **Projection relation identified:** each projection's derivation is coded
  (agent_log_section attribution, pane_status, last_hub_position).
- **Delay/loss handled:** missing/empty projections default to
  *undecidable*, which fails toward supervision (hold), never toward
  destruction (I4; lines 1625–1635, 1648).
- **Unknown state explicit:** fast-path UNKNOWN class flagged for review
  (lines 78–79); `owner=unknown` explicit; gate-held notifications state
  "none-yet" when no signal has converged (line 1700).
- **Projection cannot silently become authoritative:** T25/T25b are the
  discriminating proofs (repeated pane-silence never terminates; advancing
  log vetoes). The hub-position signature requires two consecutive equal
  sightings to count (lines 1643–1646) — a single stale observation is
  insufficient.
- **Human-facing output does not claim more than authority establishes:**
  termination messages carry the full signal basis, mode, owner, downgrades,
  and evidence hashes (lines 1744–1755); observe-mode records are labelled
  dry-run.
- **Independent verification exists where projection is insufficient:** the
  evidence bundle (I6) is the independent artefact; hub comment carries
  sha256 so a reader can verify the bundle.

**Design-level:** `blocking=true` → WAITING_FOR_ORCHESTRATOR is precisely a
"projection cannot manufacture authority" rule for the *liveness* domain
(staleness projection must not classify intentional waiting as stall) —
unimplemented (P2-MSG2/9). **Status: PARTIAL.**

---

## 18. Recovery — APPLICABLE — PARTIAL

Recoverable abnormal conditions and their recovery semantics:

| Condition | Trigger | Recovery actions | Ownership preserved | No duplicate actives | No resurrection | Work not silently discarded | Observable | Test |
|-----------|---------|------------------|--------------------|--------------------|-----------------|----------------------------|-----------|------|
| Parked agent recovers | RUNNING-ALIVE | phase→active, resume_at cleared | n/a (agent still owns its worktree) | yes (same agent) | n/a | n/a | parked-recovered event | T5 |
| Park expired but agent alive-waiting | fresh rate-limit signature at expiry | park extended with grace floor | preserved | yes | no kill | n/a | parked-extended event | T5 |
| Observer double-start | second instance | refuse (live lock) / recover stale PID lock | n/a | yes (single mutator) | n/a | n/a | instance-lock events | T19 |
| Vanished tracked agent | absent from scan | reconciliation event | worktree untouched | yes | no auto-cleanup | preservation | reconciliation event | T11 |
| All agents vanish simultaneously | platform-restart signature | wave-anomaly alert, deduped, re-arms | untouched | n/a | no actions | alert | wave-anomaly event | T17 |
| Backup pass failure | hot-copy/verify/sync error | deduped loud alert + shortened retry backoff (never silent full-interval skip) | live stores untouched | n/a | n/a | watermark held | backup events | T15 |
| Cycle program failure | nonzero rc | counted toward consecutive-error cap → halt | state write atomicity preserved | n/a | n/a | n/a | error events | T10 |
| Stale lock (dead PID) | kill -0 fails | recover lock and continue | n/a | yes | n/a | n/a | stale-recovered event | T19 |

- **Behaviour remains consistent with the model:** all recovery paths land
  in modelled states (active/parked/held), never in unmodelled actions.
- **Design-level recovery (unimplemented):** messaging cross-restart
  recovery matrix (P2-MSG5, P2-MSG10) — communication written before
  Observer restart still detected; discoverable if Orchestrator unavailable.
  MODEL only.

**Status: PARTIAL.**

---

## 19. Alternative Control Paths — APPLICABLE — PARTIAL

Independent state-changing mechanisms and their mapping to the model:

1. **Observer act-mode stop/cleanup** — the modelled path (gated,
   authorized, breaker-capped). Verified.
2. **Observer observe-mode intent records** — non-mutating by construction;
   records carry would-be ownership facts (lines 1129–1145). Verified (T1).
3. **Orchestrator manual `crosslink kickoff stop/cleanup`** — outside the
   Observer; the model's position: attribution field
   (`attribution: earlyoom | observer | failed | unknown`, design P3-AC2)
   is supposed to distinguish who killed — **unimplemented** (zero
   journalctl/attribution code). A manual kill is currently
   indistinguishable from a FAILED exit in Observer records except via pane
   exit-status heuristics (T4 discriminates KILLED vs FAILED signatures,
   which partially covers this). PARTIAL.
4. **earlyoom SIGTERM (host killer)** — same attribution gap as (3): the
   design's P3-AC2/AC3 machine field and negative-check record are
   unimplemented. OPEN.
5. **OBSERVER_DRY_RUN alias** — alternate spelling of observe; wins over act
   (lines 459–461). Verified (T21 context).
6. **Direct worktree/process manipulation by humans** — outside all models;
   the Observer's orphan check + force-sweep flag is the detection net
   (T4/T18 context). Classified, not barriered (host-trust boundary).
7. **Design-level: deferred sandbox hook (§2e.5)** — explicitly forbidden in
   v1.1 (P2-DEFERRED); when added it must converge on the same
   AgentCommunication event. Not implemented — correctly absent (P2-NO-BROKER
   holds trivially today: no broker code exists).

- **Critical guards cannot be bypassed by alternate paths:** within the
  Observer, all destructive paths funnel through
  authorize→breaker→execute (verified). Paths *outside* the Observer
  (manual kills, earlyoom) are attribution gaps, not guard bypasses — the
  guard's job is Observer-initiated termination.
- **Materially different implementations tested separately:** KILLED vs
  FAILED discriminated via real pane exit drives (T4).

**Status: PARTIAL** (attribution gap is the dominant finding).

---

## 20. Purity Boundary Audit — APPLICABLE — PARTIAL

Where pure decision logic and effectful execution are separated:

**Pure core (declared per design Appendix A "verification architecture
lite"; confirmed by inspection):**

- Mode resolution (lines 444–461): total function of env → {observe, act}.
  No effects.
- `convergent_gate` (lines 1613–1671): decision function over (state, rec,
  row) + probe inputs; returns a decision dict; its *writes* are confined
  to `rec` baselines (persisted by caller) — decision logic itself is
  effect-free over the live world.
- `classify_log_line` (lines 2241–2255): total classification of a log line.
- `authorize_destructive` decision + `breaker_allow` accounting: pure
  decisions over state (effects only via log_event, which is the audit
  trail, not a world mutation).
- Admission check evaluation (lines 2922+): config-driven checks producing
  events (the *checks* are reads; the event append is the declared audit
  effect).

**Effectful shell (outside the pure boundary):**

- `kickoff_stop` / `kickoff_cleanup` (subprocess to crosslink CLI),
  `post_comment` (hub write), `compose_transition_evidence` (file I/O,
  hashing), backup pass (sqlite .backup, rclone, file I/O), lockfile
  management, tmux pane reads, `emit_event` (file append).

**Boundary violations check:** logging/audit events occur *inside* the
pure-core functions (e.g. gate-held log_event at line 1688). These are
declared, deliberate exceptions: the audit trail is the mechanism by which
pure decisions become reviewable, and it writes only to the Observer's own
state dir — it mutates no agent-visible world. Documented here per
Checklist §20's "exceptions documented and verified" requirement; verified
by T25 (a gate denial produces events + at most one deduped comment, and
zero mutations).

**Existing VSDD Purity Boundary Audit:** the design's Appendix A.1
"verification architecture lite" row is the recorded audit; no separate
formal audit document exists. **Status: PARTIAL** (boundary explicit and
mostly clean; formal audit not executed; exceptions documented here).

---

## 21. Model→Implementation Conformance — APPLICABLE — PARTIAL

Mapping of material model elements to implementation, with divergences
called out:

| Model element (design) | Implementation | Conforms? |
|------------------------|----------------|-----------|
| Six-class verdict taxonomy unchanged | action table + act_* functions | YES (INSPECTION) |
| Evidence-at-transition, synchronous, sha256, hub ref (P3-AC1) | `compose_transition_evidence` + digest comments | YES (T3/T12/T27) |
| Multi-signal FROZEN re-verification: "pane-hash AND commit-age stale AND log-quiet AND hub-position static" (P3-AC4 wording) | `convergent_gate`: P1 set = {hub-position-static, commit-stale, process-exit, resume-contract-expired}, ANY-ONE required + log-quiet veto; pane-hash is NOT a gate signal at all | **DIVERGENT-but-stronger**: implementation is *more* conservative than the design wording (pane-hash excluded entirely; process-exit and resume-contract added as authoritative signals; any-one-of + quiet instead of all-four). The design's intent (no silence-only kill) is preserved and strengthened; the letter of P3-AC4 ("all four signals") does not match. Recorded as D3 (§37). Tests T25/T25b/T26 verify the implemented semantics. |
| Park-expiry re-verifies log tail before kill (P3-AC5) | expiry re-scan + extension (lines 1840–1865) | YES (T5) |
| Self-throttling collectors never FROZEN on pane-hash alone (P3-AC6) | gate I4 + park path | YES (T25) |
| earlyoom attribution machine field + negative check (P3-AC2/AC3) | **ABSENT** — zero journalctl references | **NO — unimplemented** (D4) |
| Fleet-size admission via Phase 1 gate (P3-AC7) | Phase 1 unimplemented; commit-age signal (F3) implemented | PARTIAL (D2) |
| Hub ground truth; /tmp loss = defect (P3-AC8) | hub refs in bundles; /tmp-wipe test absent | PARTIAL |
| Fail-closed mode (C1) | lines 444–461 | YES (T21) |
| Owner stamp + downgrade (C2) | authorize_destructive + stamp | YES (T22/T23/T27) |
| Convergent gate on termination path (C3) | line 1681 placement | YES (T25/T26) |
| Authority/evidence facts in bundles (C4) | authority.json + chain fields | YES (T27) |
| Phase 1 mechanical gates (P1-AC1..7) | **ABSENT** | NO — unimplemented (D2) |
| Phase 2 Hybrid F + messaging (P2-*) | **ABSENT** | NO — unimplemented (D2) |
| Knob inventory documented, no silent tuning | config block lines 241–295 + design table | YES (INSPECTION) |
| Implementation-specific behaviour does not alter model semantics | the one alteration found is D3 (above), disclosed | PARTIAL |

**Status: PARTIAL** — the implemented core maps faithfully (with D3
disclosed); Phase 1/2 and earlyoom attribution do not exist to map.

---

## 22. Model-Derived Tests — APPLICABLE — PARTIAL

Test inventory T1–T27 with model-element traceability (abridged; full mapping
in the test file headers):

| Test | Model element traced | Discriminating? | Exercises real implementation? |
|------|---------------------|-----------------|-------------------------------|
| T1 | COMPLETED transition + deliverable gate + evidence row | yes (T18 is the negative) | yes (real observer.sh, dry-run) |
| T2 | FINISHED-UNMARKABLE + sweep flag | yes | yes |
| T3 | FAILED conservative preservation + bundle | yes | yes |
| T4 | KILLED vs FAILED via real pane exit statuses | yes (the discrimination itself) | yes |
| T5 | PARKED signature/parse/expiry/extension/recovery | yes | yes |
| T6 | FROZEN direct + bundle + termination record | yes | yes |
| T7 | STALE-SUSPECT warning → escalation | yes | yes |
| T8 | merge detection + push suggestion + DIS trigger | yes | yes (fixture git repo) |
| T9/T20a/T20b | breaker cap + loud deny + force-sweep resolution | yes | yes |
| T10 | consecutive-error halt | yes | yes |
| T11 | vanished-agent reconciliation | yes | yes |
| T12 | evidence-at-transition full bundle + digest (F1) | yes | yes |
| T13 | fast-path cursor/classification/same-cycle fire (F2) | yes | yes |
| T14 | commit-age signal overdue/accelerated/graced (F3) | yes | yes |
| T15 | dual-store backup hot copy/export/verify/watermark (F4) | yes | yes (fixture stores) |
| T16 | admission-policy checks (F5) | yes | yes (OBSERVER_MODELS_CMD override) |
| T17 | wave-anomaly platform-restart signature (F6) | yes | yes |
| T18 | COMPLETED with UNVERIFIED deliverable → NO cleanup | yes (negative of T1) | yes |
| T19 | instance lockfile refuse + stale recovery | yes | yes |
| T21 | fail-closed mode (garbage → observe) | yes | yes |
| T22/T23 | cross-owner / unknown-owner downgrades | yes | yes |
| T24 | act-without-ID fatal | yes | yes |
| T25/T25b | pane-hash-alone never terminates; advancing log vetoes | yes (the #473 misfire class itself) | yes |
| T26 | convergence fires when signals align | yes (positive of T25) | yes |
| T27 | authority/evidence facts on terminal paths (C4) | yes | yes |

- **Created in the appropriate test-first stage / implementation not
  accepted first:** NOT EVIDENCED per-test — commits land test+implementation
  together (e.g. 2fa5a189, c5eb6e72). The red-gate discipline of VSDD Phase 2
  is not demonstrable from history. Recorded honestly; per VSDD-lite this is
  a declared thinning only for *live probes*, not for harness tests — so
  this is a genuine discipline gap, not an adopted exception (D5).
- **Mocks do not remove behaviour under test:** the harness runs the real
  `observer.sh` with `OBSERVER_DRY_RUN=1`, fixture git repos, fixture
  stores, and a neutral cwd; the liveness scan is replaced by
  `OBSERVER_INPUT_JSON` (the scan is upstream of the unit under test — the
  Observer's transition/gate/authority logic). The mode/gate/authorization
  behaviour under test is real code. Acceptable; noted.
- **Does not merely compare implementation to an independently recreated
  model:** tests assert events/state produced by the implementation, not a
  re-modelled shadow.

**Status: PARTIAL** (coverage and discrimination strong; test-first
discipline unevidenced).

---

## 23. Verification Tooling — APPLICABLE — VERIFIED

Phase 1b selection, recorded per Checklist §23's seven items:

1. **Mechanism selected:** (a) hermetic bash harness (`run-tests.sh`) for
   the implemented Observer core; (b) live probes (free -m, journalctl,
   checkpoint liveness, live n=1 shakedown) for host-coupled behaviour; (c)
   reviewer/auditor adversarial review per VSDD-lite.
2. **Representation:** bash + embedded python; fixtures as real git repos
   and fixture sqlite stores; events.jsonl as the assertion surface.
3. **Reason:** the dominant failure classes are host-resource edges
   (memory, attribution, durability) — live forensics are cheaper and more
   discriminating than formal proofs on a host-coupled supervision system
   (design Appendix A.3).
4. **Scope and limitations:** harness is dry-run and hermetic — it cannot
   evidence integration with a live hub/fleet; live probes are manual and
   not yet codified for Phase 1/2 (which are unimplemented anyway).
5. **Environment:** Linux host, bash, python3, git, sqlite3, tmux, crosslink
   CLI; tests run from neutral cwd (hermeticity proof, harness FIX 1).
6. **Evidence format:** events.jsonl lines + manager-state.json + bundle
   dirs with sha256 manifests; harness prints PASS/FAIL lines and a RESULT
   count.
7. **Implementation-conformance mechanism:** this suite (dimension-by-
   dimension instantiation) + the harness + the adversarial review gate.

The Phase 1b decision is NOT deferred — it is made and recorded here.
Status: VERIFIED.

---

## 24. Adversarial Verification — APPLICABLE — OPEN

This suite is written **for** the pedantic frontier adversarial review
(issue #523's purpose). The review has not yet run. Preparation completed:

- Explicit invariants (§9, I1–I13) with scope limits stated.
- Forbidden-transition register (§8, F1–F16) separating verified barriers
  from design-only ones.
- Authority-vs-projection separation (§17) with the discriminating tests
  named.
- Purity boundary with declared exceptions (§20).
- Discrepancy register (§37) — the reviewer's highest-value starting points
  are pre-mined rather than hidden.
- Smallest-plausible-counterexample targets, pre-staged for the reviewer
  (§30).

Review Context Independence (Checklist §24): the reviewer must evaluate the
current artefacts (design @3fc3c60a, observer.sh @68750f28, this suite) —
prior approvals (phase-1 review passes on the Observer v1.1 pass) are not
correctness evidence; builder reasoning (this suite) is an object of
challenge. Status: OPEN (by design — this is the gate input, not the gate
result).

---

## 25. Abstraction Conformance — APPLICABLE — PARTIAL

Material abstractions and their justification:

| Abstraction | Behaviour abstracted | Reason | Omitted properties covered elsewhere? | Adversary reviewed? |
|-------------|---------------------|--------|----------------------------------------|--------------------|
| Pane-hash silence heuristic | fine-grained process activity | cheap liveness signal | YES — barred from termination authority by the gate (I4, T25) | via #473 forensics; formal review pending |
| Log attribution by cwd marker | per-agent log separation from a shared log | single shared opencode.log | identity accumulation (§10) | pending |
| Hub-position signature (stamp+kind) | full hub state | cheap recency probe | two-sighting rule (§17) | pending |
| Verdict matrix as fixed six classes | richer behavioural nuance | taxonomy stability declared UNCHANGED by v1.1 | fast-path classes add nuance without changing taxonomy | design-declared |
| VSDD-lite (no formal proofs, no exhaustive catalog, no mutation CI) | formal verification | host-coupled substrate; forensics cheaper (App. A.2/A.3) | harness + live probes + review (§23) | design-reviewed; this suite re-derives it |
| Knob values as documented non-positions | calibration | deliberate non-position; measurement-first | two-repo sync rule on change | design-declared |

Environmental/deployment assumptions: single host; tmux deployment;
crosslink CLI present; opencode.log at the documented path; owner stamps
written by the launcher (host-trust). Omitted-boundary verification: live
integration explicitly deferred to post-P3-GATE shakedown (declared, §13).

**Status: PARTIAL** (abstractions justified and documented; adversary review
pending — that is this suite's gate).

---

## 26. Scope and Guarantee Conformance — APPLICABLE — PARTIAL

Significant claims and their explicit scopes:

- **"The Observer never kills on silence alone"** — scope: Observer-initiated
  termination paths only. Does NOT cover: orchestrator manual kills,
  earlyoom, host failures (attribution gap, §19). Verified within scope
  (T25/T25b/T26).
- **"Observe mode performs zero mutations"** — scope: the Observer's own
  actions; the record appends and comments it makes are themselves
  mutations of *its own state and the flag issue*, which the mode's contract
  explicitly includes as notification (declared in code comments lines
  1129–1133). Verified (T21).
- **"Every terminal verdict emits evidence"** — scope: verdicts detected
  while the Observer runs. Does NOT cover: verdicts occurring during
  Observer downtime (no backfill mechanism). Declared limit.
- **"Durable stores survive hub compaction"** — design claim (P2-AC6);
  unimplemented. NOT CLAIMED here.
- **"Local vs cross-boundary guarantees distinguished"** — backup exports
  distinguish local GREEN from remote sync GREEN; rclone-unconfigured is an
  explicit local mode, never silently claimed as synced (lines 107–110,
  T15). Verified.
- **"Resource vs state guarantees"** — cleanup (resource) is gated
  separately from verdict recording (state); T18 shows state recorded while
  resource action withheld. Verified.
- **"Infrastructure vs feature guarantees"** — the knob inventory
  (design §Configurability) separates calibration (infrastructure) from
  behaviour (feature); no knob change without two-repo sync. MODEL-verified.
- **"Crash boundaries"** — Observer crash mid-cycle: atomic state writes +
  error cap + lockfile recovery (T10/T19); agent crash: DEAD-UNMARKED →
  FAILED conservative preservation (T3/T11). Verified within scope.
- **"Terminal states do not imply unsupported external behaviour"** —
  COMPLETED cleanup fires only after deliverable verification; FAILED never
  cleans; termination records name exactly what was executed vs downgraded
  (chain fields, lines 1721–1735). Verified (T1/T3/T18/T27).

**Status: PARTIAL** (implemented claims scoped and verified; design-level
claims not made).

---

## 27. Recovery and Refinement — APPLICABLE — VERIFIED

Discoveries that invalidated prior behaviour, and their integration (the
#460 shakedown + #466/#469/#473 fix lineage — this dimension is
demonstrably exercised in this project):

| Discovery | Model element affected | Tests affected | Implementation fix | Evidence invalidated/updated |
|-----------|------------------------|----------------|--------------------|------------------------------|
| Silent breaker-deny during 05:26–05:54 triage (#460) | breaker semantics (I7) | T20a/T20b added | every early-return emits explicit denial | prior "cleanup_ok:false" archaeology superseded |
| Park expiry weakest-kill-trigger (#466 F1) | park→frozen transition (I5) | T5 extended | fresh-signature re-scan + grace floor | fb12f590 |
| Double-run mutation risk (#466 F6) | instance model (I9) | T19 added | lockfile + stale-PID recovery | 51ed928f |
| Off-server sync failure must hold watermark (#466 F2) | backup watermark (I11) | T15 extended | watermark hold + retry backlog | 5cbfbc86 |
| Silent-failure strict mode (#469 FIX 2) | cycle error semantics (I8) | T10 | set -euo pipefail + explicit exceptions | harness + code |
| Pane-hash freeze misfire (#473) | termination authority (I4) | T25/T25b/T26 added | convergent gate on termination path | 2fa5a189; #473 finding upgraded guess→evidence-based-strong |
| Cross-domain kill risk (#472/#473) | ownership (I3) | T22/T23/T27 added | owner stamp + fail-closed authorization | 1050447c, c5eb6e72 |
| Garbage-mode lethality risk | mode model (I1/I2) | T21/T24 added | fail-closed resolution + act-requires-ID | 2e690049 |

Revised artefacts re-entered the loop (tests re-run green; this suite
records the current state). Status: VERIFIED — this is the strongest
process evidence in the project: every listed discovery has a named fix
commit, a named test, and an updated invariant.

---

## 28. Contract Chain and Traceability — APPLICABLE — PARTIAL

The chain (Checklist §28 / Profile §8), instantiated for the implemented
core. Format: Requirement → State Model → Verification Property → Tracked
VSDD Work → Test → Implementation → Evidence → Review.

| Requirement (design AC) | State model element | Verification property | Tracked work | Test | Implementation | Evidence | Review |
|------------------------|--------------------|----------------------|--------------|------|----------------|----------|--------|
| P3-AC1 evidence-at-transition | Layer B terminal verdicts | I6 | #460 F1 | T3, T12, T27 | compose_transition_evidence (928–1050) | UNIT + INSPECTION | pending (this gate) |
| P3-AC4 multi-signal FROZEN | Layer D gate | I4 | #460 v1.1 C3 | T25, T25b, T26 | convergent_gate (1613–1671) | UNIT + PROPERTY-bounded | pending |
| P3-AC5 park-expiry re-verify | park transition | I5 | #466 F1 | T5 | expiry re-scan (1840–1865) | UNIT | pending |
| P3-AC6 self-throttle not FROZEN | Layer C parked | I4/I5 | #473 | T25 | gate + park path | UNIT | pending |
| v1.1 C1 fail-closed mode | Layer D mode | I1, I2 | #460 v1.1 | T21, T24 | 444–475 | UNIT | pending |
| v1.1 C2 ownership | Layer D authorization | I3 | #460 v1.1 | T22, T23, T27 | authorize_destructive | UNIT | pending |
| v1.1 C4 authority facts | bundle schema | I6 subset | #460 v1.1 | T27 | authority.json | UNIT | pending |
| P1-AC1..7 launch gate | Layer A Phase 1 | — | **no tracked work item** | — | **absent** | — | — |
| P2-AC1..7 Hybrid F | Layer A Phase 2 | — | **no tracked work item** | — | **absent** | — | — |
| P2-MSG1..10 messaging | Layer A Phase 2 | — | **no tracked work item** | — | **absent** | — | — |
| P3-AC2/AC3 earlyoom attribution | Layer B FAILED/KILLED | — | #473 (research) | — | **absent** | — | — |
| P3-AC8 hub ground truth | durability rule | I12 | design | — | partial (hub refs yes; /tmp-wipe test no) | MODEL | — |

- **Critical requirements map to model elements:** yes for implemented core.
- **Reviewable obligations represented in tracking:** P1/P2 ACs have no
  Crosslink work items — the design defers per-issue specs to work items
  (#483–#487, #489) that do not yet exist for the messaging/filing build.
  Gap recorded.
- **Derived tests retain traceability:** yes (table above; test headers).
- **Evidence traceable:** events.jsonl + bundles + this suite.
- **Adversarial findings traceable:** this suite + the pending review.

**Status: PARTIAL** — chain complete and intact for the implemented core;
broken (absent) for Phase 1/2 and earlyoom attribution.

---

## 29. Builder Completion Gate — APPLICABLE — SELF-ASSESSMENT

Per Checklist §29's thirteen items, assessed for THIS suite's production
(the suite is the deliverable; the swarm is the governed artefact):

- [x] Model sufficient to derive obligations — three-layer model (§5).
- [x] Applicable universal dimensions instantiated — all 36 (this file).
- [x] Applicability/scope decisions explicit — per-dimension + §26.
- [~] Critical model elements mapped to implementation — §21; divergences
  disclosed (D2–D4).
- [x] Critical invariants and forbidden transitions have verification
  methods — §8/§9 (methods named even where the method is "none possible
  yet").
- [~] Identity/ownership/concurrency obligations addressed where applicable
  — §10/§11/§14; messaging identity unimplemented (disclosed).
- [x] Resource inventory sufficient for the claimed guarantee — §12.
- [x] External boundaries identified — §13.
- [x] Tooling selected in Phase 1b — §23.
- [~] Model-derived tests satisfy VSDD test-first discipline — §22 D5:
  discipline unevidenced.
- [x] Discovered refinements integrated — §27.
- [x] Evidence current — all line numbers @68750f28; harness state as of
  this suite's date.
- [x] Blocked verification explicit — §37 + per-dimension BLOCKED/OPEN.
- [x] No critical claim rests only on assertion or inspection where
  executable verification is practical — the one inspection-only critical
  claim (I10) is structural (subprocess construction) and is additionally
  evidenced by dry-run records.

Builder completion is an evidence claim, not the final verdict (Checklist
§29 closing rule). Status: SELF-ASSESSED — gate input for §30.

---

## 30. Adversarial Reviewer Gate — APPLICABLE — OPEN

Pre-staged attack surface for the reviewer (Checklist §30's fifteen items,
with the smallest plausible counterexample per critical obligation):

1. **Suite derived from actual model?** Verify §5 against design @3fc3c60a.
2. **Model represents claimed behavioural boundary?** Attack: find a
   transition in observer.sh not in §7's table.
3. **Hidden assumptions?** Start with: owner-stamp trust (§11), single-host
   assumption, launcher writes stamps correctly.
4. **Abstractions justified?** §25 — attack pane-hash and log attribution.
5. **Authority correctly assigned?** Attack: can any projection reach
   `allow=true` alone? (T25/T25b say no; try resume-contract-expired + a
   log the Observer mis-attributes.)
6. **Identity/ownership survive boundaries?** Attack: agent rename between
   stamp write and gate read; session-id reuse after restart.
7. **Forbidden transitions genuinely prevented?** F1–F10 have tests; try to
   defeat the DRY_RUN-wins alias (F2) via env ordering.
8. **Concurrency semantics explicit and implemented?** Attack: two
   Observers with different state dirs, same fleet (lock is per-state-dir —
   is that a gap? See §37 D6).
9. **External resources satisfy stated guarantee?** Attack: bundle written
   but hub comment fails (notified=false) — is evidence then durable
   anywhere but /tmp? (I12 gap, §37 D7.)
10. **Observation cannot manufacture authority?** The core claim; T25/T25b
    are the proofs — attack their fixtures, not the claim.
11. **Derived tests discriminating?** T4's pane-exit discrimination is the
    subtlest; verify it can fail.
12. **Implementation conforms to model?** §21 D3 is a known letter-vs-intent
    divergence — rule on whether "stronger than design" is conformance.
13. **Current evidence supports the claim?** All line numbers are @68750f28;
    re-verify after any rebase.
14. **Plausible mutations detected?** §31.
15. **Blocked/partial evidence honest?** §37 is the disclosure register —
    attack it for completeness.

Status: OPEN — this gate is the issue's purpose and has not run.

---

## 31. Mutation Verification — APPLICABLE — PARTIAL

Per Checklist §31, with VSDD-lite's declared deferral of systematic mutation
testing (design A.2: mutmut/Stryker class tools "overkill for a swarm whose
dominant failure mode is admission + attribution + filing durability"):

| Critical property | Plausible violating mutation | Introduced at | Detected by |
|-------------------|------------------------------|---------------|-------------|
| I1 fail-closed mode | `*)` case arm returns act; or DRY_RUN check removed | lines 454–461 | T21 (garbage → observe assertion) |
| I2 act-requires-ID | startup fatal block removed | lines 469–475 | T24 (rc≠0 + fatal event) |
| I3 ownership fail-closed | downgrade branch returns allowed | authorize_destructive | T22/T23 (downgrade events asserted) |
| I4 silence-never-kills | gate bypassed / log_quiet defaulted true | convergent_gate / act_frozen | T25 (zero frozen-termination records), T25b (veto) |
| I5 park-extension | expiry kill without re-scan | lines 1840–1865 | T5 (extension event asserted) |
| I7 loud deny | early-return without event (the ORIGINAL #460 bug) | kickoff_cleanup | T20a (deny event asserted) |
| I9 single instance | lockfile check removed | 3185–3236 | T19 |
| I11 watermark hold | advance watermark on RED | backup pass | T15 |

- **Mutations introduced at the relevant implementation/boundary:** the
  table names the exact sites.
- **The suite detects them:** each row's test asserts the property the
  mutation would break (these are mutation-*detection* properties embedded
  in the harness; the mutations themselves have not been physically
  injected and run — that is the PARTIAL, and it is the declared VSDD-lite
  deferral).
- **Surviving mutations trigger review:** rule stated (Checklist §31);
  no mutation campaign has run, so no survivors exist to review.

**Status: PARTIAL** (detection properties designed and mapped; physical
mutation campaign deferred per design A.2 — declared adaptation §35).

---

## 32. Test Environment Integrity — APPLICABLE — PARTIAL

- **Required infrastructure available:** bash, python3, git, sqlite3 present
  on host; harness executed fresh during this suite's production —
  **RESULT: 181 passed, 0 failed** (2026-08-30, full T1–T27 set including
  T20a/T20b/T25/T25b/T26/T27 sub-checks).
- **Required external boundaries exercisable:** crosslink CLI exercised in
  dry-run/record form only; tmux exercised via real panes (T4); live hub
  NOT exercised (hermetic by design).
- **Fixtures preserve relevant behaviour:** fixture git repos with real
  commit dates (backdate helper); fixture sqlite stores with integrity
  checks (T15); real pane exit drives (T4).
- **Test doubles do not remove behaviour under test:** `OBSERVER_INPUT_JSON`
  replaces the liveness *scan* (upstream input), not the transition/gate/
  authority logic under test; `OBSERVER_MODELS_CMD` override makes the
  admission catalog deterministic (T16). The mode/gate/authorization code
  paths are the real ones.
- **Environment failures recorded as BLOCKED, not PASS:** **the harness has
  no BLOCKED semantics** — a missing tool surfaces as a FAIL (or, worse, a
  skipped check that silently passes via `grep -q … 2>/dev/null` tolerance
  in `check`). This is a harness gap (D8): Checklist §32 requires
  environment failures be recorded as BLOCKED; the harness cannot express
  that. Mitigation: this suite treats any harness run with
  infrastructure errors as BLOCKED for affected dimensions, manually.
- **Evidence from the implementation under review and current:** yes —
  harness runs against the working-tree observer.sh; line numbers pinned to
  @68750f28.

**Status: PARTIAL** (hermetic integrity strong; BLOCKED semantics missing
from the harness itself).

---

## 33. Verdict — APPLICABLE — REWORK (current state)

Applying Checklist §33's four verdicts to the governed artefact as it
stands:

- **PASS** — not available: Phase 1 and Phase 2 obligations are unimplemented;
  earlyoom attribution (a P3 AC) is unimplemented.
- **REWORK** — **current verdict.** The architecture remains potentially
  viable and the implemented core (Layers B/C/D) is strongly verified
  (T1–T27, invariants I1–I11, forbidden transitions F1–F10); but material
  obligations (Phase 1 launch gate, Phase 2 filing/messaging, earlyoom
  attribution, P3-AC8 /tmp-wipe test) are incomplete, and the phase-gate
  forbidden transitions (F11–F16) exist only as prose.
- **FAIL** — not warranted: no critical obligation is *violated*, no
  forbidden transition is *reachable* in the implemented core, and
  authority/identity/ownership hold where implemented.
- **BLOCKED** — not warranted as a whole: nothing prevents the missing work
  from being implemented and verified on this host.

This verdict is the suite's honest output for the adversarial gate: the
reviewer should treat REWORK as the claim under test.

---

## 34. Minimality — APPLICABLE — VERIFIED

The suite follows one-model-property → one-obligation → one-or-more-
discriminating-mechanisms:

- Each invariant (§9) maps to named mechanism(s) and named test(s); no
  duplicate prose tests for behaviour the model already captures.
- The transition table (§7) and forbidden register (§8) reference the same
  tests rather than re-specifying behaviour.
- Known duplication, declared: §6 (state conformance) and §7 (transition
  conformance) necessarily overlap on the same tests — the Checklist's own
  dimensions demand both views. No *test* duplication exists.

Status: VERIFIED.

---

## 35. Universal Adaptation Rule — APPLICABLE — VERIFIED (with declared adaptations)

Universal obligations are instantiated, omitted only where genuinely
inapplicable, and never weakened. Project-specific additions are marked.
Declared adaptations (all sourced from the design's VSDD-lite Appendix A,
restated here so the universal obligations' thinning is explicit and
challengeable):

1. **Formal model verification (Checklist §9 "exhaustive exploration where
   tractable", §23)** — thinned to bounded property checks + live probes.
   Rationale: design A.2/A.3 (host-coupled substrate; forensics cheaper).
   The gate's boolean structure is small; exhaustive (signal × quiet)
   exploration is tractable in principle and is NOT done — this is the
   sharpest remaining thinning and a legitimate reviewer target.
2. **Mutation testing as CI gate (Checklist §31)** — thinned to
   mutation-detection properties embedded in tests; no physical mutation
   campaign. Rationale: design A.2.
3. **Exhaustive edge-case catalog** — replaced by live-probe edge cases
   (the ones that killed agents). Rationale: design A.2.
4. **Test-first red-gate (Checklist §22)** — NOT adopted as an exception;
   the discipline is unevidenced in commit history (D5). This is recorded
   as a gap, not an adaptation.
5. **Project-specific additions:** the three-layer state model itself
   (§5), the discrepancy register (§37), and the pre-staged attack surface
   (§30) are project additions that strengthen, never weaken, universal
   obligations.

No universal obligation is silently rewritten. Status: VERIFIED.

---

## 36. Governing Principle — APPLICABLE — VERIFIED

> The universal checklist defines the dimensions of conformance that
> state-based ASES work must examine. The project state model supplies the
> behavioural structure. The project-specific conformance suite instantiates
> the universal dimensions against that structure. Verification evidence
> establishes whether the resulting obligations have actually been satisfied.

This file is the instantiation; §5 is the behavioural structure; the status
columns are the evidence verdicts. The suite's own honesty rules (§0) bind
it to the principle's last sentence: evidence, not assertion, establishes
satisfaction — which is why eleven dimensions read PARTIAL and two read OPEN
rather than a comfortable uniform VERIFIED.

---

## 37. Discrepancy Register (project-specific addition)

Every design-vs-implementation or issue-vs-repository divergence found
during instantiation. This register is the reviewer's index; each entry
names the affected dimensions.

| ID | Discrepancy | Evidence | Affects | Severity for review |
|----|-------------|----------|---------|--------------------|
| D1 | Issue #523 names `run-tests.sh T28-T33` as evidence; **no T28–T33 exist on any branch** — harness ends at T27 (verified across all feature branches) | `git log --all` + branch greps (this session) | §0, §22, §28 | Low (stale pointer) — but the reviewer must not accept phantom test references |
| D2 | Design Phases 1 and 2 (P1-AC1..7, P2-AC1..7, P2-MSG1..10) have **no implementation** anywhere in the repo (zero hits: `free -m` gate, `launch-deferred-memory`, `agent-communication`, `operator-report`, `execution-engine-backlog`, `WAITING_FOR_ORCHESTRATOR`) | repo-wide search (this session) | §5.1, §8 F11–F16, §21, §28, §33 | High — the swarm's phase-gate structure is prose-only today |
| D3 | P3-AC4's letter ("pane-hash AND commit-age stale AND log-quiet AND hub-position static") vs implementation (any-one-of {hub-static, commit-stale, process-exit, resume-expired} + log-quiet veto; pane-hash excluded entirely) — implementation is *stronger* than the design's letter but does not match it | design line 645 vs observer.sh 1613–1671 | §9 I4, §21 | Medium — rule whether stronger-than-design is conformance |
| D4 | P3-AC2/AC3 earlyoom attribution (`journalctl -u earlyoom`, machine `attribution` field, explicit negative check) — **unimplemented**; zero `journalctl` references in observer.sh | grep (this session) | §13, §19, §21, §28, §33 | High — FAILED/KILLED discrimination is a stated P3 gate criterion |
| D5 | VSDD test-first red-gate discipline unevidenced: test+implementation land in the same commits (2e690049, 1050447c, 2fa5a189, c5eb6e72) | git history | §2, §22 | Medium |
| D6 | Instance lock lives under OBSERVER_STATE_DIR — two Observers with *different* state dirs supervising the same fleet would not exclude each other | lines 242, 3195 | §14, §30(8) | Medium — deployment-discipline assumption, undocumented as such |
| D7 | Evidence bundles live under the state dir (tmp-backed); hub comment carries the ref + sha256, but if the comment post fails (`notified=false`) the bundle exists only in /tmp — I12's own defect rule | lines 679–681, 1756 | §9 I12, §30(9) | Medium — the failure path of the durability mechanism is itself the durability gap |
| D8 | Harness lacks BLOCKED semantics; `check` uses `grep -q … 2>/dev/null` tolerance, so some environment failures can masquerade as PASS | run-tests.sh 32–45 | §32 | Low-Medium |
| D9 | `server-memory-management.md` is cited by the design as `.crosslink/knowledge/server-memory-management.md` but exists in git history at repo root (commit 9786d560) and is not present in this worktree's knowledge dir — pointer rot in the design's depends_on | git show 9786d560 (this session) | §13, frontmatter | Low |

---

## 38. Summary Status Table

| Checklist § | Dimension | Applicability | Status |
|-------------|-----------|---------------|--------|
| 1 | Canonicality | APPLICABLE | VERIFIED |
| 2 | Lifecycle Integration | APPLICABLE | PARTIAL |
| 3 | Checklist Semantics | APPLICABLE | VERIFIED |
| 4 | Evidence Classes | APPLICABLE | VERIFIED |
| 5 | State Model Completeness | APPLICABLE | PARTIAL |
| 6 | State Conformance | APPLICABLE | PARTIAL |
| 7 | Transition Conformance | APPLICABLE | PARTIAL |
| 8 | Forbidden Transitions | APPLICABLE | PARTIAL |
| 9 | Invariant Conformance | APPLICABLE | PARTIAL |
| 10 | Identity Conformance | APPLICABLE | PARTIAL |
| 11 | Ownership Conformance | APPLICABLE | VERIFIED |
| 12 | Resource Conformance | APPLICABLE | PARTIAL |
| 13 | External Boundary Conformance | APPLICABLE | PARTIAL |
| 14 | Concurrency Conformance | APPLICABLE | PARTIAL |
| 15 | Temporal/Asynchronous Conformance | APPLICABLE | PARTIAL |
| 16 | Transport Conformance | APPLICABLE | PARTIAL |
| 17 | Observation and Projection | APPLICABLE | PARTIAL |
| 18 | Recovery | APPLICABLE | PARTIAL |
| 19 | Alternative Control Paths | APPLICABLE | PARTIAL |
| 20 | Purity Boundary Audit | APPLICABLE | PARTIAL |
| 21 | Model→Implementation Conformance | APPLICABLE | PARTIAL |
| 22 | Model-Derived Tests | APPLICABLE | PARTIAL |
| 23 | Verification Tooling | APPLICABLE | VERIFIED |
| 24 | Adversarial Verification | APPLICABLE | OPEN |
| 25 | Abstraction Conformance | APPLICABLE | PARTIAL |
| 26 | Scope and Guarantee Conformance | APPLICABLE | PARTIAL |
| 27 | Recovery and Refinement | APPLICABLE | VERIFIED |
| 28 | Contract Chain and Traceability | APPLICABLE | PARTIAL |
| 29 | Builder Completion Gate | APPLICABLE | SELF-ASSESSED |
| 30 | Adversarial Reviewer Gate | APPLICABLE | OPEN |
| 31 | Mutation Verification | APPLICABLE | PARTIAL |
| 32 | Test Environment Integrity | APPLICABLE | PARTIAL |
| 33 | Verdict | APPLICABLE | **REWORK** |
| 34 | Minimality | APPLICABLE | VERIFIED |
| 35 | Universal Adaptation Rule | APPLICABLE | VERIFIED |
| 36 | Governing Principle | APPLICABLE | VERIFIED |

**Overall: REWORK** — implemented core strongly verified; Phase 1/2 and
earlyoom attribution unimplemented; adversarial gate is the next action and
this suite is its input.

---

## Appendix — WHAT-NOT-TESTED (claim disclosure per AGENTS.md)

This suite's own claims, with explicit negative-space disclosure:

- **WHY** — issue #523 requires a per-dimension conformance instantiation as
  the input to a pedantic adversarial review; honest status grading is the
  deliverable's core value.
- **WHAT** — every status is grounded in: the design document @3fc3c60a;
  observer.sh and run-tests.sh @68750f28 (line numbers pinned); repo-wide
  greps for Phase 1/2 implementation markers; git history across all
  branches for T28–T33 and the fix lineage; the Universal Checklist and
  VSDD Adaptation Profile texts; the server-memory-management knowledge
  page (2026-08-25 revision, from git).
- **HOW CERTAIN** — evidence-based for all VERIFIED/PARTIAL/OPEN gradings
  that cite tests or code; evidence-based-strong for the absence claims
  (D2, D4) which used multiple independent search patterns; the harness
  OPERATIONAL claim is based on the suite-author's reading of the harness
  code and prior green runs recorded in the repo, **not on a fresh
  execution performed during this suite's production**.
- **WHAT-NOT-TESTED** —
  1. ~~The harness was not re-executed~~ **RESOLVED during production:** the
     harness WAS executed fresh (2026-08-30): `RESULT: 181 passed, 0 failed`,
     log at `/tmp/opencode/observer-tests-run.log`. Note the log itself is
     tmp-backed per the durability rule — the RESULT line is restated here
     so the claim survives a /tmp wipe; the reviewer may re-run
     `bash scripts/observer/tests/run-tests.sh` to reproduce.
  2. No live-host probe was performed (no `free -m`, no `journalctl`, no
     tmux inspection) — all host-coupled claims are MODEL or OBSERVATION
     class.
  3. No mutation was physically injected (§31's deferral).
  4. The D6 lock-scope concern (two state dirs, one fleet) was reasoned,
     not experimentally demonstrated.
  5. Line numbers are pinned to @68750f28 and will drift on rebase; the
     reviewer must re-pin before relying on them.
