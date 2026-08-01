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
4. Document your plan: `crosslink comment {issue_id} "Plan: <approach>" --kind plan`
5. Implement fully — no stubs or placeholders
6. Document decisions and discoveries as you work
7. Sync periodically: `crosslink sync`
8. Log interventions if blocked: `crosslink intervene {issue_id} "..." --trigger <type>`

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
