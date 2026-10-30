# F2 hostile-fixture checkpoint - Agent C (in progress)

- Branch: `research/phase-i-hostile-fixtures-f2-20261029`
- Crosslink issue: #9
- Oracle baseline: `f2lib.py`, independent of Agent D
- Scope: T01 through T24 have explicit catalog records in `fixtures.json`; `COVERAGE.md` distinguishes partial traces, model-only executions, prepared-only traces, and blocked cases.
- Latest runner report: `results.json`: 42 executed abstract replays, 1 prepared-only trace (T05), 0 blocked fixture cases. This is not aggregate T01 through T24 passing evidence.

## Added artifacts

- `fixtures.json`: named initial states, event sequences, expected observations and assumptions for all T01 through T24, with selected fault mutations.
- `run_fixtures.py`: machine-checks oracle observations and mutation outcomes; prepared-only fixtures are not executed.
- `results.json`: raw observations, resulting modeled stores, mutation outcomes, and explicit execution scope.
- `COVERAGE.md`: trace-by-trace coverage, gaps, and limits.

## Verified

- `python3 -m py_compile f2lib.py run_fixtures.py`
- `python3 -m json.tool fixtures.json`
- Runner last reported 42 executed, 1 prepared-only, 0 blocked; 13 mutations discriminate intended faults.
- `git diff --check`

The executions are abstract reference-model replays only. No host/runtime, descriptor, concrete route, storage rollback, or ACL evidence is claimed. The T05 event sequence is prepared-only because retained OS handles and live CPU-only progress are outside the model.

## Remaining limitations

- No abstract fixture is blocked in the latest run; the six previously blocked checks were corrected only where inspection showed a runner/oracle defect against the frozen F2 condition.
- T05 remains prepared-only because actual retained OS handles, protected-route denial, and continuing CPU-only execution require an isolated runtime harness.
- Other trace families still have partial coverage and missing subcases listed in `COVERAGE.md`; 42 passing abstract histories are not aggregate T01-T24 acceptance.
- No concrete policy invalidation of already-open access, external sink contract, storage rollback resistance, or physical holder fencing was tested.

## Next operation

Review destructive-control coverage against the frozen F2 list and add remaining positive cases without reference to Agent D; assess which host-dependent traces can remain prepared-only. Keep host-dependent cases prepared-only until a suitable independent harness exists. Continue small commits and push only this branch; the previous provider HTTP 402 is not to be retried.
