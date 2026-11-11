# Fresh-session `resource-session` client

`resource-control/src/bin/resource-session.rs` is a thin Rust client for the optional trusted local gateway. Each invocation performs one operation over one Unix socket connection. The OS peer UID and gateway policy supply authority; the client has no database access and accepts no executable, PID, process identity, observation, timestamp, environment, or retry control.

## Command forms

```text
resource-session SOCKET resume JOB LAUNCH
resource-session SOCKET launch JOB LAUNCH EXPECTED_CATALOG
resource-session SOCKET poll JOB LAUNCH
resource-session SOCKET stop JOB LAUNCH STOP_ID
resource-session SOCKET finalize JOB LAUNCH OUTCOME
```

The socket path must be absolute and fit Linux `sockaddr_un`. IDs use the gateway's existing restricted 160-byte identifier alphabet. Launch catalog revisions must be nonnegative integers. Finalize outcomes are `completed`, `failed`, `cancelled`, and `interrupted`. Invalid CLI input is rejected before connecting.

The client emits only the exact existing `local_*` request fields and closes its write half after sending. Connect, read, and write are bounded; responses are capped at 8 KiB. There is no reconnect or automatic retry. Successful gateway JSON replies are passed through to stdout with exit status 0. A received `{ "ok": false, ... }` server reply is also passed through unchanged with exit status 3; it is a server error, not evidence that no effect occurred. A lost, interrupted, oversized, empty, malformed, or truncated reply produces bounded stdout JSON with `outcome: "outcome_unknown"` and exit status 4. This does not imply the request had no effect; an explicit fresh `resume` is available for recovery. Locally invalid input produces `outcome: "invalid_input"` and exit status 2 before any connection.

## Evidence

The native history in `resource-control/tests/native_session_client.rs` invokes a new client process for each operation against the actual Unix gateway and a fixed bounded worker. It captures command arguments, client stdout/stderr and exit status, durable Store event/balance snapshots, and worker launch identity/counter under `ASES_LOCAL_CLIENT_EVIDENCE_DIR`. Synthetic response-drop transport evidence is maintained separately from the actual-gateway history.
