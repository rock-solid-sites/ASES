# Crosslink Fork

The project uses a custom fork of crosslink at `/home/claude-code/projects/crosslink`. The upstream feature branch (PR #44 on dollspace-gay/crosslink, head `feat/43-configurable-kickoff-template`) was **merged upstream on 2026-08-01** (merge commit `26ee1885`, 18 files +646/-83). The upstream lint check failed on `cargo fmt` formatting-only diffs (`orchestrator.rs:67`, `token_usage.rs:408`, `launch.rs:229`) but the merge proceeded — cosmetic, not blocking.

## Fork Branches

- `fork-local/agents` is the **canonical agent-infrastructure branch** — it contains the local agent work (#43/#792/#794/#119/#138/#139).
- `main` is the clean upstream line.
- Do **not** merge `fork-local/agents` into `main`: the #160 audit found 10 conflicted files / 45 markers — the wrong direction.
- The V3 lock fix (`31a3e2e8`) is **not** yet on `fork-local`; the manual import is deferred and tracked as #166.

## Building

The binary must be rebuilt after code changes. Use lld to avoid OOM during linking:

```
CARGO_BUILD_JOBS=1 RUSTFLAGS="-C link-arg=-fuse-ld=lld" cargo install --path /home/claude-code/projects/crosslink/crosslink --force
```

If the linker is killed (SIGTERM), free memory by killing stale tmux sessions first.

## Key Features

- `agent.kickoff_template` and `agent.no_template` in hook-config.json
- Custom KICKOFF.md template at `~/.crosslink/rules/kickoff.md` (global fallback)
- `agent.type` and `agent.phase_types` for per-phase swarm agent types
- `agent.binary` support for opencode (defaults to claude)
- Placeholder substitution in custom templates (`{issue_id}`, `{branch_name}`, `{description}`)
- Swarm model reads from `sentinel.default_agent.model` instead of hardcoded "opus"

## Sandbox Permission Enforcement (resolved #109)

Kickoff agents run opencode with two plugins loaded from `.opencode/opencode.json`:
`crosslink-guard.ts` (git mutation blocking, gated commit, allowed-bash enforcement) and
`rtk-guard.ts` (transparent token-saving command rewriting).

Key mechanics:

- **rtk rewrite**: `git status` → `rtk git status`, `cat x` → `rtk read x`. The opencode
  built-in matcher evaluates the *mutated* command, so frontmatter `permission.bash`
  must allow both the plain and `rtk *` forms (the `"rtk *": allow` entries).
- **Per-agent-type overrides**: `agent_overrides.by_type.<type>` replaces the
  shared blocked/gated lists for that role — e.g. reviewer/auditor block
  `git commit` outright while builder keeps it gated, and orchestrator gates
  `git commit` **and** `git merge` while keeping push/rebase/reset/clean/etc.
  blocked (ASES gh#121). The active type is resolved at
  runtime from the `CROSSLINK_AGENT_TYPE` env var, which the `claude` wrapper
  exports from the `--agent <type>` launch flag.
- **Blocked vs gated**: `blocked_git_commands` are hard-blocked (MANDATORY COMPLIANCE
  message); `gated_git_commands` (`git commit`) are allowed-with-active-issue.

Verification (5th round, PASS 5/5): reviewer agent — `git status`/`git log`/`ls`
SUCCEED, `git push` BLOCKED, `git commit` BLOCKED. Guard log confirmed `by_type override
applied for agent: reviewer`.

## Known Issues

- Symlink/copy code in run.rs for .opencode/ propagation is unreliable (worked around by committing agent files)
- `--dangerously-skip-permissions` and `--permission-mode` are Claude Code only; ignored by wrapper
- DB rehydration: a `sync.fetch()` can rehydrate the SQLite DB from a stale hub state, dropping local-only issues/comments (tracked ASES #119; recovered via `crosslink compact`). **Root cause fixed 2026-08-06** — gate `maybe_auto_hydrate` v2 path on v3-ref presence (`hub_is_confidently_v2_only`, fail-closed), commit `ade6146b`, binary rebuilt + live-verified; `crosslink compact` remains the interim recovery for older binaries.

## Zen free models (resolved #103)

The free Zen models were hidden by the `dynamic-models.ts` / `plugin.ts` plugins in `~/.config/opencode/plugins/`, which added `opencode` to `disabled_providers` and wiped `provider.opencode.models`.

Fix (option 2 — whitelist free models only):

- Removed `opencode` from `defaultDisabled` and `hideProviders`
- Added `cfg.provider["opencode"].whitelist = [big-pickle, deepseek-v4-flash-free, laguna-s-2.1-free, ling-3.0-flash-free, mimo-v2.5-free, nemotron-3-ultra-free, north-mini-code-free]`

Verified: `opencode models opencode` lists exactly the 7 free models; 0 paid Zen models exposed; `opencode run --model opencode/deepseek-v4-flash-free` works end-to-end. Free Zen calls work unauthenticated (no `OPENCODE_API_KEY` or Zen credits needed); the Go key also authenticates.

## Next Session

- Evaluate [OpenCode Fusion](https://github.com/mihneaptu/opencode-fusion) as potential replacement for our custom agent/permission/template work
