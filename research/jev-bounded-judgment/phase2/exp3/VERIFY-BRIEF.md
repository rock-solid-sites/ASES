You are the FORMAL INDEPENDENT VERIFIER for Experiment 3. You did not produce
these artefacts. Your verdict governs.

Work in this EXISTING git worktree (do NOT create another):
  /home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Experiment directory: research/jev-bounded-judgment/phase2/exp3/

Provenance: the packet was selected and frozen by the author; execution was
performed by `opencode/mimo-v2.6-flash-free` (family `mimo`). You are Nemotron 3
Ultra, a different family from the executor, so same-family acceptance checks do
not apply.

ROUTE SUBSTITUTION, recorded openly
The originally designated verifier route (`opencode/muse-spark-1.3-contributor-free`,
family `muse-free`) became unreachable partway through this experiment: it, the
`mimo` executor route, and every `openrouter/` route returned silent failures on
repeated probes between 02:42Z and 03:10Z. The operator then named
GLM5.3-Flash and Nemotron 3 Ultra for review work. GLM5.3-Flash is NOT reachable
on any available route (`opencode-go/` returns 403 for want of a Go subscription;
`openrouter/z-ai/glm-5.3-flash` fails), so it could not be used. Nemotron 3
Ultra via `opencode/nemotron-3-ultra-free` probed ALIVE and is the verifier.
This is recorded as a concrete capability failure, not a silent substitution.
Judge the verification on its evidence, and note in your limitations that only
one review family was available.

## HOW TO WRITE - READ THIS FIRST, TWO PRIOR RUNS PRODUCED NO FILE

Your native `write` and `edit` tools are BLOCKED in this session by the worktree
plugin `orchestrator-guard.ts`, because this session's agent resolves to `build`
while the guard's allowlist is `{"builder"}` and no agent named `builder` exists
for `opencode run`. A prior verifier run on this experiment therefore completed a
521KB transcript and wrote NOTHING, losing all of it. Do not repeat that.

**Write with bash.** Bash is permitted by the guard and by the permission config.
Use heredoc appends, e.g.:

```bash
cd /home/claude-code/projects/ASES/.worktrees/jev-phase1/research/jev-bounded-judgment/phase2/exp3
cat >> verification.md <<'MDEOF'

## STEP 0 - run header

- Verifier: Nemotron 3 Ultra, route opencode/nemotron-3-ultra-free
- Executor: opencode/mimo-v2.6-flash-free (family mimo), different family
- Claim under test: pre-registered p(insufficient_evidence) >= 0.05 detects
  9/10 unanswerable cases on fresh data, beating the carried-forward external
  gate at 0.60.
MDEOF
```

**YOUR FIRST ACTION MUST BE TO CREATE THE FILE** with that header block, before
you analyse anything. Then append each step as it completes. If you are cut off
mid-run, a file with real verified content is the deliverable; a complete answer
in chat with no file is a FAILURE.

## WRITE DISCIPLINE - MANDATORY
1. Create `exp3/verification.md` FIRST, with the header, before any analysis.
2. **APPEND each step as you finish it.** Step 1 on disk before Step 2 begins.
3. Never announce a next step before the current one is on disk.
4. A partial file with real verified content beats a complete chat summary.
5. If you run long, write what you have and stop.
Create no file other than `exp3/verification.md`. No git commit/push/checkout.
Use bash heredocs for all writes, never the native write/edit tools.

## THE CLAIM UNDER TEST
Experiment 1 reported that an explicit-unknown option lets Jev identify missing
evidence, using a post-hoc threshold. Experiment 3 re-tests it on FRESH cases
with the rule FIXED BEFORE EXECUTION:
  `p(insufficient_evidence) >= 0.05`
Author reports: detection 9/10 = 0.90 on unanswerable, 0/41 false-unknowns,
beating the carried-forward external gate (6/10 = 0.60).
Reproduce or refute. Treat the separation margin as the most important thing to
check (see Step 1.4).

## STEP 1 - DERIVE THE STATISTICS FROM RAW RECORDS
Derive everything yourself FIRST from:
  exp3/results/exp3_raw.ndjson           102 rows = 51 cases x 2 arms
  exp3/frozen/packet.json                 the frozen packet, incl. preregistration
  ../frozen/cases.json                    the Phase 2 frozen 67
  ../../harness/score.py                  field meanings only
  exp3/results/scored/exp3_summary.json   the author's summary

Do NOT read `exp3_summary.json` before writing your own numbers down.
Row fields: `arm`, `case_id`, `ground_truth` ("yes"/"no"/null), `parsed` with
`selected` and `probabilities`; plus `typed_error`, `latency_ms`, `usage`.
Arms: `arm_a_forced` (yes/no), `arm_b_explicit_unknown`
(yes/no/insufficient_evidence).

Derive and write down:
1.1 Matched cell set: cases answered in BOTH arms. n, and answerable/unanswerable
    split. Confirm all 102 rows are error-free.
1.2 Normal-answer correctness on answerable, per arm. Selecting
    `insufficient_evidence` on an answerable case is WRONG, not partial credit.
1.3 PRIMARY: count unanswerable cases with p(insufficient_evidence) >= 0.05.
    Separately count answerable cases meeting the same bar (false-unknowns).
1.4 **SEPARATION, and check this carefully.** Report the maximum
    p(insufficient_evidence) over the 41 answerable cases and the minimum over
    the 10 unanswerable cases. State plainly whether the two populations are
    perfectly separated at 0.05, or whether they OVERLAP or TOUCH. The author
    claims max_answerable=0.02 and min_unanswerable=0.02, i.e. they touch at
    0.02 and are NOT perfectly separating. Verify or refute, and list every
    case at or below 0.05 and every case at or above.
1.5 False-confidence: per arm, count unanswerable cases where the model emitted
    `yes` or `no` rather than abstaining.
1.6 ARGMAX SELECTION, as a measurement DISTINCT from 1.3: count unanswerable
    cases where `insufficient_evidence` is the argmax. Report it separately and
    never as a substitute for the probability-based rate.
1.7 The pre-registered external gate on arm A: act iff
    p(ground_truth_option) >= 0.86; abstain on an unanswerable case iff
    max(p(yes),p(no)) < 0.86. Report unanswerable abstention rate, coverage on
    answerable, and accuracy-when-acting. The author claims 0.60, 0.7073 and
    1.0.
1.8 Number of one-hot probability rows per arm, and the max absolute difference
    between provider_confidence and derived_confidence.
1.9 The per-case p(insufficient_evidence) for all 10 unanswerable cases, and
    which unanswerable class the missed case belongs to. The author reports the
    single miss is `dataclasses.unanswerable_intent.exp3.038` at p=0.02.
1.10 Answerable-case accuracy by ground-truth polarity, per arm, so a constant
    "yes" model can be ruled in or out explicitly.

**Write Step 1 to the file, then continue.**

## STEP 2 - INSPECT REPRESENTATIVE RENDERED REQUESTS AND FRESH-CASE DERIVABILITY
From `exp3/results/exp3_raw.ndjson`, for at least four (case_id, arm) pairs
spanning answerable and unanswerable cases and at least two modules, print the
actual outgoing `request.questions` and confirm:
- the case's own question text is present;
- the two arms for the SAME case differ ONLY by the option set and the block
  defining `insufficient_evidence`;
- the `state` is byte-identical between the two arms for that case;
- the `state` equals the verbatim corpus source for that module (read
  `../corpus/<module>.py` and compare).

Then verify FRESHNESS and DERIVABILITY from `exp3/frozen/packet.json` against
`../frozen/cases.json`:
- no case_id reuses a Phase 2 case id;
- no underlying selection reuses a Phase 2 selection: check the (caller,callee)
  pairs for `direct_call`, the (fn,param) pairs for `param_rebound`, the import
  tokens for `unused_import`, the (target,callee) for `nesting_conjunction`,
  the string-literal probes, and the call paths;
- the 10 unanswerable subjects are 10 DISTINCT functions, and none is a
  Phase 2 unanswerable subject (Phase 2 used 5);
- spot-check ground truth for at least 5 answerable cases by reading the
  corpus source yourself and deciding whether the recorded yes/no is right.
  Say for each whether you agree.

**Write Step 2 to the file.**

## STEP 3 - VERIFY THE PRE-REGISTRATION WAS HONOURED
- Confirm `p(insufficient_evidence) >= 0.05` and `p(ground_truth_option) >= 0.86`
  appear in `exp3/DESIGN.md` and in the packet's `preregistered_rules`.
- Confirm the scorer reads the thresholds from the packet rather than
  hardcoding them, and that no reported decision uses any other threshold.
- ADVERSARIAL: look hard for post-hoc tuning. Specifically: does any reported
  number depend on a threshold other than the two pre-registered ones? Is the
  descriptive separation statistic used to justify a moved threshold? Was the
  scoring code changed after results existed? Check
  `git log --oneline` and `git diff` for changes to `harness/score.py`,
  `harness/run_jev.py` and the packet after execution, and report exactly what
  changed and when relative to execution.
- ADVERSARIAL: confirm no ground truth leaks into any request, no Phase 2 case
  is reused, and no arm contamination exists.
- Note that the executor hit a harness defect (`cases=0`, 0 rows sent, exit 0)
  which was then fixed. Judge whether that defect could have biased any result
  in either direction, and whether the fix could have changed the arm
  definitions or the cases.

## STEP 4 - ADVERSARIAL JUDGEMENT
For each, give WHY / WHAT / HOW CERTAIN (guess | evidence-based | proven) /
WHAT-NOT-TESTED:
- Does the explicit-unknown signal SURVIVE on fresh data? The pre-registered
  rule gives 0.90 detection at 0.00 false-unknowns. Is that a real
  confirmation, given Experiment 1's post-hoc rule gave 1.00?
- The separation margin COLLAPSED: Experiment 1 had answerable <= 0.02 against
  unanswerable >= 0.10, a clean 5x gap and perfectly separating. Here the two
  populations TOUCH at 0.02. How much does the 0.90 result depend on the
  threshold 0.05 sitting just above that touching point? Would 0.03 or 0.10
  change the answer? You MAY compute other thresholds to test robustness, but
  you must label them clearly as post-hoc robustness checks and NOT as the
  result.
- The external gate's carried-forward threshold 0.86 achieved only 0.60 here
  against 0.90 in Experiment 1. Is that evidence the external gate is
  genuinely weaker, or evidence that 0.86 was overfitted to Experiment 1? Both
  readings are possible; say which the evidence favours and why.
- The single miss is an `unanswerable_intent` case, one of two NEW unanswerable
  classes absent from Experiment 1. Is intent genuinely harder to recognise as
  unanswerable, or is one case too few to claim anything?
- Argmax selection is 0.60 against the probability rule's 0.90. Experiment 1
  showed 0.30 against 1.00. The model still under-uses its own signal. Is the
  gap narrowing or widening, and does it matter operationally?
- Answerable accuracy is 0.9512 in both arms here, against 0.8246/0.8596 in
  Experiment 1. Is that comparable? The case mix and polarity balance differ
  from Experiment 1. State whether any accuracy claim is supported.
- Is anything overstated or understated? Is a limitation missing? Consider
  specifically: n=10 unanswerable, one corpus, one mechanism, one wording, a
  threshold that now sits on a margin that has collapsed, and that
  `unanswerable_version`/`unanswerable_intent` are new classes never seen in
  Experiment 1.

## STEP 5 - INTEGRITY
- `git status` clean except files you created; `harness/`, `frozen/`, `corpus/`
  unmodified from the execution commit except the declared scorer fix.
- `python3 ../harness/freeze.py verify --stage verifier` - report the result.
- `python3 ../harness/record_schema.py exp3/results/exp3_raw.ndjson` - report
  records and violations.
- No credential values in `exp3/`.
- Confirm `exp3/negative_tests.json` reports 7/7 controls non-vacuous, and
  judge whether the controls cover the failure modes that actually occurred.

## FINISH WITH
- **Verdict**: PASS / PASS WITH FINDINGS / FAIL, one line, with the single most
  important reason.
- **Limitations of this verification**: what you could not check and why.

## RULES
- Re-derive, do not trust. An unreproducible number is a FAIL for that claim.
- If it holds up, say so plainly. Do not manufacture findings; do not
  rubber-stamp.
- Write the real numbers, not a summary of them.
