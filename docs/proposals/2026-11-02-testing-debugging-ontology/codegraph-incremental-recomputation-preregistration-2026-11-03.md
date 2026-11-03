---
title: CodeGraph Incremental Recalculation — Pre-observation Experiment Record
program: ASES / EDASES
document_type: Research Experiment Preregistration
status: Experimental / hypotheses frozen before execution
authority: Research; not canonical policy
date: 2026-11-03
project_repository: rock-solid-sites/ases-plugins
project_branch: experiment/cgrmcp-incremental-recompute-2026-11-03
method_source: proposal/testing-and-assurance-method-2026-11-01
---

# CodeGraph incremental recomputation — experiment preregistration

**Evidence boundary:** This is a *prospective reasoning and test-selection record*, written before new incremental-update CI tests run. Earlier cgrmcp compression/dedup measurements are retrospective inputs, not pre-observation predictions about `sync`. Do not revise the hypotheses below after seeing results; append timestamped observations and decisions in a separate companion report. This document applies the **draft** ASES testing, assurance and debugging proposals locally; it does not adopt them as global rules.

## 1. Why conduct this experiment?

The cgrmcp connector currently obtains an immutable Git commit, creates a fresh checkout and calls CodeGraph `init` for each distinct commit. Even when most source files are unchanged, each published revision receives its own graph database. Isolated two-commit synthetic tests found a store footprint of approximately **8.2 MiB**, with the CodeGraph index files occupying approximately **5.1 MiB**, before source hardlinking. Immutable source deduplication and cold Brotli compression recover some storage *after* recomputation, but cannot avoid repeated parsing, graph resolution, index writes or startup time. The ASES/EDASES Processor and reuse-substrate research instead asks whether we can **avoid computation when results remain valid**.

Upstream CodeGraph documents `codegraph sync` as incremental, changed-file indexing. That is a capability claim about a *mutable project workspace*, not yet evidence that an index safely survives a Git checkout revision change, produces graph-equivalent results to a clean rebuild, or can be used with cgrmcp's immutable published-snapshot contract. The existing cgrmcp worker calls `init` on each new staged commit; its subsequent `sync` is only a completion fallback, **not** cross-commit index reuse. Therefore we must first qualify the native tool separately, before considering cgrmcp modification.

### Source and authority

- Existing CodeGraph baseline is pinned `@colbymchenry/codegraph@1.6.0` in the cgrmcp recovered runtime. **Installed version != running production binary**; no running VPS claim is made.
- Upstream documented `sync` command: https://colbymchenry.github.io/codegraph/guides/indexing/
- Local evidence: https://github.com/rock-solid-sites/ases-plugins/pull/20 and https://github.com/rock-solid-sites/ases-plugins/pull/22. Both draft/unmerged.
- ASES proposal: https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
- ASES debugging proposal: https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
- Related upstream-awareness proposal: https://github.com/rock-solid-sites/ASES/blob/main/docs/proposals/2026-11-02-testing-debugging-ontology/upstream-change-awareness-addendum-2026-11-02.md

## 2. Claim boundaries and competing hypotheses (frozen)

| ID | Competing hypothesis | Before-run prediction | Cheapest discriminating observation |
| --- | --- | --- | --- |
| H1 | Native incremental `sync` correctly tracks changed source from an existing index | After a distinctive function-body edit, no stale definition/query; result agrees with independent fresh `init` of same revised source | Paired warm `sync` versus clean rebuild; old/new distinctive symbol queries |
| H2 | `sync` is a no-op, incomplete, or refreshes only a subset | Some edit/delete/signature cases retain stale symbol, omit new symbol, or differ from cold rebuild | A negative control using deleted unique symbol, plus positive unchanged symbol |
| H3 | Workload costs depend on changed files; there is a genuine incremental benefit | On sufficiently large, mostly unchanged fixture, warm `sync` performs less wall time and/or disk I/O than a clean rebuild | Same machine, same fixture, alternating order/repeated trials; report medians and range, not single-run speedup claims |
| H4 | A no-source-change operation avoids unnecessary parsing/index writes | No-edit `sync` returns correct results and has low write amplification | No-edit paired control and database/content measurements |
| H5 | Incremental graph semantics remain correct across structural changes | Addition, deletion and exported-signature/import dependency change all agree with clean rebuild, not just body edits | Multi-case fixture with symbol and relationship positive/negative controls |
| H6 | Cross-commit index reuse is compatible with cgrmcp's immutable snapshot and provenance model | **Not assumed.** Successful native `sync` alone cannot establish this. | Later isolated cgrmcp candidate copying an index to a new staging root, never editing a ready snapshot, with parity against fresh index, commit-binding, restart and archive/reopen |

**Strong alternative explanation:** `sync` may report fast completion while leaving stale graph edges; speed alone is not success. Another is that the *CLI startup overhead* dominates, making incremental indexing correct but not materially cheaper for short jobs. A further alternative is that the native CLI supports reuse inside one directory but index path/metadata breaks on a new commit checkout. The experiment is designed to keep those alternatives visible.

## 3. Method selected, why, and what would invalidate it

**SELECTED:** deterministic local Git/TypeScript fixture (existing 160-module corpus) + pinned CodeGraph CLI, with two parallel workspaces: (a) warm workspace indexed initially and changed one case at a time by applying the same file mutation; (b) clean workspace built from scratch after mutation. Use `codegraph status --json`, machine-readable query/file outputs where supported, exact symbol names and graph-related commands; validate the *test instrument* on a known unchanged function and a deliberately removed function. Capture stdout/stderr/exit classification, elapsed time, peak RSS if accessible, and on-disk DB size. Preserve exit/parse errors as ERROR rather than treating empty output as a successful zero graph.

**Controls:** C0 no change; C1 documentation-only; C2 function body change; C3 add distinctive function; C4 rename/remove distinctive function; C5 delete file; C6 exported function/import dependency change. The controls are chosen because they can detect both false acceptance (stale graph) and false rejection (lost unaffected symbols). Apply a change to a *copy* or fixture only, not to a previously published cgrmcp snapshot.

**Oracle limitation:** Clean rebuild under the *same* pinned CodeGraph version is an independent execution path but not a mathematically independent specification. It can share upstream parsing/resolution defects. Separately assert a handful of expected source facts/relationships directly from fixture content. Treat discrepancies in `status`/CLI serialization as instrumentation concerns until inspected.

**Why not yet implement whole-index carry-forward into cgrmcp?** It would require mutable staging, validity/compatibility metadata, safe copier/backup for SQLite WAL, version and config invalidation, recovery semantics and potentially a different snapshot derivation contract. A cheapest discriminating upstream CLI test can disprove the premise before risking those changes. No automatic deployment, deletion or Backblaze B2 access is authorized by this experiment.

## 4. Stop conditions, decision thresholds and expected learning

- Stop or classify **BLOCKED** if pinned CLI or package cannot be executed in isolated CI. Do not silently upgrade in the same comparison.
- Correctness is mandatory: every applicable changed/no-change control and source/graph query must agree with cold rebuild *and* fixture facts. Any stale symbol/edge fails promotion even if faster.
- Performance claims require repeated warm and cold runs under similar conditions. If small-fixture data is noisy, report INCONCLUSIVE and scale/replicate; do not claim a benefit from one favorable timing.
- If `sync` only helps inside one mutable workspace, record that limitation and design a new copy-index cross-commit test separately.
- If a fixture is defective, preserve the failed observation and fix the instrument with a separately dated correction; do not rewrite this preregistration.
- Promote no ASES-wide Processor API or production cgrmcp behavior from this pilot. Candidate derived-result identity must account for source/commit, CodeGraph engine version, config, parser/graph schema and index validity; an observed "fast" result is not proof of sufficient provenance.

**Expected decision:** choose between (A) native incremental reuse is correct and worth cgrmcp adapter testing, (B) correct but negligible advantage, (C) incorrect in important change class, (D) inconclusive environment/instrument. Each changes the next experiment; none automatically selects a Processor implementation.

## 5. Evidence preservation contract

For every run: record commit and CodeGraph pinned version, original test plan ID, test fixture digest, case, attempted action, process exit and parser status, cold/warm correctness, time/RSS/storage and CI run URL. Separate execution result, evidence qualification, interpretation, authorized decision and archive recovery status. GitHub CI logs alone are **not** an independent durable archive; mark `ARCHIVE_NOT_VERIFIED` until separately captured and read back. Record financial/CPU overhead where measurable, without invented token counts.

**Preregistration state as of writing:** H1–H6 OPEN / NOT_RUN; no new incremental comparison has been executed. Later observations should be appended to a separate results report referencing this record and the exact pretest commit.
