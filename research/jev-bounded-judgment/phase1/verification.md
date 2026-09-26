# verification.md — Independent Verification, Jev Phase 1 (issue #565)

**Role:** D2 verifier, fresh session, no builder context. Read-only everywhere
except this file. Scratch evidence: `/tmp/opencode/jev-phase1-verify/`.
**Model:** `opencode-go/space-bunny-free` — the *same family* as the D1 case
author, the D1 harness author and the `general_model` baseline. See **§7
self-preference**; this is an operator-scoped constraint, not a choice, and it
is a real confound on one of the two headline findings.
**Worktree:** `/home/claude-code/projects/ASES/.worktrees/jev-phase1`,
branch `research/jev-phase1-565`, HEAD `19eccb0f`. No pushes. No artefact
other than this file was modified.

**Verdict: PASS WITH FINDINGS.** Every number in `results/metrics.json` and
all twelve tables reproduced exactly from the raw files by an independent
reimplementation (**2,315 field comparisons, 0 substantive disagreements**), the
deterministic baselines re-run byte-identically, the corpus and the adversarial
controls are real, 17 live Jev calls reproduce with 0 label flips, and there is
no sign of fabricated data or of ground truth reaching any mechanism. Four
defects and four minor/documentation defects are recorded below. Two of them
(F1, F2) change how a stated result must be read, though neither overturns the
run's conclusions.

---

## 0. Verdict table

| # | Check | Verdict | Evidence |
|---|---|---|---|
| **1** | **Artifact / manifest integrity** | **PASS with 2 minor defects** | §1 |
| 1.1 | every declared file exists | PASS | 15/15 `manifest.outputs` present; 12 tables + `INDEX.md` |
| 1.2 | sha256 of cases + raw results match manifest | PASS | 3/3 exact |
| 1.3 | model IDs / endpoints / timestamps correct | PASS | 64/64 `jev-1.13-free` @ `/zen/v1/systemone`; 64/64 `space-bunny-free` @ `/zen/v1/chat/completions`; window 02:46:53Z→02:50:44Z monotone |
| 1.4 | no secrets / personal data | **PASS (F6)** | 32 files scanned, 0 credential hits; F6: scan omits `preflight_evidence.json`, the one file recording key *length* |
| **2** | **Cases** | **PASS with 1 material defect** | §2 |
| 2.1 | count within declared bounds | PASS | 64 ∈ [55,65]; validator `C1` |
| 2.2 | schema conformance | PASS | 0 violations on 64 cases, independent of `validate_cases.py` |
| 2.3 | ground truth justified | **FAIL for 1 of 6 contrastive pairs (F1)** | cp4 GT not derivable from the state text |
| 2.4 | required control coverage | PASS | all 7 `variant_kind` present |
| 2.5 | pairs differ ONLY in the deciding fact | **PASS 5/6, minor deviation on cp1 (F7)** | word-level diff of all 6 |
| 2.6 | each family in one split | PASS | 46 families, 0 span >1 split |
| **3** | **Baselines** | **PASS** | §3 |
| 3.1 | no ground-truth leakage | PASS | instrumented access probe: 0 leaks; fit is TRAIN-only |
| 3.2 | deterministic mechanisms re-run from clean clone | PASS | 192/192 rows, 0 field diffs except `timestamp_utc` |
| **4** | **Jev raw evidence** | **PASS** | §4 |
| 4.1 | ≥10 cases re-run live | PASS | 17 cases, 71 further calls |
| 4.2 | prediction / distribution / usage match | PASS | 0 label flips, 17/17 prob maps + usage identical |
| 4.3 | verbatim raw body on every call | PASS | 64/64 non-empty, parse as JSON, hash matches sent bytes |
| 4.4 | typed error on every failure | PASS | 1/1 typed (`empty_content`) |
| 4.5 | no fabricated rows | PASS | 0 discrepancies found |
| **5** | **Independent recomputation** | **PASS** | §5 — 2,315 comparisons, 0 disagreements |
| **6** | **Adversarial falsification** | **PASS with F2 + confound** | §6, §7 |
| 6.1 | try to break the strongest positive claim | claim survived | inversion probe; 0 flips |
| 6.2 | `option_reorder` really reordered | PASS | wire-level key order differs |
| 6.3 | opaque labels map back | PASS | bijection, label text identical, state byte-identical |
| 6.4 | `missing_evidence` truly removes the deciding fact | PASS | 0/2 retain it; **F2: the flag cited as proof is a tautology** |
| 6.5 | general-model baseline and case author share one family | **CONFIRMED — flag** | §7 |
| **7** | **Reproducibility (RUNBOOK from clean clone)** | **FAIL on 2 of 12 checklist items (F4)** | §8 |

Defects: **F1** material (ground truth) · **F2** material (tautological
evidence) · **F3** moderate (reliability understated) · **F4** minor/doc
(stale RUNBOOK hashes + a non-existent flag) · **F5** minor/doc · **F6**
minor/scope · **F7** minor · **F8** confound, unresolvable here.

---

## 1. Artifact and manifest integrity

Every hash the manifest declares, recomputed from the committed files:

```
$ cd .../research/jev-bounded-judgment/phase1
$ sha256sum cases.ndjson results/jev_raw.ndjson results/baselines_raw.ndjson
7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c  cases.ndjson
e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc  results/jev_raw.ndjson
42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba  results/baselines_raw.ndjson
```

All three equal `manifest.inputs`. All 12 `tables/*.md` + `INDEX.md` hashes
equal `manifest.outputs_sha256` (13/13). Grid is complete: 64 cases ×
5 mechanisms = 320 unique cells, 0 duplicate, 0 missing, 0 unknown-case.

Provenance is coherent and self-consistent:

* `jev` 64/64 `model_id=jev-1.13-free`, `endpoint=https://opencode.ai/zen/v1/systemone`, `http_status=200`, `attempt=1`, `retries=0`, `secrets_recorded=false`, `raw_response` non-empty on 64/64 and JSON-parseable on 64/64.
* `general_model` 64/64 `model_id=space-bunny-free`, `endpoint=…/zen/v1/chat/completions`, `max_tokens=256`, `temperature=0`. The disclosed route change (Go → Zen) is recorded per-row *and* in the manifest; it is a route change, not a model substitution. Correctly disclosed.
* Timestamps: jev 02:46:53Z→02:47:30Z, general_model 02:49:19Z→02:50:44Z; both inside the manifest's declared window and monotone with row order.
* The preserved pre-fix file's internal `_meta.sha256` (`d70a9e79…`) is the hash of its first 256 data lines, i.e. the file *before* the `_meta` line was appended. Verified — internally consistent, though the manifest does not say so.
* `request_hash` on all 64 jev rows equals `sha256` of the exact serialised body that was sent (0 mismatches).

**Secret / personal-data scan** — 32 files across the whole `phase1/` tree
(harness, tables, results, docs), 11 credential-shaped patterns:

```
TOTAL pattern hits: 484   -- all benign
  longhex_32: 484  -> git SHAs and sha256 request/output hashes
  email:       1  -> "git@github.com" in manifest.git.remote
  sk-/AKIA/gh_pat_/PEM/JWT/bearer-literal/assignment: 0
```

`secrets_recorded` is `false` on all 320 raw rows and 320 scored rows; the
`OPENCODE_GO_API_KEY` *name* appears in code and docs, its value nowhere.
`cases.ndjson` contains no name-like proper noun outside an allow-list, no
email, no IP, no credential shape. Provenance flags are `synthetic: true`,
`contains_personal_content: false`, `contains_secrets: false` on all 64.

> **F6 (minor, scope).** `manifest.secrets.scan` reports
> `files_scanned: 14` — the 14 files `score.py` emits. It never scans
> `results/preflight_evidence.json`, which is the **only** file that records
> anything about the key itself: `"length": 67` (line 4). Recording the length
> is a small but real information disclosure about a live credential, and the
> one file where it matters is outside the scan's reach. Not a leak; a gap in
> the check that is documented as covering the directory.

---

## 2. Cases

`cases.ndjson`: **64** cases (README "~60"; validator bound 60±5). Ids unique
and ascending. Composition: area A 23 / B 13 / C 16 / D 12; splits train 21 /
dev 21 / test 22; `noul` 50 / `choice` 12 / `score` 2; 50 answerable /
14 unanswerable; `abstain_expected` true on exactly the 14 unanswerable.

I wrote an independent conformance checker (does **not** import
`validate_cases.py`) covering every `MUST` in `schema.md` §2, including the
per-`type` `criteria` container rules:

```
-- schema MUST conformance (independent) --
 violations: 0
-- abstain_expected subset of unanswerable --
  unanswerable = 14  abstain_expected = 14
  abstain_expected but answerable: []
  unanswerable but not abstain_expected: []
-- split discipline: every family (pair_id) in ONE split --
  families = 46;  families spanning >1 split = 0 {}
```

The builder's own validator agrees: `29/29 checks passed`,
`VALIDATOR RESULT: PASS`, from a clean clone.

**Control coverage.** All seven `variant_kind` values present, in the counts
`base 50, irrelevant_change 4, distractor 2, missing_evidence 2, noise 2,
opaque_labels 2, option_reorder 2`. The five controls the brief names
(`option_reorder`, `opaque_labels`, `distractor`, `missing_evidence`, `noise`)
are each present; `base` and `irrelevant_change` complete the enum. Ground
truth is invariant under the four GT-preserving kinds (checked case by case;
0 drift). `missing_evidence` invariants hold on both instances
(`answerable=false`, `answer=null`, `abstain_expected=true`).

**Contrastive pairs differ only in the deciding fact** — word-level diff of all
six (my own `difflib` pass, not the validator's):

| pair | members | same question | word similarity | change hunks | verdict |
|---|---|---|---|---|---|
| cp1 | c-p1a / c-p1b | yes | 0.733 | 2 | deciding fact flips (merge-ready → not) but **two** facts change — see F7 |
| cp2 | c-p2a / c-p2b | yes | 0.778 | 2 | single fact: actor field present ↔ empty |
| cp3 | c-p3a / c-p3b | yes | 0.957 | 1 | single token: 100% ↔ 12% traffic share |
| cp4 | c-p4a / c-p4b | yes | 0.957 | 1 | single token: `7a11c2` ↔ `9f0e44` — **but see F1** |
| cp5 | c-p5a / c-p5b | yes | 0.667 | 1 | single clause: clean/0 warnings ↔ 3 warnings |
| cp6 | c-p6a / c-p6b | yes | 0.792 | 2 | single fact: probes 200 ↔ connection refused |

Five of six are clean single-fact flips with the deciding fact stated verbatim
in the text. cp4 is a clean single-token flip but of a fact the text never
defines (F1). cp1 changes two facts (F7).

> **F1 (MATERIAL — ground truth).** **cp4's ground truth is not derivable from
> the model-visible text.** The question is *"Is build 903 reproducible from the
> recorded commit?"*; the state is *"The archived build manifest states: 'The
> recorded build manifest lists commit 7a11c2 as the source.'"* Nothing
> anywhere in the corpus establishes that `7a11c2` **is** the recorded commit.
> I grepped: `7a11c2` occurs 5× and `9f0e44` 4× in `cases.ndjson`, and every
> occurrence is inside c-p4a/c-p4b or their `irrelevant_change` variants — never
> a definition. The labels `yes`/`no` are an author convention imposed on
> indistinguishable evidence. The two members are, strictly, **both
> unanswerable**, and this is the only pair in the corpus with that defect.
> `validate_cases.py` cannot catch it: it checks GT *coherence*, never GT
> *derivability from the state text*.
>
> **Consequence, quantified.** Reclassifying c-p4a and c-p4b as unanswerable
> (the treatment every other unanswerable case already gets) gives:
>
> | mechanism | answerable acc as committed | answerable acc corrected | false-confidence as committed | corrected |
> |---|---|---|---|---|
> | prior | 44.0% | 43.8% | 14/14 | 16/16 |
> | rule | 78.0% | 79.2% | 14/14 | 16/16 |
> | lexical | 58.0% | 58.3% | 14/14 | 16/16 |
> | **jev** | **98.0%** | **100.0%** | 14/14 | 16/16 |
> | general_model | 100.0% | 100.0% | 13/14 | 15/16 |
>
> Jev's *only* answerable error is c-p4b (it answered `yes`, GT `no`, noul
> 0.55) — i.e. the single error in the whole grid is an artefact of a mislabelled
> case. Two further consequences: (a) T7a's one non-trivial Jev confidence
> verdict, cp4 `correct_order` (0.14 vs 0.10), becomes `unmeasurable`, leaving
> Jev with **zero** informative confidence-ordering verdicts on the grid; and
> (b) `b-miss1` aside, the corpus loses one of its two
> answerable→unanswerable `missing_evidence` flips. The direction of the
> correction is *against* the run's negative conclusions and *in favour of*
> Jev, so it does not rescue any escalation claim — it removes one.

> **F7 (minor).** cp1 is not a single-fact edit: c-p1a asserts "All required
> reviewers have approved **and** the continuous integration gate is green"
> while c-p1b asserts only "The continuous integration gate is red because the
> new validation test fails" — the approvals clause is *dropped*, not flipped.
> The deciding fact still differs, so the pair is valid, but it does not meet
> "differing **only** in the deciding fact" in the strict sense. 1 of 6.

**Ground-truth justification elsewhere — PASS.** I read all 13 area-B cases in
full: each is genuinely unanswerable with a stated deciding fact and a rationale
that names the absence (conflicting records, truncated minutes, empty advisory
result, absent result files, unstated configuration identity). Each area-A
answerable case states its deciding numbers in the text. The two area-D
`missing_evidence`-style families and all four `irrelevant_change` cases hold
their GT. My automated "is the deciding fact present in the state" probe flagged
19 cases; all 19 are legitimate (area-B deciding facts are *absence* statements,
area-D deciding facts are policy evaluations), i.e. false positives of the
heuristic, not corpus faults.

> **F5 (minor, doc).** `schema.md` §5 says *"At n=62 the cheapest-test-first
> bar applies"*. The corpus is 64. The other stale-number candidate
> (`README.md` "~60 synthetic cases") is a declared approximation and is fine.

---

## 3. Baselines

### 3.1 Ground-truth leakage — none found, proven by instrumented access

Rather than reading the code and judging, I wrapped every case in a recording
`dict` proxy and ran each mechanism, logging every key actually touched:

```
=== fit_prior reads ===
  ['ground_truth', 'ground_truth.answer', 'ground_truth.answerable',
   'questions', 'questions[].type', 'split']
=== run_prior (prediction time) reads ===
  ['control', 'control.label_map', …, 'questions[].criteria', 'questions[].type']
  LEAK: NONE
=== run_rule (prediction time) reads ===
  ['area', 'questions[].criteria', 'questions[].instructions', 'questions[].type',
   'routing', 'routing.signals', 'routing.signals.known_root_cause', …, 'state']
  LEAK: NONE
=== run_lexical (prediction time) reads ===
  ['control', 'control.label_map', …, 'questions[].instructions', 'questions[].type', 'state']
  LEAK: NONE
=== run_jev.build_request reads ===
  ['questions', 'questions[].criteria', 'questions[].instructions', 'questions[].type', 'state']
  LEAK: NONE (reads only state + questions)
=== run_baselines.build_general_request reads ===
  ['questions', 'questions[].criteria', 'questions[].instructions', 'questions[].type', 'state']
  LEAK: NONE (reads only state + questions)
```

Four conclusions:

1. **No mechanism reads `ground_truth` at prediction time.** The only
   ground-truth read is `fit_prior`, and it is filtered on `split == "train"`
   and `answerable` — a legitimate train-only fit, and the split discipline in
   §2.6 keeps dev/test out of it.
2. **Neither model request builder can leak.** `run_jev.build_request` and
   `build_general_request` read exactly `state` + `questions[0]`. Routing
   signals, ground truth, `legal_roles` and `expected_role` are structurally
   unreachable from the wire. The schema's claim holds by construction, not by
   convention.
3. **`rule` on area D recomputes rather than reads.** It touches
   `routing.signals` and never `routing.expected_role` / `legal_roles` /
   `illegal_roles`. Its 12/12 is therefore a *tautology* (same policy defines
   the answer) — which `README.md`, `T9` and `DISPATCH.md` all disclose. One
   thing they do **not** say, which I found: on area D `rule` never reads
   `state` at all. It is a policy simulation over hand-authored signals, not a
   text mechanism. Worth stating, because "rule got area D right" otherwise
   reads as evidence that rules can read prose.
4. **The cue lexicons are hand-authored with the corpus in view** — disclosed in
   `run_baselines.py`, `README.md`, `INDEX.md` and `DISPATCH.md`. `rule` 78.0%
   and `lexical` 58.0% are upper bounds on a generic cue engine, not
   measurements of one. Correctly and repeatedly disclosed.

### 3.2 Deterministic mechanisms re-run from a clean clone

```
$ git clone --branch research/jev-phase1-565 <worktree> /tmp/opencode/jev-phase1-verify/clone
$ cd .../phase1 && python3 harness/run_baselines.py --skip-general \
      --out /tmp/opencode/jev-phase1-verify/baselines_offline_repro.ndjson
  baselines 64/64
  run_baselines: wrote 192 rows
```

```
committed offline rows: 192  repro rows: 192
same key set: True
field diffs (excluding timestamp_utc): 0
rows whose timestamp_utc differs: 192 of 192
```

**PASS with the documented tolerance only** — `timestamp_utc` is wall clock,
declared a non-scoring input in `schema.md` §3.4 and confirmed unused by every
metric. Nothing else moved. `prior`, `rule` and `lexical` are exactly
reproducible from the corpus.

---

## 4. Jev raw evidence — live re-run

`OPENCODE_GO_API_KEY` was confirmed **set and non-empty**; its value was never
printed, never passed on a command line, and never written to any artefact.
I wrote my own minimal client (`live_jev.py`) that rebuilds the request body
from `cases.ndjson` and does **not** import `common.py` or `run_jev.py`, so
this is an independent reproduction rather than a rerun of the builder's
client. Endpoint `POST https://opencode.ai/zen/v1/systemone`, explicit
`User-Agent` (mandatory — Cloudflare 1010 without it).

**17 cases re-run once each** (saturated answerable, unanswerable, the
`missing_evidence` control, a contrastive pair, both `option_reorder` members,
an `opaque_labels` base+variant, and both `score` cases):

```
label flips: 0/17   correctness flips: 0/17   probability MAP identical: 17/17
input tokens identical: 17/17
output tokens identical: 17/17
request_hash committed == repro: True  (17/17)
```

`request_hash` matching on 17/17 is the strongest single check here: my
independently-built bodies are **byte-identical** to the ones the builder sent,
so the comparison is like-for-like. Every observable moved by at most ±0.01 and
nothing crossed the 0.5 decision boundary. The closest call, b-i03, sat at
0.55 committed and 0.54–0.56 across 6 further observations — above the boundary
every time, but with only 0.04 of headroom.

**54 further calls** to characterise the stochasticity that `RUNBOOK` §4
declares and that preflight P2c measured (0.59 then 0.61 on the same request):

| case | committed | 6 further observations | boundary crossings |
|---|---|---|---|
| b-i01 (unanswerable) | 0.56 | 0.56, 0.57, 0.56, 0.60, 0.56, 0.58 | 0 — Jev said *yes* 7/7 |
| b-i03 (unanswerable) | 0.55 | 0.56, 0.55, 0.54, 0.54, 0.56, 0.56 | 0 — said *yes* 7/7 |
| b-a01 (unanswerable) | 0.69 | 0.69, 0.69, 0.67, 0.68, 0.70, 0.69 | 0 — said *yes* 7/7 |
| b-a02 (unanswerable) | 0.08 | 0.08, 0.09, 0.09, 0.08, 0.09, 0.09 | 0 |
| a-miss1 (evidence removed) | 0.28 | 0.27, 0.28, 0.29, 0.29, 0.30, 0.27 | 0 |
| c-p4a / c-p4b (8 reps each) | 0.57 / 0.55 | 0.56–0.57 / 0.55–0.57 | 0 |

The run's central negative finding — **Jev emits a confident `yes` on
unanswerable cases** — reproduced 7/7 on each of three independent unanswerable
cases, and the `missing_evidence` control's confidence **rose** rather than fell
(0.27–0.30 vs base 0.28) in 6/6 repeats. That is a stable observation, not a
draw.

**Raw-body integrity.** All 64 jev rows: `raw_response` non-empty, JSON-parseable,
and consistent with the stored `parsed` / `prediction` / `usage` on re-parse
(0 mismatches on the `noul` → `{yes, no}` expansion, the reported-confidence
field and the token counts). The single failure in the grid
(`general_model` / `b-i03`) is a typed `empty_content` with the full body
preserved, including `finish_reason: "length"` and the truncated
`reasoning_content` — exactly as `schema.md` §3.2 requires. No missing rows, no
duplicates, no untyped failures, nothing that looks fabricated.

> **F3 (moderate — reliability understated).** I re-ran `general_model` 35 times
> at the committed `max_tokens=256` and hit `empty_content` **4 times
> (≈11%)** — 3/20 in a focused repeat, plus 1 in a 15-case sweep, landing on a
> *different* case each time (b-a01, where the committed run succeeded). The
> committed run's `general_model` error count of **1/64 (1.6%)** is therefore a
> lucky draw, not a measured reliability. `RUNBOOK` §4 gotcha 4 and the comment
> at `run_baselines.py:84` both read as though 256 *fixed* the problem ("256
> cleared all three probe cases"); it reduces it from ~22% (14/64 at 16) to
> ~11%, it does not eliminate it. The non-determinism *is* disclosed; its
> **magnitude at 256 is not**. Nothing downstream depends on this — the
> unusable cell is excluded from accuracy and T1/T5/T6 already show
> `general_model` as 63 usable — but T11's "typed errors `empty_content=1`"
> should not be read as a rate.

---

## 5. Independent recomputation of the scoring math

I reimplemented the scoring from the written definitions in `schema.md`,
`README.md` and `DISPATCH.md` — **not importing `score.py`, `common.py`,
`routing_policy.py` or `validate_cases.py`** — reading only
`cases.ndjson` + `jev_raw.ndjson` + `baselines_raw.ndjson`. I restated the
routing policy from `schema.md` §2.2 by hand, and re-derived Jev's label and
probability vector straight from each verbatim `raw_response`.

Recomputed independently: per-cell correctness, the un-normalised
multi-category Brier, the accuracy triple (answerable-only / mixed /
false-confidence) overall and per area and split, McNemar paired deltas along
the whole cost chain and Jev-vs-everything, the coverage/error curve at
0.70/0.80/0.90/0.95, the Jev curve split by confidence convention, error
budgets at 1/5/10%, contrastive pairs and the four-valued confidence verdict,
every control's label-stability and Δconfidence, option-order perturbation and
position-bias histograms, routing legality recomputed from signals, and the
confidence-derivation test.

```
$ python3 indep.py && python3 compare.py
field comparisons run: 2315
DISAGREEMENTS: 60
```

**All 60 are the same artefact: `m8_routing.<mech>.per_case` does not record the
`is_expected` key at all** (my checker read it as absent). It is computed in
`build_cell`'s routing block but omitted from the `per_case` projection. The
aggregate `n_expected` that the table actually uses matches exactly for all five
mechanisms (prior 3, rule 12, lexical 4, jev 12, general_model 12), as does
per-case `is_legal`, `is_illegal`, `correct` and `confidence`. A cosmetic
omission, not a numerical one.

**Substantive disagreements: 0.** Spot-checks of the headline numbers against my
own figures:

| quantity | committed | mine |
|---|---|---|
| jev answerable-only accuracy | 98.0% | 0.98 (49/50) |
| jev vs lexical (chain) | +40.0pp, b=20 c=0, n=50 | +0.40, b=20, c=0, n=50 |
| jev vs general_model | −2.0pp, b=0 c=1, n=50 | −0.02, b=0, c=1, n=50 |
| jev Brier (all answerable) | 0.0355 | 0.0355 |
| jev coverage @0.90 | 38 acted, 59.4%, 0 errors | 38, 0.5938, 0 |
| jev @0.70 errors: false-conf / wrong-label | 4 / 0 | 4 / 0 |
| convention split @0.70: reported + derived | 13 + 35 = 48 acted, 0+4 = 4 err | identical, and 13+35=48 ✓ |
| routing recompute mismatches | 0 over 60 area-D cells | 0 over 60 |
| stored `confidence_formula` recheck | 0 mismatches / 319 | 0 / 319 |
| hypothesis A `(n·max(p)−1)/(n−1)` | mean 0.0005, max 0.005, 13/14 exact @2dp | mean 0.0005, max 0.005, 13/14 |
| hypothesis B `max(p)` | mean 0.0071, max 0.08, 12/14 exact | mean 0.0071, max 0.08, 12/14 |
| T7a jev verdicts | 1 correct_order, 0 inverted, 0 tied, 5 n/a | identical |
| T7b control Δconfidence (all 30 rows) | see T7b | identical, every cell |
| T7c selection (13 rows) | 3 inert-but-moved + 10 missing_evidence | re-derived from the stated filters, identical |
| T8a label stability | 4/4 for all five mechanisms | identical |
| T8b position histograms | prior {1:1,3:10,5:1} etc. | identical |
| T11 latency min/median/max, tokens, retries | — | identical |

Two things the recomputation also confirms about the *method*, not just the
arithmetic: the T5c convention split is exactly additive
(`reported.acted + derived.acted == combined.acted` and likewise for errors, at
all four thresholds), so T5b is not double-counting; and the `general_model`
usable count of 63 propagates consistently into T1 (`n_usable`), T5 (`excluded=1`)
and T6 without contaminating any accuracy denominator, because its one unusable
cell (`b-i03`) is unanswerable and accuracy is computed over answerable cells
only. No survivorship bias in the 100%.

I also verified the `confidence ≈ (n·max(p)−1)/(n−1)` claim independently of the
scorer: mean absolute residual **0.0005**, max 0.005, 13/14 exact at 2 dp,
versus `max(p)` at mean 0.0071 / max 0.08 — hypothesis A is ~14× better and is
supported. It is only testable on 14 of 64 cells, because Jev publishes no
confidence and no probabilities for `noul`, which is 50 of 64. That caveat is
stated in `README.md`, `T5a`, `T5c`, `T10` and `score.py`'s header. Correctly
stated everywhere it matters.

---

## 6. Adversarial falsification

The strongest positive claims in the tables are: **Jev 98.0% answerable-only
with +40.0pp over `lexical` and `c = 0`**, and **`general_model` 100.0%** —
i.e. "on this corpus Jev adds nothing over a free chat model".

**Attempt 1 — is the +40pp an artefact of pairing?** No. `c = 0` means Jev was
right on every case `lexical` was right on, across all 50 paired answerable
cases. That is a strict dominance on this corpus, not a coin-flip artifact, and
I reproduced `b=20, c=0` from raw data.

**Attempt 2 — inversion probe (does either model actually read, or pattern-match
the corpus author's prose style?).** I re-asked four cases with the *logically
negated* question, keeping the state fixed. A mechanism that reads must flip; a
mechanism matching surface style will not.

```
a-h01  inv "Did the flagged cohort exceed its stated 0.5% error budget?"  (exp yes)
       JEV noul=0.98 -> yes  correct | GEN 'YES' -> yes  correct
c-p1a  inv "Did the change fail its required approvals or its validation?"  (exp no)
       JEV noul=0.06 -> no   correct | GEN 'NO'  -> no   correct
c-p3b  inv "Did the dataset carry a positive rate above 50%?"               (exp no)
       JEV noul=0.18 -> no   correct | GEN 'NO'  -> no   correct
a-m01  inv "Are all nodes still running a release older than 4.7?"          (exp — my probe was malformed)
       JEV noul=0.04 -> no            | GEN 'NO' -> no
```

Both mechanisms track question semantics, including the `c-p3b` case where the
inverted question is about a *different subject* (the dataset) than the state
text supports. **The probe failed to break the claim**, which strengthens it:
`general_model`'s 100% is not a template artefact.

**Attempt 3 — are the adversarial controls real?** Verified on the wire, not in
the metadata.

* `option_reorder` **actually reorders.** The `criteria` key order inside the
  stored `request_body` sent to Jev differs between base and variant, and the
  declared `control.option_order` matches the variant's real order:
  `d-03` `['build','escalate','investigate','redesign','repair','review']` →
  `d-r01` `['review','escalate','build','repair','investigate','redesign']`;
  `d-06` → `d-r02` likewise. Same option set, same per-key label text, different
  order. The state sent is byte-identical.
* I also confirmed the harness's stated reason for insertion-order hashing: a
  `sort_keys` canonical hash of `d-03` and `d-r01` **collides** (`True`), while
  the insertion-order hash does not (`False`). The comment in `common.py` is
  correct and load-bearing.
* `opaque_labels` **map back**. `label_map` is a bijection onto the base's key
  set; the variant's option *label text* is byte-identical to the base's; the
  state is byte-identical; the wire keys are content-free
  (`opt_k7a1 → build`, `opt_w1e6 → repair`, …). Jev answered the opaque variant
  with the opaque key `opt_w1e6`, which `common.parse_jev` maps back to
  `repair` — correct. Independently reproduced live (§4).
* `missing_evidence` **truly removes the deciding fact.** 0 of 2 variants retain
  it. `a-miss1` sends only *"Feature flag 'new-checkout' was enabled for 5% of
  traffic. The flag was disabled the following morning. The cohort was not
  re-measured…"* — the 3.1% error rate and the 0.5% budget are both gone. I
  re-ran it 7×: confidence 0.27–0.30 against a base of 0.28, i.e. flat, and it
  answered anyway.
* `distractor` appends and does not alter: `a-dist1` state starts with the base
  state verbatim, +270 chars of explicitly irrelevant text.
* `noise` alters only surface form, as claimed: `a-noise1` shows word
  duplication (`THE THE dependency specifier specifier`), capitalisation and
  line breaks, and preserves `2.4.0` and `run 4412` — the deciding tokens.

> **F2 (MATERIAL — the cited evidence is a tautology).** The claim *"0 of 320
> cells set the `abstained` flag"* is presented in `README.md`, `DISPATCH.md`,
> `T1` and `T7c` as an empirical finding about the five mechanisms. It is not.
> `abstained` is **hard-coded** at construction and can never be anything else:
>
> ```
> $ grep -rn "abstained" harness/*.py
> harness/common.py:298:        "abstained": False,      <-- the only writer
> harness/score.py:236:        "abstained": bool(row.get("abstained")),
> ```
>
> `make_result` is the single constructor for every result row and sets
> `False` unconditionally; no harness path sets it `True`. So
> `n_abstained_flag == 0` is a property of the harness, not of the mechanisms.
> The honest statement is **"no mechanism in this grid has the ability to
> record an abstention"** — which is a stronger claim about the experiment
> design, and a weaker claim about the mechanisms, than the one made.
>
> **The substantive conclusion survives, on evidence that does measure it.** The
> real observations are independent of the flag: 69 of the 70 unanswerable cells
> (14 cases × 5 mechanisms) produced a non-null `prediction.label`, and the one
> exception (`b-i03`) failed in transport, not judgement. I re-derived both
> from raw data. So "no mechanism withheld an answer when the deciding fact was
> missing" stands; the `abstained`-flag citation does not support it and should
> be replaced by the label-presence count. `DISPATCH.md` already gets this right
> in one place ("the single cell that emitted no label did so because the
> transport failed") while `T7c` still leads with the flag.

**Attempt 4 — is the routing result a lookup?** I checked whether the area-D
states leak the answer. They do not: the role word (`build`, `repair`, …) never
appears in any state, and the option labels are semantically distinct. The
states actively contain **negations of the other roles' preconditions** — e.g.
d-01: *"No defect is known, no failure is unexplained, and no governing
assumption is known to be invalid"* — so the task requires tracking negation, not
matching a keyword. And it is not degenerate: an always-`escalate` strategy
would score 10/12, not 12/12. Jev's 12/12 and `general_model`'s 12/12 are
therefore real, and the fact that `lexical` managed only 5/12 legal shows the
text is not trivially keyword-addressable. `rule`'s 12/12 remains a tautology
and is labelled as one in three places.

**Attempt 5 — is T8b's `chi2 = 0.0` independent evidence?** No, and this is a
presentational point rather than a fault: because Jev, `rule` and
`general_model` are 12/12 on area D, their predicted-position histogram is
*identically* the expected-position histogram, so `chi2` is necessarily 0.0 and
`pred == expected position` is necessarily 12/12. The chi2 column restates T9;
it is not a second, independent measurement. The table's own framing (a
single-slot-picker would score far above uniform) is sound, and `prior`
(chi2 22.83) and `lexical` (4.83) do use it meaningfully.

---

## 7. Self-preference risk — CONFIRMED, and it is structural

**Confirmed.** One model family, `opencode-go/space-bunny-free`, occupies four
of the five seats in this experiment:

| seat | model |
|---|---|
| case author (`gen_cases.py`, all 64 cases, all ground truth, all rationales) | `opencode-go/space-bunny-free` |
| harness author (`run_baselines.py` cue lexicons, `score.py`, `GEN_SYS` prompt) | `opencode-go/space-bunny-free` |
| `general_model` baseline (the free comparator) | `opencode-go/space-bunny-free` (`space-bunny-free`) |
| D1 result author, and **D2 verifier (me)** | `opencode-go/space-bunny-free` |
| `jev` | `jev-1.13-free` — a different family |

`DISPATCH.md` discloses the D1/D2 same-family constraint for the *agents*; it
does not name the sharper instance, which is that **the free general model being
compared against Jev is the same model that wrote the corpus it is being tested
on, wrote the prompt template it is being asked to answer, and wrote the
vocabulary its 100% is scored against.**

Direction of the confound: it can only **inflate** `general_model`, never Jev.
So the affected claim is the one that decides the brief —
*"vs the free general model −2.0pp"* / *"a free chat model matched Jev"* — and
the confound pushes in the direction of that claim being **less** impressive than
it looks. Equivalently: the run may be understating Jev's advantage over a free
chat model.

**What I could do about it, and what I could not.** With operator-approved
models only (`space-bunny-free`; the Go route 403s with this credential; no
other model is approved for this task, and model selection is operator-gated), I
could not run a cross-family general-model control. The inversion probe (§6,
Attempt 2) is the strongest available substitute and it passed: the model
tracks question semantics rather than template shape. That rules out the crudest
version of the artefact but **not** the stylistic one — a same-family model may
parse same-family prose more reliably, and 50 synthetic cases cannot separate
that from genuine comprehension. **This confound is unresolved and cannot be
resolved inside the current model-approval envelope.** It is a legitimate Phase 2
question: add one cross-family general-model baseline, same prompt, same corpus.

---

## 8. Reproducibility — RUNBOOK from a clean clone

Executed in a genuine clone outside the worktree, in the order written.

| # | RUNBOOK §5 check | Result |
|---|---|---|
| 1 | `validate_cases.py` → `29/29`, `VALIDATOR RESULT: PASS`, `cases=64` | **PASS** |
| 2 | the three input hashes | **PASS** (3/3) |
| 3 | `score.py --self-check` exits 0, prints the determinism line | **PASS** |
| 4 | `320 cells, complete` | **PASS** |
| 5 | `routing recompute mismatches: 0` | **PASS** |
| 6 | `confidence recheck mismatch : 0` | **PASS** (319 cells) |
| 7 | `scored.ndjson` = `662d6ec6…` | **PASS** |
| 8 | `metrics.json` = `3d2e3ac5…` | **FAIL** — actual `d080965f…` |
| 9 | `git status` after re-scoring names only the manifest | **PASS** |
| 10 | `0 hits over 14 emitted files` | **PASS** |
| 11 | the §3.4 manifest assertion block | **FAIL** — same stale hash |
| 12 | tier 2, live reachability | **PASS** (§4) |

Actual scorer output from the clean clone:

```
self-check: scoring is deterministic (byte-identical)
score.py 1.0.0
  grid                       : 64 cases x 5 mechanisms = 320 cells, complete
  routing recompute mismatches: 0
  confidence recheck mismatch : 0
  scored.ndjson sha256        : 662d6ec615b5d9193f905145dc731e095db6c8203418a6fcf3ccdb6dacb179b3
  metrics.json sha256         : d080965f47dd683038009f78fa31471d1bd59bb06424b488753f83e0ccfbcab9
  secret scan                 : 0 hits over 14 emitted files (boolean only)
  outputs                     : 15 files
```

and the §3.4 block, verbatim:

```
RUNBOOK 3.4 ASSERTION BLOCK: FAIL
  actual metrics.json sha in manifest: d080965f47dd683038009f78fa31471d1bd59bb06424b488753f83e0ccfbcab9
  runbook expects                     : 3d2e3ac5bf00acc9c90c2917f59cd59347201547fb13731317658a7db6a3a9ee
```

**Determinism and reproducibility themselves are sound.** Re-scoring in the
clean clone reproduced `scored.ndjson`, `metrics.json` and all 13 table files
byte-for-byte; `git status --porcelain` named **only** `results/manifest.json`,
and a key-by-key diff of the two parsed manifests showed exactly **two**
differing keys — `git.commit` and `git.remote` — precisely the two the RUNBOOK
§3.4 says can move. `results/manifest.json` is self-consistent: every hash it
records for `scored.ndjson`, `metrics.json` and the 13 tables matches the
committed bytes.

> **F4 (minor, documentation — but it breaks the verifier checklist).**
> `RUNBOOK.md` records stale hashes for `metrics.json` and `manifest.json`, so
> §5 checks 8 and 11 **fail on a clean clone of the current HEAD**.
>
> | artefact | RUNBOOK says | actually is |
> |---|---|---|
> | `results/metrics.json` | `3d2e3ac5…` (§3.3, §3.4, §5 twice) | `d080965f…` |
> | `results/manifest.json` | `d07dad4a…` | `0a54daa6…` |
>
> Cause, and it is *not* silent tampering: commit `19eccb0f` (titled
> `docs(jev-phase1): D1 result, guard incident, and pre-quote caveats`) also
> changed `harness/score.py` to add `n_abstained_flag` and
> `n_unanswerable_no_label`, and regenerated `metrics.json`, `T1`, `T7` and the
> manifest. The commit message states the hash change explicitly and correctly
> (`metrics.json sha256 is now d080965f… (previous 3d2e3ac5…)`). I diffed
> `metrics.json` across that commit: the **only** changes are the two added
> counter fields per mechanism block; no accuracy, gain, Brier, coverage or
> routing figure moved. `scored.ndjson` is unchanged at `662d6ec6…`. So the
> data is sound — but the RUNBOOK was not updated with it, and a `docs(...)`
> commit that modifies a scorer and four generated artefacts is mislabelled by
> conventional-commit terms, which is what let the drift go unnoticed.
>
> **F4b (minor, documentation).** RUNBOOK §4.1 is not executable as written:
>
> ```bash
> python3 harness/gen_cases.py --out /tmp/opencode/jev-cases-repro.ndjson
> sha256sum /tmp/opencode/jev-cases-repro.ndjson   # must equal the cases hash
> ```
>
> `gen_cases.py` has **no argument parsing at all**. `--out` is silently
> ignored and `main()` unconditionally writes `<repo>/cases.ndjson`. I ran it in
> the clone: the scratch file was never created (`sha256sum: … No such file or
> directory`) and the in-tree `cases.ndjson` was rewritten. It happens to be
> byte-identical, so nothing was lost, but the step as documented would both
> fail *and* mutate the committed corpus. This also **contradicts the RUNBOOK's
> own gotcha #1** ("`gen_cases.py` … take no arguments … `gen_cases.py`
> **overwrites `cases.ndjson`**"). Gotcha #1 is right; §4.1 is wrong.

**Nondeterminism recorded (as required).**

| source | magnitude | affects |
|---|---|---|
| Jev, saturated `noul` answers | 0.00 (byte-identical) | — |
| Jev, mid-range `noul` (0.5–0.7) | ±0.01 observed, up to 0.06 over 6 reps (b-i01 0.56→0.60) | could flip a label only within ~0.05 of 0.5; no committed label is that close except c-p4b at 0.55, which stayed wrong 9/9 |
| Jev, `choice` / `score` | 0.00 on the 5 re-run (probabilities saturated at 1.0) | — |
| `general_model` at `max_tokens=256` | ≈11% `empty_content` (4/35) | `n_usable` 63/64 was a lucky draw (F3) |
| `timestamp_utc` on every row | wall clock | none — verified unused by every metric |
| `latency_ms` | run to run | none — `schema.md` §3.4, confirmed |
| Tier 1 (scoring) | **0** — byte-identical across clones and re-runs | — |

---

## 9. Unresolved uncertainties

1. **Self-preference (§7) is unresolved and unresolvable under the current
   model-approval envelope.** The one claim it threatens —
   *"a free general model matched Jev"* — is the claim that decides the brief,
   and the confound biases it toward looking better than it is. Highest-value
   open question from this verification.
2. **Whether Jev's near-boundary `noul` values can cross 0.5.** b-i03 sat at
   0.54–0.56 over 7 observations; 0.04 of headroom against a ±0.01 wobble. If
   it crosses, Jev's unanswerable false-confidence count drops by one and its
   `c-p4b` error may or may not resolve. n is far too small to characterise the
   tail.
3. **The `general_model` reliability rate (F3)** rests on 35 calls concentrated
   on 4 cases. The per-call rate is plausibly ~5–15%; I did not measure it
   across the full 64, so I cannot say whether the failures are
   case-independent (my evidence says yes: b-a01, b-i03, b-a01, b-i03 across
   the two experiments) or partly case-driven.
4. **Statistical power.** n=64 (50 answerable). No significance test is claimed
   anywhere and none should be added without a power calculation first. My
   `c = 0` reading of the +40pp is a statement about this corpus, not a
   population claim.
5. **Whether `cp4` was intended to be answerable** (F1). I can prove the ground
   truth is not derivable from the text; I cannot know whether the author
   intended an out-of-band convention (e.g. "7a11c2 is *the* recorded commit by
   construction of the fixture") or simply mislabelled it. The corpus does not
   say. The correction I quantified in §2 is what the text supports.
6. **Areas not exercised at all**, correctly declared: multi-question requests;
   `state` as an object; `instructions` as object/array; a per-area or
   per-difficulty prior; the Go chat route (403 with this credential).
7. **I did not re-run the full 64-case live grid** (I ran 17 distinct cases and
   54 repeats, 71 calls total). The 47 un-run cases rest on the committed raw
   rows, which I verified are internally consistent and hash-linked to the sent
   bytes — but their *values* are not independently re-measured.

---

## 10. Claims that could NOT be verified

Stated explicitly, as required.

1. **That the committed `noul` / `choice` / `score` values for the 47 cases I
   did not re-run are the values the API actually returned.** I verified they
   are internally consistent, that `request_hash` matches the sent bytes, and
   that the 17 I did re-run reproduce — but I cannot re-derive 47 unobserved
   responses. In particular no claim is made here that Jev's per-case numbers
   are exactly what a fresh run would produce.
2. **That the reported `confidence` field is *derived* by
   `(n·max(p)−1)/(n−1)` — only that it is *consistent* with it.** The residual
   is 0.0005 mean / 0.005 max over 14 cells, which is the rounding floor of the
   published probabilities, so this is strong consistency evidence and **not**
   proof of the mechanism. The API's internal computation is a black box.
3. **That `noul` = P(yes).** Accepted on the preflight reverse-anchor argument
   (pass→0.99, fail→0.01) and on 17 live calls whose labels matched ground truth
   100% of the time on answerable cases. Strong behavioural evidence, not a
   specification.
4. **The `general_model` reliability figure in `T11` / the manifest's
   `error_counts`** as a *rate*. I measured ≈11%; the committed artefact says
   1/64. I verified the committed run is a faithful record *of that run*; I
   cannot confirm it characterises the mechanism (F3).
5. **Whether `rule`'s and `lexical`'s cue lexicons constitute leakage in the
   stronger sense.** They read no ground truth (proved), but they were authored
   with the corpus in view, so their 78.0% / 58.0% are upper bounds on a
   *generic* cue engine only. I cannot measure the generic version without
   authoring new cues, which would repeat the same circularity.
6. **That the corpus represents real engineering-judgement tasks.** Every case
   is synthetic, template-generated prose. The 98%/100% figures measure
   performance on this corpus, full stop.
7. **Any cross-family general-model comparison** (§7) — not attempted, outside
   the operator-approved model set.
8. **The provenance claim `git.commit = 00729ea9` in the committed manifest.**
   The manifest necessarily records the commit *before* the one containing it,
   so it can never name itself; it correctly names `00729ea9`, the parent of
   `19eccb0f`. Self-consistent, and a fixed point is impossible by
   construction.
9. **Whether `metrics.json`'s two new counters (`n_abstained_flag`,
   `n_unanswerable_no_label`) were present when the earlier 33-claim re-derivation
   in `19eccb0f` ran.** The commit says every number in `DISPATCH.md` and
   `README.md` was re-derived from `metrics.json` by script before committing.
   I independently re-derived **all** the DISPATCH/README numbers I could
   identify and they match; I could not reconstruct the builder's original
   33-item checklist, so I verified the *values*, not the *claim that 33 items
   were checked*.
10. **That `b-miss1` is a meaningful `missing_evidence` control.** Its base
    `b-a01` is *already* unanswerable, so removing evidence from it tests
    nothing about evidence removal. The corpus discloses this in its own
    rationale, and `a-miss1` is a proper answerable→unanswerable flip — so the
    control class has n=1 discriminating instance, not n=2.

---

## 11. What the verification changes about how the run should be read

Nothing in this report overturns the run's two governing conclusions, and one
correction moves against them.

* **Unchanged and now independently confirmed.** Jev's answerable-only accuracy
  is 98.0% (100.0% on the justified subset, F1) and it strictly dominates the
  hand-built lexical baseline (`b=20, c=0`). Jev emitted a confident label on
  14/14 unanswerable cases — reproduced 7/7 on three cases in a fresh live
  sample — and no mechanism in the grid withheld an answer when the deciding
  fact was absent. Jev publishes no confidence for `noul` (50/64), so its
  escalation numbers rest on a locally derived quantity; the convention
  sensitivity is reported honestly in `T5c` and is arithmetically consistent.
* **Needs restating, same direction as the run.** The `abstained`-flag citation
  (F2) must be replaced by the label-presence count, and the
  `general_model` reliability figure (F3) must be reported as a rate with a
  measured range rather than a single lucky draw.
* **Needs correcting.** `RUNBOOK` §3.3/§3.4/§5 hashes and §4.1 (F4, F4b);
  `schema.md` §5 `n=62` (F5); the secret scan's file set (F6); cp1's
  single-fact claim (F7).
* **Must be carried into `findings.md` as a first-class limitation.** The
  self-preference confound (§7) is structural, is disclosed nowhere in the
  current artefacts, and weakens the single comparison that decides the brief.

---

*Verification performed 2026-09-26 by the D2 verifier, `opencode-go/space-bunny-free`,
in session isolation from D1 (no builder context; all state read from git).
Scratch evidence, including the independent reimplementation (`indep.py`),
the field-by-field comparator (`compare.py`), the corpus checker
(`cases_check.py`), the leakage probe (`leak_probe.py`), the independent live
client (`live_jev.py`) and every raw response body, is under
`/tmp/opencode/jev-phase1-verify/`.*
