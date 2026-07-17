# Design: `rtk-guard.ts` — OpenCode Native RTK Rewrite Plugin (Revised Design B)

**Status:** Design Proposal (Revised per Adversarial Review)
**Date:** 2026-07-13
**Author:** Independent verification agent
**Canonical Location:** `.opencode/design/rtk-guard-plugin-design.md`
**Target Implementation:** `.opencode/plugins/rtk-guard.ts`

---

## 1. Overview

`rtk-guard.ts` is an OpenCode native TypeScript plugin that transparently rewrites bash commands to prepend `rtk` where doing so reduces LLM token consumption via RTK's output caching and compression. It is the OpenCode equivalent of RTK's `PreToolUse` hook for Claude Code (`~/.claude/settings.json` → `rtk hook claude`), adapted for OpenCode's plugin architecture.

The plugin is auto-discovered from `.opencode/plugins/rtk-guard.ts` — no changes to `opencode.json` required. It runs inside the Bun runtime that OpenCode provides for plugins.

### Design philosophy

This design is grounded in **latency-gate-first** discipline: all performance-critical decisions are driven by measurement in the actual Bun runtime, not by assumption. The default posture is **static pattern matching** (zero subprocess overhead). Live subprocess-based rewriting via `rtk rewrite` is activated only if a hard latency gate (p95 ≤ 15ms) permits. This inverts the common "try live, fall back statically" ordering because the cost of being wrong about latency is paid on every bash call, indefinitely.

### Key properties

| Property | Value |
|---|---|
| **Scope** | Per-project (`.opencode/plugins/`) |
| **Runtime** | OpenCode's Bun runtime (guaranteed available) |
| **Hook** | `tool.execute.before` on `tool === "bash"` |
| **Default mechanism** | Static pattern match (in-process string matching, zero subprocess overhead) |
| **Fallback mechanism** | Live `rtk rewrite` subprocess (only if latency gate permits) |
| **Latency budget** | Must not add more than 15ms p95 per bash call |
| **Subprocess timeout** | Hard 100ms per call; if exceeded, drop to static fallback for that call |
| **Failure mode** | Silent pass-through — never block or error on bash |
| **Loop safety** | Structural early-return guard required; infinite recursion would crash the session |
| **Opt-out** | `RTK_DISABLED=1` env var prefix honored |

---

## 2. Hook Registration & Lifetime

### Registration

The plugin exports a default factory function matching the `Plugin` type from `@opencode-ai/plugin`:

```typescript
import type { Plugin } from "@opencode-ai/plugin";

const rtkGuardPlugin: Plugin = async (pluginInput) => {
  // Initialisation (runs once when plugin loads)
  return {
    "tool.execute.before": async (input, output) => {
      // Hook logic
    },
  };
};

export default rtkGuardPlugin;
```

The file at `.opencode/plugins/rtk-guard.ts` is auto-discovered by OpenCode. No `opencode.json` entry or explicit registration is needed.

### Lifetime

| Phase | Behaviour |
|---|---|
| **Plugin load** | Perform binary integrity check (§5). Detect `rtk` binary path, validate minimum version. If unavailable or below version floor, log warning and operate in static-fallback mode. |
| **Session open** | First `tool.execute.before` invocation triggers lazy initialisation of cached state (binary path, version check result, fallback command list, latency probe). |
| **Each bash call** | Hook fires → opt-out check (§5.3) → loop guard → binary integrity re-check → command classification → rewrite → audit log (§6) → return. |
| **Plugin dispose** | No state to clean up (subprocess handles are created per-call and cleaned by OS). |

The plugin is stateless between calls. The only mutable state is a lazily-resolved reference to the RTK binary path and its version string.

---

## 3. Command Classification Strategy

### 3.1 The latency gate (measure in Bun, not in bash)

The `tool.execute.before` hook fires on every bash call, in every session, forever. If classification requires a subprocess, that subprocess sits on the critical path of every bash invocation. The cost of being wrong about latency accumulates on every call.

**Measurement methodology (must execute in Bun runtime, not shell):**

1. **Bare subprocess overhead in Bun.** Use `Bun.nanoseconds()` (or equivalent high-resolution timer) to measure `Bun.spawnSync(["rtk", "--version"], ...)` in a tight loop of 100 iterations. Record:
   - p50 (median) latency
   - p95 latency (95th percentile)
   - p99 latency

2. **Calls-per-session estimate.** Historical data shows ~793 commands tracked across a session; recent activity ~113 commands / 4 days. Use 100–200 as the planning midpoint.

3. **Added latency per session** = `p95_classify_latency_ms × calls_per_session`.

4. **Hard threshold:** If p95 latency exceeds **15ms**, the live subprocess path is disabled entirely for the session and the plugin operates exclusively in static pattern match mode. If p95 ≤ 15ms, live subprocess may be enabled — but each individual call is still subject to a **100ms hard timeout** (not the 1s timeout from the original design).

5. **Re-evaluation:** Re-run the latency probe every 500 calls or on session restart. Do not cache the result indefinitely — system load changes.

### 3.2 Decision tree

```
                    ┌─────────────────────┐
                    │  Bash call received   │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │  RTK_DISABLED=1 set?              │──────── Opt-out → return (no rewrite)
              └──────────────────────────────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │  Loop guard: starts with "rtk "? │──────── Yes → return (no rewrite)
              └──────────────────────────────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │  Binary integrity check passed?   │──────── No → STATIC mode for this call
              └──────────────────────────────────┘
              (version ≥ min, binary exists,      │
               not corrupted)                     │
                               │
                               ▼
              ┌──────────────────────────────────┐
              │  Latency gate: p95 ≤ 15ms?        │
              └────────────────┬─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              LIVE subprocess         STATIC pattern match
              (rtk rewrite)           (in-process prefix list)
                    │                     │
                    ▼                     ▼
              ┌──────────────┐      ┌──────────────┐
              │ stdout       │      │ Match found? │
              │ non-empty?   │      └──────┬───────┘
              └──────┬───────┘             │
              ┌──────┴──────┐      ┌───────┴───────┐
              ▼             ▼      ▼               ▼
         Use as        Fall to   Return          Return
         rewritten     STATIC   (rewritten)   (no rewrite)
              │
              ▼
       ┌──────────────────┐
       │ Write RTK audit   │
       │ log entry (§6)    │
       └──────────────────┘
```

### 3.3 Default mechanism: static pattern match

If the latency gate disallows live subprocess (the expected default), the plugin uses a hardcoded list of command prefixes that RTK is known to optimise. This adds **zero** subprocess overhead — pure in-process string matching.

The static list is derived from `rtk --help` subcommands (as of rtk v0.40.0) and validated against `rtk gain --history` for the actual deployment:

```
ls, tree, git, gh, glab, aws, psql, pnpm, find, diff, grep,
wc, docker, kubectl, curl, wget, cargo, npm, npx, tsc, jest,
vitest, playwright, prisma, next, dotnet, go, pip, ruff,
pytest, mypy, rubocop, rspec, rake, gradlew, golangci-lint,
gt, err, test, json, deps, env, log, summary, read
```

**Special mapping:** `cat` → `rtk read` (not `rtk cat`). This is the only known non-identity mapping and must be encoded explicitly.

**Excluded meta-commands** (RTK's own subcommands, not optimisable tools): `init`, `gain`, `config`, `discover`, `session`, `telemetry`, `learn`, `run`, `proxy`, `pipe`, `trust`, `untrust`, `verify`, `hook`, `hook-audit`, `rewrite`, `cc-economics`, `smart`.

**Static list limitations (explicitly documented, not silently ignored):**
- Does not handle chained commands (`&&`, `;`, `|`) — only the first segment is checked
- Does not handle subshells (`$(...)`, backticks)
- Does not handle redirects or heredocs
- Does not handle the `cat` / `rtk read` identity mapping
- May be stale if RTK adds new optimisable commands
- **Does handle** single simple commands like `git status`, `ls -la`, `grep -rn 'foo' src/`

### 3.4 Optional mechanism: live subprocess (if latency gate permits)

If p95 ≤ 15ms, the plugin may call `rtk rewrite <command>` as a subprocess. RTK ships this dedicated subcommand for hook-based rewriting:

| Input | stdout | Exit code | Meaning |
|---|---|---|---|
| `git status` | `rtk git status` | 3 | Supported → use stdout as rewritten command |
| `echo hello` | *(empty)* | 1 | Not supported → do not rewrite |
| `cargo build && cargo test` | `rtk cargo build && rtk cargo test` | 3 | Supported (chained) |
| `grep foo \| head -5` | `rtk grep foo \| head -5` | 3 | Supported (pipe) |
| `rtk git status` | `rtk git status` | 3 | Already rewritten → passthrough |

**Important:** The exit code 3 is intentional from RTK. The authoritative signal for "supported" is **non-empty stdout**, not exit code.

**Per-call timeout:** 100ms (not 1s as in the original design). If the subprocess does not return within 100ms, the plugin falls through to static fallback for that call. This prevents a slow RTK binary from delaying agent bash commands.

**Edge case handling:**

| Input | After rewrite | Behaviour |
|---|---|---|
| `git status` | `rtk git status` | Rewrite |
| `ls -la` | `rtk ls -la` | Rewrite |
| `cat file.txt` | `rtk read file.txt` | Non-identity mapping |
| `grep -rn 'foo' src/` | `rtk grep -rn 'foo' src/` | Rewrite |
| `rtk git status` | *(unchanged)* | Loop guard |
| `cargo build && git status` | `cargo build && rtk git status` | Partial chain |
| `grep foo \| head -5` | `rtk grep foo \| head -5` | Pipe rewrite |
| `echo hello` | *(unchanged)* | Not supported |
| `export FOO=bar` | *(unchanged)* | Not supported |
| `sudo git status` | *(unchanged)* | sudo-prefixed not rewritten |
| *(empty string)* | *(unchanged)* | No-op |

---

## 4. Infinite-Loop Prevention

### 4.1 The hazard

After `output.args.command` is rewritten from `git status` to `rtk git status`, OpenCode executes the command via bash. The `tool.execute.before` hook fires for every bash call, including rewritten ones. Without a guard, the plugin would see `rtk git status` and attempt to rewrite it again, producing `rtk rtk git status`, then `rtk rtk rtk git status`, ad infinitum.

### 4.2 Primary guard (structural, mandatory)

The very first action after confirming `tool === "bash"` is:

```typescript
"tool.execute.before": async (input, output) => {
  if (input.tool !== "bash") return;
  const command = (output.args?.command as string) ?? "";
  if (!command) return;

  // ---- INFINITE LOOP GUARD ----
  // Structural early return: before any I/O, before any classification.
  // This is the FIRST logic check after the tool filter.
  if (command.startsWith("rtk ")) return;
  if (command.trim() === "rtk") return;
  // ---- END GUARD ----

  // ... rest of rewrite logic
}
```

This is **structural**, not stateful: it relies on the idempotency of the rewrite. Once a command begins with `rtk `, every subsequent firing sees that prefix and bails. No counters, no shared state, no cross-invocation tracking.

### 4.3 What the guard must handle

| Scenario | Command example | Guard catches? |
|---|---|---|
| First invocation, non-rtk | `git status` | No — passes through (correct) |
| After rewrite, re-entry | `rtk git status` | Yes — `startsWith("rtk ")` |
| Bare rtk | `rtk` | Yes — `trim() === "rtk"` |
| Double space after rtk | `rtk  git status` | Yes — starts with `rtk ` |
| rtk as part of larger word | `rtk-build` | No — correct, not an RTK command |
| Uppercase RTK | `RTK git status` | No — but bash is case-sensitive; this never occurs |

### 4.4 What v1 explicitly does NOT do for loop safety

No stateful watchdog, no bounded rewrite counter, no cross-call tracking. The structural guard by construction prevents recursive wrapping. A stateful watchdog would add complexity (reentrancy concerns, memory leaks from accumulating command history) with zero marginal benefit. If a future bug bypasses the prefix check (e.g., a rewrite that drops the space after `rtk`), a stateful guard would not help anyway — it would see two different command strings. The structural guard is the correct and complete solution.

---

## 5. Binary Integrity, Opt-Out, and Execution Safety

### 5.1 Version/integrity check for the rtk binary

Before any rewrite attempt, the plugin must confirm the `rtk` binary is present and at a minimum viable version.

**Check procedure (runs once at plugin init, then once every 200 calls):**

1. **Binary existence:** Attempt `Bun.spawnSync(["rtk", "--version"], { encoding: "utf-8" })`. If the spawn fails (ENOENT, EACCES), mark binary as unavailable for the session.

2. **Version parsing:** Parse the stdout for a semver string (e.g., `rtk 0.40.0`). Extract major.minor.patch.

3. **Version floor:** Require `rtk >= 0.38.0`. This is the minimum version where `rtk rewrite` and `rtk hook-audit` are known stable. If version < 0.38.0 or unparseable:
   - Log warning to `/tmp/rtk-guard.log`
   - Fall to static pattern match mode
   - Do not attempt live subprocess

4. **Graceful degradation:** If the binary is missing, corrupted, or below version floor, the plugin operates in static-fallback mode. No error reaches the agent. No bash call is blocked.

### 5.2 Safety boundaries: subshells, -exec, redirects, heredocs

**v1 explicitly rejects rewriting on any command containing these constructs.** This matches RTK's own conservatism on unattestable shell constructs. The plugin does not parse shell syntax — it uses simple string detection to refuse rewriting when uncertainty exists.

**Refused constructs (command contains any of these → no rewrite):**

| Construct | Example | Detection | Rationale |
|---|---|---|---|
| Subshell | `$(git status)` | Contains `$(` | Nested command substitution alters shell state; RTK cannot attest the output |
| Backtick | `` `git status` `` | Contains `` ` `` | Same as subshell, older syntax |
| Redirect | `git status > file.txt` | Contains `>` (outside quotes) | Output redirection changes what RTK caches |
| Heredoc | `cat << EOF` | Contains `<<` | Multi-line input not attestable |
| Process substitution | `diff <(git log)` | Contains `<(` or `>(` | Subshell-like behaviour |
| `sudo` prefix | `sudo git status` | Starts with `sudo ` | Privilege escalation not attestable |
| `env` prefix | `env VAR=val git status` | Starts with `env ` | Environment mutation not attestable |

**Detection approach:** Simple substring matching on the raw command string, with awareness of quoted regions to avoid false positives (e.g., `echo '$('` should not trigger a skip). A lightweight quote-aware scanner is used: track whether inside single-quote, double-quote, or unquoted, and only match the constructs when outside quotes.

**If any refused construct is detected, the plugin does NOT rewrite.** The command passes through unchanged. This is conservative by design — a missed optimisation is acceptable; a corrupted command is not.

### 5.3 Agent opt-out mechanism

The plugin honors an opt-out mechanism for commands that need raw, un-rewritten output.

**Mechanism:** If the env var `RTK_DISABLED=1` is set in the bash command's environment, the plugin skips all rewrite logic and passes the command through unchanged.

**Detection:** At the top of the hook handler (before the loop guard), check:
- `process.env["RTK_DISABLED"] === "1"` — global opt-out for the entire session
- Command starts with `RTK_DISABLED=1 ` — per-command opt-out via env prefix

**Examples:**

```bash
# Global opt-out (set once, affects all subsequent commands)
export RTK_DISABLED=1
git status          # NOT rewritten

# Per-command opt-out (one-shot)
RTK_DISABLED=1 git diff   # NOT rewritten
```

**Use cases for opt-out:**
- Commands whose output must not be cached (secrets, ephemeral data)
- Commands whose output must be fully faithful (no RTK compression)
- Debugging the plugin itself (compare raw vs. rewritten output)
- Piping to downstream parsers that expect exact output format

**Logging:** When a command is skipped due to opt-out, an audit entry is written with `skip:opt_out`.

### 5.4 Plugin execution order with crosslink-guard.ts

Both `rtk-guard.ts` and `crosslink-guard.ts` register `tool.execute.before` hooks on bash calls. They operate on the same `output.args.command` field. Execution order matters.

**Ordering:** OpenCode fires hooks in alphabetical plugin file order (this is the observed behaviour, not an API guarantee). Since `c` < `r`, `crosslink-guard.ts` fires before `rtk-guard.ts` when both are present in `.opencode/plugins/`.

**The problem:** If `rtk-guard.ts` runs first and rewrites `git push` → `rtk git push`, then `crosslink-guard.ts` sees `rtk git push`. Crosslink's `normalizeGitCommand()` checks whether the command starts with `git push` — it does not (it starts with `rtk git push`). The result is that crosslink-guard misses the blocked git command.

**Resolution strategy (chosen):** Modify `crosslink-guard.ts`'s `normalizeGitCommand()` to strip a leading `rtk ` prefix before performing git command matching. This is a targeted, one-line change that makes crosslink-guard `rtk`-aware without any circular dependency or layering violation. `rtk-guard.ts` remains entirely unaware of crosslink — it does not import or reference crosslink-guard's rules.

**Implementation in crosslink-guard.ts:**
```typescript
function normalizeGitCommand(command: string): string {
  let normalized = command.trim();
  // Strip rtk prefix if present (for interoperability with rtk-guard.ts)
  if (normalized.startsWith("rtk ")) {
    normalized = normalized.slice(4).trim();
  }
  // Remove global git flags like -C, --git-dir, --work-tree
  // ... existing logic ...
}
```

**Alternative considered and rejected:** Make `rtk-guard.ts` aware of crosslink's blocklist to avoid rewriting blocked commands. Rejected because it violates the abstraction boundary — `rtk-guard.ts` should not embed knowledge of another plugin's policy rules. The crosslink-side modification is cleaner and matches the existing pattern where `normalizeGitCommand` already strips git global flags.

**Edge case:** If crosslink renames or removes `normalizeGitCommand`, the `rtk ` strip could be lost. Mitigation: add a crosslink-guard test case that verifies `rtk git push` is detected as a push. Document the dependency in both plugins' reference sections.

---

## 6. RTK-Compliant Audit-Log Entry Writing

### 6.1 The requirement

RTK's hook-audit mechanism writes pipe-delimited entries to `~/.local/share/rtk/hook-audit.log`. These entries allow `rtk hook-audit` to measure rewrite activity. Without this, the verification protocol (§8) has no data source.

The canonical format (source: `src/hooks/hook_cmd.rs::audit_log_inner()`):

```
2026-02-16T14:30:01Z | rewrite | git status | rtk git status
```

### 6.2 Format specification

Each entry is a single line with four pipe-delimited fields:

```
<ISO_timestamp> | <action> | <original_command> | <result_command>
```

Where:
- **ISO_timestamp**: UTC ISO 8601 with seconds precision, e.g., `2026-07-13T14:30:01Z`
- **action**: One of `rewrite`, `skip:no_match`, `skip:already_rtk`, `skip:opt_out`, `skip:unsafe_construct`, `skip:binary_unavailable`, `skip:version_below_floor`
- **original_command**: The original bash command (truncated to 500 chars to avoid log bloat; secrets are the user's responsibility)
- **result_command**: The rewritten command (for `rewrite` actions), or the original command (for `skip:*` actions)

### 6.3 Log file path and permissions

**Path:** `~/.local/share/rtk/hook-audit.log`

**Resolution:** Resolve the path by:
1. `$HOME` env var → `$HOME/.local/share/rtk/hook-audit.log`
2. If `$HOME` is unset, fall back to `geteuid()` → `getpwuid()` lookup
3. If all lookups fail, skip audit logging (no crash)

**Permissions:** The file may not exist yet (RTK's own hook creates it on first write). The plugin must:
- Attempt to open the file in append mode; if the directory does not exist, attempt `mkdir -p ~/.local/share/rtk/` first
- If mkdir or open fails, skip audit logging silently
- Never create the file with world-writable permissions (use `O_APPEND` / `O_CREAT` with `0o644` or equivalent)

### 6.4 Condition: write only when RTK_HOOK_AUDIT=1

Audit entries are written **only** when `RTK_HOOK_AUDIT=1` is set in the process environment. This matches RTK's own behaviour — audit logging is opt-in to avoid unnecessary I/O for users who do not use `rtk hook-audit`.

**Detection:** `process.env["RTK_HOOK_AUDIT"] === "1"`

**Behaviour when not set:** Skip all audit-log I/O. No log entries, no file creation, no directory creation.

### 6.5 Log entry table (all actions)

| Scenario | Action field | Example entry |
|---|---|---|
| Command rewritten via static match | `rewrite` | `2026-07-13T14:30:01Z \| rewrite \| git status \| rtk git status` |
| Command rewritten via live subprocess | `rewrite` | `2026-07-13T14:30:02Z \| rewrite \| ls -la \| rtk ls -la` |
| Command not in static list | `skip:no_match` | `2026-07-13T14:30:03Z \| skip:no_match \| make build \| make build` |
| Command already starts with `rtk ` | `skip:already_rtk` | `2026-07-13T14:30:04Z \| skip:already_rtk \| rtk git diff \| rtk git diff` |
| Command opted out via `RTK_DISABLED=1` | `skip:opt_out` | `2026-07-13T14:30:05Z \| skip:opt_out \| git diff \| git diff` |
| Command contains unsafe construct | `skip:unsafe_construct` | `2026-07-13T14:30:06Z \| skip:unsafe_construct \| echo $(git log) \| echo $(git log)` |
| RTK binary not found | `skip:binary_unavailable` | `2026-07-13T14:30:07Z \| skip:binary_unavailable \| git status \| git status` |
| RTK binary below version floor | `skip:version_below_floor` | `2026-07-13T14:30:08Z \| skip:version_below_floor \| git status \| git status` |

### 6.6 Logging best practices

- **Append-only:** Open the file in append mode (`O_APPEND`). Never truncate or overwrite.
- **No rotation:** The plugin does not rotate the log. RTK itself does not rotate it. The user may add rotation if desired.
- **No locking:** Multiple concurrent hook calls may append simultaneously. On Linux, `O_APPEND` with `write()` is atomic for small writes (< PIPE_BUF, typically 4096 bytes). Log entries are well under this limit. Risk of interleaved lines is negligible.
- **No throw:** Wrap the entire write in try/catch. If the write fails (disk full, permissions changed), the plugin continues silently.
- **Secrets policy:** Truncate the original command to 500 characters. If a command contains secrets beyond that length, they are truncated. This is consistent with RTK's own audit-log truncation.

---

## 7. Validity / Output-Fidelity Constraints

### 7.1 The requirement

Before broad deployment, the plugin must confirm that rewritten commands produce output that is functionally equivalent (from the agent's perspective) to the un-rewritten version. RTK compresses output; for most commands this is transparent, but some cases exist where exact output format matters.

### 7.2 Test commands (representative set for fidelity validation)

These commands must be tested with and without `rtk` prefix, comparing stdout and exit codes:

| Command | Why critical |
|---|---|
| `git status --porcelain` | Machine-parseable output; must remain parseable |
| `git diff` | Agent may read diff for code changes; must show full diff |
| `git log --oneline -5` | Agent may parse commit hashes |
| `grep -rn 'pattern' src/ --include '*.rs'` | Line numbers and file paths must be preserved |
| `ls -la` | File sizes, permissions, timestamps must be exact |
| `find . -name '*.rs' -type f` | Path list must be complete |
| `cat Cargo.toml` | File contents must be exact (no truncation) |
| `wc -l src/main.rs` | Count must be exact |
| `cargo check --message-format=json 2>&1` | JSON parseable diagnostics |
| `npm audit --json` | JSON output must be parseable |
| `docker ps --format '{{.ID}}'` | Structured output with custom format |
| `curl -s https://example.com/api` (if applicable) | Raw HTTP response must be complete |

### 7.3 Validation protocol (before broad deployment)

1. **Select candidate commands** from the optimisable set (Section 3.3) that the agent actually uses. Base this on `rtk gain --history` for the specific deployment.
2. **Run each command twice**: once without `rtk`, once with `rtk` prepended.
3. **Compare:**
   - Exit codes are identical
   - Stdout is semantically equivalent (same information content)
   - Machine-parseable output (JSON, `--porcelain`, CSV) remains syntactically valid
   - Line counts match (RTK should not drop lines, only compress individual line output)
4. **Flag failures:** If any command in the test set shows output divergence (missing lines, truncated content, altered format), that command is **removed from the optimisable set** and added to a blocklist.
5. **Document results:** Record the validation matrix in a companion document. This becomes the authoritative list of "safe to rewrite" commands for this deployment.

### 7.4 Conservative deployment strategy

**Phase 1 — Minimal set (immediate deploy):**
Start with only the most obviously safe commands: `git status`, `ls`, `tree`, `wc`, `head`, `tail`. These are read-only listing commands where RTK compression is transparent.

**Phase 2 — Expanded set (after validation):**
Add `git diff`, `git log`, `grep`, `find`, `cat`/`read`, `cargo check` (text output only), `npm` (text output only). Each addition requires validation against the fidelity protocol.

**Phase 3 — Full set (after extensive validation):**
Add all remaining commands from the static list, including JSON-emitting commands. Each is validated individually.

**Never add:** Commands whose output is fed into downstream parsers that cannot tolerate RTK's output format. This is deployment-specific and must be determined by the agent operator.

---

## 8. Verification Protocol

### 8.1 Redefined metrics (per adversarial review)

The original design's "≥20% hook-rewrite" target is retired. The 0.6% baseline came from a telemetry path distinct from `rtk gain`'s "Hook Rewritten" row, and the percentage could not be measured reliably. The revised verification uses four concrete, independently measurable metrics:

| Metric | Source | Baseline | Success threshold |
|---|---|---|---|
| **RTK session adoption %** | `rtk session` → (RTK-covered commands / total commands) | Current session's coverage | ≥ 50% of bash commands in the session are RTK-rewritten |
| **Audit-log rewrite count** | `rtk hook-audit` (requires §6 implementation and `RTK_HOOK_AUDIT=1`) | ~5 rewrites per session (baseline from Claude Code hook) | ≥ 5× baseline (25+ rewrites per session) |
| **Tokens-saved delta** | `rtk gain` → "Tokens saved" row | Current session's delta | Positive increase over baseline (no fixed target; any increase = tokens not spent) |
| **Zero double-prefix** | `grep 'rtk rtk' ~/.local/share/rtk/hook-audit.log 2>/dev/null` | Zero | Zero across all sessions; any occurrence is a loop-guard failure |

**Failure signals:**
- Session adoption % remains at or below baseline → plugin loaded but did not rewrite
- Audit-log shows zero `rewrite` entries → plugin bypassed or RTK_HOOK_AUDIT not set
- Tokens-saved delta is negative → RTK overhead exceeds savings (unlikely but measurable)
- Any `rtk rtk …` entry in audit log → loop guard failed OR guard is not structural

### 8.2 Pre-deployment: smoke test

Before committing the plugin, verify that `output.args.command` mutation works:

1. Create a test plugin at `.opencode/plugins/test-rewrite.ts` that hooks `tool.execute.before`, prepends `echo "REWRITTEN:" && ` on bash calls, and has a loop guard skipping if command already starts with `echo "REWRITTEN:"`.
2. In a test session, issue `ls` — expect output: `REWRITTEN:` followed by directory listing.
3. Verify re-entry: next bash call should NOT have double prefix.
4. If test passes, delete the test plugin. If test fails, the entire approach is invalidated — escalate.

### 8.3 Pre-deployment: latency confirmation in Bun

```typescript
// Pseudocode for timing in Bun runtime
const iterations = 100;
const times: number[] = [];
for (let i = 0; i < iterations; i++) {
  const start = Bun.nanoseconds();
  const result = Bun.spawnSync(["rtk", "rewrite", "git status"], { encoding: "utf-8" });
  const elapsed = (Bun.nanoseconds() - start) / 1_000_000; // ms
  times.push(elapsed);
}
times.sort((a, b) => a - b);
const p95 = times[Math.floor(0.95 * times.length)];
console.log(`p95 latency: ${p95}ms`);
// Threshold: if p95 > 15ms, disable live subprocess
```

### 8.4 Post-deployment: effectiveness measurement

**Before deploying:**
```bash
rtk session > /tmp/rtk-session-before-$(date +%Y%m%d).txt
rtk gain > /tmp/rtk-gain-before-$(date +%Y%m%d).txt
export RTK_HOOK_AUDIT=1   # Enable audit logging before starting session
```

**After a real work session (minimum 50 bash calls):**
```bash
rtk session > /tmp/rtk-session-after-$(date +%Y%m%d).txt
rtk gain > /tmp/rtk-gain-after-$(date +%Y%m%d).txt
rtk hook-audit 2>&1 > /tmp/rtk-hook-audit-after-$(date +%Y%m%d).txt
```

**Compare:**
- Session adoption %: `rtk session` shows coverage change
- Rewrite count: `rtk hook-audit | grep '| rewrite |' | wc -l`
- Double-prefix: `grep 'rtk rtk' ~/.local/share/rtk/hook-audit.log | wc -l` must be 0
- Tokens saved: `rtk gain` delta

### 8.5 Long-term monitoring

Weekly check:
```bash
export RTK_HOOK_AUDIT=1
# After a session:
rtk hook-audit | grep '| rewrite |' | wc -l >> /var/log/rtk-guard-rewrite-count.log
grep 'rtk rtk' ~/.local/share/rtk/hook-audit.log | wc -l  # must be 0
```

If rewrite count drops to near-zero for two consecutive checks, investigate:
- Did OpenCode update change plugin API?
- Did the plugin fail to load silently?
- Did `RTK_HOOK_AUDIT` get unset?

---

## 9. Error Handling & Failure Modes

### 9.1 Core principle: never block, never throw, never error

The plugin operates on the principle of **silent pass-through**. If anything goes wrong, the original command executes unmodified. The agent sees normal output, never an error from the plugin.

### 9.2 Failure mode matrix

| Failure mode | Detection | Behaviour | Impact |
|---|---|---|---|
| **RTK binary not found** | `spawnSync("rtk", ["--version"])` fails | Enable static-fallback mode; log warning; write `skip:binary_unavailable` audit entry | Static list may be stale; ~5% of possible rewrites missed |
| **RTK binary below version floor** | `rtk --version` returns < 0.38.0 | Enable static-fallback mode; log warning; write `skip:version_below_floor` audit entry | Same as above |
| **Subprocess timeout** | `spawnSync` with 100ms timeout expires | Fall through to static fallback for this call; log | Single command not rewritten; no cascade |
| **Empty command string** | `!command` check | Return immediately | None |
| **Subshell/redirect/heredoc detected** | Quote-aware scan finds `$(`, `` ` ``, `>`, `<<`, etc. | Return immediately; write `skip:unsafe_construct` audit entry | Missed optimisation; no corruption |
| **`output.args` undefined** | `?.` optional chaining | Return immediately | Plugin state error — first invocation safety |
| **Spawn failure (OOM, no mem)** | `spawnSync` throws | Wrap in try/catch, fall through | Single command not rewritten |
| **Opt-out active** | `RTK_DISABLED=1` detected | Return immediately; write `skip:opt_out` audit entry | Expected behaviour |
| **OpenCode API version mismatch** | TypeScript compilation error at load time | OpenCode reports plugin load failure; bash calls proceed without rewriting | Zero rewrites until user fixes the plugin |
| **Audit log write failure** | File cannot be opened or written | Catch silently; no audit entry for this call | One missing audit entry; no functional impact |

### 9.3 Logging (plugin log, not audit log)

The plugin logs operational events to `/tmp/rtk-guard.log` (append-only, never rotates). Log format:

```
2026-07-13T10:00:00.000Z [rtk-guard] Plugin loaded, mode=static, reason=binary_not_found
2026-07-13T10:00:00.012Z [rtk-guard] REWRITE: "git status" → "rtk git status"
2026-07-13T10:00:00.019Z [rtk-guard] SKIP (unsafe construct): "echo $(git log)"
2026-07-13T10:00:00.025Z [rtk-guard] SKIP (loop guard): "rtk git status"
2026-07-13T10:00:00.031Z [rtk-guard] SKIP (opt-out): "git diff"
2026-07-13T10:00:00.037Z [rtk-guard] SKIP (no match): "make build"
2026-07-13T10:00:00.043Z [rtk-guard] SKIP (binary unavailable, static fallback): "find ."
```

Logging is best-effort (never throws). If the log file cannot be written, the plugin continues silently. Commands are truncated to 200 characters in log entries to avoid exposing secrets at full length.

---

## 10. Implementation Plan

### Phase 1: Validate (before writing any production code)

| Step | Action | Verification |
|---|---|---|
| 1.1 | Create smoke test plugin `.opencode/plugins/test-rewrite.ts` | `ls` → output shows `REWRITTEN:` prefix |
| 1.2 | Loop guard test: two sequential bash calls | No double `REWRITTEN:` prefix on second call |
| 1.3 | Measure `rtk rewrite` latency in Bun runtime (100 iterations, p95) | p95 ≤ 15ms for live subprocess consideration |
| 1.4 | Validate output fidelity on test command set (§7.2) | All commands produce equivalent output |
| 1.5 | Confirm audit-log path exists and is writable | `echo test >> ~/.local/share/rtk/hook-audit.log` succeeds |
| **Gate** | All 5 steps pass | Proceed to Phase 2 |

### Phase 2: Scaffold

| Step | Action | Artifact |
|---|---|---|
| 2.1 | Create `.opencode/plugins/rtk-guard.ts` | Plugin file with correct import, factory, export |
| 2.2 | Implement binary path resolution + version check (§5.1) | `resolveBinary()` returns `{ path, version, ok }` |
| 2.3 | Implement latency gate and mode selection (§3.1) | `chooseMode()` returns `"live"` or `"static"` |
| 2.4 | Implement static command list and `staticRewrite()` | Map of prefix → rewrite, with `cat`→`rtk read` special case |
| 2.5 | Implement unsafe-construct scanner (§5.2) | `hasUnsafeConstruct(command): boolean` |
| 2.6 | Implement opt-out check (§5.3) | `isOptedOut(command): boolean` |
| 2.7 | Wire `tool.execute.before` handler with loop guard, all checks, and logging | Complete handler body |

### Phase 3: Audit-log integration

| Step | Action | Verification |
|---|---|---|
| 3.1 | Implement audit-log writer for all action types (§6) | Correct pipe-delimited format for each action |
| 3.2 | Test with `RTK_HOOK_AUDIT=1` set | Entries appear in `~/.local/share/rtk/hook-audit.log` |
| 3.3 | Test with `RTK_HOOK_AUDIT` unset | No file created, no I/O |
| 3.4 | Test directory-not-exists case | Directory created automatically |
| 3.5 | Test concurrent writes (multiple hook invocations) | No interleaved lines |

### Phase 4: Edge cases & hardening

| Step | Action | Test case |
|---|---|---|
| 4.1 | Test with RTK binary missing → static fallback | `RTK_BINARY=/nonexistent` in env |
| 4.2 | Test with RTK binary below version floor | Replace with old `rtk` binary |
| 4.3 | Test with empty command string | `output.args.command = ""` |
| 4.4 | Test with `output.args` undefined | Remove `command` from args |
| 4.5 | Test subprocess timeout (live mode only) | Insert `sleep 0.2` in RTK binary path |
| 4.6 | Test opt-out with env var and with command prefix | Both forms skip rewrite |
| 4.7 | Test unsafe constructs: `$(...)`, backtick, `>`, `<<`, `<(` | All skip rewrite |
| 4.8 | Test rapid sequential calls (100 in a loop) with audit logging | No crashes, no resource leak, all audit entries correct |

### Phase 5: Crosslink interop

| Step | Action | Verification |
|---|---|---|
| 5.1 | Modify `crosslink-guard.ts` `normalizeGitCommand()` to strip `rtk ` prefix | `rtk git push` detected as blocked git push |
| 5.2 | Test with rtk-guard.ts and crosslink-guard.ts both active | Blocked git commands still blocked; rewritable commands still rewritten |
| 5.3 | Test edge case: `rtk git push` with no crosslink-guard active | `rtk git push` passes through (correct — no plugin to block it) |

### Phase 6: Production verification

| Step | Action | Duration |
|---|---|---|
| 6.1 | Run pre-deployment latency confirmation (Phase 1.3) | 5 minutes |
| 6.2 | Set `RTK_HOOK_AUDIT=1` | 1 minute |
| 6.3 | Run fidelity validation on Phase 1 command set (§7.2) | 15 minutes |
| 6.4 | Load the plugin and run a real work session (Phase 1 minimal set only) | 1+ hours |
| 6.5 | Compare metrics against success thresholds (§8.1) | 5 minutes |
| 6.6 | If successful, expand to Phase 2 command set; repeat validation | Iterative |
| 6.7 | Remove test plugin, commit | 5 minutes |

---

## 11. Risks & Unknowns

### R1: `output.args.command` mutation not validated at runtime

**Severity:** Critical (blocks entire approach). **Probability:** Low (API type defines `output.args` as `any`, mutable). **Mitigation:** Phase 1 smoke test proves or disproves this before any production code.

### R2: RTK `hook-audit` log format changes

**Severity:** Medium (audit trail breaks silently). **Probability:** Low (RTK is mature at v0.40.0; breaking this format would break their own tooling). **Mitigation:** The format is simple pipe-delimited; if RTK changes it, the plugin's audit entries become unparseable by `rtk hook-audit` but the plugin continues to function. The verification protocol would fall back to `rtk session` and `rtk gain` metrics.

### R3: Subprocess overhead is higher in Bun than in bash

**Severity:** Low (only performance, not correctness). **Probability:** Medium (Bun's `spawnSync` may have different overhead than Node.js or bash `time`). **Mitigation:** The latency gate (p95 ≤ 15ms) is measured in Bun, not in bash. If Bun overhead pushes p95 over threshold, live subprocess is disabled and static mode is used.

### R4: Static list drift

**Severity:** Medium (missed optimization). **Probability:** Medium (RTK adds new optimisable commands over time). **Mitigation:** Periodically regenerate from `rtk --help` and `rtk gain --history`. The live subprocess mode, if enabled, self-corrects by delegating to RTK's own rewrite logic.

### R5: Unsafe-construct scanner has false positives

**Severity:** Low (missed optimization, not corruption). **Probability:** Low (the constructs detected are genuinely unsafe for RTK rewriting; false positives skip a rewrite but never corrupt output). **Mitigation:** The scanner is trivially correct for the constructs it detects. If too conservative, the set of detected constructs can be narrowed.

### R6: Crosslink-guard modification not merged

**Severity:** Medium (`rtk git push` bypasses crosslink guard). **Probability:** Low (the modification is a one-line addition to `normalizeGitCommand`). **Mitigation:** The plugin works without the crosslink modification; the only symptom is that `rtk`-prefixed blocked git commands (push, merge, etc.) pass through. The agent could still explicitly write `git push` (without `rtk`) and crosslink catches it. The modification is a defense-in-depth improvement, not a correctness requirement.

### R7: RTK compression drops agent-critical output

**Severity:** Medium (agent acts on incomplete information). **Probability:** Low (RTK is designed for LLM consumption and preserves information content). **Mitigation:** The fidelity validation protocol (§7) catches this before broad deployment. The conservative deployment strategy (start small, expand only after validation) limits exposure.

### R8: Audit log disk-full condition

**Severity:** Low (plugin continues silently). **Probability:** Very low (audit entries are ~100 bytes each; even 10,000 entries = 1MB). **Mitigation:** The audit write is wrapped in try/catch. If write fails, the plugin continues. The user is responsible for log management.

---

## 12. Design Decisions Record

| # | Decision | Rationale | Alternatives Considered |
|---|---|---|---|
| D1 | Static pattern match is the **default** | Zero subprocess overhead; p95 latency gate may not be met in Bun runtime | Live subprocess as default (rejected — risk of cumulative latency) |
| D2 | Latency gate threshold is p95 ≤ 15ms | Consistent with original design's latency budget; measured in Bun, not bash | Hardcoded "always live" (rejected — no measurement) |
| D3 | Structural `startsWith("rtk ")` loop guard | Stateless, simple, covers all re-entry scenarios | Stateful rewrite counter (rejected — unnecessary complexity, memory leak risk) |
| D4 | Audit log writes to RTK's canonical path with pipe-delimited format | Enables `rtk hook-audit` to measure rewrites | Custom audit log (rejected — RTK tooling would not see it) |
| D5 | Crosslink-guard modified, not rtk-guard | Maintains abstraction boundary; rtk-guard stays unaware of crosslink | rtk-guard embeds crosslink blocklist (rejected — layering violation) |
| D6 | Unsafe constructs detected by simple quote-aware scanner | Conservative; avoids parsing full shell grammar | Full shell AST parse (rejected — overengineered for v1) |
| D7 | Version floor at rtk ≥ 0.38.0 | Ensures `rtk rewrite` and `rtk hook-audit` are stable | No version check (rejected — risk of silent breakage with older RTK) |
| D8 | Opt-out via `RTK_DISABLED=1` env var | Simple, matches RTK's own env-var patterns | Special comment syntax (rejected — fragile); separate config file (rejected — overengineered for v1) |
| D9 | Verification metrics: session %, audit count, tokens delta, zero double-prefix | Concrete, independently measurable, sourced from RTK's own tooling | "Hook-rewrite %" from `rtk gain` (retired — metric not reliably reported) |
| D10 | Conservative deployment: start with 5 safe commands, expand iteratively | Limits blast radius of output-fidelity issues | Full deploy (rejected — unvalidated risk) |

---

## Appendix A: Static Rewrite Map

### Identity mappings (prefix → `rtk <prefix>`)

```
ls, tree, git, gh, glab, aws, psql, pnpm, find, diff, grep,
wc, docker, kubectl, curl, wget, cargo, npm, npx, tsc, jest,
vitest, playwright, prisma, next, dotnet, go, pip, ruff,
pytest, mypy, rubocop, rspec, rake, gradlew, golangci-lint,
gt, err, test, json, deps, env, log, summary, read
```

### Non-identity mapping

| Original prefix | RTK rewrite |
|---|---|
| `cat ` | `rtk read ` |

### Excluded meta-commands (not optimisable)

`init`, `gain`, `config`, `discover`, `session`, `telemetry`, `learn`, `run`, `proxy`, `pipe`, `trust`, `untrust`, `verify`, `hook`, `hook-audit`, `rewrite`, `cc-economics`, `smart`

### Code representation

```typescript
const RTK_STATIC_REWRITE_MAP: Record<string, string> = {
  "cat ": "rtk read ",    // Non-identity mapping
};

const RTK_SUPPORTED_PREFIXES: string[] = [
  "ls ", "tree ", "git ", "gh ", "glab ", "aws ", "psql ",
  "pnpm ", "find ", "diff ", "grep ", "wc ", "docker ", "kubectl ",
  "curl ", "wget ", "cargo ", "npm ", "npx ", "tsc ",
  "jest ", "vitest ", "playwright ", "prisma ", "next ",
  "dotnet ", "go ", "pip ", "ruff ", "pytest ", "mypy ",
  "rubocop ", "rspec ", "rake ", "gradlew ", "golangci-lint ", "gt ",
  "err ", "test ", "json ", "deps ", "env ", "log ", "summary ",
  "read ",
];
```

---

## Appendix B: Output-Fidelity Test Matrix

This matrix must be filled during Phase 1.4 validation before broad deployment.

| Command | Raw exit | `rtk` exit | Raw stdout | `rtk` stdout | Parseable? | Verdict |
|---|---|---|---|---|---|---|
| `git status --porcelain` | | | | | | |
| `git diff` | | | | | | |
| `git log --oneline -5` | | | | | | |
| `grep -rn 'fn main' src/` | | | | | | |
| `ls -la` | | | | | | |
| `find . -name '*.rs' -type f` | | | | | | |
| `cat Cargo.toml` | | | | | | |
| `wc -l src/main.rs` | | | | | | |

Each row compares raw vs. RTK-rewritten. If any row shows output divergence that changes semantic content (not just formatting/compression), the command is removed from the optimisable set.

---

## Appendix C: Crosslink Interop Detail

### Problem statement

When both `rtk-guard.ts` and `crosslink-guard.ts` are active, plugin execution order determines whether crosslink's git-command blocking works correctly.

### Execution order

OpenCode fires `tool.execute.before` hooks in alphabetical plugin filename order. Since `crosslink-guard.ts` (c) sorts before `rtk-guard.ts` (r), crosslink fires **first**.

### Flow with crosslink first (current ordering)

```
1. Agent issues: git push
2. crosslink-guard.ts fires:
   - normalizeGitCommand("git push") → "git push"
   - "git push" is in blocked set → THROW (blocked)
3. rtk-guard.ts never fires (crosslink already threw)
```

**Result: Correct.** Crosslink blocks the command before RTK can rewrite it.

### Flow with rtk first (hypothetical, if ordering changes)

```
1. Agent issues: git push
2. rtk-guard.ts fires first:
   - Rewrites to: "rtk git push"
   - Writes audit entry
   - Returns
3. crosslink-guard.ts fires:
   - normalizeGitCommand("rtk git push") → currently checks startsWith("git push") → FALSE
   - Command passes through unblocked ⚠️
```

**Result: Incorrect.** The blocked `git push` bypasses crosslink.

### Resolution

Add `rtk ` prefix stripping to `crosslink-guard.ts`'s `normalizeGitCommand()`:

```typescript
function normalizeGitCommand(command: string): string {
  let normalized = command.trim();
  // Strip rtk prefix if present (for interoperability with rtk-guard.ts)
  if (normalized.startsWith("rtk ")) {
    normalized = normalized.slice(4).trimStart();
  }
  // Continue with existing logic...
}
```

This is a one-line change to crosslink-guard, not to rtk-guard. The change must be accompanied by a test case verifying `rtk git push` is detected as a push.

### Alternative: not modifying crosslink-guard

If the crosslink modification is not made, the practical consequence is that `rtk git push`, `rtk git merge`, `rtk git rebase`, etc. would bypass crosslink. Since the agent would need to explicitly include `rtk` in its command to trigger this (rtk-guard rewrites `git push` → `rtk git push`, but crosslink-guard fires first and blocks it), the bypass only happens if the agent explicitly writes `rtk git push`. This is a low-probability scenario. However, making the modification is still recommended for correctness.

---

## Appendix D: Decision Flow Diagram (Complete)

```
                      ┌─────────────────────┐
                      │  Bash call received   │
                      └──────────┬───────────┘
                                 │
                                 ▼
               ┌──────────────────────────────────┐
               │  tool lowercased === "bash"?       │
               └────────────────┬─────────────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
                  Continue              Return
                                        (not bash)
                     │
                     ▼
               ┌──────────────────────────────────┐
               │  RTK_DISABLED=1?                  │──────── Yes → Return (no rewrite)
               └────────────────┬─────────────────┘
                                │
                                ▼
               ┌──────────────────────────────────────┐
               │  Command starts with "rtk "?         │
               └────────────────┬─────────────────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
                  Return                Continue
               (loop guard)               │
                                          ▼
               ┌──────────────────────────────────────┐
               │  Has unsafe construct (§5.2)?          │
               │  $(...)  `...`  >  <<  <( )  sudo env  │
               └────────────────┬─────────────────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
                  Return                Continue
               (unsafe)                   │
                                          ▼
               ┌──────────────────────────────────────┐
               │  Binary integrity check (§5.1)        │
               │  Exists and version ≥ 0.38.0?          │
               └────────────────┬─────────────────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
               Check latency           STATIC mode
               gate (§3.1)             (no binary)
                     │                     │
                     ▼                     ▼
               ┌──────────────┐     ┌──────────────┐
               │ p95 ≤ 15ms? │     │ Match found  │
               └──────┬──────┘     │ in prefix    │
                      │            │ list?        │
               ┌──────┴──────┐     └──────┬───────┘
               ▼             ▼            │
           LIVE sub     STATIC      ┌─────┴─────┐
         (rtk rewrite)  (fallback)  ▼           ▼
               │             │   Return      Return
               │             │  (rewrite)  (no rewrite)
               ▼             │
         ┌──────────────┐    │
         │ stdout      │    │
         │ non-empty?  │    │
         └──────┬──────┘    │
             ┌──┴──┐        │
             ▼     ▼        │
         Rewrite  Fall      │
         (use     to        │
         stdout)  STATIC    │
             │     │        │
             └──┬──┘        │
                │           │
                ▼           ▼
         ┌──────────────────────┐
         │ Write RTK audit entry│
         │ (§6)                 │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ output.args.command  │
         │ = rewritten          │
         └──────────┬───────────┘
                    │
                    ▼
                 Return
```

---

## Appendix E: Changelog

| Date | Author | Change |
|---|---|---|
| 2026-07-13 | Independent verification agent | Initial design proposal (Design B) |
| 2026-07-13 | Independent verification agent | Revised per adversarial review: added audit-log integration (§6), redefined metrics (§8.1), crosslink execution order (§5.4), hard latency gate (§3.1), output fidelity validation (§7), opt-out (§5.3), subshell rejection (§5.2), binary integrity check (§5.1) |
