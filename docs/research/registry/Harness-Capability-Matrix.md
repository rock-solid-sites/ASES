---
title: Harness Capability Matrix
program: EDASES
layer: Research
document_type: Research Record
status: Historical
authority: Derived
canonical_repository: edases

depends_on:
  - Research Addendum 01

consumed_by:
  - AI Capability Registry

related_documents:
  - Harness Evaluation: Microsoft AutoGen
  - Harness Evaluation: Microsoft Agent Framework

supersedes: []
last_updated: 2026-08-10
---

# Harness Capability Matrix

> **Historical local snapshot (June–August 2026; scope reviewed 2026-11-24).** The product versions, strategic status, framework feature claims and layer mapping below are dated research, not a current comparison or adoption decision. The original [source snapshot](https://github.com/rock-solid-sites/ASES/blob/19b38545d88bac8bc072ef9547d1dbd97e050f3b/docs/research/registry/Harness-Capability-Matrix.md) retains its original metadata. This local classification does not change EDASES upstream ownership. Apply the [current orchestration methodology](../../methodology/AI%20Orchestration%20Guide.md) and [current agent-launch skill](../../../skills/current/agent-launch/SKILL.md) for present task decisions; verify actual harness version, host, route and required effects separately. The matrix remains useful as evidence of previous evaluation dimensions; no claim of present runtime capability follows from it.

**Date:** 2026-06-23
**Source:** Fulfilling Addendum 01 §6 (Harness Capability Matrix) incrementally. First row: Microsoft AutoGen (see `docs/research/harness-evaluations/Microsoft-AutoGen.md`).
**Convention:** Rows are EDASES layer requirements (per Addendum 01). Columns are evaluated harnesses/frameworks. Cells describe coverage. Add a new column for each evaluated harness.

## Matrix

| EDASES Layer Requirement | Microsoft AutoGen | Microsoft Agent Framework (MAF) |
|---|---|---|
| **Principal** — oversight surface, evidence review, decision support, progress dashboard | **Not provided.** No Principal-facing UI in the framework. AutoGen Studio is a prototyping GUI, not an oversight surface. | **Partial/Improved.** Interactive **DevUI** provides visual tracing, debugging, and visualization. **Request-Response API** provides first-class human-in-the-loop workflow steering and gates (see `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`). |
| **Organizational** — task coordination, role management, workflow management, information flow | **Substantial, in-process.** 2 preset agent types (`AssistantAgent`, `UserProxyAgent`) + custom `BaseChatAgent` subclasses. 5 first-class team patterns (`RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm`, `GraphFlow`). `AgentTool` for agent-as-tool composition. Typed `termination_condition` objects. State is in-process `TaskResult(messages=[...])`. **Gap:** no Crosslink-like persistent org store; org-level state is delegated to user via `Component` JSON serialization. | **Strong, durable.** Graph-based, typed **Workflow** model using executors (agents, functions, nested sub-workflows) and edges. **AgentSession** manages conversation state. Presets via `SequentialBuilder`, `ConcurrentBuilder`, and `MagenticBuilder`. **Gap:** Still delegates externalization of org state to user (see `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`). |
| **Knowledge** — persistent project memory, historical learning, decision capture, knowledge reuse | **Partial, per-agent.** Pluggable `Memory` protocol with shipped backends (`ListMemory`, `ChromaDBVectorMemory` w/ persistent on-disk config, `RedisMemory`, `Mem0Memory`). `Component` JSON export. **Gap:** no org-level knowledge store; no Source→Observation→Finding→Assumption→Decision→Outcome provenance; no evidence-lineage primitives in the message vocabulary. | **Partial, per-agent.** Dynamic **Agent Skills** design for agent discovery/use of knowledge from files or inline code. **Gap:** No global, org-orchestrated knowledge store or Source→Observation→Finding→Decision provenance (see `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`). |
| **Capability** — model evaluation, capability tracking, routing decisions, workforce composition | **Substantial, no registry.** Pluggable model clients (OpenAI, Azure, etc.) via `autogen-ext`. MCP-server integration (`McpWorkbench`). Cross-language Core (Python + .NET). **Gap:** no built-in capability registry or routing decision layer; composition is user-coded, not registry-driven. | **Strong, no registry.** Multi-language support (Python and C#/.NET), multiple provider support (OpenAI, Azure, Foundry), and pluggable model clients supporting structured Responses API and reasoning models. Native MCP support (`MCPStdioTool`, etc.). **Gap:** No dynamic routing registry (see `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`). |
| **Verification** — testing, review, formal verification, confidence generation | **Not provided in framework.** `AutoGenBench` (`agbench`) is a separate sibling package that runs tasks in fresh Docker containers and tabulates completion metrics — a benchmarking harness, not an in-loop verification layer. No testing, review, or formal-verification primitives in the runtime. | **Partial/Substantial.** Built-in **Checkpointing** (`FileCheckpointStorage`) automatically serializes iteration, executor state, and requests, enabling durable recovery and **time-travel debugging**. Companion evaluation packages in **AF Labs** (see `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`). |
| **Execution** — code generation, tool execution, file modification | **Strong.** Code execution, MCP tool integration, file handling, Magentic-One generalist team. | **Strong.** Dynamic and local tool execution, hosted tools (code interpreter, web search), native MCP integration, and Azure/Foundry hosting (see `docs/research/harness-evaluations/Microsoft-Agent-Framework.md`). |

## Strategic Status

| Harness | Status | Latest release | Source |
|---|---|---|---|
| Microsoft AutoGen | Maintenance mode (community-managed, no new features) | `python-v0.7.5` — Sep 30, 2025 | https://github.com/microsoft/autogen |
| Microsoft Agent Framework (MAF) | Production-ready successor (under active development) | `python-1.9.0` — Jun 18, 2026 | https://github.com/microsoft/agent-framework |

**Strategic note:** For EDASES adoption decisions, AutoGen is a sunsetting foundation. Any AutoGen investment is either portable to MAF or accepted as a fixed target. MAF is the forward-looking candidate and should be evaluated separately before any architectural commitment (see Addendum 01 §6 deliverable: "Harness Capability Matrix").

## Adding a new harness column

1. Create `docs/research/harness-evaluations/<Harness-Name>.md` following the harness-evaluations template.
2. Add a new column to the matrix above, mirroring the row labels.
3. For each cell, cite the harness evaluation file (`docs/research/harness-evaluations/<X>.md`).
4. If a new layer requirement emerges, add a row and reference the originating addendum.
