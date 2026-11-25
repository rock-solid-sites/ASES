---
title: "Project: Identifier-First Tool Calling for Token- and Resource-Efficient AI Agents"
program: EDASES
layer: Research
document_type: Research Framework
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - Documentation Standard
  - Concept: Levels of Abstraction
  - research/toolregistry-lazy-mcp/report.md
  - research/toolregistry-lazy-mcp/output-schema-drift/report.md
  - research/toolregistry-lazy-mcp/retry-classification/report.md
  - research/toolregistry-lazy-mcp/c2-gap-investigation/report.md

related_documents:
  - research/toolregistry-lazy-mcp/report.md
  - research/toolregistry-lazy-mcp/output-schema-drift/report.md
  - research/toolregistry-lazy-mcp/retry-classification/report.md
  - research/toolregistry-lazy-mcp/c2-gap-investigation/report.md

consumed_by:
  - identifier-first research programme

last_updated: 2026-08-08
---

# Project: Identifier-First Tool Calling for Token- and Resource-Efficient AI Agents

> **Local research reconciliation (2026-11-25) — operation identity, description compression and task intent.** The original EDASES research framework and its two independent axes are retained below. This note reconciles the interface-description axis with later experimental evidence; it does not adopt the proposed ToolRegistry/Lexicon realization, establish current landscape novelty or settle connector lifecycle, drift and retry questions.

## Interface-description axis — what the later experiments actually establish

The original Phases 1–4 distinguish comparative baselines, an identifier-only representation, incremental augmentation and compiled-CLI comparison. The [capability/schema validation research index](../../research/capability-schema-validation/README.md) preserves later #498 and #530 experiments addressing part of that question.

| Original question | Evidence and current disposition |
| --- | --- |
| Phase 1 — raw/progressive MCP, CLI and compiled-CLI baseline | No matched comparison across these four baselines recovered in the reviewed sources. The later experiments compare representations within their own harness; description-block token savings do not establish proximity to a CLI baseline or a whole-task cost advantage. |
| Phase 2 — identifiers with summary/search hint only | The precise `nsid`, `cid`, `summary`, `search_hint` representation remains untested in the recovered series. Both #498 and #530 use stable operation IDs in their full and compressed arms, and retain parameter shape information in the compressed arm. Their results cannot isolate the causal contribution of an identifier or validate NSID ownership/CID resolution. |
| Phase 3 — minimal sufficient augmentation | #498 tests full, short and concise descriptions with names/types and enum literals across 14 operations/22 tasks (198 deterministic harness trials). Its 73.3% description reduction and 98.4% proxy argument accuracy versus 100% full are not live model results. #530 adds one actual model comparison on a 17-operation corpus with 24 tasks per arm, one repetition, temperature 0. Its minimal representation retains names/types, required/optional and enum literals, omitting some authoritative constraints. This is partial evidence for an augmented payload, not a sweep identifying the minimum sufficient interface. |
| Phase 4 — comparison against compiled CLI | No head-to-head outcome recovered; no comparative superiority claim. Dynamic resolution, namespace consistency and version pinning remain candidate properties to demonstrate independently of token counts. |

### Live evidence: the success condition matters

The [#530 report](../../research/capability-schema-validation/corpus-530/report.md) and [measurement summary](../../research/capability-schema-validation/corpus-530/measurements/summary.json) record 8,915 → 2,588 description-block tokens (71.0% reduction); selection 24/24 in both arms; full/minimal harness-valid arguments 23/24 versus 22/24 (4.2 percentage-point loss, inside 5pp); strict expected arguments 23/24 versus 20/24 (12.5-point loss, outside 5pp). The summary JSON uses strict equality; the report uses harness validity for its primary tolerance. These results are not contradictory once the measured property is identified. The model was GPT-4o-mini via OpenRouter, issuing JSON in prompt-directed calls rather than a native function-calling API; the experiment did not exercise ToolRegistry/Lexicon discovery or lifecycle.

The lost optional `filter.since` in C3-T11 is concrete intent loss even though authoritative schema validation succeeded. The C3-T10 wording variation is an exact-match difference, not necessarily a semantic failure. C5-T18's invalid enum illustrates a different, schema-detectable failure. Recovery likewise distinguishes 8/12 harness-valid repairs from 4/12 expected-argument matches. A structurally valid repair may change the intended value; neither successful validation nor exact equality alone is a complete measure of task fidelity.

The defensible unresolved research question is therefore **what task-relevant information and progressive disclosure are sufficient to preserve intended effects at the lowest practical context and execution cost?** A later study would need an independent semantic/task oracle, valid alternatives, explicit coverage of optional but intent-bearing inputs, and separate measures of selection, validation, effect, repair, total tokens, latency and cost. It would need representative tasks and repeated model comparisons before generalization. This is an analytical research direction, not an approved experiment, new benchmark queue or requirement to extend the frozen corpus.

### Operation identity, authority and realization

Keep the logical operation identity, interface/schema revision, governing authority, actual invocation and observable effect distinct. A compact identifier or content hash can refer to a definition, but neither supplies permission, proves semantic suitability, or guarantees that the live implementation matches that definition. The original internal NSID authority/collision convention remains unresolved in this framework. Whether to use Lexicon, another schema/identifier system or direct native interfaces is a realization question, not implied by stable IDs. The current [ASES task-scoped information method](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) already requires task-relevant authoritative information and source identity; it does not mandate a universal resolver/gateway. The [Resource Solver operation-to-route ontology research](Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) is a separate admission/resource question, not a consequence of compression results.

**Ownership and status:** interface representation, progressive discovery, semantic fidelity and comparative tool-calling efficiency are broadly applicable independent/shared software and agent-tooling research subjects; grouping and primary ownership beyond the retained EDASES record remain unresolved. ASES owns its adopted task-context method and its own realization decisions. Actual protocol/library changes belong to their implementation owners. The original August landscape/novelty claims are dated hypotheses and survey findings, not current verification. Keep connector activation, resource scaling, typed drift/retry and RPC/namespace/authority choices separate for subsequent reconciliation. Do not infer Phase 5/6 completion, production adoption or authorization to rerun #530 from this interface evidence.

Source cutoff: [1c4e12ee](https://github.com/rock-solid-sites/ASES/tree/1c4e12ee5f464254ca185ab2a3ae1719303b9366). No experiment or external landscape survey was performed in this review; original reports, corpora and measurements remain unchanged.

## Connector lifecycle axis — scoped validation and remaining questions (2026-11-25)

The original Phase 5 description says partially complete. Read that against the later [catalog-scale validation](../../research/toolregistry-lazy-mcp/catalog-scale/report.md) (#295/#306), which closes the bounded catalog-residency question, not every original lifecycle objective. The [foundational proxy report](../../research/toolregistry-lazy-mcp/report.md) and catalog-scale evidence are version-bound: ToolRegistry 0.15.0, MCP Python SDK 2.0.0, Python 3.10.12, single Linux host, stdio on both hops. No model is needed to establish these process-lifecycle findings.

| Question | Observed result and limitation |
| --- | --- |
| Can discovery precede actual backend activation? | A temporary proxy supplies cached tool descriptions without spawning the backend; first invocation activates a persistent proxy/backend pair. Subsequent calls reuse that pair. This is not zero-cost discovery or zero process creation. Registration and refresh each start a temporary proxy. |
| Does post-acquisition residency grow with configured catalog size? | At N = 1, 5, 10, 20, 50 connectors (one tool each), K = 0 invoked, 20/20 sequential/concurrent × teardown-on/off sweep conditions settled to zero resident proxies and backends. At N = 50, registration plus refresh starts 100 temporary proxies without a backend spawn. This is scoped process-residency evidence, not a theorem about arbitrary catalogs or total runtime memory. |
| What happens under sparse use? | At N = 20, K = 3 distinct called connectors, three proxy/backend pairs remained; the other 17 left no resident proxy. The [teardown-on record](../../research/toolregistry-lazy-mcp/catalog-scale/logs/test4/test4-teardown-on.json) records summed process RSS of 190,480 + 188,948 kB before explicit close and zero connector processes afterward. This is summed RSS, not unique physical memory, and excludes the registry itself. K counts distinct activated connectors retained by the tested policy, not simultaneously executing calls. |
| Does laziness eliminate transient cost? | No. The [N=50 concurrent acquisition record](../../research/toolregistry-lazy-mcp/catalog-scale/logs/test3/n50-concurrent-off.json) measured 50 peak proxies and 2,824,560 kB peak summed proxy RSS, then zero resident processes. Acquisition took 79,758.8 ms on the loaded host; not benchmark-grade timing. The foundational report observed first-call latency 2,155–2,761 ms (n=3), direct-backend baseline 1,453 ms, and warm calls 7–17 ms versus 3–9 ms direct. Compare peak, settled and cumulative costs separately. |
| Does owner death reclaim retained connections? | **No in this fixture.** The [owner-death record](../../research/toolregistry-lazy-mcp/catalog-scale/logs/owner-death/owner-death-lifecycle.json) confirms three proxies and three backends still alive at 5.11 s after owner exit, with explicit TERM followed by zero processes. The report additionally describes prior observations beyond 15 minutes. Neither establishes infinite persistence; both disprove automatic reclamation in the observed conditions. A cleanup call made only by the departed owner cannot be the entire failure-handling design. |
| Does thread count grow per connector? | No such growth was observed. The [fresh-process thread check](../../research/toolregistry-lazy-mcp/catalog-scale/logs/threadcheck/threadcheck.json) recorded zero shared async-runtime threads after async-only use and one after sync use. The N=50 async-labelled sweep artifact nevertheless records one such thread. Preserve this difference in actual process history; do not claim every async-labelled run had zero threads, or infer execution serialization solely from the presence of one event-loop thread. |

### Status of Phase 5 and scope of follow-up

- **Completed, scoped evidence:** lazy stdio backend activation, reuse, bounded catalog-residency scaling, and explicit live-owner reclamation. The pure addition-tool recovery after backend loss is reachability/reuse evidence, not safe replay of state-changing operations.
- **Observed failure:** owner loss can leave the entire persistent connector pair behind. Any future lifecycle realization needs verified ownership and reclamation under abrupt interruption, not just normal close. Connector lifetime, execution lifetime and durable work identity are distinct. This finding can inform Work Unit research without establishing any particular Engine or Kernel requirement.
- **Still open:** configurable idle timeout and connection pooling across independent consumers or sessions, safe handling of in-flight work during teardown, policy choice for retention, and full eager-versus-lazy comparative CPU/memory/time costs across representative heterogeneous workloads. A live-owner explicit-close test is not an idle-timeout or crash-safe supervision implementation. Distinguish authentication/account/authority isolation and state affinity before considering reuse across sessions. No general transport equivalence or current-library compatibility was verified; retest version-sensitive behavior when relevant. Catalog invalidation, schema drift, typed errors and retries are separate questions.

The surviving research question is how to make **resource cost proportional to useful work without compromising correctness, availability or reclamation**. Separate catalog representation, discovery execution, process startup, retained connections, and actual task execution. A catalog can be cheap to retain but expensive to acquire; a connector can remain expensive after the task that activated it finishes. The older hypothesis of a single integrated ToolRegistry/Lexicon lifecycle runtime remains a candidate realization, not a current architecture decision or demonstrated market gap. No new always-on service, pooling implementation, or scheduled refresh is implied.

**Ownership:** general connector lifecycle, resource scaling and supervision are independent/shared agent-infrastructure research. Actual library/proxy changes belong to their implementation owners; ASES-owned Work Unit authority and continuity requirements and Resource Solver account/meter admission are distinct research areas. Preserve this as a candidate subject for later topic grouping, without creating a new project or reopening the historical programme.

Source cutoff: [dcb29e97](https://github.com/rock-solid-sites/ASES/tree/dcb29e97a1e67d12bd1242e4baa878a7f411b93a). Reviewed the two reports and selected raw artifacts cited above; original corpus and measurements unchanged. No reruns, current upstream survey, deployments or runtime changes. Do not silently reinterpret the dated report's Phase-5 completion label as completion of pooling, idle-timeout policy, or general memory optimization.

## Preserved original research framework

**Status:** Revised investigation; foundational lazy-proxy and validate-before-spawn claims empirically validated (stdio only); connector-lifecycle policy surface (idle timeout, pooling) and a ToolRegistry-internals scope decision remain open
**Target environment:** Model-agnostic, open-source agent harnesses (e.g. OpenCode) using MCP as the primary connector protocol

---

## Executive Summary

This project investigates whether AI tool calling can be redesigned so that models reason primarily over **stable capability identifiers** instead of **verbose tool schemas**, and — as a second, largely independent axis — whether the **connectors themselves** (MCP servers) can be run at a fraction of their current memory and startup cost by activating them only while they're doing work.

The two axes have different maturity levels in the existing ecosystem and are treated separately below:

- **Token cost** (what the model sees in context): the architectural direction here has largely converged industry-wide. Further work is likely incremental (better retrieval, better compression, better summarization) rather than a fundamental change to the model/runtime boundary. This project's contribution on this axis is to combine existing, validated techniques correctly — not to invent a new one.
- **Connector runtime cost** (memory, process count, startup latency for the servers backing those tools): no mature reference implementation combining a typed, validated, namespaced tool registry with lifecycle-aware, on-demand connector activation currently exists. This is the more defensible and more novel part of the project.

---

## Problem Statement

Two distinct costs are conflated in most discussions of "MCP is expensive," and this project treats them as separate problems with separate solutions:

1. **Standing token cost.** Naive MCP tool use injects full JSON Schema definitions for every registered tool into every turn. Reported overhead ranges roughly 4x to over 100x the token cost of an equivalent CLI-style tool call on the same task, depending on catalog size and benchmark. This is a context-window problem.
2. **Connector process/memory cost.** Each MCP server (particularly stdio-transport servers) is typically a persistent process, started at session initialization regardless of whether any of its tools are used, and held resident for the session's duration. Loading a full suite of MCP servers per repository is reported as impractical at scale for exactly this reason. This is an infrastructure problem, and it persists even after the token problem above is fully solved — deferring what's *shown* to the model does not defer *starting* the underlying server.

A viable architecture needs to address both, and the two require different mechanisms.

---

## Landscape Review

### Token cost: converged, multiple validated solutions exist

The following all solve the standing-token-cost problem via variations on the same mechanism — show the model a lightweight index at session start, fetch full schema/detail only for tools actually selected:

- **MCP's own current client guidance** describes a three-layer pattern (catalog → inspect → execute), where only tool name and one-line description are shown up front and full schema is fetched only for a candidate tool before invocation.
- **ToolRegistry's** `defer=True` / `discover_tools` mechanism excludes schemas from the initial prompt and injects them on demand via BM25F-scored search, reporting the same pattern.
- Third-party proxies — **mcp-lazy**, **lazy-mcp** (PyPI), **voicetreelab/lazy-mcp** — and platform-native features such as **Claude Code's MCP Tool Search** all report 90%+ reductions in standing context cost using this approach.
- **mcp2cli / OnlyCLI**-style projects take a different mechanism (compiling MCP schemas into generated CLI commands) to the same end, reporting 92-99% reduction on repeated calls.

Given this, the project's token-axis contribution is not to invent a new discovery mechanism — it's to correctly compose these existing, validated patterns (progressive disclosure via ToolRegistry's discovery mechanism, informed by Lexicon-cached schemas) *and* to answer an open empirical question none of the systems above directly address: what is the minimum interface description required for accurate tool invocation? The identifier-only payload originally proposed (`nsid`, `cid`, `summary`, `search_hint`) is a starting hypothesis for that question, not an assumed answer — it likely needs minimal parameter-shape information (names and types, not full descriptions) to hold up at the argument-construction step, but the actual minimum is unmeasured. That measurement is itself a publishable result, independent of the composition work around it. See Research Program, Phase 2/3 below.

### Connector runtime cost: real, largely unaddressed gap

Checking the same landscape against the process-lifecycle question surfaces a much thinner set of results:

- **ToolRegistry**, by its own architecture documentation, maintains **persistent connections by default** for both MCP and OpenAPI integrations. Its `defer` mechanism only withholds schema visibility from the model — the underlying connection (and, for stdio transport, the subprocess) is established at registration time regardless of use. ToolRegistry does not solve this problem; it should not be listed as "mature" on this axis.
- Most of the token-lazy tools above are **not** process-lazy: PicoClaw's manager connects to all configured servers in parallel at startup specifically to minimize discovery latency, and mcp-lazy's own documentation states its first run connects to every registered server to build a search index, before any lazy behavior applies. Deferring what's shown to the model is routinely conflated with deferring what's running; they are not the same thing in most of these implementations.
- **voicetreelab/lazy-mcp** is the one clear exception found: an MCP proxy that defers actually spawning the backing server until one of its tools is invoked. It validates that on-demand connector activation is practical, but it is a proxy only — it does not attempt typed registration, validation, namespacing, permissions, or multiple execution backends, and it is unconfirmed whether it implements idle-timeout teardown or connection pooling once a server has been spawned (only cold-start deferral is confirmed from available documentation).
- Requests for native, per-server lazy activation (`"lazy": true` config, start-on-first-call) remain **open, unresolved feature requests** against mainstream hosts (Claude Code, OpenCode) as of this writing — a signal that this is a recognized but unmet need at the host level, not a solved problem being reinvented here.
- **MCP's own client best-practices documentation names this exact direction.** Alongside Progressive Discovery and Programmatic Tool Calling, it describes a third, independent pattern — **Dynamic Server Management** — recommending that clients maintain a registry of servers, connect to a server only when the model determines it needs that server's capabilities, and disconnect servers no longer relevant to the task. This confirms the standards body has identified connector lifecycle as a desirable property. What it explicitly does not provide is a reference runtime implementing that policy together with typed registration, validation, namespaces, and pooling — it states the policy and leaves implementation to hosts.

**Conclusion:** to the best of our survey, we did not identify an existing project that combines (a) a typed, validated, namespaced, heterogeneous tool registry with (b) lifecycle-aware connector activation (spawn on demand, idle timeout, pooling, warm/cold start policy) while (c) remaining transparently compatible with existing MCP servers. lazy-mcp demonstrates (b) is practical; ToolRegistry demonstrates (a) is practical; MCP's own documentation recommends (b) as a policy without shipping a reference implementation of it. This is best framed as a direction the standard already points to, not one that hasn't been imagined — the project's contribution is providing the comprehensive, reusable runtime that direction currently lacks. The proposed architecture below is positioned as a fourth layer on top of MCP's own three named patterns (Progressive Discovery → Programmatic Tool Calling → Dynamic Server Management → this project's lifecycle-aware typed registry), not as a replacement for any of them.

**Open item:** this conclusion is based on two independent searches (this review and a separate ChatGPT-assisted search) that surfaced partially non-overlapping tool lists and converged on the same gap. That convergence is reasonably strong evidence, but a reconciled, verified landscape survey (pooling both lists, confirming each candidate is a real, maintained project) should be a first task before implementation begins, given how fragmented and SEO-dependent this space is.

---

## Proposed Architecture

```
                    Lexicon
          canonical schema repository
          (schema format/validators only —
           no live DNS resolution; internal
           namespace-authority convention
           needed in place of it)

                       │
                       ▼

                 ToolRegistry
        registration · namespaces
        permissions · execution
        discovery (defer / BM25F)

                       │
             connection target for
             register_from_mcp()
                       │
                       ▼

              Lazy Connector Layer
        spawn on demand · idle timeout
        cache discovery · connection pool
        validate against cached schema
        BEFORE spawning backing process

                       │
                       ▼

                  MCP servers
```

Key design points:

- The Lazy Connector Layer is a drop-in swap at the connection target ToolRegistry already points `register_from_mcp()` at. **Validated:** a minimal stdio proxy answering `tools/list` from a cached manifest and deferring backend spawn to first `tools/call` works against `register_from_mcp()` with zero modification to ToolRegistry itself — confirmed via a working prototype (cold registration with no backend running, first-call spawn, steady-state reuse without respawn, and genuine connection-failure retry all behaved correctly). This claim is now evidence-backed for **stdio transport only**; streamable HTTP/SSE/websocket transports are untested and should not be assumed to behave the same way. See Validated Prototype Results below.
- Because Lexicon provides a cached, CID-versioned schema independent of whether the backing server is running, the pipeline can validate a tool call's **input** against the cached schema before paying the cost of spawning the actual server process — this half of the claim holds and is a concrete efficiency gain unavailable to lazy-mcp on its own. It does **not** extend to output: whether a call's result conforms to its declared `output_schema` can only be checked after the backend has already responded, meaning **the spawn cost is unavoidable when the cached manifest's output schema has drifted from what the live backend actually returns.** This was tested directly and confirmed — see Validated Prototype Results. "Validate against cached schema before spawning" should be understood as covering request validation only, not response conformance.
- Internal NSID namespace authority (who may register `com.example.foo`) must be defined explicitly as a local convention, since this deployment does not resolve NSIDs over the public internet and therefore has no DNS-based collision backstop.

### Validated Prototype Results

Three rounds of testing (each independently reviewed) against a working stdio proxy in front of ToolRegistry:

**1. Proxy redirect (foundational claim).** Confirmed: `register_from_mcp()` works unmodified against a lazy proxy. Cold registration with the real backend never started succeeds; the first `tools/call` correctly triggers a spawn (observed cold-start range 2155-2761ms, n=3, stdio only); subsequent calls in the same session reuse the running backend rather than respawning; a genuine connection failure (backend or proxy killed) still triggers ToolRegistry's reconnect-retry correctly.

**2. Output-schema drift (confirmed hard-failure mode).** When a cached manifest's `output_schema` no longer matches what the live backend actually returns, the mismatch is undetectable at every layer prior to backend spawn and response — no pre-spawn signal exists. Initial measurement found this compounded badly: the drift failure was misclassified as a connection failure, triggering both the proxy's internal retry and ToolRegistry's reconnect-retry independently, resulting in 4 backend spawns and 2 persistent proxies per single failed call (~2.3-2.4x the latency of a successful call, worst observed 23.7s under load). No refresh/invalidation mechanism exists anywhere in the current stack (ToolRegistry, the SDK, or a Lexicon-CID path) to recover from this automatically — the failure is deterministic and repeats identically on retry. Blast radius is contained: an unrelated tool in the same session is unaffected.

**3. Retry-classification fix (mitigation, partially effective).** Tagging a schema-validation failure as a terminal application error, distinguishable from a connection failure, eliminates the compounding: spawns drop from 4 to 1 and latency drops 57-75% (residual ≈1.35-2.2x a successful call, dominated by the single unavoidable backend init). Confirmed not to overcorrect — genuine connection failures still retry and recover correctly. Two gaps remain unresolved by proxy-only classification, both because they require changes inside ToolRegistry's client rather than the proxy: (a) the caller-visible error is a `ToolCallResult` wrapping the schema error rather than a clean typed error, because ToolRegistry only builds `ErrorResult` from a raised exception, and that same raise is what previously triggered the reconnect; (b) a backend that has been consistently upgraded (its schema now permanently differs from the cached manifest, rather than failing intermittently) is invisible to proxy-side classification, since the triggering exception fires inside ToolRegistry's own client past the proxy's visibility — this variant still pays 2 spawns/2 proxies.

**Implication for scope:** the "no modification to ToolRegistry required" premise holds for the core lazy-activation and input-validation claims, but does **not** fully hold for output-schema-drift handling — closing the two remaining gaps requires deciding whether to extend into ToolRegistry's client internals, which is a materially larger commitment than the proxy-only work done so far. This decision is tracked as an open item below rather than assumed.

### Connector-lifecycle constraints observed (version-bound: toolregistry 0.15.0 / mcp 2.0.0)

Two reusable constraints from the C2-gap investigation (`research/toolregistry-lazy-mcp/c2-gap-investigation/report.md`, #228), valid for **toolregistry 0.15.0 / mcp 2.0.0**; verify on upgrade (re-validation trigger filed under epic #212):

- **The C2 schema-validation exception is SDK-origin, and ToolRegistry 0.15.0 has NO failure-class distinction.** The `RuntimeError("Invalid structured content returned by tool ...")` is raised by the mcp SDK itself at `mcp/client/session.py:1110` (`validate_tool_result`, called from `session.py:1064`), passes through ToolRegistry's `MCPClient.call_tool` (`toolregistry/integrations/mcp/client.py:133`) as a pure pass-through, and trips the catch-all reconnect at `toolregistry/integrations/mcp/connection.py:106` — a bare `except Exception:` that cannot tell a schema-validation failure from a connection loss. Any client-side classification must therefore inspect the exception message, not a failure class.
- **`register_from_mcp` hardcodes `MCPConnectionManager` at `integration.py:323`.** ToolRegistry's registration API constructs the connection manager internally with no injection point / factory / hook / callback, so any connection-layer customisation (subclass, alternate manager, interception) requires manual registration assembly via public API (`MCPTool.from_tool_json` + `registry.register`) instead of `register_from_mcp`. This is the concrete registration-assembly cost for every future connection-layer option in this line.

Three further constraints from the catalog-scale validation (`research/toolregistry-lazy-mcp/catalog-scale/report.md`, #295/#306), also valid for **toolregistry 0.15.0 / mcp 2.0.0**; verify on upgrade (re-validation trigger #279 is already filed under epic #212):

- **Connector processes orphan on owner-process death without explicit close.** When the ToolRegistry process exits WITHOUT explicitly closing persistent MCP connections, the proxy and backend subprocesses persist indefinitely — observed three times, still alive 15+ minutes after parent death, blocked in `ep_poll` with stdin at EOF (reproduced deliberately and committed as `logs/owner-death/owner-death-lifecycle.json`: 3 proxies + 3 backends survived owner SIGKILL through a 5s observation interval, all in `ep_poll`; reclamation required explicit TERM). The mcp 2.0.0 stdio server does not terminate on bare EOF in this state. Consequence for a lifecycle-aware runtime: process death alone is NOT sufficient reclamation — the lifecycle policy must own explicit teardown, and any runtime that assumes OS-level cleanup on owner death will leak connector processes.
- **ToolRegistry 0.15.0 does not consume `notifications/tools/list_changed`.** The SDK parses the notification (`mcp_types/methods.py:217`), but ToolRegistry's `MCPClient` registers no message handler and has zero `list_changed` code (grep-verified). A backend that emits `list_changed` (as lazy proxies do after tool-set mutation) is invisible to the registry: catalog unchanged, no re-list, and a fresh refresh returns the stale static manifest. The `list_changed`-consumption gap is the invalidation half of the drift problem — with no consumer, the refresh path cannot see backend-side changes even when the backend signals them. Also relevant to the SDK-side re-list behaviour: the persistent proxy sees a `tools/list` right after the first `tools/call` response on a persistent session and must keep answering it (report.md §9 item 5).
- **Sync mode runs on ONE process-wide shared thread, not one per connector.** Every sync-mode entry point funnels through the single shared `AsyncRuntime` daemon thread (`toolregistry/_async_runtime.py:65,72`); the thread count is exactly ONE at every N (1-50) and never grows with N (recorded in every `resident_after.threads` profile; `logs/threadcheck/threadcheck.json` shows zero `async-runtime` threads in a fresh async-only process). The sync API cannot be made truly concurrent — all sync calls serialize through that loop. Consequence for a runtime scheduling many connectors in sync mode: concurrency claims must assume serialization at the shared-loop boundary unless the async API is used; "one thread per connector" must not be assumed.

---

## Research Question

Given that the token-cost problem is architecturally converged (further gains are incremental) and the connector-lifecycle problem has no unified reference implementation, the project's central question is:

> Can a typed, validated, namespaced tool registry (ToolRegistry, schema-backed by Lexicon) be combined with a lifecycle-aware connector layer (spawn-on-demand, idle timeout, pooling) to approach CLI-level token efficiency *and* usage-proportional memory/process cost, while remaining a transparent drop-in for existing MCP servers and preserving tool-call accuracy?

A secondary, dependent question: what is the minimum interface information (beyond identifier + summary) a model needs to preserve argument-construction accuracy once full schemas are removed from context?

---

## Research Program

**Phase 0 — Reconciled landscape survey.** Pool all candidate projects identified across independent searches to date, verify each is real and maintained (not just plausible-sounding), and re-run the connector-lifecycle question specifically against the fuller list before any implementation work begins.

**Phase 1 — Baseline measurement (token axis).** Measure token cost and task accuracy on a fixed set of representative tool-calling tasks across: raw MCP, MCP/ToolRegistry with progressive disclosure already applied, a CLI-style baseline, and a compiled-CLI baseline (mcp2cli/OnlyCLI-style). This is the reference frame every later number gets compared against.

**Phase 2 — Minimal-payload prototype.** Implement the identifier-only discovery payload (`nsid`, `cid`, `summary`, `search_hint`) exactly as originally specified and measure tool-selection and argument-construction accuracy against Phase 1's baselines. Expect an accuracy gap on argument construction; treat it as the useful result, not a failed experiment.

**Phase 3 — Augmentation sweep.** If Phase 2 shows an accuracy gap, iteratively add the smallest additional information that closes it (parameter names/types first, full descriptions only if needed), remeasuring token/accuracy tradeoff at each step. This produces the actual answer to "how much interface information does the model need," rather than assuming it.

**Phase 4 — Head-to-head against compiled-CLI.** Compare the resulting payload shape's token cost and capability set directly against mcp2cli/OnlyCLI. If not clearly better on cost, the architecture needs to win on dynamic runtime resolution, cross-server namespace consistency, or version pinning — demonstrated, not asserted.

**Phase 5 — Connector lifecycle baseline and prototype (parallel to Phases 1-4).** **Partially complete.** The proxy-redirect and spawn-on-demand claims are validated (see Validated Prototype Results above): cold-start latency 2155-2761ms (n=3, stdio only), steady-state reuse confirmed, genuine connection-failure retry confirmed. Remaining: idle-timeout teardown and connection pooling are not yet built or tested (the prototype so far covers spawn-on-first-use only); a full eager-vs-lazy memory/process-count comparison against the Phase 1 task set is still outstanding; lazy-mcp's own idle-timeout behavior remains unconfirmed from documentation and was not re-derived from the prototype work, since a purpose-built proxy was used instead of adapting lazy-mcp directly.

**Phase 6 — Validate-before-spawn integration test.** **Complete for input validation; a confirmed limitation was found on output.** Input-side validate-before-spawn works as designed. Output-schema conformance cannot be checked before spawn under any tested configuration — this is now a confirmed property of the architecture, not an open question, with a partially effective mitigation (retry-classification, see above) that bounds but does not eliminate the residual cost. Closing the two remaining gaps identified in the mitigation work is a new, separate decision — see Open Risks.

---

## Success Criteria

- **Token cost:** standing and marginal cost per call materially closer to the CLI baseline than to the optimized-MCP baseline from Phase 1, with an explicit numeric target set once that baseline is measured (not "lower than raw MCP").
- **Accuracy:** tool selection and argument correctness within a small, pre-specified tolerance of the full-schema baseline. This is a constraint, not a metric to trade against token savings.
- **Connector memory footprint:** idle memory for a session with N configured connectors scales with connectors actually used, not connectors configured (e.g., a session touching 2 of 10 configured connectors should carry close to the cost of 2 live connectors).
- **Cold-start latency:** validated at 2155-2761ms (n=3, observed ceiling 2761ms) for stdio transport in the working prototype. This figure is scoped to stdio only — treat it as unvalidated for streamable HTTP/SSE/websocket until those transports are tested separately.
- **Drift-failure cost:** with retry-classification applied, a schema-drift failure should cost no more than ~1.35-2.2x a successful call (validated). Without classification, this cost is unbounded (4x spawns, up to 23.7s observed) and should be treated as a blocking defect, not an acceptable tradeoff.
- **Competitive position (token axis):** either beats the compiled-CLI baseline on the token/accuracy curve, or clearly delivers something that approach structurally cannot (dynamic resolution, versioning, namespacing) at comparable cost.
- **Competitive position (connector axis):** delivers the full property set — typed registry, heterogeneous registrations, validation, namespaces, discovery, on-demand connector instantiation, configurable lifecycle policy, transparent compatibility with existing MCP servers — that no single existing project currently combines.
- **Practicality:** internal NSID namespace/authority scheme works end to end without live DNS resolution, demonstrated in the prototype rather than asserted as solvable.

---

## Open Risks and Unresolved Items

**Resolved by prototype work (no longer open):**

- ~~Whether `register_from_mcp()` can be redirected to a lazy proxy without modifying ToolRegistry~~ — confirmed yes, for stdio transport.
- ~~Whether output-schema drift is a real risk~~ — confirmed yes; confirmed undetectable before spawn under any tested configuration.

**Still open:**

- Internal NSID authority/collision convention is not yet defined and blocks Phase 2 of ToolRegistry namespace usage.
- Idle-timeout teardown and connection pooling are unbuilt and untested — the validated prototype covers spawn-on-demand only, not the full lifecycle-policy surface Phase 5 requires.
- Transport scope: all validated results (spawn redirect, drift behavior, retry-classification fix) are stdio-only. Streamable HTTP, SSE, and websocket transports are untested and results should not be assumed to transfer.
- **New — ToolRegistry-internals decision required.** The retry-classification mitigation resolves the drift-cost problem for the common case but leaves two gaps that cannot be closed from the proxy alone: (a) caller-visible error shape stays a wrapped `ToolCallResult` rather than a clean typed error, and (b) a consistently-drifted backend (vs. an intermittent failure) is invisible to proxy-side classification because the triggering exception fires inside ToolRegistry's own client. Closing either requires extending into ToolRegistry's client internals rather than staying proxy-only — a materially larger scope commitment than anything built so far. This needs an explicit go/no-go decision, weighed against how common the "consistently upgraded backend" scenario (b) is expected to be in real deployments versus the "intermittent/edge-case drift" scenario the current mitigation already covers.
- The Phase 0 landscape survey (reconciling this review's tool list against independently-sourced lists) has not yet been formally completed as a standalone task, though its main purpose — checking whether the connector-lifecycle gap is real — has been substantially addressed by convergent independent searches finding the same gap.

---

## Documentation References

- Lexicon: https://atproto.com/guides/lexicon , https://atproto.com/guides/installing-lexicons , https://atproto.com/guides/publishing-lexicons
- ToolRegistry: https://toolregistry.readthedocs.io/en/latest/ , https://toolregistry.readthedocs.io/en/latest/architecture/overview/ , https://toolregistry.readthedocs.io/en/latest/usage/integrations/mcp/
- MCP: https://modelcontextprotocol.io/docs/learn/architecture , https://modelcontextprotocol.io/docs/develop/clients/client-best-practices (Progressive Discovery, Programmatic Tool Calling, Dynamic Server Management)
- lazy-mcp (proxy, connector-lifecycle prior art): https://github.com/voicetreelab/lazy-mcp
- Smithy: https://smithy.io/2.0/spec/
- OpenAPI: https://spec.openapis.org/oas/latest.html

### Internal Validation Artifacts

- Lazy-proxy validation brief and report — confirms `register_from_mcp()` redirect works unmodified (stdio).
- Validation report revision (commit `b40c980`) — pinned dependencies (`toolregistry==0.15.0`, `mcp==2.0.0`), reconciled timing data, corrected `listChanged` claim with captured `initialize` artifact.
- Output-schema-drift validation brief and report — confirms drift is undetectable pre-spawn; quantifies the 4x compounding failure mode.
- Retry-classification isolation brief and report (`research/toolregistry-lazy-mcp/retry-classification/report.md`) — confirms classification-only fix bounds the drift cost to ~1.35-2.2x; identifies the two residual gaps requiring ToolRegistry-internals changes to close fully.
