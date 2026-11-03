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
