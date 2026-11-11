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

The client emits only the exact existing `local_*` request fields and closes its write half after sending. Connect is bounded to 2 seconds, request write to 3 seconds, and the complete response read to 3 seconds; responses are capped at 8 KiB. There is no reconnect or automatic retry. Replies must match the gateway shape: success has an object `result`; a server error has a string `error`. Successful gateway JSON replies are passed through to stdout with exit status 0. A received `{ "ok": false, "error": "..." }` server reply is also passed through unchanged with exit status 3; it is a server error, not evidence that no effect occurred. A lost, interrupted, oversized, empty, malformed, or truncated reply produces bounded stdout JSON with `outcome: "outcome_unknown"` and exit status 4. This does not imply the request had no effect; an explicit fresh `resume` is available for recovery. Locally invalid input produces `outcome: "invalid_input"` and exit status 2 before any connection.

## Evidence

The native history in `resource-control/tests/native_session_client.rs` invokes a new client process for each operation against the actual Unix gateway and a fixed bounded worker. It captures command arguments, client stdout/stderr and exit status, durable Store event/balance snapshots, and worker launch identity/counter under `ASES_LOCAL_CLIENT_EVIDENCE_DIR`. The focused target passed 2/2 tests. Its histories show hot launch/resume without redispatch, exact stop and natural code-0 exit observed before finalize, cold resume as unknown, a real viewer peer-policy denial, and a spawn server error after durable launch intent with capacity retained. The server error is passed through without a claim that it had no effect; explicit fresh resume returns unknown. Exact command, commit, source hashes and record counts are in `evidence/client/manifest.json`. Synthetic response-drop transport evidence is maintained separately from the actual-gateway history.

## Actual lost-reply history

`actual_client_loses_accepted_launch_reply_then_recovers_without_redispatch` inserts a bounded same-UID Unix transport proxy between a fresh `resource-session launch` process and the actual admin gateway. The focused history passed 1/1. The proxy forwards the request exactly once, captures the gateway's actual successful `running` reply, then closes the client connection without returning that reply. It does not make an authorization or lifecycle decision. The client returns exit status 4 with `outcome_unknown`; the real Store retains `RUNNING`, exact start evidence, and 50 units of reserved capacity, and the fixed worker counter remains one. Fresh `resume`, exact launch replay, explicit stop and explicit finalize complete recovery without a second child and release the reservation. This transport fixture is separate from the synthetic malformed/timeout tests and from the ordinary direct-gateway histories. Its retained request, discarded reply, client result, Store snapshots, worker identity and exact run command are under `evidence/client-lost-reply/`.
