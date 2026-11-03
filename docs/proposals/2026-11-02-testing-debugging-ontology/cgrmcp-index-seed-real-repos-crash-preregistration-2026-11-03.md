---
title: cgrmcp index-seed real-repository and crash/concurrency qualification
date: 2026-11-03
status: prospective hypotheses, before new CI execution
project: rock-solid-sites/ases-plugins
method: ASES proposed testing-and-assurance + debugging ontology, local application
authority: research only; draft branches remain nonproduction
---

# Index seeding: real-repository and crash/concurrency qualification — preregistration

**This is prospective.** Original rationale/controls and synthetic evidence are separately in [seed preregistration](cgrmcp-index-seed-hypotheses-2026-11-03.md) and [observations](cgrmcp-index-seed-results-2026-11-03.md). Do not modify these predictions after running the new CI; append results in a separate record. Draft PR #24 is working code, not evidence of production acceptance.

## Reason for experiment

Previous CodeGraph 1.6.0 trials on synthetic TypeScript and Go indicate that a new staged index can be backed up from a ready immutable commit, incrementally synchronized and queried without editing its source. The savings varied substantially (about 14–46% in single-run worker measurements), while whole-task latency was inconsistent. We need to find out if results generalize to **real public source trees with real developer commits**, whether an actual failed or killed backup leaves recoverable state, and whether online backup remains consistent with WAL writers/readers. Without these answers, changing automatic ASES Processor routing or production cgrmcp is premature.

## Frozen test cases and competing hypotheses

| ID | Hypothesis / alternative | Discriminating measurement | Falsification or uncertainty |
| --- | --- | --- | --- |
| R1 | Index seeding is graph-equivalent to clean indexing for real TS source | Exact pinned parent/child of `unjs/ofetch`, full indexed file/node/edge counts, sampled symbol queries, complete callers, independent source facts | Stale/missing changed-file node, mismatched graph result, parser error; count-only equality insufficient |
| R2 | A different parser/language is not accidentally assumed compatible | Rust `sharkdp/fd` and Go `junegunn/fzf` pinned adjacent commits, same oracle | Rust-specific module-scope known limitation may fail in both branches: classify upstream/shared-oracle issue rather than silently accepting |
| R3 | Warm sync is cheaper in total than rebuilding | Repeated alternated A/B order, record prep/backup/index time, start-to-ready, DB growth, wall time; report medians/ranges, not a favorable sample | Backup/runtime overhead eliminates savings; CI variance makes claim inconclusive |
| R4 | Existing valid source remains unchanged despite WAL writes and overlapping readers | Cross-process SQLite writer/readers active while backup, checksum/quick_check and row-set invariants before/after; WAL activity counts | Source mutated unexpectedly, backup corrupt, lost rows; classify BLOCKED on lock contention |
| R5 | Kill during the backup/staging workflow does not create a ready snapshot | SIGKILL a disposable child producing an incomplete staging index; boot reconciliation marks pending attempt interrupted, clears tmp and locks; existing ready snapshot unaffected | Partial stage becomes ready, source modified, or boot cannot reconcile |
| R6 | Wrong engine/config identity invalidation refuses unsafe reuse | Match canonical URL, commit format, actual engine executable and extraction version; wrong flags and corrupt metadata return clean path | Reuse despite changed identity, no fallback classification |

## Real repository fixtures (read-only public sources)

Source revisions are immutable Git object IDs. Cloning is into disposable CI temp folders with hooks disabled; repository files are **never executed**, dependencies are not installed, and CodeGraph analysis only indexes source text. The test can fail closed on network failure or unexpected tree size rather than silently pick a different revision.

| Language | Repository | Parent commit | Changed commit / case |
| --- | --- | --- | --- |
| Rust | `sharkdp/fd` | `d96ed27204480561d07fe78de416bebc7b382845` | `4f757533d0b5861a82c24024e4efb450cc6fb5f7`: `src/filesystem.rs` modified |
| Go | `junegunn/fzf` | `26ff936df038b6a62ec42cf18db27b2ea2bb8ec3` | `99bfd5aa0f66133d7dcfbf18f8044eb765f04649`: `src/actiontype_string.go`, `src/options.go`, `src/terminal.go`, plus docs/tests |
| TypeScript | `unjs/ofetch` | `6a879d46bdf9f9d4e65b975b91ba3e005e132771` | `5f17585adc357ba4626874d69e377d970ae4b276`: `src/fetch.ts`, tests and package metadata |

These are three **public projects**, not the user's private production repositories. Pin and record SHA-256 digests of extracted input trees; report actual index/version sizes, not GitHub advertised sizes. Do not infer license or source safety from repository popularity; disable hooks, do not run repository scripts. If the selected CodeGraph version cannot index one project in CI under time limits, classify appropriately and retain the scope.

## Tests and acceptance boundaries

Native fixed CodeGraph 1.6.0, Node 22, explicit query limits to avoid the documented 20-caller truncation. Compare independent cold index, seed copy+sync, direct expected source facts and file list; preserve errors as **ERROR**, a missing symbol as **FAIL** only if oracle confirms its presence, and unavailable network/runtime as **BLOCKED**. Include no-op/doc-only control if time permits. Run multiple trials with order alternation; report wall timing and variance separately from correct/incorrect state. No false claim of CPU/RSS or total provider savings without actual measurements. Limit disk/time/temporary file growth.

Crash and WAL tests use isolated synthetic stores. Require positive and negative controls: a valid preexisting ready snapshot, an interrupted in-progress attempt, a clean retry, and a second boot no-op. A healthy status from CodeGraph is not an independent proof of graph completeness. All three different levels (source-fact, direct graph query, and cold-index parity) matter.

## Stop and next decision

Stop promotion immediately on a substantive graph mismatch, changed original source DB, partial-ready artifact, failed automatic cleanup, or unexpected binary execution. If a fixture exposes CodeGraph 1.6.0's upstream defect, preserve and classify; optionally repeat against the newer upstream release **as a separate versioned experiment**, never quietly upgrade the pinned baseline. If all controls pass, continue to build a **reuse cost predictor** based on observed changed-file ratio and backup overhead—but remain opt-in until actual task-value, resource and recovery evidence exists.

**Preservation:** commit fixtures, trial metadata, CI links and failure classifications. GitHub Actions logs are not a durable independent evidence copy; `ARCHIVE_NOT_VERIFIED` until downloaded, hashed, uploaded and read back. No external archive, no production or Backblaze B2 operations authorized in this research slice.
