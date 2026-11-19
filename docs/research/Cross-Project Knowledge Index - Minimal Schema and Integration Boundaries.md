---
title: Cross-Project Knowledge Index - Minimal Schema and Integration Boundaries
program: EDASES
layer: Research
document_type: Research Framework
status: Experimental
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/standards/Documentation Standard.md
related_documents:
  - docs/research/LLM Agents and Distributed Systems - Research Topic.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
last_updated: 2026-11-19
---

# Cross-project knowledge index: minimal schema

## Purpose and non-goals
A reusable, regenerable **derived** index linking research, concepts, evidence, decisions, designs, and tests across independently owned projects. The first pilot is LLM-agent/distributed-systems research. This is distinct from the conversation archive's preservation, classification, completeness, and historical search obligations. It must not alter archives or replace Projektor's issue graph.

This is an **initial design proposal**, not an implemented or approved production schema. Test against actual source shapes before adopting it.

## Existing systems and constraints (inspection 2026-11-19)
- EDASES documentation already uses YAML frontmatter with layer, status, authority, dependencies and related documents. Reuse those fields; do not require other projects to adopt EDASES's standard.
- The ASES workflow topology research record documents information asymmetry, source attribution, certainty and untested assumptions. The index must not turn experimental interpretations into canonical methodology.
- PJDEV-9 targets a read-only graph of **existing** Projektor issue/wiki relationships, explicitly excluding general semantic graph persistence. Do not expand its scope or rely on its deployment.
- CHATARCH-3 documents a separate historical SQLite FTS5 corpus (228 graphs, 10,804 messages, 122,168 graph nodes), 28 prior concept IDs/78 typed relationships and unreviewed lexical candidates. These are historical reports, **not** a current inventory or verified semantic graph. Reuse identifiers or adapters where feasible, but do not treat unreviewed candidates as facts.
- Projektor remains human-facing planning; Work Notes remains operational agent tracking. The knowledge index is neither.

## Identity and provenance
All nodes have a stable, namespaced `id`, `kind`, `title`, `source_uri`, `source_system`, `visibility`, `updated_at`, and optional `source_revision` (Git commit SHA, immutable archive ID, etc.). No public export may contain private source text, sensitive URLs or private graph topology.

Node kinds (initial): `source`, `concept`, `claim`, `design`, `decision`, `experiment`, `evidence`. The kind identifies the thing, not its truth. The source record points to a canonical location and version; indexing does not confer authority.

Edges have `id`, `from`, `to`, `relation`, `evidence_refs`, `assessment`, `review_status`, and optional `explanation`. Relation candidates: `discusses`, `supports`, `challenges`, `tests`, `implements`, `depends_on`, `related_to`, `supersedes`. Direction and semantics must be defined and tested. `supports` means *the cited evidence is relevant to the specific claim*, not that the entire design is proven. `assessment` distinguishes observed, inferred, hypothesized, and disputed; `review_status` distinguishes candidate and reviewed.

Stable identifiers are source-native when available (DOI, repository + document ID, Projektor issue ref plus workspace identity, archive conversation UUID); local concept IDs use a namespaced registry. Never identify nodes solely by title or path. Maintain aliases on rename/move; avoid generating new IDs on each import.

## Example record shapes (illustrative only)

```json
{"id":"doi:10.1073/pnas.2612825123","kind":"source","title":"Language model teams as distributed systems","source_system":"doi","source_uri":"https://doi.org/10.1073/pnas.2612825123","visibility":"public","updated_at":"2026-11-19"}
{"id":"edases:concept:central-task-assignment","kind":"concept","title":"Central task assignment","source_system":"edases","source_uri":"https://github.com/rock-solid-sites/ASES","visibility":"public","updated_at":"2026-11-19"}
{"id":"edases:edge:paper-discusses-assignment","from":"doi:10.1073/pnas.2612825123","to":"edases:concept:central-task-assignment","relation":"discusses","evidence_refs":["doi:10.1073/pnas.2612825123"],"assessment":"observed","review_status":"candidate"}
```

A real ingestion pipeline must validate source access, identifiers, edge direction, visibility and source versions. The example is not a verified citation-to-claim mapping.

## Storage and retrieval
- Canonical research notes and reviewed graph assertions: Git-tracked Markdown and JSONL (or existing compatible structured source).
- Rebuildable projections: SQLite FTS5 for lexical search and relational node/edge traversal. Do not introduce a graph database until measurements justify it.
- Graph viewer: initially read-only, filtered and source-linked; reuse the Projektor UI only if it can consume the projection without changing Projektor ownership or security.
- Semantic/vector search: optional derived projection; do not substitute similarity for reviewed edges.

## Integration contracts
1. **Repository importer**: read Markdown frontmatter and selected structured records; respect repo-specific conventions; emit normalized records with provenance. No source writes.
2. **Projektor adapter**: read issue/wiki references and existing explicit links; preserve workspace/project IDs; do not invent semantic edges from mere co-occurrence. No automatic issue creation.
3. **Conversation archive adapter (later)**: consume *published, verified* IDs and access-controlled references. Archive ingestion and reconciliation remain independently scheduled. No archive writes and no dependency on completion of the 275-conversation reconciliation.
4. **Work Notes adapter (later)**: read approved technical findings only; no workflow-state mutations.
5. **Cross-project joins**: candidate edges are not promoted without evidence review. The lowest source visibility/permission applies to any derived view revealing its contents or existence.

## First discriminating tests
- Ingest the PNAS paper record and an existing ASES research document, retrieve both by ID, and show a candidate relationship with a source link and unverified status.
- Rebuild twice: identical canonical input produces equivalent nodes and edges, with no duplicates.
- Change a document title/path: identity and links remain stable through alias/revision handling.
- Introduce missing targets, duplicate IDs, circular dependencies, and conflicting source assertions: validation reports them without silent repair.
- Feed private archive references into a public viewer: neither text nor node existence leaks.
- Verify the index can operate while CHATARCH-3 is incomplete and PJDEV-9 is not deployed.

## Next decision gate
Inventory actual source layouts and existing graph utilities; prototype a single read-only importer and validator; measure index size, correctness and graph-query usefulness. Do not build a second archive search engine or a general graph editor.
