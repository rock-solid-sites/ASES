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

# Cross-project knowledge index — real-source evidence and limits

## Verified source and executable proof

- Remote feature branch: `feature/knowledge-index-prototype-20261119` (draft PR #61).
- Verified revision: `f4d58fb970ff10fa04b8b70cd0bd34c6541fb692`.
- [Successful GitHub Actions run](https://github.com/rock-solid-sites/ASES/actions/runs/44571399972): **25/25 tests**, including tests against actual checked-out ASES documents, fixture adversarial cases, registry identity continuity, graph redaction and script integrity. Real-document tests did **not** skip in CI.
- Full selected `docs/` subtree, plus the explicit literature/design JSONL pilot: **194 nodes, 303 candidate edges, 84 diagnostics**. Includes research, methodology, requirements, architecture and standards. These are not corpus-wide counts for every repository root and not 303 verified semantic claims.
- Eight-document precision test: 8 nodes, 10 candidate edges and 12 diagnostics, reproducible from unchanged sources.
- The committed [GitHub-rendered Mermaid preview](knowledge-index/graph-preview.md) was regenerated from source and verified byte-for-byte by the remote workflow. Graph: 5 public nodes, 3 evidence-linked candidate edges. Offline interactive HTML/JSON projections were generated and tested, **not deployed**.
- CI used sparse checkout and uploaded **no retained artifacts**, so this did not consume artifact storage.

## Diagnostic breakdown and interpretation

| Class | Count | Meaning |
| --- | ---: | --- |
| unresolved_unverified | 71 | A name could not be resolved uniquely in the chosen indexed set; **not** proof the target is absent from the repository |
| outside_index_scope | 5 | A source filename/path exists in the available checkout but was excluded from the indexed set |
| unsupported_metadata | 7 | Legacy or unsupported metadata syntax; the importer quarantines uncertain relationships |
| malformed_frontmatter | 1 | Frontmatter delimiter/content cannot safely be parsed |
| **Total** | **84** | Diagnostic events, **not** 84 confirmed defects |

No source documents were rewritten, and uncertain relationships remain candidates.

## Mechanisms actually tested

- **Source separation:** EDASES research documents, methodology and other docs are read-only inputs. No conversation archive, Projektor or Work Notes schema, data or workflow was changed.
- **Identity:** reviewed `identities.json` pins eight selected documents. A rename plus simultaneous content/title edit preserves the ID when the registry path and alias are updated. Conflicting inline IDs, duplicate aliases, invalid alias types and duplicate node IDs are rejected. Other files still have provisional path-derived IDs.
- **Provenance and evidence:** explicit unambiguous frontmatter relations become candidate edges; JSONL assertions carry assessment and evidence refs. Unresolved and ambiguous names do not create guessed edges. Source content hashes are preserved; rebuilding unchanged input reproduces identical relational records.
- **Visibility:** JSONL edges default private unless explicitly public. Graph projections omit private nodes, private edges and edges whose evidence references are not present in the public set. Default graph query APIs use the same public-only filtering. Tests cover several private/public cross-boundary cases.
- **Viewer:** GitHub-rendered Mermaid for immediate read-only retrieval, plus deterministic generated offline interactive HTML with search, node focusing, source links and keyboard-accessible list. Malicious source titles/URLs are tested for HTML/Markdown escaping, script/URL containment and CSP hash correctness. There is no hosted service.
- **Failure behavior:** malformed syntax and unresolved names produce diagnostics; invalid schema relationships fail. A failed build preserves the prior SQLite projection through atomic replacement.

## What these results do NOT establish

- No authenticated multi-workspace access control, revocation correctness, protection against inference/timing side channels or safe publication of private archived material. The public-only graph is **not** a production authorization API.
- No validated semantic conclusion from the PNAS paper and no architectural promotion of experimental ASES research. Candidate edges do not establish causation or support for a whole system.
- Stable identifiers are not yet available for every indexed document; no automatic move detection or cross-repository identity authority.
- The prototype intentionally uses disposable Python/SQLite under the experimental exception. A maintained service requires the canonical realization/language/assurance gate.
- No live Projektor graph integration or independent graph server. Those require separate scope and permission decisions.

## Remaining actions

1. Review the 71 unresolved references against a wider source inventory and assign verified aliases where appropriate, retaining negative evidence for truly missing records.
2. Extend reviewed stable IDs to other repositories and source systems without assigning an independent authority to the index.
3. Select and test a maintained implementation, including real authentication/visibility, permission revocation, exported-view integrity and update/rebuild behavior.
4. If hosting a viewer becomes useful, handle deployment authorization separately. Until then the tracked Mermaid view is accessible directly in GitHub.

**Decision:** prototype demonstrated reusable provenance-linked indexing and read-only graph extraction over real ASES docs; cross-project secured service remains experimental and unapproved.

## Security review verification update (2026-11-19)

After independent Phoenix Grove review, negative tests were written for out-of-root imports and symlinks, unregistered or retired source identity reuse, malicious or malformed JSONL, metadata-derived public-edge spoofing, nonempty evidence types, FTS punctuation, limited YAML quote parsing, unsupported frontmatter, and hostile Markdown authority strings. The separate viewer/browser, authenticated ACL, and cross-project ownership requirements remain outside this experiment.

Reproducible CI checkpoints:
- [Run 44584279907](https://github.com/rock-solid-sites/ASES/actions/runs/44584279907): **red** — a source authority value could inject a standalone Markdown image link; two other new regression cases passed at the then-current source state.
- [Run 44584754767](https://github.com/rock-solid-sites/ASES/actions/runs/44584754767): **red** — four identity/visibility/source-registry boundary tests failed and a required-registry API was missing.
- [Run 44585007924](https://github.com/rock-solid-sites/ASES/actions/runs/44585007924): **green** — 47/47 unit tests passed, real-document import and graph preview regeneration succeeded. At that exact revision the docs corpus contained **197 nodes, 311 candidate edges, and 86 diagnostic events** (71 unresolved/unverified, 7 outside scope, 7 unsupported metadata, 1 malformed frontmatter).

The negative tests establish that the previously observed unsafe cases were reachable and the repaired implementation rejects or neutralizes those exact counterexamples. They do not establish a complete security proof. In particular, explicitly public JSONL remains subject to upstream source trust, and nonempty evidence references are not a determination of research truth. The index is a disposable cache; no private conversation archive was ingested or published.

Detailed case-to-code review: [Phoenix Grove Review Triage](../proposals/knowledge-index/Phoenix%20Grove%20Review%20Triage%202026-11-19.md). Technical behavior: [implementation contract](../../scripts/knowledge_index/TECHNICAL.md). Draft PR #61 remains unmerged pending a human decision on accepting the *experimental* baseline. Production integration remains unapproved.
