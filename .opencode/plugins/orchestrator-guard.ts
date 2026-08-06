/**
 * Orchestrator Guard — OpenCode Plugin
 *
 * Closes the edit:deny gap (OpenCode issue #33677). Native write/edit/apply_patch
 * and MCP filesystem_write_file / filesystem_edit_file tools succeed regardless of
 * `edit: deny` in the permission config. This plugin blocks them at the
 * tool.execute.before hook level for all non-Builder agents.
 *
 * Tracks the current agent via chat.params since tool.execute.before does not
 * expose the agent field.
 *
 * @module orchestrator-guard
 */

import type { Plugin } from "@opencode-ai/plugin";
import * as fs from "fs";

const LOG_FILE = "/tmp/orchestrator-guard.log";

function log(...args: unknown[]): void {
  try {
    const line =
      new Date().toISOString() +
      " [orchestrator-guard] " +
      args.map((a) => String(a)).join(" ") +
      "\n";
    fs.appendFileSync(LOG_FILE, line, "utf-8");
  } catch {
    // best-effort, never throw
  }
}

const BLOCKED_TOOLS = new Set([
  "write",
  "edit",
  "apply_patch",
  "filesystem_write_file",
  "filesystem_edit_file",
]);

const ALLOWED_AGENTS = new Set(["builder"]);

const BLOCK_MESSAGE =
  "ORCHESTRATOR WRITE BLOCK — You attempted to use the '%s' tool, " +
  "which modifies project files. This is NOT your role.\n\n" +
  "The Orchestrator must delegate all file modifications to the Builder " +
  "subagent. Use the Task tool to delegate to the Builder instead.\n\n" +
  "This block is enforced at the plugin level because edit:deny in the " +
  "permission config does not block native writes (OpenCode issue #33677).";

let currentAgent: string | null = null;

// Per-session agent map. One opencode process hosts multiple sessions (the
// interactive session plus Task-tool subagents), and every session's
// chat.params fires in that same process. A single shared variable would be
// clobbered by the most recent subagent event, so the parent session's tool
// calls would resolve to the subagent's type (same defect fixed in
// crosslink-guard for the #204 git-merge regression). Keying by sessionID
// keeps each session's agent independent.
const agentBySession = new Map<string, string>();

const orchestratorGuardPlugin: Plugin = async () => {
  log("Plugin initialised");

  return {
    "chat.params": async (input, _output) => {
      currentAgent = input.agent;
      if (input.sessionID && input.agent) {
        agentBySession.set(input.sessionID, input.agent);
      }
      log("chat.params agent:", currentAgent, "session:", input.sessionID);
    },

    "chat.message": async (input, _output) => {
      if (input.sessionID && input.agent) {
        agentBySession.set(input.sessionID, input.agent);
      }
      log("chat.message agent:", input.agent ?? "(none)", "session:", input.sessionID);
    },

    "tool.execute.before": async (input, _output) => {
      const toolName = (input.tool as string || "").toLowerCase();

      if (!BLOCKED_TOOLS.has(toolName)) {
        return;
      }

      // Resolve the agent for THIS session first. Fall back to the most
      // recent chat.params event ONLY when no sessionID is available (the
      // plugin API always provides sessionID, so this is a defensive path);
      // never fall back across sessions, which would let a builder subagent's
      // event authorize a write from the orchestrator session.
      const sessionAgent = input.sessionID
        ? agentBySession.get(input.sessionID) ?? null
        : currentAgent;

      if (ALLOWED_AGENTS.has(sessionAgent ?? "")) {
        log("ALLOW write tool:", toolName, "agent:", sessionAgent, "session:", input.sessionID);
        return;
      }

      log("BLOCK write tool:", toolName, "agent:", sessionAgent, "session:", input.sessionID);
      throw new Error(BLOCK_MESSAGE.replace("%s", toolName));
    },
  };
};

export default orchestratorGuardPlugin;
