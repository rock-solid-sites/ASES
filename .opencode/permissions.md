# Permissions — ASES Agent Definitions

**Snapshot** of the four roles' permission maps. **NOT the source of truth** —
the live sources are `.opencode/agents/*.md`, `.opencode/opencode.json`, and
`.crosslink/hook-config.json`. This file can go stale; if a setting here
disagrees with an agent definition, the plugin, or the running behavior, the
agent definition and the live CLI win (§5 in `SESSION-START.md`).

---

## Orchestrator (Primary Agent)

| Permission | Setting | Rationale |
|------------|---------|-----------|
| `edit` | `deny` | Must never write project files (Builder's job) |
| `bash` | `{"*": "deny", "crosslink *": "allow", "opencode models *": "allow", "git status *": "allow", "git diff *": "allow", "git log *": "allow", "git show *": "allow", "git branch *": "allow", "git commit *": "allow", "git merge *": "allow", "ls *": "allow", "cat *": "allow", "rtk *": "allow"}` | Coordination shell: crosslink CLI, model catalog, read-only git, the two gated git commands, and `ls`/`cat`/`rtk` |
| `task` | `{"*": "deny", "builder": "allow", "reviewer": "allow", "auditor": "allow"}` | May only delegate to the three specialist subagents |
| `question` | `allow` | Must be able to ask user for direction on delegation failure |
| `webfetch` | `deny` | No external fetching |
| `websearch` | `deny` | No external search |
| `read` | `allow` | Needs full read access to plan and coordinate |
| `glob` / `grep` / `list` | `allow` (inherited) | Needs to explore codebase |
| `model` | runtime-resolved (hook-config `sentinel.default_agent.model` / launch `--model`) — verify with `opencode models <provider>` | Not a static pin; stale pins are the #1 failure cause |

**Git write (ASES rule — deliberate deviation from tripn-astro, which has no git):**
- **Gated** (require active Crosslink issue): `git commit`, `git merge`
- **Blocked** (permanently): `git push` (incl. `--force`/`-f`), `git rebase`,
  `git cherry-pick`, `git reset`, `git clean`, `git checkout .`, `git restore .`,
  `git stash`, `git tag`, `git am`, `git apply`, `git branch -d/-D/-m`
- Enforced by `agent_overrides.by_type.orchestrator` in
  `.crosslink/hook-config.json` via the `crosslink-guard` plugin.

**Prompt-enforced rules (not expressible in permissions):**
- NEVER produce implementation, review verdict, or audit conclusion as own output
- On ANY delegation failure → HALT → `question` tool → wait for user → NO retry/substitution/self-execution
- Verify HEAD clean and on the expected branch before acting

---

## Builder (Subagent)

| Permission | Setting | Rationale |
|------------|---------|-----------|
| `edit` | `allow` | Implements approved changes |
| `bash` | `allow` | Runs build, lint, test, git commands |
| `task` | `deny` | Cannot spawn subagents |
| `question` | `ask` | May ask clarifying questions during work |
| `webfetch` | `allow` | May fetch external docs |
| `websearch` | `allow` | May search for solutions |
| `read` / `glob` / `grep` / `list` | `allow` | Full exploration access |
| `model` | runtime-resolved — verify with `opencode models <provider>` | Not a static pin; stale pins are the #1 failure cause |

**Git write:** `git commit` gated on an active issue; the shared blocked list
(push/merge/rebase/cherry-pick/reset/clean/checkout ./restore ./stash/tag/am/apply/branch -d/-D/-m)
is hard-blocked.

---

## Reviewer (Subagent)

| Permission | Setting | Rationale |
|------------|---------|-----------|
| `edit` | `deny` | Read-only review |
| `bash` | `{"*": "deny", "crosslink issue comment *": "allow", "crosslink issue show *": "allow", "crosslink session status *": "allow", "crosslink sync *": "allow", "crosslink knowledge search *": "allow", "crosslink knowledge list *": "allow", "crosslink knowledge add *": "allow", "crosslink knowledge edit *": "allow", "git status *": "allow", "git diff *": "allow", "git log *": "allow", "git show *": "allow", "git branch -a *": "allow", "git branch -r *": "allow", "git branch -vv *": "allow", "git branch --show-current *": "allow", "ls *": "allow", "cat *": "allow", "rtk read *": "allow", "rtk ls *": "allow", "rtk tree *": "allow", "rtk grep *": "allow", "rtk find *": "allow", "rtk wc *": "allow", "rtk diff *": "allow"}` | Narrow crosslink surface (comment/show, session status, sync, knowledge search/list/add/edit — no delete, no lifecycle/dispatch); read-only git (status/diff/log/show + branch listing forms), ls/cat, read-only rtk proxies (deny-by-default per #342) |
| `task` | `deny` | Cannot delegate |
| `question` | `deny` | No user interaction during review |
| `webfetch` | `allow` | May fetch external docs for reference |
| `websearch` | `deny` | No search needed |
| `read` / `glob` / `grep` / `list` | `allow` | Full read-only exploration |
| `model` | runtime-resolved — verify with `opencode models <provider>` | Not a static pin; stale pins are the #1 failure cause |

**Git write:** all git writes blocked, including `git commit` (read-only).

---

## Auditor (Subagent)

| Permission | Setting | Rationale |
|------------|---------|-----------|
| `edit` | `deny` | Read-only audit |
| `bash` | `{"*": "deny", "crosslink issue comment *": "allow", "crosslink issue show *": "allow", "crosslink session status *": "allow", "crosslink sync *": "allow", "crosslink knowledge search *": "allow", "crosslink knowledge list *": "allow", "crosslink knowledge add *": "allow", "crosslink knowledge edit *": "allow", "git status *": "allow", "git diff *": "allow", "git log *": "allow", "git show *": "allow", "git branch -a *": "allow", "git branch -r *": "allow", "git branch -vv *": "allow", "git branch --show-current *": "allow", "ls *": "allow", "cat *": "allow", "rtk read *": "allow", "rtk ls *": "allow", "rtk tree *": "allow", "rtk grep *": "allow", "rtk find *": "allow", "rtk wc *": "allow", "rtk diff *": "allow"}` | Narrow crosslink surface (comment/show, session status, sync, knowledge search/list/add/edit — no delete, no lifecycle/dispatch); read-only git (status/diff/log/show + branch listing forms), ls/cat, read-only rtk proxies (deny-by-default per #342) |
| `task` | `deny` | Cannot delegate |
| `question` | `deny` | No user interaction |
| `webfetch` | `allow` | May fetch external docs for architectural context |
| `websearch` | `deny` | No search needed |
| `read` / `glob` / `grep` / `list` | `allow` | Full read-only exploration |
| `model` | runtime-resolved — verify with `opencode models <provider>` | Not a static pin; stale pins are the #1 failure cause |

**Git write:** all git writes blocked, including `git commit` (read-only).

---

## Git Write Rules Summary

| Role | `git commit` | `git merge` | push / rebase / reset / clean / checkout . / restore . / stash / tag / am / apply / branch -d -D -m |
|------|--------------|-------------|--------------------------------------------------------------|
| Orchestrator | Gated (active issue) | Gated (active issue) | Blocked |
| Builder | Gated (active issue) | Blocked | Blocked |
| Reviewer | Blocked | Blocked | Blocked |
| Auditor | Blocked | Blocked | Blocked |

---

## Permission Model Notes

1. **File-write blocking (FIXED)** (OpenCode 1.18.x): `edit: deny` alone does not
   block writes to files inside the project worktree (upstream issue #33677) —
   native edit/write, `apply_patch`, and MCP `filesystem_write_file`/
   `filesystem_edit_file` all succeed regardless. **This gap is closed by the
   `orchestrator-guard.ts` plugin** (loaded via `.opencode/opencode.json`), which
   blocks all write-path tools at the `tool.execute.before` hook level for all
   agents except the Builder. The plugin requires an OpenCode restart after
   deployment.

2. **Subagent allowlist**: The `task` permission uses exact subagent names
   (`builder`, `reviewer`, `auditor`) as defined in `.opencode/opencode.json`.
   Adding new specialist agents requires updating both the Orchestrator's `task`
   allowlist and the new agent's definition.

3. **Orchestrator shell access**: The Orchestrator's `bash` permission is an
   explicit allowlist — `crosslink *`, `opencode models *`, read-only git, the
   two gated git commands, and `ls`/`cat`/`rtk`. The `git commit *` and
   `git merge *` patterns exist so the OpenCode matcher lets those commands reach
   the `crosslink-guard` plugin's active-issue gate; the gate itself lives in
   `by_type.orchestrator.gated_git_commands` (`.crosslink/hook-config.json`).

4. **Question tool in headless/SDK mode**: The `question` tool produces a
   blocking prompt waiting for stdin. In TUI mode this renders interactively; in
   SDK/headless mode it hangs until input arrives. This is acceptable — the
   Orchestrator halts and waits for human direction per protocol.

5. **Restart required**: Agent definitions, plugin registration, and
   `by_type` overrides are read at session start. Deploying a new role requires
   an OpenCode restart before the new permissions take effect.

6. **Meta-instruction compliance gap** — Process-level "how to work" instructions
   (e.g., delegate via subagents, use RTK prefixing) stated at task start have no
   structural enforcement. Unlike `edit`/`bash`/`task` which are permission-gated,
   tool-routing preferences are a decision-of-method failure with no re-check
   mechanism. The RTK half is resolved (structural — no OpenCode plugin exists for
   transparent command rewriting). The subagent-delegation half is a known,
   documented gap. See Knowledge page: `meta-instruction-compliance-gap`
   (`crosslink knowledge show meta-instruction-compliance-gap`).

---

## Version

- OpenCode: 1.18.11
- Config schema: https://opencode.ai/config.json
- Last updated: 2026-08-10
