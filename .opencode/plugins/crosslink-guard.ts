/**
 * Crosslink Guard — OpenCode Native TypeScript Plugin
 *
 * Replicates the full logic of crosslink's `work-check.py` PreToolUse hook
 * as a native TypeScript OpenCode plugin. Runs inside the Bun runtime that
 * OpenCode provides, using `bun:sqlite`, `node:fs`, `node:path`, and the
 * BunShell (`$`) API.
 *
 * Behaviour (in priority order):
 *   1. Operator kill/pause flags (highest priority — `crosslink agent flags --strict`)
 *   2. ~/.claude/ exemption for write/edit (Claude Code's own config)
 *   3. Permanently blocked git commands (push, rebase, reset, clean, …)
 *   4. Gated git commands (git commit — requires active issue + optional plan comment)
 *   5. Issue close comment discipline (requires --kind result comment)
 *   6. Allowed bash commands (safe read-only list)
 *   7. Active-issue enforcement for write/edit/non-allowed bash
 *
 * Stage 4 context: this is the native TS successor to the Python hook that
 * crosslink`init` deploys to .claude/hooks/work-check.py.
 *
 * @module crosslink-guard
 */

import type { Plugin, PluginInput } from "@opencode-ai/plugin";
// @ts-expect-error - bun:sqlite is provided by the Bun runtime
import { Database } from "bun:sqlite";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

// ---------------------------------------------------------------------------
// Logging
// ---------------------------------------------------------------------------

const LOG_FILE = "/tmp/crosslink-guard.log";

function log(...args: unknown[]): void {
  try {
    const line =
      new Date().toISOString() +
      " [crosslink-guard] " +
      args.map((a) => String(a)).join(" ") +
      "\n";
    fs.appendFileSync(LOG_FILE, line, "utf-8");
  } catch {
    // Best-effort logging — never throw from a hook
  }
}

// ---------------------------------------------------------------------------
// Constants (mirror work-check.py defaults exactly)
// ---------------------------------------------------------------------------

const DEFAULT_BLOCKED_GIT: string[] = [
  "git push",
  "git rebase",
  "git reset",
  "git clean",
];

const DEFAULT_AGENT_BLOCKED_GIT: string[] = [
  "git push --force",
  "git push -f",
  "git reset --hard",
  "git clean -f",
  "git clean -fd",
  "git clean -fdx",
  "git checkout .",
  "git restore .",
];

const DEFAULT_GATED_GIT: string[] = ["git commit"];

const DEFAULT_ALLOWED_BASH: string[] = [
  "crosslink ",
  "git status",
  "git diff",
  "git log",
  "git branch",
  "git show",
  "jj log",
  "jj diff",
  "jj status",
  "jj show",
  "jj bookmark list",
  "cargo test",
  "cargo build",
  "cargo check",
  "cargo clippy",
  "cargo fmt",
  "npm test",
  "npm run",
  "npx ",
  "tsc",
  "node ",
  "python ",
  "ls",
  "dir",
  "pwd",
  "echo",
  "gh ",
  "cat ",
  "head ",
  "tail ",
  "wc ",
  "grep ",
  "rg ",
  "find ",
  "sort ",
  "uniq ",
  "which ",
  "command ",
  "mktemp",
  "sleep ",
  "date",
  "env",
  "uname",
  "id ",
  "basename ",
  "dirname ",
  "realpath ",
  "stat ",
  "file ",
];

// ---------------------------------------------------------------------------
// Normalise git commands — strip global flags so bypasses are caught
// ---------------------------------------------------------------------------

/**
 * Strip git global flags (-C, --git-dir, --work-tree, -c) from a command
 * string so 'git -C /x push' normalises to 'git push'.
 */
function normalizeGitCommand(command: string): string {
  // Repeatedly strip leading "rtk " prefixes so "rtk rtk git push" collapses
  // to "git push" and is caught by the blocklist (Issue 5).
  while (command.startsWith("rtk ")) command = command.slice(4);
  // Use a simple shell-aware split (not full shlex, but good enough for git)
  const parts = shellSplit(command);
  if (parts.length === 0 || parts[0] !== "git") return command;

  let i = 1;
  const flagsWithArg = new Set(["-C", "--git-dir", "--work-tree", "-c"]);
  while (i < parts.length) {
    if (flagsWithArg.has(parts[i]) && i + 1 < parts.length) {
      i += 2;
    } else if (
      parts[i].startsWith("--git-dir=") ||
      parts[i].startsWith("--work-tree=")
    ) {
      i += 1;
    } else {
      break;
    }
  }

  if (i < parts.length) {
    return "git " + parts.slice(i).join(" ");
  }
  return command;
}

/**
 * Minimal shell-aware split that handles single and double quotes.
 */
function shellSplit(input: string): string[] {
  const parts: string[] = [];
  let current = "";
  let inSingle = false;
  let inDouble = false;
  for (const ch of input) {
    if (inSingle) {
      if (ch === "'") {
        inSingle = false;
      } else {
        current += ch;
      }
    } else if (inDouble) {
      if (ch === '"') {
        inDouble = false;
      } else {
        current += ch;
      }
    } else if (ch === "'") {
      inSingle = true;
    } else if (ch === '"') {
      inDouble = true;
    } else if (ch === " ") {
      if (current.length > 0) {
        parts.push(current);
        current = "";
      }
    } else {
      current += ch;
    }
  }
  if (current.length > 0) {
    parts.push(current);
  }
  return parts;
}

// ---------------------------------------------------------------------------
// Detect crosslink directory
// ---------------------------------------------------------------------------

/**
 * Walk up from `startDir` to find an initialised .crosslink directory
 * (one that contains hook-config.json).
 */
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

// ---------------------------------------------------------------------------
// Agent-context detection
// ---------------------------------------------------------------------------

/**
 * Check whether we are running inside an agent worktree.
 * - agent.json with role "agent"
 * - CWD contains "/.claude/worktrees/"
 */
function isAgentContext(crosslinkDir: string | null): boolean {
  if (crosslinkDir) {
    const agentJsonPath = path.join(crosslinkDir, "agent.json");
    if (fs.existsSync(agentJsonPath)) {
      try {
        const data = JSON.parse(fs.readFileSync(agentJsonPath, "utf-8"));
        if (data && typeof data === "object" && data.role === "agent") {
          return true;
        }
      } catch {
        // Malformed — fall through to cwd check
      }
    }
  }
  const cwd = process.cwd();
  if (cwd.includes("/.claude/worktrees/")) {
    return true;
  }
  return false;
}

// ---------------------------------------------------------------------------
// Config loading (with .local overlay and +key array-extend support)
// ---------------------------------------------------------------------------

interface HookConfig {
  tracking_mode?: string;
  blocked_git_commands?: string[];
  gated_git_commands?: string[];
  allowed_bash_prefixes?: string[];
  comment_discipline?: string;
  agent_overrides?: {
    tracking_mode?: string;
    blocked_git_commands?: string[];
    gated_git_commands?: string[];
    allowed_bash_prefixes?: string[];
    comment_discipline?: string;
    agent_lint_commands?: string[];
    agent_test_commands?: string[];
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

function loadConfigMerged(crosslinkDir: string | null): HookConfig {
  const config: HookConfig = {};

  if (!crosslinkDir) return config;

  const configPath = path.join(crosslinkDir, "hook-config.json");
  if (fs.existsSync(configPath)) {
    try {
      const raw = fs.readFileSync(configPath, "utf-8");
      Object.assign(config, JSON.parse(raw));
    } catch {
      // Malformed — keep defaults
    }
  }

  const localPath = path.join(crosslinkDir, "hook-config.local.json");
  if (fs.existsSync(localPath)) {
    try {
      const raw = fs.readFileSync(localPath, "utf-8");
      const local = JSON.parse(raw) as Record<string, unknown>;
      mergeWithExtend(config as Record<string, unknown>, local);
    } catch {
      // Malformed local override — ignore
    }
  }

  return config;
}

function mergeWithExtend(
  base: Record<string, unknown>,
  override: Record<string, unknown>,
): void {
  for (const [key, value] of Object.entries(override)) {
    if (key.startsWith("+")) {
      const realKey = key.slice(1);
      if (
        Array.isArray(value) &&
        Array.isArray(base[realKey])
      ) {
        base[realKey] = (base[realKey] as unknown[]).concat(value);
      } else {
        base[realKey] = value;
      }
    } else {
      base[key] = value;
    }
  }
}

interface LoadedConfig {
  tracking_mode: string;
  blocked_git: string[];
  gated_git: string[];
  allowed_bash: string[];
  is_agent: boolean;
  comment_discipline: string;
}

function loadConfig(crosslinkDir: string | null): LoadedConfig {
  const isAgent = isAgentContext(crosslinkDir);

  // Start with defaults
  const result: LoadedConfig = {
    tracking_mode: "strict",
    blocked_git: [...DEFAULT_BLOCKED_GIT],
    gated_git: [...DEFAULT_GATED_GIT],
    allowed_bash: [...DEFAULT_ALLOWED_BASH],
    is_agent: isAgent,
    comment_discipline: "encouraged",
  };

  if (isAgent && !crosslinkDir) {
    // No crosslink dir but agent context — relax
    result.tracking_mode = "relaxed";
    result.blocked_git = [...DEFAULT_AGENT_BLOCKED_GIT];
    result.gated_git = [];
    result.comment_discipline = "off";
    return result;
  }

  const config = loadConfigMerged(crosslinkDir);

  // No config at all
  if (Object.keys(config).length === 0) {
    if (isAgent) {
      result.tracking_mode = "relaxed";
      result.blocked_git = [...DEFAULT_AGENT_BLOCKED_GIT];
      result.gated_git = [];
      result.comment_discipline = "off";
    }
    return result;
  }

  // Apply root-level config
  if (config.tracking_mode && ["strict", "normal", "relaxed"].includes(config.tracking_mode)) {
    result.tracking_mode = config.tracking_mode;
  }
  if (config.blocked_git_commands) {
    result.blocked_git = [...config.blocked_git_commands];
  }
  if (config.gated_git_commands) {
    result.gated_git = [...config.gated_git_commands];
  }
  if (config.allowed_bash_prefixes) {
    result.allowed_bash = [...config.allowed_bash_prefixes];
  }
  if (config.comment_discipline && ["required", "encouraged", "off"].includes(config.comment_discipline)) {
    result.comment_discipline = config.comment_discipline;
  }

  // Apply agent overrides
  if (isAgent && config.agent_overrides) {
    const o = config.agent_overrides;
    result.tracking_mode = o.tracking_mode ?? "relaxed";
    result.blocked_git = o.blocked_git_commands
      ? [...o.blocked_git_commands]
      : [...DEFAULT_AGENT_BLOCKED_GIT];
    result.gated_git = o.gated_git_commands
      ? [...o.gated_git_commands]
      : [];
    result.comment_discipline = o.comment_discipline ?? "off";

    // Merge agent lint/test commands into allowed prefixes
    if (o.agent_lint_commands) {
      for (const cmd of o.agent_lint_commands) {
        if (!result.allowed_bash.includes(cmd)) {
          result.allowed_bash.push(cmd);
        }
      }
    }
    if (o.agent_test_commands) {
      for (const cmd of o.agent_test_commands) {
        if (!result.allowed_bash.includes(cmd)) {
          result.allowed_bash.push(cmd);
        }
      }
    }

    // Per-agent-type refinement: agent_overrides.by_type.<type> replaces the
    // shared blocked/gated lists for that specific agent role (e.g. reviewer/
    // auditor block git commit while builder keeps it gated). The type comes
    // from hook-config agent.type (the fork's read_agent_type equivalent).
    const byTypeMap = o.by_type as
      | Record<string, { blocked_git_commands?: string[]; gated_git_commands?: string[]; allowed_bash_prefixes?: string[] }>
      | undefined;
    const byType = byTypeMap?.[resolveAgentType(crosslinkDir)];
    if (byType) {
      if (byType.blocked_git_commands) {
        result.blocked_git = [...byType.blocked_git_commands];
      }
      if (byType.gated_git_commands) {
        result.gated_git = [...byType.gated_git_commands];
      }
      if (byType.allowed_bash_prefixes) {
        result.allowed_bash = [...byType.allowed_bash_prefixes];
      }
    }
  }

  return result;
}

/**
 * Resolve the configured agent type from hook-config.json `agent.type`.
 *
 * Mirrors the fork's `read_agent_type()`: reads `agent.type` (default
 * "builder") so per-agent-type overrides in `agent_overrides.by_type`
 * can be applied. Returns "builder" when absent or unparseable.
 */
function resolveAgentType(crosslinkDir: string | null): string {
  if (!crosslinkDir) return "builder";
  const configPath = path.join(crosslinkDir, "hook-config.json");
  try {
    const raw = fs.readFileSync(configPath, "utf-8");
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const agent = parsed.agent as Record<string, unknown> | undefined;
    const type = agent?.type as string | undefined;
    return type && type.trim().length > 0 ? type.trim() : "builder";
  } catch {
    return "builder";
  }
}

// ---------------------------------------------------------------------------
// Command matching helpers
// ---------------------------------------------------------------------------

/**
 * Check if a command (directly or via chaining) matches any entry in a list.
 * Normalises git commands before matching.
 */
function matchesCommandList(command: string, cmdList: string[]): boolean {
  const normalized = normalizeGitCommand(command);
  for (const entry of cmdList) {
    if (normalized.startsWith(entry)) return true;
  }
  // Check chained commands
  for (const sep of [" && ", " ; ", " | "]) {
    for (const part of command.split(sep)) {
      const trimmed = part.trim();
      if (trimmed) {
        const normPart = normalizeGitCommand(trimmed);
        for (const entry of cmdList) {
          if (normPart.startsWith(entry)) return true;
        }
      }
    }
  }
  return false;
}

/**
 * Check if a single sub-command (non-chained) matches any allowed prefix.
 */
function isSingleCommandAllowed(command: string, allowedList: string[]): boolean {
  // Strip leading "rtk " prefixes so "rtk git status" matches the "git status"
  // allowlist entry instead of falling through to strict-mode block (Issue 1).
  let cmd = command;
  while (cmd.startsWith("rtk ")) cmd = cmd.slice(4);
  for (const prefix of allowedList) {
    if (cmd.startsWith(prefix)) return true;
  }
  return false;
}

/**
 * Check if a bash command is entirely composed of allowed sub-commands.
 * Splits on chain operators (&&, ;, |) — EVERY sub-command must be allowed.
 */
function isAllowedBash(command: string, allowedList: string[]): boolean {
  if (!command) return false;

  // Progressive split: start with the full command, then split on each separator
  let parts = [command];
  for (const sep of [" && ", " ; ", " | "]) {
    const expanded: string[] = [];
    for (const part of parts) {
      expanded.push(...part.split(sep));
    }
    parts = expanded;
  }

  for (const part of parts) {
    const trimmed = part.trim();
    if (trimmed && !isSingleCommandAllowed(trimmed, allowedList)) {
      return false;
    }
  }
  return true;
}

// ---------------------------------------------------------------------------
// ~/.claude/ memory path exemption
// ---------------------------------------------------------------------------

function isClaudeMemoryPath(filePath: string | undefined): boolean {
  if (!filePath) return false;
  try {
    const home = os.homedir();
    const claudeDir = path.resolve(home, ".claude");
    const resolved = path.resolve(filePath);
    return resolved.startsWith(claudeDir);
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Crosslink CLI interaction via BunShell
// ---------------------------------------------------------------------------

async function runCrosslink(
  shell: PluginInput["$"],
  args: string[],
  cwd: string,
): Promise<{ stdout: string; exitCode: number } | null> {
  try {
    // Construct the command string safely
    const cmd = "crosslink " + args.map((a) => (a.includes(" ") ? `"${a}"` : a)).join(" ");
    const proc = shell.cwd(cwd)`${cmd}`.nothrow().quiet();
    const output = await proc;
    return {
      stdout: output.text().trim(),
      exitCode: output.exitCode,
    };
  } catch (e) {
    log("runCrosslink error:", String(e));
    return null;
  }
}

async function runCrosslinkGetStdout(
  shell: PluginInput["$"],
  args: string[],
  cwd: string,
): Promise<string | null> {
  const result = await runCrosslink(shell, args, cwd);
  if (result && result.exitCode === 0) {
    return result.stdout;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Control flags (kill / pause)
// ---------------------------------------------------------------------------

interface AgentFlags {
  kill?: boolean;
  paused?: boolean;
  reprioritise?: { issue_id?: number } | null;
}

async function checkControlFlags(
  shell: PluginInput["$"],
  crosslinkDir: string | null,
  throwBlock: (msg: string) => never,
): Promise<void> {
  if (!crosslinkDir) return;

  const result = await runCrosslink(shell, ["agent", "flags", "--strict"], crosslinkDir);
  if (!result) return; // crosslink not available or hung — fail open

  if (result.exitCode === 0) return; // No blocking flags

  if (result.exitCode === 2) {
    let state: AgentFlags = {};
    try {
      state = JSON.parse(result.stdout) as AgentFlags;
    } catch {
      state = {};
    }

    if (state.kill) {
      throwBlock(
        "AGENT KILL REQUESTED — an operator (dashboard or CLI) has " +
          "asked this agent to stop after the current tool use.\n" +
          "Acknowledge the request, summarise progress, then exit " +
          "your session cleanly. Do not attempt further tool calls.",
      );
    } else {
      let extra = "";
      if (state.reprioritise?.issue_id) {
        extra =
          `\nReprioritise hint pending: switch focus to issue ` +
          `#${state.reprioritise.issue_id} when resuming.`;
      }
      throwBlock(
        "AGENT PAUSED — an operator has paused this agent via the " +
          "dashboard. Tool use is blocked until they resume.\n" +
          "Wait for the resume signal or explain to the user that " +
          "you've been paused." + extra,
      );
    }
  }
}

// ---------------------------------------------------------------------------
// Active issue helpers
// ---------------------------------------------------------------------------

async function getActiveIssueId(
  shell: PluginInput["$"],
  crosslinkDir: string,
): Promise<number | null> {
  const stdout = await runCrosslinkGetStdout(shell, ["session", "status", "--json"], crosslinkDir);
  if (!stdout) return null;
  try {
    const data = JSON.parse(stdout) as {
      working_on?: { id?: number } | null;
    };
    const workingOn = data.working_on;
    if (workingOn && typeof workingOn.id === "number") {
      return workingOn.id;
    }
  } catch {
    // JSON parse error
  }
  return null;
}

function issueHasCommentKind(
  crosslinkDir: string,
  issueId: number,
  kind: string,
): boolean {
  const dbPath = path.join(crosslinkDir, "issues.db");
  if (!fs.existsSync(dbPath)) return true; // No database — don't block

  try {
    const db = new Database(dbPath, { readonly: true });
    try {
      const stmt = db.prepare<{ count: number }, [number, string]>(
        "SELECT COUNT(*) as count FROM comments WHERE issue_id = ? AND kind = ?",
      );
      const row = stmt.get(issueId, kind);
      return row !== null && row.count > 0;
    } finally {
      db.close();
    }
  } catch {
    return true; // DB error — don't block
  }
}

// ---------------------------------------------------------------------------
// Issue close command detection
// ---------------------------------------------------------------------------

/**
 * Detect `crosslink issue close <id>` or `crosslink close <id>` commands.
 * Returns the issue ID string or null.
 */
function detectIssueCloseCommand(command: string): string | null {
  // Match: crosslink issue close <id>, crosslink close <id>, crosslink -q issue close <id>, etc.
  const m = command.match(/crosslink\s+(?:-[qQ]\s+)?(?:issue\s+)?close\s+(\S+)/);
  if (m) {
    const issueArg = m[1];
    // Skip flags like --no-changelog
    if (issueArg.startsWith("-")) return null;
    return issueArg;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Block message helpers
// ---------------------------------------------------------------------------

const BLOCKED_GIT_MESSAGE =
  "MANDATORY COMPLIANCE — DO NOT ATTEMPT TO WORK AROUND THIS BLOCK.\n\n" +
  "Git mutation commands (push, merge, rebase, reset, etc.) are " +
  "PERMANENTLY FORBIDDEN. The human performs all git write operations.\n\n" +
  "You MUST NOT:\n" +
  "  - Retry this command\n" +
  "  - Rewrite the command to achieve the same effect\n" +
  "  - Use a different tool to perform git mutations\n" +
  "  - Ask the user if you should bypass this restriction\n\n" +
  "You MUST instead:\n" +
  "  - Inform the user that this is a manual step for them\n" +
  "  - Continue with your other work\n\n" +
  "Read-only git commands (status, diff, log, show, branch) are allowed.\n\n" +
  "--- INTERVENTION LOGGING ---\n" +
  'Log this blocked action for the audit trail:\n' +
  '  crosslink intervene <issue-id> "Attempted: <command>" ' +
  '--trigger tool_blocked --context "<what you were trying to accomplish>"';

const GATED_GIT_NO_ISSUE_MESSAGE =
  "Git commit requires an active crosslink issue.\n\n" +
  'Create one first:\n' +
  '  crosslink quick "<describe the work>" -p <priority> -l <label>\n\n' +
  "Or pick an existing issue:\n" +
  "  crosslink issue list -s open\n" +
  "  crosslink session work <id>\n\n" +
  "--- INTERVENTION LOGGING ---\n" +
  'If a human redirected you here, log the intervention:\n' +
  '  crosslink intervene <issue-id> "Redirected to create issue before commit" ' +
  '--trigger redirect --context "Attempted git commit without active issue"';

function buildPlanCommentMessage(issueId: number): string {
  return (
    "Comment discipline: git commit requires a --kind plan comment " +
    "on the active issue before committing.\n\n" +
    "Add one now:\n" +
    `  crosslink issue comment ${issueId} "<your approach>" --kind plan\n\n` +
    "This documents WHY the change was made, not just WHAT changed."
  );
}

function buildResultCommentMessage(issueId: number): string {
  return (
    "Comment discipline: closing an issue requires a --kind result " +
    "comment documenting what was delivered.\n\n" +
    "Add one now:\n" +
    `  crosslink issue comment ${issueId} "<what was delivered>" --kind result\n\n` +
    "This creates the audit trail for the work that was done."
  );
}

const STRICT_MODE_MESSAGE =
  "MANDATORY COMPLIANCE — DO NOT ATTEMPT TO WORK AROUND THIS BLOCK.\n\n" +
  "You cannot Write, Edit, or run Bash commands without an active crosslink issue. " +
  "This is a hard requirement enforced by the project, not a suggestion.\n\n" +
  "You MUST NOT:\n" +
  "  - Retry the same tool call hoping it will work\n" +
  "  - Try alternative tools or approaches to bypass this check\n" +
  "  - Proceed without creating an issue first\n" +
  "  - Tell the user the hook is preventing you from working\n\n" +
  'You MUST do exactly this, right now, before anything else:\n\n' +
  '  crosslink quick "<describe what you are about to do>" -p <priority> -l <label>\n\n' +
  "This single command creates an issue AND sets it as your active work item. " +
  "After running it, your tool calls will succeed.\n\n" +
  "If an issue already exists for this work, use:\n" +
  "  crosslink issue list -s open\n" +
  "  crosslink session work <id>\n\n" +
  "This is how the project tracks work. Comply, then continue.\n\n" +
  "--- INTERVENTION LOGGING ---\n" +
  'After creating the issue, log this intervention:\n' +
  '  crosslink intervene <issue-id> "Blocked: no active issue" ' +
  '--trigger tool_blocked --context "<what you were about to do>"';

const NORMAL_MODE_MESSAGE =
  "Reminder: No active crosslink issue. You should create one before making changes.\n\n" +
  '  crosslink quick "<describe what you are about to do>" -p <priority> -l <label>\n\n' +
  "Or pick an existing issue:\n" +
  "  crosslink issue list -s open\n" +
  "  crosslink session work <id>";

// ---------------------------------------------------------------------------
// Plugin factory
// ---------------------------------------------------------------------------

const crosslinkGuardPlugin: Plugin = async (pluginInput) => {
  const projectDir = pluginInput.directory;
  const shell = pluginInput.$;

  log(
    "Plugin initialised, projectDir:",
    projectDir,
    "cwd:",
    process.cwd(),
  );

  // Lazily computed state (computed on first hook call to avoid slow startup)
  let resolvedCrosslinkDir: string | null = null;
  let resolvedConfig: LoadedConfig | null = null;

  function ensureState(): { crosslinkDir: string | null; config: LoadedConfig } {
    if (resolvedConfig === null) {
      resolvedCrosslinkDir = findCrosslinkDir(projectDir);
      resolvedConfig = loadConfig(resolvedCrosslinkDir);
      log(
        "State resolved — crosslinkDir:",
        resolvedCrosslinkDir,
        "tracking_mode:",
        resolvedConfig.tracking_mode,
        "is_agent:",
        resolvedConfig.is_agent,
      );
    }
    return { crosslinkDir: resolvedCrosslinkDir, config: resolvedConfig };
  }

  // Apply the per-agent-type override for the runtime agent once the actual
  // agent name is known (opencode passes it as `input.agent`, reflecting the
  // `--agent <type>` launch flag). This is re-applied on every call so a
  // type change mid-session is honoured, but resolution is cheap.
  function applyAgentTypeOverride(
    crosslinkDir: string | null,
    config: LoadedConfig,
  ): LoadedConfig {
    // Authoritative source: CROSSLINK_AGENT_TYPE exported by the claude
    // wrapper at launch (reflects `--agent <type>`). Fall back to the
    // worktree hook-config agent.type.
    const runtimeAgent = process.env.CROSSLINK_AGENT_TYPE || resolveAgentType(crosslinkDir);
    if (!runtimeAgent || !crosslinkDir) return config;
    const merged = loadConfigMerged(crosslinkDir);
    const byTypeMap = merged.agent_overrides?.by_type as
      | Record<string, { blocked_git_commands?: string[]; gated_git_commands?: string[]; allowed_bash_prefixes?: string[] }>
      | undefined;
    const byType = byTypeMap?.[runtimeAgent];
    if (!byType) return config;
    const next: LoadedConfig = { ...config };
    if (byType.blocked_git_commands) next.blocked_git = [...byType.blocked_git_commands];
    if (byType.gated_git_commands) next.gated_git = [...byType.gated_git_commands];
    if (byType.allowed_bash_prefixes) next.allowed_bash = [...byType.allowed_bash_prefixes];
    log("by_type override applied for agent:", runtimeAgent);
    return next;
  }

  return {
    "tool.execute.before": async (input, output) => {
      const toolName = input.tool as string;
      const toolLower = toolName.toLowerCase();

      // Only intercept write, edit, bash
      if (toolLower !== "write" && toolLower !== "edit" && toolLower !== "bash") {
        return;
      }

      log("Intercepting tool:", toolName, "callID:", input.callID);

      // ------------------------------------------------------------------
      // 1. Operator kill/pause flags (highest priority)
      // ------------------------------------------------------------------
      const tmpCrosslinkDir = findCrosslinkDir(projectDir);
      await checkControlFlags(shell, tmpCrosslinkDir, (msg: string) => {
        log("BLOCK: kill/pause flag");
        throw new Error(msg);
      });

      // ------------------------------------------------------------------
      // 2. ~/.claude/ exemption (write/edit only)
      // ------------------------------------------------------------------
      if (toolLower === "write" || toolLower === "edit") {
        const filePath = output.args?.filePath as string | undefined;
        if (isClaudeMemoryPath(filePath)) {
          log("ALLOW: ~/.claude/ path:", filePath);
          return;
        }
      }

      // ------------------------------------------------------------------
      // Resolve state (config, crosslink dir) + per-agent-type override
      // ------------------------------------------------------------------
      const { crosslinkDir, config: baseConfig } = ensureState();
      const config = applyAgentTypeOverride(crosslinkDir, baseConfig);

      // ------------------------------------------------------------------
      // 3. Permanently blocked git commands
      // ------------------------------------------------------------------
      if (toolLower === "bash") {
        const command = (output.args?.command as string) ?? "";
        if (matchesCommandList(command, config.blocked_git)) {
          log("BLOCK: blocked git command:", command);
          throw new Error(BLOCKED_GIT_MESSAGE);
        }
      }

      // ------------------------------------------------------------------
      // 4. Gated git commands (git commit with active issue + plan comment)
      // ------------------------------------------------------------------
      if (toolLower === "bash") {
        const command = (output.args?.command as string) ?? "";
        if (matchesCommandList(command, config.gated_git)) {
          if (!crosslinkDir) {
            log("ALLOW: gated git but no crosslink dir");
            return;
          }

          // Fast path: check .active-issue sentinel file (matches Section 9 behavior)
          const sentinelPath = path.join(crosslinkDir, ".active-issue");
          let hasActiveIssue = false;
          if (fs.existsSync(sentinelPath)) {
            try {
              const sentinelContent = fs.readFileSync(sentinelPath, "utf-8").trim();
              if (sentinelContent) {
                log("ALLOW: gated git, active issue sentinel present:", sentinelContent);
                // Sentinel is valid — short-circuit the subprocess call
                hasActiveIssue = true;
              }
            } catch {
              // Fall through to subprocess
            }
          }

          // Check for active issue (only if sentinel didn't already confirm one)
          if (!hasActiveIssue) {
            const statusStdout = await runCrosslinkGetStdout(
              shell,
              ["session", "status"],
              crosslinkDir,
            );
            hasActiveIssue =
              statusStdout !== null &&
              (statusStdout.includes("Working on: #") ||
                statusStdout.includes("Working on: L"));
          }

          if (!hasActiveIssue) {
            log("BLOCK: gated git without active issue:", command);
            throw new Error(GATED_GIT_NO_ISSUE_MESSAGE);
          }

          // Comment discipline: plan comment required
          if (
            config.comment_discipline === "required" ||
            config.comment_discipline === "encouraged"
          ) {
            const issueId = await getActiveIssueId(shell, crosslinkDir);
            if (issueId !== null && !issueHasCommentKind(crosslinkDir, issueId, "plan")) {
              const msg = buildPlanCommentMessage(issueId);
              if (config.comment_discipline === "required") {
                log("BLOCK: gated git no plan comment, issue:", issueId);
                throw new Error(msg);
              } else {
                log("REMINDER: gated git no plan comment, issue:", issueId);
                // Encouraged mode: print reminder but allow through
                // In OpenCode plugin, we can't print to the model like a reminder,
                // but we return without blocking — the model sees the tool succeed.
                // We log the reminder and allow the tool to proceed.
                log("Encouragement reminder (not blocking):", msg);
              }
            }
          }

          log("ALLOW: gated git with active issue:", command);
          return;
        }
      }

      // ------------------------------------------------------------------
      // 5. Issue close comment discipline
      // ------------------------------------------------------------------
      if (
        toolLower === "bash" &&
        crosslinkDir &&
        (config.comment_discipline === "required" ||
          config.comment_discipline === "encouraged")
      ) {
        const command = (output.args?.command as string) ?? "";
        const closeTarget = detectIssueCloseCommand(command);
        if (closeTarget !== null) {
          let issueId: number | null = null;

          // Try numeric parsing first
          const stripped = closeTarget.replace(/^#/, "");
          const parsed = parseInt(stripped, 10);
          if (!isNaN(parsed)) {
            issueId = parsed;
          } else {
            // L-prefixed or other format — try crosslink show --json
            const showStdout = await runCrosslinkGetStdout(
              shell,
              ["issue", "show", closeTarget, "--json"],
              crosslinkDir,
            );
            if (showStdout) {
              try {
                const showData = JSON.parse(showStdout) as { id?: number };
                if (typeof showData.id === "number") {
                  issueId = showData.id;
                }
              } catch {
                // JSON parse error
              }
            }
          }

          if (issueId !== null && !issueHasCommentKind(crosslinkDir, issueId, "result")) {
            const msg = buildResultCommentMessage(issueId);
            if (config.comment_discipline === "required") {
              log("BLOCK: issue close without result comment, issue:", issueId);
              throw new Error(msg);
            } else {
              log("REMINDER: issue close without result comment, issue:", issueId);
              // Encouraged mode: log reminder but allow
            }
          }
        }
      }

      // ------------------------------------------------------------------
      // 6. Allowed bash commands pass through
      // ------------------------------------------------------------------
      if (toolLower === "bash") {
        const command = (output.args?.command as string) ?? "";
        if (isAllowedBash(command, config.allowed_bash)) {
          log("ALLOW: allowed bash command:", command.slice(0, 120));
          return;
        }
      }

      // ------------------------------------------------------------------
      // 7. Relaxed mode: no issue-tracking enforcement
      // ------------------------------------------------------------------
      if (config.tracking_mode === "relaxed") {
        log("ALLOW: relaxed tracking mode");
        return;
      }

      // ------------------------------------------------------------------
      // 8. No crosslink dir — can't enforce
      // ------------------------------------------------------------------
      if (!crosslinkDir) {
        log("ALLOW: no crosslink dir");
        return;
      }

      // ------------------------------------------------------------------
      // 9. Active issue enforcement (fast path via sentinel, slow via subprocess)
      // ------------------------------------------------------------------

      // Fast path: .active-issue sentinel file
      const sentinelPath = path.join(crosslinkDir, ".active-issue");
      if (fs.existsSync(sentinelPath)) {
        try {
          const content = fs.readFileSync(sentinelPath, "utf-8").trim();
          if (content) {
            log("ALLOW: active issue sentinel present:", content);
            return;
          }
        } catch {
          // Fall through to subprocess
        }
      }

      // Slow path: session status subprocess
      const statusStdout = await runCrosslinkGetStdout(
        shell,
        ["session", "status"],
        crosslinkDir,
      );
      if (!statusStdout) {
        log("ALLOW: crosslink not available");
        return;
      }

      if (
        statusStdout.includes("Working on: #") ||
        statusStdout.includes("Working on: L")
      ) {
        log("ALLOW: active issue from session status");
        return;
      }

      // ------------------------------------------------------------------
      // 10. No active work item — behaviour by tracking mode
      // ------------------------------------------------------------------
      if (config.tracking_mode === "strict") {
        log("BLOCK: strict mode, no active issue");
        throw new Error(STRICT_MODE_MESSAGE);
      } else {
        // normal mode — remind but allow
        log("REMINDER (normal mode):", NORMAL_MODE_MESSAGE);
        // In OpenCode plugin we can't print to stderr like Claude Code hooks do.
        // We return without blocking. The model sees the tool succeed.
        // Logging the reminder is the best we can do.
        return;
      }
    },
  };
};

export default crosslinkGuardPlugin;
