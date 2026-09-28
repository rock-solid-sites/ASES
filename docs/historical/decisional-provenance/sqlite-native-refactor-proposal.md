# Proposal: Native SQLite Architecture for ASES Telemetry, Queue, and Decisional Provenance
## Consolidating Concurrency, Transactionality, and Indexing into a Native Database Layer

**Status:** Draft / Pending Review  
**Author:** OpenCode (Principal Architect)  
**Target File Location:** `.design/sqlite-native-refactor-proposal.md`  

---

## 1. Introduction & Current State

### 1.1 Where the Project Is Now (The "Database Impersonator" Anti-Pattern)
In its current v9 specification, the ASES Documentation Process Refactor has evolved into a highly complex, stateful system. To guarantee context capping, non-blocking telemetry, and parallel safety, we have designed a file-system based database:
*   **The Active State:** Capped `decisions.json` rolling window of 5 entries.
*   **The Archive Space:** Partitioned `decisions_archive_YYYYMM.jsonl` files (JSON Lines).
*   **The Index Caches:** Flat `index.json` arrays to accelerate lookups.
*   **The Transactional Queue:** Timestamped `{epoch_ns}_{uuid4}.json` files moved across transactional subdirectories: `.crosslink/telemetry/pending/`, `.crosslink/telemetry/processing/{uuid4}/`, and `.crosslink/telemetry/complete/`.
*   **The Concurrency Shield:** Multi-process locks managed via the Python `filelock` library (`decisions.json.lock`).

### 1.2 The Hidden Complexity of File-System State Machines
While this file-based architecture is highly elegant on paper, five rounds of rigorous adversarial reviews have exposed its structural fragility:
1.  **Shared-Writing Race Conditions:** Processing queues concurrently from multiple git worktrees requires complex, explicit file locking.
2.  **No Native Transactionality (Crash Vulnerability):** Moving files across directories is not atomic. If a process crashes mid-run, we risk orphaned files, duplicate records, or silent data loss.
3.  **Derived Index Drift:** The index (`index.json`) is derived data, meaning it can permanently drift from the active decisions file on unhandled exceptions, manual edits, or merge conflicts, producing false-pass audit results.
4.  **Scaling and Deserialization Bottlenecks:** Every record append requires deserializing the entire `decisions.json` or `index.json` array, modifying it in memory, and writing it back to disk. As the history grows, lock contention and execution time degrade linearly ($O(N)$).

---

## 2. What the SQLite Native Proposal Aims to Solve

The proposed refactor consolidates all four disjoint file-system states (JSON, JSONL, index arrays, and directory queues) into a single, transactional, concurrent-safe SQLite database: **`.crosslink/crosslink.db`** (stored inside the shared Git common directory to ensure cross-worktree synchronization).

By transitioning to a native database layer, we solve our core architectural problems at the database engine level:

### 2.1 Native Concurrency & LOCK-FREE Reads
*   **Current Issue:** Serializing all read/write paths through a single `FileLock` file blocks concurrent processes (such as the audit script) even when they only need read access.
*   **SQLite Solution:** Enabling **Write-Ahead Logging (WAL) mode** in SQLite allows concurrent readers to query the database *without acquiring any locks*, completely eliminating read-block friction. Multiple write processes are safely serialized by SQLite’s native locking mechanisms, completely removing the Python-level `filelock` library dependency.

### 2.2 True ACID Transactionality & Crash Safety
*   **Current Issue:** Moving files across physical directories is vulnerable to system crashes, leaving the queue in a corrupt, partially processed state.
*   **SQLite Solution:** Updates to the queue, decisions log, and index are wrapped in a single, atomic SQL transaction block:
    ```sql
    BEGIN TRANSACTION;
    -- Update queue status, write decision, update index
    COMMIT;
    ```
    If a process crashes or loses power at any microsecond during execution, SQLite's database journal guarantees that either the entire transaction succeeds or it rollback completely—guaranteeing **zero corruption, zero duplicate records, and zero orphaned states**.

### 2.3 Constant-Time Indexing and Zero Audit Drift
*   **Current Issue:** `index.json` is a derived list that must be manually read, set-deduplicated, and rewritten, leading to permanent write-drift and $O(N)$ time complexity.
*   **SQLite Solution:** The audit script performs a constant-time $O(\log N)$ index-lookup directly against the indexed `crosslink_issue` column of the `decisions` table:
    ```sql
    SELECT 1 FROM decisions WHERE crosslink_issue = ? LIMIT 1;
    ```
    There is **no derived index file** to maintain; the index is built natively by the SQLite engine over the source-of-truth table, eliminating any possibility of index drift.

### 2.4 Stateful, Single-Table Queue Management
*   **Current Issue:** Managing queue transactionality requires creating and moving UUID files across `pending/`, `processing/`, and `complete/` folders.
*   **SQLite Solution:** The entire telemetry queue is managed inside a single database table `telemetry_queue`. Moving a queue item from pending to processing is a simple, atomic SQL statement:
    ```sql
    UPDATE telemetry_queue SET status = 'processing', claimed_by = ? WHERE status = 'pending';
    ```
    *Lease/Heartbeat Model:* We can store the claiming process's PID and a high-resolution heartbeat timestamp. If a process crashes, the next run can instantly identify and reclaim the lease without arbitrary 10-minute wall-clock delays.

---

## 3. The Consolidated SQLite Database Schema

The entire state machine is structured under **three highly optimized tables** inside `.git/crosslink/crosslink.db`:

```
  +-----------------------------------------------------------------------------------+
  |                                CROSSLINK.DB SCHEMA                                |
  +-----------------------------------------------------------------------------------+
  | TELEMETRY_QUEUE TABLE                                                             |
  | (id VARCHAR PRIMARY KEY, timestamp TEXT, commit_sha VARCHAR, status VARCHAR,      |
  |  claimed_by INTEGER, heartbeat INTEGER, git_diff TEXT)                            |
  +-----------------------------------------------------------------------------------+
                                           │
                                           ▼ (post-execution async processing)
  +-----------------------------------------------------------------------------------+
  | DECISIONS TABLE                                                                   |
  | (id VARCHAR PRIMARY KEY, timestamp TEXT, commit_sha VARCHAR UNIQUE,               |
  |  decider VARCHAR, selection TEXT, crosslink_issue INTEGER)                        |
  | ---> INDEX on crosslink_issue (for O(log N) constant-time audit checks)           |
  | ---> INDEX on commit_sha (for O(1) idempotency checks)                            |
  +-----------------------------------------------------------------------------------+
                                           │
                                           ▼ (rotation of older decisions)
  +-----------------------------------------------------------------------------------+
  | DECISIONS_ARCHIVE TABLE                                                           |
  | (id VARCHAR PRIMARY KEY, timestamp TEXT, commit_sha VARCHAR,                      |
  |  decider VARCHAR, selection TEXT, crosslink_issue INTEGER)                        |
  +-----------------------------------------------------------------------------------+
```

### 3.1 Table definitions (SQL DDL):

```sql
-- 1. The Telemetry Queue Table
CREATE TABLE IF NOT EXISTS telemetry_queue (
    id VARCHAR PRIMARY KEY,                  -- UUIDv4 combined with timestamp
    timestamp TEXT NOT NULL,                 -- ISO 8601 UTC
    commit_sha VARCHAR(40) NOT NULL,         -- The associated git commit hash
    status VARCHAR(12) DEFAULT 'pending',    -- 'pending' | 'processing' | 'complete'
    claimed_by INTEGER,                      -- Process PID holding the lease
    heartbeat INTEGER,                       -- Unix epoch ns timestamp of last heartbeat
    git_diff TEXT NOT NULL                   -- The raw cached git diff payload
);

-- 2. The Active Decisions Table
CREATE TABLE IF NOT EXISTS decisions (
    id VARCHAR PRIMARY KEY,                  -- DEC-YYYY-MM-DD-NN
    timestamp TEXT NOT NULL,                 -- ISO 8601 UTC
    commit_sha VARCHAR(40) UNIQUE NOT NULL,  -- Unique commit SHA (Idempotency Guard)
    decider VARCHAR(255) NOT NULL,           -- Author agent ID
    selection TEXT NOT NULL,                 -- Selected target name
    crosslink_issue INTEGER NOT NULL         -- Parent Crosslink issue ID
);

-- 3. The Decisions Archive Table
CREATE TABLE IF NOT EXISTS decisions_archive (
    id VARCHAR PRIMARY KEY,
    timestamp TEXT NOT NULL,
    commit_sha VARCHAR(40) NOT NULL,
    decider VARCHAR(255) NOT NULL,
    selection TEXT NOT NULL,
    crosslink_issue INTEGER NOT NULL
);

-- Indexes for constant-time performance
CREATE INDEX IF NOT EXISTS idx_decisions_issue ON decisions (crosslink_issue);
CREATE INDEX IF NOT EXISTS idx_decisions_sha ON decisions (commit_sha);
CREATE INDEX IF NOT EXISTS idx_archive_issue ON decisions_archive (crosslink_issue);
```

---

## 4. The Simplified, Concurrency-Safe Workflow

By using SQLite, the shared I/O module `scripts/lib/decisions_io.py` is reduced from complex file-locks and JSON manipulations to clean, transactional Python DB-API calls:

```python
import sqlite3
import subprocess

def get_db_path() -> str:
    try:
        git_common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"]).decode().strip()
        return os.path.abspath(os.path.join(git_common, "crosslink", "crosslink.db"))
    except:
        return ".crosslink/crosslink.db"

def append_and_rotate(record: dict) -> None:
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30.0) # Native concurrent lock-waiting
    try:
        conn.execute("PRAGMA journal_mode=WAL;") # Enable concurrent read/write (WAL mode)
        conn.execute("BEGIN IMMEDIATE TRANSACTION;")
        
        # 1. Idempotency Guard (Indexed O(1) query)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM decisions WHERE commit_sha = ? LIMIT 1", (record["commit_sha"],))
        if cur.fetchone():
            return # Skip duplication
        
        # 2. Insert new active decision
        cur.execute(
            "INSERT INTO decisions (id, timestamp, commit_sha, decider, selection, crosslink_issue) VALUES (?, ?, ?, ?, ?, ?)",
            (record["id"], record["timestamp"], record["commit_sha"], record["decider"], record["selection"], record["crosslink_issue"])
        )
        
        # 3. Rotate older active decisions exceeding rolling cap of 5 entries
        cur.execute("SELECT COUNT(*) FROM decisions")
        count = cur.fetchone()[0]
        if count > 5:
            # Get oldest active decision
            cur.execute("SELECT id, timestamp, commit_sha, decider, selection, crosslink_issue FROM decisions ORDER BY timestamp ASC LIMIT 1")
            oldest = cur.fetchone()
            
            # Archive the evicted record
            cur.execute(
                "INSERT INTO decisions_archive (id, timestamp, commit_sha, decider, selection, crosslink_issue) VALUES (?, ?, ?, ?, ?, ?)",
                oldest
            )
            # Delete from active table (caps LLM context window size)
            cur.execute("DELETE FROM decisions WHERE id = ?", (oldest[0],))
            
        conn.commit() # Atomic, crash-safe write-ahead journal update
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```

---

## 5. Summary of Solved Failure Modes

| Failure Mode | Current File-System Solution (v9) | Stated SQLite Solution |
| :--- | :--- | :--- |
| **Double-Lock Deadlocks** | Nesting FileLock contexts (non-reentrant locks crash). | **Solved.** SQLite manages its own internal, reentrant write-locks; no manual python `FileLock` needed. |
| **Orphaned Queue Files** | Files get stuck in `processing/` forever if a crash occurs mid-run. | **Solved.** Atomic leases with PIDs and heartbeats in the `telemetry_queue` table allow instant, safe recovery of dead processes on startup. |
| **Index Drift** | `index.json` can diverge permanently from active decisions on write errors. | **Solved.** Index is constructed dynamically by the DB engine over the source tables, preventing any drift. |
| **Bypassed / Broken Idempotency** | Proposes scanning multiple `.jsonl` files on disk (unbounded file I/O). | **Solved.** A simple `UNIQUE(commit_sha)` constraint on the indexed `decisions` table provides true, constant-time idempotency checks. |
| **Context Window Bloat** | Evicts records to files, but still injects too many JSON tokens. | **Solved.** Active decisions table is strictly capped at 5 entries. Only the lightweight active table is serialized to `decisions.json` for LLM context, keeping footprint at $O(1)$. |
| **Corruption on Power-Loss** | Writing via plain `open(..., "w")` is highly vulnerable to zero-byte corruptions. | **Solved.** ACID transactions rollback automatically on crash, preserving total database integrity. |
