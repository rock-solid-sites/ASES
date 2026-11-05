---
date: 2026-11-05
type: ASES experimental results, retrospective after CI
status: development-only: five green workflows; production cutover and real B2 unverified
baseline: cgrmcp pinned CodeGraph 1.6.2, draft PR #30
experiment: cgrmcp operational continuity / versioned IDs, draft PR #31
preregistration: cgrmcp-operational-continuity-archive-preregistration-2026-11-03.md
---

# cgrmcp operational continuity and archive — observed acceptance

**Chronology:** The prospective [continuity and archive preregistration](cgrmcp-operational-continuity-archive-preregistration-2026-11-03.md) was committed on November 3 before implementing the test suite. [Public snapshot-ID collision hypotheses](cgrmcp-versioned-snapshot-identity-preregistration-2026-11-03.md) were committed separately before their implementation and subsequent positive/negative tests. This **results record was committed later, November 5**, after the previous chat output was interrupted; it does not change any prospective hypothesis.

**Code branch:** [draft PR #31](https://github.com/rock-solid-sites/ases-plugins/pull/31), based on earlier [draft #30](https://github.com/rock-solid-sites/ases-plugins/pull/30). All are unmerged. Tests ran in isolated GitHub Actions runners; they did not run on the VPS or access an actual Backblaze bucket.

## Final confirmed evidence (November 3, 2026)

| Discriminating test | CI run | Result | What the test shows |
| --- | --- | --- | --- |
| Read-only migration inventory | [41718127696](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41718127696) | PASS | Six preflight controls, five engine-scope compatibility controls and two older concurrency/crash controls, all green. Old ready snapshots remain byte-unchanged; simulated no-space, invalid registry, cross-version ID collision and symlink paths are rejected. |
| Two actual simultaneously running MCP endpoints | [41718127659](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41718127659) | PASS | Real CodeGraph **1.6.0 legacy** and **1.6.2 scoped** binaries both index, read and explore the *same pinned Git commit*. Public IDs are now different; each rejects the other's ID; old DB SHA-256 stays identical. |
| Bounded archive + genuine MCP restore | [41718127634](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41718127634) | PASS | Five archive integrity/negative unit tests; index exported using SQLite online backup into an approximately **251 KiB** gzip containing **43 members**, restored into a new empty engine-scoped store with checksum/version/extraction/ID checks. A separate MCP server can read and explore that restored index without a local Git mirror. |
| Native backup crash and WAL | [41718127547](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41718127547) | PASS | SIGKILL after real backup progress against a **11.9 MiB** SQLite source: original bytes unchanged; partial stage purged, indexing manifest failed with attempt preserved, verified backup retry has **2,700 rows**. Four simultaneous WAL backups captured consistent **29, 33, 35 and 35-row** committed prefixes, writer completed **400** rows. |
| Backblaze B2 Native API v4 adapter | [41718127604](https://github.com/rock-solid-sites/ases-plugins/actions/runs/41718127604) | **MOCK PASS; REAL NOT_RUN** | Mock provider accepts scope-restricted authorization, upload and readback by file ID; SHA-1/SHA-256 verified. Wrong permissions, host, data or object path fail. Real B2 credentials, bucket upload and remote read-back **not tested**. |

All five cited workflows reached a green conclusion at the same branch revision, prefix `bee0b820`. Earlier failures, including a wrong test assertion that expected only an engine mismatch but encountered the stronger *scoped identity mismatch*, remain visible in the historical CI record. The test was corrected to accept either fail-closed denial; the actual assertion that wrong-version archive cannot be restored was not removed.

## Hypotheses and decisions

**M1 and I1–I4, session continuity and identities:** SUPPORTED for two local simultaneous MCP instances. Previous `snapshot_id` combined repository, Git commit prefix and truncated URL hash, so two otherwise separated engine stores could expose an identical public identifier. That is a dangerous cross-version routing ambiguity. An opt-in versioned store now creates IDs with a 10-hex digest of the CodeGraph producer version in the prefix while retaining the required 12-hex SHA/6-hex URL suffix and frozen ID character grammar; unscoped legacy stores retain their original ID algorithm. Both actual servers refused the opposing ID. No automatic translation or silent change of old IDs. **This supports retaining old endpoint access for old conversations, but does not provide a production session router**.

**M2, disk admission:** SUPPORTED only as a conservative read-only *preflight instrument*, not proof that peak indexing fits. `migration-preflight.mjs` enumerates store manifests, registry versions, source/ready counts and allocated storage, checks an independent scope, and displays sizes in MiB. Under the fixture's 128 MiB Git mirror cap, the bounded 3× mirror + 512 MiB heuristic is **896 MiB**. The separate coexistence reserve uses max(floor, 1.5× observed legacy unique allocation + 512 MiB); **not** a guaranteed bound on checkout, SQLite growth or dual-store peak. The actual host's free space and existing snapshot inventory remain NOT_RUN.

**M3/M4, crash and repeated WAL:** SUPPORTED for observed stress cases. Source hash, SQLite quick_check and contiguous sequences survived the native in-progress backup kill; the interrupted staging record never became ready; a later normal backup worked. Four simultaneous online-backup consumers under a live WAL writer returned consistent committed prefixes and no writer failure. No proof for arbitrary instruction-boundary crashes, OOM, sustained multi-hour write contention or multiprocess registry races.

**M5, cold archive:** SUPPORTED for *one small synthetic fixture and a real MCP reopening*. `snapshot-bundle-export.mjs` exports source plus a bounded SQLite online backup, excludes the Git mirror, and never deletes anything. `snapshot-bundle-restore.mjs` requires detached SHA-256 and exact versioned ID, manifest engine/extraction identity, per-member hashes and SQLite quick_check, and only accepts a new empty destination. Negative tests reject wrong hash, missing metadata, symlink, duplicate members, path traversal, wrong engine and populated destination. A partially interrupted restore may leave an unreferenced published snapshot if a later manifest/registry publication fails; there is no automatic remote recovery or eviction. The **archive is local and temporary**, not an independent durability guarantee.

**M6, B2 retention:** MOCK PASS; real service NOT_RUN. The adapter follows the Backblaze B2 v4 native authorization, bucket upload URL, upload receipt and download-by-file-ID pattern with hash verification and a no-delete API. A test stub validates protocol behavior only. Real B2 bucket restrictions, provider-specific failures, remote billing, latency, upload and independent read-back, retention settings and restore from remote bytes require an authenticated Backblaze connection and an explicit destination. **ARCHIVE_NOT_VERIFIED** externally. Do not claim archived evidence.

## Recommendations and remaining blockers

1. Preserve the [draft #31](https://github.com/rock-solid-sites/ases-plugins/pull/31) atop the rest of the development stack. Do not merge into production, delete old snapshots, or enable any automatic archive eviction. Preserve the 1.6.0 missing-14-Go-edges negative fixture.
2. The next production prerequisite is **actual host/store identity**: active cgrmcp binary and version, root, free/allocated GiB, number of old snapshots, live session and endpoint layout. No such host was inspected by these workflows. Execute the read-only preflight only against the confirmed target after approval.
3. Before a live cutover, verify old 1.6.0 requests remain pinned to their old service, 1.6.2 requests use versioned IDs and fresh clean indexes, preflight has adequate *observed* peak headroom, and full rollback can restore prior endpoint routing without rewriting any store.
4. For durable independent archive qualification, supply or connect a Backblaze B2 application key restricted to one specific bucket/prefix with `writeFiles` and `readFiles` permissions, and select its bucket ID. Use an isolated test object; retain detached checksum and download evidence. The assistant has not received B2 credentials or selected a real bucket and therefore cannot truthfully complete real read-back.
5. Remaining engineering risks: symlink replacement race between path validation and file operations, live SQLite file-size limits, large representative cross-language repos, high-load concurrent writer/reader behavior, and crash after snapshot rename before by-id registry publication. These require further focused testing before production promotion.

**General ASES insight:** a producer version belongs in the *public address of a derived result* (not just its backing directory) when clients can retain result references across independent endpoint cutovers. The evidence here concerns cgrmcp specifically and does **not** establish a global Processor policy.

**Status:** five local GitHub Actions workflows passed; no production cgrmcp process or stored snapshot was changed; no real Backblaze B2 request was issued.
