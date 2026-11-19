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

**Validation:** `validate()` rejects duplicate/missing IDs, missing required node fields, invalid kinds, unsupported relation/status/assessment/visibility, absent endpoints and public edges pointing at private endpoints. Validation now requires evidence references to be nonempty lists of nonempty string IDs and checks required node/edge field types. It **does not** independently verify evidence provenance, relationship truth, cycle and abstraction-order semantics, or source permission grants.

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

- Unsupported metadata: emit a diagnostic and quarantine uncertain relationships; index the source **private by default** even when the caller sets a public default. If malformed frontmatter contains an explicit `knowledge_id`, reject the build to avoid silent identity reassignment.
- Unresolved/ambiguous target: emit a diagnostic, do not choose a likely destination based on string similarity.
- Registry mismatch or duplicate ID: fail the build, keep the previous database intact.
- Public edge to nonpublic endpoint: fail validation; private evidence missing from the public projection: suppress the edge.
- Changes to generated preview: CI fails when the preview diverges; update source assertions first.
- Reviewer findings must identify a source path, exact violated invariant, reproduction and untested surface. Reviewer agreement alone does not constitute verification.

## Post-review repair contract and verified tests

The first frozen Phoenix Grove reviews were performed against commit `bef2782144ca5553b1632c6f0747169d5933e1ff`; later fixes were **not** model-reviewed. The [red–green repair record](../../adversarial-reviews/knowledge-index/2026-11-19-phoenix-grove-review.md) lists exact failing controls, fixes, residual uncertainty, and [passing CI run 44585134777](https://github.com/rock-solid-sites/ASES/actions/runs/44585134777) (**47 tests**).

**Current implementation rules added after adversarial review:**

- Source include paths are bounded to the configured resolved root before reading; `..`, absolute escapes, and symlinks targeting outside the source root are rejected. Registry reads are also constrained to that root. This is not a credential/permission system.
- `identities.json` may be optional for disposable fixture work; real ASES CI explicitly supplies `--require-registry` or `require_registry=True`, causing a missing registry to fail. Registered identity IDs are reserved across partial-index builds, so an unregistered document cannot claim one when the registered owner is excluded. Retired path aliases resolve *references* but are not valid active source identities.
- The bounded YAML scalar parser removes only matched enclosing quote pairs; a trailing apostrophe is not silently discarded. Unsupported frontmatter without an identity is still indexed but defaults private; malformed **identity-bearing** frontmatter fails. General YAML compliance remains out of scope.
- JSONL input must contain objects with valid string node IDs; importer-private fields (`_metadata`, `_path`, `_aliases`, `_derived_metadata`) are stripped before graph derivation. An explicitly authored `meta:` edge ID cannot impersonate an importer-generated edge. Its visibility remains private unless explicitly specified.
- Evidence references must be nonempty string IDs; this does not yet prove every external source exists or has passed review. Query input is interpreted as bounded literal lexical tokens, not raw SQLite FTS syntax; malformed punctuation returns an empty result rather than a parser crash.
- Public Markdown graph text escapes `authority` metadata including raw HTML, Markdown image notation and newlines. The independent HTML graph viewer uses its separate DOM rendering/CSP controls. Real browser-service security remains unverified.

**Observed scope:** the selected ASES `docs/` and literature pilot now index **197 nodes, 311 unreviewed candidate edges and 86 diagnostics**. These numbers include additional review documentation; they do not validate the semantic accuracy of the edges. The published Mermaid preview still matches source-generated output. No archive, Projektor or Work Notes data has been ingested or changed.

**Remaining gates:** stable IDs for all sources, independent review of the repair diff, a maintained realization selection, real source ACL/revocation and inference-leak tests for any authenticated multi-project connector, and separate authorization for hosting/deployment.

## Review questions before integration

1. Does every imported source have a stable identity independent of mutable file path and a verifiable source/version reference?
2. Does a real source-permission check, not an asserted visibility label, control **node existence, edge existence, evidence, search and exports**?
3. Does the system reject unsupported YAML/JSONL without dropping valid information silently, and can it distinguish absent documents from records outside the index scope?
4. Can each candidate edge be traced to an authoritative source, assessed by a reviewer, challenged or retracted without altering source history?
5. Does the design avoid duplicating CHATARCH-3, PJDEV-9 and Projektor's human planning ownership?
6. Is the maintained implementation selected via the ASES [realization and assurance method](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md), rather than treating this disposable Python prototype as automatically approved?
7. Do CI, accessibility and threat-model tests demonstrate the required guarantees in the **actual integration environment**?

**Disposition:** experimentally verified prototype; **not approved for production integration**. The corresponding [proposal and review gates](../../docs/proposals/knowledge-index/Design%20and%20Integration%20Proposal.md) govern next steps.


## Adversarial negative-test verification (2026-11-19)

The [Phoenix Grove triage and red–green record](../../docs/proposals/knowledge-index/Phoenix%20Grove%20Review%20Triage%202026-11-19.md) maps reviewer claims to reproducible cases. [GitHub Actions run 44585007924](https://github.com/rock-solid-sites/ASES/actions/runs/44585007924) passed **47/47 tests**, the real ASES documents traversal, and the checked-in Mermaid preview comparison. The docs-inclusive run observed **197 nodes, 311 candidate relationships, and 86 diagnostic events**. These numbers are tied to the cited run, not permanent corpus invariants.

Security/authority refinements from the review:

- Import paths and registry paths must resolve within the configured root. Out-of-root includes and symlinks are rejected before reading. Active registry paths, not retired aliases, are authoritative for identity attribution. A registry may be explicitly required by a caller; absent registries remain optional for the default disposable-fixture mode.
- JSONL-supplied internal parser/provenance fields are stripped; generated metadata links alone may inherit public visibility when both endpoints are public. An imported `meta:` ID does **not** make a JSONL edge public. Explicit `visibility: public` from an authorized JSONL source remains a trusted label, not a proof of access permission.
- Malformed or unsupported frontmatter is not interpreted as a public authority grant: identity-bearing unparseable metadata fails rather than silently allocating a substitute ID; other such source records are conservatively quarantined to private visibility. This is a fail-closed prototype behavior, not general YAML support.
- Invalid JSONL types and invalid/empty evidence IDs cause a controlled validation failure. Nonempty, well-typed references still require separate *semantic* and provenance review.
- FTS query input is interpreted as bounded literal word tokens to avoid permitting arbitrary FTS5 operator syntax; callers should not assume support for advanced full-text expressions. Rendered authority strings are neutralized for HTML tags, Markdown images, escapes and line breaks in generated Markdown. The separately generated offline HTML still requires contextual review before any hosting.
- No source ACL lookup, tenancy, revocation, real trust attestations, or privacy-safe publication of archived conversations was added. CI remains a **read-only disposable experiment**; passing does not approve a service.

The final review gate is still divided: **Decision A**, whether to accept an experimental baseline through PR #61, requires a human scope/merge decision; **Decision B**, a maintained cross-project index/graph service, remains unapproved.


## Fresh reviewer delta: registered JSONL IDs and namespace (19 November 2026)

A fresh [three-model Phoenix Grove review](../../adversarial-reviews/knowledge-index/2026-11-19-postrepair-phoenix-grove-review.md) found that previous stable-ID reservation checked Markdown metadata but not JSONL nodes in a partial index, allowing the identity of an excluded registered Markdown source to be impersonated. JSONL nodes now **cannot** use any ID registered to a source document, even if the registered source is not selected. The importer also validates the GitHub namespace with a constrained safe character pattern rather than checking only the prefix and slash count. Invalid namespace examples with embedded spaces are rejected; the no-slash example cited by GLM was already rejected before this change.

The targeted tests failed at [run 44587686163](https://github.com/rock-solid-sites/ASES/actions/runs/44587686163); after repair, [run 44587792625](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625) passed **49/49** tests, with real-document indexing and graph preview verification intact. All three reviewer jobs delivered reports, but **the last two fixes were tested rather than independently re-reviewed by the models**. Future cross-project namespace/provider formats require their own reviewed adapter; this strict rule applies to the current GitHub-only prototype.
