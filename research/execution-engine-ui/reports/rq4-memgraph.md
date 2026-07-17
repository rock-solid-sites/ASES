# RQ4 — Memgraph

## Question

Can a graph database naturally represent artefacts, versions, evidence, provenance, and supersession without excessive schema complexity?

This report investigates **Memgraph** (https://memgraph.com) — an in-memory, C++-based graph database that is compatible with Neo4j's Cypher query language (via the openCypher standard) and the Bolt wire protocol — as a candidate backend for the EDASES execution-engine / artefact store. The focus is on whether the five EDASES concerns (artefacts, versions, evidence, provenance, supersession) can be modelled as first-class graph constructs, and whether doing so keeps the schema clean and navigable rather than requiring excessive intermediate nodes, relationship types, or properties.

## Scope

**Investigated:**
- Memgraph's property graph model: nodes, labels, relationships (typed, directed), and properties on both nodes and relationships.
- How artefacts (documents, code, decisions) map to nodes with labels and properties.
- How versions are modelled: the entity–state versioning pattern (carried over from the Neo4j/Cypher modelling idiom, since Memgraph implements the same property graph model and openCypher).
- How evidence (observations, test results, reviews) links to artefacts/versions via relationships.
- How provenance chains (who created what, when, based on what) are represented without join tables.
- How supersession (`A supersedes B`, including chains) is represented and traversed.
- Schema complexity: whether the above require excessive intermediate structure.
- Performance characteristics relevant to EDASES queries (provenance traversal, superseded-artefact discovery, version history), including the in-memory advantage and its RAM-bound limitation.
- Persistence and export: WAL, snapshots, backup/restore, graph serialisation.
- Neo4j compatibility: how real the Cypher/Bolt compatibility is and whether Neo4j query patterns transfer.
- Maintenance and ecosystem: active development, licensing (Community/BSL vs Enterprise/MEL), cost, community size.
- Composition: serving as a backend for a React/TypeScript frontend; client libraries.

**Excluded:**
- Hands-on deployment, benchmarking, or running Memgraph (this is a literature/evidence review; no Memgraph instance was executed).
- Quantitative throughput/latency profiling for the specific EDASES workload shape (no authoritative benchmark located for that shape; vendor benchmarks are noted as such).
- Deep comparison against other graph databases (e.g. Neo4j, Amazon Neptune, ArangoDB) — covered by sibling reports in this research line where present.
- Any recommendation or implementation proposal (per research constraints; Memgraph is named only as evidence).

## Evidence

### 1. Property graph model — artefacts as nodes

- **Observation:** Memgraph uses the property graph model. "Memgraph uses the Cypher query language… This is achieved by using the property graph data model, which stores data in terms of objects, their attributes, and the relationships that connect them." (HandWiki / EverybodyWiki, citing Memgraph docs; consistent with Memgraph's own documentation describing nodes, labels, and properties.)
- **Observation:** Memgraph "supports data ingestion from sources like Kafka, SQL, or plain CSV files. It provides a standard interface to query data with openCypher, a widely-used and declarative query language." (HandWiki)
- **Observation:** Memgraph's Cypher syntax includes node creation with labels and properties: `CREATE (n:Person {name: "Alice", age: 30});` and typed, property-bearing relationships: `CREATE (a)-[:KNOWS {since: 2020}]->(b);` (Memgraph `memgraph-cypher-syntax` skill / docs).
- **Interpretation:** Engineering artefacts (a document, a code module, a decision) map directly to **nodes** carrying a domain label (e.g. `:Artefact`, `:Document`, `:Decision`) and arbitrary properties (id, title, content reference, status). There is no fixed schema to declare upfront — the model is schema-optional. This is a natural fit: an artefact is an entity, and its attributes are properties. No join table is needed to attach attributes. This is structurally identical to the Neo4j property graph model (see sibling RQ4-Neo4j report), so the same modelling reasoning applies.

### 2. Versions

- **Observation:** Memgraph implements openCypher, including variable-length path patterns (`MATCH (a)-[*1..3]->(b)`, `MATCH (a)-[*]->(b)`), `MERGE`, `CREATE`, `SET`, and label/relationship manipulation (`SET n:Employee`, `REMOVE n:Intern`). (Memgraph `memgraph-cypher-syntax` skill / docs)
- **Observation:** Memgraph supports the same relationship-direction and typing primitives as Neo4j, and the property graph model is shared. The official Neo4j entity–state versioning pattern (immutable entity node linked to per-version `State` nodes via typed relationships, with a `LATEST`/chain pointer) is a pure modelling idiom expressed in Cypher, not a Neo4j-specific engine feature. (Interpretation grounded in the shared openCypher property graph model; see RQ4-Neo4j for the primary source of the pattern.)
- **Interpretation:** "Version 3 of document X" is modelled in Memgraph exactly as in Neo4j: a **`State`/version node** attached to an immutable `:Document` entity node by a typed relationship (e.g. `:HAS_VERSION` with a `version` property, or a `NEXT` link in a chain, or `:V3`). Branching versions are expressible by giving the entity multiple outgoing version relationships (a version tree). **Assumption (not Memgraph-specific documentation):** because Memgraph implements the same property graph model and openCypher, the entity–state idiom transfers without modification. The cost is one intermediate `State`/version node per version, plus a `LATEST`/chain pointer to maintain — a recognised, low-cost idiom, not "excessive" schema complexity. This is an interpretation; no Memgraph-specific versioning guide was located in this review.

### 3. Evidence

- **Observation:** Because relationships are first-class, typed, directed, and can carry properties in Memgraph's property graph model, an evidence item (an observation, a test result, a review) is naturally a **node** (e.g. `:Evidence`, `:TestResult`, `:Review`) connected to the artefact or version node by a typed relationship such as `:SUPPORTS`, `:CONTRADICTS`, `:EVIDENCE_FOR`, or `:REVIEWED`. The relationship itself can carry properties (e.g. `confidence`, `date`, `author`). (Interpretation grounded in the shared property graph model and Memgraph's documented `CREATE (a)-[:KNOWS {since: 2020}]->(b)` syntax.)
- **Interpretation:** Linking evidence to a specific *version* of an artefact is simply a relationship to that version's `State` node. No join table is required — the edge is the link. This is the same mechanism Memgraph markets for knowledge graphs and GraphRAG ("surfacing precise structural context… with full audit trails"). (memgraph.com / slashdot summary)

### 4. Provenance

- **Observation:** Memgraph implements openCypher variable-length relationship patterns, e.g. `MATCH (a)-[*BFS]->(b)` and `MATCH (a)-[*]->(b)` for arbitrary-depth traversal, plus standard `MATCH (a)-[:DERIVED_FROM]->(b)` patterns. (Memgraph `memgraph-cypher-syntax` skill)
- **Observation:** Memgraph supports snapshot isolation by default (each query operates on a consistent snapshot at query start), with MVCC and ACID compliance. (Memgraph blog on ACID/isolation levels; simplyblock glossary)
- **Interpretation:** Provenance chains are expressed as chains of typed relationships — `(Agent)-[:CREATED]->(Artefact)`, `(Artefact)-[:DERIVED_FROM]->(OtherArtefact)`, `(Artefact)-[:BASED_ON]->(Evidence)` — traversable in one Cypher clause via variable-length patterns (`MATCH path = (a:Artefact)-[:DERIVED_FROM*]->(root) RETURN path`). **No join tables** are required — the relationship *is* the provenance edge, and traversal follows pointers. This is precisely the class of problem graph databases exist for, and Memgraph's in-memory architecture makes multi-hop traversal especially cheap (see Performance).

### 5. Supersession

- **Observation:** Memgraph supports typed, directed relationships as first-class constructs (documented `CREATE (a)-[:KNOWS]->(b)` syntax; openCypher pattern matching).
- **Interpretation:** "Artefact A supersedes artefact B" is a typed, directed relationship, e.g. `(a:Artefact)-[:SUPERSEDES]->(b:Artefact)`. A chain of supersession is a path `(a)-[:SUPERSEDES]->(b)-[:SUPERSEDES]->(c)`, traversable with a variable-length pattern `MATCH (a)-[:SUPERSEDES*]->(x) RETURN x`. Supersession is a **natural, first-class relationship** — no intermediate node is required unless one wants to attach metadata to the supersession event itself (e.g. `reason`, `date`), in which case a `:Supersession` event node can sit on the edge. Chains are navigable in one Cypher clause. This is the cleanest of the five concerns: it maps directly onto a directed, typed edge. (Interpretation grounded in the shared property graph model; structurally identical to the Neo4j case.)

### 6. Schema complexity — overall assessment

- **Observation:** Memgraph is schema-optional. Constraints (uniqueness, existence) and indexes are added explicitly and are optional. Memgraph "accepts both its native `ON :Label(property)` / `ASSERT` syntax **and** the Neo4j-compatible `FOR (...) ON (...)` / `FOR (...) REQUIRE ...` syntax, so existing Neo4j code that creates indexes or constraints can run unchanged." (Memgraph docs, "Differences in Cypher implementations")
- **Observation (caveat):** In Memgraph, "creating a constraint does not automatically create an index, so you may need to explicitly create indexes to ensure optimal performance." (Memgraph Cypher-differences blog)
- **Interpretation:** For the five EDASES concerns, the schema stays clean: artefacts = labelled nodes; versions = `State`/version nodes hung off an immutable entity (one extra node per version — a recognised, low-cost idiom); evidence = nodes linked by typed edges; provenance = typed relationship chains; supersession = a typed edge (optionally an event node). The only recurring "extra" structure is the version `State` node and its `LATEST`/chain pointer. This is **not excessive** schema complexity. The main discipline required is using meaningful labels and relationship types rather than a generic catch-all — a modelling convention, not a database limitation (same anti-pattern warning as Neo4j). The schema complexity profile is effectively identical to Neo4j's, because both use the same property graph model and Cypher.

### 7. Performance

- **Observation (in-memory advantage):** Memgraph is an in-memory graph database: "All data is held in memory for ultra-low-latency queries, with disk persistence for durability." (simplyblock glossary) "Being in memory, Memgraph is fast and really performant… the entire infrastructure runs start to end in two hours on average" (Capitec Bank, scoring 3.5M+ clients daily — vendor case study). (memgraph.com/knowledge-graph)
- **Observation (latency/throughput, vendor benchmark):** A 2026 comparison table reports Memgraph P50 latency 1–5 ms and throughput 100K+ txns/sec, vs Neo4j 5–50 ms and 10–50K txns/sec; "Memgraph typically achieves 10–100x lower latency for graph traversals due to its memory-first architecture." (solosoft.dev, 2026-05-05 — third-party blog citing comparative figures; treat as indicative.)
- **Observation (architecture):** Memgraph is written in C++ (vs Neo4j's JVM/Java), avoiding JVM GC pauses. It uses MVCC and snapshot isolation, ACID-compliant. (HandWiki; Memgraph blog on isolation levels)
- **Observation (limitation — RAM-bound):** "The in-memory-first approach places constraints on dataset size… Memgraph follows a vertical scaling model: to handle larger graphs, you increase the available RAM. It also supports replication for high availability… but write scaling remains a limitation, since Memgraph has no built-in sharding and cannot partition a graph across multiple nodes." (puppygraph.com blog; simplyblock) "Max dataset: RAM-bound" (solosoft.dev comparison table).
- **Observation (deep traversals):** Memgraph provides built-in C++ traversal algorithms via relationship-expansion syntax, including BFS, DFS, weighted shortest path (WSP), and K-shortest paths with filter/weight lambdas — useful for provenance/supersession path queries. (Memgraph `memgraph-cypher-syntax` skill)
- **Interpretation:** The EDASES query shapes — traversing provenance chains, finding superseded artefacts, walking version history — are exactly local/global traversals that benefit from in-memory storage (no disk seeks / page-cache misses). Performance should be strong for these access patterns, and likely better than disk-based Neo4j for deep multi-hop traversals under load. **Caveats:** (a) the dataset must fit in RAM — for EDASES this is an assumption about artefact-graph size; (b) there is no built-in sharding, so horizontal write scaling is limited; (c) the "10–100x lower latency / 100K+ txns/sec" figures are vendor or third-party blog benchmarks, not independently verified for the EDASES artefact graph. The architectural claim (in-memory = no disk I/O on the read path) is well established and is the relevant structural point.

### 8. Persistence and export

- **Observation (durability mechanisms):** "Memgraph uses two mechanisms to ensure the durability of stored data: write-ahead logging (WAL) and periodic snapshot creation." Snapshots and WAL files are stored under the data directory (default `/var/lib/memgraph`, in `snapshots/` and `wal/` subfolders). "Memgraph **cannot be used with only WAL files enabled**. You can either have only snapshots or snapshots and WAL files." (Memgraph docs, "Data durability")
- **Observation (snapshot behaviour):** Memgraph takes full snapshots of the entire in-memory database to disk (not copy-on-write); WAL records changes since the last snapshot for transaction-level durability. By default it retains the three most recent snapshots (`--storage-snapshot-retention-count=3`). Snapshots can be triggered manually with `CREATE SNAPSHOT;`. (Memgraph blog "Understanding Database Snapshots"; docs)
- **Observation (backup/restore procedure):** Documented steps: `CREATE SNAPSHOT;` → `LOCK DATA DIRECTORY;` → copy snapshot (and optionally WAL) files → `UNLOCK DATA DIRECTORY;`. Restore via `RECOVER SNAPSHOT /path/to/snapshot [FORCE];`. `SHOW SNAPSHOTS;` lists available snapshots. (Memgraph docs, "Backup and restore")
- **Observation (cloud/off-host backup):** "Memgraph currently does not automate backing up data to 3rd party locations, so integrating a backup process into your system is highly recommended" (e.g. using `rclone` to push snapshots/WALs to cloud storage). (Memgraph docs, "Memgraph in mission-critical workloads")
- **Observation (data loss on shutdown):** "The data is not lost when you shutdown your computer" — durability is provided by WAL + snapshots; GQLAlchemy is *not* required for persistence (it is an on-disk storage helper for large node/relationship properties). (Stack Overflow, Memgraph team answer)
- **Interpretation:** The graph is durably persisted to disk via WAL + snapshots and is restorable. Backup is a manual copy-of-files procedure (with a lock to prevent retention deletion), not an integrated managed-backup service in Community Edition. For EDASES, periodic `CREATE SNAPSHOT` + file copy (or volume mount in Docker/K8s) provides a workable backup strategy; off-host backup must be scripted. **Assumption (not verified):** snapshot/restore of a large in-memory graph may be I/O-heavy and pause-averse; the full-snapshot design means backup size scales with total graph size, not just deltas.

### 9. Neo4j compatibility

- **Observation (Cypher):** Memgraph "implements a high-performance subset of Cypher (openCypher)" and "aims to be as close as possible to the most commonly used openCypher implementations." (solosoft.dev; Memgraph docs) It is "compatible with Neo4j's Cypher query language" and the Bolt protocol. (odbms.org, 2026-07-09)
- **Observation (Bolt / drivers):** Memgraph speaks the Bolt wire protocol. The official Memgraph Node.js documentation instructs using the **`neo4j-driver`** npm package to connect (`neo4j.driver("bolt://localhost:7687")`). (Memgraph docs, "Connect to Memgraph / drivers / nodejs"; Stack Overflow Neo4j-driver example)
- **Observation (differences):** There are documented Cypher differences: index/constraint syntax (Memgraph native `CREATE INDEX ON :Person(surname)` vs Neo4j `CREATE INDEX FOR (n:Person) ON (n.surname)` — though Memgraph *also* accepts the Neo4j-style syntax); Memgraph does not auto-create an index when a constraint is created; some Neo4j constructs/expressions/functions are unsupported. A dedicated "Differences in Cypher implementations" page and a "Cypher Differences Between Neo4j and Memgraph" blog exist. (Memgraph docs; Memgraph blog, 2024-08-21)
- **Observation (migration):** Memgraph provides a built-in Neo4j migration module and a "Migrate from Neo4j" guide; "stream data directly with a single Cypher query." (memgraph.com/knowledge-graph)
- **Interpretation:** Cypher compatibility is **real but partial** — it is openCypher, not full Neo4j Cypher, and a documented set of dialect differences exists. For the EDASES modelling patterns (node/relationship creation, `MERGE`, variable-length traversal, typed edges), the overlap is essentially complete, so Neo4j query patterns transfer with at most minor syntax adjustments. The Bolt protocol compatibility means the standard `neo4j-driver` works as the client. "Compatibility is not identity" — engine behaviour (in-memory vs disk, isolation, limits) differs even where the query language matches. (glukhov.org comparison note)

### 10. Maintenance and ecosystem

- **Observation (active development):** Memgraph follows **6-week release cycles**; latest stable at review time is **v3.10.1 (May 15, 2026)** with v3.10.0 (May 13, 2026) adding features (coordinator read-only queries, runtime TLS reload, etc.). Daily builds are published. (github.com/memgraph/memgraph/releases; github.com/memgraph/roadmap)
- **Observation (repo health):** `memgraph/memgraph` GitHub repo: ~4,232 stars, ~245 forks, ~5,069 commits, C++ codebase, active issue/milestone tracking, contributing guide, Discord and Stack Overflow communities. (github.com/memgraph/memgraph)
- **Observation (company):** Developed by Memgraph Ltd (London); raised >$18M (led by Microsoft's M12, 2021). Customers cited include NASA, Cedars-Sinai, Capitec Bank. (HandWiki; memgraph.com/knowledge-graph)
- **Observation (licensing — Community):** "Memgraph Community is available under the **Business Source License (BSL) 1.1**." The BSL is explicitly "not an 'open source' license" (source-available). The licensed work is "Memgraph Community Edition (MCE) version 2.0"; the **Additional Use Grant** permits production use for "internal business purposes" provided you do not (a) embed/distribute to third parties or give third parties standalone control, (b) offer it as database-as-a-service, or (c) build a competing product. The **Change License** is Apache License 2.0, effective on the Change Date. (github.com/memgraph/memgraph/licenses/BSL.txt)
- **Observation (licensing — Change Date discrepancy):** The fetched BSL.txt states `CHANGE DATE: 2030-15-05` (an internally inconsistent / malformed date string), while a DeepWiki summary of the same license states `Change Date: March 28, 2029`. Both agree the license converts to Apache 2.0 on the Change Date. (github BSL.txt vs deepwiki.com/memgraph/memgraph/9-licensing-and-legal — discrepancy noted as an unknown.)
- **Observation (licensing — Enterprise):** "Memgraph Enterprise is available under the **Memgraph Enterprise License (MEL)**" — a proprietary commercial license (fixed-term subscription, minimum 1 year, capacity-limited, includes support). Enterprise adds HA management, advanced auth/SSO, multi-tenancy, audit logging, TTL, parallel execution. (Memgraph docs; deepwiki licensing page)
- **Observation (cost):** Community Edition (BSL) is free to use under the Additional Use Grant. Enterprise is commercial (per MEL, paid subscription). Memgraph Cloud (managed, AWS, Enterprise instances) is offered. No per-query or per-replica charges are advertised for self-hosted Community. (memgraph.com/pricing; saasworthy; memgraph-vs-tigergraph blog noting Community replication/HA is available even in Community)
- **Interpretation:** Memgraph is actively and professionally maintained, with a regular release cadence, a real (if smaller than Neo4j's) community, and commercial backing. **Licensing is the key differentiator from Neo4j Community (GPLv3, true open source):** Memgraph Community is BSL — source-available but *not* OSI open source, with usage restrictions (no DBaaS, no redistribution/competing product) that lapse to Apache 2.0 only on the Change Date. For EDASES internal research/use this is likely permissible, but the BSL restrictions and the open-source conversion date are legal questions to assess separately.

### 11. Composition with a React/TypeScript frontend

- **Observation (JS/TS driver):** The official Memgraph Node.js documentation instructs using the **`neo4j-driver`** npm package (`npm install neo4j-driver`), connecting over Bolt (`bolt://localhost:7687`). The driver is JavaScript/TypeScript with types and supports both Node and browser (WebSocket) usage. (Memgraph docs "connect-to-memgraph/drivers/nodejs"; Stack Overflow example; neo4j-javascript-driver README)
- **Observation (no first-party React graph component):** Unlike Neo4j (which ships the Neo4j Visualization Library React wrappers, `@neo4j-nvl/react`), no Memgraph-first-party React visualization wrapper was found in this review. Memgraph provides **Memgraph Lab** (a separate visual query/exploration UI) and the **GQLAlchemy** Python OGM/query-builder, but the browser-side composition relies on the generic `neo4j-driver` plus any third-party React graph renderer (e.g. the RQ1 candidates in this research line). (Memgraph docs; comparison with RQ4-Neo4j evidence)
- **Interpretation:** Memgraph can serve as a backend for a React/TypeScript frontend via the `neo4j-driver` (Bolt, browser or via a Node/BFF layer). The driver is the same one used for Neo4j, so the composition story is essentially the same as Neo4j's, minus a first-party React graph component. **Security note (observation):** connecting a browser directly to Memgraph over WebSockets typically requires exposing the Bolt port and credentials to the client; production deployments normally route queries through a backend (BFF) that holds the driver and credentials. This is an architectural convention, not a Memgraph limitation.

## Findings

1. **Artefacts** map naturally to labelled nodes with properties; no fixed schema is required (schema-optional property graph model, shared with Neo4j).
2. **Versions** are modelled via the entity–state pattern: an immutable entity node linked to per-version `State` nodes, with a `LATEST`/chain pointer. Branching is supported by multiple version relationships. This adds one intermediate node per version — a recognised, low-cost idiom. **Assumption:** the pattern transfers from Neo4j because Memgraph implements the same property graph model and openCypher; no Memgraph-specific versioning guide was located.
3. **Evidence** links to artefacts/versions as nodes connected by typed, property-bearing relationships; no join table needed.
4. **Provenance** is a chain of typed relationships (`CREATED`, `DERIVED_FROM`, `BASED_ON`), traversable in one Cypher clause via variable-length patterns; no join tables.
5. **Supersession** is the cleanest case: a typed, directed `SUPERSEDES` relationship (optionally an event node on the edge for metadata), with chains traversable via `[:SUPERSEDES*]`.
6. **Schema complexity** remains low across all five concerns — effectively identical to Neo4j, because both use the same property graph model and Cypher. The only recurring extra structure is the version `State` node + pointer. Discipline required: meaningful labels/relationship types, not a generic catch-all.
7. **Performance** for EDASES-style traversals is structurally favoured by in-memory storage (no disk I/O on the read path, C++ with no JVM GC). Deep multi-hop provenance/supersession queries should be especially fast. **Caveats:** the dataset must fit in RAM (no built-in sharding; vertical scaling only); write scaling is limited; vendor/third-party latency/throughput figures are not independently verified for EDASES.
8. **Persistence/backup**: durable via WAL + periodic full snapshots to `/var/lib/memgraph`; restore via `RECOVER SNAPSHOT`. Backup is a manual file-copy procedure (with `LOCK DATA DIRECTORY`); off-host backup must be scripted (no built-in cloud backup).
9. **Neo4j compatibility** is real but partial: openCypher + Bolt, so the `neo4j-driver` works and the EDASES modelling patterns transfer with at most minor syntax adjustments. Documented dialect differences exist (index/constraint syntax, no auto-index-on-constraint, some unsupported constructs). "Compatibility is not identity" — engine behaviour differs.
10. **Maintenance/licensing**: actively maintained (6-week cadence, v3.10.1 May 2026, ~4.2k GitHub stars, commercial backing). Community Edition is **BSL (source-available, not OSI open source)** with internal-use permitted and conversion to Apache 2.0 on the Change Date; Enterprise is commercial MEL. Cost: Community free under BSL; Enterprise paid.
11. **React/TS composition**: via the `neo4j-driver` (Bolt, browser or Node/BFF). No first-party React graph component (unlike Neo4j NVL); relies on generic driver + third-party renderers. A BFF is the usual production topology to avoid exposing credentials.

**Overall:** Memgraph can represent artefacts, versions, evidence, provenance, and supersession as first-class graph constructs with low schema complexity — structurally the same answer as Neo4j, because both rest on the property graph model and Cypher. The distinguishing factors versus Neo4j are: (a) an **in-memory architecture** that should make EDASES traversal queries faster but **RAM-bounds** the dataset and lacks sharding; (b) **BSL licensing** (source-available, not true open source) versus Neo4j Community's GPLv3; (c) **partial** rather than full Cypher compatibility, with documented dialect differences; (d) no first-party React visualization wrapper. The principal trade-offs are the RAM-bound scale limit, the BSL licensing restrictions, and the manual (scripted) backup/off-host strategy.

## Rejected options

- **Storing versions as node properties only (e.g. a `version` integer on the artefact node).** Rejected for the same reason as in the Neo4j analysis: it overwrites history — it cannot retain multiple coexisting versions or support provenance/evidence per version. The entity–state pattern (separate version nodes) is preferred.
- **Modelling everything as a single generic `Node` label with a `type` property.** Rejected: defeats label-based indexing (Memgraph supports label and label-property indexes) and forces full-graph scans. Meaningful labels are required for performance and clarity — same anti-pattern as Neo4j.
- **Relying on WAL-only persistence.** Rejected: Memgraph documentation states the database "cannot be used with only WAL files enabled" — snapshots (or snapshots + WAL) are required for durability. (Observation, not a modelling choice.)
- **Direct browser-to-Memgraph WebSocket connection in production.** Rejected as a production topology (credential exposure on the Bolt port); a backend/BFF holding the driver is the standard approach. Architectural convention, not a database limitation.
- **Treating Memgraph as a drop-in, fully Neo4j-compatible substitute.** Rejected as an assumption: compatibility is openCypher + Bolt, with documented differences; engine behaviour (in-memory, RAM-bound, no sharding) also differs. Queries and clients transfer, but operational characteristics do not.

## Unknowns

- **EDASES workload shape and scale** are unknown, so the structural performance advantage (in-memory, no disk I/O) is established but the absolute latency/throughput and, critically, whether the artefact graph fits in RAM, are not determined.
- **BSL Change Date** is inconsistent across sources (fetched license text `2030-15-05` vs DeepWiki `March 28, 2029`); the exact open-source conversion date is unconfirmed. The license converts to Apache 2.0 regardless.
- **BSL implications** for how EDASES would use, distribute, or embed Memgraph (internal research use is permitted; redistribution/DBaaS/competing-product use is not) are a legal question not resolved here.
- **Memgraph-specific versioning guidance** was not located; the entity–state versioning claim for Memgraph is an interpretation carried over from the shared property graph model, not sourced from a Memgraph versioning document.
- **Independent, third-party benchmarks** of Memgraph vs Neo4j for EDASES-shaped queries are scarce; the speed/throughput figures cited are vendor or third-party blog comparisons and are indicative only.
- **Super-node risk** for any artefact that accumulates very many relationships (e.g. a root artefact with thousands of derived versions/evidence links) is a known graph-database modelling concern whose relevance to EDASES is unquantified. (Memgraph's index/query-planner behaviour on super-nodes was not specifically verified.)
- Whether EDASES requires **temporal/bitemporal** versioning (point-in-time reconstruction of the whole artefact graph) — Memgraph supports it via modelling patterns (properties on nodes/relationships, as in Neo4j) but it is not a built-in feature and adds modelling overhead.

## Confidence

**Medium-High.**

- **High** for the modelling-capability claims (artefacts, evidence, provenance, supersession): these follow directly from Memgraph's documented property graph model and openCypher support, which are consistent across multiple independent sources and are structurally identical to Neo4j (covered in depth by the sibling RQ4-Neo4j report).
- **Medium-High** for the versioning claim: the entity–state pattern is a pure Cypher modelling idiom that transfers to any openCypher property graph database, but no Memgraph-specific versioning document was located, so it is carried as an interpretation/assumption.
- **High** for ecosystem/maintenance facts (GitHub release history v3.10.1, 6-week cadence, stars/commits, company funding) and for the persistence mechanism (WAL + snapshots, documented backup/restore commands).
- **Medium** for licensing: the BSL-vs-open-source distinction and the Additional Use Grant are clearly documented, but the Change Date is inconsistent across sources and the precise legal implications for EDASES are unassessed.
- **Medium** for performance: the architectural claim (in-memory = no disk I/O on reads, C++ no GC) is well established, but the quantitative "10–100x lower latency / 100K+ txns/sec" figures are vendor/third-party and not independently verified for the EDASES artefact graph; the RAM-bound / no-sharding limitation is a real constraint whose impact depends on unknown graph size.
- **High** for Neo4j compatibility at the query/driver level (openCypher + Bolt + `neo4j-driver`), with the caveat that dialect differences exist and "compatibility is not identity."

The core research question — *can Memgraph represent these five concerns naturally without excessive schema complexity?* — is answered with reasonable confidence: **yes**, with the same low schema-complexity profile as Neo4j, the only modest addition being the version-history `State`-node idiom. The decision-relevant differentiators are operational (in-memory/RAM-bound, BSL licensing, partial Cypher compatibility, manual backup), not modelling-capability limitations.

## References

- Memgraph, official site. https://memgraph.com
- Memgraph, documentation (property graph model, Cypher, durability, backup/restore, drivers). https://memgraph.com/docs
- Memgraph, "Differences in Cypher implementations". https://memgraph.com/docs/querying/differences-in-cypher-implementations
- Memgraph, "Cypher Differences Between Neo4j and Memgraph" (blog), 2024-08-21. https://memgraph.com/blog/cypher-differences-between-neo4j-and-memgraph
- Memgraph, "Data durability" (fundamentals). https://memgraph.com/docs/fundamentals/data-durability
- Memgraph, "Backup and restore". https://memgraph.com/docs/database-management/backup-and-restore
- Memgraph, "How Does Memgraph Ensure Data Durability?" (blog), 2023-10-04. https://memgraph.com/blog/how-does-memgraph-ensure-data-durability
- Memgraph, "Understanding Database Snapshots" (blog). https://memgraph.com/blog/understanding-database-snapshots
- Memgraph, "Memgraph in mission-critical workloads" (backup/off-host note). https://memgraph.com/docs/deployment/workloads/memgraph-in-mission-critical-workloads
- Memgraph, `memgraph-cypher-syntax` skill (openCypher syntax, deep traversals). https://github.com/memgraph/skills/blob/main/skills/memgraph-cypher-syntax/SKILL.md
- Memgraph, GitHub repository (`memgraph/memgraph`): stars, commits, releases (v3.10.1, May 2026), license. https://github.com/memgraph/memgraph
- Memgraph, BSL license text. https://github.com/memgraph/memgraph/blob/master/licenses/BSL.txt
- Memgraph, roadmap (6-week release cycles). https://github.com/memgraph/roadmap
- Memgraph, "Connect to Memgraph / Node.js driver" (uses `neo4j-driver`). https://memgraph.com/docs/memgraph/connect-to-memgraph/drivers/nodejs
- Memgraph, "Migrate from Neo4j". https://memgraph.com/docs/data-migration/migrate-from-neo4j
- Memgraph, knowledge-graph / case studies (NASA, Cedars-Sinai, Capitec Bank). https://memgraph.com/knowledge-graph
- DeepWiki, "Licensing and Legal | memgraph/memgraph" (BSL/MEL, Change Date 2029). https://deepwiki.com/memgraph/memgraph/9-licensing-and-legal
- HandWiki / EverybodyWiki, "Software:Memgraph" (property graph model, openCypher, BSL/MEL, funding). https://handwiki.org/wiki/software:memgraph
- SoloSoft, "Memgraph: Real-Time Graph Database for Streaming Data" (2026 comparison table). https://www.solosoft.dev/post/memgraph-database-2026/
- simplyblock, "What is Memgraph?" (in-memory + WAL/snapshots, ACID). https://simplyblock.io/glossary/what-is-memgraph/
- PuppyGraph, "Memgraph vs Neo4j" (RAM-bound, no sharding, vertical scaling). https://www.puppygraph.com/blog/memgraph-vs-neo4j
- ODBMS.org, "Memgraph" listing, 2026-07-09. https://www.odbms.org/2026/07/memgraph/
- Stack Overflow, "How to persist Memgraph data to local hard drive?" (WAL + snapshots, Docker volumes). https://stackoverflow.com/questions/69637461/how-to-persist-memgraph-data-to-local-hard-drive
- Stack Overflow, "Memgraph is an in-memory database. Does that mean that data is lost…?" (durability, GQLAlchemy note). https://stackoverflow.com/questions/73631960/memgraph-is-an-in-memory-database-does-that-mean-that-data-is-lost-when-i-shutd
- Stack Overflow, "What is the easiest way to connect to Memgraph using Node.js?" (neo4j-driver example). https://stackoverflow.com/questions/74429887/what-is-the-easiest-way-to-connect-to-memgraph-using-node-js
- npm, `neo4j-driver` package (official JS/TS Bolt driver used for Memgraph). https://www.npmjs.com/package/neo4j-driver
- Rost Glukhov, "Neo4j graph database for GraphRAG…" (note: "compatibility is not identity"). https://www.glukhov.org/data-infrastructure/databases/neo4j
- Sibling report: RQ4 — Neo4j (property graph model, entity–state versioning pattern, supersession/evidence/provenance modelling). /home/claude-code/projects/ASES/research/execution-engine-ui/reports/rq4-neo4j.md
