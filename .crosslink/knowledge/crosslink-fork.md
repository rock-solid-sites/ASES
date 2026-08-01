# Crosslink Fork

The project uses a custom fork of crosslink at `/home/claude-code/projects/crosslink` with changes that aren't yet merged upstream (PR #44 on dollspace-gay/crosslink).

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
- **Per-agent-type overrides**: `agent_overrides.by_type.<type>` (reviewer/auditor)
  replaces the shared blocked/gated lists for that role — e.g. reviewer/auditor block
  `git commit` outright while builder keeps it gated. The active type is resolved at
  runtime from the `CROSSLINK_AGENT_TYPE` env var, which the `claude` wrapper exports
  from the `--agent <type>` launch flag.
- **Blocked vs gated**: `blocked_git_commands` are hard-blocked (MANDATORY COMPLIANCE
  message); `gated_git_commands` (`git commit`) are allowed-with-active-issue.

Verification (5th round, PASS 5/5): reviewer agent — `git status`/`git log`/`ls`
SUCCEED, `git push` BLOCKED, `git commit` BLOCKED. Guard log confirmed `by_type override
applied for agent: reviewer`.

## Known Issues

- Symlink/copy code in run.rs for .opencode/ propagation is unreliable (worked around by committing agent files)
- `--dangerously-skip-permissions` and `--permission-mode` are Claude Code only; ignored by wrapper
- DB rehydration: a `sync.fetch()` can rehydrate the SQLite DB from a stale hub state, dropping local-only issues/comments (tracked ASES #119; recovered via `crosslink compact`)

## Zen free models (resolved #103)

The free Zen models were hidden by the `dynamic-models.ts` / `plugin.ts` plugins in `~/.config/opencode/plugins/`, which added `opencode` to `disabled_providers` and wiped `provider.opencode.models`.

Fix (option 2 — whitelist free models only):

- Removed `opencode` from `defaultDisabled` and `hideProviders`
- Added `cfg.provider["opencode"].whitelist = [big-pickle, deepseek-v4-flash-free, laguna-s-2.1-free, ling-3.0-flash-free, mimo-v2.5-free, nemotron-3-ultra-free, north-mini-code-free]`

Verified: `opencode models opencode` lists exactly the 7 free models; 0 paid Zen models exposed; `opencode run --model opencode/deepseek-v4-flash-free` works end-to-end. Free Zen calls work unauthenticated (no `OPENCODE_API_KEY` or Zen credits needed); the Go key also authenticates.

## Next Session

- Evaluate [OpenCode Fusion](https://github.com/mihneaptu/opencode-fusion) as potential replacement for our custom agent/permission/template work
