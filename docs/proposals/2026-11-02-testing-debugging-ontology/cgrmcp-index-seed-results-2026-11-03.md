---
title: cgrmcp Index Seed — Observations and Evidence Qualification
program: ASES / EDASES
document_type: Experiment Result and Decision Record
status: Preliminary outcomes; further controls in progress
authority: Research (not ASES-wide acceptance)
date: 2026-11-03
preregistration: cgrmcp-index-seed-hypotheses-2026-11-03.md
project_branch: experiment/cgrmcp-index-seed-2026-11-03
---

# cgrmcp copied-index reuse — empirical record

**Reasoning was frozen before implementation** in [cgrmcp-index-seed-hypotheses-2026-11-03.md](cgrmcp-index-seed-hypotheses-2026-11-03.md), ASES commit `3904c3aed0cff438d84511843da10de57aa7aecd`. This is the *later observation and interpretation*, not retroactive preregistration. The original CodeGraph experiment also lives in [preregistration](codegraph-incremental-recomputation-preregistration-2026-11-03.md) and [results](codegraph-incremental-recomputation-results-2026-11-03.md). Each test and acceptance claim is scoped to its executing artifact, not the live VPS.

## 1. Implementation and experimental identity

[Draft PR #24](https://github.com/rock-solid-sites/ases-plugins/pull/24) is stacked on unmerged #23, #22 and #20. The recovered JavaScript cgrmcp runtime with CodeGraph **1.6.0** now contains a **disabled-by-default** `CGRMCP_REUSE_INDEX=1` experiment. It searches manifests for the latest ready snapshot of the same canonical URL, Git object-ID length and exact engine version, and uses a read-only SQLite online backup in a 20-second-bounded Node child to seed the **new staging checkout**. The already published source snapshot is never modified or hardlinked. After `sync`, status must be complete, show zero pending changes/refs, match engine and extraction versions, and not recommend a rebuild; any ordinary invalid seed or failed sync discards only the staged index and takes the original clean-init path. Candidate search is bounded, and successful/failed decisions are retained in `index_seed` manifest provenance.

**Security and correctness caveat:** SQLite structural `quick_check` is not a semantic graph oracle. CodeGraph may still have shared upstream mistakes in both seeded and cold builds. A 16-hex truncated URL hash alone would be insufficient identity; exact canonical URL comparison was added. Node 22 `node:sqlite` is experimental. The feature remains off without an explicit opt-in; no production authorization follows.

## 2. Evidence chronology and failure classes

| Evidence | Actual observation | Classification |
| --- | --- | --- |
| [41687153451](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41687153451) | Recovered-source provenance check ran after `npm ci`, so new `node_modules` files appeared as unexplained original-source files. | FAIL, **test-order instrument defect** |
| [41687285580](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41687285580) | Three new unit cases passed fixture `stage` rather than API `stagePath`; separate real SQLite backup probe passed. | FAIL, **fixture parameter defect** |
| [41687384827](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41687384827) | First full MCP seeded case rejected with `invalid_identity_or_engine`. Inspecting cgrmcp URL parsing established its canonical URL hash is **16 hex**, not the assumed 64. | FAIL, **candidate identity implementation mismatch**, correctly failed closed |
| [41687580529](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41687580529) | Repaired identity, version and WAL unit controls passed; first seeded two-commit MCP test and independent cross-checkout parity passed. Backed-up index approx. **2.5 MiB** in **49 ms**, with old DB SHA-256 unchanged. Wrong engine version cleanly skipped. | PASS in isolated TypeScript scope |
| [41688090471](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41688090471) | Added direct CodeGraph CLI symbol positive/negative checks on old/new published snapshots. Corrupted staged SQLite copy rejected after failed sync, then a clean index was built and queried successfully. | PASS, fallback and oracle qualified |
| [41688690001](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41688690001) | All eight unit controls, two-commit baseline/reuse, invalid-engine and corrupt-stage recovery, restart and independent TypeScript parity passed. Added explicit engine/extraction compatibility, full canonical URL identity and stable source hash. | PASS, **development acceptance only** |

The last step expands the earlier positive result beyond transport: the original and modified commit return different expected symbol sets and both remain usable after restart. The original failed steps remain visible and are not rewritten as successes.

## 3. What the performance evidence actually says

The first end-to-end MCP timings were coarsened by `repo_status` polling at approximately 600 ms intervals. In [41688090471](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41688090471), observed full rebuild took **1.97 s** and seeded path **1.98 s** by that measure; this does not establish faster task completion.

A more discriminating worker-local instrument in [41688690001](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41688690001) recorded:

| Work | Measured | Interpretation |
| --- | ---: | --- |
| Full index worker processing | **954 ms** | Exact loop within cgrmcp (excluding queue/fetch and status polling) |
| Seeded `sync` worker processing | **769 ms** | Index loop only |
| SQLite backup cost | **55 ms** | Added to seeded path |
| Seeded combined measured work | **824 ms** | About **14%** less than baseline in **one** run |
| Corrupt-seed clean fallback worker work | **1,183 ms**, plus **64 ms** backup | Expected extra cost of failed optimization; correctness preserved |

Do not interpret these as CPU usage, provider billing, 14% total savings, or multi-run robust median. The separate earlier native CLI experiment showed a larger change-class performance gain, but a cgrmcp service has additional backup, process, manifest and polling costs. Two ready indexes still occupy two databases, so **cross-commit reuse reduces reprocessing work, not retention storage**.

## 4. ASES Processor connection

The generic result-reuse substrate should store the **source identity and versioned derivation conditions**, not merely a cache hit: canonical repository, Git object format, immutable commit, CodeGraph binary/version/extraction schema, prior result identity, trusted backing DB state, independently checked dependency changes, and evidence of the next result's completeness. `index_seed` is a project-local, testable example of this contract, **not** the adopted Processor schema or a requirement of Kernel-0.

The experiment also demonstrates why admission, cheap validity checks, actual recomputation, and cost accounting are distinct. On small tasks, the cost of checking/backup may offset saved indexing. A safe fallback can be more expensive than declining reuse. Hence the next useful decision is a measured **reuse-or-rebuild threshold** after representative small/medium/large, Go/Rust and repeated runs, rather than a globally assumed efficiency benefit.

## 5. Remaining falsifiers, preservation and decision

Additional synthetic Go generalization and tiny-fixture cost controls are **pending at the time of this record** and must not be reported as passing until their own CI completes. A synthetic Rust case, representative real Git repositories, concurrent cross-process writers, sustained WAL churn, process crash at backup boundaries, disk/RSS accounting, parser upgrade with unchanged semver and repeated-run variability remain **NOT_RUN**. The existing version gate is deliberately conservative but not cryptographic executable identity. SQLite online backup's source read-only mode and WAL unit case are meaningful controls, not a complete cross-process correctness proof.

**Recommendation so far:** keep feature **off by default** on an unmerged development PR. Further investigate whether the ratio of changed files to total files, indexing duration and backup/validation costs predicts a reuse win; qualify a minimal decision record for later optional ASES Processor work. No live production service change, deletion, B2 transfer or automatic artifact eviction. No independent durable CI archive read-back: `ARCHIVE_NOT_VERIFIED`.

**Authority rule:** preserving the upstream evidence, failed diagnostic episodes and corrections under the draft ASES testing/assurance method is a project-local evidence trial. This record does not silently promote the methodology proposal or change any canonical production guarantee.

## 6. Later results addendum — 2026-11-03, after the initial record

The preceding section's **pending** classification describes its state at original authorship; it is intentionally retained as chronology rather than silently edited away.

[Final completed expanded CI 41689657899](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41689657899), development commit `d16f68aec5c1a5df13f68fa7c328bff780abfe81`, passed the existing historical-source provenance check, eight unit/fault controls, baseline and seeded two-commit TypeScript MCP/restart sequences, incompatible-version rejection, intentionally corrupted staged DB with clean fallback, source+graph query oracles, earlier cross-checkout source integrity, and the two new generalization controls.

**Go generalization:** Synthetic 74-file Go source with a real second Git revision: copied-index sync **503 ms**, clean initialization **788 ms**, index-copy overhead about **2 ms**. Checked graph status, symbols, removed/added file, direct expected source symbols and a known caller relationship. All matched fresh reference. This is a **synthetic Go fixture** and does not resolve CodeGraph 1.6.0's known Rust module-scope issue, nor establish correct arbitrary Go graph extraction.

**Tiny-repository control:** Two-commit synthetic TypeScript fixture: clean indexing **1,190 ms** versus seeded sync **988 ms + 39 ms** online backup, approximately **14%** less measured work on one runner. The hypothesis that a tiny repository must be slower under reuse was **not supported in this one sample**. More sizes and repeated timings are necessary before a threshold can be derived.

**Larger TypeScript repetition:** The same 160-module class recorded **1,991 ms** clean versus **1,029 ms sync + 54 ms backup**; this is approximately **46%** less measured work on that runner. Compare with the earlier same-class sample (954 ms clean vs 769 ms sync + 55 ms backup; ~14% less). The substantial variability precludes treating either result as a predictive general speedup. Both paths maintain separate published indexes; no claim of persistent storage reduction.

**Additional invariant:** seed selection now also requires the **exact canonical repository URL**, not merely the 16-hex truncated hash, and the same Git object-ID format, with unit controls for colliding-short-hash identities and priority among multiple compatible previous commits. Engine-version and extraction-version validation remain in place. A documented opt-in flag is present in the recovered runtime README/`.env.example`.

**Decision:** H/S research receives positive evidence to continue with an isolated, **off-by-default** mechanism; **no production release, merge or automatic reuse threshold is authorized**. Next consequential falsifiers are real repositories, larger and sustained WAL writers, process-kill boundaries, concurrent cross-process access, resource/I/O monitoring, engine version/extraction changes and outcome-level agent work. The Go/tiny tests change the earlier pending classification only in the narrow scopes stated above.

**Archive:** `ARCHIVE_NOT_VERIFIED` remains unchanged. GitHub Actions logs and repository commits are direct/native evidence, not independent long-term archive readback. No Backblaze B2 upload or deletion occurred.
