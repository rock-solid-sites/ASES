# Bug Report: `sync` and `compact` reset issue UUIDs in SQLite, causing hydration mismatches

### Summary
In Crosslink `0.9.0-beta.1`, running either `crosslink sync` or `crosslink compact` causes the UUIDs of existing issues in the local SQLite database (`issues.db`) to be overwritten or reset. This results in immediate hydration failures (e.g., reporting `N sqlite-only issue(s)`) when checking integrity, because the SQLite-resident UUIDs no longer match the canonical JSON event log payload.

> **Draft Bug Report:** Intended for submission to https://github.com/forecast-bio/crosslink/issues/new

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
