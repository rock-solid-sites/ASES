# Knowledge index — experimental prototype

**Status:** read-only experiment on draft [ASES PR #61](https://github.com/rock-solid-sites/ASES/pull/61); tracked in ASES-19. **Not deployed, not an authenticated service, not yet an approved maintained implementation.**

## Where to read first

- [Design and Integration Proposal](../../docs/proposals/knowledge-index/Design%20and%20Integration%20Proposal.md) — why this exists, source ownership, relationship model, integration roadmap and architectural boundaries.
- [Final Review Checklist](../../docs/proposals/knowledge-index/Final%20Review%20Checklist.md) — independent review, required negative tests, findings format, and separate experimental-merge vs production-integration decisions.
- [Technical Reference](TECHNICAL.md) — exact component responsibilities, input/output schema, identity registry, parser, validation, search, graph views, visibility limitations, CI tests and operating contract.
- [Initial Phoenix Grove adversarial review](../../adversarial-reviews/knowledge-index/2026-11-19-phoenix-grove-review.md) — all three model reports received after a focused MiMo retry; concrete findings now have red–green regression tests; maintained-service security is still unreviewed.
- [Real Repository Test Record](../../docs/research/Knowledge%20Index%20Prototype%20-%20Real%20Repository%20Test%20Record%202026-11-19.md) — scope, evidence, exact runs and remaining gaps.
- [GitHub-rendered read-only graph preview](../../docs/research/knowledge-index/graph-preview.md) — navigable candidate relationships from the literature/ASES pilot.

## Component map

- `indexer.py`: read-only Markdown/JSONL ingestion, metadata relationships, validation, SQLite FTS5 and graph queries.
- `registry.py` + `identities.json`: explicitly reviewed IDs and former-path aliases for eight pilot documents; other IDs remain path-derived and provisional.
- `graph_view.py`: public-only JSON/Mermaid/offline HTML views. The HTML export is generated in CI but **not hosted**.
- `fixtures/records.jsonl` + `tests/test_indexer.py`: schema, provenance, identity, visibility, injection and real-document regression tests.
- [GitHub Actions workflow](../../.github/workflows/knowledge-index-prototype.yml): minimal read-only sparse checkout and tests; no retained artifacts.

## Verification and integration boundaries

The latest verified [red–green repair run 44585134777](https://github.com/rock-solid-sites/ASES/actions/runs/44585134777) passed **47/47 tests**, indexing **197 nodes and 311 *candidate* edges** with **86 diagnostics** from the selected ASES `docs/` tree and pilot assertions. Earlier 25-test and 194/303/84 figures remain historical baseline observations. Counts will change as documents are added; the [test record](../../docs/research/Knowledge%20Index%20Prototype%20-%20Real%20Repository%20Test%20Record%202026-11-19.md) pins its observations. No candidate edge is a validated scientific finding.

Do not import private archives, Work Notes or authenticated Projektor records into the public repository/CI. Visibility labels and the public projection are **not authorization controls**. No conversation archive or Projektor data is modified or required. Integration requires independent architecture, security, identity and maintained-realization reviews as specified in the proposal.

**Do not ask the operator to run commands.** Agents/CI own prototype execution and testing. The underlying Python/SQLite implementation is a disposable experiment, subject to the existing ASES implementation realization/assurance method before being retained as maintained software.


## Fresh independent review and verified follow-up (19 November 2026)

All three fresh Phoenix Grove models reviewed immutable pre-fix source `2c7bdb2a624b53e41f08bf23dffe496e19d7e6e0`: DeepSeek and MiMo found no material defects in their bounded source assignments; GLM identified a JSONL reserved-ID impersonation defect and malformed namespace acceptance. Both were reproduced in [failing run 44587686163](https://github.com/rock-solid-sites/ASES/actions/runs/44587686163), repaired and checked in [green run 44587792625](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625): **49/49 tests passed**. See the [full three-reviewer record and raw outputs](../../adversarial-reviews/knowledge-index/2026-11-19-postrepair-phoenix-grove-review.md).

This does **not** constitute model re-review of the last corrective diff, production security sign-off, or operator authorization to merge. PR #61 remains experimental and draft.
