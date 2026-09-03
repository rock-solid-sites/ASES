# Adversarial Review — Experiment A Tooling & Context-Efficiency v2

**Reviewer:** ling-3.0-flash-fin-free — substitution disclosed
**Document:** `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2, 2026-09-03)
**Date:** 2026-09-03
**Source:** Independent zero-context adversarial review — Experiment A v2
**Verdict:** NEEDS REVISION — excellent scaffolding, missing measurement contract

> **Model substitution note:** Requested `opencode/ling-3.0-flash-free` not in catalog (66 models listed, 2026-09-03). Used closest available `ling-3.0-flash-fin-free`. Disclosure per review protocol. Behavior expected to be near-identical for review task; no advantage conferred.

---

## 1. Strengths (Independent — Convergent With Other Reviewers)

**S1 — Correct causal isolation `2:27-51` + `21:721-737`.** "One agent, one model, one task, one role" plus deferral of Sol/orchestrator/routing to Experiment B is right identification. Prevents layer contamination.

**S2 — A/B/C taxonomy `3:57-93`.** Avoid / Retrieve higher-density / Compress retained correctly deconfounds RTK, Serena, summarization. `not competing versions of the same thing` `3:91-93` is the key correction.

**S3 — Gated metric `1:21-23` + `16:556-565` + `19:646-664`.** `tokens-to-verified-success` with correctness hard gate, plus `Never treat RTK's own savings counter as result` `5:165`, implements anti-Goodhart measurement.

**S4 — Compensatory measurement `5:149-162`.** Pre-registers "less output → follow-up command → extra turn" as outcome, not anecdote.

**S5 — R1-R4 economics stratification `6:177-254`.** Task-dependent hypothesis ("lexical dominates localization" `6:195`) falsifiable, not assumed.

**S6 — R5 adaptive and R6 stopping `7:258-327` isolated.** Tests avoidance independent of technology — more valuable than tool bake-off.

**S7 — Simple deterministic C2/C3 first `11:410-424`.** Establishes sufficiency of less context before optimizing summarizer representation.

**S8 — Interaction taxonomy + adversarial classes `12:451-471` `14:516-522` `15:527-551`.** Additive/Redundant/Compensatory/Synergistic plus misleading matches / generated files / stale results prevents trivial-task Goodharting.

**Overall:** Decomposition and sequencing `22:742-776` are research-grade (A-). Operationalization is underspecified (D).

---

## 2. Threats To Validity

### 2.1 Internal

| # | Threat | Location |
|---|--------|----------|
| I1 | Hold-constant contradiction: `model settings fixed` vs `dynamic-models` active | `2:37-38` vs `2:43-47` |
| I2 | T0 ≡ T2 ambiguity (normal workflow already has rtk-guard) | `4:96-120` vs `5:129-136` |
| I3 | No repo reset, no randomization, no cache invalidation (Serena, FS) | `13:473-491` |
| I4 | Stochasticity unpinned (temp/seed/top_p/version) | `13:487-489` |
| I5 | Guard prompt injection unmeasured | `2:41-48` |
| I6 | R5 conflates tool vs classifier accuracy | `7:262-286` |

### 2.2 Construct

| # | Threat | Location |
|---|--------|----------|
| C1 | `verified` gate qualitative, no per-task oracle, no numeric non-inferiority | `16:590-595` `19:646-664` |
| C2 | `useful/relevant/duplicate` requires rubric/blinding/IRR/tokenizer | `9:330-361` `16:573-585` |
| C3 | Token accounting: system/guard/raw-vs-compressed/reasoning, measurement point undefined | `4:101-119` `16:566-572` |
| C4 | R6b self-judged sufficiency circular | `8:302-315` |
| C5 | C2 field list folk, not versioned schema | `10:375-398` |

### 2.3 Statistical

* **S1** No N/power/MDE (`multiple times where practical` `13:475`).
* **S2** No alpha/ROPE/correction; multiplicity across interactions×classes → inflated false positives.
* **S3** Mean for heavy-tailed tokens `13:481` without primary median/nonparametric pre-registration.
* **S4** No stopping rule (interim peeking).

### 2.4 External

* Single repo/model, `SessionRunCoordinator` illustrative examples `6:182-184` not executable tasks. Generalization to "software-engineering work" `1:11` unsupported until suite instantiated.

---

## 3. Missing / Underspecified (Blocking)

| # | Location | Gap |
|---|----------|-----|
| M1 | `16:590-595` `19:646-656` | Verified-success oracle + margin |
| M2 | `14:494-523` | Concrete task suite (≥18, ground truth, oracle, holdout) |
| M3 | `13:473-491` | N / randomization / SAP |
| M4 | `4:101-118` `16:566-588` | Token instrumentation at API boundary |
| M5 | `7:262-324` `10:375-404` | R5/R6/C2 enforcement (who judges, when checkpoint, compactor version) |
| M6 | `5:129-147` | Tool freeze (RTK rules, Serena, rg, model) |
| M7 | `12:440-450` | Interaction adaptive bound |
| M8 | `15:527-550` | Failure injection protocol |
| M9 | data | Logging schema (raw vs compressed vs follow-up) |

---

## 4. Prioritized Improvements

### MUST-FIX

**MF1 — Verified-success oracle + margin (M1/C1).**
Per-task script: tests+lint+typecheck+gold diff + blinded audit; margin 5% absolute (Wilson). **WHY:** tokens meaningless otherwise. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** oracle gaming. **Cheapest test (1 hr):** 2 pilot oracles, 2 raters, κ>0.8.

**MF2 — Task bank (M2).**
≥3 per class A-F, commit pin, scope, ground truth, oracle, T0 difficulty pilot, 2 holdout. **WHY:** cannot randomize abstract classes. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** cross-repo. **Cheapest test (2 hr):** 6 tasks ×3 runs T0.

**MF3 — N / randomization / analysis (M3/S1-S3).**
N=10 primary, N=5 interactions; Latin square; seed pin; primary bootstrap 95% CI on `mean(tokens)/success_rate`; win iff CI excludes ±10% ROPE + non-inferior correctness; Holm. **WHY:** "where practical" → p-hacking. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** drift. **Cheapest test (30 min):** pilot variance → power for 20%.

**MF4 — Token instrumentation at API (M4/C3).**
Σ(system+user+tool_post_filter+assistant) per API call; raw vs compressed; guard separated; per-run JSON. **WHY:** shell vs model boundary diverges. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** embedding. **Cheapest test (1 hr):** T0 guard vs API delta.

**MF5 — External enforcement (M5/C4-C5).**
R5 logged classification; R6 external checklist; C2 deterministic checkpoint (every 5 tools) with versioned JSON schema, script-authored, cost separately reported. **WHY:** avoids tautology/hidden labor. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** checklist gaps (E/F tests). **Cheapest test (1 hr):** checklist pilot on R2.

### SHOULD-FIX

* Repo/guard reset & pin (SF1); density rubric+IRR (SF2); dual denominator (SF3); adaptive interaction bound (SF4); failure injection scored (SF5).

### CONSIDER

Temp 0, dollar cost, wall-time/guard covariates, adverse stopping.

---

## 5. Verdict

**NEEDS REVISION — not executable.**

Philosophy excellent; instrumentation sketch. 1–2 days to close MF1-MF5 + 6-task pilot → runnable. Preserve central principle `22:779` verbatim.

**Risk if run now:** anecdotal, non-replicable, selection-biased, illusory RTK/Serena wins, variance-dominated.
