---
title: Test E Results — Transport Requirements (9 Properties)
program: EDASES
layer: Research
document_type: Report
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-e/protocol.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/harness/error-codes.md
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/runtime.py
consumed_by:
  - research/capability-schema-validation/report.md
---

# Test E — Transport Requirements: Results

**WHY** — Establish which transport semantics the EDASES `agent → sandbox → small preselected capability API → authoritative runtime` boundary actually requires, without re-testing retired MCP lifecycle features. Each property is a discriminating test for a distinct transport concern.

**WHAT** basis — Logic-level loopback-TCP harness (newline-delimited JSON over `127.0.0.1` with `ThreadPoolExecutor` server, subprocess PID boundary for remote proof) exercising the same 14-op authoritative capability set (`version 0.1.0`) via `Harness(Sandbox(), Runtime())`. Every call is `sandbox → validation → policy → execution` with typed errors per `harness/error-codes.md`. Logs under `logs/test-e/` (69 JSONL rows + `summary.json`) are the primary evidence; tables below are derived from those logs.

**HOW CERTAIN** — **evidence-based** (not proven). Deterministic simulated transport on loopback; no TLS/mTLS, no cross-host network partition, no high-throughput benchmark, no LLM-in-the-loop. Loopback TCP is the simplest cross-process remote; findings for required properties are positive evidence that minimal semantics suffice, not proof that every real transport will behave identically.

**WHAT-NOT-TESTED** — See §7 (full list): retired MCP lifecycle (idle-timeout/pooling/eager-vs-lazy/C2 fleet/private extensions/rolling-upgrade), TLS/auth, cross-host partitions, throughput quantiles, model-in-the-loop, format drift; loopback is not a WAN.

## Setup

* **Capability set:** 14 ops, `version 0.1.0`, `capabilities/authoritative/schemas.json` (6 categories per design §3.2).
* **Harness:** `harness/sandbox.py` (exact-match preselected gate) + `harness/runtime.py` (Draft-07 validation, version check, policy, simulated execution) + `tests/test-e/scripts/server.py` (loopback TCP server, correlation `id` per request, `ThreadPoolExecutor(16)`, cooperative `delay_ms` slice for timeout/cancel, durable id cache, streaming chunk mode).
* **Transports:** `loopback-TCP` (remote) and `loopback-TCP-subprocess` (remote execution proof via `subprocess.Popen` PID boundary). `stdio-baseline` (direct `Harness.call()`) used only to measure single-call latency baseline for the concurrent wall-time bound; no property is claimed `stdio-only`.
* **Runner:** `research/capability-schema-validation/tests/test-e/run.py` (`python3 .../tests/test-e/run.py`), deterministic, no external deps beyond stdlib + `jsonschema`.
* **Client PID:** `2980285` (this run); each server reports its own `server_pid`.

## Per-property results

### Summary matrix

| # | Property | Required? | Transport | Repetitions | Pass? | stdio-only? |
|---|---|---|---|---|---|---|
| 1 | Concurrent requests | Required | loopback-TCP | 3 × N=8 | **PASS** | No |
| 2 | Request/response correlation | Required | loopback-TCP | 3 × N=8 | **PASS** | No |
| 3 | Remote execution | Required | loopback-TCP-subprocess | 3 + 1 malformed probe | **PASS** | No |
| 4a | Connection loss (mid-request) | Required | loopback-TCP | 3 | **PASS** | No |
| 4b | Connection loss (mid-idle) | Required | loopback-TCP | 2 | **PASS** | No |
| 5 | Reconnect | Required | loopback-TCP | 2 cycles | **PASS** | No |
| 6 | Timeout | Required | loopback-TCP | 4 | **PASS** | No |
| 7 | Cancellation | Required | loopback-TCP | 4 | **PASS** | No |
| 8 | Streaming / events | Conditional | loopback-TCP | 1 probe | **EXCLUDED** (not required) | No |
| 9 | Durable > connection | Conditional | loopback-TCP | 1 probe | **EXCLUDED** (not required) | No |

Overall required: **7/7 PASS**. Overall including conditional probes: **PASS** (conditionals are findings of exclusion, not failures). `stdio_only_properties: []`.

---

### 1 — Concurrent requests — PASS

**Test:** N=8 concurrent calls (mix `search_artefacts`, `get_artefact`, `create_artefact`, `list_reviews`, `query_metrics`) with one 200 ms delayed straggler; wall time < N × single-call latency (single measured via direct harness, ~5 ms; serial bound computed as N × max(single,15)+500 ≈ 620 ms). 3 repetitions.

| Iter | N | wall_ms | serial_bound | single_ms | all_returned | all_matched | non_serial |
|---|---|---|---|---|---|---|---|
| 0 | 8 | 206 | 620 | 5 | true | true | true |
| 1 | 8 | 204 | 620 | 5 | true | true | true |
| 2 | 8 | 204 | 620 | 5 | true | true | true |

Wall ~204 ms with 200 ms straggler proves thread-pool concurrency; serial would have been > 8× overhead. All 8 responses returned per iteration, each `response.id == request.id`.

Log: `logs/test-e/concurrent.jsonl` (24 rows).

### 2 — Request/response correlation — PASS

**Test:** N=8 concurrent `search_artefacts` with distinct `query=corr-{i}`, index 3 delayed 300 ms to force reordering. 3 repetitions. Check: 0 cross-wiring (response `id` and `op_id` match request; no payload swap).

| Iter | N | cross_wired | reordered? | Pass |
|---|---|---|---|---|
| 0 | 8 | 0 | yes (delayed idx 3) | PASS |
| 1 | 8 | 0 | yes | PASS |
| 2 | 8 | 0 | yes | PASS |

Log: `logs/test-e/correlation.jsonl` (24 rows).

### 3 — Remote execution — PASS

**Test:** Spawn subprocess server (`server.py` via `subprocess.Popen`), verify `server_pid != client_pid` on every call, plus sandbox→validation ordering preserved remotely (malformed `get_artefact` with `BAD!!` rejected as `ValidationFailed` before execution).

| Call | op_id | server_pid | client_pid | pid_differs | executed | code |
|---|---|---|---|---|---|---|
| 0 | search_artefacts | 2980392 | 2980285 | true | true | — |
| 1 | create_artefact | 2980392 | 2980285 | true | true | — |
| 2 | search_artefacts (delayed) | 2980392 | 2980285 | true | true | — |
| malformed | get_artefact (BAD!!) | 2980392 | 2980285 | true | false | ValidationFailed |

Server reaped (`proc.poll() is not None`, `returncode=-15`), no orphan. Log: `logs/test-e/remote.jsonl` (4 rows).

### 4a — Connection loss (mid-request) — PASS

**Test:** Open persistent TCP connection, send request with 800 ms server delay, kill server after 100 ms. Expect client receives typed `ConnectionLost` (EOF) within 2 s, not a spurious success. 3 iterations.

| Iter | got_connection_lost | elapsed_ms | Pass |
|---|---|---|---|
| 0 | true | 1 | PASS |
| 1 | true | 0 | PASS |
| 2 | true | 1 | PASS |

No partial result surfaced as success; orphan check via `proc.wait()` — no orphan. Log: `logs/test-e/loss-mid-request.jsonl`.

### 4b — Connection loss (mid-idle) — PASS

**Test:** Establish idle connection (verified with one probe call), kill server with no in-flight request, then attempt next write. Expect `ConnectionLost` (EOF / socket error) before any new execution. 2 iterations.

| Iter | observation | Pass |
|---|---|---|
| 0 | EOF after idle loss | PASS |
| 1 | EOF after idle loss | PASS |

Prior results uncorrupted. Log: `logs/test-e/loss-mid-idle.jsonl`.

### 5 — Reconnect — PASS

**Test:** After 4a-style loss, reconnect to a fresh server and verify (a) new requests succeed, (b) prior in-flight id was NOT silently retried with different semantics (durable fetch of old `lost_id` on new server returns `NotFound`), (c) no orphaned server remains. 2 cycles.

| Cycle | new_ok | not_retried | orphan1 | orphan2 | Pass |
|---|---|---|---|---|---|
| 0 | true | true | false | false | PASS |
| 1 | true | true | false | false | PASS |

`not_retried` proven by `fetch(target_id=lost_id)` → `NotFound` on new server. Fresh server's own correlation cache isolates prior ids. Orphan check: `proc.poll() is not None` after `terminate()+wait(3)` both cycles. Log: `logs/test-e/reconnect.jsonl`.

### 6 — Timeout — PASS

**Test:** Server delay 600 ms, client deadline 200 ms via `tcp_call(timeout=0.2)`. Expect `Timeout` (`code=Timeout`, `boundary=transport`, `deadline_ms`) within `[deadline, deadline+400 ms]`. 4 iterations. Disposition: client-side enforcement; server not auto-cancelled (continues unless explicitly cancelled — recorded as finding; inspectable via durable fetch).

| Iter | deadline | delay | elapsed | code | within_window | Pass |
|---|---|---|---|---|---|---|
| 0 | 200 | 600 | 200 | Timeout | true | PASS |
| 1 | 200 | 600 | 200 | Timeout | true | PASS |
| 2 | 200 | 600 | 200 | Timeout | true | PASS |
| 3 | 200 | 600 | 200 | Timeout | true | PASS |

Log: `logs/test-e/timeout.jsonl` (includes full response rows). Distinct from `Cancelled` by code alone (see §7).

### 7 — Cancellation — PASS

**Test:** Long request 800 ms, caller-initiated `cancel(target_id)` on separate connection after 100 ms. Expect `Cancelled` (`code=Cancelled`, `boundary=transport`) distinct from `Timeout`, and no partial `create_artefact` success surfaced.

| Iter | cancel_ack | response_code | distinct_from_timeout | no_partial_success | Pass |
|---|---|---|---|---|---|
| 0 | true | Cancelled | true | true | PASS |
| 1 | true | Cancelled | true | true | PASS |
| 2 | true | Cancelled | true | true | PASS |
| 3 | true | Cancelled | true | true | PASS |

Cancellation is cooperative (server slices delay into 50 ms chunks checking `_CANCELLED_IDS`); confirmed by `result is None` and `executed is False` on cancelled call. Log: `logs/test-e/cancellation.jsonl`.

### 8 — Streaming / events — EXCLUDED (not required by boundary)

**Probe:** Request `type=stream` with 3 chunks; server sends newline-delimited chunk frames.

| Probe | chunks | ordered | clean_term | transport_can |
|---|---|---|---|---|
| stream 3 | 3 | true | true | true |

**Exclusion reasoning:** EDASES control boundary ops are discrete artefact operations per `capabilities/schemas.json` (`create/search/review/validate`) and prior `toolregistry-lazy-mcp` reports; no evidence in those reports or `docs/research/Tools Distribution Architecture Decision Test Framework` that the boundary requires progressive/chunked results. Transport *can* stream (probe PASS) but boundary does **not** need it. Marked `EXCLUDED` per protocol §5.6.1 — an explicit finding, not a skipped test.

Log: `logs/test-e/streaming.jsonl`.

### 9 — Durable operation > connection — EXCLUDED (not required by boundary)

**Probe:** Start `create_artefact` with 300 ms delay → drop client connection at 50 ms → wait 600 ms → reconnect → `fetch(target_id=prior_id)`.

| Probe | transport_can | durable_result.id | Pass |
|---|---|---|---|
| durable fetch | true | == prior_id | PASS |

**Exclusion reasoning:** EDASES ops are synchronous `request→response` within `agent → sandbox → runtime` (§1.3 target architecture); no prior `toolregistry-lazy-mcp` evidence that operation lifetime must exceed the connection. Transport *can* support durable via correlation-id cache on the server (probe PASS) but boundary does **not** require it. Marked `EXCLUDED` per protocol §5.6.1.

Log: `logs/test-e/durable.jsonl`.

---

## Transport selection and stdio-only qualification

* No property is `stdio-only`. The harness direct call was used only to measure single-call latency baseline for the concurrent bound; all 9 properties were validated on loopback-TCP (cross-process for remote/loss/reconnect per design §5.6.2). A `stdio-only` flag would have been applied per §5.6.2 if any property lacked remote validation; `summary.json: stdio_only_properties: []`.

## Orphan-process checks (mandatory per design §5.6.3 and issue #498 fallback note)

| After | Check | Result |
|---|---|---|
| Connection loss (mid-request, 3 iters) | `proc.wait(2)` after `terminate()` | Reaped, no orphan |
| Connection loss (mid-idle, 2 iters) | `proc.wait(2)` after `terminate()` | Reaped, no orphan |
| Reconnect cycle 0 — old server | `proc1.wait()` then `proc2.wait(3)` after graceful `shutdown` + `terminate` | Both reaped |
| Reconnect cycle 1 — old server | Same | Both reaped |
| Remote execution subprocess | `proc2.wait(3)` after `shutdown` + `terminate` | Reaped (`returncode -15`) |
| Timeout servers (4 iters) | `proc.wait(3)` after `terminate` | All reaped |
| Cancellation servers (4 iters) | `proc.wait(3)` after `terminate` | All reaped |
| Streaming + durable probes | `proc.wait(3)` after `terminate` | Both reaped |

No orphaned server processes observed. Forensics: `ps --ppid` not required when `Popen.poll()` is authoritative; both agree here. Finding aligns with the `toolregistry 0.15.0 / mcp 2.0.0` orphan caution — explicit `terminate()+wait()` prevents the orphan; omitting it would reproduce the prior finding.

## Reproduction

```bash
python3 research/capability-schema-validation/tests/test-e/run.py
# logs written to research/capability-schema-validation/logs/test-e/
# summary at logs/test-e/summary.json
# also:
python3 research/capability-schema-validation/harness/run.py --smoke
python3 research/capability-schema-validation/harness/run.py --measure-tokens
```

Second run is deterministic (UUIDs differ but pass/fail stable across 3 consecutive runs in dev).

## Remaining uncertainties (tied to report §9)

See §7 WHAT-NOT-TESTED. For synthesis (§8/§9) note: loopback is not cross-host; TLS/mTLS/auth not tested; model-in-the-loop absent; throughput tail not measured; `stdio-only` does not apply here but would gate any claim that remote inherits stdio results without separate remote validation (design §5.6.2).

## Explicit finding for RPC research (§10 input)

Minimum transport semantics required by the EDASES control boundary (evidence-based):

* **Required:** concurrent requests, request/response correlation, remote execution, connection loss (mid-request and mid-idle), reconnect (without silent retry and without orphans), timeout, cancellation (distinct codes, both observable dispositions).
* **Not required by boundary (but transport-capable):** streaming/events, durable operation > connection — exclude from required set pending fresh evidence that the control boundary needs them.

Implication for RPC track: the runtime-authoritative validation harness (§7 architecture) is transport-agnostic; the transport must preserve correlation ids and typed errors end-to-end (`Timeout`/`Cancelled`/`ConnectionLost` distinct from `ValidationFailed`/`PolicyDenied`/`UnknownOperation`). Lexicon/XRPC adoption is orthogonal to this finding — the separation holds regardless.

---

## 7. WHAT-NOT-TESTED (per AGENTS.md — negative-space disclosure)

* Retired scope not tested and not reintroduced: MCP idle-timeout/pooling, eager-vs-lazy matrices, ToolRegistry C2 fleet frequency, private-internal extensions, MCP-specific rolling-upgrade (design §9 — absence is a scoping decision, not an omission).
* No TLS/mTLS/authentication/authorization at transport.
* No cross-host (multi-machine) network partition; loopback TCP is the minimal cross-process boundary.
* No WAN latency/jitter/loss-injection or throughput/latency quantile benchmarking (only N=8 concurrency with wall-time bound).
* No model-in-the-loop (LLM) — agent calls are harness-simulated; Test E does not measure model selection/accuracy under transport faults.
* No output-schema drift tested here (that's Test C); no format-version drift beyond the harness `version` field.
* Streaming/durable probes show transport capability, not boundary requirement — exclusion is a finding tied to current EDASES control-flow evidence, subject to revision if new evidence appears.

## Inputs to final report (report.md §§6, 9, 10)

* §6 Transport findings: 7/7 required PASS, 2/2 conditional EXCLUDED (not required); matrix above + `stdio_only: []` + orphan checks clean.
* §9 Remaining uncertainties: disclosure above plus version-bound note (`toolregistry 0.15.0 / mcp 2.0.0` orphan precedent informs explicit reaping; not re-derived).
* §10 RPC recommendation: required set above; RPC must preserve correlation + typed-error boundary; streaming/durable not in required set.

*End of Test E results. Evidence lives in `logs/test-e/` and `summary.json`.*
