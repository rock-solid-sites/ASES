# Adversarial Review — Experiment A Tooling & Context-Efficiency v2

**Reviewer:** nemotron-3-ultra-free, zero-context, read-only session
**Document:** `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2, 2026-09-03)
**Date:** 2026-09-03
**Source:** Independent zero-context adversarial review — Experiment A v2
**Verdict:** NEEDS REVISION — Underspecified for execution

---

## 1. Strengths

**S1 — Correct narrowing.** Holding `model/role/repo/task/spec/guards/settings/verification` constant (L28-39) while varying only tooling/context is the right causal isolation. Explicitly deferring Sol/orchestrator/routing to Experiment B (L720-737) fixes the layer-contamination that plagued v1.

**S2 — Mechanism decomposition is non-trivial and correct.** Splitting into Avoid (A) / Retrieve higher-density (B) / Compress retained (C) (L56-92) and stating `RTK, Serena and context summarization are not competing versions of the same thing` (L93) prevents the common "one optimized agent vs baseline" confound.

**S3 — Compensatory behavior recognized.** L149-168 `Never treat RTK's own savings counter as the experiment result` and requiring measurement of follow-up commands / extra turns is the sharpest insight in the doc. Most tooling papers fail here.

**S4 — Task-dependent economics for retrieval.** R1-R4 (L179-254) correctly rejects a universal "Serena > grep" claim and hypothesizes `lexical should dominate` for localization. This is falsifiable.

**S5 — Failure/adversarial tests built in, not bolted on.** Task classes E-F (L514-521) + Section 15 (L526-551) testing misleading matches, generated files, stale results, incomplete handoffs. `The last two prevent optimization toward trivial tasks` (L522) is excellent.

**S6 — Deliberate simplicity for C2/C3** (L408-424) — `Do not prematurely optimize the summary format` — avoids turning the experiment into a summarizer benchmark before establishing `is less context sufficient?`.

**S7 — Interaction taxonomy** (L451-471: additive/redundant/compensatory/synergistic) gives a useful interpretive frame for Phase 6.

---

## 2. Threats to Validity

### 2.1 Internal Validity

| # | Threat | Location | Description |
|---|--------|----------|-------------|
| I1 | **Order / learning / cache confound** | L474-491, L743-776 | No randomization or counterbalancing of condition order. Serena index warm-up, filesystem caches, git state, and even LLM context via guard state can carry over. Sequential phases (Baseline→RTK→Retrieval→Adaptive) guarantee order is confounded with treatment. |
| I2 | **Repo-state contamination** | L28-39 hold-constant list; L474-491 | No `repo reset` procedure between runs. A `files changed` from T0 persists into T2 unless explicitly reverted. Multi-file change tasks (R4) are inherently stateful. |
| I3 | **Stochastic model not controlled** | L487-489 | `For stochastic models, repeated runs are particularly important` acknowledges issue but does not fix `temperature`, `seed`, `top_p`, or API version. Non-determinism becomes unexplained variance. |
| I4 | **Experimenter-as-instrument** | L330-361, L558-595 | Agent behavior change under RTK (L151-160) is confounded with who judges `useful evidence`/`relevant tokens`. If scorer sees condition label, expectation bias inflates/deflates density. |
| I5 | **Classifier conflation in R5** | L257-286 | Adaptive routing (R5) conflates *tool capability* with *classifier accuracy* (lexical vs relationship question). If agent misclassifies question type, failure is attributed to tool incorrectly. |
| I6 | **Guard-stack token injection** | L41-50 | `crosslink-guard / orchestrator-guard / rtk-guard / dynamic-models remain active` — their prompts/tool injections consume tokens and can steer behavior, but not measured as covariate. Rtk-guard ON vs OFF is treatment; other guards are hidden treatment. |

### 2.2 Construct Validity

| # | Threat | Location | Description |
|---|--------|----------|-------------|
| C1 | **`tokens-to-verified-success` underspecified** | L18-23, L556-564, L592-594 | `verified` is a hard gate but verification criteria are never operationalized. Is it `tests pass`? Which tests? Who authors oracle? Human verification introduces subjectivity; test-only verification invites gaming (agent can write weak tests). |
| C2 | **`useful / relevant / duplicate` is subjective** | L332-361, L573-585, L598-614 | Density metrics `useful evidence / context tokens` (L346) and M4-M6 have no annotation protocol, no definition of token unit (which tokenizer?), no inter-rater reliability plan. Construct is not measurable as written. |
| C3 | **Token counting ambiguous** | L99-121, L138-147, L567-571 | `total input tokens / output tokens / trajectory tokens / tool output entering context` — which tokenizer? Does system prompt count? Do guard injections count? Are RTK-compressed vs raw both counted? Without this, M1-M3 are incomparable across conditions. |
| C4 | **Sufficiency judgment is circular** | L290-325 (R6b) | `supporting evidence + confidence sufficient for task` (L303-311) — if the agent itself judges sufficiency, the stopping condition is not independent of the outcome. No external sufficiency oracle defined. |
| C5 | **Compact state schema is folk definition** | L374-403 | `objective/constraints/known facts/...` is an informal list, not a schema. Two annotators will produce incomparable C2 states, so C1 vs C2 contrast is ill-defined. |

### 2.3 Statistical Validity

| # | Threat | Location | Description |
|---|--------|----------|-------------|
| S1 | **No sample size / power / MDE** | L473-491, L647-677 | `multiple times where practical` (L475), `several representative tasks` (L490) — no N per cell, no power analysis, no minimum detectable effect for `lower tokens-to-verified-success`. Cannot know if experiment can detect, e.g., a 15% saving. |
| S2 | **No decision rule / alpha / correction** | L647-677, Sec 19-20 | What p/threshold counts as a win? Mean vs median as primary? Multiple comparisons across ~8 interactions (L441-449) with no family-wise correction → inflated false-positive rate for "wins". |
| S3 | **Distribution assumptions ignored** | L481-486 | Token counts are heavy-tailed (one bad trajectory dominates mean). Reporting `mean/median/range` without pre-specifying primary statistic and non-parametric test invites post-hoc selection. |
| S4 | **Variance from stochastic LLM underestimated** | L487-489 | No estimate of within-condition variance from pilot. If intra-condition SD is 30% of mean (common for agentic tasks), even n=5 per cell is underpowered. |

### 2.4 External Validity

| # | Threat | Location |
|---|--------|----------|
| E1 | Single model, single role, single repo limits generalizability. Doc admits this as deliberate scope (L2-3), but then claims output `becomes the baseline tooling stack for Experiment B` (L736-737) — a general claim from a narrow sample. |
| E2 | Task classes A-F (L494-523) are synthetic place-holders (`SessionRunCoordinator` examples L183, L208, L232). No sampling frame mapping to real EDASES workload distribution; easy to over-represent tasks where lexical search shines. |
| E3 | Tooling (RTK, Serena) is OpenCode-specific. No argument for transfer to other harnesses. |

---

## 3. Missing / Underspecified Decisions Blocking Execution

Execution cannot start without answers to:

1.  **Task bank (blocking).** How many concrete tasks per class A-F? Who authors them? Where are ground-truth oracles stored? Difficulty calibration? Without this, Phase 2-4 cannot be scheduled. (L179-254 are examples, not tasks)
2.  **Token instrumentation (blocking).** Exact counting method: OpenCode API logs vs model provider billing vs tiktoken? Include system/developer/guard tokens? Tool-output tokens counted raw or post-RTK? Granularity per turn vs per trajectory? (Sec 4, Sec 16)
3.  **Relevance annotation protocol (blocking).** Who labels `relevant/duplicate/new evidence` (L338-342)? Human? LLM judge? Rubric? Blinded? IRR target? Without this M4-M6 cannot be measured.
4.  **Verification harness (blocking).** Concrete `success/failure` gate: test suite + manual review + lint? Pre-registered for each task? What about tasks where existing tests are insufficient? (L115, L556-594)
5.  **Randomization & reset (blocking).** Run order randomization, repo `git reset --hard` + clean, Serena index invalidation, inter-run washout. Not specified. (Sec 13, Sec 22)
6.  **Model settings freeze (blocking).** Exact model ID, temperature (0? 0.2?), seed, max tokens, API version pinned. `model settings` held constant (L38) but not enumerated.
7.  **R5 classifier operationalization.** Who/what decides `lexical/local vs relationship/symbol question` routing (L264-273)? Pre-tagged by experimenter or agent-classified at runtime? If agent-classified, prompt for classifier must be fixed and logged.
8.  **R6b evidence-based stopping implementation.** Is it a prompt instruction (`you must state proposition/evidence/confidence before stopping`)? A guard that blocks further retrieval? How is `sufficiency` judged? (L302-313)
9.  **C2 checkpoint & author definition.** When do checkpoints trigger (every N turns? manual phase boundary?)? Who authors compact state — deterministic script extracting fields or human? If human, blinding? Exact schema (JSON?) for `objective/constraints/...` (L375-388). If deterministic script, its code is part of treatment and must be versioned.
10. **Statistical decision rule.** Pre-registered one-tailed or two-tailed test, alpha, primary statistic (median tokens-to-verified-success among successful runs? mean across all runs with penalty for failure?), handling of failed runs in M1 denominator, multiple-comparison correction for interaction tests. (Sec 16,19)
11. **RTK ON/OFF fidelity.** Does T1 (RTK OFF) literally bypass `rtk-guard` or also change prompt to account for larger output? If shell output is truncated by model context limit when RTK OFF, is that a confound? (L127-147)
12. **Wall-time vs token tradeoff & budget.** No cap on retries/wall-time; an agent could loop infinitely under unbounded exploration (R6a). Need max trajectory length / max tool calls per task.
13. **Data recording schema.** Where do `raw output / compressed output / follow-up commands` (L139-147) get logged? Durable store? Sheet? No experiment data dictionary.

Items 1-5, 9-10 are **hard blockers** — running without them yields non-replicable numbers.

---

## 4. Prioritized Improvements

### MUST-FIX (blocking — cannot claim a result without)

**MF1 — Pre-register verified-success oracle & token-counting definition**

*   **WHY:** Without an oracle, `tokens-to-verified-success` is unfalsifiable; experimenter can declare any output "verified" post-hoc. Without token definition, M1-M3 are incomparable.
*   **WHAT:** Based on L556-564/M1-M8 and L592-594 hard gate. Certainty that current text leaves gate undefined is **proven** (no definition present).
*   **HOW CERTAIN:** Proven — inspected Sec 16-19, no operational definition found.
*   **WHAT-NOT-TESTED:** Does not test whether chosen oracle (tests vs human review) is itself biased; does not test tokenizer parity with provider billing.
*   **Cheapest discriminating test:** Draft oracle for *one* pilot task (Task A easy localization) — concrete test file + `pass criteria` checklist + token counting script using OpenCode logs. Have two independent reviewers apply to same trajectory; if agreement <90% or token counts diverge >5% from provider, definition fails before any full runs.

**MF2 — Fix task bank + randomization + repo-reset protocol**

*   **WHY:** Place-holder examples (L183-251) are not tasks; order confound (I1) and state carryover (I2) guarantee internal-validity failure if run sequentially on same repo.
*   **WHAT:** Based on R1-R4 examples and Sec 13/14. Uncertainty is about *which* 2-3 tasks per class are representative, not whether a bank is needed.
*   **HOW CERTAIN:** Proven — Sec 14 lists classes, not instances.
*   **WHAT-NOT-TESTED:** Does not test external validity (whether bank represents real workload distribution); does not test task difficulty balance.
*   **Cheapest discriminating test:** Instantiate *one task per class* (6 total) with ground truth + oracle. Run same task twice back-to-back without reset vs with `git reset --hard + Serena reindex`; if second run token count differs >10% without reset, contamination is demonstrated and protocol is required.

**MF3 — Operationalize relevance/density with blinded annotation protocol**

*   **WHY:** M4-M6 hinge on `relevant/duplicate/useful` but no rubric exists; current construct will produce experimenter-biased labels (C2).
*   **WHAT:** Based on L332-361 and M4-M6 definitions.
*   **HOW CERTAIN:** Evidence-based — analogous agentic retrieval studies show IRR <0.6 without rubric.
*   **WHAT-NOT-TESTED:** Does not test whether LLM-as-judge could replace human (that is a separate validation); does not test rubric completeness for all task classes.
*   **Cheapest discriminating test:** Write 1-page rubric (relevant = evidence directly supports required proposition; duplicate = semantically identical to already-counted evidence). Have two people independently score 3 sampled retrieval outputs from a pilot run; compute Cohen's kappa. If kappa <0.7, rubric insufficient.

**MF4 — Pre-register statistical decision rule & N per cell**

*   **WHY:** `lower tokens-to-verified-success + no unacceptable correctness regression` (L649-653) is not a decision rule. Without N/alpha/primary statistic/correction, any saving can be claimed.
*   **WHAT:** Based on Sec 16-19. Requires specifying: primary = median tokens-to-verified-success among successes, penalty for failures (e.g., infinite), alpha=0.05 two-sided, power for 20% MDE, multiple-comparison correction (Holm) for Phase 6 interactions.
*   **HOW CERTAIN:** Proven — no thresholds present; guess that 20% is meaningful MDE for this domain (evidence-based: RTK README claims operation-level savings >50% but end-to-end unknown).
*   **WHAT-NOT-TESTED:** Does not test normality; does not test which effect size is practically important to EDASES users.
*   **Cheapest discriminating test:** Take pilot variance from T0 (run T0 n=5 on one task). Compute required N for 20% reduction at 80% power using bootstrap. If required N >15 per cell, full factorial (8+ interactions × 6 task classes) is infeasible — forces scope reduction before committing.

### SHOULD-FIX (high value, not blocking first pilot)

**SF1 — Make R5 classifier explicit and logged, not implicit**

*   **WHY:** Adaptive retrieval's value cannot be attributed if classification is opaque (I5). A bad classifier makes good tools look bad.
*   **WHAT:** Based on L264-286 routing diagram. Approach: pre-tag each task with expected route *or* log agent's explicit `I classify this as lexical/relationship because...` before tool choice.
*   **HOW CERTAIN:** Evidence-based — adaptive selection's benefit is well-documented to be classifier-sensitive.
*   **WHAT-NOT-TESTED:** Does not test whether agent can classify accurately with given prompt; does not test cost of classification itself (extra tokens).
*   **Cheapest discriminating test:** On 6 pilot tasks, have agent emit classification before retrieval; compare to experimenter pre-tag. If mismatch >30% on R1 vs R3 boundary, classifier is the bottleneck, not tool.

**SF2 — Define C2/C3 author & checkpoint mechanics + version the compactor**

*   **WHY:** `compact state` (L375-388) without author/schema is irreproducible; if a human authors it, human skill becomes treatment.
*   **WHAT:** Based on Sec 10-11. Specify: checkpoint every K turns or at phase boundary, author = deterministic script with fixed template, structured handoff = JSON with enumerated fields, script version pinned.
*   **HOW CERTAIN:** Evidence-based — context-compression literature shows summarizer quality dominates effect.
*   **WHAT-NOT-TESTED:** Does not test whether deterministic template is sufficient vs LLM summarizer (deliberately deferred per L411-421, correctly).
*   **Cheapest discriminating test:** Hand-author C2 for one multi-step task (Task C) vs script-generated C2; feed both to fresh agent as C3 handoff. If success diverges, author variance is treatment — freeze author.

**SF3 — Instrument compensatory behavior causally, not anecdotally**

*   **WHY:** L151-160 correctly predicts RTK may cause extra turns but only says `determine whether compression changes agent behavior` without causal instrument.
*   **WHAT:** Based on Sec 5 secondary measurement. Add: log per-turn `output tokens truncated?` + `agent's next action is another shell call?` + `extra turn count`. Pre-register test: RTK ON vs OFF difference in follow-up command rate.
*   **HOW CERTAIN:** Evidence-based — RTK README (ref [2]) reports per-operation savings, not trajectory savings; compensatory effect is plausible but unquantified.
*   **WHAT-NOT-TESTED:** Does not test *why* agent compensates (uncertainty vs missing data).
*   **Cheapest discriminating test:** Pilot T1 vs T2 on Task D (test/debug with large output, L512-513). Count follow-up shell calls. If T2 shows >20% more calls, RTK saving is partially illusory — must report net, not gross.

**SF4 — Separate `same cost + higher reliability` win criterion**

*   **WHY:** Sec 19 secondary win `same token cost + higher reliability` (L657-664) is important but currently conflated with token saving. Needs separate reliability metric (success rate, variance) with its own threshold.
*   **WHAT:** Based on L657-664. Define reliability as `success rate` and `coefficient of variation` of tokens-to-success across repeats.
*   **HOW CERTAIN:** Guess — reliability gain may be more valuable than 10% token saving in EDASES, but not evidenced in doc.
*   **WHAT-NOT-TESTED:** Does not test user value of determinism vs speed.
*   **Cheapest discriminating test:** Report CV for T0 pilot (n=5). If CV >0.4, reliability is a real problem and secondary win criterion matters.

### CONSIDER (improve robustness, low cost)

**CO1 — Pin model temperature=0 and log API version; report stochastic sensitivity as secondary analysis**

*   **WHY:** Reduces variance, increases replicability; temperature>0 inflates required N (S4).
*   **WHAT-NOT-TESTED:** Whether temperature=0 harms agent reasoning quality (test with one Task E architectural investigation).
*   **Test:** Run same task at temp 0 vs 0.7 (n=3 each); if temp 0 success rate drops, keep temp fixed but report sensitivity.

**CO2 — Add cost-in-dollars as secondary metric alongside tokens**

*   **WHY:** Tokens map non-linearly to cost across models; Experiment B (routing) will need dollar cost. Cheap to log now.
*   **WHAT-NOT-TESTED:** Pricing changes.
*   **Test:** Compute dollar cost from pilot token counts × provider pricing; check if rank-order of conditions by tokens matches rank by dollars.

**CO3 — Log wall-time and guard-token overhead as covariates**

*   **WHY:** Guards (L41-48) and Serena startup consume time/tokens not counted in M1; may dominate for small tasks and invert conclusions.
*   **WHAT-NOT-TESTED:** Whether guard overhead is constant.
*   **Test:** Instrument one run with guard token count separated; if guard tokens >15% of trajectory, report condition effects both with/without guard.

---

## 5. Overall Verdict

### **NEEDS REVISION — Underspecified for execution**

**Conceptual design: Strong (B+).** Narrow scope, mechanism decomposition, compensatory-behavior awareness, failure tests, and interaction taxonomy are well-reasoned and reflect genuine research synthesis. The central principle (L779) — *ask which information the model actually needed* — is the right framing.

Path to ready is ~1–2 days specification work to close MF1–MF4 plus a 6-task pilot to calibrate variance, verify instrumentation, and lock N.
