/**
 * Orchestrator Guard — OpenCode Plugin
 *
 * Closes the edit:deny gap (OpenCode issue #33677). Native write/edit/apply_patch
 * and MCP filesystem_write_file / filesystem_edit_file /
 * filesystem_create_directory / filesystem_move_file tools succeed regardless of
 * `edit: deny` in the permission config. This plugin blocks them at the
 * tool.execute.before hook level for all non-Builder agents.
 *
 * Tracks the current agent via chat.params since tool.execute.before does not
 * expose the agent field.
 *
 * @module orchestrator-guard
 */

import type { Plugin, PluginInput } from "@opencode-ai/plugin";
// @ts-expect-error - bun:sqlite is provided by the Bun runtime
import { Database } from "bun:sqlite";
import * as fs from "fs";
import * as path from "path";

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
  "filesystem_create_directory",
  "filesystem_move_file",
]);

const ALLOWED_AGENTS = new Set(["builder"]);

const BLOCK_MESSAGE =
  "ORCHESTRATOR WRITE BLOCK — You attempted to use the '%s' tool, " +
  "which modifies project files. This is NOT your role.\n\n" +
  "The Orchestrator must delegate all file modifications to the Builder " +
  "subagent. Use the Task tool to delegate to the Builder instead.\n\n" +
  "This block is enforced at the plugin level because edit:deny in the " +
  "permission config does not block native writes (OpenCode issue #33677).";

// ---------------------------------------------------------------------------
// Model-gated Task launch (operator approval, same tier as git merge)
// ---------------------------------------------------------------------------

function findCrosslinkDir(startDir: string): string | null {
  let current = startDir;
  for (let i = 0; i < 10; i++) {
    const candidate = path.join(current, ".crosslink");
    if (
      fs.existsSync(candidate) &&
      fs.statSync(candidate).isDirectory() &&
      fs.existsSync(path.join(candidate, "hook-config.json"))
    ) {
      return candidate;
    }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return null;
}

function getActiveIssueIdFromSentinel(crosslinkDir: string): number | null {
  const sentinelPath = path.join(crosslinkDir, ".active-issue");
  if (!fs.existsSync(sentinelPath)) return null;
  try {
    const c = fs.readFileSync(sentinelPath, "utf-8").trim();
    if (!c) return null;
    const n = parseInt(c.replace(/^#/, ""), 10);
    return isNaN(n) ? null : n;
  } catch {
    return null;
  }
}

function hasApprovalForModel(
  crosslinkDir: string,
  issueId: number,
  modelId: string,
): boolean {
  const dbPath = path.join(crosslinkDir, "issues.db");
  if (!fs.existsSync(dbPath)) return true;
  try {
    const db = new Database(dbPath, { readonly: true });
    try {
      const stmt = db.prepare(
        "SELECT content FROM comments WHERE issue_id = ? AND kind = ?",
      );
      const rows = stmt.all(issueId, "approval") as { content: string }[];
      for (const row of rows) {
        if (row.content && row.content.includes(modelId)) return true;
      }
      return false;
    } finally {
      db.close();
    }
  } catch {
    return true;
  }
}

function extractModelFromTaskArgs(args: unknown): string | null {
  if (!args || typeof args !== "object") return null;
  const a = args as Record<string, unknown>;
  // Direct model fields
  for (const key of ["model", "modelId", "model_id", "modelID"]) {
    const v = a[key];
    if (typeof v === "string" && v.trim().length > 0) {
      return v.trim().replace(/^["']|["']$/g, "");
    }
  }
  // Nested agent/model structures
  for (const key of ["agent", "agentType", "agent_type", "subagent_type", "subagentType"]) {
    const v = a[key];
    if (typeof v === "string" && v.includes("/")) {
      // heuristic: if it looks like a model id (contains /)
      // and not just "builder"/"reviewer", treat as model if it contains prefix
      if (v.includes("opencode") || v.includes("google") || v.includes("cohere")) {
        return v.trim();
      }
    }
  }
  // Fallback: stringify and regex for --model or provider/model pattern
  try {
    const blob = JSON.stringify(a);
    const m = blob.match(/--model(?:\s*=\s*|\s+)(?:"([^"]+)"|'([^']+)'|([^"'\s,}\\]+))/);
    if (m) {
      const raw = (m[1] ?? m[2] ?? m[3] ?? "").trim().replace(/^["']|["']$/g, "");
      if (raw) return raw;
    }
    const p = blob.match(/(opencode-go\/[a-z0-9._-]+|opencode\/[a-z0-9._-]+|google-vertex\/[a-z0-9._-]+|cohere\/[a-z0-9._-]+)/i);
    if (p) return p[1];
  } catch {
    // ignore
  }
  return null;
}

function buildTaskModelGateNoIssueMessage(modelId: string | null): string {
  const modelPart = modelId ? ` (model: ${modelId})` : " (no model found in Task args)";
  return (
    `AGENT LAUNCH BLOCK — Did your operator approve a model selection?${modelPart}\n\n` +
    "Model-gated launches via Task (orchestrator → builder/reviewer/auditor) " +
    "require an active crosslink issue AND per-launch operator approval — same tier as git merge.\n\n" +
    "You have no active issue. Required steps BEFORE retry:\n" +
    "  1. question — Ask the operator via the question tool: Which model for this dispatch? (cheaper-first: prefer cheaper models that satisfy the task; frontier requires explicit approval every launch)\n" +
    "  2. opencode models — Verify the exact ID: opencode models <provider>  (e.g. opencode models opencode-go) — copy the ID exactly, never guess\n" +
    "  3. approval comment — Operator posts on the active issue: crosslink issue comment <id> \"Approved model: <exact model ID> verified via opencode models <provider>\" --kind approval\n" +
    "  4. retry — Re-run the same Task; the gate checks the active issue has an --kind approval comment containing the exact model ID\n\n" +
    "Cheaper-first: never select a frontier/expensive model over a cheaper option without operator approval.\n\n" +
    "Create/claim an issue first:\n" +
    '  crosslink quick "<describe the work>" -p <priority> -l <label>\n' +
    "  crosslink session work <id>\n"
  );
}

function buildTaskModelGateNoApprovalMessage(issueId: number, modelId: string | null): string {
  const modelPart = modelId ? `model: ${modelId}` : "no model found in Task args (all launches must specify a model)";
  const approvalExample = modelId
    ? `crosslink issue comment ${issueId} "Approved model: ${modelId} verified via opencode models <provider>" --kind approval`
    : `crosslink issue comment ${issueId} "Approved model: <exact model ID> verified via opencode models <provider>" --kind approval`;
  return (
    `AGENT LAUNCH BLOCK — Did your operator approve a model selection? (${modelPart})\n\n` +
    "Model-gated launches via Task (orchestrator → builder/reviewer/auditor) " +
    `require per-launch operator approval on issue #${issueId} — same tier as git merge.\n\n` +
    `You attempted a Task launch with ${modelPart} but issue #${issueId} has no --kind approval comment containing the exact model ID.\n\n` +
    "Required steps BEFORE retry:\n" +
    "  1. question — Ask the operator via the question tool: Which model for this dispatch? (cheaper-first: prefer cheaper models that satisfy the task; frontier requires explicit approval every launch)\n" +
    "  2. opencode models — Verify the exact ID: opencode models <provider>  (e.g. opencode models opencode-go) — copy the ID exactly, never guess\n" +
    `  3. approval comment — Operator posts: ${approvalExample}\n` +
    "  4. retry — Re-run the same Task; the gate checks the active issue has an --kind approval comment containing the exact model ID\n\n" +
    "Cheaper-first: never select a frontier/expensive model over a cheaper option without operator approval. Each launch needs its own approval.\n"
  );
}

let currentAgent: string | null = null;

// Per-session agent map. One opencode process hosts multiple sessions (the
// interactive session plus Task-tool subagents), and every session's
// chat.params fires in that same process. A single shared variable would be
// clobbered by the most recent subagent event, so the parent session's tool
// calls would resolve to the subagent's type (same defect fixed in
// crosslink-guard for the #204 git-merge regression). Keying by sessionID
// keeps each session's agent independent.
const agentBySession = new Map<string, string>();

const orchestratorGuardPlugin: Plugin = async (pluginInput: PluginInput) => {
  const projectDir = (pluginInput as { directory?: string })?.directory ?? process.cwd();
  log("Plugin initialised, projectDir:", projectDir);

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

    "tool.execute.before": async (input, output) => {
      const toolName = (input.tool as string || "").toLowerCase();

      // ------------------------------------------------------------------
      // Model-gated Task launches (operator approval, same tier as git merge)
      // ------------------------------------------------------------------
      if (toolName === "task") {
        const crosslinkDir = findCrosslinkDir(projectDir);
        if (!crosslinkDir) {
          log("ALLOW task: no crosslink dir");
          return;
        }
        const modelId = extractModelFromTaskArgs(output.args);
        // If Task has no model (e.g. non-agent task), don't gate
        // Heuristic: only gate Tasks that look like agent launches (contain builder/reviewer/auditor or opencode model)
        const blob = (() => {
          try {
            return JSON.stringify(output.args ?? {});
          } catch {
            return "";
          }
        })();
        const looksLikeAgentLaunch =
          blob.includes("builder") ||
          blob.includes("reviewer") ||
          blob.includes("auditor") ||
          (modelId !== null && (modelId.includes("/") || modelId.includes("opencode") || modelId.includes("google") || modelId.includes("cohere")));
        if (!looksLikeAgentLaunch && modelId === null) {
          log("ALLOW task: not an agent launch, no model");
          return;
        }

        let activeIssueId = getActiveIssueIdFromSentinel(crosslinkDir);
        if (activeIssueId === null) {
          // Try sessions table fallback
          const dbPath = path.join(crosslinkDir, "issues.db");
          if (fs.existsSync(dbPath)) {
            try {
              const db = new Database(dbPath, { readonly: true });
              try {
                const row = db
                  .prepare("SELECT active_issue_id as id FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1")
                  .get() as { id: number | null } | undefined;
                if (row && typeof row.id === "number") activeIssueId = row.id;
              } finally {
                db.close();
              }
            } catch {
              // ignore
            }
          }
        }

        if (activeIssueId === null) {
          log("BLOCK task: no active issue, model:", modelId);
          throw new Error(buildTaskModelGateNoIssueMessage(modelId));
        }
        if (!modelId) {
          log("BLOCK task: missing model, issue:", activeIssueId);
          throw new Error(buildTaskModelGateNoApprovalMessage(activeIssueId, null));
        }
        if (!hasApprovalForModel(crosslinkDir, activeIssueId, modelId)) {
          log("BLOCK task: no approval for model:", modelId, "issue:", activeIssueId);
          throw new Error(buildTaskModelGateNoApprovalMessage(activeIssueId, modelId));
        }
        log("ALLOW task: approval ok for model:", modelId, "issue:", activeIssueId);
        return;
      }

      if (!BLOCKED_TOOLS.has(toolName)) {
        return;
      }

      // Narrow exemption (#434 liveness accounting): read-only roles
      // (auditor/reviewer) must be able to write their own .kickoff-status
      // DONE marker; without this exception kickoff cleanup classifies live
      // and finished read-only roles as stale forever. Applies ONLY to
      // filesystem_write_file targeting a path whose basename is exactly
      // ".kickoff-status" — every other tool and path stays blocked below.
      if (toolName === "filesystem_write_file") {
        const targetPath = (output.args as { path?: string } | undefined)?.path;
        if (targetPath && path.basename(targetPath) === ".kickoff-status") {
          log(
            "ALLOW .kickoff-status marker write (#434 liveness):",
            targetPath,
            "session:",
            input.sessionID,
          );
          return;
        }
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
