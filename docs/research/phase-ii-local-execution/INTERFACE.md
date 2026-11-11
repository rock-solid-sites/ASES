# Optional trusted local execution interface

Status: implementation interface for ASES-4 priority D. The optional local profile is loaded by the Linux `resource-gateway` at startup from a JSON file. Existing four-argument gateway invocation remains valid and preserves the existing protocol. A fifth absolute profile path enables local operations.

## Trusted profile

The profile is a single JSON object with exactly these fields (unknown fields are rejected):

```json
{
  "program": "/absolute/path/to/worker",
  "args": ["--fixed-mode"],
  "cwd": "/absolute/working/directory",
  "env": {"LANG": "C"},
  "account_id": "account-id",
  "project_id": "project-id",
  "environment_id": "environment-id"
}
```

`program` and `cwd` must be absolute. `args` are passed as literal arguments, without shell parsing. The child receives only the listed environment variables and null stdin/stdout/stderr. Children receive RLIMIT_CPU 5 seconds, RLIMIT_AS 256 MiB, RLIMIT_NOFILE 64, RLIMIT_CORE 0, and Linux `PR_SET_NO_NEW_PRIVS`. The profile scope must exactly match the selected job proposal. The gateway administrator is the profile trust boundary.

## Requests and responses

Every request is one JSON object with an `op` and operation-specific fields. Unknown request fields are rejected. `job_id` and `launch_id` select existing durable records; clients cannot provide a command, PID, process identity, observation, timestamp, or environment. The five `local_*` operations require the existing SO_PEERCRED policy to resolve the peer as `admin`; caller role grants are unchanged.

- `{"op":"local_launch","job_id":"…","launch_id":"…","expected_catalog":7}` consumes `Store.begin_launch`'s one-use dispatch grant, spawning at most once. Response `result` is `{ "state":"running"|"unknown", "job_id":"…", "launch_id":"…" }`. Replays never spawn; they refresh only a retained Child, and after gateway restart report `unknown`. A post-intent spawn error remains unknown with capacity held.
- `{"op":"local_poll","job_id":"…","launch_id":"…"}` checks only the retained child. Response `result` is `{ "state":"running"|"exit_observed"|"unknown", "job_id":"…", "launch_id":"…", "exit":null|{"code":0}|{"signal":15} }`. Poll may durably record exact wait evidence but never finalizes. Cold unknown has no adopted PID.
- `{"op":"local_stop","job_id":"…","launch_id":"…","stop_id":"…"}` durably records one launch-bound stop intent before signaling the retained child, then sends SIGKILL to the retained child, waits/reaps it, and records actual exit if the child is owned. Response `result` is `{ "state":"stop_requested"|"exit_observed"|"unknown", "job_id":"…", "launch_id":"…", "stop_id":"…" }`. Exact replay is idempotent; conflicting selectors have no effect. A cold gateway cannot signal an unowned process.
- `{"op":"local_resume","job_id":"…","launch_id":"…"}` returns the existing compact `resume_view` plus a bounded `result` (maximum 4 KiB) containing `resume_view` and `local_state` (`owned_child_unobserved`, `exit_observed`, or `unknown`) and optional retained stop pointer. Resume never launches, signals, or finalizes.
- `{"op":"local_finalize","job_id":"…","launch_id":"…","outcome":"completed"}` calls the existing explicit `Store.finalize` path. For intent-backed running jobs this remains blocked until exact launch exit evidence exists. The accepted outcomes are `completed`, `failed`, `cancelled`, and `interrupted`.

Successful replies use the gateway's existing `{ "ok": true, "result": ... }` shape. Errors use `{ "ok": false, "error": "..." }`. The profile is optional; when absent, all existing operations and behavior remain available unchanged.

## Evidence boundary

The in-process supervisor retains each spawned `std::process::Child`; it never reconstructs ownership from durable PIDs. Spawn success and exit/wait status are observed from that retained child and passed to the existing typed Store APIs. A post-intent spawn or observation failure leaves the durable job unresolved and capacity held. Local stop intent is persisted through the existing SQLite event owner before a signal is sent. The stop event is `local-stop:{job_id}` / `LOCAL_STOP_REQUESTED` with `{launch_id,stop_id}`; one exact request per job is durable and conflicting IDs fail. Stop intent is not exit evidence or semantic completion; only explicit finalize releases capacity. Controller restart yields unknown liveness and prohibits redispatch, signaling, or fabricated exit evidence.
