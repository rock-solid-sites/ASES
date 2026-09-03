# Adversarial Review — Experiment A Tooling & Context-Efficiency v2

**Reviewer:** laguna-s-2.1-free, zero-context, independent, read-only
**Document:** `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2, 2026-09-03)
**Date:** 2026-09-03
**Source:** Independent zero-context adversarial review — Experiment A v2
**Verdict:** NEEDS REVISION — conceptually excellent, instrumentally incomplete

---

## 1. Strengths — Convergent With Other Reviewers, Independently Observed

**S1 — Scope isolation is the single most important correction in v2.** `2:27-39` hold-constant list plus `21:721-737` explicit deferral to Experiment B removes the orchestrator/Sol/model-routing confound that made v1 untestable. This is not scope narrowing for convenience — it is causal identification.

**S2 — A/B/C orthogonalization (Avoid / Retrieve / Compress) `3:57-93`.** Correctly reframes RTK, Serena, compaction as non-competitors acting on different phases of the information lifecycle. Prevents the naive "optimized agent vs baseline" trial that hides compensatory effects.

**S3 — Compensatory behavior as first-class outcome `5:149-168`.** The directive `Never treat RTK's own savings counter as the experiment result` is methodologically load-bearing. Most tooling evaluations fail precisely here — they report filter-level compression while net trajectory cost rises via extra turns.

**S4 — Task-conditional retrieval economics R1-R4 `6:177-254`.** Hypothesis "lexical dominates localization" is falsifiable and task-stratified. Document correctly does not assume universal Serena superiority.

**S5 — Adaptive routing R5 `7:258-287` and evidence-based stopping R6 `8:290-327` isolated before combination.** Tests whether avoidance beats density improvements — a rarer and more valuable question than tool bake-off.

**S6 — Deterministic compaction first `10:370-424`.** "Do not prematurely optimize the summary format" avoids conflating "is less context sufficient?" with "which summarizer is best?" — correct cheapest-test-first sequencing.

**S7 — Interaction taxonomy L451-471 and failure classes E/F `14:516-522` + `15:527-551`.** Additive/Redundant/Compensatory/Synergistic framing plus adversarial tasks (misleading matches, generated files, stale results, incomplete handoff) prevents Goodharting toward trivial localization.

**S8 — Phased experimental sequence `22:742-776`.** Baseline → RTK → retrieval → adaptive → stopping → compression → interactions → adversarial is correctly ordered to establish main effects before testing interactions.

> **Laguna independent judgment:** S1-S8 are genuine strengths. No other tooling proposal reviewed in this corpus achieves this decomposition clarity.

---

## 2. Threats To Validity

### 2.1 Internal

| # | Threat | Location | Detail |
|---|--------|----------|--------|
| I1 | Hold-constant contradiction | `2:37-38` vs `2:43-47` | `model settings` "remain fixed" while `dynamic-models` remains active — permits silent per-task model mutation. Uncontrolled treatment. |
| I2 | T0/T2 identity confusion | `4:96-120` vs `5:129-136` | T0 = "current normal workflow" already includes `rtk-guard`. If so, T0 ≡ T2 and baseline is duplicated; if not, T0 definition is ambiguous. |
| I3 | No repo/reset, no randomization | `13:473-491` | Sequential phases without `git worktree` reset, without order counterbalancing, without cache invalidation. State carryover guarantees confounding. |
| I4 | Stochasticity unpinned | `13:487-489` | No temperature/seed/top_p/max_tokens/model version pin. Free-tier `laguna-s-2.1-free` stochasticity alone can exceed hypothesized effect sizes. |
| I5 | Guard injection as hidden treatment | `2:41-48` | `crosslink-guard` / `orchestrator-guard` / `rtk-guard` prompt injections consume tokens and can steer retrieval/tool choice but are not measured. |

### 2.2 Construct

| # | Threat | Location | Detail |
|---|--------|----------|--------|
| C1 | Verified-success gate undefined | `16:556-594` / `19:646-664` | `verified` conflates tests-pass, lint, typecheck, gold diff, human audit without pre-registered per-task oracle. `unacceptable correctness regression` has no numeric threshold. |
| C2 | Density subjectivity | `9:330-361` / `16:574-585` | `useful / relevant / duplicate / new evidence` requires a rater, no rubric, no blinding, no IRR target, no tokenizer specified. |
| C3 | Token accounting ambiguous | `4:101-119` / `5:138-147` / `16:566-572` | Whether system + guard + tool raw vs post-RTK + reasoning tokens count, at which boundary (guard vs model API), not defined. |
| C4 | Sufficiency circularity | `8:302-315` | R6b stopping judged by agent's own proposition/evidence/confidence — self-judgment tautology without external checklist. |
| C5 | C2 schema informal | `10:375-398` | `objective/constraints/known facts/...` is folk list, not versioned schema. Inter-annotator incomparability expected. |

### 2.3 Statistical

| # | Threat | Location |
|---|--------|----------|
| S1 | No N, power, MDE. `multiple times where practical` `13:475` and `several representative tasks` `13:490` are not specifications. Tokens heavy-tailed; mean alone misleading. |
| S2 | No alpha/decision rule/ROPE, no multiplicity correction across ~7 interaction cells × 6 task classes. Family-wise false positives guaranteed. |
| S3 | No pre-registered primary statistic (median vs mean vs expected cost). Post-hoc selection risk. |
| S4 | No stopping rule — can declare win after favorable interim look. |

### 2.4 External

* Single repo (EDASES), single model, illustrative-not-executable task examples (`SessionRunCoordinator` placeholders `6:183`). Output claims to become "baseline tooling stack for Experiment B" `21:735` — generalization not supported by design.

---

## 3. Missing / Underspecified Decisions (Blocking)

| # | Location | Gap | Why Blocks |
|---|----------|-----|------------|
| M1 | `16:590-595` `19:646-656` | Verified-success oracle + non-inferiority margin | Tokens-to-verified-success uncomputable; correctness subjective |
| M2 | `14:494-523` | Concrete task suite (≥3 per class, ground truth, oracle, difficulty pilot, holdout) | Cannot sample, randomize, or score; selection bias 100% |
| M3 | `13:473-491` | N, randomization (Latin square), seed, power, SAP, multiplicity | Anecdotal results, p-hacking |
| M4 | `4:101-118` `16:566-588` | Token instrumentation at model API boundary (system/guard/raw-vs-compressed) | Replication impossible; accounting flips RTK effect |
| M5 | `7:262-284` `8:302-324` `10:375-404` | Who enforces R5 routing / R6 sufficiency / C2 checkpoint+compaction author | Tautology (agent judges itself); hidden human labor |
| M6 | `2:41-48` `5:129-147` | Tool version freeze (RTK rules, Serena/LSP, rg flags, model pin) + guard isolation | Conditions not replicable |
| M7 | `12:440-450` `22:742-776` | Interaction adaptive bound (not full 2⁴ factorial up front) | Free-tier budget exhaustion before Phase 7 |
| M8 | `15:527-550` | Failure injection protocol (base rate, blinding, scoring `detect → retrieve → correct`) | Adversarial tests become anecdotes |
| M9 | `16:598-614` `17:598-614` | Data dictionary / durable logging of raw vs compressed vs follow-up | No audit trail |

---

## 4. Prioritized Improvements

### MUST-FIX

**MF1 — Operationalize verified-success + non-inferiority (C1/M1).**
Define per task: verification script = `tests + lint + typecheck + gold output diff` plus blinded audit of out-of-scope edits. Non-inferiority margin: success rate drop >5% absolute or any critical-path invariant violation = reject. Use Wilson CI. **WHY:** tokens are meaningless without correctness gate. **WHAT:** methodology + EDASES verification needs. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** oracle gaming. **Cheapest test (1 hr):** draft 2 pilot oracles; two raters blind to script; if κ<0.8, fail.

**MF2 — Instantiate task bank (M2).**
≥18 tasks (3×A-F), each: commit pin, file scope, ground-truth patch/answer, verification script, fails-without baseline, difficulty stratum from T0 pilot tokens, 2 holdout tasks. **WHY:** abstract classes cannot be randomized. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** cross-repo generalization. **Cheapest test (2 hr):** 1 per class ×3 runs on T0; if any floor/ceiling, recalibrate.

**MF3 — Pre-register N / randomization / analysis (S1-S3/M3).**
N=10 for T1 vs T2 and R5 contrasts, N=5 for interaction cells; Latin square order; bootstrap 95% CI on `expected tokens per verified success = mean(tokens)/success_rate`; secondary median+IQR; win iff CI excludes ±10% ROPE AND non-inferior correctness; Holm across task classes. **WHY:** "where practical" guarantees post-hoc wins. **HOW CERTAIN:** evidence-based (heavy tails). **WHAT-NOT-TESTED:** provider drift. **Cheapest test (30 min):** pilot variance → power calc; if N>budget, reduce conditions.

**MF4 — Instrument token accounting at API boundary (C3/M4).**
`trajectory tokens = Σ(system+user+tool_output_post_filter+assistant)` per turn as seen by model API; log raw vs compressed separately; guard tokens separated; per-run JSON. **WHY:** shell savings ≠ model savings. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** embedding costs. **Cheapest test (1 hr):** one T0 run: compare guard-reported RTK saving vs API delta; if >15% divergence, broken.

**MF5 — Externalize routing/stopping/compaction enforcement (C4-C5/M5).**
R5: prompt rule, log agent's `classify: lexical/relationship because…`; R6: external checklist, not self-report; C2: deterministic checkpoint (every 5 tool calls or file edit), script-authored compact state with versioned JSON schema, compaction cost reported separately. **WHY:** self-judgment tautology. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** checklist misses decision-critical info — E/F tests this. **Cheapest test (1 hr):** checklist pilot on R2; if R6b never escalates, trigger wording fails.

### SHOULD-FIX

**SF1 — Repo/guard isolation.** Pin all guard versions, disable or log `dynamic-models` mutations, `git worktree` reset per run, Serena reindex. Log guard interventions.

**SF2 — Density rubric with IRR.** Automated heuristic (`useful` = lines in final patch/gold/verification diff), blinded human audit 10%, target Spearman ρ>0.7 / κ>0.7.

**SF3 — Report both denominators:** `mean(tokens|success)` and `expected tokens per verified success`; primary win needs expected cost win.

**SF4 — Adaptive interaction bound.** Only full factorial if each single mechanism >10% effect; else test T2+R6 and R5+C2 + final combined.

**SF5 — Failure injection as separate tasks** with `uncertainty → escalate` pass/fail scoring.

### CONSIDER

Pin temperature=0, log API version; add dollar cost; log wall-time/guard overhead; pre-register adverse stopping (halt condition if success drops >10% after n=5).

---

## 5. Verdict

**NEEDS REVISION — not executable as written.**

Conceptual grade A- ; operational readiness D. Bridging spec is ~1–2 days (MF1-MF5) + 6-task pilot. The A/B/C principle `22:779` is correct and should be preserved verbatim. Fix instrumentation and the experiment becomes publishable.

**Risk if run now:** underpowered anecdotes, non-replicable token counts, selection bias, illusory RTK/Serena wins that vanish under proper denominator, free-tier variance swamping signal.
