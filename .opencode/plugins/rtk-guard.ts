/**
 * RTK Guard — OpenCode Native TypeScript Plugin
 *
 * Transparently rewrites bash tool calls through RTK's CLI proxy
 * (`rtk rewrite`), restoring the token-saving transparent rewriting that
 * Claude Code's PreToolUse hook provides but OpenCode cannot run natively.
 *
 * Hooks `tool.execute.before`, intercepts bash calls, and mutates
 * `output.args.command` to prepend `rtk` where appropriate.
 *
 * Core safety properties (fail-open, never blocks):
 *   - Defaults to no-op if the binary is missing, degraded, or too slow
 *   - Rewrites only validated commands (v1 conservative allowlist)
 *   - Structural loop guard prevents double-wrapping
 *   - Every error path degrades to passing the original command through
 *
 * @module rtk-guard
 */

import type { Plugin } from "@opencode-ai/plugin";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

// ---------------------------------------------------------------------------
// Logging
// ---------------------------------------------------------------------------

const ERR_LOG = "/tmp/rtk-guard.log";

function logErr(...args: unknown[]): void {
  try {
    const line =
      new Date().toISOString() +
      " [rtk-guard] " +
      args.map((a) => String(a)).join(" ") +
      "\n";
    fs.appendFileSync(ERR_LOG, line, "utf-8");
  } catch {
    // Best-effort logging — never throw from a hook
  }
}

// ---------------------------------------------------------------------------
// Audit logging (gated on RTK_HOOK_AUDIT=1, matches RTK's exact format)
// ---------------------------------------------------------------------------

const AUDIT_LOG = path.join(os.homedir(), ".local/share/rtk/hook-audit.log");

function localTimestamp(d: Date): string {
  const pad = (x: number, n = 2) => String(x).padStart(n, "0");
  return (
    d.getFullYear() +
    "-" +
    pad(d.getMonth() + 1) +
    "-" +
    pad(d.getDate()) +
    "T" +
    pad(d.getHours()) +
    ":" +
    pad(d.getMinutes()) +
    ":" +
    pad(d.getSeconds()) +
    "." +
    pad(d.getMilliseconds(), 3)
  );
}

function sanitizeLogField(s: string): string {
  return s
    .replace(/\\/g, "\\\\")
    .replace(/\|/g, "\\|")
    .replace(/\n/g, "\\n")
    .replace(/\r/g, "\\r");
}

function audit(action: string, original: string, rewritten: string): void {
  if (process.env.RTK_HOOK_AUDIT !== "1") return;
  try {
    fs.mkdirSync(path.dirname(AUDIT_LOG), { recursive: true });
    const line =
      localTimestamp(new Date()) +
      " | " +
      action +
      " | " +
      sanitizeLogField(original) +
      " | " +
      sanitizeLogField(rewritten) +
      "\n";
    fs.appendFileSync(AUDIT_LOG, line, "utf-8");
  } catch {
    // Best-effort audit — never throw from a hook
  }
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const OPT_OUT_PREFIX = "RTK_DISABLED=1 ";
const RTK_FALLBACK = path.join(os.homedir(), ".cargo/bin/rtk");
const SPAWN_TIMEOUT_MS = 100;
const LATENCY_SAMPLE_SIZE = 200;
const LATENCY_P95_LIMIT_MS = 15;
const LATENCY_RECHECK_CALLS = 500;
const MIN_RTK_VERSION = 0 * 10000 + 40 * 100 + 0; // 0.40.0

// v1 conservative allowlist — only rewrite commands whose leading token is here
const V1_VALIDATED = new Set([
  "git",
  "ls",
  "grep",
  "find",
  "diff",
  "wc",
  "cat", // rtk rewrite maps cat to rtk read
]);

// ---------------------------------------------------------------------------
// Lazy session state
// ---------------------------------------------------------------------------

interface GuardState {
  gateChecked: boolean;
  mode: "live" | "no-op";
  binaryPath: string | null;
  liveDisabled: boolean; // latency gate disabled live mode
  samples: number[]; // rolling latency samples (ms), last 200
  callsSinceDisable: number;
}

const state: GuardState = {
  gateChecked: false,
  mode: "live",
  binaryPath: null,
  liveDisabled: false,
  samples: [],
  callsSinceDisable: 0,
};

// ---------------------------------------------------------------------------
// Binary gate (runs once at first invocation)
// ---------------------------------------------------------------------------

function resolveBinary(): string | null {
  const env = process.env.RTK_BINARY;
  if (env && fs.existsSync(env)) return env;
  let whichEmpty = false;
  try {
    const p = Bun.spawnSync(["which", "rtk"], { timeout: SPAWN_TIMEOUT_MS });
    const out = (p.stdout?.toString() ?? "").trim();
    if (out && fs.existsSync(out)) return out;
    whichEmpty = !out;
  } catch {
    // `which` unavailable — fall through to fallback below
  }
  // Issue 2: PATH-resolvability is a gate requirement. If `which rtk` returned
  // empty (rtk not in PATH), do NOT fall back to the hardcoded absolute path:
  // a rewrite would emit bare `rtk ...` which bash cannot resolve, violating
  // fail-open. Only use the fallback when `which` itself was unavailable.
  if (!whichEmpty && fs.existsSync(RTK_FALLBACK)) return RTK_FALLBACK;
  return null;
}

function checkBinaryGate(): boolean {
  const bin = resolveBinary();
  if (!bin) {
    logErr("EVENT: binary gate FAILED — rtk binary not found");
    return false;
  }
  state.binaryPath = bin;

  // Version check: require >= 0.40.0
  try {
    const v = Bun.spawnSync([bin, "--version"], { timeout: SPAWN_TIMEOUT_MS });
    const out = (v.stdout?.toString() ?? "").trim();
    const m = out.match(/(\d+)\.(\d+)\.(\d+)/);
    if (!m) {
      logErr("EVENT: binary gate FAILED — could not parse version from:", out);
      return false;
    }
    const versionNum =
      parseInt(m[1], 10) * 10000 +
      parseInt(m[2], 10) * 100 +
      parseInt(m[3], 10);
    if (versionNum < MIN_RTK_VERSION) {
      logErr("EVENT: binary gate FAILED — rtk version", out, "requires >= 0.40.0");
      return false;
    }
  } catch (e) {
    logErr("EVENT: binary gate FAILED — version check error:", String(e));
    return false;
  }

  // Integrity probe: rtk rewrite "git status" must return non-empty stdout starting with "rtk "
  try {
    const p = Bun.spawnSync([bin, "rewrite", "git status"], {
      timeout: SPAWN_TIMEOUT_MS,
    });
    const out = (p.stdout?.toString() ?? "").trim();
    if (!out.startsWith("rtk ")) {
      logErr("EVENT: binary gate FAILED — integrity probe returned:", JSON.stringify(out));
      return false;
    }
  } catch (e) {
    logErr("EVENT: binary gate FAILED — integrity probe error:", String(e));
    return false;
  }

  logErr("EVENT: binary gate PASSED — rtk at", bin);
  return true;
}

function ensureGate(): void {
  if (state.gateChecked) return;
  state.gateChecked = true;
  if (!checkBinaryGate()) {
    state.mode = "no-op";
    logErr("EVENT: entering no-op mode for session");
  }
}

// ---------------------------------------------------------------------------
// Latency gate (rolling p95 over last 200 calls)
// ---------------------------------------------------------------------------

function computeP95(samples: number[]): number {
  if (samples.length === 0) return 0;
  const sorted = [...samples].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.floor(sorted.length * 0.95));
  return sorted[idx];
}

function recordSample(ms: number): void {
  state.samples.push(ms);
  if (state.samples.length > LATENCY_SAMPLE_SIZE) state.samples.shift();
}

// ---------------------------------------------------------------------------
// Unattestable construct scan (quote-aware)
// ---------------------------------------------------------------------------

function hasUnattestable(command: string): boolean {
  let inSingle = false;
  let inDouble = false;
  const n = command.length;
  for (let i = 0; i < n; i++) {
    const ch = command[i];
    if (inSingle) {
      if (ch === "'") inSingle = false;
      continue;
    }
    if (inDouble) {
      if (ch === '"') {
        inDouble = false;
        continue;
      }
      // Issue 6: bash evaluates $() and backticks inside double quotes
      // (unlike single quotes), so still flag those as unattestable. The
      // >, <, sudo, env checks below are only reached outside quotes, so they
      // remain correctly skipped inside double quotes.
      if (ch === "$" && command[i + 1] === "(") return true; // $()
      if (ch === "`") return true; // backtick
      continue;
    }
    if (ch === "'") {
      inSingle = true;
      continue;
    }
    if (ch === '"') {
      inDouble = true;
      continue;
    }
    // Outside quotes — check for unattestable constructs
    if (ch === "$" && command[i + 1] === "(") return true; // $()
    if (ch === "`") return true; // backtick
    if (ch === ">") return true; // >, >>, >()
    if (ch === "<") return true; // <, <<, <()
    if (ch === "s" && command.startsWith("sudo", i)) {
      const prev = i > 0 ? command[i - 1] : " ";
      const after = command[i + 4];
      const boundary = (c: string) =>
        c === undefined || /\s/.test(c) || ";|&()".includes(c);
      if (boundary(prev) && boundary(after)) return true;
    }
    if (ch === "e" && command.startsWith("env", i)) {
      const prev = i > 0 ? command[i - 1] : " ";
      const after = command[i + 3];
      const boundary = (c: string) =>
        c === undefined || /\s/.test(c) || ";|&()".includes(c);
      if (boundary(prev) && boundary(after)) return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------------------
// Plugin factory
// ---------------------------------------------------------------------------

const rtkGuardPlugin: Plugin = async () => {
  logErr("EVENT: plugin initialised, cwd:", process.cwd());

  return {
    "tool.execute.before": async (input, output) => {
      try {
        // 1. Only intercept bash
        const toolName = (input as { tool?: string }).tool ?? "";
        if (toolName.toLowerCase() !== "bash") return;

        const command = ((output as { args?: { command?: string } }).args?.command ?? "") as string;
        if (!command) return;

        // 2. Loop guard — prevent double-wrapping / re-entry
        // Issue 4: use trimStart() so leading whitespace ("  rtk git status")
        // is still recognised as already-wrapped.
        const trimmedCmd = command.trimStart();
        if (
          trimmedCmd.startsWith("rtk ") ||
          trimmedCmd.startsWith("rtk:") ||
          command.trim() === "rtk"
        ) {
          audit("skip:already_rtk", command, "");
          return;
        }

        // 3. Opt-out — RTK_DISABLED=1 env or command prefix
        if (process.env.RTK_DISABLED === "1") {
          audit("skip:opt_out", command, "");
          return;
        }
        if (command.startsWith(OPT_OUT_PREFIX)) {
          const stripped = command.slice(OPT_OUT_PREFIX.length);
          (output as { args: { command: string } }).args.command = stripped;
          audit("skip:opt_out", command, stripped);
          return;
        }

        // 4. Unattestable constructs — quote-aware rejection
        if (hasUnattestable(command)) {
          audit("skip:unattestable", command, "");
          return;
        }

        // 5. Binary gate — fail → no-op mode for session
        ensureGate();
        if (state.mode === "no-op") {
          audit("skip:no_op", command, "");
          return;
        }

        // 6. Latency gate — disable live mode if p95 over last 200 calls > 15ms
        if (state.liveDisabled) {
          // Issue 3: re-enable counter lives HERE (not in recordSample, which
          // is never reached while liveDisabled). After LATENCY_RECHECK_CALLS
          // calls, re-enable live mode, clear stale high-latency samples (so
          // the gate doesn't re-trip immediately), and reset the counter.
          state.callsSinceDisable++;
          if (state.callsSinceDisable >= LATENCY_RECHECK_CALLS) {
            state.liveDisabled = false;
            state.callsSinceDisable = 0;
            state.samples = [];
            logErr("EVENT: latency gate re-check — re-enabling live mode after", LATENCY_RECHECK_CALLS, "calls");
          }
          audit("skip:latency", command, "");
          return;
        }
        if (state.samples.length >= LATENCY_SAMPLE_SIZE) {
          const p95 = computeP95(state.samples);
          if (p95 > LATENCY_P95_LIMIT_MS) {
            state.liveDisabled = true;
            state.callsSinceDisable = 0;
            logErr("EVENT: latency gate exceeded — p95=" + p95.toFixed(2) + "ms > 15ms; disabling live mode");
            audit("skip:latency", command, "");
            return;
          }
        }

        // 7. Live rewrite via rtk rewrite <command>
        const start = performance.now();
        const proc = Bun.spawnSync([state.binaryPath!, "rewrite", command], {
          timeout: SPAWN_TIMEOUT_MS,
        });
        const elapsed = performance.now() - start;
        recordSample(elapsed);

        const rewritten = (proc.stdout?.toString() ?? "").trim();

        // 8. Empty stdout → command not supported → pass through
        if (!rewritten) {
          audit("skip:no_match", command, "");
          return;
        }

        // 9. Validated allowlist — only rewrite known-safe leading commands
        const firstToken = command.trim().split(/\s+/)[0];
        if (!V1_VALIDATED.has(firstToken)) {
          audit("skip:unvalidated", command, rewritten);
          return;
        }

        // 10. Audit the rewrite
        audit("rewrite", command, rewritten);

        // 11. Mutate the command
        (output as { args: { command: string } }).args.command = rewritten;
      } catch (e) {
        // Never throw, never block — degrade to pass-through
        logErr("EVENT: unexpected error in hook body:", String(e));
      }
    },
  };
};

export default rtkGuardPlugin;
