---
title: "Catalog Scale vs Connector Residency — Session-Boundary Cost-Assumption Validation"
program: EDASES
layer: Research
document_type: Research Finding
status: Validated
authority: Experimental
canonical_repository: edases
depends_on:
  - Documentation Standard
  - Concept: Levels of Abstraction
  - research/toolregistry-lazy-mcp/report.md
  - research/toolregistry-lazy-mcp/output-schema-drift/report.md
  - research/toolregistry-lazy-mcp/retry-classification/report.md
  - research/toolregistry-lazy-mcp/c2-gap-investigation/report.md
  - docs/research/Identifier-First Tool Calling.md
related_documents:
  - docs/research/Identifier-First Tool Calling.md
  - research/toolregistry-lazy-mcp/report.md
implements:
implemented_by:
supersedes:
superseded_by:
last_updated: 2026-08-08
---

# Research Finding: Catalog Scale vs Connector Residency (Phase-5 completion, identifier-first line)

## 1. Purpose and research question

This is an **evidence-only validation task** — a measurement, not a system to
ship. It validates the session-boundary confirmation model's cost assumption:

> Can a tool runtime maintain knowledge of N registered tools while keeping
> physical connector-process residency proportional to K (the number actually
> used), not N (the number configured or refreshed)?

The objective is the decoupling claim: **knowing a capability must not require
continuously paying the physical resource cost of keeping its implementation
alive.** This is the Phase-5 completion for the identifier-first line of the
execution-engine research programme (epic #212).

Throughout this report, **observations** (what the logs and timings show) are
kept distinct from **findings** (interpretation). Observations reference the
artifacts under `logs/`; findings are labelled as such.

## 2. Terminology (used exactly as defined by the brief)

| Term | Meaning |
|---|---|
| **catalog state** | Information to know a tool exists / describe it (NOT residency) |
| **proxy residency** | A lazy proxy process alive after catalog acquisition even though its tool was never invoked — the PRIMARY leakage signal |
| **backend residency** | The actual MCP server process required to execute a tool (expected after invocation, NOT a failure) |
| **active connector** | Required for execution, or retained per lifecycle policy |
| **teardown on** | Immediate disconnect-after-list (the crude boundary case, NOT the configurable idle-timeout feature — which is out of scope throughout) |

Proxy residency and backend residency are **always reported as separate
numbers** in this report — never collapsed into one "connector process" count.

## 3. Environment and exact versions

| Component | Version | Notes |
|---|---|---|
| `toolregistry` | **0.15.0** | installed at `/tmp/toolregistry-venv` (reused, not reinstalled) |
| `mcp` (Python SDK) | **2.0.0** | direct dependency of the `[mcp]` extra |
| Python | **3.10.12** | venv python |
| Platform | Linux | single host, all processes local |

Versions re-confirmed per run via `importlib.metadata` and recorded in every
per-run JSON result (`versions` field).

**Persistence-related configuration state (addendum B — verified against the
installed source, not assumed):** the parameter governing persistence is
`persistent: bool = True` on `register_from_mcp` /
`register_from_mcp_async` (`toolregistry/_mixins/registration.py:94,167`)
and on `MCPConnectionManager.__init__` (`toolregistry/integrations/mcp/
connection.py:37`). Default is `True` — the persistent connection is held
lazily across calls (created on first `call_tool`), which is the exact
configuration used for every run in this report.

## 4. Method

### 4.1 The connector model under test

Each connector is one lazy stdio proxy (`proxy.py`, reused from the #213
corpus via a copy under `catalog-scale/`) in front of one trivial stdio MCP
backend (`backend.py`, one `add(a,b)` tool). N connectors = N registered
tools (one per connector, namespaced `c0-add` … `cN-1-add`), registered into
a fresh `ToolRegistry` per run. Transport is **stdio only** — both the
ToolRegistry→proxy hop and the proxy→backend hop.

### 4.2 What "catalog acquisition (session-init refresh)" means here

ToolRegistry 0.15.0 has **no public catalog-refresh API**. Source read shows
two equivalent discovery paths, both via a **temporary `MCPClient`** that
spawns the proxy, lists tools, and closes it (the process exits when its
stdin closes):

- registration: `async with MCPClient(transport, ...) as client: ... await
  client.list_tools()` (`toolregistry/integrations/mcp/integration.py:331`);
- refresh: `MCPConnectionManager.list_tools()` uses the identical temp-client
  pattern (`toolregistry/integrations/mcp/connection.py:73`).

The session-init refresh in every test is therefore operationalized as each
connection manager's `list_tools()` — the same code path registration uses.
This matters because the temp client is the mechanism that already yields
zero residency after acquisition (see Finding 1).

### 4.3 Measurement rules

- **resident** = still running and holding resources at the measurement
  instant; briefly-defunct within the stated grace period (2.5 s actual,
  recorded per run) does NOT count; defunct beyond grace = lifecycle finding.
- **peak** = max process count sampled at 50 ms cadence during acquisition
  (concurrency legitimately raises peak; peak is NOT the decisive measure).
- Process classification: /proc cmdline scan matching this worktree's
  `catalog-scale/proxy.py` vs `catalog-scale/backend.py` (also
  `proxy_5a.py` / `backend_5a.py` for Test 5). RSS = summed `VmRSS`.
- Daemon-thread profile: `threading.enumerate()` in the harness process, with
  `async-runtime` counted separately (addendum B).

### 4.4 Calling modes (addendum B — recorded per run)

- **sequential** runs use the **sync** calling mode
  (`register_from_mcp` + `AsyncRuntime.run_sync` refresh). The first sync
  call lazily starts ONE shared daemon thread running a persistent event
  loop (`toolregistry/_async_runtime.py:65`).
- **concurrent** runs use the **async** calling mode
  (`register_from_mcp_async` + `asyncio.gather`). The sync API cannot be made
  truly concurrent — every sync entry point funnels through the single
  shared `AsyncRuntime` loop, which serializes the coroutines
  (`_async_runtime.py:72`).
- **Observed daemon-thread profile (addendum B):** exactly ONE
  `async-runtime` thread exists in sync-mode runs, zero in async-only runs —
  it is a single process-wide shared thread, **not one per connector**. A
  "daemon-thread leak per connector" was NOT observed in any run; the thread
  count never grows with N (recorded in every `resident_after.threads`).

### 4.5 Scope statement

Every finding in this report is for **stdio transport only** — stdio for
both hops. Streamable HTTP, SSE, and websocket were not tested. The full
configurable idle-timeout teardown feature is out of scope; every "teardown"
tested is the crude immediate-disconnect-after-list boundary case. Catalog
invalidation and unreachable-connector failure design are out of scope.
ToolRegistry source is unmodified.

## 5. Host-load caveat for timing data

The host was under heavy concurrent load during most runs (13 users, load
average 11–17; a pre-positioned auditor and other agents running
alongside). **Process-count and residency observations are load-independent**
and are the decisive measurements. Wall-clock durations are inflated by CPU
starvation and are treated as indicative on this host, not benchmark-grade.
Where durations matter they are reported with this caveat attached.

## 6. Test results

### Test 1 — Catalog Acquisition Without Backend Activation — **PASS**

Scope guard: register N connectors, perform catalog acquisition (session-init
refresh), capture proxy-start and backend-start events, wait settlement,
record residency. PASS criterion: `backend_spawn_count == 0`.

| N | Proxy starts (events) | Backend spawns | Resident proxies after | Resident backends after | Peak proxies (sequential) |
|---|---|---|---|---|---|
| 1 | 2 | **0** | 0 | 0 | 1 |
| 5 | 10 | **0** | 0 | 0 | 1 |
| 10 | 20 | **0** | 0 | 0 | 1 |
| 20 | 40 | **0** | 0 | 0 | 1 |
| 50 | 100 | **0** | 0 | 0 | 1 |

(Full per-N JSON: `logs/test1/n*/test1-n*.json`; run stream: `logs/test1/run.log`.)

Observations: proxy starts are exactly 2 per connector (one registration
discovery session, one refresh session); **zero** backend spawn events across
all 100 acquisition proxy sessions; resident-after 0 proxies / 0 backends at
every N; no backend process ever appeared during acquisition. The lazy-backend
premise holds; no stop-and-investigate condition was triggered.

Finding: ToolRegistry 0.15.0 acquisition is **backend-lazy by construction**
— discovery runs over a temporary MCPClient that spawns the proxy, lists
tools, and closes it before any call can occur (source: `integration.py:331`;
`connection.py:73`).

### Test 2 — Catalog Refresh Residency (single N=10) — **PASS**

Full acquisition (register 10 + refresh 10), nothing invoked. Proxies and
backends measured separately.

| Condition | Meaning | Peak proxies | Resident proxies | Peak backends | Resident backends | Backend spawns | Acquisition ms (loaded host) |
|---|---|---|---|---|---|---|---|
| A (no explicit reclamation) | normal/current behavior | 1 | **0** | 0 | **0** | 0 | 436510 |
| B (immediate teardown) | disconnect right after catalog returns | 2* | **0** | 0 | **0** | 0 | 40180 |

\* Transient peak: under load a refresh proxy for connector i+1 could spawn
while connector i's proxy was still exiting; both were defunct within the
2.5 s grace. Peak is not the decisive measure.

Observations: Condition B shows proxy residency ≈ 0 and backend residency =
0 — the proxy's own connection lifecycle does not misbehave. Condition A shows
the **same zero residency without any explicit reclamation**: ToolRegistry's
refresh path uses a temporary client that disconnects after `tools/list`
returns, so "no teardown" and "immediate teardown" are observationally
identical for the catalog-refresh workload at K=0.

(JSON: `logs/test2/test2-condA.json`, `logs/test2/test2-condB.json`.)

### Test 3 — Scaling Sweep (N = 1, 5, 10, 20, 50) — **PASS**

Four conditions per N (sequential/concurrent × teardown off/on), 20 runs.
Calling mode: sequential → sync (`register_from_mcp`), concurrent → async
(`register_from_mcp_async` + gather) — recorded per run. RSS is 0 kB for all
rows because resident counts are 0.

| N | Mode | Teardown | Call mode | Peak proxies | Resident proxies | Peak backends | Resident backends | Proxy RSS kB | Backend RSS kB | Acq ms | AsyncRuntime threads | Backend spawns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | sequential | off | sync | 1 | **0** | 0 | **0** | 0 | 0 | 3544 | 1 | 0 |
| 1 | sequential | on | sync | 1 | **0** | 0 | **0** | 0 | 0 | 3019 | 1 | 0 |
| 1 | concurrent | off | async | 1 | **0** | 0 | **0** | 0 | 0 | 2545 | 1 | 0 |
| 1 | concurrent | on | async | 1 | **0** | 0 | **0** | 0 | 0 | 3013 | 1 | 0 |
| 5 | sequential | off | sync | 1 | **0** | 0 | **0** | 0 | 0 | 15528 | 1 | 0 |
| 5 | sequential | on | sync | 1 | **0** | 0 | **0** | 0 | 0 | 14900 | 1 | 0 |
| 5 | concurrent | off | async | 5 | **0** | 0 | **0** | 0 | 0 | 10173 | 1 | 0 |
| 5 | concurrent | on | async | 5 | **0** | 0 | **0** | 0 | 0 | 10659 | 1 | 0 |
| 10 | sequential | off | sync | 1 | **0** | 0 | **0** | 0 | 0 | 32973 | 1 | 0 |
| 10 | sequential | on | sync | 1 | **0** | 0 | **0** | 0 | 0 | 27266 | 1 | 0 |
| 10 | concurrent | off | async | 10 | **0** | 0 | **0** | 0 | 0 | 18542 | 1 | 0 |
| 10 | concurrent | on | async | 10 | **0** | 0 | **0** | 0 | 0 | 15813 | 1 | 0 |
| 20 | sequential | off | sync | 1 | **0** | 0 | **0** | 0 | 0 | 52291 | 1 | 0 |
| 20 | sequential | on | sync | 1 | **0** | 0 | **0** | 0 | 0 | 53344 | 1 | 0 |
| 20 | concurrent | off | async | 20 | **0** | 0 | **0** | 0 | 0 | 33192 | 1 | 0 |
| 20 | concurrent | on | async | 20 | **0** | 0 | **0** | 0 | 0 | 35214 | 1 | 0 |
| 50 | sequential | off | sync | 1 | **0** | 0 | **0** | 0 | 0 | 125464 | 1 | 0 |
| 50 | sequential | on | sync | 1 | **0** | 0 | **0** | 0 | 0 | 115812 | 1 | 0 |
| 50 | concurrent | off | async | 50 | **0** | 0 | **0** | 0 | 0 | 79759 | 1 | 0 |
| 50 | concurrent | on | async | 50 | **0** | 0 | **0** | 0 | 0 | 80381 | 1 | 0 |

DECISIVE MEASUREMENT (resident-after, not peak): **resident-after is exactly
flat at 0 proxies / 0 backends as N grows from 1 to 50, under every mode and
teardown condition, with K=0.** Peak proxies equal the concurrency degree (1
sequential, N concurrent) — transient, as expected. Backend peak is 0
everywhere.

(Per-run JSON: `logs/test3/n*-\*.json`; run stream: `logs/test3/run.log`.)

### Test 4 — Sparse-Use Workload (N=20, K=3) — principal scenario — **PASS**

Acquire full 20-tool catalog at init without invoking; invoke exactly 3
selected tools (c0, c7, c15) twice each (steady state); measure residency in
three categories.

| Category | N | K | Teardown | Resident proxies | Resident backends | RSS kB (proxy) | RSS kB (backend) |
|---|---|---|---|---|---|---|---|
| Called tools (3) | 20 | 3 | off | 3 | 3 | 190660 | 188880 |
| Called tools (3) | 20 | 3 | on (before teardown) | 3 | 3 | 190480 | 188948 |
| Called tools (3) | 20 | 3 | on (after explicit teardown) | **0** | **0** | 0 | 0 |
| **Refreshed-but-never-called (17)** | 20 | 3 | off | **0** | — | 0 | — |
| **Refreshed-but-never-called (17)** | 20 | 3 | on | **0** | — | 0 | — |

Observations:
1. **Called tools' backends (3): resident** — persistence expected, not a defect.
2. **Called tools' proxies (3): resident post-call** — ToolRegistry holds the
   persistent MCP connection (`connection.py:42` `_client` kept after first
   call); the proxy and its backend stay alive for reuse.
3. **Refreshed-but-never-called tools' proxies (17): 0 resident** — THE
   HEADLINE NUMBER, under both teardown off and on. The 17 connectors that
   were registered and refreshed but never invoked leave zero proxy
   processes behind after settlement.
4. Explicit teardown (close all 20 connection managers) reclaims everything:
   resident drops to 0 proxies / 0 backends.

Addendum D (connector identity/reuse): for each called connector, the proxy
PID and backend PID are **identical across acquisition → first call → second
call** (e.g. c0: proxy 2572274/2572274, backend 2572278/2572278). The
resident count of 3+3 is therefore 3 correctly-reused active connectors, not
3 new + 3 abandoned netting to the same count. (Acquisition proxy pid is null
by design — no persistent proxy exists at acquisition.)

(JSON: `logs/test4/test4-teardown-off.json`, `logs/test4/test4-teardown-on.json`.)

### Test 5 — Catalog Invalidation Behavior (characterize, do NOT fix)

#### 5a INVALIDATION TEST — observations

Sequence: register connector a (proxy_5a declares `tools.listChanged: true`),
first call `a-add` succeeds (backend spawned, 1 persistent proxy + 1 backend
resident), backend tool set modified (add removed, sub added), control call
`a-_emit_list_changed` makes the proxy emit `notifications/tools/list_changed`
to the client.

| Question | Observation |
|---|---|
| Did the proxy emit the notification? | **Yes.** `sent notifications/tools/list_changed` (proxy log; `logs/test5/5a/a-proxy.log`). |
| Did the registry's catalog change? | **No.** `catalog_initial == catalog_after_notify == ['a-_emit_list_changed', 'a-add']`; `catalog_changed = False`. |
| Did the registry refresh / re-list? | **No.** No `tools/list` request from ToolRegistry after the notification. |
| Any unnecessary backend start? | **No.** `backend_spawn_start = 1` total (only the legitimate first call). |
| Residual residency? | Unchanged: 1 proxy + 1 backend before and after the notification. No new processes. |
| Fresh refresh after the change? | Returns the **stale static manifest** (`['_emit_list_changed','add']`) via a temp client, while the live backend serves `['sub']` — the refresh path cannot see the backend-side change. |

Finding (implementation gap, NOT a bug to fix here — recorded as the brief
requires): **ToolRegistry 0.15.0 does not consume or propagate
`notifications/tools/list_changed`.** Source-verified: the SDK `ClientSession`
parses the notification (it is a known method in the core tables for the
negotiated 2025-11-25 protocol, `mcp_types/methods.py:217`), but ToolRegistry's
`MCPClient` registers no message handler and has zero `list_changed` code
(grep-verified across the installed package). This is the widely documented
current gap across major MCP clients; it is a characterization, not a fix.

#### 5b STALE-CATALOG BASELINE — observations (baseline measurement, no drift-detection expectation)

Sequence: register connector b, refresh (temp client), backend tool set
changed to `{sub}` with **no signal**, then next first-use of `b-add`.

| Question | Observation |
|---|---|
| Catalog retained as-is? | **Yes.** `catalog_initial == ['b-_emit_list_changed','b-add']`; a fresh refresh returns the same stale static manifest. |
| Next first-use of a tool whose backend changed underneath it? | Returns an **application-level error**: `error: unknown tool 'add'` with `is_error=True`. NOT a connection failure — no reconnect, no respawn, no extra process. |
| Tool added on the backend but absent from the catalog? | `registry.invoke("b-sub", ...)` → `KeyError: "Tool 'b-sub' is not registered"` — the registry refuses to call tools it does not know. |
| Residency | 0 proxies / 0 backends before first use (clean baseline); 1 proxy + 1 backend after first use (the called connector's persistent pair — expected). |

Finding: with no invalidation signal, the stack retains the previous catalog
as-is and there is **no drift detection** — the first use of a changed tool
fails at the backend with a clean application error. This is the baseline the
session-boundary model assumes; no signal, no refresh, no surprise spawns.

### Test 6 — Immediate Teardown as a Boundary Condition — **PASS**

Reframes the teardown dimension: if the runtime explicitly disconnects the
catalog-acquisition proxy right away, does physical residency disappear?

| Phase | Resident proxies | Resident backends |
|---|---|---|
| Catalog-refresh workload (N=10, K=0), NO teardown | **0** | **0** |
| Catalog-refresh workload, IMMEDIATE teardown | **0** | **0** |
| After 1 call (K=1, persistence expected) | 1 | 1 |
| After immediate teardown of all managers | **0** | **0** |

Finding: immediate teardown **suffices** for the catalog-refresh workload —
but it is not even required for it, because ToolRegistry 0.15.0's refresh path
already disconnects after `tools/list` (temp client). The only residency that
appears is the called connector's persistent pair (K), and it is fully
reclaimable by explicit teardown. The eventual configurable idle-timeout
feature is therefore a **policy optimization**, not a prerequisite for the
core scaling claim.

## 7. One-sentence scaling conclusion

**Resident connector-process count scales with K (actually used), not N
(configured/refreshed): at K=0, resident proxies and backends are both 0 at
every N from 1 to 50 across all 20 sweep runs (Test 3), and at N=20/K=3
exactly the 3 called connectors' proxies+backends are resident while the 17
refreshed-but-never-called tools' proxies are 0 (Test 4).**

Supporting measurement: Test 3's decisive resident-after column is 0/0 in
every one of the 20 rows; Test 4's headline category (17 never-called
proxies) is 0 under both teardown conditions; Test 1's acquisition produced
100 proxy sessions with zero backend spawns.

## 8. Architectural conclusion

**STRONG PASS.**

- Catalog size up with K=0 → resident connector processes ≈ 0: **confirmed**
  at N = 1, 5, 10, 20, 50, sequential and concurrent, teardown off and on
  (20/20 sweep rows: 0 proxies, 0 backends resident-after).
- N ≫ K → resident connector resources bounded by workload/lifecycle policy
  rather than increasing proportionally with N: **confirmed** — at N=20, K=3
  the resident population is exactly the 3 called connectors (3 proxies + 3
  backends); the 17 refreshed-but-never-called connectors hold zero
  processes. (Addendum C: the claim is NON-SCALING with N, not a literal
  resident-count==K identity — in this stdio model each connector maps 1:1
  to a proxy+backend pair, so the observed population is K pairs.)
- The session-boundary model's cost assumption is **validated**: knowing N
  tools costs no connector residency at K=0.
- Immediate teardown is sufficient for the catalog-refresh workload — indeed
  ToolRegistry 0.15.0's temp-client refresh already achieves the minimum
  without any teardown policy. The configurable idle-timeout remains useful
  as general lifecycle policy but is **no longer a prerequisite** for the
  core catalog-scale claim.

Caveats that keep this from overclaiming:
- **stdio only** — both hops. Other transports are untested.
- ToolRegistry 0.15.0's discovery path is inherently temporary (temp client);
  a future ToolRegistry that kept discovery connections alive would need the
  teardown policy to preserve the same property.
- Host load inflated all wall-clock durations; counts/residency are
  load-independent.

## 9. Behaviours and findings beyond the brief's expectations

1. **Registration/refresh is inherently disconnect-after-list in ToolRegistry
   0.15.0.** Both registration discovery (`integration.py:331`) and the
   connection manager's `list_tools()` (`connection.py:73`) use a temporary
   MCPClient that closes after listing. Consequence: the "no teardown"
   condition already achieves the "minimum achievable" residency at K=0; the
   teardown dimension only matters for CALLED (persistent) connectors. This
   is the mechanism behind the STRONG PASS.
2. **The daemon thread is shared, not per-connector (addendum B).** Async-only
   runs hold zero `async-runtime` threads (verified in a fresh process:
   `logs/threadcheck/threadcheck.json` — 1 thread, MainThread only); the
   first sync call starts exactly ONE process-wide `async-runtime` daemon
   thread, and the count never grows with N (observed 1 at every N and in
   every sync run). A "daemon-thread leak per connector" was NOT observed.
   Sync mode additionally shows anyio's `ThreadPoolExecutor-0_0` and a
   `waitpid-2` reaper thread (4 threads total after a sync call).
3. **Orphaned connectors on owner-process death (lifecycle finding).** When
   the ToolRegistry process exits WITHOUT explicitly closing persistent MCP
   connections, the proxy and backend processes persist indefinitely —
   observed three times, still alive 15+ minutes after parent death, blocked
   in `ep_poll` with stdin at EOF (no write end held by any process). The
   mcp 2.0.0 stdio server does not terminate on bare EOF in this state.
   Consequence: reclamation of connector processes REQUIRES explicit teardown
   (the lifecycle policy); process death alone is not sufficient. This is a
   constraint the session-boundary runtime must assume.
4. **Proxy exit path can be noisy (observation).** The mcp 2.0.0
   `stdio_server.__aexit__` occasionally raises a `BrokenPipeError`
   ExceptionGroup when the client closes while the server flushes. The
   process still exits in the normal close path; the traceback appears in
   run logs (e.g. `logs/test2/run.log` tail).
5. **SDK re-lists after the first call on a persistent session (reproduced).**
   Round-1 item 2 reproduces: the persistent proxy sees a `tools/list` right
   after the first `tools/call` response (proxy_5a log, `live_tools=['add']`),
   and the proxy must keep answering it.
6. **A crashed/raised proxy handler triggers ToolRegistry's reconnect once.**
   During Test 5 instrument debugging an instrument bug made the proxy raise
   inside `on_call_tool`; ToolRegistry's `_call_persistent` reconnected and
   respawned the proxy+backend before retrying (source `connection.py:106`).
   Not a finding about the stack (the crash was instrument-induced), but
   confirms the reconnect-retry layer exists at the proxy level.

## 10. Log index

All logs under `research/toolregistry-lazy-mcp/catalog-scale/logs/`:

| Test | Run stream | Per-run artifacts |
|---|---|---|
| Test 1 | `test1/run.log` | `test1/n*/test1-n*.json`, per-connector proxy logs |
| Test 2 | `test2/run.log` | `test2/test2-cond{A,B}.json`, `test2/condition-{A,B}/*-proxy.log` |
| Test 3 | `test3/run.log` | `test3/n*-{sequential,concurrent}-{off,on}.json` (20 runs), per-run proxy logs |
| Test 4 | `test4/run.log` | `test4/test4-teardown-{off,on}.json`, `test4/teardown-{off,on}/*-proxy.log` |
| Test 5 | `test5/run.log` | `test5/5a/test5a.json`, `test5/5b/test5b.json`, proxy logs (`5a/a-proxy.log`, `5b/b-proxy.log`), control files |
| Test 6 | `test6/run.log` | `test6/test6.json`, `test6/run/*-proxy.log` |
| Addendum B | `threadcheck/run.log` | `threadcheck/threadcheck.json` |
| Orchestration | `run-all*.log` | sequential test runner output |

Every result JSON embeds: `versions` (toolregistry 0.15.0, mcp 2.0.0,
python 3.10.12), `calling_mode` (sync/async), `teardown` (off/on),
`grace_seconds` (2.5), and the `resident_after.threads` profile. The
persistence config state for every run is `persistent=True` (default),
verified against the installed source (`registration.py:94`,
`connection.py:37`).

