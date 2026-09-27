You are the FORMAL INDEPENDENT VERIFIER for Phase 2 of a research programme in
the EDASES/ASES methodology repository. You did not produce these artefacts. Your
verdict governs.

Work in this existing git worktree (already checked out; do NOT create another):
/home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Phase 2 directory (all paths relative to it):
research/jev-bounded-judgment/phase2/

## What Phase 2 claims

Question: does deterministic code structure materially improve the efficiency or
reliability of bounded semantic judgments? Subject: direct TypeSafe
`jev-1.13.0`. Representations: R1 raw source, R2 deterministic structure from
stdlib `ast`, plus irrelevant-context variants of both.

The headline claim to check hardest: **"structure's clear measurable benefit is
efficiency, not accuracy"** — efficiency gains are exact (1.92x smaller state,
1.49x fewer input tokens, 1.63x cheaper), while all four accuracy comparisons are
directionally positive for structure and NONE reach significance
(McNemar exact p = 0.6875, 0.0654, 0.1250, 1.0000).

## STEP 1 — REPRODUCE REPRESENTATIVE SOURCE->STRUCTURE TRANSFORMATIONS

You must verify the extraction itself, independently. Do NOT read
`findings/findings.md` or `harness/score.py` output before doing this.

For these six (module, function) pairs, read `corpus/<module>.py` and decide for
yourself what the structure SHOULD say, THEN compare to the extractor's output:

  (shlex.py,        shlex.__init__)
  (shlex.py,        split)
  (json_encoder.py, JSONEncoder.iterencode)
  (textwrap.py,     TextWrapper._wrap_chunks)
  (dataclasses.py,  dataclass)
  (configparser.py, RawConfigParser._read)

For each: parameter names in `def` order; names ASSIGNED in the body (`=`, `+=`,
`for x`, `with as x`, `except as x`, `:=`), excluding names merely read; maximum
control-flow nesting depth (new level: if / for / while / with / try / except
handler / nested def / nested class / match; the function itself does not count;
`else` adds no level); whether the body has a `try`; whether it has an explicit
`raise`; and the dotted names called directly in the body, EXCLUDING calls inside
a nested `def`/`class` body.

Get the extractor's view with:
  cd research/jev-bounded-judgment/phase2
  python3 -c "
import sys; sys.path.insert(0,'harness')
import extract, json
m=extract.load_module('corpus/shlex.py','shlex')
f=m.qualified_functions['shlex.__init__']
print(json.dumps({k:f[k] for k in ('params','assigned_locals','max_nesting','has_try','has_raise')},indent=1))
print('edges:',[e for e in m.call_edges if e[0]=='shlex.__init__'])"

**Write your Step 1 results into `verification.md` now, before doing anything
else.** Then continue.

Report every DISAGREEMENT with the line range you read and which reading you
believe and why. Report agreement just as explicitly. A verification that finds
nothing is not a verification; neither is one that manufactures faults.

## STEP 2 — REPRODUCE THE FINAL REPORTED STATISTICS

Re-derive every number in `findings/findings.md` from the raw evidence, without
trusting that document. Sources:
- `results/jev_raw.ndjson` (218 scored cells)
- `results/jev_unanswerable_obs.ndjson` (40 observation-only cells)
- `results/jev/metrics.json` and `results/jev/scored.ndjson`
- `frozen/cases.json` and `frozen/admissibility.json`
- `harness/*.py`

**Append your Step 2 table to `verification.md` as you complete it.**

Derive independently:
1. Per-condition n_admissible, accuracy, mean state bytes, mean input tokens,
   median/p95 latency, total cost.
2. The four paired comparisons and their EXACT McNemar p-values:
   raw vs struct (n=52), raw_ic vs struct_ic (n=52), raw vs raw_ic (n=57),
   struct vs struct_ic (n=52). Use the exact binomial test, not a normal
   approximation. The claim is that NONE reach p<0.05.
3. Accuracy by case type per condition (the 6x4 table).
4. The degradation-under-distraction counts: raw loses 4 gains 0; struct loses 1
   gains 2.
5. The lookup-vs-judgment split: `lookup_under_struct` n=25 gaining +4.0pp and
   `judgment_under_both` n=27 gaining +3.7pp. Verify the group assignment rule in
   `harness/score.py:case_group` is correct and that it does not drop or
   double-count cases.
6. Probability behaviour: mean/min/max noul per condition, count at exactly 0 or
   1 (claimed 0 everywhere), count near 0.5 (claimed raw 7/8, struct 3/5).
7. Unanswerable behaviour: 40/40 answered, 0 abstentions; `unanswerable_runtime`
   0 of 5 decided in every condition; `unanswerable_semantic` 2-3 of 5 decided.
8. Confirm no unanswerable cell was scored: every cell with
   `ground_truth is None` must have `correct is None`.

## STEP 3 — ADVERSARIAL JUDGEMENT

**Append Step 3 to `verification.md` as you go.**

This is the part that matters. For each, argue from evidence:

- Is "efficiency, not accuracy" the correct headline, or is it a way of
  under-claiming? Could the accuracy result be presented as showing structure
  helps, and is refusing to do so justified at n=52?
- Is the "no lookup concentration" reading sound? The claim is that gains are
  equal in both groups so trivialisation did not drive the result. With 6
  discordant cells total, is that defensible, or is it a non-result dressed as
  a finding? The document calls it a non-result — is that the right call?
- Is the robustness signal (raw 4-0 vs struct 1-2, p=0.125) being sold too
  strongly? Check the per-type claim that `nesting_conjunction` halves under raw
  (0.8 -> 0.4) while struct holds 0.8.
- Is the evidence-removal finding (string_literal_probe 0.40 raw, unanswerable
  struct) correctly characterised as structure HURTING? Could it be defended as
  a fair scoping decision instead?
- Is `unused_import` being worse under structure (0.6 vs 0.8) correctly called a
  cost rather than noise at n=5?
- Is the cost model right? $0.042/1M input, output free, sourced from followup-04
  dated 2026-09-26. Is treating that as valid today defensible, and is the
  1.63x cost ratio computed correctly?
- Is anything in `findings/findings.md` overstated, understated, or claimed
  beyond what the sample supports? Is any limitation missing?
- Are the limitations honest? Specifically: one mechanism only, whole-module
  representations only, 5 modules from one language, one distractor, no repeat
  measurement, template-generated questions over real code.
- Is the "smallest justified next experiment" actually the smallest? Does it
  avoid spending budget on questions this phase did not open?

## STEP 4 — INTEGRITY AND REPRODUCTION

- Confirm `git status` is clean except for files you created, and that
  `harness/`, `corpus/`, `frozen/` are unmodified from commit `ef4dc698`.
- Confirm the frozen digests in `frozen/MANIFEST.md` still match the files.
- Re-run `bash reproduce.sh` (offline tier) and confirm it reports
  `REPRODUCTION OK (tier 1)`.
- Scan `phase2/` for credential VALUES. Credentials live in
  `~/.local/share/opencode/auth.json` and `~/.secrets/typesafe.env`. A mention
  of the NAME `TYPESAFE_API_KEY` or a label like `auth.json#opencode-go` is
  acceptable; a key value is not.
- Confirm the `noul` answer was not silently coerced: state is the whole
  representation, one question per request, and no case had its state
  concatenated with another scenario.

## DELIVERABLE

Write `research/jev-bounded-judgment/phase2/verification.md` and nothing else.

Structure:
1. **Verdict**: PASS / PASS WITH FINDINGS / FAIL, one line, with the single most
   important reason.
2. **Step 1 table**: six pairs x fields, your reading vs the extractor's, with
   line references. Plus every disagreement argued.
3. **Step 2 table**: every derived statistic, YOUR number vs the document's.
4. **Step 3**: an argued answer to each question, each with WHY / WHAT / HOW
   CERTAIN (guess | evidence-based | proven) / WHAT-NOT-TESTED.
5. **Step 4**: integrity, reproduction and secret-scan results.
6. **Limitations of this verification**: what you could NOT check and why.

## THE WRITE DISCIPLINE — READ THIS FIRST, IT IS WHY TWO PRIOR RUNS FAILED

Two previous runs of this brief did all the analysis and then STOPPED at a
message like "now re-deriving the statistics", producing no file at all. That is
the single most likely outcome again, so:

1. **Write to disk as you go, not at the end.** Append your Step 1 results to
   `verification.md` IMMEDIATEATELY after finishing Step 1, before starting
   Step 2. Then append Step 2. Then append Step 3. A partial file is
   recoverable; a summary in chat is not.
2. **Never announce a next step before the current step is on disk.** If you
   find yourself writing "now I will...", stop and write the file first.
3. The file must exist and be non-empty when you stop, even if you only
   completed Step 1. Partial verified content beats a complete-looking summary.
4. Budget accordingly: if you sense you are running long, write what you have
   and stop. Do not abandon the file.

## RULES

- Create `verification.md` and nothing else. Do NOT edit `findings/findings.md`,
  `README.md`, `frozen/MANIFEST.md`, anything in `harness/`, `corpus/`,
  `results/`, or `tables/`. Do not run git commit, push or checkout.
- Do the Step 1 extraction check BEFORE reading any conclusion document. Reading
  findings.md first would anchor you and destroy the point of the exercise.
- Re-derive, do not trust. An unreproducible number is a FAIL for that claim.
- If everything holds up, say so plainly. Do not manufacture findings to look
  rigorous, and do not rubber-stamp.
- Write the full document with your actual numbers, not a summary. If you run
  out of room, prioritise Step 1 disagreements and Step 2 mismatches.
