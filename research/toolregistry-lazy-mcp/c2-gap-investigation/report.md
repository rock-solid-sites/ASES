---
title: C2 Gap — Self-Healing vs ToolRegistry Client Interception vs Patch — Decision-Ready Comparison of Three Candidate Approaches
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
  - research/toolregistry-lazy-mcp/retry-classification/report.md
  - research/toolregistry-lazy-mcp/report.md
implements:
implemented_by:
supersedes:
superseded_by:
last_updated: 2026-08-08
---

# Research Finding: Closing the Consistently-Drifted-Backend (C2) Gap — Self-Healing vs Client Interception vs Patch

## 1. Purpose and question

This is an **investigation**, not a build (#228, child of epic #212). #217
(retry-classification) removed the 4x spawn multiplier for the primary drift
variant but explicitly did **not** cover the C2 variant (test `Test C2` of
#213): a backend whose declaration *and* behaviour are internally consistent
and diverged, so only the **cached manifest** is stale. In that variant the
proxy forwards a conforming-looking response, the `RuntimeError` fires inside
ToolRegistry's own client, and ToolRegistry's reconnect-retry
(`toolregistry/integrations/mcp/connection.py:106`) still fires — 2 backend
spawns / 2 persistent proxies per failed call.

The three candidate approaches tested:

* **Option A** — proxy-side self-healing: the proxy detects repeated
  schema-validation failures against its **own served manifest**, captures
  the live backend response shape, and updates the manifest it serves; no
  ToolRegistry change.
* **Option B** — ToolRegistry client interception point: full tracebacks,
  SDK-vs-ToolRegistry origin, a public extension-point review of the
  installed source, and the smallest PoC wrapper if a clean point exists
  (STOP if none).
* **Option C** — patch assessment: only if B finds no clean point; a minimal
  `connection.py` change with diff size + upgrade-fragility assessment.

Deliverable: a decision-ready comparison with A's before/after cost numbers +
flapping check, B's yes/no + traceback + PoC size, C's diff/fragility **only
if reached**, and a one-paragraph recommendation. Proof-of-concept quality
only; no production build, no upstream PR, stdio transport only.

Throughout this report, **observations** (what logs/timings/source show, with
file/line references) are kept distinct from **findings** (interpretation).

## 2. Environment and exact versions

Same pinned venv as #213/#217 (reused, not reinstalled; re-confirmed live on
2026-08-08):

| Component | Version | Notes |
|---|---|---|
| `toolregistry` | **0.15.0** | `pip install toolregistry[mcp]==0.15.0`; MCP extra named `mcp` |
| `mcp` (Python SDK) | **2.0.0** | Direct dependency of the `[mcp]` extra; re-confirmed live via `importlib.metadata.version("mcp")` |
| Python | 3.10.12 | venv at `/tmp/toolregistry-venv` (NOT committed) |
| Platform | Linux | single host, all processes local |

All tests ran with the transport pair **stdio → proxy → stdio → backend**
(identical to #196/#213/#217 scope). ToolRegistry's persistent MCP connection
is lazy: no backend process exists between registration and the first tool
call.

**Host-load caveat.** The preserved initial run (commit `7dd054be`,
2026-08-06) was machine-load-affected (backend `init_ms` up to 18 896 ms);
the fresh verification run (2026-08-08) ran under light load (`init_ms`
~800–940 ms). Both runs produce the same event sequences, spawn counts, and
outcome classes; absolute latencies differ. All numbers quoted below are from
the fresh committed run unless explicitly labelled "preserved". The key
latency phases (A1, A2, B2) were additionally re-measured to n=3 under
normal load on 2026-08-08 (`logs/n3/`, §7): the committed single-run values
fall inside the n=3 ranges, except B2's committed 2373 ms which was
load-affected (that run's backend `init_ms` was 1163 ms vs ~790–845 ms in
the n=3 runs).

## 3. What was built / verified

All artefacts live in `research/toolregistry-lazy-mcp/c2-gap-investigation/`.
The preserved evidence from the stalled builder (commit `7dd054be`) was
verified, extended (harness logs were missing — the phases had been run as
direct scripts, not via `run_c2.py`), and completed:

| File | Role |
|---|---|
| `backend.py` | Byte-identical copy of the #213 drift backend (md5 `279c7520...` verified against the #213 corpus). |
| `manifest.json` | Byte-identical copy of the #213 cached manifest (md5 `f8977f8a...` verified): `add` declares `output_schema={"sum": ...}`, `multiply` declares `null`. |
| `backend_intermittent.py` | #213 backend + one documented delta (`BACKEND_RESPONSE_MODE=alternating`): the `add` tool's returned shape alternates `{"sum": n}` / `{"result": n}` per-process. |
| `proxy_self_heal.py` | Option A self-healing proxy (deltas documented in its docstring): DELTA A per-tool consecutive-failure counter + heal-on-threshold (N=1) + live-schema capture + served-manifest update + persisted heal state; DELTA B intermittent backend support; DELTA C optional #217 classification (`PROXY_CLASSIFY_SCHEMA=1`). |
| `intercept_poc.py` | Option B PoC: `SchemaAwareConnectionManager` (subclasses public `MCPConnectionManager`, overrides `_call_persistent`) + `register_with_connection` (manual registration assembly via public `MCPTool.from_tool_json` / `registry.register`). |
| `tests/run_c2.py` | Driver: runs A1/A2/A3/B1/B2 as clean subprocesses, captures harness logs. |
| `tests/common_c2.py` | Shared helpers (transport builder, `invoke_recorded`, proxy-log parsers). |
| `tests/phase_a1_control.py` … `phase_b2_poc.py` | One clean session per phase (fresh registry, fresh proxy processes). |
| `logs/` | One proxy log + one harness log per phase. `logs/preserved-initial-run/` holds the original (load-affected) logs untouched. |

Reproduce (versions pinned to the exact installed set):

```bash
cd research/toolregistry-lazy-mcp/c2-gap-investigation
/tmp/toolregistry-venv/bin/python tests/run_c2.py          # A1, A2, A3, B1, B2
/tmp/toolregistry-venv/bin/python tests/phase_a2b_preabsorbed.py   # A2b boundary
/tmp/toolregistry-venv/bin/python tests/phase_b2b_preabsorbed.py   # B2b pre-absorbed (Option B)
/tmp/toolregistry-venv/bin/python tests/measure_poc_size.py        # PoC-size counts
A3_HEAL_THRESHOLD=2 /tmp/toolregistry-venv/bin/python tests/phase_a3_intermittent.py  # flapping sweep N=2
A3_HEAL_THRESHOLD=3 /tmp/toolregistry-venv/bin/python tests/phase_a3_intermittent.py  # flapping sweep N=3
```

The n=3 latency runs in `logs/n3/` are produced by re-running
`tests/phase_a1_control.py`, `tests/phase_a2_selfheal_c2.py`, and
`tests/phase_b2_poc.py` three times each, redirecting stdout to
`logs/n3/<phase>-run<N>-harness.log`.

## 4. Option A — proxy-side self-healing

### 4.1 Test A1 — CONTROL: C2 scenario against the ORIGINAL #213 drift proxy — **PASS (reproduces #213 C2)**

Setup: cached manifest `{"sum": ...}`; backend `schema_mode=diverging` +
`response_mode=diverging` (internally consistent); proxy = UNMODIFIED
`output-schema-drift/proxy.py`.

| Observation | Value | Evidence |
|---|---|---|
| Backend spawns | **2** | `A1_RESULT pass=True spawns=2 proxies=3 reconnect=True` |
| Proxy processes | **3** = registration temp + **2 persistent** | `A1_SPAWN_COUNTS proxy_processes=3 reconnect_fired=True` |
| Reconnect-retry fired | **YES** | `A1_RESULT reconnect=True` |
| Caller-visible outcome | `ErrorResult`, message carries the SDK `RuntimeError` schema text verbatim (§9) | `INVOKE|add(2,3) ... ok=False outcome_type=ErrorResult` |
| Failure latency | **5680 ms** | `INVOKE|add(2,3) ... delta_ms=5680` |

**This confirms the C2 baseline exactly as #213 measured it:** 2 backend
spawns / 2 persistent proxies / reconnect per failed call.

### 4.2 Test A2 — SELF-HEAL: C2 scenario, N=1, fresh session — **PASS (best case)**

Setup identical to A1 except the proxy is `proxy_self_heal.py` with
`PROXY_HEAL_THRESHOLD=1`; calls: `add(2,3)`, `add(1,1)`, `multiply(4,5)`.

| Observation | Value | Evidence |
|---|---|---|
| Call 1 `add(2,3)` outcome | **SUCCESS `'5.0'`** — not a failure | `INVOKE|add(2,3) delta_ms=1849 ok=True result='5.0'` |
| Call 1 spawn cost | **1 backend spawn, 1 persistent proxy, no reconnect** | `A2_CALL_METRICS label=add(2,3) spawn_increment=1 cumulative_spawns=1 persistent_proxies=1 reconnect_fired=False` |
| Heal event | 1 heal on call 1, `{"sum":...}` → `{"result":...}` | `A2_HEAL_EVENT`; proxy log `self_heal name=add before_schema={'properties': {'sum': ...}} after_schema={'properties': {'result': ...}}` |
| Call 2 `add(1,1)` | SUCCESS `'2.0'`, **8 ms, 0 new spawns** | `INVOKE delta_ms=8 ok=True`; `spawn_increment=0` |
| Call 3 `multiply(4,5)` (other tool) | SUCCESS `'20.0'`, **5 ms, 0 new spawns**, schema untouched (`multiply` stays `None`) | `INVOKE delta_ms=5 ok=True`; `A2_SERVED ... served={'add': {'properties': {'result': ...}}, 'multiply': None}` |
| Persisted heal state | `phase-a2-selfheal-c2-heal-state.json` — `add` corrected to `{"result":...}`, toolcount 2 | file in `logs/` |

**Why call 1 succeeds in a fresh session:** the proxy detects the mismatch
against its own served manifest *before returning the response*, heals the
served manifest, and ToolRegistry's client's cache-miss re-absorb
(`mcp/client/session.py:1086` → `_absorb_tool_listing`, session.py:1273-1276)
re-reads `tools/list` — which now carries the corrected schema — so the
response validates and the call succeeds. The "first failing call still costs
2 spawns/2 proxies" expectation from the brief is **NOT what happens in a
fresh session**: N=1 heals mid-call and the first call succeeds at
**1 spawn / 1 persistent proxy / no reconnect**.

### 4.3 Test A2b — SELF-HEAL boundary: schema PRE-ABSORBED before the drift call — **PASS (boundary characterised)**

Setup same as A2 but the harness calls `multiply` first, which triggers a
full `tools/list` re-absorb of the **stale** manifest into ToolRegistry's
persistent client — so when `add` is called, the stale `{"sum":...}` schema
is already in `_tool_output_schemas` and there is **no cache-miss re-list** to
pick up the proxy's mid-call heal.

| Observation | Value | Evidence |
|---|---|---|
| `multiply(4,5)` (pre-absorb) | SUCCESS `'20.0'`, 1852 ms | `INVOKE|multiply(4,5) delta_ms=1852 ok=True` |
| `add(2,3)` (first drifted call) | **SUCCESS after reconnect-retry** `'5.0'`, **4070 ms** | `INVOKE|add(2,3) delta_ms=4070 ok=True result='5.0'` |
| Cost of the first drifted call | **2 spawns, 2 persistent proxies, reconnect fired** | `A2B_SPAWN_COUNTS backend_spawn_count=2 proxy_processes=3 persistent_proxies=2 reconnect_fired=True` |
| Heal | 1 heal on the first drifted call; persisted before the retry | `A2B_HEAL ... after_schema={'properties': {'result': ...}}` |
| `add(1,1)` (repeat) | SUCCESS `'2.0'`, **9 ms, warm** | `INVOKE delta_ms=9 ok=True` |

**Boundary finding:** when the stale schema is already absorbed by
ToolRegistry's client, the first drifted call still costs **2 spawns / 2
proxies / reconnect** — but the proxy's persisted heal state means the
reconnect-respawned proxy serves the corrected manifest, so the **retried
call succeeds** and subsequent calls are warm. This is the "one wasted call
cycle per drift event" boundary that N=1 avoids in the fresh-session case.

### 4.4 Test A3 — INTERMITTENT-drift flapping check — **PASS (no heal-flapping; cost depends on the classification delta)**

Setup: `proxy_self_heal.py` (N=1) against `backend_intermittent.py`
(`response_mode=alternating`); four `add` calls. Three sub-scenarios:

| Sub-scenario | Backend declaration | Classification | Spawns | Persistent proxies | Reconnect | Heal events | Flapping? |
|---|---|---|---|---|---|---|---|
| **A3a** (`schema_mode=none`) | no output schema; responses alternate conforming/diverging | OFF | **2** | **2** | **YES** (fired once) | **1** (converged to `None`) | **NO** — 1 heal, no heal-back |
| **A3b** (`schema_mode=conforming`) | conforming; responses alternate | **ON** | **1** | **1** | **NO** | 0 (served schema untouched) | **NO** — classified terminal, no thrash |
| **A3c** (`schema_mode=conforming`) | conforming; responses alternate | OFF | **4** | **1** | **NO** | 0 | **NO heal-flap**, but each diverging response costs a proxy-internal respawn |

Evidence (fresh run):

* **A3a**: `A3_METRICS tag=a3a spawns=2 persistent_proxies=2 reconnect_fired=True heal_events=1`; `A3_HEAL tag=a3a ... after_schema=None` (the live backend declares no schema, so the heal converges to `None`); calls `1724 / 3730 / 7 / 7 ms` — call 2 (`add(4,5)`, the first diverging response after call 1 absorbed the stale schema) still triggers the ToolRegistry reconnect (the A2b boundary again), but the retried call succeeds and calls 3–4 are warm. **The heal converges; there is no heal-back, so no flapping of the heal mechanism.**
* **A3b**: `A3_METRICS tag=a3b spawns=1 persistent_proxies=1 reconnect_fired=False heal_events=0 schema_failure_classified=2`; alternating diverging responses are caught at the proxy's OWN client (Test C signature) and classified terminal as `isError=True` responses — the served schema stays untouched (no heal, no flap), cost = **1 spawn / no reconnect**. Caller-visible classified shape verbatim in §9.
* **A3c**: `A3_METRICS tag=a3c spawns=4 persistent_proxies=1 reconnect_fired=False heal_events=0`; each alternating diverging response raises in the proxy's own client, is treated as a connection failure (classification OFF), and respawns the backend — the respawned backend's counter restarts at conforming, so every diverging call costs **2 spawns** (4 total for 4 calls). No ToolRegistry reconnect because the retried call succeeds. **This documents that plain self-heal WITHOUT the #217 classification delta regresses the Test-C-signature intermittent case to proxy-respawn cost** — the classification delta is required to preserve the #217 benefit (A3b).

**Flapping verdict:** the self-heal mechanism itself does **not** flap or
thrash: heal events are at most 1 per drift event, converge, and never
heal-back. The residual cost is the **one reconnect cycle when the stale
schema is pre-absorbed** (A2b/A3a), and — for the Test-C-signature
intermittent case — the proxy-respawn cost when classification is OFF (A3c,
fixed by DELTA C = A3b).

**Threshold sweep (N=2 and N=3).** The flapping check was repeated with the
heal threshold raised to N=2 and N=3 (`A3_HEAL_THRESHOLD` env knob on
`tests/phase_a3_intermittent.py`; fresh runs 2026-08-08 in
`logs/n3/phase-a3-n2-harness.log` and `logs/n3/phase-a3-n3-harness.log`):

| N | Sub-scenario | Spawns | Persistent proxies | Reconnect | Heal events | Flapping? |
|---|---|---|---|---|---|---|
| 2 | a3a (`schema_mode=none`) | **4** | **4** | **YES** | **0** | **NO** — no heal fires, no heal-back |
| 2 | a3b (`schema_mode=conforming`, classification ON) | **1** | **1** | **NO** | 0 | **NO** — classified terminal, as N=1 |
| 2 | a3c (`schema_mode=conforming`, classification OFF) | **4** | **1** | **NO** | 0 | **NO** — proxy-respawn, as N=1 |
| 3 | a3a (`schema_mode=none`) | **4** | **4** | **YES** | **0** | **NO** — no heal fires, no heal-back |
| 3 | a3b (`schema_mode=conforming`, classification ON) | **1** | **1** | **NO** | 0 | **NO** — classified terminal, as N=1 |
| 3 | a3c (`schema_mode=conforming`, classification OFF) | **4** | **1** | **NO** | 0 | **NO** — proxy-respawn, as N=1 |

Evidence: N=2 `A3_METRICS tag=a3a spawns=4 persistent_proxies=4
reconnect_fired=True heal_events=0`, `tag=a3b spawns=1 ... heal_events=0
schema_failure_classified=2`, `tag=a3c spawns=4 persistent_proxies=1 ...
heal_events=0`; N=3 identical (`phase-a3-n2-harness.log:102,152,235` and
`phase-a3-n3-harness.log:102,152,235`).

**Threshold-sweep finding:** no heal-back or thrashing at any tested N —
A3a's heal never fires at N≥2 because the alternating backend resets the
per-tool consecutive-failure counter before it reaches the threshold (each
diverging response is followed by a conforming one), so the mechanism stays
quiescent rather than flapping. The cost consequence is important: at N≥2
the heal does **not** engage, so A3a reverts to the un-healed pre-absorbed
pattern — 4 spawns / 4 persistent proxies / reconnect for 4 calls (vs
2/2/1-heal at N=1). N=1 remains the correct threshold for the
alternating-drift signature this check targets; higher N buys nothing here
and loses the mid-call heal.

### 4.5 Option A verdict

**FULLY effective for the fresh-session C2 case** (first call succeeds at 1
spawn / 1 proxy / no reconnect, warm thereafter, other tools untouched).
**PARTIALLY effective for the pre-absorbed C2 case** (first drifted call
still costs 2 spawns / 2 proxies / reconnect, but the persisted heal makes
the retry succeed and warm thereafter). **No flapping.** Requires the #217
classification delta (DELTA C) to avoid proxy-respawn cost on
Test-C-signature intermittent drift.

## 5. Option B — ToolRegistry client interception point

### 5.1 B1 — FULL traceback from the reconnect trigger to the origin — **PASS**

Same C2 scenario against the UNMODIFIED #213 drift proxy, with a runtime
monkeypatch of `MCPClient.call_tool` (in the harness process only; installed
packages untouched) capturing `traceback.format_exc()` at the client boundary.
Two tracebacks captured (first attempt + retried attempt after the
reconnect), both identical:

```
Traceback (most recent call last):
  File ".../tests/phase_b1_traceback.py", line 66, in traced_call_tool
    return await _orig_call_tool(self, name, arguments)
  File "/tmp/toolregistry-venv/lib/python3.10/site-packages/toolregistry/integrations/mcp/client.py", line 133, in call_tool
    return await self._session.call_tool(name, arguments)
  File "/tmp/toolregistry-venv/lib/python3.10/site-packages/mcp/client/session.py", line 1064, in call_tool
    await self.validate_tool_result(name, result)
  File "/tmp/toolregistry-venv/lib/python3.10/site-packages/mcp/client/session.py", line 1110, in validate_tool_result
    raise RuntimeError(f"Invalid structured content returned by tool {name}: {error}") from error
RuntimeError: Invalid structured content returned by tool add: 'sum' is a required property
...
```

**Origin answer — SDK-raised, ToolRegistry-passed-through.** The `RuntimeError`
is raised by the **mcp SDK itself** (`mcp/client/session.py:1110`
`validate_tool_result`, called from `session.py:1064` `call_tool`).
ToolRegistry's `MCPClient.call_tool` (`client.py:133`) is a **pure
pass-through** — `return await self._session.call_tool(name, arguments)` —
with **zero ToolRegistry frames between the SDK raise and the client
boundary**. ToolRegistry's reconnect-retry (`connection.py:103-111`
`_call_persistent`) catches **any** `Exception` and reconnects; there is no
failure-class distinction in ToolRegistry code (verified by source read).

### 5.2 Source-read: public extension points in the installed source

`toolregistry 0.15.0` installed at `/tmp/toolregistry-venv`:

* `MCPConnectionManager` (`connection.py:16`) — **public class** with public
  `call_tool`, `list_tools`, `call_tool_sync`, `close`, `close_sync`; the
  reconnect logic is the **private** `_call_persistent` (lines 97-111) and
  `_call_per_request` (113-118).
* `MCPClient` (`client.py`) — **public class**; `call_tool` is a pass-through
  to the SDK session (line 133).
* `MCPIntegration.register_mcp_tools_async` (`integration.py:296-352`) —
  **hardcodes** `MCPConnectionManager(...)` construction (line 323) with **no
  injection point / factory / hook / callback** for the connection manager.
* `MCPTool.from_tool_json` (`integration.py:223`) — **public classmethod**.
* `ToolRegistry.register` — **public API**.
* `mcp/client/session.py` — the SDK's `validate_tool_result` (line 1110)
  raises the `RuntimeError`; its cache-miss re-list (`_absorb_tool_listing`)
  is the refresh path that, against a cached-manifest proxy, re-absorbs the
  stale schema.

**Clean-point verdict: YES.** A clean, dependency-free interception point
exists: **subclass the public `MCPConnectionManager` and override the private
`_call_persistent` seam** (the exact method containing `connection.py:106`),
plus **manual registration assembly using only public API**
(`MCPTool.from_tool_json` + `registry.register`) — the one injection point
`register_from_mcp` does not expose. No fork, no monkeypatch of installed
sources, no fragile patch required.

### 5.3 B2 — PoC: `SchemaAwareConnectionManager` — **PASS (gap closed)**

Same C2 scenario against the UNMODIFIED #213 drift proxy; registration goes
through `intercept_poc.register_with_connection`, which wires a
`SchemaAwareConnectionManager` (subclass of the public
`MCPConnectionManager`) whose `_call_persistent` override classifies the
schema-validation `RuntimeError` as **terminal** — re-raise without reconnect.

| Observation | Value | Evidence |
|---|---|---|
| Backend spawns | **1** | `B2_SPAWN_COUNTS backend_spawn_count=1` |
| Proxy processes | **2** = registration temp + **1 persistent** | `B2_SPAWN_COUNTS proxy_processes=2 persistent_proxies=1 reconnect_fired=False` |
| Reconnect-retry fired | **NO** | `B2_RESULT reconnect=False interception_effective=True` |
| Interception counter | `schema_validation_failures=1` | `B2_SPAWN_COUNTS schema_validation_failures=1` |
| Caller-visible outcome | **`ErrorResult` with the SAME verbatim RuntimeError text as the control (§9)** — no shape degradation | `B2_RESULT error_preserved=True`; `INVOKE delta_ms=1830 ok=False outcome_type=ErrorResult` (run 1, `logs/n3/phase-b2-poc-run1-harness.log:70`) |
| Failure latency | **1799–1830 ms** n=3 (vs control 5612–6132 ms n=3 in adjacent runs) | `INVOKE delta_ms=1830/1814/1799` (`logs/n3/phase-b2-poc-run{1,2,3}-harness.log:70`) |

**Gap closed:** the C2 failure now costs **1 backend spawn / 1 persistent
proxy / no reconnect** — the same single-spawn residual #217 achieved for the
Test-C variant — reached from the ToolRegistry side **without touching the
proxy or the SDK**, and with the caller-visible error **shape preserved**
(clean `ErrorResult`, unlike #217's `ToolCallResult`-with-repr degradation).

### 5.3b B2b — PoC PRE-ABSORBED: schema already absorbed before the drift call — **PASS**

The same interception, tested in the pre-absorbed session state that the
fresh-session B2 does not cover: the harness calls `multiply` first (no
output schema, succeeds), which triggers a full `tools/list` re-absorb of
the STALE manifest — so when `add` is called, the stale `{"sum": ...}`
schema is already in `_tool_output_schemas` and there is no cache-miss
re-list. This directly answers the "in every tested session state (fresh or
pre-absorbed)" claim of §8 under the tested = directly-measured-only
convention (see §Limitations): the interception fires pre-absorbed, at the
same 1 spawn / 1 persistent proxy / no reconnect cost.

| Observation | Value | Evidence |
|---|---|---|
| `multiply(4,5)` (pre-absorb) | SUCCESS `'20.0'`, 1695 ms | `INVOKE|multiply(4,5) delta_ms=1695 ok=True` (`phase-b2b-preabsorbed-harness.log:24`) |
| `add(2,3)` (first drifted call, pre-absorbed) | **`ErrorResult` verbatim — intercepted, no reconnect** | `INVOKE|add(2,3) delta_ms=119 ok=False outcome_type=ErrorResult` (`:77`) |
| Cost of the first drifted call | **1 spawn / 1 persistent proxy / no reconnect** | `B2B_SPAWN_COUNTS backend_spawn_count=1 proxy_processes=2 persistent_proxies=1 reconnect_fired=False schema_validation_failures=2` (`:138`) |
| Warm repeat `add(1,1)` (intercepted session) | `ErrorResult` verbatim, **9 ms** | `INVOKE|add(1,1) delta_ms=9 ok=False` (`:130`) |
| Other tool `multiply(6,7)` after the failures | **SUCCESS `'42.0'`, 7 ms** | `INVOKE|multiply(6,7) delta_ms=7 ok=True` (`:137`) |
| Interception fired pre-absorbed | **YES** (`schema_validation_failures=2`, 1 spawn, no reconnect) | `B2B_RESULT pass=True preabsorb_interception_fired=True add1_error_preserved=True warm_add_error_preserved=True other_tool_success=True` (`:141`) |

**Pre-absorbed result:** the interception fires **regardless of absorption
state** — the first drifted `add` returns the verbatim `ErrorResult` at
**1 spawn / 1 persistent proxy / no reconnect**, exactly as in the fresh B2
run, at 119 ms (the persistent connection is already up from the pre-absorb
call). Warm repeats on the intercepted session fail identically at 9 ms with
**no new spawns**, and the other tool (`multiply`) is untouched after the
failures. The `"works in every tested session state (fresh or pre-absorbed)"`
claim is therefore **tested, not merely inferred**, for both session states.

**PoC code size:**

Counts emitted by the committed counter script `tests/measure_poc_size.py`
(tokenize-based; rule = non-blank / non-comment / non-docstring, post-shebang;
output in `logs/measure-poc-size.log`):

| Unit | Lines |
|---|---|
| `intercept_poc.py` total | **147** |
| Code lines (non-blank/non-comment/non-docstring, post-shebang) | **64** |
| Mechanism proper (code − 6 imports − 1 constant) | **57** |
| `_is_schema_validation_error` (classifier helper) | **5** |
| `SchemaAwareConnectionManager` class body (the interception) | **20** |
| `_call_persistent` override (the classification decision) | **16** |
| `_register_async` (registration assembly, async loop) | **22** |
| `register_with_connection` (sync entry point) | **10** |

The whole interception mechanism is **57 code lines** (5 classifier + 20
class body incl. the 16-line override + 22 registration loop + 10 sync
entry — components sum to 57, matching the mechanism-proper figure) over
plain public-API usage — the smallest clean wrapper the installed source
permits.

### 5.4 Option B verdict

**YES — a clean interception point exists and the PoC closes the gap.**
Full traceback proves the origin is the mcp SDK (`session.py:1110`), the
public `MCPConnectionManager` subclass seam is clean and dependency-free, the
PoC removes the reconnect amplification (2→1 spawns, 2→1 persistent proxies,
reconnect NO), preserves the caller-visible `ErrorResult` verbatim, and is
57 code lines of interception + registration assembly. The only cost: callers
must use `register_with_connection` instead of `register_from_mcp` because
the latter hardcodes the connection manager.

### 5.5 Upgrade fragility of the recommended option

Option B's mechanism overrides a **private** method and **re-implements its
body by copy**: `intercept_poc.py:86-103` duplicates
`connection.py:101-111` (the try/except/retry body of `_call_persistent`),
differing only by the classification branch and the **dropped
`logger.warning`** that the original emits at `connection.py:107` before
reconnecting. The override therefore carries genuine upgrade fragility:

* it couples to a **private, version-bound internal** of toolregistry 0.15.0
  / mcp 2.0.0 — no compatibility guarantee on upgrade;
* if upstream alters `_call_persistent` (backoff, lock discipline,
  telemetry, retry count), the subclass **diverges silently** while still
  importing and passing — no test detects the drift because no backoff /
  lock / telemetry divergence detection exists in the PoC;
* the copy drops the `logger.warning` at `connection.py:107`, so a
  telemetry-observant deployment loses the reconnect-warning line for every
  non-schema failure the subclass handles.

This is the same fragility dimension Option C would have been assessed on,
and it is now assessed for the *recommended* option (audit gap C2/S3). The
brief scoped the fragility assessment to Option C only; this paragraph
closes the resulting blind spot. Consequence for the recommendation: Option
B is **dependency-free but NOT patch-free** — it is a non-invasive
*dependency-coupling* that must be re-validated on every toolregistry / mcp
upgrade (see the re-validation trigger in §11 and issue #279, filed under
epic #212).

## 6. Option C — patch assessment

**NOT REACHED.** Option B found a clean interception point (§5), so per the
brief Option C (minimal `connection.py` change, diff-size + upgrade-fragility
assessment) was **not** exercised. No fragile patch was evaluated or applied.

## 7. Timing comparison — the quantified before/after

All times in milliseconds. Rows marked **n=3** were re-measured on 2026-08-08
under normal load (three fresh runs each, logs in `logs/n3/`); rows marked
**n=1** are single measurements from the committed fresh run (2026-08-08,
light load, `init_ms` ~800–940 ms). Where variance is high the range is
reported, not a point. "Persistent proxies" counts the persistent proxy
process(es) in addition to the registration-temp proxy.

| Phase | Scenario | Caller outcome | Delta (ms) | n | Backend spawns | Persistent proxies | Reconnect |
|---|---|---|---|---|---|---|---|
| A1 | C2 control (ORIGINAL proxy) | `ErrorResult` | 5612–6132 | **3** | **2** | **2** | **YES** |
| A2 | C2 self-heal N=1, call 1 (fresh) | **SUCCESS `'5.0'`** | 1812–2020 | **3** | **1** | **1** | **NO** |
| A2 | C2 self-heal N=1, call 2 (warm) | SUCCESS | 9–10 | **3** | 0 | 1 | NO |
| A2 | C2 self-heal N=1, call 3 (multiply) | SUCCESS | 7–8 | **3** | 0 | 1 | NO |
| A2b | C2 self-heal N=1, pre-absorbed, first `add` | SUCCESS (after retry) | 4070 | 1 | **2** | **2** | **YES** |
| A2b | C2 self-heal N=1, pre-absorbed, repeat `add` | SUCCESS | 9 | 1 | 0 | 1 | NO |
| A3a | intermittent `schema_mode=none` (N=1) | SUCCESS (retry on call 2) | 1724 / 3730 / 7 / 7 | 1 | **2** | **2** | YES (once) |
| A3b | intermittent `schema_mode=conforming` + classification | success / classified `isError` | 1847 / 7 / 9 / 9 | 1 | **1** | **1** | **NO** |
| A3c | intermittent `schema_mode=conforming`, no classification | SUCCESS (proxy respawns) | 1687 / 1111 / 1012 / 1020 | 1 | **4** | **1** | NO |
| B1 | C2 traceback (ORIGINAL proxy) | `ErrorResult` | 5561 | 1 | **2** | **2** | **YES** |
| B2 | C2 interception PoC | `ErrorResult` (verbatim) | 1799–1830 | **3** | **1** | **1** | **NO** |
| B2b | C2 interception PoC, pre-absorbed, first `add` | `ErrorResult` (verbatim) | 119 | 1 | **1** | **1** | **NO** |
| B2b | C2 interception PoC, pre-absorbed, warm `add` | `ErrorResult` (verbatim) | 9 | 1 | 0 | 1 | NO |
| B2b | C2 interception PoC, pre-absorbed, other tool `multiply` | SUCCESS | 7 | 1 | 0 | 1 | NO |

Notes on variance and sources:

* **A1 n=3** (5612–6132 ms): `logs/n3/phase-a1-control-run{1,2,3}-harness.log`
  INVOKE lines (5851 / 6132 / 5612). The committed single run (5680 ms,
  `phase-a1-control-harness.log:88`) falls inside this range.
* **A2 n=3** (call 1 1812–2020 ms, warm 9–10 ms, multiply 7–8 ms):
  `logs/n3/phase-a2-selfheal-c2-run{1,2,3}-harness.log` INVOKE lines
  (2020/2001/1812; 9/10/9; 7/8/8). The committed single run (1849 / 8 / 5 ms,
  `phase-a2-selfheal-c2-harness.log:30,39,48`) is inside/near these ranges;
  the multiply warm delta (5 ms committed vs 7–8 ms n=3) is sub-10-ms noise.
* **B2 n=3** (1799–1830 ms): `logs/n3/phase-b2-poc-run{1,2,3}-harness.log`
  INVOKE lines (1830 / 1814 / 1799). The committed single run (2373 ms,
  `phase-b2-poc-harness.log:70`) is **higher** — that run's backend
  `init_ms` was 1163 ms vs ~790–845 ms in the n=3 runs (the committed run
  coincided with heavier host load), so the 2373 ms figure is load-affected
  rather than mechanism-affected. The spawn/proxy/reconnect verdict is
  identical across all four runs.
* **A2b, A3a/b/c, B1, B2b** are n=1 single measurements from the committed
  run (B2b was newly added on 2026-08-08, `logs/phase-b2b-preabsorbed-*`).

Reference baselines (cross-document rows carry their source n): #213 Test B
success (conforming schema, conforming shape) 1810–3124 ms under normal
load, n=3 (`output-schema-drift/report.md:350`); #213 C2 failure 5871–5913
ms normal load / 9008 ms load-affected (2 spawns / 2 proxies), n=2
(`output-schema-drift/report.md:353`). The fresh C2 control (A1/B1)
re-measured at 5561–6132 ms under the fresh run's load — same 2/2 pattern.

## 8. The central claim — explicit YES/NO per option

> Can the C2 gap (consistently-drifted backend, 2 spawns / 2 proxies per
> failed call) be closed without a ToolRegistry source patch?

* **Option A (proxy-side self-healing):** **YES for the fresh-session case**
  (first call succeeds at 1/1), **partial for the pre-absorbed case** (first
  drifted call still 2/2 + reconnect, but the persisted heal makes the retry
  succeed and warm thereafter). No heal-flapping. Requires the #217
  classification delta for Test-C-signature intermittent drift.
* **Option B (ToolRegistry client interception):** **YES** — clean public
  subclass seam (`MCPConnectionManager._call_persistent`) + public
  registration assembly; the PoC closes the gap at 1 spawn / 1 proxy / no
  reconnect / verbatim `ErrorResult`, in every tested session state —
  **fresh (B2) and pre-absorbed (B2b) are both directly measured**; the
  interception fires regardless of what the client has absorbed.
* **Option C (patch):** not reached; B made it unnecessary.

**Version validity.** The Option B conclusions above are valid for
**toolregistry 0.15.0 / mcp 2.0.0** only and depend on a private internal
(`MCPConnectionManager._call_persistent`) with no compatibility guarantee.
**Verify on upgrade** — a re-validation trigger is filed under epic #212
(see §11).

## 9. Verbatim error text

**Control (A1) and Option B PoC (B2) caller-visible `ErrorResult.message` —
IDENTICAL (fresh committed run):**

```
RuntimeError: Error executing add: Invalid structured content returned by tool add: 'sum' is a required property

Failed validating 'required' in schema:
    {'properties': {'sum': {'type': 'number',
                            'description': 'The sum of a and b'}},
     'required': ['sum'],
     'type': 'object'}

On instance:
    {'result': 5.0}
```

**Option B traceback tail (B1, verbatim — SDK origin):**

```
  File ".../toolregistry/integrations/mcp/client.py", line 133, in call_tool
    return await self._session.call_tool(name, arguments)
  File ".../mcp/client/session.py", line 1064, in call_tool
    await self.validate_tool_result(name, result)
  File ".../mcp/client/session.py", line 1110, in validate_tool_result
    raise RuntimeError(f"Invalid structured content returned by tool {name}: {error}") from error
RuntimeError: Invalid structured content returned by tool add: 'sum' is a required property
```

**A3b classified failure caller-visible shape (verbatim excerpt; the #217
`ToolCallResult`-with-repr degradation, reproduced on intermittent drift):**

```
meta=None content=[TextContent(type='text', text="Invalid structured content returned by tool add: 'sum' is a required property\n\n...", annotations=None, meta=None)] structured_content=None is_error=True result_type='complete'
```

## 10. Findings (interpretation, distinct from observations)

1. **The C2 exception is SDK-raised and ToolRegistry-transparent.** The full
   traceback (B1) proves the `RuntimeError` originates in the mcp SDK
   (`session.py:1110 validate_tool_result`), passes through ToolRegistry's
   `MCPClient.call_tool` with zero ToolRegistry frames, and trips
   `connection.py:106`'s catch-all reconnect. ToolRegistry 0.15.0 has no
   failure-class distinction anywhere in its MCP integration.
2. **Self-healing is strongest in a fresh session because of a re-absorb
   accident.** The proxy's mid-call heal only reaches ToolRegistry's client
   because the SDK's cache-miss re-list re-reads `tools/list` after the call;
   when the stale schema is already absorbed (A2b/A3a), that mechanism is
   gone and the first drifted call still pays the reconnect — the persisted
   heal state is what makes the *retry* succeed. Option A therefore depends
   on the SDK's re-list behaviour plus the heal-state persistence; it is not
   a uniform guarantee.
3. **The flapping check is clean for the heal itself, but the cost varies by
   drift signature.** No heal-back occurred in any A3 sub-scenario. However,
   plain self-heal (classification OFF) regresses the Test-C-signature
   intermittent case to proxy-respawn cost (A3c: 4 spawns for 4 calls);
   DELTA C (classification ON) restores 1 spawn / no reconnect (A3b). A
   self-heal proxy should therefore ship with classification enabled.
4. **Option B is the smallest, most uniform close.** The interception fires
    at the reconnect trigger itself, independent of session state — fresh
    (B2) and pre-absorbed (B2b) are both directly measured — preserves the
    clean `ErrorResult` shape (unlike #217's
    classified `ToolCallResult`-with-repr), and requires only public-API
    usage — at the cost of replacing `register_from_mcp` with a 32-line
    registration assembly (22-line `_register_async` loop + 10-line
    `register_with_connection` sync entry; counts from
    `tests/measure_poc_size.py`) because the connection manager is hardcoded
    (integration.py:323).
5. **The two options are complementary rather than competing.** Option A
   additionally *recovers* the mismatch (heals the manifest so the backend's
   real schema is served), which Option B does not do — B only removes the
   amplification and returns the error cleanly. A combined deployment (B for
   the caller-visible cost+shape guarantee, A's heal for manifest
   convergence) would be the strongest, but the brief asks for a comparison;
   the recommendation below reflects the decision-ready answer.

## 11. Recommendation

**Option B is the better path to close the C2 gap, with Option A's heal kept
as an optional complementary improvement rather than the primary mechanism.**
B removes the 2-spawn/2-proxy/reconnect amplification at the exact trigger
(`_call_persistent`). It is **dependency-free but NOT patch-free**: it is a
public `MCPConnectionManager` subclass + public `MCPTool.from_tool_json` /
`registry.register` usage, but the subclass override duplicates a **private,
version-bound internal** of toolregistry 0.15.0 / mcp 2.0.0 and must be
re-validated on every upgrade (see §5.5 and the re-validation trigger
below). It preserves the caller-visible `ErrorResult` verbatim (the one
thing #217's classification degraded), and works uniformly whether or not
the stale schema is pre-absorbed — fresh (B2) and pre-absorbed (B2b) are
both directly tested — with a 57-code-line PoC that closed the gap at 1
spawn / 1 proxy / no reconnect (1799–1830 ms n=3 vs 5612–6132 ms n=3 control
in adjacent runs). Option A is fully effective only in a fresh session (first call
succeeds at 1/1 thanks to the SDK's cache-miss re-absorb), degrades to a
reconnect cycle when the stale schema is pre-absorbed (A2b/A3a, though the
persisted heal then makes the retry succeed), and needs the #217
classification delta to avoid respawn-cost regression on intermittent drift
(A3c vs A3b) — while B's interception has none of those conditions and none
of that delta-dependency. If manifest convergence (serving the backend's real
schema, not just failing cleanly) is desired, adding Option A's heal on top
of B is worthwhile; as a standalone close of the C2 gap, B is the smaller,
more uniform, error-shape-preserving choice.

**Version validity.** This recommendation is valid for **toolregistry 0.15.0
/ mcp 2.0.0** only. Because Option B couples to a private internal
(`MCPConnectionManager._call_persistent`), the conclusion must be
re-validated on every toolregistry / mcp upgrade. A re-validation trigger
issue is filed under epic #212 (see §8).

## 12. Transport scope

Every finding in this report is for **stdio transport only** — stdio for
both the ToolRegistry→proxy hop and the proxy→backend hop. Streamable HTTP,
SSE, and websocket transports were **not** tested (matching #196/#213/#217
scope).

## 13. Log index

All logs under `research/toolregistry-lazy-mcp/c2-gap-investigation/logs/`.
The committed corpus is the fresh run (2026-08-08); the original
load-affected run is preserved untouched in `logs/preserved-initial-run/`.

| Phase | Harness log | Proxy log | Extra |
|---|---|---|---|
| A1 control | `phase-a1-control-harness.log` | `phase-a1-control-proxy.log` | |
| A2 self-heal C2 | `phase-a2-selfheal-c2-harness.log` | `phase-a2-selfheal-c2-proxy.log` | `phase-a2-selfheal-c2-heal-state.json` |
| A2b pre-absorbed | `phase-a2b-preabsorbed-harness.log` | `phase-a2b-preabsorbed-proxy.log` | `phase-a2b-preabsorbed-heal-state.json` |
| A3 intermittent | `phase-a3-intermittent-harness.log` | `phase-a3-a3a-proxy.log` / `phase-a3-a3b-proxy.log` / `phase-a3-a3c-proxy.log` | `phase-a3-a3a-heal-state.json` |
| B1 traceback | `phase-b1-traceback-harness.log` | `phase-b1-traceback-proxy.log` | |
| B2 PoC | `phase-b2-poc-harness.log` | `phase-b2-poc-proxy.log` | |
| B2b PoC pre-absorbed | `phase-b2b-preabsorbed-harness.log` | `phase-b2b-preabsorbed-proxy.log` | |
| PoC size | `logs/measure-poc-size.log` | — | emitted by `tests/measure_poc_size.py` |
| n=3 re-measurements | `logs/n3/phase-{a1-control,a2-selfheal-c2,b2-poc}-run{1,2,3}-harness.log` | `logs/n3/phase-...-run{1,2,3}-proxy.log` | A1/A2/B2 latency ranges |
| A3 threshold sweep | `logs/n3/phase-a3-n2-harness.log` / `logs/n3/phase-a3-n3-harness.log` | — (full interleaved `PROXY|` stream carried in each harness log) | N=2 / N=3 flapping check |

The harness logs contain the full interleaved stream (`HARNESS|`, `PROXY|`,
`BACKEND|` prefixed lines), including the `INVOKE ... delta_ms` measurement
lines and the per-phase `*_RESULT` / `*_SPAWN_COUNTS` verdict lines. Proxy-only
logs are written by each proxy process via `PROXY_LOG_FILE`; multiple
`proxy_started` blocks in one log (different pids) are the reconnect
evidence.

## 14. Limitations and conventions

**What was NOT tested before this report closed** (declared scope, per the
Phase-2 audit gaps G2/G4/G5/G6/G10):

* **Option B pre-absorbed (B2b):** not run before this revision — the §8
  "fresh or pre-absorbed" uniformity claim was inferred, not tested. Now
  directly measured (§5.3b): PASS. (G2)
* **Option B warm call / other-tool-untouched:** not measured before this
  revision — B had one traceback + a one-call PoC. Now recorded in B2b
  (warm repeat 9 ms, other tool `multiply` SUCCESS 7 ms). (G6)
* **Latency n:** A1/A2/B2 were n=1 single measurements; now re-measured to
  n=3 under normal load with ranges (§7). A2b/A3a-c/B1/B2b remain n=1.
  (G4)
* **Flapping threshold sweep:** only N=1 was tested before this revision;
  N=2 and N=3 are now run (no flapping at any N; heal stays quiescent at
  N≥2 on alternating drift). (G5)
* **Single host, all processes local** — no cross-host or containerised
  measurements.
* **stdio transport only** — streamable HTTP / SSE / websocket untested
  (§12).

**Conventions adopted** (per the Phase-2 audit recommendations and the
plan addendum):

* **"tested" = directly measured only.** Throughout this report, "tested"
  appears only for session states that were actually run (fresh B2,
  pre-absorbed B2b). Anything argued from mechanism is labelled as such.
  (big-pickle R5 / SR2 convention half.)
* **Agent-computed metrics are script-emitted.** PoC line counts come from
  the committed `tests/measure_poc_size.py` (S1 mitigation), not from
  hand-computed figures.
* **Version-bound findings carry an expiry marker** — §8/§11 state their
  validity for toolregistry 0.15.0 / mcp 2.0.0 and a re-validation trigger
  is filed under epic #212 (G8).
* The line-wide tested-vs-inferred label convention across
  #196/#213/#217/#228 is filed as a follow-up note on epic #212 (deferred
  with rationale: retrofitting prior reports is out of scope for this
  execution).
