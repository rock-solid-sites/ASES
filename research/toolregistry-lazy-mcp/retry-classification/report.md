---
title: Retry Classification Alone — Can Tagging Schema-Validation Failure as a Terminal Application Error Remove the 4x Spawn Multiplier? — Evidence
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
  - research/toolregistry-lazy-mcp/output-schema-drift/report.md
  - research/toolregistry-lazy-mcp/report.md
implements:
implemented_by:
supersedes:
superseded_by:
last_updated: 2026-08-06
---

# Research Finding: Retry Classification Alone — Before/After on the 4x Spawn Multiplier

## 1. Purpose and question

This is an **evidence-only validation task**, follow-on to #213 (output-schema
drift, merged to main at `2b6735d`). #213 found that one caller-visible drift
failure costs **4 backend spawns and 2 persistent proxy processes** because
**two uncoordinated retry layers stack**:

1. the proxy's internal retry respawns the backend after the forwarded call
   fails (`BackendClient.call` in the #213 `proxy.py`), and
2. ToolRegistry's reconnect-retry
   (`toolregistry/integrations/mcp/connection.py:106`) treats the
   schema-validation failure as a connection problem, closes the `MCPClient`,
   spawns a **fresh proxy process**, which respawns the backend again.

The single question:

> If the proxy signals "backend responded, but the result failed schema
> validation" in a way that does NOT resemble a dropped connection — a normal
> MCP tool-error response (`CallToolResult(isError=True, ...)`), not a
> connection close / socket error — does ToolRegistry's reconnect-retry stop
> firing, does the proxy stop respawning the backend for this failure class,
> and does the observed cost drop from ~4x to roughly the single-spawn cost?

The deliverable is pass/fail evidence per test, timings, full logs, verbatim
caller-visible error text, and a documented, empirically-verified choice of
response shape — **not** a product and **not** the heavier mitigation
(periodic revalidation / fallback live-schema fetch are explicitly out of
scope; they are only to be built next if this test shows classification alone
insufficient).

Throughout this report, **observations** (what logs and timings show, with
file/line references) are kept distinct from **findings** (interpretation).

## 2. Environment and exact versions

Same pinned venv as #196/#213 (reused, not reinstalled):

| Component | Version | Notes |
|---|---|---|
| `toolregistry` | **0.15.0** | `pip install toolregistry[mcp]==0.15.0`; MCP extra named `mcp` |
| `mcp` (Python SDK) | **2.0.0** | Direct dependency of the `[mcp]` extra; re-confirmed live 2026-08-06 via `importlib.metadata.version("mcp")` |
| Python | 3.10.12 | venv at `/tmp/toolregistry-venv` (NOT committed) |
| Platform | Linux | single host, all processes local |

All tests ran with the transport pair **stdio → proxy → stdio → backend**
(identical to #196/#213 scope). ToolRegistry's persistent MCP connection is
lazy: no backend process exists between registration and the first tool call.

**Host-load caveat.** This host ran several parallel agent workloads during
the measurement window (load average peaked ~15 on 4 cores; `uptime`
observations in `logs/`). Backend `initialize` handshakes in this corpus
measured **1160–12 207 ms** versus the 773–1555 ms range of #213's
normal-load runs (n=32). Absolute latencies are therefore load-inflated;
every conclusion that depends on absolute ms is additionally reported as a
ratio against the control run under the **same** load conditions, and per-run
`init_ms` values are logged so the inflation can be separated from the
measured effect.

## 3. What was built

All new artefacts live in a clean sibling directory,
`research/toolregistry-lazy-mcp/retry-classification/`; nothing in the #213
corpus was modified (`backend.py` and `manifest.json` are byte-identical
copies — md5-verified — so the proxy in this directory spawns identical
artefacts).

| File | Role |
|---|---|
| `proxy_classified.py` | **The single-variable modified proxy.** Copy of the #213 drift `proxy.py` with exactly two deltas (both documented in its docstring): (1) classification — a schema-validation failure is terminal: no proxy respawn/retry, and the failure is returned as a normal MCP tool-error response (`CallToolResult(isError=True, content=[text])`) instead of a raise; (2) test instrumentation — optional `PROXY_PID_FILE` (same pattern as the backend's `BACKEND_PID_FILE`) used by Test 3 to kill the persistent proxy mid-call. Everything else is byte-for-byte #213 behaviour: lazy spawn on first `tools/call`, one reused session, respawn + single retry on ACTUAL connection failures, cached `tools/list`, no notifications. |
| `backend.py` | Byte-identical copy of the #213 drift backend (md5 `279c7520...`). |
| `manifest.json` | Byte-identical copy of the #213 cached manifest (md5 `f8977f8a...`): `add` declares `output_schema={"type":"object","properties":{"sum":...},"required":["sum"]}`. |
| `tests/common_retry.py` | Shared helpers. `make_transport` takes an explicit `proxy_path` (Test 1 runs the ORIGINAL drift proxy; Tests 2/3 run `proxy_classified.py`) and passes the same raised backend/call timeouts to every phase (45 s / 120 s — see §3.1). `invoke_recorded` records the classified failure shape (a `ToolCallResult` whose stringified `result` carries `is_error=True`) verbatim. |
| `tests/phase_1_control.py` | Test 1 (control): ORIGINAL drift proxy, drift scenario. |
| `tests/phase_2_classified.py` | Test 2: `proxy_classified.py`, identical drift scenario. |
| `tests/phase_3_connection.py` | Test 3: `proxy_classified.py`, healthy backend, persistent proxy killed mid-call. |
| `tests/phase_3b_proxy_retry.py` | Supplementary (within Test 3's "did not overcorrect" intent): `proxy_classified.py`, healthy backend, **backend** killed mid-call — verifies the proxy's OWN respawn-retry still fires. |
| `tests/run_retry.py` | Driver: runs each phase as a clean subprocess, captures `logs/<phase>-harness.log`, echoes the measurement lines. |
| `logs/` | One proxy log + one harness log per phase, per run. |

Reproduce (versions pinned to the exact installed set):

```bash
cd research/toolregistry-lazy-mcp/retry-classification
/tmp/toolregistry-venv/bin/python tests/run_retry.py
```

### 3.1 Test-environment tuning (documented, not a proxy-behaviour change)

The proxy's documented `PROXY_BACKEND_TIMEOUT` (default 10 s) and
`PROXY_CALL_TIMEOUT` (default 15 s) were raised to 45 s / 120 s for **all**
phases via the transport env (the #213 proxy reads the same vars). Reason,
observed: on this loaded host backend init reached 12 207 ms, which exceeded
the 10 s default and aborted calls with `error: backend did not become ready
in 10.0s` before the tested failure class could be exercised. The same
values apply to control and modified phases, so the comparison is
like-for-like.

## 4. Empirical investigation: what response shape avoids `connection.py:106`?

The #213 report documented the failure chain: proxy raises → stdio dispatcher
converts to a JSON-RPC error (`mcp/shared/jsonrpc_dispatcher.py:755-757`,
`code=0, message=str(e)`) → ToolRegistry's client raises `MCPError` →
`_call_persistent` (`connection.py:103-105`) catches **any** `Exception`
(`connection.py:106`) and reconnects. Source read confirmed the catch-all is
the whole story: `_call_persistent` has no failure-class distinction — ANY
raised exception from `MCPClient.call_tool` is treated as connection loss.

Two probes (in `/tmp`, not committed) established the response-shape facts
empirically before the proxy was modified:

**Probe 1 — an `isError=True` tool-error response round-trips without a
raise.** A minimal stdio MCP server returned
`CallToolResult(isError=True, content=[TextContent(...)])` for `tools/call`.
Registered via ToolRegistry 0.15.0 and invoked:

* `registry.invoke` returned a **`ToolCallResult`**, NOT an `ErrorResult`,
  whose `result` was the **stringified pydantic repr** of the `CallToolResult`
  (e.g. `meta=None content=[TextContent(type='text', text="...", ...)]
  structured_content=None is_error=True result_type='complete'`). Root
  cause: `MCPToolWrapper._post_process_result`
  (`toolregistry/integrations/mcp/integration.py:148-150`) returns an
  isError result unchanged, and ToolRegistry's `_finalize_result`
  (`tool_registry.py:899-945`) stringifies non-content-block results.
  `ErrorResult` is only produced when an exception propagates — which is
  exactly the path that triggers the reconnect.
* **No reconnect fired** for the invoke: exactly one persistent server
  process existed during the call (a second `probe_server_started` was the
  registration-time temporary connection, which exits after `tools/list`).

**Probe 2 — the classifier boundary is clean.** A proxy-side
`ClientSession.call_tool` against a backend killed out from under it raised
`MCPError(-32000, 'Connection closed', None)` — NOT a `RuntimeError` with the
schema-validation message. So a classifier keyed on the SDK's exact
validation signature (`RuntimeError` whose message contains
`"Invalid structured content returned by tool"`,
`mcp/client/session.py:1096-1100`) cannot swallow genuine connection
failures.

**Chosen shape (documented + verified).** `proxy_classified.py` catches the
SDK's schema-validation `RuntimeError` in `BackendClient.call`, skips the
respawn, and re-raises an internal `SchemaValidationFailure` marker;
`on_call_tool` converts it to `CallToolResult(isError=True, content=[text])`
with the full schema-error text. This is the **only** shape that both (a)
returns normally through `_call_persistent` (no reconnect) and (b) carries
the schema error verbatim. Its caller-visible side effect — the
`ToolCallResult`-with-repr shape instead of an `ErrorResult` — is a finding
in itself (§9).

## 5. Test results

Every phase passed (exit 0). "PASS" means the characterised behaviour
occurred as expected. All numbers are from the committed driver runs; the
committed corpus is run 5 (the last full run); run-by-run ranges cover all
successful runs made for this task (n=4 for Test 1, n=5 for Test 2, n=4 for
Test 3).

### Test 1 — CONTROL: reconfirm the 4x multiplier (unmodified #213 proxy) — **PASS**

Setup: cached `manifest.json` (conforming `{"sum": ...}`); backend
`schema_mode=conforming` (still declares the conforming schema) +
`response_mode=diverging` (returns `structured_content={"result": n}`);
proxy = the ORIGINAL `output-schema-drift/proxy.py`.

| Observation | Result | Evidence |
|---|---|---|
| Backend spawns | **4** (`backend_spawn_count=4`, `backend_up_count=4`, `backend_call_failed_count=4`) | `logs/test-1-control-proxy.log` |
| Proxy processes | **3** = registration temp + **2 persistent** (`reconnect_fired=True`) | `proxy_pids=[...3 pids...]`; `TEST1_SPAWN_COUNTS` |
| Caller-visible outcome | `ErrorResult`, message starts `MCPError: Error executing add: Invalid structured content returned by tool add: 'sum' is a required property...` (verbatim §8) | `TEST1_RESULT pass=True (observed: ErrorResult)` |
| Failure latency | **12 176–42 518 ms** (n=4; per-run 42 518 / 12 176 / 14 867 / 27 330) — load-inflated, see §2 | `INVOKE ... delta_ms=...` per run |

**The 4x multiplier still reproduces exactly:** the control run shows the
same event sequence #213 documented — proxy-internal retry (be-1 → be-2)
inside proxy A, then ToolRegistry's reconnect spawning proxy B, which does
it again (be-1 → be-2): 4 backend spawns, 2 persistent proxies, one
caller-visible `MCPError`. `init_ms` for the 4 spawns in the committed run:
2762.6 / 2975.3 / 3246.4 / 5930.1.

### Test 2 — MODIFIED proxy, identical drift scenario — **PASS**

Setup identical to Test 1 except the transport points at
`proxy_classified.py`.

**(a) Spawn/proxy counts for the single failed call:**

| Observation | Value | Evidence |
|---|---|---|
| Backend spawns | **1** (`backend_spawn_count=1`, `backend_up_count=1`) | `TEST2_SPAWN_COUNTS` |
| Proxy processes | **2** = registration temp + **1 persistent** (`reconnect_fired=False`) | `proxy_pids=[2 pids]` |
| Proxy internal retry | **did NOT fire** (`backend_call_failed_count=0`, `retry_succeeded_count=0`) | `TEST2_SPAWN_COUNTS` |
| Classification events | 1 × `backend_schema_validation_failed terminal=yes respawn=no`; 1 × `call_tool_classified_schema_failure returning_tool_error_response` | `logs/test-2-classified-proxy.log` |

**(b) Did ToolRegistry's reconnect-retry fire? — NO.** The proxy log
contains exactly ONE `proxy_started` after registration (the persistent
proxy, pid present in `TEST2_PROXY_STARTED`); there is no fresh
`proxy_started` after the failure. `reconnect_fired=False` in every run.
The `isError=True` response returned normally through
`_call_persistent` — `connection.py:106` had nothing to treat as connection
loss.

**(c) Failure latency:** **4224–14 471 ms** (n=5; per-run 11 990 / 14 471
(smoke) / 5 242 / 4 224 / 6 887). Direct before/after against Test 1 on the
same runs:

| Run | Test 1 control (ms) | Test 2 classified (ms) | Ratio T2/T1 |
|---|---|---|---|
| 1 | 42 518 | 11 990 | 0.28 |
| 3 | 12 176 | 5 242 | 0.43 |
| 4 | 14 867 | 4 224 | 0.28 |
| 5 | 27 330 | 6 887 | 0.25 |
| smoke (heavy load) | — | 14 471 | — |

**Test 2 = 25–43 % of the Test 1 control latency** (matched runs).
Against the #213 successful-call baseline (1810–3124 ms, n=3, measured
under normal load): Test 2's committed-run latency (6 887 ms) is 2.2× the
baseline midpoint; its lightest run (4 224 ms) is 1.35× the baseline max.
The dominant component of Test 2's latency is the single backend init
(2 313–7 400 ms in this corpus vs 773–1 555 ms normal load) — i.e. the
residual cost is essentially **one spawn + forward + validate + classify**,
the same order as a successful cold call, plus millisecond-scale classify
overhead.

**(d) The exact error surfaced to the caller — VERBATIM (committed run).**
The outcome is a `ToolCallResult` whose `result` is the stringified
`CallToolResult`:

```
meta=None content=[TextContent(type='text', text="Invalid structured content returned by tool add: 'sum' is a required property\n\nFailed validating 'required' in schema:\n    {'properties': {'sum': {'type': 'number',\n                            'description': 'The sum of a and b'}},\n     'required': ['sum'],\n     'type': 'object'}\n\nOn instance:\n    {'result': 5.0}", annotations=None, meta=None)] structured_content=None is_error=True result_type='complete'
```

The embedded text content, verbatim (the full schema-validation error):

```
Invalid structured content returned by tool add: 'sum' is a required property

Failed validating 'required' in schema:
    {'properties': {'sum': {'type': 'number',
                            'description': 'The sum of a and b'}},
     'required': ['sum'],
     'type': 'object'}

On instance:
    {'result': 5.0}
```

**Assessment of (d): the error is still attributable and the schema text is
preserved verbatim, but the caller-visible SHAPE is degraded.** Test 1
delivers an `ErrorResult` whose `message` is the clean
`MCPError: Error executing add: <schema error>` string; Test 2 delivers a
`ToolCallResult` whose `result` is a pydantic repr wrapping the same text.
ToolRegistry 0.15.0 produces `ErrorResult` only from a raised exception —
and any exception through `_call_persistent` is what fires the reconnect —
so the classification cannot have both no-reconnect AND `ErrorResult`
without changing ToolRegistry itself (out of scope). Callers that branch on
`isinstance(outcome, ErrorResult)` would mis-handle the classified failure.
This is finding §9.2.

### Test 3 — real connection failure (proxy killed mid-call) still retries — **PASS**

Setup: `proxy_classified.py`, healthy backend
(`schema_mode=conforming`, `response_mode=conforming` — no drift). The
harness starts the call in a thread, waits for `backend_spawn_start` in the
proxy log, SIGKILLs the persistent proxy (via `PROXY_PID_FILE`), and joins.

| Observation | Result | Evidence |
|---|---|---|
| Reconnect-retry fired? | **YES** — `proxy_processes=3` (registration + killed persistent + fresh persistent), `reconnect_fired=True` | `TEST3_PROXY_STARTED` (3 pids) |
| Backend spawns | **2** (be-1 under the killed proxy; be-1 under the fresh proxy) | `TEST3_SPAWN_COUNTS backend_spawn_count=2` |
| Final caller-visible outcome | **Success `'5.0'`** — the fresh proxy + respawned backend completed the retried call | `TEST3_OUTCOME result='5.0'` |
| Classifier swallowed it? | **No** — `backend_schema_validation_failed_count=0`, `classified_response_count=0` | `TEST3_SPAWN_COUNTS` |
| Latency | 3 173–8 613 ms across runs (the killed call is retried by the fresh proxy) | `TEST3_INVOKE_THREAD_DONE delta_ms=...` |

**The fix did not overcorrect at the ToolRegistry layer:** a genuine
connection-level failure still triggers the reconnect-retry exactly as
before, and the retried call recovers.

### Supplementary Test 3B — backend killed mid-call: the proxy's OWN retry still fires — **PASS**

Same setup as Test 3 but the **backend** process is killed (via
`BACKEND_PID_FILE`) instead of the proxy, exercising
`proxy_classified.py`'s internal `BackendClient.call` respawn path.

| Observation | Result | Evidence |
|---|---|---|
| Proxy-internal retry fired? | **YES** — `backend_call_failed ... type=MCPError msg=MCPError(-32000, 'Connection closed', None) attempt=1 respawning` then `backend_call_retry_succeeded` | `logs/test-3b-proxy-retry-proxy.log` |
| Backend spawns | **2** (be-1 killed, be-2 respawned by the proxy) | `TEST3B_SPAWN_COUNTS backend_spawn_count=2` |
| ToolRegistry reconnect fired? | **NO** — the proxy recovered internally (`proxy_processes=2`, `reconnect_fired=False`) | `TEST3B_SPAWN_COUNTS` |
| Classifier swallowed it? | **No** — `backend_schema_validation_failed_count=0`; the failure surfaced as `MCPError(-32000)`, NOT the schema-validation `RuntimeError` | `TEST3B_SPAWN_COUNTS`; `TEST3B_FAILURE_EVENT` |
| Final caller-visible outcome | Success `'5.0'` (5 583 ms) | `TEST3B_OUTCOME result='5.0'` |

**The fix did not overcorrect at the proxy layer either:** genuine
connection failures (raised as `MCPError(-32000, 'Connection closed')`) are
routed to the unchanged respawn-retry path and recover; only the
schema-validation `RuntimeError` signature is classified terminal.

## 6. Timing comparison — the quantified before/after

All times in milliseconds; per-run `init_ms` logged so load inflation is
visible. The committed corpus is run 5; "range" covers every successful run.

| Event | Committed run (ms) | Range (ms) | Backend spawns | Persistent proxies | Reconnect fired |
|---|---|---|---|---|---|
| Test 1 control (drift failure, ORIGINAL proxy) | 27 330 | 12 176–42 518 (n=4) | **4** | **2** (+1 registration) | **YES** |
| Test 2 classified (drift failure, MODIFIED proxy) | 6 887 | 4 224–14 471 (n=5) | **1** | **1** (+1 registration) | **NO** |
| Test 3 connection failure (MODIFIED proxy, proxy killed) | 8 613 | 3 173–8 613 (n=4) | 2 | 2 (killed + fresh) | YES (expected) |
| Test 3B connection failure (MODIFIED proxy, backend killed) | 5 583 | 5 583 (n=1) | 2 (proxy retried) | 1 | NO (proxy recovered) |
| #213 Test B success baseline (reference) | — | 1 810–3 124 (n=3, normal load) | 1 | 1 (+1 registration) | NO |

Test 1 `init_ms` (committed run): 2762.6 / 2975.3 / 3246.4 / 5930.1.
Test 2 `init_ms` (committed run): 3141.1 — a single spawn.

## 7. The central claim — explicit YES/NO

> Does classifying schema-validation failure as a terminal application error
> (returning a normal MCP tool-error response and skipping the proxy's own
> respawn for that class) eliminate the compounding — the 4x spawn
> multiplier?

**YES — the compounding is eliminated, with evidence.**

* Spawn count per failed call: **4 → 1** (Test 1 vs Test 2, every run).
  The two retry layers each paid 2 spawns in the control; after
  classification neither pays any (proxy: classified terminal before its
  respawn; ToolRegistry: `_call_persistent` returned normally, so
  `connection.py:106` never ran).
* Persistent proxy processes per failed call: **2 → 1**.
* Reconnect-retry: fired in every control run, **never** in any Test 2 run.
* Failure latency: **12 176–42 518 ms → 4 224–14 471 ms**; matched-run ratio
  **0.25–0.43** (Test 2 is 25–43 % of the control), i.e. classification
  removes ~57–75 % of the failure latency on top of removing 75 % of the
  spawns.

**Residual single-failure cost:** one backend spawn, one persistent proxy,
one forwarded call, one classify + `isError` conversion. Absolute range
4 224–14 471 ms on this loaded host (committed run 6 887 ms), dominated by
the unavoidable single backend init. Against the #213 successful-call
baseline (1 810–3 124 ms under normal load): 1.35–2.2× the baseline — the
same order as a successful cold call, not a 4× failure-class cost.

**Boundary of the claim (scoping finding).** This classification works where
the **proxy's own** client detects the drift (Test C: backend declares the
conforming schema but returns a diverging shape). It does NOT cover #213's
Test C2 variant, where the backend drifts consistently (declaration +
behaviour both `{"result": ...}`) and only ToolRegistry's client sees the
mismatch: there the proxy forwards a conforming-looking response, the
`RuntimeError` is raised inside ToolRegistry's client, and
`connection.py:106` still fires (2 spawns, 2 proxies — #213's C2 numbers).
Classification alone therefore removes the compounding for the primary
variant but cannot reach the C2 case without a proxy-side live-schema check
(part of the heavier mitigation, out of scope).

## 8. Verbatim error text

**Test 1 (control) — `ErrorResult.message`, VERBATIM (committed run):**

```
MCPError: Error executing add: Invalid structured content returned by tool add: 'sum' is a required property

Failed validating 'required' in schema:
    {'properties': {'sum': {'type': 'number',
                            'description': 'The sum of a and b'}},
     'required': ['sum'],
     'type': 'object'}

On instance:
    {'result': 5.0}
```

**Test 2 (classified) — caller-visible `ToolCallResult.result`, VERBATIM
(committed run)** — see §5 Test 2 (d) for the un-repr'd embedded text, which
is the same jsonschema detail. The `is_error=True` flag is present on the
`CallToolResult`.

## 9. Findings (interpretation, distinct from observations)

1. **The compounding is caused by the exception path, not by retry logic per
   se.** The only thing `connection.py:106` needs to fire is *any* exception
   from `_client.call_tool`. Returning a normal `CallToolResult` — even an
   error result — bypasses it entirely. The empirical probes and Test 2 both
   confirm: an `isError=True` response travels the full ToolRegistry call
   chain without a single reconnect.
2. **Classification trades the error TYPE for the spawn cost.** ToolRegistry
   0.15.0 builds `ErrorResult` only from a raised exception, and the raise is
   exactly what fires the reconnect. So a proxy-only classification cannot
   deliver both "no reconnect" AND "`ErrorResult`": the caller receives a
   `ToolCallResult` whose `result` is a pydantic repr wrapping the full
   schema-error text. The error stays attributable (verbatim text present,
   `is_error=True` flag present), but callers branching on `ErrorResult`
   would mis-handle it. A clean `ErrorResult` with no reconnect requires a
   change at the ToolRegistry integration layer (`_post_process_result` /
   `_finalize_result` treating isError results as errors) — out of scope
   here, and a candidate for the epic's next iteration.
3. **The classifier boundary is clean and empirically verified.** The SDK's
   output-schema validation raises `RuntimeError("Invalid structured content
   returned by tool ...")`; genuine connection failures raise
   `MCPError(-32000, 'Connection closed')` (probe B, Test 3B). Tests 3 and
   3B prove genuine failures at BOTH layers (ToolRegistry reconnect, proxy
   respawn) still fire and recover — the fix did not overcorrect.
4. **Classification does not cover the consistently-drifted (C2) variant.**
   When the backend's declaration and behaviour are internally consistent
   and only the cached manifest is stale, the proxy passes the response
   through and ToolRegistry's client raises — `connection.py:106` fires
   regardless of proxy classification (2 spawns, 2 proxies, #213 C2). The
   heavier mitigation (fallback live-schema fetch / periodic revalidation)
   is the only mechanism that reaches that variant.
5. **The residual single-failure cost after classification is bounded and
   roughly equal to a successful cold call** (one spawn + forward), i.e. the
   cost the identifier-first brief originally hypothesised as "one wasted
   spawn".

## 10. Conclusion — does classification alone resolve the cost problem?

**Classification alone removes the compounding for the primary drift
variant and brings the cost down to the single-spawn level the original
brief hypothesised — but a gap remains, and its size is the caller-visible
degradation plus the C2 variant, not the spawn cost.** After classification,
a drift failure costs 1 backend spawn / 1 persistent proxy / 4 224–14 471 ms
(committed run 6 887 ms) instead of 4 spawns / 2 proxies / 12 176–42 518 ms
— a 75 % spawn reduction and a 57–75 % latency reduction (matched-run
ratio 0.25–0.43), leaving a residual failure latency ~1.35–2.2× the #213
success baseline that is dominated by the single unavoidable backend init.
So on cost, the heavier mitigation now has **at most the single-spawn
residual (one init, ~2.3–7.4 s on this host; ~0.8–1.6 s under normal load)
plus the ~0 ms classify overhead** left to save — it can no longer save the
three extra spawns and the extra proxy, because classification already
eliminated them. What the heavier mitigation would still buy is (a) turning
the failure into a success by re-validating against the live backend schema
(eliminating even the residual single wasted spawn), (b) reaching the C2
consistently-drifted variant that classification cannot see, and (c) a clean
`ErrorResult`/success shape instead of the `ToolCallResult`-with-repr
degradation (§9.2). If the identifier-first proposal requires bounded
single-spawn cost, classification alone is sufficient; if it requires the
failure to be a clean, typed error (or the call to succeed at all in the C2
variant), the heavier mitigation is still required, with the quantified
residual above as its remaining target.

## 11. Transport scope

Every finding in this report is for **stdio transport only** — stdio for
both the ToolRegistry→proxy hop and the proxy→backend hop. Streamable HTTP,
SSE, and websocket transports were **not** tested (matching #196/#213
scope).

## 12. Log index

All logs under `research/toolregistry-lazy-mcp/retry-classification/logs/`.
The committed corpus is the last full driver run (run 5); earlier runs'
numbers are quoted in §5/§6 with per-run ranges.

| Phase | Proxy log | Harness log |
|---|---|---|
| Test 1 (control) | [`test-1-control-proxy.log`](logs/test-1-control-proxy.log) | [`test-1-control-harness.log`](logs/test-1-control-harness.log) |
| Test 2 (classified) | [`test-2-classified-proxy.log`](logs/test-2-classified-proxy.log) | [`test-2-classified-harness.log`](logs/test-2-classified-harness.log) |
| Test 3 (proxy killed) | [`test-3-connection-proxy.log`](logs/test-3-connection-proxy.log) | [`test-3-connection-harness.log`](logs/test-3-connection-harness.log) |
| Test 3B (backend killed) | [`test-3b-proxy-retry-proxy.log`](logs/test-3b-proxy-retry-proxy.log) | [`test-3b-proxy-retry-harness.log`](logs/test-3b-proxy-retry-harness.log) |

The harness logs contain the full interleaved stream (`HARNESS|`, `PROXY|`,
`BACKEND|` prefixed lines), including the `INVOKE ... delta_ms` measurement
lines, `*_SPAWN_COUNTS` counters, and `backend_up ... init_ms` values per
spawn. Proxy-only logs are written by each proxy process via
`PROXY_LOG_FILE`; multiple `proxy_started` blocks in one log (different
pids) are themselves the reconnect evidence (Test 1 vs Test 2).
