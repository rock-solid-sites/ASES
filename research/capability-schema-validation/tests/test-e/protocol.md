---
title: Test E Protocol — Transport Requirements (9 Properties)
program: EDASES
layer: Research
document_type: Protocol
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/harness/error-codes.md
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/runtime.py
consumed_by:
  - research/capability-schema-validation/tests/test-e/results.md
  - research/capability-schema-validation/report.md
---

# Test E — Transport Requirements: Protocol

**Question addressed:** 7 — which transport properties are required by the EDASES control boundary.

**Constraint:** Do NOT test MCP lifecycle features (idle-timeout/pooling/eager-vs-lazy/C2 frequency/private extensions/rolling-upgrade). Establish minimum transport semantics using the simplest representative transport(s). Compare `stdio` only as baseline; do NOT infer remote behavior from stdio results. Orphan-process checks after loss/reconnect are mandatory (catalog-scale orphan finding: `toolregistry 0.15.0 / mcp 2.0.0` orphans without explicit close).

## Transports under test

| Transport | Scope | Boundary | Notes |
|---|---|---|---|
| **stdio-baseline** | In-process direct `Harness.call()` | Collocated (same PID) | Baseline only. Any property validated only here is flagged `stdio-only` per design §5.6.2 and not claimed for remote without separate remote validation. |
| **loopback-TCP** | Newline-delimited JSON over loopback `127.0.0.1` TCP to a Python `socket` server handling requests via `ThreadPoolExecutor` (or subprocess for remote-exec proof) | Cross-process where required; otherwise loopback thread | Simplest representative remote that can evidence every required property without external deps. At least `remote execution`, `connection loss`, `reconnect` use a true cross-process boundary (subprocess server) per §5.6.2. |

Remote server speaks: request `{id, op_id, args, delay_ms?, payload_version?}` → response `{id, op_id, result, error, trace, server_pid, duration_ms}`. Correlation key is `id` (UUID v4). Server dispatches via `Harness(Sandbox(), Runtime())` with thread-per-request. A small `delay_ms` field is honored server-side (`time.sleep`) to simulate slow operations for timeout/cancellation tests without needing a special op.

## Property matrix (9 properties — 7 required + 2 conditional)

| # | Property | Required? | Definition (§5.6.1) | Minimal test | Iterations | Pass criterion |
|---|---|---|---|---|---|---|
| 1 | **Concurrent requests** | Required | Multiple in-flight without serializing at transport | Issue N=8 concurrent calls (mix of `search_artefacts`, `get_artefact`, `create_artefact`) with one delayed (200 ms) straggler; verify all complete, wall time < N × single-call latency (demonstrates non-serial), and no dropped requests | 3 repetitions | All N responses returned; each matches its request payload; wall time < sum of serial latencies; effective concurrency ≥ 2 |
| 2 | **Request/response correlation** | Required | Response unambiguously matched to request under concurrency + reordering | Concurrent load (N=8) with injected 300 ms delay on one request to force reordering; verify each response `id` == request `id` and payload/args match; inject a duplicate-id guard check | 3 repetitions | 0 cross-wiring: every response id+payload matches originating request; reordered response still correctly correlated |
| 3 | **Remote execution** | Required | Capability executes on authoritative runtime, not sandbox process | Start loopback-TCP server as **subprocess** (`python -m research.capability-schema-validation.tests.test-e.scripts.server` or inline server in subprocess); client sends call; verify `server_pid != client_pid` and side-effect (`create_artefact` id generation) observable only via server response; also verify sandbox gate still enforced remotely | 3 calls | `server_pid != client_pid` on every call; execution not in client PID; sandbox→validation ordering preserved remotely |
| 4a | **Connection loss — mid-request** | Required | Transport drop while request is in-flight | Open TCP connection, send request with 800 ms server delay, **kill socket/server** after 100 ms mid-flight; record client observation (typed `ConnectionLost` within 2 s, not silent hang); verify no partial result surfaced as success | 3 iterations | Client receives typed `ConnectionLost` (code+boundary+in_flight flag); `executed` not spuriously true; no partial success |
| 4b | **Connection loss — mid-idle** | Required | Transport drop while idle between requests | Establish idle connection, kill server without in-flight request; verify client detects loss on next call (or via heartbeat/failed write) with `ConnectionLost`; idle state requires re-establishment | 2 iterations | Next call after drop returns `ConnectionLost`; idle drop does not corrupt prior results |
| 5 | **Reconnect** | Required | Re-establish after loss without leaking prior state | After 4a drop, reconnect new TCP socket and verify (a) new requests succeed, (b) prior in-flight requests were NOT silently retried with different semantics (compare ids/counts), (c) **orphan check**: no orphaned server process remains (`subprocess` handle reaped, `ps` check if available, socket closed); also verify no state leakage across reconnect (counters/artefacts isolated if server restarted, or preserved if server persisted — record which) | 2 cycles (loss→reconnect) | New requests after reconnect succeed; prior in-flight not auto-retried; no orphan PID remains; state disposition recorded |
| 6 | **Timeout** | Required | Per-request deadline → typed timeout; runtime disposition observable | Send request with server delay 600 ms but client deadline 200 ms; verify caller receives `Timeout` (code, op_id, deadline_ms) within [deadline, deadline+200 ms]; verify server disposition observable via log/trace (completed vs cancelled) — server continues unless explicitly cancelled (record which) | 4 iterations | 4/4 return `Timeout` within window; `Timeout` has required fields; disposition logged |
| 7 | **Cancellation** | Required | Caller-initiated cancel distinct from timeout | Send long request (800 ms delay), cancel after 100 ms via `cancel(id)` control frame; verify caller receives `Cancelled` (code, op_id) and server reports disposition (stopped or explicit "continues" — not silent success); verify no partial side effect surfaced as success (e.g., `create_artefact` not returned as success after cancel) | 4 iterations | 4/4 return `Cancelled` with distinct code from `Timeout`; runtime reports disposition; no successful `create_artefact` result on cancelled call |
| 8 | **Streaming / events** | Conditional | Incremental result delivery if control boundary requires it | **Inclusion test:** attempt a `stream_metrics` chunked delivery over TCP (3 chunks + terminator). **Exclusion reasoning (§5.6.1):** EDASES control boundary work is discrete artefact ops (create/search/review/validate per `capabilities/schemas.json`); no evidence in prior `toolregistry-lazy-mcp` reports or `docs/research/Tools Distribution Architecture Decision Test Framework` that the boundary requires chunked/progressive results. If streaming is not shown as required, record exclusion with this reasoning and mark property as `EXCLUDED — not required` (not a skipped test). Probe still executed to confirm transport *can* stream but boundary does not need it. | 1 probe + reasoning | If excluded: exclusion reasoning tied to EDASES control-flow evidence, probe result recorded but not claimed as requirement |
| 9 | **Durable operation > connection** | Conditional | Operation continues/queryable after originating transport drops | **Inclusion test:** start `create_artefact` with 500 ms delay → drop client connection → reconnect → query status/result by `op_id`+correlation id. **Exclusion reasoning:** EDASES boundary ops are synchronous request/response within `agent→sandbox→runtime` (§1.3 target architecture); no `toolregistry-lazy-mcp` evidence of operations whose lifetime must exceed the connection. Mark as `EXCLUDED — not required` if not evidenced; record transport probe (whether TCP server can support durable handles) separately. | 1 probe + reasoning | If excluded: exclusion reasoning recorded; probe shows server *could* support it via idempotent correlation-id cache but not required by boundary |

## Harness and logging

* Each property test is independent; runner is `research/capability-schema-validation/tests/test-e/run.py` which orchestrates all 9 checks. Per-property scripts live under `tests/test-e/scripts/` if needed (server helper).
* Every call logs `{property, transport, iteration, request_id, op_id, args, response_id, latency_ms, error_code, wall_ms, server_pid, client_pid, pass}`.
* Logs committed under `research/capability-schema-validation/logs/test-e/`:
  `concurrent.jsonl`, `correlation.jsonl`, `remote.jsonl`, `loss-mid-request.jsonl`, `loss-mid-idle.jsonl`, `reconnect.jsonl`, `timeout.jsonl`, `cancellation.jsonl`, `streaming.jsonl`, `durable.jsonl`, `summary.json`.
* Orphan checks: after connection-loss and reconnect tests, runner asserts no orphaned server subprocess (via `Popen.poll()` + socket close); if `ps` is unavailable the subprocess-handle check is the authoritative gate.

## Acceptance / gate to Phase 3 (§11 Phase 2 gate)

* `tests/test-e/protocol.md` (this file) + `tests/test-e/results.md` (per-property pass/fail matrix with `stdio-only` qualifications) + raw logs committed.
* `stdio-only` qualifications applied where a property was validated only on direct harness without remote transport.
* Orphan checks recorded after loss/reconnect.
* Conditional properties 8/9 have explicit inclusion/exclusion reasoning per §5.6.1 (exclusion is a finding, not a skip).

## WHAT-NOT-TESTED (protocol-level)

* No MCP idle-timeout/pooling/eager-vs-lazy/C2 fleet/private extensions/rolling-upgrade (retired scope §9 — out of scope unless gating question demands it).
* No TLS/mTLS/auth at transport — only minimal semantics per §5.6.1.
* No cross-host (true remote machine) test — loopback TCP is the minimal cross-process boundary; multi-host network partitions are not exercised.
* No high-throughput/throughput-latency quantile benchmarking — only N=8 concurrency with wall-time < serial bound.
* Model-in-the-loop is absent (harness simulates agent→sandbox calls; no LLM selects ops during transport tests).
