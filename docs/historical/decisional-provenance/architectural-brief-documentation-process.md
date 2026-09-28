# Architectural Brief: Documentation & Decisional Provenance Process Refactor
## State of the Architecture, Explored Paradigms, and Identified Failure Modes

**Status:** Under Architectural Review (Brief for Fresh Reviewers)  
**Author:** OpenCode (Principal Architect)  
**Target File Location:** `.design/architectural-brief-documentation-process.md`  

---

## 1. Project Objectives (What We Are Trying to Do)

The ASES project relies on maintaining an absolute, un-degraded, and mathematically auditable record of AI-assisted and human-in-the-loop decisions (including selection rationales, harness evaluations, and capability matrices). This record-keeping serves as the **organizational memory** of our system.

Our core challenge is designing a documentation and telemetry process that satisfies three competing constraints:
1.  **Zero-Friction for Active Agent Loops:** High-performance coding agents must face zero pre-execution ceremony or latency. Writing long natural-language justification essays prior to execution slows down throughput.
2.  **Absolute Context Conservation ($O(1)$ Payload):** Narrative-heavy historical logs (syntheses, rationales, old evaluations) must be evicted from the active context window. The active context footprint must be strictly capped at a minimal token budget (e.g., <500 tokens) to prevent context-window saturation and latency.
3.  **Strict Distributed Data Integrity (DRY):** Facts must have a single source of truth. We must eliminate duplicate manual entries across folders, which cause write-drift, while ensuring that the audit trail is 100% synchronized across distributed clones and git worktrees.

---

## 2. Paradigms Explored So Far

To achieve these goals, the architecture has explored several major paradigms across five rounds of peer and adversarial reviews:

```
  +---------------------------------------------------------------------------------+
  |                             EVOLUTION OF PARADIGMS                              |
  +---------------------------------------------------------------------------------+
  | EPOCH 1: Predecessor CSS/JS Overlay ─────────────────────────> [Aesthetic War]   |
  +---------------------------------------------------------------------------------+
                                           │
                                           ▼ (Pivot to decoupled backend)
  +---------------------------------------------------------------------------------+
  | EPOCH 2: PHP WordPress decoupled plugin ─────────────────────> [MySQL DB Bloat]  |
  +---------------------------------------------------------------------------------+
                                           │
                                           ▼ (Pivot to stateless edge serverless)
  +---------------------------------------------------------------------------------+
  | EPOCH 3: Astro Serverless Module (Cloudflare Pages/Workers) ──> [Static & DRY]  |
  +---------------------------------------------------------------------------------+
                                           │
                                           ▼ (Need for local-first metadata)
  +---------------------------------------------------------------------------------+
  | PARADIGM A: File-System State Machine                                           |
  | - Queue: pending/, processing/, complete/ directories                           |
  | - Storage: decisions.json, index.json, decisions_archive_YYYYMM.jsonl files      |
  | - Concurrency: Python 'filelock' library                                        |
  +---------------------------------------------------------------------------------+
                                           │
                                           ▼ (Need to eliminate file-locking complexity)
  +---------------------------------------------------------------------------------+
  | PARADIGM B: Local Embedded Database                                             |
  | - Centralized state, queue, and index under .git/crosslink/crosslink.db         |
  | - Concurrency: SQLite WAL (Write-Ahead Logging) & native transaction locks       |
  +---------------------------------------------------------------------------------+
```

---

## 3. Structural Failure Modes & Issues Identified

Adversarial audits conducted by multiple parallel LLM engines (Gemini 3.1 Pro Preview, Zhipu GLM 5.1, Deepseek, and ChatGPT) have exposed critical, systemic vulnerabilities across both Paradigms:

### 3.1 Version Control System (VCS) & Git Hook Integration Gaps
*   **The Commit SHA Timing Mismatch (Critical):** If telemetry is dumped during `pre-commit`, the commit SHA is unavailable because the commit object has not been created yet.
*   **The Unpushed Notes Ref (Critical):** Git Notes (`git notes`) are local refs and are *not pushed or fetched by default* during standard branch operations. This leaves the remote repository permanently out of sync with the local audit trail.
*   **The Premature Notes Push (Critical):** Pushing notes inside the `pre-push` hook forces Git to transmit the notes and the associated commit objects to the remote *before* the remote validates the main push. If the main branch push is rejected (e.g., due to branch protections or rejections), the remote is left with orphaned notes for commits that do not exist on the remote branch, corrupting history.
*   **The Staging Area Leakage (High):** Compiling tracked Markdown assets (like the Capability Matrix) inside `pre-commit` from the raw filesystem working directory leaks unstaged code changes (`git add -p`) into the final commit.
*   **The Pre-Push Matrix Update Drift (High):** Overwriting or generating tracked Markdown files during `pre-push` results in uncommitted changes left behind in the local working directory.

### 3.2 Concurrency & Locking Failures
*   **Siloed Worktree State (Critical):** Using standard relative paths or `git rev-parse --show-toplevel` inside isolated git worktrees returns local worktree roots. This siloes `.crosslink/` states, preventing parallel agents from coordinating writes and bypassing the concurrency lock.
*   **POSIX Double-Lock Deadlock (Critical):** POSIX file locks (used by `filelock` and `lockf` in Python) are non-reentrant. Nesting lock acquisitions in a processing script and an internal I/O library will deadlock the process indefinitely.
*   **Lock Contention Under Swarm Loads (High):** Holding an exclusive lock during slow, synchronous network LLM API calls completely blocks and serializes parallel swarm agents.
*   **The Thread-based Concurrency False-Pass (High):** POSIX locks are per-process, not per-thread. Testing lock safety using thread pools yields false-passes, masking real multi-process race conditions.

### 3.3 Transactionality & Queue Processing Failures
*   **The processing/ Queue Orphan (Critical):** If a queue-processing process crashes after moving files to `.crosslink/telemetry/processing/{uuid}/` but before completion, the files are permanently orphaned. Since the main loop only polls `pending/`, those files will never be reprocessed.
*   **The Queue-Stealing Race Condition (Critical):** Releasing the lock while files are in a shared `processing/` directory allows concurrent pre-push hooks to "recover" and steal active files mid-run.
*   **The Bulk-Claiming Queue Defect (Critical):** Dequeuing telemetry via bulk queries like `UPDATE telemetry_queue SET status='processing' WHERE status='pending'` will atomically claim *all* pending items at once, preventing proper multi-agent distribution.
*   **Fragile PID-based Leases (Critical):** Using OS PIDs to track lease ownership is fragile because PIDs are recycled by the operating system.

### 3.4 Data Integrity, Idempotency, and DRY Violations
*   **The Archive Idempotency Loophole (Critical):** Restricting idempotency checks to the active, rolling `decisions.json` allows replayed queue files to write duplicate records to the archives once the original record has rotated out.
*   **The Derived Index Drift (High):** Maintaining a separate `index.json` file creates a derived state that can permanently drift from the active decisions file on unhandled exceptions, manual edits, or merge conflicts.
*   **The "Database Impersonator" Anti-Pattern (High):** Attempting to build transactional event-sourcing structures out of loose JSON files, index arrays, and directory renames is highly overengineered and prone to power-loss corruption.
*   **The Distributed State Divergence (Critical - SQLite Only):** Storing state in a local binary SQLite database (`crosslink.db`) completely destroys Git's distributed consensus. Binary files cannot be merged or synchronized across machines, leaving developers with permanently fragmented, divergent audit trails.

---

## 4. Challenge for the Reviewer

We are currently at an architectural crossroads. We must find a way to resolve:
1.  How to achieve **exactly-once processing and atomic, crash-safe transactionality** locally,
2.  WITHOUT introducing **network LLM latency inside git commit/push hooks**,
3.  WITHOUT **corrupting Git branch lifecycles or SHA histories**,
4.  And crucially, **WITHOUT breaking Git's distributed replication and merge consensus** (avoiding local binary database silos).

How can we structure our telemetry, queue, and index layers to satisfy all of these constraints? Propose your solution.
