# Future Research Topic: File-per-Node CRDT Graph for Provenance

## Context
During the resolution of the "State/Consensus Paradox" in the ASES Decisional Provenance Architecture, an adversarial review process involving Claude, Deepseek, GLM, ChatGPT, and Gemini concluded that attempting to maintain provenance using a single appended log file or database resulted in insurmountable merge conflicts and data loss during Git branching and history mutation.

## The Finding
The models unanimously converged on a "File-per-Node CRDT (Conflict-free Replicated Data Type) Graph" approach.

### Key Concepts
*   **File-per-Node:** Every entity (Source, Observation, Finding, Decision) is saved as its own immutable JSON file, keyed by a UUID (e.g., `.memory/nodes/<uuid>.json`).
*   **Git as the Transport:** By using separate files for each node, Git's native tree merge mechanism handles distributed consensus perfectly. Two branches creating new nodes concurrently will merge without conflicts.
*   **Append-Only Graph:** Edits or updates to nodes are handled by creating a *new* node that references the old one with a `supersedes` edge, rather than mutating the original file.
*   **Read-Time Projection:** A local, `.gitignored` SQLite database is built on-the-fly by parsing the nodes. This index acts purely as a disposable read-cache for fast querying and is never synced across repositories.

## Future Research Directives
1.  **Schema Definition:** Develop a rigorous JSON schema for the different node types (Decision, Observation, Finding, Validation) and their edges (`supports`, `contradicts`, `supersedes`, `derives_from`).
2.  **CLI Tooling:** Design the `./ases record` CLI tooling to enforce this schema and automatically generate the UUID files, abstracting the raw JSON files away from the developer.
3.  **Threat Modeling:** Before implementation, define a formal threat model specifying who the provenance is for, what threats it protects against, and the data lifecycle (how to handle "provenance rot" when referenced code is deleted).
4.  **Performance Envelope:** Benchmark the speed of the local SQLite index reconstruction over large datasets (e.g., 100,000+ node files) to determine if periodic CI-generated snapshotting is required.
