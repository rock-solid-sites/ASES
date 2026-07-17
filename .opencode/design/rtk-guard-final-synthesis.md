# Design: `rtk-guard.ts` — Final Synthesis

**Status:** Canonical — to be implemented
**Date:** 2026-07-13
**Source:** Synthesis of four independent designs + two adversarial reviews
**Target:** `.opencode/plugins/rtk-guard.ts`

---

## Overview

`rtk-guard.ts` is an OpenCode plugin that transparently rewrites bash tool calls through RTK's CLI proxy, restoring the token-saving transparent rewriting that Claude Code's PreToolUse hook provides but OpenCode cannot run. It hooks `tool.execute.before`, intercepts bash calls, and mutates `output.args.command` to prepend `rtk` where appropriate.

**Core safety properties:**
- Never blocks or errors a bash call (fail-open)
- Defaults to no-op if anything is wrong (binary missing, degraded, too slow)
- Rewrites only validated commands (v1 conservative allowlist)
- Structural loop guard prevents double-wrapping

---

## Architecture

### Hook registration

```typescript
import type { Plugin } from "@opencode-ai/plugin";

const rtkGuardPlugin: Plugin = async () => ({
  "tool.execute.before": async (input, output) => {
    // Hook body
  },
});

export default rtkGuardPlugin;
```

Auto-discovered from `.opencode/plugins/rtk-guard.ts`. No `opencode.json` changes.

### Decision pipeline (in order)

```
bash call received
  │
  ├── tool !== "bash" → return
  │
  ├── Loop guard: command.startsWith("rtk ") or "rtk:" or exactly "rtk" → return
  │
  ├── Opt-out: RTK_DISABLED=1 env or "RTK_DISABLED=1 " prefix → strip & pass through
  │
  ├── Unattestable construct? ($(...), backticks, redirects, heredocs) → return
  │
  ├── Binary gate failed? → return (no-op mode)
  │
  ├── Latency gate exceeded? → return (no-op mode)
  │
  ├── rtk rewrite <command> (100ms timeout)
  │
  ├── stdout empty? → return (not supported)
  │
  ├── In validated allowlist? → no → return (not yet validated)
  │
  ├── Write audit entry (if RTK_HOOK_AUDIT=1)
  │
  └── output.args.command = rewritten
```

### Binary gate (runs once at plugin load)

1. Resolve path: `RTK_BINARY` env → `which rtk` → `/home/claude-code/.cargo/bin/rtk`
2. Version check: `rtk --version` → parse semver → require ≥ 0.40.0
3. Integrity probe: run `rtk rewrite "git status"` once — must return non-empty stdout starting with `rtk `
4. Gate failure → enter **no-op mode** for session (all bash calls pass through unchanged)

### Latency gate

- Measure `rtk rewrite` wall time in Bun via `performance.now()` around `Bun.spawnSync()`
- Maintain rolling sample of last **200** calls (not 50 — avoids flapping)
- Per-call hard timeout: **100ms** (ceiling, not target)
- If rolling p95 exceeds **15ms**: disable live mode for remainder of session → fall back to no-op
- Re-check after 500 calls (in case system load drops)

### Loop guard

Structural, stateless, first thing after bash check:

```typescript
if (command.startsWith("rtk ") || command.startsWith("rtk:") || command.trim() === "rtk") {
  log("skip:already_rtk", command);
  return;
}
```

Covers all re-entry paths. No stateful tracking, no cross-invocation counters.

---

## Command classification

### Live mode: `rtk rewrite <command>` (primary)

- Call via `Bun.spawnSync()` with 100ms timeout
- **Authoritative signal:** non-empty stdout (NOT exit code — exit codes vary across RTK versions)
- RTK handles chains (`&&`, `;`), pipes (`|`), and non-identity mappings (`cat` → `rtk read`) internally
- Empty stdout → command not supported → pass through

### Validated allowlist (secondary gate)

Even when `rtk rewrite` returns a rewrite, the plugin checks whether the **leading command** is in the v1 validated allowlist:

```typescript
const V1_VALIDATED = new Set([
  "git", "ls", "grep", "find", "diff", "wc",
  "cat",  // mapped to "rtk read" by rtk rewrite
]);
```

Commands outside this set are NOT rewritten in v1 (write `skip:unvalidated` audit entry). This set expands only after output-fidelity validation on each command.

### No static fallback in v1

When the binary gate fails, the plugin goes **no-op**, not static. Prepending `rtk` without a working binary produces `rtk: command not found`. Static fallback is explicitly out of scope for v1.

---

## Rewrite edge cases

| Input | Output | Reason |
|---|---|---|
| `git status` | `rtk git status` | Validated |
| `rtk git status` | unchanged | Loop guard |
| `RTK_DISABLED=1 git status` | `git status` (stripped) | Opt-out |
| `echo $(ls)` | unchanged | Unattestable: `$()` |
| `ls > /tmp/out` | unchanged | Unattestable: redirect |
| `cat <<EOF ... EOF` | unchanged | Unattestable: heredoc |
| `sudo git status` | unchanged | Sudo-prefixed not rewritten |
| `git push origin main` | `rtk git push origin main` | Rewritten (crosslink handles blocking) |

---

## Crosslink-guard integration

**Problem:** `rtk-guard.ts` loads before `crosslink-guard.ts` alphabetically. If `rtk-guard` rewrites `git push` → `rtk git push`, crosslink misses its block.

**Fix (single point — in crosslink-guard, not rtk-guard):**

In `crosslink-guard.ts:normalizeGitCommand()`, strip a leading `rtk ` before evaluating:

```typescript
function normalizeGitCommand(cmd: string): string {
  if (cmd.startsWith("rtk ")) cmd = cmd.slice(4);
  // ... existing git-flag normalization ...
}
```

No Layer 2 blocklist in rtk-guard. No coupling between plugins. Crosslink's policy lives in crosslink.

---

## Audit logging

Write to `~/.local/share/rtk/hook-audit.log` when `RTK_HOOK_AUDIT=1`. Match RTK's exact format:

**Format:** `timestamp | action | original | rewritten`

- Timestamp: local time, ISO 8601, no `Z` suffix (match RTK's `audit_log_inner`)
- Escape `|`, `\`, `\n`, `\r` in command fields (match RTK's `sanitize_log_field`)
- Actions: `rewrite`, `skip:no_match`, `skip:already_rtk`, `skip:opt_out`, `skip:unattestable`, `skip:unvalidated`, `skip:no_op`, `skip:latency`

---

## Verification protocol

### Pre-deployment

1. **Smoke test:** Minimal plugin proving `output.args.command` mutation works. If fails, stop — the entire approach is invalid.
2. **Latency measurement:** Measure `rtk rewrite` in Bun. If p95 > 15ms, ship in no-op mode.
3. **Output fidelity:** For each v1 allowlist command, run raw vs RTK and confirm output is parseable.

### Post-deployment (four valid metrics)

| Metric | Source | Success signal |
|---|---|---|
| Adoption % | `rtk session` → RTK-covered / total | Increases vs baseline |
| Rewrite count | `rtk hook-audit` | > 0 and growing |
| Tokens saved | `rtk gain` | Positive delta vs baseline |
| Double-prefix | All logs | **Zero** `rtk rtk` |

**Failure signals:** adoption % unchanged, zero rewrite counts, any `rtk rtk` in logs.

---

## Implementation order

1. **Smoke test plugin** — prove `output.args.command` mutation works in OpenCode
2. **Latency measurement** — verify `rtk rewrite` p95 ≤ 15ms in Bun; if > 15ms, ship no-op
3. **Skeleton + fail-open wrapper** — hook registration, bash branch, try/catch over everything
4. **Loop guard** — structural `startsWith("rtk ")` and related checks, first after bash detection
5. **Opt-out** — `RTK_DISABLED=1` env and prefix handling
6. **Unattestable construct scan** — quote-aware lexical check rejecting `$()`, backticks, redirects, heredocs
7. **Binary gate** — path/version/integrity probe; on failure → no-op mode
8. **Latency gate** — Bun-measured rolling p95, 100ms timeout, session-level disable
9. **Live rewrite + validated allowlist** — call `rtk rewrite`, check allowlist, mutate `output.args.command`
10. **Audit writer** — exact RTK format, gated on `RTK_HOOK_AUDIT=1`
11. **Crosslink-guard fix** — one-line `rtk ` strip in `normalizeGitCommand()`
12. **Output-fidelity validation** — run the test matrix before expanding the allowlist
13. **Verification run** — before/after `rtk gain`, `rtk session`, `rtk hook-audit`

---

## Constraints

- Never blocks or errors on any bash call
- No `opencode.json` changes (auto-discovered)
- Works with OpenCode's Bun runtime
- `rtk` binary path configurable via `RTK_BINARY` env var or auto-detected
- No static fallback in v1 — gate failure = no-op, not broken commands
