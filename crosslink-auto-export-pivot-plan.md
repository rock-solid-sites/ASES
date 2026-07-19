# Auto-Export Issues Snapshot: Design Pivot

**Status:** Draft — pivot proposal under review
**Date:** 2026-07-17
**Context:** 5 rounds of adversarial review on plugin-based approach (15 model reviews total)

---

## Problem

`issues.db` is gitignored. Issue history is not version-controlled. Fresh clones lose all issue state.

---

## What We Tried (Plugin Approach)

A plugin (`crosslink-guard.ts`) detects crosslink mutation commands in `tool.execute.before` and schedules a debounced export to `.crosslink/issues-snapshot.json`. A pre-commit hook re-exports at commit time as a safety net.

### Issues Found Across 5 Review Rounds

| Category | Findings |
|----------|----------|
| **Phantom commands** | Verb list had 9 entries that don't exist in the crosslink CLI (`issue archive`, `milestone edit`, `issue unassign`, top-level `reopen`/`delete`, etc.) |
| **Missing commands** | Verb list was missing 7 real mutation commands (`issue unlabel`, `issue unrelate`, `issue unblock`, `issue tested`, `archive add/remove/older`, `sync`, `compact`, `migrate`) |
| **Prefix collisions** | `issue block` matched `issue blocked` (read-only), `issue relate` matched `issue related` (read-only) — fixed with word-boundary check |
| **Flag-stripping** | Regex failed on `--log-level debug`, `--config=value`, `-C/path` — replaced with arg-aware loop |
| **Concurrency bugs** | Initial `pendingRetry` was dead code — renamed to `needsReExport` with corrected reschedule logic |
| **Temp file race** | Fixed filename `.tmp` enabled concurrent writes on timeout — changed to unique `pid.timestamp` names |
| **Missing timeout** | Export could hang indefinitely on large DBs — added 30s `Promise.race` |
| **Pre-commit hook** | Didn't check exit code, silently swallowed failures, used `2>/dev/null` — all fixed |
| **Phantom flags** | `argFlags` set contained `--config` and `-C` which don't exist in crosslink — removed |
| **Stale snapshot** | Slow bulk verbs (`sync`/`compact`/`migrate`) can miss terminal export — acknowledged as limitation |

### Fundamental Fragility

The command-pattern detection approach has a structural weakness: **a static verb list that must be manually updated whenever crosslink adds new mutation commands.** Every new subcommand that modifies `issues.db` must be discovered, verified, and added to the array. False negatives (missing verbs) silently lose data. False positives (phantom verbs) waste cycles.

---

## Proposed Pivot: Crosslink Builtin

Instead of detecting commands externally, add a post-mutation export directly in crosslink's command dispatch. Crosslink **already knows** when it mutates `issues.db` — no pattern detection needed.

### How It Would Work

```
crosslink issue close 5
  │
  ├─ close issue 5 in issues.db
  ├─ auto-export: crosslink export --output .crosslink/issues-snapshot.json
  └─ return
```

### Implementation Sketch

In crosslink's Rust source, after each command that modifies `issues.db`:

```rust
// After successful mutation
if self.config.auto_export {
    let snapshot_path = self.crosslink_dir.join("issues-snapshot.json");
    let _ = self.export_issues(&snapshot_path); // best-effort, non-blocking
}
```

### Affected Commands

All commands that write to `issues.db`:
- `issue` subcommands: create, quick, close, close-all, reopen, delete, comment, update, label, unlabel, block, unblock, relate, unrelate, intervene, tested
- `archive` subcommands: add, remove, older
- `milestone` subcommands: create, close, delete, add, remove
- `import`, `sync`, `compact`, `migrate`

### What Changes

| Aspect | Plugin Approach | Builtin Approach |
|--------|----------------|------------------|
| Detection mechanism | Static verb list, regex matching | None — crosslink knows internally |
| Code location | ~100 lines TypeScript in plugin | ~20 lines Rust in crosslink |
| Reliability | Fragile (verb drift, flag stripping, debounce races) | Deterministic (runs after every mutation) |
| Coverage | Only OpenCode sessions | All invocations (terminal, CI, scripts) |
| Timing | Debounced 2s, stale on slow commands | Immediate, synchronous |
| Temp file | Unique pid.timestamp names needed | Direct write, no temp needed |
| Concurrency | Needs `needsReExport` flag | No concurrency concerns |
| Maintenance | Must update verb list per crosslink release | No maintenance — automatic |

### What We Keep

- **Pre-commit hook** (Option A from original plan) — safety net, guarantees snapshot at commit time
- **Initial seed** — `crosslink export --output .crosslink/issues-snapshot.json`
- **Snapshot file** — `.crosslink/issues-snapshot.json` (git-tracked)

### What We Drop

- Plugin mutation detection (Steps 1-3 of original plan)
- Debounce logic
- Concurrency guard (`needsReExport`)
- Flag-stripping logic
- Word-boundary matching
- 30s timeout
- Unique temp filenames

### Migration Path

1. Implement builtin in crosslink (this plan)
2. Keep pre-commit hook as safety net during transition
3. Once builtin is confirmed working, optionally remove plugin detection code

---

## Questions for Reviewers

1. Is the pivot sound? Does a builtin solve the problem more reliably than external detection?
2. Are there edge cases where the builtin would miss mutations that the plugin would catch?
3. Should the builtin be opt-in (config flag) or always-on?
4. Should the export be synchronous (blocks the command) or async (fire-and-forget)?
5. Is ~20 lines of Rust the right estimate, or is this more complex?
6. Any concerns about the export running on every mutation (performance, disk I/O)?
7. Should the pre-commit hook be kept as a safety net, or is the builtin sufficient alone?
