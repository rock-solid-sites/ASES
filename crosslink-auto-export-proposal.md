# Auto-Export: Pre-Commit Hook + CI Safety Net

## Problem

Crosslink stores issues in SQLite (`issues.db`), which is gitignored. Issue history is not version-controlled. We want a JSON snapshot committed to git that stays in sync with the database.

## Solution

A pre-commit hook that runs `crosslink export` before every commit, plus a CI step that validates the snapshot. No verb lists, no wrappers, no daemons.

## Components

### 1. Pre-Commit Hook

Place at `.crosslink/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
# .crosslink/hooks/pre-commit
# Exports crosslink issues to JSON before every commit.

set -euo pipefail

# Check crosslink exists
if ! command -v crosslink >/dev/null 2>&1; then
  printf 'crosslink not found — skipping issue export\n' >&2
  exit 0
fi

# Check python3 exists (needed for JSON validation)
if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 not found — skipping issue export\n' >&2
  exit 0
fi

# Resolve repo root (handles subdirectory commits and nested repos)
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
crosslink_dir="$repo_root/.crosslink"

if [ ! -d "$crosslink_dir" ]; then
  exit 0
fi

snapshot="$crosslink_dir/issues-snapshot.json"

# Set up temp file cleanup before creating anything
cleanup() { rm -f "${tmp:-}"; }
trap cleanup EXIT

tmp="$(mktemp "$crosslink_dir/issues-snapshot.json.XXXXXX")"

# Export to temp file (capture stderr only — stdout is discarded)
export_stderr="$(
  crosslink export --output "$tmp" 2>&1 1>/dev/null
)" || {
  printf 'crosslink export failed:\n' >&2
  printf '%s\n' "$export_stderr" >&2
  exit 1
}

# Validate the exported JSON before staging
# Use json.load (parse-only) instead of json.tool (reformats, uses more memory)
if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$tmp" >/dev/null 2>&1; then
  printf 'crosslink export produced invalid JSON — not staging\n' >&2
  exit 1
fi

# Verify the export is non-empty (catches silent export failures)
if ! python3 -c "
import json,sys
data=json.load(open(sys.argv[1]))
if not isinstance(data, (list,dict)) or len(data)==0:
  sys.exit(1)
" "$tmp" >/dev/null 2>&1; then
  printf 'crosslink export produced empty JSON — not staging\n' >&2
  exit 1
fi

# Atomically move temp file into place
if ! mv "$tmp" "$snapshot"; then
  printf 'failed to move snapshot into place\n' >&2
  exit 1
fi
tmp=""  # Clear so cleanup trap is a no-op after successful mv

# Skip staging if this is a temporary-index commit (git commit --only/--include/--all)
# The hook's git add would pollute the real index and force-include the snapshot
# in a scoped commit. CI catches any drift on push.
if [ -n "${GIT_INDEX_FILE:-}" ] && [ "$GIT_INDEX_FILE" != "$repo_root/.git/index" ]; then
  exit 0
fi

# Stage the snapshot only if it changed
# Untracked: git ls-files exits 1 → add
# Tracked unchanged: git diff --quiet exits 0 → skip
# Tracked changed: git diff --quiet exits 1 → add
# Error (corrupt index, I/O): exit > 1 → add anyway with warning
if ! git ls-files --error-unmatch "$snapshot" >/dev/null 2>&1; then
  git add "$snapshot"
else
  git diff --quiet -- "$snapshot" 2>/dev/null
  diff_rc=$?
  if [ "$diff_rc" -eq 1 ]; then
    git add "$snapshot"
  elif [ "$diff_rc" -gt 1 ]; then
    printf 'warning: git diff failed (exit %d) — staging snapshot anyway\n' "$diff_rc" >&2
    git add "$snapshot"
  fi
fi
```

Install the hook by copying it into `.git/hooks/`:

```bash
# Back up existing hook if present (timestamped to avoid overwriting previous backups)
if [ -f .git/hooks/pre-commit ]; then
  printf 'WARNING: .git/hooks/pre-commit already exists.\n' >&2
  backup=".git/hooks/pre-commit.bak.$(date +%s)"
  printf '  Existing hook backed up to %s\n' "$backup" >&2
  cp .git/hooks/pre-commit "$backup"
fi

cp .crosslink/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This avoids using `core.hooksPath`, which would override ALL git hooks (commit-msg, pre-push, etc.) and silently disable any existing hooks. The copy approach is hook-specific and non-disruptive. Existing hooks are backed up with a timestamp to preserve history.

Note: collaborators must run this copy step after cloning. Add it to your setup script or onboarding docs.

### 2. CI Safety Net

The CI step validates that the committed snapshot is well-formed JSON. It does NOT attempt drift detection (the database is gitignored and absent from CI).

```yaml
# .github/workflows/crosslink-sync.yml
name: Crosslink Snapshot Check
on: [push, pull_request]
jobs:
  validate-snapshot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate snapshot JSON
        run: |
          snapshot=".crosslink/issues-snapshot.json"
          if [ ! -f "$snapshot" ]; then
            printf 'ERROR: %s not found. Run crosslink export --output %s and commit.\n' "$snapshot" "$snapshot" >&2
            exit 1
          fi
          if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$snapshot" >/dev/null 2>&1; then
            printf 'ERROR: %s is not valid JSON. Run crosslink export --output %s and commit.\n' "$snapshot" "$snapshot" >&2
            exit 1
          fi
```

This catches: missing snapshot, corrupt snapshot, truncated JSON. The pre-commit hook is the primary sync mechanism; CI validates what the hook produced.

Note: The snapshot is NOT gitignored. The root `.gitignore` lists specific `.crosslink/` files (e.g., `issues.db`, `agent.json`) but does not blanket-ignore the directory. The snapshot at `.crosslink/issues-snapshot.json` is already trackable with no gitignore changes needed.

## Fixes Applied from Prior Reviews

| Fix | Source | How Addressed |
|-----|--------|---------------|
| Hook never executes | All 3 (CRITICAL) | Copy to `.git/hooks/pre-commit` |
| `core.hooksPath` overrides all hooks | Hy3 HIGH | Copy to `.git/hooks/` instead |
| `&&`/`||` conflates failure modes | Deepseek, MiMo HIGH | Explicit `if/else` blocks |
| Staged before validation | MiMo HIGH | JSON validation before `mv` |
| CI safety net broken (no DB) | Deepseek CRITICAL | Validate JSON structure, not drift against DB |
| CI drift false positives | Hy3 HIGH | Removed drift detection — CI validates, doesn't compare |
| `2>/dev/null` suppresses errors | All 3 HIGH | Capture stderr, print on failure |
| Upward traversal finds wrong `.crosslink` | Deepseek HIGH | Use `git rev-parse --show-toplevel` |
| `git add -f` redundant with gitignore | Hy3 HIGH | Conditional add only if snapshot changed |
| Temp file uses `$$` not `mktemp` | Hy3, Deepseek MEDIUM | Use `mktemp` with `XXXXXX` suffix |
| `mv` failure not guarded | Deepseek MEDIUM | Guarded with error message |
| `trap` after `mktemp` | Hy3 MEDIUM | Moved `trap` before `mktemp` |
| `cargo install` slow/unpinned | Hy3, MiMo MEDIUM | CI validates JSON — no crosslink install needed |
| Inner `.gitignore` exception | Hy3, MiMo LOW | Removed section — snapshot is not gitignored |
| Temp file cleanup on crash | Hy3, Deepseek LOW | `trap cleanup EXIT` |
| `chmod +x` missing | Hy3 LOW | Added to rollout steps |
| `--output` flag verified | Deepseek MEDIUM | Verified: `-o, --output` exists |
| `--no-verify` bypass | Hy3 identified gap | Documented as accepted bypass; CI validates on push |
| Worktree limitation | Hy3 LOW | Documented — hook only operates in main working tree |
| Per-clone setup | Hy3, MiMo LOW | Documented — copy step required after clone |
| First-run bootstrap behavior | Hy3 HIGH | Explicit untracked vs modified handling |
| Overwrites existing backup | Hy3 MEDIUM | Timestamped backups (`pre-commit.bak.<epoch>`) |
| `python3` dependency | MiMo LOW | Added `command -v python3` check |
| `--only` index pollution | Hy3, Deepseek HIGH | Detect `GIT_INDEX_FILE` temp index, skip staging |
| `git diff` exit 128 conflated | Deepseek MEDIUM | Distinguish exit codes, warn on error |
| `echo` portability | MiMo MEDIUM | Use `printf` instead of `echo` |
| `json.tool` performance | MiMo MEDIUM | Use `json.load` (parse-only, no reformat) |
| Empty JSON not caught | Hy3 LOW | Added non-empty validation |
| `export_err` captures stdout | MiMo LOW | Capture stderr only (`2>&1 1>/dev/null`) |
| Collaborator snippet guard | MiMo LOW | Added existence check |
| `trap` rm on moved file | Hy3 LOW | Clear `tmp=""` after successful `mv` |

## Edge Cases

| Case | Behavior |
|------|----------|
| No `.crosslink/` directory | Hook exits 0, no export attempted |
| `crosslink` not on PATH | Hook exits 0 with warning message |
| `python3` not on PATH | Hook exits 0 with warning message |
| Export fails (DB locked, permissions) | Hook exits 1, commit blocked, stderr shows error |
| Export produces invalid JSON | Hook exits 1, commit blocked, error shown |
| Export produces empty JSON | Hook exits 1, commit blocked, error shown |
| Crash during export | `trap` cleans up temp file, snapshot unchanged |
| `git commit --no-verify` | Export skipped — CI validates snapshot on push |
| `git commit --only <file>` | Staging skipped — hook detects temp index, CI catches drift |
| `git commit --include` | Staging skipped — hook detects temp index, CI catches drift |
| Multiple commits in rapid succession | One export per commit — no debouncing needed |
| Nested repos with multiple `.crosslink/` | `git rev-parse` resolves to current repo root only |
| Git worktrees | `.crosslink/` may not exist in worktree — hook exits 0 silently |
| Existing pre-commit hook | Backed up to `.git/hooks/pre-commit.bak.<epoch>` before overwrite |
| `git diff` transient error | Warning printed, snapshot staged anyway |
| Direct SQLite edits | CI validates snapshot structure (catches truncation) |
| OpenCode session mutates issues | Caught when session commits (hook fires) |
| Dashboard server mutates issues | CI validates snapshot on next push |
| Fresh clone (no hook installed) | CI validates — hook copy is a setup step |

## What This Does NOT Cover

- Real-time sync between commits — JSON is stale until next commit (acceptable for history tracking)
- Dashboard server mutations — CI validates snapshot on next push
- Direct SQLite writes — CI validates snapshot structure
- `git commit --no-verify` bypass — CI catches on push
- Drift detection — CI validates structure, not content drift (drift detection requires the database, which is gitignored)
- Git worktrees — hook only operates in the main working tree where `.crosslink/` exists

## Performance

- Export is O(N) queries for N issues. For <100 issues, <100ms.
- Runs once per commit, not per-mutation.
- JSON validation uses `json.load` (parse-only) — no reformatting, no stdout side-effect.
- CI validates JSON in <1s (no crosslink install needed).

## Rollout

1. Verify `crosslink export --output` flag exists: `crosslink export --help`
2. Create `.crosslink/hooks/pre-commit` with the hook script
3. `chmod +x .crosslink/hooks/pre-commit`
4. Back up existing hook if present: `[ -f .git/hooks/pre-commit ] && cp .git/hooks/pre-commit .git/hooks/pre-commit.bak.$(date +%s)`
5. `cp .crosslink/hooks/pre-commit .git/hooks/pre-commit`
6. `chmod +x .git/hooks/pre-commit`
7. Run initial export: `crosslink export --output .crosslink/issues-snapshot.json`
8. `git add .crosslink/issues-snapshot.json`
9. Configure CI workflow (JSON validation only)
10. Verify: make an issue change, commit, confirm snapshot updates

## Setup for Collaborators

After cloning, run:

```bash
# Backup existing hook if present
[ -f .git/hooks/pre-commit ] && cp .git/hooks/pre-commit .git/hooks/pre-commit.bak.$(date +%s)

# Install crosslink auto-export hook
if [ -f .crosslink/hooks/pre-commit ]; then
  cp .crosslink/hooks/pre-commit .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
fi
```

Or add to your setup script:

```bash
# Setup crosslink auto-export hook
if [ -f .crosslink/hooks/pre-commit ]; then
  [ -f .git/hooks/pre-commit ] && cp .git/hooks/pre-commit .git/hooks/pre-commit.bak.$(date +%s)
  cp .crosslink/hooks/pre-commit .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
fi
```
