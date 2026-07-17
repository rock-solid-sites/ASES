# RQ4 — Neo4j

## Question

Can a graph database naturally represent artefacts, versions, evidence, provenance, and supersession without excessive schema complexity?

This report investigates **Neo4j** (https://neo4j.com) — the most widely used property-graph database, using the property graph model and the Cypher query language — as a candidate backend for the EDASES execution-engine / artefact store. The focus is on whether the five EDASES concerns (artefacts, versions, evidence, provenance, supersession) can be modelled as first-class graph constructs, and whether doing so keeps the schema clean and navigable rather than requiring excessive intermediate nodes, relationship types, or properties.

## Scope

**Investigated:**
- Neo4j's property graph model: nodes, labels, relationships (typed, directed), and properties on both nodes and relationships.
- How artefacts (documents, code, decisions) map to nodes with labels and properties.
- How versions are modelled: the official Neo4j "entity–state" versioning pattern, time-based versioning, linked-list versioning, and timeline trees.
- How evidence (observations, test results, reviews) links to artefacts/versions via relationships.
- How provenance chains (who created what, when, based on what) are represented without join tables.
- How supersession (`A supersedes B`, including chains) is represented and traversed.
- Schema complexity: whether the above require excessive intermediate structure.
- Performance characteristics relevant to EDASES queries (provenance traversal, superseded-artefact discovery, version history).
- Persistence and export: backup, dump/restore, graph serialisation.
- Maintenance and ecosystem: active development, licensing (Community vs Enterprise), cost.
- Composition: serving as a backend for a React frontend; client libraries.

**Excluded:**
- Hands-on deployment, benchmarking, or running Neo4j (this is a literature/evidence review; no Neo4j instance was executed).
- Quantitative throughput/latency profiling for the specific EDASES workload shape (no authoritative benchmark located for that shape; vendor benchmarks are noted as such).
- Deep comparison against other graph databases (e.g. Amazon Neptune, ArangoDB) — covered by sibling reports in this research line where present.
- Any recommendation or implementation proposal (per research constraints; Neo4j is named only as evidence).

## Evidence

### 1. Property graph model — artefacts as nodes

- **Observation:** Neo4j uses the property graph model. "The property graph model consists of the following three main components: Nodes (entities, each with labels and properties), Relationships (connect nodes, typed, directed, with optional properties), and Properties (key-value pairs on both nodes and relationships)." (neo4j.com, Introduction to Neo4j / GraphAcademy; educative.io course material)
- **Observation:** "A label is a named graph construct that is used to group nodes into sets; all nodes labeled with the same label belong to the same set… A node may be labeled with any number of labels, including none." (Neo4j developer manual / Stack Overflow citation of official docs)
- **Observation:** "Nodes have labels (like `Person`, `Account`, or `Product`) that categorize them; relationships have types (like `KNOWS`, `TRANSFERRED_TO`, `PURCHASED`) and a direction; and both nodes and relationships can carry any number of properties." (medium.com/@artemkhrenov, "Graph Database Patterns", 2026-03-08)
- **Interpretation:** Engineering artefacts (a document, a code module, a decision) map directly to **nodes** carrying a domain label (e.g. `:Artefact`, `:Document`, `:Decision`) and arbitrary properties (id, title, content reference, status). There is no fixed schema to declare upfront — the model is schema-optional. This is a natural fit: an artefact is an entity, and its attributes are properties. No join table is needed to attach attributes.

### 2. Versions

- **Observation (official pattern):** Neo4j's own data-modelling guide documents an **entity–state** versioning strategy: "The entity `Product` is linked to its different versions by an explicit relationship. The entity `Product` is immutable. Only the properties that are stored in the different versions (`State` nodes) change. The `LATEST` relationship links the entity `Product` to its most recent version (`State`)." Query example from the docs: `MATCH (:Product {id:1})-[:V2]->(s:State) RETURN s.name` and `MATCH (:Product {id:1})-[:LATEST]->(s:State) RETURN s.name`. (neo4j.com/docs/getting-started/data-modeling/versioning)
- **Observation (official pattern):** The same guide documents **time-based versioning** (each element carries `validFrom`/`validTo` properties; nodes share a relationship only if validity intervals overlap) and **linked-list versioning** (an immutable entity node linked via `NEXT` relationships to ordered `State` nodes, with `FIRST`/`LAST` pointers). (ibid.)
- **Observation:** A community/third-party "entity-state model" library, **Neo4j Versioner Core** (Apache-2.0), implements exactly this pattern as stored procedures (`graph.versioner.update`, `graph.versioner.get.current.state`), confirming the pattern is a recognised, reusable idiom. (github.com/h-omer/neo4j-versioner-core)
- **Observation:** A 2025 blog describes a "production-grade, bitemporal versioning model" for Neo4j using `StartDate`/`EndDate` (or `Status`) on every node and relationship, supporting time-travel and historical reconstruction. (dev.to, 2025-12-05)
- **Interpretation:** "Version 3 of document X" is modelled as a **`State` node** (or a version node) attached to an immutable `:Document` entity node by a typed relationship (e.g. `:V3`, or a generic `:HAS_VERSION` with a `version` property, or a `NEXT` link in a chain). Branching versions are expressible by giving the entity multiple outgoing version relationships (a version tree) rather than a single linear chain. This is a **modelling choice, not a limitation** — Neo4j imposes no single versioning scheme. The cost is one intermediate `State`/version node per version, plus a `LATEST`/chain pointer to maintain; the official guide itself lists "updating nodes requires the deletion of the `LATEST` relationship, and the creation of a new relationship" as the main con. This is modest, not "excessive," schema complexity.

### 3. Evidence

- **Observation:** Because relationships are first-class, typed, directed, and can carry properties, an evidence item (an observation, a test result, a review) is naturally a **node** (e.g. `:Evidence`, `:TestResult`, `:Review`) connected to the artefact or version node by a typed relationship such as `:SUPPORTS`, `:CONTRADICTS`, `:EVIDENCE_FOR`, or `:REVIEWED`. The relationship itself can carry properties (e.g. `confidence`, `date`, `author`).
- **Interpretation:** Linking evidence to a specific *version* of an artefact is simply a relationship to that version's `State` node. No join table is required — the edge is the link. This is the same mechanism Neo4j markets for data lineage: "knowledge graphs… naturally capture how information flows and transforms across systems" and provenance "tracks the sourcing of data… and might also capture the modifications that have occurred along the way." (neo4j.com/blog/graph-database/what-is-data-lineage, 2025-03-06)

### 4. Provenance

- **Observation:** Provenance chains are expressed as chains of typed relationships. A canonical pattern: `(Agent)-[:CREATED]->(Artefact)`, `(Artefact)-[:DERIVED_FROM]->(OtherArtefact)`, `(Artefact)-[:BASED_ON]->(Evidence)`, with `createdAt`/`author` properties on the relationship or node. Neo4j's agent-memory docs state relationships are "first-class citizens in Neo4j, not afterthoughts requiring join tables." (neo4j.com/labs/agent-memory)
- **Observation:** Multi-hop provenance traversal is a single Cypher pattern, e.g. `MATCH path = (a:Artefact)-[:DERIVED_FROM*]->(root) RETURN path` returns the full provenance ancestry. Variable-length relationship patterns (`*`, `*1..5`) are a core Cypher feature. (neo4j.com/docs/cypher-manual)
- **Interpretation:** Provenance is represented **without join tables** — the relationship *is* the provenance edge, and traversal follows pointers. This is precisely the class of problem graph databases exist for ("traverse an unknown number of relationship hops at runtime… efficiently"), contrasted with SQL where the equivalent requires recursive CTEs or repeated self-joins. (medium.com/@artemkhrenov, 2026-03-08)

### 5. Supersession

- **Observation:** "Artefact A supersedes artefact B" is a typed, directed relationship, e.g. `(a:Artefact)-[:SUPERSEDES]->(b:Artefact)`. A chain of supersession is a path `(a)-[:SUPERSEDES]->(b)-[:SUPERSEDES]->(c)`, traversable with a variable-length pattern `MATCH (a)-[:SUPERSEDES*]->(x) RETURN x`.
- **Interpretation:** Supersession is a **natural, first-class relationship** — no intermediate node is required unless one wants to attach metadata to the supersession event itself (e.g. `reason`, `date`), in which case a `:Supersession` event node can sit on the edge. Chains are navigable in one Cypher clause. This is the cleanest of the five concerns: it maps directly onto a directed, typed edge.

### 6. Schema complexity — overall assessment

- **Observation:** Neo4j is schema-**optional**. "It features a flexible, schema-optional property graph model that adapts to changing data needs." (educative.io) Constraints (uniqueness, existence) and indexes are added explicitly and are optional. (neo4j.com/docs)
- **Observation (anti-pattern warning):** Neo4j's own modelling guidance warns against "modelling everything as a single label" (a generic `Node` with a `type` property), which "defeats Neo4j's label-based indexing entirely." Labels are the intended categorisation mechanism. (medium.com/@artemkhrenov, 2026-03-08)
- **Observation (scaling caveat):** Densely connected nodes ("super nodes") can degrade read/write performance; Neo4j publishes modelling strategies to mitigate them. (medium.com/neo4j, "Graph Modeling: All About Super Nodes", 2020-10-23)
- **Interpretation:** For the five EDASES concerns, the schema stays clean: artefacts = labelled nodes; versions = `State`/version nodes hung off an immutable entity (one extra node per version — a recognised, low-cost idiom); evidence = nodes linked by typed edges; provenance = typed relationship chains; supersession = a typed edge (optionally an event node). The only recurring "extra" structure is the version `State` node and its `LATEST`/chain pointer, which the official guide presents as simple and maintainable. This is **not excessive** schema complexity. The main discipline required is using meaningful labels and relationship types rather than a generic catch-all — a modelling convention, not a database limitation.

### 7. Performance

- **Observation:** Neo4j uses a **native graph storage engine** with **index-free adjacency**: "each node contains direct pointers to its relationships, and each relationship points directly to its start and end nodes. Traversing a relationship is an O(1) pointer follow, not a table scan or an index lookup." Local traversal cost is O(k) where k is the node degree, independent of total graph size n. (medium.com/@artemkhrenov, 2026-03-08; inferensys.com glossary on index-free adjacency)
- **Observation (vendor benchmark):** Neo4j's product page claims "The property graph data model enables queries to run 1000x faster than relational databases. Multi-hop queries execute fluidly… unlike relational databases which require slow, expensive join operations." (neo4j.com/product/neo4j-graph-database) A widely cited Neo4j benchmark (2022, 1M users / 50M friendships) reports 2-hop ~2 ms vs ~30 s in SQL, 3-hop ~5 ms vs ~2 min, 4-hop ~10 ms vs timeout. (scribd.com summary of Neo4j benchmark study; this is a vendor figure and should be treated as indicative, not independently verified for EDASES.)
- **Observation:** Neo4j 5/6 adds Cypher Parallel Runtime for analytical queries across large graph portions, and (per a 2025 third-party article) parallel relationship traversal and optimised page cache. (neo4j.com/blog/developer/speed-up-queries-neo4j-parallel-runtime; markaicode.com, 2025-04-03)
- **Interpretation:** The EDASES query shapes — traversing provenance chains, finding superseded artefacts, walking version history — are exactly local/global traversals that benefit from index-free adjacency. Performance should be strong for these access patterns. **Caveat:** the headline "1000x / 100x" figures are Neo4j's own marketing benchmarks; they are not validated against the EDASES artefact graph, whose size and shape are unknown. The architectural claim (O(k) local traversal, no join tables) is well established and is the relevant structural point.

### 8. Persistence and export

- **Observation:** Neo4j Community Edition includes `neo4j-admin` commands for **offline database backup** (dump) and **restore of a database dump**, plus a **consistency checker**. (neo4j.com/docs/operations-manual/current/backup-restore)
- **Observation:** Neo4j **Enterprise Edition** adds **online** backup (hot backup), backup-chain aggregation, backup inspection, and copy-database. (ibid.)
- **Observation:** Graphs can be exported/serialised via the **APOC** plugin (community-supported procedures) to JSON, CSV, GraphML, and Cypher scripts, and imported via `LOAD CSV` / `cypher-shell`. (neo4j.com/docs; community examples) APOC is a plugin, not core, and its licensing/availability differs by edition.
- **Interpretation:** The graph is serialisable and restorable. Community Edition covers offline dump/restore (sufficient for versioned, backed-up artefact storage); online/hot backup requires Enterprise. Export to portable formats (Cypher/JSON/GraphML) is available via APOC, enabling the graph to be versioned in an external VCS or exchanged. **Assumption (not verified):** round-tripping a large graph through APOC export may be slower/heavier than a native dump; native dump/restore is the recommended path for backup.

### 9. Maintenance and ecosystem

- **Observation:** Neo4j is actively maintained. The supported-versions knowledge base lists 2026.x releases (e.g. 2026.04.0, April 2026). (neo4j.com/developer/kb/neo4j-supported-versions, 2026-03-20)
- **Observation (licensing):** "Neo4j Community Edition is available as Open Source Software under the GPLv3 license. Neo4j Enterprise Edition is available under a commercial license." (g2.com, Neo4j Graph Database Pricing 2026; neo4j.com/licensing) The official licensing page lists "Neo4j Community Edition (GPL v3)" as a developer offering. (neo4j.com/licensing)
- **Observation (licensing history):** Since Neo4j 3.5, Enterprise Edition source is no longer published on GitHub; it moved to an open-core commercial model. Community remains GPLv3. (neo4j.com/open-core-and-neo4j, 2026-02-24)
- **Observation (cost):** Community Edition is free (no licensing fee). Managed cloud (AuraDB) has a free tier (AuraDB Free: ~50K nodes / 175K relationships) and paid tiers: AuraDB Professional ~$65/GB/month, Business Critical ~$146/GB/month; self-managed Enterprise is per-server commercial licensing (reported annual contracts in the tens-of-thousands-to-hundreds-of-thousands USD range). (toolradar.com, checkthat.ai, 2026 pricing aggregators)
- **Interpretation:** Neo4j is mature, actively developed, and has a large ecosystem. For EDASES, the **Community Edition (GPLv3, free)** covers the core property-graph, Cypher, and offline dump/restore needs. Enterprise features (hot backup, clustering/HA, fine-grained security, fabric/sharding) are only needed at scale or for strict operational/security requirements. **Note:** GPLv3 is a strong copyleft license — its implications for how EDASES distributes or links code are a separate legal question outside this report's scope.

### 10. Composition with a React frontend

- **Observation:** The **official `neo4j-driver`** (npm package `neo4j-driver`, Apache-2.0) is the supported JavaScript/Node.js client. Latest stable is 6.2.0 (released ~12 days before this writing, 2026); it supports Node 18+, browser/WebSocket connections, TypeScript types, and `executeQuery`. (npmjs.com/package/neo4j-driver; github.com/neo4j/neo4j-javascript-driver)
- **Observation:** A browser build of the driver connects to Neo4j over WebSockets and can be loaded directly via CDN (`<script src="https://unpkg.com/neo4j-driver">`). (neo4j-javascript-driver README)
- **Observation:** Neo4j publishes **Neo4j Visualization Library (NVL)** React wrappers (`@neo4j-nvl/react`) — ready-to-use React components (`BasicNvlWrapper`) that take `nodes`/`rels` props and reflect updates. (neo4j.com/docs/nvl/current/react-wrappers)
- **Observation:** Community tutorials demonstrate integrating `neo4j-driver` directly into React/Next.js apps (context state holding query results, pagination). (medium.com, "Integrating Neo4j with Your React App", 2024-07-26)
- **Interpretation:** Neo4j can serve as a backend for a React frontend via the official driver (browser or via a Node/BFF layer) and offers first-party React visualization components. **Security note (observation):** connecting a browser directly to Neo4j over WebSockets typically requires exposing the Bolt port and credentials to the client; production deployments normally route queries through a backend (BFF) that holds the driver and credentials. This is an architectural convention, not a Neo4j limitation.

## Findings

1. **Artefacts** map naturally to labelled nodes with properties; no fixed schema is required (schema-optional model).
2. **Versions** are modelled via the official entity–state pattern: an immutable entity node linked to per-version `State` nodes, with a `LATEST`/chain pointer. Branching is supported by multiple version relationships. This adds one intermediate node per version — a recognised, low-cost idiom, not excessive complexity.
3. **Evidence** links to artefacts/versions as nodes connected by typed, property-bearing relationships; no join table needed.
4. **Provenance** is a chain of typed relationships (`CREATED`, `DERIVED_FROM`, `BASED_ON`), traversable in one Cypher clause via variable-length patterns; no join tables.
5. **Supersession** is the cleanest case: a typed, directed `SUPERSEDES` relationship (optionally an event node on the edge for metadata), with chains traversable via `[:SUPERSEDES*]`.
6. **Schema complexity** remains low across all five concerns. The only recurring extra structure is the version `State` node + pointer, which Neo4j's own guide presents as simple and maintainable. Discipline required: use meaningful labels/relationship types, not a generic catch-all (an anti-pattern Neo4j explicitly warns against).
7. **Performance** for EDASES-style traversals (provenance chains, supersession discovery, version history) is structurally favoured by index-free adjacency (O(k) local traversal, no joins). Vendor benchmarks claim large speedups over SQL for multi-hop queries; these are indicative, not independently verified for the EDASES workload.
8. **Persistence/export**: Community Edition supports offline dump/restore and consistency checks; Enterprise adds hot backup. Graph export to JSON/CSV/GraphML/Cypher is available via the APOC plugin.
9. **Maintenance/licensing**: actively maintained (2026.x releases); Community Edition is GPLv3 (free), Enterprise is commercial (open-core). Cost scales from free (Community/self-host) to per-GB/month (AuraDB) or per-server (Enterprise).
10. **React composition**: official `neo4j-driver` (browser + Node) and first-party NVL React wrappers exist; a backend/BFF is the usual production topology to avoid exposing credentials.

**Overall:** Neo4j can represent artefacts, versions, evidence, provenance, and supersession as first-class graph constructs with low schema complexity. The modelling is natural for four of the five concerns and idiomatic (entity–state) for versions. The principal trade-offs are: (a) version history requires the entity–state intermediate-node idiom and pointer maintenance; (b) hot backup and clustering need Enterprise; (c) GPLv3 licensing of Community Edition carries copyleft implications to be assessed separately; (d) performance claims beyond the structural O(k) argument are vendor benchmarks not validated for EDASES.

## Rejected options

- **Storing versions as node properties only (e.g. a `version` integer on the artefact node).** Rejected because it overwrites history — it cannot retain multiple coexisting versions or support provenance/evidence per version. The entity–state pattern (separate version nodes) is preferred and is the official recommendation.
- **Modelling everything as a single generic `Node` label with a `type` property.** Rejected: Neo4j's own guidance states this defeats label-based indexing and forces full-graph scans. Meaningful labels are required for performance and clarity.
- **Using relationship properties alone for versioning (e.g. `validFrom`/`validTo` on every relationship, duplicating nodes).** Noted as the official "time-based" pattern's con: it duplicates node data and complicates updates; retained only as a supplementary option, not the primary model.
- **Direct browser-to-Neo4j WebSocket connection in production.** Rejected as a production topology (credential exposure); a backend/BFF holding the driver is the standard approach. This is an architectural convention, not a database limitation.

## Unknowns

- **EDASES workload shape and scale** are unknown, so the structural performance advantage (index-free adjacency) is established but the absolute latency/throughput for EDASES queries is not benchmarked.
- **GPLv3 implications** for how EDASES would distribute or link against Community Edition are a legal question not resolved here.
- **APOC availability/licensing per edition** and the cost of large-graph export round-trips are not verified.
- **Super-node risk** for any artefact that accumulates very many relationships (e.g. a root artefact with thousands of derived versions/evidence links) is a known Neo4j modelling concern whose relevance to EDASES is unquantified.
- Whether EDASES requires **temporal/bitemporal** versioning (point-in-time reconstruction of the whole artefact graph) — Neo4j supports it via modelling patterns but it is not a built-in feature and adds modelling overhead.

## Confidence

**Medium-High.**

- **High** for the modelling-capability claims (artefacts, evidence, provenance, supersession, and the entity–state versioning pattern): these are documented in Neo4j's own official data-modelling guide and are consistent across multiple independent sources.
- **High** for ecosystem/maintenance/licensing facts (official licensing page, supported-versions KB, npm driver metadata).
- **Medium** for performance: the architectural claim (index-free adjacency, O(k) traversal, no join tables) is well established, but the quantitative "1000x / 100x vs SQL" figures are Neo4j's own vendor benchmarks and are not independently verified for the EDASES artefact graph.
- **Medium** for cost: figures are from 2026 third-party pricing aggregators and depend on deployment choice (Community self-host vs AuraDB vs Enterprise).

The core research question — *can Neo4j represent these five concerns naturally without excessive schema complexity?* — is answered with reasonable confidence: **yes**, with the version-history idiom being the only modest, well-documented addition to the schema.

## References

- Neo4j, "Versioning" (data modelling guide). https://neo4j.com/docs/getting-started/data-modeling/versioning/
- Neo4j, "Introduction to Neo4j" (GraphAcademy / Educative course material). https://www.educative.io/courses/graph-rag/introduction-to-neo4j
- Artem Khrenov, "Graph Database Patterns: Neo4j for Complex Relationship Modeling", Medium, 2026-03-08. https://medium.com/@artemkhrenov/graph-database-patterns-neo4j-for-complex-relationship-modeling-f2281567aada
- Neo4j, "Property graph model" (O'Reilly Neo4j Graph Data Modelling). https://learning.oreilly.com/library/view/neo4j-graph-data/9781784393441/ch01s02.html
- Neo4j, "What is data lineage?" blog, 2025-03-06. https://neo4j.com/blog/graph-database/what-is-data-lineage/
- Neo4j, Agent Memory — "Graph-Native Memory Architecture". https://neo4j.com/labs/agent-memory/explanation/graph-architecture/
- David Allen, "Graph Modeling: All About Super Nodes", Neo4j Developer Blog, 2020-10-23. https://medium.com/neo4j/graph-modeling-all-about-super-nodes-d6ad7e11015b
- Neo4j, "Neo4j Graph Database" product page. https://neo4j.com/product/neo4j-graph-database/
- Neo4j, "Cypher Parallel Runtime" developer blog. https://neo4j.com/blog/developer/speed-up-queries-neo4j-parallel-runtime/
- Markaicode, "Node.js 22.x + Neo4j 6: Solving Billion-Node Graph Traversal Performance Issues", 2025-04-03. https://markaicode.com/nodejs-22-neo4j-billion-node-performance
- Ken Wagatsuma, "Index-free Adjacency in Graph Databases", 2021-09-24. https://kenwagatsuma.com/blog/neo4j-index-free-adjacency-in-graph
- Inferensys, "Index-Free Adjacency" glossary. https://inferensys.com/glossary/enterprise-knowledge-graphs/graph-query-optimization/index-free-adjacency
- Neo4j, "Backup and restore" (Operations Manual). https://neo4j.com/docs/operations-manual/current/backup-restore/
- h-omer/neo4j-versioner-core (Apache-2.0 entity-state procedures). https://github.com/h-omer/neo4j-versioner-core
- Satyam Shree, "A Practical Guide to Temporal Versioning in Neo4j", dev.to, 2025-12-05.
- Neo4j, "Supported Versions" knowledge base, 2026-03-20. https://neo4j.com/developer/kb/neo4j-supported-versions
- Neo4j, "Open Core Licensing Model" FAQ, 2026-02-24. https://neo4j.com/open-core-and-neo4j/
- Neo4j, "Licensing" page. https://neo4j.com/licensing/
- G2, "Neo4j Graph Database Pricing 2026". https://www.g2.com/products/neo4j-graph-database/pricing
- Toolradar / checkthat.ai, "Neo4j Pricing 2026" aggregators.
- npm, `neo4j-driver` package (official JS driver, Apache-2.0). https://www.npmjs.com/package/neo4j-driver
- Neo4j, "Neo4j Visualization Library — React wrappers". https://neo4j.com/docs/nvl/current/react-wrappers
- Ali Alhaddad, "Integrating Neo4j with Your React App", Medium, 2024-07-26.
- Neo4j JavaScript Driver repository. https://github.com/neo4j/neo4j-javascript-driver
