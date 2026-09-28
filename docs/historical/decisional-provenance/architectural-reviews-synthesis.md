# Synthesis of Adversarial Reviews: Decisional Provenance Architecture

**Status:** Synthesis Complete. Ready for next-stage adversarial review or swarm selection.
**Context:** This document synthesizes 5 rounds of multi-model adversarial reviews (Claude, Deepseek, GLM 5.1, ChatGPT, Gemini) analyzing two proposed architectures for "Decisional Provenance"—a system to record AI-assisted decisions locally and sync them via Git without concurrency deadlocks or binary database silos.

---

## 1. The Original Proposals

To resolve the "State/Consensus Paradox" (the conflict between local transactional locks and Git's plain-text distributed consensus), two architectures were originally proposed:

### Option 1: CQRS & Event-Sourced SQLite-Cache
*   **Write Path:** Agents write immutable, uniquely named JSON event files (`.crosslink/events/{uuid}.json`) with zero locks.
*   **Linkage:** A `prepare-commit-msg` hook injects the UUID into the Git commit footer.
*   **Compaction:** A `post-commit` hook spawns a detached `nohup python3` daemon. The daemon ingests events into a local, `.gitignored` SQLite database (`runtime.db`), safely handling local concurrency queues to query an LLM and eventually commit a compiled Markdown/JSONL matrix.

### Option 2: Git-Log Append-Only JSONL LSM
*   **Write Path:** Agents write fragments to an ignored spool directory (`.crosslink/queue/{uuid}.jsonl`).
*   **Compaction:** A `post-commit` hook uses POSIX atomic `os.replace` to merge queued fragments into a tracked `.crosslink/log/decisions.jsonl`.
*   **Consensus:** Relies on a Git `.gitattributes` `merge=union` driver to blindly concatenate log files during branch merges to avoid conflicts.
*   **Sync:** A `pre-push` hook runs compaction and executes `git commit --amend` to silently attach the log updates to the outgoing commit.

---

## 2. Universal Consensus: The Fatal Flaws

Across all 5 adversarial reviews, there was unanimous agreement on three fatal flaws in the original proposals:

1.  **Option 1's Daemon is Fragile:** Relying on a detached `nohup` background process is an anti-pattern. It risks silent failures, queue stalling, and (under high-concurrency micro-commits) SQLite WAL lock starvation resulting in dropped events.
2.  **Option 2's `pre-push` Amend is Catastrophic:** Executing `git commit --amend` during a push breaks Git distributed consensus. It pushes the old SHA while advancing the local tree to a new SHA, ensuring immediate divergence and forced-push conflicts.
3.  **Union Merge is Not Consensus:** Relying on Git's `merge=union` blindly concatenates files. This destroys chronological ordering, duplicates entries, and risks physical file corruption (e.g., if JSONL fragments lack trailing newlines).

---

## 3. Divergent Solutions

While the reviewers agreed on the flaws, they splintered into four distinct architectural proposals for how to fix the commit-linkage and compaction problems.

### Path A: The Two-Event Mapping Model
*   **Concept:** Make immutable events the absolute sole source of truth and fix linkage ambiguity.
*   **Mechanism:** Stop trying to attach commits to events via hooks. Instead, write a `DecisionEvent` pre-commit. Post-commit, write a second immutable `CommitBoundEvent` that explicitly records the resulting Git SHA.
*   **Pros:** Strict Event-Sourcing purity. Highly auditable.
*   **Cons:** Doubles file I/O. Relies on post-commit execution completing successfully to finalize provenance.

### Path B: Synchronous Post-Commit Amend
*   **Concept:** Fix Option 2's push-divergence by amending immediately.
*   **Mechanism:** Agents write event files. A synchronous `post-commit` hook instantly compiles the logs/indexes and runs `git commit --amend --no-edit` before returning terminal control to the user.
*   **Pros:** Keeps the git tree perfectly clean. 1:1 mapping of code to provenance.
*   **Cons:** Amending a commit changes its SHA. This can break CI tools watching for the original SHA, disrupts IDE git watchers, and creates recursion risks in hooks.

### Path C: The Separate "Provenance Commit"
*   **Concept:** Avoid all history rewriting.
*   **Mechanism:** Agent writes the event UUID manually into their commit message. A `post-commit` script instantly processes the event, compiles the log, and automatically generates a *new*, separate child commit (e.g., `chore(telemetry): update provenance`).
*   **Pros:** Git history is strictly append-only. Zero amend dangers. Fully distributed-safe.
*   **Cons:** Doubles the commit volume in the repository, potentially creating noisy "chore" commit pollution in the main branch history.

### Path D: Immanent Topological Linkage (The "Pointer Paradox" Critique)
*   **Concept:** Any system storing explicit Git SHAs (in SQLite, logs, or secondary events) is doomed by Git's mutable local history (`rebase`, `cherry-pick`, `squash`).
*   **Mechanism:** Abandon the mapping entirely. The agent stages the `.crosslink/events/{uuid}.json` file *and* the codebase edits simultaneously. They are committed in one single, atomic Git commit. Because the event file exists in the exact same Merkle tree as the code change, Git handles the linkage automatically. If the commit is rebased or cherry-picked, the event file moves with it. Compaction to Markdown/JSONL is pushed entirely to the Read-Path (dynamic compilation at runtime) or CI/CD, keeping local hooks empty.
*   **Pros:** Mathematically immune to Git lifecycle edge cases (rebasing/squashing). Zero local daemons, zero hooks, zero amend paradoxes.
*   **Cons:** Requires runtime dynamic parsing of the `events/` folder when a user queries provenance, requiring fast O(N) reads rather than relying on pre-compiled O(1) indices.