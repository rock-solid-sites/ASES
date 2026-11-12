# Legacy native regression after cooperative stop

The cooperative-stop change alters the shared local supervisor and client
transport path. The focused legacy native targets were rerun once after the
new cooperative native target passed. All five passed, **14/14 tests total**:

- `native_local_gateway`: 4/4, including the prior force-kill stop history,
  exact legacy `{launch_id, stop_id}` event payload, exit signal 9, and
  capacity held until explicit finalization.
- `native_local_cold`: 2/2, retaining unknown liveness and held capacity after
  gateway loss.
- `native_local_contention`: 3/3, preserving one dispatch owner and exact
  stop/replay behavior under competing gateways and a lost reply.
- `native_session_client`: 3/3, preserving legacy client selectors, hot/cold
  histories and server-error behavior.
- `native_session_drive`: 2/2, preserving the separate bounded driver's
  natural exit, nonzero, cold and lost-reply histories.

Raw per-target observations and the complete test log are retained in
[`evidence/legacy`](evidence/legacy). The tested source commit is recorded in
`evidence/legacy/source-commit.txt` as `aab258485b282c3b665e53623fe808dba048ea08`.
The exact command, working directory, shared target and reduced-debug
environment are in `evidence/legacy/command.txt`.

**WHY:** The new feature shares process ownership, stop-event replay and
response handling with the pre-existing force-kill path, so those established
histories must remain intact. **WHAT:** These are the five specified legacy
native targets; the result is 14 passes and zero failures. **HOW CERTAIN:**
Experimental for the recorded Linux source commit; captured logs and native
JSON observations support the result. **WHAT NOT TESTED:** This is not a full
suite, independent CI, a review, or a host-loss/hostile-process test. It does
not validate the new cooperative cases; those are separately owned and
reported with the new native test target.

The capture used source `aab258485b282c3b665e53623fe808dba048ea08`. A later
commit, `50e2e06b`, changes the new graceful helper's exit-observation
timestamp to use the time after grace/wait. This legacy run does not claim to
test that correction; the cooperative target receives a separate rerun.
