---
title: Knowledge Index - Final Integration Review Checklist
program: ASES
layer: Architecture
document_type: Research Protocol
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/proposals/knowledge-index/Design and Integration Proposal.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
related_documents:
  - scripts/knowledge_index/TECHNICAL.md
  - docs/research/Knowledge Index Prototype - Real Repository Test Record 2026-11-19.md
last_updated: 2026-11-19
---

# Knowledge index — independent review and decision record

This is a **pre-integration review protocol**, not a self-certified completion checklist. Its owner is **ASES-19**; the technical experiment is draft [ASES PR #61](https://github.com/rock-solid-sites/ASES/pull/61). Read the [proposed design](Design%20and%20Integration%20Proposal.md), [technical contracts](../../../scripts/knowledge_index/TECHNICAL.md), source code, fixtures and the real CI logs **before** filling in verdicts.

## Scope of approval

Reviewers must distinguish two independent decisions:

- **Decision A — Merge research/prototype material:** May this documented, explicitly experimental source, CI test and read-only public diagram enter ASES as a reproducible experiment without being presented as sanctioned production software?
- **Decision B — Integrate a maintained knowledge service:** Does the implementation and its deployment satisfy the stronger, cross-repository identity, privacy, authorization, update, availability and assurance guarantees? **Not demonstrated as of 2026-11-19.**

A pass on Decision A must not be interpreted as a pass on Decision B. Merging any research artifacts does not authorize a production launch, user-data indexing or archive writes.

## Evidence available before independent review

| Evidence | Artifact | Verified scope |
| --- | --- | --- |
| Source and diffs | [Draft PR #61](https://github.com/rock-solid-sites/ASES/pull/61) | Code, pilot JSONL, workflow and docs; branch not yet merged |
| Remote test run | [Actions 44571399972](https://github.com/rock-solid-sites/ASES/actions/runs/44571399972) | 25 tests passed on remote runner, including real ASES docs |
| Review-packet validation | [Actions 44574342042](https://github.com/rock-solid-sites/ASES/actions/runs/44574342042) | **28 tests passed**, including documentation metadata and all internal link checks; docs-inclusive snapshot: 196 nodes, 311 candidate edges, 86 diagnostics |
| Research measurements | [Test record](../../research/Knowledge%20Index%20Prototype%20-%20Real%20Repository%20Test%20Record%202026-11-19.md) | Selected `docs/`: 194 nodes, 303 **candidate** edges, 84 diagnostics |
| Public graph | [Graph preview](../../research/knowledge-index/graph-preview.md) | Five nodes, three candidate edges; CI checks regenerated Markdown |
| Component contracts | [Technical reference](../../../scripts/knowledge_index/TECHNICAL.md) | Interface semantics, tests, known limits, non-goals |
| Source-of-truth rules | [EDASES documentation standard](../../standards/Documentation%20Standard.md) | Authority, relationship, lifecycle, layer constraints |

## Review tasks with required negative tests

Record each task **PASS / FAIL / UNRESOLVED / NOT-APPLICABLE**, the commit or run tested, a minimal counterexample, and what was *not* tested. Do not infer completion from a checkmark or agent consensus.

### R1 — Source authority and correctness

- [ ] Verify that GitHub docs/research and methodology authority are preserved when interconnected. No experimental claims become canonical through graph traversal.
- [ ] Check that all graph edge types have precise direction and testable meanings. `supports` must not imply universal validation; `related_to` must not be silently presented as causal support.
- [ ] Audit candidate links in the PNAS paper/Resource Solver comparison for bibliographic correctness and absence of unwarranted performance claims.
- [ ] Confirm CHATARCH-3, PJDEV-9 and Work Notes remain independent owners; no duplicate archive indexing or implicit Work Notes/Projektor writes are introduced.
- [ ] Confirm root and other project conventions can be adapted rather than forcing EDASES frontmatter onto HMS or Trip'n.

### R2 — Stable identity and source provenance

- [ ] Validate ID collision behavior across repositories, projects, workspaces and aliases; include case and Unicode edge cases.
- [ ] Move/rename/edit a file and test continuity and old alias resolution; simulate a split/merge, deletion, replacement and ID re-use attempt.
- [ ] Resolve provisional path IDs and prove no old IDs are silently misattributed to new files.
- [ ] Require a source version suitable for audit (commit-pinned link or equivalent), not only `blob/main` and a content hash.
- [ ] Define how conflicting claims, supersession, retraction and stale evidence are represented without rewriting historical facts.

### R3 — Parser, relationship validation and fault tolerance

- [ ] Test valid and malformed YAML (nested structures, duplicate keys, embedded lists, quoting), JSONL duplicates and unsupported schema versions; inputs fail or warn **without invented links**.
- [ ] Reconcile the 84 diagnostics by verified category. The 71 unresolved/unverified references require research; do **not** mark them nonexistent merely because a subset search missed them.
- [ ] Test dependencies for cycles and methodology-layer violations where those constraints are applicable; classify `related_to` separately from dependency edges.
- [ ] Exercise incomplete source reads, corrupt index output, interrupted atomic replacement and simultaneous reindexing; protect the last verified projection.
- [ ] Measure rebuild time, memory and index size on more than the chosen `docs/` subset, then test low-cost incremental updates. No performance guarantees exist from the pilot counts alone.

### R4 — Security and isolation (blocking before a shared service)

- [ ] Derive visibility from actual authenticated, source-specific permissions, not user-controlled `visibility` labels or default-public environment settings.
- [ ] Demonstrate no leakage of private **node existence**, edge existence, evidence IDs, title, URL, neighboring topology, search match counts or timing signals.
- [ ] Test permission revocation, user/project switching, workspace isolation, deleted documents and stale cached projections.
- [ ] Deny unauthorized `include_private=True`, raw SQL/full-text access, file-system paths and arbitrary input URLs in every remote integration.
- [ ] Exercise malicious Markdown/frontmatter, JSONL, URL, metadata and graph label injection in the actual rendering environment (not just unit-output checks).
- [ ] Confirm public GitHub Actions and logs never receive private archive or connector records; no unintended artifacts, secrets or copied private databases.

### R5 — Graph and retrieval UX

- [ ] Verify public-only Mermaid preview matches generated content and all source links are appropriate for branch/version.
- [ ] Validate local neighborhood limits, search queries, keyboard operation, accessible source-list fallback, readable labels and mobile behavior.
- [ ] Confirm `candidate` vs `reviewed`, citation provenance, conflicts and uncertainty are visible to humans *and* machine consumers.
- [ ] For any proposed hosted UI, check actual browser CSP, external navigation, tenant scoping, authorization, caching and rendering security; the offline HTML test is insufficient.

### R6 — Integration topology and realization

- [ ] Verify the architecture introduces no dependency of research on implementation and no automatic redesign of Kernel-Zero, Work Units or Resource Solver.
- [ ] Evaluate reusing compatible existing indexes/graph viewers vs implementing a new service; quantify maintenance, Actions/storage and operating cost.
- [ ] Apply [Implementation Realization and Assurance Selection Method](../../methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md) before adopting a maintained language/runtime; the Python proof is disposable, not an approved final implementation.
- [ ] Test each proposed read-only connector independently on real permissions before any cross-project rollout; do not tie readiness to the conversation-archive reconciliation.
- [ ] Identify rollback and ownership for schema upgrades, changing identities, stale source data, connector failures and accidental overpublication.

## Severity and decision rules

**Blocker:** an authority violation, unpermitted write, private information disclosure, unverifiable source/identity mutation, or a critical invariant without a falsifying test. Blockers prohibit **Decision B** integration. A proof-of-concept may still be archived as experimental evidence only if the defect is visibly documented and cannot affect production.

**Major:** unsupported or ambiguous source mapping producing misleading assertions, silent data loss, unbounded resource consumption or serious usability barriers. Resolve or explicitly scope out before the affected feature is accepted.

**Minor:** labels, layout or documentation refinements not affecting truth, security or identity. These may be tracked as follow-up work.

For each finding preserve: `id`, `severity`, `source file/line`, `observed result`, `reproduction`, `expected invariant`, `evidence`, `certainty`, `not tested`, `suggested cheapest falsifying test`, and `status`. The repo owns technical findings; Projektor tracks the human-level outcome and cross-project dependency.

## Required independent review record

| Field | Record |
| --- | --- |
| Review date, model/reviewer, independent execution context | NOT YET RECORDED |
| Reviewed PR head SHA and relevant source revisions | NOT YET RECORDED |
| Architecture/source-authority verdict | UNREVIEWED |
| Parser/identity/provenance verdict | UNREVIEWED |
| Security/permission verdict | UNREVIEWED |
| Retrieval/accessibility verdict | UNREVIEWED |
| Language/realization verdict | UNREVIEWED |
| Unresolved and untested areas | Must be itemized |
| Decision A: merge research/prototype | PENDING |
| Decision B: production integration | **NOT APPROVED** |
| Blocking findings and retests | PENDING |
| Operator approval and scope | PENDING |

An automated reviewer must not fill the operator-approval field. An independent reviewer may recommend one of **approve experimental materials**, **conditional integration design only**, **fix and retest**, or **reject/rearchitect**.

## Present disposition

The real-repository prototype is a credible **review candidate**: documented code, CI, typed source links, identity registry and generated graph preview exist. The public-source scope was tested; real secured multi-project integration was not. Retain the draft PR and use this checklist as the input to the final review. No conclusion about production integration is justified until the unresolved gates have explicit evidence.
