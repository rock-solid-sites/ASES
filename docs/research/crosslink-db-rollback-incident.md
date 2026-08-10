---
title: Crosslink DB Rollback Incident
program: EDASES
layer: Research
document_type: Incident Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:

* Documentation Standard

consumed_by:

* Future agent sessions
* #125

last_updated: 2026-08-03
---

## Primary Source

Primary source: tripn-astro .crosslink/.knowledge-cache/crosslink-db-rollback-incident.md (contributor 4Adb). This record converged on ASES issue #125 (Crosslink hydration/sync state-integrity) — same failure family: sync.fetch() rehydrating SQLite from a stale hub checkpoint, dropping local-only issues.

## Crosslink DB Rollback Incident (2026-08-02)

### What happened
Mid-session, the Crosslink issue database reset to a June-era state. All July/August issues created since the last hub push (#338, #342, #370-376, #378) became unresolvable: 'Issue #N not found' for every one, even ones just used successfully seconds earlier.

### Root cause evidence
- .crosslink/.hub-cache/checkpoint/state.json shows next_display_id: 1, display_id_map: {}, watermark 2026-06-09T12:18:00 — the hub checkpoint is a June 9 baseline.
- crosslink sync re-hydrated the local SQLite from this stale hub, discarding local-only issues that had never been pushed to the hub.
- The July/August issues were LOCAL-ONLY: created after the last hub sync, never pushed to the crosslink/hub branch.
- crosslink integrity layout/schema/hydration/counters all PASS after reset — the DB is internally consistent but the WRONG dataset. Repair flags cannot resurrect issues the hub does not know about.

### Trigger
A 'crosslink sync' run during pre-flight (before reviewer retry) re-hydrated from the stale hub branch. The Landing kickoff dispatched against #338 succeeded because the local DB still had it; seconds later the OG kickoff against the same ID failed because the re-hydration had already swapped the dataset. The DB swap was noticed because two consecutive --issue 338 dispatches behaved differently.

### Impact
- #370 (Seaside Properties dropdown): builder commit 97677c8b + reviewer PASS (posted 18:09) are SAFE in git/hub history. The issue registration and its close are lost from the tracker.
- #338 fan-out (Landing/OG/PB/CZ): halted. Landing agent 9Lg8-5XrZ killed (no commits; bound to phantom #338).
- #342, #372-376, #378: registrations lost from tracker.
- No code was lost. All builder/reviewer work lives in git commits and branches.

### Lessons
1. Do NOT run 'crosslink sync' casually mid-session when local issues may not yet be pushed to the hub. Verify hub is up-to-date first (or push local state) before syncing.
2. Treat .kickoff-status flags as LIES: a review agent that posts its review to the issue and never flips its flag is DONE, not stalled (this session's first reviewer 9Lg8-N96w had actually PASSED at 18:09; the stall diagnosis was wrong).
3. Check the ISSUE COMMENT TRAIL (the artifact) before declaring an agent stalled, not just status flags.
4. Review timeouts should be short (a review of one file + build finished in ~2 min). 30m is far too long for a review.
5. Model discipline: --model opus/sonnet/haiku hard-fail; verify against 'opencode models' (live catalog) before every launch; builder = opencode-go/deepseek-v4-flash, reviewer = opencode-go/mimo-v2.5 (both verified).
6. Prove serially, then fan out. The dropdown pattern WAS proven on Seaside (passed build+review), so fan-out was justified — but fan-out must not proceed when the tracker is unstable.

### Recovery state for next session
- Git branches: feature/9Lg8-SXUW-add-a-properties-dropdown-to-the-seaside-navigation (commit 97677c8b) holds the proven Seaside dropdown work.
- Tracker needs re-creation of: nav dropdown issue (#338 work), #342, #372-376, #378, and re-registration of the Seaside dropdown work.
- Recommended next step: operator recovers local-only issues from git reflog/backup, OR re-creates them in the current DB, THEN resume fan-out.
