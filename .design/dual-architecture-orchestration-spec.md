# Specification: Dual-Architecture Design Options for ASES Decisional Provenance
## Resolving Concurrency, Git Lifecycles, and Distributed Consensus in AI-Assisted Development

**Status:** Ready for Swarm Selection  
**Target File Location:** `.design/dual-architecture-orchestration-spec.md`  
**Intended Audience:** High-Performance LLM Agents, Swarm Orchestrators, and Systems Architects  

---

## 1. Problem Statement & The Architectural Journey

### 1.1 The Stated Goal
The ASES project requires an absolute, un-degraded, and mathematically auditable record of AI-assisted and human-in-the-loop decisions (selection rationales, harness evaluations, and capability matrices). This "decisional provenance" serves as the **organizational memory** of our system. 

We must satisfy four competing, high-performance constraints:
1.  **Zero-Friction for Active Agent Loops:** Zero pre-execution ceremony or latency (<10ms local commits).
2.  **Absolute Context Conservation ($O(1)$ Payload):** Active context window size is strictly capped at under 500 tokens. Historical trivia must be evicted from the active context window.
3.  **Strict Distributed Data Integrity (DRY):** Zero manually duplicated facts, with 100% remote notes/branch synchronization.
4.  **Distributed Merge & Replication Consensus:** Avoid local binary database silos (like `.git/crosslink.db`) which cannot be natively pushed, fetched, or merged by Git.

### 1.2 How We Arrived Here (The Five-Round Evolutionary Journey)
The project began with a naive **File-System State Machine** (using loose JSON files, index caches, and directory renames with Python `FileLock`). This failed due to POSIX file locking limitations and race conditions under parallel execution.

We then pivoted to a **Native Embedded Database** (storing everything inside local SQLite files under `.git/`). While this solved local concurrency, five rounds of parallel, multi-model adversarial reviews (conducted by Gemini 3.1 Pro, Zhipu GLM 5.1, Deepseek, and ChatGPT) exposed a fatal **State/Consensus Paradox**: *You cannot have both local transactional locks (which require centralized binary files like SQLite) and distributed Git consensus (which requires plain-text, mergeable files) in the same tracked repository asset.*

This paradox has narrowed the design space down to **only two mathematically viable, distributed-safe architectures**. Both options decouple the **write path** (agent execution) from the **compaction/read path** (indexing and remote sync), allowing both Git and SQLite to execute flawlessly without fighting each other.

---

## 2. Option 1: The CQRS & Event-Sourced SQLite-Cache Model (Gemini/ChatGPT)

This architecture utilizes **Command Query Responsibility Segregation (CQRS)** and **Event Sourcing**, using Git strictly as a distributed consensus engine of plain-text event files, and SQLite strictly as a local, ignored, transactional cache.

```
 [1. WRITE PATH (Event Sourcing)]
     Agent Loop ──> Writes uniquely named JSON: .crosslink/events/{uuid}.json (No locks, <1ms)
                                │
                                ▼
 [2. THE LINKAGE (prepare-commit-msg)]
     Injects 'Telemetry-ID: {uuid}' into Commit Message Footer (Zero SHA timing gap)
                                │
                                ▼ (commits instantly)
 [3. LOCAL TRANSACTIONAL CACHE (Ignored SQLite)]
     .git/crosslink/runtime.db is in .gitignore (Zero distributed db silos)
     Post-commit daemon ingests events from events/ into SQLite
     SQLite handles all transactional leases, queues, and retries safely
                                │
                                ▼ (background worker / CI)
 [4. OUTPUT PATH (Asynchronous Synthesis)]
     Background daemon processes SQLite queue and queries LLM asynchronously
     Compiles and commits append-only decisions.jsonl and capability matrices
```

### 2.1 File-on-Disk Topology
```text
repo-root/
├── .gitignore                      # Ignore .git/ and local caches
├── .crosslink/
│   ├── events/                     # Git-tracked, immutable event ledger
│   │   └── 2026/06/24/
│   │       └── {uuid4}.json        # Uniquely named event files
│   └── projections/                # Statically compiled, disposable read-views
│       ├── decisions.jsonl         # Append-only processed decisions
│       └── capability-matrix.md    # Compiled Markdown matrices
└── .git/
    └── crosslink/
        └── runtime.db              # Local-only, uncommitted SQLite cache
```

### 2.2 Schema Specifications
#### A. The Immutable Event File (`.crosslink/events/.../{uuid4}.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DecisionalEvent",
  "type": "object",
  "properties": {
    "event_id": { "type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$" },
    "timestamp": { "type": "string", "format": "date-time" },
    "type": { "type": "string", "enum": ["selection", "evaluation", "review"] },
    "actor": { "type": "string" },
    "payload": { "type": "object" }
  },
  "required": ["event_id", "timestamp", "type", "actor", "payload"]
}
```

#### B. The Ephemeral Local SQLite Cache Schema (`runtime.db`):
```sql
CREATE TABLE IF NOT EXISTS telemetry_queue (
    id VARCHAR(36) PRIMARY KEY,              -- Matches the Event UUID
    timestamp TEXT NOT NULL,                 -- ISO 8601 UTC
    status VARCHAR(12) DEFAULT 'pending',    -- 'pending' | 'processing' | 'completed'
    lease_token VARCHAR(36),                 -- Unique worker UUID holding the lease
    heartbeat INTEGER,                       -- Unix epoch ns timestamp of last heartbeat
    commit_sha VARCHAR(40)                   -- Set post-commit
);
CREATE INDEX IF NOT EXISTS idx_queue_lease ON telemetry_queue (status, heartbeat);
```

### 2.3 Operational Workflow & Git Hooks
1.  **Write Phase (Agent Loop):** The agent writes the event directly as a uniquely named `.json` file to `.crosslink/events/.../{uuid4}.json`. Because files are uniquely named, **there are zero write collisions and zero locking is required**.
2.  **VCS Linkage (`prepare-commit-msg` Hook):** The hook reads the pending Event UUID from disk and injects `Telemetry-ID: <uuid>` into the commit message footer. This permanently, cryptographically binds the telemetry to the Git SHA at creation.
3.  **Local Ingestion (`post-commit` Hook):** Spawns a detached process `nohup python3 scripts/process_telemetry_queue.py &` and exits in <1ms. The script reads the events folder, resolves the commit SHA, and populates the local `runtime.db` queue.
4.  **Asynchronous Compilation (Daemon):**
    *   The background daemon claims an item in SQLite atomically using a lease update:
        ```sql
        UPDATE telemetry_queue SET status='processing', lease_token=?, heartbeat=? 
        WHERE id = (SELECT id FROM telemetry_queue WHERE status='pending' LIMIT 1) RETURNING *;
        ```
    *   Queries the LLM API asynchronously (zero commit/push latency).
    *   Appends the output to `.crosslink/projections/decisions.jsonl` and compiles the Markdown matrices.
    *   Commits the changes asynchronously using a `chore(telemetry): compile matrices [skip ci]` commit.

---

## 3. Option 2: The Git-Log, Append-Only JSONL LSM Model (GLM/Claude/Deepseek)

This architecture utilizes a **Log-Structured Merge (LSM)** design, treating the local filesystem as an append-only transaction log and Git's native tree graph as our distributed queue and consensus engine.

```
 [1. Active Agent Loop]
        │ (sub-millisecond write, zero locks, zero commit latency)
        ▼
 [2. Spool Queue] ──────────> Writes uniquely named JSONL fragment to:
                                .crosslink/queue/{uuid}.jsonl
        │
        ▼ (commits instantly, pre-commit hook does absolutely nothing)
 [3. Local Compaction Daemon]
        ├── 3.1 Scans queue/ directory
        ├── 3.2 Moves fragments to log/decisions.jsonl via POSIX Atomic File Replacement (os.replace)
        ├── 3.3 Deduplicates records using cryptographic SHA256 (Idempotency Guard)
        └── 3.4 Slices the tail of the log to compile index/decisions.json (<500 tokens)
        │
        ▼ (during git push)
 [4. Pre-Push Refactor Gate]
        ├── 4.1 Stages the compiled index: git add .crosslink/index/
        ├── 4.2 Amends last commit: git commit --amend --no-edit
        └── 4.3 Pushes the branch atomically (notes refs abolished completely)
```

### 3.1 File-on-Disk Topology
```text
repo-root/
├── .crosslink/
│   ├── queue/                      # Spool directory (ephemeral, .gitignored)
│   │   └── {uuid4}.jsonl           # Unprocessed telemetry fragments
│   ├── log/                        # Local append-only audit trail (Git-tracked)
│   │   └── decisions.jsonl         # Combined, mergeable JSONL history
│   └── index/                      # Derived state (compiled, Git-tracked)
│       ├── decisions.json          # <500 tokens, strictly capped active context
│       └── archive/                # Sharded monthly archive files (e.g. 202606.jsonl)
```

### 3.2 Schema Specifications
#### A. The Immutable Log Entry (`log/decisions.jsonl`):
```json
{
  "id": "sha256(payload)",
  "timestamp": "ISO-8601 UTC",
  "commit_sha": "git-commit-hash",
  "decider": "agent-id",
  "selection": "target-name",
  "crosslink_issue": 123
}
```
*Note: Stored as single-line, line-delimited JSON. Order does not matter.*

#### B. Git Union Merge Configuration (`.gitattributes`):
To prevent any merge conflicts when parallel branches append to the same log files concurrently, we register a native Git union merge driver:
```text
.crosslink/log/decisions.jsonl merge=union
.crosslink/index/archive/*.jsonl merge=union
```
This forces Git to automatically concatenate lines from both branches during merges, ensuring 100% automated distributed consensus.

### 3.3 Operational Workflow & Git Hooks
1.  **Write Phase (Agent Loop):** The agent writes raw, unvalidated telemetry to `.crosslink/queue/{uuid}.jsonl` in <1ms. No locks. No validation.
2.  **Pre-Commit Gate (`compile_matrix.py`):**
    *   Parses only the strict YAML frontmatter of `harness-evaluations/*.md` in the `pre-commit` hook.
    *   **Staging Integrity:** The compiler reads target files directly from the Git index using `git show :<file_path>` instead of the raw working directory, preventing unstaged changes from leaking into the matrix.
    *   If a malformed YAML header is found, the script **exits with code 1 and aborts the commit**.
3.  **Local Compaction (`post-commit` Hook):** Spawns a detached process `nohup python3 scripts/ases-compact.py &` which:
    *   Scans the `.crosslink/queue/` folder.
    *   Moves queue fragments to `.crosslink/log/decisions.jsonl` using OS-level **Atomic File Replacement** (`os.replace`), completely avoiding file locks.
    *   Deduplicates records using their cryptographic `id` hash.
    *   Slices the tail of `log/decisions.jsonl` to compile the active `index/decisions.json` (<500 tokens).
4.  **Pre-Push Sync Gate (`pre-push` Hook):**
    *   Runs `ases-compact.py` to ensure local state synchronization.
    *   Stages the compiled index: `git add .crosslink/index/`
    *   Amends the commit tree: `git commit --amend --no-edit --no-verify`
    *   This guarantees that the remote receives the code and the updated index atomically, preventing SHA divergence.

---

## 4. Architectural Selection Matrix

| Architectural Dimension | Option 1: CQRS Event-Sourced SQLite-Cache | Option 2: Git-Log Append-Only JSONL |
| :--- | :--- | :--- |
| **Commit Latency** | **Zero.** <10ms local commits. | **Zero.** <10ms local commits. |
| **Concurreny & Locking** | SQLite WAL (concurrency handled by DB engine). | **POSIX `os.replace`** (concurrency handled by OS kernel). |
| **Idempotency Guard** | `UNIQUE(commit_sha)` constraint in SQLite. | Cryptographic `SHA256(payload)` deduplication. |
| **Distributed Consensus** | Rebuilt from plain-text `events/*.json` files. | Git native **`merge=union`** text-line concatenation. |
| **Active Context Size** | Capped at 5 entries via SQLite queries. | Capped at 5 entries via JSON log-slicing. |
| **VCS State Changes** | Telemetry UUID bound to commit message footer. | Index files committed/amended during pre-push. |
| **System Complexity** | High-level (requires background processing daemon). | Low-level (requires light Python helper scripts). |
| **Silent Failures Protection** | SQLite transaction rollback (`BEGIN; COMMIT;`). | Immutable append-only log with atomic `replace()`. |
