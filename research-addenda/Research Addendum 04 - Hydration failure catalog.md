# EDASES Research Addendum 04

## Crosslink Hydration / Sync State-Integrity Failure Catalog

> **Canonical reference document** for the crosslink hydration/sync
> state-integrity failure family. This catalog consolidates every observed
> failure mode, its symptom, root-cause area, current status, and recovery
> path, so future agents have a single source instead of scattered notes.
>
> Sources folded in: Research Addendum 03 (uuid-sync bug), `.crosslink/knowledge/crosslink-fork.md` Known Issues, issue #125 consolidated state-of-knowledge comment (2026-08-03 17:52) and subsequent findings (2026-08-03 through 2026-08-06), issue #208 result, `session-handoffs/Session Handoff 3.md`, `CHANGELOG.md` honest note, and the tripn-astro crosslink-db-rollback incident record.
>
> **Status of the family:** **root cause RESOLVED 2026-08-06** — the safe
> re-hydration guard landed in the crosslink fork (commit `ade6146b`, binary
> rebuilt and live-verified): `maybe_auto_hydrate` gates the destructive v2
> file path on confident v3-ref presence (`hub_is_confidently_v2_only`,
> fail-closed), so a stale hub projection can no longer wipe agent-authored
> rows. Prior fixes: #119 (code-level trap), #166 (lock persistence), #207/#125
> (SSH event push). Remaining: the hub's reduced `issues/` projection rebuild
> (2.9), tracked by #125 (open), epic #157, and this catalog's sub-issue #126.

---

## 1. Core mechanism

`crosslink sync` re-hydrates the local SQLite DB (`issues.db`) from the hub
state (hub branch / hub-cache). The local DB is a **projection**; the hub is
supposed to be the source of truth. When the hub or hub-cache is stale —
or when local issues were never pushed to the hub — the sync path has **no
safe guard for "local ahead of hub"**, so local-only issues are dropped,
remapped, or become unresolvable.

Two independent root causes feed the family:

1. **The hub cannot be updated** (gh-auth event-push failure, #207 family) —
   so the hub stays a stale baseline and every re-hydration pulls it back.
   Fixed 2026-08-06 by switching the origin remote from HTTPS to SSH.
2. **The sync/hydration path has no concurrency guard and no local-ahead-of-hub
   protection** — concurrent kickoff launches each trigger their own
   hydration, racing the main-repo DB; a casual `sync` at the wrong moment
   rolls the projection back.

> **STATUS 2026-08-06:** the unguarded auto-hydration root cause is
> **RESOLVED** — the safe re-hydration guard landed in the crosslink fork
> (commit `ade6146b`, binary rebuilt, gate live): `maybe_auto_hydrate` runs
> the destructive v2 `hydrate_to_sqlite` path only when
> `hub_is_confidently_v2_only` (meta + checkpoint refs absent AND v2 branch
> present); any doubt — including a concurrent-launch git race — fails closed
> to a skip, so the stale `issues/` projection can no longer wipe
> agent-authored rows. The historical failure modes below remain accurate for
> pre-`ade6146b` binaries; `crosslink compact` (playbook §6.5) remains the
> interim recovery for them.

Recovery (validated in two independent incidents): **`crosslink compact`** —
see playbook §6.5 (Hydration Recovery). This catalog does not duplicate the
procedure; agents should follow §6.5 for the actual recovery steps.

---

## 2. Failure-mode catalog

Statuses referenced: **#119** closed, **#125** open, **#142** open,
**#167** open, **#208** done (recovery doc merged to main, 7056cc7).

### 2.1 June-era rollback

- **Symptom:** mid-session, the issue DB resets to a June-era state. All
  issues created since the last hub push resolve as `Issue #N not found` —
  even ones used successfully seconds earlier. Checkpoint evidence:
  `next_display_id: 1`, `display_id_map: {}`, watermark `2026-06-09`.
- **Root-cause area:** `sync.fetch()` re-hydrates the SQLite DB from a stale
  hub checkpoint. Local-only issues (never pushed) are dropped. Observed
  identically in tripn-astro (2026-08-02, #338/#342/#370-376/#378) and ASES
  (2026-08-06, #206/#208 mid-session rollback to the June-23 4-issue set).
  Underlying enabler: the hub could not advance past its baseline (see 2.8).
- **Status:** **RESOLVED 2026-08-06** for the unguarded auto-hydration root
  cause — fail-closed gate on v3-ref presence, fork commit `ade6146b`, binary
  rebuilt + live-verified; the June-baseline wipe path is now inert (stale
  files no longer trigger hydration). Historical occurrences (tripn-astro
  2026-08-02, ASES 2026-08-06 #206/#208) predate the gate; pre-fix binaries
  remain vulnerable and should use the compact recovery. #125 open (family),
  #142 open (mechanism verification — which ref hydration reads, and why
  hub-cache lands on the wrong ref), #208 done (recovery documented).
- **Recovery path:** `crosslink compact` → `crosslink sync` → verify
  (playbook §6.5). If compact does not restore, re-create active issues from
  hub agent refs (`git show refs/heads/crosslink/agents/<id>/events.log` —
  `IssueCreated` events carry full content). Never blind-sync repeatedly.
  Note: after hub checkpoint advance, display ids may be reassigned — verify
  before posting to a recovered issue (2026-08-06 #206→#208 incident).

### 2.2 Mid-session "not found" drops on concurrent kickoff launches

- **Symptom:** after (or during) a kickoff launch, `crosslink issue list`
  shows only 3-4 legacy issues; hub issues resolve as `not found`; further
  kickoff dispatches fail with `Issue #N not found`. The launch itself
  succeeds (worktree + hub intact); only the main-repo DB view collapses.
- **Root-cause area:** each kickoff launch sequence runs its own hydration,
  which rewrites the main DB (DB mtime == launch time). Concurrent launches
  race; the loser's DB view is clobbered. First observed with #123/#124/#137
  (2026-08-03), recurring a third time 2026-08-04 (session #13: three clobbers
  at 06:23, 06:35, 06:45, each after a launch).
- **Status:** **RESOLVED 2026-08-06** for the destructive auto-hydration
  trigger — the fail-closed gate (fork commit `ade6146b`, binary live) skips
  the v2 wipe path on any doubt, including the concurrent-launch git race
  (catalog 2.2), so a racing launch can no longer clobber the main-repo DB
  view. #125 open (family). Sequential-launch mitigation (sync between
  launches) remains best practice.
- **Recovery path:** `crosslink sync` re-hydrates (181+ issues restored, all
  resolvable). Mitigation: launch agents **sequentially** with a sync between;
  do NOT race concurrent launches (see `agent-orchestration-playbook.md`).

### 2.3 Worktree comments invisible until explicit sync

- **Symptom:** an agent posts a review/result comment from its worktree; the
  main-repo DB and hub do not show it. Comment is local-only until a sync
  happens. Observed with #120/#121/#123 reviewers; tripn-astro #379 was
  misdiagnosed as stalled for the same reason (comment existed, DB didn't
  see it).
- **Root-cause area:** comments are written to the worktree's local store /
  agent ref; they do not reach the hub until an explicit `crosslink sync`.
  Visibility is therefore decoupled from liveness — a missing comment is not
  evidence of a stalled agent.
- **Status:** #125 open (documented rule); operational rule codified in
  playbook §6.5 (hub refs are ground truth).
- **Recovery path:** to verify agent output, read the hub agent refs
  (`git show refs/heads/crosslink/agents/<id>/events.log`) — no sync needed.
  Do NOT run `crosslink sync` in the main repo merely to "refresh"
  visibility: that is the rollback trigger (2.1).

### 2.4 uuid-sync quirk (0.9.0-beta.1)

- **Symptom:** every `crosslink sync` or `crosslink compact` reverts the
  SQLite issue UUIDs; `crosslink integrity` then reports
  `N sqlite-only issue(s)` because DB UUIDs no longer match the canonical
  JSON event log payloads.
- **Root-cause area:** sync/compaction update logic re-inserts issues without
  preserving historical UUIDs — generates fresh (or zeroed) UUIDs instead of
  reading the canonical `IssueCreated` payload. Bug report filed:
  `research-addenda/Research Addendum 03 - Crosslink 0.9.0-beta.1 uuid-sync bug.md`
  (draft for upstream).
- **Status:** #125 open. No code fix in the fork; workaround in use.
- **Recovery path:** re-run the uuid-sync SQL after each sync/compact
  (specific `UPDATE issues SET uuid = ...` statements in
  `session-handoffs/Session Handoff 3.md`; see also `scripts/audit_research_issues.py`
  for the analogous post-create pattern). Data is correct in both stores;
  only the integrity check misreports.

### 2.5 Display-id collisions

- **Symptom:** local-only issues collide with hub-assigned ids and get
  remapped to negative local ids (ASES 2026-08-03: 4 local-only issues
  collided with hub ids [1,2,3,4]) or to L-prefixed legacy ids (L1/L2/L3/L4
  from the pre-rollback 2026-06-23 hierarchy). A hub checkpoint advance can
  also reassign display ids to unrelated issues (2026-08-06: #206/#207 →
  #208+ mid-session).
- **Root-cause area:** hydration collision logic remaps local records to
  protect hub-assigned numeric ids; when the hub baseline is stale and local
  issues are ahead, the projection mangles identity.
- **Status:** #125 open. L-prefixed legacy issues intentionally left open
  (data preservation — they carry the pre-rollback research hierarchy).
- **Recovery path:** before posting to a recovered issue, verify the display
  id still points at the intended issue (posting to a reassigned id
  contaminates another agent's thread — see #208 meta-note, playbook §5.6).
  Do not delete/close legacy remapped records without operator direction.

### 2.6 Stale-lock steal inconsistency

- **Symptom:** `crosslink locks steal N` succeeds (ownership transfers per the
  lock command), but a subsequent `crosslink session work N` still reports the
  old holder and warns `Issue is locked by X but lock appears STALE`. Session
  runs, posts, and syncs normally, but lock ownership is inconsistent.
- **Root-cause area:** lock-table state and session-work claim logic disagree;
  staleness detection is unreliable because heartbeat hooks are not deployed
  in worktrees (#135 Phase 2 item), so the code defaults to warn-and-proceed
  rather than risk blocking a live agent.
- **Status:** #125 open; #167 open (wire the lock table into the
  crosslink-guard plugin so locks actually block — the plugin currently never
  consults the lock table). #166 resolved the persistence half (see 2.7).
- **Recovery path:** treat stale-lock warnings as non-blocking noise; proceed
  with the deliverable (recurring warnings were a documented agent-drift
  trigger — 2026-08-04 systemic-drift finding). After #166, locks can be
  cleaned via release/steal and the table is trustworthy.

### 2.7 Lock-persistence gap — FIXED (#166)

- **Symptom:** lock mutations do not persist — steal says success, release
  says not-locked, `locks list` keeps showing the stale locks (18 stale OL2r
  locks; 4 agent-held locks unremovable). Pre-`31a3e2e8` binary.
- **Root-cause area:** V3 lock-protocol defect in the installed binary;
  mutations never reached the lock table.
- **Status:** **FIXED and verified** 2026-08-04 — #166 (V3 lock-protocol fix,
  commit `31a3e2e8`) imported to fork-local/agents (commit `00e71b38`), binary
  rebuilt. Lock mutations now persist; `locks list` shows no active locks
  after cleanup. Removes the agent-drift trigger and unblocks #167.
- **Recovery path:** none needed post-fix. If stale locks appear again,
  verify the installed binary is post-`31a3e2e8` before attempting mutation.

### 2.8 gh-auth event-push failure — RESOLVED via SSH (2026-08-06)

- **Symptom:** crosslink's internal push of agent refs / hub updates fails
  with `gh auth git-credential: erase operation not supported ... Authentication
  failed`; events are "saved locally only"; the hub never advances past its
  baseline.
- **Root-cause area:** primary failure was a real auth failure — `gh` had NO
  stored credential (`gh auth status`: not logged in; `~/.config/gh/hosts.yml`
  empty); HTTPS push sent no credentials → GitHub 401. The `erase operation
  not supported` error was secondary noise after the 401 (verified by
  reproduction; fixing erase would not have fixed the push).
- **Status:** **RESOLVED** 2026-08-06 04:25 — ASES origin switched from HTTPS
  to SSH (`git@github.com:rock-solid-sites/ASES.git`); `ssh -T git@github.com`
  authenticates as rock-solid-sites (existing `~/.ssh/id_ed25519`). Verified:
  local and remote agent refs match at seq 929, no auth error. The concrete
  mechanism preventing hub updates ("events saved locally only") is gone.
- **Recovery path:** on a fresh machine, set both remotes to SSH:
  `git -C <repo> remote set-url origin git@github.com:<org>/<repo>.git` and
  the same for `.crosslink/.hub-cache`, then `crosslink sync` to flush
  locally-saved events. (Exact commands recorded on #125, 04:01 verdict.)

### 2.9 Hub reduced `issues/` projection still 4 June-era files (remaining #125 item)

- **Symptom:** the hub branch's reduced `issues/` projection contains only the
  4 June-era issues (commits 55991f4c/56547c9d/c8097b1a/f4919301). Every
  re-hydration pulls that 4-issue baseline back; locally-created issues are
  renumbered when the hub checkpoint advances (#206/#207 → #208+ observed).
- **Root-cause area:** the reduce/checkpoint projection was never rebuilt —
  distinct from the push-auth failure (2.8) which is fixed. The projection is
  the remaining #125 root-cause item feeding #157 (Hydration epic).
- **Status:** **wipe trigger RESOLVED 2026-08-06** — the unguarded
  auto-hydration that re-imported this stale projection is fixed by the
  fail-closed gate (fork commit `ade6146b`, binary live); the 4 June-era
  files are now inert for hydration. The projection **rebuild itself remains
  open** — #125 (remaining item), #157 (epic), #142 (mechanism verification).
- **Recovery path:** interim — the compact recovery (playbook §6.5) is the
  standing safety net. Definitive fix requires rebuilding the hub's reduced
  projection from the full event history so re-hydration imports the modern
  issue set (tracked by #125/#157; do not attempt ad-hoc in this repo).

### 2.10 Validated compact recovery path

- **Symptom:** main-repo DB re-hydrated to a stale baseline; local-only issues
  appear lost (any of the above scenarios).
- **Root-cause area:** n/a — this is the recovery procedure, not a failure.
- **Status:** **DONE** — validated in TWO independent incidents (tripn-astro
  2026-08-03, ASES 2026-08-06); documented repo-agnostically as playbook §6.5
  (merged to main 7056cc7, #208).
- **Recovery path:** **see `agent-orchestration-playbook.md` §6.5 — do not
  duplicate here.** Summary: `crosslink compact` → `crosslink sync` →
  `crosslink issue list`; do NOT blind-sync; if compact does not restore,
  re-create from hub agent refs, not from scratch.

---

## 3. Issue status cross-reference

| Issue | Title | Status | Role in family |
|---|---|---|---|
| #119 | Fix DB rehydration wipe during sync-fetch | **closed** | Fixed the `created_by IS NULL` filter trap + regression test. Family persists (operational stale-hub hazard unaddressed). |
| #125 | Hydration/sync state-integrity family | **open** | Parent tracking issue for the whole family; hosts the consolidated state-of-knowledge evidence. |
| #126 | Document: catalog hydration problems | **open** | This catalog's sub-issue. |
| #142 | Mechanism verification (which ref hydration reads) | **open** | Was stalled before verdict; needs resolution to answer "why hub-cache lands on wrong ref". |
| #157 | EPIC: Hydration — safe re-hydration + lock consistency | **open** | Session-scale workstream for consolidated root-cause fix. |
| #166 | V3 lock-protocol fix | **resolved** | Lock persistence fixed; imported + binary rebuilt 2026-08-04. |
| #167 | Wire lock table into crosslink-guard plugin | **open** | Makes locks actually block; needs #166's reliable lock table. |
| #208 | Document validated hydration recovery | **done** | Playbook §6.5 merged to main (7056cc7). |

---

## 4. Operational rules (distilled from the evidence)

1. **Hub agent refs are ground truth**, not the main-repo SQLite DB.
   Verify agent output via `git show refs/heads/crosslink/agents/<id>/events.log`
   — no sync required.
2. **NEVER run `crosslink sync` in the main repo to "refresh" visibility** —
   that is the rollback trigger (2.1).
3. **Recover visibility with `crosslink compact`** (playbook §6.5), never a
   blind re-hydration.
4. **Launch agents sequentially** with a sync between; concurrent kickoff
   launches race the main DB (2.2).
5. **Stale-lock warnings are non-blocking noise** — proceed with the
   deliverable; do not investigate lock mechanics mid-task (2.6, 2.7).
6. **Liveness and data-visibility are separate failures** — check the comment
   trail on the issue before declaring an agent stalled (2.3).
7. **Checkpoint `state.json` is the diagnostic** — `next_display_id`,
   `watermark`, `display_id_map` reveal stale-baseline re-hydration (2.1).

---

## 5. Relationship to upstream / fork

- Crosslink fork: `/home/claude-code/projects/crosslink` (custom fork, PR #44
  on dollspace-gay/crosslink). Known-issues detail in
  `.crosslink/knowledge/crosslink-fork.md`.
- uuid-sync bug: draft upstream bug report in
  `research-addenda/Research Addendum 03 - Crosslink 0.9.0-beta.1 uuid-sync bug.md`
  (intended for `github.com/forecast-bio/crosslink/issues/new`).
- This catalog is documentation only — it makes **no crosslink code changes**.
  Code fixes are tracked by #125/#157 (family), #142 (mechanism), #167
  (lock-guard wiring).
