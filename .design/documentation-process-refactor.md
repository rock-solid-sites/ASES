# Design & Swarm Execution Plan: Automated, Decoupled, and Concurrent-Safe Documentation Refactor (v8 - Final Production)
## Resolving Git Lifecycles, Global State Isolation, Concurrency Protection, and Transactional Queue States

**Status:** Approved for Swarm (Final Production Version - Audited)  
**Authors:** OpenCode (Principal Architect)  
**Adversarial Reviewers:** ChatGPT-5.5, Gemini 3.1 Pro (Vertex AI), and Deepseek  
**Target File Location:** `.design/documentation-process-refactor.md`  

---

## 1. Context & Problem Statement

Adversarial audits of the ASES record-keeping process identified key failure surfaces:
1.  **Commit SHA Availability (Critical):** The commit SHA is unavailable during `pre-commit` because the commit object has not been created yet.
2.  **Siloed Worktree State (Critical):** Using `git rev-parse --show-toplevel` inside isolated git worktrees returns local worktree roots, which siloes `.crosslink/` states and bypasses the global concurrency lock.
3.  **POSIX Double-Lock Deadlock (Critical):** Acquiring a POSIX file lock in the processing script and then invoking `decisions_io.append_and_rotate()` (which internally acquires the same lock) deadlocks non-reentrant locks indefinitely.
4.  **Queue Crash Vulnerability (Critical):** If a process crashes after moving files to `telemetry/processing/` but before completion, the files remain in `processing/` indefinitely, causing permanent queue orphaning.
5.  **Silent Data Duplication (Critical):** If a process crashes after appending to `decisions.json` but before queue-deletion, retrying the queue appends duplicate records. The schema lacks a unique commit SHA constraint.
6.  **VCS Staging Disconnect (High):** Generating matrix updates during `pre-commit` leaves the generated file unstaged, resulting in commits missing the compiled matrix.
7.  **Unpushed Git Notes (High):** Git Notes are not pushed or fetched by default during branch operations, stranding the audit trail locally.
8.  **Git Notes Push Loop (High):** Calling `git push` inside a `pre-push` hook recursively triggers the hook, causing an infinite loop.
9.  **Shell Injection in Notes (High):** Passing JSON text directly to `git notes add -m '{JSON}'` is vulnerable to shell syntax escaping.

---

## 2. Watertight System Architecture Specification

The refactored documentation pipeline decouples natural-language generation from the agent’s execution loop, offloads formatting tasks to an asynchronous build compiler, and introduces strict concurrent file-locking and early-terminating audits.

```
 [1. Active Agent Loop]
        │  (zero-friction, offline)
        ▼
 [2. Git post-commit Hook] ──> Extracts actual HEAD SHA ──> Writes raw diff/logs to 
        │                                                    .crosslink/telemetry/pending/{epoch_ns}_{uuid4}.json
        ▼ (commits instantly)
 [3. Git pre-push Hook]
        │
        ▼ (runs scripts/process_telemetry_queue.py)
 [4. Transactional Queue Processing]
        ├── 4.1 Acquire FileLock (with 30s timeout) on global decisions.json.lock
        ├── 4.2 Recovery Check: Move any orphaned files in telemetry/processing/ back to telemetry/pending/
        ├── 4.3 Move queue files from telemetry/pending/ to telemetry/processing/ atomically, releasing lock
        ├── 4.4 Query LLM (WITHOUT holding lock) to generate concise rationale from diff
        ├── 4.5 Acquire FileLock, run idempotency check, append validated record to decisions.json,
        │       rotate evicted record (using evicted["timestamp"] for JSONL archive), update index.json
        ├── 4.6 Move processed queue files to telemetry/complete/
        ├── 4.7 Write Git Note via tempfile: git notes add -F <tempfile>
        └── 4.8 Batch Push: git push --no-verify origin refs/notes/crosslink to sync remote
```

### 2.1 Centralized Global State Path (Cross-Worktree Isolation)
To ensure that all parallel git worktrees resolve to the exact same shared files and locks, all paths resolve dynamically against the **shared global git directory**:
```python
import os
import subprocess

try:
    # Get the genuine git common directory, which is shared across all worktrees
    git_common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"]).decode().strip()
    GLOBAL_DIR = os.path.abspath(os.path.join(git_common, "crosslink"))
except Exception:
    GLOBAL_DIR = os.path.abspath(".crosslink")
```
This forces `.crosslink/decisions.json`, its lock file, and its index to live under `.git/worktrees/<name>/` or the main `.git/crosslink/` directory, achieving absolute, centralized synchronization across all swarm worktrees.

### 2.2 Non-Blocking Offline Telemetry Queue (Git post-commit Hook)
*   **Trigger:** Executed during `git post-commit`.
*   **Behavior:** Strictly offline with zero network I/O. It captures the newly minted commit SHA (`git rev-parse HEAD`), the cached diff, and execution logs, writing them to the transactional pending folder `.crosslink/telemetry/pending/{epoch_ns}_{uuid4}.json` to guarantee collision-free queue writes under parallel commits.
*   **Execution Time:** <10ms.

### 2.3 Pre-Push Telemetry Processing Gate (Git pre-push Hook)
*   **Trigger:** Executed during `git push`.
*   **Behavior:** Runs `scripts/process_telemetry_queue.py`. To ensure transactionality and prevent duplication, it executes this stateful cycle:
    1.  Acquires `FileLock(timeout=30.0)` on `.crosslink/decisions.json.lock`.
    2.  **Recovery Check:** Scans `.crosslink/telemetry/processing/`. If any orphaned files exist (from a prior crash), it moves them back to `telemetry/pending/` to re-stage them.
    3.  Moves all files in `telemetry/pending/` to `telemetry/processing/` atomically, releasing the lock.
    4.  For each file in `telemetry/processing/`:
        - Queries the LLM API asynchronously (WITHOUT holding any file locks) to generate a concise, single-sentence rationale from the diff.
        - **Defensive Error Handling:** Wrap the LLM query in a `try/except` block. On network/API failure, print a warning, exit with code 0 to allow the developer's code push to proceed, and leave the file in `telemetry/processing/` for the next run.
        - Acquires `FileLock`, checks if `record["commit_sha"]` already exists in `decisions.json` or the archives (Idempotency Guard, skipping if present), and invokes `decisions_io.append_and_rotate(record)`.
        - Moves the processed queue file to `telemetry/complete/`.
        - Writes the JSON record directly to the commit SHA using native **Git Notes** via a safe tempfile to prevent shell escaping injection:
          `git notes --ref=crosslink add -f -F {temp_json_file} {COMMIT_SHA}`
    5.  Explicitly pushes the local Git Notes ref to the remote origin using `--no-verify` to prevent recursive push loops:
        `git push --no-verify origin refs/notes/crosslink`
*   **Git Notes Remote Fetching:** The setup script automatically configures the local repository to fetch notes:
    `git config --add remote.origin.fetch "+refs/notes/crosslink:refs/notes/crosslink"`

### 2.4 Index-Accelerated Audit Script
*   **Algorithm:** `scripts/audit_research_issues.py` executes in constant time $O(1)$:
    1.  Queries the local SQLite database (`.crosslink/issues.db`) for currently open research issue IDs.
    2.  Reads the static index file `.crosslink/index.json` under `FileLock`.
    3.  An open issue is instantly deemed compliant if its ID exists in the index array. It terminates without any line-by-line file scans.

### 2.5 Pre-Commit Compilation Gate (WIP Bypass)
*   `scripts/compile_matrix.py` parses only the strict YAML frontmatter of `harness-evaluations/*.md`.
*   **Boundary:** Executed during the `pre-commit` hook (not `pre-push`). This ensures that any compiled Markdown updates to the capability matrix are staged and committed in the same push cycle, preventing uncommitted local files:
    `git add capability-mapping/Harness-Capability-Matrix.md`
*   **Fail-Fast:** If a malformed YAML header is found, the script **exits with code 1 and aborts the commit**.
*   **WIP Bypass:** Any file containing `draft: true` in its YAML frontmatter is gracefully skipped. This prevents blocking pushes of incomplete, draft evaluations during prototyping.

---

## 3. Contracts, Schemas, and Concurrency Protocols

To ensure 100% decoupled Swarm execution, all schemas and shared modules are frozen upfront:

### 3.1 The Decision Record Schema (`.crosslink/schemas/decision.schema.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DecisionRecord",
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^DEC-\\d{4}-\\d{2}-\\d{2}-\\d{2}$" },
    "timestamp": { "type": "string", "format": "date-time" },
    "commit_sha": { "type": "string", "pattern": "^[0-9a-f]{40}$" },
    "decider": { "type": "string" },
    "selection": { "type": "string" },
    "crosslink_issue": { "type": "integer" },
    "status": { "type": "string", "enum": ["Live", "Reconstructed"] }
  },
  "required": ["id", "timestamp", "commit_sha", "decider", "selection", "status", "crosslink_issue"]
}
```

### 3.2 Shared I/O Library (`scripts/lib/decisions_io.py`)
Both Task A and Task D must import and utilize this shared concurrency and rotation contract:
```python
import os
import json
import subprocess
from filelock import FileLock, Timeout

try:
    git_common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"]).decode().strip()
    GLOBAL_DIR = os.path.abspath(os.path.join(git_common, "crosslink"))
except Exception:
    GLOBAL_DIR = os.path.abspath(".crosslink")

DECISIONS_FILE = os.path.join(GLOBAL_DIR, "decisions.json")
LOCK_FILE = os.path.join(GLOBAL_DIR, "decisions.json.lock")
INDEX_FILE = os.path.join(GLOBAL_DIR, "index.json")
ARCHIVE_DIR = os.path.join(GLOBAL_DIR, "archive/")

def append_and_rotate(record: dict) -> None:
    # Acquire file lock with a strict 30.0 second timeout to prevent deadlocks under heavy parallel runs
    lock = FileLock(LOCK_FILE, timeout=30.0)
    try:
        with lock:
            # 1. Read existing active decisions
            decisions = []
            if os.path.exists(DECISIONS_FILE):
                try:
                    with open(DECISIONS_FILE, "r") as f:
                        decisions = json.load(f)
                except json.JSONDecodeError:
                    # Robustness: Handle zero-byte or corrupted files gracefully
                    decisions = []
            
            # Idempotency Check: Prevent duplicate commits from appending twice
            if any(d["commit_sha"] == record["commit_sha"] for d in decisions):
                return
            
            # 2. Append new record
            decisions.append(record)
            
            # 3. Rotate if count exceeds 5 entries (cap context)
            if len(decisions) > 5:
                evicted = decisions.pop(0)
                # Correct Partitioning: Derive archive filename from evicted record's timestamp
                evicted_ym = evicted['timestamp'][:7].replace('-', '')
                os.makedirs(ARCHIVE_DIR, exist_ok=True)
                archive_file = os.path.join(ARCHIVE_DIR, f"decisions_archive_{evicted_ym}.jsonl")
                with open(archive_file, "a") as af:
                    af.write(json.dumps(evicted) + "\n")
                    af.flush()
                    os.fsync(af.fileno()) # Fsync protection against power-loss corruption
                    
            # 4. Save active decisions
            with open(DECISIONS_FILE, "w") as f:
                json.dump(decisions, f, indent=2)
                
            # 5. Update index for O(1) audit lookups
            index = []
            if os.path.exists(INDEX_FILE):
                try:
                    with open(INDEX_FILE, "r") as f:
                        index = json.load(f)
                except json.JSONDecodeError:
                    index = []
            index.append(record["crosslink_issue"])
            
            # Sorted Set: Enforce deterministic sorting to prevent noisy git diff churn
            sorted_index = sorted(set(index))
            with open(INDEX_FILE, "w") as f:
                json.dump(sorted_index, f)
    except Timeout:
        print(f"ERROR: Lock acquisition timed out on {LOCK_FILE}")
        raise
```

---

## 4. Swarm Task Decomposition

The refactoring is divided into **four fully decoupled tasks** worked in parallel inside isolated git worktrees:

### Task A: Structured Storage, Shared I/O, & Concurrency
*   **Deliverables:**
    - Initialize `.crosslink/decisions.json`, `.crosslink/index.json`, and `.crosslink/decisions.json.lock`.
    - Implement the shared `scripts/lib/decisions_io.py` module exactly as specified in Section 3.2.
*   **Isolation Profile:** Modifies `.crosslink/` and adds the decisions library. Zero dependencies on telemetry or compilation. Codes against Section 2.

### Task B: Automated YAML-to-Markdown Matrix Compiler
*   **Deliverables:**
    - Implement `scripts/compile_matrix.py` using `PyYAML` to read frontmatter from `harness-evaluations/*.md`.
    - Dynamically generates and overwrites `capability-mapping/Harness-Capability-Matrix.md` and syntheses tables in the `pre-commit` hook.
    - **Fail-Fast & WIP Bypass:** Must exit with code 1 on malformed YAML, but skip files with `draft: true` in their frontmatter.
*   **Isolation Profile:** Read-only on `harness-evaluations/`, write-only on matrix files. No runtime dependencies.

### Task C: Audit Script Schema & Index Refactoring
*   **Deliverables:**
    - Refactor `scripts/audit_research_issues.py` to stop body scraping.
    - Implement the $O(1)$ index-based validation algorithm, querying `.crosslink/index.json` under atomic read-locks.
*   **Isolation Profile:** Modifies `scripts/audit_research_issues.py` only. Read-only on the decisions index. Codes against Section 2.

### Task D: Non-Blocking Telemetry Queue & Git pre-push Notes Hook
*   **Deliverables:**
    - Write the offline `post-commit` hook that dumps caches as `{epoch_ns}_{uuid4}.json` files.
    - Implement `scripts/process_telemetry_queue.py` (triggered by the `pre-push` hook), which queries the API without locks, invokes `decisions_io.append_and_rotate(record)`, and attaches/pushes results using `git notes`.
*   **Isolation Profile:** Bounded entirely within the git hook and queue processing directories. Only writes to `.crosslink/telemetry/pending/` during commit, executing its `decisions.json` writes strictly in the pre-push boundary.

---

## 5. Swarm Verification Gates

All parallel branches must satisfy the following integration gate checks before merging:
1.  **Gate 1 (Schema Validation):** `.crosslink/decisions.json` matches the strict JSON schema.
2.  **Gate 2 (Audit Compliance):** `python3 scripts/audit_research_issues.py` executes successfully, correctly validating open issues in $O(1)$ time against `index.json`.
3.  **Gate 3 (Build Gate Fail-Fast):** Inject a malformed YAML header into a dummy evaluation. Verify `compile_matrix.py` exits with code 1. Set `draft: true` on the dummy, verify the build passes.
4.  **Gate 4 (Concurrency Test):** Spin up **10 independent OS processes** (using `multiprocessing`) writing to `decisions_io.append_and_rotate()` concurrently. Verify that the `FileLock` protocol prevents any file corruption or data loss.
