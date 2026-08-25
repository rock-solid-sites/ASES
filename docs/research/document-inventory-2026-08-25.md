---
title: "Document Inventory Snapshot — 2026-08-25"
program: EDASES
layer: Research
document_type: Observational-evidence
status: Active
authority: Observational
canonical_repository: edases
references:
  - "Crosslink issue #462 (doctrine propagation + doc inventory + housekeeping dispatch)"
created: 2026-08-25
---

# Document Inventory Snapshot — 2026-08-25

An observational snapshot of all documentation files across
`/home/claude-code/projects/`, taken 2026-08-25 under issue #462. This is
**evidence, not methodology**: it records what exists on disk at a point in
time and flags duplicate/orphan/fossil candidates for later disposition by the
orchestrator. No cleanup action is proposed as binding here.

## Method

* Batch `find` over every project directory under `/home/claude-code/projects/`.
* Documentation file class: `*.md` and `*.markdown`. No `.rst` / `.adoc` /
  `.org` files exist anywhere in the scanned tree (verified), so markdown is
  the complete documentation surface.
* Exclusions: `.git` internals, `node_modules`, binary backup blobs (none
  matched the documentation globs).
* Sizes via `du -b`; duplicates verified with `md5sum`; divergence between
  live repos and their backups via `diff -rq`.

## Per-project counts

| Project | md files | md bytes | Notes |
|---|---:|---:|---|
| ASES (incl. 4 `.worktrees/`) | 2,535 | 6,168,668 | Main tree only: **575**; worktree mirrors: **1,960** (~77% of count is duplication) |
| ASES-backup | 329 | 2,707,460 | Whole-repo fossil (see below) |
| crosslink | 144 | 1,073,997 | Tool repo; CHANGELOG.md is largest doc (48,772 B) |
| tripn-astro | 151 | 1,078,382 | CHANGELOG.md 76,688 B; docs/ holds per-fix notes |
| Tools (incl. 1 `.worktrees/`) | 178 | 819,147 | TOOLING.md 42,906 B canonical |
| Tools-backup | 88 | 424,445 | Whole-repo fossil (see below) |
| server | 71 | 375,540 | Mostly `.claude/skills` copies; 3 real top-level docs |
| 100percentaiart | 57 | 312,365 | docs/Phase-6-Plan.md 53,216 B largest |
| rock-solid-sites | 9 | 51,386 | docs/design-system.md 20,521 B largest |
| HMS | 1 | 7,926 | Single spec: `Hospitality Management Suite Specification.md` |
| tripn-instagram-feed | 1 | 4,757 | README.md only |
| Loose top-level (`projects/*.md`) | 2 | 8,248 | `AGENTS.md` (1,301 B), `gemini-codewhale-setup.md` (6,947 B) |
| **Total** | **3,566** | **13,032,321 (~12.4 MiB)** | |

## Notable paths

* `ASES/docs/` — canonical documentation home: `ORCHESTRATOR.md`,
  `SESSION-END.md`, `architecture/`, `methodology/`, `requirements/`,
  `research/`, `standards/`, `historical/`.
* Largest single document anywhere:
  `ASES/research-addenda/Research Addendum 05 - Workflow Topology Design Conversation.md`
  (166,244 B) — mirrored byte-identically into each active worktree.
* `crosslink/CHANGELOG.md` (48,772 B) and `tripn-astro/CHANGELOG.md`
  (76,688 B) are the heaviest changelogs.
* `server/`: real docs are `fortified-server-architecture.md` (17,563 B),
  `migration-handoff-summary.md`, `tailscale-implementation.md`; the rest of
  its 71-file count is `.claude/skills` + `.claude/commands` scaffolding.
* Filename-frequency noise: `README.md` ×532, `SKILL.md` ×498, `AGENTS.md`
  ×211 across the tree — dominated by vendored skill/rule scaffolding, not
  authored documents.

## Duplicate / orphan / fossil candidates

### Fossils (whole-repo backups, stale)

1. **`Tools-backup/`** — full git repo copy of `Tools/`. Last meaningful
   content touch 2026-07-15 (`TOOLING.md`) / 2026-07-20 (`.crosslink/rules`).
   Diverged from live `Tools/`: 10 md files differ, ≥13 files exist only in
   live Tools (`agents/big-pickle.md`, `agents/gemini-35-flash.md`,
   `agents/glm5.2-auditor.md`, `agents/laguna-general.md`,
   `agents/ling-general.md`, `agents/nemotron-general.md`,
   `agents/north-mini-code.md`, `agents/north-mini-general.md`,
   `.claude/findings-interrupt-plugin.md`,
   `.crosslink/.knowledge-cache/server-memory-management.md`, …). The backup
   is strictly older; no unique content was detected in it during this pass.
2. **`ASES-backup/`** — full git repo copy of an *older ASES layout*
   (top-level `adversarial-reviews/`, `syntheses/`, `to-file/`,
   `research-programs/` …). Last touched 2026-07-17 / 2026-07-20. Live ASES
   has since reorganised research material under `docs/research/`; the backup
   preserves the pre-reorganisation tree. Candidate for archive-or-delete
   review — its unique value is historical layout evidence only.

### Duplicates (byte-identical copies)

3. **`dynamic-models.ts` ×8, all byte-identical**
   (md5 `ce91fa1394e51711857234e758de07ad`, 1,451 B):
   * Canonical home: `Tools/plugins/dynamic-models.ts` (+ its worktree copy,
     + `Tools-backup/plugins/dynamic-models.ts`);
   * **Misplaced copies:** `ASES/docs/research/dynamic-models.ts` (+ 4
     identical worktree mirrors). A TypeScript plugin file does not belong in
     a research documents directory — candidate for relocation/removal from
     `docs/research/` once its provenance note (if any) is preserved.
   * Sibling artefact: `ASES/docs/research/dynamic-models.js` (362 B) — same
     misplaced-class suspicion, not checksummed against any original.

### Drift candidates (same-name, diverged content)

4. **`agent-orchestration-playbook.md`**: ASES canonical
   (`.crosslink/knowledge/`) vs `tripn-astro/.crosslink/knowledge/` copy have
   **diverged** (different md5). The playbook itself declares the ASES copy
   authoritative ("the ASES copy wins on conflict"), so the tripn-astro copy
   is drift to be re-synced or deleted.
5. **Root `AGENTS.md` variants**: `/home/claude-code/projects/AGENTS.md`
   (loose), `ASES/AGENTS.md`, and `tripn-astro/AGENTS.md` are three distinct
   documents sharing a name (211 `AGENTS.md` copies exist tree-wide). The
   loose projects-root file is an orphan — it belongs to no repository.
6. **`tripn-astro/docs/` near-duplicate names**: `Seaside Fixes.md` vs
   `Seaside-Fixes.md` (space/hyphen pair) and several `X Fixes.md` working
   notes — consolidation candidates.

### Structural observations

7. **Worktree inflation**: 1,960 of ASES's 2,535 md files (77%) are active
   `.worktrees/` mirrors of main-tree documents. Any future inventory should
   report main-tree vs worktree counts separately (as above) or the numbers
   mislead by ~3.4×.
8. **Skill/command scaffolding dominates small repos**: `server/` (71),
   `Tools/` (178) counts are mostly `.claude/skills/*/SKILL.md` +
   `.claude/commands/*` copies of shared tooling, not project-authored docs.

## Certainty statement

* **WHY**: #462 requested a documentation snapshot before any housekeeping;
  stale-copy risk (Tools-backup class) and misplaced-artefact risk
  (dynamic-models.ts class) were named explicitly.
* **WHAT**: direct filesystem observation (`find`/`du`/`md5sum`/`diff -rq`)
  on 2026-08-25; all counts and checksums in this document are reproducible
  from the stated commands.
* **HOW CERTAIN**: evidence-based for counts, sizes, checksum equality, and
  divergence facts; interpretive for the fossil/orphan labels (a backup may
  be intentional retention).
* **WHAT-NOT-TESTED**: content-level similarity beyond name+checksum for
  unlisted file pairs; whether either backup directory contains unique
  *content* (only that its md set is a subset/diverged subset of the live
  repo's); git history depth of the two backup repos; the provenance of
  `dynamic-models.js`.
