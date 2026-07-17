# RQ4 — Kuzu

## Question

Can a graph database naturally represent artefacts, versions, evidence, provenance, and supersession without excessive schema complexity? This report investigates **Kuzu** (https://kuzudb.com), an embedded, Cypher-speaking property graph database, as a candidate technology for answering that question.

## Scope

**Investigated:**
- Kuzu's data model (node tables, relationship tables, typing, schema requirements) and how it maps to artefacts, versions, evidence, provenance, and supersession.
- The "embedded" nature of Kuzu and its implications for a web-application backend (server requirement, process model, persistence format).
- Performance characteristics for graph traversal, with published benchmark figures.
- Persistence and backup ergonomics.
- Cypher compatibility (openCypher coverage, deviations).
- Licensing.
- Maintenance status, community size, and corporate backing — including the archival event of October 2025.
- Client libraries (JavaScript/TypeScript) and REST/HTTP composition options.

**Excluded:**
- Hands-on benchmarking or code execution (this is a literature/evidence investigation; no Kuzu instance was run).
- Detailed comparison against other candidates beyond what is needed to contextualise findings (a separate RQ4 report covers Neo4j; forks are mentioned only where they bear on maintenance risk).
- Security hardening, access-control models, and distributed/clustered deployment (out of scope for an embedded single-node library).
- Any recommendation or implementation proposal (forbidden by task rules).

## Evidence

### E1. Data model: structured property graph with node and relationship tables
- Kuzu implements a **structured property graph model**. Data is organised into **node tables** and **relationship (rel) tables**; the documentation deliberately uses "table" rather than "label" because Kuzu is "ultimately a relational system" storing sets of tuples (kuzudb.github.io/docs/cypher/data-definition/create-table).
- Every node or relationship has **exactly one** label/table (kuzudb.github.io/docs/cypher/data-definition/create-table). This is a deviation from Neo4j, where a node may carry multiple labels.
- **Node tables require a primary key** (STRING, INT64, DATE, or BLOB), which is automatically indexed. Relationship tables require no primary key (kuzudb.github.io/docs/get-started).
- Properties are **strongly typed** and must be declared up front; the schema is pre-defined, not schema-optional (kuzudb.github.io/docs/get-started).
- Relationship tables declare **multiplicity** (`MANY_ONE`, `ONE_MANY`, `MANY_MANY`, `ONE_ONE`) between source and destination node tables, e.g. `CREATE REL TABLE LivesIn (FROM User TO City, MANY_ONE)` (kuzudb.github.io/docs/cypher/data-definition/create-table).
- Schema can be evolved with `ALTER TABLE` to add columns/properties without dropping the table (kuzudb/kuzu GitHub discussion #3594).
- A "relationship table group" syntax (`CREATE REL TABLE GROUP`) existed but was **deprecated in v0.8.0**; multiple `FROM ... TO ...` clauses in a single `CREATE REL TABLE` are now the supported way to relate a relationship to multiple node-table pairs (kuzudb.github.io/docs/cypher/data-definition/create-table).

### E2. Cypher / openCypher support
- Kuzu implements **openCypher** (kuzudb.github.io/docs; LangChain docs). It supports `MATCH`, `CREATE`, property filters, aggregation, variable-length traversals (e.g. `[:FRIEND*1..4]`), and `shortestPath` (puppygraph.com/blog/what-is-kuzudb; brightcoding.dev blog).
- The query planner uses a dynamic-programming join optimizer and factorized/vectorized execution (maxnilz.com PDF of the CIDR 2023 Kuzu paper; kuzudb.github.io/docs).
- Deviation from Neo4j-style Cypher: one label per node, and the "table" terminology; no "exactly 1" foreign-key constraint semantics are enforced (kuzudb.github.io/docs/cypher/data-definition/create-table).

### E3. Embedded, in-process, serverless
- Kuzu is an **embedded database**: it runs **in-process within the host application**; there is **no separate server process** to manage (kuzudb.github.io/docs; deepwiki.com/kuzudb/kuzu; LangChain docs).
- The `Database` object is the database software (buffer manager, storage manager, transaction manager). Only **one `READ_WRITE` Database object** may exist for a given database file; multiple `READ_ONLY` objects are permitted. Two concurrent `READ_WRITE` objects (even across processes) are unsafe and blocked by a file lock (kuzudb.github.io/docs/concurrency).
- **Concurrency model:** Kuzu allows **one writer transaction at a time**, which can run concurrently with multiple read transactions. Transactions are **serializable ACID**. Multi-version concurrency control for multiple concurrent writers was on the roadmap but **not implemented in the original project** (maxnilz.com CIDR 2023 paper; kuzudb.github.io/docs/concurrency; Vela-Engineering/kuzu README).
- For a web-application backend, the embedded model means a server process must host the `Database` object and expose it (e.g. via the official `kuzu-api-server`, an Express.js REST-style server — github.com/kuzudb/api-server; or the Bighorn fork which adds server mode — vela.partners blog). Kuzu itself does not ship a built-in multi-client server.

### E4. Persistence and backup ergonomics
- Kuzu supports **on-disk** and **in-memory** modes. On-disk mode persists to a database directory; all transactions are logged to a **Write-Ahead Log (WAL)** and periodically merged via checkpoints (kuzudb.github.io/docs/get-started).
- Because the database is a **folder on disk**, it is trivially copyable, movable, zippable, and can be placed under version control — described as "git-friendly workflows" (brightcoding.dev blog). This makes backup and snapshotting straightforward at the file level.
- In-memory mode (`:memory:` or `""`) writes nothing to disk and loses all data on process exit (kuzudb.github.io/docs/get-started).

### E5. Performance and benchmarks
- Architecture: columnar disk-based storage, Compressed Sparse Row (CSR) adjacency-list/join indices, vectorized and factorized query processor, worst-case-optimal join algorithms, and multi-core (morsel-driven) parallelism (kuzudb.github.io/docs; README; CIDR 2023 paper).
- Kuzu is explicitly **OLAP/analytical**-oriented (optimised for complex join-heavy analytical workloads on large graphs), not an OLTP system (kuzudb.github.io/docs; puppygraph.com/blog/what-is-kuzudb).
- Published benchmark (prrao87/kuzudb-study, GitHub; thedataquarry.com/blog/embedded-db-2): artificial social network of **~100K nodes and ~2.4M edges** on an M3 MacBook Pro (36 GB). Ingestion was **~18x faster overall** than Neo4j Community (52.8x total: 30.64s vs 0.58s). Query results (averaged over ≥5 runs):
  - Query 8 (2nd-degree path enumeration): **Kuzu 0.0086s vs Neo4j 3.22s ≈ 374x faster**.
  - Query 9 (filtered path enumeration): Kuzu 0.0955s vs Neo4j 3.897s ≈ 40.8x faster.
  - Other queries ranged from ~0.5x (slower) to ~10x faster; a few simple lookups were marginally slower than Neo4j.
- Kuzu is regularly tested on the **LDBC SNB SF100** benchmark (~280M nodes, 1.7B edges) (thedataquarry.com/blog/embedded-db-2; brightcoding.dev blog).
- Follow-up benchmarks (prrao87/graph-benchmark, 2026) re-run the same suite on the **LadybugDB** fork (successor to Kuzu) and show near-identical multi-hop performance to original Kuzu (e.g. q8: Ladybug 6.5ms vs Kuzu 6.5ms vs Neo4j 2831ms), confirming the engine's traversal speed is preserved in the maintained fork.
- **Interpretation (labelled):** The 374x figure is a single path-enumeration query on one dataset/machine; it should not be read as a universal speedup. The consistent signal across queries is that Kuzu is substantially faster than Neo4j Community on multi-hop analytical traversals, and competitive or slightly slower on trivial lookups.

### E6. Licensing
- Kuzu is licensed under the **MIT License** (permissive), confirmed on the GitHub repo LICENSE file, README, and multiple secondary sources (github.com/kuzudb/kuzu; LangChain docs; puppygraph.com). MIT permits commercial and proprietary use.

### E7. Maintenance status — archived October 2025 (critical finding)
- The official repository **github.com/kuzudb/kuzu was archived by the owner on Oct 10, 2025** and is now read-only. The archival notice states: "Kuzu is working on something new! We are archiving the KuzuDB project here… prior Kuzu releases will continue to be usable in the same way without modifications to your code" (github.com/kuzudb/kuzu; The Register, 2025-10-14; gdotv.com weekly-edge, 2025-10-17).
- **Corporate backing / acquisition:** Kuzu Inc. was a University of Waterloo spin-off (Toronto/Waterloo, Canada), founded ~2023, ~11 employees. In 2025 **Apple Inc. acquired Kuzu Inc.** (an acqui-hire); the transaction was completed around October 2025 and publicly disclosed via EU filings in February 2026. Following the acquisition, kuzudb.com was shut down and the GitHub repo archived (grokipedia.com; gdotv.com blog, 2026-05-28; The Verge coverage referenced therein).
- **Community size (at archival):** ~4,000 GitHub stars, ~498 forks, ~5,231 commits, 36 releases (latest v0.11.3, Oct 10 2025) (github.com/kuzudb/kuzu).
- **Active forks** now carry the codebase forward (all MIT-licensed):
  - **LadybugDB** (github.com/LadybugDB/ladybug) — community fork described as gdotv's pick to carry Kuzu forward; actively developed; single-writer (gdotv.com, 2026-05-28).
  - **Vela-Engineering/kuzu** (github.com/Vela-Engineering/kuzu) — maintained by Vela Partners; adds **concurrent multi-writer** support; 6 releases since fork (vela.partners blog; cmu-db/dbdb.io issue #162).
  - **Bighorn** (github.com/Kineviz/bighorn) — Kineviz fork; adds server mode alongside embedded; single-writer (vela.partners blog).
  - **RyuGraph** (github.com/predictable-labs/ryugraph) — Predictable Labs fork; WASM bindings highlighted (github README).
  - **Lance Graph** — spiritual heir inside LanceDB by ex-Kuzu engineer Prashanth Rao (gdotv.com, 2026-05-28).
- **Interpretation (labelled):** The original Kuzu project is **no longer maintained by its authors**. For any new adoption, the realistic path is a community fork. Fork health varies; LadybugDB and Vela-Engineering/kuzu are the most cited active successors as of mid-2026.

### E8. Client libraries and composition
- **Official language bindings:** Python, Node.js, Java, Rust, Go, Swift, C, C++ (github.com/kuzudb/kuzu README; iCharlesHu/Kuzu mirror).
- **JavaScript/TypeScript:** `npm install kuzu` provides a Node.js wrapper supporting **both CommonJS (`require`) and ES Modules (`import`)**, usable from JavaScript or TypeScript. Prebuilt native binaries are bundled in the npm package (kuzudb.github.io/api-docs/nodejs).
- **REST API:** An official **`kuzu-api-server`** (REST-style, Express.js) exists in the Kuzu GitHub org, allowing HTTP access to a Kuzu database (github.com/kuzudb; github.com/kuzudb/api-server). Persistence to local DB files is supported via Docker volume mounts (github.com/Rehket/kuzu-api-server).
- **WASM:** Kuzu ships **WebAssembly bindings** that run the full database in a browser (README; gdotv.com; puppygraph.com), enabling fully client-side graph operation.
- **MCP server:** A `kuzu-mcp-server` (Model Context Protocol) is published by the Kuzu org (github.com/kuzudb/kuzu-mcp-server).
- **Interoperability:** Reads/writes Parquet and Arrow, can attach/scan DuckDB databases, and scan Iceberg/Delta Lake; query results convert to Pandas/Polars without serialization (puppygraph.com/blog/what-is-kuzudb).

## Findings

**F1 — Artefacts as nodes.** Kuzu can represent engineering artefacts directly as node tables, e.g. `CREATE NODE TABLE Artefact(id STRING PRIMARY KEY, kind STRING, content STRING)`. Each artefact is a typed, indexed node. (Observation from E1.)

**F2 — Versions.** Versions are naturally modelled as a separate node table `ArtefactVersion` linked to an `Artefact` via a `HAS_VERSION` relationship. A **version chain** is a linear sequence of `PRECEDES`/`NEXT` relationships between version nodes; **branching** is expressed by a version node having multiple outgoing `NEXT` edges. Multiplicity constraints can enforce, e.g., that a version has at most one predecessor (`MANY_ONE`). (Observation from E1; modelling is a direct application of the property-graph primitives.)

**F3 — Evidence.** Evidence is naturally a node table `Evidence` connected to artefacts and/or versions through typed relationships such as `EVIDENCE_FOR` / `SUPPORTS`. Linking evidence to specific versions (rather than only to artefacts) is straightforward because versions are first-class nodes. (Observation from E1/E2; modelling inference.)

**F4 — Provenance.** Provenance chains are the natural strength of a graph DB: a `DERIVED_FROM`, `PRODUCED_BY`, or `GENERATED_BY` relationship traversed multi-hop answers "where did this come from?" directly. Kuzu's factorized/WCOJ engine is specifically built for such many-to-many multi-hop traversals (E2, E5). (Observation from E2/E5; the fit is inherent to the graph model.)

**F5 — Supersession.** Supersession is a typed relationship, e.g. `SUPERSEDES FROM ArtefactVersion TO ArtefactVersion`, optionally carrying properties (e.g. `superseded_at`, `reason`). Querying "what is the current valid version?" reduces to traversing `SUPERSEDES` chains. (Observation from E1/E2; modelling inference.)

**F6 — Schema complexity stays low for these concepts.** Because artefacts, versions, evidence, provenance links, and supersession links are each a small number of node/rel tables with declared typed properties, the schema is compact and readable — arguably **cleaner than a normalised relational schema**, where the same concepts require join tables and foreign keys. (Interpretation from E1, consistent with the property-graph thesis.)

**F7 — Two modelling constraints to note.** (a) **One label per node** means an artefact cannot simultaneously carry multiple labels; if an artefact must play several roles, that must be expressed via relationships or separate node tables (E1). (b) The schema is **pre-defined and strongly typed** (not schema-optional), so the artefact/version/evidence model must be declared before data is loaded; this is a trade-off — more upfront structure, but it enables the vectorized performance and type safety that benefit a rigorous provenance/supersession model. (Observation from E1.)

**F8 — Embedded model fits "local-first" but complicates a multi-user web backend.** Kuzu runs in-process with no server, which is excellent for local tooling, CLIs, and browser/WASM use. For a concurrent multi-user web application, a hosting process must wrap the `Database` object (api-server, or a fork with server mode), and the **single-writer constraint** of the original engine becomes a throughput ceiling under concurrent writes. (Observation from E3; interpretation for web-backend fitness.)

**F9 — Maintenance is the dominant risk.** The original project is archived and its authors acquired by Apple; continued use depends on a community fork. The engine itself is mature (CIDR 2023 paper, LDBC SF100 testing, 5k+ commits) and the MIT license permits forking, but **long-term maintenance cannot be assumed from the original vendor**. (Observation from E7; interpretation.)

## Rejected options

- **Using the original `github.com/kuzudb/kuzu` as a dependency going forward.** Rejected as a primary dependency because the repository is archived/read-only as of Oct 10 2025 and the vendor no longer supports it (E7). If Kuzu is adopted, a maintained fork (LadybugDB, Vela-Engineering/kuzu, or Bighorn) would be the realistic source — this is a finding, not a recommendation.
- **Relying on Kuzu's built-in server for a web backend.** Rejected because Kuzu ships no native multi-client server; composition requires the separate `kuzu-api-server` or a fork with server mode (E3, E8).
- **Treating Kuzu as an OLTP system.** Rejected because the engine is explicitly analytical (OLAP) and single-writer; high-frequency concurrent transactional writes are not its design centre (E3, E5).

## Unknowns

- **U1.** The exact post-acquisition status of the Kuzu *trademark* and whether Apple may re-release a product based on the codebase — unknown; only the open-source repo archival and EU filing disclosure are confirmed (E7).
- **U2.** Long-term health and governance of the community forks (LadybugDB, Vela-Engineering/kuzu, Bighorn, RyuGraph). As of mid-2026 they are active, but governance models and contributor counts are not firmly established (E7).
- **U3.** Whether the "exactly 1" foreign-key constraint semantics will ever be added to Kuzu/forks — the docs state it is "planned for a future release" but unconfirmed (E1).
- **U4.** Real-world write-throughput behaviour of the Vela concurrent-multi-writer fork under contention was not independently benchmarked in the sources reviewed; the 374x figure concerns read-path traversal, not write concurrency (E5, E7).
- **U5.** Behaviour of Kuzu's WASM build for larger graphs in-browser (memory/performance ceilings) was not quantified in the sources reviewed (E8).

## Confidence

**Medium-High** on the core modelling claim (artefacts, versions, evidence, provenance, supersession can be represented naturally with low schema complexity): this follows directly from Kuzu's documented structured property-graph primitives (E1–E2, F1–F7) and is consistent with how graph DBs model connected concepts generally.

**Medium** on the web-backend and maintenance assessment: the embedded/serverless model and single-writer constraint are well documented (E3), but the practical implications for an EDASES web application depend on unmeasured write-concurrency and fork-health factors (U2, U4). The archival event is a confirmed, high-impact fact (E7) that materially lowers confidence in adopting the *original* project, though the MIT license and active forks preserve the *technology's* viability.

Justification summary: modelling fitness is well-evidenced; the decisive uncertainty is not technical fit but **project continuity**, which is documented as terminated for the upstream project and ongoing only via community forks.

## References

1. Kuzu GitHub repository (archived notice, README, LICENSE): https://github.com/kuzudb/kuzu
2. Kuzu documentation — Get Started (persistence, schema, on-disk/in-memory): https://kuzudb.github.io/docs/get-started/
3. Kuzu documentation — Create Table (node/rel tables, one label, multiplicity, ALTER): https://kuzudb.github.io/docs/cypher/data-definition/create-table/
4. Kuzu documentation — Connections & Concurrency (single writer, READ_WRITE/READ_ONLY, file lock): https://kuzudb.github.io/docs/concurrency/
5. Kuzu documentation — home / why-Kuzu: https://kuzudb.github.io/docs/
6. Jin et al., "KÙZU* Graph Database Management System", CIDR 2023: https://www.cidrdb.org/cidr2023/papers/p48-jin.pdf (mirror: https://maxnilz.com/papers/KUZU%20Graph%20Database%20Management%20System.pdf)
7. prrao87/kuzudb-study (Kuzu vs Neo4j benchmark, 100K nodes / 2.4M edges): https://github.com/prrao87/kuzudb-study
8. prrao87/graph-benchmark (LadybugDB/Kuzu/Lance follow-up benchmarks): https://github.com/prrao87/graph-benchmark
9. The Data Quarry, "Embedded databases (2): Kùzu…", benchmark write-up: https://thedataquarry.com/blog/embedded-db-2/
10. The Register, "KuzuDB graph database abandoned, community mulls options", 2025-10-14: https://www.theregister.com/2025/10/14/kuzudb-graph-database-abandoned-community-mulls-options/1142229
11. gdotv, "Adieu Kuzu, State of the Graph", 2025-10-17: https://gdotv.com/blog/weekly-edge-adieu-kuzu-state-of-the-graph-17-october-2025
12. gdotv, "Kuzu's Legacy and the New Wave of Embedded Graph Databases", 2026-05-28: https://gdotv.com/blog/kuzu-legacy-embedded-graph-database-landscape/
13. Grokipedia, "Kuzu (graph database)" — Apple acquisition summary: https://grokipedia.com/page/Kuzu_graph_database
14. Vela-Engineering/kuzu fork (concurrent multi-writer, archival context): https://github.com/Vela-Engineering/kuzu
15. Vela Partners blog, "KuzuDB Fork for AI Agents": https://vela.partners/blog/kuzudb-ai-agent-memory-graph-database
16. cmu-db/dbdb.io issue #162 (fork listing / archival note): https://github.com/cmu-db/dbdb.io/issues/162
17. Kuzu Node.js API docs (npm `kuzu`, CommonJS/ESM, TypeScript): https://kuzudb.github.io/api-docs/nodejs/
18. Kuzu api-server (REST, Express.js): https://github.com/kuzudb/api-server
19. Kuzu MCP server: https://github.com/kuzudb/kuzu-mcp-server
20. PuppyGraph, "What Is KuzuDB?": https://www.puppygraph.com/blog/what-is-kuzudb
21. LangChain Kuzu integration docs (embedded, MIT, Cypher summary): https://docs.langchain.com/oss/python/integrations/graphs/kuzu_db
22. BrightCoding, "Kuzu: The Embedded Graph Database…": https://www.blog.brightcoding.dev/2025/09/24/kuzu-the-embedded-graph-database-for-fast-scalable-analytics-and-seamless-integration
