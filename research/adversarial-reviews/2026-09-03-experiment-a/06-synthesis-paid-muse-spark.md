# Synthesis — Five Adversarial Reviews of Experiment A v2 (Paid)

**Synthesizer:** muse-spark-1.3-contributor (opencode-go, paid, verified via `opencode models opencode-go`, operator approved)
**Date:** 2026-09-03
**Source reviews (independent, zero-context, read-only):**
- 01 — `opencode/big-pickle` (free)
- 02 — `nemotron-3-ultra-free` (free)
- 03 — `laguna-s-2.1-free` (free)
- 04 — `muse-spark-1.3-free` (free)
- 05 — `ling-3.0-flash-fin-free` (free; substitution disclosed — requested `ling-3.0-flash-free` not in 66-model catalog)

**Target document:** `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2, 2026-09-03)
**Scope disclosure:** Synthesis is read-only; no edits to target. Sol feedback (`research/Sol A and B feedback.md`) not yet integrated — see `07-integrated-synthesis-with-sol.md`.

---

## 0. Method

Five reviewers read the 784-line document independently with no prior context and no cross-reviewer communication. Paid synthesis reconciles findings without re-running analysis, preserving reasoning per `AGENTS.md` (observations / assumptions / findings / decisions distinguished; evidence not presented as methodology).

**Certainty vocabulary:** guess = plausible but unevidenced in this doc; evidence-based = supported by analog studies or partial doc evidence; proven = textual contradiction or directly inspectable gap in this doc.

---

## 1. Convergent Strengths — S1–S8 (5/5 reviewers, independently observed)

These are durable assets; revision must preserve them verbatim.

| # | Strength | Location | Why It Matters |
|---|----------|----------|----------------|
| **S1** | **Narrow causal isolation — one agent / one model / one task / one role; vary only tooling/context** | `2:27-51` + `21:721-737` | Prevents Sol/orchestrator/routing confound that broke v1. Correct identification strategy. |
| **S2** | **A/B/C orthogonalization: Avoid / Retrieve higher-density / Compress retained** | `3:57-93` | `RTK, Serena and context summarization are not competing versions of the same thing` `3:91-93` is the strongest sentence — prevents naive "optimized agent" confound. |
| **S3** | **Gated primary metric `tokens-to-verified-success` + anti-Goodhart stance** | `1:21-23` `16:556-565` `5:165-166` | `Never treat RTK's own savings counter as result`; correctness gate prevents proxy optimization. |
| **S4** | **Compensatory behavior as first-class outcome** | `5:149-162` | "less output → follow-up command → extra turn" pre-registered; most RTK studies fail here. |
| **S5** | **Task-conditional retrieval economics R1-R4** | `6:177-254` | "Lexical should dominate localization" stated as falsifiable hypothesis `6:195-201`, not assumption. |
| **S6** | **Adaptive R5 + evidence-based stopping R6 isolated before combination** | `7:258-287` `8:290-327` | Tests avoidance independent of density — more valuable than tool bake-off. |
| **S7** | **Deterministic compact state first C2/C3** | `10:368-406` `11:410-424` | `Do not prematurely optimize the summary format` — establishes sufficiency before representation optimization. |
| **S8** | **Interaction taxonomy + adversarial classes E/F** | `12:451-471` `14:516-522` `15:527-551` | Additive/Redundant/Compensatory/Synergistic + misleading matches / generated files / stale results prevents trivial-task Goodharting. |
| — | Phased sequence Baseline→RTK→Retrieval→Adaptive→Stopping→Compression→Interactions→Adversarial `22:742-776` | — | Correct cheapest-test-first ordering (noted by 3/5 explicitly, implicit in all). |

**Reviewer agreement:** 5/5 marked S1-S4; 5/5 marked S2 or equivalent; 4/5 explicitly listed S5-S8 with S7 noted as "deliberate simplicity" by Nemotron and Laguna independently.

---

## 2. Convergent Blockers — C1–C10 (unanimous or near-unanimous)

| # | Blocker | Aggregate Finding | Location | Certainty | Consequence |
|---|---------|-------------------|----------|-----------|-------------|
| **C1** | **Verified-success denominator undefined** | `tokens-to-verified-success` — no per-task oracle (tests/lint/typecheck/gold diff/audit) and no numeric non-inferiority margin for "unacceptable correctness regression" | `16:556-594` `19:646-664` | **proven** — no definition present (all 5) | Token comparison meaningless; any failure rate makes metric incomputable or gameable |
| **C2** | **Useful/relevant/duplicate density subjective** | `useful evidence / context tokens` `9:346` + M4-M6 require rater but no rubric, no blinding, no IRR, no tokenizer | `9:330-361` `16:573-585` | **proven** | Construct collapses to investigator judgment |
| **C3** | **Token accounting ambiguous** | System/guard/tool raw vs post-RTK/reasoning inclusion; measurement point (guard vs model API) unspecified; `where measurable` `4:119` is loophole | `4:101-119` `5:138-147` `16:566-572` | **proven** | Replication impossible; accounting choice flips RTK conclusion |
| **C4** | **No N / power / alpha / ROPE / SAP / multiplicity** | `multiple times where practical` `13:475` + `several representative tasks` `13:490` not specifications; no power for heavy-tailed tokens; no alpha; no family-wise correction for 7 interactions ×6 classes =84 cells | `13:473-491` `19:646-677` | **proven** | Anecdotal wins; inflated false-positive rate; p-hacking |
| **C5** | **Repo / cache contamination + no randomization** | No `git worktree` reset, no Serena/FS invalidation, no Latin square / counterbalancing | `13:473-491` | **proven** | Sequential phases confound treatment with order/state |
| **C6** | **Model stochasticity unpinned** | No temperature/seed/top_p/max_tokens/model version pin | `2:37-38` `13:487-489` | **proven** | Sampling noise can exceed hypothesized effect |
| **C7** | **Hold-constant contradiction** | `model settings` fixed `2:37-38` vs `dynamic-models` active `2:43-47` | `2:30-48` | **proven** (textual contradiction, flagged by Big-Pickle & Laguna & Nemotron) | Silent per-task mutation = hidden treatment |
| **C8** | **R5 / R6 / C2 enforcement violates §2** | R5 routing, R6 sufficiency, C2 checkpoint+compaction author not specified — if self-judged, tautology; if human, hidden labor | `7:262-284` `8:302-324` `10:375-404` | **evidence-based** (all 5 flagged; tautology risk proven by text) | Tests agent compliance, not mechanism |
| **C9** | **No concrete task suite / oracle** | Classes A-F `14:494-523` are placeholders; zero concrete tasks, file paths, ground truth, difficulty, holdout | `14:494-523` `6:182-184` | **proven** | Cannot sample, randomize, stratify — selection bias 100% |
| **C10** | **Single-repo narrow external validity** | One repo + one model + synthetic placeholders → claim `1:11` "software-engineering work" and `21:735` "baseline for Experiment B" overgeneralizes | `1:11` `21:735` `6:182-251` | **evidence-based** | Generalization not supported; needs disclosure as limitation |

**Additional convergent threats (4/5):** T0/T2 identity confusion (`4:96-120` vs `5:129-135`; T0 already includes rtk-guard), guard injection `2:41-48` unmeasured, wall-time confounded by free-tier latency, failure injection `15:527-550` not operationalized.

---

## 3. Divergent Insights (Not Universal — Value-Add From Specific Reviewers)

* **Big-Pickle unique:** Quantified multiplicity explosion numerically (~84+ cells, free-tier infeasible with N=3 → 250+ runs) and proposed concrete N=10/N=5 split; added SF4 adaptive bounding rule (>10% single-mechanism gate). Most actionable statistical framing.
* **Nemotron unique:** Explicit I4 experimenter-as-instrument bias (scorer sees condition label) and C5 folk-schema point; most detailed data-recording schema gap (13 vs 8 items); CO1-CO3 guard-token and dollar-cost suggestions.
* **Laguna unique:** Cleanest MF table with M1-M9 mapping to locations; SF2 density rubric with automated heuristic + Spearman validation — best construct-validity fix.
* **Muse-Spark-Free unique:** Emphasized T0/T2 collapse resolution and guard-isolation as SHOULD-FIX; most concise MF-approach.
* **Ling-Fin unique:** Substitution disclosure model; compactness of argument useful for operator-facing summary.

No divergent insight contradicts convergent blockers; all extend MF set.

---

## 4. Consolidated MUST-FIX List — MF-1 to MF-9

Each item states WHY (reasoning), WHAT (basis), HOW CERTAIN, WHAT-NOT-TESTED, cheapest discriminating test — per `AGENTS.md` certainty style for key recommendations that cross producer→consumer boundary. All MF items are **blocking — cannot claim a result without**.

| # | Title (Blocker) | Location | Fix | WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED | Cheapest Discriminating Test |
|---|-----------------|----------|-----|---------------------------------------------|------------------------------|
| **MF-1** | **Operationalize verified-success + non-inferiority margin** | `16:590-595` `19:646-664` | Per-task verification script: `tests + lint + typecheck + gold output diff` + blinded human audit of out-of-scope edits. Margin: success rate drop >5% absolute (Wilson CI) or any critical-path invariant failure = reject. Pre-register per task. | **WHY:** tokens are meaningless without correctness gate that prevents proxy Goodhart. **WHAT:** non-inferiority methodology + EDASES verification needs. **HOW CERTAIN:** proven — gap inspectable, proven harm in prior studies. **WHAT-NOT-TESTED:** oracle itself gameable; does not test verification gaming. | Write 2 pilot oracles (1 localization, 1 multi-file); two independent raters blind to script; if inter-rater κ<0.8 or script-rater disagreement, spec insufficient — fail fast (<1 hr). |
| **MF-2** | **Instantiate concrete task bank** | `14:494-523` `6:182-251` | ≥18 tasks (≥3 per class A-F), each with: repo commit pin, file scope, ground-truth patch/answer, verification script, fails-without baseline, difficulty stratum from T0 pilot median tokens, 2 holdout tasks never used during design. | **WHY:** abstract classes cannot be randomized, scored, or stratified — selection bias 100%. **WHAT:** experimental design evidence on class×tool interaction (R1-R4). **HOW CERTAIN:** proven — zero instances present. **WHAT-NOT-TESTED:** cross-repo generalization. | Pilot 1 task per class ×3 runs on T0 (6 tasks, 18 runs); if any class shows floor (<500 tokens) or ceiling (100% fail), class mis-calibrated — revise before scaling (2-3 hr). |
| **MF-3** | **Pre-register N / randomization / statistical analysis plan** | `13:473-491` `16:556-595` | N=10 runs/condition for 2 primary contrasts (T1 vs T2, R5 vs single-tool), N=5 for interaction cells; Latin square counterbalancing; seed pin where supported else report seedless variance; primary = bootstrap 95% CI on `expected tokens per verified success = mean(tokens)/success_rate`; secondary median+IQR; win iff CI excludes ROPE ±10% tokens AND correctness non-inferior; Holm correction across task classes; adverse stopping if success drops >10% after n=5. | **WHY:** "where practical" guarantees post-hoc wins for heavy-tailed, stochastic LLMs. **WHAT:** best practice for stochastic LLMs; tokens heavy-tailed. **HOW CERTAIN:** evidence-based (heavy tails empirical). **WHAT-NOT-TESTED:** provider drift beyond sampling. | Simulate power: assume σ≈0.4×mean, compute N for 20% reduction @80% power; if N>budget, reduce conditions now (30 min, no execution). |
| **MF-4** | **Instrument token accounting at model API boundary** | `4:101-118` `16:566-588` | Define `trajectory tokens = Σ(system+user+tool_output_post_filter+assistant)` per turn as seen by model API; log raw vs compressed tool output separately; log tool_calls, follow_up_calls, additional turns; instrument in guard not agent self-report; store per-run JSON in durable store; guard tokens separated. | **WHY:** RTK savings at shell ≠ savings at model boundary — accounting flips conclusions. **WHAT:** direct measurement principle; `5:165-166` acknowledges gap. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** embedding/cache outside model. | One T0 run: compare guard-reported RTK saving vs API-input delta; if divergence >15%, accounting broken (1 hr). |
| **MF-5** | **Specify who/what enforces R5 / R6 / C2** | `7:262-284` `8:302-324` `10:375-404` | R5 routing = prompt rule + post-hoc logged classification `classify: lexical/relationship because…` (agent-autonomous, not hard router) vs documented; R6 sufficiency = external checklist not self-report; C2 checkpoint = deterministic rule (every file edit or 5 tool calls) with versioned JSON schema for `objective/constraints/known facts/relevant files/completed/tests/unresolved/next`; compaction by script (versioned), cost reported separately (not hidden labor). | **WHY:** self-judgment tautology tests compliance not mechanism. **WHAT:** construct validity for stopping. **HOW CERTAIN:** evidence-based (LLM self-judgment overconfident). **WHAT-NOT-TESTED:** checklist misses decision-critical info — E/F tests this. | Write 1-page R2 checklist; agent R6a vs R6b on same task; if R6b never escalates despite missing evidence, trigger insufficient (1 hr). |
| **MF-6** | **Freeze tool & model boundaries** | `5:129-147` `2:41-48` `7:262-284` | Pin RTK compression rules/level, Serena/LSP version+prompt, LSP config, rg flags, model ID (e.g., `opencode-go/muse-spark-1.3-contributor`), temperature=0, seed, max_tokens, API version; log guard interventions; disable or log `dynamic-models` mutations per §2 hold-constant repair. | **WHY:** any filter-list or prompt change is a different condition. **WHAT:** replicability. **HOW CERTAIN:** proven — conditions not versioned. **WHAT-NOT-TESTED:** provider-side model drift mid-phase. | Two sequential T0s without reset vs fresh-clone; if >10% divergence, reset mandatory; query model version pre/post phase. |
| **MF-7** | **Isolate repo / cache / state per run** | `13:473-491` `14:494-523` | Immutable starting commit; isolated `git worktree` per run + `git clean -fdx` + DB reset + Serena reindex + inter-run washout; randomized condition order (Latin square); hidden verification where possible; `useful evidence` rubric with blinded scorer. | **WHY:** multi-file tasks mutate repo; caches carry over. **WHAT:** internal validity. **HOW CERTAIN:** proven — no reset procedure present. **WHAT-NOT-TESTED:** whether holdout tasks leak via evaluator knowledge. | One task twice: without reset vs with reset+reindex; if token diff >10%, protocol required (1 hr). |
| **MF-8** | **Operationalize information-density with rubric + IRR** | `9:330-361` `16:573-585` | Define `useful` = returned lines that appear in final patch, gold evidence set, or verification diff (automatable); duplicate = semantically identical to already-counted; blinded rater audits 10% sample; targets Spearman ρ>0.7 / Cohen κ>0.7; tokenizer specified (provider billing tokenizer). | **WHY:** M4-M6 otherwise experimenter-biased. **WHAT:** analogous studies show κ<0.6 without rubric. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** semantic usefulness not surfacing in patch. | Hand-label 5 retrievals vs heuristic; if ρ<0.7, heuristic invalid (1 hr). |
| **MF-9** | **Bound interaction phase adaptively; pre-register failure injection** | `12:440-450` `15:527-550` `22:742-776` | Do not obligate full 2⁴ factorial. Rule: full factorial only if each single mechanism shows >10% effect in Phases 1-5; else test only `T2+R6` and `R5+C2` plus final combined (2 most complementary pairs) — saves ~60% runs. Failure injection: 6 pre-defined cases (misleading match, duplicate impl, generated file, comment-only ref, stale test, incomplete handoff) as task variants scored `detect uncertainty → retrieve → correct → verify` pass/fail. | **WHY:** full factorial impractical on free tier; adversarial tests without protocol become anecdotes. **WHAT:** redundancy hypothesis `12:458-460`; failure taxonomy. **HOW CERTAIN:** evidence-based / guess for injection realism. **WHAT-NOT-TESTED:** injection realism. | Estimate run budget tokens×N×conditions; if >free-tier quota, adaptive bound mandatory; pilot one misleading-match injection (1 hr). |

**Conflict resolutions (where reviewers flagged contradictions):**

* **T0/T2 collapse:** T0 ("current normal workflow" includes `rtk-guard` `5:135`) ≡ T2 (RTK ON). Resolution: collapse T0 into T2; define T1=RTK OFF (bypass `rtk-guard`), T2=RTK ON; retain T0 only as non-experimental warm-up calibration if needed. All 5 reviewers noted; resolution is deterministic (not a judgment call).
* **Hold-constant vs treatment:** §2 list claims `model settings` fixed while §2 infrastructure lists `dynamic-models` active. Resolution: carve out MF-5/MF-6 — explicitly disable `dynamic-models` mutation during Experiment A or log every mutation as covariate; pin versions; treat any unlogged mutation as protocol violation.
* **Token boundary:** Guard-reported RTK savings vs model API delta. Resolution: MF-4 — primary is API boundary; guard counter is diagnostic covariate only.

---

## 5. Revision Plan — 3–4 Days + 1-Day Pilot (Cheapest-Test-First Order)

| Day | Work | Output | Fail-fast test |
|-----|------|--------|----------------|
| **Day 0 (0.5 hr)** | Simulate power + budget estimate (MF-3) | N per cell, run budget, feasibility | If N>budget, immediately cut conditions (adaptive bound) |
| **Day 0 (1 hr)** | Instrument token accounting at API boundary (MF-4) | Logging in guard, per-run JSON schema | Guard vs API delta >15% → fix before any condition |
| **Day 1** | Operationalize verified-success oracles + margin (MF-1) + instantiate task bank skeleton (MF-2, 6 pilot tasks) | 6 concrete tasks (1×A-F) with ground truth + oracles | Two raters κ<0.8 → oracle insufficient |
| **Day 2** | Freeze tool/model boundaries (MF-6) + isolate repo/reset protocol (MF-7) + enforce R5/R6/C2 spec (MF-5) + density rubric (MF-8) | Version pins, reset script, routing checklist, compact-state JSON schema v1 | T0×2 without vs with reset >10% → protocol required; R6b never escalates → trigger wording fails |
| **Day 3** | Pre-register SAP with ROPE/Holm/adverse stopping (MF-3) + bound interactions (MF-9) + failure injection cases | Written SAP document, interaction test list, 6 injection variants | Budget >free-tier → adaptive bound forced |
| **Day 4** | **Pilot:** 6 tasks ×3 runs on T1 vs T2 + R5 contrast (36-42 runs) + measure follow-up command rate, CV, guard overhead | Pilot results: variance estimate, effect size ballpark, compensatory rate | If CV>0.4, secondary reliability win matters; if T2 extra calls >20%, net saving illusory — revise R6 threshold |
| **Then** | Decide GO/NO-GO for full Phase 1-6 based on pilot CI width + correctness gate | Full experiment or scope cut | — |

**Estimated cost before full experiment:** ~3–4 days spec work + ~1 day pilot execution + logging instrumentation. No model-heavy runs before MF-3/MF-4 checks.

---

## 6. Readiness Checklist — When Is Experiment A Ready To Run?

- [ ] MF-1: ≥18 tasks each have per-task verification script + non-inferiority margin defined; two-rater pilot κ≥0.8
- [ ] MF-2: Task bank instantiated, commit pin + ground truth + fail-without baseline + difficulty stratum + 2 holdout
- [ ] MF-3: SAP written with N per cell, Latin square order, seed, primary (`expected tokens per verified success`), median+IQR secondary, ROPE ±10%, Holm, stopping rule
- [ ] MF-4: Token logging at API boundary verified; guard vs API delta <15% on T0 pilot; per-run JSON schema validated
- [ ] MF-5: R5 classification logged, R6 external checklist, C2 checkpoint rule + versioned JSON schema + script compactor
- [ ] MF-6: RTK rules, Serena/LSP, rg flags, model ID pinned; `dynamic-models` disabled/logged
- [ ] MF-7: `git worktree` reset + `git clean -fdx` + Serena reindex per run; condition order randomized
- [ ] MF-8: Density rubric written; pilot hand-label vs heuristic ρ≥0.7 / κ≥0.7; tokenizer specified
- [ ] MF-9: Interaction bounding rule + failure injection cases defined; run budget fits quota
- [ ] Pilot (Day 4) completed: CI width estimated; compensatory rate measured; guard overhead quantified

---

## 7. Final Verdict — 5-Review Synthesis

**NEEDS REVISION — operationally not executable as written; conceptually close to runnable.**

* **Conceptual strength unanimous (5/5):** S1-S8 are genuine research contributions. Central principle `22:779` — *ask which information the model actually needed, how cheaply it could obtain it, and how quickly the system could stop carrying it* — is correct and should be preserved verbatim.
* **Operational readiness unanimous (5/5):** C1-C10 block execution. No reviewer judged the document runnable without MF-1 to MF-5 at minimum. Risk if executed as-is: anecdotal/underpowered claims, non-replicable token counts, selection bias, illusory RTK/Serena wins that vanish under proper `expected tokens per verified success` denominator, free-tier variance swamping signal.
* **Path to ready:** MF-1 through MF-9 as listed; 3–4 days spec + 1 day pilot converts the design to a publishable tooling-efficiency experiment. MF-3/MF-4 checks must precede data collection (cheapest-test-first).
* **What remains excellent regardless:** A/B/C framing, compensatory measurement, fixed-agent discipline, phased ordering, policy output `20:683-716` — all retained.

**Recommendation to operator:** Do not run Phase 1 data collection until readiness checklist is fully checked. Landing these reviews plus the integrated Sol synthesis (`07`) satisfies the adversarial-review gate; next step is MF remediation.

---

*Synthesized by muse-spark-1.3-contributor (paid, opencode-go). Synthesis preserves headings, tables, and reasoning from source reviews; compresses only where duplication existed. No new empirical claims introduced beyond reconciliation.*
