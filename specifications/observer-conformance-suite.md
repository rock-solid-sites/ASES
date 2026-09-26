---
title: Observer Conformance Suite — Instantiation of the Universal Conformance Checklist against Observer Swarm v1.1
program: EDASES
layer: Implementation
document_type: Conformance Suite
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 527
suite_version: "2.0"
canonical_baseline: to-file/ASES Universal Conformance Checklist.md (2026-08-29 revision)

depends_on:
  - to-file/ASES Universal Conformance Checklist.md (2026-08-29)
  - .design/observer-swarm-v1.1-resilience.md @3fc3c60a
  - to-file/VSDD Adaptation Profile.md
  - to-file/VSDD.md (lite adoption per design Appendix A)
  - .crosslink/knowledge/agent-orchestration-playbook.md (§5.4, §5.8, §5.8.1)
  - server-memory-management knowledge page (2026-08-25 revision)
  - docs/standards/Documentation Standard.md
  - specifications/Adverarial Test Suite Reviews:.md (seven meta-reviews synthesized into this v2; see §40)

consumed_by:
  - Observer Swarm v1.1 phase gates (P1-GATE, P2-GATE, P3-GATE)
  - VSDD Phases 2–6 gates (lite adoption)
  - Adversarial reviewer gate (Hy4 Preview adversarial review, issues #523/#527)
  - Builder completion gate

related_documents:
  - scripts/observer/observer.sh
  - scripts/observer/tests/run-tests.sh
  - .design/lifecycle-manager-design.md (superseded in part; lifecycle-semantics baseline)
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/conformance/Stop-Button-Conformance-Suite.md (sibling instantiation, format precedent)

implements:
  - ASES Universal Conformance Checklist instantiation (§§1–36)

supersedes:
  - Observer Conformance Suite v1.0 (2026-08-30, issue #523 lineage; preserved in git history)
superseded_by: []
last_updated: 2026-09-01
---

# Observer Conformance Suite — Universal Checklist §§1–36 vs Observer Swarm v1.1 (v2)

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

## 0. Reading Guide and Evidence-Grading Discipline (v2)

### 0.1 Status vocabulary (dimension level)

**Status vocabulary** (Checklist §3, extended at project layer — a
strengthening, declared §35(6)): `[ ] OPEN`, `[x] VERIFIED`, `[~] PARTIAL`,
`[!] FAILED`, and — new in v2 — `[⏸] BLOCKED` **as a dimension-level
status**. Applicability vocabulary: `APPLICABLE`, `NOT APPLICABLE`,
`OUT OF SCOPE`, `BLOCKED (applicability)`. `BLOCKED` is not `VERIFIED` —
and v2 makes that enforceable rather than admonitory (§0.4, §0.6).

v1 used `BLOCKED` only as an applicability label and an overall-verdict
option, while §32 of v1 already needed to say "treat affected dimensions as
BLOCKED" — a dimension status the vocabulary did not define. That gap is
closed here (meta-review finding: Deepseek #1, GLM-5.3-Flash F3.2, Muse D2).

**Precise dimension-status semantics** (disambiguating what v1 left
implicit — meta-review finding: GLM-5.3 D16):

| Status | Meaning | Entry condition | Exit condition |
|--------|---------|-----------------|----------------|
| `OPEN` | Not yet assessed (or assessment not started). No claim either way. | Default at instantiation. | Any assessment progress re-grades it. |
| `PARTIAL` | The obligation is **partially met and/or partially verified**, and the record states **which part is met, which is not, and what remains**. A bare PARTIAL with no remainder statement is malformed. | Assessment produced mixed results. | Remainder verified → VERIFIED; remainder shown violated → FAILED. |
| `VERIFIED` | The obligation is met AND verified with evidence satisfying the **evidence-class floor** (§0.5). | Full assessment + floor met. | Invalidation (§0.7) re-opens it. |
| `FAILED` | The obligation is assessed and **not met** (or its verification demonstrates violation). | Assessment demonstrates violation. | Fix + re-verification. |
| `BLOCKED` | A **necessary verification cannot currently be performed** because required evidence, infrastructure, or external capability is unavailable. Distinct from OPEN (not yet assessed) and PARTIAL (partially assessed): the *blocking* is itself an assessed fact. | Missing capability identified + acquisition attempts recorded (§0.4). | Evidence arrives → re-grade; capability declared out of scope → applicability re-graded with §35 declaration; escalation resolves. |

**Applicability vocabulary, disambiguated** (meta-review finding: Sonnet
D5, GLM-5.3 D15 — v1 carried two labels with no stated criterion):

- `NOT APPLICABLE` — the dimension's *subject matter does not exist* in the
  governed artefact (e.g. Concurrency against a genuinely single-threaded,
  single-actor artefact). The dimension is inapplicable **as a matter of
  fact about the artefact**.
- `OUT OF SCOPE` — the subject matter exists but is **deliberately excluded
  from this suite's claim** by a declared exclusion (§26 exclusion list).
  The dimension is inapplicable **as a matter of declared claim boundary**.
- Criterion of choice: ask "would this dimension apply to a future revision
  that grew the excluded behaviour?" If yes (the subject could appear) →
  `OUT OF SCOPE`. If no (the artefact's class cannot have the subject) →
  `NOT APPLICABLE`. Both require a one-line justification in the dimension
  record; an unjustified either is treated as a discrepancy (§37).
- `BLOCKED (applicability)` — applicability itself cannot be decided
  because the artefact information needed to decide is unavailable. Subject
  to the same acquisition-attempt discipline as status-BLOCKED (§0.4).

**Gate-state vocabulary** (distinct from dimension status — meta-review
finding: GLM-5.3-Flash F3.1, GLM-5.3 D3: v1's §29 used `SELF-ASSESSED`,
which was not in the vocabulary): `SELF-ASSESSED` is a **gate-state**,
defined here: the named gate has been discharged by the party whose work is
under assessment, without independent verification. A gate-state never
propagates as a dimension status: §29's SELF-ASSESSED feeds §30, whose
output is the reviewer's own graded statuses. Builder self-assessment is
gate input, not conformance evidence (Checklist §29 closing rule).

### 0.2 Evidence classes

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

**Class-overlap disambiguation rule** (meta-review finding: Qwen D4, GLM-5.3
D12 — UNIT vs PROPERTY overlap; CONFORMANCE purpose-defined overlap): the
class set is **closed** — these eleven, no more. When one artefact of
evidence spans multiple classes (e.g. a property-based test is both UNIT and
PROPERTY), the evidence row labels **all** classes it spans, and the claim
it supports is **bounded by the weakest class in the span**. Classification
precedence: classify by the primary property the evidence establishes, not
by the tool that produced it. A claim that seems to need a twelfth class is
recorded as a discrepancy (§37), never silently shoehorned into an existing
label.

### 0.3 Evidence-strength floor (claim type → minimum evidence class)

Meta-review finding: Deepseek #9, GLM-5.3-Flash hardening #2, Muse D1,
GLM-5.3 C3/D5. v1 stated evidence rules as prose addressed to a vigilant
reviewer; v2 makes the floor mechanical and checkable per row.

| Claim type (as used in this suite) | Minimum evidence class for VERIFIED | Weaker evidence caps status at |
|------------------------------------|--------------------------------------|-------------------------------|
| Implementation-conformance claim ("the code does X") | UNIT / INTEGRATION / PROPERTY (executable, against the real artefact) | MODEL-only → PARTIAL; INSPECTION-only → PARTIAL unless the claim is structural (see below) |
| Absence claim ("no bypass path exists", "no forbidden transition reachable") | Negative test (attempted trigger, observed refusal) or bounded reachability argument **plus** INSPECTION of the entry surface | Assertion-only → OPEN |
| Structural claim (subprocess construction, file layout — not behavioural) | INSPECTION with function/line pointer | MODEL-only → PARTIAL |
| Design-existence claim ("the design says X") | MODEL (this is the only claim MODEL can verify) | — |
| Resource-lifecycle claim (cleanup, backup, watermark) | RESOURCE (test exercising the lifecycle) | MODEL/INSPECTION-only → PARTIAL |
| Historical-behaviour claim ("it behaved thus in the incident") | OBSERVATION, labelled historical, never presented as reproducible | — (cannot reach VERIFIED for a current-behaviour claim) |

**The floor rule:** a dimension status of `VERIFIED` requires **at least one
evidence row of a class at or above the floor for its claim type, with an
artifact locator** (test ID, file:line, commit, or log path). MODEL-only
evidence caps the status at `PARTIAL` — mechanically, not by reviewer
discipline. Every VERIFIED status in this suite is auditable against this
table; a reviewer finding a VERIFIED below floor records it as an S2
discrepancy (§37 severity scale).

### 0.4 BLOCKED discipline (dimension level)

`BLOCKED` is the most gameable status in any review vocabulary — it can
launder an avoided FAIL into an indefinite pause (meta-review finding:
GLM-5.3-Flash F5). v2 discipline, binding on every BLOCKED dimension row:

1. **Acquisition-attempt record (mandatory):** the row states (a) *what*
   is missing (evidence, infrastructure, or external capability); (b) *what
   acquisition was attempted* — at least one concrete attempt, or a reasoned
   statement of why no attempt is possible; (c) *who owns the escalation*
   and where it is recorded; (d) whether the missing capability is inside or
   outside the declared scope (§26).
2. **BLOCKED is not a FAIL shelter:** if the underlying obligation would
   grade FAILED if assessed with available evidence, the reviewer MUST grade
   FAILED, not BLOCKED. BLOCKED is only available when the *verification
   itself* — not an unfavourable result — is what cannot proceed.
3. **Forbidden transitions (review-process level, §39):** BLOCKED → VERIFIED
   without citing the new evidence that unblocked it; BLOCKED held on a
   Critical dimension (§33.1) without escalation beyond one review cycle.
4. **Escalation:** BLOCKED on a Critical dimension escalates immediately to
   the orchestrator (for this project: a blocker comment on the commissioning
   issue). BLOCKED on a Material/Supporting dimension is recorded and
   reviewed at the next gate.

### 0.5 Stopping rules for closed enumerations

Meta-review finding: Sonnet D3 (no stopping rule for dimension, evidence-
class, or mutation enumeration), Qwen D2 (no halting condition for the
adversarial review itself). v1 demanded falsifiable completeness of the
governed artefact while leaving its own enumerations open-ended — trying one
trivial mutation technically satisfied §31 as written. v2 closes each
enumeration:

1. **Dimensions (§1):** the dimension set is **closed at exactly the
   canonical checklist's 36**. Coverage is checkable by count and by
   checklist-mapping (§1's baseline block). Candidate 37th dimensions are
   handled by the declared exclusion list (§26) and the meta-lifecycle
   (§40.3), never by silent addition.
2. **Evidence classes (§0.2):** closed at the canonical eleven; a claimed
   need for a twelfth is a discrepancy, not an extension.
3. **Mutations (§31):** minimum set = **one plausible violating mutation per
   Critical invariant** (§33.1's critical set), generated by the named
   strategy ("mutate the mechanism that enforces the invariant, at its
   implementation site"). The enumeration stops when every Critical
   invariant has ≥1 mutation row. Additional mutations are optional, not
   required for discharge.
4. **Adversarial review (§30):** the review halts when the attack log
   (§30.2) covers all mandatory items AND the halting criterion of §30.3 is
   met. Unbounded attack generation is not required, and demanding it is
   itself a process defect.

### 0.6 Honesty rules (v1 rules retained, v2 additions marked)

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
4. **(v2) Underclaiming is policed symmetrically with overclaiming**
   (meta-review finding: GLM-5.3 attack-surface "asymmetric evasion"):
   downgrading a claim ("exhaustive exploration is infeasible", "this
   dimension is OUT OF SCOPE") to escape verification burden is treated
   exactly like an unsupported upgrade — it requires a §35 declaration or a
   §26 exclusion entry, and an unjustified downgrade is an S2 discrepancy.
5. **(v2) Freshness has consequences, not just disclosure** (meta-review
   finding: GLM-5.3-Flash F8, GLM-5.3 C4/D4, Kimi D6): every evidence row
   carries a locator pinned to a revision (commit hash for code, date for
   runs). Evidence older than the governed artefact's current revision does
   not support VERIFIED — it supports at best PARTIAL with a staleness
   note, and the affected dimension re-enters assessment. Verdict
   invalidation on artefact change is modelled in §39.6, not left to
   reviewer vigilance.
6. **(v2) An empty Discrepancy Register must be earned** (meta-review
   finding: Sonnet D4 — "an empty register is treated as compatible with
   PASS when it is at least as likely to mean nobody looked hard enough"):
   a review concluding with an empty register must cite, from the attack log
   (§30.2), the attacks that were attempted and held. An empty register
   without an attack log is graded as "no adversarial effort", not as
   "no findings".

### 0.7 Terms of art

Terms used with specific meaning in this suite (meta-review finding:
GLM-5.3 D13 — undefined terms of art): **guard** = a predicate that must
hold for a transition to fire; **effect** = an action performed as a
consequence of a transition; **barrier** = the authoritative mechanism that
makes a forbidden transition impossible or refused; **discriminating
evidence** = evidence that could have come out differently if the obligation
were violated (a test that cannot fail is not discriminating); **tractable**
(§9 scope statements) = the enumeration's state space is small enough to
exhaust on this host within one harness run — used only where the suite
claims it and otherwise declared as bounded/sampled; **settlement** = the
act of recording a terminal outcome in durable state. Where a term is used
in the canonical checklist's sense, the checklist (2026-08-29) is the
glossary of record.

---

## 1. Canonicality — APPLICABLE — VERIFIED

### 1.1 Version and canonical baseline (v2)

Meta-review finding: Deepseek #7, GLM-5.3 D1 — v1 was unversioned and cited
no baseline, making reviews non-reproducible and silent weakening
undetectable. v2 states both:

- **This suite's version:** 2.0 (frontmatter `suite_version`), 2026-09-01.
  v1.0 (2026-08-30, issue #523 lineage) is superseded by this file; v1 is
  preserved in git history and remains the record of what the v1-era
  statuses were graded against.
- **Canonical baseline:** `to-file/ASES Universal Conformance Checklist.md`,
  **2026-08-29 revision** — this is the universal instrument this suite
  instantiates, by revision. A revision of the checklist invalidates this
  baseline: the instantiation must be re-diffed against the new revision
  before any of its verdicts are consumed (§39.6 invalidation triggers).
- **Changelog:** v1→v2 changes are itemised with per-finding traceability in
  the Synthesis Record (§40). No obligation was silently rewritten between
  versions; every v2 change is traceable to a meta-review finding ID or a
  synthesis-discovered gap (§40.2).

### 1.2 Dimension-set closure (stopping rule, §0.5(1) instantiated)

The Universal Checklist remains domain-independent; this file carries all
project-specific states, events, resources, tests, and assumptions. No
universal obligation has been silently rewritten. Where the swarm's VSDD-lite
adoption (design Appendix A) deliberately thins a universal obligation
(e.g. no formal proof harnesses, no exhaustive edge-case catalog, no
mandatory mutation-testing CI gate), the thinning is **declared in §35
adaptations** with the design's rationale, not smuggled in.

The dimension set is **closed at exactly the canonical 36** (§§1–36 here map
one-to-one to Checklist §§1–36). This suite's coverage claim is bounded to
that set plus the declared project additions (§0, §37, §39, §40 — additions
strengthen, never replace). Behaviour classes with no corresponding
dimension (threat model, capacity, specification quality, migration/
composition, deployed-artefact identity) are handled by the declared
exclusion list in §26 — making the coverage claim falsifiable rather than
vacuously universal (meta-review finding: GLM-5.3-Flash F1, Kimi D1).

Evidence: this file exists; the Universal Checklist is quoted by dimension
number throughout; adaptations are itemised in §35; the baseline revision is
named above and re-checkable. Status: VERIFIED.

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

Convention adopted verbatim at universal level and **extended at project
layer** (declared §35(6)): dimension statuses `[ ] OPEN`, `[x] VERIFIED`,
`[~] PARTIAL`, `[!] FAILED`, `[⏸] BLOCKED` (v2 addition, §0.1); applicability
`APPLICABLE / NOT APPLICABLE / OUT OF SCOPE / BLOCKED (applicability)` with
the NA-vs-OOS criterion of §0.1; `BLOCKED` is not `VERIFIED`, enforced by the
§0.4 discipline and the §39.4 forbidden-transition register rather than by
admonition. Every dimension below carries both an applicability and a status;
no dimension is left unstated. Gate-states (`SELF-ASSESSED`) are defined and
kept distinct from dimension statuses (§0.1). Status: VERIFIED (the v2
vocabulary is self-consistent by §40.2's inspection checks; the v1
violations — undefined SELF-ASSESSED, undefined dimension-BLOCKED — are
closed in this version).

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

**Class-set closure and overlap handling (v2):** the class set is closed at
the canonical eleven (§0.2). Known overlaps in this suite, disambiguated by
the §0.2 rule (label all spanned classes; claim bounded by the weakest):
T21–T26 rows are labelled UNIT and PROPERTY (they are executable tests of
invariant-shaped properties — the PROPERTY label adds the invariant-scoped
reading, the UNIT label the executable one; neither may be cited alone for a
claim the other cannot support). CONFORMANCE rows in this suite are
purpose-defined (evidence of conformance produced by the VSDD process
itself); where a CONFORMANCE row exists it names its underlying class too,
so double-counting one artefact as two independent evidence rows is
detectable. A claim needing a class outside the eleven is a §37
discrepancy, not a new label.

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

### 26.1 Declared exclusion list (v2)

Meta-review finding: GLM-5.3-Flash F1, Kimi D1 — an undeclared-exclusion
universality claim is unfalsifiable: any gap can be reclassified post hoc as
"not state-based". v2 declares the exclusion list, making the coverage claim
falsifiable. Behaviour classes **outside this suite's claim** (each either
genuinely absent from the governed artefact's class, or deliberately
excluded — with the §0.1 criterion applied):

| Excluded area | Why excluded | NOT APPLICABLE or OUT OF SCOPE | Re-entry trigger |
|---------------|--------------|-------------------------------|------------------|
| Adversarial-input / threat model (injection, hostile input to the Observer itself) | The Observer's inputs are the operator's own host surfaces (logs, tmux, hub); a threat-model dimension does not exist in the canonical 36 and is not added at project layer | OUT OF SCOPE (the subject could exist in a future revision that parses untrusted input) | Any revision that parses externally-controlled input |
| Capacity / quantitative obligations (latency, throughput, degradation under load) | The Observer is a periodic batch scanner; its cycle interval is a declared calibration knob, not a guarantee | OUT OF SCOPE | Any revision with a latency/throughput SLO |
| Specification quality (attacking the design document itself) | Partially covered: D3 (§37) is a spec-quality catch (letter-vs-intent divergence); a full ambiguity/contradiction scan of the design is not a checklist dimension | OUT OF SCOPE (partially exercised via §21/§37) | Commissioning of a design-review gate |
| Data integrity across model versions (restart into states persisted by an earlier model version; schema evolution) | manager-state.json schema is single-version today; no migration exists to verify | OUT OF SCOPE | Any schema change to persisted state |
| Composition (two independently reviewed components holding incompatible assumptions) | The Observer composes with crosslink CLI + tmux + git; boundary assumptions are inventoried (§13) but cross-component assumption auditing is not a checklist dimension | OUT OF SCOPE | Any second supervised component with its own suite |
| Deployed-artefact identity (binding reviewed revision to what runs) | Partially covered: evidence is pinned to @68750f28 and the §0.6(5) freshness rule invalidates on revision change; the Observer does not yet self-report its running revision | OUT OF SCOPE (partially exercised via §0.6(5)/§39.6) | Any deployment where the running revision can drift from the reviewed one |

This list is part of the suite's claim boundary: a reviewer may challenge an
exclusion (via §30/§37) but may not treat an unlisted area as covered by
implication. Status contribution: the exclusions are declared, which is what
§26 requires; the underlying dimension status remains PARTIAL for the
implemented-claims scoping above.

**Status: PARTIAL** (implemented claims scoped and verified; design-level
claims not made; exclusion list declared in §26.1).

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
§29 closing rule). Status: SELF-ASSESSED (gate-state, defined §0.1) — gate
input for §30, never conformance evidence by itself.

---

## 30. Adversarial Reviewer Gate — APPLICABLE — OPEN

### 30.1 Reviewer diligence requirements (v2 — mirrors the builder gate)

Meta-review finding: Sonnet D4, GLM-5.3-Flash F6, GLM-5.3 C5/D6 — v1's
builder gate was carefully flagged non-authoritative, but nothing checked
*reviewer* diligence: a rubber-stamp review was structurally
indistinguishable from a rigorous one, and nothing required reviewer
independence. v2 imposes on the reviewer the same class of discipline the
builder gate imposes on the builder:

1. **Identity and independence attestation (mandatory, before verdict
   acceptance):** the reviewer records who they are (agent identity or
   name), attests they are not the builder of the governed artefact or the
   author of this suite, and discloses any conflict of interest. A review
   without the attestation is not accepted as gate output — self-review
   laundered through adversarial vocabulary is the exact "prior approval is
   not correctness evidence" failure, one level up.
2. **Attack log (mandatory sink, distinct from §37):** every attack is
   recorded with: ID, target obligation (by § reference), attempted
   input/method, expected-safe behaviour, observed behaviour, evidence
   pointer, and outcome — `HELD` (barrier held), `BREACHED` (→ §37 entry),
   or `NOT-ATTEMPTED` (with reason). v1 commanded attacks but had no record
   sink: a barrier attacked-and-held was indistinguishable from a barrier
   never attacked (meta-review finding: GLM-5.3 D8, Deepseek #6, Kimi §30).
   The attack log is the fix: attempted-and-held becomes visible evidence.
3. **Beyond-the-list attacks (minimum 3):** the pre-staged list below is
   public and enumerable, which permits anticipatory hardening — a builder
   can pre-harden exactly the listed attacks (meta-review finding:
   GLM-5.3-Flash F6). The reviewer must derive and log **at least three
   attacks not on the pre-staged list** before the gate can discharge.
4. **Empty-register rule:** if the review concludes with no new §37
   entries, the verdict must cite the attack-log `HELD` rows that justify
   it (§0.6(6)). An empty register without an attack log is graded "no
   adversarial effort".
5. **Calibration requirement (declared, not yet built):** the full form of
   this check is a calibration harness — a sample instantiation with N
   seeded defects of known types (MODEL-only evidence marked VERIFIED, an
   untested forbidden transition, a BLOCKED-avoided FAIL), with reviewer
   acceptance gated on detecting a threshold (meta-review finding:
   GLM-5.3-Flash F6's constructive flip; GLM-5.3 C8/D9 positive-control).
   **The harness does not exist yet.** This is declared here and recorded
   as §37 D12; until it exists, requirements 1–4 are the interim diligence
   check, and the suite's own verdict is capped at REWORK by §33.3 rule 3
   (open S2 entry). Building the harness is a follow-on obligation, not a
   silent omission.

### 30.2 Pre-staged attack surface

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

### 30.3 Halting rule (stopping rule for the review itself)

Meta-review finding: Qwen D2 — v1 mandated exhaustive adversarial attack
with no termination condition, risking infinite review loops. The review
halts when **all** of:

1. every §30.2 item has an attack-log entry (`HELD`, `BREACHED`, or
   justified `NOT-ATTEMPTED`);
2. the §30.1(3) minimum of three beyond-the-list attacks is logged;
3. the **stability criterion** holds: the last five logged attacks produced
   no new §37 entry (five is the declared stability window — large enough
   to outlast clustering of easy findings, small enough to bound the review);
4. the reviewer states the halting basis in the verdict (which items, how
   many attacks, when the stability window closed).

Halting is a floor, not a ceiling: a reviewer may continue, but no
consumer may demand unbounded attack generation as a gate condition.

### 30.4 Dissent and adjudication

Reviewer disagreements with builder-graded statuses, and reviewer/builder
deadlocks, are recorded as §37 entries with severity per the §37 scale and
escalated to the adjudicator named in §33.4 (the human orchestrator, via
the commissioning issue). The verdict re-derives after adjudication
(§33.3); it is never negotiated between the parties.

Status: OPEN — this gate is the issue's purpose and has not run. The v2
diligence requirements (§30.1) are part of the gate's acceptance criteria
for the Hy4 Preview review.

---

## 31. Mutation Verification — APPLICABLE — PARTIAL

Per Checklist §31, with VSDD-lite's declared deferral of systematic mutation
testing (design A.2: mutmut/Stryker class tools "overkill for a swarm whose
dominant failure mode is admission + attribution + filing durability"):

**Minimum set and generation strategy (v2 stopping rule, §0.5(3)
instantiated):** meta-review finding: Sonnet D3 — v1 asked reviewers to
"identify plausible violating mutations" with no minimum count or strategy,
so one trivial mutation technically satisfied the instruction. v2 fixes the
minimum set: **one plausible violating mutation per Critical invariant**
(§33.1's Critical set: I1–I5, I7, I9), generated by the named strategy —
*mutate the mechanism that enforces the invariant, at its implementation
site*. The enumeration stops when every Critical invariant has ≥1 row;
additional rows (e.g. I11 below, a Material invariant) are optional
strengthening. The table below meets the minimum: I1, I2, I3, I4, I5, I7,
I9 each have a row; I6/I8/I10/I12/I13 are Material/OPEN and outside the
minimum set.

| Critical property | Plausible violating mutation | Introduced at | Detected by |
|-------------------|------------------------------|---------------|-------------|
| I1 fail-closed mode | `*)` case arm returns act; or DRY_RUN check removed | lines 454–461 | T21 (garbage → observe assertion) |
| I2 act-requires-ID | startup fatal block removed | lines 469–475 | T24 (rc≠0 + fatal event) |
| I3 ownership fail-closed | downgrade branch returns allowed | authorize_destructive | T22/T23 (downgrade events asserted) |
| I4 silence-never-kills | gate bypassed / log_quiet defaulted true | convergent_gate / act_frozen | T25 (zero frozen-termination records), T25b (veto) |
| I5 park-extension | expiry kill without re-scan | lines 1840–1865 | T5 (extension event asserted) |
| I7 loud deny | early-return without event (the ORIGINAL #460 bug) | kickoff_cleanup | T20a (deny event asserted) |
| I9 single instance | lockfile check removed | 3185–3236 | T19 |
| I11 watermark hold *(optional — Material invariant)* | advance watermark on RED | backup pass | T15 |

- **Mutations introduced at the relevant implementation/boundary:** the
  table names the exact sites.
- **The suite detects them:** each row's test asserts the property the
  mutation would break (these are mutation-*detection* properties embedded
  in the harness; the mutations themselves have not been physically
  injected and run — that is the PARTIAL, and it is the declared VSDD-lite
  deferral).
- **Surviving mutations trigger review:** rule stated (Checklist §31);
  no mutation campaign has run, so no survivors exist to review.
- **Deferral is verdict-visible (v2):** meta-review finding: Deepseek #3 —
  v1's language prevented false mutation *claims* but left the loophole
  that zero mutation campaigns still permitted PASS via the undefined
  critical-obligations rule. v2 closes it: §33.3 rule 4 makes physical
  discharge of the minimum set a PASS precondition, and rule 3 caps any
  declared deferral at REWORK. The deferral cannot be argued around; it can
  only be discharged (run the campaign) or re-declared with a fresh §35
  rationale that the reviewer may attack.

**Status: PARTIAL** (minimum set designed, strategy named, and mapped;
physical mutation campaign deferred per design A.2 — declared adaptation
§35(2), verdict-visible per §33.3).

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

## 33. Verdict — APPLICABLE — REWORK (current state, derived by §33.3 algebra)

### 33.1 Criticality taxonomy (defines "critical obligation")

Meta-review finding: Deepseek #2 ("the single most exploitable gap"),
Qwen D1, GLM-5.3-Flash F2, GLM-5.3 C6/D7 — v1's verdict turned on
"critical obligations" that were never defined, letting a reviewer mark
failures non-critical and reach PASS. v2 defines criticality by derivation,
not by reviewer judgement:

**Derivation rule:** an obligation of this suite is **Critical** iff
violating it falsifies a registered §26 guarantee or defeats a core purpose
of the governed artefact (the Observer's reason to exist: supervise without
becoming the hazard it supervises). It is **Material** iff violating it
materially weakens enforcement or the evidence claim without falsifying a
§26 guarantee. It is **Supporting** otherwise (structural hygiene).

Applied to this suite's obligation set:

| Criticality | Obligations (by suite reference) | Rationale |
|-------------|----------------------------------|-----------|
| **Critical** | Invariants I1–I5, I7, I9 (lethality control: mode, identity, ownership, convergent gate, park, breaker, single-instance); forbidden transitions F1–F10 (each is the reachable form of a lethality hazard); §17's observation-cannot-authorize claim; §11 ownership fail-closed; §10 identity non-aliasing | Violating any of these = the Observer kills or mutates without authority — falsifies "the Observer never kills on silence alone" and the ownership/mode guarantees (§26) |
| **Material** | I6, I8, I10–I13; F11–F16 (design-only phase-gate barriers); §5.1 Layer A implementation; §22 test-first discipline; §28 traceability completeness; §12 resource inventory; §13 boundary semantics; §15 freshness; §16 transport; §18 recovery; §20 purity; §32 environment integrity | Violating weakens durability, traceability, or disclosure but does not create unauthorised lethality |
| **Supporting** | §23 tooling selection; §25 abstraction documentation; §34 minimality mechanics; §35 adaptation declarations; §0 vocabulary hygiene | Violating degrades review quality, not the artefact's guarantees |

The assignment is itself reviewable: a reviewer who disputes a criticality
assignment raises it as a dissent (§30.4); the adjudication rule is §33.4.
Criticality re-derivation is required when §26's claims change.

### 33.2 Verdict inputs

The algebra consumes, and only consumes:

1. The §38 summary table: every dimension's applicability, status, and
   criticality class (per §33.1, for the obligations each dimension carries).
2. The §37 Discrepancy Register with severities per the §37 scale, each
   entry adjudicated or open.
3. The §30 gate outputs: attack log completeness (§30.2) and halting
   criterion (§30.3).
4. The §31 mutation table discharge state (minimum set met or declared
   deferral standing).

### 33.3 Aggregation algebra (deterministic, first match wins)

Meta-review finding: Sonnet D2, Kimi (§33 finding), Deepseek #2/#3, Qwen D1,
GLM-5.3-Flash F3, GLM-5.3 C6 — two honest reviewers holding an identical
filled-out suite could issue opposite verdicts. v2 replaces prose with an
ordered rule set; the reviewer's role is to challenge *statuses* (via
§30/§37), never to override the derivation:

1. **FAIL** — if ANY APPLICABLE **Critical** obligation is `FAILED`; or any
   forbidden transition F1–F10 is demonstrated reachable in the implemented
   core; or authority/identity/ownership is broken where implemented.
2. **BLOCKED** — else, if verification of ANY APPLICABLE **Critical**
   obligation is `BLOCKED` (status-level, §0.4) with acquisition attempts
   recorded and the capability inside declared scope. BLOCKED on a Critical
   obligation blocks the verdict — it does not downgrade to REWORK and never
   rounds up to PASS.
3. **REWORK** — else, if ANY APPLICABLE **Critical** or **Material**
   obligation is not `VERIFIED` (i.e. `OPEN`, `PARTIAL`, or `BLOCKED` where
   the §0.4 discipline shows acquisition is still possible), or the §37
   register holds any open S1/S2 entry, or the §30 attack log is incomplete,
   or the §31 minimum mutation set stands only as a declared deferral.
4. **PASS** — else (all of): every APPLICABLE **Critical** obligation
   `VERIFIED` with the §0.3 floor met; every APPLICABLE **Material**
   obligation `VERIFIED` or `PARTIAL` with an explicit accepted-limitation
   declaration naming what remains and why it is accepted; no APPLICABLE
   dimension `OPEN` or `BLOCKED`; §37 holds no open S1/S2 entries; §30
   attack log complete with halting criterion met; §31 minimum set
   physically discharged (a declared deferral caps at REWORK — rule 3).
   `Supporting` obligations may be PARTIAL under PASS only with a
   one-line accepted-limitation note each.

**Properties of the algebra:** monotone (improving a status never worsens
the verdict); no rounding (PARTIAL never counts as VERIFIED; BLOCKED never
counts as anything but blocked); verdict-relevant and verdict-irrelevant
findings are distinguished by criticality, not by reviewer discretion; the
derivation is reproducible by any reviewer from the §38 table alone.

### 33.4 Disputes, tie-breaks, and adjudication

- A reviewer disputing a *status* or a *criticality assignment* files a
  §37 entry (or §30.4 dissent) naming the row; the verdict is then
  **re-derived**, never negotiated.
- Builder/reviewer deadlock (same evidence, contested grade) goes to the
  **adjudicator**: for this project, the human orchestrator (the operator),
  via the commissioning issue. The adjudicator's ruling is recorded in §37
  and the algebra re-runs.
- FAIL-vs-REWORK boundary cases are decided by the algebra, not by
  judgement: if rule 1's conditions literally hold, FAIL; otherwise REWORK.
  (Meta-review finding: GLM-5.3-Flash F3(4) — v1 could not adjudicate its
  own FAIL-vs-REWORK boundary; v2 makes the boundary mechanical.)

### 33.5 Verdict expiry and invalidation

A verdict is bound to the evidence revisions it was derived from (§0.6(5)).
Invalidation triggers (modelled as §39.6 transitions, not reviewer
vigilance): governed-artefact revision change (any code commit touching
observer.sh or run-tests.sh after the evidence-pinning revision); canonical
baseline revision change (§1.1); a §37 S1 entry opened after verdict
issuance. Invalidation re-opens the affected dimensions and forces
re-derivation; the expired verdict is marked superseded in §39's state
record, never silently retained.

### 33.6 Current verdict (v2, derived)

Applying §33.3 to the §38 table as of this revision:

- Rule 1 (FAIL): not triggered — no Critical obligation is FAILED; F1–F10
  all VERIFIED-barriered; no reachable forbidden transition demonstrated.
- Rule 2 (BLOCKED): not triggered — no Critical obligation is BLOCKED
  (I12 is OPEN, not BLOCKED: nothing prevents implementing P3-AC8).
- Rule 3 (REWORK): **triggered** — Critical obligations I12 (evidence
  durability, OPEN) and I13-messaging (PARTIAL) are not VERIFIED; Material
  obligations §5.1 Layer A (unimplemented), F11–F16 (design-only), §22
  test-first (D5), §28 (PARTIAL) are not VERIFIED; §31 stands as declared
  deferral; §30 attack log does not yet exist (gate not run).
- Rule 4 (PASS): therefore unreachable.

**Verdict: REWORK** — identical to v1's verdict but now *derived*, not
asserted: the reviewer can re-run the algebra from §38 and must get the
same answer. This verdict is the suite's honest output for the adversarial
gate: the reviewer should treat REWORK as the claim under test.

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

**Cross-reference mechanics (v2):** meta-review finding: GLM-5.3-Flash F4,
Qwen D5 — duplicated evidence rows drift apart unnoticed. v2 rule: whenever
two sections cite the same test for overlapping obligations (e.g. §6 and §7
both citing T25), the row must cross-reference the other section
("same evidence as §7 row X"). If one copy is later re-graded, the
cross-reference forces the other copy to be re-checked — divergence between
copies becomes detectable instead of silent.

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
6. **(v2) Extended status vocabulary** — dimension-level `BLOCKED` status,
   NA-vs-OOS criterion, gate-state `SELF-ASSESSED`, evidence-class floor,
   evidence-strength table, stopping rules, freshness consequences, and
   underclaiming policing (all §0). These **strengthen** universal
   obligations (Checklist §3/§4/§31/§32), never weaken them. Rationale:
   close gaps flagged by seven independent meta-reviews (§40).
7. **(v2) Reviewer diligence gate (§30.1)** — identity/independence
   attestation, attack log, beyond-the-list attacks, halting rule,
   dissent/adjudication. Project addition strengthening Checklist §30.
8. **(v2) Verdict aggregation algebra (§33)** — criticality taxonomy +
   deterministic status→verdict mapping. Project addition strengthening
   Checklist §33.
9. **(v2) Review-process state model (§39)** — project addition; the
   canonical checklist has no state model for the review process itself
   (flagged upward, see §40.3).

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
satisfaction — which is why twenty-three dimensions read PARTIAL and two
read OPEN rather than a comfortable uniform VERIFIED. (v2 correction: v1's
§36 claimed "eleven dimensions read PARTIAL", contradicting v1's own §38
table — recorded as §40.4(6).)

---

## 37. Discrepancy Register (project-specific addition)

Every design-vs-implementation or issue-vs-repository divergence found
during instantiation. This register is the reviewer's index; each entry
names the affected dimensions.

**Severity scale (v2 — defined; meta-review finding: GLM-5.3 D17):**

- **S1 (Critical)** — defeats a core purpose of the governed artefact or
  falsifies a §26 guarantee. Blocks PASS permanently until resolved.
- **S2 (High)** — materially weakens enforcement or the evidence claim.
  Blocks PASS while open (§33.3 rule 3/4).
- **S3 (Medium)** — inconsistency, redundancy, or documentation drift.
  Does not block PASS but must be adjudicated before gate closure.
- **S4 (Low)** — cosmetic, stale pointers, rot. Recorded for completeness.

| ID | Discrepancy | Evidence | Affects | Severity for review |
|----|-------------|----------|---------|--------------------|
| D1 | Issue #523 names `run-tests.sh T28-T33` as evidence; **no T28–T33 exist on any branch** — harness ends at T27 (verified across all feature branches) | `git log --all` + branch greps (this session) | §0, §22, §28 | S4 (stale pointer) — but the reviewer must not accept phantom test references |
| D2 | Design Phases 1 and 2 (P1-AC1..7, P2-AC1..7, P2-MSG1..10) have **no implementation** anywhere in the repo (zero hits: `free -m` gate, `launch-deferred-memory`, `agent-communication`, `operator-report`, `execution-engine-backlog`, `WAITING_FOR_ORCHESTRATOR`) | repo-wide search (this session) | §5.1, §8 F11–F16, §21, §28, §33 | S2 — the swarm's phase-gate structure is prose-only today |
| D3 | P3-AC4's letter ("pane-hash AND commit-age stale AND log-quiet AND hub-position static") vs implementation (any-one-of {hub-static, commit-stale, process-exit, resume-expired} + log-quiet veto; pane-hash excluded entirely) — implementation is *stronger* than the design's letter but does not match it | design line 645 vs observer.sh 1613–1671 | §9 I4, §21 | S3 — rule whether stronger-than-design is conformance |
| D4 | P3-AC2/AC3 earlyoom attribution (`journalctl -u earlyoom`, machine `attribution` field, explicit negative check) — **unimplemented**; zero `journalctl` references in observer.sh | grep (this session) | §13, §19, §21, §28, §33 | S2 — FAILED/KILLED discrimination is a stated P3 gate criterion |
| D5 | VSDD test-first red-gate discipline unevidenced: test+implementation land in the same commits (2e690049, 1050447c, 2fa5a189, c5eb6e72) | git history | §2, §22 | S3 |
| D6 | Instance lock lives under OBSERVER_STATE_DIR — two Observers with *different* state dirs supervising the same fleet would not exclude each other | lines 242, 3195 | §14, §30(8) | S3 — deployment-discipline assumption, undocumented as such |
| D7 | Evidence bundles live under the state dir (tmp-backed); hub comment carries the ref + sha256, but if the comment post fails (`notified=false`) the bundle exists only in /tmp — I12's own defect rule | lines 679–681, 1756 | §9 I12, §30(9) | S3 — the failure path of the durability mechanism is itself the durability gap |
| D8 | Harness lacks BLOCKED semantics; `check` uses `grep -q … 2>/dev/null` tolerance, so some environment failures can masquerade as PASS | run-tests.sh 32–45 | §32 | S3 |
| D9 | `server-memory-management.md` is cited by the design as `.crosslink/knowledge/server-memory-management.md` but exists in git history at repo root (commit 9786d560) and is not present in this worktree's knowledge dir — pointer rot in the design's depends_on | git show 9786d560 (this session) | §13, frontmatter | S4 |
| D10 | **(v2 synthesis)** Calibration harness for reviewer diligence (§30.1(5)) does not exist — reviewer competence remains an untested trust assumption | §30.1(5) | §30, §33 | S2 — caps suite verdict at REWORK until built or formally waived |
| D11 | **(v2 synthesis)** v1 statuses were graded before the §0.3 evidence floor existed; re-audit during synthesis confirmed all carried-over VERIFIED rows meet the floor (UNIT/INSPECTION-with-locator for implementation claims, MODEL for design-existence claims), but the floor itself has never been enforced mechanically | §0.3 audit (this session) | §0, §4, §38 | S3 — reviewer should spot-check §38 rows against the floor table |
| D12 | **(v2 synthesis)** The Observer does not self-report its running revision — deployed-artefact identity relies on external pinning (@68750f28) and the §39.6 invalidation trigger | §26.1 exclusion table | §10, §26.1 | S3 — declared exclusion; re-entry trigger documented |

---

## 38. Summary Status Table

| Checklist § | Dimension | Applicability | Criticality (§33.1) | Status |
|-------------|-----------|---------------|--------------------|--------|
| 1 | Canonicality | APPLICABLE | Supporting | VERIFIED |
| 2 | Lifecycle Integration | APPLICABLE | Material | PARTIAL |
| 3 | Checklist Semantics | APPLICABLE | Supporting | VERIFIED |
| 4 | Evidence Classes | APPLICABLE | Supporting | VERIFIED |
| 5 | State Model Completeness | APPLICABLE | Material | PARTIAL |
| 6 | State Conformance | APPLICABLE | Material | PARTIAL |
| 7 | Transition Conformance | APPLICABLE | Material | PARTIAL |
| 8 | Forbidden Transitions | APPLICABLE | Critical | PARTIAL |
| 9 | Invariant Conformance | APPLICABLE | Critical | PARTIAL |
| 10 | Identity Conformance | APPLICABLE | Critical | PARTIAL |
| 11 | Ownership Conformance | APPLICABLE | Critical | VERIFIED |
| 12 | Resource Conformance | APPLICABLE | Material | PARTIAL |
| 13 | External Boundary Conformance | APPLICABLE | Material | PARTIAL |
| 14 | Concurrency Conformance | APPLICABLE | Material | PARTIAL |
| 15 | Temporal/Asynchronous Conformance | APPLICABLE | Material | PARTIAL |
| 16 | Transport Conformance | APPLICABLE | Material | PARTIAL |
| 17 | Observation and Projection | APPLICABLE | Critical | PARTIAL |
| 18 | Recovery | APPLICABLE | Material | PARTIAL |
| 19 | Alternative Control Paths | APPLICABLE | Material | PARTIAL |
| 20 | Purity Boundary Audit | APPLICABLE | Material | PARTIAL |
| 21 | Model→Implementation Conformance | APPLICABLE | Material | PARTIAL |
| 22 | Model-Derived Tests | APPLICABLE | Material | PARTIAL |
| 23 | Verification Tooling | APPLICABLE | Supporting | VERIFIED |
| 24 | Adversarial Verification | APPLICABLE | Material | OPEN |
| 25 | Abstraction Conformance | APPLICABLE | Supporting | PARTIAL |
| 26 | Scope and Guarantee Conformance | APPLICABLE | Material | PARTIAL |
| 27 | Recovery and Refinement | APPLICABLE | Material | VERIFIED |
| 28 | Contract Chain and Traceability | APPLICABLE | Material | PARTIAL |
| 29 | Builder Completion Gate | APPLICABLE | Material | SELF-ASSESSED |
| 30 | Adversarial Reviewer Gate | APPLICABLE | Material | OPEN |
| 31 | Mutation Verification | APPLICABLE | Material | PARTIAL |
| 32 | Test Environment Integrity | APPLICABLE | Material | PARTIAL |
| 33 | Verdict | APPLICABLE | — | **REWORK** |
| 34 | Minimality | APPLICABLE | Supporting | VERIFIED |
| 35 | Universal Adaptation Rule | APPLICABLE | Supporting | VERIFIED |
| 36 | Governing Principle | APPLICABLE | Supporting | VERIFIED |

**Overall: REWORK (derived by §33.3, reproducible from this table)** —
implemented core strongly verified; Phase 1/2 and earlyoom attribution
unimplemented; adversarial gate is the next action and this suite is its
input. Criticality column is the §33.1 assignment per dimension's dominant
obligations; a dimension can carry obligations of mixed criticality — the
verdict algebra (§33.3) consumes the obligation-level classes, this column
is the reviewer's index.

---

## 39. Review-Process State Model (v2 project addition)

Meta-review finding: Kimi D2/D5/D10, Qwen D6, Muse D3, GLM-5.3 C4 — the
checklist demands a state model of every governed system while the review
process itself had none: no states, no guards, no recovery from a wrong
verdict, no concurrency rules, no freshness/invalidation semantics. v2
models the review itself. This is a project addition that strengthens
Checklist §5/§18 applied reflexively (flagged upward for the universal
layer, §40.3).

### 39.1 States (one review instance)

`DRAFT` → `IN_REVIEW` → {`BLOCKED`, `NEEDS_REWORK`} → `VERDICT_ISSUED` →
{`ACCEPTED`, `REOPENED`, `EXPIRED`}.

- **DRAFT** — suite instantiated, statuses being graded. Not gate input.
- **IN_REVIEW** — adversarial gate active (§30). Attack log open.
- **BLOCKED** — ≥1 Critical obligation status-BLOCKED (§0.4). Verdict
  derivation is suspended, not issued (§33.3 rule 2).
- **NEEDS_REWORK** — algebra derived REWORK; builder remediation in flight.
- **VERDICT_ISSUED** — algebra run, verdict recorded with its inputs
  (§38 table snapshot + §37 register state + attack log ref).
- **ACCEPTED** — verdict consumed by the commissioning decision.
- **REOPENED** — a §33.5 invalidation trigger fired or adjudication
  overturned a status; affected dimensions re-enter assessment.
- **EXPIRED** — evidence revisions drifted past the §0.6(5) freshness rule
  without a re-derivation; verdict is retained as historical record only.

### 39.2 Identity of a review instance

A review instance = (suite version, canonical-baseline revision, governed-
artefact revision, reviewer identity, start date). Resumption after a pause
is the **same** review iff the governed-artefact revision is unchanged; any
revision change starts a new review (the old one EXPIRED). Reviewer
substitution mid-review is permitted only with a recorded reason and does
not alias the instance — the new reviewer re-attests independence (§30.1(1))
and inherits the attack log.

### 39.3 Ownership

- The **reviewer** owns the attack log and their graded statuses.
- The **builder** owns remediation of NEEDS_REWORK items.
- The **orchestrator** (adjudicator, §33.4) owns disputes, reviewer
  replacement, and ACCEPTED.
- The verdict itself is owned by no party: it is derived, and any owner
  triggering an invalidation re-derives it. A verdict cannot be disowned
  silently — supersession is recorded (§39.6).

### 39.4 Forbidden transitions (review process)

| Forbidden transition | Barrier |
|----------------------|---------|
| BLOCKED → VERDICT_ISSUED (any verdict) | §33.3 rule 2 — BLOCKED on Critical suspends derivation |
| BLOCKED → VERIFIED (dimension) without new evidence cited | §0.4(3) |
| VERDICT_ISSUED → ACCEPTED with open S1/S2 §37 entries | §33.3 rule 4 |
| Any state → PASS derivation skipping the algebra | §33.3 is the only derivation path |
| Reviewer issuing a verdict without independence attestation | §30.1(1) |
| Verdict accepted while attack log incomplete | §30.3 halting rule |

### 39.5 Concurrency

Multiple reviewers: findings merge through the adjudicator; **last-write-
wins on a graded status is forbidden** — conflicting grades become §37
entries and re-derive. A builder running a parallel "friendly" review does
not dilute this gate: only reviews meeting §30.1 (attestation + attack log)
count as gate input. The system under review changing mid-review is the
EXPIRED trigger, not a race to be won.

### 39.6 Recovery and invalidation

- **Wrong verdict** (new counterexample post-issuance): REOPENED with a
  scoped re-review (affected dimensions only, attack log appended). The
  superseded verdict stays on record with a pointer to its replacement.
- **Reviewer capture/conflict revealed:** reviewer replaced (§39.2);
  all their statuses re-graded by the replacement.
- **Evidence proven fraudulent:** affected dimensions → FAILED, §37 S1
  entry, full re-derivation.
- **Invalidation triggers (automatic):** governed-artefact revision change;
  canonical-baseline revision change (§1.1); post-issuance S1 entry. Each
  fires EXPIRED/REOPENED — freshness is a modeled transition, not reviewer
  vigilance (§0.6(5)).

---

## 40. Synthesis Record (v2 — meta-reviews → this suite)

### 40.1 Inputs

`specifications/Adverarial Test Suite Reviews:.md` — **seven** meta-reviews
(the issue named four; the file grew): Claude Sonnet 5 High, Kimi K2.6
Instant, Deepseek V4 Pro, Qwen3.8-Pro, Muse Spark 1.2, GLM-5.3-Flash,
GLM-5.3. All seven reviewed the *generic instrument* (the Universal
Conformance Checklist); their findings apply to this instantiation mutatis
mutandis. All four named reviewers issued REWORK; the three later ones
concurred.

### 40.2 Finding → disposition map

Every flagged gap, with where v2 addresses it. "UP" = flagged upward to the
Methodology layer (the universal checklist itself needs the fix; this suite
can only instantiate a strengthening, not rewrite the canon).

| Gap (flagged by) | v2 disposition |
|------------------|----------------|
| No verdict aggregation rule; two honest reviewers can diverge (Sonnet D2, Kimi, Deepseek #2, Qwen D1, Muse, GLM-Flash F3, GLM C6) | **ADDRESSED** — §33.3 deterministic algebra; §33.4 adjudication; §33.6 derivation shown |
| "Critical obligations" undefined — most exploitable gap (Deepseek #2, Qwen D1, GLM-Flash F2, GLM D7) | **ADDRESSED** — §33.1 derivation rule + applied taxonomy; §38 criticality column |
| BLOCKED not a dimension status (Deepseek #1, GLM-Flash F3.2, Muse D2) | **ADDRESSED** — §0.1 dimension-BLOCKED + §0.4 discipline (v1 already used it informally in §32) |
| BLOCKED as FAIL-shelter, no arbiter/escalation (GLM-Flash F5) | **ADDRESSED** — §0.4(2) BLOCKED-is-not-a-FAIL-shelter + (4) escalation |
| No stopping rules: dimensions/evidence/mutations (Sonnet D3) | **ADDRESSED** — §0.5 closed enumerations; §31 minimum mutation set + strategy |
| No halting condition for the review (Qwen D2) | **ADDRESSED** — §30.3 halting rule + stability window |
| Reviewer diligence unchecked; rubber-stamp invisible (Sonnet D4, GLM-Flash F6, GLM C5) | **ADDRESSED** — §30.1 diligence gate; §0.6(6) empty-register rule; §39.5 concurrency |
| No reviewer independence/attestation (GLM C5/D6, Kimi D10/D11) | **ADDRESSED** — §30.1(1); §39.2 identity; §39.5 friendly-review rule |
| No attack log; held attacks invisible (GLM D8, Deepseek #6/#7, Kimi §30) | **ADDRESSED** — §30.1(2) attack log as mandatory sink |
| Anticipatory hardening vs public attack list (GLM-Flash F6) | **ADDRESSED** — §30.1(3) ≥3 beyond-the-list attacks |
| Reviewer calibration harness / positive control (GLM-Flash F6 flip, GLM C8/D9) | **DECLARED, NOT BUILT** — §30.1(5) + §37 D10 (S2, verdict-visible) |
| Unversioned, no canonical baseline (Deepseek #7, GLM D1) | **ADDRESSED** — frontmatter suite_version + §1.1 baseline block |
| NA vs OUT OF SCOPE undefined (Sonnet D5, GLM D15) | **ADDRESSED** — §0.1 criterion |
| SELF-ASSESSED outside status vocabulary (GLM-Flash F3.1, GLM D3) | **ADDRESSED** — §0.1 gate-state definition (v1's own §29 violation) |
| PARTIAL semantics ambiguous (GLM D16) | **ADDRESSED** — §0.1 status table (remainder must be stated) |
| Evidence-class floor; MODEL-only VERIFIED (Muse D1, GLM-Flash hardening #2, GLM C3/D5) | **ADDRESSED** — §0.3 floor table + §0.6(1) retained |
| Evidence-strength table claim→class (Deepseek #9) | **ADDRESSED** — §0.3 |
| UNIT/PROPERTY + CONFORMANCE overlap (Qwen D4, GLM D12) | **ADDRESSED** — §0.2 disambiguation + §4 instantiation |
| No freshness consequence / verdict expiry (Kimi D6, GLM-Flash F8, GLM C4/D4) | **ADDRESSED** — §0.6(5) + §33.5 + §39.6 triggers |
| No STALE/reopen states (GLM C4) | **ADDRESSED** — §39.1 REOPENED/EXPIRED |
| No review-process state model (Kimi D2, Qwen D6, Muse D3, GLM C4) | **ADDRESSED** — §39 (new) |
| No recovery from wrong verdict (Kimi D10) | **ADDRESSED** — §39.6 |
| Review identity/ownership (Kimi D10/D11, Muse D4) | **ADDRESSED** — §39.2/§39.3 |
| Chain of custody / evidence transport (Kimi D9) | **PARTIAL** — §0.3 locators + §39.6 fraud path; full custody chain is UP (needs universal evidence-provenance class, Qwen D4's META-VERIFICATION) |
| Mutation testing effectively optional (Deepseek #3) | **ADDRESSED** — §31 verdict-visible deferral; §33.3 rules 3/4 |
| Exhaustive verification only "recorded" (Deepseek #3) | **PARTIAL** — §0.7 defines tractable; mandatory-when-tractable is UP (universal §9 wording) |
| "Absence of bypass paths" unverifiable (Deepseek #4) | **ADDRESSED** — §0.3 absence-claim row (negative test + inspection) |
| Forbidden-transition "tested barrier" undefined (Deepseek #5) | **PARTIAL** — §0.7 barrier definition; per-barrier test taxonomy is UP |
| Universality unscoped; no exclusion list (GLM-Flash F1, Kimi D1) | **ADDRESSED** — §26.1 declared exclusion list with re-entry triggers |
| Missing coverage: threat model, capacity, spec quality, migration, composition, deployed identity (GLM-Flash F1) | **ADDRESSED as declared exclusions** — §26.1 (adding dimensions is UP; two partially covered: D3 spec-quality catch, §0.6(5) deployed-identity pinning) |
| Spec-quality gate (GLM-Flash hardening #7) | **UP** — new universal dimension required; D3 shows the suite already catches this class |
| Minimality: duplicated evidence drifts (GLM-Flash F4, Qwen D5, GLM D11) | **ADDRESSED** — §34 cross-reference mechanics |
| Severity scale undefined in registers (GLM D17) | **ADDRESSED** — §37 S1–S4 scale |
| Underclaiming not policed (GLM attack surface) | **ADDRESSED** — §0.6(4) |
| Terms of art undefined (GLM D13) | **ADDRESSED** — §0.7 |
| Meta-lifecycle: checklist consuming its own findings (Qwen D3, Kimi feedback gap) | **PARTIAL** — §40 is the consumption record; a standing revision procedure is UP |
| Applicability decisions reviewed not just declared (Deepseek #10, Kimi) | **ADDRESSED** — §0.1 justification requirement + §30.2(15) attack item |
| Test environment: reproducibility check required (Deepseek #11) | **PARTIAL** — §32 mitigation retained; harness BLOCKED-semantics fix is §37 D8 (code change, out of doc scope) |
| Instrument self-validation (Kimi D7, GLM D9) | **DECLARED** — §37 D10; the Hy4 Preview review itself is the first live validation run |
| Redundant dimension clusters in the canon (Qwen D5, GLM D11) | **UP** — universal-layer consolidation |

### 40.3 Upward flags (Methodology layer — for the orchestrator to file)

These gaps live in `to-file/ASES Universal Conformance Checklist.md`
(2026-08-29) itself and cannot be fixed from an Implementation-layer suite
without weakening/rewriting canon, which §35 forbids. Recommended: one
Methodology-layer issue covering (1) verdict aggregation rule in Checklist
§33, (2) dimension-level BLOCKED in §3, (3) criticality definition, (4)
stopping rules §1/§4/§31, (5) reviewer-diligence + independence in §30,
(6) evidence-provenance class in §4, (7) declared-exclusion requirement in
§26, (8) review-process state model as a universal reflexive obligation,
(9) redundancy consolidation (§1/§3, §24/§30). This suite's §0/§30/§33/§39
mechanisms are written to be lifted into the canon nearly verbatim.

### 40.4 Additional gaps found during synthesis (beyond those flagged)

1. v1 §32 used dimension-level BLOCKED informally while §0 didn't define it
   — internal inconsistency of the exact class the meta-reviews flagged.
2. v1 §37 severities ("Low-Medium") had no scale — fixed with S1–S4.
3. v1's §38 verdict was asserted, not derived — even though v1's own §33
   prose contained enough signal to derive it. Fixed by §33.6 showing the
   derivation.
4. The evidence floor re-audit (§37 D11): all carried-over VERIFIED rows
   meet §0.3 — checked during synthesis, not assumed.
5. The suite's §30 pre-staged list is itself an anticipatory-hardening
   surface for the *Observer's* builder — mitigated by §30.1(3), but a
   reviewer should treat the published list as the minimum, not the menu.
6. v1's §36 claimed "eleven dimensions read PARTIAL" while v1's own §38
   table showed twenty-three — a self-contradiction of the class the
   meta-reviews flagged. Corrected in v2 (§36).

### 40.5 What v2 does NOT claim

- No claim that the aggregation algebra has been exercised by two
  independent reviewers yet — the Hy4 Preview review is its first run.
- No claim that the §39 state model is enforced by tooling — it is
  procedure, recorded in the commissioning issue.
- No claim that the calibration harness exists (§37 D10).
- The seven meta-reviews are INSPECTION-class evidence about the canon;
  this synthesis is likewise INSPECTION-class about v2. Per the suite's own
  §36 principle, v2's conformance claim awaits the adversarial gate.

---

## Appendix — WHAT-NOT-TESTED (claim disclosure per AGENTS.md)

This suite's own claims, with explicit negative-space disclosure:

- **WHY** — issues #523/#527 require a per-dimension conformance
  instantiation as the input to a pedantic adversarial review; honest status
  grading is the deliverable's core value. v2 additionally synthesizes the
  seven meta-reviews (§40) into enforceable mechanisms.
- **WHAT** — every status is grounded in: the design document @3fc3c60a;
  observer.sh and run-tests.sh @68750f28 (line numbers pinned); repo-wide
  greps for Phase 1/2 implementation markers; git history across all
  branches for T28–T33 and the fix lineage; the Universal Checklist and
  VSDD Adaptation Profile texts; the server-memory-management knowledge
  page (2026-08-25 revision, from git); the seven meta-reviews in
  `specifications/Adverarial Test Suite Reviews:.md` (read in full, all
  findings mapped in §40).
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
  6. **(v2)** The §33.3 verdict algebra, §0.3 evidence floor, §0.4 BLOCKED
     discipline, §30.1 diligence gate, and §39 state model are new
     mechanisms with zero runtime history — they have never gated a real
     review. The Hy4 Preview adversarial review is their first exercise;
     treat their behavior under attack as unproven.
  7. **(v2)** The §33.1 criticality assignments are the synthesizer's
     derivation from §26's guarantees — a reviewer may reasonably assign
     differently; disputes route through §33.4 adjudication.
  8. **(v2)** The seven meta-reviews were read and mapped (§40), but no
     reviewer was contacted to confirm interpretation of their findings.
