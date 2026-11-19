---
title: Knowledge Index Prototype - Technical Reference
program: ASES
layer: Implementation
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Cross-Project Knowledge Index - Minimal Schema and Integration Boundaries.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
related_documents:
  - docs/research/Knowledge Index Prototype - Real Repository Test Record 2026-11-19.md
  - docs/proposals/knowledge-index/Design and Integration Proposal.md
last_updated: 2026-11-19
---

# Knowledge index prototype: implementation contract and review map

**Scope:** the executable, disposable prototype under `scripts/knowledge_index/` in draft [PR #61](https://github.com/rock-solid-sites/ASES/pull/61). This document describes what that code **currently does**. The proposed system and decisions still needed before integration are separately documented in [the integration proposal](../../docs/proposals/knowledge-index/Design%20and%20Integration%20Proposal.md). Do not confuse a passing prototype with an approved maintained service.

## Architectural purpose and authority

This component is a **read-only, derived knowledge projection** across independently owned sources. Git repositories own technical documents and evidence; Projektor owns human planning/issues; Work Notes owns agent work tracking; conversation archives own historical originals and their reconciliation. The index owns only normalized references, candidate relationships, diagnostics and rebuildable views. No source mutations, project-management writes, archive processing or semantic promotion are permitted.

**Abstraction boundary:** EDASES develops research, ASES develops methodology and the Execution Engine implements it. Reading experimental research into a graph must not change its authority. A graph edge marked `supports` is not automatically a verified guarantee, and a candidate edge is not a methodology decision.

## File map: review each component against its contract

| Component | Path | Implemented behavior / responsibility |
| --- | --- | --- |
| Importer, validators, local store | `indexer.py` | Read Markdown/JSONL, limited YAML metadata, unambiguous reference matching, validation, SQLite FTS5/edges, atomic rebuild and query functions |
| Stable identity registry reader | `registry.py` | Parse checked-in registry; reject duplicate IDs, alias collisions and malformed alias values |
| Reviewed identity data | `identities.json` | Pins IDs of eight pilot ASES documents; explicit current path and optional previous path aliases |
| Public derived graph exporters | `graph_view.py` | Filter nodes/edges/evidence; render bounded Mermaid view, self-contained offline HTML, public JSON projection |
| Initial research link assertions | `../../docs/research/knowledge-index/pilot-2026-11-19.jsonl` | Three concept/source nodes and three explicitly labeled candidate edges with evidence references; no research finding promoted |
| GitHub-readable graph | `../../docs/research/knowledge-index/graph-preview.md` | Checked-in, source-linked public Mermaid subgraph; CI regenerates and checks exact content |
| Test suite + fixtures | `tests/test_indexer.py`, `fixtures/records.jsonl` | Controlled counterexamples plus tests requiring checkout of real ASES documents |
| Remote test workflow | `../../.github/workflows/knowledge-index-prototype.yml` | Sparse checkout of docs and prototype; no artifact upload; test, rebuild, traverse, classify and verify preview |
| Source evidence summary | `../../docs/research/Knowledge Index Prototype - Real Repository Test Record 2026-11-19.md` | Published test results and the specific unverified surfaces |

The relative paths above are from `scripts/knowledge_index/`.

## Data flow (current implementation)

```text
Canonical Markdown + explicitly reviewed JSONL + identities.json
                      |
                      v
  limited metadata parser + source identity resolution
                      |
                      v
  collect nodes + explicit/metadata-derived candidate edges
                      |
                      v
  validate IDs, endpoints, relation vocabulary and visibility
                      |
                      v
        atomic rebuild of disposable SQLite
         /               |                  \
   FTS5 search     edge traversal      public-only projection
                                             |
                              JSON / Mermaid / offline HTML
                                             |
                            GitHub preview and CI job summary
```

**Input authority:** the importer reads a checkout but never writes to it. `include_paths` selects Markdown and JSONL files, and `source_records()` collects records. A limited metadata parser accepts simple scalar and one-level list YAML; unsupported nested, legacy or malformed metadata produces diagnostic warnings, not guessed relationships. Filenames, exact titles and explicit aliases resolve only when unique. Unresolved or ambiguous references do not create edges.

**Identity:** `knowledge_id` in document metadata, when present, may supply an explicit ID. Otherwise a matching entry in `identities.json` supplies the stable ID. A conflict fails. Remaining documents fall back to `github:rock-solid-sites/ASES:doc:<repo-relative-path>`, which is **provisional** and changes upon a move. A reviewed registry update with a current path and old-path aliases preserves identity through moves and text changes; it is not automatic rename detection.

**Provenance:** source records contain title, kind, canonical source URL, `source_system`, visibility, content, authority when known, and a SHA-256 **content digest** in `source_revision`. That digest is not a Git commit ID and does not by itself provide an immutable Git permalink. Links currently target `main`, so draft-branch-only documents may not resolve through that link until merged. Explicit JSONL edges contain stable IDs, relation, `evidence_refs`, assessment, review status and explanation; generated metadata edges cite the source document. Treat all existing graph edges as candidates even when the underlying metadata is explicit.

**Validation:** `validate()` rejects duplicate/missing IDs, missing required node fields, invalid kinds, unsupported relation/status/assessment/visibility, absent endpoints and public edges pointing at private endpoints. The prototype does **not** yet enforce all semantic constraints anticipated by the proposed schema (e.g. citation validity/required nonempty evidence, cycle and abstraction-order checks).

**Projection:** a disposable SQLite database stores nodes, typed edges and an FTS5 virtual table. `build()` creates a temporary database then atomically replaces its destination after successful validation/inserts. Failures preserve the previous database. Identical inputs produce equivalent relational content on repeated builds; cross-environment byte-identical database files are **not** promised. The database is a cache, never a canonical record. External full-text search queries are for trusted local use only and must not be exposed as an unauthenticated API.

## Visibility and security contract: crucial limitations

The current repository is public, and the selected GitHub Actions test sets the default visibility of its checked-out documentation to `public`. In other contexts, importer default visibility is `private`. These are *labels*, not verified permission grants.

- JSONL edges without explicit visibility default to `private`. Metadata-derived edges may be public only when both source and target are marked public.
- `public_projection()` emits public nodes, public edges connecting public endpoints, and only edges whose **every** evidence ID is included in that public node set. Default `graph()` and `graph_details()` use that projection.
- An explicit trusted local `include_private=True` code path exists; **never wrap it in a remote interface**. No identity verification, revocation, tenancy or dynamic permission recheck exists.
- The offline HTML graph includes only the public projection; source title text is assigned through DOM text APIs, JSON embedded in the page escapes `<`, `>` and `&`, and the inline viewer script is pinned with a content-security-policy hash. URLs are restricted to basic HTTPS syntax. These are scoped containment defenses, **not** a complete hosted-viewer security review.
- The HTML graph has search, focus, reset, zoom, clickable SVG nodes and an accessible text-list fallback; it is **generated but not deployed**. The Markdown/Mermaid preview is the current accessible remote representation.
- Do not ingest private archived conversations or restricted connector data into a public Git checkout or the public CI export. A public/private flag alone cannot protect them.

## Executable entrypoints and behavior

For a contributor/CI agent working in an ASES checkout, `indexer.py` accepts positional **source root** and **SQLite destination**, plus optional `--namespace`, `--default-visibility`, repeatable `--include` paths, `--search`, `--graph` and `--diagnostics`. The indexing functions (`source_records`, `validate`, `build`, `query`, `graph`, `graph_details`, `summarize_diagnostics`) are callable for tests.

`graph_view.py` exports `public_projection`, `neighborhood`, `render_mermaid`, `render_html`, and `write_views`. The generated views are derived output: **do not edit them as a substitute for editing sources**. The checked-in pilot Mermaid preview is deliberately an exception for remote read-only discoverability, mechanically compared with regenerated content in CI.

The GitHub Actions workflow on `feature/knowledge-index-prototype-20261119` is currently bound to that branch, with minimal contents-read permissions and a short timeout. It checks out `docs/` and the prototype, runs Python standard-library unit tests, traverses selected real documents and the broader `docs/` subtree, checks the committed preview, prints diagnostic classes, and generates a Mermaid view in the job summary. No persistent Actions artifact, deployment or production write is performed. The workflow must be adapted when integrating, not simply copied with a permanent feature-branch filter.

## Test evidence and interpretation

[Run 44571399972](https://github.com/rock-solid-sites/ASES/actions/runs/44571399972) passed **25/25 tests**; later [run 44571598117](https://github.com/rock-solid-sites/ASES/actions/runs/44571598117) also succeeded after documentation changes. The tested `docs/` sweep contained **194 nodes, 303 candidate edges, 84 diagnostic events**: 71 unresolved/unverified, five outside indexed scope, seven unsupported metadata and one malformed frontmatter. These are **not** 84 proven corrupt source files or 303 reviewed truths. The CI-only eight-document subset additionally exercised exact links, authority metadata, search, deterministic rebuild and graph candidate status.

The tests cover identity changes and collisions, malformed/unresolved metadata, duplicate/missing IDs and endpoints, public/private edge behavior, hidden evidence references, unsafe HTML/URLs, CSP script hash integrity, atomic-rebuild failure and source-linked graph generation.

**Review-packet verification:** [GitHub Actions run 44574342042](https://github.com/rock-solid-sites/ASES/actions/runs/44574342042) passed **28/28 tests**, including checks that the proposal, final-review checklist and technical reference have valid classification metadata, no broken relative links, and do not claim review or production approval. The larger docs-inclusive snapshot then contained **196 nodes, 311 candidate edges and 86 diagnostics** (71 unresolved/unverified, 7 outside the index scope, 7 unsupported metadata, 1 malformed frontmatter). Previous 194/303/84 measurements above are historical, commit-scoped observations. They **do not** establish cross-repository identity continuity, semantic accuracy, complete YAML support, real credentials, multi-tenant authorization, permission revocation, time-of-check/time-of-use safety, concurrency, incremental ingest or production accessibility.

## Failure-handling and audit rules

- Unsupported metadata: emit a diagnostic, quarantine uncertain relationships and keep the source record searchable.
- Unresolved/ambiguous target: emit a diagnostic, do not choose a likely destination based on string similarity.
- Registry mismatch or duplicate ID: fail the build, keep the previous database intact.
- Public edge to nonpublic endpoint: fail validation; private evidence missing from the public projection: suppress the edge.
- Changes to generated preview: CI fails when the preview diverges; update source assertions first.
- Reviewer findings must identify a source path, exact violated invariant, reproduction and untested surface. Reviewer agreement alone does not constitute verification.

## Review questions before integration

1. Does every imported source have a stable identity independent of mutable file path and a verifiable source/version reference?
2. Does a real source-permission check, not an asserted visibility label, control **node existence, edge existence, evidence, search and exports**?
3. Does the system reject unsupported YAML/JSONL without dropping valid information silently, and can it distinguish absent documents from records outside the index scope?
4. Can each candidate edge be traced to an authoritative source, assessed by a reviewer, challenged or retracted without altering source history?
5. Does the design avoid duplicating CHATARCH-3, PJDEV-9 and Projektor's human planning ownership?
6. Is the maintained implementation selected via the ASES [realization and assurance method](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md), rather than treating this disposable Python prototype as automatically approved?
7. Do CI, accessibility and threat-model tests demonstrate the required guarantees in the **actual integration environment**?

**Disposition:** experimentally verified prototype; **not approved for production integration**. The corresponding [proposal and review gates](../../docs/proposals/knowledge-index/Design%20and%20Integration%20Proposal.md) govern next steps.
