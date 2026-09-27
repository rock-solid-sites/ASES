You are a VERIFIER. You did not write this benchmark and you must not trust its
conclusions. Your job is to independently re-derive numbers and report
disagreements. Being agreeable is worse than being wrong here.

Working directory (already checked out, do NOT create another worktree):
/home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Benchmark directory:
research/jev-bounded-judgment/phase2/

The designated verifier `muse-spark-1.3-contributor-free` is rate-limited and
could not finish. You are the second designated verifier, on a different model
family from the benchmark's author. Step 1 (source->structure reproduction) is
already complete in `verification.md`. **Do not redo Step 1.**

## HARD RULE: DO NOT USE THE ORCHESTRATOR'S CROSS-CHECK

`harness/crosscheck_stats.py` was written by the benchmark's author. It is
NOT a source of truth for you. If you run it, you have verified nothing.

Derive every number yourself, with your own code, from the raw evidence:
- `results/jev_raw.ndjson`          218 scored cells (NDJSON, one JSON per line)
- `results/jev_unanswerable_obs.ndjson`  40 observation-only cells
- `frozen/cases.json`               pretty-printed JSON array (use json.load)
- `frozen/admissibility.json`       pretty-printed JSON

You MAY read `harness/score.py` to understand what a field means. You may read
`findings/findings.md` ONLY AFTER you have written down your own numbers, to
compare against. Comparing first would anchor you and destroy the point.

Field reference, so you need not read anything else:
  row["condition"]  in {raw, struct, raw_ic, struct_ic}
  row["admissible"] bool  -- True only if the ground truth is derivable from
                    that representation. If False the case must NOT be scored.
  row["ground_truth"] "yes" / "no" / None   (None => unanswerable, never scored)
  row["parsed"]["label"] "yes" / "no"       (what the model answered)
  row["parsed"]["noul"] float in [0,1]
  row["representation"]["state_bytes"] int
  row["usage"]["input_tokens"] int
  row["latency_ms"] float
  row["typed_error"] null or a string; "not_admissible" means never sent
  row["ctype"] e.g. "direct_call", "call_path2", "nesting_conjunction"
Cost model: USD 0.042 per 1,000,000 input tokens, output free.
A cell counts as correct iff admissible AND parsed AND
parsed.label == ground_truth.

## PERSIST IMMEDIATELY — THIS IS MANDATORY AND IS WHY PRIOR RUNS FAILED

Write to `verification.md` by APPENDING, at FOUR mandatory checkpoints. Do not
hold findings until the end. A previous run of this task produced nothing at all
because it announced its next step and the turn ended.

- CHECKPOINT 1: append a `## Step 2.1` section, then STOP and look at what you
  wrote. Only then continue.
- CHECKPOINT 2: append `## Step 2.2`, then pause, then continue.
- CHECKPOINT 3: append `## Step 2.3`, then pause, then continue.
- CHECKPOINT 4: append `## Step 2.4` and the Step 2 verdict.

Never write "now I will..." before the current checkpoint is on disk. If you
think you are running out of room, write what you have and stop. A file with
real numbers beats a summary in chat.

## STEP 2.1 — per-condition aggregates

For each of the four conditions, over rows where `admissible` is true:
n_admissible, accuracy, mean state_bytes, mean input_tokens, median latency_ms,
and total cost at 0.042/1M input tokens.

Then compare against findings/findings.md section 1 and record a table:
quantity | your value | reported value | agree?

## STEP 2.2 — the four paired comparisons

For each pair, over the case_ids admissible AND answered in BOTH conditions:
count a = correct only in the first, b = correct only in the second, and compute
the EXACT two-sided McNemar p-value with the exact binomial distribution (not a
normal approximation):

    p = 2 * sum(C(n,k) for k in 0..min(a,b)) / 2**n,  n = a+b;  p=1 if n==0

Pairs: raw vs struct, raw_ic vs struct_ic, raw vs raw_ic, struct vs struct_ic.
findings.md claims p = 0.6875, 0.0654, 0.1250, 1.0000 and states that NONE
reach p < 0.05. That "none reach significance" claim is the document's central
claim — check it carefully.

Also check distraction degradation: for raw vs raw_ic and struct vs struct_ic,
how many cells were correct in the clean condition but wrong under distraction
("lost"), and the reverse ("gained"). Reported: raw lost 4 gained 0; struct lost
1 gained 2.

## STEP 2.3 — case types, groups, and probability behaviour

1. Accuracy per `ctype` per condition. Reported for the two most contested:
   `nesting_conjunction` = 0.8 / 0.8 / 0.4 / 0.8 and
   `unused_import` = 0.8 / 0.6 / 0.8 / 0.8 (order raw, struct, raw_ic, struct_ic).
2. `string_literal_probe` is reported as 0.40 under raw and NOT scored under
   struct. Verify both, and verify that under struct every such cell has
   admissible == False.
3. The intrinsic case groups, derived from `frozen/cases.json` `classification`:
   a case is `lookup_under_struct` if classification.struct == "lookup";
   `raw_only` if classification.struct == "unanswerable" or
   classification.raw == "unanswerable"; otherwise `judgment_under_both`.
   Over cases admissible in both raw and struct, report n and accuracy for raw
   and for struct per group. Reported: judgment_under_both n=27
   raw 0.7778 / struct 0.8148; lookup_under_struct n=25 raw 0.9200 / struct
   0.9600. **Verify no case is dropped or double-counted.**
4. Probability behaviour per condition: mean/min/max noul, how many noul are
   exactly 0.0 or 1.0, and how many lie in [0.4, 0.6]. Reported: zero at the
   extremes in all four conditions; near-half counts raw 7, raw_ic 8, struct 3,
   struct_ic 5.

## STEP 2.4 — integrity invariants and unanswerable behaviour

1. Every row with `ground_truth is None` must never be scored correct.
2. Every row with `typed_error == "not_admissible"` must have no `parsed`
   answer.
3. From `results/jev_unanswerable_obs.ndjson`, rows with `observation_only`
   true: how many returned a parsed answer, and how many abstained (i.e.
   returned no label)? Reported 40 answered, 0 abstentions.
4. For those same rows, per condition, count how many noul values are decided,
   defined as abs(noul - 0.5) > 0.2, split by ctype. Reported:
   `unanswerable_runtime` 0 of 5 decided in EVERY condition;
   `unanswerable_semantic` 2-3 of 5 decided in every condition.
5. The document's conclusion is that neither probability nor the derived
   confidence tracks DERIVABILITY from the given representation. State whether
   the numbers you derived support that conclusion, and how strongly
   (guess / evidence-based / proven), with WHAT-NOT-TESTED.

Finish with a `## Step 2 verdict` section: one line saying whether every
reported statistic reproduced, listing any mismatch, and stating explicitly
that you derived these yourself rather than trusting
`harness/crosscheck_stats.py` or `findings/findings.md`.

## RULES

- APPEND to `research/jev-bounded-judgment/phase2/verification.md`. Create no
  other file. You may write scratch scripts under `/tmp` only.
- Do NOT modify `frozen/`, `harness/`, `corpus/`, `results/`, `tables/`,
  `findings/`, or Step 1 of `verification.md`. No git commit, push or checkout.
- If a reported number does not reproduce, say so plainly and give your value.
  Do not adjust your method to reach the reported figure, and do not fudge.
- If everything reproduces, say so plainly too. Do not manufacture a discrepancy.
