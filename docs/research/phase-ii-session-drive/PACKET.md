# Bounded session driver over the native execution API

ASES-4 priority D continuation, stacked on draft #31 at 127fb9d0.
Reuse the actual `resource-session` client and gateway. The resource Store
remains the only durable job/intent/exit owner. No new scheduler, session
registry, process adoption, credentials, Kernel primitive or Work Unit model.

## Interface and authority

New Rust binary `resource-drive SOCKET JOB LAUNCH EXPECTED_CATALOG OUTCOME
BUDGET_MS`. IDs, revision and outcome follow the existing client rules. Budget
is 100..10000 ms, a bounded polling budget, not a termination guarantee.
`OUTCOME` is an explicit caller-selected semantic finalization decision, never
inferred from an exit code or equated to engineering-task correctness. The
invocation authorizes finalization with that outcome only after exact exit has
actually been observed. On budget exhaustion there is no automatic stop or
finalization; existing stop authority remains a separate explicit operation.

Invoke only the fixed sibling `resource-session` binary derived from this
binary's absolute current_exe directory, never a caller-selected executable or
shell. Preserve actual peer authority (same process UID) and existing profile
scope. Client output is bounded to its protocol; validate statuses/reply shape
and selected job/launch where supplied. Request selectors are literal args.
Do not reconstruct PID, process identity, observations or clocks.

## State machine

Issue at most one exact launch request per invocation. A running observation
permits bounded polling through the same API. A received `exit_observed`
permits exactly one explicit finalize with the preselected OUTCOME. Each
successful action and selected evidence remain with the existing Store.
There is never a launch retry, stop-on-timeout, or finalize retry inside the
driver. Server error, client outcome_unknown, unsupported reply, cold unknown
custody, or expired polling budget ends the invocation with a structured
non-success/recovery-needed result. No absence-of-effect assertion follows a
lost reply. A new invocation still passes through the same durable one-use
intent arbitration; it cannot acquire a second dispatch grant for that launch.

Use finite sleep intervals (<=100ms) and the existing bounded client transport.
A request in progress can exceed the remaining polling budget by at most the
client transport bound; report that limit explicitly rather than promising a
hard worker deadline. Launch/stop/finalize authority remains solely at the
actual gateway. No additional effect follows an unknown result.

## Required native histories

Use actual driver -> actual client -> actual gateway -> fixed owned child ->
exact observed exit -> explicit selected finalization. Verify one worker and
one launch intent, durable exit before finalize, capacity held until finalize.
Test a nonzero natural exit with an explicitly selected outcome (no guessed
semantic classification), budget exhaustion while child alive (held capacity,
no stop/finalize), and a fresh invocation after gateway loss (cold unknown,
no duplicate child or capacity release). Retain raw driver/client/server
outputs, actual events and worker counters, exact commands and source hashes.
A bounded dropping Unix proxy may test unknown driver outcome after actual
accepted launch; label it as a transport fixture and keep gateway truth separate.

WHY: turn the proven thin API into a bounded execution consumer that can run
without conversation reconstruction. WHAT: real existing intent, custody,
exit and finalization transitions. HOW CERTAIN: experimental until native
histories pass. WHAT NOT TESTED: remote providers, hostile same-UID code,
whole-host loss, arbitrary programs, hard wall-time quiescence, generalized
methodology automation or automatic repair of unknown outcomes.
