---
title: Knowledge Index - Experimental Pilot Charter and Handoff 2026-11-19
program: ASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/proposals/knowledge-index/Design and Integration Proposal.md
  - docs/proposals/knowledge-index/Final Review Checklist.md
related_documents:
  - scripts/knowledge_index/TECHNICAL.md
  - docs/research/Knowledge Index Prototype - Real Repository Test Record 2026-11-19.md
last_updated: 2026-11-19
---

# Knowledge index — accepted scope for an experimental pilot

## Disposition and ownership

The experimental prototype from [ASES PR #61](https://github.com/rock-solid-sites/ASES/pull/61) is suitable to retain as a **research pilot** after its source-pinned Phoenix Grove reviews and reproducible red→green tests. This is permission to *experiment with the approach*, **not** adoption of the implementation, a new required workflow, approval of a hosted service or elevation of research findings to methodology.

The technical record is in this ASES GitHub repository. Human decisions and evaluation progress belong to Projektor **ASES-19**. Agent execution and evidence collection for the retrieval benchmark belong to the **already-existing** Work Notes task **WNASES-16**. The empirical property-testing laboratory is a different pilot, [ASES PR #60](https://github.com/rock-solid-sites/ASES/pull/60) and **WNASES-14**; its proposed *method promotion* is reviewed independently via **WNASES-10**. Do not create a second index-benchmark issue or a second testing laboratory.

## What was demonstrated before pilot acceptance

- GitHub Actions real-source and adversarial-regression suite: [49/49 tests passed](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625), including source-linked search/traversal, source identity, visibility, JSONL import hardening and graph preview determinism. The selected `docs/` and JSONL pilot contained 197 nodes, 311 **candidate** relationships and 86 diagnostics. These are indexed records, not 311 reviewed truths.
- Three fresh Phoenix Grove models independently inspected the pre-final-fix source: [review run](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355); DeepSeek and MiMo reported no material findings in their bounded scopes; GLM found two concrete problems. Both were reproduced in [red CI](https://github.com/rock-solid-sites/ASES/actions/runs/44587686163) and repaired in the green suite. The final corrective diff was **not** re-reviewed by those models.
- [Complete review and reproducibility record](../../../adversarial-reviews/knowledge-index/2026-11-19-postrepair-phoenix-grove-review.md); [implementation contract](../../../scripts/knowledge_index/TECHNICAL.md). CI retains no uploaded Actions artifacts.

The existing method for differentiating evidence from inference remains authoritative; the knowledge index has no independent policy authority.

## Next pilot: property-testing research retrieval

Use the existing public research in ASES and linked public source-controlled experiments as **the first real corpus**. Work Notes **WNASES-16** is the execution contract and already specifies the initial sources: ASES PRs #58, #59 and #60; HMS PRs #20, #21 and #23; Trip'n PR #30; plus the index prototype. The property-testing introduction under the experimental testing lab is the narrative entry point. The knowledge-index experiment must remain distinct from the underlying assurance-method evaluation.

**Minimum experiment:**

1. Freeze a manifest of exact `owner/repo/SHA/path` for the permitted public source documents. Draft branches are not equivalent to `main`, and changed URLs must not be silently normalized to newer versions.
2. Establish **15–20 questions and reference answers independently of the index**, spanning true source evidence, deliberately absent results, negative controls, experimental candidate vs deployed implementation, rejected oracle, conflicting review findings and reproducible test/version claims.
3. Answer each question twice against the same frozen source set: using the experimental index and ordinary repository search. Record correct sources, wrong/missing links, misleading relationships, unsupported status/authority promotions, retrieval time and incremental update cost **only where observed**.
4. Preserve at least one minimal reproducible miss, false connection or identity failure *if found*. A negative result is a legitimate outcome; do not invent a defect to make the pilot look useful.
5. Record a concise **measured** comparison, false positive/negative analysis, maintenance/operating assumptions, and decision to **retain, revise or discard**. Commit source-pinned experiment and transferable lesson to ASES testing/research; Work Notes owns granular execution checkpoints; Projektor ASES-19 owns the go/no-go decision.

**Stop condition:** once the bounded evaluation gives enough evidence to decide whether the index adds useful retrieval value relative to simple search, stop expanding it by default. Even a failed or discarded implementation must yield a reusable lesson and minimal counterexample where available.

## Explicit exclusions

- No production deployment, always-on daemon or service, automatic ASES/Engine dependency, promotion to a canonical methodology, or changes to active skills.
- No private raw conversation archival material, private graph metadata, authenticated Projektor/Work Notes connectors, or cross-tenant access. An `is_public` label is not a permission system.
- No autonomous mutations to source files, Projektor issue graph, Work Notes task state beyond planned checkpoints, property-testing PR #60, or project-owned HMS/Trip'n test implementations.
- No compulsory full-corpus ID migration, 71 unresolved diagnostic reference repairs, or speculative graph infrastructure as a prerequisite to this bounded retrieval pilot.
- No artificial requirement to make the implementation permanent. Prototype scripts, SQLite projections and the experimental graph may be replaced or discarded.

## Routing and lifecycle

- **GitHub ASES**: executable prototype, stable test and fixtures, source-linked experimental records, review findings and transferable lessons. Experimental work stays labeled; code paths under `scripts/knowledge_index/` are not production entrypoints.
- **Projektor ASES-19**: track *pilot objective, evidence links, decision and status*. Keep open while the benchmark runs; do not close as a production integration. ASES-18 continues separate distributed-systems literature research.
- **Work Notes WNASES-16**: sole bounded retrieval-benchmark work packet; no duplicate issue. WNASES-14 (testing lab) and WNASES-10 (independent method review) retain separate responsibilities.
- **GitHub ASES PR #60**: property-testing lab source and experiments, managed in its own thread; do not merge or modify it as a side effect of this closeout.
- **Chat archive/CHATARCH-3 and Projektor graph/PJDEV-9**: independent systems, no new adapter or source ingestion implied.

**Pilot success** requires measured evidence of whether the index improves source-grounded retrieval, including the cost of errors and maintenance, not just passing importer tests. It is acceptable to stop with a negative finding and keep only the learned method.

## Session handoff

At the next dedicated session, open **WNASES-16**, this charter and the pinned ASES research/test sources. Start with source manifest and reference question set. Do **not** reconstruct this chat's timeline, rerun already-completed Phoenix Grove reviews, redownload the whole chat archive or restart the prototype build. The technical files and exact CI/review evidence are already tracked remotely.

**Decision B — maintained cross-project service or production integration:** explicitly **not approved**. If a later evaluation supports it, plan a separate assurance, permissions and realization review.
