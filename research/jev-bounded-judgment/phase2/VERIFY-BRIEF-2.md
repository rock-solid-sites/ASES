You are continuing a FORMAL INDEPENDENT VERIFICATION that is already partly on
disk. Step 1 is COMPLETE and written to `verification.md`. Do not redo it.

Working directory (already checked out, do NOT create another worktree):
/home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Phase 2 directory:
research/jev-bounded-judgment/phase2/

## State

`research/jev-bounded-judgment/phase2/verification.md` already contains a
complete Step 1: six (module, function) pairs checked by reading the corpus
source independently, then compared to the extractor. Conclusion recorded there:
6/6 confirmed correct, with the verifier's own first-pass readings corrected.
**Preserve all of it. Append to the file. Do not delete or rewrite Step 1.**

The previous run stopped after announcing it would re-derive the statistics.
That is the work you must now do.

## THE WRITE DISCIPLINE — THIS IS WHY THE PRIOR RUN STOPPED

The prior run ended at a message like "now the deeper cuts" with Steps 2-4
missing. So:

1. **APPEND to `verification.md` as you complete each step.** Do not hold
   everything until the end.
2. **Never announce a next step before the current step is on disk.** If you
   catch yourself writing "now I will...", write the file first.
3. If you are running long, write what you have and stop. A partial file with
   real verified content beats a complete-looking chat summary.
4. Prioritise in this order if you must truncate: **Step 2 statistics, then
   Step 3 adversarial judgement, then Step 4 integrity.**

## STEP 2 — REPRODUCE THE FINAL REPORTED STATISTICS (the required gate)

Re-derive from raw evidence, not from the prose. You may now read
`findings/findings.md` to know what to check, but derive every number yourself.

Sources:
- `results/jev_raw.ndjson` (218 scored cells)
- `results/jev_unanswerable_obs.ndjson` (40 observation-only cells)
- `results/jev/metrics.json`, `results/jev/scored.ndjson`
- `frozen/cases.json`, `frozen/admissibility.json`
- `harness/score.py`

Derive and tabulate YOUR value against the document's claim:

1. Per condition (`raw`, `raw_ic`, `struct`, `struct_ic`): n_admissible,
   accuracy, mean state bytes, mean input tokens, median and p95 latency, total
   cost.
2. The four paired comparisons with EXACT McNemar p-values (exact binomial, not
   a normal approximation):
     raw vs struct (n=52) claimed p=0.6875
     raw_ic vs struct_ic (n=52) claimed p=0.0654
     raw vs raw_ic (n=57) claimed p=0.1250
     struct vs struct_ic (n=52) claimed p=1.0000
   The document's central claim is that NONE reach p<0.05. Verify that.
3. Accuracy by case type per condition (the 6 x 4 table). Verify
   `nesting_conjunction` = 0.8 / 0.8 / 0.4 / 0.8 and
   `unused_import` = 0.8 / 0.6 / 0.8 / 0.8, and `string_literal_probe` = 0.40
   under raw and unanswerable under struct.
4. Distraction degradation counts: raw loses 4 / gains 0; struct loses 1 /
   gains 2.
5. The group split rule in `harness/score.py:case_group`. Verify
   `lookup_under_struct` n=25 and `judgment_under_both` n=27, that no case is
   dropped or double-counted, and that the claimed gains (+4.0pp and +3.7pp)
   follow.
6. Probability behaviour per condition: mean/min/max noul, count at exactly 0 or
   1 (claimed 0 everywhere), count with noul in [0.4, 0.6] (claimed raw 7,
   raw_ic 8, struct 3, struct_ic 5).
7. Unanswerable: 40/40 answered with 0 abstentions;
   `unanswerable_runtime` 0 of 5 decided in EVERY condition;
   `unanswerable_semantic` 2-3 of 5 decided.
8. **Confirm no unanswerable cell was scored**: every cell whose
   `ground_truth is None` must have `correct is None`, and every cell with
   `typed_error == "not_admissible"` must have no `parsed` answer.
9. Verify the cost arithmetic: $0.042 per 1M input tokens, output free, applied
   to the recorded `usage.input_tokens`. Check the 1.63x cost ratio.

## STEP 3 — ADVERSARIAL JUDGEMENT

Argue from evidence, not preference. For each, give WHY / WHAT / HOW CERTAIN
(guess | evidence-based | proven) / WHAT-NOT-TESTED:

- Is "efficiency, not accuracy" the right headline, or an under-claim? Could the
  accuracy result legitimately be presented as structure helping, and is
  refusing to do so justified at n=52?
- Is the no-lookup-concentration reading sound, given only 6 discordant cells
  in total? The document calls it a NON-RESULT. Is that the right call, or is
  it a non-result dressed as a finding?
- Is the robustness signal (raw 4-0 vs struct 1-2, p=0.125) oversold?
- Is the evidence-removal finding (string_literal_probe 0.40 raw, unanswerable
  struct) correctly characterised as structure HURTING, or is it fairly a
  scoping decision?
- Is `unused_import` worse under structure (0.6 vs 0.8) correctly called a cost
  rather than noise at n=5?
- Is anything overstated, understated, or claimed beyond the sample? Is any
  limitation missing from the document's section 9?
- Are the limitations honest: one mechanism, whole-module representations only,
  5 modules one language, one distractor, no repeat measurement,
  template-generated questions over real code?
- Is the proposed smallest next experiment actually the smallest, and does it
  avoid spending budget on questions this phase did not open?

## STEP 4 — INTEGRITY AND REPRODUCTION

- Confirm `harness/`, `corpus/`, `frozen/`, `results/` are unmodified from
  commit `ef4dc698` (use `git status` and `git diff`). The only new file should
  be `verification.md`.
- Confirm the frozen digests recorded in `frozen/MANIFEST.md` still match the
  files on disk.
- Re-run `bash reproduce.sh` and report whether it prints
  `REPRODUCTION OK (tier 1)`.
- Scan `phase2/` for credential VALUES. Credentials are in
  `~/.local/share/opencode/auth.json` and `~/.secrets/typesafe.env`. The NAME
  `TYPESAFE_API_KEY` or a label like `auth.json#opencode-go` is acceptable; a
  key value is not.
- Confirm the harness never concatenated two scenarios into one state, and that
  each request carried exactly one question.

## APPEND THIS AT THE END

- **Overall verdict**: PASS / PASS WITH FINDINGS / FAIL, one line, with the
  single most important reason.
- **Limitations of this verification**: what you could not check and why.

## RULES

- APPEND to `verification.md`. Create no other file. Do not edit
  `findings/findings.md`, `README.md`, `frozen/`, `harness/`, `corpus/`,
  `results/`, or `tables/`. Do not run git commit, push or checkout.
- Re-derive, do not trust. An unreproducible number is a FAIL for that claim.
- If everything holds, say so plainly. Do not manufacture findings, and do not
  rubber-stamp.
