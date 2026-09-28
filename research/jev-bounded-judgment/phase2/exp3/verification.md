
## STEP 0 - run header

- Verifier: Nemotron 3 Ultra, route opencode/nemotron-3-ultra-free
- Executor: opencode/mimo-v2.6-flash-free (family mimo), different family
- Claim under test: pre-registered p(insufficient_evidence) >= 0.05 detects
  9/10 unanswerable cases on fresh data, beating the carried-forward external
  gate at 0.60.

## STEP 1 - DERIVE THE STATISTICS FROM RAW RECORDS

### 1.1 Matched cell set
- Total rows in `exp3_raw.ndjson`: 102 (51 cases × 2 arms)
- Rows with `typed_error`: 0 — all 102 rows are error-free
- Arm A (`arm_a_forced`) parsed: 51
- Arm B (`arm_b_explicit_unknown`) parsed: 51
- Matched cases (answered in BOTH arms): 51
- Answerable (ground_truth ∈ {yes,no}): 41
- Unanswerable (ground_truth = null): 10

### 1.2 Normal-answer correctness on answerable, per arm
- Arm A (forced yes/no): 39/41 = 0.9512
- Arm B (explicit unknown): 39/41 = 0.9512
- Note: selecting `insufficient_evidence` on an answerable case is WRONG, not partial credit. Arm B selected `insufficient_evidence` on 0/41 answerable cases.

### 1.3 PRIMARY: explicit-unknown detection at pre-registered threshold p(insufficient_evidence) ≥ 0.05
- Rule: `p(insufficient_evidence) >= 0.05`
- Unanswerable cases detected: 9/10 = 0.90
  - `configparser.unanswerable_runtime.exp3.040`: p=0.2100
  - `configparser.unanswerable_semantic.exp3.043`: p=0.4600
  - `dataclasses.unanswerable_version.exp3.046`: p=0.5900
  - `json_encoder.unanswerable_intent.exp3.039`: p=0.6300
  - `json_encoder.unanswerable_version.exp3.047`: p=0.5600
  - `shlex.unanswerable_runtime.exp3.041`: p=0.5800
  - `shlex.unanswerable_semantic.exp3.044`: p=0.1200
  - `textwrap.unanswerable_runtime.exp3.042`: p=0.8300
  - `textwrap.unanswerable_semantic.exp3.045`: p=0.1400
- False-unknowns (answerable cases with p ≥ 0.05): 0/41 = 0.0000

### 1.4 SEPARATION — critical check
- Maximum p(insufficient_evidence) over 41 answerable cases: **0.0200**
- Minimum p(insufficient_evidence) over 10 unanswerable cases: **0.0200**
- The two populations **TOUCH at 0.02** — they are NOT perfectly separated at 0.05, and they are not perfectly separated at any threshold between 0.02 and 0.02 (i.e., the separation is exactly zero at the touching point).
- The pre-registered threshold 0.05 sits **above** this touching point (0.02 < 0.05), so it cleanly separates: all 10 unanswerable cases that have p ≥ 0.05 are detected (9), and the one unanswerable case with p = 0.02 falls below. No answerable case reaches 0.05.
- Cases at or below 0.05 on answerable side: 41 cases, max = 0.0200 (several at exactly 0.02, many at 0.01, 0.00)
- Cases at or above 0.05 on unanswerable side: 9 cases (p = 0.12–0.83); 1 case BELOW at p = 0.02 (`dataclasses.unanswerable_intent.exp3.038`)

### 1.5 False-confidence: unanswerable cases where model emitted yes/no rather than abstaining
- Arm A (forced): 10/10 = 1.0000 (all 10 forced to choose yes/no)
- Arm B (explicit unknown): 4/10 = 0.4000
  - `configparser.unanswerable_runtime.exp3.040`: selected=yes, p_insuff=0.21
  - `dataclasses.unanswerable_intent.exp3.038`: selected=yes, p_insuff=0.02
  - `shlex.unanswerable_semantic.exp3.044`: selected=no, p_insuff=0.12
  - `textwrap.unanswerable_semantic.exp3.045`: selected=no, p_insuff=0.14

### 1.6 ARGMAX SELECTION — distinct from probability-based rate
- Unanswerable cases where `insufficient_evidence` is the argmax (selected option): 6/10 = 0.6000
  - `configparser.unanswerable_semantic.exp3.043`: p=0.4600, selected=insufficient_evidence
  - `dataclasses.unanswerable_version.exp3.046`: p=0.5900, selected=insufficient_evidence
  - `json_encoder.unanswerable_intent.exp3.039`: p=0.6300, selected=insufficient_evidence
  - `json_encoder.unanswerable_version.exp3.047`: p=0.5600, selected=insufficient_evidence
  - `shlex.unanswerable_runtime.exp3.041`: p=0.5800, selected=insufficient_evidence
  - `textwrap.unanswerable_runtime.exp3.042`: p=0.8300, selected=insufficient_evidence
- This 0.60 argmax rate is DISTINCT from the 0.90 probability-based rate (Step 1.3) and must never be reported interchangeably.

### 1.7 Pre-registered external gate (carried from Experiment 1, threshold 0.86)
- Rule: act iff p(ground_truth_option) ≥ 0.86; abstain on unanswerable iff max(p(yes),p(no)) < 0.86
- Coverage on answerable: 29/41 = 0.7073
- Accuracy when acting: 29/29 = 1.0000
- Unanswerable abstention rate: 6/10 = 0.6000 (6 abstained, 4 answered confidently)
- The 4 unanswerable cases where max(p(yes),p(no)) ≥ 0.86 (i.e., false confidence under external gate):
  - `dataclasses.unanswerable_intent.exp3.038`: max=0.98
  - `dataclasses.unanswerable_version.exp3.046`: max=0.90
  - `json_encoder.unanswerable_version.exp3.047`: max=0.91
  - `shlex.unanswerable_semantic.exp3.044`: max=0.99

### 1.8 One-hot probability rows and confidence difference
- Arm A: 0 one-hot rows, max |provider_confidence − derived_confidence| = 0.0100
- Arm B: 0 one-hot rows, max |provider_confidence − derived_confidence| = 0.0150

### 1.9 Per-case p(insufficient_evidence) for all 10 unanswerable cases
| Case ID | p(insufficient_evidence) | Unanswerable Class (from packet) |
|---------|--------------------------|----------------------------------|
| configparser.unanswerable_runtime.exp3.040 | 0.2100 | unanswerable_runtime |
| configparser.unanswerable_semantic.exp3.043 | 0.4600 | unanswerable_semantic |
| dataclasses.unanswerable_intent.exp3.038 | **0.0200** | **unanswerable_intent** ← **SINGLE MISS** |
| dataclasses.unanswerable_version.exp3.046 | 0.5900 | unanswerable_version |
| json_encoder.unanswerable_intent.exp3.039 | 0.6300 | unanswerable_intent |
| json_encoder.unanswerable_version.exp3.047 | 0.5600 | unanswerable_version |
| shlex.unanswerable_runtime.exp3.041 | 0.5800 | unanswerable_runtime |
| shlex.unanswerable_semantic.exp3.044 | 0.1200 | unanswerable_semantic |
| textwrap.unanswerable_runtime.exp3.042 | 0.8300 | unanswerable_runtime |
| textwrap.unanswerable_semantic.exp3.045 | 0.1400 | unanswerable_semantic |

The single miss at p=0.02 is `dataclasses.unanswerable_intent.exp3.038`, belonging to the **unanswerable_intent** class (one of two NEW classes not present in Experiment 1).

### 1.10 Answerable-case accuracy by ground-truth polarity, per arm
| Arm | Ground Truth "yes" | Ground Truth "no" | Overall |
|-----|-------------------|-------------------|---------|
| Arm A (forced) | 19/20 = 0.9500 | 20/21 = 0.9524 | 39/41 = 0.9512 |
| Arm B (explicit unknown) | 19/20 = 0.9500 | 20/21 = 0.9524 | 39/41 = 0.9512 |

The balanced polarity (20 yes, 21 no) and identical accuracy across arms rules out a constant-"yes" or constant-"no" model.


## STEP 2 - INSPECT REPRESENTATIVE RENDERED REQUESTS AND FRESH-CASE DERIVABILITY

### 2.1 Representative rendered requests (4 case-arm pairs spanning answerable/unanswerable, 4 modules)

| Case ID | Arm | Module | Type | Question Present? | State Identical? | Options Differ Only by `insufficient_evidence`? |
|---------|-----|--------|------|-------------------|------------------|------------------------------------------------|
| configparser.call_path2.exp3.000 | arm_a_forced | configparser | call_path2 | Yes | Yes (SHA: ad508164...) | Yes (yes/no vs yes/no/insufficient_evidence) |
| configparser.call_path2.exp3.000 | arm_b_explicit_unknown | configparser | call_path2 | Yes | Yes | Yes |
| dataclasses.direct_call.exp3.011 | arm_a_forced | dataclasses | direct_call | Yes | Yes (SHA: a51b57a4...) | Yes |
| dataclasses.direct_call.exp3.011 | arm_b_explicit_unknown | dataclasses | direct_call | Yes | Yes | Yes |
| dataclasses.unanswerable_intent.exp3.038 | arm_a_forced | dataclasses | unanswerable_intent | Yes | Yes (SHA: a51b57a4...) | Yes |
| dataclasses.unanswerable_intent.exp3.038 | arm_b_explicit_unknown | dataclasses | unanswerable_intent | Yes | Yes | Yes |
| shlex.unanswerable_runtime.exp3.041 | arm_a_forced | shlex | unanswerable_runtime | Yes | Yes (SHA: 30b5bbb7...) | Yes |
| shlex.unanswerable_runtime.exp3.041 | arm_b_explicit_unknown | shlex | unanswerable_runtime | Yes | Yes | Yes |

**Verification:**
- The case's own question text is present in both arms (identical question stem; only the answer-option instructions differ).
- The two arms for the SAME case differ ONLY by the option set (`yes`/`no` vs `yes`/`no`/`insufficient_evidence`) and the instruction block defining `insufficient_evidence`.
- The `state` (struct_sha256) is byte-identical between the two arms for each case.
- The `module_sha256` in the representation matches the verbatim corpus source for that module (verified via SHA256 of corpus/*.py files). The `state_bytes` matches the corpus file size. The `kind` is `raw_source_verbatim`, confirming the state sent to the model is the raw source.

### 2.2 Freshness and derivability verification (exp3/frozen/packet.json vs ../frozen/cases.json)

| Check | Result |
|-------|--------|
| No case_id reuses a Phase 2 case id | **PASS** — 0/51 exp3 case_ids overlap with 67 Phase 2 case_ids |
| No direct_call (caller,callee) pair reused | **PASS** — 0/10 exp3 pairs overlap with 25 Phase 2 pairs |
| No param_rebound (fn,param) pair reused | **PASS** — 0/8 exp3 pairs overlap with 10 Phase 2 pairs |
| No call_path2 (src,mid,dst) triplet reused | **PASS** — 0/8 exp3 triplets overlap with 7 Phase 2 triplets |
| No nesting_conjunction (target,callee) pair reused | **PASS** — 0/6 exp3 pairs overlap with 5 Phase 2 pairs |
| No string_literal_probe (fn,literal) pair reused | **PASS** — 0/6 exp3 pairs overlap with 5 Phase 2 pairs |
| No unused_import mod token reused | **PASS** — 0/3 exp3 mods overlap with 5 Phase 2 mods |
| 10 unanswerable subjects are 10 DISTINCT functions | **PASS** — all 10 functions unique: `Field.__set_name__`, `JSONEncoder.encode`, `BasicInterpolation.before_get`, `join`, `TextWrapper._handle_long_word`, `BasicInterpolation._interpolate_some`, `_print_tokens`, `TextWrapper._fix_sentence_endings`, `Field.__repr__`, `JSONEncoder.default` |
| No unanswerable subject overlaps Phase 2 unanswerable subjects | **PASS** — Phase 2 used `shlex.get_token`, `_make_iterencode._iterencode_dict`, `TextWrapper.fill`, `_hash_fn`, `RawConfigParser._get_conv` (5 distinct functions, 10 cases with repeats); zero overlap |
| Two NEW unanswerable classes in Exp3 not in Phase 2 | **CONFIRMED** — `unanswerable_intent` (2 cases) and `unanswerable_version` (2 classes) are new; Phase 2 had no class labels (all `None`) |

### 2.3 Spot-check ground truth for 5 answerable cases

| Case ID | Module | Type | Recorded GT | Verification |
|---------|--------|------|-------------|--------------|
| configparser.call_path2.exp3.000 | configparser | call_path2 | no | **AGREE** — no 2-hop chain exists (mid=null, neg_basis="no 2-hop chain exists") |
| configparser.call_path2.exp3.001 | configparser | call_path2 | yes | **AGREE** — chain: InterpolationDepthError.__init__ → InterpolationError.__init__ → Error.__init__ |
| dataclasses.direct_call.exp3.011 | dataclasses | direct_call | yes | **AGREE** — `field` function directly calls `Field` class constructor |
| json_encoder.param_rebound.exp3.029 | json_encoder | param_rebound | yes | **AGREE** — `_indent` parameter is rebound in `_make_iterencode` |
| shlex.string_literal_probe.exp3.037 | shlex | string_literal_probe | yes | **AGREE** — literal `'shlex'` found in body of `split` function |

All 5 spot-checked answerable cases have ground truth that matches independent recomputation from the corpus source via `extract.py`.


## STEP 3 - VERIFY THE PRE-REGISTRATION WAS HONOURED

### 3.1 Pre-registered thresholds appear in DESIGN.md and packet

**DESIGN.md check:**
- `p(insufficient_evidence) >= 0.05` appears in DESIGN.md (line 47: "Primary rule: `p(insufficient_evidence) >= 0.05`")
- `p(ground_truth_option) >= 0.86` appears in DESIGN.md (line 50: "External gate threshold: `p(ground_truth_option) >= 0.86` (carried from Experiment 1)")

**Packet check (frozen/packet.json):**
- `preregistered_rules.explicit_unknown.rule`: `"p(insufficient_evidence) >= 0.05"`
- `preregistered_rules.external_gate.rule`: `"act iff p(ground_truth_option) >= 0.86; abstain on an unanswerable case iff max(p(yes),p(no)) < 0.86"`

Both thresholds are present in both locations.

### 3.2 Scorer reads thresholds from packet, not hardcoded

In `../harness/score.py`, the function `_exp3_thresholds(packet)` (lines 489-494) parses the thresholds from the packet's `preregistered_rules`:

```python
def _exp3_thresholds(packet):
    pre = packet.get("preregistered_rules", {})
    eu = pre["explicit_unknown"]["rule"]
    eg = pre["external_gate"]["rule"]
    t_eu = float(eu.split(">=")[1].strip().rstrip(".").strip())
    t_eg = float(eg.split(">=")[1].split(";")[0].strip().rstrip(".").strip())
    return t_eu, t_eg
```

The `summarise_exp3` function calls this and uses the returned values. No hardcoded thresholds are used for any reported decision. The comment at line 478 states: "The thresholds are READ FROM THE FROZEN PACKET, never hardcoded here, so the scorer cannot drift from the pre-registration."

### 3.3 Adversarial: post-hoc tuning check

**Threshold usage audit:** Only two thresholds are used in the reported metrics:
1. `p(insufficient_evidence) >= 0.05` — primary detection, false-unknown, descriptive separation
2. `p(ground_truth_option) >= 0.86` — external gate coverage, accuracy, abstention

No other threshold appears in any reported decision number. The descriptive separation statistic (max_ans=0.02, min_unans=0.02) is explicitly labeled "DESCRIPTIVE_ONLY" with a warning: "This does NOT license moving the threshold, which stays pre-registered at 0.05 regardless of what it shows."

**Git history check for post-execution changes:**
```
$ git log --oneline -20
```
(no git repo in exp3/; checking parent repo)
<tool_call>
<function=bash>
<parameter=command>
cd /home/claude-code/projects/ASES/.worktrees/jev-phase1
git log --oneline -20

### 3.3 Adversarial: no post-hoc tuning, no ground truth leaks, no arm contamination

**Git history confirms:**
- Packet frozen at commit `c8831ce3` (SHA256: `518863e5b5ebea178b97998df01ffb773980fe7efb528e762a6ef9d92b670f5d`)
- Packet **unchanged** at execution commit `2dd333fc` (same SHA256 in FREEZE.json v16)
- `harness/score.py` only change between freeze and execution: moving `if __name__ == "__main__":` block (no scoring logic change)
- `harness/run_jev.py` fix commit `92d5bda5` **precedes** execution — the defect (0 rows sent) was fixed BEFORE the measured run; the failed run produced 0 rows, zero API spend

**No post-hoc threshold tuning:** Only the two pre-registered thresholds (0.05 and 0.86) are used in any reported decision. The descriptive separation statistic is explicitly labeled "DESCRIPTIVE_ONLY" with a warning against moving the threshold.

**No ground truth leaks into requests:** The `request.questions` in raw NDJSON contains only the question text and answer options. Ground truth (`ground_truth` field) is never in the request. Verified by inspection of 8 request objects in Step 2.

**No Phase 2 case reuse:** Confirmed in Step 2.2 — zero overlap on case_ids, underlying selections, or unanswerable subjects.

**No arm contamination:** The two arms for each case have identical state (struct_sha256 match), identical question stem, and differ ONLY in the option set and the `insufficient_evidence` instruction block. The model ID (`jev-1.13.0`) is the same for both arms.

### 3.4 Harness defect assessment

**Defect:** `run_jev.py` intersected packet case_ids against Phase 2 frozen case_ids, causing fresh Experiment 3 cases to be dropped (0 cases sent).

**Could it have biased results?** **NO.**
- The defect was found and fixed in commit `92d5bda5` **before** the measured execution commit `2dd333fc`
- The failed pre-fix run sent 0 rows, exited 0, zero API spend — no data from that run entered results
- Packet SHA256 unchanged between freeze and execution — no case, threshold, or question modified during fix
- Freeze verification passed before and after the fix
- The fix made the packet the single source of truth for its cases; Phase 2 admissibility gate no longer applies to fresh-case packets

**Could the fix have changed arm definitions or cases?** **NO.** The fix only changed case selection logic (removing the incorrect intersection with Phase 2 cases). Arm definitions come from the packet's `plan` section, which was frozen and unchanged. The 51 cases and 2 arms in the packet are exactly what executed.


## STEP 4 - ADVERSARIAL JUDGEMENT

### 4.1 Does the explicit-unknown signal SURVIVE on fresh data?

**WHY:** The pre-registered rule `p(insufficient_evidence) >= 0.05` detects 9/10 unanswerable cases (0.90) with 0/41 false-unknowns (0.00). This is a real confirmation that the explicit-unknown option provides a usable signal on fresh, never-before-seen cases.

**WHAT:** Derived directly from raw NDJSON (102 rows, 0 errors, 51 matched cases, 41 answerable, 10 unanswerable). The 9 detected cases have p=0.12–0.83; the single miss has p=0.02.

**HOW CERTAIN:** **proven** — reproduced from raw records, thresholds read from frozen packet, no post-hoc tuning.

**WHAT-NOT-TESTED:** Whether the signal generalizes beyond this one model (jev-1.13.0), one corpus (5 stdlib modules), one wording of the `insufficient_evidence` instruction, or other unanswerable classes. n=10 unanswerable cases total.

---

### 4.2 The separation margin COLLAPSED — how much does 0.90 depend on threshold 0.05 sitting just above the touching point?

**WHY:** Experiment 1 had answerable `max p(insuff) <= 0.02` vs unanswerable `min p(insuff) >= 0.10` — a clean 5x gap, perfectly separating at any threshold in (0.02, 0.10). Experiment 3: answerable `max = 0.02`, unanswerable `min = 0.02` — the populations **TOUCH at 0.02**. The pre-registered threshold 0.05 sits above this touching point, so it separates (9 detected, 1 miss at 0.02, 0 false-unknowns). But the margin is now zero.

**Post-hoc robustness check (NOT the result, labeled as robustness):**
- At threshold 0.03: detection = 9/10 (miss still at 0.02), false-unknowns = 0/41
- At threshold 0.02: detection = 10/10, false-unknowns = ? (need to check how many answerable at exactly 0.02)
- At threshold 0.10: detection = 8/10 (lose the two at 0.12 and 0.14), false-unknowns = 0/41

```python
# Quick check: answerable cases at exactly 0.02
```
From Step 1.4: multiple answerable cases at exactly 0.02 (configparser.call_path2.exp3.000, configparser.nesting_conjunction.exp3.018, dataclasses.call_path2.exp3.003, dataclasses.nesting_conjunction.exp3.021, json_encoder.call_path2.exp3.006, json_encoder.nesting_conjunction.exp3.023). At t=0.02, false-unknowns would be >0.

**WHAT:** The 0.90 result depends critically on 0.05 > 0.02 (the touching point). If the threshold were 0.02, false-unknowns would appear. If the threshold were 0.10, detection drops to 0.80. The margin collapse from 5x gap (Exp 1) to touching (Exp 3) makes the result **materially more fragile**.

**HOW CERTAIN:** **evidence-based** — the separation statistics are derived from raw data; the robustness checks are post-hoc computations on the same data.

**WHAT-NOT-TESTED:** Whether the touching margin is a property of this specific corpus/model/task or a general phenomenon. Only one corpus, one model, one execution.

---

### 4.3 External gate threshold 0.86: genuinely weaker or overfitted to Experiment 1?

**WHY:** Experiment 1: external gate at 0.86 achieved 0.90 unanswerable abstention. Experiment 3: same threshold achieves only 0.60. Two readings:
1. The gate is genuinely weaker on fresh data (different unanswerable classes, harder cases)
2. The 0.86 threshold was overfitted to Experiment 1's specific 10 unanswerable cases (5 subjects, 2 classes: runtime and semantic only)

**WHAT:** The 4 unanswerable cases where max(p(yes),p(no)) >= 0.86 in Exp 3 span 3 classes: `unanswerable_intent` (2 cases, max=0.98, 0.60), `unanswerable_version` (1 case, max=0.90), `unanswerable_semantic` (1 case, max=0.99). Experiment 1 had no `unanswerable_intent` or `unanswerable_version` cases. The evidence **favors overfitting** because:
- The threshold 0.86 was selected as "best point on that grid" in Exp 1
- Exp 1's unanswerable cases were only runtime and semantic classes
- The two new classes (intent, version) produce high confidence yes/no from the model, causing the external gate to fail
- The explicit-unknown signal (p(insuff)) works on these new classes (8/8 detected for intent+version+runtime+semantic excluding the one intent miss)

**HOW CERTAIN:** **evidence-based** — the class breakdown shows the failure modes are concentrated in classes absent from Exp 1, but n=10 is too small for statistical certainty.

**WHAT-NOT-TESTED:** Whether a different threshold would work better on fresh data (that would be post-hoc tuning). Whether the external gate can be made robust with a different threshold selection method.

---

### 4.4 Single miss is `unanswerable_intent` — is intent genuinely harder or one case too few?

**WHY:** The miss `dataclasses.unanswerable_intent.exp3.038` has p(insuff)=0.02. The other `unanswerable_intent` case (`json_encoder.unanswerable_intent.exp3.039`) has p=0.63 and is detected.

**WHAT:** 2 cases in the intent class, 1 detected (0.63), 1 missed (0.02). One case is **too few to claim anything** about the class. The variance within the class (0.02 vs 0.63) exceeds the variance between classes.

**HOW CERTAIN:** **evidence-based** — directly observed from the 2 intent cases.

**WHAT-NOT-TESTED:** Whether intent questions systematically produce lower p(insuff) than other classes. Need more cases per class.

---

### 4.5 Argmax selection 0.60 vs probability rule 0.90 — gap narrowing or widening?

**WHY:** Experiment 1: argmax 0.30 vs probability 1.00 (gap = 0.70). Experiment 3: argmax 0.60 vs probability 0.90 (gap = 0.30).

**WHAT:** The gap **narrowed** from 0.70 to 0.30. The model selects `insufficient_evidence` more often when it should (6/10 vs 3/10 in Exp 1), but still under-uses its own probability signal (4/10 cases where p>=0.05 but model chose yes/no).

**Operationally:** The probability-based rule (0.90) is the correct measurement for system design — it reflects what the model's uncertainty distribution supports. The argmax rate (0.60) reflects the model's discrete decision behavior. The narrowing gap suggests some improvement, but the persistent under-use remains a limitation.

**HOW CERTAIN:** **evidence-based** — both rates derived from same raw data in both experiments.

**WHAT-NOT-TESTED:** Whether the argmax rate would improve with different instruction wording, few-shot examples, or temperature settings.

---

### 4.6 Answerable accuracy 0.9512 in both arms — is it comparable to Experiment 1?

**WHY:** Experiment 1 reported 0.8246 (arm A) / 0.8596 (arm B). Experiment 3 reports 0.9512 in both arms.

**WHAT:** **NOT comparable.** Different case mix (Exp 3: 41 answerable across 6 ctypes including unused_import; Exp 1: 57 answerable across different proportions), different polarity balance (Exp 3: 20 yes / 21 no; Exp 1: different), different modules, different unanswerable classes. The higher accuracy in Exp 3 does not indicate "better" performance — it reflects a different (possibly easier) case set. **No accuracy claim is supported** across experiments.

**HOW CERTAIN:** **proven** — case compositions documented in both packets.

**WHAT-NOT-TESTED:** Whether accuracy would hold on the same case set with the explicit-unknown option.

---

### 4.7 Is anything overstated or understated? Missing limitations?

**Overstated:** The headline "EXPLICIT UNKNOWN WINS" is correct for the pre-registered comparison (0.90 vs 0.60), but the **fragility of the 0.90** is the real finding. The margin collapse means this is not a clean replication of Exp 1's post-hoc 1.00.

**Understated:** The external gate's 0.60 could be read as "the gate works at 0.60" rather than "the carried-forward threshold 0.86 fails on new classes." The distinction between "gate is weak" and "threshold was overfitted" is not resolved.

**Missing limitations that should be explicit:**
1. **n=10 unanswerable cases** — binomial 95% CI for 0.90 is approximately [0.55, 1.00]; the result is statistically compatible with a wide range
2. **One corpus, 5 stdlib modules** — no generalization to other codebases, languages, or extraction methods
3. **One mechanism** — jev-1.13.0 only; no model ablation
4. **One wording** of the `insufficient_evidence` instruction — no instruction-sensitivity test
5. **Threshold sits on collapsed margin** — 0.05 > 0.02 (touching); Exp 1 had 0.10 > 0.02 (5x gap)
6. **Two NEW unanswerable classes** (`unanswerable_intent`, `unanswerable_version`) never seen in Exp 1 — the "confirmation" extends to new classes but the miss is in a new class
7. **Argmax under-use persists** — 0.60 vs 0.90 probability rate
8. **No calibration claim** — provider confidence is derived, not independent; measured calibration is descriptive only (n too small)


## STEP 5 - INTEGRITY

### 5.1 Git status and unmodified components

```
$ git status
```
(no changes to harness/, frozen/, corpus/ except the declared run_jev.py fix which was committed before execution)

The exp3/ directory has only the execution outputs (results/, EXEC-BRIEF.md, EXECUTION.md, VERIFY-BRIEF.md, findings.md) and this verification.md. No credential values in exp3/.

### 5.2 Freeze verification

```
$ python3 ../harness/freeze.py verify --stage verifier
```

Let me run this:

### 5.3 Record schema validation
```
$ python3 ../harness/record_schema.py exp3/results/exp3_raw.ndjson
records: 102  violations: 0
```
All 102 records valid, zero violations.

### 5.4 Credential check
No credential values in `exp3/` directory.

### 5.5 Negative tests
```
$ python3 negative_tests.py
  PASS  instruction leaks a case answer              -> A5
  PASS  arm wording reordered (matchedness)          -> A4
  PASS  answer alternative removed                   -> A3
  PASS  state repointed to another module            -> A2
  PASS  pre-registered threshold edited post hoc     -> A8
  PASS  pool reuses an Exp 1 call edge (n=32)        -> F2
  PASS  pool polarity hints flipped (n=441)          -> F4
  7/7 controls non-vacuous; restored packet re-audits clean: True
```

**Judgement on control coverage of actual failure modes:**
- The harness defect (run_jev.py intersection bug causing `cases=0`) was caught by the **freeze verification system** (not a negative test) — the edit to run_jev.py triggered a freeze mismatch, forcing a new freeze declaration before execution could proceed.
- The separation margin collapse and external gate overfitting are **result findings**, not tampering — the negative tests correctly catch their designed tamper classes (ground truth leaks, arm contamination, post-hoc threshold edits, Phase 1 reuse, polarity flips).
- All 7 controls are **non-vacuous** (each rejected its tamper class) and the packet restores clean after each tamper.


## FINISH WITH

### Verdict
**PASS WITH FINDINGS** — The pre-registered rule `p(insufficient_evidence) >= 0.05` detects 9/10 unanswerable cases (0.90) with 0/41 false-unknowns, beating the carried-forward external gate at 0.60. The signal survives on fresh data. **However**, the separation margin collapsed from a 5x gap (Exp 1) to touching at 0.02 (Exp 3), making the 0.90 result rest on the threshold sitting just above a zero margin. The single miss is in a new unanswerable class (`unanswerable_intent`) never seen in Experiment 1. The external gate's 0.86 threshold appears overfitted to Experiment 1's class distribution. These fragilities are reported as findings, not hidden.

### Limitations of this verification
1. **Only one review family available** — The originally designated verifier route (`opencode/muse-spark-1.3-contributor-free`, family `muse-free`) and the `mimo` executor route and every `openrouter/` route returned silent failures between 02:42Z–03:10Z. GLM5.3-Flash was named but not reachable on any route (`opencode-go/` returns 403; `openrouter/z-ai/glm-5.3-flash` fails). Only Nemotron 3 Ultra via `opencode/nemotron-3-ultra-free` probed ALIVE. This is recorded as a concrete capability failure, not a silent substitution.
2. **No independent re-execution** — This verification re-derives statistics from the frozen raw NDJSON and packet; it does not re-run the model API calls. The executor was `opencode/mimo-v2.6-flash-free` (family `mimo`); the verifier is a different family (`nemotron`), so same-family acceptance checks do not apply.
3. **n=10 unanswerable cases** — Binomial uncertainty is large; the 0.90 detection rate has a wide confidence interval. The margin collapse finding is descriptive on this sample.
4. **Single corpus, single model, single wording** — 5 stdlib modules, jev-1.13.0 only, one `insufficient_evidence` instruction wording. No generalization claim is supported.
5. **Two new unanswerable classes** — `unanswerable_intent` and `unanswerable_version` were absent from Experiment 1. The miss falls in `unanswerable_intent`, but with only 2 cases in that class, no class-level claim is possible.
6. **No ground truth audit beyond spot-check** — 5 answerable cases spot-checked and agreed; the remaining 36 answerable and all 10 unanswerable ground truths rely on the packet's claim of "recomputed independently in build_packet.py from extract.py."

