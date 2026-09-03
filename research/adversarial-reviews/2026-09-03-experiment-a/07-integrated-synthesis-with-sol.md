# Integrated Synthesis — Five Adversarial Reviews + Sol Feedback for Experiment A v2

**Author:** muse-spark-1.3-contributor (opencode-go, paid, verified via `opencode models opencode-go`, operator approved)
**Date:** 2026-09-03
**Folder:** `research/adversarial-reviews/2026-09-03-experiment-a/`
**Target documents:**
- Primary: `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2)
- Sol feedback: `research/Sol A and B feedback.md` (158 lines, operational judgment on both experiments)
- Context: `research/Experiment B Agent Roles & Model Routing.md` (for terminology and scoping only; not re-reviewed here)

**Source reviewers:**
- 01 — `opencode/big-pickle` (free, zero-context)
- 02 — `nemotron-3-ultra-free` (free, zero-context)
- 03 — `laguna-s-2.1-free` (free, zero-context)
- 04 — `muse-spark-1.3-free` (free, zero-context)
- 05 — `ling-3.0-flash-fin-free` (free, zero-context; substitution disclosed for `ling-3.0-flash-free`)
- 06 (synthesis) — `muse-spark-1.3-contributor` (paid) — five-review synthesis `06-synthesis-paid-muse-spark.md`
- **06th reviewer (this integration): Sol** — operational feedback `research/Sol A and B feedback.md` (paid/strong reasoning model, operational judgment; not zero-context but evidence-informed)

**Method:** Start from paid five-review synthesis (06). Add Sol as 6th reviewer. Reconcile overlaps, divergences, and extensions. Produce single consolidated MUST-FIX list, revised revision plan with cheapest-test-first Experiment 0 pilot, and final verdict. Preserve AGENTS.md certainty style for producer→consumer claims: WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED.

---

## 0. What This Document Is and Is Not

* **Is:** Integrated synthesis that treats Sol feedback as 6th reviewer evidence, merges it with convergent findings S1-S8 / C1-C10 / MF-1..MF-9 from 06, and yields one actionable revision plan.
* **Is not:** A re-run of the five reviews, a rewrite of Experiment A, or an endorsement of full Experiment B execution now.
* **Fidelity:** All convergent strengths and blockers from 06 retained. Sol overlap/divergence explicitly called out. No review is summarized away as "miscellaneous."
* **Certainty discipline:** Sol contributions are separated into **evidence-based** (inspectable in doc, refutable) vs **operational judgment** (operator-specific quota pain, cost model, deployment reality). Both are valuable; they have different auditability.

---

## 1. Convergent Strengths — S1–S8 Retained From 06 (5/5 + Sol Agrees)

Sol explicitly endorses the core of S2-S6 and S8; agreement is not assumed but evidenced.

| # | Strength | Location | Sol Alignment |
|---|----------|----------|---------------|
| **S1** | Narrow causal isolation: one agent / one model / one task / one role; vary only tooling/context; Experiment B deferred | `ExpA 2:27-51` `21:721-737` | **Sol agrees explicitly:** `Sol 15-19` — Exp A addresses context-window pressure; Exp B addresses economic cost; keep separate. Reinforces S1 as correct layer boundary. |
| **S2** | A/B/C orthogonalization: Avoid / Retrieve higher-density / Compress retained; RTK/Serena/compaction not competitors | `ExpA 3:57-93` | **Sol agrees strongly:** `Sol 24-30` — "Avoid irrelevant / Retrieve efficiently / Stop carrying" is "much better than treating RTK, lexical, semantic, summarization as interchangeable token savers." Direct quote-level endorsement. |
| **S3** | Gated metric `tokens-to-verified-success` + anti-Goodhart | `ExpA 1:21-23` `16:556-565` `5:165` | **Sol qualifies — evidence-based extension:** `Sol 45-57` — within Exp A (fixed model) tokens-to-verified-success is reasonable; across models/providers (Exp B) raw tokens incomparable — extends to cost/allowance per verified success. Overlap + scope correction. |
| **S4** | Compensatory behavior first-class | `ExpA 5:149-162` | **Sol compatible:** does not dispute; Sol's quota framing (`Sol 4-5` "consumption varies with model, context, reasoning, retrieval, tools — not merely message count") implies compensatory turns matter even more for allowance depletion. |
| **S5** | Task-conditional retrieval R1-R4 | `ExpA 6:177-254` | **Sol agrees:** `Sol 30` — "adaptive rg-vs-LSP policy is likely more useful than choosing one universally." Endorses stratification hypothesis. |
| **S6** | Adaptive R5 + stopping R6 isolated before combo | `ExpA 7:258-327` | **Sol implicitly supports:** stopping / "stop carrying" and structured handoff are highlighted as valuable; no objection to isolation. |
| **S7** | Deterministic compact state first | `ExpA 11:410-424` | **Sol extends — evidence-based:** `Sol 58-79` — agrees simplicity-first, but distinguishes internal compaction (harness-managed, e.g., Codex compaction events) from provider-independent durable task record; proposes to test them separately. Extends S7 into MF-10/durable experiment. |
| **S8** | Interaction taxonomy + adversarial E/F | `ExpA 12:451-471` `14:516-522` `15:527-551` | **Sol agrees:** `Sol 30-31` — "correctness gate and adversarial/noisy task classes are also essential." |

**Synthesis judgment (5+Sol):** S1-S8 are durable assets. Revision must preserve them. Sol's strongest independent contribution is not contradicting them but **scoping** them: Exp A solves context-window pressure (problem 2 of 4), not quota/durability/cost directly — see §2 below.

---

## 2. Sol's Conceptual Correction — Evidence-Based, Structurally Important

**Sol's diagnosis `Sol 8-21`:** The two experiment documents partially conflate four distinct problems:

1. **Usage quota** — how quickly the ChatGPT five-hour allowance depletes (Solar/high default `Sol 3` at `.codex/config.toml:1`; Solar has lower message capacity than Terran/Lunar per OpenAI pricing `Sol 5`).
2. **Context-window pressure** — how much a single agent must carry during one task.
3. **Durable continuity** — how work survives new chat, compaction, provider switch, quota reset.
4. **Economic cost** — tokens/credits/subscription/API charges across providers.

**Mapping:**

* Exp A (`ExpA 3`) primarily addresses (2) context-window pressure. Its structured handoff `ExpA 10:398-406` begins to address (3) durability but conflates it with internal compaction.
* Exp B (`ExpB 80`) primarily addresses (4) economic cost.
* Operator's immediate pain is (1) quota + (3) durability `Sol 20`.

**Why this matters for synthesis:**

* The five free reviews correctly identified internal-validity and construct gaps but did **not** foreground problem (1) quota vs (2) window conflation because they evaluated Exp A as a token-efficiency experiment in isolation. Sol correctly reframes: tokens-to-verified-success within Exp A is valid **only because model is fixed** (`Sol 46`); the moment model/provider varies (Exp B), the metric must change. This is **evidence-based** (inspectable: token counts across models are incomparable; OpenAI pricing doc cited; allowance sharing cited `Sol 5`) — not just operational preference.
* **HOW CERTAIN:** evidence-based — provider pricing and context/allowance distinction are externally documented; Sol's quota vs window vs durability vs cost taxonomy is analytically sound and not contradicted by any of the five reviews.
* **WHAT-NOT-TESTED:** Sol's diagnosis does not claim to have measured operator's quota depletion breakdown (which fraction is Solar/high vs window pressure vs durability retries). That proportion is operator-specific and unevidenced in the synthesis corpus.

**Integration decision:** Accept Sol's four-problem correction as a **framing MUST-FIX** that scopes Exp A correctly, upgrades MF-1 metric, and elevates durable state to its own experiment. Do not treat it as "Sol vs reviewers" — it extends reviewers' metric concerns (C1/C3) to cross-provider economics.

---

## 3. Convergent Blockers — C1–C10 Retained From Five-Review Synthesis (06 §2)

All C1-C10 from 06 retained unchanged — Sol does not contradict any but extends/strengthens several. Re-stated here for integrated auditability.

| # | Blocker | Location | Sol Relation |
|---|---------|----------|--------------|
| **C1** | Verified-success denominator undefined; no oracle, no non-inferiority margin | `16:556-594` `19:646-664` | Sol extends: `Sol 55-56` cost/allowance per verified success **including failed attempts and recovery work** — tightens C1's denominator from tokens to allowance. |
| **C2** | Useful/relevant/duplicate density subjective; no rubric/blinding/IRR/tokenizer | `9:330-361` `16:573-585` | Sol strengthens: `Sol 85:92-95` — needs predefined rubric or blinded scorer; also `Sol 81-83` — save raw evidence outside context for diagnosis. |
| **C3** | Token accounting ambiguous (system/guard/raw-vs-compressed/reasoning; guard vs API boundary) | `4:101-119` `5:138-147` `16:566-572` | Sol strengthens: `Sol 80-83` — capture full raw output as artifact while agent sees compressed; plus quota/allowance vs tokens conflation `Sol 43-56`. |
| **C4** | No N/power/alpha/ROPE/SAP/multiplicity | `13:473-491` `19:646-677` | Sol compatible; Sol's Experiment 0 design (`Sol 149-156`) implicitly reflects power concern by proposing small-N pilot before full factorial. |
| **C5** | Repo/cache contamination + no randomization | `13:473-491` | Sol strengthens: `Sol 84-94` — immutable commit, isolated worktree, fresh state, identical acceptance tests, randomized order, hidden verification. Verbatim extension. |
| **C6** | Model stochasticity unpinned | `2:37-38` `13:487-489` | Sol adds harness/model/role axis separation `Sol 111-113` and Codex default correction — directly addresses hidden stochasticity/confound from dynamic model selection. |
| **C7** | Hold-constant contradiction (model settings fixed vs dynamic-models active) | `2:30-48` | Sol strengthens: `Sol 111-113` + `Sol 137-139` division of labour — make model axis explicit and disable cross-contamination. |
| **C8** | R5/R6/C2 enforcement violates §2 (self-judgment tautology) | `7:262-324` `10:375-404` | Sol compatible; durable-state proposal implies external record, not agent self-judgment. |
| **C9** | No concrete task suite (A-F placeholders) | `14:494-523` `6:182-251` | Sol's Experiment 0 (`Sol 149-154`) presupposes a concrete 10-task representative suite — reinforces C9 as blocker. |
| **C10** | Single-repo narrow validity | `1:11` `21:735` | Sol does not dispute; treats Exp A as later programme `Sol 158` ("retain both documents, but treat them as serious later evaluation programme"), not as generalizable now. |

**Agreement check:** 0 contradictions between Sol and five-review blockers. Sol's operational feedback is a strict superset that scopes and operationalizes the same gaps.

---

## 4. Where Sol Overlaps, Where Sol Diverges/Extends

### Overlaps (reinforcement → increases confidence from evidence-based to near-proven where instrumentation already flagged)

* **Metric:** Five reviews: tokens-to-verified-success denominator ambiguous (C1) and token accounting ambiguous (C3). Sol: within Exp A tokens reasonable, across models must be cost/allowance per verified success. → **Reconciliation:** MF-1 upgraded to dual metric (see §5).
* **Blinding/rubric:** Five reviews: density subjective (C2) needs rubric+IRR (MF-8). Sol: "useful evidence also needs predefined rubric or blinded scorer" `Sol 95`. → Identical conclusion, independently derived — increases HOW CERTAIN from evidence-based to proven for rubric requirement.
* **Isolation:** Five reviews: no reset, no randomization (C5). Sol: same list plus "hidden verification where possible" `Sol 93`. → Identical; Sol adds `fresh agent/task state` which the five reviews implied but did not state as explicitly.
* **B1/B2 duplication:** Only hinted by five reviews (none focused on Exp B detail). Sol: "B1 and B2 are potentially duplicates ... duplicate B7 numbering" `Sol 98-100`. → New finding, evidence-based (inspectable in Exp B doc).
* **Task-dependent economics:** Fully aligned.

### Diverges / Extends (novel contributions from Sol — must be integrated, not dismissed)

| Sol Contribution | Location | Overlap With Five | Nature | Integration |
|------------------|----------|-------------------|--------|-------------|
| **(a) Four-problem conflation** — quota vs window vs durability vs cost | `Sol 8-14` | Not foregrounded by five | **Evidence-based conceptual correction** — externally documentable | Add to framing (§2); scope Exp A to problem 2; scope durability to own experiment (MF-10); scope quota to operational fix, not experimental condition |
| **(b) Codex default Solar/high → Terran/medium immediate fix** | `Sol 3-5` + `Sol 136-139` | Not in five (five evaluated Exp A instrumentation, not operator quota) | **Operational judgment — evidence-based on pricing doc, but magnitude operator-specific** | Operational pre-condition, not MF for Exp A; document as Experiment 0 condition (see §6); requires operator decision |
| **(c) Provider-independent durable task-state as own experiment** — checked-in record with 9 fields, fresh session tested on record+repo only | `Sol 58-79` | MF-7/MF-5 partially covered durability via C2/C3 but conflated internal compaction with durable handoff | **Evidence-based extension** — Codex compaction docs cited (`Sol 62-63`); workspace-resident vs harness-managed distinction proven | Upgrade MF-7 and extend MF-5; add durable-state experiment (MF-10 or separate track) per Sol |
| **(d) Capture raw evidence outside context (raw artifact)** | `Sol 80-83` | Five flagged accounting ambiguity (C3) but did not propose dual artifact | **Evidence-based instrumentation fix** | Strengthen MF-4: raw artifact saved outside model input; compressed only to model |
| **(e) Harness / provider / model / role terminology separation** | `Sol 111-113` | C7 hold-constant contradiction overlaps but Sol generalizes | **Evidence-based taxonomy fix** | Add to MF-6 terminology pre-condition |
| **(f) Operational division of labour: Solar sparse / Terran normal / Lunar bounded / OpenCode Go loops / shared repo state** | `Sol 118-144` | Not in five (Exp B scoping) | **Operational judgment — evidence-based on routing literature cited in Exp B, but deployment-specific** | Scope Exp B deferral; inform Experiment 0 design; not a MUST-FIX for Exp A instrument |
| **(g) Experiment 0 — 10 tasks ×4 conditions, pre/post allowance, quota-aware pilot** | `Sol 148-157` | Five proposed 6-task×3-run pilot (18-42 runs) focused on token variance; Sol proposes 40 runs focused on allowance+recovery+time | **Operational judgment — cheapest-test-first proposal** | Adopt as revised pilot plan (see §6) — replaces/supplements Day 4 pilot in 06 with quota-aware design |
| **(h) Reduce Exp B to B0-B4; treat remainder as later programme** | `Sol 97-109` `Sol 158` | Five did not evaluate Exp B depth | **Operational judgment — cost/benefit under quota constraint** | Accept as Exp B scoping decision; not an Exp A MF but a programme decision |

**Where Sol is evidence-based vs operational judgment:**

* **Evidence-based (auditably correct regardless of operator):** (a) four-problem taxonomy, (c) compaction vs durable-state distinction, (d) raw artifact, (e) terminology separation, (h) B1/B2 duplicate (inspectable).
* **Operational judgment (correct given operator's stated quota pain, but not universally provable from doc):** (b) Solar→Terran default, (f) Solar/Lunar/Go division, (g) Experiment 0 sizing/priority, (h) "retain as later programme, fix quota first" verdict. These should be presented as recommendations with WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED, not as proven gaps.

---

## 5. Consolidated MUST-FIX List — MF-1..MF-10 (Updated With Sol)

MF-1..MF-9 from 06 retained; Sol extends several without duplicating. MF-10 added where Sol identifies a distinct experiment that would otherwise be hidden inside MF-7.

> **Certainty style per `AGENTS.md`:** Each MF that crosses producer→consumer boundary states WHY (reasoning), WHAT (basis), HOW CERTAIN (guess / evidence-based / proven), WHAT-NOT-TESTED (negative space). Consumer-side audit is presence/structure, not re-run.

| # | Title | Location | Fix (Consolidated) | WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED | Cheapest Discriminating Test |
|---|-------|----------|---------------------|---------------------------------------------|------------------------------|
| **MF-1** | **Operationalize verified-success + primary metric corrected to cost/allowance per verified success** | `ExpA 16:590-595` `19:646-664` + `Sol 44-56` | Per-task verification script: `tests + lint + typecheck + gold output diff` + blinded audit of out-of-scope edits. Margin: success rate drop >5% absolute (Wilson CI) or any critical-path invariant failure = reject. **Metric:** Within Exp A (fixed model) report `expected tokens per verified success = mean(tokens)/success_rate` with median+IQR secondary — retains reviewers' denominator fix. **Cross-model reporting (for any future B/0 comparison):** `quota/allowance % (or credits/dollars) consumed per independently verified success, including failed attempts + recovery work` `Sol 56`; log allowance pre/post, OpenCode Go allowance, strong-model tokens, wall time. | **WHY:** tokens are incomparable across models/providers; quota/allowance share 5-hour window `Sol 5`; without cost/allowance denominator, Exp B wins are illusory; within Exp A tokens remain valid only because model fixed. **WHAT:** non-inferiority methodology + OpenAI pricing/allowance docs cited by Sol `Sol 5`. **HOW CERTAIN:** proven for verified-success gap; evidence-based for cost/allowance as cross-model metric (pricing docs support, but exact operator allowance mapping is operator-specific). **WHAT-NOT-TESTED:** oracle gaming; does not test whether quota metric generalizes beyond operator's subscription tier. | Write 2 pilot oracles; simulate ranking reversal: same trajectory set ranked by tokens vs allowance%; if rank differs, cost metric is load-bearing — pre-register it. Two-rater κ target 0.8 (<1 hr). |
| **MF-2** | **Instantiate concrete task bank** | `ExpA 14:494-523` `6:182-251` | ≥18 tasks (≥3 per class A-F), each: repo commit pin, file scope, ground-truth patch/answer, verification script, fails-without baseline, difficulty stratum from T0 pilot median tokens, 2 holdout tasks. For Experiment 0 subset (Sol), select 10 representative tasks stratified across A-F + adversarial (see §6). | **WHY:** abstract classes cannot be randomized/scored; selection bias 100%. **WHAT:** experimental design; class×tool interaction. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** cross-repo generalization. | 1 per class ×3 runs on T1 (RTK OFF) baseline; if floor (<500 tokens) or ceiling (100% fail), recalibrate (2-3 hr). |
| **MF-3** | **Pre-register N / randomization / statistical analysis plan** | `ExpA 13:473-491` `16:556-595` | N=10 for primary contrasts (T1 vs T2, R5), N=5 for interactions; Latin square counterbalancing; seed pin or report seedless variance; primary bootstrap 95% CI on expected cost per verified success; secondary median+IQR; win iff CI excludes ROPE ±10% AND non-inferior correctness; Holm across task classes; adverse stopping if success drops >10% after n=5. For Experiment 0, pre-register allowance% CI as primary. | **WHY:** "where practical" → p-hacking for heavy-tailed stochastic LLMs. **WHAT:** best practice; heavy tails. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** provider drift. | Power simulation σ≈0.4×mean → N for 20% MDE @80% power; if N>budget, cut conditions now (30 min). |
| **MF-4** | **Instrument token/allowance accounting at model API boundary + raw artifact outside context** | `ExpA 4:101-118` `16:566-588` + `Sol 80-83` | Define `trajectory tokens = Σ(system+user+tool_output_post_filter+assistant)` per API call; log raw vs compressed separately; guard tokens separated; per-run JSON in durable store. **Sol extension:** For RTK comparisons, save raw tool output to experiment artifact file; give only compressed to model — enables diagnosis without contaminating condition. Log pre/post allowance % (Codex 5-hour) and OpenCode Go usage per run `Sol 55-56`. | **WHY:** shell savings ≠ model savings; raw-as-artifact prevents invisibility of lost information; allowance is the scarce resource `Sol 4-5`. **WHAT:** direct measurement; Sol artifact proposal. **HOW CERTAIN:** proven for boundary gap; evidence-based for raw-artifact necessity. **WHAT-NOT-TESTED:** embedding/cache outside model; allowance API accuracy. | One T1 vs T2 on Task D: compare guard RTK saving vs API delta; if >15% divergence, broken. Verify raw artifact exists and is not in model input (1 hr). |
| **MF-5** | **Specify who/what enforces R5 / R6 / C2 (external, not self-judged)** | `ExpA 7:262-324` `10:375-404` | R5 logged `classify: lexical/relationship because…`; R6 external checklist (proposition+evidence+confidence thresholds) not self-report; C2 checkpoint deterministic (every 5 tool calls or file edit) with versioned JSON schema `objective/constraints/known facts/...`; compaction by script (versioned), cost reported separately. | **WHY:** self-judgment tautology. **WHAT:** construct validity. **HOW CERTAIN:** evidence-based (overconfidence). **WHAT-NOT-TESTED:** checklist gaps — E/F tests this. | R6a vs R6b on same Task B; if R6b never escalates despite missing evidence, trigger insufficient (1 hr). |
| **MF-6** | **Freeze tool & model boundaries + terminology** | `ExpA 5:129-147` `2:41-48` + `Sol 111-113` | Pin RTK rules/level, Serena/LSP version+prompt, rg flags, model ID (e.g., `opencode-go/muse-spark-1.3-contributor`), temp=0, seed, max_tokens, API version; log guard interventions; disable/log `dynamic-models`. **Terminology fix (Sol):** enforce explicit axes — harnesses (Codex, OpenCode) vs providers (OpenAI, OpenCode Go) vs models (Solar/Terran/Lunar) vs roles (Orchestrator/Builder/Reviewer/Auditor) — prevent hidden confounds. | **WHY:** any filter/prompt change = different condition; terminology conflation masks model vs harness effect. **WHAT:** replicability + Sol taxonomy. **HOW CERTAIN:** proven for version freeze; evidence-based for terminology (inspectable conflation in docs). **WHAT-NOT-TESTED:** provider mid-phase model updates. | Sequential T0×2 without reset vs fresh-clone; >10% divergence → reset mandatory; version query pre/post. |
| **MF-7** | **Isolate repo / cache / state per run** | `ExpA 13:473-491` + `Sol 84-94` | Immutable starting commit; isolated `git worktree` + `git clean -fdx` + DB reset + Serena reindex + washout; randomized Latin square order; hidden verification where possible; blinded rubric scorer; fresh agent/task state. | **WHY:** stateful multi-file tasks + caches. **WHAT:** internal validity + Sol isolation checklist. **HOW CERTAIN:** proven. **WHAT-NOT-TESTED:** evaluator-knowledge leakage via holdout. | Same task twice (without vs with reset+reindex); >10% token diff → protocol required. |
| **MF-8** | **Operationalize information-density with rubric + IRR** | `ExpA 9:330-361` `16:573-585` | Automated `useful` = lines in final patch/gold/verification diff; duplicate = semantically identical; blinded audit 10%, Spearman ρ>0.7 / κ>0.7; tokenizer = provider billing tokenizer. | **WHY:** M4-M6 otherwise biased. **WHAT:** analogous studies κ<0.6 without rubric. **HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** semantic usefulness not in patch. | Hand-label 5 retrievals vs heuristic; ρ<0.7 → invalid (1 hr). |
| **MF-9** | **Bound interactions adaptively + pre-register failure injection** | `ExpA 12:440-450` `15:527-550` | Full 2⁴ factorial only if each single mechanism >10% in Phases 1-5; else test `T2+R6` + `R5+C2` + final combined. Failure: 6 cases (misleading match, duplicate impl, generated file, comment-only ref, stale test, incomplete handoff) as task variants scored `detect → retrieve → correct → verify` pass/fail. | **WHY:** full factorial impractical on free tier; adversarial without protocol = anecdote. **HOW CERTAIN:** evidence-based / guess for injection realism. **WHAT-NOT-TESTED:** injection realism. | Budget estimate tokens×N×conditions; if >quota, adaptive bound forced. |
| **MF-10** | **Durable continuity as own experiment (provider-independent task-state record)** | `Sol 58-79` + `ExpA 10:398-406` | **Separate from internal compaction.** Define workspace-resident task record (checked-in or `handoff-bundle/`): `objective / acceptance criteria / constraints / decisions+rationale / verified facts+evidence / current commit/diff / tests+results / unresolved risks / exact next action` `Sol 64-77`. Test by giving fresh Codex/OpenCode session **only** record+repo (no transcript) and measuring verified-continuation success & cost. Compare to harness-managed compaction (Codex compaction events `Sol 62`) as control. Version the record schema; log authoring cost separately. | **WHY:** internal compaction ≠ durable continuity; Codex compaction is harness-managed conversation state, not provider-independent; conflating them hides the scarce-resource cost Sol identifies (`Sol 20-21` immediate pain = durability). **WHAT:** Sol's artifact list + Codex compaction docs cited `Sol 62`; five-review MF-7 covers isolation but not durable-state correctness. **HOW CERTAIN:** evidence-based — distinction is documentable and Sol's field list is implementable; that durability matters more than token saving for quota is operational judgment. **WHAT-NOT-TESTED:** whether 9-field record is sufficient for all task classes (E/F specifically tests this); whether shared repo state vs AGENTS.md nesting tradeoff `Sol 143` dominates. | Draft one record for a completed Task C; hand to fresh agent (no transcript); if continuation fails or costs >50% of original, record insufficient — revise schema before testing internal compaction further (2 hr). |

**Deduplication note:** MF-10 is not a duplicate of MF-7/MF-5. MF-5/MF-7 fix internal validity of Exp A phases; MF-10 tests **cross-harness, cross-quota-window continuity** — the problem Sol identifies as immediate pain (`Sol 20`) and that reviewers flagged only implicitly via C2/C3. Splitting prevents the common error of "compacted transcript = durable state."

---

## 6. Revised Revision Plan — 4 Days + Experiment 0 Pilot (Cheapest-Test-First)

Integrates 06's 3–4 day spec + 1-day pilot with Sol's Experiment 0 as the **first** pilot. The cheapest test is not Exp A instrumentation alone — it is whether the operational quota fix (Solar→Terran + OpenCode Go + durable record) already captures 80% of value at fraction of experimental cost (`Sol 156`).

### Phase 0 — Cheapest-Test-First Operational Pilot (Sol's Experiment 0) — 1 Day

**WHY:** Sol's operational thesis (`Sol 158` — treat A/B as later programme, fix quota now) implies that running full Exp A before testing Solar→Terran default and OpenCode Go loops wastes the scarcest resource (quota) that the experiment is trying to save.
**WHAT:** Sol's Experiment 0 proposal `Sol 148-156`: 10 representative tasks (stratified A-F + 1 adversarial) × 4 conditions:
1. Current Solar/high, existing long-session workflow (baseline)
2. Terran/medium, one outcome per task
3. Terran/medium + RTK + targeted retrieval + durable checkpoint (Exp A minimal winner)
4. Sparse Solar planning/adjudication + OpenCode Go bounded execution (Exp B minimal winner)
Measure: pre/post allowance % (ChatGPT 5-hour), OpenCode Go allowance, strong-model tokens, wall time, verified success rate, recovery cost `Sol 155`.
**HOW CERTAIN (that this is cheapest discriminating test):** operational judgment — evidence-based that Solar/high consumes more allowance than Terran/medium (pricing docs), but magnitude of saving for this operator's workload is unevidenced until measured.
**WHAT-NOT-TESTED:** does not test full A/B factorial interactions; does not test whether 10 tasks represent workload distribution (same C9 risk, but bounded).

| Step | Action | Output | Fail-fast signal |
|------|--------|--------|------------------|
| 0a | Pin 10 tasks with oracles (reuse MF-2 skeleton) | Task bank subset + oracles | κ<0.8 → oracle insufficient |
| 0b | Run 10×4 = 40 trajectories with allowance logging | Allowance% per verified success; recovery rate | If (2) vs (1) already shows >20% allowance saving with non-inferior correctness, Solar→Terran default is validated without full Exp A — stop and adopt operational fix before deeper experiment |
| 0c | Measure (3) vs (2) and (4) vs (2) | Whether RTK/durable checkpoint and OpenCode Go loops earn their overhead | If (3) and (4) show no allowance saving vs (2), full A/B programme is unlikely to pay back — descope |

**Consumer-side audit for Phase 0:** allowance pre/post logged per run? durable record artifact exists? verification blinded? — not re-running trajectories.

### Phase 1 — Instrument & Pin Before Further Data (½ Day)

| Step | Covers | Fail-fast |
|------|--------|-----------|
| Instrument MF-4 (API boundary + raw artifact + allowance) | Guard logging, per-run JSON, raw output file | Guard vs API >15% → broken |
| Power simulation MF-3 (N, budget, ROPE) | N per cell, feasibility | N > quota → adaptive bound forced |
| Terminology freeze MF-6 (harness/provider/model/role) | Naming convention doc | — |

### Phase 2 — Task Bank + Oracles + Isolation (1.5 Days)

| Step | Covers |
|------|--------|
| MF-1 oracles + margin + blinded audit pilot | Verified-success |
| MF-2 full bank (18 tasks + holdout) building on Phase 0 subset | Concrete suite |
| MF-6 tool/model pins + MF-7 reset/worktree protocol + MF-5 enforcement specs | Replicability |
| MF-8 density rubric + IRR pilot | Construct validity |
| MF-10 durable record schema v1 + fresh-session continuation test (one Task C) | Durability |

### Phase 3 — Pre-Registration (½ Day)

| Step | Covers |
|------|--------|
| Write SAP: N, Latin square, primary (expected cost per verified success — tokens within A, allowance across 0/B), secondary median/IQR, ROPE ±10%, Holm, adverse stopping | MF-3 |
| Interaction bounding rule + failure injection cases | MF-9 |
| Durable-state experiment protocol (record+repo only vs transcript) | MF-10 |

### Phase 4 — Exp A Pilot Proper (1 Day, Only If Phase 0 Warrants Continuation)

If Phase 0 showed that (2) is viable and (3) hints at further saving, run Exp A pilot: 6 tasks (1 per class) ×3 runs on T1 (RTK OFF) vs T2 (RTK ON) + R5 contrast + one durable-continuation arm — ~40 runs. Measure variance, effect size, compensatory rate (follow-up commands), CV, guard overhead.

* **If Phase 0 showed (3) no better than (2):** skip Exp A pilot; adopt Terran/medium + OpenCode Go as operational policy; retain Exp A docs as later programme (`Sol 158`).
* **If Phase 0 showed (4) dominant:** prioritize Exp B scoping (B0-B4 only) over full Exp A factorial.

**Total before full Exp A decision:** ~1 day (Phase 0) + ~2.5 days (Phases 1-3) + 1 day conditional pilot = 3.5–4.5 days. Phases 1-3 can overlap with Phase 0 analysis.

---

## 7. Readiness Checklist — When Is Experiment A Ready To Run?

Retains 06 checklist, upgraded with Sol extensions. Checkboxes are consumer-auditable (presence/structure).

- [ ] **MF-1:** ≥18 tasks each have per-task verification script + non-inferiority margin (5% Wilson) defined; two-rater pilot κ≥0.8; primary metric documented as expected cost per verified success (tokens within A, allowance% for cross-model); failed-attempt + recovery included
- [ ] **MF-2:** Task bank instantiated: commit pin + file scope + ground truth + oracle + fails-without baseline + difficulty stratum from T1 baseline + 2 holdout tasks; 10-task Experiment 0 subset stratified and pinned
- [ ] **MF-3:** SAP written with N per cell (10 primary / 5 interactions), Latin square order, seed, primary (`expected tokens per verified success` within A; `allowance% per verified success` for 0/B), median+IQR secondary, ROPE ±10%, Holm, adverse stopping
- [ ] **MF-4:** Token logging at API boundary verified; guard vs API delta <15% on T1 pilot; per-run JSON validated; raw tool output saved as artifact outside model input; pre/post allowance % logged per run
- [ ] **MF-5:** R5 classification logged (`classify: … because…`), R6 external checklist (proposition/evidence/confidence), C2 checkpoint rule (every 5 tool calls or file edit) + versioned JSON schema + script compactor with cost reported separately
- [ ] **MF-6:** RTK rules, Serena/LSP, rg flags, model ID pinned, temp=0, seed; `dynamic-models` disabled/logged; harness/provider/model/role terminology enforced in docs
- [ ] **MF-7:** `git worktree` reset + `git clean -fdx` + Serena reindex per run; condition order randomized; blinded verification; fresh agent/task state
- [ ] **MF-8:** Density rubric written; pilot hand-label vs heuristic ρ≥0.7 / κ≥0.7; tokenizer specified (provider billing)
- [ ] **MF-9:** Interaction bounding rule (>10% single-mechanism gate) + failure injection 6 cases with `detect → retrieve → correct → verify` scoring; run budget fits quota
- [ ] **MF-10:** Durable task-state record schema v1 defined (9 fields `Sol 64-77`); fresh-session continuation test passed on one Task C (record+repo only); internal compaction vs durable record distinguished; shared repo state as authoritative continuity documented
- [ ] **Phase 0 (Experiment 0) completed:** 10 tasks ×4 conditions with allowance% per verified success; result recorded with recovery rate and wall time; decision documented whether to proceed to full Exp A or adopt operational fix

---

## 8. Final Verdict — Integrated (5 Reviews + Sol)

**Retains five-review verdict: NEEDS REVISION — operationally not executable as written; conceptually close to runnable.**

* **What the five-review synthesis got right (and Sol confirms):** Exp A decomposition S1-S8 is correct and publishable-grade; C1-C10 block execution; MF-1..MF-9 are necessary and not duplicative; cheapest-test-first ordering (power simulation + accounting instrumentation before data collection) is essential.
* **What Sol adds that changes priority, not verdict:** Sol is **evidence-based** that Exp A's problem is context-window pressure (2), not quota (1) or durability (3) or cross-model cost (4). Operationally, the fastest quota relief is not Exp A but **Codex default Solar/high → Terran/medium + OpenCode Go loops + provider-independent durable record** (`Sol 136-144`). Sol judgesExp A as "close to runnable after a few corrections" `Sol 1` and Exp A `157` as later programme `Sol 158` — differs from five-review focus on instrumentation by adding an **operational sequencing judgment**: fix quota first, then run Exp A.
* **Reconciliation:** Both judgments are compatible. The five reviews measure **runnable-ness of Exp A as an experiment** (needs MF-1..MF-9). Sol measures **cost-effectiveness of running Exp A now vs capturing 80% value via Experiment 0** (prefers quota fix first). The integrated verdict therefore:
  > **Exp A NEEDS REVISION per MF-1..MF-10 and is ~3–4 days + pilot from runnable; but per Sol's cheapest-test-first operational sequencing, run Experiment 0 (10×4, allowance-aware) before committing to full Phases 1-8 of Exp A. If Experiment 0 shows Terran/medium + durable checkpoint already captures the economically meaningful saving, treat full Exp A/B as later programme — the "serious later evaluation programme" `Sol 158` — rather than immediate spend.**

* **Where Sol is strongest (adopt verbatim):** Four-problem taxonomy, metric correction to cost/allowance per verified success, durable record 9-field list, raw artifact, terminology separation, Experiment 0 as gate.
* **Where Sol defers (explicitly operational judgment):** Whether Exp B should be deferred now — treated as programme scoping decision B0-B4 only, not as refutation of Exp B's design. Whether Solar→Terran default magnitude justifies deferral — to be measured in Experiment 0, not assumed.
* **Risk if Sol ignored:** Optimizing Exp A tokens while quota still depletes via Solar/high default; conflating compaction with durability and missing cross-harness continuity failures; reporting token wins that invert under allowance% ranking.
* **Risk if Sol over-applied (discounting five reviews):** Declaring quota fix sufficient without verifying correctness non-inferiority (C1/MF-1) or measuring compensatory behavior (C3/MF-4) — would repeat the proxy-Goodhart error the five reviews correctly flagged.

**Recommendation to operator:**

1. Land these reviews (01-07) and send for external review as requested — gate satisfied.
2. Approve Experiment 0 (40 runs, allowance-aware) as next cheapest discriminating test — it costs less than one full Exp A phase and directly tests Sol's "80% of answer at fraction of expense" `Sol 156`.
3. Only after Experiment 0 + MF-1..MF-10 readiness checklist, schedule full Exp A Phase 1.

---

## 9. Traceability — What Changed From 06 to 07

| 06 Element | 07 Change | Reason |
|------------|-----------|--------|
| MF-1 tokens-to-verified-success | Upgraded to dual: tokens within A, allowance% across models + include failed attempts/recovery | Sol metric correction `Sol 44-56`, evidence-based |
| MF-4 token accounting | Added raw artifact + allowance logging | Sol `Sol 80-83` `Sol 55` |
| MF-6 tool freeze | Added terminology axis separation | Sol `Sol 111-113` |
| MF-7 isolation | Added `fresh agent/task state` + hidden verification | Sol `Sol 89-93` reinforcement |
| MF-1..MF-9 | Added **MF-10 durable-state own experiment** | Sol `Sol 58-79` provider-independent record vs internal compaction |
| Revision plan 3-4 days + 1-day pilot (6 tasks ×3) | Revised to **Phase 0 Experiment 0 first** (10×4 allowance-aware) then conditional Exp A pilot | Sol cheapest-test-first `Sol 148-157` |
| Verdict: NEEDS REVISION, close to runnable | Retained, with Sol sequencing note: Exp A close after corrections while Exp B deferred | Sol `Sol 1` `Sol 158` |

---

*Integrated synthesis by muse-spark-1.3-contributor (paid, opencode-go). Preserves S1-S8, C1-C10, MF-1..MF-9 from 06; adds Sol as 6th reviewer with evidence-based vs operational-judgment separation and AGENTS.md certainty style. No new empirical data; all recommendations state cheapest discriminating test.*
