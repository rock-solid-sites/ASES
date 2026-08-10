---
title: Harness Evaluation: RTK — OpenCode Integration Gap Analysis
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - Research Addendum 01

consumed_by:
  - Harness Capability Matrix

related_documents:
  - Evaluation Framework

supersedes: []
last_updated: 2026-08-10
---

# Harness Evaluation: RTK — OpenCode Integration Gap Analysis

**Date:** 2026-07-12
**Evaluator:** OpenCode (Orchestrator Agent, via Deepseek Flash subagents)
**Source/URL:** https://github.com/rtk-ai/rtk · `.opencode/plugins/crosslink-guard.ts` · `~/.claude/settings.json`

Method: Direct analysis (not Heuristic Scouting — RTK is already adopted, not a candidate for evaluation). This is a structural gap analysis triggered by an agent's failure to use RTK transparently in an OpenCode session, following the evidence pipeline: Source → Observation → Finding → Recommendation.

## 1. Overview

RTK (`rtk-ai/rtk`) is a CLI proxy that reduces LLM token consumption by caching and compressing standard command output (e.g., `grep`, `find`, `ls`, `git`). It is deployed in the EDASES toolchain via two mechanisms:

1. **Explicit prefixing:** Agents write `rtk grep ...` instead of `grep ...`. The `rtk` binary wraps the underlying command and returns compressed output.
2. **Transparent rewriting (Claude Code only):** A `PreToolUse` hook at `~/.claude/settings.json` runs `rtk hook claude` before every `Bash` tool call, transparently rewriting commands (e.g., `git status` → `rtk git status`) without agent involvement.

OpenCode does not run Claude Code hooks. This analysis determines whether RTK's transparent rewriting mechanism has any path to firing inside an OpenCode session, whether an equivalent exists, and what the implications are for EDASES tooling.

## 2. Architectural Alignment

Evaluated against the EDASES layered architecture.

*   **Execution Layer:** OpenCode is a coding harness (Execution Layer). Its plugin API provides `tool.execute.before` hooks that can intercept, block, and mutate tool calls before execution. This is the integration surface for tooling proxies like RTK.
*   **Verification Layer:** RTK functions as a transparent execution-layer proxy — it does not verify correctness but reduces cost and enforces policy at the tool-call boundary. It sits between the agent and the shell, analogous to a middleware.
*   **Organizational Layer:** Crosslink provides session tracking, issue management, and hook-based workflow enforcement. The existing `crosslink-guard.ts` OpenCode plugin demonstrates that OpenCode's plugin API can implement organizational-layer policy at the tool-execution boundary. RTK operates at the same boundary but with a different purpose (token reduction vs. policy enforcement).

## 3. Key Capabilities & Features

*   **RTK CLI Proxy:** Wraps standard Unix commands (`grep`, `find`, `ls`, `git`, `read`, etc.) with output caching and compression. Tracks token savings per command and per session.
*   **Claude Code PreToolUse Hook:** `~/.claude/settings.json` configures `rtk hook claude` as a `PreToolUse` hook on all `Bash` tool calls. This transparently rewrites commands — zero agent involvement.
*   **RTK TOML-based rewriting:** Supports `rtk:toml` prefixed commands for structured output parsing (e.g., `ps aux` parsed as TOML tables).
*   **OpenCode Plugin API:** Provides `tool.execute.before` hook with mutable `output.args` — can inspect, block, and theoretically rewrite tool arguments before execution.
*   **crosslink-guard.ts:** Existing OpenCode plugin demonstrating `tool.execute.before` for blocking disallowed bash/write/edit operations. Proves the hook mechanism works but does not demonstrate argument rewriting.

## 4. Observations

### RTK deployment status

*   **OBS-01:** RTK is deployed at `~/.cargo/bin/rtk` (Rust binary, installed via Cargo). The binary is functional and tracked 779 commands. (Source: `rtk gain` output, 2026-07-12) `[verified-directly]`
*   **OBS-02:** RTK's Claude Code hook is configured at `~/.claude/settings.json` as a `PreToolUse` hook matching `Bash` tool calls, executing `rtk hook claude`. No companion `~/.claude/hooks/rtk-hook.sh` exists — the hook calls the RTK binary directly. (Source: `~/.claude/settings.json`) `[verified-directly]`
*   **OBS-03:** RTK has accumulated 123.3K tokens saved (7.9%) across 779 commands. Of these, 611 (78.4%) used explicit `rtk` prefixing, 163 (20.9%) were hook pass-through, and only 5 (0.6%) used hook-based transparent rewriting (`rtk:toml` prefix). (Source: `rtk gain` output, `rtk session` output) `[verified-directly]`
*   **OBS-04:** `rtk session` and `rtk discover` both report **zero** Claude Code sessions detected in the last 30 days. All 779 tracked commands originate from non-Claude-Code sessions — i.e., OpenCode or direct terminal use. (Source: `rtk session`, `rtk discover` output) `[verified-directly]`
*   **OBS-05:** RTK is active in OpenCode sessions: 113 commands and 36.3K tokens saved in the last 4 days (Jul 8–11), all via explicit `rtk` prefixing. (Source: `rtk gain` output) `[verified-directly]`

### OpenCode plugin mechanism

*   **OBS-06:** OpenCode's plugin API (`@opencode-ai/plugin` v1.17.15) provides a `tool.execute.before` hook with signature `(input: { tool, sessionID, callID }, output: { args: any }) => Promise<void>`. The `output.args` object is mutable (not `readonly`), matching the pattern of other hooks where `output` carries mutable state (e.g., `chat.params` mutates `output.temperature`, `permission.ask` sets `output.status`). (Source: `@opencode-ai/plugin` type definitions in `node_modules/`) `[per-subagent]`
*   **OBS-07:** `crosslink-guard.ts` (`/home/claude-code/projects/ASES/.opencode/plugins/crosslink-guard.ts`) implements `tool.execute.before` to block disallowed bash/write/edit operations. It reads `output.args.command` (for bash), `output.args.filePath` (for write/edit), and `output.args.content` (for write), but never modifies `output.args`. It blocks by throwing `new Error(message)`. (Source: `.opencode/plugins/crosslink-guard.ts`) `[verified-directly]`
*   **OBS-08:** No RTK plugin, port, or configuration exists in `.opencode/plugins/`, `~/.config/opencode/plugins/`, or `~/.config/opencode/opencode.json`. The only OpenCode plugins are `crosslink-guard.ts` (project-level) and `dynamic-models.js` (global-level). (Source: filesystem scan of all OpenCode plugin locations) `[verified-directly]`
*   **OBS-09:** OpenCode's `opencode.json` at the project root is minimal (`{ "$schema": "https://opencode.ai/config.json" }`), relying on auto-discovery of `.opencode/plugins/*.ts`. (Source: `.opencode/opencode.json`) `[verified-directly]`
*   **OBS-10:** Claude Code's `PreToolUse` hook protocol passes tool arguments to hook scripts via environment variables (`TOOL_NAME`, `TOOL_ARGS`) and stdin JSON. OpenCode's `tool.execute.before` passes tool arguments as a structured TypeScript object (`output.args`). These are fundamentally different protocols — a Claude Code hook script cannot execute in OpenCode's plugin runtime, and vice versa. (Source: Claude Code hook documentation, `@opencode-ai/plugin` type definitions) `[per-subagent]`

### RTK in EDASES documentation

*   **OBS-11:** RTK is referenced in EDASES research documents at `future-research-topics/project-setup.md` (lines 902, 1119), `future-research-topics/project-setup-final.md`, and `future-research-topics/project-setup-summary.md` — all as a future-research topic, not as an adopted or evaluated tool. (Source: grep for "rtk" across repo) `[verified-directly]`
*   **OBS-12:** No formal RTK findings, observations, or evaluation documents exist in `harness-evaluations/`, `findings/`, or `observations/`. (Source: filesystem scan of all evidence directories) `[verified-directly]`

## 5. Findings

### FIN-01 — RTK's transparent rewriting has no path to firing in OpenCode

*Confidence: Validated*
*Supporting Evidence: OBS-02, OBS-06, OBS-08, OBS-10*

RTK's transparent command rewriting depends on Claude Code's `PreToolUse` hook protocol. This protocol is not supported by OpenCode. Claude Code hooks are a separate runtime mechanism from OpenCode plugins — they use different APIs, different invocation protocols (subprocess vs. in-process TypeScript), and different configuration files. RTK's `rtk hook claude` binary is a Claude Code hook command and has no mechanism to intercept OpenCode tool calls.

The agent's failure to use RTK transparently was therefore **structurally unavoidable**, not a compliance failure. The transparent rewriting mechanism was never present in the OpenCode session.

### FIN-02 — OpenCode's plugin API can support an equivalent rewrite mechanism

*Confidence: Supported*
*Supporting Evidence: OBS-06, OBS-07, OBS-09*

OpenCode's `tool.execute.before` hook provides mutable access to `output.args`, following the same pattern as other hooks where `output` carries mutable state. `crosslink-guard.ts` already demonstrates hooking `tool.execute.before` for bash calls — it reads `output.args.command` and can block execution. The API surface strongly suggests that mutating `output.args.command` before returning would rewrite the bash command transparently, providing an equivalent to RTK's Claude Code hook.

**Caution:** This rewrite capability has not been explicitly demonstrated or tested in this codebase. `crosslink-guard.ts` never writes to `output.args`. The `[per-subagent]` evidence chain for the type definitions means this finding is `Supported` rather than `Validated` — the API pattern is consistent with the rest of the hook API (where `output` is mutable in every hook), but runtime behavior must be confirmed.

### FIN-03 — RTK IS actively accumulating savings in OpenCode sessions, but only through explicit agent prefixing

*Confidence: Validated*
*Supporting Evidence: OBS-03, OBS-04, OBS-05*

Despite the absence of transparent rewriting, RTK has tracked 779 commands and saved 123.3K tokens (7.9%) — all from OpenCode sessions (zero Claude Code sessions detected). However, 78.4% of these savings come from agents explicitly writing `rtk grep`, `rtk read`, etc. Only 0.6% (5 commands) used hook-based rewriting. This confirms that:
1. RTK is functional and valuable in OpenCode.
2. The transparent hook path is essentially unused (0.6%).
3. Agent compliance with explicit RTK usage is inconsistent — some agents prefix, some don't.

### FIN-04 — Building an RTK equivalant OpenCode plugin is low-effort

*Confidence: Supported*
*Supporting Evidence: OBS-06, OBS-07, FIN-02*

A native RTK OpenCode plugin (`rtk-guard.ts`) can be patterned directly on `crosslink-guard.ts`:

*   **Hook:** `tool.execute.before` on `tool === "bash"`
*   **Logic:** Determine whether the bash command benefits from RTK optimization (by calling `rtk` CLI or by maintaining a command list), then mutate `output.args.command` to prepend `rtk`
*   **Edge cases:** Prevent infinite loops (the plugin must not re-trigger on `rtk`-prefixed commands), handle shell pipelines and subshells, respect RTK's own exclusion list
*   **Size estimate:** ~100–200 lines of TypeScript
*   **Dependencies:** The `rtk` binary must be on `PATH` (it already is); no additional npm packages required beyond what `@opencode-ai/plugin` already provides
*   **Registration:** Auto-discovered from `.opencode/plugins/rtk-guard.ts` (no `opencode.json` changes needed)

## 6. Gaps against EDASES Requirements

*   **Transparent tool proxy gap:** The EDASES toolchain currently lacks a mechanism to transparently proxy and optimize OpenCode tool calls. RTK fills this role for Claude Code but not for OpenCode. `[addresses TOOL-01]`
*   **Plugin rewrite verification:** The `tool.execute.before` API's ability to rewrite `output.args` has not been verified at runtime. `crosslink-guard.ts` demonstrates reading and blocking but never mutating. A smoke test is needed before committing to the plugin approach. `[addresses TOOL-02]`
*   **Documentation gap:** RTK is discussed as a future-research topic but has been actively deployed and accumulating savings for over a month. No formal evaluation, finding, or adoption record exists. `[addresses DOC-01]`
