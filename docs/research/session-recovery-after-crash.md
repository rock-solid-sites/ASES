---

title: Session Recovery After VPS Crash
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:

* server-crash-postmortem.md
* Documentation Standard

consumed_by:

* Future agent sessions
* Operational runbooks

related_documents:

* to-file/crosslink-gates/server-crash-postmortem.md
* to-file/handoff-failure-analysis.md

supersedes: []

## last_updated: 2026-07-20

# Session Recovery After VPS Crash

## Purpose

Document what survives, what is lost, and how to assess session state after a VPS crash during an active opencode session. This record was produced by investigating the July 13, 2026 crash that killed an active Crosslink Gates research session.

---

## Incident Reference

**Date:** 2026-07-13, ~17:46 UTC
**Session:** `ses_0a6ae7d67ffeg41R1H3eP6IQPo` ("Read evidence-based-gates")
**Agent:** `build` (model: `hy3-free`)
**Duration:** Jul 13 02:32 → Jul 14 00:58 (22.5 hours, spans crash)
**Crash cause:** Memory exhaustion from concurrent subagents on 8GB VPS (see server-crash-postmortem.md)

---

## Findings

### What Survives a Crash

| Layer | Storage | Survives? | Notes |
|-------|---------|-----------|-------|
| **Crosslink issues** | SQLite (`issues.db`) | ✅ Yes | File on disk, no in-memory buffer |
| **Crosslink events** | Git (event log commits) | ✅ Yes | Committed to git before crash |
| **Crosslink comments** | SQLite | ✅ Yes | Written directly to DB |
| **Git commits** | Git objects | ✅ Yes | Immutable once written |
| **Opencode session metadata** | SQLite (`opencode.db`) | ✅ Yes | Session record (title, timestamps, agent, model) persists |
| **Tool output files** | Disk (`~/.local/share/opencode/tool-output/`) | ✅ Yes | Written per-tool-call |
| **Opencode log** | Disk (`~/.local/share/opencode/log/`) | ✅ Yes | Append-only log file |
| **Research documents** | Git (committed files) | ✅ Yes | If committed before crash |

### What Is Lost in a Crash

| Layer | Storage | Lost? | Notes |
|-------|---------|-------|-------|
| **AI conversation messages** | SQLite (`session_message` table) | ⚠️ Possibly | Buffer may not flush to disk before crash |
| **In-memory daemon state** | Process memory | ✅ Yes | Daemon log confirms: "Daemon exiting due to parent termination" |
| **Uncommitted working tree changes** | Disk (untracked) | ⚠️ Possibly | Depends on filesystem sync |
| **Git index state** | `.git/index` | ⚠️ Possibly | May end up in `AD` state (staged but deleted from working tree) |

### The `AD` Index State

After the crash, two files appeared in `git status` as:

```
AD .crosslink/issues-snapshot.json
AD other_only.txt
```

This means:
1. Files were `git add`-ed to the index (staged)
2. Files were then deleted from the working tree before commit
3. The index considers them "added" but the working tree disagrees

**Resolution:** `git reset HEAD` clears the broken index state. This is a crash artifact, not data loss — the files were likely generated transiently during the staging operation.

---

## Opencode Session Message Storage

### Observed Behaviour

The `session_message` table in `opencode.db` contained only **93 messages**, all from **June 24 – July 1**. No messages from July 13+ were persisted despite sessions running actively.

### Hypothesis

Opencode may buffer conversation messages in memory and flush periodically. If the flush interval is longer than the time between last flush and crash, messages are lost. This is consistent with:

- Session metadata (written at session start) survives
- Tool outputs (written per-call) survive
- Conversation messages (buffered) do not survive

### Implication for Recovery

After a crash, **do not rely on opencode's `/sessions` command to reconstruct conversation content**. Instead, rely on:

1. Git history (commits, event logs)
2. Crosslink issue database (issues, comments, labels)
3. Tool output files on disk
4. Research documents committed to the repository
5. The opencode log (tool calls and permission evaluations are logged, though not full conversation)

---

## Recovery Procedure

After a VPS crash, run these checks in order:

### 1. Assess Git State

```bash
git status
git log --oneline -10
```

Look for:
- `AD` staged files (crash artifact — run `git reset HEAD`)
- Lock files in `.git/` (should be absent after clean reboot)
- Merge/rebase state in `.git/` (should be absent)
- Unpushed commits

### 2. Assess Crosslink State

```bash
crosslink status
sqlite3 .crosslink/issues.db "SELECT id, title, status FROM issues WHERE status='open' ORDER BY id;"
```

Look for:
- Daemon status (may need restart: `crosslink daemon start`)
- Active issue (in `.crosslink/.active-issue`)
- Stale sessions or locks

### 3. Assess Opencode State

```bash
sqlite3 ~/.local/share/opencode/opencode.db "SELECT id, title, created_at, updated_at FROM session ORDER BY updated_at DESC LIMIT 10;"
ls -la ~/.local/share/opencode/tool-output/
```

Look for:
- Last session metadata (reconstructable)
- Tool output files (may contain useful intermediate work)
- Log entries around crash time

### 4. Reconstruct Work from Artifacts

If conversation content is lost, reconstruct what happened from:

1. **Git commits** — `git log --oneline --since="<date>"`
2. **Crosslink events** — `sqlite3 .crosslink/issues.db "SELECT * FROM events WHERE created_at LIKE '<date>%' ORDER BY seq;"`
3. **Issue comments** — `sqlite3 .crosslink/issues.db "SELECT * FROM comments WHERE created_at LIKE '<date>%';"`
4. **Research documents** — committed files in the repository
5. **Tool outputs** — `ls -lt ~/.local/share/opencode/tool-output/ | head -20`

---

## Key Lessons

1. **Session records and session content are independent.** The session metadata (title, timestamps) is written at session start. The conversation messages are buffered. After a crash, you may have one without the other.

2. **Crosslink state is crash-resilient.** Issues, events, and comments are written directly to SQLite and git. They survive crashes that kill opencode sessions.

3. **Committed work is safe.** Anything committed to git before the crash is recoverable. The risk window is between "last commit" and "crash."

4. **The `/sessions` command is not a recovery tool.** It shows session metadata, not conversation content. For post-crash reconstruction, use git log, crosslink DB queries, and tool output files.

5. **Multiple concurrent subagents amplify crash risk.** The July 13 crash was caused by memory exhaustion from context cloning across subagents. This is documented separately in the server-crash-postmortem.md.

---

## Open Questions

1. What is opencode's message flush interval? Can it be configured?
2. Would enabling WAL mode on `opencode.db` improve crash resilience for messages?
3. Should crosslink's session tracking be made mandatory (strict mode) to ensure all work is wrapped in a recoverable session record?
