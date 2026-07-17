# RQ4 — PostgreSQL+pgvector

## Question

Can a graph database naturally represent artefacts, versions, evidence, provenance, and supersession without excessive schema complexity?

This report investigates **PostgreSQL with the pgvector extension** — a mature relational (SQL) database used in a *graph-like* manner (adjacency-list tables, self-referential foreign keys, recursive Common Table Expressions) plus vector similarity search via the `pgvector` extension — as a candidate backend for the EDASES execution-engine / artefact store. The focus is on whether the five EDASES concerns (artefacts, versions, evidence, provenance, supersession) can be modelled in a relational schema that behaves like a graph, and whether doing so keeps the schema clean or requires excessive join tables, recursive CTEs, or complex SQL. The added dimension is what `pgvector` brings: semantic/vector similarity search across artefacts and evidence.

## Scope

**Investigated:**
- PostgreSQL's relational model and its graph-like capabilities: adjacency lists, self-referential foreign keys, and recursive CTEs (`WITH RECURSIVE`, available since PostgreSQL 8.4).
- How artefacts map to relational tables.
- How versions are modelled: version tables with self-referential predecessor FKs, version chains, and branching.
- How evidence links to artefacts/versions (join tables for many-to-many).
- How provenance chains are represented and traversed via recursive CTEs, and how that compares to native graph index-free adjacency.
- How supersession is modelled (typed relationship rows + recursive CTE traversal).
- Schema complexity: whether the above require excessive join tables / recursive CTEs / complex SQL.
- The `pgvector` extension: vector storage, indexing (HNSW, IVFFlat), distance operators, and what semantic search adds.
- Performance of graph-like queries (recursive CTEs, multi-hop joins) at scale vs native graph databases.
- Maturity, adoption, and licensing of PostgreSQL and pgvector.
- Client-library support for JavaScript/TypeScript (pg, postgres.js, Prisma, Drizzle, etc.).

**Excluded:**
- Hands-on deployment, benchmarking, or running PostgreSQL/pgvector (this is a literature/evidence review; no instance was executed).
- Quantitative throughput/latency profiling for the specific EDASES workload shape (no authoritative benchmark located for that shape; vendor and third-party benchmarks are noted as such).
- Deep comparison against other candidates beyond what is needed to contextualise findings (sibling RQ4 reports cover Neo4j, Memgraph, Kuzu).
- Any recommendation or implementation proposal (per research constraints; PostgreSQL+pgvector is named only as evidence).

## Evidence

### 1. PostgreSQL is relational, not a native graph store — graph behaviour is simulated

- **Observation:** PostgreSQL is a relational database management system with ACID compliance, point-in-time recovery, JOINs, and rich SQL features (postgresql.org/about; pgvector README). It is not a graph database; relationships are expressed through foreign keys and join tables, and graph traversal is simulated with recursive CTEs.
- **Observation:** Recursive CTEs (`WITH RECURSIVE`) have been a standard SQL feature in PostgreSQL since version 8.4, enabling iterative edge-walking: "start at a node, find its neighbors, find their neighbors, repeat until you run out." (medium.com/@tihomir.manushev, "Graph Queries with Recursive CTEs — You Don't Need Neo4j", 2026-05-11)
- **Observation:** A documented recursive-CTE graph-traversal pattern walks an `friendships` edge table to a fixed hop depth, with an explicit warning: "Recursive CTEs can loop infinitely on cyclic graphs. Always add a depth/hop limit (`WHERE depth < 100`) or use `UNION` (deduplicates) instead of `UNION ALL`." (jusdb.com, "PostgreSQL CTEs and Recursive Queries for Hierarchical Data", updated 2026-06-20)
- **Interpretation:** PostgreSQL *can* behave like a graph, but only by convention: edges live in adjacency-list tables and traversals are computed per-query by recursive CTEs. This is fundamentally different from a native graph store where edges are first-class, index-free pointers. The relational model requires the engineer to *construct* the graph semantics (join tables, recursive SQL) rather than declaring them.

### 2. Artefacts as relational tables

- **Observation:** An artefact (document, code module, decision) maps to a base table, e.g. `artefacts(id PK, kind, title, content_ref, status, created_at)`. Attributes are columns; there is no graph "node" abstraction.
- **Interpretation:** This is a natural fit for *structured* artefact metadata and benefits from PostgreSQL's strong typing, constraints, and indexing. It is not "graph-native," but for artefacts that are primarily records with attributes, a table is arguably simpler than a graph node. The graph-like quality only becomes relevant when artefacts are *connected* to each other, to versions, evidence, and provenance — at which point foreign keys and join tables enter.

### 3. Versions

- **Observation:** Versions are modelled as a separate table `artefact_versions(id PK, artefact_id FK, version_no, content_ref, created_at)` with a self-referential foreign key `predecessor_id` pointing to the previous version row, forming a linked list / chain. (This is the direct relational analogue of the entity–state pattern; see also the recursive-CTE category-tree example in jusdb.com which uses `parent_id` self-references.)
- **Observation:** Branching is expressible because a version row may have multiple *successor* rows referencing it (one-to-many from a parent version), or a `version_edges(from_id, to_id, branch_label)` table can hold an explicit DAG.
- **Interpretation:** Version chains and branches are representable, but each requires either self-referential FKs (linear chains) or an explicit edge table (branches/DAGs). Maintaining "latest version" pointers, chain integrity, and branch metadata is application-level bookkeeping — there is no built-in versioning primitive. This is more machinery than a graph DB's typed `HAS_VERSION`/`NEXT` relationships, but it is standard, well-understood relational design, not exotic.

### 4. Evidence

- **Observation:** Evidence (observations, test results, reviews) is a table `evidence(id PK, kind, payload, author, created_at)`. Because an evidence item can relate to *many* artefacts/versions and vice versa, the link is a **join table**: `evidence_links(evidence_id FK, artefact_id FK NULL, version_id FK NULL, relation_type, confidence, created_at)`.
- **Interpretation:** Linking evidence to a *specific version* is a row in `evidence_links` pointing at `version_id`. This requires a join table (many-to-many), whereas a native graph DB uses a typed edge with no join table. The relational approach is more verbose but fully expressive and benefits from declarative FK constraints and indexes.

### 5. Provenance

- **Observation:** Provenance is an adjacency list, e.g. `provenance_links(source_id, target_id, relation_type, author, created_at, PK(source_id, target_id, relation_type))`, where ids may reference artefacts, versions, or agents. Multi-hop traversal uses a recursive CTE: `WITH RECURSIVE path AS (SELECT ... FROM provenance_links WHERE source_id = $1 UNION ALL SELECT ... JOIN path ON path.target_id = provenance_links.source_id) SELECT * FROM path;`
- **Observation (performance contrast):** A third-party comparison states: "Neo4j completes a 6-hop graph traversal on 10 million nodes in 12 ms, while PostgreSQL takes 1.2 seconds — a 100× advantage. This difference widens with depth because PostgreSQL's recursive CTE must inspect rows at each step, whereas Neo4j follows pointers." (markaicode.com, "Neo4j vs PostgreSQL: Graph Queries 100x Faster on Complex …", citing neo4j). The same source notes PostgreSQL "handles shallow graphs (≤4 hops) with acceptable latency" with careful indexing and tuning.
- **Interpretation:** Provenance chains are fully representable and traversable in PostgreSQL, but every hop is a join over an index at query time, not a pointer follow. For the EDASES provenance shape (likely shallow, versioned chains), this is acceptable; for deep or high-frequency traversals it is structurally disadvantaged vs native graph stores. The recursive CTE also requires explicit cycle protection (depth limit or `UNION` dedup).

### 6. Supersession

- **Observation:** "Artefact A supersedes B" is a typed row in the provenance/relationship edge table, e.g. `relationship_links(source_id, target_id, type='SUPERSEDES', reason, created_at)`, or a dedicated `supersession(superseded_id, superseding_id, reason, created_at)` table. A chain is traversed by the same recursive-CTE pattern as provenance.
- **Interpretation:** Supersession is representable as a directed, typed edge row and is traversable via recursive CTE. No intermediate node is required unless metadata on the supersession event itself is needed (then a row in an event table suffices). This is clean *relationally* but, like provenance, depends on recursive SQL for chain discovery rather than a single declarative pattern match.

### 7. Schema complexity — overall assessment

- **Observation:** The five concerns translate to roughly: 1 base `artefacts` table, 1 `artefact_versions` table (+ self-FK or edge table for branches), 1 `evidence` table, 1–2 join/edge tables (`evidence_links`, `provenance_links`/`relationship_links`), plus recursive CTEs for any multi-hop query (provenance ancestry, supersession chains, version history walk).
- **Interpretation:** The schema is *not* excessive in the sense of being unmanageable, but it is **structurally more verbose than a native property graph**: many-to-many links need join tables, chains need self-referential FKs or edge tables, and traversals need recursive CTEs written per query. The "graph" is emergent from conventions, not intrinsic. Whether this counts as "excessive schema complexity" is a judgement: for teams fluent in SQL and relational modelling it is ordinary; for a graph-centric domain it is more boilerplate and more query-level machinery than Neo4j/Kuzu, where edges are first-class. The recurring cost is recursive-CTE authoring and cycle safety, repeated for each traversal need.

### 8. pgvector — what vector similarity search adds

- **Observation:** `pgvector` is an open-source PostgreSQL extension (created by Andrew Kane, first released 2021; ~22,000 GitHub stars as of the sources reviewed) that adds a `vector` column type and similarity operators. It supports exact and approximate nearest-neighbor search, single/half/binary/sparse vectors, and L2, inner product, cosine, L1, Hamming, and Jaccard distances via operators `<->`, `<#>`, `<=>`, `<+>`. (github.com/pgvector/pgvector README; grokipedia.com/page/Pgvector)
- **Observation:** Two primary index types: **HNSW** (high recall/speed, in-memory index, no rebuild on insert) and **IVFFlat** (compact, needs rebuild). A 2025 optimisation write-up reports HNSW ~15× faster queries than IVFFlat. (zylos.ai/research/pgvector-optimization-2025)
- **Observation:** pgvector 0.8.0 (Oct 2024) introduced **iterative scans** fixing the "overfiltering" problem (up to 9× faster filtered queries, 100× better relevance for filtered queries); latest referenced versions are 0.8.2 (Feb 2026) and 0.8.5. (grokipedia.com; github.com/pgvector/pgvector)
- **Observation:** A companion extension, **pgvectorscale** (Timescale, PostgreSQL License, written in Rust), adds a DiskANN-based index ~9× smaller than HNSW and further improves large-scale performance; a benchmark cited by Timescale claims pgvector+pgvectorscale is "as fast as Pinecone at 75% less cost." (tigerdata.com/blog; zylos.ai)
- **Interpretation:** pgvector enables **semantic search** across artefacts and evidence — e.g. embedding artefact text/decisions and querying "find artefacts semantically similar to X," or "find evidence relevant to this claim." This is a capability a pure graph DB does not provide natively and is a genuine differentiator for EDASES: it lets the artefact store answer *similarity* questions (retrieval, deduplication, related-evidence discovery) inside the same database that holds the structured graph. It is, however, orthogonal to the graph-modelling question — it augments, not replaces, the relational graph representation.

### 9. Performance of graph-like queries at scale

- **Observation:** Recursive-CTE multi-hop traversal on PostgreSQL is reported ~100× slower than native Neo4j at 6 hops / 10M nodes (12 ms vs 1.2 s), with the gap widening with depth because each hop inspects rows via indexes rather than following pointers. (markaicode.com, citing neo4j)
- **Observation:** A counter-view argues recursive CTEs "solve 95% of graph problems" and "scale to tens of millions of edges with sub-second response times for typical depths" when the edge table is properly indexed. (medium.com/@tihomir.manushev, 2026-05-11)
- **Observation (vector scale):** pgvector handles "50–100M vectors well"; beyond that, partitioning or a dedicated vector DB is advised. At 50M vectors, one source reports pgvector at 28× lower latency and 16× higher throughput than Pinecone at 75% cost. (zylos.ai; tigerdata.com)
- **Interpretation:** For EDASES's likely artefact-graph scale (thousands to low millions of nodes, shallow traversals), PostgreSQL's recursive-CTE performance is adequate and the operational simplicity (one database for both structured graph and vectors) is a strong point. The native-graph performance advantage is real but matters mainly at deep traversal depth and very large scale. **Caveat:** the 100× figure is a vendor-adjacent comparison and the EDASES workload shape is unbenchmarked.

### 10. Maturity, adoption, licensing

- **Observation:** PostgreSQL is decades-old, battle-tested, and widely adopted; it offers strong role-based access control, row-level security, encryption, and auditing. (enterprisedb.com/blog/mariadb-vs-postgresql; postgresql.org/about)
- **Observation:** pgvector is rapidly maturing and broadly available: preinstalled on Postgres.app and many hosted providers (AWS RDS, Azure Database for PostgreSQL, Google Cloud SQL, Supabase). (github.com/pgvector/pgvector; supabase.com/docs)
- **Observation (licensing):** PostgreSQL is released under the **PostgreSQL License**, a permissive BSD/MIT-style license with no fee and a commitment to remain free/open-source in perpetuity. (postgresql.org/about/licence)
- **Observation (licensing):** pgvector is licensed under the **PostgreSQL License** (described equivalently as BSD 2-Clause / "similar to MIT" in secondary sources such as gitee.com and zilliz.com). pgvectorscale is also PostgreSQL License. All are permissive and free for commercial and proprietary use.
- **Interpretation:** Both components are permissively licensed and free, with no copyleft obligations — a lower legal-risk profile than Neo4j Community's GPLv3. Maturity of PostgreSQL is maximal; pgvector is young but fast-moving and widely deployed via managed Postgres.

### 11. Composition — JavaScript/TypeScript client libraries

- **Observation:** The dominant Node.js client is **`pg` (node-postgres)** — ~8.22.0, ~15,000 dependents, supports Node 18–24, Bun, Deno, and Cloudflare Workers, with connection pooling, parameterized queries, and streaming. TypeScript types via `@types/pg`. (npmjs.com/package/pg; node-postgres.com)
- **Observation:** **postgres.js** (`postgres`, by porsager) is a 0-dependency alternative; benchmarks show `pg-native` (libpq bindings) ~1.13× faster than `pg` and ~1.25× faster than `postgres.js`. (dev.to/nigrosimone, 2025-09-07)
- **Observation:** Higher-level tooling with first-class PostgreSQL support includes **Prisma**, **Drizzle ORM**, **Kysely**, **TypeORM**, **Sequelize**, and **Knex** — all listed in community driver discussions for Node.js/TypeScript. (reddit.com/r/node; sql.holt.courses)
- **Interpretation:** Client-library support for JS/TS is excellent and mature — the strongest in this RQ4 candidate set alongside Neo4j's official driver. pgvector's `vector` type is passed as a string literal (e.g. `'[1,2,3]'`) and works through any of these drivers without special client support.

## Findings

1. **Artefacts** map naturally to a relational base table with typed columns and constraints — simple and well-supported, though not "graph-native."
2. **Versions** are modelled via a `artefact_versions` table with self-referential predecessor FKs (chains) or an explicit edge table (branches/DAGs). Representable and standard, but versioning is application-level bookkeeping with no built-in primitive.
3. **Evidence** requires a **join table** (`evidence_links`) to relate evidence to artefacts and/or specific versions (many-to-many). Fully expressive, more verbose than a typed graph edge.
4. **Provenance** is an adjacency-list edge table traversable by **recursive CTEs**. Representable and adequate for shallow chains; structurally slower than native index-free adjacency at depth/scale, and requires explicit cycle protection.
5. **Supersession** is a typed edge row (dedicated or in the relationship table), traversable by the same recursive-CTE pattern. Clean relationally; chain discovery depends on recursive SQL.
6. **Schema complexity** is moderate: the five concerns need ~3–5 tables plus recursive CTEs per traversal. Not unmanageable, but more boilerplate and more query-level machinery than a native property graph where edges are first-class. The "graph" is emergent from conventions.
7. **pgvector adds semantic search** — embedding artefacts/evidence and querying by similarity (retrieval, deduplication, related-evidence discovery) within the same database. This is a genuine differentiator vs pure graph DBs and is orthogonal to (augments) the graph modelling.
8. **Performance** for EDASES-scale shallow traversals is adequate; native-graph stores hold a real but depth/scale-dependent advantage (~100× at 6 hops / 10M nodes per a vendor-adjacent benchmark). pgvector scales to ~50–100M vectors before dedicated solutions are advised.
9. **Maturity/licensing:** PostgreSQL is maximally mature and permissively licensed (PostgreSQL License); pgvector is young-but-rapidly-maturing, broadly available on managed Postgres, and also PostgreSQL License (permissive, free, no copyleft). Lower legal risk than GPLv3 graph options.
10. **JS/TS composition** is excellent: `pg` (node-postgres) is the de-facto client with huge adoption; postgres.js, Prisma, Drizzle, Kysely, TypeORM, Sequelize, Knex all support PostgreSQL; pgvector works through any of them via string-literal vector values.

**Overall:** PostgreSQL+pgvector *can* represent artefacts, versions, evidence, provenance, and supersession, but it does so by *simulating* a graph through tables, foreign keys, join tables, and recursive CTEs rather than declaring graph semantics natively. The schema stays manageable (not pathologically complex) but is more verbose and query-heavy than a native graph DB. The distinctive value-add is pgvector's semantic search over the same store. The core research question — *can it represent these concerns naturally without excessive schema complexity?* — is answered: **yes, but only with relational conventions and recursive SQL; "natural" is qualified, and "without excessive complexity" holds for shallow/moderate scale but not as cleanly as a purpose-built graph database.**

## Rejected options

- **Modelling versions as a `version` integer column on the artefact row only.** Rejected because it overwrites history — it cannot retain multiple coexisting versions or attach evidence/provenance per version. A separate version table (entity–state analogue) is required.
- **Using a single generic edge table for *all* relationships without `relation_type`.** Rejected as a modelling anti-pattern: it forfeits PostgreSQL's ability to index and constrain specific relationship kinds (evidence vs provenance vs supersession), forcing filtering in every query. Typed edge tables / a `relation_type` column with partial indexes is preferred.
- **Relying on recursive CTEs without cycle protection.** Rejected as unsafe: documented guidance warns recursive CTEs loop infinitely on cyclic graphs; a depth/hop limit or `UNION` (dedup) is mandatory.
- **Treating pgvector as a substitute for the graph representation.** Rejected: vector similarity answers *semantic similarity* questions, not *structural* ones (provenance ancestry, supersession chains). The two are complementary, not interchangeable.
- **Choosing pgvector alone (without PostgreSQL) as the "database."** Not applicable — pgvector is an extension, not a standalone store; it presupposes PostgreSQL.

## Unknowns

- **EDASES workload shape and scale** are unknown, so absolute latency/throughput for recursive-CTE traversals and vector search are unbenchmarked; the ~100× native-graph advantage is a vendor-adjacent figure at a specific scale.
- **Traversal depth distribution** in EDASES (how often provenance/supersession chains exceed 4 hops) is unknown and determines how much the recursive-CTE performance gap matters.
- **Whether EDASES needs bitemporal/point-in-time reconstruction** of the whole artefact graph — PostgreSQL supports this via modelling patterns and range types, but it is not built-in and adds schema overhead not quantified here.
- **pgvector behaviour at >100M vectors** for EDASES is outside the comfortable range per the sources; partitioning or a dedicated vector DB would be needed, but EDASES is unlikely to reach that scale.
- **Operational topology** (self-hosted vs managed Postgres; whether pgvector is installed/allowed on the chosen managed tier) is a deployment unknown not resolved by this evidence review.
- **Recursive-CTE planner behaviour** on cyclic or dense artefact graphs (super-node analogues) and its interaction with PostgreSQL's query planner is not independently benchmarked here.

## Confidence

**Medium.**

- **High** for the modelling-capability claims (artefacts→tables, versions→version tables + self-FKs, evidence→join tables, provenance/supersession→edge tables + recursive CTEs): these follow directly from documented PostgreSQL features (recursive CTEs since 8.4, FKs, join tables) and are consistent across multiple independent sources.
- **High** for licensing and maturity facts: PostgreSQL License (postgresql.org), pgvector PostgreSQL License / BSD-2-Clause (github, gitee, zilliz), managed-provider availability (github pgvector README, supabase), and client-library facts (npm `pg`, node-postgres.com) are well established.
- **Medium** for performance: the architectural claim (recursive CTEs inspect rows per hop; native graphs follow pointers) is well documented, but the quantitative "100× at 6 hops / 10M nodes" figure is vendor-adjacent and the EDASES workload is unbenchmarked. pgvector scale guidance (50–100M vectors) is from secondary benchmark write-ups.
- **Medium** for the "excessive complexity" judgement: it is a qualitative assessment that the relational-graph approach is more verbose than native graph DBs — well supported by the structural comparison, but the threshold of "excessive" is inherently context-dependent (team SQL fluency, scale, traversal depth).

The core question is answered with reasonable confidence: PostgreSQL+pgvector *can* represent the five concerns, but as a simulated graph requiring join tables and recursive CTEs, with pgvector as a valuable orthogonal semantic-search layer — not as naturally or as compactly as a native property-graph database.

## References

1. PostgreSQL, "License" (PostgreSQL License, BSD/MIT-style, perpetual free/open-source). https://www.postgresql.org/about/licence/
2. PostgreSQL, "About" (ACID, features, maturity). https://www.postgresql.org/about/
3. pgvector GitHub repository (README, install, operators, versions, license). https://github.com/pgvector/pgvector
4. Grokipedia, "Pgvector" (history, license, versions, features). https://grokipedia.com/page/Pgvector
5. Zilliz, "pgvector vs Pinecone" (license = PostgreSQL License / MIT-like; open source). https://zilliz.com/comparison/pgvector-vs-pinecone
6. Gitee mirror of pgvector LICENSE (BSD 2-Clause). https://gitee.com/tarekyuan/pgvector/blob/master/LICENSE
7. Tihomir Manushev, "Graph Queries with Recursive CTEs — You Don't Need Neo4j", Medium, 2026-05-11. https://medium.com/codex/graph-queries-with-recursive-ctes-you-dont-need-neo4j-3aade6fb7f85
8. JusDB, "PostgreSQL CTEs and Recursive Queries for Hierarchical Data" (recursive CTE graph traversal, cycle warning), updated 2026-06-20. https://www.jusdb.com/blog/postgresql-cte-recursive-queries-hierarchical-data
9. Markaicode, "Neo4j vs PostgreSQL: Graph Queries 100x Faster on Complex …" (6-hop 10M-node: Neo4j 12ms vs Postgres 1.2s). https://markaicode.com/vs/neo4j-vs-postgres
10. Zylos Research, "pgvector Performance & Optimization 2025" (HNSW vs IVFFlat, scale 50–100M, vs Pinecone). https://zylos.ai/research/pgvector-optimization-2025
11. Timescale/TigerData, "pgvector is now as fast as Pinecone at 75% less cost" (pgvectorscale, DiskANN, PostgreSQL License). https://www.tigerdata.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost
12. Supabase, "pgvector: Embeddings and vector similarity" (usage, managed availability). https://supabase.com/docs/guides/database/extensions/pgvector
13. EnterpriseDB, "MariaDB vs PostgreSQL" (PostgreSQL maturity, security, licensing). https://www.enterprisedb.com/blog/mariadb-vs-postgresql
14. node-postgres (`pg`) npm package and documentation (Node/Bun/Deno/Cloudflare support, ~15k dependents). https://www.npmjs.com/package/pg ; https://node-postgres.com/
15. Nigro Simone, "Benchmarking PostgreSQL Drivers in Node.js: node-postgres vs postgres.js", dev.to, 2025-09-07. https://dev.to/nigrosimone/benchmarking-postgresql-drivers-in-nodejs-node-postgres-vs-postgresjs-17kl
16. Reddit r/node, "Which postgreSQL node.js client library to choose today?" (Prisma, Drizzle, Kysely, TypeORM, Sequelize, Knex). https://www.reddit.com/r/node/comments/15thz1o/which_postgresql_nodejs_client_library_to_choose/
17. Northflank, "PostgreSQL vector search guide: Everything you need to know about pgvector" (pgvector vs dedicated vector DBs, when to choose). https://northflank.com/blog/postgresql-vector-search-guide-with-pgvector
18. Severalnines, "Vector Similarity Search with PostgreSQL's pgvector – A Deep Dive". https://severalnines.com/blog/vector-similarity-search-with-postgresqls-pgvector-a-deep-dive/
