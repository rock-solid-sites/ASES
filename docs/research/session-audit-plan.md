---

title: Session Audit and DB Recovery Plan
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Operational
canonical_repository: edases

depends_on:

* session-recovery-after-crash.md
* server-crash-postmortem.md

consumed_by:

* Current and future opencode sessions

related_documents:

* docs/research/session-recovery-after-crash.md
* to-file/crosslink-gates/server-crash-postmortem.md

supersedes: []

## last_updated: 2026-07-20

# Session Audit and DB Recovery Plan

## Purpose

Audit all 969 opencode sessions to identify work worth preserving before deleting session data to reclaim the 890MB opencode.db. Must be executed in stages to avoid OOM crashes on the 8GB VPS.

---

## Current State

| Metric | Value |
|--------|-------|
| Total sessions | 969 |
| DB size | 890 MB |
| Date range | 2026-06-21 to 2026-07-20 (29 days) |
| Backup files | 1.6 GB (`.backup-20260717` + `.bak`) |
| Never archived | 969 / 969 |
| Never compacted | 969 / 969 |

### Projects

| Project ID (prefix) | Sessions | Events | Likely Repo |
|---------------------|----------|--------|-------------|
| `9cc66630...` | 526 | 102,609 | tripn-astro |
| `b826eb8e...` | 320 | 82,852 | ASES/EDASES |
| `d6567cd2...` | 37 | 3,552 | crosslink-related |
| `38bb1843...` | 30 | — | unknown |
| `a5edb4f3...` | 29 | — | unknown |
| `global` | 25 | 890 | testing/debug |
| `6727749c...` | 2 | — | unknown |

### Top 5 Sessions by Event Count

| Session | Title | Events |
|---------|-------|--------|
| `ses_098d3708...` | north-mini-code review plan | 12,004 |
| `ses_09f81174...` | Updating crosslink for Opencode compatibility | 7,112 |
| `ses_0b1ef0e6...` | Making Crosslink work with any model | 6,513 |
| `ses_0a25746b...` | Plan conversation history analysis | 5,572 |
| `ses_0a156a12...` | Check project status via crosslink | 5,402 |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| OOM from loading full session data | Process in batches of 20-30 sessions, metadata only |
| Losing undocumented work | Cross-reference with git, crosslink DB, committed docs before deleting |
| Crash mid-audit | Export audit findings to committed files after each stage |
| Subagent context bloat | Each audit subagent gets only the batch it needs, not full DB |

---

## Stage 1: Metadata Extraction (low memory)

**Goal:** Build a complete session index with metadata only — no message content loaded.

**Approach:** Single SQLite query, output to file.

**Commands:**
```bash
sqlite3 ~/.local/share/opencode/opencode.db \
  "SELECT s.id, s.project_id, s.title, s.agent, s.model,
          datetime(s.time_created/1000, 'unixepoch') as created,
          datetime(s.time_updated/1000, 'unixepoch') as updated,
          s.cost, s.tokens_input, s.tokens_output
   FROM session s
   ORDER BY s.time_created;" \
  -header -csv > /tmp/session-index.csv
```

**Output:** `/tmp/session-index.csv` — committed to repo after review.

**Memory impact:** Negligible (metadata only, no JSON blobs).

---

## Stage 2: Per-Project Session Grouping

**Goal:** Group sessions by project, classify each as "productive" or "ephemeral."

**Approach:** Read Stage 1 output, classify by title patterns.

**Classification rules:**
- **Ephemeral** (auto-delete candidates):
  - Titles matching `@... subagent` with no crosslink issue reference
  - Titles matching `New session - <timestamp>`
  - Sessions with 0 events
  - Test/debug sessions (`global` project)
- **Productive** (needs audit):
  - Sessions with crosslink issue references
  - Sessions with meaningful titles (not auto-generated)
  - Sessions with high event counts (>100)
  - Sessions with high cost (> $0.50)

**Output:** `/tmp/session-classification.csv`

**Memory impact:** Negligible (CSV processing only).

---

## Stage 3: Cross-Reference with Git and Crosslink

**Goal:** For each productive session, verify work was committed or documented.

**Approach:** For each project repo, run a subagent that:

1. Gets the session date range from Stage 2
2. Runs `git log --oneline --since=<start> --until=<end>` in the project repo
3. Queries crosslink DB for issues/comments in that date range
4. Checks if research docs exist in the repo for that timeframe
5. Marks session as "documented" or "needs review"

**Batching:** Process one project at a time. Within each project, process date ranges in 3-day windows.

**Memory impact:** One subagent at a time. Each subagent loads only git log + crosslink queries for a small date range.

**Output per project:**
```
/tmp/audit-<project-prefix>.md
```

---

## Stage 4: Deep Audit of Undocumented Sessions

**Goal:** For sessions marked "needs review" in Stage 3, check if any work was lost.

**Approach:** For each undocumented session:

1. Query session metadata (title, agent, model, cost, date)
2. Check if a crosslink issue exists for that work
3. Check if commits exist in any branch for that date
4. Check tool output files: `ls -lt ~/.local/share/opencode/tool-output/ | head`
5. Classify as:
   - **Documented elsewhere** — work found in git/crosslink/docs
   - **Subagent ephemeral** — disposable subagent session
   - **Potentially lost** — work that may not have been captured

**Batching:** Process 10 sessions per subagent invocation.

**Memory impact:** Low — metadata queries only, no full message loading.

**Output:**
```
/tmp/undocumented-sessions.md
```

---

## Stage 5: Export Preserved Sessions

**Goal:** Export any sessions identified as worth preserving before deletion.

**Approach:**
```bash
opencode export <session-id> --sanitize > /tmp/session-exports/<session-id>.json
```

**Batching:** One export at a time. Monitor memory between exports.

**Output:** `/tmp/session-exports/` directory, committed to repo.

---

## Stage 6: Deletion and VACUUM

**Goal:** Delete ephemeral sessions, then reclaim space.

**Approach:**
1. Delete ephemeral sessions in batches of 50:
   ```bash
   opencode session delete <id>
   ```
2. Checkpoint WAL:
   ```bash
   sqlite3 ~/.local/share/opencode/opencode.db "PRAGMA wal_checkpoint(TRUNCATE);"
   ```
3. VACUUM:
   ```bash
   sqlite3 ~/.local/share/opencode/opencode.db "VACUUM;"
   ```
4. Delete backup files:
   ```bash
   rm ~/.local/share/opencode/opencode.db.backup-20260717
   rm ~/.local/share/opencode/opencode.db.bak
   ```

**Memory impact:** VACUUM rewrites the entire DB. Must be done with no other opencode sessions running.

**Expected result:** DB size should drop from ~890MB to ~200-300MB (estimate based on productive session data).

---

## Stage 7: Document Findings and Update Recovery Guide

**Goal:** Commit all audit artifacts and update session-recovery-after-crash.md with lessons learned.

**Artifacts to commit:**
- `session-index.csv`
- `session-classification.csv`
- `audit-<project>.md` files
- `undocumented-sessions.md`
- Any exported session JSONs

---

## Execution Rules

1. **Two concurrent subagents max.** Light audit work (SQLite queries, git log) is safe at concurrency 2. No more.
2. **Metadata first.** Never load full message/event data until Stage 5.
3. **Commit after each stage.** Audit findings must persist across crashes.
4. **Monitor memory.** Check `free -m` before and after each subagent.
5. **3-day windows.** Date range queries should never span more than 3 days.
6. **No VACUUM with sessions active.** Close all opencode instances before Stage 6.
7. **Single subagent for heavy stages.** Stages 5 (export) and 6 (delete/VACUUM) run one at a time.
