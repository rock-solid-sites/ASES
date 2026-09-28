CONTINUATION. A prior run of this verification completed Steps 1-3 and wrote
them to `exp1/verification.md` (about 20KB). DO NOT REDO THEM. Steps 4, 5 and
the verdict are missing.

Work in /home/claude-code/projects/ASES/.worktrees/jev-phase1 (existing
worktree, branch research/jev-phase1-565).

## WRITE DISCIPLINE - MANDATORY
APPEND to `research/jev-bounded-judgment/phase2/exp1/verification.md`. Do not
rewrite or reorder Steps 1-3. Write Step 4 to disk, then Step 5, then the
verdict. Never announce a next step before the current one is on disk. If you
run long, write what you have and stop. Create no other file.

## STEP 4 - ADVERSARIAL JUDGEMENT

Argue from the numbers already in Step 1 of the file and from the raw records.
For each point give WHY / WHAT (the basis) / HOW CERTAIN (guess | evidence-based
| proven) / WHAT-NOT-TESTED.

1. Is "external gating dominates explicit unknown" actually supported, or does
   it depend on a favourable threshold choice? At tau=0.90 the gate reaches
   0.90 abstention on unanswerable while acting on 0.649 of answerable at
   accuracy 1.0000. Is that a USEFUL operating point, or is abstaining on
   ~35% of answerable cases and 90% of unanswerable ones close to vacuous?
   What would a practitioner actually gain?
2. Arm B never exceeds 0.20 detection on its own sweep and detection FALLS as
   theta rises (0.20 at theta<=0.60 down to 0.00 at theta>=0.80). Is that a
   real property of the model, or an artefact of sweeping that way? Does it
   mean arm B has no usable operating point at all, or that the argmax point
   (0.30) is simply better than any thresholded one?
3. Arm B's answerable accuracy 0.8596 EXCEEDS arm A's 0.8246. Step 1 found arm
   B fixes 3 of arm A's errors and introduces 1 new one. Is that a capability
   gain, a calibration artefact of a 3-way distribution partitioning
   probability mass differently, or noise at n=57? Would you defend claiming
   the explicit-unknown option IMPROVES accuracy?
4. Arm C's accuracy-when-acting is exactly 1.0000 at every tau, meaning every
   arm-A error has p(ground truth) < 0.50. How much should a reader trust
   perfect separation on n=57? Propose the cheapest test that would
   falsify it.
5. Is anything in the author's reported claim overstated or understated? Is a
   limitation missing? Consider specifically: representation fixed to `raw`;
   n=10 unanswerable, which is the denominator for the headline 0.30 vs 0.90;
   one corpus; one mechanism; the same corpus Phase 2 already used.
6. The headline 0.30 vs 0.90 rests on 3 detected vs 9 detected out of 10
   unanswerable cases. Is that difference large enough to be more than noise?
   Give the exact counts and say plainly how fragile it is.
7. Does the 0.30 detection result depend on the instruction wording? Step 3
   judged the wording sound. Is there a formulation that would plausibly change
   the result, and would testing it violate the frozen design?

## STEP 5 - INTEGRITY

- `git status`: clean except files you created. `harness/`, `frozen/`,
  `corpus/` unmodified from commit 16f64b37.
- `python3 ../harness/freeze.py verify --stage verifier` - report the result.
- `python3 ../harness/record_schema.py results/exp1_raw.ndjson` - report
  records and violations.
- `git diff 16f64b37 --stat -- ../harness ../frozen ../corpus` - should be
  empty or explained.
- No credential values anywhere in `exp1/`.
- Confirm `results/VOIDED-no-question-in-request.ndjson` is present and
  clearly quarantined, and state whether anything in the CURRENT results could
  still be contaminated by either reported harness defect.

## FINISH WITH

- **Verdict**: PASS / PASS WITH FINDINGS / FAIL, one line, with the single most
  important reason.
- **Limitations of this verification**: what you could not check and why.

## RULES
- APPEND to `research/jev-bounded-judgment/phase2/exp1/verification.md` only.
  No git commit, push or checkout.
- If the claim holds up, say so plainly. Do not manufacture findings and do
  not rubber-stamp.
