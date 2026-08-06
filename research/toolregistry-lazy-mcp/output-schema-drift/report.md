---
title: Output-Schema Drift Between a Cached Manifest and a Live Backend in the ToolRegistry Lazy-MCP Proxy — Evidence
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
  - research/toolregistry-lazy-mcp/report.md
  - research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md
implements:
implemented_by:
supersedes:
superseded_by:
last_updated: 2026-08-06
---

# Research Finding: Output-Schema Drift Between a Cached Manifest and a Live Backend

## 1. Purpose and question

This is an **evidence-only characterisation task**, not a system to ship and
not a mitigation to build. The single question, flagged by reviewers of #196
(hy3 in #199, big-pickle in #205) as the most consequential open question for
the identifier-first tool-calling proposal:

> In the lazy-MCP proxy architecture, the cached manifest declares an
> `output_schema` (e.g. an object `{"sum": <number>}`) but the live backend's
> actual response does not conform (e.g. returns `{"result": <number>}`).
> The mismatch is only detectable against the RESPONSE — so the backend must
> already be running (spawn cost already paid) before any mismatch can be
> found. Is that true empirically? What exactly happens at runtime, and is
> there any recovery path?

The deliverable is pass/fail evidence per observation, timings, full logs,
verbatim exception text, and a source read of every layer's refresh /
invalidation behaviour — **not** a working product and **not** a mitigation.

Throughout this report, **observations** (what the logs and timings show,
with file/line references) are kept distinct from **findings** (interpretation).

## 2. Environment and exact versions

Same pinned venv as #196 (reused, not reinstalled):

| Component | Version | Notes |
|---|---|---|
| `toolregistry` | **0.15.0** | `pip install toolregistry[mcp]==0.15.0`; MCP extra is named `mcp` |
| `mcp` (Python SDK) | **2.0.0** | Direct dependency of the `[mcp]` extra; re-confirmed live 2026-08-06 via `importlib.metadata.version("mcp")` |
| `pydantic` | 2.13.4 | transitive |
| `jsonschema` | (mcp dependency) | used for input-schema validation in Test D, exactly as `mcp/client/session.py` uses it |
| Python | 3.10.12 | venv at `/tmp/toolregistry-venv` (NOT committed) |
| Platform | Linux | single host, all processes local |

All tests ran with the transport pair **stdio → proxy → stdio → backend**
(identical to #196's scope). ToolRegistry's persistent MCP connection is
lazy: no backend process exists between registration and the first tool call.

## 3. Artifacts and how to reproduce

All new artefacts live in a clean sibling directory,
`research/toolregistry-lazy-mcp/output-schema-drift/`, so nothing in the #196
corpus was modified.

| File | Role |
|---|---|
| `backend.py` | Extended backend (delta from #196): the `add(a, b)` tool's **declared** `output_schema` is controlled by `BACKEND_SCHEMA_MODE` (`none` / `conforming` / `diverging`), and its **returned** shape by `BACKEND_RESPONSE_MODE` (`text` / `conforming` / `diverging` / `bare`). A second tool `multiply(a, b)` has **no** `output_schema` in any mode (the unrelated tool for Test F). |
| `proxy.py` | #196 proxy copied with exactly two deltas (both documented in its docstring): (1) `PROXY_MANIFEST` env var selects the cached manifest per test; (2) all `BACKEND_*` env vars are passed through to the backend subprocess. Everything else — lazy spawn on first `tools/call`, one reused session, respawn + single retry on forwarded-call failure, no notifications — is byte-for-byte the #196 behaviour. |
| `capture_manifest.py` | Captures `tools/list` from the drift backend into `manifest.json` (schema_mode=conforming) or `manifest-null.json` (schema_mode=none). |
| `manifest.json` | Cached manifest used by Tests B–F/C2/C3: `add` declares `output_schema={"type":"object","properties":{"sum":{"type":"number"}},"required":["sum"]}`, `multiply` declares `output_schema=null`. |
| `manifest-null.json` | Cached manifest used by Test A: both tools declare `output_schema=null` (reproduces #196's `manifest.json:30`). |
| `tests/run_drift.py` | Driver: runs each phase as a clean subprocess, captures `logs/<phase>-harness.log`. |
| `tests/common_drift.py` | Shared helpers (based on #196's `common.py`): transport builder with manifest + backend mode envs, `invoke_recorded` (records `ErrorResult.message` **verbatim**), proxy/backend event counters, input-schema validator. |
| `tests/phase_a.py` … `phase_f.py`, `phase_c2.py`, `phase_c3.py` | One clean session per phase (fresh registry, fresh proxy processes). |
| `logs/` | One proxy log + one harness log per phase. The harness log also carries inherited proxy/backend stderr, so the full per-session stream is captured. |

Reproduce (versions pinned to the exact installed set — `toolregistry` 0.15.0
and `mcp` 2.0.0, re-confirmed live in the venv on 2026-08-06):

```bash
cd research/toolregistry-lazy-mcp/output-schema-drift
BACKEND_SCHEMA_MODE=conforming /tmp/toolregistry-venv/bin/python capture_manifest.py   # -> manifest.json
BACKEND_SCHEMA_MODE=none       /tmp/toolregistry-venv/bin/python capture_manifest.py   # -> manifest-null.json
/tmp/toolregistry-venv/bin/python tests/run_drift.py
```

Each phase runs as its own clean session; Tests E and F intentionally share a
session *within* their phase scripts (E: the repeat happens in the same
session as its reproduced Test C call; F: the unrelated tool is called in the
same session as the failure).

## 4. Test results

Every phase passed (exit 0). "PASS" for the failure tests means *the
characterised behaviour occurred as expected*, not that the system worked.

### Test A — baseline reconfirmation (`output_schema: null`) — **PASS**

Setup: cached manifest `manifest-null.json`; backend `schema_mode=none`
(declares no schema, exactly #196's `manifest.json:30`) and
`response_mode=diverging` — the backend returns structured content
`{"result": n}`, the **same shape that fails in Tests C/D**.

| Observation | Result | Evidence |
|---|---|---|
| Does registration succeed? | Yes. | `logs/test-a-harness.log` `TESTA_REGISTER result=ok` |
| Does the call succeed despite the non-conforming returned shape? | **Yes.** `add(2,3)` → `'5.0'` in **2475 ms** (committed run; 1847–2475 ms across runs). No validating client (proxy's client against the live listing, ToolRegistry's client against the cached manifest) validates when no `output_schema` is declared. | `logs/test-a-harness.log` `INVOKE|add(2,3)...delta_ms=2475...ok=True`; `TESTA_PROXY backend_spawn_count=1 backend_up_count=1 response_count=1 proxy_processes=2` |
| Contrast with C/D | The **identical** `{"result": n}` response shape succeeds here and fails in C/D solely because of the cached `output_schema`. | this report, §4 C/D |

**Verdict:** reproduces #196's null-schema baseline and sharpens it: even a
*structured, non-conforming* response succeeds when the cached manifest
declares no output schema.

### Test B — matching schema — **PASS**

Setup: cached `manifest.json` (conforming `{"sum": ...}`); backend
`schema_mode=conforming`, `response_mode=conforming` (returns
`structured_content={"sum": n}`).

| Observation | Result | Evidence |
|---|---|---|
| Call succeeds cleanly with a declared output schema? | **Yes.** `add(2,3)` → `'5.0'`. | `logs/test-b-harness.log` `INVOKE|add(2,3)...ok=True` |
| Success latency (for the C comparison) | **2995 ms** end-to-end in the committed run (all runs: 1810–3124 ms, n=3). | `logs/test-b-harness.log` |
| Spawn cost | 1 backend spawn, 1 forward, 2 proxy processes (registration proxy + persistent proxy, as documented in #196). | `TESTB_PROXY backend_spawn_count=1 backend_up_count=1 forward_count=1 response_count=1 proxy_processes=2` |

**Verdict:** with the cached schema matching the backend's response, the
identifier-first call works end-to-end.

### Test C — diverging schema, first exposure — **PASS** (failure characterised)

Setup: same cached `manifest.json` as B; backend `schema_mode=conforming`
(still **declares** the conforming schema) but `response_mode=diverging`
(actually returns `structured_content={"result": n}`) — i.e. the brief's
"change the backend's runtime return shape without re-capturing".

**(a) Exact exception type and message, VERBATIM** (the `ErrorResult.message`
that `registry.invoke` returned; ToolRegistry 0.15.0 never raises):

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

The caller-visible type is **`MCPError`**, not `RuntimeError`. The
`RuntimeError` from `mcp/client/session.py:1096-1100` occurred **inside the
proxy** (the proxy's own client validated the backend's response against the
backend's *live* declared schema and failed); the stdio dispatcher converted
it to a JSON-RPC error with `code=0, message=str(e)` (source:
`mcp/shared/jsonrpc_dispatcher.py:755-757`, the non-MCPError catch-all), and
ToolRegistry's client raised `MCPError` with that message. The schema-error
text is preserved on the wire, but the type is a generic protocol error.

**(b) WAS THE BACKEND SPAWNED BEFORE THE FAILURE? — YES (key measurement).**

| Observation | Value | Evidence |
|---|---|---|
| Harness call start epoch | 1785994055335 | `logs/test-c-harness.log` `INVOKE` `start_ms` |
| First `backend_spawn_start` | 1785994057819 → **2484 ms after call start** | `TESTC_WAS_SPAWNED_BEFORE_FAILURE`; `logs/test-c-proxy.log` |
| First drift detection (`backend_call_failed` RuntimeError) | 1785994061182 (5847 ms after call start) — only after `backend_up` (1785994061025) + `forward` + response-validation | `logs/test-c-proxy.log` (`backend_up` rel 3220, `backend_call_failed` rel 3377 within proxy A) |
| Failure surfaced to caller | 1785994079072 → **23737 ms after call start** (this run was machine-load-affected; see (c)) | `INVOKE` `end_ms` |

The backend had to be spawned, respond, and only then was the mismatch
detectable. There is no pre-spawn signal: at capture time the backend declared
the conforming schema and returned conforming content; the drift is invisible
until actual response bytes arrive.

**(c) Elapsed ms and cost.** The committed run measured 23737 ms end-to-end;
two earlier runs under normal load measured 6054 ms and 7280 ms → **6054–23737
ms (n=3)**. The committed run captured a machine-load period: its backend
`init_ms` were 3205.2 / 4144.3 / 3413.1 / 4151.9 ms versus the 773.0–1555.7 ms
range of every other run in the corpus, so all absolute numbers in that run
are inflated ~3×. The event sequence, exception, and spawn counts are
identical to the normal-load runs. Under normal load the drift failure takes
**roughly 2.3× the successful-with-schema baseline** (see §5); the load-affected
sample shows the upper tail can be far worse, which is itself a cost
observation. Compare: Test B success 1810–3124 ms; #196 cold-start 2155–2761
ms (n=3, observed max 2761 ms).

**(d) How it surfaces; retry layers fired.** It surfaces **cleanly** — an
`ErrorResult` after 7.3 s under normal load (23.7 s in the load-affected
committed run), no hang, no timeout. But the cost is **four backend spawns
and two persistent proxy processes** for one caller-visible attempt
(observations from `logs/test-c-proxy.log`; run-3 pids/init values):

1. Proxy A (pid 2082215) spawns backend be-1 (init 3205.2 ms) → response
   fails validation → **proxy-internal retry**: proxy A respawns be-2
   (init 4144.3 ms) → fails again → proxy A raises.
2. **ToolRegistry's own reconnect-retry fires** (`connection.py:106`):
   it closes proxy A, spawns a **fresh proxy process** (pid 2083433),
   which spawns be-1 again (init 3413.1 ms) → fails → proxy-internal retry
   be-2 (init 4151.9 ms) → fails → second `MCPError` propagates to the caller.

Counts: `backend_spawn_count=4`, `backend_up_count=4`,
`backend_call_failed_count=4`, `retry_succeeded_count=0`, `proxy_processes=3`
(registration proxy + 2 persistent). Every one of the four backend spawns was
**wasted**. This is a material amplification of the naive
"one wasted spawn" hypothesis: in this architecture the drift failure trips
**both** retry layers, each of which pays its own spawn.

### Test D — input-valid / output-invalid isolation — **PASS**

Setup identical to C. Before the call, the harness explicitly validated
`{"a": 2, "b": 3}` against the **cached manifest's input schema** using
jsonschema (the same library/mechanism `mcp/client/session.py` uses for
outputs).

| Observation | Result | Evidence |
|---|---|---|
| Input valid against cached input schema? | **Yes** — `input_valid=True, detail=valid per cached input schema`. | `logs/test-d-harness.log` `TESTD_INPUT_VALIDATION` |
| Was the backend spawned before the failure? | **Yes** — first spawn 1192 ms after call invocation (committed run); 4 spawns / 3 proxies total. | `TESTD_SPAWNED_BEFORE_FAILURE`; `TESTD_SPAWN backend_spawn_count=4 ... proxy_processes=3` |
| Failure after the backend responded? | Yes — identical `MCPError` message to C (6605–7657 ms across runs; committed run 7657 ms). | `TESTD_ERROR_RESULT message_verbatim=...` |

**Isolation conclusion:** this is **not** an input-validation failure and
validate-before-spawn cannot prevent it. Input-side validate-before-spawn lets
the call through (input valid), the backend IS spawned, and the call fails
only after the backend responds with a non-conforming shape. Test D exists
only to isolate this claim, not to retest input validation.

### Test E — determinism + recovery — **PASS** (deterministic, no recovery)

Same setup as C. Call 1 reproduces the C failure; call 2 immediately repeats
the identical call **in the same session**.

| Observation | Result | Evidence |
|---|---|---|
| Call 1 | Fails: `MCPError: Error executing add: Invalid structured content returned by tool add: 'sum' is a required property...` (verbatim same as C), 7269 ms (committed run; 6482–7269 ms across runs), 4 backend spawns, 3 proxies. | `logs/test-e-harness.log` `TESTE_CALL1_MESSAGE_VERBATIM`; `TESTE_CALL1_SPAWN_COUNT` |
| Call 2 (immediate repeat) | **Fails identically.** Same verbatim message, 6731 ms (committed run; 5528–6731 ms across runs), **4 more** backend spawns (total 8) and 1 more proxy (total 4). | `TESTE_CALL2_SPAWN_COUNT backend_spawn_count=8 proxy_processes=4`; `TESTE_DETERMINISM call1_failed=True call2_failed=True identical_message=True` |
| Any self-healing? | **None.** Every repeat pays the full double-retry cost again and fails the same way. | this table |

**Source read — is there ANY refresh / invalidation mechanism?** Explicit
statement, so this is not left untested by omission:

* **ToolRegistry (0.15.0):** no refresh / re-sync / invalidation API for
  MCP-registered tool schemas. `grep -rn "refresh|reload|re-register|invalidat|list_changed|update_schema"` over `toolregistry/integrations/mcp/` and
  `toolregistry/_mixins/registration.py` → **zero matches**. The public API
  surface has no such method (`register_from_mcp` is the only registration
  path, and re-running it captures from the proxy, which serves the same
  cached manifest). The only resilience behaviour is the reconnect-and-retry
  in `toolregistry/integrations/mcp/connection.py:106`, which respawns the
  proxy and retries — proven by Test E to make the failure **worse**, not
  better.
* **The proxy:** serves the static `manifest.json` for every connection
  forever. No re-capture, no invalidation, no notification of change
  (`tools.listChanged` = false, per #196 §6 item 1a). This drift proxy adds
  nothing on that axis.
* **The mcp SDK client:** `validate_tool_result` re-issues `tools/list` on an
  output-schema cache miss (`mcp/client/session.py:1086`) and
  `_absorb_tool_listing` re-caches whatever the listing declares (session.py:
  1273-1276). In the proxy architecture that re-list is answered from the
  **same stale cached manifest**, so the re-absorbed schema is identical — the
  mechanism *looks* like a refresh but is a no-op against a cached-manifest
  proxy. In Test C the re-list never even runs at ToolRegistry level (the call
  fails with `MCPError` before any successful result); in Test C2 it runs and
  re-absorbs the stale schema, which is what triggers the RuntimeError.
* **Lexicon-CID-based cache invalidation:** **no such mechanism exists in the
  current implementation.** A repo-wide search for `Lexicon|lexicon|CID|
  cid-based|invalidation|cache_invalidate` returns zero matches, and neither
  #196's proxy nor this drift proxy contains any such logic. Stated
  explicitly: nothing was left uninvestigated because a mechanism appeared to
  exist.

**Verdict:** the failure is **deterministic** and **no recovery/refresh
mechanism exists** in ToolRegistry, the proxy, the SDK's use of it, or the
repository.

### Test F — blast radius — **PASS** (contained)

Same setup as C. After `add` fails, call the unrelated `multiply(4, 5)`
(declared with no output schema in both the cached manifest and the backend),
then `add` again.

| Observation | Result | Evidence |
|---|---|---|
| `add(2,3)` fails | Yes — identical `MCPError` (6061–8484 ms across runs; committed run 7023 ms). | `logs/test-f-harness.log` `TESTF_ADD_ERROR` |
| Unrelated tool after the failure | **Succeeds normally** — `multiply(4,5)` → `'20.0'` in **1091 ms** (committed run; 923–1335 ms across runs). | `INVOKE|multiply(4,5)...ok=True` |
| Same failing tool again after the unrelated success | Fails again with the same drift error (message shows `On instance: {'result': 2.0}` for the new arguments). | `INVOKE|add(1,1)...ok=False` |
| Registry state after the failure | Discovery intact: `list_tools=['add','multiply']`; the registry connection is not left bad (multiply used the reconnected session successfully). | `TESTF_AFTER list_tools=['add','multiply']` |

**Verdict:** blast radius is **contained to the failing tool/call**. The
drift failure does not poison registry state, does not block the unrelated
tool in the same session, and does not permanently break the connection. The
only cost is the wasted spawns per failing call (deterministic, per Test E).

### Supplementary: Test C2 — pure cached-manifest drift — **PASS** (failure characterised)

Setup: same cached `manifest.json`; backend `schema_mode=diverging` **and**
`response_mode=diverging` — the backend's own declaration and its responses
are internally *consistent* (both `{"result": ...}`); only the **cached
manifest** is stale. This is the purest identifier-first drift scenario and
the one the #196 grounding (session.py:1096-1100) describes.

| Observation | Result | Evidence |
|---|---|---|
| Exception type + message, VERBATIM | **`RuntimeError: Error executing add: Invalid structured content returned by tool add: 'sum' is a required property`** … (same jsonschema detail, `On instance: {'result': 5.0}`). The `RuntimeError` now surfaces **directly** at the caller, because the proxy's client validated against the backend's *live* (diverging) schema and passed the response through (`response tools/call ... ok=True`); ToolRegistry's client then validated against the **cached** schema and raised. | `logs/test-c2-harness.log` `TESTC2_ERROR_RESULT`; `logs/test-c2-proxy.log:13` (`response ok=True`) then `:14` (post-call `tools/list` re-list, `backend_connected=True`) |
| Cost | 2 backend spawns (one per persistent proxy), 2 proxies, **no** proxy-level `backend_call_failed` (the proxy never saw a failure). 5871–5913 ms under normal load (n=2); committed run 9008 ms (load-affected). | `TESTC2_SPAWN backend_spawn_count=2 ... backend_call_failed_count=0 proxy_processes=3` |
| The SDK's cache-miss re-list in action | The ToolRegistry client's first call triggered `list_tools` (served from the cached manifest) before validating → the stale `{"sum":...}` schema was re-absorbed → RuntimeError. This confirms the "refresh" mechanism is a no-op against a cached-manifest proxy. | `logs/test-c2-proxy.log:14,24` |

**Verdict:** when the backend drifts *consistently* (declaration + behaviour),
the drift is detected at ToolRegistry level as the exact `RuntimeError` the
brief predicted — still only after spawn + response, still doubled by the
reconnect-retry (2 proxies), but at **half** the spawn cost of Test C (2 vs 4
backend spawns) because the proxy's own validation does not fire.

### Supplementary: Test C3 — "bare number" non-conforming shape — **PASS** (failure characterised)

Setup: same cached `manifest.json`; backend `schema_mode=none` (so the proxy
passes the response through) and `response_mode=bare` (returns
`structured_content=5.0`, a bare JSON number — the brief's alternative
non-conforming shape).

| Observation | Result | Evidence |
|---|---|---|
| Exception type + message, VERBATIM | **`MCPError: Error executing add: Handler returned an invalid result`** — an **opaque** protocol error with no schema detail. | `logs/test-c3-harness.log` `TESTC3_ERROR_RESULT` |
| Why so opaque | The **backend's own server** rejects `structured_content=5.0` before any schema validation runs: protocol 2025-11-25 restricts `structured_content` to a JSON *object* (`mcp/types.py` `CallToolResult`), so the backend's response serialization fails (`mcp/server/runner.py:385-386` → `MCPError(-32603, 'Handler returned an invalid result')`). The proxy's client sees that MCPError and the standard retry layers fire. | `logs/test-c3-proxy.log:13` `backend_call_failed type=MCPError msg=MCPError(-32603, 'Handler returned an invalid result', None)` |
| Cost | 4 backend spawns, 2 persistent proxies, 5943–6730 ms under normal load (n=2); committed run 8117 ms (load-affected). | `TESTC3_SPAWN backend_spawn_count=4 proxy_processes=3` |

**Verdict:** the "bare number" variant is a **harder** failure than object
drift: it never even reaches output-schema validation. It is a
protocol-conformance failure that surfaces as an opaque, non-actionable
`MCPError` after the same double-retry cost. This is the worst diagnostic
outcome of the three shapes tested.

## 5. Timing comparison — the quantified "wasted cost"

All times in milliseconds, epoch-derived from log `epoch_ms` fields
(cross-process deltas are wall-clock accurate to ±1 ms scheduling noise).
The committed corpus is the `run_drift.py` run; the "across runs" column
covers every run made for this task (n=3 for most phases; the committed run
was machine-load-affected — its backend `init_ms` were 3205–4152 ms vs the
773.0–1555.7 ms of every other run — so its absolute numbers are ~3× inflated
but its event sequence, exception, and spawn counts are identical). #196
cold-start numbers are quoted from the #196 report (§5): **2155–2761 ms**
(n=3, observed max **2761 ms**).

| Event | Committed run (ms) | Across runs (ms) | Backend spawns | Persistent proxies |
|---|---|---|---|---|
| Test A success (null schema, diverging shape) | 2475 | 1847–2475 (n=3) | 1 | 1 (+1 registration) |
| Test B success (conforming schema, conforming shape) | 2995 | 1810–3124 (n=3) | 1 | 1 (+1 registration) |
| #196 cold-start first call (success, null schema) | — | 2155–2761 (n=3, max 2761) | 1 | 1 (+1 registration) |
| **Test C drift failure** (backend declares conforming, returns diverging) | 23737 (load-affected) | **6054–7280 normal load (n=2); 23737 worst** | **4** | **2** (+1 registration) |
| Test C2 drift failure (backend drifted consistently) | 9008 (load-affected) | 5871–5913 normal (n=2) | 2 | 2 (+1 registration) |
| Test C3 bare-number failure | 8117 (load-affected) | 5943–6730 normal (n=2) | 4 | 2 (+1 registration) |
| Test D failure (same as C, input proven valid) | 7657 | 6605–7657 (n=3) | 4 | 2 (+1 registration) |
| Test E call 1 failure | 7269 | 6482–7269 (n=3) | 4 | 2 (+1 registration) |
| Test E call 2 failure (repeat) | 6731 | 5528–6731 (n=3) | **4 more** | 1 more |
| Test F `add` failure | 7023 | 6061–8484 (n=3) | 4 | 2 (+1 registration) |
| Test F `multiply` success after failure | 1091 | 923–1335 (n=3) | 1 fresh backend (the failed `add` closed the proxy's backend session; multiply spawned `be-3` then succeeded) | 0 (same proxy reused) |
| Test F `add` again (still drifting) | 5013 | 4964–6845 (n=3) | **4 more** | 1 more |

Ratio against the same-day successful-with-schema baseline (Test B, normal
load, midpoints): C ≈ **2.3×**, C2 ≈ 1.9×, C3 ≈ 2.0×, D ≈ 2.3×, E call 2 ≈
2.0×. Ratio against #196's cold-start max (2761 ms): C ≈ **2.4×**, E call 2 ≈
2.1×. Against the minimum success (1810 ms): C ≈ **3.7×**.

The "wasted cost" of a drift failure under normal load is therefore
**roughly 2–4 backend spawns + 1 extra proxy process + 3.2–4.9 s of
additional latency** beyond a successful cold call — and each repeat pays it
again (Test E). Backend `init_ms` across the corpus ranged **773.0–1555.7 ms**
for all non-load-affected spawns (n=32); the load-affected run's spawns were
3205.2–4151.9 ms.

## 6. The central claim — explicit YES/NO

> Output-schema drift is only detectable AFTER backend spawn, so the spawn
> cost is unavoidable in this failure mode.

**YES, with evidence.** In every drift variant the mismatch was first detected
only after a backend had been spawned *and had responded*:

* Test C (committed run): first `backend_spawn_start` 2484 ms after call
  start; `backend_up` 5690 ms after call start; first drift detection
  (`backend_call_failed` RuntimeError) 5847 ms after call start — i.e.
  ~157 ms after the backend became ready, only after `forward` +
  response-validation; caller-visible failure at 23737 ms (load-affected
  committed run; 6054–7280 ms under normal load).
* Test C2: the proxy returned `response tools/call ... ok=True`; the
  `RuntimeError` was raised by ToolRegistry's client only *after* the
  response arrived and the post-call `tools/list` re-absorbed the stale
  cached schema.
* Test C3: the backend's own server rejected the bare number during response
  serialization — again only after the backend existed and produced a
  response.

No pre-spawn signal exists in any layer: the cached manifest is a static
snapshot, the backend's declaration and behaviour are only observable by
spawning it, and the SDK's "refresh" path (cache-miss `tools/list`) re-reads
the same stale cached manifest. **The backend must be running before any
mismatch can be found — confirmed empirically in every variant.**

## 7. Recovery / refresh — explicit statement (Test E)

**No recovery or refresh mechanism exists, and nothing works to recover.**
See §4 Test E source read: ToolRegistry has no schema-refresh API (grep:
zero matches; no such public method), the proxy serves the static manifest
forever, the SDK's cache-miss re-list re-absorbs the same stale schema from
the proxy, and there is **no Lexicon-CID-based cache-invalidation path** in
the current implementation (repo-wide search: zero matches). Test E shows the
failure is deterministic and repeats identically; each repeat pays the full
double-retry spawn cost. The only "mechanism" present — ToolRegistry's
reconnect-and-retry (`connection.py:106`) — actively multiplies the wasted
spawns instead of recovering.

## 8. Blast radius — explicit statement (Test F)

**Contained.** After a drift failure the registry connection is not left bad,
discovery still returns all tools, an unrelated tool (`multiply`) with a
matching manifest succeeds normally in the same session, and the failing tool
fails the same way on every subsequent call. The failure's blast radius is
the single failing tool/call plus the wasted spawns it triggers; it does not
poison the registry or block other tools.

## 9. Findings (interpretation, distinct from observations)

1. **Two validation points exist, and the drift can surface at either.** The
   proxy's own SDK client validates the backend response against the backend's
   **live** declared schema (Test C: fails there first, surfaces as
   `MCPError`), while ToolRegistry's client validates against the **cached**
   manifest schema (Test C2: fails there, surfaces as `RuntimeError`). The
   caller-visible error type therefore depends on *which layer's schema* is
   stale — the type itself is not a reliable drift signal.
2. **The failure is amplified by two retry layers, not one.** For every
   caller-visible drift failure the proxy-internal retry respawns the backend
   once, and ToolRegistry's reconnect-retry spawns a second proxy which
   respawns the backend again — **4 backend spawns + 2 persistent proxies per
   failed attempt** in the primary (C/D/E/F) case. The naive
   "one wasted spawn" reading of the architecture is wrong; the real cost is
   roughly 4× the spawn cost of a successful cold call.
3. **Diagnostics degrade as the drift gets "simpler".** Object-shaped drift
   keeps the full jsonschema text (C/C2), but a bare-number shape never
   reaches schema validation — the backend's own response serialization
   rejects it for protocol 2025-11-25 and the caller sees only the opaque
   `MCPError(-32603, 'Handler returned an invalid result')`.
4. **Input-side validate-before-spawn is orthogonal to this failure mode.**
   Test D proves the input is valid against the cached input schema; the call
   is let through and fails only after the backend responds. This is a
   *complementary* gap, not a contradiction of #196's input-side finding.
5. **The failure is deterministic, unbounded in repeats, and unrecoverable
   without a mechanism that does not exist** (no manifest revalidation, no
   fallback live-schema fetch, no Lexicon-CID invalidation anywhere in the
   current implementation).

## 10. Conclusion for the identifier-first proposal

The identifier-first proposal's efficiency claim (validate-before-spawn)
holds for **input** validation (#196) but **cannot** cover output-schema
drift: this corpus proves the drift is only detectable after the backend is
spawned and responds, the failure then costs roughly **2–4 backend spawns +
1 extra proxy process + 3–5 s** over a successful cold call per attempt under
normal load (Test C/D/E/F: 4 spawns, 2 proxies, 6054–8484 ms vs Test B
success 1810–3124 ms and #196 cold-start max 2761 ms; the worst observed
sample was 23.7 s under machine load), it repeats deterministically with no
recovery/refresh mechanism in any layer (Test E), and its blast radius is
contained to the failing tool (Test F). The failure surfaces either as a
generic `MCPError` (when the backend still declares the stale-compatible
schema, Test C) or as the raw `RuntimeError` (when the backend drifted
consistently, Test C2), and in the "bare number" case as an opaque
`Handler returned an invalid result` (Test C3). This task characterises only;
it recommends, it does not build:

**Verdict: not an acceptable bounded cost.** One wasted spawn with a clean,
actionable failure might be tolerable; what this corpus shows is 2–4 wasted
spawns per call, a protocol-level (not schema-level) error in the primary
variant, deterministic repetition with no recovery, and a dependency on
accidental consistency between the backend's declared schema and its actual
behaviour to even get the informative `RuntimeError`. The identifier-first
proposal therefore **requires a mitigation** — the minimal candidates being
periodic manifest revalidation against the live backend, or a fallback
live-schema fetch on mismatch (the backend is already running when the
mismatch is found, so a fallback re-list is cheap). These mitigations are
explicitly **not built** here, per scope.

## 11. Transport scope

Every finding in this report is for **stdio transport only** — stdio for both
the ToolRegistry→proxy hop and the proxy→backend hop. Streamable HTTP, SSE,
and websocket transports were **not** tested, and the conclusion must not be
read as covering them (matching #196's scope).

## 12. Log index

All logs under `research/toolregistry-lazy-mcp/output-schema-drift/logs/`:

| Phase | Proxy log | Harness log (proxy+backend+registry stream) |
|---|---|---|
| Test A (null-schema baseline) | [`test-a-proxy.log`](logs/test-a-proxy.log) | [`test-a-harness.log`](logs/test-a-harness.log) |
| Test B (matching schema) | [`test-b-proxy.log`](logs/test-b-proxy.log) | [`test-b-harness.log`](logs/test-b-harness.log) |
| Test C (diverging, first exposure) | [`test-c-proxy.log`](logs/test-c-proxy.log) | [`test-c-harness.log`](logs/test-c-harness.log) |
| Test C2 (pure cached-manifest drift) | [`test-c2-proxy.log`](logs/test-c2-proxy.log) | [`test-c2-harness.log`](logs/test-c2-harness.log) |
| Test C3 (bare-number shape) | [`test-c3-proxy.log`](logs/test-c3-proxy.log) | [`test-c3-harness.log`](logs/test-c3-harness.log) |
| Test D (input-valid isolation) | [`test-d-proxy.log`](logs/test-d-proxy.log) | [`test-d-harness.log`](logs/test-d-harness.log) |
| Test E (determinism + recovery) | [`test-e-proxy.log`](logs/test-e-proxy.log) | [`test-e-harness.log`](logs/test-e-harness.log) |
| Test F (blast radius) | [`test-f-proxy.log`](logs/test-f-proxy.log) | [`test-f-harness.log`](logs/test-f-harness.log) |

The harness logs contain the full interleaved stream (`HARNESS|`, `PROXY|`,
`BACKEND|` prefixed lines). Proxy-only logs are written directly by each proxy
process via `PROXY_LOG_FILE`; because ToolRegistry's reconnect-retry spawns a
fresh proxy with the same `PROXY_LOG_FILE`, a single proxy log can contain
multiple `proxy_started` blocks (different pids) — this is itself part of the
cost evidence (Test C/E/F).
