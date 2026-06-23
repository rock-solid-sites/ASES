# Harness Evaluation: Microsoft Agent Framework

**Date:** 2026-06-23
**Evaluator:** OpenCode (Principal/Orchestrator Agent)
**Source/URL:** https://github.com/microsoft/agent-framework · https://learn.microsoft.com/en-us/agent-framework/

Method: Heuristic Scouting (see `methodology-reviews/Heuristic-Scouting.md`). 4-step pipeline:

- **Scout:** WebFetch proxies for GitHub README and the official migration guide.
- **Target:** 4 research questions — (1) memory/persistence model, (2) organizational primitives, (3) verification pathway, (4) status/successor.
- **Verify:** Orchestrator directly verified claims via web-fetched primary documents (GitHub README and Learn Migration Guide).
- **Synthesize:** FIN-* derived from OBS-* per the harness-evaluations template §5; gaps named against Addendum 01 layers.

## 1. Overview

Microsoft Agent Framework (MAF) is an open-source, multi-language (Python and C#/.NET) SDK for building **production-grade AI agents and multi-agent workflows**. It represents a significant architectural evolution of Microsoft AutoGen and Semantic Kernel, incorporating real-world lessons to deliver a more robust, durable, and restartable system. 

Unlike AutoGen, which paired an event-driven core with broadcast-based `Team` structures, MAF introduces a unified, data-flow based, typed `Workflow` model. It is designed for enterprise-grade applications, introducing durability (checkpointing), restartability (time-travel), middle-ware, declarative agents, and first-class hosting.

## 2. Architectural Alignment

Evaluated against the EDASES layered architecture from `research-addenda/Research Addendum 01.md`.

*   **Principal Layer:** Partial/Improved. While still lacking a dedicated Principal decision-support dashboard, MAF's interactive **DevUI** provides debugging, testing, and workflow visualization. Crucially, the **Request-Response API** offers a first-class human-in-the-loop gate, enabling Principal intervention, approval, and steering of workflows. `[addresses CRIT-04]`
*   **Organizational Layer:** Strong, durable. Replaces broadcast-based teams with a graph-based, typed **Workflow** model. Task breakdown and routing are done via structured edges and executors (which can be agents, pure functions, or nested workflows). Conversation history is managed explicitly using `AgentSession`. Supports first-class orchestration presets via `SequentialBuilder`, `ConcurrentBuilder`, and `MagenticBuilder`.
*   **Knowledge Layer:** Partial, per-agent. Provides an **Agent Skills** design for building domain-specific knowledge bases from multiple sources (files, inline code, libraries) for agents to discover and use. Still lacks an organizational-level, end-to-end evidence lineage store (Source→Observation→Finding→Decision), but provides a much stronger foundation for persisting session state.
*   **Capability Layer:** Strong. Multi-language (Python & .NET), multiple agent provider support (OpenAI, Azure, GitHub Copilot SDK), and pluggable model clients including reasoning models and structured responses (via the Responses API). Supports Model Context Protocol (MCP) natively via `MCPStdioTool`, `MCPStreamableHTTPTool`, and `MCPWebsocketTool`. `[addresses CRIT-03]`
*   **Verification Layer:** Partial/Substantial. Built-in **Checkpointing** (`FileCheckpointStorage`) automatically captures workflow iteration, executor state, and pending requests, enabling **time-travel debugging** and replay. Paired with **AF Labs** (experimental benchmarking, reinforcement learning, and research packages) and OpenTelemetry. No in-runtime formal verification or automated code-review, but the durability primitives are a massive step forward for verification and recovery.
*   **Execution Layer:** Strong. Code execution (both local and service-managed), hosted tools (code interpreter, web search), MCP server integration, and multi-language local/cloud deployment.

**Summary:** Microsoft Agent Framework is a massive step forward from AutoGen. It elevates **Organizational** from in-process to durable/restartable, introduces real **Principal** interaction gates (Request-Response, DevUI), provides a robust **Verification** foundation (Checkpointing, Time-travel, AF Labs), and retains a **Strong Execution** layer. It is a highly cohesive substrate for building enterprise-grade, evidence-driven organizational workflows. `[addresses CRIT-03]`

## 3. Key Capabilities & Features

*   **Durable Workflows with Checkpointing:** Built-in support via `FileCheckpointStorage` to pause, persist, and resume execution from any iteration point.
*   **Time-Travel Debugging:** Ability to reload prior checkpoints and replay execution, a major feature for verification and failure triage.
*   **Data-Flow Graph (Workflow):** Nodes are executors (functions, agents, sub-workflows) connected by typed edges, replacing control-flow broadcasts with strict targeted routing.
*   **First-Class Human-in-the-loop:** Pausing workflows using the Request-Response API to capture external human inputs/approvals.
*   **Flexible Middleware System:** Pluggable middleware for preprocessing requests, custom safety validation, caching, logging, and error/exception handling.
*   **Agent Skills:** Declarative skills from files, class libraries, or inline code that agents can discover and consume dynamically.
*   **Responses API & Reasoning Models:** Native support for OpenAI/Azure OpenAI structured responses and reasoning models (not available in AutoGen).
*   **DevUI & OpenTelemetry:** An interactive developer UI for visualizing, testing, and debugging workflows, paired with deep OpenTelemetry tracing.

## 4. Observations

### Memory and persistence model

*   **OBS-01:** MAF uses `AgentSession` to explicitly manage conversation state across multiple agent invocations, preventing the statelessness of individual `Agent.run()` calls. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-02:** Built-in workflow checkpointing is supported via `FileCheckpointStorage` and the `checkpoint_storage` parameter on `WorkflowBuilder`. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-03:** Checkpoints capture the workflow execution iteration count, the internal state of all executors, and any pending request-response items, allowing fully restartable long-running processes. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-04:** The checkpointing framework enables "time-travel", allowing developers to list, inspect, and resume workflows from any historical checkpoint. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`

### Organizational primitives

*   **OBS-05:** MAF replaces AutoGen's `Team` with a unified data-flow based `Workflow` model built using `WorkflowBuilder`, `@executor`, and explicit edges. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-06:** Executors in a workflow can be `Agent` instances, pure Python/C# functions, or nested sub-workflows (wrapped using `WorkflowExecutor`), supporting hierarchical organization. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-07:** Workflows support targeted routing (explicitly sending to specific executors using `target_id` inside `WorkflowContext.send_message`), replacing the broadcast-to-all pattern used in AutoGen's teams. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-08:** Preset orchestrations are available through orchestration builders, including `SequentialBuilder` (round-robin), `ConcurrentBuilder` (parallel), and `MagenticBuilder` (manager-led teams). (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-09:** Human-in-the-loop is handled as a first-class primitive via the Request-Response API, which allows workflows to pause, emit request events, and resume upon receiving response events. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-10:** MAF includes a middleware system that enables custom request/response processing, exception handling, and custom validation pipelines at the agent level. (Source: https://github.com/microsoft/agent-framework) `[verified-directly]`

### Verification pathway

*   **OBS-11:** MAF introduces "AF Labs", containing experimental packages for cutting-edge features including benchmarking, reinforcement learning, and research initiatives. (Source: https://github.com/microsoft/agent-framework) `[verified-directly]`
*   **OBS-12:** The interactive "DevUI" provides developers with visual tracing, testing, and debugging workflows in real time. (Source: https://github.com/microsoft/agent-framework) `[verified-directly]`
*   **OBS-13:** Model Context Protocol (MCP) is natively integrated with built-in classes: `MCPStdioTool`, `MCPStreamableHTTPTool`, and `MCPWebsocketTool` for standardized verification of external tools. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`

### Status and successor

*   **OBS-14:** Microsoft Agent Framework is the official, production-ready successor to Microsoft AutoGen. It is actively co-developed by the core AutoGen and Semantic Kernel teams at Microsoft. (Source: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) `[verified-directly]`
*   **OBS-15:** MAF is under highly active development, with version `python-1.9.0` released on June 18, 2026, while AutoGen's development has been restricted to community-managed bug and security fixes. (Source: https://github.com/microsoft/agent-framework) `[verified-directly]`

## 5. Findings

*   **FIN-01 — Durability transforms Organizational State from transient to persistent:** By introducing `FileCheckpointStorage` and structured checkpointing in the `Workflow` runtime, MAF solves the transient-state limitation of AutoGen's teams. Workflows can be completely persisted to disk (iteration count, executor states, requests), offering true fault tolerance and long-running process capability. (OBS-02, OBS-03)
*   **FIN-02 — Targeted routing and diverse node types yield clean, modular hierarchies:** Replaced broadcast-based message streams with a typed, data-flow based graph. Using pure functions, nested workflows, or specialized agents as executors with explicit targeted routing allows developers to build clean, modular, and non-bleeding organizational taxonomies. (OBS-05, OBS-06, OBS-07)
*   **FIN-03 — First-class Human-in-the-loop and DevUI provide a viable Principal interface:** AutoGen lacked a clean oversight boundary. MAF's combination of the Request-Response API (which elegantly pauses and resumes workflows for human validation) and the interactive DevUI establishes a true Principal-facing surface for oversight, intervention, and confidence-generation. (OBS-09, OBS-12)
*   **FIN-04 — Checkpointing enables powerful Verification and debugging pathways:** The "time-travel" capability of MAF's checkpointing is a load-bearing verification primitive. It allows replay-based validation, state audits, and failure reconstruction—crucial for verification layers that need to inspect exactly when and why an organizational state diverged from expectations. (OBS-04, OBS-12)
*   **FIN-05 — Strong strategic and release trajectory makes MAF the only viable Microsoft foundation:** MAF is actively developed, heavily co-authored by the AutoGen and Semantic Kernel teams, and rapidly iterating (release `1.9.0` in June 2026). AutoGen's maintenance mode status makes any continued exclusive investment in AutoGen an architectural dead-end. (OBS-14, OBS-15)

## 6. Gaps against EDASES Requirements

What is still missing to make MAF a complete evidence-driven organizational system:

*   **No native decision-capture or evidence-provenance architecture.** While sessions and checkpoints persist raw message logs and state, MAF has no concept of a structured, auditable evidence ledger (Source→Observation→Finding→Assumption→Decision→Outcome). Building EDASES-style traceability still requires a user-built layer. `[addresses CHK-02]`
*   **No organizational-level Knowledge Store.** MAF introduces "Agent Skills" (OBS-10) for per-agent knowledge, but does not provide an organizational-level memory sync or an enterprise-wide shared knowledge index. `[addresses CHK-02]`
*   **No autonomous capability registry or routing decisions.** While MAF has rich client and provider abstractions (including the Responses API), composition remains user-coded and hardwired in the workflow graph. It lacks a dynamic, registry-driven routing layer that matches tasks to agents based on real-time capability evaluations. `[addresses CHK-01]`
*   **Testing and Benchmarking remain in experimental "Labs".** Unlike a robust runtime Verification Layer that generates confidence metrics in-loop, benchmarking and evaluation are quarantined in "AF Labs" (OBS-11), keeping verification and execution decoupled. `[addresses CHK-01]`
