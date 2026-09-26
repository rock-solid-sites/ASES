# Findings — Jev Phase 1 Diagnostic (issue #565)

**Role:** D3 analyst, fresh session, no D1 builder context and no D2 verifier
context beyond the committed `verification.md`. **Model:**
`opencode-go/space-bunny-free` — the same family that authored the corpus, the
harness, the `general_model` baseline, and the D1/D2/D3 agents. See **§4 L1**;
this is a real confound on the one comparison the brief turns on.
**Worktree:** `.worktrees/jev-phase1`, branch `research/jev-phase1-565`. No
pushes. No artefact other than this file was modified.

**Method of this document.** Every number below was re-derived directly from
`cases.ndjson`, `results/jev_raw.ndjson`, `results/baselines_raw.ndjson`,
`results/baselines_raw_prefix_max_tokens16.ndjson`, `results/scored.ndjson`,
`results/metrics.json` and `results/manifest.json` — not quoted from `tables/`.
Where a figure appears in a table it is cited to the underlying field, not to
the table. Figures marked **[analyst-derived]** are computed here and appear in
no table; they are reproducible from `scored.ndjson` but were not covered by the
D2 verifier's 2,315-comparison check.

**Standing reading rule (inherited, and it still holds).** n=64 synthetic cases.
No significance test is claimed anywhere and none should be added without a
power calculation (`schema.md` §5). 50 of the 64 cases are `noul`, for which Jev
publishes no confidence. The `rule` and `lexical` cue lexicons were hand-authored
with the corpus vocabulary in view. `rule` on area D is a tautology.
`general_model` is hard-decoded. Every one of these caveats is load-bearing for
at least one claim below, and each is restated at the point of use.

---

## 1. What was measured

One run of a 5-mechanism grid over a **64-case** synthetic corpus — **320
cells**, all present, no duplicates (`manifest.json:grid` → `n_cases` 64,
`n_mechanisms` 5, `n_cells` 320, `cells_complete` true; `scored.ndjson` 320
lines). The mechanisms, in the normative cost order of `schema.md` §3.1, are
**`prior`** (measured label distribution fit on the train split only),
**`rule`** (deterministic cue engine, offline), **`lexical`** (token-overlap
softmax, offline), **`jev`** (`jev-1.13-free`, TypeSafe AI System One, `POST
https://opencode.ai/zen/v1/systemone`, 64/64 `typed_error: null`) and
**`general_model`** (`space-bunny-free`, `POST
https://opencode.ai/zen/v1/chat/completions`, 63/64 `typed_error: null` + 1
`empty_content`) — `manifest.json:models`, `manifest.json:error_counts`,
`metrics.json:m10_cost_reliability`. Composition: **50 answerable / 14
unanswerable**; areas **A 23 / B 13 / C 16 / D 12**; splits **train 21 / dev 21
/ test 22**; question types **noul 50 / choice 12 / score 2**; difficulty **hard
47 / medium 9 / easy 8**; **30 distinct generator templates**; control mix
`base 50, irrelevant_change 4, distractor 2, missing_evidence 2, noise 2,
opaque_labels 2, option_reorder 2`; **6 contrastive pairs** (`cp1`–`cp6`).
Scored at four fixed confidence thresholds (0.70/0.80/0.90/0.95) and three
error budgets (1/5/10%), plus routing legality recomputed from
`routing.signals` before any model saw a case. The live raw run occupies
**2026-09-26T02:46:53Z–02:50:44Z** (`manifest.json:raw_run_window_utc`) — under
four minutes, **one attempt per cell, zero retries**
(`manifest.json:max_attempt_per_mechanism`, `retry_counts`). Scoring is offline
and byte-deterministic (`manifest.json:scoring.deterministic` true,
`self_check_passed` true); the raw run is not, and is not claimed to be.

---

## 2. Supported findings

Supported = the number is reproducible from the committed raw evidence at the
cited field, the sample size is stated, and the caveat is stated with it.

### S1 — Jev answered 49 of the 50 answerable cases correctly, and the 50th is a defective case

**Observation.** `scored.ndjson` rows with `mechanism=jev`, `answerable=true`:
**49/50 `correct`** (`metrics.json:m1_accuracy.overall.jev.acc_answerable` =
0.98). The single error is `c-p4b` (`gt_answer: "no"`, `pred_label: "yes"`,
`probabilities: {yes: 0.55, no: 0.45}`, `confidence: 0.10`).

**Observation.** `c-p4b`'s ground truth is not derivable from the model-visible
text. I re-checked this independently: the token `7a11c2` occurs **5 times** in
`cases.ndjson`, and every occurrence is inside `c-p4a`'s `state`, `c-p4a`'s
`ground_truth.rationale`/`deciding_fact`, or `c-p4b`'s
`ground_truth.rationale` — never in any field a mechanism can read. In
`c-p4b`'s `state` the manifest lists `9f0e44`; nothing in the corpus says
`9f0e44` is *not* the recorded commit. `verification.md` §2 F1 makes the same
finding and quantifies the correction: reclassifying `c-p4a`/`c-p4b` as
unanswerable takes Jev to **49/49 on the justified answerable subset** and
raises every mechanism's false-confidence count from 14/14 to 16/16.

**Interpretation.** Jev's observed error count on ground truth that is derivable
from the corpus text is **zero**. That is a real (if small-sample) result *and*
it removes Jev's error-side evidence entirely: the run contains no case on which
Jev is known to be wrong.

**Caveats.** n=50 answerable, one run. The corpus was authored by a *different*
model family from Jev (`space-bunny-free` wrote it, `jev-1.13-free` answers it),
so the self-preference confound of **§4 L1** does **not** inflate Jev's score —
it inflates the comparator's. `c-p4b` is not the only ground-truth weakness
class — it is the only one that was found, and `validate_cases.py` checks GT
*coherence*, never GT *derivability*, so the corpus may contain others that
neither D2 nor I looked for.

---

### S2 — Jev beats its cheapest preceding mechanism everywhere, with zero reverse wins

`lexical` is Jev's cheapest preceding mechanism under the normative cost order
(`schema.md` §3.1). I re-derived all seven paired comparisons from
`scored.ndjson` (pairing: both mechanisms produced a usable label on an
**answerable** case; `b` = challenger right / incumbent wrong, `c` = reverse):

| scope | n paired | Jev | `lexical` | delta | McNemar `b`/`c` |
|---|---|---|---|---|---|
| ALL | 50 | 98.0% | 58.0% | **+40.0pp** | **20 / 0** |
| area A | 22 | 100.0% | 59.1% | +40.9pp | 9 / 0 |
| area C | 16 | 93.8% | 75.0% | +18.8pp | 3 / 0 |
| area D | 12 | 100.0% | 33.3% | +66.7pp | 8 / 0 |
| split train | 18 | 100.0% | 66.7% | +33.3pp | 6 / 0 |
| split dev | 15 | 93.3% | 53.3% | +40.0pp | 6 / 0 |
| split test | 17 | 100.0% | 52.9% | +47.1pp | 8 / 0 |

**Observation.** `c = 0` in all seven scopes. On every answerable case where
`lexical` was right, Jev was also right. Jev also beat `rule` (+20.0pp,
`b=10 c=0`, n=50) and `prior` (+54.0pp, `b=28 c=1`, n=50)
(`metrics.json:m3b_jev_vs_all`).

**Interpretation.** Strict dominance over the hand-built lexical baseline on
this corpus, stable across area and across all three splits. This is the brief's
literal question ("does Jev beat the cheapest preceding mechanism") and the
answer is yes, unambiguously, on this corpus.

**Caveats, all material.** (a) `lexical`'s 58.0% is an **upper bound on a
generic cue engine**, not a measurement of one — its lexicon was written by the
corpus author with the corpus vocabulary in view, so +40.0pp is an upper bound on
the gap, not a point estimate of it. (b) Pairing excludes the 14 unanswerable
cases, where `lexical` also answered 14/14. (c) n=50, one run, no significance
test. (d) On area D, `lexical` scored 4/12 and `rule` 12/12 — but `rule`'s 12/12
is a tautology (**§4 L6**), so the area-D row measures a lexical engine against
a policy simulator.

---

### S3 — Jev does **not** beat the free general model; the one discordant cell is defective

**Observation.** `metrics.json:m3b_jev_vs_all`, `jev vs general_model`: n=50,
Jev 98.0% vs 100.0%, **−2.0pp, `b=0`, `c=1`**. The single discordant cell is
`c-p4b` (S1) — the same cell. `general_model` was correct on **50/50** answerable
cases (`metrics.json:m1_accuracy.overall.general_model.n_correct_answerable` =
50).

**Interpretation.** On this corpus, a free-tier general chat model matched or
beat Jev, and the entire margin is one case whose ground truth is not derivable
from the text. Whether Jev holds a niche at all therefore reduces to a question
this run cannot answer: **is that 50/50 a property of cheap general models, or a
property of this one model family reading prose this one model family wrote?**
(§4 L1, §6 Q1.)

**Caveats.** `general_model`'s advantage here is one cell; the honest reading is
"tied, with a 1-cell deficit for Jev that is itself an artefact". n=50. The
comparison is the one most exposed to the self-preference confound.

---

### S4 — Routing: Jev picked a legal role 12/12, but its confidence is saturated

**Observation.** Recomputing legality independently from `routing.signals` via
`routing_policy.compute_legality` (0 mismatches against the stored
`routing.legal_roles`, as `metrics.json:m8_routing` also reports): Jev
**12/12 legal, 12/12 the expected role**; `general_model` 12/12 and 12/12;
`lexical` 5/12 legal and 4/12 expected; `prior` 3/12 legal and 3/12 expected.
The area-D states do not leak the role word, and they contain explicit negations
of the other roles' preconditions (e.g. `d-01`: "No defect is known, no failure
is unexplained, and no governing assumption is known to be invalid"), so the task
requires tracking negation rather than matching a keyword. It is not degenerate:
I enumerated every constant-role strategy. Expected roles across the 12 cases are
`redesign`×3, `repair`×3, `investigate`×3, `review`×2, `escalate`×2, `build`×1;
no single role is correct on more than **3/12**, and no single role is *legal* on
more than **3/12** (`escalate` is legal on 2/12, `repair` and `investigate` on
3/12 each). The best constant strategy scores 3/12.

> **Discrepancy found — `verification.md` §6 Attempt 4 does not reproduce.** That
> section states "an always-`escalate` strategy would score 10/12, not 12/12".
> An always-`escalate` strategy scores **2/12** correct and is legal on **2/12**;
> I could not construct any reading of the area-D corpus under which 10/12 is
> correct. The *conclusion* the sentence supports is sound and in fact stronger
> than stated (max constant strategy = 3/12, not 10/12), but the number should
> not be quoted. The non-degeneracy argument stands on the enumeration above.

**Observation.** Jev's area-D confidences (`scored.ndjson:confidence`, area D)
are **exactly 1.0 on 11 of 12 cells**; the exception is `d-07` at 0.52
(probabilities `{escalate: 0.6, investigate: 0.4}` — the one case with two legal
roles and a genuinely close call). `d-08`, also two-legal
(`escalate`/`repair`), is 0.99.

**Interpretation.** The routing *answer* is a real result. The routing
*confidence* carries no ordering information — 11/12 saturated at 1.0 — and the
one cell where it dropped (`d-07`) is the one cell where a drop was warranted.
That is n=1 supportive against n=1 contradicting (`d-08`, also ambiguous, 0.99);
**no signal**.

**Caveats.** n=12, one run, six fixed options. `rule`'s 12/12 is a tautology
(**§4 L6**). `T8b`'s `chi2 = 0.0` for Jev is a restatement of this 12/12, not
independent evidence (`verification.md` §6 attempt 5) — the informative
`chi2` rows are `prior` (22.83) and `lexical` (4.83).

---

### S5 — The escalation result is real, cheap, and **0.04 away from collapsing**

This is the only positive *operational* result in the run, so it gets the most
scrutiny.

**Observation — the curve** (`metrics.json:m4_coverage_error.jev`, reproduced
from `scored.ndjson`):

| threshold | acted | coverage | errors | of which false-confidence | of which wrong label |
|---|---|---|---|---|---|
| 0.70 | 48/64 | 75.0% | 4 | 4 | 0 |
| 0.80 | 45/64 | 70.3% | 3 | 3 | 0 |
| **0.90** | **38/64** | **59.4%** | **0** | 0 | 0 |
| 0.95 | 25/64 | 39.1% | 0 | 0 | 0 |

At **0.90**: 38 cells act, **38/38 correct**, composition **25 answerable
`noul` + 11 answerable `choice` + 2 answerable `score`**, zero unanswerable
cells, areas A 18 / C 9 / D 11. The 26 withheld cells are 14 genuinely
unanswerable + **12 answerable cases Jev would have answered** — of which **11
correctly and 1 incorrectly** (`c-p4b`, derived confidence 0.10, which the gate
happens to catch for the wrong reason: it is the lowest-confidence cell in the
grid, not because the case is unanswerable). **[analyst-derived]**

**Observation — what "confidence" is here.** Jev publishes **no** confidence and
**no** probabilities for `noul`. The raw body proves it: `jev_raw.ndjson` for
`b-a01` is `{"model":"jev-1.13-free","answers":{"q":{"type":"noul","noul":0.69}},"usage":{...}}` —
no confidence field — while `d-07` is `{"type":"choice","choice":"escalate","confidence":0.52,"probabilities":{...}}`.
50 of 64 cells are `noul` (`scored.ndjson:confidence_source` → `derived` 50,
`reported` 14). The derived value is
`confidence_formula` (`harness/common.py:177`) applied to the harness's
`{yes, no}` expansion of `noul`, i.e. for n=2, `2·max(p) − 1`. That is the
*same* formula that was empirically confirmed against the 14 API-reported cells
(**S7**). So the derived value is a deterministic monotone function of the API's
own probability and carries no information beyond it.

**Observation — the margin [analyst-derived].** Jev's derived confidence on the
**14 unanswerable** cells, sorted: `0.10, 0.12, 0.18, 0.26, 0.26, 0.38, 0.40,
0.44, 0.44, 0.46, 0.76, 0.82, 0.84, 0.86`. The maximum is **0.86**. The
zero-error result at threshold 0.90 is therefore separated from failure by
**0.04**, on **n=14**. At 0.95 the margin widens to 0.09 and coverage falls to
39.1%. The four unanswerable cells that *do* act at 0.70/0.80
(`b-dist1` 0.86, `b-a02` 0.84, `b-a04` 0.82, `b-miss1` 0.76) **are the entire
false-confidence error set at those thresholds** — the high-coverage
zero-error operating point is also the thinnest-margin one.

**Observation — threshold-free separation [analyst-derived].** Rank AUC of the
stored `confidence` for correct-answerable cells vs unanswerable cells:
Jev **0.941** (n=49 vs 14), `lexical` 0.732, `rule` 0.671, `prior` 0.568,
`general_model` **0.500** (exactly chance, as expected from a constant).

**Interpretation.** On this corpus a harness rule of the form *"act only when
`2·max(p) − 1 ≥ 0.90`"* would have produced 38 correct actions and zero errors,
and would have caught all 14 cases where the deciding fact was missing. That is
a usable mechanism. The cost is 26 escalations, **12 of which were unnecessary**
— a 40.6% over-escalation rate against a 100% catch rate on unanswerable cases.
Stated in the other direction, and this is the sharpest form of the finding: the
gate spends **11 correct answers and 1 wrong answer** (12 answerable cells) to
eliminate **14 false-confidence errors** — and the 1 wrong answer it eliminates
is `c-p4b`, the defective case from S1, which it catches by accident (lowest
confidence in the grid), not because the case is unanswerable.

Applying the S1 correction (both `cp4` members reclassified unanswerable, per
`verification.md` §2 F1) gives the cleaner and more favourable trade: answerable
becomes 48, the acted set is **unchanged at 38** (both `cp4` members were already
below 0.90), withheld answerable becomes **10, all correct**, and errors
eliminated becomes **16**. So the corrected statement is: **the gate spends 10
correct answers to eliminate 16 false-confidence errors.** That is the strongest
operational argument for Jev anywhere in this run — and it is still an argument
about *one corpus, one run, n=16, with a 0.04 margin*.

**Caveats, and they are severe.** (a) The 0.04 margin on n=14 means **one**
unanswerable case scoring above 0.90 flips the headline to 1 error. This is the
single most fragile supported finding in the document. (b) 13 of the 14
unanswerable cases are area B, which is **100% unanswerable** and therefore
contributes no answerable contrast; the 14 cover 10 distinct absence archetypes
(5 conflicting-record, 5 insufficient-evidence) plus 3 area-B controls and 1
area-A control — variety inside one hand-authored block, not an independent
sample. (c) The confidence is derived, not asserted, for 50/64 cells. (d) The
cross-mechanism AUC row is **not** a like-for-like comparison: `rule`'s
confidence is a hard-coded constant (`run_baselines.py:68-70`, `0.75/0.55/0.90`),
`lexical`'s is an uncalibrated `exp(2·score)` softmax
(`run_baselines.py:352-354`), and `general_model`'s is identically 1.0 by hard
decode. Only Jev's within-mechanism AUC is meaningful; the ordering across
mechanisms is substantially an artefact of how each confidence was manufactured.
(e) The AUC is post-hoc, computed on the same data it describes.

---

### S6 — Does Jev's uncertainty separate correct from incorrect? n=1, and that cell is defective

**Observation.** Across all 50 answerable cells, Jev produced **exactly one**
incorrect answer: `c-p4b`, at derived confidence **0.10**. Jev's 49 correct
answerable cells have derived confidence min 0.14, median 0.94. So the ordering
is correct — the one error is the lowest-confidence answerable cell in the grid.

**Observation.** `metrics.json:m6_contrastive_and_controls` `T7a` records
exactly **one** informative confidence-ordering verdict for Jev across all six
contrastive pairs: `cp4`, `correct_order` (0.14 vs 0.10). The other five pairs
are `n/a` (Jev got both members right or both wrong, so there is no ordering to
check). `cp4` **is** `c-p4a`/`c-p4b` — the S1 defective pair.

**Interpretation.** The answer to the brief's second question is: **on the
answerable side, this run provides one discordant cell of evidence, and that
cell's ground truth is not derivable from the text.** The claim "Jev's
uncertainty separates correct from incorrect cases" is *not* supported by this
evidence. It is neither refuted nor confirmed; it is unmeasured.

**Caveats.** One negative example cannot support a discrimination claim, and
`verification.md` §2 F1 quantifies what happens when the defective cell is
reclassified: Jev is left with **zero** informative confidence-ordering verdicts
on the entire grid. The separation that *is* measured (S5) is
answerable-vs-unanswerable, which is a different axis.

---

### S7 — The published confidence matches `(n·max(p) − 1)/(n − 1)` on the 14 testable cells

**Observation.** `metrics.json:m9_confidence_formula`: Jev is testable on
**14/64** cells (12 `choice` with 6 options, 2 `score` with 3). Hypothesis A
`(n·max(p)−1)/(n−1)`: mean absolute residual **0.0005**, max 0.005, **14/14
within 0.01**, 13/14 exact at 2 dp. Hypothesis B `max(p)`: mean 0.0071, max
0.08. A is ~14× better. Independently re-derived on a raw body: `d-07` has
`max(p) = 0.6` over 6 options → `(6·0.6 − 1)/5 = 0.52`, which is exactly the
reported `confidence: 0.52`.

**Interpretation.** The documented derivation is strongly *consistent* with
14/14 published confidences. Probabilities are published rounded, so a residual
of one or two units in the last place is the rounding floor.

**Caveats.** 14/64 cells. This is consistency evidence, **not** proof of the
API's internal mechanism, which is a black box (`verification.md` §10.2). For
`noul`, A and B **coincide** (n=2), which is why the S5 derived confidence
cannot be independently corroborated from the published field — there is no
published field to corroborate it against.

---

### S8 — No mechanism withheld an answer when a deciding fact was absent

**Observation.** The corpus contains **70 unanswerable cells** (14 cases × 5
mechanisms). **69 carry a non-null `pred_label`**
(`scored.ndjson:pred_label`). The one exception is `general_model` / `b-i03`,
where `typed_error: "empty_content"`, `usable: false`, `http_status: 200`,
`error_detail: "200 OK but reply did not match a candidate"` — a transport
failure, not a judgement.

**Interpretation.** This is the finding that decides whether Jev can support
escalation: it did not, and neither did anything else. High answerable-only
accuracy is not evidence of abstention capability.

**Caveat — the published evidence for this is invalid, and the correct evidence
is the one above.** `README.md`, `DISPATCH.md`, `T1` and `T7c` all present
"0 of 320 cells set the `abstained` flag" as a finding about the five
mechanisms. I confirmed it is a property of the harness: `abstained` is written
exactly once, as a literal `False`, at `harness/common.py:298`, and read at
`harness/score.py:236`; no code path can set it `True`. So `n_abstained_flag == 0`
is true by construction. The honest claim is **weaker about the mechanisms and
stronger about the design**: *no mechanism in this grid has the ability to record
an abstention, because the harness gave none of them a way to express one.*
`verification.md` §6 F2 reaches the same conclusion. The 69/70 label-presence
count is the load-bearing evidence and it does measure the mechanisms.

---

### S9 — The adversarial controls were inert against Jev — at n=2 each

**Observation** (`metrics.json:m6_contrastive_and_controls`): Jev label-stable
on **4/4** `opaque_labels` + `option_reorder`, **2/2** `distractor`, **2/2**
`noise`, **4/4** `irrelevant_change`. Confidence shifts were small:
`irrelevant_change` mean −0.01 (min −0.04), `distractor` mean +0.01
(range 0.0 to +0.02), `noise` mean −0.05 (range −0.08 to −0.02).

**Interpretation.** Jev is not brittle to option renaming, option reordering,
appended distractors or surface noise, on this corpus.

**Caveats — n=2 per control kind is very thin, and the two reorder instances
are weaker than they look.** Both `option_reorder` instances are area D (6
options) and both preserve the option set and the per-key label text verbatim;
I confirmed `d-03`/`d-r01` and `d-06`/`d-r02` share the same `state` and the
same `criteria` *set*, differing only in JSON key order. So "robust to reordering"
here means "robust to a permutation of six keys whose texts never changed", twice.
Similarly "robust to opaque labels" means "returned a content-free option key
correctly" twice.

---

### S10 — Jev is the only mechanism emitting a graded distribution, and was the faster live mechanism

**Observation.** Mean Brier over the 50 answerable cells
(`metrics.json:m2_brier`): `prior` 66.73%, `lexical` 56.36%, `rule` 28.20%,
**`jev` 3.55%** (`noul` 4.03% n=36, `choice` 2.67% n=12, `score` 0.09% n=2),
`general_model` **0.00%**.

**Observation.** `metrics.json:m10_cost_reliability`: Jev median latency
**587.5 ms** (525.3–763.5), 22,651 input / 1,882 output tokens, 0 retries,
0 typed errors. `general_model` median **1163.1 ms** (901.5–3615.2),
16,527 input / 1,321 output tokens, 0 retries, 1 typed error.

**Interpretation.** `general_model`'s 0.00% Brier is an **encoding floor, not a
calibration result** — a hard one-hot decode scores 0.0 whenever it is right and
1.0/1.8 whenever it is not, so its "perfect" Brier and its "no usable
confidence" (identically 1.0 on 63/63 cells) are the same fact. Jev is
therefore the only mechanism whose output can be thresholded at all, and the only
one for which S5 is possible. On raw latency in this run Jev was ~2× faster per
cell.

**Caveats.** Both are free tier at 0/0 cost, so "faster" is not a cost claim.
Single run, n=64 each; latency is declared a non-scoring input
(`schema.md` §3.4). Token counts are for one request shape (one question per
case) and do not test the "latency flat in question count" claim.

---

## 3. Provisional findings

Weaker evidence, single-run, or resting on a cell/case count too small to carry
a conclusion. Recorded so they are not re-litigated as if they were S-level.

**P1 — Contrastive pairs: 5/6 distinguished, and the 6th is the defective one.**
Jev gave different labels to the two members of 5 of 6 pairs and got both members
right in 5 of 6 (`T7a`). The single non-distinction is `cp4`, where it answered
`yes` to both `c-p4a` and `c-p4b` (0.57 and 0.55). Honest reading: **no observed
failure on the five pairs whose ground truth is derivable** — which is not the
same as a measured 83%, and is not a robustness rate. n=6 pairs, one run.

**P2 — Option-position bias: Jev's predicted-position histogram equals the
expected histogram 12/12, `chi2 = 0.0`.** This is arithmetically forced by
S4's 12/12, not independent evidence. The informative rows are `prior`
(`chi2` 22.83) and `lexical` (4.83), which show the metric can detect a
position-chooser. No p-value is reported and none should be (n=12).

**P3 — The `rule` baseline's coverage curve has two operating points, not four.**
`rule` acts 37 cells at thresholds 0.70 *and* 0.80, and 25 at 0.90 *and* 0.95.
The reason is that `run_baselines.py:68-70` injects exactly three constants
(`RULE_HARD_CONF = 0.75`, `RULE_SOFT_CONF = 0.55`, `ROUTING_POLICY_CONF = 0.90`).
Any reading of "rule's coverage at threshold X" is therefore an artefact of three
hand-picked numbers, not a measured curve. `T5a` states that rule's confidence
is "ASSUMED constant injected by the rule engine"; this is the quantitative form
of that caveat and is not stated in the tables.

**P4 — The `general_model` baseline produced no usable confidence at all.**
`confidence` is exactly `1.0` on 63/63 usable cells, so its coverage is flat at
98.4% with 13 errors at all four thresholds (`T5b`), and it is "not achievable"
at every error budget in `T6`. Read this as *the baseline emitted no
confidence*, not *the baseline is inaccurate* — on answerable cases it was the
most accurate mechanism in the grid.

**P5 — `b-miss1` is not a discriminating evidence-removal control.** Its
`base_case_id` is `b-a01`, which is **already unanswerable**
(`scored.ndjson:answerable` false for both), so removing evidence from it tests
nothing about evidence removal. The control class therefore has **n=1**
discriminating instance (`a-miss1`), not n=2. The corpus discloses this in
`b-miss1`'s own `difficulty_note`.

**P6 — "Cheapest" and "cost" are ordering labels, not measurements.** The
normative cost order is asserted in `schema.md` §3.1; no mechanism in this run
consumed a priced resource. Both live models are free tier. Latency and token
counts in S10 are single-run observations of one request shape.

---

## 4. Limitations

### L1 — One model family holds four of five seats (self-preference; structural)

| seat | model |
|---|---|
| case author — `gen_cases.py`, 30 templates, all 64 cases, all ground truth, all rationales | `opencode-go/space-bunny-free` |
| harness author — `run_baselines.py` cue lexicons + `GEN_SYS`, `score.py`, `common.py` | `opencode-go/space-bunny-free` |
| `general_model` baseline (the free comparator) | `opencode-go/space-bunny-free` |
| D1 result author, D2 verifier, D3 analyst | `opencode-go/space-bunny-free` |
| **`jev`** | **`jev-1.13-free` — the only different family** |

The sharper instance, which no artefact in this directory currently names: **the
free general model being compared against Jev is the same model that wrote the
corpus it is being tested on, wrote the prompt template it is answering, and
wrote the vocabulary its 100% is scored against.**

**Direction of the confound.** It can only **inflate** `general_model`, never
Jev. So the affected claim is S3 — the comparison the brief actually turns on —
and the bias runs **against** Jev. Equivalently: the run may be *understating*
Jev's position relative to a free chat model. That is the one claim in this
document whose direction of error favours the negative conclusion, and it must
be read with that in mind.

**What was done about it.** Sessions were isolated (D2 read all state from git,
no builder context; D3 likewise), and the D2 inversion probe — re-asking four
cases with the logically negated question — passed: both mechanisms track
question semantics, including an inverted question about a different subject
than the state supports. That rules out the crudest artefact (template
matching) but **not** the stylistic one: a same-family model may parse
same-family prose more reliably, and 50 synthetic cases cannot separate that from
genuine comprehension. A partial counterweight I can add from the code:
`GEN_SYS` is a minimal generic instruction ("Reply with the single required
token and nothing else"), so the confound is specifically about *prose
comprehension*, not prompt quality — the corpus, not the prompt, is the
same-family artefact. **This cannot be resolved inside the current
operator-approved model envelope.**

### L2 — The corpus is fully synthetic and template-generated

All 64 cases carry `provenance.synthetic: true`,
`contains_personal_content: false`, `contains_secrets: false`, and come from
**30 generator templates**. Every 98%/100% figure in this document measures
performance on this corpus, full stop. Nothing here measures performance on real
engineering-judgement tasks, and no personal or incident data was involved.

### L3 — One run, free-tier endpoints, unpinned models

No significance test is claimed anywhere (`schema.md` §5) and none should be
added without a power calculation. `jev-1.13-free` and `space-bunny-free` are
free-tier and unpinned: the weights or serving stack behind those IDs can change
without notice, and the Zen route for `general_model` already had to be
substituted mid-task (the Go route returns 403 with this credential —
`manifest.json:models.general_model.endpoint_note`, a disclosed route change,
not a model substitution). `RUNBOOK.md` concedes the two-tier position
explicitly: scoring is byte-reproducible, the raw run reproduces the *method* and
not the *bytes*. D2 measured the residual nondeterminism directly: ±0.01 on
mid-range `noul`, **0 label flips in 71 additional live calls**, and Jev's
saturated answers byte-identical. The closest cell to the decision boundary,
`b-i03` at 0.55, held 0.54–0.56 across 7 observations.

### L4 — `confidence` is derived from the probability, so it is not independent evidence

For **50 of 64** cells (all `noul`) Jev publishes no confidence. The stored
value is `(2·max(p) − 1)` over the harness's `{yes, no}` expansion — a
deterministic monotone transform of the probability Jev *did* publish, carrying
no information beyond it. `T5c` reports the curve under both conventions and the
split is arithmetically additive (13 reported + 35 derived = 48 acted at 0.70),
so `T5b` is not double-counting. The honest statement about S5 is therefore:
**thresholding on `2·max(p) − 1 ≥ 0.90` is thresholding on `p ≥ 0.95`** — a
legitimate, deployable rule, but not a confidence *claim* by the model.

### L5 — The cheap baselines are hand-built with the corpus in view

`rule` 78.0% and `lexical` 58.0% are **upper bounds on a generic cue engine**,
not measurements of one. I confirmed no mechanism reads `ground_truth` at
prediction time and that the `prior` fit is train-split-only
(`verification.md` §3.1), so this is not leakage — it is authorship
circularity, which no re-run of this harness can remove. Consequently T3's chain
measures *hand-tuned* cheap mechanisms, and the +40.0pp Jev-over-`lexical` gap
is an upper bound on what Jev would gain over a generic cue engine.

### L6 — `rule` on area D is a tautology, and it is a policy simulator with no text access

I confirmed this independently by instrumenting `run_rule` with a recording dict
proxy and logging every key touched: **`run_rule` reads `state` on all 52
non-area-D cases and on 0 of the 12 area-D cases.** Its area-D 12/12 is a
simulation of `routing_policy.compute_legality` over hand-authored signals, not
evidence that rules can read prose. `README.md`, `INDEX.md`, `T9` and
`DISPATCH.md` all disclose the tautology; none states the zero-text-access fact.

### L7 — `general_model` is hard-decoded, so its confidence and Brier are encoding artefacts

`confidence` is identically 1.0 on 63/63 usable cells and its Brier is 0.00% by
construction. Its threshold coverage and its perfect Brier are the same fact, and
neither is a measurement of the model's certainty.

### L8 — The escalation result is one cell away from failing

Max unanswerable derived confidence **0.86** vs threshold **0.90** on **n=14**
(**S5**). The 59.4%-at-zero-errors row of `T6` is the highest-coverage
zero-error operating point *and* the least safe one. Any statement of the form
"Jev supports escalation at 0 errors" must carry this margin.

### L9 — Corpus structure limits what the false-confidence metric can discriminate

Area B is **13/13 unanswerable** — it has no answerable contrast at all, so its
contribution to `acc answerable-only` is undefined and the whole area-B result is
the mixed and false-confidence columns. The 14 unanswerable cases span 10
distinct absence archetypes (5 conflicting-record, 5 insufficient-evidence) plus
3 area-B controls and 1 area-A control (`a-miss1`) — variety inside one
hand-authored block, not an independent sample. Meanwhile the false-confidence
rate is **saturated**: 100.0% for `prior`, `rule`, `lexical` and `jev`; 92.9% for
`general_model` (13/14, the missing cell being a transport failure). On this
corpus the metric can only distinguish "answers everything" from "answers
nothing", and nothing answers nothing.

### L10 — Interface surfaces the run did not touch

Declared in `schema.md` §5 and confirmed still untested: multi-question requests
(the schema's `questions` is a list; only one question per case was ever sent,
so the "latency flat in question count" claim is **unverified**), `state` as an
object, `instructions` as object/array, a per-area or per-difficulty prior, and
the Go chat route. The `score` question type has **n=2** and `choice` has **n=12**
(all area D).

### L11 — One material ground-truth defect, and the class may contain others

`c-p4a`/`c-p4b` (**S1**). `validate_cases.py` checks GT *coherence*, never GT
*derivability from the state text*, so this class of defect is invisible to the
harness. One was found, by reading, in 6 contrastive pairs and 13 area-B cases.
That is not a search with a known denominator.

**A related minor defect, recorded by the verifier and confirmed by me:** `cp1`
is not a single-fact edit. `c-p1a` asserts approvals *and* a green CI gate;
`c-p1b` asserts only a red CI gate — the approvals clause is **dropped**, not
flipped. The deciding fact still differs so the pair is valid, but 1 of 6 pairs
does not meet "differing only in the deciding fact" in the strict sense.

### L12 — `acc_mixed` credits a transport failure (analyst-derived; my own finding)

`acc_mixed` is defined as "over all cells, counting answering an unanswerable
case as an error" (`score.py:338-347`), and it is implemented as
`correct_answerable + count(unanswerable cells that emitted no label)`. A cell
that emitted no label **because the transport failed** therefore scores as a
pass. `general_model` is the only mechanism with such a cell, and it is worth
**1 cell = 1.56pp**: `general_model` mixed accuracy is 0.7969 = 51/64
(`metrics.json:m1_accuracy.overall.general_model.acc_mixed`), where 51 = 50
correct answerable + 1 for the `empty_content` on `b-i03`. The scorer
simultaneously refuses to call `b-i03` an abstention (`T7c`).

**Consequence for the headline ordering.** Jev 0.7656 vs `general_model` 0.7969
— a 3.1pp gap that is **entirely** one transport failure. On the behavioural
measure that actually matters (answered-unanswerable) Jev is 14/14 and
`general_model` is 13/14. The two mechanisms are within one cell of each other on
mixed accuracy and Jev is worse on the abstention axis; neither ordering should
be quoted without this note.

### L13 — Statistics introduced here are outside the verified envelope

The AUC row, the max-unanswerable-confidence margin, the acted-cell composition
at 0.90, the `run_rule` state-access counts, the `7a11c2` occurrence count, and
the `acc_mixed` decomposition are **analyst-derived** in this document. They are
reproducible from the committed files, but D2's 2,315-comparison check did not
cover them and no second pair of eyes has.

### L14 — Reproduction of the RUNBOOK is broken in two places (verified by me)

`RUNBOOK.md:103,117,147,250` records `metrics.json` as `3d2e3ac5…`; the actual
file is `d080965f…`. `RUNBOOK.md:119` records `manifest.json` as `d07dad4a…`;
the actual file is `0a54daa6…`. `scored.ndjson` matches at `662d6ec6…`.
Separately, `RUNBOOK.md` §4.1's `gen_cases.py --out …` is not executable:
`harness/gen_cases.py` contains **no `argparse` and no `sys.argv`**
(0 occurrences of either), and `main()` writes `<repo>/cases.ndjson`
unconditionally — so the documented command would silently ignore `--out` *and*
rewrite the committed corpus. The data is sound (the D2 diff across the offending
commit shows only two added counter fields, no accuracy/gain/Brier/coverage
figure moved), but the runbook as written fails 2 of its own 12 checklist items.
Anyone reproducing from the runbook will hit both.

---

## 5. Counterexamples and negative results

Preserved deliberately. Several of these cut against Jev and several cut
against the run's own framing.

**N1 — Jev has zero observed errors on derivable ground truth.** Its only
answerable error is `c-p4b` (**S1**), whose ground truth is not derivable. This
is a negative result *in Jev's favour* and simultaneously the reason S6 is
unmeasured.

**N2 — Jev answered every unanswerable case.** 14/14
(`unanswerable_but_answered`), same as `prior`, `rule` and `lexical`;
`general_model` 13/14. Four of Jev's 14 were answered with derived confidence
**≥ 0.76** (`b-dist1` 0.86, `b-a02` 0.84, `b-a04` 0.82, `b-miss1` 0.76). Those
four are the **entire** false-confidence error set at threshold 0.70 (4 of 4) and
**three of the four** at 0.80 (`b-miss1` at 0.76 falls below it). Jev never says
"I don't know"; the only reason the 0.90 gate has 0 errors is that these
particular four landed at 0.76–0.86 rather than above 0.90.

**N3 — Evidence removal moved Jev's confidence in opposite directions on the two
instances, and changed no label.** `a-miss1` (a proper answerable→unanswerable
flip, base `a-h01`): derived confidence **fell 0.52** (0.96 → 0.44) and Jev still
answered. `b-miss1` (base already unanswerable): confidence **rose 0.38**
(0.38 → 0.76) and Jev still answered. The verifier re-ran `a-miss1` 7× and got
0.27–0.30 against a base of 0.28 — flat, not fallen. So on n=1 discriminating
instance, evidence removal did not produce a reliable confidence response, and in
one direction produced the *opposite* of the expected sign.

**N4 — The normative cost chain is non-monotone in accuracy.** `lexical` is
**20.0pp worse** than `rule` on answerable cases (`b=4`, `c=14`, n=50) and 66.7pp
worse on area D (`b=0`, `c=8`, n=12). Ordering mechanisms by cost and reading the
accuracy off that order would conclude that the third rung is a regression.

**N5 — `prior` never acts at any threshold.** 0/64 acted cells at 0.70, 0.80,
0.90 and 0.95; its derived confidence is the constant 0.125 on all 64 cells
(`scored.ndjson:confidence`). All three `T6` rows read 0.0% coverage. The floor
of the chain cannot be thresholded at all.

**N6 — The `general_model` baseline's typed errors, and their true cause.** One
cell (`b-i03`) failed: `http_status: 200`, `typed_error: "empty_content"`,
`error_detail: "200 OK but reply did not match a candidate"`, and
`usage.raw.completion_tokens_details.reasoning_tokens: 256` — the entire token
budget consumed by reasoning, leaving empty content. The preserved pre-fix run
(`results/baselines_raw_prefix_max_tokens16.ndjson`, all HTTP 200) records
**14/64** `empty_content` at `max_tokens=16`; the fix to 256 reduced that to 1/64
in the committed run. D2 then measured **≈11% (4/35)** at 256, landing on a
different case each time, so the committed `error_counts` figure of 1/64 is a
**lucky draw, not a measured reliability** — `T11`'s `empty_content=1` must not
be read as a rate. Nothing downstream depends on it (the cell is unanswerable and
excluded from every accuracy denominator), but the reliability picture is
understated. Jev had **0/64** typed errors and 0 across D2's 71 extra live calls.

**N7 — The published abstention count is a harness property, not a finding.**
`abstained` is a literal `False` at `harness/common.py:298` with no other writer
(**S8**, `verification.md` §6 F2). The number cannot be anything but 0.

**N8 — Three of the grid's most-quoted numbers trace to the same defective
cell.** `c-p4b` is simultaneously Jev's only answerable error, the only paired
loss in `jev vs general_model` (`c=1`), and the only informative confidence
verdict in `T7a` for Jev. Quoting any of the three without naming the fourth is
misleading.

**N9 — The abstention axis is unmeasurable on this grid.** 0 of 320 cells can
record an abstention, and the false-confidence rate is saturated at 100%/100%/
100%/100%/92.9%. There is no spread, so no mechanism can be ranked on it.

**N10 — Two of twelve RUNBOOK reproduction checks fail on a clean clone**
(**L14**), and the runbook's own gotcha #1 (`gen_cases.py` takes no arguments and
overwrites `cases.ndjson`) directly contradicts its §4.1.

**N11 — `T8b`'s `chi2 = 0.0` for three mechanisms is arithmetically forced** by
their 12/12 on area D and is not a second independent measurement
(`verification.md` §6 attempt 5).

**N12 — A number in the independent verification report does not reproduce.**
`verification.md` §6 Attempt 4 states "an always-`escalate` strategy would score
10/12, not 12/12". Enumerating all six constant-role strategies on the area-D
corpus, always-`escalate` scores **2/12** correct and is legal on **2/12**; the
best constant strategy of any kind scores **3/12** (`redesign`). No reading of
the corpus yields 10/12. The conclusion the sentence supports is correct and
stronger than stated, but the figure must not be quoted. D2's 2,315-comparison
check covered the scoring arithmetic, not this sentence, which is why it passed
review — a reminder that the verified surface and the asserted surface are not
the same set.

---

## 6. Next-phase questions, and the smallest justified next experiment

### Open questions, in order of how much they threaten the conclusion

**Q1 (decides the brief) — Is Jev's non-advantage over a free general model a
property of cheap general models, or of this one family reading this one family's
prose?** Everything in §2 that matters operationally reduces to this. S3 records
a 1-cell deficit; S1 shows that cell's ground truth is not derivable; L1 shows
the comparator wrote the corpus. So the honest status of the brief's headline
question is **untested**, not answered. No further analysis of the existing 64
cases can resolve it — only new measurement.

**Q2 (bounds the only positive result) — Does the unanswerable confidence
distribution have a tail above 0.90?** S5's 0-errors-at-0.90 rests on a maximum
of 0.86 over n=14. If the tail extends past 0.90, the escalation mechanism fails
at its highest-coverage operating point and survives only at 0.95 (39.1%
coverage). Characterising this needs many more genuinely-unanswerable cases, and
authoring those is exactly where F1 shows it goes wrong.

**Q3 — Is Jev's graded distribution usable as a *probability*, or only as a
ranking?** `T4` deliberately reports no ECE/reliability diagram on the grounds
that these are P(label) vectors, not frequency forecasts. That argument is
reasonable, but it leaves open whether `p` means anything. On this corpus jev's
mean Brier is 3.55% — which with 49/50 correct labels says almost nothing,
because the labels are nearly saturated.

**Q4 — Does any of this survive outside a template-generated corpus?** Every
number here is on 30 synthetic templates authored by one model family (L2).

**Q5 — Do the untested interface surfaces behave?** Multi-question requests,
`state` as an object, `instructions` as object/array (L10). The "latency flat in
question count" claim is currently unverified.

**Q6 — Can a mechanism in this harness express abstention at all?** The harness
gives none of them a way to (N7). Until it does, area B is unmeasurable by
construction, and no Phase-2 escalation work should be commissioned against this
harness.

---

### THE SMALLEST JUSTIFIED NEXT EXPERIMENT

**Add exactly one cross-family general-model baseline to the existing grid.
Nothing else changes.**

*Why this one, under cheapest-test-first:* Q1 can **falsify the core premise**
that a Jev tier is needed — if a cheap general model from any family matches Jev,
the tier has no purchase. Q2 cannot falsify that premise; it only bounds one
supporting number, and it needs a purpose-built unanswerable corpus (expensive,
and exposed to the F1 defect class). So Q1 is both the higher-value question and
the cheaper test, and it is a pure add-one-baseline change on an existing corpus
with an existing, byte-deterministic scorer.

**Design (minimum viable, no new artefacts beyond the results):**

1. Select one operator-approved, **different-family** model (model selection is
   operator-gated per `AGENTS.md`; verify the exact ID with
   `opencode models <provider>` before use; record it in
   `manifest.json:models` alongside the existing entries). Cost fields must be
   recorded, not assumed.
2. Run it over the **unchanged** `cases.ndjson` (sha256
   `7dd4698f…`, unchanged) with the **byte-identical** `GEN_SYS` prompt and the
   same `build_general_request` shape already in `harness/run_baselines.py`.
   No new cases, no prompt tuning, no temperature change, no re-authoring. The
   corpus must not be touched, or the comparison is void.
3. Re-run `harness/score.py` unchanged. Read the paired McNemar cells for
   `cross_family` vs `jev` over the 50 answerable cases.
4. **Free rider, same run, no extra cost:** report the `cross_family` typed-error
   count over its own 64 cells, to replace the lucky 1/64 (**N6**) with a
   same-conditions measurement.

**Success / failure criteria, fixed before the run:**

| outcome | criterion on the 50 answerable cases | conclusion |
|---|---|---|
| **Jev's niche is supported** | cross-family accuracy **≤ 90%** (≥ 5 errors), **or** paired McNemar `c ≥ 3` (Jev right wherever the cross-family model is wrong, on ≥ 3 cells) | a cheap general model is measurably unreliable in a way that is model-family-dependent; a Jev tier has a defensible niche, and the next experiment is Q2 |
| **Jev's tier is unsupported** | cross-family accuracy **≥ 96%** (≤ 2 errors) **and** `c ≤ 1` | no cheap general model needs a special tier; the premise fails on this corpus and the budget should move to a non-synthetic evaluation of the cheap general model (Q4) |
| **inconclusive — declare it, do not pick a side** | 3–4 errors (92–94%) | n=50 cannot separate the two; this is the band where the Phase-1 sample is uninformative, and a larger corpus is required before any claim |

The bands are set by the Phase-1 sample, not chosen after the fact: with n=50, a
1–2 cell difference is inside the noise the run already documents
(`verification.md` §9.4). **The pre-registered band must be reported whichever
way it lands, including the inconclusive band.**

**What this experiment cannot tell us, stated up front:** it does not address
Q2 (the 0.04 margin), Q3 (calibration), or Q4 (synthetic corpus). If it lands in
the "niche supported" band, the *next* experiment is Q2 with **≥ 40** freshly
authored unanswerable cases whose ground truth is verified derivable-by-absence
before use — the F1 defect class makes corpus authoring, not measurement, the
bottleneck there. If it lands in the "unsupported" band, the correct next step is
to drop the Jev tier from the hypothesis and spend the remaining budget on a
non-synthetic evaluation of the cheap general model.

---

*Analysis performed 2026-09-26 by the D3 analyst, `opencode-go/space-bunny-free`,
in session isolation from D1 and D2 (all state read from git). Only
`research/jev-bounded-judgment/phase1/findings.md` was written. No pushes. No
scratch artefacts were left in the repository.*
