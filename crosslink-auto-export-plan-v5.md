# Revised Plan: Auto-Export Issues via Command-Pattern Detection

**Status:** Draft v5
**Date:** 2026-07-17
**Based on:** 8 adversarial reviews

## Problem

`issues.db` is gitignored. Issue history is not version-controlled. Fresh clones lose all issue state.

## Previous Approaches (Rejected)

- mtime-based lazy snapshot — broken due to SQLite WAL mode
- `post_command_hooks` in hook-config.json — does not exist in crosslink

## New Approach: Command-Pattern Detection

**Trigger:** Detect `crosslink issue` mutation commands in `tool.execute.before`
**Action:** After command completes, export issues to tracked JSON
**Safety:** Atomic write (temp + rename), debounce, concurrency guard, chain-aware detection

## Architecture

```
tool.execute.before fires
  │
  ├─ Is this a crosslink mutation command? (chain-aware)
  │   ├─ No → existing guard logic proceeds
  │   └─ Yes → schedule deferred export (1000ms debounce)
  │
  └─ Meanwhile, foreground bash runs the actual mutation
        │
        ▼
   issues.db updated
        │
   1000ms debounce expires
        │
        ▼
   Export fires (atomic write)
        │
        ▼
   .crosslink/issues-snapshot.json ← git-tracked
```

## Implementation

### Step 1: Mutation-Verb Detection (Complete List)

Based on `IssueCommands` enum in `main.rs:574-863` and top-level aliases:

```typescript
const CROSSLINK_MUTATION_VERBS = [
  // Issue lifecycle
  "issue create", "issue quick", "quick",
  "issue close", "close", "close-all",
  "issue reopen", "reopen",
  "issue delete", "delete",
  
  // Issue content
  "issue comment", "comment",
  "issue edit", "edit",
  "issue label", "label", "unlabel",
  "issue assign", "issue unassign",
  
  // Issue relationships
  "issue depend", "undepend",
  "issue relate", "unrelate",
  "issue block", "unblock",
  
  // Issue scheduling
  "issue schedule", "unschedule",
  
  // Bulk operations
  "import",
  "intervene", "tested",
  
  // Milestones
  "milestone create", "milestone close", "milestone edit",
  "milestone issue add", "milestone issue remove",
  
  // Top-level aliases
  "new", "subissue",
];

function isCrosslinkMutation(command: string): boolean {
  let cmd = command;
  // Strip rtk prefix
  while (cmd.startsWith("rtk ")) cmd = cmd.slice(4);
  // Strip crosslink global flags
  cmd = cmd.replace(/^crosslink\s+(?:-\S+\s+)*/, "crosslink ");
  
  // Handle chained commands: split on &&, ;, |
  const parts = cmd.split(/\s*&&\s*|\s*;\s*|\s*\|\s*/);
  
  return parts.some(part => {
    const trimmed = part.trim();
    return CROSSLINK_MUTATION_VERBS.some(v => 
      trimmed.startsWith(`crosslink ${v}`)
    );
  });
}
```

### Step 2: Debounced Export with Atomic Write

```typescript
const SNAPSHOT_FILE = "issues-snapshot.json";
const DEBOUNCE_MS = 1000; // Increased from 500ms to handle slow mutations
let exportTimer: NodeJS.Timeout | null = null;
let exportInProgress = false;

function scheduleSnapshotExport(crosslinkDir: string): void {
  if (exportTimer) clearTimeout(exportTimer);
  exportTimer = setTimeout(() => {
    runSnapshotExport(crosslinkDir);
  }, DEBOUNCE_MS);
}

async function runSnapshotExport(crosslinkDir: string): Promise<void> {
  if (exportInProgress) return;
  exportInProgress = true;
  
  try {
    const snapshotPath = path.join(crosslinkDir, SNAPSHOT_FILE);
    const tmpPath = snapshotPath + ".tmp";
    
    const result = await runCrosslink(
      shell,
      ["export", "--format", "json", "--output", `"${tmpPath}"`],
      crosslinkDir,
    );
    
    if (result?.exitCode === 0) {
      // Atomic write: rename temp → final
      fs.renameSync(tmpPath, snapshotPath);
      log("Exported issue snapshot to:", snapshotPath);
    } else {
      log("Issue snapshot export failed (exit:", result?.exitCode ?? "null", ")");
      try { fs.unlinkSync(tmpPath); } catch {}
    }
  } catch (e) {
    log("Snapshot export error:", String(e));
  } finally {
    exportInProgress = false;
  }
}
```

### Step 3: Hook Integration

Insert in `tool.execute.before`, inside the write/edit/bash guard:

```typescript
if (toolLower === "bash" && crosslinkDir) {
  const command = (output.args?.command as string) ?? "";
  if (isCrosslinkMutation(command)) {
    scheduleSnapshotExport(crosslinkDir);
    // Do NOT block — let the mutation proceed
  }
}
```

### Step 4: Gitignore Verification

- `.crosslink/issues-snapshot.json` is NOT gitignored (verified)
- Use `git add -f` in initial seed to force-add even if gitignore patterns match

### Step 5: Initial Seed

After deployment, run once to create initial snapshot:
```bash
cd /home/claude-code/projects/ASES
crosslink export --format json --output .crosslink/issues-snapshot.json
git add -f .crosslink/issues-snapshot.json
git commit -m "chore: seed issue snapshot for version tracking"
```

## Edge Cases

| Case | Handling |
|------|----------|
| Missing `.crosslink/` | `findCrosslinkDir` returns null → skip |
| Missing `issues.db` | `crosslink export` produces `[]` → harmless |
| Concurrent mutations | Debounce coalesces rapid changes; single export after last write |
| Chained commands | Split on `&&`, `;`, `|` and check each part |
| Slow mutations | 1000ms debounce gives more time; next mutation retries if stale |
| Export fails | Logged, temp file cleaned up, next mutation retries |
| Large DB | Export may be slow → still only fires on mutation, not every call |
| `crosslink` binary missing | `runCrosslink` returns non-zero → logged, no crash |
| Paths with spaces | Quote output path unconditionally |

## Scope

**In scope:** Issue mutations that change `issues.db`
**Out of scope:** Session state changes (`session work`, `session end`), timer operations, read-only commands

## Files Changed

1. `.opencode/plugins/crosslink-guard.ts` — add ~100 lines (mutation detection + debounced export)
2. `.crosslink/issues-snapshot.json` — initial seed (tracked in git)

## Rollback

1. Remove new functions from `crosslink-guard.ts`
2. `git rm .crosslink/issues-snapshot.json`

## Pros

- Works within actual constraints (`tool.execute.before` only)
- No mtime detection — uses command-pattern (reliable)
- Chain-aware — handles `crosslink issue close 5 && git add .`
- Atomic write prevents corruption
- Debounce prevents thundering herd
- Uses crosslink's own export command (format consistency)
- ~100 lines, no new dependencies

## Cons

- 1000ms latency after mutation (acceptable for VCS)
- Exports full DB on every mutation (could be slow for very large DBs)
- Requires `crosslink` on PATH
- First export after slow mutation may be stale (self-healing on next mutation)
