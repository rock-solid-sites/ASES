# Harness Evaluation: Microsoft AutoGen

**Date:** 2026-06-23
**Evaluator:** OpenCode (Principal/Orchestrator Agent)
**Source/URL:** https://github.com/microsoft/autogen · https://www.microsoft.com/en-us/research/project/autogen/ · https://arxiv.org/abs/2308.08155

Method: Heuristic Scouting (see `methodology-reviews/Heuristic-Scouting.md`). Scout: WebFetch proxies for GitHub README, MS Research overview, arXiv abstract. Verify: subagent dispatch to fetch AgentChat memory docs, AgentChat teams docs, `agbench` README, MAF repo, and AutoGen → MAF migration guide.

## 1. Overview

Microsoft AutoGen is an open-source **multi-agent orchestration framework**, not a coding harness in the OpenCode / OpenClaudia / CodeWhale sense. It provides primitives for defining agents, composing them into teams with first-class conversation patterns, and connecting them to model clients, tools, code execution, and MCP servers. The framework is delivered as a three-layer library (Core API → AgentChat API → Extensions API) plus two developer tools (AutoGen Studio for prototyping, AutoGen Bench for benchmarking).

AutoGen is now in **maintenance mode** as of 2026, with the Microsoft Agent Framework (MAF) as the recommended successor for new projects.

This evaluation is scoped to: layer-alignment against the EDASES architecture (Addendum 01), memory and persistence model, organizational primitives, verification pathway, and strategic status. It is not a code-review or performance benchmark.

## 2. Architectural Alignment

Evaluated against the EDASES layered architecture from `research-addenda/Research Addendum 01.md` (Principal / Organizational / Knowledge / Capability / Verification / Execution).

*   **Principal Layer:** Not addressed. No Principal-facing dashboard, oversight surface, evidence-review UI, or decision-support console is part of the framework. AutoGen Studio exists but is positioned as a prototyping GUI, not a Principal surface.
*   **Organizational Layer:** Substantial, in-process. Provides agent roles (`name` + `description` + `system_message`), five first-class team patterns (`RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm`, `GraphFlow`), and `AgentTool` for agent-as-tool composition. Conversation state is held in typed `BaseChatMessage` lists inside `TaskResult`; teams expose `reset()` but no org-level memory store.
*   **Knowledge Layer:** Partial, per-agent. A `Memory` protocol (`add`, `query`, `update_context`, `clear`, `close`) is provided, with multiple shipped backends (`ListMemory`, `ChromaDBVectorMemory` / `PersistentChromaDBVectorMemoryConfig`, `RedisMemory`, `Mem0Memory`). Core API lists "memory as a service" as a modular feature. There is no organizational-level knowledge store; memory is agent-attached and backend-configured by the user, not org-orchestrated.
*   **Capability Layer:** Substantial. Pluggable model clients (OpenAI, Azure, etc.) via `autogen-ext`, `Component` serialization to declarative JSON, and MCP-server integration (e.g., Playwright MCP via `McpWorkbench`). No capability registry or capability-routing decision layer is built in.
*   **Verification Layer:** Not provided in the framework. `AutoGenBench` (`agbench`) is a **separate package** that runs predefined tasks in fresh Docker containers and tabulates completion metrics — a benchmarking harness, not an in-loop test/review mechanism. There is no testing, review, formal verification, or confidence-generation pathway inside the runtime itself.
*   **Execution Layer:** Strong. Code execution, MCP tool integration, file handling, and Magentic-One's generalist team (web browsing + code + files) are all first-class.

**Summary:** AutoGen is a strong **Execution + Capability engine** with substantial **Organizational** (in-process) support, partial **Knowledge** (per-agent, pluggable), and explicitly lacks **Principal** and **Verification** layers.

## 3. Key Capabilities & Features

*   Async, event-driven Core API with local and distributed runtime; cross-language support for Python and .NET at the Core level only.
*   AgentChat preset teams: `RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm`, `GraphFlow` (DiGraph-based).
*   `AgentTool` for agent-as-tool composition (a coordinator agent invokes other agents as tools).
*   Pluggable `Memory` protocol with multiple shipped backends spanning in-process, on-disk, networked, and managed-cloud options.
*   `Component` serialization: agents, teams, and termination conditions export to / load from declarative JSON via `.dump_component()` / `.load_component()`.
*   First-class OpenTelemetry integration for tracking, tracing, and debugging agent interactions (added in v0.4 redesign).
*   MCP server integration via `McpWorkbench` (StdioServerParams) — agents can consume external tool servers such as Playwright.
*   Magentic-One: a built-in generalist multi-agent team for web browsing, code execution, and file handling.

## 4. Observations

Atomic, source-cited facts extracted during the Verify step.

### Memory and persistence model

*   **OBS-01:** AgentChat provides a `Memory` protocol with five key methods: `add`, `query`, `update_context`, `clear`, and `close`. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html)
*   **OBS-02:** The `Memory.update_context` method "mutate[s] an agent's internal `model_context` by adding the retrieved information" and is used inside the `AssistantAgent` class. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html)
*   **OBS-03:** Built-in / extension memory backends shipped in the `autogen_ext` package include `ListMemory` (in-process, list-based), `ChromaDBVectorMemory` (with `PersistentChromaDBVectorMemoryConfig` for on-disk persistence), `RedisMemory` (external Redis server), and `Mem0Memory` (Mem0.ai cloud or local). (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html)
*   **OBS-04:** `PersistentChromaDBVectorMemoryConfig` writes to a `persistence_path` on local disk; the `ChromaDBVectorMemory` config dump shows a `persistence_path` field under `~/.chromadb_autogen` by default. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html)
*   **OBS-05:** AutoGen Core lists "memory as a service" as a modular and extensible feature of the Core API. (Source: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/index.html)
*   **OBS-06:** Teams "are stateful and maintain[] the conversation history and context after each run, unless you reset the team"; teams expose `reset()` to clear state. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
*   **OBS-07:** AutoGen defines a `Component` class that "defines behaviours to serialize/deserialize component into declarative specifications" via `.dump_component()` and `.load_component()`; agents, termination conditions, and teams can all be exported to JSON and re-loaded. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/serialize-components.html)

### Organizational primitives

*   **OBS-08:** AgentChat defines an "Agent" abstraction with attributes `name` (unique) and `description` (text), and methods `run` and `run_stream` that return a `TaskResult`. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html, quoting the agents page)
*   **OBS-09:** First-class preset agents in AgentChat include `AssistantAgent` (LLM-backed) and `UserProxyAgent`; custom agents are created by subclassing `BaseChatAgent` and implementing `on_messages()`. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/serialize-components.html; https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/)
*   **OBS-10:** First-class AgentChat team presets are: `RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm`, and `GraphFlow` (DiGraph builder-based workflow). (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
*   **OBS-11:** `RoundRobinGroupChat` is documented as: "all agents share the same context and take turns responding in a round-robin fashion. Each agent, during its turn, broadcasts its response to all other agents, ensuring that the entire team maintains a consistent context." (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
*   **OBS-12:** `SelectorGroupChat` "selects the next speaker using a ChatCompletion model after each message." (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
*   **OBS-13:** `Swarm` is a team that "uses `HandoffMessage` to signal transitions between agents." (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
*   **OBS-14:** A `GraphFlow` is built via `DiGraphBuilder` and supports "ALL" and "ANY" join conditions across fan-out edges, with `activation_group` and `activation_condition` parameters. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/)
*   **OBS-15:** The unit of state inside a conversation is a list of `BaseChatMessage` objects (e.g., `TextMessage`, `MultiModalMessage`, `ToolCallRequestEvent`, `MemoryQueryEvent`) carried inside `TaskResult(messages=[...])`. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
*   **OBS-16:** AutoGen provides `AgentTool` to wrap an agent as a tool consumable by another agent. (Source: https://github.com/microsoft/autogen)
*   **OBS-17:** A team run returns `stop_reason` (e.g., `"Text 'APPROVE' mentioned"`, `"External termination requested"`); teams accept `termination_condition` objects such as `MaxMessageTermination`, `StopMessageTermination`, `TextMentionTermination`, and `ExternalTermination`. (Source: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)

### Verification pathway

*   **OBS-18:** `AutoGenBench` (package name `agbench`) is a separate package living in the AutoGen monorepo at `python/packages/agbench`, not embedded inside `autogen-core` or `autogen-agentchat`. (Source: https://github.com/microsoft/autogen/tree/main/python/packages/agbench)
*   **OBS-19:** The `agbench` README states: "AutoGenBench (agbench) is a tool for repeatedly running a set of pre-defined AutoGen tasks in a setting with tightly-controlled initial conditions. With each run, AutoGenBench will start from a blank slate." (Source: https://github.com/microsoft/autogen/tree/main/python/packages/agbench)
*   **OBS-20:** "By default, all runs are conducted in freshly-initialized docker containers, providing the recommended level of consistency and safety." (Source: https://github.com/microsoft/autogen/tree/main/python/packages/agbench)
*   **OBS-21:** The README explicitly states "AutoGenBench works with all AutoGen 0.1.*, and 0.2.* versions." (Source: https://github.com/microsoft/autogen/tree/main/python/packages/agbench)
*   **OBS-22:** `AutoGenBench` measures task-completion outcomes in benchmark scenarios including `HumanEval`, `AssistantBench`, and the MagenticOne scenario; per-run artifacts include `timestamp.txt`, `console_log.txt`, `[agent]_messages.json`, and a `./coding` directory. (Source: https://github.com/microsoft/autogen/tree/main/python/packages/agbench)
*   **OBS-23:** `agbench` exposes two main CLI subcommands: `agbench run` (executes tasks and records logs/trace) and `agbench tabulate` (computes metrics from logged results, e.g., task completion rates). (Source: https://github.com/microsoft/autogen/tree/main/python/packages/agbench)
*   **OBS-24:** The AutoGen main README lists `AutoGen Bench` separately from the core framework, as a "benchmarking suite for evaluating agent performance," and pairs it with `AutoGen Studio` under "developer tools" (not "framework API"). (Source: https://github.com/microsoft/autogen)

### Status and successor

*   **OBS-25:** The AutoGen GitHub README displays a "Maintenance Mode" badge that links to `https://github.com/microsoft/agent-framework`. (Source: https://github.com/microsoft/autogen)
*   **OBS-26:** The README contains a `Caution` block with the verbatim text: "**⚠️ Maintenance Mode** AutoGen is now in maintenance mode. It will not receive new features or enhancements and is community managed going forward." (Source: https://github.com/microsoft/autogen)
*   **OBS-27:** The README states: "New users should start with [Microsoft Agent Framework]… Existing users are encouraged to migrate using the [AutoGen → Microsoft Agent Framework migration guide]." (Source: https://github.com/microsoft/autogen)
*   **OBS-28:** The README states: "AutoGen is in maintenance mode, contributions are limited to bug fixes, security patches, and documentation improvements. For feature development, consider contributing to Microsoft Agent Framework." (Source: https://github.com/microsoft/autogen)
*   **OBS-29:** The Microsoft Agent Framework repository (`microsoft/agent-framework`) is a separate project; its README describes it as "an open, multi-language framework for building production-grade AI agents and multi-agent workflows in .NET and Python." (Source: https://github.com/microsoft/agent-framework)
*   **OBS-30:** MAF's stated key features include "graph-based workflows supporting sequential, concurrent, handoff, and group collaboration patterns" and "checkpointing, streaming, human-in-the-loop, and time-travel." (Source: https://github.com/microsoft/agent-framework)
*   **OBS-31:** The MAF migration guide's "Background" section states: "Microsoft Agent Framework… represents a significant evolution of the ideas pioneered in AutoGen and incorporates lessons learned from real-world usage. It's developed by the core AutoGen and Semantic Kernel teams at Microsoft, and is designed to be a new foundation for building AI applications going forward." (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/)
*   **OBS-32:** AutoGen's most recent tagged release is `python-v0.7.5` dated `Sep 30, 2025`; MAF's most recent tagged release is `python-1.9.0` dated `Jun 18, 2026`. (Sources: https://github.com/microsoft/autogen/releases, https://github.com/microsoft/agent-framework/releases)

### Unfetchable sources (transparency)

*   `https://arxiv.org/html/2308.08155v2` — returned HTTP 404 (no HTML rendering at that URL; only the abstract page and the PDF are available).
*   `https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/overview.html` — returned HTTP 404; fell back to the Core index page.
*   `https://arxiv.org/pdf/2308.08155` — fetched as raw binary (not human-readable in the verify session); Q2/Q3 reliance on paper §3–§5 was substituted with the AgentChat user guide and `agbench` README.

## 5. Findings

Conclusions derived from the observations above. Each FIN cites the OBS-* it draws on.

*   **FIN-01 — Memory is per-agent and pluggable, not organizational:** AutoGen provides first-class in-agent memory (a `Memory` protocol plus multiple shipped backends including persistent on-disk, networked Redis, and managed Mem0) and exposes `Component` serialization for declarative save/load. However, memory is attached to the agent or team, not aggregated at an organizational level. Teams are stateful but reset-bound; there is no documented org-wide knowledge store. (OBS-01, OBS-02, OBS-03, OBS-04, OBS-05, OBS-06, OBS-07)

*   **FIN-02 — Strong in-process organizational vocabulary, weak in-org persistence:** AgentChat's organizational surface is rich at the framework level — 2 preset agent types, 5 first-class team patterns (round-robin, selector, Magentic-One, swarm, DiGraph), typed conversation message units, and `AgentTool` for nested agent composition. Termination is also first-class via typed `termination_condition` objects. All of this is held as in-process Python objects; the org-level externalization is delegated to the user (e.g., via `Component` JSON or backend choice). (OBS-08, OBS-09, OBS-10, OBS-11, OBS-12, OBS-13, OBS-14, OBS-15, OBS-16, OBS-17)

*   **FIN-03 — No in-loop Verification layer; only a separate benchmark:** `AutoGenBench` is a sibling package that runs tasks in fresh Docker containers and tabulates completion metrics — useful for evaluation but external to the runtime. The framework itself has no built-in test, review, or formal-verification pathway; it is not the EDASES Verification Layer. (OBS-18, OBS-19, OBS-20, OBS-21, OBS-22, OBS-23, OBS-24)

*   **FIN-04 — Maintenance mode makes AutoGen a sunsetting foundation:** The GitHub README explicitly states AutoGen is in maintenance mode (no new features, community-managed), directs new users to Microsoft Agent Framework, and limits contributions to bug fixes / security / docs. MAF is the production successor with active release cadence (1.9.0 in Jun 2026 vs AutoGen's last 0.7.5 in Sep 2025) and an explicit migration guide. The MAF team's framing — "significant evolution of the ideas pioneered in AutoGen" — confirms AutoGen is the lineage, MAF is the new foundation. (OBS-25, OBS-26, OBS-27, OBS-28, OBS-29, OBS-30, OBS-31, OBS-32)

*   **FIN-05 — Layer-alignment placement:** Against the EDASES layers (Addendum 01), AutoGen delivers Execution (strong) and Capability + Organizational (substantial, in-process), partial Knowledge (per-agent, pluggable backends), and explicitly lacks Principal and Verification layers. It is a Capability/Organizational/Execution engine, not a complete evidence-driven organizational system. (FIN-01, FIN-02, FIN-03, FIN-04)

*   **FIN-06 — Partial empirical support for AH-002 (Progressive Externalization):** AutoGen's design exhibits piecemeal externalization — `Component` JSON serialization, pluggable persistent memory backends, OpenTelemetry tracing — exactly the pattern AH-002 predicts. However, the externalization boundary stops at "agent process + user-configured backend"; it does not extend to an org-orchestrated knowledge store. This is consistent with AH-002 (externalization is happening, but no single framework yet provides the full organizational layer EDASES requires). (OBS-03, OBS-04, OBS-05, OBS-07; cf. AH-002 in `Research Addendum 01.md`)

## 6. Gaps against EDASES Requirements

What is missing to make AutoGen a complete evidence-driven organizational system:

*   **No Principal layer.** No oversight surface, evidence-review UI, decision-support console, or progress dashboard. The Principal (per Addendum 01) has no first-class home in AutoGen.
*   **No in-loop Verification.** No in-runtime testing, code review, formal verification, or confidence-generation pathway. `AutoGenBench` is an external benchmark, not a Verification layer.
*   **No organizational-level knowledge store.** Memory is per-agent. There is no Crosslink-like persistent organizational record, no issue/decision/handoff artifacts surfaced at the org level, and no evidence chain. The `Component` JSON serialization is a step in this direction but is an export mechanism, not a live org store.
*   **Sunsetting trajectory.** Maintenance mode means future EDASES work in AutoGen must be either (a) portable to MAF or (b) accepted as a fixed-target system. MAF is the forward-looking target and should be evaluated separately before any architectural commitment.
*   **No evidence-lineage primitives.** The framework's message types (`TextMessage`, `ToolCallRequestEvent`, `MemoryQueryEvent`, etc.) capture conversation state but not Source → Observation → Finding → Assumption → Decision → Outcome provenance. Building EDASES-style traceability on AutoGen would require a user-built overlay.

**Bottom line for Track B:** AutoGen is a strong candidate for the **Execution + Capability + (in-process) Organizational** subsystems of EDASES, but the Principal, Verification, and org-level Knowledge layers are not in scope. A serious EDASES architecture would treat AutoGen (or MAF, when evaluated) as one subsystem inside a larger organizational platform, consistent with AH-001 and the layered architecture in Addendum 01.
