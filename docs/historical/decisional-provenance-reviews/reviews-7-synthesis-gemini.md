# Adversarial Architectural Review: Decisional Provenance Synthesis

**Reviewer:** Gemini 3.1 Pro Preview (Clean Room)
**Target:** `.design/architectural-reviews-synthesis.md`
**Focus:** Critique of Divergent Solutions (Paths A, B, C, D)

---

## 1. Critical Analysis of the Divergent Solutions

The fundamental challenge of Decisional Provenance is marrying relational, structured metadata (the "why") with Git's distributed, mutable, plain-text Merkle tree (the "what"). Paths A, B, and C all attempt to force relational database mechanics onto a system designed to resist them. 

### Path A: The Two-Event Mapping Model
*   **Concept:** Pre-commit `DecisionEvent` + Post-commit `CommitBoundEvent` containing the Git SHA.
*   **Hidden Failure Mode:** The **"SHA-as-Foreign-Key" Fallacy**. In Git, a SHA is ephemeral and mutable until it is pushed to a shared remote. If a developer commits locally, a `CommitBoundEvent` is generated pointing to `SHA-1`. If the developer then runs `git commit --amend` or `git rebase`, the commit is rewritten as `SHA-2`. The `CommitBoundEvent` now points to a ghost commit that no longer exists in the active branch history. The linkage is permanently severed. Furthermore, bypassing hooks (e.g., `git commit --no-verify`) leaves dangling `DecisionEvent`s without counterparts.
*   **Verdict:** **Fundamentally Unworkable.** Relational mapping against mutable distributed state is a distributed systems anti-pattern.

### Path B: Synchronous Post-Commit Amend
*   **Concept:** Agent writes event -> commit -> `post-commit` hook compiles log and runs `git commit --amend --no-edit`.
*   **Hidden Failure Mode:** **Hook Recursion and State Corruption.** Running `git commit --amend` inside a `post-commit` hook creates a new commit, which instantly triggers the `post-commit` hook *again*, leading to an infinite loop unless complex, fragile state-locking mechanisms are introduced. Beyond recursion, amending a commit natively destroys any GPG signatures applied by the developer. Crucially, if a user is performing an interactive rebase (`git rebase -i`), a hook-driven amend will violently disrupt the `rebase-merge` sequencer state, corrupting the rebase entirely.
*   **Verdict:** **Fundamentally Unworkable.** It is hostile to Git primitives, breaks standard CLI workflows, and introduces severe recursion risks.

### Path C: The Separate "Provenance Commit"
*   **Concept:** Feature commit is followed by an automated `post-commit` script that generates a separate `chore(telemetry)` commit containing the provenance data.
*   **Hidden Failure Mode:** **Atomicity Violation.** A code change and the rationale behind it are a single logical transaction. Splitting them into two commits breaks atomicity. If a developer attempts to `git revert <feature-sha>`, the code is reverted, but the accompanying provenance commit remains, leaving the system with orphaned, contradictory metadata. Furthermore, during a rebase or cherry-pick, managing an alternating sequence of `[Feature, Provenance, Feature, Provenance]` commits becomes an absolute nightmare for conflict resolution.
*   **Verdict:** **Fundamentally Unworkable.** It violates the transactional boundary of a logical codebase change and pollutes the repository history.

### Path D: Immanent Topological Linkage
*   **Concept:** Stage `.crosslink/events/{uuid}.json` AND the code edits simultaneously in a single, standard Git commit.
*   **Hidden Failure Mode:** **The Read-Path Degradation.** Unlike A, B, and C, this path has no consensus or state failure modes. Its failure mode is entirely physical performance. Over months of development, `.crosslink/events/` will accumulate thousands of tiny JSON files. Because Path D pushes compaction to the "Read-Path", any tool or developer querying the system's provenance must perform an O(N) scan across thousands of files on the filesystem. Without indexing, this creates unacceptable latency. It also forces the read-time compiler to support all historical schema evolutions of the JSON format simultaneously.
*   **Verdict:** **Workable, but incomplete.** The core write-model is perfectly sound, but the read-path requires an architectural intervention to prevent UX degradation.

---

## 2. Systems-Level Conclusion

Paths A, B, and C fail because they treat Git as a dumb block-storage layer while attempting to enforce relational integrity *outside* of it via local hooks. This will invariably shatter the moment Git's graph operations (`rebase`, `cherry-pick`, `amend`, `squash`) alter the Merkle tree beneath them.

**Path D is the only mathematically sound approach.** It succeeds because it embraces the fundamental axiom of Git: **The Tree is the Transaction.**

If a decision dictates a code change, the immutable record of that decision (`events/{uuid}.json`) and the code change itself must be staged and committed together as a single atomic snapshot. 

This guarantees:
1.  **Topological Linkage:** We do not need a foreign key (SHA) to link a decision to a code change. They are linked topologically because they exist in the exact same Merkle tree slice.
2.  **Graph Immunity:** If commits are rebased, the JSON event file moves with the code. If commits are squashed, multiple unique UUID JSON files are seamlessly merged into the new single commit tree without conflict. If a commit is reverted, the event file is deleted.
3.  **Zero-Hook Resilience:** There are no `amend` loops, no detached daemons, and no side-effects.

### The Hybrid Way Forward: Immanent Linkage + Ephemeral Projection

To solve Path D's O(N) read-path problem without reintroducing the consensus failures of A/B/C, the architecture must adopt strict **CQRS (Command Query Responsibility Segregation)**:

1.  **The Write Path (Command):** Pure Path D. Agents and humans write `.crosslink/events/{uuid}.json` alongside their source modifications. Both are committed atomically. Zero background tasks, zero hooks.
2.  **The Read Path (Query/Projection):** We introduce an **ephemeral, local index** (e.g., a `.gitignored` SQLite db `runtime.db` or an in-memory graph) that is *strictly a read-only projection*. When a user queries provenance, the system checks if the local Git `HEAD` matches the index's last-known `HEAD`. If it differs, the index drops its state and rapidly rebuilds itself from the raw JSON files in the current Git tree. **The index is never the source of truth, and it never writes back to Git.**
3.  **Global Compaction (Optional):** Instead of fragile, hook-driven local compaction, periodic log rollup (merging JSONs into a compressed archive) is executed globally via a dedicated developer command (e.g., `crosslink compact`) or an asynchronous CI/CD pipeline, treating compaction as a standard, manual Git commit.

**Final Verdict:** The conflict between state and consensus is resolved by recognizing that Git *is* the state. Adopt Path D for writes, and build an ephemeral projection for reads.