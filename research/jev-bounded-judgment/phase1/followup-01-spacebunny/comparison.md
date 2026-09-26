# followup-01-spacebunny — one new baseline vs the frozen Jev results

**Crosslink issue:** #565 · **Follow-up to:** `research/jev-bounded-judgment/phase1/`
**Run:** 2026-09-26T04:54:19Z–04:55:50Z · **Scored:** 2026-09-26T04:58:49Z
**Question:** run exactly one new baseline, `space-bunny-free`, over the
unchanged frozen corpus under frozen conditions, and compare it to the frozen
Jev results. Nothing else changed.

---

## 1. Headline

| | value |
|---|---|
| transport failures (spacebunny) | **1 / 64** (`b-a05`, `empty_content`, HTTP 200) |
| raw answerable accuracy | **49/50 = 98.0%** |
| F1-corrected answerable accuracy | **48/48 = 100.0%** |
| paired vs Jev — raw (`b`/`c`/ties) | **0 / 0 / 50** (49 both right, 1 both wrong) |
| paired vs Jev — corrected (`b`/`c`/ties) | **0 / 0 / 48** (48 both right, 0 both wrong) |
| **band verdict (F1-corrected)** | **REFUTES a Jev niche** — `acc 1.0 ≥ 0.96` and `c 0 ≤ 1`, both arms fire |

Spacebunny and Jev are **indistinguishable on this corpus**: zero discordant
cells in either direction, under either ground-truth view. Spacebunny's single
raw-GT error is `c-p4b` — the defective case from `verification.md` §2 F1, and
the same cell Jev gets wrong. Under the F1 correction both are 48/48.

**The verdict rests on a 2-cell margin, and one of those cells was observed
flipping between two runs of this very mechanism.** See §6 before quoting the
verdict.

---

## 2. Comparison, overall

Denominators are stated in every cell. `acc` divides by **usable** answerable
cells; transport failures are excluded from the semantic denominator and
reported separately, per the brief. Unanswerable behaviour is reported in its
own column and never folded into `acc` — answering an unanswerable case is an
abstention failure, not a wrong label.

### Raw ground truth (committed labels: 50 answerable / 14 unanswerable)

| mechanism | correct | usable in answerable | transport failures in answerable | acc | answered unanswerable |
|---|---|---|---|---|---|
| `jev` (frozen) | 49 | 50 | 0 | **98.0%** | 14/14 |
| `general_model` (frozen, same mechanism) | 50 | 50 | 0 | **100.0%** | 13/14 |
| `spacebunny` (this run) | 49 | 50 | 0 | **98.0%** | 13/14 |

### F1-corrected ground truth (`c-p4a`+`c-p4b` → unanswerable: 48 / 16)

| mechanism | correct | usable in answerable | transport failures in answerable | acc | answered unanswerable |
|---|---|---|---|---|---|
| `jev` (frozen) | 48 | 48 | 0 | **100.0%** | 14/14 |
| `general_model` (frozen) | 48 | 48 | 0 | **100.0%** | 15/16 |
| `spacebunny` (this run) | 48 | 48 | 0 | **100.0%** | 15/16 |

The correction is applied identically to all three mechanisms. It moves Jev
98.0% → 100.0% and spacebunny 98.0% → 100.0%, and it moves the frozen
`general_model` 100.0% → 100.0%. It is a change of yardstick, not of any
subject's score. It is applied because `verification.md` §2 F1 found `cp4`'s
ground truth is not derivable from the model-visible text, and `c-p4b` is the
**only** raw-GT error either model makes.

### Scope axes

All existing axes only. Area B has 0 answerable cases, so its `acc` is `n/a` by
construction, not by failure.

**Raw GT**

| scope | n answerable | `spacebunny` | `jev` | `general_model` |
|---|---|---|---|---|
| area A | 22 | 22/22 = 100.0% | 100.0% | 100.0% |
| area B | 0 | n/a | n/a | n/a |
| area C | 16 | 15/16 = 93.8% | 93.8% | 100.0% |
| area D | 12 | 12/12 = 100.0% | 100.0% | 100.0% |
| split train | 18 | 18/18 = 100.0% | 100.0% | 100.0% |
| split dev | 15 | 14/15 = 93.3% | 93.3% | 100.0% |
| split test | 17 | 17/17 = 100.0% | 100.0% | 100.0% |
| qtype `noul` | 36 | 35/36 = 97.2% | 97.2% | 100.0% |
| qtype `choice` | 12 | 12/12 = 100.0% | 100.0% | 100.0% |
| qtype `score` | 2 | 2/2 = 100.0% | 100.0% | 100.0% |

**F1-corrected GT** — every scope is 100.0% for all three mechanisms
(area A 22, C 14, D 12; train 18, dev 13, test 17; `noul` 34, `choice` 12,
`score` 2). No mechanism has a single semantic error left on ground truth that
is derivable from the corpus text.

Per-case verdicts for both views: `results/paired.ndjson` (64 rows).

---

## 3. Paired comparison vs frozen Jev

Pairing: answerable cells (in the view's ground truth) where **both**
mechanisms emitted a usable label. `b` = spacebunny right & Jev wrong;
`c` = Jev right & spacebunny wrong.

| view | n paired | excluded (unanswerable) | excluded (transport) | spacebunny | Jev | delta | **`b`** | **`c`** | ties (both R / both W) |
|---|---|---|---|---|---|---|---|---|---|
| raw GT | 50 | 14 | 0 | 98.0% | 98.0% | +0.0pp | **0** | **0** | 50 (49 / 1) |
| F1-corrected | 48 | 16 | 0 | 100.0% | 100.0% | +0.0pp | **0** | **0** | 48 (48 / 0) |

Discordant case ids: **none in either direction, in either view.** The one
"both wrong" cell in the raw view is `c-p4b`, which the F1 correction removes.

`b` and `c` are independently cross-checked inside the scorer against the
frozen `_paired_gain` from `harness/score.py`, which computes them by a
different code path; a disagreement is a hard stop. They agree.

The stated denominators in §2 are cross-checked the same way, against the frozen
`_acc`, for all three mechanisms under both ground-truth views: `n_answerable`,
`n_usable_in_answerable`, `n_correct` and `acc_answerable` must all match. They
do. A silent drift in a denominator would therefore stop the scorer rather than
propagate into a headline.

---

## 4. Transport failures, kept separate from judgement

| mechanism | cells | usable | transport failures | typed error | failed case | that case answerable? |
|---|---|---|---|---|---|---|
| `jev` | 64 | 64 | 0 | — | — | — |
| `general_model` (frozen) | 64 | 63 | 1 | `empty_content` | `b-i03` | no |
| `spacebunny` (this run) | 64 | 63 | 1 | `empty_content` | `b-a05` | no |

All 64 cells returned HTTP 200. The single failure is a 200 with an empty
`content` field — the documented reasoning-model failure mode that
`harness/run_baselines.py` already records at `max_tokens=16` and which forced
`max_tokens` to 256.

**The failure landed on an unanswerable case, so it cannot move a semantic
answerable accuracy under any counting convention.** `b-a05` is area B. Bounded
sensitivity:

| convention | acc | band verdict |
|---|---|---|
| excluded from denominators (point estimate) | 100.0% | REFUTES |
| transport failure counted as an error | 100.0% | REFUTES |
| transport failure counted as correct | 100.0% | REFUTES |

All three agree, because the denominator contains the failure zero times. This
is the degenerate case the scorer's `_note` warns about, and it is reported as
degenerate rather than dressed up as a sensitivity result. **Had the failure
landed on an answerable case, the two variants would have differed by 1/48
(2.1pp) and 1/48 respectively.**

Latency and cost, for the record: min 935.1 / median 1222.3 / mean 1439.7 /
max 4114.5 ms; input tokens 16527, output tokens 1747. The frozen run was
min 901.5 / median 1157.9 / mean 1342.1 / max 3615.2 ms; input 16527, output
1321. **Input tokens are identical to the unit**, which independently confirms
the requests sent were byte-identical. Output tokens differ by 426, consistent
with non-deterministic reasoning length at temperature 0.

---

## 5. Band evaluation

Bands transcribed verbatim from `findings.md` §6, applied to the
**F1-corrected semantic accuracy**, support evaluated before refute.

```
supports      acc <= 0.90  OR  c >= 3
refutes       acc >= 0.96  AND c <= 1
uninformative 0.92 <= acc <= 0.94
otherwise     OUTSIDE the defined bands
```

| | acc | c | verdict | conditions fired |
|---|---|---|---|---|
| **primary** (corrected acc + corrected `c`) | **1.0** | **0** | **REFUTES a Jev niche** | `acc 1.0 >= 0.96` (refute arm 1); `c 0 <= 1` (refute arm 2) |
| variant (raw acc + raw `c`) | 0.98 | 0 | REFUTES a Jev niche | `acc 0.98 >= 0.96`; `c 0 <= 1` |
| transport counted as error | 1.0 | 0 | REFUTES a Jev niche | `acc 1.0 >= 0.96`; `c 0 <= 1` |
| transport counted as correct | 1.0 | 0 | REFUTES a Jev niche | `acc 1.0 >= 0.96`; `c 0 <= 1` |

Support was evaluated first and **did not fire**: `acc 1.0` is not `≤ 0.90`, and
`c = 0` is not `≥ 3`. Refute then fired on **both** arms. No band was invented,
moved, or reinterpreted, and the OUTSIDE branch was not reached.

**`c` used:** 0, from the paired cells on the F1-corrected answerable set
(n=48), which is the set the corrected accuracy is measured on. The raw-set
value is also 0 (n=50), so the choice of set does not affect the verdict.

---

## 6. Execution anomalies — read this before quoting §1 or §5

**Anomaly 1 — this mechanism is not reproducible cell-by-cell at temperature 0.**
Comparing this run to the frozen run of the *same* mechanism (same model, same
`GEN_SYS`, same route, same temperature, N=1 each):

| outcome | n |
|---|---|
| label agrees | 60 |
| **label disagrees** | **2** (`b-a01`, `c-p4b`) |
| unusable in exactly one run | 2 (`b-a05` new, `b-i03` frozen) |
| unusable in both | 0 |

- `c-p4b`: frozen said `no` (correct), this run said `yes` (wrong). **This is
  the one cell that separates 100.0% from 98.0%, and it flipped between two
  samples of the same mechanism.** It is also the corpus's defective case.
- `b-a01`: frozen `yes`, this run `no`. Unanswerable, so it does not touch
  semantic accuracy.
- The transport failure also **moved**: `b-i03` in the frozen run, `b-a05`
  here. So the *rate* reproduces (1/64 `empty_content` twice) but the *cell*
  does not. `findings.md` §4 N6 called the frozen 1/64 lucky; this run
  reproduces the rate under identical conditions, which is a real reliability
  datapoint and a real non-reproducibility datapoint at the same time.

**Anomaly 2 — the band verdict has a 2-cell margin.** Re-applying the same bands
verbatim at `k` additional answerable errors (each taken on a cell Jev also got
right, so `c` rises with `k`):

| k | acc | c | verdict |
|---|---|---|---|
| 0 | 1.0000 | 0 | REFUTES |
| 1 | 0.9792 | 1 | REFUTES |
| **2** | 0.9583 | 2 | **OUTSIDE the defined bands** |
| 3 | 0.9375 | 3 | supports a Jev niche |
| 4 | 0.9167 | 4 | supports a Jev niche |
| 5 | 0.8958 | 5 | supports a Jev niche |
| 6 | 0.8750 | 6 | supports a Jev niche |

The verdict changes at **k = 2** and inverts at **k = 3**. One such answerable
flip was in fact observed between the two runs of this mechanism (`c-p4b`), and
in the raw-GT view this run already carries k = 1. **A 2-cell margin on n=48
is not a robust verdict, and I am reporting it as one.** No new threshold is
proposed; the point is that this corpus cannot carry the distinction between
"refutes" and "outside the bands".

**Anomaly 3 — the band was pre-registered for a different model class.** See §7.

No guard incident, no consent gate, no rate-limit parking, no retry, no
`internal_error`. 64/64 HTTP 200. The run is clean; the instability in §6.1 is
in the model, not the harness.

---

## 7. What this does and does not resolve

**The model-family confound runs one way, and it is the wrong way for Jev.**
Space Bunny is a *different* family from Jev — that much is true and is why the
paired comparison is worth running. But `findings.md` §4 L1 records that
Space Bunny is the **same** family as:

- the corpus author (`gen_cases.py`, all 64 cases, all ground truth),
- the harness author (`GEN_SYS`, the cue lexicons, `score.py`, `common.py`),
- the D1/D2/D3 authors (builder, verifier, analyst), and
- the verifier whose F1 finding is applied as the correction above.

So the model being compared against Jev wrote the corpus it is being tested
on, wrote the prompt it is answering, and wrote the vocabulary its accuracy is
scored against. **This confound can only inflate `spacebunny`, never deflate
it.** The measured tie is therefore an upper bound on the baseline's real
standing, and the REFUTES verdict is, if anything, conservative in the
direction that disfavours the conclusion being drawn.

**What this DOES establish.**

1. On this corpus, under byte-identical frozen conditions, a same-family free
   general model **matches Jev exactly**: 0 discordant cells in 48 paired
   answerable cells, in both directions, under both ground-truth views. The
   Phase-1 observation S3 ("Jev does not beat the free general model") is
   **reproduced on an independent sample** and is not a one-run artefact.
2. The one raw-GT error on either side is `c-p4b`, whose ground truth is not
   derivable from the text. After the F1 correction, **no mechanism in this
   directory has a single semantic error on derivable ground truth** — Jev, the
   frozen `general_model`, and this run are all 48/48.
3. A free-rider reliability datum for S3/N6: the `empty_content` rate is
   1/64 in both runs of this mechanism under identical conditions, and it moves
   between cells — so the rate is a property and the cell is not.
4. The refute band fires, and it fires on **both** arms, on both ground-truth
   views, and under both transport-failure counting conventions.

**What this does NOT resolve.**

1. **It is not the Q1 experiment.** `findings.md` §6 pre-registered this
   experiment for a **cross-family** model. This run is a same-family
   **replicate**. Q1 — *is Jev's non-advantage a property of cheap general
   models, or a property of one family reading one family's prose?* — is
   **still untested**. The band verdict in §5 is applied verbatim as
   instructed, but it is **not** the answer to Q1 and must not be reported as
   one. The genuine Q1 test needs a different-family model, which is
   operator-gated (`AGENTS.md` model discipline).
2. **It says nothing about escalation.** `findings.md` S5's zero-errors-at-0.90
   result rests on Jev's *derived* confidence distribution over 14
   unanswerable cases and a 0.04 margin. `spacebunny` is hard-decoded to
   confidence 1.0 by construction, so its threshold behaviour is an encoding
   artefact (`findings.md` §4 L7) and is not measured here at all. Q2 remains
   open.
3. **n = 64, one run, N = 1 per cell, free-tier unpinned models.** No
   significance test is claimed (`schema.md` §5). The 2-cell margin in §6.2 is
   inside the noise this corpus already documents.
4. **Nothing outside a template-generated corpus.** All 64 cases are synthetic,
   30 templates, one authoring family (§4 L2, Q4). The 100% figures are
   properties of this corpus, full stop.
5. **It cannot license "drop the Jev tier."** The refute band says a Jev tier
   has no purchase *on this corpus against this model*. Per §4 L1 that model is
   the corpus's own author, so the honest reading is that the comparison is
   uninformative about cheap general models in general — which is a stronger
   reason to run the cross-family test, not a weaker one.

**Recommended next step, unchanged from `findings.md` §6:** run the same
protocol with an operator-approved **cross-family** model. The harness here
already supports it — change only `--model` in the runner; the frozen-condition
gate will refuse any other change. That single substitution is the smallest
thing that can move Q1.

---

## 8. Artefacts

| file | contents |
|---|---|
| `harness/run_spacebunny.py` | the runner; 4 pre-call gates, `max_attempts=1` |
| `harness/score_followup.py` | the scorer; stdlib only, reuses `common.py` + `score.py` |
| `results/spacebunny_raw.ndjson` | 64 rows, same row format as `baselines_raw.ndjson` |
| `results/paired.ndjson` | 64 rows: both verdicts, transport flags, raw + corrected correctness |
| `results/comparison.json` | every number above, with denominators |
| `results/manifest.json` | frozen hashes, model, endpoint, conditions, commit, timestamps, error counts |

No frozen Phase-1 file was modified. Reproduce with `README.md` in this
directory.
