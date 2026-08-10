# Design: `rtk-guard.ts` — OpenCode Native RTK Transparent Rewriting

**Status:** Proposed
**Layer:** Execution (OpenCode plugin)
**Location:** `.opencode/plugins/rtk-guard.ts`
**Depends on:** `@opencode-ai/plugin` (already present), `rtk` binary on `PATH` (already present at `~/.cargo/bin/rtk`)
**Companion analysis:** `docs/research/harness-evaluations/2026-07-12-rtk-opencode-gap-analysis.md`
**Companion plugin:** `.opencode/plugins/crosslink-guard.ts` (pattern source — read but NOT copy-pasted)

---

## 1. Overview

`rtk-guard.ts` is an OpenCode plugin that restores RTK's **transparent command rewriting** inside OpenCode sessions. RTK (`rtk-ai/rtk`) reduces LLM token consumption by caching/compressing the output of common commands (`grep`, `find`, `ls`, `git`, `cat`, `read`, …). In Claude Code this rewriting is done by a `PreToolUse` hook (`rtk hook claude`) that fires before every `Bash` call. OpenCode does **not** run Claude Code hooks (FIN-01, validated), so that mechanism is structurally absent and agent compliance with explicit `rtk` prefixing is inconsistent (FIN-03: only 0.6% of 779 tracked commands used hook rewriting; the rest were explicit prefixes or pass-through).

`rtk-guard.ts` is the OpenCode-native equivalent: it registers a `tool.execute.before` hook, intercepts `bash` tool calls, and mutates `output.args.command` to prepend `rtk` to the parts of the command that RTK can optimize. It is **transparent and fail-open**: it never blocks, never errors on a bash call, and degrades to a no-op if anything is wrong.

It is deliberately patterned on `crosslink-guard.ts` for the *hook registration and bash-interception skeleton*, but diverges in two structurally important ways that the copy-paste trap would miss:

1. `crosslink-guard.ts` only **reads** `output.args` and **blocks** by throwing. `rtk-guard.ts` **mutates** `output.args.command` and **never throws** on a normal bash call.
2. Because it rewrites-and-reinvokes, `rtk-guard.ts` must contain an **infinite-loop guard** as a first-class design element. `crosslink-guard.ts` has no such hazard because it never rewrites.

---

## 2. Hook Registration & Lifetime

OpenCode auto-discovers plugins from `.opencode/plugins/*.ts` (OBS-09). No `opencode.json` change is required. The plugin exports a default `Plugin` factory:

```
default export async (pluginInput: PluginInput) => ({
  "tool.execute.before": async (input, output) => { ... }
})
```

- **`pluginInput`** provides `$` (BunShell), `directory` (project root), and runtime info. Used for optional subprocess classification and logging only.
- **`input`** carries `{ tool, sessionID, callID }`. We branch on `tool === "bash"` (case-insensitive).
- **`output`** carries mutable `output.args`. For bash, `output.args.command: string` is the field we rewrite. The object is mutable (OBS-06, OBS-07) — but see Risk R1: this mutability has **not** been runtime-validated for the `bash` tool specifically (FIN-02 is `Supported`, not `Validated`). A smoke test (§8, step 2) must confirm that mutating `output.args.command` actually changes what executes.

**Lifetime / state:** The factory runs once per session. Any cached state (resolved `rtk` path, static command list) is computed lazily on first hook call, mirroring `crosslink-guard.ts`'s `ensureState()` pattern, to avoid slowing plugin load. The plugin must be **reentrant** — OpenCode may fire the hook concurrently for parallel bash calls — so no shared mutable counters or global flags that assume single-threaded execution.

---

## 3. Command Classification Strategy

The core question: *does this bash command (or a segment of it) benefit from RTK optimization?* Two strategies, chosen by a latency gate.

### 3.1 Latency gate (measure BEFORE building — requirement #1)

`tool.execute.before` fires on **every** bash call, in **every** session, forever. If classification shells out to `rtk` synchronously, that subprocess is on the critical path of every bash invocation. We must measure, not assume.

**Measurement methodology:**

1. **Bare `rtk` invocation latency.** Run a representative classification subprocess (e.g., `rtk --version`, or the actual classify subcommand if one exists) in a tight loop, say 200 iterations, capturing wall-clock per call. Report p50 and p95.
   ```
   for i in $(seq 1 200); do
     /usr/bin/time -f "%e" rtk --version   # or the real classify call
   done
   ```
2. **Calls-per-session estimate.** From `rtk gain` (OBS-03/05): 779 commands tracked historically; recent OpenCode activity ~113 commands / 4 days. A single agent session plausibly issues **50–200** bash calls. Use 100 as the planning midpoint.
3. **Added latency per session** = `p95_classify_latency_ms × calls_per_session`.
4. **Threshold:** If added latency per session exceeds ~**1–2 seconds**, reject live subprocess classification and use the static pattern match. (1–2s is chosen because it is imperceptible-to-mildly-noticeable; the transparent hook must not make the agent feel slower. Tune after measurement.)

**Decision tree:**

```
measure p95(rtk classify latency)
        │
        ├─ no cheap classify subcommand exists  ──► STATIC (no subprocess at all)
        │
        ├─ p95 > ~10–20 ms  ──► STATIC
        │       (100 calls × 15ms = 1.5s/session, over threshold)
        │
        └─ p95 ≤ ~10–20 ms AND a real classify subcommand exists
                        ──► LIVE subprocess allowed (still behind fail-open)
```

**Default recommendation:** Ship **STATIC pattern match** as the primary, default strategy. It adds **zero** subprocess overhead (pure in-process string matching) and is therefore always safe on the latency axis. Promote to LIVE only if measurement proves a cheap classify subcommand exists and the budget allows. This inverts the usual "try live, fall back" ordering precisely because the cost of being wrong about latency is paid on every bash call indefinitely.

### 3.2 Static pattern match (default)

Maintain a curated, in-code list of command **prefixes** that RTK is known to optimize. Derive the initial list empirically from `rtk gain --history` (the commands that actually accrued savings) plus RTK's documented wrappable commands. Examples (to be confirmed against `rtk gain --history`):

```
git, grep, rg, find, ls, ll, cat, head, tail, wc, read,
ps, du, df, tree, locate, nl, sort, uniq, awk, sed
```

Classification = for each top-level pipeline/chain segment, take its leading token and test `knownPrefixes.includes(leadingToken)`. The list is a module-level constant, optionally overridable via an env var or a small config file (see §6).

### 3.3 Live subprocess (optional, gated)

If the latency gate permits, call `rtk` to classify. The exact subcommand is **unknown** and must be discovered during implementation (candidate: `rtk classify "<cmd>"` or a dry-run flag). If no such subcommand exists, this branch is unreachable and STATIC is used. The live call must be `nothrow().quiet()` and wrapped so a failure falls back to STATIC, never to a block.

---

## 4. Rewrite Logic

**Goal:** prepend `rtk ` to each segment of the command whose leading command is RTK-optimizable, leaving non-optimizable segments and already-wrapped segments untouched.

**Algorithm (v1 — top-level segments):**

1. **Loop guard first** (see §5): if the whole command `startsWith("rtk ")` → return immediately, no rewrite.
2. **Shell-aware split** into top-level segments on `|`, `||`, `&&`, `;` (reuse the `shellSplit` approach from `crosslink-guard.ts`, but split on separators outside quotes). Do **not** recurse into `$(…)`, backticks, or nested subshells in v1 (documented limitation, §9).
3. For each segment:
   - Trim. If empty, keep as-is.
   - If segment `startsWith("rtk ")` or starts with `rtk:` (TOML prefix) → leave unchanged (already optimized / already wrapped).
   - Else take leading token; if it is in the optimizable set → prepend `rtk `.
   - Else leave unchanged.
4. Rejoin segments with their original separators.
5. Assign `output.args.command = rewritten`.

**Illustrative sketch (not implementation):**

```
if (command.startsWith("rtk ")) return;            // loop guard
const segs = splitTopLevel(command);               // respects quotes
const out  = segs.map(s => wrapIfOptimizable(s));  // prepend "rtk " when leading token ∈ set
output.args.command = out.join(originalSeparators);
```

**Examples:**

| Input | Output |
|---|---|
| `git status` | `rtk git status` |
| `grep -r foo src` | `rtk grep -r foo src` |
| `git status \| grep dirty` | `rtk git status \| rtk grep dirty` |
| `cd build && make` | `cd build && make` (neither `cd` nor `make` in set) |
| `ls -la; rtk grep x` | `rtk ls -la; rtk grep x` |
| `rtk git status` | `rtk git status` (guard → unchanged) |

**Edge cases:**

- **Pipelines:** each segment classified independently (above). A segment that is not optimizable is left raw; this is safe and correct, only a missed-optimization, never a corruption.
- **Subshells / `$(…)` / backticks:** v1 does **not** descend into them. A command like `echo $(git status)` is left unwrapped. This is a known limitation (§9), chosen over risky nested rewriting. Future version may recurse.
- **Quoted commands:** `shellSplit` must respect single/double quotes so `"git status"` inside a string is not mangled.
- **`rtk:` TOML prefix:** RTK's own structured-output prefix (`rtk:toml …`) is treated as already-optimized and left alone.
- **Empty / whitespace command:** pass through unchanged.

---

## 5. Infinite-Loop Prevention

This is the hazard class that makes a naive copy of `crosslink-guard.ts` **defective by default**: that plugin only blocks/allows and never rewrites-and-reinvokes, so it has no loop risk. `rtk-guard.ts` rewrites `git status` → `rtk git status`; OpenCode then executes `rtk git status` as a **new** bash call, the hook fires **again**, and without a guard we get `rtk rtk git status` → `rtk rtk rtk git status` → unbounded recursion (or at least wasteful double-wrapping).

**Design: structural early-return guard (primary, mandatory).**

The very first action after confirming `tool === "bash"` is:

```
if (typeof output.args?.command === "string"
    && output.args.command.startsWith("rtk ")) {
  return;   // already rewritten by us (or explicitly by agent) — do not re-wrap
}
```

This is **structural**, not stateful: it relies on the idempotency of the rewrite. Once a command begins with `rtk `, every subsequent firing sees that prefix and bails. No counters, no shared state, no cross-invocation tracking required. This is sufficient because the hook observes *every* resulting bash call, including the rewritten one, and the prefix check catches it on the next firing.

**Edge cases the guard must handle correctly:**

- **`rtk` with no trailing space** (bare `rtk`, or `rtk` as a whole command): `startsWith("rtk ")` is false, so it would be "processed." But a bare `rtk` invocation is itself an RTK command and should not be wrapped anyway — classification (§4 step 3) already leaves `rtk`-leading segments alone, and a bare `rtk` has no optimizable sub-command to wrap. No loop. (If desired, also guard on exact `=== "rtk"`.)
- **`rtk` as a substring of another command name** (`myrtk foo`, `rtktool`, `srtk`): `startsWith("rtk ")` is false for `myrtk foo` (starts with `myrtk`), so it is *not* mistaken for an already-wrapped command and is instead classified normally. `myrtk` is not in the optimizable set, so it is left unchanged. Correct — no false guard, no false wrap.
- **`rtk:` TOML prefix:** handled by the per-segment check in §4, not the whole-command guard; the whole-command guard still fires first for the common `rtk git status` case.

**Optional defense-in-depth (NOT required, documented only):** A bounded stateful watchdog could track `(callID, normalizedCommand)` and throw/abort if the same command is wrapped more than N times within a short window. This protects against a future bug where the prefix check is bypassed (e.g., a rewrite that drops the space). It is **not** part of v1 because the structural guard already makes loops impossible by construction; adding stateful tracking introduces reentrancy and lifetime complexity that v1 does not need. Recommend revisiting only if the structural guard is ever found insufficient.

**Conclusion:** structural early-return is the correct and complete solution. Stateful loop detection is unnecessary for v1.

---

## 6. Error Handling & Failure Modes

The plugin is **transparent and fail-open**. Under no circumstance may it block or error a legitimate bash call. Every code path that can fail must degrade to "pass the command through unchanged."

| Failure mode | Behavior |
|---|---|
| `rtk` binary missing / not on `PATH` | Detect once at state-resolve (probe `rtk --version`). If absent, set a `rtkAvailable=false` flag and the hook becomes a complete no-op (returns immediately). Log once. |
| `rtk` path misconfigured by user | Same as missing: no-op + log. Never throw. |
| Command string missing / not a string | Pass through unchanged. |
| Command cannot be parsed by `shellSplit` | Pass through unchanged (do not wrap a half-parsed command). |
| Static list empty / misconfigured | Treat as "no optimizable commands" → no-op. |
| Live classify subprocess errors / times out | Fall back to STATIC classification for that call; if STATIC also unavailable, pass through. `nothrow().quiet()` always. |
| Unexpected exception in hook body | Wrap entire hook logic in `try { … } catch { return; }`. A throwing hook could block the tool call — absolutely forbidden. |
| Plugin fails to load / register | OpenCode logs the plugin error; bash calls proceed normally (no RTK rewriting, but no breakage). Acceptable degradation. |

**Logging:** best-effort append to `/tmp/rtk-guard.log` (mirror `crosslink-guard.ts`'s `log()`), wrapped so logging never throws. Log: plugin init, rtk-availability probe result, each rewrite (command truncated), each skip reason (guard/non-optimizable), and any caught error. Never log command contents that may contain secrets at full length — truncate to ~200 chars.

**Configurability of `rtk` path:**

- **Auto-detect:** probe `rtk` via `which`/direct spawn on `PATH` (it is at `~/.cargo/bin/rtk`, already on PATH per OBS-01).
- **Override:** honor env var `RTK_GUARD_RTK_BIN` (absolute path) if set, taking precedence over auto-detect. (A future `.opencode/rtk-guard.json` could extend this, but env var is sufficient for v1 and keeps the plugin self-contained.)

---

## 7. Verification Protocol

Trust is earned by measurement, not by "it loaded without errors." The decisive metric is RTK's own **hook-rewrite percentage**, which is currently **0.6%** (5 of 779 commands, OBS-03). A plugin that loads but never rewrites is a failure.

**Baseline (before build/deploy):**
1. Run `rtk gain` and capture: total commands, explicit-prefix count, hook-rewrite count, hook-rewrite %.
2. Run `rtk session` / `rtk discover` to confirm session attribution works.
3. Record the numbers as the baseline (expect hook-rewrite ≈ 0.6%).

**Deploy:** place `rtk-guard.ts` in `.opencode/plugins/`, start a fresh OpenCode session.

**Exercise (the real test):** in the new session, perform typical agent work that *should* trigger rewriting: `git status`, `git log`, `grep -r`, `ls -la`, `find . -name`, `cat` on a file, etc. — written **without** the `rtk` prefix, to simulate the inconsistent-compliance scenario the plugin exists to fix. Also include a pipeline (`git status | grep`) and a chained command (`ls && grep`).

**Measurement (after):** run `rtk gain` again and compare:

| Metric | Baseline | Success threshold | Failure signal |
|---|---|---|---|
| Hook-rewrite % | ~0.6% | **> 20%** of *new* session commands that are optimizable are counted as hook rewrites (absolute % should rise clearly off 0.6%) | Unchanged at 0.6% → plugin did not rewrite |
| Double-wrapping | none | No command in `rtk gain --history` shows `rtk rtk …` | Any `rtk rtk …` → loop guard failed |
| Session latency | n/a | No perceptible slowdown (STATIC mode adds ~0ms) | Noticeable lag → latency gate was violated |
| Plugin load errors | n/a | None in OpenCode startup log; `/tmp/rtk-guard.log` shows init + rewrites | Load error → plugin not registered |

**Success definition:** hook-rewrite % moves **decisively off the 0.6% baseline** (target: the majority of optimizable commands in the test session are now attributed to hook rewriting) **and** zero double-wrapped commands appear. If the percentage does not move, the plugin did not work *regardless of whether it loaded cleanly* — re-run the §8 smoke test to find where rewriting breaks (registration vs. mutation vs. classification).

**Secondary check:** inspect `/tmp/rtk-guard.log` to confirm rewrites occurred for the expected commands and that the loop guard fired on the rewritten `rtk …` calls (proving §5 works).

---

## 8. Implementation Plan (ordered, with dependencies)

1. **Latency measurement (GATE — do first, before any code).** Measure `rtk` classify/version p95 latency; compute per-session cost; decide STATIC vs LIVE. *Dependency: none. Blocks step 3's strategy choice.*
2. **Mutation smoke test (validates FIN-02).** Build a minimal plugin that prepends a harmless marker (e.g., `echo MARKER `) to every bash command and confirm in a real session that the marker actually executes. *This de-risks the single biggest unknown (whether `output.args.command` mutation affects execution) before investing in full logic.* If mutation does **not** take effect, stop and escalate — the entire approach is invalidated.
3. **Skeleton + loop guard.** Port the `tool.execute.before` / bash-branch skeleton from `crosslink-guard.ts`; add the §5 structural guard as the **first** statement after the bash check. *Dependency: step 2 passed.*
4. **Static command list + classification.** Hard-code the optimizable prefix list (derived from `rtk gain --history`); implement `shellSplit` + top-level segment split + per-segment classification. *Dependency: step 1 result (STATIC is the default).*
5. **Rewrite logic.** Implement §4 algorithm; rejoin with original separators; assign `output.args.command`.
6. **Error handling / fail-open.** Wrap everything in try/catch; rtk-availability probe; all failure modes → pass-through (§6).
7. **Config + logging.** `RTK_GUARD_RTK_BIN` override + auto-detect; `/tmp/rtk-guard.log` best-effort logger.
8. **(Optional) LIVE subprocess branch.** Only if step 1's gate permits; behind the same fail-open wrapping; falls back to STATIC.
9. **Verification run.** Execute §7 protocol; compare before/after `rtk gain`; confirm no double-wrapping and no latency regression.

**Sequencing principle:** steps 2 and 5 are the risk-bearing steps (mutation validity, loop safety). They are built and tested early and independently so a defect is caught before the full feature is assembled.

---

## 9. Risks & Unknowns

- **R1 — Mutation validity (FIN-02 is `Supported`, not `Validated`).** `crosslink-guard.ts` reads `output.args` but never writes it. Whether mutating `output.args.command` actually changes the executed bash command in OpenCode is unproven at runtime. *Mitigation: step 2 smoke test before any further investment. If invalid, escalate — no plugin possible.*
- **R2 — RTK behavior on wrapped commands.** RTK compresses/caches output. Wrapping a command RTK does not recognize could alter stdout format or exit codes in ways that break agent parsing (same risk RTK's Claude Code hook already carries, but must be re-confirmed for OpenCode). *Mitigation: only wrap commands confirmed in `rtk gain --history` as beneficial; never wrap unknown commands.*
- **R3 — Output fidelity.** RTK's compression may drop content the agent relies on (e.g., exact line numbers, full file text). This is inherent to RTK, not the plugin, but the plugin multiplies exposure by wrapping more commands. *Mitigation: start conservative (small optimizable set), expand only after verifying agent task success is unaffected.*
- **R4 — Subshells / `$(…)` / backticks not handled in v1.** Commands with nested command substitution are left unwrapped (missed optimization, not corruption). *Mitigation: documented limitation; future recursion. Acceptable for v1.*
- **R5 — Reentrancy.** Parallel bash calls fire the hook concurrently. Shared mutable state (counters, caches written non-atomically) could race. *Mitigation: keep state read-only after lazy init; no cross-call mutable flags; the loop guard is stateless by design.*
- **R6 — Classification drift.** The static list can go stale as RTK adds optimizable commands. *Mitigation: periodically regenerate from `rtk gain --history`; LIVE mode (if enabled) self-corrects.*
- **R7 — Agent intent to run raw.** Some commands must produce raw, uncompressed output (e.g., piping into a parser, or the agent explicitly wants full `git diff`). Transparent wrapping may interfere. *Mitigation: an exclusion prefix the agent can use (e.g., a leading `!` or an env-flagged "raw" marker) that the guard honors and skips; out of scope for v1 but noted.*
- **R8 — Hook fires on the `rtk` binary's own internal bash?** RTK is a Rust binary; it does not spawn bash tool calls through OpenCode, so the guard will not see RTK's internals. Low risk. *Mitigation: the `startsWith("rtk ")` guard also covers any command the agent explicitly prefixes.*

---

## Appendix A — Relationship to `crosslink-guard.ts`

| Aspect | `crosslink-guard.ts` | `rtk-guard.ts` |
|---|---|---|
| Hook | `tool.execute.before` | `tool.execute.before` |
| Intercepts | write/edit/bash | bash |
| Reads `output.args` | yes | yes |
| **Mutates `output.args`** | **no** | **yes (`command`)** |
| Blocks by throwing | yes (policy) | **never** (fail-open) |
| **Infinite-loop guard** | **N/A (no rewrite)** | **required, structural** |
| Subprocess on hot path | yes (crosslink CLI) | **no (STATIC default)** |
| Purpose | policy enforcement | token-cost reduction |

The skeleton (plugin factory, bash branch, `shellSplit`, lazy state, logging) is reused. The mutation, fail-open error model, and loop guard are net-new and are the substance of this design.
