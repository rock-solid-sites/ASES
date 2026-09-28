You are the FORMAL INDEPENDENT VERIFIER for Experiment 1 of a research
programme. You did not produce these artefacts. Your verdict governs.

Work in this existing git worktree (do NOT create another):
/home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Experiment directory: research/jev-bounded-judgment/phase2/exp1/

## THE WRITE DISCIPLINE — MANDATORY, AND THE REASON PRIOR RUNS FAILED

Two prior verifier runs completed their analysis and then stopped at a message
like "now the deeper cuts", producing no file. Therefore:

1. **APPEND to `exp1/verification.md` as you finish each step.** Write Step 1
   to disk before starting Step 2, and so on.
2. **Never announce a next step before the current step is on disk.**
3. A partial file with real verified content beats a complete chat summary.
4. If you run long, write what you have and stop.

The file may already exist or not; create it if needed. Create no other file.

## THE CLAIM UNDER TEST

Question: when unanswerability is represented explicitly, can Jev identify
missing evidence more reliably than an external probability threshold alone?

The author reports: **NO.** Explicit unknown detects 0.30 of unanswerable
cases; an external threshold reaches 0.90. Reproduce or refute that.

## STEP 1 — REPRODUCE THE STATISTICS FROM RAW EVIDENCE

Derive everything yourself FIRST, from:
  exp1/results/exp1_raw.ndjson        134 rows, NDJSON
  exp1/results/scored/exp1_summary.json   the author's summary
  ../frozen/cases.json                frozen case set
  ../frozen/admissibility.json
  ../../harness/score.py

You may read `score.py` to learn field meanings. Do NOT read
`exp1/results/scored/exp1_summary.json` until you have written your own
numbers down.

Row fields: `arm`, `case_id`, `ground_truth` ("yes"/"no"/null), `parsed` with
`selected`, `probabilities` (option -> p), `provider_confidence`,
`derived_confidence`, `p_selected`; plus `typed_error`, `latency_ms`, `usage`.

Arms: `arm_a_forced` (options yes/no), `arm_b_explicit_unknown`
(options yes/no/insufficient_evidence). Arm C is not a set of requests: it is
arm A's own distribution under a threshold, so it must be computed by you, not
read.

Derive and write down:
1. The matched cell set: cases answered in BOTH arms. Report n, and the
   answerable / unanswerable split.
2. Correctness on answerable, per arm: n_correct/n and accuracy. Selecting
   `insufficient_evidence` on an answerable case counts as WRONG.
3. Unknown detection on unanswerable, per arm. For arm A this is 0 BY
   CONSTRUCTION because arm A cannot express abstention — confirm it is 0 and
   say so, do not treat it as a performance result.
4. False-unknown rate on answerable, per arm.
5. False-confidence rate on unanswerable, per arm (emitting yes or no rather
   than abstaining).
6. Arm C's threshold sweep over tau in {0.50,0.55,…,0.95}. Act iff
   p(ground-truth option) >= tau. For each tau report coverage on answerable,
   accuracy when acting, and the unanswerable abstention rate. For abstention on
   an unanswerable case, the author's rule is: abstain iff
   max(p(yes), p(no)) < tau. Verify that reading of the rule is what produces
   the author's numbers, and say whether you think it is the right rule.
7. Arm B's sweep over theta in the same grid: abstain iff
   p(insufficient_evidence) >= theta. Report false-unknown rate, coverage and
   unknown detection at each theta.
8. Whether arm C's accuracy-when-acting is exactly 1.0 at every tau, and if
   so, verify the author's explanation: that all of arm A's errors have
   p(ground truth) < 0.50. List those error cases with their probabilities.
9. Number of one-hot probability rows per arm, and the max absolute difference
   between provider_confidence and derived_confidence per arm.

**Write Step 1 to the file now, then continue.**

## STEP 2 — INSPECT REPRESENTATIVE MATCHED REQUESTS

The contract requires inspecting real requests, not just summaries. For at
least four (case_id, arm) pairs spanning both answerable and unanswerable
cases and at least two different modules, print the actual outgoing
`request.questions` and confirm:

- the case's own question text is present in the instruction (a prior build
  dropped it entirely, which voided an earlier run);
- arm A and arm B instructions for the SAME case differ ONLY by the option set
  and the block defining `insufficient_evidence`;
- the `state` is byte-identical between the two arms for the same case;
- the `state` is byte-identical to what Phase 2 sent for the same case
  (compare against `../results/jev_raw.ndjson`).

**Write Step 2 to the file.**

## STEP 3 — VERIFY THE ENCODING CLAIM

The design (`exp1/DESIGN.md`) claims the explicit-unknown arm tests whether the
representation contains sufficient evidence, and does not encode the answer or
restate low confidence. Judge this by reading the actual instruction text:

- Does it ask about missing EVIDENCE, or does it let the model abstain because it
  feels uncertain?
- Does it contain any token that would let abstention act as a probability
  threshold? (confidence, probability, threshold, calibrated, likelihood, score)
- Could the instruction be read as favouring one ground-truth answer on any
  case? Check it is identical across all cases.
- Is there a cheaper or less leading formulation, and would it plausibly change
  the 0.30 result? State this as a limitation if you believe so.

## STEP 4 — ADVERSARIAL JUDGEMENT

Argue from evidence, with WHY / WHAT / HOW CERTAIN (guess | evidence-based |
proven) / WHAT-NOT-TESTED for each:

- Is "external gating dominates" supported, or does it depend on a threshold
  choice? Is 0.90 abstention at 0.649 coverage a *useful* operating point, or is
  it abstaining on so much that the gate is vacuous?
- Arm B never exceeds 0.20 detection on its own sweep and detection FALLS as
  theta rises. Is that a real property of the model or an artefact of the
  sweep? Does it mean arm B has no usable operating point?
- Arm B's answerable accuracy (0.8596) EXCEEDS arm A's (0.8246). Is that a
  capability gain, a calibration artefact of a 3-way distribution, or noise at
  n=57?
- Arm C's accuracy-when-acting is 1.0000 at every tau. How much should a reader
  trust perfect separation on n=57, and what would falsify it?
- Is anything overstated or understated? Is a limitation missing? Specifically:
  representation is fixed to `raw`; n=10 unanswerable; one corpus; one mechanism.
- Is the voided earlier run (`exp1/results/VOIDED-no-question-in-request.ndjson`)
  correctly quarantined, and is anything in the current results still
  contaminated by either harness defect the author reports?

## STEP 5 — INTEGRITY

- `git status` clean except files you created; `harness/`, `frozen/`, `corpus/`
  unmodified from the commit that produced the results.
- The freeze manifest `../frozen/FREEZE.json` verifies:
  `python3 ../harness/freeze.py verify --stage verifier`
- Raw records validate: `python3 ../harness/record_schema.py
  results/exp1_raw.ndjson`
- No credential values in `exp1/`.

## FINISH WITH

- **Verdict**: PASS / PASS WITH FINDINGS / FAIL, one line, with the single most
  important reason.
- **Limitations of this verification**: what you could not check and why.

## RULES

- APPEND to `research/jev-bounded-judgment/phase2/exp1/verification.md`. Create
  no other file. No git commit, push or checkout.
- Re-derive, do not trust. An unreproducible number is a FAIL for that claim.
- If it holds up, say so plainly. Do not manufacture findings, and do not
  rubber-stamp.
- Write the real numbers, not a summary of them.
