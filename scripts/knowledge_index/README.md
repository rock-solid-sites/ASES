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
