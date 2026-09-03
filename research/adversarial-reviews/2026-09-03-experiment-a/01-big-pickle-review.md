# Adversarial Review: `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines)

**Reviewer stance:** Read-only, zero-context, independent. Model: `opencode/big-pickle` (free). File read in full. No edits, no synthesis with other reviewers.

**Date:** 2026-09-03
**Source:** Independent zero-context adversarial review — Experiment A v2
**Verdict:** NEEDS REVISION — operationally underspecified, not ready to execute

---

## 1. What The Experiment Gets Right (Strengths)

**Conceptual separation is correct and non-trivial.**

* `1:11` / `3:57-92` — Three mechanisms (A: avoid, B: higher-density retrieval, C: compress retention) are correctly orthogonalized. Document explicitly rejects the common conflation `3:91-93` that RTK/Serena/summarization compete as “same thing.” This is the sharpest architectural insight in the design — proven by prior confusion in v1 and synthesis notes on lifecycle-ownership tension.
* `2:27-51` / `21:721-737` — Narrow scope discipline: one agent / one model / one task / fixed role, only tooling/context varies. Hold-constant list is explicit and directly addresses the Sol/orchestrator confound that would otherwise contaminate Experiment A. Separation into Experiment B is methodologically sound.
* `1:21-23` / `16:556-565` — Primary metric `tokens-to-verified-success` gated on correctness. This anti-Goodhart choice `5:165-166` (“Never treat RTK’s own savings counter as result”) is essential; many context-efficiency studies fail here by optimizing proxy token counts while ignoring recovery cost.
* `5:149-162` — Secondary measurement of compensatory behavior (compression → extra tool calls → extra turns) is excellent. This is where naive RTK evaluations collapse; the design correctly treats it as first-class.
* `6:177-179` / `18:619-644` — Task-dependent economics hypothesis for lexical vs semantic retrieval (R1-R4 stratification) avoids the false universal-winner framing. The hypothesis is stated but not assumed `6:195-201`.
* `7:258-287` / `8:290-327` — Adaptive retrieval R5 and evidence-based stopping R6 are isolated as independent variables before combination. Tests `avoid` independently of `density`.
* `10:368-406` / `11:410-424` — Context-retention (C2/C3) wisely starts with deterministic, simple compaction before building summarizers/vector DBs. “First establish whether less retained context is sufficient” prevents premature optimization on representation.
* `12:428-471` / `14:494-523` — Interaction taxonomy (Additive/Redundant/Compensatory/Synergistic) and explicit failure/adversarial task classes (E/F) prevent optimization toward trivial tasks. This is rare and strong.
* `22:742-776` — Phased sequence is logically ordered to establish baselines before interactions — correct cheapest-test-first ordering.

> **Overall scaffold grade:** High. The decomposition is research-grade. Failures are not conceptual but operational — the bridge from principles to executable protocol is underspecified.

---

## 2. Threats To Validity

### 2.1 Internal Validity (confounds / controls)

* **`2:30-38` Hold-constant claim is unenforceable without freeze.** `2:43-47` lists `dynamic-models` as active infrastructure but `2:37-38` says model settings remain fixed. `dynamic-models` by definition can mutate model settings per-task. Contradiction unless explicitly disabled/pinned. **WHY:** infrastructure vs. control conflict; **WHAT:** doc text; **HOW CERTAIN:** proven (textual contradiction).
* **`4:96-120` T0 vs `5:129-135` T1/T2 confound.** T0 is “current normal workflow” (which already includes rtk-guard per `5:135`). T1 is “RTK OFF.” If T0 = T2, then T0 is redundant. If T0 ≠ T2, baseline is ambiguous. Order effects not controlled — agent learning across repeated runs on same repo/task contaminates within-subjects design.
* **Repository mutation.** `16:602-605` counts `files changed` but no reset procedure between conditions. If tasks mutate files, subsequent conditions start from dirty state. Without `git worktree` reset + `git clean -fdx` + DB reset per run, internal validity collapses.
* **Model stochasticity uncontrolled.** No temperature, top-p, seed, or `max_tokens` specified; `opencode/big-pickle` on free tier has high variance and non-determinism even at temp 0. Repeated runs without seed control conflate mechanism effect with sampling noise.
* **Free-tier execution confound.** Rate-limit parking, queue delays, and model-version drift on `opencode` free tier affect `17:609` wall-clock and may truncate trajectories invisibly. This is not a neutral substrate.
* **Agent compensation is measured but not controlled.** `5:149-162` correctly anticipates it, but no decision rule prevents it from swamping effect size. The agent’s system prompt that encourages tool use is itself a confound between conditions.

### 2.2 Construct Validity (does the metric measure the claim?)

* **`16:556-564` tokens-to-verified-success undefined for failures.** If success rate < 100%, is the denominator per-success or per-attempt? Two definitions diverge massively: `mean(tokens | success)` vs. `mean(tokens) / success_rate` (expected tokens per verified success). Without this, a 50% success-rate condition with low tokens looks artificially good.
* **`9:332-360` Useful-information density is subjective.** `9:336-341` `relevant tokens / duplicate tokens / new evidence` requires a rater. No rubric, no inter-rater reliability, no blinding. Construct collapses to investigator judgment unless operationalized as post-hoc task-relevant lines covering gold evidence set.
* **`16:586-589` Recovery cost double-counts.** If tokens-to-verified-success already includes retries, M7 is not independent — it is a decomposition, not a separate outcome. Needs causal definition.
* **Verification construct overloaded.** “Verified” sometimes means tests pass, sometimes means evidence sufficient, sometimes means human review. No single verification harness is defined.

### 2.3 Statistical Conclusion Validity

* **`13:473-491` “multiple times where practical” is not a sample-size specification.** No N, no power analysis, no handling of skewed distributions. Tokens are heavy-tailed; `mean` `13:481` is misleading without log-transform or median/IQR reporting. No pre-registered test (e.g., Mann-Whitney, bootstrap CI, Bayesian ROPE).
* **Multiplicity explosion.** Phases 1-6 imply ~8 primary conditions + `12:440-450` 7 interaction combos × 6 task classes (A-F) = 84+ cells. With N=3 per cell, that is 250+ runs on free tier — underpowered per cell and uncorrected for multiple comparisons. Family-wise error will produce false “wins.”
* **Variance handling `13:480-485` lists descriptives but no decision rule.** “Record mean/median/range/success_rate” does not state when a difference is declared real. Without pre-registered ROPE (e.g., >15% token reduction + non-inferior correctness), any noise becomes a finding.
* **Stopping rule absent.** Experiment can be declared “won” after any favorable run; no pre-commit to N before looking.

### 2.4 External Validity

* **One repo + one model + synthetic tasks = narrow generalization.** Claim `1:11` about “software-engineering work” requires diversity; design acknowledges this via task classes but provides no repo-diversity plan. Results on EDASES repo with `big-pickle` may not transfer.
* **Task class examples are placeholders, not tasks.** `6:182-184` “Find every occurrence of SessionRunCoordinator” is an illustrative query, not an executable task with file scope, ground truth, and verification script. External validity cannot be assessed until suite is instantiated.

---

## 3. Missing Or Underspecified Decisions (Blocking for Execution)

| # | Location | Gap | Why It Blocks |
|---|----------|-----|---------------|
| **M1** | `19:646-679` / `16:590-595` | **Success/verification gate undefined.** What counts as “verified”? Which tests, which harness, lint/typecheck, human audit? What is “unacceptable correctness regression” — 1%? 5%? Non-inferiority margin? | Without this, `tokens-to-verified-success` is uncomputable and every correctness claim is subjective. |
| **M2** | `14:494-523` / `15:527-550` | **Task suite not instantiated.** Classes A-F described abstractly; zero concrete tasks, zero file paths, zero ground-truth answers, zero difficulty calibration, no holdout/injection procedure. | Cannot run, randomize, or stratify. Selection bias risk is 100%. |
| **M3** | `13:473-491` / `16:556-595` | **N, randomization, and analysis plan absent.** No runs-per-condition, no counterbalancing order, no seed control, no statistical test, no pre-registration. “Where practical” delegates the most consequential decision. | Any result is anecdotal; cannot distinguish mechanism from noise. |
| **M4** | `4:101-118` / `16:566-588` | **Token counting and instrumentation undefined.** Does “total trajectory tokens” include system prompt, tool outputs before vs after RTK, reasoning tokens, or only model input+output? Is RTK savings measured at guard or at model boundary? Tool “where measurable” `4:119` is a loophole. | Replication impossible; RTK effect can be inflated/deflated by accounting choice. |
| **M5** | `5:129-147` / `15:532-538` | **Tool boundary freeze missing.** RTK compression level/rules, Serena version + prompt, LSP config, rg flags, model version pin — none versioned. `7:262-284` routing policy: who routes — hard router, agent prompt, or orchestrator-guard? | A change in RTK filter list or Serena prompt is a different condition entirely; without freeze, conditions are not replicable. |
| **M6** | `8:290-324` / `10:375-404` | **Evidence-sufficiency and compact-state spec circular.** R6b `8:304-311` says agent “must establish required proposition + supporting evidence + confidence” but provides no judge, no rubric, no threshold. C2 `10:377-387` lists fields to retain but not who/what compacts, when checkpoint triggers, or token budget. | If the agent judges its own sufficiency, R6 tests agent compliance, not mechanism. If compaction is manual, cost of compaction is unmeasured. |
| **M7** | `12:430-450` / `22:742-776` | **Interaction phase underpowered and unsequenced.** No rule for which combos to test if early results are null; full 2⁴ factorial is impractical on free tier. | Resource exhaustion before reaching Phase 7. |
| **M8** | `15:527-550` | **Failure injection procedure absent.** Lists interesting failures but not how to inject, at what base rate, blinded or not, or how “detects uncertainty → retrieves” is scored. | Failure tests become ad-hoc anecdotes. |

**Additional underspecification:** Wall-time confounded by API latency (`17:609`); cache/embedding state; file-system reset; logging schema; cost budget; responsible disclosure of WHAT-NOT-TESTED per condition.

---

## 4. How To Improve — Prioritized Recommendations

> Per `AGENTS.md`: each recommendation states **WHY** (reasoning), **WHAT** (basis), **HOW CERTAIN** (guess / evidence-based / proven), **WHAT-NOT-TESTED** (negative-space), and **cheapest discriminating test** (fastest falsifier).

### MUST-FIX (blocking — cannot execute without)

**MF1 — Operationalize verified-success and non-inferiority margin**
* `file:16:590-595` + `19:646-656` — Define: task succeeds iff (a) task-specific verification script passes (tests/lint/typecheck/gold-output diff) AND (b) human or automated audit confirms no spurious change outside task scope. Define correctness regression as >5% absolute drop in success rate or any critical-path failure. Quantify 5% via binomial CI; justify margin pre-hoc.
* **WHY:** Without a hard gate, token savings are meaningless.
* **WHAT:** accepted methodology for non-inferiority + EDASES verification needs.
* **HOW CERTAIN:** proven — every prior context-efficiency study that omitted this produced false wins.
* **WHAT-NOT-TESTED:** does not test whether verification script itself is flawed or gameable.
* **Cheapest discriminating test ( < 1 hr):** Write verification script for 2 pilot tasks (one localization, one multi-file). Run unmodified agent; have two raters independently judge “verified” blind to script output. If inter-rater κ < 0.8 or script disagrees with raters, spec is insufficient — fail fast before any token measurement.

**MF2 — Freeze task suite with concrete instances and ground truth**
* `file:14:494-523` — Instantiate ≥3 concrete tasks per class A-F (min 18 tasks), each with: repo commit pin, file scope, ground-truth answer/patch, verification script, and `fails-without-task` baseline. Stratify difficulty by pre-measured median T0 tokens (pilot). Include holdout tasks never used during design.
* **WHY:** Abstract classes cannot be randomized or scored.
* **WHAT:** experimental design evidence on task sampling bias.
* **HOW CERTAIN:** evidence-based — heterogeneous SE tasks show class × tool interaction (see R1-R4 rationale).
* **WHAT-NOT-TESTED:** does not test cross-repo generalization; single-repo limitation remains.
* **Cheapest discriminating test (2-3 hrs):** Pilot 1 task per class (6 tasks) 3 runs each on T0. If any class shows ceiling/floor (100% fail or <500 tokens trivial), class definition is mis-calibrated — revise before scaling.

**MF3 — Pre-register N, randomization, and analysis rule**
* `file:13:473-491` — Fix: N=10 runs/condition for 2 primary conditions (T1 vs T2, R5 vs single-tool) and N=5 for interaction cells; counterbalance order via Latin square; pin seed where provider supports it, else report seedless variance explicitly; primary analysis = bootstrap 95% CI on difference in `expected tokens per verified success = mean(tokens)/success_rate`; secondary = median + IQR (median is robust to tails). Declare win only if CI excludes ROPE (±10% tokens) AND correctness non-inferior. Apply Holm correction across task classes.
* **WHY:** “Where practical” guarantees p-hacking and anecdotal wins.
* **WHAT:** statistical best practice for stochastic LLMs; heavy-tailed token costs.
* **HOW CERTAIN:** evidence-based — LLM trajectory tokens are empirically heavy-tailed.
* **WHAT-NOT-TESTED:** does not test provider-side non-determinism beyond sampling; model drift remains.
* **Cheapest discriminating test (30 min, no execution):** Simulate power with pilot variance: assume σ ≈ 0.4×mean (typical). Compute N needed to detect 20% reduction at 80% power. If N > budget, reduce conditions now — failing this test before spending tokens saves the experiment.

**MF4 — Instrument token accounting at model boundary**
* `file:4:101-118` / `16:566-588` — Define `total trajectory tokens = Σ (system+user+tool_output_post_filter+assistant)` per turn as seen by model API; log raw vs compressed tool output separately; log `tool_calls`, `follow_up_calls`, additional turns. Instrument in guard, not in agent self-report. Store per-run JSON.
* **WHY:** RTK savings counted at shell ≠ savings at model boundary; accounting choice flips conclusions.
* **WHAT:** direct measurement principle; RTK is a filter — measure after filter.
* **HOW CERTAIN:** proven — `5:165-166` acknowledges the gap but leaves accounting undefined.
* **WHAT-NOT-TESTED:** does not test embedding/cache token costs outside model context.
* **Cheapest discriminating test (1 hr):** Add logging to single T0 run; compare guard-reported RTK savings vs actual delta in model-input tokens. If they diverge >15%, accounting is broken — fix before any condition.

**MF5 — Specify who/what enforces routing, stopping, and compaction**
* `file:7:262-284` / `8:302-324` / `10:375-404` — Hard decisions: R5 routing = prompt rule + post-hoc classifier of tool choice (agent 자율, not hard router) vs. hard router (describe which); R6 sufficiency judged by external checklist (not agent self-report); C2 checkpoint = deterministic rule (e.g., after each file edit or every 5 tool calls) with fixed retained fields; compaction performed by script, not by agent, and its token cost is excluded from trajectory but reported separately to avoid hidden labor.
* **WHY:** If agent judges its own sufficiency, R6 is tautological.
* **WHAT:** construct validity of “stopping” requires external criterion.
* **HOW CERTAIN:** evidence-based — LLM self-judgment of sufficiency is overconfident without calibration.
* **WHAT-NOT-TESTED:** does not test whether external checklist itself misses decision-critical info (Class E/F specifically tests this).
* **Cheapest discriminating test (1 hr):** Write 1-page sufficiency checklist for R2 task; have agent run R6a vs R6b on same task. If R6b agent never escalates despite missing evidence, checklist or enforcement is insufficient — revise trigger wording.

### SHOULD-FIX (high value, not strictly blocking)

**SF1 — Isolate repository state and guard stack**
* `file:2:41-48` — Pin `crosslink-guard` / `orchestrator-guard` / `rtk-guard` / `dynamic-models` versions, disable `dynamic-models` mutation or log every mutation; reset repo via `git worktree` per run. Log guard interventions as covariates.
* **WHY:** prevents cross-run contamination and model-setting drift.
* **HOW CERTAIN:** evidence-based.
* **WHAT-NOT-TESTED:** does not test guard overhead tokens themselves.
* **Cheapest test:** Run two sequential T0s without reset; if second run shows >10% token difference vs. fresh-clone run, reset is mandatory.

**SF2 — Operationalize information density without human bias**
* `file:9:330-361` — Define “useful” as: returned lines that appear in final patch, gold evidence set, or verification script diff. Compute automatically; have blinded rater audit 10% sample for precision/recall. Report `useful / returned` alongside trajectory cost.
* **HOW CERTAIN:** guess — automation quality unknown; needs validation.
* **WHAT-NOT-TESTED:** semantic usefulness (reasoning that does not surface in patch).
* **Cheapest test:** Hand-label useful tokens for 5 retrievals; compare to automated heuristic; if Spearman ρ < 0.7, heuristic is invalid.

**SF3 — Explicitly handle failure denominator**
* `file:16:556-564` — Report both `mean(tokens|success)` and `expected tokens per verified success`. Primary win requires both to improve or expected cost to improve with non-inferior success rate.
* **HOW CERTAIN:** proven — denominator ambiguity is a known source of false efficiency claims.
* **Cheapest test:** Simulate 30% failure case; show how the two definitions reverse rankings. If team disagrees on which to use, pre-register resolves it.

**SF4 — Bound interaction testing adaptively**
* `file:12:440-450` — Do not pre-commit to full 2⁴ factorial. Rule: test full factorial only if each single mechanism shows >10% effect in Phase 1-5; otherwise test only `T2+R6` and `R5+C2` plus final combined — the two most theoretically complementary pairs. Saves ~60% runs.
* **HOW CERTAIN:** evidence-based (redundancy hypothesis `12:458-460`).
* **Cheapest test:** Estimate run budget (tokens × N × conditions). If > free-tier quota, adaptive bound is mandatory.

**SF5 — Failure-injection protocol**
* `file:15:527-550` — Pre-define 6 injected cases (misleading match, duplicate impl, generated file, comment-only ref, stale test, incomplete handoff), each as a separate task variant with expected “detect uncertainty → escalate” behavior scored as pass/fail. Base rate: 1 per class.
* **HOW CERTAIN:** guess — injection realism uncertain.
* **Cheapest test:** Inject one misleading lexical match pilot; if efficient strategy does not detect it, stopping threshold is too aggressive.

### CONSIDER (if budget allows)

**C1 — Model-version drift guard.** Log model ID string per run; if provider updates mid-experiment, stratify analysis pre/post. *Cheapest test:* query model version endpoint before/after phase.

**C2 — Cost-of-compaction accounting.** If human writes compact state, log human time; if script does, log script tokens. Prevents externalizing cost. *Cheapest test:* time one manual compaction.

**C3 — Report wall-time and dollar cost alongside tokens** for practical relevance; free-tier wall-time is noisy, so report with and without queue wait.

**C4 — Pre-register adverse stopping rule:** halt a condition if success rate drops >10% after N=5 runs — prevents burning budget on harmful compression.

---

## 5. Overall Verdict

**NEEDS REVISION — operationally underspecified, not ready to execute.**

The design is **conceptually ready** (strong decomposition, correct metric philosophy, correct phased order, correct anti-Goodhart stance) but **operationally not ready** (no executable task suite, no verification gate, no N/analysis plan, no instrumentation spec, no tool-version freeze, no sufficiency judge).

**Risk if executed as-is:** High probability of (a) anecdotal, underpowered claims, (b) non-replicable token counts due to accounting ambiguity, (c) selection bias from ad-hoc task choice, (d) inflated RTK or Serena wins that vanish under proper `tokens-to-verified-success` with correct denominator, (e) free-tier variance swamping true effects.

**Path to ready:** ~1–2 days of specification work to close MF1–MF5, plus a 6-task pilot (one per class, 3 runs) to calibrate variance, verify instrumentation, and lock N. The cheapest discriminating tests above are ordered to fail fast: instrument accounting (MF4) and power calc (MF3) should be done before any data collection; pilot per-class (MF2) next.

**What remains excellent regardless:** The A/B/C framing, the compensatory-behavior measurement, the decision to keep agent/model fixed, and the final policy-output goal `20:683-716` are the right abstractions. Fix the operational layer and this becomes a publishable tooling-efficiency experiment.
