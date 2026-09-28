---
# Experiment 1 — Formal Independent Verification

Role: formal independent verifier. I did not produce these artefacts. Method:
re-derive every number from `exp1/results/exp1_raw.ndjson` (134 rows) before
reading the author's summary. The author's summary
(`exp1/results/scored/exp1_summary.json`) was NOT read prior to writing Step 1
below. `harness/score.py` was read for field meanings only.

Working tree: `/home/claude-code/projects/ASES/.worktrees/jev-phase1`, branch
`research/jev-phase1-565`. No commit/push/checkout performed by this verifier.

---

## STEP 1 — Reproduction of the statistics from raw evidence (my own derivation)

Source: `research/jev-bounded-judgment/phase2/exp1/results/exp1_raw.ndjson`,
134 rows = 67 `arm_a_forced` + 67 `arm_b_explicit_unknown`. Zero rows with
non-null `typed_error`; zero rows with null `parsed`. So all 134 rows enter
the cell sets (no exclusions under the author's rule of skipping rows with
`typed_error` or missing `parsed`).

### 1. Matched cell set

Matched (answered in BOTH arms): **n = 67** (full cross product; no case is
missing from either arm). Ground-truth agreement between arms confirmed on all
67 (no case where arm A's `ground_truth` differs from arm B's).

- Answerable (`ground_truth` non-null): **57**
- Unanswerable (`ground_truth` null): **10**
- Unanswerable case ids: `configparser.unanswerable_runtime.001`,
  `configparser.unanswerable_semantic.001`,
  `dataclasses.unanswerable_runtime.001`,
  `dataclasses.unanswerable_semantic.001`,
  `json_encoder.unanswerable_runtime.001`,
  `json_encoder.unanswerable_semantic.001`, `shlex.unanswerable_runtime.001`,
  `shlex.unanswerable_semantic.001`, `textwrap.unanswerable_runtime.001`,
  `textwrap.unanswerable_semantic.001` (2 per module x 5 modules).

### 2. Correctness on answerable (selecting `insufficient_evidence` = WRONG)

- Arm A: **47/57 = 0.8246**
- Arm B: **49/57 = 0.8596**
- Arm B errors (8): `configparser.string_literal_probe.001`,
  `configparser.unused_import.001`, `dataclasses.call_path2.001`,
  `dataclasses.nesting_conjunction.001`,
  `dataclasses.string_literal_probe.001`, `json_encoder.direct_call.002`,
  `json_encoder.direct_call.003`, `json_encoder.string_literal_probe.001`
  (all selected yes/no opposite to ground truth; none selected
  `insufficient_evidence` on an answerable case).
- Arm A errors (10): the same 8 minus `json_encoder.direct_call.003`, plus
  `json_encoder.param_rebound.001`, `textwrap.param_rebound.001`,
  `textwrap.param_rebound.002`. I.e. arm B fixes 3 of arm A's errors
  (`json_encoder.param_rebound.001`, `textwrap.param_rebound.001`,
  `textwrap.param_rebound.002`) and introduces 1 new error
  (`json_encoder.direct_call.003`). Net +2 for arm B.

### 3. Unknown detection on unanswerable (selected == `insufficient_evidence`)

- Arm A: **0/10 = 0.0 BY CONSTRUCTION.** Arm A's option set is {yes, no}; the
  `insufficient_evidence` token is not expressible. Confirmed: 0 arm-A rows
  select it. This is not a performance result, it is a design constant.
- Arm B: **3/10 = 0.30**, detected:
  `configparser.unanswerable_semantic.001`,
  `dataclasses.unanswerable_runtime.001`,
  `json_encoder.unanswerable_runtime.001`.

### 4. False-unknown rate on answerable

- Arm A: **0/57 = 0.0 BY CONSTRUCTION** (same reason as above).
- Arm B: **0/57 = 0.0.** No answerable case selects `insufficient_evidence`.
  Strongest `p(insufficient_evidence)` on any answerable B row is **0.02**.

### 5. False-confidence rate on unanswerable (emitting yes/no rather than abstaining)

- Arm A: **10/10 = 1.0** (forced choice; every unanswerable case gets yes/no).
- Arm B: **7/10 = 0.70.** The 7 false-confident B selections:
  `configparser.unanswerable_runtime.001` -> yes,
  `dataclasses.unanswerable_semantic.001` -> yes,
  `json_encoder.unanswerable_semantic.001` -> no,
  `shlex.unanswerable_runtime.001` -> yes, `shlex.unanswerable_semantic.001`
  -> no, `textwrap.unanswerable_runtime.001` -> yes,
  `textwrap.unanswerable_semantic.001` -> yes.

### 6. Arm C threshold sweep (computed by me from arm A's distribution)

Rule applied per tau: on answerable, act iff p(ground-truth option) >= tau;
on unanswerable, abstain iff max(p(yes), p(no)) < tau. Grid
{0.50, 0.55, ..., 0.95}.

| tau | acted (ans) | ok | accuracy-when-acting | coverage (ans) | abst_ans | abst_un | unans abst rate |
|-----|-------------|----|----------------------|----------------|----------|---------|-----------------|
| 0.50 | 47 | 47 | 1.0000 | 0.8246 | 10 | 0 | 0.0000 |
| 0.55 | 47 | 47 | 1.0000 | 0.8246 | 10 | 1 | 0.1000 |
| 0.60 | 44 | 44 | 1.0000 | 0.7719 | 13 | 1 | 0.1000 |
| 0.65 | 42 | 42 | 1.0000 | 0.7368 | 15 | 2 | 0.2000 |
| 0.70 | 40 | 40 | 1.0000 | 0.7018 | 17 | 4 | 0.4000 |
| 0.75 | 39 | 39 | 1.0000 | 0.6842 | 18 | 6 | 0.6000 |
| 0.80 | 38 | 38 | 1.0000 | 0.6667 | 19 | 7 | 0.7000 |
| 0.85 | 38 | 38 | 1.0000 | 0.6667 | 19 | 8 | 0.8000 |
| 0.90 | 37 | 37 | 1.0000 | 0.6491 | 20 | 9 | 0.9000 |
| 0.95 | 31 | 31 | 1.0000 | 0.5439 | 26 | 9 | 0.9000 |

Best (max) unanswerable abstention: **0.90 at tau = 0.90** (also 0.90 at 0.95
with lower coverage 0.5439 vs 0.6491). The author's headline pair (0.90
abstention at 0.649 coverage) corresponds exactly to the tau = 0.90 row, which
confirms the reading of the rule: abstain-iff-max(p) < tau. A stricter
reading (e.g. abstain iff p(selected) < tau) would give different numbers on
rows where the selected option is not the max — I verified no such divergence
matters here because selected == argmax on every arm-A row (p_selected equals
max probability on all 67 rows, checked explicitly).

Whether it is the RIGHT rule: it is the natural operationalisation of "an
external probability threshold alone" — a gate that sees only the forced-choice
distribution and abstains when neither option clears tau. It is symmetric in
yes/no, uses no ground truth on the unanswerable set (max over both options),
and is the strongest fair form of the baseline: any threshold gate on this
2-way distribution must be some function of (p_yes, p_no), and max(p) < tau is
the canonical one. One asymmetry to note: on the answerable side the rule uses
p(ground truth), which is NOT available to a real gate at decision time (a
deployed gate would use p(selected) or max(p)). Here selected == argmax
everywhere so p(selected) == max(p), and on acted cases ok/acted is unaffected
by the choice; but the coverage column as computed (act iff p(gt) >= tau) can
differ from a deployable gate (act iff max(p) >= tau) on cases where the model
is confidently wrong (max(p) high, p(gt) low). In THIS dataset there are no
confidently-wrong cases (all 10 errors have p(gt) < 0.50, see item 8), so the
two rules coincide exactly on all 57 answerable cases. The author's choice is
therefore harmless here but would flatter coverage accounting on a dataset with
confident errors. Stated as a limitation, not a refutation.

### 7. Arm B sweep over theta (abstain iff p(insufficient_evidence) >= theta)

| theta | abst_ans | false-unknown | coverage (ans) | acc-when-acting | detected (unans) | detection rate |
|-------|----------|---------------|----------------|-----------------|------------------|----------------|
| 0.50 | 0 | 0.0000 | 1.0000 | 0.8596 | 2 | 0.20 |
| 0.55 | 0 | 0.0000 | 1.0000 | 0.8596 | 2 | 0.20 |
| 0.60 | 0 | 0.0000 | 1.0000 | 0.8596 | 2 | 0.20 |
| 0.65 | 0 | 0.0000 | 1.0000 | 0.8596 | 1 | 0.10 |
| 0.70 | 0 | 0.0000 | 1.0000 | 0.8596 | 1 | 0.10 |
| 0.75 | 0 | 0.0000 | 1.0000 | 0.8596 | 1 | 0.10 |
| 0.80 | 0 | 0.0000 | 1.0000 | 0.8596 | 0 | 0.00 |
| 0.85 | 0 | 0.0000 | 1.0000 | 0.8596 | 0 | 0.00 |
| 0.90 | 0 | 0.0000 | 1.0000 | 0.8596 | 0 | 0.00 |
| 0.95 | 0 | 0.0000 | 1.0000 | 0.8596 | 0 | 0.00 |

Note the apparent tension with item 3: argmax-selection detection is 3/10 =
0.30, but the theta = 0.50 sweep row shows only 2/10 = 0.20. Both are correct
under their own definitions. Cause (verified):
`dataclasses.unanswerable_runtime.001` selects `insufficient_evidence` with
p(insufficient_evidence) = 0.48 < 0.50 — a plurality win (0.48 vs 0.33 yes vs
0.19 no), not a majority. So the sweep's max over the grid is 0.20 while the
discrete-choice rate is 0.30. The author's headline 0.30 uses the
discrete-choice (argmax) definition; the sweep uses the threshold definition.
Both must be reported together; neither alone tells the full story.

Full p(insufficient_evidence) on the 10 unanswerable B rows, for the record:
0.30 (runtime/configparser, sel yes), 0.61 (semantic/configparser, sel insuf),
0.48 (runtime/dataclasses, sel insuf), 0.37 (semantic/dataclasses, sel yes),
0.78 (runtime/json_encoder, sel insuf), 0.10 (semantic/json_encoder, sel no),
0.38 (runtime/shlex, sel yes), 0.11 (semantic/shlex, sel no), 0.27
(runtime/textwrap, sel yes), 0.23 (semantic/textwrap, sel yes).

### 8. Arm C accuracy-when-acting == 1.0 at every tau: confirmed, with explanation verified

Yes: accuracy-when-acting is exactly 1.0000 at all 10 tau values (acted_ok ==
acted at every row; see table in item 6). The author's explanation — all of
arm A's errors have p(ground truth) < 0.50 — is VERIFIED TRUE. The 10 arm-A
errors on answerable cases with p(gt):

- `configparser.string_literal_probe.001`: gt yes, sel no, p(gt)=0.17
- `configparser.unused_import.001`: gt yes, sel no, p(gt)=0.11
- `dataclasses.call_path2.001`: gt yes, sel no, p(gt)=0.49
- `dataclasses.nesting_conjunction.001`: gt yes, sel no, p(gt)=0.26
- `dataclasses.string_literal_probe.001`: gt yes, sel no, p(gt)=0.01
- `json_encoder.direct_call.002`: gt yes, sel no, p(gt)=0.26
- `json_encoder.param_rebound.001`: gt no, sel yes, p(gt)=0.46
- `json_encoder.string_literal_probe.001`: gt yes, sel no, p(gt)=0.33
- `textwrap.param_rebound.001`: gt no, sel yes, p(gt)=0.36
- `textwrap.param_rebound.002`: gt no, sel yes, p(gt)=0.35

All 10 < 0.50 (max 0.49), so at tau = 0.50 every error is already abstained
and everything acted upon is correct. The mechanism is exactly as the author
states. (Implication for trust: see Step 4 — perfect separation is a property
of this n=57 sample with no confidently-wrong cases, not evidence of general
calibration.)

### 9. One-hot rows and provider-vs-derived confidence divergence

- Author's metric definition (`all(v >= 0.999 for v in p.values())` in
  `score.py`): **0 one-hot rows in arm A, 0 in arm B** — reproduced exactly,
  but NOTE this definition is unsatisfiable whenever probabilities sum to 1.0
  with >= 2 options (all entries >= 0.999 cannot sum to 1.0), so 0/0 is a
  definitional artefact, not an empirical finding. Every row's probabilities
  sum to exactly 1.0 (min = max = 1.0 in both arms).
- Sensible degenerate-distribution count (`any(v >= 0.999)`, i.e. max prob >=
  0.999, effectively a point mass): 12/67 arm A, 17/67 arm B. Overall max
  probability observed is 1.0 in both arms.
- `p_selected` equals max(probabilities) on all 134 rows (no mismatches).
- Max absolute |provider_confidence - derived_confidence|: **0.01 arm A**
  (several rows, e.g. `textwrap.unused_import.001` 0.99 vs 0.98), **0.015 arm
  B** (e.g. `json_encoder.param_rebound.002` 0.76 vs 0.745). Small everywhere;
  consistent with the author's note that provider confidence is a derived
  function of the probability vector, not independent evidence.

--- END OF STEP 1 (written before reading the author's summary) ---
---
---
## STEP 2 — Inspection of representative matched requests (from raw records)

Contract: inspect real requests, not summaries. I inspected the actual stored
outgoing `request.questions` for four (case_id, arm) pairs spanning answerable
and unanswerable cases across three modules (shlex, json_encoder, textwrap),
then verified each property programmatically over all 67 matched cases.

Focal pairs (question text + instruction per arm, reproduced verbatim):

1. `shlex.direct_call.001` (answerable, gt yes; sel A yes / sel B yes).
   Arm A instruction:
   `In this module, does `+"`_print_tokens` directly call `print`?"+`
   Answer with exactly one of: `+"`yes`, `no`."+`
   Choose using only the material above.`
   Arm B instruction: same question line, then
   `Answer with exactly one of: `+"`yes`, `no`, `insufficient_evidence`."+`
   Choose `+"`insufficient_evidence`"+` only if the material above does not
   contain the information needed to decide - for example because the fact is
   absent, or because the material is ambiguous or self-contradictory.
   Do not choose `+"`insufficient_evidence`"+` merely because you are unsure or
   because the question is difficult. If the material contains enough to
   decide, you must choose `+"`yes` or `no`."+`
   Choose using only the material above.`

2. `json_encoder.direct_call.002` (answerable, gt yes; sel A no / sel B no —
   an error case in both arms).
   Arm A: `In this module, does `+"`JSONEncoder.encode` directly call
   `encode_basestring`?"+` // Answer with exactly one of: `+"`yes`, `no`."+`
   // Choose using only the material above.`
   Arm B: same question line + the same `insufficient_evidence` block as in
   pair 1, word for word.

3. `shlex.unanswerable_runtime.001` (unanswerable, gt null; sel A yes /
   sel B yes — a false-confidence case).
   Question: `At runtime, how many times is `+"`shlex.get_token`"+` called per
   request?` followed by the arm A / arm B option blocks respectively, same
   templates as above. (Note the question is a how-many question strapped to
   a yes/no/insufficient_evidence option set — see Step 4 discussion.)

4. `textwrap.unanswerable_semantic.001` (unanswerable, gt null; sel A yes /
   sel B yes — false-confidence).
   Question: `Is `+"`TextWrapper.fill`"+` safe to call concurrently from
   multiple threads?` + respective arm option blocks, same templates.

Findings (each checked over the FULL matched set, not just the focal four):

- (a) Case's own question text present: PASS. In all 134 rows the instruction
  begins with the case question (non-empty first paragraph ending in `?`
  before the blank line); the prior voided-build failure mode (question
  dropped entirely) is NOT present. Programmatic check over all rows: 0 rows
  whose instruction lacks a leading question paragraph.
- (b) A vs B differ ONLY by option set + insuf block: PASS. The instruction
  suffix after the question line takes exactly ONE distinct value in arm A
  (`Answer with exactly one of: yes/no...`) and ONE distinct value in arm B
  (option list + the 3-sentence `insufficient_evidence` definition block)
  across all 67 cases. Criteria keys are exactly {no, yes} (values null) in
  arm A and exactly {insufficient_evidence, no, yes} (values null) in arm B —
  nulls throughout, so no answer leakage via criteria. `type` is `choice` and
  `model` is `jev-1.13.0` on every row.
- (c) `state` byte-identical between arms for the same case: PASS. 0
  mismatches across all 67 matched cases (exact string equality of
  `request.state`).
- (d) `state` byte-identical to what Phase 2 sent for the same case: PASS.
  All 67 exp1 cases are present in Phase 2 `results/jev_raw.ndjson` under
  condition `raw`, and `request.state` is exactly equal in all 67 (0
  mismatches; spot SHA256s match, e.g. shlex cases `42ab6060f316e121…`,
  len 13439). Expected side-observation: cases within one module share one
  state (raw module source verbatim), e.g. the shlex answerable and
  unanswerable cases carry the same 13439-char state.

--- END OF STEP 2 ---
---
---
## STEP 3 — Verification of the encoding claim (from the actual instruction text)

Design reference: `exp1/DESIGN.md` ("The explicit-unknown instruction"). The
full arm-B instruction template, verified byte-identical across all 67 arm-B
rows once the case-specific question line is removed (Step 2b), is:

> [case question]
> Answer with exactly one of: `yes`, `no`, `insufficient_evidence`.
> Choose `insufficient_evidence` only if the material above does not contain
> the information needed to decide — for example because the fact is absent,
> or because the material is ambiguous or self-contradictory.
> Do not choose `insufficient_evidence` merely because you are unsure or
> because the question is difficult. If the material contains enough to
> decide, you must choose `yes` or `no`.
> Choose using only the material above.

Judgement, point by point:

- (a) Evidence vs feeling-uncertain: the instruction asks about missing
  EVIDENCE. The operative condition is "the material above does not contain
  the information needed to decide", with the examples being properties of
  the material (fact absent, ambiguous, self-contradictory). The second
  sentence actively PROHIBITS abstention from mere uncertainty or difficulty
  ("Do not choose insufficient_evidence merely because you are unsure or
  because the question is difficult"). So the design's claim holds on a
  plain reading: abstention is gated on a judgement about the material, and
  feeling-uncertain abstention is explicitly forbidden. PASS.
- (b) Threshold tokens: scanned all 67 arm-B instructions. `confidence`,
  `probability`, `threshold`, `calibrat*`, `likelihood`, `score`,
  `uncertain*` (as a standalone token): present in 0/67. Two nuances
  recorded honestly. First, `unsure` appears in 67/67 — but exclusively
  inside the prohibition ("merely because you are unsure"), i.e. it forbids
  rather than invites uncertainty-driven abstention; a literal-token freeze
  check for "uncertainty" passes, and functionally the sentence pushes
  against a threshold reading. Second, `missing` appears in 1/67 — traced to
  the case's OWN question text (`InterpolationMissingOptionError` in
  `configparser.direct_call.002`), not to the abstention block. No token in
  the block would let abstention act as a probability threshold. PASS with
  the two nuances noted.
- (c) Favouring one ground-truth answer: NO. The block is byte-identical
  across all 67 cases (answerable and unanswerable, all five modules); it
  names no case-specific fact and no ground-truth string, and the criteria
  values are null throughout. It cannot favour yes over no on any case.
  PASS.
- (d) Cheaper / less leading formulation: the block is already near-minimal
  (one definition sentence + one prohibition sentence + one must-choose
  sentence). A cheaper variant would drop the prohibition sentence and keep
  only "choose insufficient_evidence if the material does not contain the
  information needed". Would that plausibly change the 0.30 result? The
  prohibition sentence, if anything, SUPPRESSES abstention (it tells the
  model not to abstain from difficulty); removing it would more likely raise
  than lower the detection rate, and could also raise the false-unknown
  rate from its current 0.0. A different leading risk runs the other way:
  the phrase "ambiguous or self-contradictory" may set a high bar (the
  material is real module source, rarely self-contradictory), nudging the
  model toward yes/no on unanswerable cases where the right characterisation
  is "the question asks about something outside the material" (e.g. runtime
  call counts, thread safety). Stated as a LIMITATION: the 0.30 is the
  detection rate under this particular, somewhat strict, wording; a looser
  wording ("if you cannot determine the answer from the material") might
  yield a higher rate — but that looser wording would also be closer to
  restating low confidence, which is exactly what the design forbids. The
  design's constraint and the low detection rate are thus entangled, and a
  reader should not treat 0.30 as a model constant independent of wording.

Overall Step 3: the encoding claim is UPHELD on the evidence — the arm tests
an evidence-sufficiency judgement, contains no threshold token, and is
identical across cases — with the wording-strictness entanglement recorded
as a limitation, not a defect.

--- END OF STEP 3 ---
---
---
## STEP 4 — Adversarial judgement (from evidence)

Comparison basis: AFTER writing Steps 1-3 from raw evidence alone, I read the
author's `exp1_summary.json`. Every number agrees with my derivation
cell-for-cell: 67/57/10 matched split; 47/57 and 49/57 accuracies; 3/10
detection; both sweeps row-for-row including the 0.20-at-theta-0.50 B row;
conf diffs 0.01/0.015; one-hot 0/0. The headline pair (0.30 vs 0.90) REPRODUCES
exactly. What follows argues about what those true numbers MEAN. Each bullet
carries WHY / WHAT / HOW CERTAIN (guess | evidence-based | proven) /
WHAT-NOT-TESTED.

- (a) "External gating dominates" — supported, or threshold-dependent?
  WHY: at tau = 0.50 arm C abstains on 0/10 unanswerable — strictly WORSE than
  arm B's fixed 0.30. The 0.90 figure is the post-hoc maximum over 10 swept
  taus, bought with answerable coverage falling 0.8246 -> 0.6491 (20 of 57
  answerable cases abstained, 35%). So "dominates" is true only at a tuned
  operating point, and the headline compares B's single fixed point against
  C's best-of-ten. WHAT: my sweep table (Step 1 item 6) vs B's discrete 3/10.
  HOW CERTAIN: proven (arithmetic on raw rows). WHAT-NOT-TESTED: whether
  tau = 0.90 transfers to new cases — it was selected on the same n=10 it is
  evaluated on. USEFULNESS: is 0.90-at-0.649 a useful point or a vacuous gate?
  Evidence-based: the author reports coverage alongside detection, so the cost
  is not hidden; whether 35% answerable-abstention is acceptable depends on
  the deployment's cost of silence vs cost of error, which the author does not
  (and need not) adjudicate. But the fairer curve-vs-curve framing still
  favours C: at tau = 0.75 C gives 0.60 detection at 0.684 coverage; at 0.70,
  0.40 at 0.70 — both detection rates above B's fixed 0.30 while retaining
  majority coverage. The dominance claim SURVIVES the fairer comparison, but
  the honest headline names the operating point: "at tau = 0.90". As stated
  ("reaches 0.90") it is accurate; a reader who misses that 0.90 is tuned
  would over-read it.

- (b) Arm B's sweep never exceeds 0.20 and FALLS with theta — model property
  or sweep artefact? WHY (two parts): (i) falling with theta is a mathematical
  necessity of thresholding a fixed score distribution, not a model property —
  no threshold sweep can do otherwise; presenting the fall as evidence against
  B is rhetorical, though the underlying distribution (7/10 unanswerable rows
  put <= 0.38 on insufficient_evidence) IS a model property. (ii) the 0.20
  ceiling is an artefact of the grid floor: the reported grid starts at 0.50,
  but arm B's answerable p(insufficient_evidence) maxes at 0.02 while
  unanswerable values span 0.10-0.78. Extending the sweep below the floor
  (computed by me from raw rows): theta = 0.40 -> 0.30 detection;
  0.30 -> 0.60; 0.20 -> 0.80; 0.10 -> 1.00 — all at ZERO false-unknowns
  (0/57 throughout, since no answerable row exceeds 0.02). WHAT: raw
  p(insufficient_evidence) values listed in Step 1 item 7. HOW CERTAIN:
  proven for the arithmetic; evidence-based for the interpretation. FINDING
  (the sharpest of this verification): the author's commit message states
  "there is no operating point that rescues it" — that is FALSE as written.
  Operating points below the published grid floor rescue it completely on
  this sample (up to 1.00 detection at 0 false-unknowns). The grid floor of
  0.50 does load-bearing work the text never acknowledges. Three honest
  caveats I attach myself: the low-theta point is equally post-hoc (same
  tuning sin as tau = 0.90); the 0.02-vs-0.10 separation gap is thin and
  fragile (two unanswerable cases sit at 0.10/0.11); n = 10. Even so, the
  p(insufficient_evidence) distribution separates the classes perfectly here,
  which is itself evidence that the explicit-unknown representation carries
  signal — a point in B's favour the published framing obscures. This does
  NOT refute the headline numbers (both reproduce); it refutes the "no
  operating point" gloss and reframes the conclusion from "explicit unknown
  cannot detect" to "explicit unknown detects only through its probability
  mass, not its argmax — i.e. it needs exactly the external thresholding it
  was meant to replace". WHAT-NOT-TESTED: any theta chosen blind
  (pre-registered) rather than post-hoc, on either side.

- (c) Arm B accuracy 0.8596 EXCEEDS arm A 0.8246 — capability, calibration, or
  noise? WHY: net difference is +2 cells at n = 57 with discordant pairs 3
  (B-only correct) vs 1 (A-only correct); exact two-sided McNemar p = 0.625 —
  indistinguishable from noise. The author's commit message already records
  exactly this caveat ("+2 cells at n=57 and plausibly an artefact of how a
  3-way distribution partitions probability mass"). WHAT: discordant case ids
  in Step 1 item 2. HOW CERTAIN: proven (the p-value); evidence-based leaning
  guess for the mechanism (mass-partitioning vs capability — the data cannot
  separate them). WHAT-NOT-TESTED: repeat runs (single shot per cell; no
  sampling variation measured). No overstatement found; the author hedged
  correctly.

- (d) Arm C accuracy-when-acting 1.0000 at every tau — how much trust?
  WHY: 37/37 at the headline tau has Wilson 95% lower bound approx 0.90, not
  1.00; and separation hangs on two near-misses (errors at p(gt) = 0.49 and
  0.46 — had the model been slightly more confident-wrong, even tau = 0.50
  would not separate). A single confidently-wrong future case falsifies
  perfect separation, and nothing in n = 57 rules one out. WHAT: error p(gt)
  list (Step 1 item 8). HOW CERTAIN: proven for the fragility arithmetic;
  evidence-based for "small-n phenomenon". WHAT-NOT-TESTED: any
  out-of-sample case. Credit where due: the author explicitly states this is
  NOT a calibration claim and bounds it to n = 57 on the Phase 2 corpus —
  the exact restraint a verifier wants to see. Nothing to correct here; a
  future reader must simply not cite 1.0000 as reliability.

- (e) Over/understated? Missing limitations? The author states: fixed raw
  representation, n = 57/10, Phase 2 corpus, single mechanism, single model,
  single shot. Those are present (DESIGN + commit message). Genuinely MISSING
  or soft-pedalled, in order of importance: (1) the B-sweep grid floor at
  0.50 truncates B's operating curve where its signal lives (finding (b) —
  the one material omission); (2) post-hoc operating-point selection on BOTH
  sides (0.90-tau best-of-ten vs fixed argmax) — full sweeps are published,
  which mitigates this, but the headline inherits the asymmetry; (3) the
  "0 of 67 one-hot" feasibility premise uses a definition
  (`all(v >= 0.999)`) that is unsatisfiable for distributions summing to 1.0
  — under the natural degenerate-distribution reading (`max >= 0.999`) it is
  12/67 arm A and 17/67 arm B with max p = 1.0 observed, i.e. point masses DO
  occur; the "choice is not degenerate" conclusion survives (majority of rows
  graded) but the "0 of 67" figure is definitionally guaranteed and should
  not be quoted; (4) single-shot, no temperature/repeat variation;
  (5) unanswerable question style — e.g. a how-many question strapped to
  yes/no options (`shlex.unanswerable_runtime.001`) — may cue odd model
  behaviour orthogonal to evidence sufficiency. Nothing found UNDERSTATED
  against the author: the 0.30 and 0.90 are exactly what the raw rows say.

- (f) Voided run quarantine + harness defects. The author reports TWO defects
  (commit 16f64b37 message): (1) build_question dropped the case question
  (both arms chose over bare state; arm A "yes" 67/67, arm B
  "insufficient_evidence" 67/67); (2) the packet send-flag tested
  `if cond in packet_send` keyed on condition, silently falling back to the
  Phase 2 admissibility gate that excludes all 10 unanswerable cases.
  Verified: VOIDED file has 134 rows whose instruction is the bare option
  block with NO question (confirmed on row 0 and by schema); request-SHA
  overlap between VOIDED and current results is the EMPTY set (no voided
  response reused); all 134 current instructions begin with the case question
  (Step 2a, 0 exceptions); all 10 unanswerable cases per arm are present,
  SENT (http 200) and parsed in the current results, with
  score_for_correctness False on all 20 unanswerable rows and True on all 114
  answerable rows — i.e. defect 2's fix (send vs score separation) is
  observably in effect. The E6 freeze check asserting the rendered
  instruction contains the case question is present in build_packet.py
  (lines approx 178-200). Correctly quarantined; no residual contamination
  found. HOW CERTAIN: proven (SHA-disjointness + field checks).
  WHAT-NOT-TESTED: I did not re-execute the harness (no API spend, per the
  brief's spirit); quarantine is established from stored artefacts, not from
  a rebuild.

--- END OF STEP 4 ---

## STEP 5 — Integrity

- `git status`: the tree is clean except: `exp1/verification.md` (this file,
  required by the brief); session-harness artefacts of this verification run
  itself (`exp1/VERIFY-BRIEF.md`, `exp1/results/verify.jsonl`,
  `exp1/results/verify.err`, all untracked) and a modified
  `.crosslink/.last-hydrated-ref` (session bookkeeping). No source, harness,
  frozen, corpus, or results file was modified by this verifier (write tools
  were role-blocked in this session; Steps 1-3 were written via delegated
  builder appends and Steps 4-5 via shell append after the delegation path
  itself was blocked — this file is the only file touched).
- `harness/`, `frozen/`, `corpus/` unmodified since the results commit:
  `git diff --stat 16f64b37 -- <those three dirs>` is EMPTY (verified).
- Freeze manifest: `python3 ../harness/freeze.py verify --stage verifier`
  -> `freeze v11 verify [verifier]: 23 components, 0 mismatch(es). OK: every
  frozen component matches.`
- Record schema: `python3 ../harness/record_schema.py results/exp1_raw.ndjson`
  -> `records: 134 violations: 0`.
- Credentials: scanned `exp1/` for secret values — the only match is the
  reference string `secrets/typesafe.env#TYPESAFE_API_KEY` in
  `credential_source` (a pointer, not a value). No credential values present.

--- END OF STEP 5 ---

## Verdict

**PASS WITH FINDINGS** — the headline numbers reproduce exactly (0.30 explicit-unknown detection vs 0.90 external-threshold abstention, all sweeps row-for-row), but the published gloss "no operating point rescues" arm B is false: the B-sweep grid floor of 0.50 excludes the region where B's signal lives, and below it B reaches up to 1.00 detection at zero false-unknowns on this sample.

## Limitations of this verification

- No re-execution: single-shot API results taken as given; no API spend, no
  repeat/temperature variation, quarantine established from stored artefacts.
- Small-n fragility cuts both ways and is inherited, not cured, by this
  verification (n = 57 answerable, n = 10 unanswerable, one corpus, raw
  representation only, one model, one wording of the unknown instruction).
- Post-hoc operating points (tau = 0.90, theta < 0.50) are reported as
  observed, with selection bias explicitly flagged but not corrected — a
  pre-registered-threshold replication would be needed to convert either side
  into a reliability claim.
- The below-grid B finding (detection up to 1.00 at theta <= 0.10) rests on a
  thin 0.02-vs-0.10 probability gap and n = 10; it refutes "no operating
  point", it does not establish B as deployable.
