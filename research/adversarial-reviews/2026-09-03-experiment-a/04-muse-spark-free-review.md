# Adversarial Review — Experiment A Tooling & Context-Efficiency v2

**Reviewer:** muse-spark-1.3-free, zero-context, independent, read-only
**Document:** `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2, 2026-09-03)
**Date:** 2026-09-03
**Source:** Independent zero-context adversarial review — Experiment A v2
**Verdict:** NEEDS REVISION — strong decomposition, missing operational contract

---

## 1. Strengths (Independently Observed)

**S1 — Narrow causal isolation `2:27-51` + `21:721-737`.** "One agent, one model, one task, one role; change tooling/context only" plus explicit Experiment B deferral is correct identification strategy. Directly prevents Sol/orchestrator routing contamination.

**S2 — Three-mechanism decomposition `3:56-93`.** Avoid (A) / Retrieve higher-density (B) / Compress retained (C) correctly separates RTK vs Serena vs summarization. Statement `RTK, Serena and context summarization are not competing versions of the same thing` `3:91-93` is the strongest sentence in the document.

**S3 — tokens-to-verified-success as gated primary metric `1:21-23`, `16:556-565`, `19:646-656`.** Anti-Goodhart design `5:165` ("Never treat RTK's own savings counter as result") is essential. Most context papers optimize proxy compression ratios without recovery cost.

**S4 — Compensatory behavior measurement `5:149-162`.** Explicitly anticipates "less output → extra command → extra turn" erasing savings. Rare to see this pre-registered.

**S5 — Task-conditional retrieval hypotheses R1-R4 `6:177-254`.** "Lexical should dominate" for localization is stated as hypothesis not assumption `6:195-201`; testable stratification.

**S6 — R5 adaptive + R6 stopping `7:258-327` as independent factors.** Isolates "avoid" from "density" before testing interactions — correct factorial logic.

**S7 — C2/C3 deliberate simplicity `11:410-424`.** Deterministic compact state before vector DBs / learned summarizers. Tests "is less sufficient?" before representation optimization.

**S8 — Interaction taxonomy `12:451-471` + failure classes `14:516-522` / `15:527-551`.** Additive/Redundant/Compensatory/Synergistic plus adversarial tasks (misleading matches, generated files, stale results) prevents trivial-task overfitting.

---

## 2. Threats To Validity

### 2.1 Internal

* **I1 — Hold-constant vs infrastructure contradiction `2:37-38` vs `2:43-47`.** `dynamic-models` active while `model settings` "remain fixed" is contradictory without explicit disable/pin.
* **I2 — Baseline duplication `4:96-120` vs `5:129-135`.** T0 ("normal workflow" includes rtk-guard) is indistinguishable from T2 (RTK ON) unless T0 definition is repaired.
* **I3 — No reset / no randomization `13:473-491`.** Sequential phases, no `git worktree` reset, no Latin square, no cache invalidation (Serena index, filesystem). Carryover confounds treatment.
* **I4 — Stochasticity uncontrolled.** No temperature/seed/top_p/model version pin. Even at temp 0, provider-side nondeterminism unmeasured.
* **I5 — R5 classifier conflation `7:262-286`.** Tool power confounded with "lexical vs relationship" classification accuracy.
* **I6 — Guard token injection `2:41-48`.** Guard stack tokens and steering not measured as covariate.

### 2.2 Construct

* **C1 — Verification gate undefined `16:590-595` / `19:646-664`.** No per-task oracle (tests/lint/typecheck/gold diff/audit) and no non-inferiority threshold (`unacceptable` is qualitative).
* **C2 — Useful/relevant subjective `9:330-361` / `16:573-585`.** No rubric, no blinding, no IRR, no tokenizer definition.
* **C3 — Token accounting ambiguous `4:101-119` / `16:566-572`.** System/guard/raw-vs-compressed/reasoning inclusion, measurement point (guard vs API), not specified.
* **C4 — Sufficiency circular `8:302-315`.** Self-judged proposition/evidence/confidence without external oracle.
* **C5 — C2 schema folk `10:375-398`.** Informal field list, not JSON schema, not versioned.

### 2.3 Statistical

* **S1 — No N/power/MDE.** `multiple times where practical` `13:475` not a specification.
* **S2 — No alpha/ROPE/correction.** Multiple comparisons across interactions × task classes with no family-wise control.
* **S3 — Distributional naïveté.** Mean `13:481` reported for heavy-tailed tokens without pre-specifying median/log-transform/nonparametric test.
* **S4 — No stopping rule.** Interim peeking permitted.

### 2.4 External

* Single repo/model, placeholder `SessionRunCoordinator` examples `6:182-184` not executable tasks. Claim `21:735` of becoming Experiment B baseline overstates generalizability.

---

## 3. Missing / Underspecified Decisions (Blocking)

1. **M1 — Verified-success oracle + non-inferiority margin** `16:590-595` `19:646-656`
2. **M2 — Concrete task suite** `14:494-523` (≥18 tasks, ground truth, oracle, difficulty, holdout)
3. **M3 — N / randomization / statistical analysis plan** `13:473-491` `16:556-595`
4. **M4 — Token instrumentation at model boundary** `4:101-118` `16:566-588`
5. **M5 — R5/R6/C2 enforcement (who judges/routes/compacts, checkpoint rule, compactor version)** `7:262-324` `10:375-404`
6. **M6 — Tool version freeze** `5:129-147` (RTK rules, Serena/LSP, rg flags, model pin)
7. **M7 — Interaction adaptive bounding** `12:440-450` (avoid obligatory 2⁴ factorial)
8. **M8 — Failure injection protocol** `15:527-550` (base rate, blinding, scoring)
9. **M9 — Data dictionary / durable logging** `16:598-613`

---

## 4. Prioritized Improvements

### MUST-FIX

**MF1 — Operationalize verified-success.**
Per-task verification script (tests + lint + typecheck + gold diff) + blinded audit; non-inferiority margin 5% absolute (Wilson CI). **WHY:** otherwise token comparison meaningless. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** oracle gameability. **Cheapest test (1 hr):** 2 pilot oracles, two raters, κ target 0.8.

**MF2 — Instantiate task bank.**
≥3 per class A-F, commit pin, file scope, ground truth, oracle, difficulty pilot, 2 holdout. **WHY:** abstract classes not runnable. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** cross-repo. **Cheapest test (2 hr):** 1×6 pilot, 3 runs each on T0.

**MF3 — Pre-register N / randomization / analysis.**
N=10 for primary contrasts, N=5 for interactions; Latin square; seed pin; primary = bootstrap 95% CI on `expected tokens per verified success = mean(tokens)/success_rate`; secondary median+IQR; win iff CI excludes ±10% ROPE AND non-inferior correctness; Holm correction. **WHY:** prevents p-hacking. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** provider drift. **Cheapest test (30 min):** pilot variance → power for 20% MDE.

**MF4 — Instrument token accounting at API boundary.**
Σ(system+user+tool_output_post_filter+assistant) per API call; raw vs compressed logged; guard tokens separated; per-run JSON in durable store. **WHY:** shell vs model boundary diverges >15% typically. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** embedding costs. **Cheapest test (1 hr):** one T0: guard RTK saving vs API delta.

**MF5 — Externalize enforcement.**
R5 routing logged as `classify: … because…`; R6 sufficiency via external checklist; C2 checkpoint deterministic (e.g., every 5 tool calls) with versioned JSON schema, script-authored, cost reported separately. **WHY:** avoids tautology. **HOW CERTAIN:** evidence-based (self-judgment overconfident). **WHAT-NOT-TESTED:** checklist completeness (E/F tests). **Cheapest test (1 hr):** checklist pilot on R2 — does R6b ever escalate?

### SHOULD-FIX

* Repo/guard reset + version pin; density rubric with IRR; dual denominator reporting (mean|success + expected cost); adaptive interaction bound; failure injection as scored tasks.

### CONSIDER

Temperature=0 + API version log; dollar cost secondary metric; guard/wall-time covariates; adverse stopping rule.

---

## 5. Verdict

**NEEDS REVISION — operationally not executable.**

Philosophy and decomposition are research-grade; operational layer is a sketch. ~1–2 days to close MF1-MF5 plus 6-task pilot yields runnable experiment. Central principle `22:779` should be retained verbatim.

**Risk if run as-is:** anecdotal wins, non-replicable accounting, selection bias, illusory RTK/Serena effects under correct denominator, variance swamping signal.
