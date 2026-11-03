---
date: 2026-11-03
type: ASES development rollout and rollback proposal
status: NOT EXECUTED; requires operational preflight and explicit production approval
scope: cgrmcp CodeGraph 1.6.0 to 1.6.2
---
# cgrmcp CodeGraph 1.6.2 scoped cutover and rollback gates

**Authority:** a plan, not a deployment order. [Development PR #30](https://github.com/rock-solid-sites/ases-plugins/pull/30) is unmerged. [ASES evidence](cgrmcp-engine-scope-migration-results-2026-11-03.md) establishes exact pin, version-isolated registries, fail-closed mismatched-ready routing and bounded sampled benefits. The 1.6.0 Go fzf lost-14-edges failure remains a negative regression.

## Preconditions

1. Enumerate actual cgrmcp host, systemd/container process, running executable SHA-256 and `--version`, root, environment flags, API endpoint, open chats/snapshot IDs, repository/commit usage and available allocated/free GiB. Do **not** confuse cgrmcp's sandbox store with the user's development VPS without verifying deployment identity.
2. Snapshot and independently verify the current legacy store **without deleting or changing it**. Preserve manifest, by-id registry, Git source and CodeGraph SQLite databases. A live WAL database requires an online backup or a fully quiescent archive, not raw file copying.
3. Calculate safe temporary headroom for **both** old and fresh 1.6.2 store roots, mirrored source trees, staging and temporary restored SQLite pages; compare with cgrmcp's configured disk-admission floor. Do not claim source dedup across different version scopes unless it has been measured and qualified.
4. Pin and inspect exact package/lock, Node runtime, actual binary/version, extraction metadata and the intended versioned-store root. No custom executable override under the experimental scoped/reuse flags. Keep source dedup/prune/reuse disabled initially to isolate correctness from optimizations.

## Development acceptance then cutover

5. Start an independent development service pointing only at a fresh `engine-scopes/codegraph-v1.6.2` root. Clean-index representative exact existing Git commits; **never copy, relabel or rename 1.6.0 SQLite into the new scope**.
6. Check every target snapshot's manifest identity, completed state, engine.version and actual built-with/extraction data, source-file readbacks and complete CodeGraph query/caller/edge checks against clean 1.6.2 indexes, including the pinned fzf 14-edge negative regression case. Include Git SHA-256 and live remote transport.
7. Replay all four MCP tools, concurrent clients, long-lived sessions, interrupted index work and restarts. Deliberately insert a wrong-engine ready manifest and prove repo_open/repo_explore/repo_read fail closed. Verify repo_status does not falsify historical metadata.
8. Test source dedup, Git metadata pruning and incremental reuse separately and then together, using unique allocated disk blocks and total task time. Preserve 1.6.0 Go negative results and full 1.6.2 graph-parity gates; do not enable reuse solely from a green status output.
9. Provide a transition policy for **old conversation snapshot IDs**, which are scoped to the previous store registry. Retain an old-engine read route until clients have moved or until a formally agreed retention deadline. Never silently reroute an old ID to an unrelated 1.6.2 index.
10. Only after operator approval, change the active endpoint or runtime target to the versioned service. Monitor real query parity, task-level latency, RSS, SQLite/WAL errors, disk admission and error taxonomy. Keep old service/data recoverable during the acceptance window.

## Stop, rollback and evidence

- On any missing edge, stale engine graph served, increased error rate, inaccessible legacy IDs, failed disk-admission or invalid source manifest, stop promotion and revert routing to the old service **without mutating either store**. Versioned paths make rollback a routing/config decision, not an index downgrade.
- Retain all original failures and decisions; publish raw CI evidence and verified read-back at a durable independent destination before treating evidence retention as closed. The existing 30-day GitHub Actions artifact read-back is insufficient for a long-term ASES evidence archive.
- Storage consolidation, cold Brotli/gzip SQLite archive and Backblaze B2 upload/download/delete are **separate** experiments; their timing, correctness, provider credentials and restore tests are NOT_RUN in this round. No deletion of live or historical ready snapshots without verified replacement and explicit operator approval.

**Open question for next test round:** Can a read-only cross-version *source-only* retrieval path preserve historical chats' raw file access while refusing all stale CodeGraph exploration? Current implementation deliberately blocks both in an incompatible shared store; separate old-engine serving remains the simplest safe initial rollback design.
