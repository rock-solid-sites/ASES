# F2 hostile-fixture checkpoint - Agent C (in progress)

- Branch: `research/phase-i-hostile-fixtures-f2-20261029`
- Crosslink issue: #9
- Oracle baseline: `f2lib.py`, independent of Agent D
- Scope: T01 through T24 have explicit catalog records in `fixtures.json`; `COVERAGE.md` distinguishes partial traces, model-only executions, prepared-only traces, and blocked cases.
- Latest runner report: `results.json`: 40 executed abstract replays, 1 prepared-only trace (T05), 2 blocked fixture cases. This is not aggregate T01 through T24 passing evidence.

## Added artifacts

- `fixtures.json`: named initial states, event sequences, expected observations and assumptions for all T01 through T24, with selected fault mutations.
- `run_fixtures.py`: machine-checks oracle observations and mutation outcomes; prepared-only fixtures are not executed.
- `results.json`: raw observations, resulting modeled stores, mutation outcomes, and explicit execution scope.
- `COVERAGE.md`: trace-by-trace coverage, gaps, and limits.

## Verified

- `python3 -m py_compile f2lib.py run_fixtures.py`
- `python3 -m json.tool fixtures.json`
- Runner last reported 40 executed, 1 prepared-only, 2 blocked; 11 mutations discriminate intended faults.
- `git diff --check`

The executions are abstract reference-model replays only. No host/runtime, descriptor, concrete route, storage rollback, or ACL evidence is claimed. The T05 event sequence is prepared-only because retained OS handles and live CPU-only progress are outside the model.

## Blocked outcomes requiring follow-up

- T24: ordered post-revocation use and out-of-band policy consistency observations fail their expected checks.

T01-T04, T06-T23 contain selected passing model histories; coverage is not complete within those traces (see matrix).

## Next operation

Debug the two blocked T24 ACL observations without reference to Agent D, add remaining destructive mutations and positive controls, then run supported lightweight cases. Keep host-dependent cases prepared-only until a suitable independent harness exists. Continue small commits and push only this branch; the previous provider HTTP 402 is not to be retried.
