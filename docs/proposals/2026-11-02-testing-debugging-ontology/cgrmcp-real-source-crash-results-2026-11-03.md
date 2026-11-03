---
date: 2026-11-03
document_type: ASES experimental observation and decision record
status: partial qualification; Go failure remains unresolved
authority: research only, not production release or Processor policy
preregistration: cgrmcp-index-seed-real-repos-crash-preregistration-2026-11-03.md
---
# Real-source CodeGraph index-seed qualification — observed results

**Chronology:** This is written after [the prospective test/hypothesis record](cgrmcp-index-seed-real-repos-crash-preregistration-2026-11-03.md) was committed at `407d1690b5a77d4c4db802e0585a9a4f85645d3c` and after the initial real-source matrix ran. That preregistration remains unchanged. A [Go-specific prediagnostic plan](cgrmcp-go-edge-discrepancy-diagnostic-plan-2026-11-03.md) was separately committed at `1ebafa15ff46b89a40ad97b3cef3bb055a3b04b1` **before** follow-up diagnostic CI.

## Scope and evidence

[GitHub Actions run 41701139522](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41701139522) executed pinned CodeGraph **1.6.0** on one Ubuntu runner per job. All three real-source cases used a deterministic **actual adjacent Git parent and child**, extracted as source from public Git archives; no upstream scripts/dependencies were run. A complete parent index was used as an online-backup seed, synchronized into a newly staged child worktree and compared against a separate clean index of the identical child source. Trials alternated seeded-first versus clean-first and reported CLI+backup duration, indexed file list, node/edge/kind counts, sampled exact symbols and callers with explicit nontruncating query limits, plus the source-file SHA-256. The initial parent DB was checked for modification. These measures are **index correctness and worker costs**, not a complete cgrmcp MCP launch or user-agent benefit measurement.

The workflow itself was **FAIL**, because the larger Go example revealed a graph disagreement. Do not summarize it as a green suite or average this failure away.

## Real-source observations

| Case | Changed revision | Parity | Seeded median | Clean median | Observed change |
| --- | --- | --- | ---: | ---: | --- |
| Rust: `sharkdp/fd`, `src/filesystem.rs` | `4f757533d0b5861a82c24024e4efb450cc6fb5f7` | **PASS 3/3** | **421 ms** | **662 ms** | ~36% less wall time |
| TypeScript: `unjs/ofetch`, `src/fetch.ts` | `5f17585adc357ba4626874d69e377d970ae4b276` | **PASS 3/3** | **652 ms** | **865 ms** | ~25% less wall time |
| Go: `junegunn/fzf`, several `src/*.go` files | `99bfd5aa0f66133d7dcfbf18f8044eb765f04649` | **FAIL on first trial** | **Not qualified** | **Not qualified** | Seeded **13,091** edges, clean **13,105** edges |

**Rust:** Indexed about 30 recognized source files and 712 nodes in the parent; tested `path_absolute_form`, `absolute_path` and `strip_verbatim_prefix` symbols/callers in each child trial. The resulting child databases were around **2.1 MiB**. Seed/clean trial timings were 539/662, 413/663 and 421/631 ms. The initial seed trial included a comparatively slow **182 ms** backup; subsequent backups were 51–66 ms. Report the variability; do not infer a stable 36% general speedup.

**TypeScript:** Indexed 22 recognized files and 104 nodes in the parent; tested `retryStatusCodes`, `nullBodyResponses` and `createFetch` symbols/callers in each child trial. The child seed databases were **508 KiB**, versus **492 KiB** clean. Seed/clean timings were 652/864, 660/880 and 644/865 ms. This illustrates why an incremental path might be faster but larger on disk.

**Go failure:** The first real `fzf` fixture had **116 indexed files, 2,925 nodes, matching kinds and extraction version 25** on both paths, but **14 fewer edges in the seeded graph**. These are raw indexed relationship counts, not the already-diagnosed 20-item CLI caller query truncation. We have **no license to assume the seeded result is correct or production-safe**. It may be incremental-specific omission, upstream cold-build nondeterminism, or a subtle graph-identity problem. The follow-up test compares a *second independent clean build* and complete canonical SQLite edge multisets. Record the outcome in a later addendum, not by altering the original result here.

## Concurrency and crash controls

The same CI run's independent crash/concurrency job **passed**. A separate live SQLite WAL writer produced **200 rows**, while the online backup ran after 20 rows, alongside another read-only connection. The backed-up database held a consistent **27-row prefix** with successful SQLite `quick_check` and no missing row, and the writer later completed normally. This is a one-shot WAL overlap, not a 24-hour sustained concurrency or backup starvation test.

A separately launched temporary index-worker fixture wrote a partial `.codegraph` staging DB, an `indexing` manifest and a stale lock, then was terminated with **SIGKILL**. `reconcileAtBoot` changed the manifest to `failed(index_interrupted)` while preserving the consumed attempt; it cleared one stage and one lock and left the previous ready DB unchanged and selectable. A second boot was a no-op. **This simulates a worker killed with partial staged data, but it does not prove killing the native SQLite `backup()` call at every possible instruction boundary.**

Existing seed regression unit controls (eight cases) also passed; the further existing cgrmcp service tests are in the preceding [seed results record](cgrmcp-index-seed-results-2026-11-03.md). CI artifacts of the successful real-source trials are retained temporarily by GitHub Actions for **30 days**, not independently archived and read back. Classification: `ARCHIVE_NOT_VERIFIED`.

## Architectural decision (provisional)

- **Do not merge, deploy or globally enable index reuse.** A real Go graph discrepancy blocks correctness qualification regardless of favorable timings in Rust and TypeScript.
- The passed writer and crash tests strengthen confidence in the isolated online-backup and boot cleanup paths, but do not establish concurrent active-engine resolution correctness.
- Correctness and validity must precede ASES Processor cost optimization. A fast, wrong graph is not a cache hit. The minimum reusable-result contract may need more than a complete-status bit and matching extraction version: relationships may require source-level revalidation or an independent graph fingerprint/oracle.
- Next cheapest test is an independent second clean graph plus a canonical edge multiset diff. If cold builds disagree, investigate upstream nondeterminism and test stability. If they agree but seeded differs, investigate incremental-specific dropped edges and versioned upstream fixes. Do not relax the graph-count gate to obtain a green CI run.

## Later diagnostic addendum — exact Go relationship-loss evidence

[Diagnostic run 41701972587](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41701972587) performed the prospective [Go discrimination plan](cgrmcp-go-edge-discrepancy-diagnostic-plan-2026-11-03.md) and preserved a canonical SQLite edge-multiset diff. CodeGraph engine remained **1.6.0** and the pinned `junegunn/fzf` parent/child commits were unchanged.

| Graph | Files | Nodes | Edges | Compared with cold A |
| --- | ---: | ---: | ---: | --- |
| Seeded index + `sync` | 116 | 2,925 | **13,091** | 14 missing, 0 extra |
| Independent cold A | 116 | 2,925 | **13,105** | Reference |
| Independent cold B | 116 | 2,925 | **13,105** | **Exactly same edge multiset** |

The seed lost precisely **14 `contains` edges** linking Go type aliases/structs to method nodes. Missing relationships included `resumableState::Enabled/Force/Set`, `actionType::String/Name`, `Terminal::inListWindow/markEmptyLine/markOtherLine`, `byTimeOrder::Len/Swap/Less`, `Options::initProfiling` from both build-tag files and `placeholderFlags::encodePlaceholder`. They originate in `src/terminal.go`, `src/actiontype_string.go`, `src/options*.go` and `src/terminal_test.go`. These relationships were present in both clean builds and missing from the seeded graph; the difference was not caused by truncating caller queries. No extraneous edges were observed, and the filenames, nodes, kinds and index extraction version agreed.

**Evidence classification:** G1 (incremental-specific edge loss) **SUPPORTED**, G2 (cold-build nondeterminism in this fixture) **WEAKENED**, G3 (mere query truncation/instrument defect) **REJECTED** for this observation. G4 (precise causal mechanism in the Go extractor/incremental linker) remains **UNRESOLVED**. A healthy CodeGraph `status --json` is **not** sufficient proof that the graph is equivalent to a fresh build.

**Consequence:** this is a correctness-blocking negative result. **Do not merge, deploy or automatically enable index seeding** on the basis of Rust/TypeScript timing wins. The next smallest discriminating check is a *separate versioned* CodeGraph 1.6.2 control and/or a local minimal reproduction for upstream. Do not silently change the production 1.6.0 pin, weaken the graph-parity oracle or bury this failure in aggregate passing counts. The CI artifact expires; independent archive remains `ARCHIVE_NOT_VERIFIED`.

## Later upstream-version control — CodeGraph 1.6.2 (separately qualified)

[Version-isolated CI run 41702509899](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41702509899) used an independent temporary installation of `@colbymchenry/codegraph@1.6.2`, leaving the cgrmcp 1.6.0 runtime package and lockfile unchanged. It repeated the **exact pinned `junegunn/fzf` parent/child source**, seeded index `sync`, and **two independent cold builds** against that single version.

The 1.6.2 seeded, cold A and cold B results were **identical across the complete canonical SQLite edge multisets**: 116 indexed files, 2,925 nodes and **13,024 edges**, with **0 missing or extra** edges. The 1.6.2 extraction version was **27**, whereas the observed 1.6.0 failure used extraction version **25**. Different absolute edge counts across these versions must **not** be interpreted as missing edges; compare indexed results *within* one version. The first 1.6.2 seeded path took approximately **2.46 s** versus **4.43 s** clean, with a **single** timing sample.

**Interpretation:** the Go edge-loss symptom is reproducible on the tested 1.6.0 installation and **does not reproduce under 1.6.2** for these pinned sources. That supports testing a version-specific upgrade in development, but does not identify the exact upstream commit that fixed it or prove general 1.6.2 correctness. The upstream 1.6.2 release explicitly recommends reindexing because the index extraction semantics changed. **Never seed or serve a 1.6.0 database under a 1.6.2 engine by merely relabeling the manifest**; exact version/extraction gates remain necessary. Three alternating 1.6.2 repetitions are scheduled separately and must be recorded before treating the timing benefit as repeatable.

Decision remains: **no production deployment, merge or default-on setting**. The user-authorized development experiment may now examine an explicit development-only 1.6.2 pin and migration plan, with clean rebuild of old indexes and a fresh correctness/assurance gate.

## 1.6.2 repeated-trial qualification — later addendum

[CI 41702907364](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41702907364) repeated the exact pinned `junegunn/fzf` real Go source comparison with isolated CodeGraph **1.6.2**. The first independent three-way seed/cold/cold comparison again produced **13,024 identical edge multisets**, **116** indexed files and **2,925** nodes, at extraction version **27**.

The subsequent three alternating clean-versus-seeded comparisons all passed full file/count parity plus sampled exact symbols/callers (`init`, `Enabled`, `Force`), with timings:

| Trial | Order | Seeded update incl. backup | Full rebuild |
| --- | --- | ---: | ---: |
| 1 | Seed first | 2.64 s | 3.14 s |
| 2 | Clean first | 2.26 s | 3.12 s |
| 3 | Seed first | 2.28 s | 3.11 s |
| **Median** | | **2.28 s** | **3.12 s** |

The seeded path saved approximately **27%** of the median measured operation time on this pinned real Git source, one runner, and one CodeGraph version. It did **not** reduce stored index size: child seeded DB approx. **12.24 MiB**, cold DB approx. **11.86 MiB**. No CPU, RSS, peak filesystem allocation, electricity, provider billing, end-user agent task improvement or production QPS conclusions follow.

**Epistemic distinction:** 1.6.2 **does not reproduce** the observed 1.6.0 Go incremental relationship omission on these inputs; the different absolute edge counts across upstream versions cannot establish that 1.6.2 is universally semantically correct, or pinpoint which upstream change repaired this case. A versioned clean-rebuild oracle, extraction identity and pinned source facts are essential. The stronger proposal is to run a dev-only 1.6.2 upgrade acceptance suite and **rebuild 1.6.0 indexes** instead of attempting cross-version seeding. The current cgrmcp development runtime remains pinned to 1.6.0 and is not thereby upgraded, merged or deployed.

**Next acceptance gates:** versioned cgrmcp MCP end-to-end across Rust/Go/TS, migration/reindex behavior on startup or explicit operator action, checks for mixed-version manifest/index registry, multiple commits/branches, repeated WAL contention and crash boundaries, representative large repositories, performance/resource accounting, independent evidence archiving. The Go 1.6.0 negative test must remain a **failure** until an explicit fix or version guard is installed; no silent downgrade or waived graph-parity oracle.

## Migration blocker discovered in source review — version-agnostic snapshot identity

Before considering a direct cgrmcp upgrade, inspecting the current recovered runtime found a **separate compatibility hazard**: `SnapshotManager.open` short-circuits a manifest in state `ready` by `(canonical URL hash, commit)` without checking the running CodeGraph version. `resolveSnapshot` likewise requires `ready` but does **not** compare `manifest.engine.version` with the current execution engine. The public `snapshot_id` is derived from repository, commit and shortened URL hash, **not** from the index producer/version/extraction schema.

Consequently, merely bumping the CodeGraph package in an existing cgrmcp store could label and route **1.6.0-built database snapshots as ready under a 1.6.2 engine**, despite the upstream 1.6.2 release explicitly advising reindexing. The opt-in *seed selection* version gate is **not enough**: it governs only building a new snapshot, not serving an existing ready snapshot through `repo_explore`.

**Safety decision:** Do **not** directly upgrade an existing store in place. First qualify an isolated **new, version-scoped store root** or explicit versioned snapshot IDs/registry migration, plus a `repo_explore`/engine compatibility gate that does not unnecessarily block safe raw source reads. Reindex previous revisions cleanly under 1.6.2; never relabel or silently seed old 1.6.0 SQLite. Preserve old snapshots/manifest evidence until explicitly verified replacement and rollback. Test the behavior of `repo_open`, `repo_status`, `repo_explore` and `repo_read` separately across an engine-version transition. This is a **design blocker**, not a committed implementation change.

**ASES Processor generalization:** a derived result's address must not falsely imply cross-producer reuse. Existing cgrmcp's commit-only snapshot IDs make this a concrete example: work identity and result identity are distinct, and validity must also bind to the actual producing engine/version/schema. Retain this as a proposed architectural requirement, not a global kernel rule.

## Later 1.6.2 cross-language replication

[Cross-language CI run 41703432405](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41703432405) added three alternating, independently indexed source comparisons for each of the same immutable public Rust and TypeScript revisions under an isolated CodeGraph **1.6.2** binary (extraction version 27). Both language jobs **PASSED all 3/3 source/graph parity controls**.

| Real source | Seed median (backup included) | Fresh median | Difference | Indexed DB size (seed / fresh) |
| --- | ---: | ---: | ---: | ---: |
| `sharkdp/fd` Rust | **742 ms** | **1,228 ms** | ~40% less elapsed time | ~2.11 / 2.12 MiB |
| `unjs/ofetch` TypeScript | **834 ms** | **1,026 ms** | ~19% less elapsed time | 588 / 560 KiB |

The independently completed [Go 1.6.2 triplicate run 41702907364](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41702907364) likewise **PASSED 3/3** with 2.28 s seeded and 3.12 s clean median (~27% less). The source fixture, CodeGraph binary and query oracle are versioned, but these are three samples per source, not general-purpose engine guarantees, nor agent-level cost improvements.

The 1.6.2 Rust/Go/TS trials show that the earlier 1.6.0 Go failure is not an inevitable property of our SQLite-backup mechanism. They **do not** erase the negative evidence, justify serving 1.6.0-built databases under 1.6.2, or prove the entire graph correct where both paths could share the same extractor error. A version-scoped, clean-reindexed cgrmcp store and cross-version query gate remain mandatory before any development upgrade acceptance.
