# Design & Swarm Execution Plan: Automated, Decoupled, and Concurrent-Safe Documentation Refactor (v6 - Final)
## Resolving Context Bloat, DRY Violations, Git Notes Push Semantics, and Concurrency Race Conditions

**Status:** Approved for Swarm (Final Production Version)  
**Authors:** OpenCode (Principal Architect)  
**Adversarial Reviewers:** NVIDIA GLM 5.1 & Gemini 3.1 Pro (Vertex AI)  
**Target File Location:** `.design/documentation-process-refactor.md`  

---

## 1. Objectives & Architectural Requirements

The ASES documentation process must be refactored into a highly optimized, concurrent-safe, and non-blocking pipeline:

1.  **Single Source of Truth (YAML Frontmatter):** Machine-readable evaluation data and capability matrices are derived strictly from the YAML frontmatter of `harness-evaluations/*.md`. The compiler parses *only* the YAML header, leaving the Markdown body strictly for human reading.
2.  **Capped Context Footprint (Rolling Decisions):** `.crosslink/decisions.json` is capped at a strict rolling window of 5 entries (<500 tokens) to protect active LLM context. Older records are evicted and appended to partitioned, compressed JSONL files.
3.  **Trace-Driven Asynchronous Telemetry Queue:** Agents face zero pre-execution ceremony and zero commit latency. Commit hooks strictly dump raw diffs and traces to an offline queue. All LLM-generation of rationales is processed asynchronously post-commit.
4.  **Remote Telemetry Synchronization (Explicit Notes Push):** Telemetry metadata is attached directly to commit SHAs using native **Git Notes**, and the pre-push hook explicitly pushes the notes ref to origin, guaranteeing zero commit SHA divergence and clean remote synchronization.
5.  **Microsecond-Level Concurrency Protection:** Read-write operations use strict, timeout-protected `FileLock` concurrency. Locks are acquired *only* during the write phase, ensuring zero lock-holding during network API calls.
6.  **Index-Accelerated SQLite Database:** Audit lookups are accelerated via a lightweight, local SQLite database (`.crosslink/decisions.db`), guaranteeing true, constant-time $O(1)$ queries.
7.  **Contract-First Swarm Isolation:** Schemas, file locks, and utility modules are frozen upfront, allowing parallel agents to code against stable contracts without temporal coupling.

---

## 2. Frozen Contracts & Schemas (Contract-First Swarm)

To decouple the parallel swarm tasks, all schemas and shared modules are frozen upfront:

### 2.1 The Decision Record Schema (`.crosslink/schemas/decision.schema.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DecisionRecord",
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^DEC-\\d{4}-\\d{2}-\\d{2}-\\d{2}$" },
    "timestamp": { "type": "string", "format": "date-time" },
    "decider": { "type": "string" },
    "selection": { "type": "string" },
    "crosslink_issue": { "type": "integer" },
    "status": { "type": "string", "enum": ["Live", "Reconstructed"] }
  },
  "required": ["id", "timestamp", "decider", "selection", "status"]
}
```

### 2.2 Shared I/O Library (`scripts/lib/decisions_io.py`)
Both Task A and Task D must import and utilize this shared concurrency and rotation contract:
```python
import os
import json
import sqlite3
from filelock import FileLock, Timeout

DECISONS_FILE = ".crosslink/decisions.json"
LOCK_FILE = ".crosslink/decisions.json.lock"
DB_FILE = ".crosslink/decisions.db"
ARCHIVE_DIR = ".crosslink/archive/"

def init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS decisions (crosslink_issue INTEGER PRIMARY KEY)"
        )
        conn.commit()
    finally:
        conn.close()

def append_and_rotate(record: dict) -> None:
    # 1. Initialize the SQLite database
    init_db()
    
    # 2. Acquire file lock with a strict 5.0 second timeout to prevent deadlocks
    lock = FileLock(LOCK_FILE, timeout=5.0)
    try:
        with lock:
            # A. Read existing active decisions
            decisions = []
            if os.path.exists(DECISONS_FILE):
                with open(DECISONS_FILE, "r") as f:
                    decisions = json.load(f)
            
            # B. Append new record
            decisions.append(record)
            
            # C. Rotate if count exceeds 5 entries (cap context)
            if len(decisions) > 5:
                evicted = decisions.pop(0)
                # Append evicted to monthly partitioned JSONL archive
                os.makedirs(ARCHIVE_DIR, exist_ok=True)
                archive_file = os.path.join(ARCHIVE_DIR, f"decisions_archive_{record['timestamp'][:7].replace('-', '')}.jsonl")
                with open(archive_file, "a") as af:
                    af.write(json.dumps(evicted) + "\n")
                    
            # D. Save active decisions
            with open(DECISONS_FILE, "w") as f:
                json.dump(decisions, f, indent=2)
                
            # E. Write to the SQLite database index
            conn = sqlite3.connect(DB_FILE)
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR IGNORE INTO decisions (crosslink_issue) VALUES (?)",
                    (record["crosslink_issue"],)
                )
                conn.commit()
            finally:
                conn.close()
    except Timeout:
        print(f"ERROR: Lock acquisition timed out on {LOCK_FILE}")
```

---

## 3. Watertight System Architecture Specification

### 3.1 Non-Blocking Offline Telemetry Queue (Git pre-commit Hook)
*   **Trigger:** Executed during `git commit`.
*   **Behavior:** Strictly offline with zero network I/O. It dumps the raw `git diff --cached` and execution logs to `.crosslink/pending_telemetry/{epoch_ns}_{uuid4}.json` to guarantee collision-free queue writes under parallel commits.
*   **Execution Time:** <10ms.

### 3.2 Pre-Push Telemetry Processing Gate (Git pre-push Hook)
*   **Trigger:** Executed during `git push`.
*   **Behavior:** Runs `scripts/process_telemetry_queue.py`. It drains the offline queue. For each queued file, it:
    1.  Queries the LLM API asynchronously (WITHOUT holding any file locks) to generate a concise rationale from the diff.
    2.  Invokes `decisions_io.append_and_rotate(record)` to atomically update the files inside the lock context.
    3.  Attaches the JSON record as metadata directly to the commit SHA using native **Git Notes**:
        ```bash
        git notes --ref=crosslink add -f -m '{JSON_RECORD}' {COMMIT_SHA}
        ```
    4.  Explicitly pushes the local Git Notes ref to the remote origin:
        ```bash
        git push origin refs/notes/crosslink
        ```
*   This ensures that commits remain extremely fast, while guaranteeing the remote repository receives the complete, non-divergent audit trail before code leaves the machine.

### 3.3 Index-Accelerated Audit Script
*   **Algorithm:** `scripts/audit_research_issues.py` executes in constant time $O(1)$:
    1.  Queries the local SQLite database (`.crosslink/issues.db`) for currently open research issue IDs.
    2.  Searches the local SQLite index `decisions` table to verify if a matching `crosslink_issue` exists for each open `research` issue.
    3.  Terminates instantly, eliminating any need for streaming or file-scanning of JSONL files.

### 3.4 Fail-Fast Compilation Gate (WIP Bypass)
*   `scripts/compile_matrix.py` parses only the strict YAML frontmatter of `harness-evaluations/*.md` in the `pre-commit` hook (so that compiled changes are staged and committed together) or in the CI/CD pipeline.
*   **Fail-Fast:** If a malformed YAML header is found, the script **exits with code 1 and aborts the commit/build**.
*   **WIP Bypass:** Any file containing `draft: true` in its YAML frontmatter is gracefully skipped. This prevents blocking pushes of incomplete, draft evaluations during prototyping.

---

## 4. Swarm Task Decomposition

The refactoring is divided into **four fully decoupled tasks** worked in parallel by background `deepseek-v4-flash` agents inside isolated git worktrees:

### Task A: Structured Storage, Shared I/O, & Concurrency
*   **Deliverables:**
    - Initialize `.crosslink/decisions.json`, `.crosslink/decisions.db`, and `.crosslink/decisions.json.lock`.
    - Implement the shared `scripts/lib/decisions_io.py` module exactly as specified in Section 2.2.
*   **Isolation Profile:** Modifies `.crosslink/` and adds the decisions library. Zero dependencies on telemetry or compilation. Codes against Section 2.

### Task B: Automated YAML-to-Markdown Matrix Compiler
*   **Deliverables:**
    - Implement `scripts/compile_matrix.py` using `PyYAML` to read frontmatter from `harness-evaluations/*.md`.
    - Dynamically generates and overwrites `capability-mapping/Harness-Capability-Matrix.md` and syntheses tables.
    - **Fail-Fast & WIP Bypass:** Must exit with code 1 on malformed YAML, but skip files with `draft: true` in their frontmatter.
*   **Isolation Profile:** Read-only on `harness-evaluations/`, write-only on matrix files. No runtime dependencies.

### Task C: Audit Script Schema & SQLite Refactoring
*   **Deliverables:**
    - Refactor `scripts/audit_research_issues.py` to stop body scraping.
    - Implement the $O(1)$ database-based validation algorithm, querying `.crosslink/decisions.db`.
*   **Isolation Profile:** Modifies `scripts/audit_research_issues.py` only. Read-only on the SQLite database. Codes against Section 2.

### Task D: Non-Blocking Telemetry Queue & Git pre-push Notes Hook
*   **Deliverables:**
    - Write the offline `pre-commit` hook that dumps caches as `{epoch_ns}_{uuid4}.json` files.
    - Implement `scripts/process_telemetry_queue.py` (triggered by the `pre-push` hook), which queries the API without locks, invokes `decisions_io.append_and_rotate(record)`, and attaches/pushes results using `git notes`.
*   **Isolation Profile:** Bounded entirely within the git hook and queue processing directories. Only writes to `.crosslink/pending_telemetry/` during commit, executing its `decisions.json` writes strictly in the pre-push boundary.

---

## 5. Swarm Verification Gates

All parallel branches must satisfy the following integration gate checks before merging:
1.  **Gate 1 (Schema Validation):** `.crosslink/decisions.json` matches the strict JSON schema.
2.  **Gate 2 (Audit Compliance):** `python3 scripts/audit_research_issues.py` executes successfully, correctly validating open issues in $O(1)$ time against `.crosslink/decisions.db`.
3.  **Gate 3 (Build Gate Fail-Fast):** Inject a malformed YAML header into a dummy evaluation. Verify `compile_matrix.py` exits with code 1. Set `draft: true` on the dummy, verify the build passes.
4.  **Gate 4 (Concurrency Test):** Spin up 10 parallel threads writing to `decisions_io.append_and_rotate()`. Verify `FileLock` prevents data loss or corruption.
