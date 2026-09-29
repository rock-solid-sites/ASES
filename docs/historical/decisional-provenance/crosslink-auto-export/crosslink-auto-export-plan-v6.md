# Revised Plan: Auto-Export Issues via Command-Pattern Detection

**Status:** Draft v6 (revised 2026-07-17)
**Date:** 2026-07-17
**Based on:** 12 adversarial reviews + 12-model review (Deepseek ×4, Hy3 ×4, Nemotron ×4)

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
tool.execute.before fires (after ensureState, before isAllowedBash)
  │
  ├─ Is this a crosslink mutation command? (chain-aware, per-part flag stripping)
  │   ├─ No → existing guard logic proceeds
  │   └─ Yes → schedule deferred export (2000ms debounce)
  │
  └─ Meanwhile, foreground bash runs the actual mutation
        │
        ▼
   issues.db updated
        │
   2000ms debounce expires (export fires AFTER mutation completes)
        │
        ▼
   Export fires (atomic write)
        │
        ▼
   .crosslink/issues-snapshot.json ← git-tracked
```

## Implementation

### Step 1: Mutation-Verb Detection (Complete List)

Based on verified `IssueCommands` enum and top-level aliases:

```typescript
const CROSSLINK_MUTATION_VERBS = [
  // Issue lifecycle
  "issue create", "issue quick", "quick",
  "issue close", "issue close-all",
  "issue reopen",
  "issue delete",
  
  // Issue content
  "issue comment",
  "issue update",
  "issue label", "issue unlabel",
  
  // Issue relationships
  "issue relate", "issue unrelate",
  "issue block", "issue unblock",
  
  // Issue state
  "issue intervene", "issue tested",
  
  // Read-only commands that start with mutation prefixes (excluded to avoid false positives)
  // "issue blocked" starts with "issue block" — word-boundary check prevents false match
  // "issue related" starts with "issue relate" — word-boundary check prevents false match
  
  // Archive (top-level command)
  "archive add", "archive remove", "archive older",
  
  // Milestones
  "milestone create", "milestone close", "milestone delete",
  "milestone add", "milestone remove",
  
  // Bulk operations
  "import",
  
  // Database mutations
  "sync",
  "compact",
  "migrate",
  
  // Top-level aliases
  "new", "subissue", "close",
];

function isCrosslinkMutation(command: string): boolean {
  // Handle chained commands: split on " && ", " ; ", " | "
  const parts = command.split(/\s*&&\s*|\s*;\s*|\s*\|(?!\|)\s*/);
  
  return parts.some(part => {
    let trimmed = part.trim();
    // Strip rtk prefix (per-part)
    while (trimmed.startsWith("rtk ")) trimmed = trimmed.slice(4);
    // Strip crosslink global flags (per-part), including flags with arguments
    // Known arg-carrying flags: --log-level, --log-format
    const argFlags = new Set(["--log-level", "--log-format"]);
    const words = trimmed.split(/\s+/);
    if (words.length > 0 && words[0] === "crosslink") {
      let i = 1;
      while (i < words.length && words[i].startsWith("-")) {
        const w = words[i];
        // Handle --flag=value form
        const eqIdx = w.indexOf("=");
        if (eqIdx > 0) {
          i += 1; // skip the entire --flag=value token
        } else if (argFlags.has(w) && i + 1 < words.length) {
          i += 2; // skip flag + its argument
        } else {
          i += 1; // skip boolean flag
        }
      }
      trimmed = ["crosslink", ...words.slice(i)].join(" ");
    }
    return CROSSLINK_MUTATION_VERBS.some(v => {
      const target = `crosslink ${v}`;
      // Word-boundary match: exact match or followed by space/flag
      return trimmed === target || trimmed.startsWith(target + " ");
    });
  });
}
```

### Step 2: Debounced Export with Atomic Write

Define inside plugin closure (accesses `shell` from `pluginInput.$`):

```typescript
const SNAPSHOT_FILE = "issues-snapshot.json";
const DEBOUNCE_MS = 2000;
let exportTimer: ReturnType<typeof setTimeout> | null = null;
let exportInProgress = false;
let needsReExport = false;

function scheduleSnapshotExport(crosslinkDir: string): void {
  if (exportTimer) clearTimeout(exportTimer);
  exportTimer = setTimeout(() => {
    exportTimer = null;
    runSnapshotExport(crosslinkDir);
  }, DEBOUNCE_MS);
}

async function runSnapshotExport(crosslinkDir: string): Promise<void> {
  if (exportInProgress) {
    // Export is in progress — mark that we need to re-export after it finishes.
    // The debounce timer for this mutation was already cleared by the in-progress
    // export's own scheduling, so without this flag the mutation would be lost.
    needsReExport = true;
    return;
  }
  exportInProgress = true;
  needsReExport = false;
  
  try {
    const snapshotPath = path.join(crosslinkDir, SNAPSHOT_FILE);
    const tmpPath = snapshotPath + `.tmp.${process.pid}.${Date.now()}`;
    
    const result = await Promise.race([
      runCrosslink(shell, ["export", "--output", tmpPath], crosslinkDir),
      new Promise<null>((resolve) => setTimeout(() => {
        log("Snapshot export timed out after 30s");
        resolve(null);
      }, 30_000)),
    ]);
    
    if (result?.exitCode === 0) {
      try {
        fs.renameSync(tmpPath, snapshotPath);
      } catch (e) {
        if (e.code === "EPERM" || e.code === "EXDEV") {
          fs.copyFileSync(tmpPath, snapshotPath);
          try { fs.unlinkSync(tmpPath); } catch {}
        } else {
          throw e;
        }
      }
      log("Exported issue snapshot to:", snapshotPath);
    } else {
      log("Issue snapshot export failed (exit:", result?.exitCode ?? "null", ")");
      try { fs.unlinkSync(tmpPath); } catch {}
    }
  } catch (e) {
    log("Snapshot export error:", String(e));
  } finally {
    exportInProgress = false;
    if (needsReExport) {
      scheduleSnapshotExport(crosslinkDir);
    }
  }
}
```

### Step 3: Hook Integration

**Critical placement:** After `ensureState()` (line ~820) and BEFORE the blocked-git check (line ~825). This ensures:
- `crosslinkDir` is resolved
- Detection runs on ALL bash commands including blocked/gated ones
- Blocked commands still get blocked — export fires but is harmless (no-op, reads unchanged DB)

```typescript
// After ensureState(), before blocked-git check:
if (toolLower === "bash" && crosslinkDir) {
  const command = (output.args?.command as string) ?? "";
  if (isCrosslinkMutation(command)) {
    scheduleSnapshotExport(crosslinkDir);
    // Do NOT block — let the mutation proceed
  }
}
```

### Step 4: Git Tracking

The snapshot file is NOT gitignored (verified). However, nothing auto-commits it.

**Option A (recommended): Pre-commit hook**
```bash
# .git/hooks/pre-commit
#!/bin/bash
if ! command -v crosslink &>/dev/null; then
  echo "Warning: crosslink not on PATH — skipping snapshot export" >&2
  exit 0
fi
if [ ! -d .crosslink ]; then
  exit 0
fi
if crosslink export --output .crosslink/issues-snapshot.json; then
  git add .crosslink/issues-snapshot.json
else
  echo "Warning: crosslink export failed — snapshot not updated" >&2
fi
```

**Option B: Document manual commit**
The snapshot accumulates as a modified file. Human commits it with their changes.

**Option C: Auto-commit in plugin** (not recommended — creates noise)
After export, run `git add` + `git commit`.

The plan recommends **Option A** (pre-commit hook) as it captures state at commit time without noise.

### Step 5: Initial Seed

After deployment:
```bash
cd /home/claude-code/projects/ASES
crosslink export --output .crosslink/issues-snapshot.json
git add -f .crosslink/issues-snapshot.json
git commit -m "chore: seed issue snapshot for version tracking"
```

## Edge Cases

| Case | Handling |
|------|----------|
| Missing `.crosslink/` | `findCrosslinkDir` returns null → skip |
| Missing `issues.db` | `crosslink export` produces `[]` → harmless |
| Concurrent mutations | Debounce coalesces rapid changes; `needsReExport` flag reschedules if mutation arrives during in-progress export |
| Chained commands | Split on `&&`, `;`, `|` (not `||`); check each part |
| Slow mutations | 2000ms debounce; next mutation retries if stale |
| Export fails | Logged, temp file cleaned up, next mutation retries |
| Large DB | Export may be slow → 30s timeout prevents indefinite hang; orphaned process completes in background |
| `--help` commands | Harmless false-positive export (reads unchanged DB, no data loss) |
| Export timeout | `Promise.race` abandons the subprocess — it completes in background. Unique temp filename prevents corruption with next export. |
| `crosslink` binary missing | `runCrosslink` returns non-zero → logged, no crash |
| Paths with spaces | Pass raw path to runCrosslink — it handles quoting |
| Windows | Fallback copyFile + unlink if rename fails (not atomic — documented trade-off) |

## Scope

**In scope:** Issue mutations that change `issues.db`
**Out of scope:** Session state changes, timer operations, read-only commands, lock operations (locks are stored in a separate mechanism, not `issues.db`)

## Files Changed

1. `.opencode/plugins/crosslink-guard.ts` — add ~100 lines (mutation detection + debounced export)
2. `.crosslink/issues-snapshot.json` — initial seed (tracked in git)
3. `.git/hooks/pre-commit` — auto-commit snapshot (optional)

## Rollback

1. Remove new functions from `crosslink-guard.ts`
2. Remove pre-commit hook
3. `git rm .crosslink/issues-snapshot.json`

## Prior Findings Resolution

| # | Finding | Resolution |
|---|---------|------------|
| C1 | `shell` not in scope | Defined functions inside plugin closure |
| C2 | Chain flag stripping not per-part | Strip flags after splitting, per-part |
| C3 | Missing verbs | Added `issue update`, `issue unlabel`, `issue unrelate`, `issue unblock`, `issue tested`, `archive add/remove/older`, `sync`, `compact`, `migrate` |
| C4 | Phantom verbs | Removed `issue edit`, `issue depend`, `issue schedule`, `issue assign`, `issue archive`, `milestone edit`, `issue unassign`, top-level `reopen`/`delete` |
| H1 | Nothing commits snapshot | Added pre-commit hook (Option A) |
| H2 | Debounce timing | Increased to 2000ms; documented limitation |
| H3 | Double-quoting | Pass raw path, let runCrosslink handle quoting |
| H4 | Integration ordering | Place after ensureState(), before blocked-git check |
| M1 | Concurrency guard drops mutations | Renamed to `needsReExport`; reschedule on `finally` when flag is set |
| M2 | Atomic write fallback missing EXDEV | Added `EXDEV` to catch condition; removed `EEXIST` (unnecessary on POSIX) |
| M3 | NodeJS.Timeout incompatible with Bun | Changed to `ReturnType<typeof setTimeout>` |
| M4 | Prefix collision: block/blocked, relate/related | Added word-boundary check in `isCrosslinkMutation` |
| M5 | Architecture diagram timing misleading | Clarified export fires after mutation via debounce |
| M6 | Chain-splitting diverges from existing code | Improved regex — accepts separators with or without whitespace |
| M7 | Export flag inconsistency | Removed redundant `--format json` from Step 5 seed |
| R1 | Flag-stripping fails on `--log-level debug` | Replaced regex with arg-aware loop using known flag set |
| R2 | Missing `sync`, `compact`, `migrate` | Added to mutation verb list (all modify `issues.db`) |
| R3 | `pendingRetry` dead code | Renamed to `needsReExport` with corrected reschedule logic |
| R4 | Export timeout missing | Added 30s `Promise.race` timeout |
| R5 | Pre-commit hook swallows failures | Added `command -v crosslink` check with warning |
| R6 | Temp file race on timeout | Use unique temp name with pid/timestamp |
| R7 | Equals-form flags not handled | Added `=` detection in flag-stripping loop |
| R8 | Pre-commit hook doesn't check export exit code | Added conditional `git add` on success only |
| R9 | Phantom flags `--config` and `-C` | Removed from argFlags (not crosslink flags) |
| R10 | Locks scope ambiguity | Documented as out of scope (not in issues.db) |

## Pros

- Works within actual constraints (`tool.execute.before` only)
- No mtime detection — uses command-pattern (reliable)
- Chain-aware — handles `crosslink issue close 5 && git add .`
- Atomic write on POSIX (best-effort on Windows via copyFile fallback)
- Debounce prevents thundering herd
- Uses crosslink's own export command (format consistency)
- Auto-commits via pre-commit hook
- ~100 lines, no new dependencies

## Cons

- 2000ms latency after mutation (acceptable for VCS)
- Exports full DB on every mutation (could be slow for very large DBs)
- Requires `crosslink` on PATH
- First export after slow mutation may be stale (self-healing on next mutation)
