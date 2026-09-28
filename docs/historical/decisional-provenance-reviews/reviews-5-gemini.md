# Adversarial Architectural Review: Decisional Provenance

**Reviewer:** Gemini 3.1 Pro (Adversarial Agent)
**Target:** `.design/dual-architecture-orchestration-spec.md`

## Executive Summary: The Pointer Paradox

Both proposed architectures—and the subsequent revisions suggested by previous models—are trapped in a **Pointer Paradox**. They attempt to build a secondary, exogenous indexing scheme (SQLite DBs, JSONL logs with `commit_sha` fields, or Commit Message Footers) to map "Decision Events" to "Git Commits."

In a distributed version control system where history is locally mutable (via `rebase`, `squash`, `cherry-pick`, and `amend`), storing explicit Git SHAs inside file contents or local databases is mathematically doomed. The moment history is rewritten, the SHAs change, leaving your secondary index filled with dangling pointers and orphaned provenance.

Neither Option 1 nor Option 2 can survive standard Git lifecycle edge cases. Below is a ruthless deconstruction of their hidden failure modes, followed by the only mathematically sound resolution.

---

## 1. Option 1 (CQRS/SQLite) Destruct-Testing

### A. The Rebase / Ghost SHA Desynchronization
Option 1's daemon reads an event and binds `{uuid}` to `{commit_sha}` in the local `runtime.db`. 
**Failure Mode:** A developer runs `git rebase -i` to clean up commits before a PR. The Git SHAs change completely. The SQLite database now maps all events to "Ghost SHAs" that no longer exist in the repository. The daemon will not re-process them because the `id` already exists in the queue. Provenance is permanently severed from the codebase.

### B. The Cherry-Pick Poison Pill
**Failure Mode:** A developer cherry-picks a commit containing an event file to a hotfix branch. The `post-commit` hook fires. The daemon attempts to insert the event into SQLite. Because it is the exact same event file, the UUID is identical. SQLite throws a `UNIQUE constraint failed` error on the Primary Key. The daemon crashes. The hotfix commit receives absolutely zero provenance.

### C. SQLite WAL Starvation (The "Zero Latency" Illusion)
The spec boasts `<1ms` hook exit times by spawning detached `nohup python3` daemons. 
**Failure Mode:** If an agent loop makes 50 micro-commits in rapid succession, 50 concurrent Python processes spawn and fight for SQLite WAL locks. SQLite allows concurrent readers but only **one concurrent writer**. 49 of those daemons will hit `SQLITE_BUSY` exceptions, block, and eventually timeout. Provenance events will be silently dropped under high concurrency. 

---

## 2. Option 2 (Git-Log LSM) Destruct-Testing

### A. The "Dirty Tree" Data Wipe
Option 2 runs local compaction `post-commit`, moving fragments from an ignored `queue/` to a tracked `log/`, but it **does not commit them** until the `pre-push` gate.
**Failure Mode:** The developer's working directory is intentionally kept dirty with tracked modifications to `log/decisions.jsonl` between commits and pushes. If the developer runs `git checkout another-branch` or `git reset --hard` before pushing, Git will obliterate the uncommitted log modifications. The agent's provenance data is permanently destroyed.

### B. The Intermediate Commit Loss
**Failure Mode:** An agent makes three commits (A, B, C) and then pushes. The `pre-push` hook stages the log and amends **only the tip commit (C)**. Commits A and B are pushed to the remote without their respective log updates. Any system analyzing Commit A or B in isolation will find their provenance completely missing. 

### C. The Ouroboros Amend Paradox
The schema for `log/decisions.jsonl` requires the `commit_sha` to be written inside the file. 
**Failure Mode:** The daemon writes the current SHA into the log. Then, the `pre-push` hook runs `git commit --amend` to save the log. **Amending the commit changes its SHA.** Thus, the `commit_sha` written *inside* the log file is instantly invalidated by the very action that commits it. It is a logical ouroboros; the log will forever record the pre-amend SHA, rendering the audit trail mathematically invalid.

---

## 3. The True Resolution: Immanent Structural Provenance

The fundamental error in all previous designs is treating "The Decision" and "The Commit" as two separate entities requiring an artificial bridge. They are not. 

Git's Merkle Tree is already a flawless, atomic, distributed database. You do not need exogenous pointers (`commit_sha` fields, SQLite mappings, or footers).

### The Architecture:
1. **Topological Linkage, No Pointers:** When the agent acts, it writes `.crosslink/events/{uuid}.json` (with NO `commit_sha` inside it) and edits the source code. Both are staged. Both are committed **atomically in the same standard Git commit**. 
2. **Rebase/Squash Survival:** Because the linkage is structural (the event file exists *in the tree* of the commit), if you rebase, squash, or cherry-pick, Git automatically moves the event file with the code changes. The linkage is indestructible.
3. **Read-Time Compaction (The O(N) Myth):** The requirement for a `<500 token` active context only applies to the Agent's prompt, not the repository history. The fear of "O(N) cold starts" is a myth. Reading and sorting 10,000 tiny JSON files from disk takes `<50ms` in modern Python/Rust. The Agent Loop should dynamically compile the last 5 events into memory at runtime.
4. **CI-Driven Projections:** `decisions.jsonl` and `capability-matrix.md` **must never be committed by local hooks**. Local projection commits cause catastrophic merge conflicts and branch pollution. Let the remote CI/CD pipeline compile and publish these artifacts.

### Conclusion
Abandon both Option 1's daemons and Option 2's pre-push amends. Write immutable event files synchronously in the same commit as the code, rely on Git's native tree atomicity for linkage, and compile projections strictly at read-time or in CI. This satisfies all four constraints with zero hooks, zero daemons, and zero paradoxes.