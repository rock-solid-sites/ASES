# Harness Capability Matrix

**Date:** 2026-06-23
**Source:** Fulfilling Addendum 01 §6 (Harness Capability Matrix) incrementally. First row: Microsoft AutoGen (see `harness-evaluations/Microsoft-AutoGen.md`).
**Convention:** Rows are EDASES layer requirements (per Addendum 01). Columns are evaluated harnesses/frameworks. Cells describe coverage. Add a new column for each evaluated harness.

## Matrix

| EDASES Layer Requirement | Microsoft AutoGen |
|---|---|
| **Principal** — oversight surface, evidence review, decision support, progress dashboard | **Not provided.** No Principal-facing UI in the framework. AutoGen Studio is a prototyping GUI, not an oversight surface. |
| **Organizational** — task coordination, role management, workflow management, information flow | **Substantial, in-process.** 2 preset agent types (`AssistantAgent`, `UserProxyAgent`) + custom `BaseChatAgent` subclasses. 5 first-class team patterns (`RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm`, `GraphFlow`). `AgentTool` for agent-as-tool composition. Typed `termination_condition` objects. State is in-process `TaskResult(messages=[...])`. **Gap:** no Crosslink-like persistent org store; org-level state is delegated to user via `Component` JSON serialization. |
| **Knowledge** — persistent project memory, historical learning, decision capture, knowledge reuse | **Partial, per-agent.** Pluggable `Memory` protocol with shipped backends (`ListMemory`, `ChromaDBVectorMemory` w/ persistent on-disk config, `RedisMemory`, `Mem0Memory`). `Component` JSON export. **Gap:** no org-level knowledge store; no Source→Observation→Finding→Assumption→Decision→Outcome provenance; no evidence-lineage primitives in the message vocabulary. |
| **Capability** — model evaluation, capability tracking, routing decisions, workforce composition | **Substantial, no registry.** Pluggable model clients (OpenAI, Azure, etc.) via `autogen-ext`. MCP-server integration (`McpWorkbench`). Cross-language Core (Python + .NET). **Gap:** no built-in capability registry or routing decision layer; composition is user-coded, not registry-driven. |
| **Verification** — testing, review, formal verification, confidence generation | **Not provided in framework.** `AutoGenBench` (`agbench`) is a separate sibling package that runs tasks in fresh Docker containers and tabulates completion metrics — a benchmarking harness, not an in-loop verification layer. No testing, review, or formal-verification primitives in the runtime. |
| **Execution** — code generation, tool execution, file modification | **Strong.** Code execution, MCP tool integration, file handling, Magentic-One generalist team. |

## Strategic Status

| Harness | Status | Latest release | Source |
|---|---|---|---|
| Microsoft AutoGen | Maintenance mode (community-managed, no new features) | `python-v0.7.5` — Sep 30, 2025 | https://github.com/microsoft/autogen |
| Microsoft Agent Framework (MAF) | Production-ready successor (under active development) | `python-1.9.0` — Jun 18, 2026 | https://github.com/microsoft/agent-framework |

**Strategic note:** For EDASES adoption decisions, AutoGen is a sunsetting foundation. Any AutoGen investment is either portable to MAF or accepted as a fixed target. MAF is the forward-looking candidate and should be evaluated separately before any architectural commitment (see Addendum 01 §6 deliverable: "Harness Capability Matrix").

## Adding a new harness column

1. Create `harness-evaluations/<Harness-Name>.md` following the harness-evaluations template.
2. Add a new column to the matrix above, mirroring the row labels.
3. For each cell, cite the harness evaluation file (`harness-evaluations/<X>.md`).
4. If a new layer requirement emerges, add a row and reference the originating addendum.
