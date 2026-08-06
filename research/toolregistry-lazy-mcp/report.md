---
title: ToolRegistry.register_from_mcp() against a Lazy MCP Proxy — Validation Evidence
program: EDASES
layer: Research
document_type: Research Finding
status: Validated
authority: Experimental
canonical_repository: edases
depends_on:
  - Documentation Standard
  - Concept: Levels of Abstraction
related_documents:
  - research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md
implements:
implemented_by:
supersedes:
superseded_by:
last_updated: 2026-08-06
---

# Research Finding: `ToolRegistry.register_from_mcp()` against a Lazy MCP Proxy

## 1. Purpose and question

This is an **evidence-only validation task**, not a system to ship. The
single question:

> Does `toolregistry.ToolRegistry.register_from_mcp()` work when pointed at a
> lightweight MCP proxy that defers starting the real MCP backend until the
> first use — **without modifying ToolRegistry itself**?

This is the architectural assumption behind the identifier-first /
lifecycle-aware tool-calling proposal in the broader EDASES execution-engine
work: an MCP server can expose a *static identifier manifest* first and only
bring a real backend to life on demand. The deliverable is pass/fail evidence
per observation, timings, full logs, and a source read of ToolRegistry's
notification behaviour — **not** a working product.

Throughout this report, **observations** (what the logs and timings show) are
kept distinct from **findings** (interpretation). Observations reference
specific log files and lines; findings are labelled as such.

## 2. Environment and exact versions

Behavior varies by version, so the exact installed versions are recorded.

| Component | Version | Notes |
|---|---|---|
| `toolregistry` | **0.15.0** | `pip install toolregistry[mcp]`; MCP extra is named `mcp` (`mcp<3,>=1.24.0`, `httpx>=0.28.1`) |
| `mcp` (Python SDK) | **2.0.0** | Direct dependency of the `[mcp]` extra |
| `pydantic` | 2.13.4 | transitive |
| Python | 3.10.12 | venv at `/tmp/toolregistry-venv` (NOT committed) |
| Platform | Linux | single host, all processes local |

All Python dependencies live in `/tmp/toolregistry-venv`; the venv and any
dependency artifacts are excluded from the repository.

**ToolRegistry API surface used** (from installed source, unmodified):
`register_from_mcp(transport: str | dict | Path, namespace, persistent, ...)`
with the stdio dict form `{"command": python, "args": [proxy.py], "env": {...}}`
(`toolregistry/_mixins/registration.py:90`). Invocation via
`registry.invoke("add", {...})` and `registry.list_tools()`. `print(registry)`
is `json.dumps(self.get_schemas(), indent=2)` (`tool_registry.py:185`).

## 3. Artifacts and how to reproduce

Under `research/toolregistry-lazy-mcp/`:

| File | Role |
|---|---|
| `backend.py` | Trivial stdio MCP server exposing one `add(a, b)` tool (mcp SDK `Server`). Logs `BACKEND\|` lines to stderr; writes its PID to `BACKEND_PID_FILE` when told. |
| `proxy.py` | Single-file lazy stdio proxy. MCP **server** to ToolRegistry (cached `tools/list`), MCP **client** to the backend (spawn on first `tools/call`, one reused session). Logs every request/action as `PROXY\|` lines to stderr + `PROXY_LOG_FILE`. Sends **no** notifications. |
| `manifest.json` | Static `tools/list` captured ahead of time from the real backend by `capture_manifest.py` (capture step: run backend once, dump `tools/list`). |
| `capture_manifest.py` | One-shot capture script that produced `manifest.json`. |
| `tests/run_tests.py` | Driver: runs each phase as a clean subprocess, captures `logs/<phase>-harness.log`. |
| `tests/phase123.py` | Tests 1–3 in one session (register → first call → 3 more calls). |
| `tests/phase4.py` | Test 4 (kill backend directly, observe respawn). |
| `tests/phase5.py` | Test 5 (notification dependency, runtime half). |
| `tests/baseline_always_on.py` | Extra baseline: register directly against the backend (no proxy) for the Test 3 latency comparison. |
| `logs/` | One proxy log + one harness log per phase; the harness logs also contain inherited proxy/backend stderr, so the full per-session stream is captured. |

Reproduce:

```bash
python3 -m virtualenv /tmp/toolregistry-venv          # system python3-venv lacked ensurepip; virtualenv used
/tmp/toolregistry-venv/bin/pip install 'toolregistry[mcp]'
/tmp/toolregistry-venv/bin/python capture_manifest.py  # (re)capture manifest.json
/tmp/toolregistry-venv/bin/python tests/run_tests.py
```

Transport is stdio for **both** the proxy and the backend. ToolRegistry spawns
the proxy process; the proxy lazily spawns the backend subprocess on the first
`tools/call` and reuses ONE backend client session afterwards.

### 3.1 Known operationalization deviation (Test 4)

The brief says Test 4 should "start proxy AND backend, register, then kill the
real backend process directly". With ToolRegistry 0.15.0 the persistent MCP
connection is **lazy** (see §6 item 1): no backend process exists between
registration and the first tool call, because the persistent connection is
established only on first `call_tool`. The literal reading is therefore
impossible without a prior call or a non-lazy registry. Test 4 was
operationalized as **register → first call (backend spawned and connected) →
kill backend directly → second call → third call**. This is distinct from
Test 1's cold-start path (backend never existed); here a live backend session
is established and then severed.

## 4. Test results

Tests 1–3 run in one session (per the brief: Test 2 and 3 "continue the same
session/registry"). Tests 4 and 5 each run in a fresh session. Baseline is a
separate extra run.

### Test 1 — Cold registration, backend never started — **PASS**

| Observation | Result | Evidence |
|---|---|---|
| Does registration succeed? | **Yes.** `register_from_mcp(<dict stdio transport>)` returned without error in **2807 ms**. | `logs/tests1-3-harness.log` line `TEST1_REGISTER result=ok delta_ms=2807` |
| Does the proxy log show ANY attempt to reach the backend during registration? | **No.** Registration proxy (pid 1497377) served exactly: `proxy_started` → `server_ready` → received `notifications/initialized` → one `request tools/list backend_connected=False` → `connection_closed exiting`. **Zero** `backend_spawn_start`, zero `backend_up`, zero backend pid-file writes. | `logs/tests1-3-proxy.log` lines 1–5 |
| `print(registry)` and manifest match? | **Yes.** `registry.list_tools()` = `['add']`; the JSON schema dump shows `add` with `a`/`b` `number` properties, identical to `manifest.json`. | `logs/tests1-3-harness.log` lines `TEST1_REGISTRY`, `REGISTRY|...` block; `manifest.json` |

Notes:
- Registration spawns a **short-lived proxy process** for discovery (ToolRegistry
  uses a temporary `MCPClient` for `list_tools`, then closes it — see Finding 1).
  That process exits when its stdin closes. The backend is never started by it.

### Test 2 — First call triggers spawn; same session/registry — **PASS**

| Observation | Result | Evidence |
|---|---|---|
| Was the backend spawned at this point and not before? | **Yes.** After Test 1, `backend_spawn_count=0`; after this call, `backend_spawn_count=1`, `backend_pid_file_exists=True`. The spawn happened inside the first `tools/call` handling. | `logs/tests1-3-harness.log` `TEST1_PROXY_LOG`, `TEST2_SPAWN`; `logs/tests1-3-proxy.log` `backend_spawn_start ... spawn_count=1` |
| ms timing: call invocation → backend-ready (first log line showing backend up) | **2614 ms** (harness call start `epoch_ms=1785983153227` → proxy `backend_up` `epoch_ms=1785983155841`). | `logs/tests1-3-harness.log` `TEST2_TIMING invocation_to_backend_up_ms=2614` |
| ms timing: backend-ready → call returning a result | **10 ms** (proxy `backend_up` → `response tools/call`). | `logs/tests1-3-harness.log` `TEST2_TIMING backend_up_to_response_ms=10`; `logs/tests1-3-proxy.log` lines `backend_up`/`response` |
| Did the call return the correct result? | **Yes.** `add(2,3)` → `'5.0'` (string). | `logs/tests1-3-harness.log` `CALL|add|...result='5.0'...pass=True` |

End-to-end call latency (harness wall clock): **2639 ms**. Decomposition
(observation → finding):
- Proxy process spawn (harness call start → persistent `proxy_started`): ~1342 ms.
- Client handshake to first `tools/call` arrival: ~16 ms.
- Backend spawn + `initialize` handshake: **1255.5 ms** (`init_ms` in proxy log).
- Forward + response: **10 ms**.

### Test 3 — Steady state; same session/registry — **PASS**

| Observation | Result | Evidence |
|---|---|---|
| Backend reused or respawned per call? | **Reused.** Exactly one `backend_spawn_start` / `backend_up` across all four calls; all four `forward` lines reference the same instance `be-1-1497407-54585`; `distinct_backend_instances=1`. | `logs/tests1-3-harness.log` `TEST3_STEADY`; `logs/tests1-3-proxy.log` |
| Latency of steady-state calls | 14 ms, 17 ms, 7 ms (calls 2, 3, 4). | `logs/tests1-3-harness.log` `CALL|add|...delta_ms=14|...17|...7` |
| Rough comparison vs always-on registration | Direct-to-backend baseline steady state: 5 ms, 9 ms, 3 ms, 5 ms. **The proxy hop adds roughly 5–10 ms per call** in steady state (one extra JSON-RPC round trip across a process boundary). | `logs/baseline-always-on-harness.log` |

Baseline (extra, not one of the five tests): direct registration against
`backend.py` succeeded; first call (cold) **1453 ms**, steady-state 3–9 ms.
Proxy cold first call **2639 ms** vs baseline cold **1453 ms** ⇒ the lazy proxy
adds ≈ **1.2 s** on the cold path, dominated by its own process startup
(see §6 item 5).

### Test 4 — Respawn resilience; fresh session — **PASS**

| Observation | Result | Evidence |
|---|---|---|
| Operationalization | register → first call (backend pid 1497567) → SIGKILL backend directly → second call → third call. | `logs/test4-harness.log` `TEST4_BEGIN` … `TEST4_THIRD_CALL` |
| Does the proxy detect the dead backend? | **Yes, immediately.** The second call's forward failed with `MCPError(-32000, 'Connection closed', None)` in the same millisecond as the request; proxy logged `backend_call_failed ... attempt=1 respawning`. | `logs/test4-harness.log` `TEST4_FAILURE_EVENT`; `logs/test4-proxy.log` |
| Does the proxy respawn automatically, and does the call succeed? | **Yes.** Proxy closed the dead session, spawned `be-2` (`spawn_count=2`, new pid 1497595), retried once, `backend_call_retry_succeeded`; the call returned `'9.0'`. | `logs/test4-harness.log` `TEST4_SECOND_CALL ... backend_respawned=True` |
| How long does recovery take? | **1587 ms** end-to-end for the second call; of which failure detection ≈ 0–3 ms, close ≈ 1 ms, respawn+init **1573.6 ms**, retry+response ≈ 6 ms. | `logs/test4-harness.log` `TEST4_SECOND_CALL end_to_end_ms=1587`; `logs/test4-proxy.log` |
| Was the kill confirmed before the call? | Yes: pid 1497567 dead within 20 ms of SIGKILL (`alive_after_kill=False`). | `logs/test4-harness.log` `TEST4_KILL_DONE kill_detection_ms=20` |
| Steady state after respawn | Third call **10 ms**, same respawned backend (pid 1497595), spawn count stays 2. | `logs/test4-harness.log` `TEST4_THIRD_CALL` |

**Finding (distinct from Test 1):** the dead-backend path is a *respawn* of an
established-but-severed session, not the cold-start path. Failure detection by
the mcp SDK client is immediate (the read loop has already hit EOF, so the next
call raises `Connection closed` rather than hanging). A defensive
`PROXY_CALL_TIMEOUT` (default 15 s) bounds pathological hangs; it did not fire.

### Test 5 — Notification dependency; fresh session — **PASS**

| Observation | Result | Evidence |
|---|---|---|
| Runtime: registry keeps functioning with **no** notifications sent by the proxy | **Yes.** Fresh register (2665 ms) with zero backend spawns; `list_tools()=['add']` before and after; one invocation returned `'5.0'`. | `logs/test5-harness.log` `TEST5_AFTER_REGISTER`, `TEST5_AFTER_CALL`, `CALL|add`; `logs/test5-proxy.log` |
| Did the proxy send any notification at any point? | **No.** The proxy has zero notification-send code paths (server capabilities omit `tools/list_changed`; `create_initialization_options()` called with default `notification_options=None`). Its only notification-related log lines are the startup marker `notifications=never` and the *received* `notifications/initialized` (client→server handshake). | `logs/test5-harness.log` `TEST5_PROXY_LOG notification_related_lines=...`; `proxy.py` |
| Source read: does ToolRegistry listen for `notifications/tools/list_changed`? | **Not required.** See below. | §4 Test 5 Part B |

### Test 5 Part B — source read (determinative, not inference alone)

Installed ToolRegistry 0.15.0 source was searched:

- `grep -rn "list_changed" …/toolregistry --include="*.py"` (excluding the
  vendored `_vendor/` directory): **zero matches**.
- `grep -rn "notification|listen|subscribe" …/toolregistry/integrations/mcp/*.py`:
  **zero matches**.
- The only MCP client class ToolRegistry uses is the SDK's **`ClientSession`**
  (`toolregistry/integrations/mcp/client.py:13` imports `ClientSession,
  StdioServerParameters`). `ClientSession` in mcp 2.0.0 has **no**
  `tools/list_changed` handling — its only `list_changed` code is for *roots*
  (`send_roots_list_changed`, `mcp/client/session.py:1289`), which ToolRegistry
  never calls. The high-level `mcp.client.Client` class has an optional
  `listen(tools_list_changed=True)` (client.py:691), but ToolRegistry does not
  use that class at all.

**Verdict: `notifications/tools/list_changed` is NOT required** for
ToolRegistry's MCP integration. The proxy's decision never to send it (or any
notification) has no observable effect on registration, discovery, or
invocation.

## 5. Timing summary (feeds cold-start latency ceiling)

All times in milliseconds, measured on the same host, epoch-derived from log
`epoch_ms` fields (cross-process deltas are therefore wall-clock accurate to
±1 ms scheduling noise).

| Event | Lazy proxy | Direct backend (baseline) |
|---|---|---|
| Registration (cold, incl. mcp SDK import + proxy spawn + list) | 2807 | 2786 |
| First call, end-to-end (harness) | **2639** | 1453 |
| — proxy process spawn (call start → `proxy_started`) | 1342 | — |
| — client handshake + `tools/call` arrival | 16 | — |
| — backend spawn+initialize | 1255.5 | (inside 1453) |
| — forward+response | 10 | — |
| Steady-state calls | 14 / 17 / 7 | 5 / 9 / 3 / 5 |
| Test 4 recovery (dead backend, end-to-end) | 1587 | — |

**Finding:** cold-start latency for the lazy-proxy architecture is dominated by
two Python subprocess startups (proxy ≈ 1.3 s, backend ≈ 1.1–1.3 s), totalling
≈ 2.6 s end-to-end for the first call. Steady-state overhead of the proxy hop
is small (≈ 5–10 ms). These are single-run measurements on one host — treated
as indicative, not benchmark-grade.

## 6. Behaviour NOT anticipated by the brief

1. **The proxy process is not long-lived across registration.** ToolRegistry
   0.15.0 performs tool discovery with a *temporary* `MCPClient` that spawns the
   proxy, lists tools, and closes it (process exits). The persistent connection
   (`persistent=True`, the default) is created **lazily on the first tool call**
   (`MCPConnectionManager._client` is `None` until `_ensure_connected`), which
   spawns a **second** proxy process. Consequence: the proxy must be
   idempotent to being spawned and torn down repeatedly, and must serve
   `tools/list` from cache for every fresh connection. It cannot rely on
   state carried between processes. (Observation: `logs/tests1-3-proxy.log`
   shows two `proxy_started` lines, pids 1497377 and 1497407.)
2. **The SDK re-lists tools after the first call on a session.** mcp 2.0.0's
   `ClientSession.call_tool` calls `validate_tool_result`, which issues a
   `tools/list` when the tool's output-schema cache misses
   (`mcp/client/session.py:1088`). On every fresh persistent connection, the
   first call is followed by an extra `tools/list`. It is harmless against a
   cached-manifest proxy (observed: `logs/tests1-3-proxy.log`
   `request tools/list backend_connected=True` after the first call), but it
   means `tools/list` is not a registration-only request, and the proxy must
   keep answering it correctly at any time.
3. **Environment filtering on stdio spawns.** The mcp SDK's `stdio_client`
   inherits only `HOME/LOGNAME/PATH/SHELL/TERM/USER` plus the explicit `env`
   dict (`mcp/client/stdio.py:75`). Probe control variables (`PROXY_LOG_FILE`,
   `BACKEND_PID_FILE`) must be passed through the transport dict's `env`, or
   they are silently dropped. (Observation: initial smoke test with an
   inherited `PROXY_LOG_FILE` produced no proxy log file.)
4. **ToolRegistry has its own reconnect-and-retry layer at the proxy level.**
   `MCPConnectionManager._call_persistent` catches a failed call, closes and
   re-creates the `MCPClient` (spawning a **fresh proxy process**), and retries
   once (`toolregistry/integrations/mcp/connection.py:106`). In Test 4 the
   proxy absorbed the backend failure internally, so ToolRegistry never saw an
   error; but if the proxy itself died or returned an error, ToolRegistry would
   silently respawn the proxy and retry. This is a resilience behaviour the
   identifier-first proposal should assume is present.
5. **Cold-start cost is process-startup-dominated.** Registration (~2.8 s) is
   mostly mcp SDK import + AsyncRuntime bootstrap + proxy spawn; the first call
   adds a second process (proxy ≈ 1.3 s) plus the backend (≈ 1.1–1.3 s). If the
   cold-start latency ceiling matters, keeping the proxy process alive across
   the registration→first-call gap would require changes on the ToolRegistry
   side (the lazy connection defeats it today) or a longer-lived transport
   than stdio.
6. **Backend failure detection is fast and clean.** A call on a dead session
   raises `MCPError(-32000, 'Connection closed')` in the same millisecond —
   no hang, no retry storm on the proxy side (one respawn, one retry).
7. **ToolRegistry emitted no registry-side log output** in these runs; its
   vendored structlog logger is silent by default. The harness logs therefore
   contain only harness, proxy, backend, and `print(registry)` lines.
8. **Result type:** the backend returns text; the registry's
   `_post_process_result` returns a plain `str` for single text results
   (`add(2,3)` → `'5.0'`), not a number and not a content-block list. Tools
   returning non-text content would come back as content-block dicts. Callers
   should not assume numeric types from schema alone.

None of these behaviours required a richer proxy for the tested surface; they
are characteristics the identifier-first proposal must accommodate.

## 7. Conclusion

`ToolRegistry.register_from_mcp()` **works against the lazy proxy with no
changes to ToolRegistry itself** for the entire tested surface: cold
registration with a static cached manifest (Test 1, PASS), spawn-on-first-call
with correct results and measurable timing (Test 2, PASS), steady-state reuse
of one backend session (Test 3, PASS), automatic respawn after the backend is
killed out from under the proxy (Test 4, PASS), and full functionality with no
MCP notifications of any kind — confirmed both at runtime and by source read
that ToolRegistry does not listen for `notifications/tools/list_changed`
(Test 5, PASS). No richer proxy simulating additional protocol behaviour is
required for this surface. Two caveats belong in the broader project's
assumptions: (a) ToolRegistry 0.15.0 treats the MCP connection as lazy and
short-lived-at-registration, so the proxy is spawned once for discovery and
again for the first call, and must be stateless across processes and serve the
cached manifest to every fresh connection; and (b) cold-start latency for the
first call is ≈ 2.6 s on this host, dominated by two Python subprocess
startups (proxy ≈ 1.3 s + backend ≈ 1.2 s), while steady-state overhead of the
proxy hop is only ≈ 5–10 ms per call.

## 8. Log index

All logs under `research/toolregistry-lazy-mcp/logs/`:

| Phase | Proxy log | Harness log (proxy+backend+registry stream) |
|---|---|---|
| Tests 1–3 (one session) | [`tests1-3-proxy.log`](logs/tests1-3-proxy.log) | [`tests1-3-harness.log`](logs/tests1-3-harness.log) |
| Test 4 | [`test4-proxy.log`](logs/test4-proxy.log) | [`test4-harness.log`](logs/test4-harness.log) |
| Test 5 | [`test5-proxy.log`](logs/test5-proxy.log) | [`test5-harness.log`](logs/test5-harness.log) |
| Baseline (always-on) | — | [`baseline-always-on-harness.log`](logs/baseline-always-on-harness.log) |

The harness logs contain the full interleaved stream (`HARNESS|`, `PROXY|`,
`BACKEND|`, `REGISTRY|` prefixed lines). Proxy-only logs are written directly
by the proxy via `PROXY_LOG_FILE`. Backend PID files (`tests1-3-backend.pid`,
`test4-backend.pid`, `test5-backend.pid`) are transient runtime by-products
written by the backend during each phase and removed after the run; the pids
they held are quoted in the harness logs.
