# followup-02-mimo-v2.6-flash — independent verification

**Crosslink issue:** #565 · **Verifying:** `followup-02-mimo-v2.6-flash/` — the paid
cross-family baseline (`mimo-v2.6-flash`, mechanism `mimo_v26_flash`), the run
that answers `findings.md` §6 Q1.

**Verifier:** fresh session, no builder context. **Verifier model:**
`opencode-go/space-bunny-free` — **which is the corpus-author family**
(`findings.md` §4 L1). That is a declared conflict of interest for *this* report
and it is discussed in §8; it is also the same family that wrote the corpus, the
harness, the `general_model` comparator, and the analyst's `findings.md`. It is
**not** the same family as the subject of the run (MiMo, family `mimo`), and the
run's own subject-side numbers are all recomputed from raw bytes rather than
trusted. Read §8 before quoting any judgement below.

**What is verified:** the committed artefacts and the committed numbers. **What
is not:** whether `mimo-v2.6-flash` is *good* — that is what the run claims and
what the band verdict is about.

**Method.** Nothing from `followup-02-mimo-v2.6-flash/harness/score_mimo.py` was
imported. The recomputation script reimplements the frozen `score.py` cell
semantics from scratch and was **validated against the frozen
`results/scored.ndjson` before use** (§3.1). The request-drift gate was written
independently of `run_mimo.py`. The live re-run used its own curl transport, its
own frozen-shape gate, and the credential read from the CLI store; the token was
piped to curl on stdin and never written to disk, argv, or this report.

---

## 0. Verdict

| # | Check | Verdict |
|---|---|---|
| 1 | Frozen-input integrity; no frozen/followup-01 file touched; writes confined | **PASS** |
| 2 | New-baseline rows: 64, format, model/endpoint, **my own** request-drift gate, verbatim bodies, typed errors, no silent retries, usage present, no fabrication | **PASS** |
| 3a | Independent recomputation — accuracy, per-scope, paired, answered-unanswerable, sufficiency | **PASS** (every figure reproduced exactly) |
| 3b | Band verdict **for the observed state** | **PASS** (`REFUTES`, both arms) |
| 3c | Band **margin/sensitivity table** (`band_flip_margin`, `comparison.md` §7) | **FAIL** — two independent defects, §5 |
| 4 | Live re-run, 8 answerable cases + 3 disclosed extras | **PASS** — 8/8 labels identical; variance quantified; **the §4 risk reproduced** |
| 5 | cp4 correction applied to both mechanisms; denominators; answered-unanswerable kept separate | **PASS** |
| 6a | Case inputs unchanged; no request-shape drift; cross-family claim true | **PASS** |
| 6b | Derived USD cost vs catalog rates | **FAIL** — understated; `cached_tokens: 0 throughout` is false, §7 |
| 6c | `comparison.md` does not overstate | **QUALIFIED** — §4's "That did not happen" is falsified by re-run; §7's flip claim mis-states the landing state |

**No fault found in the headline result.** Raw accuracy 48/50 = 96.0%, F1-corrected
47/48 = 97.9%, paired `b`=0 / `c`=1, band verdict **REFUTES a Jev niche** — all
independently reproduced from raw bytes, and the refute verdict is correct under
the pre-registered rule as written. **Three faults found, all in derived
reporting, none in the measurement:** the band-margin table (§5), the cost
arithmetic (§7), and an over-strong robustness claim that my own re-run
contradicts (§8, F3).

---

## 1. Frozen-input integrity — PASS

Recomputed digests (`sha256sum`), not read from the manifest:

| file | my recomputed sha256 | expected prefix | verdict |
|---|---|---|---|
| `cases.ndjson` | `7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c` | `7dd4698f…` | **match** |
| `results/jev_raw.ndjson` | `e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc` | `e17ae014…` | **match** |
| `results/baselines_raw.ndjson` | `42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba` | (manifest) | **match** |

`git diff --stat 6fbd1a3d~1 HEAD` over `cases.ndjson`, `results/`, `tables/`,
`harness/`, and all of `followup-01-spacebunny/` returns **empty** — no frozen
Phase 1 artefact and no followup-01 artefact was modified by the followup-02
work. The complete set of files the followup-02 commits touched is 11 paths, all
under `followup-02-mimo-v2.6-flash/`.

Working tree at verification time: only `.crosslink/.last-hydrated-ref`
(modified) and `.crosslink/agents-hygiene.json` (untracked) — Crosslink
bookkeeping, not research artefacts.

The `__pycache__/*.pyc` files present on disk are **gitignored**
(`.gitignore:38`) and are not committed (`git ls-files … | grep -c pyc` → 0).
Not a fault.

**Manifest self-consistency:** all three `manifest.outputs_sha256` digests match
the committed files byte-for-byte, and all three `manifest.frozen_inputs.actual`
values match my independently recomputed digests.

---

## 2. New-baseline rows — PASS

`results/mimo_raw.ndjson`: 64 rows, 64 unique `case_id`, exact 1:1 with
`cases.ndjson` (no missing, no extra, no duplicates).

| property | observed | verdict |
|---|---|---|
| top-level key set vs frozen `general_model` row | 0 keys added, 0 removed | **identical format** |
| `model_id` | `mimo-v2.6-flash` 64/64 | as specified |
| `endpoint` | `https://opencode.ai/zen/go/v1/chat/completions` 64/64 | as specified |
| `mechanism` | `mimo_v26_flash` 64/64 | as specified |
| `http_status` | `200` 64/64 | |
| `typed_error` | `null` 64/64 | typed-failure field present and populated |
| `attempt` / `retries` | `1` / `0` on 64/64 | **no silent retries** |
| rows missing `usage.input_tokens` or `output_tokens` | 0 | **usage present** |
| `timestamp_utc` span | `05:41:08Z … 05:44:56Z` | matches manifest window |

### 2.1 Request-drift check — performed by me, 64/64 clean

I reimplemented the frozen serialisation from `harness/common.py:53-60`
(`json.dumps(..., ensure_ascii=False, separators=(",", ":"))`, insertion order
preserved) and, for every one of the 64 cases:

1. took the **committed** `request_body` from `mimo_raw.ndjson`;
2. set `model` back to `space-bunny-free`;
3. compared the serialised bytes and the sha256 against the **frozen**
   `general_model` row.

| test | result |
|---|---|
| serialised body **byte-equal** to frozen `general_model` request | **64 / 64** |
| `request_hash` **equal** to frozen `general_model` `request_hash` | **64 / 64** |
| `messages` array identical to frozen (prompt text + system prompt) | **64 / 64** |
| `max_tokens` = 256, `temperature` = 0, no other keys | 64/64 |
| committed row's own `request_hash` consistent with its stored mimo body | **64 / 64** |

**No prompt drift, no parameter drift, no added or dropped field.** The only
difference between the committed request and the frozen `general_model` request
is the `model` string. This independently confirms the manifest's
`frozen_condition_check` claim rather than taking it on trust.

The endpoint differs from the frozen run's (`…/zen/go/…` vs `…/zen/…`). That is
disclosed in `comparison.md` §8 and `manifest.model.route_note` as forced by the
model (the Zen route returns `400 Model is unavailable` for
`mimo-v2.6-flash`); `results/route_diagnostics.json` carries the probe matrix
showing the Zen-route rejection. Acceptable, and disclosed. Note for a
re-replicator: the comparison is therefore **not same-route**, which is a real
(if second-order) difference in the experimental condition.

### 2.2 Raw bodies verbatim, parseable, and consistent with the parsed fields

| test | result |
|---|---|
| `raw_response` is a `str` and `json.loads`-able | **64 / 64** |
| response `model` field echoes `mimo-v2.6-flash` | 64/64 |
| `choices` and `usage` present in every body | 64/64 |
| `parsed.raw_content` == the wire `message.content` | **64/64** |
| row `usage.input/output_tokens` == wire `prompt/completion_tokens` | **64/64** |
| wire `total_tokens == prompt + completion` | 64/64 |

### 2.3 No fabricated rows

| test | result | why it discriminates |
|---|---|---|
| uniqueness of the provider `response.id` | **64 unique / 64** | copy-paste would collide |
| `abs(response.created)` vs `timestamp_utc` | **max 1 s** (all ≤ 60 s) | a hand-written row cannot carry a coherent provider clock |
| `latency_ms` plausibility | 3–5 s range, all > 0 | matches a reasoning model, not a template |
| committed run window vs manifest `raw_run_window_utc` | identical to the second | |

No fabrication signal. **Certainty: evidence-based, not proven** — a sufficiently
well-informed forger could satisfy all four; I did not attempt to disprove
authorship cryptographically, and no provider-side request log was available to
tie the 64 `response.id`s to this session. The `x-opencode-session` value
`d365cc37-…` is recorded in `manifest.json` and `run_session.json`, so that tie
is *possible* for someone with provider access.

---

## 3. Independent recomputation — PASS (figures), FAIL (band margin, §5)

### 3.1 My scorer was validated before use

I did not import `score_mimo.py`. I reimplemented `build_cell` from the frozen
`score.py:206-245` semantics (`usable` = `prediction.label is not None`;
`answerable` = `gt.answerable and gt.answer is not None`; `correct` =
`label == gt.answer` only when both hold) and checked it against the **frozen**
`results/scored.ndjson` over `jev` and `general_model`: **1152 field comparisons,
0 mismatches** across `usable`, `answerable`, `correct`, `pred_label`,
`gt_answer`, `unanswerable_but_answered`, `question_type`, `area`, `split`.
(An earlier run of this check reported 227 mismatches; that was a bug in my
validation harness — I compared `ref[minekey]` instead of `ref[frozenkey]` — not
a data discrepancy. Corrected, and the corrected figure is the one above.
Coincidence worth flagging so it is not misread: the comparison count 1152 is
unrelated to the 1152 *input tokens* in §4 — different quantities, same digits.)

### 3.2 Accuracy — every figure reproduced

| mechanism | raw correct/usable | raw acc | corrected correct/usable | corrected acc |
|---|---|---|---|---|
| `mimo_v26_flash` | 48/50 | **96.0 %** | 47/48 | **97.9 %** |
| `jev` (frozen) | 49/50 | 98.0 % | 48/48 | 100.0 % |
| `general_model` (frozen) | 50/50 | 100.0 % | 48/48 | 100.0 % |
| `space_bunny` (followup-01) | 49/50 | 98.0 % | 48/48 | 100.0 % |

Matches `comparison.md` §1 and §2 exactly. Denominators are *usable answerable*
cells; transport failures are excluded from the semantic denominator and
reported separately, as the brief requires (there were none).

### 3.3 Per-scope — all 11 rows reproduced exactly

`area` × {A, B, C, D}, `split` × {train, dev, test}, `qtype` × {noul, choice,
score}, each under both views — every `n answerable`, `correct`, `acc` and
`answered unanswerable` cell matches `comparison.md` §2, including `area B`
`acc = n/a` because area B has **0 answerable cases** (13 unanswerable). Both of
MiMo's raw errors are in area C, as stated.

### 3.4 Answered-unanswerable

`mimo_v26_flash` answered **14/14** unanswerable raw and **16/16** corrected;
false-confidence rate **1.00**. `abstained` is `False` on all 64 rows, so
"answered-unanswerable" and "did not abstain" coincide. Matches §2 and §10.5.

### 3.5 Paired vs frozen Jev — reproduced

| view | n paired | `b` | `c` | both right | both wrong | excluded unanswerable | excluded unusable |
|---|---|---|---|---|---|---|---|
| raw GT | 50 | **0** | **1** | 48 | 1 | 14 | 0 |
| F1-corrected | 48 | **0** | **1** | 47 | 0 | 16 | 0 |

The single `c` cell is **`c-p6a`** (area C, split test, `noul`, gt `yes`; Jev
`yes`, MiMo `no`) — as named in §3. There is **no** `b` cell: MiMo is never
right where Jev is wrong. Delta −2.0 pp raw, −2.1 pp corrected. Matches §3.

### 3.6 Sufficiency flag — reproduced

Rule: fewer than 40 usable cells of the answerable set. Observed 50/50 raw,
48/48 corrected, 0 transport failures in either. **Not triggered.** Matches §5.

### 3.7 Band verdict for the observed state — PASS

Bands transcribed from `findings.md` §6 (I read the pre-registration, not the
report's transcription of it): support `acc ≤ 0.90 OR c ≥ 3`; refute
`acc ≥ 0.96 AND c ≤ 1`; uninformative `0.92 ≤ acc ≤ 0.94`; otherwise outside.
Order: support before refute.

* F1-corrected (primary): `acc = 47/48 = 0.9792 ≥ 0.96` **and** `c = 1 ≤ 1` →
  **REFUTES a Jev niche**. Both arms fire. ✓
* Raw variant: `acc = 48/50 = 0.9600 ≥ 0.96` and `c = 1 ≤ 1` → REFUTES. ✓
  (0.96 sits *exactly* on the floor — the report says so.)

**The headline verdict is correct under the pre-registered rule as written.** It
does not depend on the transport-failure sensitivity, which is degenerate here
(0 failures, so all three variants are 47/48).

---

## 4. Live re-run — PASS, variance quantified, and §4's risk reproduced

8 answerable cases, re-sent on `mimo-v2.6-flash` with the frozen request shape.
Selection (deterministic, disclosed): MiMo's two raw error cells `c-p6a` and
`c-p4b`, plus a spread over all four areas and all three question types —
`a-e01` (A/noul), `a-h04` (A/score), `c-p3b` (C/noul), `d-04` (D/choice),
`d-l01` (D/choice + `label_map` control), `d-r01` (D/choice).

My own frozen-shape gate ran **before** any call: for all 8, normalising
`model → space-bunny-free` reproduced the frozen `general_model` hash **and**
bytes. Transport: curl, frozen `User-Agent: curl/8.5.0`, `x-opencode-session`
header, credential from `auth.json#opencode-go` piped to curl on stdin.

**Proof the request bytes were identical:** the 8 re-run calls reported
**1152 input tokens**, exactly the sum of the committed rows' input tokens for
the same 8 cases.

### 4.1 Label agreement — 8/8, zero flips

| case | re-run content | committed `parsed.raw_content` | identical |
|---|---|---|---|
| `c-p6a` | `NO` | `NO` | ✓ |
| `c-p4b` | `YES` | `YES` | ✓ |
| `a-e01` | `YES` | `YES` | ✓ |
| `a-h04` | `low` | `low` | ✓ |
| `c-p3b` | `NO` | `NO` | ✓ |
| `d-04` | `repair` | `repair` | ✓ |
| `d-l01` | `opt_w1e6` | `opt_w1e6` | ✓ |
| `d-r01` | `investigate` | `investigate` | ✓ |

`d-l01` returns the opaque option token; both runs map it through
`control.label_map` to `repair`, which is the ground truth. So the pair agrees
at the label level too. Raw accuracy on these 8 cells is 6/8 in **both** runs
(`c-p6a`, `c-p4b` wrong in both).

### 4.2 Variance — expected API nondeterminism, quantified not faulted

Reasoning-token count is **not** reproducible at `temperature = 0` on identical
request bytes: **0 of 8 cells identical**, deltas **−4 to +11 tokens**
(mean +2.1). This is the phenomenon `findings.md` §4 L3 records and
`comparison.md` §4 relies on; my measurement confirms it independently.

Three **additional, disclosed** probes on area-B *unanswerable* cells (outside
the 8, run because they carry the highest reasoning-token counts and directly
test §4's central caveat):

| case | committed reasoning | re-run reasoning | re-run `finish_reason` | re-run content |
|---|---|---|---|---|
| `b-a03` | **245** (margin 11/256) | 187 | `stop` | `YES` |
| `b-i03` | 46 | 97 | `stop` | `NO` |
| `b-a05` | 235 | **257 (capped)** | **`length`** | **`null`** |

**`b-a05` reproduced the exact failure mode `comparison.md` §4 states did not
happen**: `finish_reason: length`, `content: null`, output capped at the frozen
`max_tokens = 256`. That is the same signature the frozen `general_model` run
recorded as `typed_error: empty_content` on `b-i03` (`http 200`, `parsed:
null`). See §8 F3 for what this does and does not change.

Across all 11 re-run cells: reasoning delta **−58 to +51**, **0/11 identical**;
1 transport failure in 11 calls.

### 4.3 Extra usage and derived cost

| | input | output | of which reasoning | cache read | derived USD |
|---|---|---|---|---|---|
| 8 answerable re-run calls | 1152 | 495 | 466 | 0 | $0.00029988 |
| 3 extra area-B probes | 289 | 546 | 541 | 0 | $0.00019334 |
| **total, 11 calls** | **1441** | **1041** | **1007** | **0** | **$0.00049322** |

At the catalog rates, that is **26.6 % of one 64-cell grid run**
($0.00185578 corrected / $0.00185542 as claimed). Verification cost is
non-trivial relative to the experiment; that is the honest number.

---

## 5. FAULT 1 + FAULT 2 — the band-margin table (material to a stated conclusion)

`comparison.md` §7, `comparison.json:band_flip_margin`, and `README.md` lines 30
and 231 all assert: *"At `k = 2` extra answerable errors the band flips to
'supports a Jev niche'"* and *"One further answerable error would reverse this
result."* Two independent defects make that wrong.

### FAULT 1 — the `k` index is off by one between the accuracy and `c` columns

`band_flip_margin` defines `k` as **"k additional answerable errors"** and models
`c = 1 + k` — correct, since the observed state is 1 error with `c = 1`. But the
accuracy is computed as `(48 − k) / 48`, i.e. as if `k` were the **total** error
count. Proof from the artefact's own numbers: `k = 0 → acc 1.0` (zero errors),
whereas the run's corrected accuracy is 0.9792 (one error). The two columns
cannot both be right.

Self-consistent series under the block's own definition (n = 48, `acc =
(47 − k)/48`, `c = 1 + k`), against what the artefact reports:

| `k` (extra errors) | **correct** acc / `c` / verdict | **committed** acc / `c` / verdict |
|---|---|---|
| **0 — this IS the observed run** | 0.9792 / 1 / **REFUTES** | 1.0000 / 1 / REFUTES |
| 1 | 0.9583 / 2 / **OUTSIDE the bands** | 0.9792 / 2 / REFUTES |
| 2 | 0.9375 / 3 / supports | 0.9583 / 3 / supports |
| 3 | 0.9167 / 4 / supports | 0.9375 / 4 / supports |
| 4 | 0.8958 / 5 / supports | 0.9167 / 5 / supports |
| 5 | 0.8750 / 6 / supports | 0.8958 / 6 / supports |
| 6 | 0.8542 / 7 / supports | 0.8750 / 7 / supports |

Consequences:

* `band_flip_margin.observed_k: 1` is **wrong** under the block's own definition —
  the observed state is `k = 0`.
* The row labelled **"1 (observed)"** in `comparison.md` §7 is not the observed
  state: its accuracy 0.9792 *is* the observed accuracy, but its `c = 2`
  contradicts the `c = 1` stated for the same accuracy in §1, §6 and the
  `band_evaluation.primary` block.
* The table **omits the two-error state entirely** — the one state that is
  actually one cell away from the observed run, and the only state where the
  bands are silent.

### FAULT 2 — `evaluate_bands` implements the refute arm as OR, and declares it as AND

`score_mimo.py:554-561` builds the refute verdict if **either** arm is
non-empty (`if ref:`), while the same function's `bands_verbatim` block
(line 580) and `findings.md` §6 both state the rule as
**`acc >= 0.96 AND c <= 1`**.

This is visible as a self-contradiction inside the committed JSON: the `k = 1`
row reports `verdict: "REFUTES a Jev niche"` with
`conditions_fired: ["acc 0.9792 >= 0.96 (refute arm 1)"]` — **one** arm listed,
and `c_used: 2`, which fails `c ≤ 1`. Under the declared AND rule that row is
`OUTSIDE the defined bands`.

**Impact on the primary verdict: none.** The observed state is `acc 0.9792`
**and** `c = 1`, so both arms fire and OR/AND agree. The headline
**REFUTES a Jev niche** is correct either way. The defect is confined to the
sensitivity table and to the prose built on it.

### Why the mis-stated conclusion matters

At two total errors the corrected point is `acc = 46/48 = 0.9583` with `c = 2`.
That fires **no** pre-registered arm: not support (`0.9583 > 0.90`, `2 < 3`), not
refute (`0.9583 < 0.96`), not uninformative (`0.9583 ∉ [0.92, 0.94]`). It is a
**gap between the pre-registered bands**, which exist because they were written
for n = 50 (where 2 errors *is* 0.96) and the F1 correction moved the
denominator to 48 without re-deriving them. So:

* §1's *"a second error on a cell Jev also got right flips the band verdict to
  'supports a Jev niche'"* — **false**. Two errors put it **outside** the bands.
* §7's *"The verdict flips at `k = 2`"* — the flip to *support* does occur at
  `k = 2`, so this one happens to land on the right number, but only because the
  table's accuracy column is shifted; and the state immediately before it
  (`k = 1`) is mis-reported as `REFUTES` when it is `OUTSIDE`.
* §7's *"One further answerable error would reverse this result"* — directionally
  right (refute no longer holds at 2 errors) but the landing state is
  "outside the defined bands", not "supports a Jev niche".

**This does not rescue the Jev niche.** Outside-the-bands is not support, and the
report's own pre-registered instruction for an outside verdict is "no new
threshold is invented". The honest statement of the width is: *the refute verdict
survives exactly one additional answerable error; at two errors the
pre-registered bands are silent; support first fires at three.* The report
currently overstates both the fragility (by one cell) and the landing state.

---

## 6. Correction check — PASS

* **Correction set:** `c-p4a` + `c-p4b` (`pair_id: cp4`), sourced from
  `verification.md` §2 F1. Confirmed against `cases.ndjson`: both have
  `ground_truth.answerable = true` as committed.
* **Applied to BOTH mechanisms** — and, correctly, to all four for context
  (`jev`, `general_model`, `space_bunny`, `mimo_v26_flash`).
* **Corrected denominators:** 50 answerable / 14 unanswerable →
  **48 / 16**, identical for every mechanism. Matches §2.
* **Answered-unanswerable reported separately from semantic errors — confirmed.**
  It occupies its own column in every §2 table, is excluded from `acc`, and is
  never folded into the error count. This is the right separation and the frozen
  `score.py` comment at line 231 says why.
* **Effect of the correction, recomputed independently:** MiMo's semantic errors
  go 2 → 1 (raw errors `c-p4b`, `c-p6a`; only `c-p6a` survives as an error
  because `c-p4b` leaves the answerable set). Jev's go 1 → 0. `c-p4b` is the
  only cell both mechanisms get wrong raw, and it is the only cell the correction
  removes — exactly as §2 states. The correction therefore **helps MiMo's
  reported accuracy and helps Jev's equally** (100 % vs 98 %); it is a change of
  yardstick, not of anyone's score, and the report says so.

---

## 7. FAULT 3 — cost arithmetic and a false evidence claim

`comparison.md` §9 and `comparison.json:usage_and_cost` state
`cache_read_tokens: 0` and *"Cache read and cache write are 0 on every call
(`cached_tokens: 0` throughout), so those two rate lines contribute nothing."*

**That is false.** Summing `usage.raw.prompt_tokens_details.cached_tokens`
across the 64 committed rows gives **128**: `c-p3b` = 64, `d-r01` = 64, all
others 0.

| | input | output | cache read | derived USD |
|---|---|---|---|---|
| grid, as claimed | 7857 | 2698 | 0 | $0.00185542 |
| grid, corrected | 7857 | 2698 | **128** | **$0.00185578** |
| total, as claimed | 7934 | 2712 | 0 | $0.00187012 |
| total, corrected | 7934 | 2712 | **128** | **$0.00187048** |

Understatement **$0.00000036** on the grid, **0.019 %** of the total. Immaterial
to every conclusion — but it is a stated, falsifiable, checkable evidence claim
that is wrong, and the derived cost is a headline figure in §1 and `README.md`.

**Root cause (a field-path bug, not a judgement call).** `score_mimo.py:245-259`
`pick("cache_read_input_tokens", "cache_read_tokens", "cached_tokens")` searches
only the **top level** of the usage dict. The wire nests it one level down, in
`prompt_tokens_details`. The same function *does* descend into
`completion_tokens_details` for reasoning tokens (lines 262-268) — which is why
the reasoning accounting is right and the cache accounting is structurally
always 0 for this API shape. It would read 0 for every future run too.

Everything else in the cost account verifies against the **live catalog**
(`opencode-go` provider, `mimo-v2.6-flash`): `input 0.14`, `output 0.28`,
`cache_read 0.0028`, `family: mimo`, `limit.context 1048576` — the last matching
`manifest.model.context`. No `cache_write` key exists in the catalog; pricing it
0.0 is right. Token totals 7857 / 2698 / 2492 reasoning / 92.4 % reasoning share
/ 206 content tokens / per-cell content min-med-max 3-3-7 / max reasoning 245 on
`b-a03` are **all confirmed** from the raw usage. The preflight line
(77 + 14 tokens, $0.00001470) and the total arithmetic are internally consistent.
The attribution decision — pricing the free `general_model` comparator at 0/0/0/0
rather than at MiMo's rates — is correct and worth keeping.

---

## 8. Adversarial checks

| # | Check | Result |
|---|---|---|
| A1 | Case inputs unchanged | **PASS** — `cases.ndjson` digest matches; the re-run's 1152 input tokens equal the committed sum, so the bytes sent are the frozen bytes |
| A2 | No request-shape drift | **PASS** — 64/64 byte- and hash-equal (§2.1) |
| A3 | Cross-family claim is true | **PASS** — see below |
| A4 | Derived USD maths vs catalog | **FAIL** — §7 |
| A5 | `comparison.md` does not overstate | **QUALIFIED** — F3 below |
| A6 | Band verdict matches the pre-specified logic | **PASS** for the observed state; **FAIL** for the margin table (§5) |
| A7 | Secrets hygiene | **PASS** — I scanned every file in the directory for the live credential value: **0 hits**; only the source label `auth.json#opencode-go` is recorded. Confirms §8's claim independently. |
| A8 | Manifest self-consistency | **PASS** — all `outputs_sha256` and all `frozen_inputs.actual` verified |

**A3 — cross-family, confirmed from provenance, not asserted.** The live catalog
gives `mimo-v2.6-flash` **`family: mimo`**. `findings.md` §4 L1's seat table
records the case author (all 64 cases, all ground truth), the harness author,
the `general_model` baseline, and the D1/D2/D3 agents as
`opencode-go/space-bunny-free`, with **`jev-1.13-free` as the only other
family**. `cases.ndjson` provenance is `generator: harness/gen_cases.py`,
`synthetic: true` on all 64. So the run is a **third** family, distinct from both
the corpus author and Jev, and the confound that disqualified followup-01 does
not apply. The claim is true.

### F3 — the overstatement, and what my re-run settles

`comparison.md` §4 opens: *"The brief flagged a specific expected risk … some
cells may end `finish_reason: length` with empty content, and those count as
transport failures. **That did not happen.** No cell was empty, truncated, or
retried."* §1 tabulates **"transport failures 0 / 64"** and the **"free rider
(N6 replacement) 0/64 typed errors"**.

Read strictly as statements about the committed run, both are true — I verified
0/64, and the run really did return content on every cell. Read as a property of
the model at these conditions, **my re-run falsifies it**: `b-a05` came back
`finish_reason: length`, `content: null`, output capped at 256, i.e. **1
transport failure in 11 same-conditions calls**, with reasoning-token counts
varying by −58 to +51 across identical bytes.

The document is **not** unaware of this — §4's next paragraph and §10.6 and
`README.md` §5 both say the margin is *"a live replication risk … not a resolved
property."* So the fault is an **internal tension, not a concealment**: §4's
flat *"That did not happen"* and §1's `0/64` sit against §10.6's correct hedge,
and the flat reading is the one a skimming reader takes away. My re-run resolves
the tension in favour of §10.6.

**What the reproduced failure does and does not change — important, because it is
easy to over-correct here.** `b-a05` is an **unanswerable** area-B cell. A
failure there:

* does **not** touch any accuracy denominator (50 answerable raw / 48 corrected
  are unchanged);
* does **not** trip the sufficiency flag, which counts usable **answerable**
  cells;
* **does** move answered-unanswerable from 16/16 to 15/16 and false-confidence
  from 1.00 to 0.9375;
* therefore leaves the **band verdict (REFUTES, acc 0.9792, c 1) unchanged**.

The failure mode is real and the §4 caveat is vindicated; its consequence for the
headline verdict is nil, because area B is entirely unanswerable and therefore
invisible to the accuracy denominator. Anyone re-running should read the
sufficiency flag first, as `README.md` §5 advises — and should also expect
`answered-unanswerable` to be the metric that moves.

**One thing in §7 that I checked and found *correct*, recorded so it is not
re-litigated:** *"the raw-GT accuracy of 96.0 % sits exactly on the
pre-registered refute floor, one error from the declared-inconclusive band."*
On the raw view (n = 50) one further error gives 47/50 = **94.0 %**, which is
inside `[0.92, 0.94]`, so both halves hold. §7's error is confined to the
**corrected** view, and is covered in §5.

---

## 9. Unresolved uncertainties

1. **The refute verdict is one cell wide, and that is a property of n = 50, not
   of the model.** My §5 correction makes the width *slightly larger* than
   reported: the verdict survives exactly one additional answerable error, then
   the bands go silent, then support fires at three. The pre-registered bands
   were derived for n = 50 and the F1 correction silently moved the denominator
   to 48. **Whether the bands should have been re-derived at n = 48 is a
   methodology question I am not authorised to settle** — the pre-registration is
   a frozen artefact and re-deriving it post hoc would be exactly the
   threshold-moving the report correctly refuses elsewhere. Flagged, not fixed.
2. **The inconclusive band is unreachable at n = 48 in its stated form.** Its
   gloss is "3–4 errors (92–94%)", but at n = 48 four errors is 91.67 %, outside
   `[0.92, 0.94]`. So at 3 errors a point can be *both* "supports" (`c ≥ 3`) and
   "inconclusive". The implementation resolves this support-first, which is
   consistent with "support before refute" but not clearly with the
   pre-registration's own framing of the inconclusive band as the place to
   "declare it, do not pick a side". **I did not resolve this**; it does not
   affect the observed state, which is not near the boundary.
3. **N = 1 everywhere.** One run, one attempt per cell, zero retries, against an
   unpinned paid endpoint. My 11 calls give 8/8 label stability on a *selected*
   8 (deliberately including both error cells, which is not a random sample) and
   1/11 transport failures. This is evidence about stability, not a replication:
   11 cells cannot bound a 64-cell rate, and my sample was chosen for
   informativeness, not representativeness.
4. **Reasoning-length nondeterminism is measured, not explained.** −58 to +51
   tokens on identical bytes at `temperature = 0` is consistent with provider
   batching/scheduling nondeterminism. I did not investigate the mechanism, and I
   cannot say what fraction of cells sit close enough to 256 to fail. The
   committed grid's worst cell (`b-a03`, 245/256) re-ran at 187 — it did *not*
   fail, so the specific worst case in the report is not the one that breaks.
   `b-a05` is.
5. **Route confound.** The run used the Go route, not the frozen Zen route. Any
   difference in serving stack, prompt caching, or system behaviour between the
   two routes is uncontrolled. Disclosed in §8 of the report; not resolvable from
   here.
6. **Author independence.** See the header and §10. I share a model family with
   the corpus author, the harness author, the `general_model` comparator and the
   `findings.md` analyst. Everything in §1–§7 is a recomputation from raw bytes
   with numbers quoted verbatim, so a shared prior cannot change the arithmetic;
   but the *interpretive* judgements (which I have tried to keep few and label as
   such) carry the same family bias the run was designed to escape. I have not
   verified whether the independent verification of Phase 1 itself
   (`verification.md`, commit `b78bfca7`) was done by a different family — I
   could not determine the verifier's model from the artefacts.
7. **I did not re-derive `findings.md` §4 L3, §6, or the F1 finding.** I took
   the band thresholds, the `cp4` correction set and the corpus-authorship table
   as given inputs and verified the arithmetic built on them. If the F1 finding
   itself were wrong, §3's corrected numbers would move — though the raw numbers
   in §3.2 would not.

---

## 10. Statement of my own limits

* I did not import `score_mimo.py` or `run_mimo.py`. I read `score_mimo.py` after
  computing my own numbers, to characterise defects 1 and 2 — the recomputation
  in §3 was complete and self-consistent before I opened it, and §3.1's
  validation against the *frozen* scorer (0/1152 mismatches) is the guard
  against my semantics drifting from the corpus's.
* I did not verify that `b-a03` was genuinely the committed run's most
  reasoning-intensive cell by re-running the full grid; I took that from the
  committed usage and confirmed `b-a03` = 245 in the raw rows.
* I made 11 live API calls costing $0.00049322. They are recorded in
  `/tmp/opencode/jev-phase1-followup2-verify/` (scratch, outside the repo).
  No credential value is in any of them.
* I fixed no fault. This file is the only repository file I wrote, and I did not
  review the substance of my own findings as findings — that is the reviewer's
  and the operator's call.

---

## 11. Verdict

**PASS with three reported faults.**

The measurement is sound. Every headline number in `comparison.md` §1–§3, §5 and
§6 — 96.0 % raw, 97.9 % corrected, the full per-scope table, answered-unanswerable
14/14 and 16/16, paired `b`=0 / `c`=1 on `c-p6a`, zero transport failures, the
sufficiency flag not triggered, and the band verdict **REFUTES a Jev niche** — is
independently reproduced from the raw bytes, and the request-drift gate is clean
at 64/64 by my own check rather than by the runner's assertion. The
cross-family claim is true and the correction is applied evenhandedly.

Three faults, none of which touches the headline verdict:

1. **§5 FAULT 1** — `band_flip_margin`'s accuracy column is shifted one row
   against its own `c` column; `observed_k` is wrong; the two-error state is
   omitted; the table is not self-consistent.
2. **§5 FAULT 2** — `evaluate_bands` implements the refute arm as OR while
   declaring it as AND; visible as a one-armed `REFUTES` verdict inside the
   committed JSON.
3. **§7 FAULT 3** — `cached_tokens: 0 throughout` is false (128 tokens);
   derived cost understated by $0.00000036; caused by a field-path bug that will
   recur on every future run.

Plus one qualitative qualification (**§8 F3**): §4's flat *"That did not
happen"* is falsified by my re-run — `b-a05` returned `content: null` at
`finish_reason: length` — though §10.6 and `README.md` §5 already hedge it
correctly, and the failure lands on an unanswerable cell, so the band verdict is
unmoved.

**On the result itself:** the evidence supports the narrow claim and does not
support a broad one. A cross-family cheap general model matched a Jev tier on this
synthetic corpus, disagreeing on one cell and never ahead. That is a real answer to
Q1, and it is correctly reported as one cell wide. It is **not** evidence about
abstention (16/16 answered-unanswerable, false-confidence 1.00 — unchanged from
every other mechanism in Phase 1), and it is **not** evidence about
non-synthetic text, which is what the decision in `findings.md` §6 would actually
turn on. The report says both of these things itself; this verification confirms
it is entitled to.

---

*Verified 2026-09-26 in `/home/claude-code/projects/ASES/.worktrees/jev-phase1`,
branch `research/jev-phase1-565`, base commit `c79bd621`. Read-only except this
file. No pushes. Verifier model `opencode-go/space-bunny-free` — same family as
the corpus author; see the header and §9.6.*
