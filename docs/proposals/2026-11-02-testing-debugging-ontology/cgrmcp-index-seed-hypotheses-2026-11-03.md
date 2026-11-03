---
title: cgrmcp Indexed-Snapshot Reuse — Development Hypotheses (2026-11-03)
program: ASES / EDASES
document_type: Pre-execution experiment addendum
status: Research; opt-in local trial; NOT production acceptance
prerequisite: codegraph-incremental-recomputation-results-2026-11-03.md
date: 2026-11-03
---
# Indexed-snapshot seed and failure recovery — frozen expectations

**Recorded before the new seed-manager implementation and CI tests.** The earlier synthetic CodeGraph 1.6.0 experiment found correct warm/cold graph parity across seven source-change states, and one successful cross-checkout reuse case. The existing cgrmcp production behavior nevertheless creates a fresh index for each immutable commit. The objective here is to learn whether a **bounded, reversible seed optimization** is safe enough to warrant a larger follow-up, not to merge it or claim production readiness.

## Why test this?
Reusing indexes can avoid redundant parsing, but doing so incorrectly can silently corrupt cross-commit graph answers, mutate existing published evidence, or copy a SQLite file while a WAL writer is active. The previous test copied an offline 2.5 MiB index and matched a clean rebuild; it did not address live snapshot concurrency, provenance, invalid seed versions, crashes or fallback. SQLite's online backup facility should permit consistent copies even when the source has WAL, but it must be qualified with positive and negative controls. The expected efficiency is *not* assumed to generalize from one timing.

## Competing hypotheses and pre-run discriminators

| ID | Hypothesis / threat | Predicted distinguishing evidence |
| --- | --- | --- |
| S1 | Copying a ready same-repository snapshot index with matching engine/extraction version and healthy database permits correct incremental sync | Two commits: opt-in seeded second index matches clean reference on known source symbols and edges, and older snapshot hash stays unchanged |
| S2 | A seed from a different repository, failed manifest, same commit, incompatible version, or corrupt DB may be reused incorrectly | Negative controls: no seed selected; unmodified stage clean-init succeeds; explicitly logged selection/fallback reason |
| S3 | Uncheckpointed SQLite WAL and concurrent readers make filesystem copying unsafe | Use SQLite's online backup from a read-only connection, with a WAL-bearing source and separate active reader; byte-exact original state and consistent copied DB; if unavailable, choose clean init |
| S4 | A partial copy or runtime exception can leave a poisoned stage that looks complete | Inject copy/backup failure before index start; remove partial seed, return clean-init behavior and publish correct result; never relabel a poisoned stage 'ready' |
| S5 | Fast sync can conceal stale edges or return a misleading status | Independent fresh index and direct source-fact oracle for added/renamed/deleted/export changes; compare full caller sets (explicit non-truncating limits) |
| S6 | Reuse is beneficial once backup, compatibility checks and fallback costs are included | Measure seed time, incremental time, clean reference time, index block footprint, and secondary overhead; no blanket speedup claim without repetitions |
| S7 | A compatible seed is unavailable or invalid after a CodeGraph version/extraction change | Fail closed to clean build and retain the original complete snapshot; do not silently use old engine metadata |

## Selected method, costs and stop conditions
Use isolated GitHub Actions test stores with a disabled-by-default `CGRMCP_REUSE_INDEX=1`. Keep published snapshots immutable and identified by their own SHA; seed only the new mutable stage. Prefer node:sqlite online backup rather than `fs.copyFile` of a live DB; Node 22.16+ exposes backup; if runtime lacks it, no reuse is attempted. Bound candidate DB size and backup work; never hardlink DBs, and exclude WAL/SHM/locks from the stage. Verify SQLite integrity of the backed-up DB before sync. A wrong-version/corrupt seed must fall back cleanly, and a broken incremental result must never publish without a recognized complete state.

Do **not** interpret clean status as proof of graph correctness: use an independent fresh-index and source-fact oracle. Existing native CodeGraph 1.6.0 failures of truncated 20-item caller output are retained as instrument incidents; request complete result limits here. Capture PASS, FAIL, BLOCKED and NOT_RUN separately. The target experiment is bounded; no VPS, Backblaze, archive deletion, or broad repository scan is permitted.

**Acceptance for further experiments only:** valid neighboring clean and seed paths both pass, invalid seeds do not become ready, original snapshots remain byte-unchanged, and a retained failure record supports any fallback. Any observed graph discrepancy, source mutation, unbounded backup or destructive fallback blocks promotion. CI links do not equal verified durable evidence: `ARCHIVE_NOT_VERIFIED` until independent read-back.

**Authority:** experimental proposal methods are selectively applied, not promoted to ASES-wide governance. The user approved developing the next isolated slice, not production cutover or new remote storage side effects.
