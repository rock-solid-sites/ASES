---
name: kickoff
description: Use to launch a background Claude agent in tmux (or docker/podman) to implement a feature end-to-end. Delegates worktree creation, prompt building, and session launch to `crosslink kickoff run`, then prints how to attach (`tmux attach -t <session>`) and check status (`/check`). Trigger when the user says "kick off an agent for X", "/kickoff …", or asks for a background agent / sub-agent / worker to do a feature.
---

# Kickoff — background agent for a feature

The user provides a feature description (e.g. "add batch retry logic") and optionally additional context. Delegate to the `crosslink kickoff run` CLI command which handles worktree creation, agent prompt generation, and tmux session launch.

## Arguments

The user may pass these flags after the feature description:

- `--verify <level>`: Controls post-implementation verification depth.
  - `local` (default): Local tests + self-review checklist only.
  - `ci`: Push branch, open draft PR, wait for CI to pass, fix failures.
  - `thorough`: Everything in `ci` plus a structured adversarial self-review.
- `--issue <id>`: Use an existing crosslink issue instead of creating a new one.
- `--container <runtime>`: Use `docker` or `podman` instead of local tmux. Default: `none`.
- `--model <model>`: LLM model to use. Default: `opus`.
- `--timeout <duration>`: Max runtime (e.g. `30m`, `45m`). **Default: `1h` — do NOT rely on it. Always pass a task-matched timeout** (see "Task-matched timeouts" below). Never use a blanket `1h` on every kickoff; it overcommits and starves the operator of progress feedback.
- All other text is the feature description.

**Parsing**: Split arguments on whitespace. Extract recognized `--flag value` pairs. Everything remaining is the feature description.

## Task-matched timeouts

Choose `--timeout` from the task type — never a fixed 1h. Ceilings include
setup and verification headroom (evidence: #120's 4-file fix took ~3 min real
work on a 40m timeout; review/doc/port tasks all landed in <=30m):

| Task type | `--timeout` |
|-----------|-------------|
| Trivial (1-2 files, small change) | `10m` |
| Documentation / simple change | `20m` |
| Review / audit (read-only) | `20m` |
| Port / multi-file change | `30m` |
| Complex / multi-phase feature | `45m+` — suggest swarm, not kickoff |

**Progress checkpoints:** the child agent posts milestone checkpoint comments
(`--kind observation`) and syncs after each — this is how the operator sees
progress before the timeout. Cadence derives from the ~5-minute loss-tolerance
budget (playbook §5.4): builders commit incrementally every ~5 minutes of work;
read-only roles treat comment+sync as their commit at ~5-minute cadence. The
~4 cap is not a durability throttle. If the user asks to check on an agent,
look at its issue's checkpoint comments (`crosslink issue show <id>`), not
just `.kickoff-status`. Timeout exceeded, or no new commit / no new synced
position for >2x the ~5-minute budget, means likely stalled — investigate (see
the `agent-orchestration-playbook.md` §5.3/§5.4).

## Steps

1. **Validate prerequisites**: Check that `tmux` and `claude` are available (for local mode). If `--verify ci` or `--verify thorough`, check that `gh` is available. If missing, tell the user what to install and stop.

2. **Build the crosslink kickoff command**: Map parsed arguments to CLI flags:

   ```bash
   crosslink kickoff run "<feature description>" \
     --verify <level> \
     --container <runtime> \
     --model <model> \
     --timeout <task-matched duration per the table above, e.g. 20m or 30m>
   ```

   Add `--issue <id>` if the user specified one. Add `--dry-run` if the user asked for a dry run.

3. **Run the command**: Execute `crosslink kickoff run` with all flags. The CLI handles:
   - Creating the feature branch and worktree
   - Creating or assigning the crosslink issue
   - Initializing the agent identity
   - Detecting project conventions
   - Building the self-contained KICKOFF.md prompt
   - Launching the tmux session (or container)

4. **Report**: The CLI prints the summary. Relay it to the user. Remind them to:
   - Approve trust: `tmux attach -t <session-name>`
   - Check status: `crosslink kickoff status <agent-id>` or invoke the `check` skill on `<session-name>`
   - Follow progress via the agent's checkpoint comments on the issue (`crosslink issue show <issue-id>`), which the agent syncs after posting

## Constraints

- Never force-push or delete branches.
- Do not push the branch to a remote from this skill. (The child agent handles pushing when `--verify ci` or `--verify thorough`.)
- All prompt building and agent lifecycle is handled by `crosslink kickoff run`.
- If a tmux session with the same name already exists, the CLI appends a random suffix automatically.
