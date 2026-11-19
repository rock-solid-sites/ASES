# Knowledge index — experimental, reproducible prototype

**Status:** experimental read-only proof of concept, **not** an authenticated service, production library or stable schema. Research issue: ASES-19. First pilot: ASES-18.

## Tests

From an ASES checkout, GitHub Actions runs: PYTHONPATH=scripts/knowledge_index python -m unittest discover -s scripts/knowledge_index/tests -v

The two RealRepositoryTests use **eight actual repository documents** (full source content, not copied fixture extracts). They must run without skips on CI. Other tests use controlled fixture records.

The importer recognizes a limited subset of EDASES YAML frontmatter (scalar fields, flat dash/star lists, empty lists). It preserves source hashes and titles, produces *candidate* edges only from explicit unambiguous metadata, and reports unresolved/ambiguous or malformed metadata rather than fabricating links.

Database build uses an atomic replacement of a disposable SQLite file. Records are in Git-tracked Markdown and JSONL, not the generated index. Cross-project adapters and authorization are not implemented.

## Explicit limitations

- Document IDs fall back to repo-relative paths; only an explicit knowledge_id survives renaming.
- Many legacy research files have no metadata or have nonstandard/malformed frontmatter. They are indexed as source documents but no relationship is inferred; diagnostics are expected. **Do not auto-repair canonical documents.**
- The source URL is for the tracked GitHub repository main branch, not a source-version immutable permalink; SHA-256 content digest is stored separately.
- This prototype's include_private Python API can expose all indexed records. It is **not** an access control system. Never serve or publish its private index or expose that API to untrusted users. The CLI only returns public records.
- This Python/SQLite implementation is for a short disposable experiment. A maintained multi-project system must pass the language/assurance selection process in docs/methodology/Implementation Realization and Assurance Selection Method.md.
- No live Projektor, Work Notes or chat archive writes. The archive is an independent ingestion boundary.

## Acceptance evidence

CI results and source commit on the feature branch are the evidence. Unit tests alone do not demonstrate shared-service security, complete repository coverage, semantic truth, or the desired graph UI. Future work: schema validation, full corpus statistics, typed metadata edge coverage, stable identity registry, permission-aware adapters, and read-only graph view.


## Extended real-document run (19 November 2026)

The remote CI workflow now traverses **all Markdown under docs/** (research, methodology, requirements, architecture, standards and related documentation), not only the original two subtrees. The last measured corpus sweep at revision d1a0d272 indexed **194 nodes and 303 candidate relationships**, with **84 diagnostic warnings**: 1 malformed frontmatter, 7 unsupported-metadata cases, 5 references outside the selected index, and 71 unresolved/unverified references. These numbers are from the checked-out docs tree, not a full inventory of every repository root.

A selected public research graph is checked into [the GitHub-rendered preview](../../docs/research/knowledge-index/graph-preview.md). CI independently regenerates that graph from Markdown/JSONL and compares it byte-for-byte with the checked-in file. CI also generates offline HTML/JSON views for testing and writes the Mermaid graph to the GitHub Actions job summary; there is no retained Actions artifact. HTML is **not deployed or hosted**.

The identity registry in identities.json explicitly pins eight selected document IDs. Rename/move requires updating the registry's current path and retained aliases; the ID remains unchanged even when text/title changes. Other sources still use provisional path-derived IDs. Duplicate mappings and contradictory IDs fail closed.

Default graph queries and exports use the same public-only projection and omit hidden nodes, private edges and edges whose evidence references are inaccessible. The offline HTML escapes script-bound JSON data and pins its inline JavaScript with a CSP hash. **These are containment tests, not proof of service-level access control.**

The index remains a **separate consumer** of source material. No chat archive, Projektor or Work Notes integrations were changed.

## Remaining gates before promotion

- Apply the canonical realization/language/assurance method to select a maintained implementation; Python here is a disposable experiment.
- Extend stable IDs and alias migration to every source type, and reconcile provisional path IDs.
- Review unresolved references against a comprehensive source manifest; do not auto-promote lexical similarity to evidence.
- Build permission-aware connectors and test existence, relationship, inference and revocation leakage; this prototype is **not** an authorization API.
- Obtain separate approval for any hosted/deployed graph service. GitHub-rendered Mermaid is the read-only remote interface for now.
