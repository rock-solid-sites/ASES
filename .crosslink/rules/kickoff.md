# KICKOFF: {description}

## Context

- **Issue**: #{issue_id}
- **Branch**: `{branch_name}`

## Blocked Actions

Git commands blocked by project policy — ask the user to run these manually:

- `git push`, `git merge`, `git rebase`, `git cherry-pick`
- `git reset`, `git checkout .`, `git restore .`, `git clean`
- `git stash`, `git tag`, `git am`, `git apply`
- `git branch -d`, `git branch -D`, `git branch -m`

**Gated** (require active issue): `git commit`
**Always allowed**: `git status`, `git diff`, `git log`, `git show`, `git branch` (listing)

## Instructions

1. Run `crosslink agent status` then `crosslink sync`
2. Start session: `crosslink session start && crosslink session work {issue_id}`
3. Read AGENTS.md and explore relevant code before making changes
4. Document your plan: `crosslink issue comment {issue_id} "Plan: <approach>" --kind plan`
5. Implement fully — no stubs or placeholders
6. Document decisions and discoveries as you work
7. Sync periodically: `crosslink sync` — and always sync after posting a checkpoint comment (see below)
8. Log interventions if blocked: `crosslink issue intervene {issue_id} "..." --trigger <type>`

## Progress Check-Ins

The operator watches your progress through **checkpoint comments** on this
issue — never wait blind until timeout. You MUST post milestone checkpoints
and **sync after each one**. Session-action breadcrumbs
(`crosslink session action "..."`) are supplementary telemetry only; they do
not reach the hub and are not a substitute.

Post checkpoint comments at these milestones — the operator-visibility
skeleton, NOT a durability cap:

1. **POST-PLAN** — immediately after your plan comment (step 4):
   `crosslink issue comment {issue_id} "[PROGRESS] state=working completed=<plan posted> next=<first step> blocker=none" --kind observation`
   then `crosslink sync`.
2. **MIDPOINT** — after the first meaningful unit of work completes
   (required for tasks estimated >15m; optional for <=10m trivial tasks):
   `crosslink issue comment {issue_id} "[PROGRESS] state=working completed=<one line> next=<what's next> blocker=none" --kind observation`
   then `crosslink sync`.
3. **BLOCKER-OR-VERIFY** — if blocked, post immediately:
   `crosslink issue comment {issue_id} "[BLOCKED] state=blocked completed=<one line> next=<what's next> blocker=<detail>" --kind observation`
   then `crosslink sync`. If verification is in progress, post
   `[VERIFY] state=verifying completed=... next=... blocker=none` instead.
4. **FINAL** — your `--kind result` comment before session end (see Final
   Steps), then `crosslink sync`.

Required fields in every checkpoint: `state` (working/blocked/verifying),
`completed` (one line), `next` (what's next, or 'done'), `blocker` (detail or
none). Milestone-based, never per-action — per-item commenting is
over-checkpointing.

**Durability cadence (role-aware):** checkpointing is a **durability**
mechanism, not a reporting mechanism. Cadence derives from the ~5-minute
loss-tolerance budget (playbook §5.4), not from a fixed comment count.
- **Builders:** commit incrementally every ~5 minutes of work — small,
  resume-friendly commits, so a death loses at most one commit's worth.
- **Reviewer/auditor roles:** treat `crosslink issue comment {issue_id}
  "<position>" --kind observation && crosslink sync` as your commit, at the
  same ~5-minute cadence.
The ~4-comment cap is not a durability throttle — durability writes are not
throttled; the ~5-minute budget IS the bound (not 'unbounded').

**Missed check-in escalation:** if you realize a checkpoint was missed, post
it immediately and continue — never batch checkpoints at the end. A silent
agent is indistinguishable from a dead one; checkpoints are how the operator
distinguishes working from stalled (timeout exceeded = likely stalled; no new
commit / no new synced position for >2x the ~5-minute budget = likely stalled).

## Code Quality

- No stubs: no TODO/FIXME/pass/`...`/`unimplemented!()`
- Read files before editing
- Run tests after changes
- Use `nohup cmd > /tmp/file.log 2>&1 &` for background processes

## Reviewing Previous Phase Output

If your task is to review work from a previous phase, use git — not direct filesystem access. Each worktree shares the same git object store.

1. Fetch the previous phase's branch:
   `git fetch . feature/<phase-branch-name>`
2. View changes:
   `git diff main...feature/<phase-branch-name>`
3. Read specific files from the fetched branch:
   `git show feature/<phase-branch-name>:<path/to/file>`

Cross-worktree filesystem access is blocked. Git-based review works within the sandbox.

## Final Steps

- `crosslink sync` — push state to hub
- `crosslink session end --notes "Completed: <summary>"`
- Write `DONE` to `.kickoff-status` when finished
