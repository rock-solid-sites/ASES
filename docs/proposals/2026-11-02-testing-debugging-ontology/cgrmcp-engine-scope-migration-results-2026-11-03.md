---
date: 2026-11-03
program: ASES / EDASES
document_type: observed experimental results
authority: research, not production acceptance
status: first acceptance gates passed; repeated optimization evidence pending
preregistration: cgrmcp-engine-scope-migration-preregistration-2026-11-03.md
---
# cgrmcp engine-scoped store and path optimization — observations

This record follows the **prospective** [engine-scope migration hypotheses](cgrmcp-engine-scope-migration-preregistration-2026-11-03.md) committed at `5c170a729e479b3cb418ba2260b54c9ec43051cf`. It does **not** revise those predictions. It also follows the [14-edge Go 1.6.0 failure and 1.6.2 independent controls](cgrmcp-real-source-crash-results-2026-11-03.md). These are research experiments on GitHub Actions, not the production VPS.

## Safe compatibility change

A development-only, disabled-by-default `CGRMCP_VERSIONED_STORE=1` selector now maps the configured base store root to `engine-scopes/codegraph-v<exact-semver>`. Only the resolved scoped root is passed to store initialization, boot reconciliation, workers, query engine and MCP server. The running CodeGraph CLI is executed with `--version` **before** directory creation and must agree with the installed package version; custom executable overrides cannot be combined with versioned-store opt-in. Existing version-scoped components reject invalid versions or preexisting symlinked scope paths.

Separately, `SnapshotManager` now refuses a manifest marked `ready` if its CodeGraph engine/version differs from the running engine: the pinned-SHA cache fast path in `repo_open`, the post-fetch ready-record path, and `resolveSnapshot` for graph/raw-read routing all check compatibility. Refusal is typed `snapshot_not_ready` with `reason=engine_mismatch`; `repo_status` still describes historical state without relabeling it. Manifest publishing now records `built_with_version` and `extraction_version` reported by CodeGraph where available.

**Limit:** the inherited user-facing snapshot ID remains commit-based, but independent scoped roots have **separate** registries, making identical identifiers local to the selected engine scope. A fallback defense rejects mismatched engine manifests in a misconfigured shared root. No existing ready manifest is mutated, migrated or deleted. A production migration would require an explicitly scheduled cutover and a fresh index for each required commit.

## Observed tests

[CI run 41708452585](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41708452585) **PASS**: historical source provenance; four engine-scope unit tests covering separate registries for the same Git commit, unchanged legacy file hashes, wrong-version `repo_open` and `resolveSnapshot` refusal, negative/custom/symlink inputs and executing-binary attestation; eight seed and WAL unit tests; baseline full MCP; scoped full MCP two-commit, reading/explore and restart; scoped seeded full MCP and restart; simulated independent WAL writer and interrupted-stage crash recovery. The opt-out baseline behavior remained reachable.

[First complete CodeGraph 1.6.2 scoped matrix, 41708735413](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41708735413) **PASS**, installing 1.6.2 **only inside CI**, with the baseline source file still pinned to 1.6.0 in the repository. Five two-commit full-MCP configurations passed, including restart, graph-symbol oracle, source file reads and preserved base-store sentinel:

| Variant | Second-commit index work | SQLite seed backup | Filesystem unique allocated blocks | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Full index | **2,591 ms** | — | **8.77 MiB** | Unseeded, no dedup/pruning |
| Seeded incremental | **1,262 ms** | **64 ms** | **8.77 MiB** | Faster measured worker work, nearly same allocated size |
| Source hardlink dedup | **1,674 ms** | — | **8.14 MiB** | Distinct fresh index, retained source blocks shared |
| Seed + source dedup | **1,299 ms** | **55 ms** | **8.13 MiB** | Independent compute and retained-byte optimizations |
| Seed + source dedup + per-snapshot `.git` pruning | **1,145 ms** | **171 ms** | **7.89 MiB** | Best allocated storage in this single run |

The underlying source includes 160 synthetic TS modules. **Do not attribute the timing differences of independent matrix jobs solely to the toggles**: GitHub CI load, cold/warm OS caches and process scheduling vary. These are one-shot measurements that motivate the **subsequent three-round alternating benchmark**, not an established percent gain. Dedup/prune reduced unique physical allocation by roughly **10%**; it did not remove the dominant CodeGraph SQLite indexes. The seed itself was not a meaningful retention-storage optimization.

The package-lock version in this branch remains 1.6.0; 1.6.2 was explicitly installed in ephemeral CI runtime, and compatibility was checked against the **actually running CLI**. This is an engine-version acceptance probe, **not** a completed pin change or deployable release.

## Failure boundaries and pending work

A separate follow-on workflow added **15 alternating MCP fixtures (5 variants × 3)**, includes offline index compression roundtrips, reports allocated/unique blocks, and uploads then downloads its evidence artifact with a byte-for-byte check. This is **PENDING** until that CI completes; no median reported yet. A GitHub upload/download check will demonstrate retrieval correctness but **not** independent long-term retention outside GitHub's 30-day artifact policy (`ARCHIVE_NOT_VERIFIED`).

Critical remaining work before promotion: exact 1.6.2 package/lock pin in an isolated development branch, complete regression-suite execution at that pin, fresh-store cutover/rollback procedure with protection of old 1.6.0 graphs, active non-test repository verification, binary/config/extraction identity beyond the semver only, symlink path race hardening and independent durable archival of raw CI evidence. The established 1.6.0 Go lost-14-edges failure remains a required negative regression, **not** an accepted implementation.

## Later completed qualification: repeated optimization, exact lock and real MCP

**15 alternating optimization trials:** [run 41709276669](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41709276669) PASSED all 7 jobs. The repeated two-commit 160-module TypeScript experiment compared these median measured index + backup times and unique allocated disk:

| Path | Median index work | Unique disk | Median total MCP test |
| --- | ---: | ---: | ---: |
| Clean rebuild | 1,116 ms | 8.77 MiB | 6.46 s |
| Seeded reuse | 875 ms | 8.77 MiB | 6.51 s |
| Source dedup | 1,104 ms | 8.14 MiB | 6.68 s |
| Reuse + source dedup | 903 ms | 8.13 MiB | 6.41 s |
| Reuse + dedup + per-snapshot Git pruning | 866 ms | 7.89 MiB | 6.48 s |

Combined measured index work was about 22% lower and unique storage about 10% lower than clean baseline, but **overall MCP test duration did not significantly improve**. The CodeGraph SQLite component still occupies approximately 5.27–5.29 MiB allocated. These are small synthetic trials and do not prove large production savings.

The experiment uploaded a 15-trial JSON artifact to GitHub Actions, downloaded it into a separate directory, verified byte-for-byte equality and checked trial counts; SHA-256 **44975020668be4b04205e599693ba6be16d92aed49d84e7d520384fb75704cc1**. That qualifies GitHub upload/read-back but does not provide an independent durable archive or Backblaze B2 read-back; classification remains **ARCHIVE_NOT_VERIFIED**.

**Pinned 1.6.2 development dependency:** [CI 41710228986](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41710228986) generated a real npm-resolved package and lockfile, checked clean npm ci and version-scoped/MCP seed recovery, then committed both exact 1.6.2 dependency files to the separate development branch. [Initial red CI 41709973587](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41709973587) arose because the historical-source checker counted generated npm node_modules as unexpected recovered source. Its fix excludes only that dependency directory, retaining byte-level verification of all recorded historical sources and explicit modifications. Original failed run retained.

**Expanded pinned runtime acceptance:** [CI 41710699811](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41710699811) **PASSED all 5 jobs**: 44 security/transport/registry/source/storage/WAL/crash unit tests plus HTTP MCP/auth smoke; clean and seeded version-scoped two-commit MCP including restart; SHA-256 Git-object-format indexing; adversarial actual MCP restart with an old-engine ready manifest rejected by repo_open, repo_explore and repo_read while repo_status remained factual; and real public unjs/ofetch live transport/index/read/explore using pinned Git SHA 1dbc37fd1ceab832fc7c90cad81b1091c95ba563. This is stronger than a synthetic CLI-only test but not a production-agent performance proof.

Development PR stack: [#28 version isolation](https://github.com/rock-solid-sites/ases-plugins/pull/28), [#29 optimization benchmark](https://github.com/rock-solid-sites/ases-plugins/pull/29), [#30 exact pinned 1.6.2/runtime acceptance](https://github.com/rock-solid-sites/ases-plugins/pull/30). All are draft, unmerged and undeployed.

**Outstanding production blockers:** plan a safe cutover and rollback for conversations holding old snapshot IDs; preserve old 1.6.0 indexes and an old-engine read route until clients have transitioned; calculate temporary storage peak when two complete engine scopes coexist; further test sustained writer/OOM/crash boundaries, symlink-replacement races, and larger real repositories; decide whether raw source-only reads should remain accessible under a mismatched index engine without weakening graph rejection; independently archive CI evidence with durable read-back. No existing snapshot was migrated or deleted, no B2 operation occurred, and no default-on cache policy is justified.
