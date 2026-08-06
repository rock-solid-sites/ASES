# Bug Report: `sync` and `compact` reset issue UUIDs in SQLite, causing hydration mismatches

### Summary
In Crosslink `0.9.0-beta.1`, running either `crosslink sync` or `crosslink compact` causes the UUIDs of existing issues in the local SQLite database (`issues.db`) to be overwritten or reset. This results in immediate hydration failures (e.g., reporting `N sqlite-only issue(s)`) when checking integrity, because the SQLite-resident UUIDs no longer match the canonical JSON event log payload.

> **Document structure:** this addendum contains two parts.
> 1. The original **draft** bug report (below) — kept as historical evidence
>    and cited by Research Addendum 04 §2.4 (hydration failure catalog).
> 2. A **submission-ready report** (bottom section) — the final,
>    repo-agnostic version ready to file upstream at
>    https://github.com/forecast-bio/crosslink/issues/new, followed by an
>    internal-only evidence index.

### Steps to Reproduce
1. Initialize a Crosslink repository and create several issues.
2. Confirm that integrity checks pass successfully:
   ```bash
   crosslink integrity
   ```
   All checks (including hydration) pass (5/5).
3. Run `crosslink sync` or `crosslink compact`.
4. Run the integrity checks again:
   ```bash
   crosslink integrity
   ```
5. **Observed Result:** The hydration check fails, reporting that several SQLite-only issues exist because their UUIDs in the database no longer match the UUIDs recorded in the JSON event logs.
6. **Workaround:** Manually updating the UUID fields in the SQLite database back to their correct historical values immediately restores a passing hydration status.

### Analysis
The bug appears to reside in the synchronization/compaction loop (likely within the event compaction or SQLite sync handlers, such as `src/integrity/hydration.rs` or `src/commands/compact.rs`). 

During compaction or sync:
1. The tracker rebuilds or updates the SQLite database from the git-resident JSON transaction files (the `crosslink/hub` event stream).
2. Instead of preserving the existing, canonical historical issue UUIDs from the transaction history, the database update routine either:
   - Generates fresh random UUIDs for the synchronized issues.
   - Restores a default or zeroed UUID state.
3. This creates a divergence between the SQLite `issues` table `uuid` column and the JSON event payloads, rendering the state invalid according to the `hydration` integrity check.

### Proposed Fix
The SQLite update logic inside the sync/compaction command handlers must be modified to ensure that when updating or re-inserting issues into the local SQLite database:
1. It queries the existing SQLite record first to preserve the historical UUID, OR
2. It extracts the original, canonical UUID directly from the JSON transaction event payload (e.g., `IssueCreated` event payload) instead of generating a new one during hydration/compaction.

### Why this is critical
Because Crosslink is a local-first issue tracker, commands like `sync` and `compact` are fundamental to collaborating across machines. Frequent hydration failures force teams to either perform manual SQL database overrides or ignore integrity checks entirely, defeating the purpose of Crosslink's strong state guarantees.

---

# Submission-ready report (upstream)

> **How to use:** paste the contents of this section verbatim into a new
> issue at https://github.com/forecast-bio/crosslink/issues/new. The section
> is self-contained and repo-agnostic: it contains no internal issue numbers,
> no project-specific paths, and no references to this repository.

## Bug Report: `sync` and `compact` reset issue UUIDs in SQLite, breaking the hydration integrity check

**crosslink version:** 0.9.0-beta.1
**Environment:** Linux (expected to be platform-independent; the tracker is SQLite + git based)

### Summary

Running `crosslink sync` or `crosslink compact` overwrites the UUIDs of existing issues in the local SQLite database. Afterward, `crosslink integrity` fails its hydration check and reports `N sqlite-only issue(s)`, because the SQLite `issues.uuid` values no longer match the UUIDs recorded in the canonical JSON event log. No issue data is lost — only the UUID identity link between the SQLite projection and the event log is broken.

### Steps to reproduce

1. In a repository with existing issues and committed history, verify integrity passes:
   ```bash
   crosslink integrity
   ```
   All checks pass, including hydration.
2. Run either:
   ```bash
   crosslink sync
   # or
   crosslink compact
   ```
3. Run integrity again:
   ```bash
   crosslink integrity
   ```
4. **Observed:** the hydration check fails, reporting `N sqlite-only issue(s)`, where N is the number of issues whose SQLite UUIDs were reset (observed: all existing issues — e.g. `4 sqlite-only issue(s)` for a 4-issue tracker).

### Expected behavior

`sync` and `compact` are maintenance operations; they must not alter the UUIDs of existing issues. `crosslink integrity` should continue to pass after either command because no data was intentionally changed.

### Actual behavior

The `uuid` column of existing `issues` rows is changed during `sync`/`compact`. The hydration integrity check (which compares SQLite rows against the canonical git-resident JSON event log) then reports the mismatch as `N sqlite-only issue(s)`.

### Root-cause hypothesis

The sync/compaction path re-inserts (upserts) issues into the SQLite database from the git-resident hub event stream. When re-inserting, the update logic does not preserve each issue's historical UUID: it either generates a fresh random UUID or writes a zeroed/default value, instead of reading the canonical UUID from the `IssueCreated` event payload (or preserving the existing SQLite row's value). The hydration check then sees rows whose UUIDs do not exist in the event log and classifies them as "sqlite-only."

Note: the issue *content* (title, description, status, comments) is unaffected; only the UUID identity link diverges.

### Impact

- `sync` and `compact` are routine operations in a local-first workflow; `compact` in particular is the documented recovery step for stale-hub hydration problems.
- Every sync/compact leaves the tracker with a failing integrity check on healthy data, forcing users to either apply manual SQL corrections after each run or ignore the integrity check.
- Ignoring the check erodes trust in Crosslink's state-integrity guarantees and can mask genuine divergence.

### Workaround

Restore the canonical UUIDs in SQLite after each `sync`/`compact`:

```sql
UPDATE issues SET uuid = '<canonical-uuid>' WHERE id = <issue-id>;
```

for each affected issue, where `<canonical-uuid>` is read from the git-resident event log (`IssueCreated` event payload). This immediately restores a passing hydration check. The workaround is only practical for small issue sets.

### Suggested fix direction

In the sync/compaction SQLite update logic:

1. Before overwriting an `issues` row, read its current `uuid` and preserve it on update; and/or
2. Read the canonical UUID from the `IssueCreated` event payload in the hub event stream instead of generating a fresh UUID; and
3. Add a regression test: create one or more issues, run `sync` (and `compact`), then assert `crosslink integrity` still passes and that the `issues.uuid` values are unchanged.

---

# Evidence index (internal — do NOT submit upstream)

The submission-ready report above is intentionally repo-agnostic. This
section maps its claims to the evidence documents in this repository so the
audit trail stays explicit. None of the following references appear in the
submission text.

| Report claim | Evidence | Location |
|---|---|---|
| Symptom: sync/compact reverts SQLite UUIDs; integrity reports `4 sqlite-only issue(s)` | Session Handoff 3, Known Issues #1 (2026-06-23 reset session) | `session-handoffs/Session Handoff 3.md` |
| Workaround SQL (per-issue `UPDATE issues SET uuid = ...`) | Session Handoff 3, Known Issues #1 | `session-handoffs/Session Handoff 3.md` |
| Honest note: quirk, workaround, "worth filing upstream" | CHANGELOG.md Unreleased → Changed | `CHANGELOG.md` |
| Catalog entry: symptom, root-cause area, recovery path | Hydration failure catalog §2.4 (uuid-sync quirk) | `research-addenda/Research Addendum 04 - Hydration failure catalog.md` |
| Root-cause hypothesis (fresh/zeroed UUIDs instead of `IssueCreated` payload) | Draft analysis above + catalog §2.4 | this file (draft section) + Research Addendum 04 |

**Verification note:** in every observed occurrence, the issue data was
correct in both stores (SQLite and event log); only the UUID linkage
diverged, so only the integrity check misreports (CHANGELOG honest note,
catalog §2.4).
