# Bounded native session driver interface

`resource-drive` is a fixed sibling-process wrapper around the existing `resource-session` client. It takes exactly:

```text
resource-drive SOCKET JOB LAUNCH EXPECTED_CATALOG OUTCOME BUDGET_MS
```

`SOCKET` must be an absolute Unix socket path within `sockaddr_un` limits. `JOB` and `LAUNCH` use the existing resource-session identifier syntax. `EXPECTED_CATALOG` is a nonnegative signed 64-bit integer. `OUTCOME` is exactly `completed`, `failed`, `cancelled`, or `interrupted`. `BUDGET_MS` is an integer from 100 through 10000; it bounds the poll loop after a successful launch response. It does not bound or cancel an in-flight client call.

The driver derives `resource-session` from the absolute directory of its own `current_exe`. It never accepts a client executable or invokes a shell. Each client call is a fresh subprocess using the exact existing client arguments. It launches once, then polls only while the response says `running`, sleeping at most 100 ms between polls. An `exit_observed` result from launch replay or poll permits exactly one finalize call with the caller-selected `OUTCOME`. Exit status never selects or changes that outcome.

## Stdout and exit status

Stdout contains exactly one JSON object. Stderr is reserved for process-runtime diagnostics and is empty for ordinary validation, recovery, and success responses.

- Exit **0** means finalized. Shape:

```json
{
  "ok": true,
  "outcome": "finalized",
  "job_id": "…",
  "launch_id": "…",
  "selected_outcome": "completed",
  "poll_count": 1,
  "launch_client_status": 0,
  "launch_response": {"ok": true, "result": {}},
  "exit_client_status": 0,
  "exit_observation": {"ok": true, "result": {"state": "exit_observed"}},
  "finalize_client_status": 0,
  "finalization": {"ok": true, "result": {"finalization": "CLOSED"}}
}
```

The three nested client replies are the exact parsed `resource-session` JSON replies. If launch itself reports `exit_observed`, it is included as `exit_observation` and `poll_count` is zero.

- Exit **2** means local input validation failed before invoking the client. Shape: `{"ok":false,"outcome":"invalid_input","error":"…"}`.
- Exit **3** means recovery is required. Shape:

```json
{
  "ok": false,
  "outcome": "recovery_needed",
  "reason": "budget_exhausted",
  "job_id": "…",
  "launch_id": "…",
  "selected_outcome": "completed",
  "last_action": "poll",
  "poll_count": 4,
  "client_status": 0,
  "client_reply": {"ok": true, "result": {"state": "running"}}
}
```

`client_status` and `client_reply` are null when no client process completed or no bounded valid reply was available. Defined reasons include `server_error`, `client_outcome_unknown`, `unsupported_reply`, `unknown_custody`, `budget_exhausted`, `client_call_timeout`, and `client_unavailable`. `last_action` is `launch`, `poll`, or `finalize`. A recovery result after finalize does not assert that capacity is still held: a lost finalize reply may follow a committed finalize. A fresh `resource-session resume` is the recovery path; the driver performs no retry.

The driver accepts client process status 0 only with `{ok:true,result:{…}}`, status 3 only with `{ok:false,error:string}`, status 4 only with `{ok:false,outcome:"outcome_unknown",error:string}`, and status 2 only with `{ok:false,outcome:"invalid_input",error:string}`. It validates bounded output, action-specific state/finalization fields, and any returned job/launch selectors. Any mismatch returns recovery-needed with `unsupported_reply`.

The existing client bounds connect/write/read transport and response size. An in-flight client operation can outlast the remaining poll budget by up to the driver's per-call client bound (8 seconds); a per-call timeout returns recovery-needed and is never retried. The driver never signals or stops the worker, infers a semantic outcome, invents observations, or reports absence of effect after uncertainty.
