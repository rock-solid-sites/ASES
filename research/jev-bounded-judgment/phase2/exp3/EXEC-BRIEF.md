You are executing a FROZEN, PRE-REGISTERED experiment. You did not design it
and you must not change it.

Work in this EXISTING git worktree (do not create another):
  /home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

All paths below are relative to
  research/jev-bounded-judgment/phase2/

## WHAT YOU MAY NOT DO

You are an EXECUTOR, not a designer. Forbidden without stopping and reporting:

- changing, re-tuning, replacing or supplementing the pre-registered
  thresholds (explicit-unknown `p(insufficient_evidence) >= 0.05`, external
  gate `p(ground_truth_option) >= 0.86`);
- adding, removing, renaming or re-ground-truthing any case;
- editing the scorer to change what is reported or how a measure is defined;
- interpreting the results, drawing conclusions, or writing findings;
- editing anything under `harness/`, `frozen/`, or `corpus/`;
- any git commit, push, checkout, or branch operation.

If a step cannot run as written, STOP, write the exact blocker to the progress
file, and report. Do not work around it. Do not improvise a substitute.

## ARTIFACT PATHS (concrete; write here, nowhere else)

- `exp3/EXECUTION.md`   -- progress log, APPENDED after each substep
- `exp3/results/exp3_raw.ndjson`  -- raw records
- `exp3/results/scored/`          -- scored output
- `exp3/results/verify.jsonl`, `exp3/results/verify.err` -- your run logs

## WRITE DISCIPLINE - MANDATORY

A prior verifier run completed its analysis and then stopped without writing a
file, losing all of it. Therefore:

1. APPEND each substep's real result to `exp3/EXECUTION.md` IMMEDIATELY after
   that substep completes, BEFORE starting the next one.
2. Never announce a next step before the current one is on disk.
3. Include the actual command, its real output, and exit status.
4. If you run long or get interrupted, stop with the completed state and the
   exact blocker written to disk. A partial log with real evidence is the goal;
   a complete chat summary with no file is a failure.

Start `exp3/EXECUTION.md` with a header recording: model, route, UTC start
time, the freeze version, and the two pre-registered thresholds you were given.

## SUBSTEP 1 - verify the freeze immediately before execution

```
python3 harness/freeze.py verify --stage pre-exp3
```

Record the full output. If it reports ANY mismatch, STOP: do not execute.

## SUBSTEP 2 - Phase B: execute the frozen packet

```
python3 harness/run_jev.py \\
  --out exp3/results/exp3_raw.ndjson \\
  --packet exp3/frozen/packet.json \\
  --conditions raw \\
  --arms arm_a_forced,arm_b_explicit_unknown
```

Expect: 102 rows planned and sent, a schema gate reporting 0 violations before
any send, and a post-run freeze verification. Record all of it.

If any row reports a `typed_error` other than `None`, record which case and
which error and CONTINUE - do not retry, do not edit anything, do not re-run
the packet to "fix" it. A failed row is data.

## SUBSTEP 3 - validate the raw records

```
python3 harness/record_schema.py exp3/results/exp3_raw.ndjson
```

Record record count and violation count.

## SUBSTEP 4 - verify the freeze immediately after execution

```
python3 harness/freeze.py verify --stage post-exp3
```

Record the output. A post-run mismatch means something changed during
execution: record it and stop, do not attempt repair.

## SUBSTEP 5 - score with the pre-registered thresholds

```
python3 harness/score.py \\
  --raw results/jev_raw.ndjson \\
  --outdir exp3/results/scored \\
  --exp3 exp3/results/exp3_raw.ndjson \\
  --exp3-packet exp3/frozen/packet.json
```

The scorer reads both thresholds from the frozen packet. Do not pass a
threshold, do not edit the scorer. Record the printed EXPERIMENT 3 block
verbatim.

## SUBSTEP 6 - credential scan of the material you produced

Scan `exp3/` for secret values: the value of `TYPESAFE_API_KEY` (it is in
`~/.secrets/typesafe.env`), plus generic `sk-` patterns and `nvapi-` strings.
Report file count scanned and hit count. Do not print any secret value, only
counts and file names.

## FINISH WITH

In `exp3/EXECUTION.md`, a final block titled `## EXECUTION COMPLETE` recording:
every substep's exit status, the row count, the violation count, both freeze
verdicts, the verbatim scored block, and the credential scan result.

In your final chat reply, give ONLY: each substep's status, the row and
violation counts, both freeze verdicts, and any blocker. Do NOT interpret the
results, do NOT say whether the signal held, do NOT recommend anything.
Interpretation is the author's job, and a separate independent verifier's.

## RULES

- Only the designated OpenCode route you were launched on. Do not invoke,
  propose, or fall back to any other model or provider.
- Do not modify frozen, harness, or corpus files.
- Do not commit, push, or change branches.
