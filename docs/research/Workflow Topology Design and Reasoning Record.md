---
title: Workflow Topology Design and Reasoning Record
program: EDASES
layer: Research
document_type: Synthesis
status: Active
authority: Experimental
canonical_repository: edases

depends_on:
  - Documentation Standard
  - Concept: Levels of Abstraction
  - Model Agreement Schema (DRAFT)
  - AI Capability Registry Specification
  - docs/ORCHESTRATOR.md

consumed_by:
  - AI Orchestration Guide
  - Model Routing Matrix
  - docs/ORCHESTRATOR.md (role/workflow revisions)
  - .opencode/agents/*.md (role definition revisions)

related_documents:
  - Model Agreement Backfill (DRAFT)
  - Model Feedback Template
  - Model Routing Matrix
  - Research Synthesis: Provenance Deadlock and the Epistemic Architectural Pivot

supersedes: []

last_updated: 2026-08-08
---

> **STATUS NOTE.** This document is the consolidated record of the workflow-topology
> design and the reasoning that produced it, as of the 2026-08-08 operator-directed
> consolidation (issue #254). It synthesizes the finalized design decision posted on
> #241 (2026-08-07 23:43), the four-model first review wave (#242/#247/#248, #243,
> #244, #245), the three-model delta re-review wave (#250, #251, #252), the role-docs
> survey (#246), the draft model-agreement schema/backfill (#241, commit 5c92e9d on
> branch `feature/pp3g-GNXU-model-agreement-addition-to-the-quality-index-task-on`),
> and the reliability-epic context (#156/#154/#232).
> It is a reference record of the actual reasoning — the white-text discussion record,
> not thinking traces. Authority is Experimental: the design is operator-finalized but
> has not yet been canonized into ASES methodology documents. Canonicalization is a
> downstream step.

# Workflow Topology Design and Reasoning Record

## 1. Purpose and Provenance

### 1.1 What this document is

This document records, in one durable place:

1. the **two principles** that govern claims and testing across agent role boundaries
   (reasoning certainty; cheapest-test-first);
2. the **topology finding** — the information-asymmetry boundary as the dominant
   unguarded failure point in role-separated agent systems, and the role-justification
   criterion that follows from it;
3. the **finalized workflow design** derived this session — position-emitting agents,
   a durable store, the cheap staleness trigger, the AUDITOR as a one-role/two-phase
   in-flight divergence verifier, the orchestrator as single integration point, and
   the reviewer as a pre-consumption readiness audit;
4. the **model-agreement collection** design — finding-level agreement, the external
   correctness anchor, non-delivery as a first-class outcome, granular back-fill
   confidence;
5. the **reasoning trail** — the key discussion arcs that shaped the design (auditor
   underuse/re-positioning; no-new-role decision; operator-thinness invariant;
   agreement-as-byproduct; the 504 long-verdict finding).

### 1.2 Why it exists

The operator directed (2026-08-08, #254) that the full design and the actual reasoning
be captured as a durable reference record. The design represents a **complete break
with prior work**: earlier role/workflow thinking placed the auditor as a post-hoc
final project gate (`Plan → Approve → Implement → Review → Audit` per the original
role docs surveyed in #246); the finalized design re-positions the auditor as the
**in-flight divergence verifier** at the information-asymmetry boundary, and re-frames
the workflow around position-emitting agents and a durable store. The reasoning that
produced this break is itself the object of interest (AGENTS.md: "Reasoning Before
Artefacts").

### 1.3 Source material

All sources live on the Crosslink hub:

| Source | Ref | Content |
|---|---|---|
| Finalized synthesis | #241 decision comment (2026-08-07 23:43) | The design shape; reviewer-condition resolutions; open items |
| Model-agreement schema + backfill | #241; commit 5c92e9d | Draft schema, collection process, 7 reconstructed waves |
| First wave r1 | #242 (analysis), #247/#248 (verdict, 4 chunks) | hy3 edge-case/source lens — CONDITIONAL PASS, 12 findings, 8 blocking conditions |
| First wave r2 | #243 | luna durability/systems lens — CONDITIONAL, 6 findings, 4 preconditions |
| First wave r3 | #244 | GLM 5.2 breadth/adversarial lens — CONDITIONAL, 7 findings, 6 counterexamples |
| First wave r4 | #245 | Gemini 3.5 architectural/audit lens — PASS |
| Delta wave r1 | #250 | qwen3.7-plus — AGREE, 4 residual refinement concerns |
| Delta wave r2 | #251 | minimax-m3 — AGREE, 12 findings (2 potentially load-bearing) |
| Delta wave r3 | #252 | kimi-k2.7-code — DISAGREE on one role label; otherwise AGREE |
| Role-docs survey | #246 | Original role definitions, auditor-vs-reviewer, model pins, prior decisions |
| Reliability epic | #156/#154/#232 | Binary-vs-source misattribution that motivated the topology finding |

### 1.4 Evidence conventions

Following AGENTS.md, this record distinguishes observations, interpretations,
findings, and recommendations. Verdicts and findings from the review waves are
reported as **evidence** with their source issue. The design elements are reported as
**operator-finalized decisions**. Open items are explicitly marked as open, not
silently resolved.

---

## 2. Context: the Reliability-Epic Motivation

The topology finding did not emerge from abstract theory. It emerged from the
2026-08-05/06 reliability epic (#156) — specifically the **binary-vs-source
misattribution** that cost the epic an entire investigation chain.

### 2.1 The incident

The durable fork fix for the opencode silent-hang family (#154) was being verified.
An earlier verification agent (nHSI, #209) reported that the built binary "lacks the
bodyIdleTimeout wrapper" while the source "has it" — implying a compiler/build defect
where the binary diverged from the patched source. This claim was decision-gating:
it drove a rebuild (#226), a marker-level matrix verification (#231), and a dedicated
compile-divergence investigation (#232) — a full chain of expensive work.

The actual root cause, established at #232's breakthrough:

- the compiled binary was **byte-faithful** — there was no build defect;
- the #154 silent hang is a **consumption deadlock** in `llm.ts`
  (`effect Stream.fromAsyncIterable` scope finalizer awaits `iter.return()`;
  `ai@6 fullStream return()` rejects/hangs after a stream error);
- the fix was `safeIterable()` fire-and-forget return in `llm.ts` (commit 98dfe4a).

### 2.2 Why this is the motivating example

Two things combined to make the misattribution possible:

1. **Information asymmetry.** The producer (fork builder) could, cheaply, have tested
   whether the *source* hangs identically to the *binary* (run the source directly —
   the E3 parity test that finally proved it). The thin consumer (orchestrator) could
   not cheaply verify "binary is faithful" and had to trust the intermediate claim
   chain.
2. **Cheapest-test obligation absent.** Nobody ran the cheapest discriminating test —
   run the source, compare hang behavior — until the end of the chain. The E3 parity
   test (source `opencode run` hangs identically, exit 124) collapsed the entire
   build-defect hypothesis in minutes.

Related prior evidence in the same family: #226 → #231 marker-grep false assurance
(the marker "discriminated" while the build claim was never actually falsified),
#182 vs #183 confident-and-wrong PASS, #235/#232 claim laundering across hops, #240
brief-borne arithmetic error. These are the hub failure record against which the
topology finding's "dominant" claim must be read.

**Finding (from the record):** decision-gating claims that cross an
information-asymmetry boundary — where the producer can verify cheaply and the thin
consumer cannot — recur in the failure record, and the recurring failure is not the
existence of the boundary but the absence of a cheap verification obligation on the
producer side and of a gate on the consuming side.

---

## 3. The Two Principles

### 3.1 Principle (a): reasoning certainty

**Statement (finalized).** Claims crossing a role boundary must state:

- **WHY** — the reasoning behind the claim;
- **WHAT** — the claim's basis (what it is based on);
- **HOW CERTAIN** — the certainty level (guess / evidence-based / proven);
- **WHAT-NOT-TESTED** — what was explicitly not tested.

The "WHAT-NOT-TESTED" clause is the sharpest element: negative-space disclosure is
the corrective that targets the cheapest class of false-confidence failure. A claim
that states its untested assumptions is checkable by a thin consumer; a claim that
hides them is not.

**Source fidelity (hy3 F1, #248).** The principle is faithful to its in-repo sources
(Core System Prompt v1/v2 reasoning standards; AGENTS.md Evidence section — the
observation/interpretation/finding/recommendation distinction), and the
WHAT-NOT-TESTED clause is a genuine addition beyond those sources.

**Carrier gap (hy3 F2/C6, #248).** The Crosslink comment `--kind` vocabulary is
fixed and closed (note/plan/decision/observation/blocker/resolution/result/handoff/
human) and none of it encodes certainty. Principle (a) therefore currently lives in
unstructured prose — unenforceable, unparseable, and not mechanically consumable by
the model-agreement collection. hy3's blocking condition C6 asks for a certainty
carrier (a kind extension or a mandated fixed prose header). **Open item.**

### 3.2 Principle (b): cheapest-test-first

**Statement (finalized).** Assumptions that gate decisions must be tested with the
quickest cheapest **discriminating** test.

**Source-fidelity caveat (hy3 F1, #248 — HIGH).** The source rule, re-derived
verbatim at `syntheses/2026-06-23-beds24-booking-system-evolution.md:39`, is:

> "Rule #2: Cheapest Falsifying Test First: Before writing complex code, execute the
> absolute cheapest test that can prove the core premise wrong."

The finalized statement says "discriminating" where the source says "falsifying."
hy3 argued (and the record supports) that this is a substantive weakening, not a
paraphrase: a *discriminating* test merely separates two hypotheses, so an agent can
satisfy it with a cheap *confirming* check aimed at the premise it wants to be true.
The hub record contains the exact failure: #226 → #231's marker-grep "discriminated"
(marker present vs absent) while failing to falsify "the build actually works."

**Operator resolution.** The finalized synthesis keeps the principle named
"cheapest-test-first" with the discriminating-test phrasing, while the underlying
obligation is the falsifying-test obligation from source. The reasoning trail (§8)
records the drift finding; the obligation to prefer a *falsifying* test where one
exists should be treated as the load-bearing reading.

**Trilemma (GLM C1, #244).** The cheapest test is usually the one the producer
already ran; if the consumer re-runs it, it is not cheapest. The design resolves this
by placing the *obligation* on the producer (cheapest test that the producer can run
and report) and by making the consumer-side check a *presence/structure* audit rather
than a re-run (the auditor joins position claims against artifact evidence, not
re-execution).

**Regress (GLM C2, #244).** The certainty label is itself a claim crossing the
boundary. The design does not claim to break the regress; it bounds it by requiring
the label plus the WHAT-NOT-TESTED disclosure, which gives the consumer enough to
apply judgement without requiring meta-certainty of the label.

---

## 4. The Topology Finding

### 4.1 Statement (finalized)

> In role-separated agent systems, **decision-gating claims crossing an
> information-asymmetry boundary** — where the producer can verify cheaply and the
> thin consumer cannot — are the **dominant unguarded failure point**.

The corrective is **producer-side calibration** (certainty labeling) plus a
**cheapest-test obligation** (the two principles of §3), enforced at the boundary by
the workflow elements of §5.

### 4.2 The information-asymmetry boundary

The boundary exists wherever a producer emits a claim that a consumer will act on
(the consumer acts on it *because* it is decision-gating), and where:

- the producer can verify the claim cheaply (it built the thing, it has the artifact);
- the thin consumer cannot verify cheaply (edit-deny, read-only, context-scarce,
  or simply downstream of the work).

The failure is not the asymmetry itself — it is the **unguarded** crossing: the
consumer must either trust the claim or invest in expensive re-verification, and
without a cheap-verification obligation on the producer, trust is the default and
misattribution is the recurring outcome (§2).

### 4.3 "Dominant" — scope and honest limits

**hy3 F3 (#248, MEDIUM-HIGH)** — "dominant" is an unsupported quantifier with no
denominator. The hub record supports "a major, recurring class," not dominance as a
measured claim. Three failure classes the topology does **not** cover:

1. **No-claim failures** — the silent hangs (#138/#142). Nothing crosses the
   boundary at all; a producer-side calibration duty cannot fire when there is no
   claim, and a pre-consumption gate never runs. The corrective is **null** on
   precisely the failure mode that emits zero signal. (This is the structural reason
   position-emitting agents + staleness trigger, §5.2, exist.)
2. **Brief-borne errors upstream of the producer** (#240 arithmetic) — the asymmetry
   inverts: the orchestrator authored the error and the producer inherits it as a
   given premise. Producer-side calibration cannot falsify what it was handed as an
   axiom.
3. **Multi-hop laundering** (#235/#232) — a claim that clears hop 1 is re-emitted at
   hop 2 with the audit already marked done, and certainty is monotonically upgraded
   as provenance drops. A single-edge gate cannot bound a multi-hop chain; provenance
   retention across hops is the open corrective.

**GLM F7/C5 (#244)** — the framing is one-directional and inverts at the review edge:
at the review edge the *consumer* (reviewer) can often verify cheaply by reading the
code, while the *producer* (builder) is the one who cannot objectively assess its own
work. So "producer-side calibration" is not the correct corrective at every edge.
**GLM C6 (#244)** — silent-hang/stalled-agent failures are infrastructure telemetry
failures, not decision-gating claim failures; they are captured by the position-store
design (§5.2) rather than by the topology finding itself.

**Finalized reading.** The topology finding is stated as the dominant *class of
decision-gating claim failures* — not as an exclusive failure diagnosis. The workflow
design (§5) covers the topology's blind spots by other means (position store for
no-claim failures; reviewer readiness audit for the review-edge inversion; provenance
for laundering).

### 4.4 Role-justification criterion

The design introduces the following criterion (operator-finalized, recorded here as a
methodological principle of the workflow):

> **A role is justified iff it is a distinct point in capability/authority space AND
> it guards a distinct failure class.**

Two consequences, both load-bearing in the reasoning trail:

- **No duplicate Verifier role** (§7.2): the AUDITOR already occupies the read-only
  verification point; a separate Verifier would duplicate capability/authority
  without guarding a distinct failure class. Hence **ONE role, TWO phases** (§5.4).
- The reviewer remains a distinct role because it guards a *distinct failure class*
  (pre-consumption readiness — is the artifact verifiable before it is consumed)
  rather than the auditor's class (is the work on track as claimed / did outcome and
  process hold up).

---

## 5. The Finalized Workflow Design

### 5.1 Position-emitting agents + durable store + task-adaptive cadence

Every agent working on a task emits **structured position updates** to a **durable
store**:

```
step=<current step>
completed=<what just completed, one line>
next=<what's next>
blocker=<detail or none>
evidence=<link to artifact/evidence>
```

- **Durable store**: the Crosslink hub *is* the store — positions are posted as
  structured comments on the working issue, and they survive agent restarts
  (positions must survive for the AUDITOR to check them after the producer is gone).
- **Task-adaptive cadence**: not a fixed interval — a 5-minute task should not emit 5
  checkpoints. The dispatch spec carries the cadence (or a default policy: every
  state transition + every Nth idle minute + at any blocker). This is the checkpoint
  contract already in the orchestration playbook (§5.4), formalized as a durable,
  structured, queryable stream.
- **What it fixes**: no-claim failures (a silent hang now produces *no* advancing
  position — detectable); temporal drift (a "tests pass" claim at minute 5 that is
  stale by minute 40 is visible as an old position); luna F4's unguarded edges (state
  visibility across the workflow).

**Delta-wave refinements recorded (not yet operator-resolved):**

- #251 B1 — cadence provenance: who sets cadence? (agent can game it; recommend
  orchestrator-set parameter or canonical default policy)
- #251 B2 — position vs status terminology: "position" implies a claim; the
  step/completed/next/blocker shape is status-shaped. The two have different audit
  semantics; the design should name which.
- #251 B3 — evidence-link canonical form (URI with sub-anchor; brittle if free-text)
- #251 B4 — storage form: natural choice is first-class Crosslink artifacts
- #250 r1 — cadence-setting authority should be specified

### 5.2 The cheap staleness trigger

A position/heartbeat that is **stale >2x its expected interval** triggers
investigation. The trigger is cheap (a clock comparison against the durable store),
and it is the *primary* trigger for the AUDITOR (delta-wave reviewers asked for the
trigger set to be enumerated — #250 r1, #251 A1). Logical trigger set:

1. position/heartbeat staleness (>2x expected interval);
2. position-vs-artifact claim mismatch (text claims "tests pass" but no test run in
   the evidence);
3. reviewer disagreement (split verdicts, 1-of-N catches, `disagreed` cells per the
   #241 schema);
4. evidence-accuracy flags from the REVIEWER;
5. orchestrator-explicit request.

### 5.3 AUDITOR as divergence verifier — ONE role, TWO PHASES

**The operator decision.** The AUDITOR is the **in-flight divergence verifier** —
trigger-invoked, read-only, joining position claims against artifact evidence, and
flagging divergence to the ORCHESTRATOR (never acting directly). This is **one role
with two phases**, not two roles:

| Phase | Goal | Question |
|---|---|---|
| **Phase 1 — in-flight monitor** | divergence verification during work | "Is work on track **as claimed**?" |
| **Phase 2 — post-hoc audit** | final project-level audit | "Did outcome **and process** hold up?" |

- **Model variation across phases**: the two phases have different goals, cost
  profiles, and verification depths; they are *not required* to use the same model.
  Phase 1 is trigger-invoked and bounded (cheap structural claim-vs-evidence join);
  Phase 2 is the heavier, rarer final gate. The model for each phase is chosen at
  dispatch per the routing matrix.
- **No duplicate Verifier role** (per the operator decision, responding to kimi
  #252's DISAGREE — see §7.2). The divergence-verifier function is an *activity* of
  the existing AUDITOR role, not a new role.
- **Read-only + flag-only**: the AUDITOR cannot write project files, cannot dispatch,
  cannot act. It flags to the ORCHESTRATOR, which owns the action (investigate /
  nudge / stop-resume per #146) and surfaces only decisions to the operator.

**How this resolves the first-wave conditions:**

- **GLM F1 (STOP B self-audit paradox)** — who performs the pre-consumption result
  check? The AUDITOR, as a separate read-only role: the producer cannot audit its own
  certainty (violates no-self-review); the thin consumer cannot cheaply verify; a
  third, trigger-invoked independent verifier resolves the paradox without a standing
  per-edge dispatch.
- **GLM F2 (unbounded bounce-back)** — the flag-only, escalate-to-orchestrator design
  bounds the loop: the AUDITOR does not bounce work back; it flags, and the
  orchestrator owns the bounded action set (#146 investigate/nudge/stop-resume). The
  orchestrator's action is a decision, not an unbounded re-review loop.
- **luna F1 (STOP B contract)** — the trigger-invoked state machine replaces an
  underspecified prose audit.

**Delta-wave refinements (open):**

- #251 A1/A2 — enumerate the trigger set (done above as the logical set) and specify
  verification *depth* per trigger (cheap structural check first; escalate to
  re-derivation only on structural mismatch).
- #250 r1 — trigger conditions should be explicit.
- #252 (kimi) Finding 1 — the label disagreement, resolved by the operator's
  one-role/two-phase decision; the resolution requires that role docs be updated
  explicitly (see §7.2 and the "redefine, do not imply" rule).

### 5.4 Orchestrator as single integration point

The ORCHESTRATOR is the **single integration point** — the sole agent the operator
deals with. All agent surfaces (positions, AUDITOR flags, reviewer verdicts) flow
through the orchestrator; the orchestrator owns the action set
(investigate/nudge/stop-resume) and **surfaces only decisions** to the operator. The
operator supervises the **orchestrator**, not the swarm.

- **Thin-orchestrator preserved**: bounded flags + queue-based closeout (luna F6
  resolution); the orchestrator never re-reviews full evidence inline — it reads
  structured positions and verdicts, and delegates heavy verification (L2, AUDITOR
  phase 1) to the AUDITOR.
- **Meta-supervision gap (kimi #251 C1 — potentially load-bearing)**: the
  orchestrator now gates every other agent surface; if it misroutes, drops a flag, or
  hangs, no one catches it. Minimum mitigation recorded: the orchestrator itself
  emits a position/heartbeat (delta b applies to the orchestrator too), and a sibling
  agent or the operator can audit flag-triage decisions on a sample basis.
- **SPOF recovery (#251 C2)**: orchestrator state is durable (it owns the issue
  tracker), so a fresh orchestrator can resume from the last known state; the
  resumption contract should be made explicit.
- **Operator-thinness invariant** (§7.3): the operator's bandwidth is the scarcest
  resource; the single-integration-point design exists to protect it.

### 5.5 Reviewer = pre-consumption readiness audit

The REVIEWER is the **pre-consumption readiness audit** — the artifact gate at the
producer-consumer edge (the first wave's STOP B, repositioned).

- **Scope**: verify the artifact is *ready to be consumed*: testability, acceptance
  criteria, evidence presence, certainty labels present, cheapest-test evidence
  present. It is **not** "verify the truth" (a thin consumer cannot); it is "verify
  the artifact admits verification and carries the required calibration."
- **Naming**: the first wave's "L1 cheap" was dropped (GLM F3 — L1/L2/L3 collides
  with the existing local/ci/thorough vocabulary; and an LLM reasoning audit is not
  cheap in the mechanical-verification sense). The final label is **"pre-consumption
  readiness audit"** (kimi #252 Finding 2: readiness, not merely testability; pass
  criteria = WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED stated + cheapest-test evidence
  present).
- **What it fixes**: hy3 F6 (enforcement point for principle 1a — the reviewer checks
  the WHAT-NOT-TESTED disclosure), luna F2 (not every plan needs a post-plan gate —
  the readiness audit applies at pre-consumption, not pre-plan), GLM F6 (the
  principle-to-stop mapping now has an explicit enforcement point).
- **Untestable-claim carve-out (hy3 F8/C2)**: claims that admit no discriminating
  test (absence/negative claims, non-recurrence, timing/latent failures, judgement,
  cross-session durability) must be declared untestable **with stated residual risk**
  — a first-class, non-penalized outcome — rather than forcing a manufactured cheap
  proxy. This is a blocking condition from hy3 (C2) and is recorded as adopted in the
  finalized design.
- **STOP A timing (#251 E1 — potentially load-bearing)**: the first wave had STOP A
  (post-plan testability audit) distinct from STOP B (pre-consumption result audit).
  The finalization's delta (e) collapses them into the reviewer's pre-consumption
  audit; read literally, the cheap early-failure signal (a plan checked at plan-time
  in seconds) is lost. The synthesis should disambiguate whether STOP A is preserved
  on the orchestrator side at dispatch or dropped. **Open item.**

### 5.6 How the workflow elements map to the first-wave conditions

| First-wave condition | Resolution in finalized design |
|---|---|
| GLM F1 — STOP B has no performer (self-audit paradox) | AUDITOR as trigger-invoked, read-only divergence verifier (§5.3) |
| GLM F2 — STOP B bounce-back unbounded | Flag-only + orchestrator-owned bounded action set (§5.3) |
| GLM F3 — L1/L2/L3 vocabulary collision | Use existing local/ci/thorough vocabulary; rename to "pre-consumption readiness audit" (§5.5) |
| GLM F4 — workflow-shape coverage (sentinel/swarm/orchestrator edge) | Position store + staleness trigger covers no-claim/temporal drift; orchestrator single integration point covers orchestrator-as-consumer (§5.1, §5.2, §5.4) |
| GLM F5 — "zero-cost byproduct" overstates model-agreement cost | Honest framing: low-incremental-cost with classification tax (§6.5) |
| GLM F6 — principle 1a has no enforcement point | Reviewer readiness audit checks WHAT-NOT-TESTED disclosure (§5.5) |
| GLM F7 — asymmetry inversion at review edge | Reviewer = consumer-side readiness audit; producer-side calibration applies at other edges (§4.3, §5.5) |
| GLM C1/C2 — trilemma/regress | Producer-side obligation + presence/structure audit; bounded regress via WHAT-NOT-TESTED (§3.2) |
| GLM C3 — STOP A penalizes legitimately-expensive-to-test plans | Untestable-claim carve-out with stated residual risk, non-penalized (§5.5) |
| GLM C4 — model-agreement prerequisite unmet (schema DRAFT) | Agreement collection proceeds non-gating; draft status recorded; back-fill confidence granular (§6) |
| GLM C5 — contamination is reverse asymmetry | Recorded as a distinct failure class; position store gives visibility (§4.3) |
| GLM C6 — silent hangs outside framing | Position store + staleness trigger capture no-claim failures (§5.1, §5.2) |
| luna F1 — STOP B contract underspecified | Trigger-invoked state machine (§5.3) |
| luna F2 — STOP A shouldn't gate every plan | Readiness audit at pre-consumption, not pre-plan (§5.5) |
| luna F3 — "high stakes" needs policy | STOP C scoped as targeted L2 re-verification for high-stakes decisions (install/merge); policy definition open |
| luna F4 — unguarded edges | Position store + single integration point + operator-supervises-orchestrator (§5.1, §5.4) |
| luna F5 — agreement lifecycle incomplete | External correctness anchor + non-delivery + granular back-fill confidence (§6) |
| luna F6 — thin-orchestrator preservation not demonstrated | Bounded flags + queue-based closeout; orchestrator never re-reviews inline (§5.4) |
| hy3 C1 — restore "falsifying" | Recorded as the load-bearing reading of principle (b) (§3.2) |
| hy3 C2 — untestable-claim carve-out | Adopted (§5.5) |
| hy3 C3 — drop unqualified "dominant"; scope out no-claim/brief-borne; hop guard | Scope limits recorded (§4.3); hop guard open |
| hy3 C4 — reconcile three permission layers | Open item (implementation prerequisite) |
| hy3 C5 — STOP C needs an executable substrate before "L2" | Open item (substrate prerequisite) |
| hy3 C6 — certainty carrier | Open item (§3.1) |
| hy3 C7 — amend kickoff template; bound STOP B retry | Position/checkpoint contract formalized; retry bounded via orchestrator action set (§5.1, §5.3) |
| hy3 C8 — non-delivery + external anchor | Adopted (§6.3, §6.4) |

---

## 6. Model-Agreement Collection

### 6.1 Finding-level agreement (the load-bearing dimension)

Agreement is recorded per **finding/claim class**, not merely per verdict. Verdict-level
agreement masks divergence — the motivating example is #154 round 1: all three
reviewers returned CONDITIONAL (verdict-level consensus) while hy3 *disagreed* with
luna+big-pickle on the core issue (B2, deadline shape). Similarly B1 was a 1-of-3
catch: a 2-of-3 consensus would have agreed on the wrong answer.

The schema (draft, #241 / commit 5c92e9d) defines a fixed claim-class taxonomy
(C1–C10), a normalized verdict vocabulary (PASS/CONDITIONAL/FAIL), per-claim values
(`found` / `not-found` / `disagreed` — `disagreed` being the highest-signal cell: the
model *saw* the claim and rejected it, distinct from merely missing it), and agreement
labels (multi-model catch / 1-of-N catch / consensus miss / disagreement).

### 6.2 Collection process (non-gating)

Agreement is recorded **inside the existing orchestrator closeout synthesis** comment
on the wave parent — structuring work the orchestrator already performs, never
gating dispatch/re-review/synthesis. Missing verdicts are marked, not waited on.

### 6.3 External correctness anchor (hy3 F11 — adopted)

Agreement is **not a truth proxy**. The deep design risk in agreement collection is a
conformity loop: agreement data is collected by the same orchestrator-plus-model
population it measures, and feeding it into the routing matrix can reward
conformity (models that agree with the synthesiser get routed more, agreement rises).
The record already contains confident-and-wrong agreement (#182/#183). The corrective,
adopted into the finalized design: record an **external correctness anchor** —
*"did the finding later hold up"* — separately from agreement. The anchor is
external to the agreement instrument (test results, later implementation outcome,
independent re-derivation).

Delta-wave refinement (#251 D1, open): the anchor's provenance per claim class is
unspecified ("tests pass" anchors to the test runner; "type-safe" to the type
checker; "principle-followed" to a structural observation — each has a different
anchor). #251 D3 (open): anchor and agreement are orthogonal primitives (verification
vs confidence) and should be recorded as separate columns, not collapsed.

### 6.4 Non-delivery as a first-class outcome (hy3 F12 — adopted)

A review whose verdict never lands produces no row under the naive schema — the
dataset silently over-represents completed reviews and under-represents long,
complex, high-finding-count ones (survivorship bias). **Non-delivery** (verdict lost /
agent died / timed out / 504) is therefore a **first-class recorded outcome**,
distinct from "no findings." The 504 long-verdict finding (§7.5) is the in-repo
demonstration: hy3's own verdict was lost to a 504 twice.

Delta-wave refinement (#251 D2/D4, open): non-delivery categories are different
signals (504 = server-side/harness; hang = client-side/agent; timeout = policy;
refused = auth; broken = mid-task crash; truncated = partial) and the
agent-vs-harness source distinction matters for response (re-dispatch vs page the
harness operator).

### 6.5 Zero-cost byproduct, framed honestly

The operator's original framing (#241): agreement data is a **zero-cost byproduct** of
the standing multi-model adversarial-review workflow — the reviews already happen;
recording agreement is structuring existing work, not new work.

**Honest framing (hy3 F10 + GLM F5, adopted):** "zero-cost" is true at **verdict
level** (the orchestrator already sees all verdicts at synthesis). It is **not** true
at finding level: mapping each reviewer's free-text findings into the fixed C1–C10
taxonomy and distinguishing `disagreed` from `not-found` is real classification +
interpretation work (a "classification tax"), and it either loads the thin
orchestrator or requires a designated recorder (a hidden agent dispatch under the
naive reading). The finalized design records agreement as **low-incremental-cost by
product** (no new review-wave dispatches) with the classification tax acknowledged,
and keeps collection non-gating so it cannot silently skip under load.

### 6.6 Granular back-fill confidence

Historical waves reconstructed from the hub (#136/#137, #150–#153, #154 rounds,
#196, pre-session gemini-3.1-pro/north-mini-code) are marked
`collection: reconstructed` / lower confidence — reconstructions, not standardized
collection. Confidence is granular (per row/finding, not one wave-level label),
per luna F5's requirement that historical and live rows not be silently comparable.

---

## 7. The Review Wave Record

### 7.1 First wave (#242–#245, four lenses on the original proposal)

| Reviewer | Lens | Verdict | Highlights |
|---|---|---|---|
| hy3 (#242/#247/#248) | Edge-case/source | **CONDITIONAL PASS** | 12 findings (F1–F12), 8 blocking conditions (C1–C8). F1: falsifying→discriminating drift. F3: "dominant" unsupported; no-claim/brief-borne/multi-hop blind spots. F8: untestable claims unhandled. F11: conformity loop → external anchor. F12: survivorship bias → non-delivery. Verdict itself was lost to a 504 twice, then chunked (#7.5). |
| luna (#243) | Durability/systems | **CONDITIONAL** | STOP B contract underspecified (MUST FIX); STOP A should not gate every plan; STOP C needs policy + fallback; unguarded edges (operator→orchestrator, cross-workflow, stale reads, hangs); agreement lifecycle incomplete; thin-orchestrator preservation plausible not demonstrated. 4 preconditions for PASS. |
| GLM 5.2 (#244) | Breadth/adversarial | **CONDITIONAL** | 7 findings (2 CRITICAL: STOP B no performer/self-audit paradox; bounce-back unbounded) + 6 adversarial counterexamples (trilemma, regress, STOP A penalizes expensive plans, schema prerequisite unmet, contamination reverse-asymmetry, silent hangs outside framing). 8 hardening items. |
| Gemini 3.5 (#245) | Architectural/audit | **PASS** | Internal consistency EXCELLENT; layering respect EXCELLENT; thin-operator/thin-orchestrator preserved; abstraction level correct; bureaucracy risk LOW with mitigations (structured metadata; discriminating test defined mechanically; automated calibration audits). |

First-wave outcome: directionally correct (topology finding novel and real; principles
adoptable) but operationally incomplete. The finalized synthesis on #241 (23:43)
resolved the condition set into the design recorded in §5.

### 7.2 Delta wave (#250–#252, fresh reviewers on the finalized design)

| Reviewer | Verdict | Content |
|---|---|---|
| qwen3.7-plus (#250) | **AGREE** | All 5 deltas correct. 4 residual refinement concerns: auditor trigger conditions explicit; cadence-setting authority; orchestrator→operator edge acknowledged as unguarded boundary condition; external anchor's own certainty. |
| minimax-m3 (#251) | **AGREE** (12 findings) | All deltas right shape. 2 potentially load-bearing: C1 (orchestrator meta-supervision gap) and E1 (post-plan cheap test timing / STOP A preservation). 10 granularity findings (A1–A2 triggers/depth; B1–B4 cadence/semantics/evidence-link/storage; C2–C3 SPOF/scope; D1–D4 anchor provenance/non-delivery taxonomy/anchor-vs-agreement separation/agent-vs-harness source; E2–E3 testability methodology/consumer definition). |
| kimi-k2.7-code (#252) | **DISAGREE on one delta** | Auditor-as-divergence-verifier label violates the original auditor role (project-level final gate) and abstraction boundaries; suggested a distinct Verifier/Watcher. Otherwise AGREE. Finding 2 (clarification): rename reviewer gate to "pre-consumption readiness audit" with pass criteria. |

**Operator resolution of the #252 disagreement — the no-new-role decision** (§7.2 of
this record): the AUDITOR keeps the divergence-verifier function, **one role, two
phases** — no duplicate Verifier role. The role is *redefined explicitly* (the kimi
principle: "if the project intentionally redefines Auditor, update the role docs
explicitly; do not let the change happen by implication"). The role-justification
criterion (§4.4) is the supporting argument: a Verifier would duplicate the auditor's
read-only verification point without guarding a distinct failure class.

---

## 8. The Reasoning Trail — Key Discussion Arcs

This section preserves the *actual reasoning* — the discussion arcs that shaped the
design. Each arc records the question, the evidence brought to bear, the argument
that carried, and the decision.

### 8.1 Arc 1: why the auditor was underused and re-positioned

**Question.** The AUDITOR role existed — defined from the start as the project-level
final gate, explicitly distinct from the line-level reviewer ("You do not implement.
You do not review code line-by-line (that's the Reviewer). You evaluate the outcome
and the process" — original tripn-astro auditor.md, per #246) — but it figures little
in recent workflow discussions. The role set was designed around it; the operational
load has been reviewer-driven (#127 allowlist reviews, #136/#137 watcher reviews,
model-feedback docs mostly "reviewer role"). Why was it underused, and what should it
become?

**Evidence.** #246 survey: (a) original four roles with static pins — Orchestrator=
Nemotron 3 Ultra, Builder=HY3, Reviewer=North Mini Code, Auditor=Gemini 3.1 Pro
(Tools repo 9fede33, 2026-07-15; ASES port 09dc0eaa, 2026-07-30; orchestrator added
ba3dabc5, 2026-08-03 per #121); (b) the auditor was the *final* gate in the documented
order Plan → Approve → Implement → Review → Audit; (c) no doc supersedes or removes
it. The GLM first-wave review then made the *self-audit paradox* load-bearing: the
proposed pre-consumption result check needed a performer, and all three options
(producer self-audit / separate auditor / thin consumer) failed — producer self-audit
violates no-self-review, a standing auditor dispatch is not cheap, and the thin
consumer cannot verify.

**Argument that carried.** The auditor's underuse was a *positioning* failure, not a
capability failure. Its documented independence (independent of implementation AND
review) is exactly the property a divergence verifier needs. Re-positioning the
existing role as the **trigger-invoked in-flight verifier** solves GLM F1 (defined
performer), preserves independence, and converts an idle final gate into the
workflow's active control surface — without adding a role.

**Decision.** AUDITOR = divergence verifier, one role, two phases (§5.3).

### 8.2 Arc 2: why no new role (the no-new-role decision)

**Question.** kimi (#252) argued the divergence-verifier function violates the
auditor's original role (a live operational watchdog vs a post-hoc project audit) and
suggested a distinct **Verifier** or **Watcher** role.

**Evidence.** The original role definitions (#246): the auditor is "independent of
implementation and review" and the original text drew the reviewer boundary
explicitly. The abstraction hierarchy (Concept: Levels of Abstraction) puts real-time
state monitoring at the Architecture/Implementation layer, and the auditor at a
Methodology-layer oversight position — supporting kimi's separation instinct.

**Counter-argument that carried.** Adding a Verifier duplicates the read-only
verification point (capability/authority) that the auditor already occupies, and the
failure class a Verifier would guard (in-flight claim-vs-evidence divergence) is the
same class the re-positioned auditor guards. The role-justification criterion
(§4.4) therefore rejects the new role. The kimi concern is honored differently: the
*redefinition* is made explicit — role docs, permission matrix, and abstraction notes
must be updated explicitly (the "redefine, do not imply" rule) rather than allowing
the change by implication.

**Decision.** ONE role, TWO phases; no duplicate Verifier role. Model variation across
phases gives the design the flexibility kimi wanted from a separate role without the
role proliferation.

### 8.3 Arc 3: the operator-thinness invariant

**Question.** How much can the operator's attention be stretched before the system
becomes unmanageable?

**Evidence.** Thin-operator was an existing design goal (playbook §1: the operator "is
never handed code to read/write"; #245: the proposal "spares the human operator from
manual verification"). The first wave flagged the operator→orchestrator edge as an
unguarded boundary (luna F4; GLM F4: orchestrator→operator summary is a
decision-gating claim crossing the largest asymmetry boundary in the system).

**Argument that carried.** Operator bandwidth is the scarcest resource; the correct
shape is a **hierarchy of thinness**: agents emit positions → orchestrator consumes
structured signals and owns actions → orchestrator surfaces **only decisions** to the
operator → operator supervises the orchestrator (not the swarm). The orchestrator
absorbs agent noise; the operator gets decisions. The residual orchestrator→operator
edge is acknowledged as an unguarded boundary condition (qwen #250) and is accepted:
the operator is human and can apply judgement; the design states the boundary rather
than pretending to close it.

**Decision.** Orchestrator = single integration point; operator supervises
orchestrator (§5.4).

### 8.4 Arc 4: agreement-as-byproduct insight

**Question.** Where does agreement data come from, and at what cost?

**Evidence.** The natural experiment was already in play (#241): adversarial-review
workflows require multiple review models on the same brief, so agreement data is a
zero-cost byproduct of the standing process. The first wave then stress-tested
"zero-cost": GLM F5 (taxonomy mapping is classification + interpretation, not
reformatting; recorder-role requirement; routing on incomplete data), hy3 F10
(verdict-level yes, finding-level no).

**Argument that carried.** The byproduct insight is correct and load-bearing, but only
at verdict level; finding-level collection carries a real classification tax. The
design keeps the byproduct framing honest ("low-incremental-cost") and the collection
non-gating, and makes finding-level agreement the load-bearing dimension anyway
because verdict-level masks divergence (#154 R1 B2).

**Decision.** Collection inside closeout synthesis, non-gating, honest cost framing,
finding-level load-bearing (§6).

### 8.5 Arc 5: the 504 long-verdict finding

**Question.** Why did the hy3 verdict keep disappearing, and what does it reveal?

**Evidence.** hy3's workflow-topology verdict was lost to a **504 streaming error
twice** (#242 → re-dispatch #247 → re-dispatch 2 #248). Long verdict text exceeds the
streaming idle limit. The fix that worked: **chunked posting** — 2–4 comments of
~1–2 KB each ("VERDICT PART 1/4" … "4/4"). The preserved [VERIFY]/[PROGRESS]
checkpoints carried the analysis through the losses.

**Implication for the design.** This is the in-repo demonstration of survivorship
bias in agreement collection (hy3 F12): a review whose verdict never lands produces
no row, silently over-representing completed reviews. It motivated **non-delivery as
a first-class recorded outcome** (§6.4) — distinct from "no findings" — and the
504-loss pattern was explicitly recorded to feed the model-agreement index (#156
action log: "504-loss pattern recorded: hy3 long-verdicts exceed streaming idle limit
— will feed model-agreement index").

**Decision.** Non-delivery as first-class outcome; chunked posting as a practical
mitigation; 504-loss pattern recorded as evidence for the agreement registry.

---

## 9. Open Items and Not-Yet-Resolved

Explicitly open (from the delta wave and first-wave conditions), so the record does
not silently resolve them:

1. **Certainty carrier** (hy3 C6): the comment `--kind` vocabulary encodes no
   certainty; needs a carrier (kind extension or mandated prose header) for
   principle (a) to be mechanical. (§3.1)
2. **STOP A timing** (#251 E1): is the post-plan cheap test preserved on the
   orchestrator side at dispatch, or dropped? (§5.5)
3. **Orchestrator meta-supervision** (#251 C1): the orchestrator's own heartbeat +
   sampled audit of its flag triage. (§5.4)
4. **Trigger set + verification depth** (#251 A1/A2): enumerated as a logical set in
   §5.2 but not yet canonicalized; depth per trigger unspecified. (§5.3)
5. **Cadence provenance + position-vs-status semantics + evidence-link canonical
   form + storage form** (#251 B1–B4). (§5.1)
6. **External anchor provenance per claim class; anchor-vs-agreement separate
   columns; non-delivery taxonomy; agent-vs-harness source** (#251 D1–D4). (§6)
7. **Multi-hop laundering guard** (hy3 C3): provenance retention across hops. (§4.3)
8. **Permission-layer reconciliation** (hy3 C4): hook-config / .opencode/agents/*.md /
   permissions.md currently drift in both directions; STOP B/C cannot be costed
   against effective capability until reconciled. (§5.6)
9. **STOP C substrate** (hy3 C5): agent_test_commands unset, shellcheck not installed;
   "L2 re-verification" has no executable substrate in this repo. (§5.6)
10. **Role-doc updates**: per the kimi "redefine, do not imply" rule, the auditor's
    redefinition must be written into .opencode/agents/auditor.md, permissions.md,
    and docs/ORCHESTRATOR.md explicitly. (§8.2)

---

## 10. Evidence Base

- #241 — finalized synthesis (decision comment, 2026-08-07 23:43); model-agreement
  draft schema + backfill (commit 5c92e9d, branch
  `feature/pp3g-GNXU-model-agreement-addition-to-the-quality-index-task-on`)
- #242/#247/#248 — hy3 first-wave review (analysis + 4-chunk verdict; 12 findings,
  8 blocking conditions)
- #243 — luna first-wave review (6 findings, 4 preconditions)
- #244 — GLM 5.2 first-wave review (7 findings, 6 counterexamples, 8 hardening items)
- #245 — Gemini 3.5 first-wave review (PASS)
- #246 — role-docs read-only survey (original role definitions, model pins,
  auditor-vs-reviewer, prior role-design decisions)
- #250 — qwen3.7-plus delta re-review (AGREE, 4 refinements)
- #251 — minimax-m3 delta re-review (AGREE, 12 findings, 2 load-bearing)
- #252 — kimi-k2.7-code delta re-review (DISAGREE on auditor label; readiness-audit
  rename)
- #156/#154/#232 — reliability epic; durable fork fix; binary-vs-source
  misattribution and E3 parity breakthrough
- syntheses/2026-06-23-beds24-booking-system-evolution.md — source of Rule #2
  (Cheapest Falsifying Test First)
- Core System Prompt v1/v2; AGENTS.md (Evidence section) — sources of the
  reasoning-certainty principle
- docs/ORCHESTRATOR.md, .opencode/permissions.md, .opencode/agents/*.md — role
  contract and permission matrix
- capability-mapping/Model-Routing-Matrix.md — routing matrix (MODEL-AGREEMENT
  dimension added as DRAFT in commit 5c92e9d)
