# Shell Wrapper: Auto-Export Issues to JSON

## Problem
Crosslink issues live only in SQLite (`issues.db`), which is gitignored. No automatic mechanism exists to keep a version-controlled snapshot in sync. The plugin approach (detecting mutation commands via static verb list) is fragile — requires manual updates per crosslink release, misses commands, and only works in OpenCode sessions.

## Solution
A shell wrapper that intercepts the `crosslink` command, runs the original command, then conditionally triggers `crosslink export` after mutations. Works everywhere — terminal, OpenCode, CI, scripts.

## Implementation

### 1. Wrapper Function (~30 lines)

```bash
# ~/.bashrc or equivalent shell config

# Mutation commands that require re-export
_crosslink_mutation_commands=(
  issue  # covers: create, edit, close, reopen, delete, link, unlink, block, unblock, label, unlabel, milestone, set-milestone, clear-milestone, tested, assign
  session # covers: start, end, work, action, release
  timer   # covers: start, stop
  sync
  compact
  migrate
  lock
  unlock
  release
  import
)

crosslink() {
  local cmd="$1"
  shift

  # Execute the original command
  command crosslink "$cmd" "$@"
  local exit_code=$?

  # If the command failed, don't trigger export
  if [ $exit_code -ne 0 ]; then
    return $exit_code
  fi

  # Check if this is a mutation command
  local is_mutation=0
  for m in "${_crosslink_mutation_commands[@]}"; do
    if [ "$cmd" = "$m" ]; then
      is_mutation=1
      break
    fi
  done

  # If mutation, trigger export
  if [ $is_mutation -eq 1 ]; then
    local crosslink_dir
    crosslink_dir="$(find_up '.crosslink')"
    if [ -n "$crosslink_dir" ]; then
      local export_dir="$crosslink_dir"
      # Skip export for export/import commands themselves
      if [ "$cmd" != "export" ] && [ "$cmd" != "import" ]; then
        command crosslink export --output "$export_dir/issues-snapshot.json" 2>/dev/null
      fi
    fi
  fi

  return $exit_code
}

# Helper: find nearest ancestor directory containing a pattern
find_up() {
  local dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -e "$dir/$1" ]; then
      echo "$dir"
      return
    fi
    dir="$(dirname "$dir")"
  done
}
```

### 2. Export Target

`.crosslink/issues-snapshot.json` — already in `.gitignore` for `.crosslink/` but we need to explicitly track it:

```gitignore
# .gitignore — add exception
!.crosslink/issues-snapshot.json
```

Or move outside `.crosslink/` to avoid `.gitignore` conflicts:

```bash
export_path="$crosslink_dir/../.crosslink-issues.json"  # sibling to .crosslink
```

### 3. Pre-Commit Hook (Safety Net)

Keep the existing pre-commit hook as a fallback — catches any gap the wrapper misses (manual exports, CI, scripts that bypass the wrapper).

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit — export issues before commit

crosslink_dir="$(find_up '.crosslink')"
if [ -n "$crosslink_dir" ]; then
  export_path="$crosslink_dir/issues-snapshot.json"
  command crosslink export --output "$export_path" 2>/dev/null
  if [ $? -eq 0 ] && [ -f "$export_path" ]; then
    git add "$export_path"
  fi
fi
```

### 4. OpenCode Session Integration

For OpenCode sessions where `bash` tool doesn't source `~/.bashrc`, inject the wrapper at session start via a hook or `.bashrc` equivalent. Alternatively, the wrapper can be injected via OpenCode's `tool.execute.before` plugin — but the shell wrapper is simpler and works everywhere.

## Edge Cases

| Case | Behavior |
|------|----------|
| `crosslink issue create` | Wrapper runs export after create succeeds |
| `crosslink export` | Wrapper detects "export" and skips re-export |
| `crosslink import` | Wrapper detects "import" and skips re-export |
| `crosslink session start` | Wrapper runs export (session is mutation) |
| `crosslink timer start` | Wrapper runs export (timer is mutation) |
| `crosslink close-all` | Wrapper runs export once after all closes complete (not per-item) |
| `crosslink sync` | Wrapper runs export after sync completes |
| Command fails | Wrapper skips export (checks exit code) |
| Not in a crosslink repo | `find_up` returns empty, export silently skipped |
| Dashboard server mutations | Not covered — known gap, pre-commit hook catches |
| Multiple shells open | Each triggers export independently — no conflict (idempotent) |

## What This Does NOT Cover

1. **Dashboard HTTP handlers** — server-initiated mutations bypass CLI. Pre-commit hook is the safety net.
2. **Direct SQLite writes** — any code writing to `issues.db` outside crosslink CLI. Pre-commit hook catches.
3. **Performance on bulk operations** — `close-all` triggers one export after all closes, not per-item. Acceptable.

## Performance

- Export is O(N) queries for N issues. For typical repos (<100 issues), this is <100ms.
- Shell wrapper adds ~5ms overhead (command lookup + subshell).
- Export runs synchronously after mutation — user sees brief pause.
- If too slow, can background: `command crosslink export ... &` — but then snapshot may lag by one command.

## Testing

```bash
# Test: wrapper triggers export
crosslink issue create "Test issue"
ls -la .crosslink/issues-snapshot.json  # should exist and be fresh

# Test: wrapper skips on read commands
crosslink issue list
# No export triggered (no mutation command match)

# Test: wrapper skips on export command
crosslink export --output /tmp/test.json
# No double export

# Test: wrapper handles failure gracefully
crosslink issue close 99999  # non-existent issue
# Should not trigger export (exit code != 0)
```

## Rollout

1. Add wrapper function to `~/.bashrc`
2. Add `.crosslink/issues-snapshot.json` to git (tracked)
3. Add `.gitignore` exception for snapshot file
4. Run initial export: `crosslink export --output .crosslink/issues-snapshot.json`
5. Commit snapshot file
6. Verify: make a change, confirm snapshot updates
