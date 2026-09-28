Claude:

# Adversarial Review: ASES Documentation & Decisional Provenance Architecture

## Opening Assessment

The brief is well-articulated and self-aware — the authors have done genuine work cataloguing failure modes across five review rounds. But self-awareness of a problem is not the same as diagnosing its root cause. Reading the brief carefully, the failure modes listed in Section 3 are not independent bugs to be patched one by one. They are *symptoms* of a single, recurring architectural mistake that the project keeps repeating in different forms:

**The project is attempting to build a distributed, transactional, append-only audit ledger on top of infrastructure that was never designed to be a database, while simultaneously trying to use Git — a content-addressable version control system — as both the transport layer and the consistency guarantee.**

Every paradigm explored so far has been a variation of this same error. The refactors between Paradigm A and Paradigm B did not change the fundamental design assumption; they only swapped one wrong substrate (the filesystem) for a different wrong substrate (SQLite). The correct solution requires abandoning that assumption entirely, not iterating on it.

---

## Part I: Adversarial Critique

### 1.1 The Meta-Failure: Conflating Four Distinct Concerns

The architecture treats the following as a single unified problem, which is why every proposed solution collapses under load:

- **Capture** — recording that a decision or action occurred
- **Queue** — buffering events for asynchronous downstream processing
- **Index** — making the audit trail queryable
- **Replication** — synchronizing the trail across machines and clones

These four concerns have incompatible performance and consistency requirements. Capture must be synchronous, zero-latency, and crash-safe. Queue processing must be asynchronous and idempotent. Index maintenance is a derived read concern. Replication is a distributed systems concern. Trying to satisfy all four in a single file, hook, or database transaction is the source of virtually every failure mode listed in Section 3.

### 1.2 The Git Hook Trap

The project has made a serious category error by placing audit logic inside Git hooks. Git hooks are not a messaging bus. They are side-effect triggers designed for lightweight, fast, synchronous validation — rejecting a commit with a lint error, checking a commit message format. The moment you attempt to do any of the following inside a hook, you have left the design envelope that hooks were built for:

- Calling an LLM API (network latency, partial failures)
- Writing to a shared mutable state file (concurrency, locking)
- Generating derived artifacts (staging area contamination)
- Synchronizing a distributed audit trail (distributed consensus)

The Commit SHA Timing Mismatch, the Premature Notes Push, the Staging Area Leakage, and the Pre-Push Matrix Update Drift are not bugs in the hook implementation. They are the natural, inevitable consequence of using hooks for work that hooks cannot safely do. No amount of careful sequencing, staging area gymnastics, or notes-ref management will fix this, because the constraint is structural. Git hooks execute inside a transaction that has not yet committed; you cannot safely derive or persist state that depends on post-commit values from inside a pre-commit context.

### 1.3 The "Database Impersonator" Problem Is Understated

The brief names the "Database Impersonator" anti-pattern but treats it as a "High" severity issue rather than the architectural root cause it actually is. The filesystem queue (`pending/`, `processing/`, `complete/`) is not just overengineered — it is a manual reimplementation of a work queue, and a bad one. Every property that makes a proper work queue reliable (atomic dequeue, exactly-once delivery, crash recovery, lease management) has been hand-rolled in ways that reproduce known failure modes from distributed systems literature: the Two Generals problem appears in the Queue-Stealing Race Condition, the ABA problem appears in the PID recycling issue, and the lack of write-ahead logging appears in the Queue Orphan failure.

The authors correctly identify that SQLite solves some of these problems. But then the SQLite proposal introduces the Distributed State Divergence failure, which is not a fixable bug — it is a fundamental incompatibility between a local binary database and Git's distributed replication model. A binary file in `.git/crosslink/` cannot be branched, merged, or replicated by `git fetch`. You cannot have both "SQLite transactions" and "Git distributed consensus" on the same data store. This is not an implementation gap; it is a mathematical impossibility with the current design.

### 1.4 The $O(1)$ Context Constraint Is Being Violated at the Design Level

The brief correctly identifies the need to cap active-context token footprint. But the proposed solutions in both paradigms require the active agent to reason about queue state, lock state, and archive rotation at execution time — which means that complexity is being pushed into the agent's reasoning loop rather than eliminated from it. A truly $O(1)$ context payload means the agent writes a single structured record and stops. It does not poll queues, it does not acquire locks, and it does not know or care whether prior records have been archived. The queue, index, and replication concerns must be completely invisible to the writing agent.

### 1.5 The DRY Constraint Is Structurally Unsatisfied

The brief cites DRY as a core requirement, but both paradigms maintain at least three distinct representations of the same fact: the raw decision record, the index entry, and the archive rotation. These are kept in sync by procedural code that runs only at specific lifecycle points (commit, push). Any failure between those points — a crash, a rejected push, a manual edit — leaves the representations permanently divergent. This is not DRY. DRY requires a single authoritative representation from which all other views are derived on read, not maintained in parallel on write.

---

## Part II: Proposed Solution

The core principle of the solution is: **separate capture from processing, and make capture the only synchronous concern.**

### 2.1 Foundational Constraint Remapping

Before proposing mechanics, the constraints must be restated correctly:

- Capture must be: **synchronous, atomic, append-only, and produce no derived state**
- Processing must be: **asynchronous, idempotent, outside all Git hooks**
- Index/Query must be: **derived on demand from the append-only log, never maintained in parallel**
- Replication must be: **handled entirely by Git's existing object model, not by a separate sync mechanism**

### 2.2 The Capture Layer: Append-Only JSONL

Each decision event is written as a single-line JSON object appended to a flat JSONL file tracked by Git. The file lives at a well-known path such as `audit/decisions.jsonl`. The write is a single `flock`-guarded `O_APPEND` operation — the only operation that is safe to perform synchronously inside a hook context, because it requires no read-before-write, no index update, no queue state, and no derived artifact generation.

Each record must contain: a client-generated UUID (not a Git SHA, which is unavailable at write time), a wall-clock ISO-8601 timestamp, a human-readable event type, a structured payload, and a content hash of the payload for integrity verification. The Git SHA is deliberately omitted from the capture record. It is attached later, asynchronously, by the processing layer.

This eliminates: the Commit SHA Timing Mismatch (SHA is not required at write time), the Staging Area Leakage (no derived artifacts are generated), and the Database Impersonator anti-pattern (a JSONL file is genuinely append-only and Git-native).

The hook's only job is: open file, flock, append one line, release. This executes in under 5 milliseconds with no network call and no read dependency.

### 2.3 The Queue Layer: Git's Object Store as the Queue

Rather than maintaining a separate queue directory or database, the queue is implicit in the Git object store. When the agent writes a JSONL record, it is committed to a branch. The existence of unprocessed commits on that branch is the queue. The processing agent walks the Git log from the last processed SHA, identifies unprocessed records, processes them, and writes back a pointer to the last processed SHA to a file at `audit/.processed_head`.

This approach gives you: exactly-once processing (the processed head pointer is a monotonic cursor), crash safety (if the processor crashes, the processed head is not advanced, so records are reprocessed on restart — idempotency handles the duplicate), and zero separate queue infrastructure.

The processed head pointer file is also tracked by Git, which means it replicates automatically.

### 2.4 The Processing Layer: Asynchronous, Outside All Hooks

Processing is triggered by a lightweight post-commit hook that does nothing except spawn a detached background process — `nohup ./scripts/process_audit.py &` — and exits immediately. The hook does not wait for the process to complete. The hook's execution time is the time to fork a process, which is under 1 millisecond.

The background processor:

1. Reads the current `audit/.processed_head` value
2. Runs `git log {processed_head}..HEAD -- audit/decisions.jsonl` to get unprocessed commits
3. For each commit in order, reads the JSONL lines introduced by that commit, enriches each record with the now-available commit SHA, and writes the enriched records to `audit/archive/YYYY-MM.jsonl`
4. Advances the `audit/.processed_head` pointer
5. Commits the archive updates and pointer advance as a single atomic Git commit

Because this runs outside all hooks, LLM API calls for enrichment or synthesis can happen here without any latency concern. Because it uses Git's own commit graph as the queue, there is no separate queue infrastructure to corrupt or orphan.

This eliminates: the Network LLM Latency in hooks, the Queue Orphan failure (incomplete processing leaves the pointer un-advanced, records are reprocessed), and the Queue-Stealing Race Condition (a single processor owns the pointer; parallel processors are resolved by optimistic locking on the pointer file, with the losing writer simply retrying).

### 2.5 The Distributed Replication Layer: Pure Git

Because the entire audit trail is JSONL files and pointer files tracked by Git, replication is `git push` and `git fetch`. There is no separate sync mechanism, no Git Notes ref, and no binary database file. Merge conflicts in JSONL files are resolved by the standard append-only merge strategy: both sides' appended lines are retained, and the merged file contains the union. This is always correct for an audit log because audit records are never updated, only appended.

The processed head pointer file will conflict on merge if two processors have been running independently (as in a branched worktree scenario). This conflict is resolved by taking the chronologically later pointer value — a simple, deterministic, automatable rule — because the record with the higher-SHA pointer necessarily processed a superset of the records processed by the lower-SHA pointer, given that both sides started from the same base.

This eliminates: the Distributed State Divergence (no binary database), the Unpushed Notes Ref (no Git Notes), and the Premature Notes Push (no notes push at all).

### 2.6 The Index Layer: Derived on Demand

There is no maintained index file. The index is derived by scanning the JSONL archive on demand. For an audit trail of reasonable size (tens of thousands of records), a full scan of compressed JSONL files takes under a second on modern hardware. If query performance becomes a bottleneck, a local SQLite index is built ephemerally at query time from the JSONL source and discarded after the query. This ephemeral SQLite is never committed to Git and never treated as a source of truth.

This eliminates: the Derived Index Drift failure entirely, because there is no maintained derived index to drift.

### 2.7 Worktree Coordination

The worktree siloing problem is resolved by anchoring all audit paths to the Git common directory (`git rev-parse --git-common-dir`) rather than the worktree root or the toplevel. In a multi-worktree setup, `git rev-parse --git-common-dir` returns the shared `.git/` directory, not the per-worktree `.git` file. All worktrees write to the same `audit/decisions.jsonl` path resolved through the common directory. The `flock`-on-append serializes concurrent writes safely without any application-level lock manager.

This eliminates: the Siloed Worktree State failure.

### 2.8 Idempotency

Every record carries a client-generated UUID. The processor maintains a bloom filter (or a simple set, for small deployments) of processed UUIDs in memory during a processing run. Before writing an enriched record to the archive, it checks whether the UUID has already been archived. This check operates against the full archive, not just the rolling active file, which closes the Archive Idempotency Loophole.

---

## Summary Table of Resolved Failures

Each failure mode from Section 3 maps to a specific resolution:

The Commit SHA Timing Mismatch is resolved because SHAs are attached asynchronously by the processor, not at write time. The Unpushed Notes Ref is resolved because Git Notes are not used. The Premature Notes Push is resolved for the same reason. The Staging Area Leakage is resolved because no derived artifacts are generated inside hooks. The Pre-Push Matrix Update Drift is resolved because the hook generates nothing and commits nothing.

The Siloed Worktree State is resolved by anchoring paths to `--git-common-dir`. The POSIX Double-Lock Deadlock is resolved because there is no application-level lock manager; the only lock is a single `flock` on the append write. The Lock Contention Under Swarm Loads is resolved because the lock is held only for the duration of a single append write, not for the duration of an LLM API call. The Thread-based Concurrency False-Pass is resolved because the concurrency model is multi-process with `flock`, which is correctly testable with `fork()`.

The Queue Orphan is resolved because the queue is the Git log, not a directory. The Queue-Stealing Race Condition is resolved because there is one processor per pointer, not competing consumers on a shared directory. The Bulk-Claiming Queue Defect is resolved because the cursor advances one commit at a time. The Fragile PID-based Leases are resolved because there are no leases; the processor is either running or not.

The Archive Idempotency Loophole is resolved by UUID deduplication against the full archive. The Derived Index Drift is resolved by eliminating the maintained index. The Database Impersonator Anti-Pattern is resolved by using genuine append-only JSONL. The Distributed State Divergence is resolved by eliminating the binary database entirely.

---

## Closing Note

The solution proposed here is not clever. It is deliberately boring. It uses Git as a content-addressable append log (which is exactly what Git is), JSONL as an append-only event store (which is exactly what JSONL is good at), a background process for async work (which is exactly what background processes are for), and no custom locking, indexing, or queue infrastructure beyond what these primitives already provide. The temptation in a system with sophisticated constraints is to build sophisticated infrastructure. In this case, the sophistication is the problem. The constraints are satisfied more completely by doing less, not more.


ChatGPT:
## Executive Summary

The project has done an excellent job identifying *local implementation failures*, but the reviews so far reveal a deeper architectural issue:

> The architecture is still attempting to make Git behave like a transactional event-processing system.

Most of the "critical" defects are not actually queue defects, lock defects, SQLite defects, or Git Notes defects.

They are symptoms of a higher-level mismatch:

* Git is a distributed content-addressed version control system.
* ASES is attempting to build a distributed event ledger with exactly-once semantics and auditable provenance guarantees.

Those are related problems, but they are not the same problem.

As a result, every architecture explored so far eventually runs into the same wall.

---

# Adversarial Review

## Failure Mode 1: Contradictory Requirements

The brief simultaneously demands:

1. Exactly-once processing
2. Crash-safe transactions
3. Distributed consensus
4. No centralized service
5. No binary state
6. Full Git replication
7. O(1) active context

Taken literally, this is impossible.

Exactly-once processing is not a property of storage.

It is a property of:

* identity
* ordering
* ownership
* transaction coordination

The moment multiple machines can independently generate provenance events, you have a distributed systems problem.

The architecture currently attempts to solve that with:

* files
* hooks
* notes
* SQLite
* queues

None of those provide distributed consensus.

They only provide local durability.

---

## Failure Mode 2: Audit Trail and Runtime State Are Being Mixed

The architecture currently treats three different classes of data as one thing:

### Runtime State

Examples:

* pending jobs
* processing jobs
* leases
* retries

These are ephemeral.

---

### Audit Events

Examples:

* model selected
* evaluation performed
* rationale generated

These are immutable.

---

### Derived Knowledge

Examples:

* capability matrices
* summaries
* indexes
* decision catalogs

These are projections.

---

The current architecture repeatedly merges these concerns.

That is why:

* queues become archives
* archives become indexes
* indexes become sources of truth

This is causing most of the identified drift problems.

---

## Failure Mode 3: Git Hooks Are Being Overloaded

The reviews correctly identified dozens of hook failures.

The deeper problem:

Git hooks are being asked to do too much.

A commit hook should never be responsible for:

* LLM execution
* queue processing
* matrix compilation
* archive maintenance
* distributed synchronization

The more responsibilities assigned to hooks, the more pathological edge cases emerge.

Hooks should perform only:

1. capture
2. validation
3. enqueue

Nothing more.

---

## Failure Mode 4: SQLite Is Being Rejected for the Wrong Reason

The review correctly identifies:

> SQLite breaks Git mergeability.

True.

But the conclusion:

> Therefore SQLite must be avoided.

is not necessarily true.

The mistake is assuming:

> Runtime state and audit state must use the same storage mechanism.

They do not.

---

SQLite is excellent for:

* local queues
* leases
* retries
* worker coordination

SQLite is terrible for:

* distributed audit history

These should not be the same database.

---

## Failure Mode 5: The Search for Exactly-Once Is Misplaced

The brief asks:

> How do we achieve exactly-once processing?

The adversarial answer:

You probably don't.

You achieve:

### At-Least-Once Execution

plus

### Idempotent Event Recording

This is how nearly every serious event system works.

Examples:

* Kafka
* EventStore
* SQS consumers
* CDC pipelines

The current design spends enormous effort trying to prevent duplicates.

A better design makes duplicates harmless.

---

# Proposed Solution

The architecture should be split into three independent layers.

---

# Layer 1: Local Runtime Engine

Not tracked by Git.

Not replicated.

Not audited.

Use SQLite.

Location:

```text
.git/crosslink/runtime.db
```

Contains:

```sql
queue
leases
workers
heartbeats
retries
metrics
```

Only operational data.

Nothing historically important.

---

Benefits:

* WAL transactions
* crash recovery
* atomic dequeue
* lease ownership
* no file locks

This eliminates almost every queue-related defect identified.

---

# Layer 2: Immutable Event Ledger

Git-tracked.

Human-auditable.

Machine-generated.

The actual source of truth.

Structure:

```text
crosslink/events/
```

Example:

```text
2026/
  06/
    24/
      event-uuid.json
```

Event:

```json
{
  "event_id": "uuid",
  "timestamp": "...",
  "type": "model_selection",
  "commit": "sha",
  "actor": "agent",
  "payload": {...}
}
```

Key properties:

* append only
* immutable
* never edited
* never rewritten

This becomes the authoritative history.

---

No:

```text
decisions.json
index.json
archive.jsonl
```

No rolling files.

No rotation.

No active/history split.

Each event is independent.

---

This immediately eliminates:

* archive idempotency loophole
* derived index drift
* replay duplication

---

# Layer 3: Materialized Views

Generated.

Disposable.

Never authoritative.

Examples:

```text
capability-matrix.md
decision-summary.md
index.json
```

Generated from the ledger.

Can be rebuilt at any time.

---

Rule:

> Delete and regenerate must always be valid.

If regeneration changes meaningfully, architecture has failed.

---

# Event Flow

Instead of:

```text
Hook
 ↓
Queue
 ↓
LLM
 ↓
Archive
 ↓
Index
 ↓
Matrix
```

Use:

```text
Hook
 ↓
Capture Event
 ↓
Append Event File
 ↓
Exit
```

Done.

Milliseconds.

No latency.

---

Then:

```text
Background Worker
 ↓
Read Event Ledger
 ↓
Run Analysis
 ↓
Emit New Events
```

Not mutate existing events.

Emit new events.

---

Event sourcing.

Not state mutation.

---

# Commit SHA Problem

Solved naturally.

Use:

```text
post-commit
```

not

```text
pre-commit
```

The commit already exists.

SHA available.

No race.

---

# Git Notes Problem

Remove Git Notes entirely.

Git already replicates files.

Use Git.

Not Git Notes.

---

# Distributed Consensus Problem

The critical insight:

You do not need distributed consensus.

You need distributed replication.

Those are different.

A provenance record is not a bank account.

It is historical evidence.

Git already provides:

* replication
* merge
* history
* signatures
* conflict visibility

Use Git's strengths.

Do not build Raft on top of Git.

---

# Recommended End-State Architecture

```text
ASES
│
├── crosslink/
│   ├── events/
│   │   └── immutable ledger
│   │
│   ├── projections/
│   │   ├── capability-matrix.md
│   │   ├── summaries/
│   │   └── reports/
│   │
│   └── schemas/
│
└── .git/
    └── crosslink/
        └── runtime.db
```

Where:

### Git Tracks

* events
* projections
* schemas

### SQLite Tracks

* queues
* leases
* workers
* retries

### Hooks Perform

* capture only

### Workers Perform

* processing only

### Projections Perform

* reporting only

---

## Final Assessment

The biggest architectural mistake so far is treating *operational state* and *historical provenance* as the same problem.

Once those concerns are separated:

* SQLite becomes acceptable again (for runtime coordination only).
* Git becomes acceptable again (for immutable provenance only).
* Hooks become trivial.
* Exactly-once processing becomes unnecessary.
* Most of the identified critical defects disappear because the system is no longer attempting to force Git into the role of a transactional queue manager.

The architecture should evolve toward an **event-sourced provenance ledger with ephemeral local runtime coordination**, rather than continuing to search for a single storage mechanism that simultaneously satisfies queue semantics, transactional durability, auditability, replication, mergeability, and low-latency execution.

Deepseek:
## Adversarial Review: The Architecture of Self-Inflicted Wounds

Let’s drop the political pretense. This brief is a textbook case of **architecture astronautism**—you’ve spent five rounds of "adversarial audits" meticulously documenting failure modes that are *consequences of your own over-engineered premise*, not intrinsic constraints of the problem.

Here is the uncomfortable truth: **You are trying to build a distributed transaction processor to solve a problem that requires a static append-only logger.**

Your core failure is **coupling telemetry capture with telemetry synthesis**. By forcing LLM-generated rationales (slow, network-bound, high-latency) into the critical path of Git operations (`pre-commit`/`pre-push`), you necessitate a queue, which necessitates locks, which necessitates crash recovery, which necessitates transactionality—and you end up with a Rube Goldberg machine of POSIX locks, orphaned `processing/` directories, and PID leases.

**The queue is the anti-pattern.** You don't need a queue; you need a **log**. A queue implies *work* to be *done* before a commit finalizes. That work (LLM synthesis) is *read-only* with respect to the raw telemetry and *idempotent* with respect to the commit SHA. Why are you blocking the commit to wait for a side-effect that changes absolutely nothing about the code being committed?

Furthermore, your analysis of Git distribution is schizophrenic. You correctly reject SQLite for breaking merge consensus, yet you propose a file-system state machine with `decisions.json`, `index.json`, and rotating archives—which **also** breaks distributed consensus. Try merging two branches that both appended to `decisions.json` at the same line. You get a merge conflict. Try merging archives. You get a mess. JSON and JSONL are *not* merge-friendly unless treated as append-only with union merges, but you've built `index` arrays and rotating archives, which are mutable aggregates.

Finally, the obsession with the commit SHA *during* the commit is a false constraint. You don't know the SHA until the commit object is materialized. So *don't use the SHA* as the primary key for telemetry during the write. Use a local UUID, and *backfill* the SHA in a `post-commit` hook. This is trivial.

---

## The Proposed Solution: The "Ghost Log" Architecture

We abandon the queue, the processing directory, the PID leases, the nested locks, and the mutable indexes. We embrace **append-only plaintext** and **asynchronous materialization**.

### Layer 1: The Raw Audit Log (The Source of Truth)
- **Location**: `.crosslink/audit.jsonl` (Line-delimited JSON).
- **Content**: Each line is a raw, unsynthesized event.
  ```json
  { "id": "uuid-v4", "timestamp": "ISO8601", "type": "commit|harness|review", "data": { "files": [...], "exit_code": 0 } }
  ```
- **Write Protocol**: Append is atomic via `write(tempfile) → fsync → rename`. We hold a `fcntl.flock` for ~1ms *exclusively* for the append, then release immediately. No network calls, no LLM, no synthesis. Zero latency.

### Layer 2: The Asynchronous Synthesizer (The Background Daemon)
- **Trigger**: Run via `systemd` timer, `cron`, or a detached `post-commit` fork (no wait).
- **Logic**:
  1. Scan `audit.jsonl` for entries lacking a `synthesis_sha` or `processed` flag.
  2. For each new UUID, make the LLM call to generate the rationale.
  3. Write the synthesis result to a **separate** immutable file: `.crosslink/synthesis/{uuid}.md`.
  4. When complete, append a *new* line to `audit.jsonl` marking `{ "id": "uuid", "status": "synthesized", "sha": "final-commit-sha" }`.
- **Crash Safety**: If the daemon crashes mid-synthesis, it simply resumes on restart by scanning for UUIDs without a corresponding `synthesis/{uuid}.md` file. No orphaned state, no queue-stealing.

### Layer 3: The Git Hook Integration (The Minimal Path)
- **`pre-commit`**: **NO-OP.** (Zero latency. No telemetry. We fix the "staging area leakage" by touching nothing).
- **`post-commit`**:
  1. Read the newly created commit SHA (`git rev-parse HEAD`).
  2. Append a raw event to `audit.jsonl` containing the SHA and the diffstat (`git diff --stat HEAD~1`).
  3. Fire-and-forget the synthesizer daemon (non-blocking).
- **`pre-push`**: **NO-OP.** (We eliminate the "unpushed notes ref" and "premature notes push" errors by writing *nothing* here).
- **`post-merge` / `post-checkout`**: Trigger a *re-indexing* of the capability matrix (see Layer 4), but do not alter the audit log.

### Layer 4: The Derived Index / Capability Matrix (The O(1) Payload)
- **Location**: `.crosslink/matrix.md` (checked into Git).
- **Build**: Deterministically compiled from `audit.jsonl` and `synthesis/*.md` using a `make matrix` command or the `post-merge` hook.
- **Merge Strategy**: Since `matrix.md` is fully derived, **we do not edit it manually**. If a merge conflict arises in `matrix.md`, we resolve it by **re-running the build command** (`make matrix`) rather than editing the conflict. In `.gitattributes`, we set `matrix.md merge=ours` (or simply rebuild on conflict).
- **Context Footprint**: The active agent **only reads** `matrix.md` and the latest 3-5 synthesis summaries. This is strictly O(1) and under your 500-token budget.

---

## Addressing the 4 Mandated Challenges Head-On

| Challenge | How the Ghost Log Solves It |
| :--- | :--- |
| **1. Exactly-once & atomic crash-safety** | Atomic `rename()` provides filesystem-level transactionality for the log. Idempotency is guaranteed by the UUID: the daemon checks for existing `synthesis/{uuid}.md` before calling the LLM. If the daemon crashes, it re-scans; if the hook crashes mid-append, the write never lands (rename is atomic). No complex WAL or PID leases required. |
| **2. NO network LLM latency in hooks** | Hooks only perform local disk I/O (append JSON). The LLM call is ejected to a background process that runs *after* the commit finishes. The `pre-commit` and `pre-push` hooks have **zero** network calls. |
| **3. NO corruption of Git SHA/branch lifecycles** | We never write to `pre-commit` (no SHA timing mismatch). We never write to `pre-push` (no orphaned notes on rejection). The SHA is captured safely in `post-commit` after the object exists. No notes refs are used, avoiding the push-rejection orphan problem entirely. |
| **4. Distributed replication & merge consensus** | `audit.jsonl` is append-only plain text. By adding a custom merge driver (`.gitattributes: audit.jsonl merge=union`), Git automatically concatenates lines from both branches on merge. Since lines are independent UUIDs and timestamps, order doesn't matter. No binary blobs, no JSON array brackets to fight over. The derived `matrix.md` is rebuilt deterministically post-merge, eliminating manual merge headaches. |

---

## The Hard Truth About Your Previous Paradigms

- **Paradigm A (File queues)** failed because you treated the filesystem as a message broker. We eliminate the broker.
- **Paradigm B (SQLite)** failed because you introduced a binary state that Git can't merge. We eliminate the binary state.
- **Your "structural failure modes"** (lock contention, queue stealing, orphaned processing) are all **non-issues** in an append-only log because there is no mutable state to lock, no processing directory to steal from, and no partial writes to orphan.

**Stop engineering for a distributed queue. Start engineering for a distributed log.** Let the synthesis be a *view* over that log, built asynchronously, and let Git handle the eventual consistency of the raw facts. Your agents will have zero latency, your audits will be mathematically verifiable (hash the JSONL lines), and your reviewers will stop laughing at your POSIX double-lock deadlocks.