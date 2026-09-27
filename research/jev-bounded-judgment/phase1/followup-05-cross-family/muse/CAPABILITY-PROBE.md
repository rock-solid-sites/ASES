You are being evaluated on one narrow capability: can you independently
re-derive quantitative claims from raw evidence, without being told what the
answers are?

Work in: /home/claude-code/projects/ASES/.worktrees/jev-phase1
Do NOT read any file named COMPARISON.md, SMOKE.md, RECON.md, or anything in
out/band-*.json. Those contain someone else's conclusions and reading them
would defeat the test. Do not read findings.md section 6 either.

READ-ONLY. Do not write, edit, or delete any file. Do not run git commands that
change state. You may use shell tools to read and compute.

Your task, using the file:
  research/jev-bounded-judgment/phase1/followup-05-cross-family/staging/big-pickle/results/scored.ndjson

That file has one JSON object per line. Each has `case_id`, `mechanism`,
`answerable`, `correct`, `pred_label`, `usable`, `area`, `typed_error`, and
`abstained`. The mechanisms present are: prior, rule, lexical, jev, general_model.
`general_model` is the arm under test.

Derive and report ALL of the following, showing the command or method you used
for each. Do not guess. If something cannot be derived, say so explicitly.

1. How many lines total, and how many per mechanism.
2. For mechanism `general_model`: how many cells are `usable`, and how many have
   a non-null `typed_error`.
3. Considering ONLY cells where `answerable` is true: how many are there, how
   many have `correct` true, how many false. Give the accuracy as a fraction.
4. Over that same answerable set, compute the paired comparison between
   `general_model` and `jev`. Report three counts:
     b = general_model correct AND jev incorrect
     c = jev correct AND general_model incorrect
     ties = both correct or both incorrect
5. List the case_id of every answerable cell where general_model is incorrect.
6. For how many of the 14 unanswerable cases did `general_model` emit a
   `pred_label` (i.e. answered despite not being answerable)?
   And the same for `jev`?
7. List every case_id where the `general_model` label differs from the `jev`
   label, and for each state whether it is answerable.

Then state, in one line each:
- Does `general_model` produce the same correctness outcome as `jev` on every
  answerable case, or are there disagreements? Name the direction.
- Is there any answerable case where jev is right and general_model is wrong?

Be precise and terse. Numbers only, no editorialising.
