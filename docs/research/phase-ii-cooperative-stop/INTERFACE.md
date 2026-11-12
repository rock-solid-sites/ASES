# Cooperative stop on the existing owned-child interface

The existing force-kill operation remains unchanged. The new admin/profile-scoped request is strict:

```json
{"op":"local_stop_graceful","job_id":"…","launch_id":"…","stop_id":"…","grace_ms":500}
```

Only `grace_ms` from 1 through 2000 is accepted. `resource-session` exposes it as:

```text
resource-session SOCKET stop-graceful JOB LAUNCH STOP_ID GRACE_MS
```

The client uses the same bounded transport and no-retry behavior as its other one-shot operations. The request carries no PID, signal choice, executable, process identity, observation, timestamp, or environment. The existing SO_PEERCRED administrator grant and exact startup-profile scope check apply.

## Durable stop plan and resume

The existing single `local-stop:{job_id}` / `LOCAL_STOP_REQUESTED` event is reused. Legacy force-kill retains its exact payload shape `{ "launch_id":"…", "stop_id":"…" }`. Graceful stop stores exactly `{ "launch_id":"…", "stop_id":"…", "mode":"term_then_kill", "grace_ms":500 }`. Strict decoding accepts only these two payload shapes. Replay requires the same launch, stop ID, mode, and grace duration; a force/graceful mismatch, changed duration, malformed payload, or unknown field conflicts without another signal or event.

`local_resume.result.stop` preserves the existing event pointer and selector fields. For force-kill it remains `{event_id,kind,recorded_at,payload_sha256,launch_id,stop_id}`. For graceful stop it adds `mode:"term_then_kill"` and `grace_ms`. Resume validates the payload before returning it and remains within the existing 4 KiB outer result bound. `Store.resume_view` is unchanged.

## Response and effects

A completed response is:

```json
{"state":"exit_observed","job_id":"…","launch_id":"…","stop_id":"…","mode":"term_then_kill","grace_ms":500,"replayed":false,"term_attempted":true,"kill_attempted":false,"exit":{"code":0}}
```

If no retained Child is owned, or exact start evidence is unavailable, the response uses `state:"unknown"` and records no process result; it omits `term_attempted` and `kill_attempted` because cold durable state cannot prove what a lost runtime attempted. For an owned child, those booleans appear only when in-memory progress exists. `exit` is present only after actual wait evidence. `kill_attempted` distinguishes cooperative completion from SIGKILL escalation. The server commits the selected plan before signaling. It sends SIGTERM only to the retained unreaped Child, observes `try_wait` through the original monotonic deadline, then sends SIGKILL at most once if needed and waits/reaps. An already exited Child is observed without a signal. A repeated request continues the same in-memory plan, deadline, and attempted flags; it never resets the grace interval or repeats a signal.

Gateway restart discards Child ownership and monotonic progress. A cold exact replay can observe the durable plan but returns unknown and cannot signal or fabricate exit. Stop intent and exit observation do not finalize the job; only the separate explicit finalize operation releases capacity. The graceful interval is bounded, while final wait/reap and filesystem behavior are not a hard wall-time guarantee.
