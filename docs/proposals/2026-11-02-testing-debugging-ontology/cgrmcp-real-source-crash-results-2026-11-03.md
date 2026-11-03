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
