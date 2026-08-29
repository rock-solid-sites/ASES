---
title: V2 Guard Rewrite Design — Beta TUI Inventory + crosslink-guard V2 (tool-allowlist, path-allowlist, kill-pause, gated git)
program: EDASES
layer: Implementation
document_type: Design
status: Draft
authority: Derived
canonical_repository: edases
issue: 504
branch: feature/v2-guard-rewrite
depends_on:
  - .opencode/plugins/crosslink-guard.ts (1597 lines, current)
  - .opencode/plugins/orchestrator-guard.ts (335 lines)
  - .opencode/plugins/rtk-guard.ts (415 lines)
  - .opencode/opencode.json
  - .crosslink/hook-config.json
  - docs/research/registry/Hookability-Matrix.md (Surface Re-Validation 2026-08-24)
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md §2.4
supersedes: []
related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/research/registry/Failure-Matrix.md
  - .opencode/permissions.md
  - .crosslink/knowledge/agent-orchestration-playbook.md
  - research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md
created: 2026-08-28
authors: [muse-spark-1.2-contributor via opencode-go]
---

# V2 Guard Rewrite Design — Beta TUI Inventory + crosslink-guard V2

## 0. Reading Guide

This design answers issue #504: inventory the Beta TUI (opencode2 S1) plugin-loading and `tool.execute` payload on the current fork (S2), then draft a **V2 `crosslink-guard` design** covering **tool-allowlist**, **path-allowlist**, **kill-pause**, and **gated git**. Orchestrator/rtk implications are sketched; full expansion to all plugins is deferred to the next pass.

Every claim that crosses a role boundary carries the project's reasoning-certainty quartet (AGENTS.md: WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED). The global assessment is in §8–§9; §1 also carries a per-section WHY for the design decisions it motivates.

---

## 1. WHY — the reasoning behind this design

### 1.1 The enforcement premise this design serves

ASES runs four specialist roles (Orchestrator / Builder / Reviewer / Auditor) separated by **authority**, not suggestion. The separation is only meaningful if the tooling makes it a **structural** property — a role that is told it is read-only must be *unable* to write by any available mechanism. The project's Workflow Topology design (one-role / two-phase, position-emitting agents, durable store) plus the agent-orchestration playbook (§5.8) operationalize that premise.

**WHY a guard rewrite matters:** the current guard set is *mechanically* surface-dependent. A proposal that assumes guards are enforcement will be mis-classified as structural when it is merely directive on the wrong surface. The cheapest-test-first obligation sits with the *producer* (the side that can instrument cheaply) — so this design first inventories what actually loads and what payload the hooks actually see before drafting control logic.

### 1.2 WHY Beta TUI inventory comes first (Cheapest-Test-First)

The assurance that would be lost if the inventory were skipped is "S1-dormant enforcement" — the failure class where an orchestrator assumes a `crosslink-guard` block that does not exist on S1 and dispatches a Builder task that silently mutates state. The cheapest discriminating test is *log-proven plugin loading* plus a *payload-shape capture*, both cheap (one boot + one tool call). If the inventory shows S1 loads no worktree guards, the V2 design cannot assume S1 enforcement exists and must shape the design accordingly (prompt-discipline hardening vs plugin hardening vs CLI hardening). Committing to implementation before that knowledge is the expensive work the principle is meant to guard against.

### 1.3 WHY the four V2 pillars are non-optional

* **Tool-allowlist (deny-by-default):** the current `allowed_bash_prefixes` is an *allow-fast-path*, not a denying surface — hy3's step-6 reading proves a non-matching bash command still passes in both tracking modes when an active issue exists. Without deny-by-default, "reviewer is read-only" remains a tool-denial claim (Claim a in the reviewed report: 8/8 reviewers overstated) rather than repository immutability.
* **Path-allowlist:** even with tool-allowlist, `filesystem_write_file`/`bash` can still reach arbitrary paths (including `hook-config.json` itself — the self-modifying-trust-root finding, Sonnet 5 claim g). Path scope is the complement of tool scope; one without the other leaves bypass classes (`npm run`, `cargo build`, `opencode --pure`, `git -C`).
* **Kill-pause (fail-closed):** the current kill/pause path *fails open* when `crosslink` is unavailable (`if (!result) return` at crosslink-guard.ts:636) and is ordered *after* the health gate only by coincidence of priority. An operator kill that is best-effort is not a kill switch (Deepseek finding). V2 must order it highest and fail closed.
* **Gated git (hardened):** `git commit` gating currently normalizes global flags (`-C`, `--git-dir`, `--work-tree`, `-c`) and chained commands, but only for space-padded separators (`" && "`, `" ; "`, `" | "`) and does not cover bare `&&`/`;`/`|` or other shell forms — Qwen's prefix-matching bypass class lives here. For the `git merge` / `git push` boundary (push is operator-only everywhere; merge is gated for orchestrator, blocked for reviewer/auditor), the normalization is the denying surface.

### 1.4 Design posture

* **S2-first, S1-aware:** V2 is a S2 plugin design (the only surface where worktree plugins are loaded today). S1 considerations are captured as explicit prompts for the Beta TUI parity track (new guard vs CLI enforcement vs permission-model hardening) — not assumed as already solved.
* **Ordering is semantics:** health → kill/pause → blocked git → gated git → comment discipline → allowlists → relaxed fallback → active-issue — reordering changes guarantees. §6 codifies the new order.
* **No stubs:** every branch in §6 is a decision with a test; deferred items are marked *sketch* with the next pass named, not hidden behind TODOs.

---

## 2. WHAT — Beta TUI Plugin-Loading Inventory (S1 vs S2)

### 2.1 WHAT was observed (evidence)

**Claim: S1 (opencode2 beta TUI) loads only global fallback plugins; worktree guards are not loaded.**

* **WHAT basis (§8: WHAT):** the Hookability Matrix Surface Re-Validation (2026-08-24, per #425) and the operator handoff on #504 ("Beta TUI plugin-load = only `oh-my-openagent:tui` (do not re-prove)"). The matrix states the re-validation was established empirically by #425: S1 plugin loading = Global fallback plugins only (`plugins/plugin.ts`, `plugins/interrupt.ts`); **worktree `.opencode/plugins/` guards NOT loaded** (`orchestrator-guard`, `crosslink-guard`, `rtk-guard` absent from v2 debug config). S2 = worktree `.opencode/opencode.json` loaded; all 3 plugins active — proven by runtime logs (guard ALLOW for builder `filesystem_write_file` 19:25:27; BLOCK for auditor 19:16:48). The consequence row re-classifies every `(a)` — OpenCode `tool.execute.before` — enforcement as **[S2]**: real and log-proven on S2, absent on S1.
* **This worktree's corroboration:** the current S2 dispatch (run `0ffdfcad`, `922c9a5b`) shows repeated `WARN background dependency install failed ... @opencode-ai/plugin: No matching version found for @opencode-ai/plugin@1.18.13-pp3g-fork` for `.opencode` directories — the plugin build pipeline is fork-pinned and not fetching on every path, but `.opencode/opencode.json` plus `plugin: ["./plugins/orchestrator-guard.ts", ...]` is evaluated on S2. The Beta TUI S1 path was not re-exercised per handoff (no new `opencode2 run` probe needed).
* **Prior probe artefact preserved for forensics:** `pp3g-hK0g-track-a-v2-guard-rewrite-design-beta-tui-inventory` introduced `.opencode/plugins/v2-probe.ts` — a dependency-free diagnostic logging `MODULE-LOADED`, `PLUGIN-INIT`, and per-hook shapes to `/tmp/opencode/v2-probe.log`. That probe **failed to load** on every attempt in the opencode log: `failed to load plugin ... v2-probe.ts cause="Cause([Fail(SchemaError(Expected object at [\"default\"]))])"` — the plugin-module export shape was rejected by the loader (see §2.3).

**Claim: In the current S2 worktree (`feature/v2-guard-rewrite`), the guard log (`/tmp/crosslink-guard.log`, 4 MB) still reflects the *prior* fork session; the current session's guard initialization is visible only via orchestrator-guard logs (`/tmp/orchestrator-guard.log`) which show `Plugin initialised, projectDir: /home/claude-code/projects/ASES/.worktrees/v2-guard-rewrite` at 22:54–22:55 with `chat.params agent: builder` events advancing.**

* **WHAT basis:** direct tail of both log files (see §8: HOW CERTAIN for log evidence).

### 2.2 Plugin manifest facts (S2)

| Fact | Value | Source |
|------|-------|--------|
| Declared plugins | `./plugins/orchestrator-guard.ts`, `./plugins/crosslink-guard.ts`, `./plugins/rtk-guard.ts` | `.opencode/opencode.json:4-8` |
| Plugin runtime | Bun (`bun:sqlite`, `node:fs`, `node:path`, BunShell `$`) | file header |
| Logging | `/tmp/crosslink-guard.log`, `/tmp/orchestrator-guard.log`, `/tmp/rtk-guard.log` — best-effort, never throws from hook | guard headers |
| Agent map | `orchestrator: primary`, `builder/reviewer/auditor: subagent` in opencode.json vs `mode: primary` in `.md` (known contradiction hy3 M6, unverified winner) | `opencode.json:9-23` + `agent-tooling-and-permission-enforcement-reviewed.md §2.2` |
| MCP filesystem | `enabled: true`, rooted at `/home/claude-code/projects/ASES` (main repo, not worktree — hy3 S5) | `opencode.json:37-40` |
| Fork version | `opencode 1.18.13-pp3g-fork`; `crosslink 0.9.0-beta.1+a87bd513` (deployed) vs `6221309e` (source HEAD) — one-commit delta in kickoff surface | reviewed report §2.3 + hook-config M1 |

### 2.3 Export-shape note (why `v2-probe.ts` failed)

Current guards export as:

```ts
import type { Plugin, PluginInput } from "@opencode-ai/plugin";
const crosslinkGuardPlugin: Plugin = async (pluginInput: PluginInput) => {
  return { "tool.execute.before": async (input, output) => { ... } };
};
export default crosslinkGuardPlugin;
```

The probe exported `export default async function probe(input: any) { return { ... }; }` — same semantic shape (async function returning the hook map) but rejected as `SchemaError(Expected object at ["default"])`. Two hypotheses consistent with logs: (a) the loader's schema expects `default: { "tool.execute.before": ... }` *object* not a function in the beta TUI; (b) the dependency-resolution failure (`@opencode-ai/plugin`) prevents type-checked validation, surfacing as a schema error before the function is ever called. This worktree chose not to re-prove S1 loading (per handoff) and instead preserves the hypothesis for the next parity pass.

### 2.4 Implications carried into V2

* V2 must be **S2-authoritative**; S1 hardening is an open item (§7) — any claim that "all plugins enforce on both surfaces" is false until parity work lands.
* The fork-pinned dependency (`@opencode-ai/plugin@1.18.13-pp3g-fork`) is a build fragility carried into V2: if the plugin SDK version diverges, every guard fails to load the same way.

---

## 3. WHAT — `tool.execute` Payload Inventory (filesystem + bash)

### 3.1 The hook surface we actually intercept

All three guards use OpenCode's `tool.execute.before` with signature:

```ts
"tool.execute.before": async (input, output) => { ... }
```

where `input` carries the hook metadata and `output.args` carries the *live* tool arguments the model is about to execute. The current `crosslink-guard` intercepts only `toolLower ∈ { "write", "edit", "bash" }` at line 1281 (`write` + `edit` + `bash` only), and `orchestrator-guard` intercepts `BLOCKED_TOOLS = { write, edit, apply_patch, filesystem_write_file, filesystem_edit_file, filesystem_create_directory, filesystem_move_file }` (plus `task` for model-gated launches).

### 3.2 Filesystem payload shape (authoritative)

**Captured via live hook logging and direct code reading** (the most reliable producer-side evidence:

* `write` — `output.args.filePath: string`, `output.args.content: string` (guard reads `filePath` at 1315).
* `edit` — same `filePath`, `oldString`/`newString` plus `replaceAll`.
* `filesystem_write_file` / `filesystem_edit_file` (`orchestrator-guard`) — `output.args.path: string` (and `content`/`edits`).
* `filesystem_create_directory` / `filesystem_move_file` — `path`, `destination`/`source`.

`crosslink-guard` currently exempts only `~/.muse/` writes via `isClaudeMemoryPath()` (resolved home + `path.resolve`, prefix check) — everything else falls through to config/per-issue gating. There is **no path-allowlist** in V1 — §5.2 of the V2 design introduces one.

**Negative-space (what filesystem tools are NOT covered):**

* Only `~/.muse/` is exempted — no other directory is specially treated, and there is no deny-by-path for `.crosslink/` (so the self-modifying trust root is reachable via any allowed tool).
* `orchestrator-guard` already added `filesystem_create_directory`/`filesystem_move_file` to `BLOCKED_TOOLS` after #425; `crosslink-guard` V1 does not separately check them — V2 will (§6.2.2).

### 3.3 Bash payload shape (authoritative)

* Single string: `output.args.command: string` (guard aliases it as `command` at 1332/1342/1415).
* Helpers split on chained separators and normalize `rtk` and global git flags:

  * `normalizeGitCommand` strips leading `rtk ` prefixes (loop) then `flagsWithArg = { -C, --git-dir, --work-tree, -c }` and `startsWith("--git-dir=")`/`"--work-tree="`.
  * `shellSplit` is a minimal quote-aware splitter (single/double quotes).
  * `matchesCommandList` directly checks `normalized.startsWith(entry)` plus a per-part check after splitting on `" && "`, `" ; "`, `" | "` — note the separators require surrounding spaces.
  * `isAllowedBash` progressively splits on the same three space-padded separators and requires `EVERY` sub-command to match `allowed_bash_prefixes`.

**Bash payload negative-space (cheap-class false confidence):**

* Only three separators are parsed and only in space-padded form — bare `&&` / `;` / `|` and other shell forms (`||`, `&`, `$(...)`, backticks, subshells) are not parsed. A command that bypasses the split is still a single string so the allowlist check may mis-classify it.
* `normalizeGitCommand` does not cover `--work-tree=` form for global flags (covers `--git-dir=` + `--work-tree=` only as string checks) — minor, low-risk.
* `output.args.workdir` (the `workdir` parameter alternative to `cd && cmd`) is not inspected by V1 — a `workdir` pointing outside the project would not be flagged by bash-path logic.

### 3.4 Intended live capture (deferred, not re-proven here)

The original kickoff prompt asked for a *live* capture of the execute payload shape for filesystem + bash on Beta TUI. The handoff directs to **not re-prove** plugin loading (S1) and the probe's shape definition (`v2-probe.ts`) is preserved for the next S1 parity pass. The shapes above are the *S2 live* shapes (proven by handler code + runtime logs). S1's shape is hypothesized identical on the `tool=execute` sandbox (`tools.filesystem.*` inside `tool=execute` per the Hookability Matrix S1 column) but is **HOW CERTAIN = guess** until a successful probe writes `/tmp/opencode/v2-probe.log`.

---

## 4. WHAT — Current Crosslink-Guard Behavior Audit (V1, 1597 lines)

### 4.1 Control flow, in priority order (§3 of file header)

```
0. Crosslink health  — halt > warn > suggest  (#514, fail-closed if CLI/DB/hub-cache unavailable)
1. Operator kill/pause  — crosslink agent flags --strict  (highest priority)
2. ~/.claude/ exemption  — write/edit only
3. Permanently blocked git  — matchesCommandList(blocked_git)  (push/rebase/reset/clean/…)
4. Gated git  — git commit gated on active issue + optional plan comment
4b. Gated bash  — model-launch gate (operator approval)  — crosslink kickoff/swarm
5. Issue-close discipline  — --kind result
6. Allowed bash fast-path  — isAllowedBash(allowed_bash) → ALLOW
7. Relaxed mode  — if (tracking_mode === "relaxed") return  (any non-blocked non-gated bash passes)
8. No crosslink dir  — allow
9. Active-issue enforcement  — sentinel fast path or session status
10. No active work item  — strict throws, normal reminds
```

### 4.2 Tool-allowlist — the "allowlist that doesn't deny"

* **Reported as:** `allowed_bash_prefixes` (34 in reviewed report §2.4 for orchestrator .md; 49 in hook-config). **Operationally:** step 6 is an `early-return ALLOW`; failing to match **does not** block. Control falls to step 7/9. Because working agents always have an active issue (gated commit invariant), step 9's `.active-issue` sentinel (`/home/.../.crosslink/.active-issue` with content like `"504"`) fires before step 10 — so the allowlist never denies bash in either tracking mode (hy3 M3, confirmed by source). The *actual* bash denials in S2 are: (a) `blocked_git_commands`, (b) `gated_bash_commands` (model gate), and (c) the opencode native `.md` permission `bash: "*": deny` for orchestrator/reviewer/auditor. V2 redesigns `(a)` into a **deny-by-default** tool-allowlist (§5.1).

### 4.3 Path-allowlist — absent

* No filesystem-path check exists in V1 (neither `crosslink-guard` nor `rtk-guard`). The only path predicate is `isClaudeMemoryPath` (exemption). Consequences:
  * Builder with `edit: allow` + `bash: allow` can edit `hook-config.json`, `hook-config.local.json`, `agent.json`, `.opencode/opencode.json`, and plugins themselves — self-modifying trust root (Sonnet 5 claim g; hy3 M7 note that `--auto` makes this unconditional in the kickoff path).
  * `filesystem_*` tools hosted at the main repo root (`/home/claude-code/projects/ASES`) but invoked from a worktree can still reach `~/. crosslink` sibling paths depending on the MCP server's path validation — opencode native `external_directory: {"*": "ask", "/tmp/*": "allow"}` is the only path layer, and it is auto-approved under `--auto` (reviewed report §2.4 hy3 M7).

### 4.4 Kill-pause — best-effort path

* At lines 632–670, `checkControlFlags(shell, crosslinkDir, throwBlock)`: calls `crosslink agent flags --strict`, exits 0 → pass; exit 2 → JSON `{ kill, paused, reprioritise }` → throws kill or pause block. Two structural gaps:
  * `if (!result) return;` — **fails open** when `crosslink` is unavailable or hung; same comment at 636: `// crosslink not available or hung — fail open`. This is the Deepseek kill-switch finding: availability of the CLI is availability of the kill switch.
  * Ordering: kill/pause is correctly at priority 1 *after* health at priority 0 in V1, but the health gate (#514) still has a no-op for missing hub-cache in worktrees (logs "tolerated") rather than guaranteeing availability.

### 4.5 Gated git — hardened in parts

* **Normalization correct:** `normalizeGitCommand` + `while (command.startsWith("rtk "))` catches `rtk git push`, `git -C /x push`, `git --git-dir=... push`, `git -c ... push`.
* **Chaining:** `matchesCommandList` splits on `" && "`, `" ; "`, `" | "` per part. Correct for canonical chained forms; missing bare `&&`/`;`/`|` and `||`, `&`, `$( )`, subshells (Qwen H-02 class).
* **Sentinel fast-path:** `.active-issue` content trimmed; if non-empty → ALLOW immediately at step 4 without subprocess. This is the correct fast path but expands the trust surface to a single file write away from bypassing gated git — V1 treats the sentinel as authoritative without validating it against `session status` or issue state. V2 keeps the fast path but validates (§5.4.3).
* **Comment discipline:** `issueHasCommentKind` reads `issues.db` `comments WHERE issue_id = ? AND kind = ? COUNT(*)` — correct but `issues.db` staleness is not checked alongside the count beyond the health gate's age heuristic (>24h warn).

---

## 5. WHAT — V2 crosslink-guard Design (authoritative section)

### 5.1 Tool-allowlist — from allow-fast-path to deny-by-default

**Goal:** V2 must downgrade `allowed_bash_prefixes` from an optimization hint to a *security boundary*, per-role, per-tool, deny-by-default.

#### 5.1.1 Principle of operation (V2)

```
For bash:
  if tool != "bash": next stage
  if matchesCommandList(command, config.blocked_git): throw BLOCKED_GIT
  if matchesCommandList(command, config.gated_git):    → gated-gate ( §5.4 )
  if matchesCommandList(command, config.gated_bash):   → model gate ( §5.5 )
  if isAllowedBash(command, config.allowed_bash_for_role):
       allow (log ALLOW: tool-allowlist hit)
  else:
       // V2 CHANGED BEHAVIOR:
       if tracking_mode == relaxed and is_agent and builder:
            allow (builder relaxed: allow)  // explicit carve-out, not silent fallthrough
       else:
            throw DENY: "tool-allowlist: command not allowlisted for role <role>"
            (with hint to add to allowed_bash_prefixes in hook-config or use ask path)
```

Key differences from V1:

| Property | V1 | V2 |
|----------|----|----|
| Non-matching bash in strict + active issue | Allowed (step 9 sentinel fires) | **Denied** unless allowlisted |
| Non-matching bash in relaxed (builder) | Allowed (step 7) | Allowed but labeled explicitly `builder-relaxed-allowlist-bypass` in logs; non-builder roles still denied |
| Allowlist per-role | `allowed_bash_prefixes` global + `agent_overrides.by_type.<role>.allowed_bash_prefixes` replacement only | Same mechanism, but `allowed_bash_for_role` is the resolved per-role set (global default + `+key` overlay + by_type replacement). Builder's `allowed_bash_prefixes: ["opencode ", "cargo …"]` stays builder-only; reviewer/auditor get the restricted `rtk`/`crosslink`/`git status` set from hook-config |
| Logging | `ALLOW: allowed bash` | `ALLOW: tool-allowlist hit` vs `BLOCK: tool-allowlist deny role=X cmd=…` + `intervention` hint |

#### 5.1.2 Configuration

Reuse the existing `hook-config.json` + `hook-config.local.json` + `+key` overlay mechanism — no new file. The V2 interpretation is:

* `allowed_bash_prefixes` in root = orchestrator default (global bash surface).
* `agent_overrides.by_type.builder.allowed_bash_prefixes` = builder additions (replaces allowed set for that type if present, as today — `loadConfig` at line 449 + `applyAgentTypeOverride` at 1216). V2 documents that `by_type.*.allowed_bash_prefixes` **replaces** the root list for that type; use `+allowed_bash_prefixes` in the overlay to extend rather than replace.
* New config key `tool_allowlist_mode: "deny_by_default" | "fast_path"` — default `fast_path` at rollout (backward-compatible), flipped to `deny_by_default` once per-role sets are audited (phased rollout §6.4). This keeps the commit-series green while the allowlists are audited for false positives.

#### 5.1.3 Filesystem tool allowlist (same table, different tool names)

`write`/`edit`/`apply_patch` and MCP filesystem tools are already gated by orchestrator-guard. In V2 `crosslink-guard` also intercepts them for **path** purposes (§5.2), but the *tool* decision is:

* Orchestrator / reviewer / auditor: `write`/`edit`/`apply_patch` → **deny** (always, except `~/.muse/` exemption + explicit path allowlist for `.kickoff-status` family).
* Builder: `write`/`edit` → allowed subject to path-allowlist (§5.2) + active-issue gate.
* MCP tools: `filesystem_write_file`/`filesystem_edit_file`/`filesystem_create_directory`/`filesystem_move_file` → same decision; V2 `crosslink-guard` must handle them even if `orchestrator-guard` is primary — defense in depth for defense-widening after #425's `create_directory`/`move_file` gap.

#### 5.1.4 Why this shape

*Choosing allowlist deny-by-default over blocklist augmentation* because the reviewer/auditor attack surface is *large* (reviewed report claim a lists `npm run`, `cargo`, `opencode --pure`, redirect, interpreter trampoline classes). A blocklist fix (adding each newly discovered tool to `blocked_git_commands`) is an endless regression source; allowlist deny-by-default closes the class.

### 5.2 Path-allowlist — closing the file-system leg

**Goal:** V2 adds a path predicate so even an allowlisted tool cannot reach trust-root paths or paths outside the project sandbox without explicit allowance.

#### 5.2.1 Predicate

```
function isPathAllowed(
  filePath: string,      // resolved absolute, after symlink + workdir + "workdir" param
  tool: string,
  role: string,
  crosslinkDir: string | null,
  projectDir: string
): boolean
```

* **Canonicalization:** `path.resolve(projectDir, filePath)` + `fs.realpathSync` where available (no shell-out, catch on missing). Without canonicalization, `../.crosslink/hook-config.json` or symlink bypass would defeat the list.
* **Trusted roots to deny unconditionally (overrides any allow entry):**

  * `path.join(crosslinkDir, "hook-config.json")`
  * `path.join(crosslinkDir, "hook-config.local.json")`
  * `path.join(crosslinkDir, "issues.db")` (read allowed via SQL in gate; write never)
  * `path.join(crosslinkDir, "agent.json")`
  * `path.join(projectDir, ".opencode/opencode.json")` + `.opencode/plugins/*.ts`
  * `path.join(projectDir, ".opencode/agents/*.md")` (permission frontmatter)
  * For reviewer/auditor: everything outside `projectDir` (including `/tmp` writes via bash redirect — enforced by bash path extraction below).

* **Allowlist entries** (per-role overlays, paths relative to `projectDir`):

  * Default builder allowlist: `projectDir/**/*` except the deny set above + `projectDir/.crosslink/.active-issue` is readAllow/writeAllow only via the gated git path (not direct edit).
  * Reviewer/auditor default: `projectDir/.kickoff-status` writes only (the narrow #434 exemption: basename exactly `.kickoff-status`) + project files for `rtk` read tools (read-only — enforced by `orchestrator-guard` today, but V2 crosslink-guard adds a read-path allow for `filesystem_read_*` so the auditor can do its job without falling back to `cat` trampolines).

#### 5.2.2 Bash file-path extraction

Bash is unstructured: only bash commands that *are* file-path bearing need path enforcement. V2 extracts a **conservative** set using the same quote-aware scan as `hasUnattestable` in rtk-guard:

* Trigger tokens: `cat`, `head`, `tail`, `grep -R`, `find`, `echo ... >`, `cp`, `mv`, `rm`, `adb`-like custom. For unrecognized commands, path gate is skipped (fail to tool-allowlist instead — deny-by-default covers it).
* Extract the first non-flag argument after the trigger; resolve against `workdir` param or `process.cwd()`.

**Explicitly out of scope for V1 of the path gate:** full POSIX shell AST parsing (Qwen H-02 bypass classes `$(...)`, process substitution, env variable expansion). Bash path-allowlist is best-effort; the true hardening for worst-case bypass is tool-allowlist deny + the permission engine's `bash: "*": deny`.

#### 5.2.3 Filesystem tool vs bash duality

The filesystem surface arrives through three channels, all of which V2 covers by sharing `isPathAllowed`:

| Channel | Hook tool | V2 handler |
|---------|-----------|------------|
| Native opencode write/edit/apply_patch | `write`, `edit`, `apply_patch` | `isPathAllowed(output.args.filePath)` |
| MCP filesystem | `filesystem_write_file`, `filesystem_edit_file`, `filesystem_create_directory`, `filesystem_move_file` | `isPathAllowed(output.args.path)` + `destination/output` |
| Bash trampoline | `bash` command | Conservative arg-extraction then `isPathAllowed(arg)` |

The MCP filesystem server's root (`/home/claude-code/projects/ASES`) being the main repo rather than the worktree (hy3 S5) is treated as a **misconfiguration** to be hardened by the path gate: even if the MCP root points at the wrong tree, the gate denies writes to worktree trust roots sibling to the main repo.

#### 5.2.4 Overlapping existing path layer

Opencode's `external_directory: {"*": "ask", "/tmp/*": "allow"}` is an *additional* permission-engine layer. Under `--auto` (every tmux kickoff) `"ask"` is auto-approved (reviewed report §2.4 hy3 M7), so V2 treats `external_directory` as **supplementary** — it is not relied upon as the deny. The V2 path gate runs regardless of `--auto`.

### 5.3 Kill-pause — making the operator kill switch authoritative

#### 5.3.1 Ordering (V2)

The revised priority is document-order and test-order:

```
0. Crosslink health (halt)
1. Kill-pause ← AUTHORITATIVE, highest non-health priority
2. Claude memory exemption
3. Blocked git
4. Gated git / gated bash (model)
5. Issue-close discipline
6. Tool-allowlist (deny-by-default) + path-allowlist
7. Active-issue / relaxed fallbacks
8. Strict no-issue block
```

Kill-pause is moved explicitly *before* the `~/.claude/` exemption and disconnected from any subsequent fast-path that could swallow it (the sentinel active-issue path cannot bypass it).

#### 5.3.2 Fail semantics — fail-closed when operator intent is explicit

* **V1 behavior:** `checkControlFlags` returns on `!result` (crosslink unavailable) and on exit 0 (no flags) — both are passthroughs, labeled `// fail open` at 636.
* **V2 behavior:**

  * If `crosslink` is unavailable **and** `.crosslink/.pause` or `.crosslink/.kill` sentinel file exists on disk (laid by the dashboard as a sibling to the CLI availability check), V2 **blocks** (fail-closed). The CLI is best-effort; the filesystem sentinel is not.
  * If neither sentinel nor CLI result is available, V2 **blocks writes and non-allowed bash** but **allows reads** (`read`/`grep`/`glob`), degrading to read-only — the "halt > warn > suggest" gradation from #514 extended to kill.
  * The health gate (§5.5's counterpart) already blocks all tool calls when CLI/DB/hub-cache are corrupt/locked; kill-pause's fail-closed reinforces that rather than duplicating it.

#### 5.3.3 Signal surface

* Primary: `crosslink agent flags --strict` exit 2 JSON (as today).
* Secondary: `crosslink agent flags` without `--strict` (if the flag ever changes meaning).
* Tertiary: on-disk sentinel files `.crosslink/.pause` / `.crosslink/.kill` (10-line addition, matches the 15s systemd watcher's polling cadence so the operator's dashboard action does not require a live CLI).
* Message: today's kill/pause block strings are kept verbatim (they already instruct the model to summarize and exit cleanly), plus a 1-line fix: the `reprioritise` hint is surfaced only after a resume, not after a kill.

### 5.4 Gated git — hardening the normalization and the sentinel fast path

#### 5.4.1 What V2 keeps

* Global-flag stripping (`-C`, `--git-dir`, `--work-tree`, `-c`) + loop over `rtk ` prefixes.
* `matchesCommandList` AND `isAllowedBash` structure (chain splitting), but with widened separators (below).
* `.active-issue` sentinel fast path and comment-discipline (`--kind plan` before commit, `--kind result` before close).
* `by_type` overrides for `orchestrator` (gates `git commit` + `git merge`) vs `reviewer`/`auditor` (block `git commit` entirely).

#### 5.4.2 What V2 hardens

* **Separators:** split on all of `&&`, `||`, `;`, `|`, `&`, `()` (still quote-aware). The three-entry `[" && ", " ; ", " | "]` list is expanded to a regex `/(?:\s*(?:&&|\|\||[;|&()])\s*)/` applied inside quotes only when not single-quoted. Each sub-command is then trimmed + `rtk`-stripped before matching.
* **Global flags:** add `--work-tree=` (already present), `--git-dir=` (already present), plus `--config`/`-c key=value` forms for `git -c`.
* **Commit message tampering:** `git commit --no-verify`, `GIT_EDITOR=true`, `GIT_SEQUENCE_EDITOR=:` are not denied — they are pre-commit-hook bypasses, not git-write bypasses. V2 notes them as out of scope and relies on post-commit auditing (the `issues.db` comment discipline is not a safety gate for pre-commit hook content).
* **Comment discipline mode:** `comment_discipline: "encouraged"` stays the default. Flipping to `"required"` is an independent rollout gated on audit of existing issue flows (many short-lived fixes create issues without a plan comment and rely on the reminder path).

#### 5.4.3 Sentinel trust — validating the fast path

* `.active-issue` is currently trusted as "active issue exists" on its own. V2 adds a **one-shot validation**: on the first gated git or strict write after sentinel is observed, also query `crosslink session status --json` (asynchronously, non-blocking for that call, but memoize the validation result for 60s). If the sentinel's issue ID disagrees with `session.status.working_on.id` by more than one ID window (sibling branch), log `SENTINEL_MISMATCH` and require a `crosslink session work <id>` before the *next* gated operation — the current operation still passes, so this is not a commit-breaking check, but it prevents a long-lived stale sentinel from masking an abandoned session.
* The `.active-issue` path is also excluded from the path-allowlist's unconditional deny (it must be writable by the builder to track work), but direct `edit` of `.active-issue` is denied outside the `crosslink session work` codepath — enforced by a literal path deny on `write`/`edit` to `.active-issue` unless `CROSSLINK_AGENT_TYPE=builder` and `tool.execute.before` was reached via `crosslink session work` (not reliably detectable — so V2 instead allows direct writes to `.active-issue` but validates as above, favoring practicality over perfect mediation on one metadata file).

### 5.5 Tool-allowlist, path-allowlist, kill-pause, gated git — priority summary

| Priority | Gate | What it governs | Intervenes on | V1 status | V2 change |
|----------|------|-----------------|---------------|-----------|-----------|
| 0 | Crosslink health | CLI/DB/hub-cache availability (fail-closed) | all tools | Exists (#514), lenient on hub-cache in worktrees | Keep; tighten hub-cache warning → block for stale sentinel age >24h |
| 1 | Kill-pause | Operator kill/pause flags (+ sentinel) | all writes + non-allowed bash | Exists, fails open on CLI unavailability | **Reorder before Claude exemption + fail-closed on sentinel** |
| 2 | Claude memory | `~/.claude/` write exemption | write/edit only | Exists | Keep |
| 3 | Blocked git | `blocked_git_commands` normalized + chained | bash | Exists (correct for canonical forms) | **Widen separators + global flags** |
| 4 | Gated git | `gated_git_commands` + active-issue + plan comment | bash | Exists | Keep + harden sentinel validation |
| 4b | Gated bash (model) | `gated_bash_commands` + approval gate | bash Task/kickoff | Exists (#508) | Keep |
| 6 | Tool-allowlist | `allowed_bash_prefixes` per-role deny-by-default | bash | Fast-path only | **Promote to denying surface** |
| 6b | Path-allowlist | `isPathAllowed` for filesystem + bash paths | write/edit/MCP/bash | Absent | **New gate** |
| 7 | Active-issue | Sentinel + session status | write/edit/non-allowed bash | Exists | Keep as fallback after allowlists |
| 8 | Strict no-issue | Final block | write/edit/non-allowed bash | Exists | Keep |

---

## 6. Orchestrator / RTK Implications — Sketch for the Next Pass

### 6.1 Orchestrator-guard

No structural change for Beta TUI parity until S1 plugin parity exists. On S2, orchestrator-guard remains the **sole** write-block for non-Builder roles (the #33677 fallback). V2 additions:

* Add a one-line re-export notice: `orchestrator-guard` now consults the shared `isPathAllowed` definition for the narrow `.kickoff-status` exemption — the exemption path check moves from basename-only to resolved-path check (prevents `/tmp/kickoff-status` masquerading if bash redirect were ever allowed for that role).
* Task-gated model approval already handled; no change.

### 6.2 RTK-guard

* Transparent rewrite is **fail-open** (binary gate, version gate, latency p95, unattestable scan all degrade to pass-through). V2 preserves that invariant — RTK is an optimization, not a boundary.
* One interaction: when `--model misspecification` tool-allowlist flips to deny, a `git` command rewritten from `git status` → `rtk read ...` will be evaluated **as the rewritten string** — so `rtk read` must be in the allowlist for the rewritten sub-command to still be allowed. Today's hook-config already allowlists `rtk read` for reviewer/auditor; V2 documents that invariant explicitly.

---

## 7. Rollout Plan (phased — keeps the commit series green)

| Phase | What | Flag | Test | Risk |
|-------|------|------|------|------|
| **P0 — no-behavior change** | Land `isPathAllowed` + `tool_allowlist_mode: fast_path` default + widened separators as fast-path additions (no deny yet) | none | `crosslink-guard.log` observe | None |
| **P1 — dry-run deny** | Switch `tool_allowlist_mode` to a logging-only `deny_would_block` mode for one distribution cycle (log BLOCK without throwing) | `tool_allowlist_mode: dry_run` | Tail logs for false positives (cargo test coverage, docs builds) | Log volume only |
| **P2 — enforce deny** | Flip to `deny_by_default`; path deny for trust roots enforced; kill-pause sentinel reordered + fail-closed | `tool_allowlist_mode: deny_by_default` | `scripts/guard-halt-cheapest-test.js`-style auto-hydration probe + direct `tool.execute.before` harness | Reviewer/auditor breakage if allowlist missing `rtk` |
| **P3 — S1 parity** | Decide v2-guard-for-S1 shape (v2 `execute` sandbox interceptor vs container wrapper vs CLI hardening) — separate design | separate issue | Beta TUI probe with successful `/tmp/opencode/v2-probe.log` | S1/S2 divergence reappears if not closed here |

The P0+P1 sequence is the project's cheapest-test-first posture: the most discriminating test before the behavioral change is a dry-run that can falsify the allowlist without blocking any agent.

---

## 8. HOW CERTAIN — the basis and confidence for every major claim

| # | Claim | HOW CERTAIN | WHY (basis) |
|---|-------|-------------|-------------|
| A | S1 beta TUI loads only global fallback plugins; worktree guards NOT loaded | **evidence-based** (inherited, not re-proven this pass) | Hookability Matrix Surface Re-Validation § (2026-08-24) says established empirically by #425 with debug config + runtime logs; operator handoff on #504 directs "do not re-prove"; corroborated indirectly by the v2-probe rejection on S2 (different surface, same loader family) |
| B | S2 worktree loads `.opencode/opencode.json` + all three guards | **proven** (observed) | This dispatch's `opencode.log` `loading plugin` events for `crosslink-guard.ts`/`orchestrator-guard.ts`/`rtk-guard.ts` at mtime `1787955...` plus `/tmp/orchestrator-guard.log` `Plugin initialised, projectDir: .../v2-guard-rewrite` at 22:54–22:55 with advancing `chat.params` events |
| C | Current file at 1597 lines is the deployed crosslink-guard; `opencode.json` at 46 lines; `hook-config.json` as quoted | **proven** (read) | Direct file reads with line counts; hashes captured by `crosslink session status` snapshot `209b99e807…` |
| D | `tool.execute.before` payload shape for filesystem + bash as documented in §3 | **proven** (code-read) | Direct reading of `output.args.command`, `output.args.filePath`, `output.args.path` consumers plus the prior probe's `output?.args` serializer shape — no inference about changed opencode API |
| E | `allowed_bash_prefixes` is an allow-fast-path not a denying surface | **proven** (code-read) | `crosslink-guard.ts` lines 1542–1592 control flow: early-return ALLOW at step 6 → fallthrough to relaxed-allow + active-issue sentinel, confirmed identically in the reviewed report §3.5 hy3 M3 |
| F | Path-allowlist absent; `hook-config.json` writable via `edit: allow` | **proven** (code-read) | No `isPathAllowed` predicate exists; `~/.muse/` only predicate is exemption not denylist; `isAgentContext` worktree + `agent_overrides.tracking_mode: relaxed` leaves builder on worktree with unrestricted path |
| G | Kill-pause fails open on CLI unavailability | **proven** (code-read) | Line 636 `if (!result) return; // crosslink not available or hung — fail open` |
| H | `normalizeGitCommand` loop + space-padded split covers canonical chaining only | **proven** (code-read) | Lines 144–172 + 497–563 + 525 `[" && ", " ; ", " | "]` literals; missing forms are visible absence |
| I | `orchestrator-guard` BLOCKED_TOOLS correct for filesystem, rtk-guard fail-open invariant holds | **evidence-based** | Direct read of `BLOCKED_TOOLS` including the #425 fix; `rtk-guard.ts` `if (state.mode === "no-op") return` + `try { … } catch { logErr }` path proven by the constant set, not a runtime fault injection |
| J | S1 payload shape inside `tool=execute` sandbox matches S2's `output.args` shape | **guess** | Reasoning by analogy from Hookability Matrix S1 column ("filesystem access routed through code-mode execute sandbox `tools.filesystem.*` inside tool=execute"), not a live capture — probe still pending |

---

## 9. WHAT-NOT-TESTED — what was explicitly not tested (negative-space disclosure)

The WHAT-NOT-TESTED clause is the sharpest class of false-confidence failure. A claim that states its untested assumptions is checkable by a thin consumer; a claim that hides them is not.

1. **No live Beta TUI (S1) probe was run in this pass.** S1 plugin loading and the `tool.execute` sandbox payload were not captured into `/tmp/opencode/v2-probe.log` here — per the #504 handoff, re-proof was intentionally skipped. The probe artefact `v2-probe.ts` exists in the forensics worktree `pp3g-hK0g-…` and is preserved for the next S1 pass, but it has not written a log in this worktree.
2. **No runtime enforcement harness was run against V2 logic** (the design is written but not yet implemented as `crosslink-guard.ts` edits). The phased dry-run (§7 P1) harness that would falsify the allowlist — a `dry_run` mode that logs would-be blocks without throwing — has not been built or run.
3. **Instrumented kill-pause fail-closed was not fault-injected.** The sentinel fallback (`.crosslink/.kill` fs file when `crosslink agent flags` returns null) and the read-only degradation path have not been injected against a real `crosslink` unavailability — they are code-shaped.
4. **Full bash AST path extraction not tested against POSIX edge cases** (`$()` inside double quotes is now flagged like rtk-guard, but `for i in …; do git push; done`, process substitution `> >(...)`, env expansion `$GIT_DIR`, nested subshells, and heredocs were all not exercised). The design acknowledges bash path-allowlist is best-effort and deferred.
5. **No cross-agent race test on the by_type resolution fallback.** The `resolveAgentType` → `builder` default and per-session map clobbering class (§3.1 of reviewed report claim f, hy3 M4a) were analyzed statically; no session was forced into the unresolved state to demonstrate a reviewer actually committing under the fallback.
6. **No V1→V2 log-diffusion rehearsal.** The log files `/tmp/crosslink-guard.log` (now 4 MB, inherited) roll across sessions without rotation; the new V2 log tags (`BLOCK: tool-allowlist deny`, `SENTINEL_MISMATCH`) have not been tail-verified against a real multi-agent swarm to confirm they do not alias prior log consumers.
7. **No S1/S2 divergence fix evaluated.** Whether the Beta TUI parity shape should be (a) a v2 `execute` sandbox interceptor for `tools.filesystem.*`, (b) an `execute` deny, or (c) CLI/wrapper hardening remains undecided — marked sketch in §6.1. That choice requires an S1 parity design review.

---

## Appendix A — Files Read and Evidence Anchors

| Path | Lines / note |
|------|--------------|
| `.opencode/plugins/crosslink-guard.ts` | 1597 lines (full read, both halves) |
| `.opencode/plugins/orchestrator-guard.ts` | 335 lines |
| `.opencode/plugins/rtk-guard.ts` | 415 lines |
| `.opencode/opencode.json` | 46 lines |
| `.crosslink/hook-config.json` | 252 lines |
| `docs/research/registry/Hookability-Matrix.md` | Surface Re-Validation + §1–§5 sampled (full file not quoted) |
| `docs/research/agent-tooling-and-permission-enforcement-reviewed.md` | §1–§2 full (534 lines from template 2026-08-09) |
| `/tmp/crosslink-guard.log` | tail 100 sampled (4 MB total, session-filtered at 22:54–22:55) |
| `/tmp/orchestrator-guard.log` | tail 50 sampled (1.2 MB total) |
| `~/.local/share/opencode/log/opencode.log` | `loading plugin` + `failed to load plugin` + `NpmInstallFailedError` sampled for runs `0ffdfcad`/`922c9a5b`/`a20374e4` |
| `~/.local/share/opencode/log/opencode.log` | `v2-probe` not-loaded evidence (all attempts `SchemaError(Expected object at ["default"])`) |
| `/tmp/opencode/v2-probe.log` | confirmed absent (never written; probe never loaded) |
| `pp3g-hK0g-…/.opencode/plugins/v2-probe.ts` | 83 lines, preserved forensics |

## Appendix B — V2 `crosslink-guard.ts` Skeleton Diff (what changes, not the full patch)

```diff
 // 0. health (existing, unchanged except hub-cache leniency tightened)
 // 1. kill/pause  [REORDERED]  + fail-closed on .crosslink/.kill sentinel
 await checkControlFlags(shell, tmpCrosslinkDir, throwBlock);
+// inside checkControlFlags: if (!result) check sentinel file; if exists → throw
-// inside tool.execute.before: move kill/pause BEFORE Claude exemption
 // 2. Claude memory exemption (kept, now priority 2)

 // 3. blocked git: widen separators
-function matchesCommandList(command, list) { split on /\\s*(?:&&|\\|\\||[;|&()])\\s*/ quote-aware }
+function matchesCommandList(command, list) { new split + per-part rtk+flag strip }

 // 6. tool-allowlist: NEW deny mode
-if (isAllowedBash(command, config.allowed_bash)) return; // fast path
+if (isAllowedBash(command, resolvedAllowedForRole)) { log ALLOW; return; }
+if (config.tool_allowlist_mode === "deny_by_default"
+    && !(config.tracking_mode === "relaxed" && isAgent && role==="builder")) {
+  throw new Error(TOOL_ALLOWLIST_DENY_MESSAGE);
+}

 // 6b. path-allowlist: NEW gate (after tool-allowlist)
+if (toolLower === "write" || toolLower === "edit" || toolLower.startsWith("filesystem_")) {
+  const p = resolveAbsolute(output.args.filePath ?? output.args.path, projectDir, output.args.workdir);
+  if (!isPathAllowed(p, toolLower, role, crosslinkDir, projectDir)) throw new Error(PATH_DENY);
+}
+if (toolLower === "bash") {
+  const extracted = extractBashFileArgs(command); // best-effort
+  for (const p of extracted) if (!isPathAllowed(p, "bash", role, crosslinkDir, projectDir)) throw new Error(PATH_DENY);
+}
```

The reviewer consuming this design can check the real V1 file at the listed line numbers; any drift in those numbers between `feature/v2-guard-rewrite` HEAD (`020c6409` series checkpoints) and implementation time should be treated as an explicit re-validation requirement for the diff.

## Appendix C — Attribution

This design re-uses the reasoning-certainty framing from AGENTS.md and the reviewed report's eight-external-review synthesis style (claims A–J table in §8, WHAT-NOT-TESTED list in §9). The Beta TUI surface tag convention (`[S1]`/`[S2]`/`[surface-independent]`) and evidence language are taken verbatim from the Hookability Matrix per #425 — the operator-maintained source of truth for guard validity.
