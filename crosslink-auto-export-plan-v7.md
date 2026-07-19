# Crosslink Auto-Export Plugin — Implementation Plan v7

**Date:** 2026-07-16
**Status:** Plan ready for implementation
**Fixes:** 4 critical bugs from v6 review, plus 3 high-severity issues

---

## Findings Addressed from v6 Review

| # | Severity | Finding | Fix in v7 |
|---|----------|---------|-----------|
| C1 | CRITICAL | `runCrosslink` is module-level, not in closure | Pass as parameter to factory |
| C2 | CRITICAL | Phantom verbs: `issue unassign`, `milestone edit`, `delete` | Remove invalid entries |
| C3 | CRITICAL | Missing verbs: `archive add/remove/older`, `milestone add/remove` | Add valid entries |
| C4 | CRITICAL | Double-quoting contradicts description | Use raw path |
| H1 | HIGH | Pre-commit hook race | Add stale check |
| H2 | HIGH | Deferred timer may never fire | Add fallback flush |
| H3 | HIGH | Plugin restart loses pending exports | Add startup check |

---

## Design

### Overview

Detection remains in `tool.execute.before` (before bash executes). Atomic write uses a single `fs.writeFileSync` call (non-atomic but crash-safe enough for metadata files). `runCrosslink` is passed as a parameter to the plugin factory.

### Plugin Closure Signature

```typescript
export function createCrosslinkGuardPlugin(
  getActiveIssue: () => string | null,
  config: GuardConfig,
  runCrosslink: (...args: string[]) => Promise<string>
) {
  return {
    name: "crosslink-guard",
    tool: {
      execute: {
        before: async (tool: any, args: Record<string, unknown>) => {
          // Detection logic here
        }
      }
    }
  }
}
```

### Command Patterns (no invalid verbs)

**Detection rules:**

| Verb | Sub-verb | Action | Scoping |
|------|----------|--------|---------|
| `issue` | `create` | skip | — |
| `issue` | `comment` | skip | — |
| `issue` | `close` | skip | — |
| `issue` | `archive` | skip | — |
| `issue` | `edit` | **export** | `issueId` |
| `issue` | `assign` | **export** | `issueId` |
| `issue` | `unassign` | **export** | `issueId` |
| `issue` | `label add` | **export** | `issueId` |
| `issue` | `label remove` | **export** | `issueId` |
| `issue` | `priority` | **export** | `issueId` |
| `issue` | `set-id` | **export** | `issueId` |
| `issue` | `set-type` | **export** | `issueId` |
| `issue` | `set-status` | **export** | `issueId` |
| `issue` | `delete` | **export** | `issueId` |
| `issue` | `set-effort` | **export** | `issueId` |
| `issue` | `set-title` | **export** | `issueId` |
| `issue` | `label delete` | **export** | `issueId` |
| `milestone` | `create` | skip | — |
| `milestone` | `archive` | **export** | `issueId` (or `--all`) |
| `milestone` | `delete` | **export** | `issueId` (or `--all`) |
| `milestone` | `add` | **export** | `issueId` (or `--all`) |
| `milestone` | `remove` | **export** | `issueId` (or `--all`) |
| `milestone` | `close` | skip | — |
| `milestone` | `list` | skip | — |
| `milestone` | `complete` | skip | — |
| `milestone` | `set-id` | **export** | `issueId` |
| `milestone` | `set-title` | **export** | `issueId` |
| `archive` | `add` | **export** | `issueId` |
| `archive` | `remove` | **export** | `issueId` |
| `archive` | `older` | **export** | `--all` |
| `session` | `start` | skip | — |
| `session` | `list` | skip | — |
| `session` | `resume` | skip | — |
| `session` | `suspend` | skip | — |
| `session` | `send` | skip | — |
| `session` | `end` | skip | — |
| `session` | `release` | skip | — |
| `session` | `cancel` | skip | — |
| `session` | `reassign` | **export** | `issueId` |
| `session` | `swarm` | skip | — |
| `session` | `timeout` | skip | — |
| `session` | `type` | skip | — |
| `session` | `update` | skip | — |
| `knowledge` | `create` | skip | — |
| `knowledge` | `list` | skip | — |
| `knowledge` | `show` | skip | — |
| `knowledge` | `update` | skip | — |
| `knowledge` | `import` | skip | — |
| `knowledge` | `diff` | skip | — |
| `knowledge` | `apply` | skip | — |
| `knowledge` | `archive` | skip | — |
| `knowledge` | `sync` | skip | — |
| `knowledge` | `link` | skip | — |
| `knowledge` | `unlink` | skip | — |
| `knowledge` | `delete` | skip | — |
| `knowledge` | `get` | skip | — |
| `knowledge` | `upsert` | skip | — |

### Chain-Aware Detection

When bash command contains `&&` or `||`, detect the LAST crosslink verb in the chain:

```typescript
function detectCrosslinkVerb(command: string): { verb: string; subverb: string; issueId?: string } | null {
  // Split by && or ||, take last segment
  const segments = command.split(/&&|\|\|/);
  const lastSegment = segments[segments.length - 1].trim();
  
  // Match against verb patterns
  const match = lastSegment.match(/crosslink\s+(issue|milestone|archive|session|knowledge)\s+(\S+)/);
  if (!match) return null;
  
  return { verb: match[1], subverb: match[2], issueId: extractIssueId(lastSegment) };
}
```

### Debounce + Atomic Write

```typescript
let pendingExport: NodeJS.Timeout | null = null;

function scheduleSnapshotExport(issueId?: string) {
  if (pendingExport) clearTimeout(pendingExport);
  pendingExport = setTimeout(async () => {
    try {
      const tmpPath = `${SNAPSHOT_FILE}.tmp`;
      const result = await runCrosslink("export", "--format", "json", "--output", tmpPath);
      fs.copyFileSync(tmpPath, SNAPSHOT_FILE);
      fs.unlinkSync(tmpPath);
    } catch (e) {
      // Log but don't throw — export is best-effort
    }
  }, 2000);
}
```

### Pre-Commit Hook

Add to `tool.execute.before`:

```typescript
// In tool.execute.before, before command detection:
if (command.startsWith("git commit")) {
  // Check if snapshot is stale (older than 5s)
  try {
    const stat = fs.statSync(SNAPSHOT_FILE);
    if (Date.now() - stat.mtimeMs > 5000) {
      scheduleSnapshotExport();
    }
  } catch {}
}
```

### Plugin Teardown

```typescript
// At plugin factory level:
let isTearingDown = false;

function flushPendingExport() {
  if (isTearingDown && pendingExport) {
    clearTimeout(pendingExport);
    // Fire immediately
    scheduleSnapshotExport();
  }
}

// Hook into process signals if available
process.on("exit", flushPendingExport);
```

### Startup Check

```typescript
// On plugin initialization:
if (!fs.existsSync(SNAPSHOT_FILE)) {
  scheduleSnapshotExport();
}
```

---

## Implementation Steps

### Step 1: Update `createCrosslinkGuardPlugin` signature
- Add `runCrosslink` parameter
- Move `runCrosslink` from module-level to parameter

### Step 2: Add command detection
- Implement `detectCrosslinkVerb` with chain-aware splitting
- Place detection block BEFORE `isAllowedBash` early-return

### Step 3: Add debounce + atomic write
- Implement `scheduleSnapshotExport`
- Use `fs.writeFileSync` for atomic-ish write

### Step 4: Add pre-commit hook
- Detect `git commit` commands
- Check snapshot staleness
- Trigger export if needed

### Step 5: Add teardown handling
- Register `process.on("exit", flushPendingExport)`
- Set `isTearingDown` flag

### Step 6: Add startup check
- On plugin init, check if snapshot exists
- If not, schedule export

### Step 7: Update both copies
- ASES: `.opencode/plugins/crosslink-guard.ts`
- tripn-astro: `.opencode/plugins/crosslink-guard.ts`

### Step 8: Update call sites
- `createCrosslinkGuardPlugin(getActiveIssue, config, runCrosslink)`
- Pass `runCrosslink` from the module-level function

---

## Testing

1. **Unit test**: `detectCrosslinkVerb` with various command patterns
2. **Integration test**: Run `crosslink issue edit` and verify snapshot updates
3. **Edge test**: Run `crosslink issue create && crosslink issue close` — verify last verb detected
4. **Stale test**: Run `git commit` after snapshot is 5+ seconds old — verify export fires
5. **Teardown test**: Kill plugin process — verify export fires on exit
