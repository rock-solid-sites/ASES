# cgrmcp operational continuity and archive qualification — preregistration

Date: 2026-11-03. Status: PROSPECTIVE before this qualification CI. Scope: separate development-only branch stacked on pinned CodeGraph 1.6.2 PR #30. No production VPS connection or write authorized by this experiment.

### Why this round exists

Index reuse, source deduplication, `.git` pruning and a version-scoped 1.6.2 store passed bounded correctness tests. The remaining operational risks are a user's old snapshot IDs becoming unavailable, temporary disk pressure while old/new stores coexist, interruptions while backing up SQLite, archive tampering, and missing independent retention. Existing source must never be migrated by simply copying 1.6.0 CodeGraph index bytes into 1.6.2.

### Precommitted competing hypotheses and minimum discriminating tests

| ID | Hypothesis / risk | Test | Falsifier or blocked conclusion |
| --- | --- | --- | --- |
| M1 | Old and new snapshot IDs are namespace-local; a dual-service handover may preserve access without unsafe ID remapping. | Start independent old/new runtime instances against separated roots, index same Git revision in both, query old ID against each and assert new-store never routes to old index; legacy endpoint remains valid. | Old ID unexpectedly accesses wrong engine, or prior service unable to resolve it |
| M2 | Disk preflight can report planned coexistence correctly without claiming a precise future growth forecast. | Read-only manifest inventory + actual unique allocated store footprint + statfs, clear MiB/GiB display, conservative configurable headroom and forced negative controls; run on isolated old and new roots. | Writes during dry run, symlink following, misleading available-space claim or passing a simulated insufficient-disk case |
| M3 | Abrupt termination during real SQLite backup does not corrupt the source or make an incomplete snapshot ready. | SIGKILL real backup subprocess on a large WAL-active source; check source hash/quick_check, partial staging invalidation, fresh backup retry and restore, no ready manifest publication. | Source changed unexpectedly, false readiness, corrupted retry, symlink or unbounded child survival |
| M4 | Concurrent WAL writer/reader overlap remains consistent under repeated backups. | Several read-only backups at staggered intervals against one independent WAL writer, SQLite quick_check and gap-free transaction sequence, 1.6.2 scoped worker controls. | Missing committed rows, non-monotone snapshots, indefinite lock, corrupted source or writer |
| M5 | A cold snapshot archive can be created and restored without an existing store's registry being overwritten. | Portable snapshot-scoped archive with SHA-256 manifest, filename/path validation, verify-before-import, wrong version rejection, interrupted/truncated/tampered archive tests; restore into *new* empty store only. | Invalid or partial restore appears ready, existing manifest overwritten, corrupted archive passes, filesystem traversal |
| M6 | Temporary GitHub CI evidence can be uploaded/downloaded and hashed; durable B2 requires real authorized credentials/bucket. | Test offline artifact roundtrip and S3-compatible adapter against a local mock; do not claim remote B2 success without authenticated readback. | Claimed external archive without real verification; unexpected storage deletion |

### Frozen boundary decisions

- A read-only preflight never deletes, modifies or freezes a running service. The production filesystem location is not inferred from repo paths or user memory; access to the actual host/provider must be established explicitly.
- Preserve old snapshots and a route to the original engine for long-lived sessions; do not silently redirect a colliding commit-only ID across engines. Source-only bridging to legacy stores is optional, guarded, and separate from graph exploration.
- Archive means only a portable verified backup, not live eviction. Never erase an index on evidence of a compressed copy alone; remote B2 upload, download, credentials, retention, cost and restart are separate gates.
- Require exact CodeGraph producer/extraction identity when restoring an indexed snapshot. Do not merge a whole by-id registry into a populated store. If mixed-version store cannot be made safe without a broader identity redesign, keep separate engine scopes.
- Record all failed and passing CI runs separately; don't convert environment failures into model correctness. Compare total elapsed time and storage with measured values; no CPU, RAM or electricity savings without direct instruments.

### Stop conditions

Any unexpected legacy mutation, symlink escape, cross-version graph served, incomplete SQLite published ready, archive path traversal, evidence write to production, or uncontrolled storage deletion stops promotion. Final deployment, remote B2 read-back and active session cutover remain BLOCKED until their prerequisites are actually accessible. This proposal is local evidence-method application, not a global ASES Kernel-0 or Processor rule.