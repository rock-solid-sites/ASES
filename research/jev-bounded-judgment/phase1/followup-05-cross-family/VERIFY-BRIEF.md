You are the VERIFIER OF RECORD for a completed research experiment in the
EDASES/ASES methodology repository. You are independent of its author. Report
honestly, including if the work is wrong. A verification that rubber-stamps is
worse than no verification.

Work in this existing git worktree (already checked out; do NOT create another):
/home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Experiment directory (all paths relative to it):
research/jev-bounded-judgment/phase1/followup-05-cross-family/

Background: research/jev-bounded-judgment/phase1/PHASE1-VERDICT.md and ERRATA.md
for the prior phase. findings.md section 6 holds the pre-registered experiment
design and decision bands.

## Context

Phase 1 of a Jev (TypeSafe "System One") bounded-judgment evaluation is done.
The pre-registered next experiment was executed as followup-05.

A premise changed mid-flight: the Zen chat route began returning HTTP 403
FreeTierError for all free Zen models when called from a harness process, on
both available credentials and across four header variants. The models remain
reachable only from inside OpenCode. So arms were produced through an AGENT
ROUTE (`opencode run --format json`) rather than direct HTTP. That forfeits
byte-level request equivalence with the frozen followup-02 cells. The author
declared this and added a transport control (the `mimo` arm) to MEASURE the
effect rather than assert it.

Four arms were operator-selected. `longcat` failed (403, no Go entitlement).
`ling` scored 24/64. `big-pickle` and `mimo` each produced complete 64/64 grids
and were scored with the frozen harness.

## STEP 1 — INDEPENDENT DERIVATION (do this BEFORE reading any conclusion)

Do NOT read `COMPARISON.md` yet. Derive everything yourself from raw evidence.
Record your own numbers as you go.

Primary evidence:
- staging/big-pickle/results/scored.ndjson and metrics.json
- staging/mimo/results/scored.ndjson and metrics.json
- staging/*/results/baselines_raw.ndjson (the per-arm complete grids)
- out/answers-<arm>.ndjson (raw model answers as emitted)
- out/runlog-<arm>.json (per-chunk attempt/exit/validation log)
- out-chunk16-record/answers-big-pickle.ndjson (earlier chunk-16 run)
- ../followup-02-mimo-v2.6-flash/results/mimo_raw.ndjson (direct-HTTP baseline)
- ../followup-02-mimo-v2.6-flash/comparison.md and verification.md
- ../cases.ndjson (frozen corpus; sha256 must be 7dd4698f...f558c)
- ../../harness/score.py, run_baselines.py, common.py (frozen harness)

Derive and report:
1. For `big-pickle` and `mimo`: cells, usable, typed_error count, and accuracy
   over ANSWERABLE cases only (state your n).
2. Paired McNemar vs `jev` on that same answerable set: b (arm right, jev
   wrong), c (jev right, arm wrong), ties.
3. Which case(s) are errors per arm.
4. `big-pickle` vs `jev`: every case_id where labels differ, and for each
   whether answerable, its area, and its abstain_expected.
5. Transport control: label-by-label diff between followup-02's direct-HTTP
   mimo and followup-05's agent-routed mimo. Count flips, name them, compute
   accuracy for both.
6. Whether out-chunk16-record/answers-big-pickle.ndjson and
   out/answers-big-pickle.ndjson are identical.
7. Corpus integrity: sha256 of ../cases.ndjson, and whether staging/*/cases.ndjson
   matches it.
8. Reproducibility: re-run the frozen scorer yourself and confirm it reproduces
   without modification:
     cd ../../harness && python3 score.py --phase1-dir <abs>/staging/big-pickle --no-tables
   and the same for staging/mimo. Confirm 320/320 cells and unchanged
   scored.ndjson / metrics.json hashes. Confirm you modified no harness file.
9. `ling`: from out/runlog-ling.json and out/events-ling-0*.jsonl verify it
   collected 24/64, that chunks 03-07 exited 0, and that NO parseable
   {"case_id","content"} object exists in any text block. Quote its false
   NDJSON-compliance self-claim verbatim.
10. Ground-truth containment: inspect smoke/build_tasks.py and verify
    out/tasks-*.json contain no ground_truth, deciding_fact, difficulty_note,
    rationale or answerable field.
11. Re-derive the pre-registered band for big-pickle from the findings.md
    section 6 bands. State the band and the criterion that decides it.

## STEP 2 — ADJUDICATION

NOW read COMPARISON.md. Adjudicate each claim PASS / FAIL / PARTIALLY
SUPPORTED, citing YOUR number:

- C1. big-pickle 49/50 answerable = 0.980, b=0, c=0, ties=50.
- C2. big-pickle has 0 unusable cells and 0 typed errors over 64 cells.
- C3. big-pickle and jev produce the SAME label on all 50 answerable cases.
- C4. The sole big-pickle error is c-p4b, the known ground-truth defect (D2 F1 /
  PHASE1-VERDICT 1.3) not derivable from model-visible text.
- C5. big-pickle differs from jev on exactly 4 labels and ALL FOUR are
  unanswerable area-B cases with abstain_expected=true.
- C6. All three mechanisms emitted a label on 14/14 unanswerable cases.
- C7. Transport control: exactly 1 label flip in 64 between followup-02
    direct-HTTP mimo and followup-05 agent-routed mimo, favouring the agent
    route (48/50 -> 49/50).
- C8. That flipped cell c-p6a is the SAME single discordant cell that produced
    followup-02's c=1, half of that run's pre-registered refutation band.
    VERIFY CAREFULLY against followup-02 comparison.md and verification.md.
    This is the sharpest claim in the document and it may be wrong.
- C9. Pre-registered band for big-pickle is "Jev's tier UNSUPPORTED".
- C10. Programme-level verdict is INCONCLUSIVE by construction, because the
     two-arm agreement rule cannot be satisfied with one scorable cross-family
     arm.
- C11. longcat failed with non-retryable 403 "an active OpenCode Go
     subscription is required to use Go models".
- C12. The chunk-16 and chunk-8 big-pickle runs are byte-identical.

## STEP 3 — THE HARD PART: DOES THE AUTHOR OVERSTATE?

Re-derivation is arithmetic. Adversarial judgement is the actual job. Answer
each with evidence, not opinion:

- Is the c-p6a fragility argument (COMPARISON.md 5.1) sound, overstated, or
  wrong? Does transport instability of ONE cell really undermine a band that
  was met on accuracy AND c<=1? Consider that the band needed BOTH conditions.
- Was staging a per-arm grid a legitimate substitution of the `general_model`
  mechanism, or a quiet change of the instrument? Inspect smoke/stage_arm.py
  and decide. This determines whether followup-05 is comparable to followup-02
  at all.
- Is the author's refusal to write a prose parser for `ling` correct, or did it
  discard recoverable signal?
- Is the "four comparisons converge on a tie" argument in section 6 sound, or
  is it stacking non-independent evidence? followup-01 is the corpus-author
  family; followup-02 and followup-05-mimo are the SAME MODEL on two
  transports.
- Is anything in COMPARISON.md overstated relative to what n=50 supports?
- Is the claim that this does NOT overturn the followup-04 operational case
  accurate and correctly scoped?
- Are Q2, Q3, Q4, Q6 correctly listed as untouched? Is Q4 correctly called the
  binding limitation?

## STEP 4 — HARNESS CONTAMINATION AND SECRETS

- Confirm harness/score.py, run_baselines.py, common.py and cases.ndjson are
  byte-identical to committed state. Use `git status` and `git diff` (the
  experiment is committed through 6c9abf71).
- Confirm the author did not modify frozen harness code to accommodate the new
  arms.
- Scan followup-05-cross-family/ for credential VALUES. Credentials live in
  ~/.local/share/opencode/auth.json and ~/.secrets/typesafe.env. A mention of
  the NAME TYPESAFE_API_KEY or a label like auth.json#opencode-go is acceptable;
  a key value is not.

## Deliverable

Write your verdict to:
research/jev-bounded-judgment/phase1/followup-05-cross-family/verification.md

Structure:
1. Verdict: PASS / PASS WITH FINDINGS / FAIL, one line.
2. Independent derivation table: every Step-1 quantity with the value YOU
   computed. Do not quote the author's numbers as your own.
3. Claim table: C1-C12 with verdict, your number, author's number, and the
   artefact+field verified.
4. Material findings. For each: WHY / WHAT (basis) / HOW CERTAIN
   (guess | evidence-based | proven) / WHAT-NOT-TESTED.
5. Answers to every Step-3 question, argued from evidence.
6. Contamination check: git diff evidence and credential-scan result.
7. Limitations of this verification: what you could NOT check and why.

## Rules

- You are running as the `build` agent and you DO have write access. Your
  deliverable is `verification.md`. Write it. Do not ask for permission to
  write it, do not propose delegating the write to another agent or model, and
  do not stop short of delivering it — a prior run of this brief completed all
  the analysis and then failed to deliver the document, losing its draft.
  Write the file as your final action.
- You may create `verification.md` and nothing else. Do NOT edit COMPARISON.md,
  MUSE-PROBE.md, RECON.md, SMOKE.md, VERIFY-BRIEF.md, anything under smoke/,
  staging/ or out/, or anything in harness/. Do not run git commit, git push,
  or git checkout.
- Re-running `harness/score.py` rewrites `manifest.json` in each staging dir,
  changing only `git.commit` and `scoring.generated_utc`; `scored.ndjson` and
  `metrics.json` are pure functions and do not change. Verify that, then
  restore those two manifest files with
  `git checkout -- <staging>/big-pickle/results/manifest.json <staging>/mimo/results/manifest.json`
  so the tree is left clean. That single targeted restore is the only git write
  permitted, and it exists to undo your own side effect.
- Re-derive, do not trust. If a number in COMPARISON.md cannot be reproduced
  from raw evidence, that is a FAIL for that claim, not a documentation nit.
- Preserve negative results, including your own.
- If everything checks out, say so plainly. Do not manufacture findings to look
  rigorous. Equally, do not rubber-stamp.
- Quote raw output liberally. Numbers with provenance beat conclusions.
- Write the full document, not a summary. Include the actual numbers you
  derived, the actual case_ids, and your reasoning for every Step-3 judgement.
