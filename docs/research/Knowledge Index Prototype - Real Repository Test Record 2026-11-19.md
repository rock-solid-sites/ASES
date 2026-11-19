---
title: Knowledge Index Prototype - Real Repository Test Record 2026-11-19
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Cross-Project Knowledge Index - Minimal Schema and Integration Boundaries.md
related_documents:
  - docs/research/LLM Agents and Distributed Systems - Research Topic.md
last_updated: 2026-11-19
---

# Real repository knowledge-index prototype test

## Verified execution
- Remote branch: feature/knowledge-index-prototype-20261119.
- Last green revision: e6081aa6b96e9a64a487652236deb220979774aa.
- GitHub Actions run: https://github.com/rock-solid-sites/ASES/actions/runs/44567135467 (success).
- Fifteen executable tests passed without skips on GitHub Actions, including two that read eight actual ASES Markdown documents from the repository checkout. Fixture-only local runs do not count as real-document tests.
- Independent broader traversal over the checked-out docs/research and docs/standards directories, plus an explicit three-concept/source candidate graph, produced **146 nodes, 247 candidate edges and 89 warnings**. Count includes the additional JSONL pilot nodes. No CI artifacts were uploaded or retained.
- In the bounded eight-document test: **8 nodes, 10 candidate edges, 12 warnings**. Search and source-linked edge traversal succeeded. Rebuilding from unchanged inputs reproduced identical indexed node/edge records.

## What is established
1. EDASES-style Markdown frontmatter can be read from real source files without modifying those files.
2. Unambiguous, explicit metadata references can create *candidate* graph edges. Citation and design relations can also be declared explicitly in reviewable JSONL.
3. Full-text lookup and provenance-aware graph queries run against derived SQLite. Default graph queries filter out non-public endpoints.
4. Malformed metadata and unresolved names are surfaced diagnostically rather than silently treated as verified links.
5. Duplicate IDs, missing endpoints and a public edge to a private node are rejected. Rebuilds use atomic output replacement.
6. An additional regression test intentionally failed when it made a node private without lowering the edge's visibility; this exposed **correct validator behavior**, and the test setup was corrected. Final run is green.

## Warning interpretation
Eighty-nine warnings are not eighty-nine confirmed source defects. They include unresolved names when intentionally indexing only two documentation subtrees, references to other source paths, legacy Markdown-bullet-style frontmatter, unsupported nested metadata and a record with unterminated frontmatter. Examples: Canonical Terminology, Paseo Role Capability Matrix, combined-verify-server-retrospective. Nothing was auto-rewritten, and unreviewed source assertions remain marked candidate. A subsequent corpus-wide diagnostic pass should classify warnings into true metadata defects, missing-scope references, ambiguous aliases, and intentionally external references.

## Not established
- No authenticated authorization or cross-workspace confidentiality guarantee; default public/private filtering is not a permission service.
- No stable ID for legacy documents that lack an explicit knowledge_id (file moves can change fallback IDs).
- No graph UI or production query API, no live Projektor, Work Notes, or conversation-archive connectors.
- No claim that the 247 edges are semantically correct, that the PNAS paper validates any ASES design, or that the prototype is production-ready.
- Python code is a disposable test under the short-experiment exception; maintained multi-project implementation needs a separate assurance/language selection decision.

## Next test frontier
- Classify the 89 diagnostics against a broader source inventory and add explicit alias resolution with provenance.
- Test canonical ID continuity under real file moves and contradictory metadata.
- Define public/internal/private derived projections and prove permission non-disclosure independently of this local CLI.
- Build a read-only graph projection/view from documented candidate links; keep Projektor's existing issue/wiki graph separate.
- Extend the metadata extraction pilot to relevant ASES methodology, design and evidence docs, then benchmark incremental indexing.
