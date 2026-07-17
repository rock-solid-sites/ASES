# RQ4 — SQLite+edge tables

## Question

Can a graph database naturally represent artefacts, versions, evidence, provenance, and supersession without excessive schema complexity? This report investigates **SQLite used with explicit edge/relationship tables** — the "just use SQLite" approach, where SQLite is treated as a lightweight relational database and graph-like structures are modelled with adjacency-list tables plus recursive CTEs for traversal.

## Scope

**Investigated:**
- SQLite's data model (single-file relational store, tables, foreign keys, JSON columns) and how artefacts, versions, evidence, provenance, and supersession map onto tables and edge tables.
- Recursive CTEs as the mechanism for multi-hop graph traversal in SQLite, and their documented performance characteristics and limits.
- SQLite's JSON support (JSON1 / JSONB) as a way to reduce schema rigidity for flexible properties.
- SQLite's full-text search (FTS5) as a mechanism for text search across artefacts.
- The embedded, zero-config, single-file nature of SQLite and its implications for portability, git-friendliness, and a web/edge application backend.
- Client library and composition options: Node.js (`node:sqlite`, `better-sqlite3`, `node-sqlite3`), browser/WASM (`sql.js`, official `sqlite3` WASM + OPFS, `wa-sqlite`).
- Licensing (public domain).
- The single-writer limitation and the replication/edge workarounds (Litestream, LiteFS).

**Excluded:**
- Hands-on benchmarking or code execution (this is a literature/evidence investigation; no SQLite instance was run). Performance figures are taken from third-party benchmarks and the SQLite documentation.
- Detailed comparison against other RQ4 candidates beyond what is needed to contextualise findings (separate reports cover Neo4j, Kuzu, and Memgraph).
- Security hardening, access-control models, and distributed/cluster deployment (out of scope for an embedded single-node library, except where replication tools bear on the single-writer limit).
- Any recommendation or implementation proposal (forbidden by task rules).

## Evidence

### E1. Data model: single-file relational store with tables, FKs, and JSON columns
- SQLite is an embedded, serverless, zero-configuration relational database stored in a single cross-platform file (sqlite.org; Wikipedia "SQLite"). It is ACID-compliant and uses a B-tree page structure; tables carry an implicit `rowid` unless declared `WITHOUT ROWID` (Wikipedia "SQLite"; sqlite.org/docs).
- Foreign key constraints are supported but **disabled by default** and must be enabled with `PRAGMA foreign_keys = ON` (Wikipedia "SQLite"; sqlite.org/docs). This is a recurring source of "orphaned node/edge" integrity problems when modelling graphs in SQLite (runebook.dev, "Graph Traversal in SQLite").
- SQLite is **dynamically/loosely typed** ("manifest typing"): a column's declared type is advisory; values are stored in one of five storage classes (NULL, INTEGER, REAL, TEXT, BLOB). This flexibility aids semi-structured storage but weakens the type-safety a rigorous provenance model might want (sqlite.org/quirks; Fedora Magazine, "JSON and JSONB support in SQLite 3.45.0").
- JSON is stored as ordinary `TEXT`; there is no dedicated `JSON` column type. The convention is a `TEXT` column plus a `CHECK(json_valid(...))` constraint (jsonic.io guide; w3resource).

### E2. JSON1 / JSONB functions built in
- The JSON1 extension (15 scalar functions, 2 aggregate, 2 table-valued functions such as `json_each`, `json_tree`) became **built in by default from SQLite 3.38.0 (2022-02-22)**, previously opt-in (sqlite.org/json1; sqlite.org matrix/json1).
- **JSONB** (a binary serialization of SQLite's internal JSON representation, avoiding re-parsing on each access) was added in **SQLite 3.45.0 (2024)** (Wikipedia "SQLite"; Fedora Magazine). JSON5 syntax support arrived in 3.42.0 (sqlite.org/json1).
- JSON functions operate at >1 GB/s parse speed; SQLite deliberately does not add a binary JSON *type*, keeping JSON as text for backwards compatibility (sqlite.org/json1).
- **Interpretation (labelled):** JSON columns let flexible artefact/evidence properties live in one column without a wide, fixed schema — a real lever for reducing schema complexity, at the cost of weaker validation and no native indexing on nested fields (indexing requires expression indexes on `json_extract(...)`).

### E3. Graph modelling via edge tables and recursive CTEs
- SQLite has **no native graph type, no `CONNECT BY`, and no graph query language** (runebook.dev; mako.ai guides). The standard approach to graph structures is an **adjacency-list / edge table**: a `nodes` (or domain) table plus an `edges(source_id, target_id, relation, ...)` table, with indexes on `source_id`/`target_id` (dev.to/rohansx "SQLite as a Graph Database"; runebook.dev).
- Multi-hop traversal is performed with **`WITH RECURSIVE` common table expressions** (CTEs): an anchor `SELECT` plus a recursive `SELECT` that self-joins the CTE against the edge table (runebook.dev; devsolus.com; mako.ai). Depth is bounded with a `level` column and a `WHERE level <= N` guard; cycle detection requires an accumulated path column (mako.ai "Common mistakes").
- A 2026 blog (dev.to/rohansx) documents a production-style "SQLite as a graph DB" schema: `entities`, `edges` (with `valid_from`/`valid_until` bi-temporal columns, `confidence`, `episode_id`), plus FTS5 virtual tables and recursive-CTE traversal — explicitly chosen to replace a Neo4j + Docker + separate vector/FTS services stack with "one binary and one file" (dev.to/rohansx; github.com/rohansx/sqlite-graph, an embeddable graph lib built on SQLite).
- **Interpretation (labelled):** The edge-table + recursive-CTE pattern can express all five RQ4 concepts (artefacts, versions, evidence, provenance, supersession), but every traversal is hand-written SQL rather than a declarative graph pattern, and correctness (termination, cycle guards, FK enforcement) is the developer's responsibility.

### E4. Recursive CTE traversal performance and limits
- A 2026 benchmark suite (congraphdb-benchmark, "SQLite") ranks SQLite **4th of the engines tested (overall 65.8/100)**, with traversal **5th** at **~8.5 ms average for a 4-hop query**, ingestion 5th (~45K nodes/s), PageRank 4th (~5.5 s / 10 iterations), memory 3rd (~85 MB). Its stated weaknesses: "No Native Graph — Recursive CTEs are slow", "Traversal Limits — 4-hop max before timeouts", "Complex Queries — Graph queries are verbose", "Performance — 180% slower than CongraphDB" (congraphdb-benchmark/engines/sqlite).
- A separate 2026 benchmark gist (kkollsga, "SQLite vs KGLite graph traversal benchmark") compares SQLite recursive CTEs against a graph DB on a ~30K-node / ~220K-edge knowledge graph across hop depths 1–8, variable-depth, shortest path, reachability, and triangle queries. The gist's stated premise is to test the claim that "B-tree joins outperform index-free adjacency" for graph traversal; both engines are embedded/in-process (github.com/kkollsga/16aff9d2dd84a7b75fa87de801447559). **Observation:** the gist exists and is structured to measure exactly this; the specific numeric results were not extracted into this report and are treated as unverified here.
- mako.ai's guide notes recursive CTEs are **always materialized**, and warns of missing termination (infinite recursion until an internal limit or OOM), cycle-guard-on-wrong-column bugs, and `LIKE '%2%'` substring false positives in path tracking (mako.ai).
- **Interpretation (labelled):** The consistent signal across sources is that recursive-CTE traversal is adequate for modest graphs (tens of thousands of nodes, shallow hops) but degrades and becomes verbose at deeper hops; the "4-hop max before timeouts" figure is one benchmark's threshold, not a hard SQLite limit, and depends on graph shape, indexing, and machine.

### E5. FTS5 full-text search
- SQLite ships **FTS5** (successor to FTS3/FTS4), a virtual-table full-text search extension: inverted index, customizable tokenizers (`unicode61`, `ascii`, `porter`, `trigram`), boolean (`AND`/`OR`/`NOT`), phrase, prefix, NEAR/proximity queries, `BM25()` ranking, `snippet()`, `highlight()`, and column filters (sqlite.org/fts5; blog.sqlite.ai; manujpaliwal.substack "SQLite FTS5").
- FTS5 supports "external content" tables (index text but read originals from a real table via triggers, ~half the disk) and "contentless delete" mode for append-heavy workloads (manujpaliwal.substack).
- FTS5 is a **virtual table** backed by shadow tables (`%_data`, `%_idx`, `%_content`, `%_docsize`); schema-dump tooling (e.g. Rails) can mishandle these shadow tables (sqlite.org/fts5; rubyonrails-discuss).
- **Interpretation (labelled):** FTS5 can index artefact/evidence text in the same single file as the graph, enabling relevance-ranked search without a separate search service — directly relevant to "text search across artefacts" for EDASES.

### E6. Embedded, zero-config, single-file, portable
- SQLite runs **in-process** with no server, no configuration, and no separate administration (sqlite.org; Wikipedia). The database is a single file that is trivially copyable, movable, emailable, and can be placed under version control — described as "git-friendly" (dev.to/rohansx; brightcoding.dev on Kuzu makes the same point for single-file DBs).
- In WAL mode on NVMe, a single SQLite server can exceed **100,000 read queries/second**, with per-query latency of **10–20 µs** (50–100× faster than intra-region Postgres) when the DB is co-located with the app (daily.dev "SQLite for Production", citing Fly.io/Ben Johnson). Expensify is cited as processing billions of transactions on SQLite in production (daily.dev).
- **Interpretation (labelled):** For EDASES, a single-file, git-friendly, portable artefact store is a strong fit for local-first / research-reproducibility workflows; the same file can be committed, shared, and opened by any SQLite tool.

### E7. Browser and Node.js composition
- **Browser / WASM:** `sql.js` (github.com/sql-js/sql.js) runs SQLite in the browser via WASM but is **in-memory / transient** by default (DB disappears on reload unless exported to a file/blob) (sql-js/sql.js; sqlite.org/wasm demo). The **official `sqlite3` WASM/JS** subproject (sqlite.org/wasm) adds persistence via the **Origin Private File System (OPFS)** and Worker-based APIs; it is the SQLite project's sanctioned WASM deliverable (developer.chrome.com; sqlite.org/wasm). `wa-sqlite` (github.com/rhashimoto/wa-sqlite) is an alternative WASM wrapper with different VFSes (sqlite.org/forum). OPFS-backed concurrency across tabs/workers is supported but with caveats (sqlite.org/forum, Stephan Beal, 2026-04-17).
- **Node.js:** `node:sqlite` (the built-in `DatabaseSync` module) shipped experimentally in **Node v22.5.0** and reached **release-candidate stability in v25.7.0** (nodejs.org/api/sqlite). Mature native bindings `better-sqlite3` (synchronous, fast) and `node-sqlite3` exist; `node-sqlite3-wasm` ports SQLite to WASM for Node/Electron with persistent file access (github.com/tndrle/node-sqlite3-wasm; sqlite.org/copyright confirms SQLite is public domain). `better-sqlite3` is synchronous/blocking; pool wrappers move queries to worker threads for non-blocking parallel reads (github.com/dilipvamsi/better-sqlite3-pool).
- **Interpretation (labelled):** SQLite can run in the browser (WASM+OPFS), in Node.js (built-in or native bindings), and embedded in the host app — so a single artefact file can be read across client, server, and CLI without a network boundary.

### E8. Single-writer limitation and replication/edge workarounds
- SQLite permits **only one writer process at a time**; concurrent writes serialize (this is inherent to the file-based design). Platforms that enable Litestream backups explicitly cap the writer to **a single instance** (slasha.com/docs; litestream.io).
- **Litestream** (github.com/benbjohnson/litestream, MIT-ish/Apache-style, actively maintained) is a standalone DR tool that streams SQLite's WAL to S3-compatible storage for continuous replication and point-in-time restore; it runs as a separate sidecar process with **no code changes** (litestream.io; datasette.cloud blog). It is single-node (primary writer + optional read replicas in beta) (community.fly.io).
- **LiteFS** (Fly.io) is a FUSE-based filesystem that replicates WAL segments from a single primary writer to multiple read replicas across regions for low-latency global reads; it still enforces a **single writer** (daily.dev; community.fly.io).
- A 2026 Litestream issue (#1083) reports a **silent replication-failure bug in v0.5.6+** (WAL-space reuse not detected) causing stale backups; workaround is pinning v0.5.5 (github.com/benbjohnson/litestream/issues/1083). **Observation:** this is an open, dated bug report; its production impact depends on version and workload.
- **Interpretation (labelled):** The single-writer constraint is a real ceiling for concurrent multi-user writes, but read-heavy EDASES-style workloads (98/2 read-write is cited as common) are well within SQLite's comfort zone; network/multi-writer access requires an added layer (Litestream/LiteFS or a hosting process), which reintroduces operational complexity the "just use SQLite" approach sought to avoid.

### E9. Licensing — public domain
- SQLite is **dedicated to the public domain** by its authors; the code and documentation are released for any use, commercial or non-commercial, with no attribution requirement (sqlite.org/copyright.html; github.com/sqlite/sqlite/LICENSE.md; VAPOR docs). Contributors sign affidavits dedicating work to the public domain; the core is kept "clean" of third-party licensed code (sqlite.org/copyright.html; simonwillison.net, 2025-12-29).
- For jurisdictions that do not recognise public-domain dedication, Hwaci sells a **Warranty of Title** (sqlite.org/copyright.html). This is distinct from the Hippocratic License (EthicalSource), which is *not* SQLite's license and is mentioned only to avoid confusion (spdx.org/licenses/Hippocratic-2.1).
- **Observation:** Public-domain status removes licensing friction for EDASES adoption and redistribution, including proprietary or modified derivatives.

## Findings

**F1 — Artefacts as rows.** Engineering artefacts map directly to a table, e.g. `artefacts(id PK, kind, content, meta JSON)`. Each artefact is a row; relationships to other concepts live in edge tables. (Observation from E1, E3; modelling is a direct application of the relational primitive.)

**F2 — Versions via a version table + edge table.** Versions are a `artefact_versions(id PK, artefact_id FK, version_no, content, meta JSON)` table; a **version chain** is an edge table `version_edges(from_version, to_version, relation='PRECEDES')`; **branching** is expressed by a version row having multiple outgoing `PRECEDES` edges. (Observation from E3; modelling inference.)

**F3 — Evidence linked via edge tables.** Evidence is a `evidence(id PK, ...)` table connected to artefacts and/or versions through a typed edge table (`evidence_links(evidence_id, target_type, target_id, relation='SUPPORTS'|'CONTRADICTS')`). Linking evidence to a *specific version* (not just the artefact) is straightforward because versions are first-class rows. (Observation from E3; modelling inference.)

**F4 — Provenance via recursive CTE over edge tables.** Provenance (`DERIVED_FROM`, `GENERATED_BY`, `PRODUCED_BY`) is an edge table; "where did this come from?" is answered by a `WITH RECURSIVE` CTE walking those edges multi-hop (E3, E4). The fit is achievable but the traversal is hand-written SQL, not a declarative graph pattern, and needs explicit depth bounds and cycle guards.

**F5 — Supersession via a typed edge table.** Supersession is an edge table `supersedes(from_version, to_version, reason, superseded_at)`; "what is the current valid version?" reduces to traversing the `SUPERSEDES` chain (or maintaining an `is_current` flag). (Observation from E3; modelling inference.)

**F6 — Schema complexity is moderate, not zero.** Representing the five concepts needs roughly: 2–4 domain tables (artefact, version, evidence, provenance-source) + 1–3 edge tables + indexes, plus recursive CTEs for any multi-hop query. This is **more verbose than a native property-graph schema** (where the same is a handful of node/rel tables and a `MATCH` pattern) but **less machinery than a fully normalised relational schema with many join tables** for ad-hoc relationships. The dominant complexity is in the *traversal queries* (recursive CTEs), not the *storage schema* (Interpretation from E3, E4; consistent with the "edge tables" thesis).

**F7 — JSON columns reduce property-schema rigidity.** Flexible artefact/evidence metadata can live in a `meta JSON`/`TEXT` column with `CHECK(json_valid(...))`, avoiding a wide fixed column set; JSONB (3.45+) avoids re-parsing. Trade-off: weaker validation and no native nested indexing without expression indexes (Observation from E2; interpretation).

**F8 — FTS5 enables in-file text search.** Artefact/evidence text can be indexed by FTS5 in the same database file, with BM25 ranking and snippet/highlight — no separate search service required (Observation from E5).

**F9 — Portability and composition are strengths.** Single-file, git-friendly, zero-config, public-domain, and runnable in browser (WASM+OPFS), Node.js (built-in `node:sqlite` or native bindings), and embedded — a single artefact file is portable across client/server/CLI (Observation from E1, E6, E7, E9).

**F10 — Single-writer is the decisive constraint for concurrent web use.** Read-heavy workloads are well served; concurrent multi-writer access requires Litestream/LiteFS or a hosting process, reintroducing operational complexity, and LiteFS/Litestream still enforce a single writer (Observation from E8; interpretation).

## Rejected options

- **Relying on SQLite's native graph features.** Rejected because SQLite has no native graph type, no graph query language, and no `CONNECT BY`; traversal must be built from edge tables + recursive CTEs (E3, E4). This is a finding about the technology, not a recommendation.
- **Treating recursive CTEs as a drop-in for a graph engine at scale.** Rejected for deep/high-volume traversals: benchmarks show traversal is the weakest dimension (5th; ~8.5 ms 4-hop; "4-hop max before timeouts" in one suite) and queries are verbose (E4). Suitable for modest graphs only.
- **Using Litestream/LiteFS to obtain multi-writer SQLite.** Rejected as a true multi-writer solution: both preserve a single primary writer and add a sidecar/replication layer; they address DR and read-scaling, not concurrent write scaling (E8).
- **Assuming `sql.js` gives persistent browser storage.** Rejected: `sql.js` is in-memory/transient by default; persistence requires the official `sqlite3` WASM + OPFS or `wa-sqlite` (E7).

## Unknowns

- **U1.** The exact numeric results of the SQLite-vs-KGLite traversal benchmark (kkollsga gist) at each hop depth were not extracted; the relative ranking of SQLite recursive CTEs vs a graph DB on that dataset remains unverified here (E4).
- **U2.** The real-world degradation curve of recursive-CTE traversal as a function of node count, edge density, and hop depth is not pinned down by a single source; the "4-hop timeout" is one benchmark's threshold, not a universal constant (E4).
- **U3.** Behaviour and performance ceilings of the official `sqlite3` WASM + OPFS build for larger graphs in-browser (memory, cross-tab concurrency) are documented only at a high level; quantitative limits were not established in the sources reviewed (E7).
- **U4.** Production impact of the Litestream v0.5.6+ silent-replication bug (#1083) for an EDASES deployment depends on version pinning and write pattern; it is an open, dated report, not a resolved fact (E8).
- **U5.** Whether EDASES's write concurrency profile is read-heavy enough to stay within SQLite's single-writer comfort zone is a workload question not answerable from SQLite's documentation alone (E8, E10).

## Confidence

**Medium-High** on the core modelling claim: artefacts, versions, evidence, provenance, and supersession *can* each be represented with SQLite + edge tables, and the storage schema stays moderate (not "excessive") for modest graphs. This follows directly from SQLite's documented relational + JSON + recursive-CTE primitives (E1–E3, F1–F6) and is consistent with how adjacency-list modelling works generally.

**Medium** on the "without excessive schema complexity" half of the question and on web-backend fitness. The *storage* schema is moderate, but the *traversal* complexity (recursive CTEs, cycle guards, depth bounds) and the documented traversal-performance ceiling (E4) mean the "naturalness" is weaker than a native graph DB. The single-writer limit (E8) is a confirmed, well-documented constraint that materially affects concurrent multi-user use but not read-heavy or local-first use.

Justification summary: modelling fitness and portability are well-evidenced; the decisive uncertainties are (a) traversal performance/verbosity at scale versus a true graph engine, and (b) whether EDASES's write-concurrency needs exceed the single-writer model — both are documented as real but not quantified for this specific workload.

## References

1. SQLite official site / documentation: https://sqlite.org/
2. SQLite Copyright (public domain): https://sqlite.org/copyright.html
3. SQLite GitHub mirror — LICENSE.md (public domain): https://github.com/sqlite/sqlite/blob/master/LICENSE.md
4. SQLite JSON Functions and Operators (JSON1 / JSONB): https://sqlite.org/json1.html
5. SQLite FTS5 Extension documentation: https://sqlite.org/fts5.html
6. SQLite WASM/JS subproject (official, OPFS persistence): https://sqlite.org/wasm/doc/trunk/about.md
7. Chrome for Developers — "SQLite Wasm in the browser backed by the Origin Private File System": https://developer.chrome.com/blog/sqlite-wasm-in-the-browser-backed-by-the-origin-private-file-system
8. Node.js `node:sqlite` documentation: https://nodejs.org/api/sqlite.html
9. sql.js (SQLite in browser via WASM, in-memory): https://github.com/sql-js/sql.js
10. wa-sqlite (alternative WASM wrapper): https://github.com/rhashimoto/wa-sqlite
11. better-sqlite3 (Node.js native binding): https://github.com/WiseLibs/better-sqlite3
12. node-sqlite3-wasm (WASM port for Node/Electron): https://github.com/tndrle/node-sqlite3-wasm
13. Litestream (streaming SQLite replication / DR): https://litestream.io/ and https://github.com/benbjohnson/litestream
14. Litestream issue #1083 (silent replication failure v0.5.6+): https://github.com/benbjohnson/litestream/issues/1083
15. LiteFS (Fly.io, FUSE WAL replication, single writer): https://github.com/superfly/litefs
16. CongraphDB Benchmark — SQLite engine page (traversal/ingestion/PageRank/memory scores): https://congraph-ai.github.io/congraphdb-benchmark/engines/sqlite
17. kkollsga — "SQLite vs KGLite graph traversal benchmark" gist: https://gist.github.com/kkollsga/16aff9d2dd84a7b75fa87de801447559
18. dev.to/rohansx — "SQLite as a Graph Database: Recursive CTEs, Semantic Search, and why we ditched Neo4j" (2026-03-24): https://dev.to/rohansx/sqlite-as-a-graph-database-recursive-ctes-semantic-search-and-why-we-ditched-neo4j-1ai
19. github.com/rohansx/sqlite-graph (embeddable graph lib on SQLite, bi-temporal edges, FTS5): https://github.com/rohansx/sqlite-graph
20. runebook.dev — "Graph Traversal in SQLite: A Guide to Recursive CTEs": https://runebook.dev/en/docs/sqlite/lang_with/rcex3
21. mako.ai — "Advanced Recursive CTEs in SQLite: Graphs, Cycle Detection": https://mako.ai/guides/sqlite/common-table-expressions-advanced
22. blog.sqlite.ai — "SQLite Extensions: Full-text search with FTS5": https://blog.sqlite.ai/fts5-sqlite-text-search-extension
23. manujpaliwal.substack — "SQLite FTS5: The Full-Text Search Engine Already in Your App" (2026-04-17): https://manujpaliwal.substack.com/p/sqlite-fts5-the-full-text-search
24. daily.dev — "SQLite for Production: When and How to Use It Beyond Prototyping" (2026-05-25, Litestream/LiteFS, latency figures): https://daily.dev/blog/sqlite-production-guide-when-how-to-use-beyond-prototyping
25. Wikipedia — "SQLite" (data model, FK default-off, FTS5, JSON/JSONB, public domain): https://en.wikipedia.org/wiki/SQLite
26. Fedora Magazine — "JSON and JSONB support in SQLite 3.45.0": https://fedoramagazine.org/json-and-jsonb-support-in-sqlite-3-45-0
27. Simon Willison — "Copyright Release for Contributions To SQLite" (2025-12-29, public-domain contribution process): https://simonwillison.net/2025/Dec/29/copyright-release/
