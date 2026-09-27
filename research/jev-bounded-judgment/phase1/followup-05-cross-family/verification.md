# followup-05-cross-family — independent verification (verifier of record)

**Crosslink issue:** #565 · **Branch:** `research/jev-phase1-565`
**Verifying:** `research/jev-bounded-judgment/phase1/followup-05-cross-family/`
**Verifier:** independent session, no builder context. `COMPARISON.md` was NOT
read until all Step-1 numbers below were derived from raw evidence.
**Date:** 2026-09-27 · **Worktree:**
`/home/claude-code/projects/ASES/.worktrees/jev-phase1`

## 1. Verdict

**PASS WITH FINDINGS**

## 2. Independent derivation (mine, from raw bytes — not the author's numbers)

All quantities below were computed by me before opening `COMPARISON.md`,
from `staging/*/results/scored.ndjson`, `staging/*/results/baselines_raw.ndjson`,
`out/answers-*.ndjson`, `out/runlog-*.json`, `out/events-ling-*.jsonl`,
`out-chunk16-record/`, `../followup-02-mimo-v2.6-flash/results/mimo_raw.ndjson`,
`../cases.ndjson`, and `../harness/score.py`.

### 2.1 big-pickle and mimo grids (from `staging/<arm>/results/scored.ndjson`)

| quantity (my computation) | big-pickle | mimo |
|---|---|---|
| total scored rows | 320 | 320 |
| `general_model` cells | 64 | 64 |
| `general_model` usable | 64 | 64 |
| `general_model` unusable | 0 | 0 |
| `general_model` typed_error distribution | `null`: 64 (0 typed errors) | `null`: 64 (0 typed errors) |
| answerable n (general_model) | 50 | 50 |
| correct (answerable) | 49 | 49 |
| accuracy (answerable) | 49/50 = **0.98** | 49/50 = **0.98** |
| errors (answerable, case_ids) | **`c-p4b` only** | **`c-p4b` only** |
| unanswerable n | 14 | 14 |
| unanswerable emitted label (`pred_label is not None`) | 14/14 | 14/14 |
| unanswerable `unanswerable_but_answered` | 14 | 14 |
| unanswerable `abstained` | 0 | 0 |
| jev answerable errors (same file, `mechanism==jev`) | `c-p4b` only | `c-p4b` only |
| `c-p4b` detail (both mechanisms, both arms) | `pred=yes gt=no area=C answerable=true abstain_expected=false usable=true` | identical |

Corroborating raw scorer output (`metrics.json:m1_accuracy.overall`,
read as evidence, not trusted — my table above is from `scored.ndjson`):

```
big-pickle general_model: n_answerable=50 n_correct_answerable=49 acc_answerable=0.98
  n_cells=64 n_usable=64 n_unusable=0 n_unanswerable=14 n_answered_unanswerable=14
mimo general_model: identical figures
```

### 2.2 Paired McNemar vs jev (same answerable set, both usable)

Pairing restricted to cases where BOTH mechanisms produced a usable label on an
ANSWERABLE case (the frozen `score.py` rule, reimplemented independently by
joining `scored.ndjson` on `case_id`):

| arm | n paired | b (arm right, jev wrong) | c (jev right, arm wrong) | ties |
|---|---|---|---|---|
| big-pickle vs jev | 50 | **0** | **0** | **50** |
| mimo vs jev | 50 | **0** | **0** | **50** |

Cross-check: `metrics.json:m3_incremental_gain.ALL` for
`general_model vs jev` reports `n_paired=50 discordant_b=0 discordant_c=0`
in both arms — consistent with my join, but my numbers above are from the join.

### 2.3 Label-by-label arm-vs-jev diffs (all 64 cases)

big-pickle vs jev — **4 diffs**, all unanswerable area-B with
`abstain_expected=true`:

```
('b-a01', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
('b-a05', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
('b-i01', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
('b-i03', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
```

mimo vs jev — **3 diffs** (subset of the above):

```
('b-a05', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
('b-i01', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
('b-i03', arm=no, jev=yes, answerable=False, area=B, abstain_expected=True)
```

Hence: **0 answerable label diffs** for either arm (same label on all 50
answerable cases). big-pickle's extra diff vs mimo is `b-a01`.

### 2.4 Transport control (followup-02 direct-HTTP mimo vs followup-05 agent-routed mimo)

Joined `followup-02-mimo-v2.6-flash/results/mimo_raw.ndjson` (64 rows,
`mechanism=mimo_v26_flash`) against
`staging/mimo/results/baselines_raw.ndjson` filtered to
`mechanism=general_model` (64 rows), labels from `prediction.label`,
ground truth from `cases.ndjson:id/ground_truth`:

```
total flips: 1 ['c-p6a']
c-p6a f02: no f05: yes gt: yes answerable: True area: C abstain_exp: False
f02 acc: 48/50 = 0.96, errors ['c-p4b', 'c-p6a']
f05 acc: 49/50 = 0.98, errors ['c-p4b']
```

So: exactly **1 label flip in 64 (1.6%)**, favouring the agent route,
`48/50 -> 49/50`. The flipped cell is answerable area-C `c-p6a`.

### 2.5 Chunk-16 vs chunk-8 identity

```
out/answers-big-pickle.ndjson:                bytes 2524 sha256 cb8862568e74ec82eac24b7d7dc352cf03a821a42b30ca71fca0d68e4f332435 lines 64
out-chunk16-record/answers-big-pickle.ndjson: bytes 2524 sha256 cb8862568e74ec82eac24b7d7dc352cf03a821a42b30ca71fca0d68e4f332435 lines 64
diff: IDENTICAL
```

Per-chunk counts: `out/answers-big-pickle-0*.ndjson` 8 lines x 8 chunks = 64;
`out-chunk16-record/answers-big-pickle-0*.ndjson` 16 lines x 4 chunks = 64.

### 2.6 Corpus integrity

```
phase1/cases.ndjson:              7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c
staging/big-pickle/cases.ndjson:  7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c
staging/mimo/cases.ndjson:        7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c
```

Prefix `7dd4698f...f558c` matches the frozen value. Staging copies are
byte-identical to the frozen corpus. `jev_raw.ndjson` is likewise identical
in all three places (`e17ae014...d3bc`).

### 2.7 Reproducibility (frozen scorer re-run by me)

Hashes BEFORE re-run:

```
big-pickle scored.ndjson: de1686e03b02e65a32979850673ed7a6855efb3eb3ca59d4166164d716453498
big-pickle metrics.json:  744dff6ef6f591ed2834af3d71a93a826e425a9c8f18b93ded352aaeee31933a
mimo scored.ndjson:       933d8d486e22c932678691391467e5d8fba064b2dde4bb74dedb56c3979ab3ac
mimo metrics.json:        9773e8e6bbc74416179c5d3ee79fed4cd5b40b4d49a4ea5fca15d539d2339a13
```

Commands (frozen harness, unmodified):

```
python3 phase1/harness/score.py --phase1-dir <abs>/staging/big-pickle --no-tables → EXIT 0
  grid: 64 cases x 5 mechanisms = 320 cells, complete
  routing recompute mismatches: 0 / confidence recheck mismatch: 0
  scored.ndjson sha256: de1686e0... (match) / metrics.json sha256: 744dff6e... (match)

python3 phase1/harness/score.py --phase1-dir <abs>/staging/mimo --no-tables → EXIT 0
  grid: 64 cases x 5 mechanisms = 320 cells, complete
  routing recompute mismatches: 0 / confidence recheck mismatch: 0
  scored.ndjson sha256: 933d8d48... (match) / metrics.json sha256: 9773e8e6... (match)
```

After re-run `scored.ndjson`/`metrics.json` hashes were UNCHANGED (pure
functions). Only `manifest.json` changed, and only two fields:

```
- "commit": "0f25e4926a61b88f7b1725bcc4c2d91badc42da7"
+ "commit": "fefdce0859ae116316943ddb41229bd2dc4f8ce8"
- "generated_utc": "2026-09-27T15:43:51Z"
+ "generated_utc": "2026-09-27T16:57:24Z" (big-pickle) / "16:57:27Z" (mimo)
```

I restored both manifests with the single permitted targeted restore
(`git checkout -- <both manifest.json>`); the tree is clean of my side effect.
No harness file was modified: `git diff HEAD -- phase1/harness/ phase1/cases.ndjson`
is empty (see section 6).

### 2.8 ling (24/64, exit-0 failures, no parseable text-block JSON)

`out/runlog-ling.json`: `n_collected=24`, `missing_case_ids` 40 entries.
Attempts:

```
chunk 00 attempt 1 exit 0 stage ok n_rows 8
chunk 01 attempt 1 exit 0 stage ok n_rows 8
chunk 02 attempt 1 exit 0 stage ok n_rows 8
chunk 03 attempt 1 exit 0 stage validation error "count=0 expected=8 ... unparsable_lines=1"
chunk 04 attempt 1 exit 0 stage validation error "count=0 expected=8 ... unparsable_lines=32"
chunk 05 attempt 1 exit 0 stage validation error "count=0 expected=8 ... unparsable_lines=1"
chunk 06 attempt 1 exit 0 stage validation error "count=0 expected=8 ... unparsable_lines=1"
chunk 07 attempt 1 exit 0 stage validation error "count=0 expected=8 ... unparsable_lines=9"
```

Verified: **24/64 collected; chunks 03-07 all exited 0** (transport healthy,
validation failed with `count=0`).

Text-block scan (`out/events-ling-*.jsonl`, `part.type==text`):
chunks 00/01/02 contain 8 parseable single-line `{"case_id","content"}`
objects each. Chunks 03-07 contain **0 parseable single-line objects in every
text block**:

```
ling-03 text blocks: 0, 0
ling-04 text[0] (pretty-printed multi-line JSON, 8 objects over ~40 lines): 0 single-line
ling-05 text[0..2]: 0, 0, 0
ling-06 text[0..1]: 0, 0
ling-07 text[0]: 0
```

Note: ling-04's text block DOES contain 8 JSON objects, but pretty-printed
across multiple lines, so no single line parses and the strict NDJSON extractor
correctly rejects the chunk. Valid NDJSON for chunks 03/05/06 exists only in
bash-tool fields, which the frozen extractor does not read.

False NDJSON-compliance self-claims, verbatim:

> `The NDJSON output above contains one line per case in order, each with the answer derived from the text in user_message. Every case has ambiguous, insufficient, or contradictory evidence that cannot affirmatively confirm a YES, so all resolve to NO.` — chunk 03

> `The NDJSON output is complete with all 8 cases answered based solely on the text in each user_message.` — chunk 05

> `8 cases answered: 4 noul (YES/NO) and 4 choice (build/redesign/investigate/repair), each derived solely from the user_message text.` — chunk 06

### 2.9 Ground-truth containment

`smoke/build_tasks.py` strips `ground_truth`, `control.deciding_fact`,
`difficulty_note`, `routing` and enforces a leak guard on
`ground_truth|deciding_fact|difficulty_note|rationale|answerable`.
All 25 `out/tasks-*.json` files scanned: **NONE contain any of**
`ground_truth`, `deciding_fact`, `difficulty_note`, `rationale`, `answerable`
as substrings. Emitted per-case keys are exactly
`case_id/question_type/instructions/criteria/system_prompt_frozen/user_message`.

### 2.10 Pre-registered band for big-pickle (re-derived from `findings.md` section 6)

Verbatim criteria:

| outcome | criterion on the 50 answerable cases |
|---|---|
| Jev's niche supported | acc <= 90% (>= 5 errors) OR paired c >= 3 |
| **Jev's tier (is) unsupported** | **acc >= 96% (<= 2 errors) AND c <= 1** |
| inconclusive | 3-4 errors (92-94%) |

big-pickle observed: acc 49/50 = 0.98 (1 error, <= 2) AND c = 0 (<= 1).
**Both arms fire → band "Jev's tier UNSUPPORTED".**

## 3. Claim table (C1-C12)

| # | claim (author) | my number | author number | verdict | artefact + field verified |
|---|---|---|---|---|---|
| C1 | big-pickle 49/50 = 0.980, b=0 c=0 ties=50 | 49/50 = 0.98, b=0 c=0 ties=50 (n paired 50) | same | **PASS** | `staging/big-pickle/results/scored.ndjson` (join on `case_id`/`mechanism`/`answerable`/`usable`/`correct`); `metrics.json:m1_accuracy.overall` + `m3_incremental_gain.ALL` |
| C2 | 0 unusable, 0 typed errors over 64 | usable 64/64, `typed_error=null` 64/64 | same | **PASS** | `scored.ndjson` (`usable`, `typed_error`); `metrics.json:m10_cost_reliability.general_model.typed_errors.{None:64}` |
| C3 | same label on all 50 answerable | 0 answerable label diffs | same | **PASS** | `scored.ndjson:pred_label` join arm-vs-jev; diffs are exactly 4 unanswerable cases |
| C4 | sole error `c-p4b`, known D2-F1 / 1.3 defect, not derivable | sole error `c-p4b` (`pred=yes gt=no area=C`); state lacks recorded source commit `7a11c2` | same | **PASS** | `scored.ndjson`; `cases.ndjson` (`c-p4a`/`c-p4b`); `ERRATA.md:A6`; `PHASE1-VERDICT.md:1.3` |
| C5 | exactly 4 label diffs, ALL unanswerable area-B `abstain_expected=true` | 4 diffs: `b-a01 b-a05 b-i01 b-i03`, all `answerable=false area=B abstain_expected=true`, arm `no` vs jev `yes` | same | **PASS** | `scored.ndjson` (`pred_label`, `answerable`, `area`, `abstain_expected`) |
| C6 | all three mechanisms emitted label on 14/14 unanswerable | 14/14 emitted for EVERY mechanism, `abstained=0` | same | **PASS** | `scored.ndjson` per mechanism; holds for any triple |
| C7 | transport: exactly 1 flip in 64, favouring agent route (48/50 → 49/50) | 1 flip `c-p6a` (`no`→`yes`); f02 48/50 errs `[c-p4b,c-p6a]`; f05 49/50 errs `[c-p4b]` | same | **PASS** | `followup-02/results/mimo_raw.ndjson` vs `staging/mimo/results/baselines_raw.ndjson`, ground truth from `cases.ndjson` |
| C8 | flipped `c-p6a` IS followup-02's single `c=1` cell, half its refutation band | f02 single `c` cell is `c-p6a`; band was `acc>=96% AND c<=1` | same | **PASS** | `followup-02/comparison.md` section 3 + section 6; `followup-02/verification.md` section 3.5; my section 2.4 join |
| C9 | band for big-pickle is "Jev's tier UNSUPPORTED" | unsupported (acc 0.98 >= 0.96 AND c 0 <= 1) | same | **PASS** | `findings.md` section 6; `out/band-big-pickle.json:band_verdict` |
| C10 | programme INCONCLUSIVE by construction (two-arm rule, one scorable arm) | rule requires BOTH cross-family arms in same band; only big-pickle scored | same | **PASS** | `SMOKE.md` section 5; `RECON.md` section 6; `out/runlog-ling.json`; `out/smoke-longcat.jsonl` |
| C11 | longcat 403 "an active OpenCode Go subscription is required to use Go models" | same string, `statusCode=403 isRetryable=false` | same | **PASS** | `out/smoke-longcat.jsonl`; `SMOKE.md` section 1 |
| C12 | chunk-16 and chunk-8 big-pickle runs byte-identical | sha256 `cb886256...` both, 2524 bytes, 64 lines, `diff IDENTICAL` | same | **PASS** | `out/answers-big-pickle.ndjson` vs `out-chunk16-record/answers-big-pickle.ndjson` |

No C-claim fails. Every number reproduces from raw evidence.

## 4. Material findings

### F1 (material — prose overstates convergence; headline band unaffected): section 6 "four independent comparisons" / "four measurements of a tie" / "not one ... at any point"

- **WHY:** `COMPARISON.md` section 6 states `Four independent comparisons now point the same way`, `it is four measurements of a tie`, and `Not one of them has produced a cell where Jev is right and a free cross-family general model is wrong, at any point`. Three parts are inaccurate: (a) not independent — followup-02-direct and followup-05-agent are the SAME MODEL on two transports, and followup-01 is the declared weaker same-family reference; (b) not four ties — followup-02-direct is 48/50 vs 49/50 with `c=1`, a one-cell deficit; (c) "Not one at any point" is falsified by followup-02's `c-p6a`.
- **WHAT (basis):** my section 2.4 join; `followup-02/comparison.md` section 3 (`b=0/c=1`, named `c-p6a`) and section 6; `followup-02/verification.md` section 3.5; `COMPARISON.md` section 6 table (correctly lists `c=1`, contradicting its own sentence).
- **HOW CERTAIN:** proven (byte-level joins + author's own table).
- **WHAT-NOT-TESTED:** whether "independent" was meant loosely as distinct runs; I judge the sentence as written. Impact bounded: direction converges, headline band unaffected.

### F2 (informational — scan file count; no secret fault): 139 vs 151 files

- **WHY:** `COMPARISON.md` section 8 reports `139-file scan, 0 hits`. My walk finds 151 files. Delta is 5 untracked files created after the author's scan: `VERIFY-BRIEF.md` plus `out/verify-muse.err/.jsonl` and `out/verify-muse2.err/.jsonl`.
- **WHAT (basis):** `git status --short`; walk count 151; pattern scan for `sk-*`, key assignments: **0 credential VALUES**. Only permitted NAME/label mentions (`secrets/typesafe.env#TYPESAFE_API_KEY`, `auth.json#opencode-go`).
- **HOW CERTAIN:** evidence-based (pattern scan, not full entropy audit).
- **WHAT-NOT-TESTED:** did not scan `~/.local/share/opencode/auth.json` or `~/.secrets/typesafe.env` (out of scope by design).

No other material findings. C1-C12 all reproduce; scorer byte-deterministic; containment holds; transport control correctly measured.

## 5. Step-3 answers (adversarial judgement, from evidence)

### 5.1 Is the c-p6a fragility argument (section 5.1) sound, overstated, or wrong?

**Sound, carefully hedged.** The band needed BOTH `acc >= 96%` AND `c <= 1`; followup-02 met both on a one-cell margin (raw 48/50 exactly on floor; `c=1` exactly on ceiling). My join proves the `c=1` cell is `c-p6a` and the same model flips it under agent route. The author labels general instability a guess (`n=1 cell, n=1 model`), lists WHAT-NOT-TESTED, and notes big-pickle `b=0/c=0` is unaffected. The claim is that the transport axis was never in the noise model — true. Verdict: sound.

### 5.2 Was per-arm staging a legitimate substitution or a quiet instrument change?

**Legitimate, openly declared.** `smoke/stage_arm.py` refuses partial grids, copies `cases.ndjson`/`jev_raw.ndjson` byte-identical (hashes match), keeps prior/rule/lexical unchanged replacing ONLY 64 `general_model` rows, builds bodies via FROZEN `build_general_request`, hashes via FROZEN `request_hash`, parses via FROZEN `parse_general`, records agent-route endpoint explicitly with `latency_ms=null`/`usage=null` by design and `harness_version=1.0.0-followup05`, touches nothing in `harness/` (`git diff` empty), and frozen `score.py` consumes grids unchanged (320/320, 0 mismatches). Forfeiture of byte-level equivalence is DECLARED (`RECON.md` section 1/4) and MEASURED via mimo control (1/64).

### 5.3 Was refusing a prose parser for ling correct?

**Correct.** Frozen extractor reads ONLY final text block, strict single-line NDJSON; chunks 03-07 yield 0 lines there, with NDJSON-shaped content only in bash-tool fields outside the contract. A post-hoc bold/backtick parser would be invented after seeing failures, needs new `choice` rules (chunk 07 uses backticked raw keys requiring `label_map` translation the prose never performs), and converts compliance failure into pass. The property under test IS machine-actionable commitment; plausible prose is not measurement. Leaving 40 cells unscored is honest.

### 5.4 Is "four comparisons converge on a tie" stacking non-independent evidence?

**Yes — see F1.** followup-01 is corpus-author family (weaker test); followup-02-direct and followup-05-agent are same model twice (disagreeing on `c-p6a`); only big-pickle is new independent datum. Directional convergence is real; "four independent ties" is not. The INCONCLUSIVE programme verdict is the correct guardrail and the author reports it.

### 5.5 Anything overstated relative to n=50?

Two items, both section 6 prose (C1-C12 NOT overstated): (a) F1's "not one at any point" (false); (b) "question now answered in the negative" carries a thin qualifier for n=50, one scorable arm, uncharacterised family variance (author's own "outlier UNKNOWN"), untested batching beyond one arm, unsuppressible system prompt. Section 7 qualifiers (no significance test, 1-2 cells in noise, sample-only, variance unknown, confounders unquantified) are present and correct; overstatement is localised to section 6 convergence paragraph.

### 5.6 Does this overturn the followup-04 operational case? Scoping accurate?

**Accurate — does not overturn.** Operational axis (latency, concurrency, failures, cost) is unmeasured here by design (`latency_ms=null usage=null`; agent-route clock not comparable). Capability tie does not imply operational tie; author states exactly that. I did not re-audit followup-04 figures (out of scope); non-interference is structural.

### 5.7 Are Q2, Q3, Q4, Q6 correctly listed as untouched? Is Q4 binding?

**Yes.** Q2 (0.04 margin): no new unanswerable corpus; 14/14 answered reproduced. Q3 (calibration): big-pickle one-hot 64/64, no new evidence. Q6 (abstention): `abstained=false`, 14/14 answered. Q4 (non-synthetic): untouched and binding — per `findings.md` section 6 an "unsupported" band routes next budget to Q4 non-synthetic evaluation, which is why programme stays INCONCLUSIVE despite arm-level band firing.

## 6. Contamination check

```
git diff HEAD -- phase1/harness/ phase1/cases.ndjson → EMPTY
git diff HEAD -- phase1/results/ → EMPTY
git log --oneline -8 -- phase1/harness/ → newest 19eccb0f; no followup-05 commit touches harness/
git status --short (after manifest restore):
  M .crosslink/.last-hydrated-ref
  ?? .../followup-05-cross-family/VERIFY-BRIEF.md
  ?? .../followup-05-cross-family/out/verify-muse.err/.jsonl
  ?? .../followup-05-cross-family/out/verify-muse2.err/.jsonl
```

`.crosslink` is session bookkeeping. Untracked files post-date author scan; none scored. Author modified NO frozen harness code: staging reuses frozen builder/parser/hash/scorer unmodified (my section 2.7 re-run proof).

Credential scan over `followup-05-cross-family/` (151 files): **0 credential VALUES**. Only permitted NAME/label mentions. `secrets_recorded=false` on sampled raw rows; scorer secret scans report 0 hits.

## 7. Limitations of this verification

- No live model re-run; fabrication resistance rests on retained event streams/runlogs + hash consistency, not independent replication.
- Did not re-derive band thresholds, F1 correction set, or authorship table; took as frozen inputs, verified arithmetic on them.
- Ling chunk-07 bash rejected by permissions; "0 parseable in text blocks" holds regardless.
- followup-04 figures NOT re-verified (out of scope); non-interference judgement structural.
- `verify-muse*.jsonl` untracked logs are prior aborted run outputs, not author artefacts; scanned for secrets only.
- F1 "independent" judged as written; if meant colloquially as separate runs, reduces to diction. Numbers in table correct; INCONCLUSIVE stands.

---

*Verified 2026-09-27 in `/home/claude-code/projects/ASES/.worktrees/jev-phase1`, branch `research/jev-phase1-565`. Read-only except this file plus the single permitted `git checkout --` restore of two `manifest.json` files (no commit, no push). All numbers are my own derivations from raw evidence.*
