# followup-01-spacebunny — INDEPENDENT VERIFICATION

**Crosslink issue:** #565 · **Under test:** `research/jev-bounded-judgment/phase1/followup-01-spacebunny/`
**Verifier:** fresh session, no builder context, read-only except this file.
**Date:** 2026-09-26 · **Branch:** `research/jev-phase1-565` @ `a15b0b97`
**Scratch:** `/tmp/opencode/jev-phase1-followup-verify/` (nothing written inside the repo)

---

## 0. Method, and what it deliberately does not do

**Not done, by instruction and by design:** the follow-up scorer
(`followup-01-spacebunny/harness/score_followup.py`) was **not imported** for any
recomputation. Every number in §2–§5 below was recomputed from `cases.ndjson` +
the three raw `.ndjson` files by a script written for this verification
(`indep.py`, `diff.py`, `paired_check.py`, `bands.py`, `ci.py` in the scratch
directory), using an independently reimplemented request-hash function and an
independently written band evaluator. The follow-up's outputs were read only as
*things to be diffed against*, never as inputs to a computation.

**What was done:** frozen-hash re-derivation; `git diff` audit of the three
follow-up commits; byte-level request/body comparison against the frozen
`general_model` rows; anti-fabrication forensics on the raw rows; an exhaustive
numeric diff of every figure in `comparison.json`; a full 64-row field-level
re-derivation of `paired.ndjson`; a band-logic analysis including
order-independence; a byte-identity re-score of the committed artefacts; and a
**live 8-case re-run** against the production endpoint.

**Standing on the results of the follow-up itself:** one — that its scorer is
deterministic and reproduces the committed bytes. That claim is checkable
without trusting its arithmetic, so it was checked by re-running the scorer into
a scratch directory rather than taken on trust.

---

## 1. PASS / FAIL table

| # | Task | Claim under test | Verdict | Evidence |
|---|---|---|---|---|
| 1 | Frozen inputs | `cases.ndjson` = `7dd4698f…f558c` | **PASS** | recomputed sha256 identical |
| 1 | Frozen inputs | `results/jev_raw.ndjson` = `e17ae01…d3bc` | **PASS** | recomputed sha256 identical |
| 1 | Frozen inputs | no frozen Phase 1 file modified | **PASS** | `git diff --name-only 355ab6ad..HEAD` outside followup dir → empty |
| 1 | Frozen inputs | only new files under `followup-01-spacebunny/` | **PASS** | 8 tracked files, all in that dir; only untracked are `.crosslink/` infra + gitignored `__pycache__` |
| 2 | New rows | 64 rows | **PASS** | 64 lines, 64 unique `case_id`, set-equal to frozen `general_model` |
| 2 | New rows | row format matches `baselines_raw.ndjson` | **PASS** | identical 21-key schema, all rows |
| 2 | New rows | request hash == frozen `general_model` | **PASS** | 64/64; and 64/64 `request_body` byte-equal (insertion order preserved) |
| 2 | New rows | stored hash recomputes from stored body | **PASS** | 64/64 with an independent sha256 reimplementation |
| 2 | New rows | `model_id` `space-bunny-free`, correct endpoint | **PASS** | 64/64 `space-bunny-free`; 64/64 `https://opencode.ai/zen/v1/chat/completions` |
| 2 | New rows | raw bodies parse, verbatim | **PASS** | 64/64 parse; `parsed.raw_content == choices[0].message.content` 64/64 |
| 2 | New rows | transport failures typed, none silently retried | **PASS** | `attempt=1`, `retries=0` on 64/64; 1 × `empty_content` typed |
| 2 | New rows | no fabricated rows | **PASS** | 64 unique provider ids, 0 overlap with the frozen run, all timestamps within 0–4 s of the provider's own `created` field |
| 3 | Recomputation | raw acc n=50 | **PASS** | Jev 49/50 = 98.0 %, `general_model` 50/50 = 100.0 %, spacebunny 49/50 = 98.0 % |
| 3 | Recomputation | F1-corrected acc n=48 | **PASS** | all three 48/48 = 100.0 % |
| 3 | Recomputation | per-scope, 10 scopes × 3 mechs × 2 views | **PASS** | 0 discrepancies |
| 3 | Recomputation | paired b/c/ties vs Jev | **PASS** | raw `b=0 c=0 ties=50 (49R/1W)`; corrected `b=0 c=0 ties=48 (48R/0W)` |
| 3 | Recomputation | band logic, support before refute | **PASS** | reproduced; and shown **order-immaterial** for the verdict |
| 3 | Recomputation | 92–94 % uninformative; outside reported as-is | **PASS** | band reproduced exactly; OUTSIDE branch present and unreached |
| 3 | Recomputation | every figure in `comparison.json` | **PASS** | **0 discrepancies** across the exhaustive diff |
| 3 | Recomputation | all 64 rows of `paired.ndjson` | **PASS** | 0 field-level discrepancies |
| 4 | Live re-run | 8 answerable cases, frozen request shape | **PASS** | 8/8 label agreement, 0 transport failures, same 7/8 accuracy |
| 4 | Live re-run | transport-failure variance quantified | **PASS** | 2 `empty_content` / 136 cells over two full runs, different cells; 0/8 in re-run (P=0.88 under p=1/64) |
| 5 | Correction | cp4 unanswerable for BOTH mechanisms | **PASS** | `cp4` = exactly `{c-p4a, c-p4b}`; applied to all three; `raw_f1_corrected=true` on both |
| 5 | Correction | corrected denominators 48 / 16 | **PASS** | 50→48 answerable, 14→16 unanswerable |
| 5 | Correction | false-confidence denominators | **PASS** | Jev 14/14→16/16; `general_model` 13/14→15/16; spacebunny 13/14→15/16 |
| 6 | Adversarial | case inputs unchanged | **PASS** | frozen hash, unchanged at every follow-up commit |
| 6 | Adversarial | no request-shape drift | **PASS** | 64/64 body-byte-equal; input tokens 16527 in both runs, identical to the unit |
| 6 | Adversarial | `comparison.md` does not overstate | **PASS** | confound disclosed in 5 places; explicitly refuses the Q1 and "drop the tier" readings |
| 6 | Adversarial | band verdict matches pre-specified logic + numbers | **PASS** | REFUTES on both arms; margin claim holds in **both** views |
| — | Determinism | scorer reproduces committed bytes | **PASS** | re-scored into scratch → `comparison.json` `c1808199…`, `paired.ndjson` `23c016f5…`, `manifest.json` `07b3c98a…`; `DETERMINISM: IDENTICAL`; `cmp` byte-identical |

**29 / 29 PASS. Zero FAIL. Three minor faults, none of which affects any
reported number** (§4).

---

## 2. Task 1 — frozen-input integrity

Recomputed on the working tree:

```
7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c  cases.ndjson
e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc  results/jev_raw.ndjson
42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba  results/baselines_raw.ndjson
```

Both named digests match exactly. The third (also gated by the runner, and
carried in `manifest.json`) matches too.

**No frozen Phase 1 file was modified.** The follow-up is three commits —
`42d2fdbc` (runner), `f4ad24ac` (raw run), `a15b0b97` (scorer + report). Diffing
the pre-follow-up tree against `HEAD`:

```
$ git diff --name-only 355ab6ad..HEAD -- . | grep -v 'followup-01-spacebunny/'
(none)
```

Every path changed since the findings commit is inside
`followup-01-spacebunny/`. Stronger still, the two frozen digests are **byte-
identical at every one of those commits** (`355ab6ad`, `42d2fdbc`, `f4ad24ac`,
`a15b0b97`, `HEAD`), so no frozen file was touched and reverted either.

**New files.** The only tracked additions are the 8 files inside
`followup-01-spacebunny/`. The only untracked paths in the repo are
`.crosslink/agents-hygiene.json` and a one-line change to
`.crosslink/.last-hydrated-ref` — both crosslink infrastructure, neither a Phase 1
artefact. The stray `harness/__pycache__/*.pyc` are covered by
`.gitignore:38`. **No push** was performed by this verification.

---

## 3. Tasks 2–5 — the substantive recomputation

### 3.1 Request integrity (Task 2)

| check | result |
|---|---|
| stored `request_hash` recomputes from stored `request_body` | **64/64** |
| `request_hash` == frozen `general_model` `request_hash` | **64/64** |
| `request_body` == frozen `general_model` `request_body`, **byte-exact, insertion order preserved** | **64/64** |
| `temperature` / `max_tokens` / `model` / message count | `{0}` / `{256}` / `{space-bunny-free}` / `{2}` — uniform |
| system prompt identical to the frozen run | **True** (1 distinct value) |

The body check matters more than the hash check, because the frozen harness
deliberately hashes *unsorted* bytes so that the `option_reorder` control cannot
collide with its base. Comparing the serialised bodies directly, not
key-sorted, closes that gap: **there is no prompt or parameter drift of any
kind.**

### 3.2 Transport hygiene and non-fabrication (Task 2)

```
http_status : {200: 64}          attempt : {1: 64}      retries : {0: 64}
typed_error : {None: 63, empty_content: 1}             secrets_recorded : {False: 64}
```

One attempt, zero retries on every cell — **no silent retry anywhere**. The
single failure is `b-a05`: HTTP 200, `finish_reason: "length"`,
`output_tokens = 256 = max_tokens`, `reasoning_tokens = 256`, empty `content`.
That is exactly the reasoning-model failure mode the frozen harness documents at
`max_tokens=16`; the row is correctly typed, not silently dropped.

Fabrication forensics — the strongest evidence available without provider logs:

* 64/64 `raw_response` bodies parse as JSON; `parsed.raw_content` equals
  `choices[0].message.content` on 64/64.
* `model` inside the provider's own response body is `space-bunny-free` 64/64.
* 64/64 provider response `id`s are **unique**, and the overlap with the frozen
  run's ids is **zero** — a replayed or synthesised file would not do this.
* Every recorded `timestamp_utc` agrees with the provider's own `created` field
  to within **0–4 s**; the provider span is 90 s and the recorded span is 91 s.
  Fabricated timestamps would not track a third party's clock this closely.
* `finish_reason`: 63 × `stop`, 1 × `length` — a plausible, non-uniform shape.
* Input tokens total **16527 in this run and 16527 in the frozen run**,
  identical to the unit across 64 independent calls. This is a
  near-impossible coincidence to manufacture and is independent confirmation
  that the requests sent were byte-identical.

**No fabricated rows.**

### 3.3 Independent recomputation (Task 3)

Recomputed from raw, scorer not imported:

| view | mechanism | n answerable | usable | transport | correct | acc | answered unanswerable |
|---|---|---|---|---|---|---|---|
| raw | `jev` (frozen) | 50 | 50 | 0 | 49 | **98.0 %** | 14/14 |
| raw | `general_model` (frozen) | 50 | 50 | 0 | 50 | **100.0 %** | 13/14 |
| raw | **`spacebunny`** | 50 | 50 | 0 | 49 | **98.0 %** | 13/14 |
| corrected | `jev` (frozen) | 48 | 48 | 0 | 48 | **100.0 %** | 16/16 |
| corrected | `general_model` (frozen) | 48 | 48 | 0 | 48 | **100.0 %** | 15/16 |
| corrected | **`spacebunny`** | 48 | 48 | 0 | 48 | **100.0 %** | 15/16 |

Per-scope (raw GT), all three mechanisms:

| scope | n | spacebunny | jev | general_model |
|---|---|---|---|---|
| area A | 22 | 22/22 | 22/22 | 22/22 |
| area B | 0 | n/a | n/a | n/a |
| area C | 16 | 15/16 = 93.8 % | 15/16 | 16/16 |
| area D | 12 | 12/12 | 12/12 | 12/12 |
| train / dev / test | 18 / 15 / 17 | 18/18, 14/15, 17/17 | identical | 18/18, 15/15, 17/17 |
| `noul` / `choice` / `score` | 36 / 12 / 2 | 35/36, 12/12, 2/2 | identical | 36/36, 12/12, 2/2 |

F1-corrected: every scope is 100 % for all three mechanisms (A 22, C 14, D 12;
train 18, dev 13, test 17; `noul` 34, `choice` 12, `score` 2).

Paired, spacebunny vs Jev (`b` = spacebunny right / Jev wrong):

| view | n paired | excl. unanswerable | excl. transport | b | c | ties |
|---|---|---|---|---|---|---|
| raw | 50 | 14 | 0 | **0** | **0** | 50 (49 R / 1 W) |
| corrected | 48 | 16 | 0 | **0** | **0** | 48 (48 R / 0 W) |

**Exhaustive diff against `comparison.json`: 0 discrepancies.** Every
`n_answerable`, `n_correct`, `n_usable_in_answerable`,
`n_transport_failures_in_answerable`, `n_unanswerable`,
`n_answered_unanswerable`, `n_semantic_errors`, `acc_answerable`, `acc_pct`,
`false_confidence_rate`, every `by_area` / `by_split` / `by_question_type` cell,
the `accuracy_cross_check` block, the `frozen_general_model_reference` block,
the `paired_vs_jev` and `paired_cross_check` blocks, the `transport` block and
the `f1_correction` block reproduce exactly. The only differences encountered
anywhere were four values stored rounded to 4 dp (`0.9333`, `0.9722`, `0.9286`);
each is the correct 4-dp rounding of its exact fraction, and the matching
`acc_pct` strings are exact.

**All 64 rows of `paired.ndjson` re-derived field by field — 0 discrepancies**,
including per-view correctness, usability, paired outcome, area, split, question
type, HTTP status, latency and the full usage block.

### 3.4 Band logic (Tasks 3 and 6)

Bands transcribed from `findings.md` §6, applied to the F1-corrected accuracy,
support evaluated before refute:

```
supports      acc <= 0.90  OR  c >= 3
refutes       acc >= 0.96  AND c <= 1
uninformative 0.92 <= acc <= 0.94
otherwise     OUTSIDE the defined bands
```

| | acc | c | verdict | my result |
|---|---|---|---|---|
| primary (corrected) | 1.0 | 0 | REFUTES | **REFUTES** ✔ both arms |
| variant (raw) | 0.98 | 0 | REFUTES | **REFUTES** ✔ |
| transport as error | 1.0 | 0 | REFUTES | **REFUTES** ✔ |
| transport as correct | 1.0 | 0 | REFUTES | **REFUTES** ✔ |

Two structural checks the report does not make, both of which **strengthen** it:

* **Support and refute are mutually exclusive.** Over a sweep of all
  `acc ∈ [0, 1]` at 0.001 resolution × `c ∈ [0, 11]`, the number of points where
  both fire is **0**. The "support before refute" ordering is therefore
  **immaterial to the verdict**; I confirmed all four reported variants return
  the same label under three different evaluation orders.
* **The 2-cell margin holds in both views.** Corrected (n=48): `k=0` REFUTES,
  `k=1` REFUTES, `k=2` **OUTSIDE**. Raw (n=50): `k=0` REFUTES, `k=1` REFUTES,
  `k=2` **uninformative**. The verdict changes at `k=2` either way, so the
  report's "2-cell margin" is not an artefact of choosing the corrected view.

### 3.5 Live re-run of 8 answerable cases (Task 4)

8 answerable cases, including the observed flip cell `c-p4b`, replayed from the
**frozen request bytes** (taken verbatim from the frozen `general_model` row, so
the request shape is frozen by construction), 1 attempt, 0 retries, same headers
as the frozen harness. This uses neither the follow-up runner nor its scorer.

| case | GT | committed | frozen `general_model` | Jev | **re-run** | status | agree |
|---|---|---|---|---|---|---|---|
| `c-p4b` | no | yes | no | yes | **yes** | 200 | ✔ |
| `c-p4a` | yes | yes | yes | yes | **yes** | 200 | ✔ |
| `a-dist1` | no | no | no | no | **no** | 200 | ✔ |
| `d-01` | build | build | build | build | **build** | 200 | ✔ |
| `a-h04` | low | low | low | low | **low** | 200 | ✔ |
| `c-i1` | yes | yes | yes | yes | **yes** | 200 | ✔ |
| `a-m01` | no | no | no | no | **no** | 200 | ✔ |
| `d-04` | repair | repair | repair | repair | **repair** | 200 | ✔ |

* **Label agreement 8/8. Transport failures 0/8.**
* Accuracy on these 8: **7/8 — identical to the committed run's 7/8.** Error
  rate unchanged.
* **`c-p4b` has now been sampled three times by the same mechanism**: frozen
  `general_model` said `no` (correct), the committed run said `yes` (wrong), my
  re-run said `yes` (wrong). Three samples, two distinct labels, 2/3 wrong. This
  **independently confirms and strengthens** the report's own Anomaly 1 — the
  mechanism is genuinely not cell-reproducible at `temperature 0`, and the
  committed run landed on the majority-wrong side of the corpus's defective
  case. It also shows the F1 correction is doing real work rather than papering
  over a scorer artefact.

**Transport-failure variance** (reported as API nondeterminism, *not* as
misconduct):

| sample | `empty_content` | rate | 95 % CI (exact, Clopper-Pearson) |
|---|---|---|---|
| frozen `general_model` run | 1/64 (`b-i03`) | 1.56 % | [0.04 %, 8.40 %] |
| committed `spacebunny` run | 1/64 (`b-a05`) | 1.56 % | [0.04 %, 8.40 %] |
| this re-run (answerable cells only) | 0/8 | 0 % | [0 %, 36.9 %] |
| pooled, two full runs | 2/136 | 1.47 % | [0.18 %, 5.21 %] |

`P(0 failures in 8 | true rate 1/64) = 0.88`, so the re-run is unremarkable. The
**rate** is similar across the two full runs; the **cell** is not
(`b-i03` vs `b-a05`). Both failures are the same typed mode
(`finish_reason: length`, all 256 tokens spent on reasoning). This is exactly
what the report says it is: expected nondeterminism on a free-tier unpinned
endpoint.

### 3.6 Correction check (Task 5)

* `cp4` is exactly `{c-p4a, c-p4b}`; both carry `raw_f1_corrected: true` in
  `paired.ndjson` and both are reclassified unanswerable.
* Applied **identically to all three mechanisms** — Jev, the frozen
  `general_model`, and the new run — so it is a change of yardstick, not of any
  subject's score. Confirmed by re-deriving all three columns.
* **Corrected denominators:** answerable 50 → **48**, unanswerable 14 → **16**.
* **False-confidence denominators (16 where relevant):**

  | mechanism | raw | corrected |
  |---|---|---|
  | `jev` | 14/14 | **16/16** |
  | `general_model` | 13/14 (`b-i03` failed) | **15/16** |
  | `spacebunny` | 13/14 (`b-a05` failed) | **15/16** |

  `false_confidence_rate` 0.9286 → 0.9375. The Jev and `general_model` rows
  reproduce the frozen F1 table in `verification.md` §2 exactly; the spacebunny
  row is new and consistent with it. Note both mechanisms show 13/14 raw and
  15/16 corrected for *different* reasons (a different case failed in each) —
  the coincidence of the counts is correctly not treated as meaningful anywhere.

### 3.7 Determinism of the committed artefacts

The scorer was re-run into a scratch `--results-dir` with the documented pins:

```
$ python3 .../score_followup.py --results-dir <scratch> --self-check \
    --generated-utc 2026-09-26T04:58:49Z --commit f4ad24acf6c6a2467445ba8d242aaf0895594769
  3 frozen digests OK
  pass 1 / pass 2: comparison.json c1808199…  paired.ndjson 23c016f5…  manifest.json 07b3c98a…
  DETERMINISM: IDENTICAL
```

`cmp` against the committed files: **all three byte-identical**, and the digests
match the README's clean-clone claim. The README's reproduction instructions
are accurate, with the one exception noted in F1 below.

### 3.8 Adversarial: does `comparison.md` overstate? (Task 6)

**No. If anything it under-claims.** The same-family confound — corpus author,
harness author, `GEN_SYS` author, and the verifier whose F1 finding is applied
as the correction are all `space-bunny-free` — is disclosed in **five** separate
places: `README.md` §"How to read a number" item 4, `manifest.json`
`model.family`, `comparison.json` `_read_before_quoting` and
`band_evaluation._design_caveat`, and `comparison.md` §7 (heading plus body).

The direction of the confound is stated correctly and argued correctly: it can
only **inflate** the baseline, so the measured tie is an **upper bound** on its
real standing. The report then explicitly refuses the two readings a reader would
be tempted to take:

* "**It is not the Q1 experiment.** … Q1 is **still untested**. The band verdict
  … is **not** the answer to Q1 and must not be reported as one."
* "**It cannot license 'drop the Jev tier.'**"

It also volunteers the finding that cuts against its own headline — the 2-cell
margin, and the fact that one of the two cells was observed flipping between
runs. It reports the ceiling effect on the tie ("The 100 % figures are
properties of this corpus, full stop") and declines to claim any significance
test, consistent with `schema.md` §5. **I found no overstatement.**

The band verdict itself matches the pre-specified logic and the numbers, with
the ordering shown immaterial above.

---

## 4. Faults

Three minor faults. **None affects any number, verdict, or band outcome.** None
is a fabrication, a drift, or a miscount. Reported, not fixed, per instruction.

### F1 — `--check-only` prints an unverified constant (minor, reporting defect in a gate)

`run_spacebunny.py:200-201` guards the actual request comparison behind
`if not check_only:` — so in `--check-only` mode
`verify_frozen_requests()` **is never called**, while the function still prints:

```
  frozen-condition check: 64/64 requests identical (preflight)
```

That line is a hardcoded f-string, not a result. Proven by instrumenting the
function:

```
>>> verify_frozen_requests INVOKED during --check-only ? False
>>> verify_frozen_requests INVOKED during real run    ? True
```

`README.md` §Reproduce step 1 presents this command as *the* way to "Verify the
gates — zero HTTP calls" and lists "64/64 requests identical" among the expected
output. A reader following the README would take a constant as a verification.
The underlying claim is nonetheless **true** — I confirmed 64/64 body-byte
equality independently, from the stored rows, without the runner (§3.1) — so no
result is affected. Impact is confined to a reader's assurance, on the one gate
that is described as checkable before spending money.

*Suggested remedy (not applied):* run `verify_frozen_requests(cases)` in both
modes — it makes no HTTP call, so it belongs in `--check-only`.

### F2 — "the rate is a property" overreaches two observations (minor, inference strength)

`comparison.md` §7 point 3: *"the `empty_content` rate is 1/64 in both runs of
this mechanism under identical conditions, and it moves between cells — so the
rate is a property and the cell is not."*

From n=2 observations, "the rate **is** a property" is stronger than the
evidence. What two samples establish is that the rate is *similar* across two
samples and that cell identity is *not* stable. My third sample (0/8) is
consistent with p=1/64 (P=0.88) and adds no support either way. The exact
pooled interval is **[0.18 %, 5.21 %]** — wide enough that "1/64 is the rate" is
not established.

*Suggested remedy:* "the rate is **similar** across the two full runs (1/64 each,
pooled 95 % CI 0.18–5.21 %) and the cell is not."

### F3 — "as pre-registered" overstates the source for the band ordering (minor, attribution precision)

`comparison.md` §5 and `comparison.json`
`band_evaluation.primary.evaluation_order` both say the support-before-refute
order is used "as pre-registered". `findings.md` §6 states the three criteria as
an **unordered** table and specifies **no precedence**.

Consequences, both checked:

* **Immaterial to the headline.** Support and refute are disjoint (0 overlapping
  points in a 1001 × 12 sweep), and all four reported variants are
  order-independent. The verdict is safe.
* **Material to one modelled row.** Support and uninformative *do* overlap —
  189 points with `acc ∈ [0.92, 0.94]` and `c ≥ 3`. This affects only the
  `k = 3` row of the §6.2 margin sweep, where the report's order yields
  "supports a Jev niche" and the alternative yields "uninformative". That row is
  a modelled sensitivity, not an observation, and the difference does not touch
  `first_k_that_changes_the_verdict = 2`.

*Suggested remedy:* "as chosen; the order is immaterial to this verdict because
support and refute are mutually exclusive."

---

## 5. Observations (not faults)

**O1 — the primary band is applied to n=48 where the pre-registration says n=50.**
`findings.md` §6 states the criteria on "the 50 answerable cases". The report's
primary is the F1-corrected set (n=48). It discloses this, reports the raw
variant (acc 0.98, c 0 → REFUTES), and the verdict is invariant — and I verified
the `k = 2` margin holds in **both** views (§3.4). Not a fault; noted because
"applied verbatim" and "n=48" read together could mislead a reader who skips
§5's variant row.

**O2 — "reproduced on an independent sample" is the weakest phrase in the report.**
`§7` point 1 says S3 "is reproduced on an independent sample". The *sample* is
independent; the *mechanism* is identical to the frozen `general_model` run (same
model, route, prompt, temperature, decoding) — a replicate, not an independent
model. This is disclosed five times over, including
`comparison.json` `_read_before_quoting[3]`: *"spacebunny is a REPLICATE of the
frozen general_model mechanism under the same route, prompt and decoding, not an
independent model."* Acceptable given the disclosure density; flagged only
because the unqualified phrase is quotable out of context.

---

## 6. Unresolved uncertainties

These are **not** defects. They are limits of what the recorded evidence can
establish, stated so the numbers are not read as more than they are.

**U1 — weight identity behind the model id is unverifiable from the artefacts.**
The route is free-tier and unpinned. Nothing in the recorded evidence can prove
that `space-bunny-free` served the same weights on 2026-09-26 as it will
tomorrow. 60/62 label agreement between two runs ~2 h apart is consistent with
one model but does not prove it. The report notes "free-tier unpinned models"
(`README` item 6, `§7` point 3) but does not draw out this specific limit.

**U2 — determinism at `temperature 0` is empirically false here, and why is
untested.** Observed: 2 label flips between the two full runs, plus `c-p4b`
wrong in 2 of 3 samples. The endpoint is unpinned, so a *pinned* endpoint might
be deterministic; that was not tested and is not claimed. The report's framing
("expected … and is recorded, not smoothed") is appropriate.

**U3 — the width of "indistinguishable".** 0 discordant pairs in 48 gives a 95 %
CI on the per-pair discordance probability of **[0 %, 7.40 %]**. A true
discordance rate as high as ~7 % is compatible with the observation. The report
correctly claims **no** significance test and asserts only a *tie* — which is
exactly the claim a 0/48 observation supports and no more. The 100 % figures are
ceiling effects on a synthetic corpus where, once the one defective case is
removed, all three mechanisms are at 48/48; the report says so in §7 points 2
and 4.

**U4 — the transport-failure rate is loosely bounded.** Pooled 2/136 = 1.47 %,
95 % CI [0.18 %, 5.21 %]. Wide. The report's stronger phrasing here is F2.

**U5 — one unmodelled alternative remains open for the `k = 3` sweep row**, per
F3. No effect on the verdict or on the margin.

**U6 — what was NOT tested, explicitly.** No cross-family model was run (the
genuine Q1 test, operator-gated). No escalation or confidence-threshold analysis
— `spacebunny` is hard-decoded to confidence 1.0 by construction, so its
threshold behaviour is an encoding artefact (`findings.md` §4 L7) and was not
measured. No significance test. No re-run of the 56 cells I did not re-sample;
my 8-case re-run bounds reproducibility, it does not establish it. The
unanswerable cases were not re-sampled at all, so the 13/14 and 15/16
false-confidence figures rest on the single committed run.

---

## 7. Verdict

**PASS.**

All six tasked checks pass on the evidence. Every number in `comparison.md`,
`comparison.json`, `paired.ndjson` and `manifest.json` reproduces from the raw
files under an independently written recomputation that does not import the
follow-up scorer — **0 discrepancies** across the exhaustive diff, and **0**
field-level discrepancies across all 64 `paired.ndjson` rows. The frozen corpus
and frozen Jev results are provably untouched. The requests are provably
byte-identical to the frozen `general_model` requests, 64/64. The raw rows show
no sign of fabrication: 64 unique provider ids, zero overlap with the prior run,
and timestamps tracking the provider's own clock to within 4 seconds. A live
8-case re-run against the production endpoint reproduced 8/8 labels with an
unchanged error rate and zero transport failures, and it **strengthened** the
report's own most self-incriminating finding by showing `c-p4b` is wrong in 2 of
3 samples of the same mechanism.

The report does not overstate. It discloses the same-family confound five times,
argues its direction correctly, and explicitly refuses both the "this answers Q1"
and the "drop the Jev tier" readings. The band verdict is arithmetically correct
and, as a bonus the report does not claim, **order-independent**.

Three minor faults are recorded in §4 — one is a real gate defect worth fixing
(F1: `--check-only` prints a hardcoded `64/64` without performing the check; the
claim is true but the gate does not test it), two are inference/attribution
precision (F2, F3). **None changes a number, a denominator, a verdict, or the
margin claim.** I did not fix them, as instructed.

The single most important thing a reader should carry away is not the REFUTES
verdict — it is that the verdict rests on a **2-cell margin** on n=48, that one
of those cells has been observed flipping between samples of this very
mechanism, and that the comparison is against the **same family** that authored
the corpus, the prompt and the verifier. The report says all three of these
things itself, in its own headline, before any number is quoted. That is the
correct posture and this verification does not disturb it.

---

*Verification performed 2026-09-26 in session isolation from the builder. No
builder context, no builder artefacts consulted beyond the committed files under
test. Read-only except this file. No push. Scratch evidence in
`/tmp/opencode/jev-phase1-followup-verify/` (`indep.py`, `diff.py`,
`paired_check.py`, `bands.py`, `ci.py`, `rerun8.py`, `rerun8.json`,
`rescore/`).*
