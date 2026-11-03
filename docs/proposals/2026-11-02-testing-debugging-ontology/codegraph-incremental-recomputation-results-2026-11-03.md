---
title: CodeGraph Incremental Recomputation — Observations and Decision Record
program: ASES / EDASES
document_type: Research Experiment Result
status: Experimental evidence; production acceptance not granted
authority: Research; not canonical policy
date: 2026-11-03
preregistration: docs/proposals/2026-11-02-testing-debugging-ontology/codegraph-incremental-recomputation-preregistration-2026-11-03.md
project_repository: rock-solid-sites/ases-plugins
project_branch: experiment/cgrmcp-incremental-recompute-2026-11-03
---

# CodeGraph incremental recomputation — observed results

**Chronology / evidence authority:** The [pre-observation hypotheses and acceptance controls](codegraph-incremental-recomputation-preregistration-2026-11-03.md) were committed to ASES main at `f6e5c528fa01ee18a71d0caf98e162a1f5ebdf87` **before** executing the experiments below. This document is a later observation and interpretation record; it does not retrospectively change that preregistration, adopt the draft testing method globally, or authorize a production migration.

**Project:** [draft PR #23](https://github.com/rock-solid-sites/ases-plugins/pull/23) stacked on the deduplication experiment (#22). **Executed engine:** pinned CodeGraph CLI `1.6.0`; the cgrmcp runtime dependency is also `@colbymchenry/codegraph@1.6.0`. This does **not** prove the VPS service's actually running version. **Fixture:** synthetic, commit-controlled 160-module TypeScript repository, about 1,280 generated callable functions plus a small core and consumer. **Environment:** GitHub Actions Ubuntu runner / Node 22. All workspaces and databases were temporary; no live VPS or Backblaze B2 operations occurred.

## 1. Source-backed reasons and pretest expectations

cgrmcp's current immutable-snapshot builder uses CodeGraph `init` on every distinct pinned Git commit. A `sync` call exists only as an incomplete-initial-index fallback. Its separate per-commit CodeGraph databases dominated our earlier two-commit storage sample, at approximately **5.1 MiB of 6.6 MiB** in published snapshots. Source deduplication and compression reduce *retained data*, but not redundant recomputation. The ASES Processor/reuse-substrate research supplies the broader question: which previously derived results are still valid, and is recomputing only invalidated dependencies cheaper than starting over?

Native `codegraph sync` is documented upstream for updating changed files. We froze six hypotheses (H1–H6) and directly tested the native CLI before attempting to change cgrmcp's materialization or ready-snapshot contracts.

## 2. Execution chronology — failures are not erased

| Event / evidence | Actual observation | Classification |
| --- | --- | --- |
| [Run 41668599872](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41668599872) | `--version` confirmed 1.6.0. No-op `sync` reported up-to-date; one changed-file sync removed the old function and indexed a new one. | PASS — CLI instrument discovery, not full parity |
| [Run 41669110359](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41669110359) | Seven cases executed; only no-change and documentation-only comparisons passed. Differences appeared in caller lists on source-changing cases. | FAIL — initial parity instrument |
| [Run 41669548094](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41669548094) | All seven cases agreed on file/node/edge counts and checked symbol outputs. The only mismatches were 20-entry `coreBase` caller lists; different valid callers occupied the cutoff. | FAIL — **instrument limitation isolated**, no proven index defect |
| [Run 41670081543](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41670081543) | Changed caller/callee queries to explicit `--limit 5000`; query symbol limit explicit too. **7/7** parity and source-oracle cases passed. | PASS — corrected full CLI oracle |
| [Run 41670688612](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41670688612) | Repeated **7/7** pass. Independently copied a quiescent index to another Git checkout, modified and removed source there, synced and compared against clean rebuild; original source and DB SHA-256 unchanged. | PASS — isolated cross-checkout reuse proof |

**Why the false failure matters:** CodeGraph issue [#1639](https://github.com/colbymchenry/codegraph/issues/1639) documents that the pinned CLI silently defaults to a 20-item limit for `callers`/`callees` and 10 for `query`, without reporting truncation. Graph rows had changed order after indexing, so two equally complete graphs returned different truncated subsets. This is a **test-oracle error**, not established evidence of stale call edges. The original failed CI executions are deliberately retained. Upstream has also investigated genuinely stale incremental edges in other versions/issues ([#773](https://github.com/colbymchenry/codegraph/issues/773), [#1240](https://github.com/colbymchenry/codegraph/issues/1240)); those incidents are contextual threats, not a diagnosis of this fixture.

## 3. Hypotheses adjudicated, within tested scope

| Hypothesis | Observation | Research conclusion |
| --- | --- | --- |
| H1: native incremental `sync` updates changed source and preserves graph-query results | Fresh vs warm agreement in 7/7 controlled source states; changed functions removed/added correctly | **SUPPORTED within tested source facts and query surfaces** |
| H2: sync is incomplete/no-op for certain changes | Positive/negative controls for renaming, deletion, newly added symbols and import changes passed | **WEAKENED**, not globally eliminated |
| H3: changed-file recomputation costs less than fresh rebuild | First successful run changed-case median **0.53 s sync / 0.82 s clean**; later run **0.64 s / 1.02 s** | **PRELIMINARILY SUPPORTED** on this corpus, about 36–37% less elapsed time; not a universal benchmark |
| H4: no-change sync avoids unnecessary work | Reported already up-to-date with no graph differences; one run observed approx. **0.28 s** vs approx. **0.80 s** clean | **PARTIAL**; physical I/O and actual writes not measured |
| H5: structural changes preserve correct symbols and caller relationships | Added, renamed and deleted function/file cases and changed exported symbol + importer matched complete cold-query sets and selected direct source facts | **SUPPORTED within cases**; not a global correctness proof |
| H6: complete quiescent index can be copied to a different checkout and synced safely | The new stage was indexed from a copied seed with one changed and one deleted source file. Status, exact-symbol/caller observations and graph counts matched fresh rebuild; original files and DB were unchanged. | **SUPPORTED for one isolated synthetic cross-checkout comparison** |

The oracle is **not fully independent**: both paths use the same upstream CodeGraph engine. Direct assertions about source symbols/relationships qualify a subset of possible wrong answers, not all AST or parser behavior. Successful CLI queries do not establish live MCP or ChatGPT-client behavior.

## 4. Storage and timing evidence, readable units

On the seven-case 160-module fixture the CodeGraph index stayed approximately **2.5–2.6 MiB**. Sync only reported changed source files rather than scanning all source for a full rebuild. Timings are wall-clock command times *including Node/CLI startup and runner caching*. Report medians for change classes instead of claiming CPU-cycle savings from these numbers.

**Cross-checkout control (run 41670688612):** an approximately **2.5 MiB** quiescent index was copied to a different temporary checkout in **0.003 s**; `sync` took **0.69 s**, compared with **1.01 s** for independent fresh `init`. Approximately **31% less wall time** for copy plus update in this single controlled comparison. Source and DB in the previous checkout retained their recorded hashes. The `sync` log reported **two changed files** (one modified, one removed). This is not a measurement of a deployed snapshot-cache manager, filesystem peak/RSS, or speed at larger scale.

## 5. Interpretation versus decision

**Supported decision:** investigate a **disabled-by-default** cgrmcp index-seeding candidate, operating only on a new staging tree: identify a compatible ready source index by repo identity, CodeGraph version/extraction/schema/config; acquire or validate safe read-only/quiescent source access; copy (never hardlink) the SQLite database and any required metadata; then `sync`, validate graph/status/source consistency and publish the *new* commit's immutable snapshot. On missing, stale, corrupt, partial-WAL or incompatible seed, use the already-tested clean `init` path; never mutate a published ready snapshot. Record seed provenance and fallback reason for later Processor/reuse research.

**Not authorized or not established:** production release or merge; implicit index reuse without an explicit `sync`; SQL/WAL live backup correctness; concurrent readers/writers or cross-process locking; crash/restart while copying; invalidation when extraction/parser/schema/config changes; Rust/Go/large real-repository parity; CPU/RSS/peak disk and amortized storage/remote costs; any claim that a globally shared Processor or ASES-wide caching API exists. CodeGraph 1.6.2 is published but was **not** the executing engine in these tests; version-to-version comparison remains separate.

**Next cheapest discriminating test:** test a **copy-seed failure or invalidation case** (partial copied DB, mismatched engine extraction version, active WAL, or interrupted copy) with a clean-build fallback and intact prior snapshot, then compare representative Rust, Go and TypeScript repositories. Only after evidence of correctness and meaningful total savings should cgrmcp's new-snapshot worker be changed.

**Evidence qualification:** GitHub Actions job logs and commit hashes are linked, but no independent archive with verified download/read-back was performed: `ARCHIVE_NOT_VERIFIED`. The independent raw artifact-retention requirement remains open. This research result is not an operator acceptance of any production change.
