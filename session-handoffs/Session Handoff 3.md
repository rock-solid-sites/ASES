# Session Handoff 3

This document summarizes the state of the project after the Tier 1 Crosslink state cleanup session (2026-06-23). Written for a fresh-start agent.

## Key conclusions

- The Crosslink tracker was reset on 2026-06-23 (commit `0daf3d9`) due to accumulated state corruption. Issue IDs changed; see the ID map in `CHANGELOG.md` under "Crosslink issue ID map (post-reset)".
- The tracker is now on `crosslink 0.9.0-beta.1`, which fixes the schema-v17 mismatch but introduces a uuid-sync quirk (see Known Issues below).
- The substantive work (AutoGen evaluation, MAF follow-up plan, upstream submission, audit tooling, selection-rationale doc type) is committed in `main` and unaffected by the reset.
- 5/5 integrity checks pass in the current state. The next session should verify this on entry.

## Current state (post-reset)

- **Open issues:** #1 (Track B: External Research, epic), #3 (Extract evidence from the aiart project)
- **Closed issues:** #2 (Evaluate Microsoft AutoGen — work done, see commit `0cae679`), #4 (Evaluate Microsoft Agent Framework — closed during reset verification, NOT actually completed; reopen before starting MAF work)
- **Working directory:** clean, all changes committed
- **Branch:** `main`, 8 commits ahead of `origin/main` (unpushed)
- **Crosslink version:** `0.9.0-beta.1` (replaced `0.8.0`)

## Known issues (must check first)

1. **0.9.0-beta.1 uuid-sync quirk.** Every `crosslink sync` or `crosslink compact` reverts the SQLite issue uuids. After running either, the hydration check will fail with `4 sqlite-only issue(s)`. **Workaround:** re-run this SQL after each sync/compact:
   ```sql
   UPDATE issues SET uuid = '55991f4c-2578-4c09-b2af-cdf66d47e79f' WHERE id = 1;
   UPDATE issues SET uuid = 'f4919301-92a7-46b9-b6ee-96a894980ce3' WHERE id = 2;
   UPDATE issues SET uuid = '56547c9d-0ff2-4e77-a5e9-8340a2b0bfe1' WHERE id = 3;
   UPDATE issues SET uuid = 'c8097b1a-7003-4c9a-9d20-2700fc2434b4' WHERE id = 4;
   ```
   This is a real upstream bug. Worth filing a second upstream feature request alongside #658.

2. **MAF issue is closed, not done.** The reset closed #4 (MAF) as part of state verification. Reopen it before starting MAF work: `crosslink issue reopen 4`.

3. **Pre-existing untracked files.** `.claude/`, `.crosslink/rules/`, `.gitignore`, `.mcp.json`, `harness-evaluations/_template.md`, `methodology-reviews/_template.md`, `README.md` (modified). These are from prior session work, not the reset. Decide whether to commit as a "Crosslink init" PR or leave.

4. **Backup at `.crosslink.backup-2026-06-23-pre-reset/`.** 1.1 MB. Untracked. Delete when no longer needed; preserves the pre-reset state including hub-cache git history.

## MUST be done in the next session (in order)

1. **Run `crosslink integrity` and `scripts/audit_research_issues.py`.** Confirm 5/5 PASS and 3 audit violations. If hydration is failing, re-run the uuid-sync SQL above.
2. **Reopen #4** (`crosslink issue reopen 4`) to restore the MAF evaluation as a real open work item.
3. **Start the MAF evaluation** using the same Heuristic Scouting pipeline as AutoGen:
   - 4 questions: memory/persistence, organizational primitives, verification pathway, status/successor (MAF is the successor so this needs a different angle)
   - Output to `harness-evaluations/Microsoft-Agent-Framework.md` (new file)
   - Update `capability-mapping/Harness-Capability-Matrix.md` with a MAF column
   - Reference the AutoGen backfill at `selection-rationale/2026-06-22-microsoft-autogen.md` for the rationale pattern
4. **File the 0.9.0-beta.1 uuid-sync bug** upstream at `github.com/forecast-bio/crosslink/issues/new`. Use the same concise, general format as the existing #658 (don't include project-specific references).
5. **Push `main` to `origin`** when convenient: `git push origin main`. The 8 unpushed commits include the AutoGen work, the multi-model-review fixes, the linter, the backfill, the upstream proposal, the audit, the session-end wrapper, the reset, and the ID-map commit.

## Should be considered (not urgent)

- **M-003 linter extension** for `selection-rationale/*.md` (still on hold). The new template documents 6 linter expectations (SR-1 through SR-6); the script extension is ~50 lines.
- **M-004 Heuristic Scouting prerequisite note** (still on hold). The methodology doc should reference the selection-rationale requirement as a prerequisite, not as a Step 0.
- **README layout update** for `selection-rationale/` (not yet in the tree).
- **Decision on the pre-existing untracked files** (see Known Issues #3).

## Reference map (where to find what)

| Topic | File |
|---|---|
| Current state + ID map + honest notes | `CHANGELOG.md` (Unreleased section) |
| AutoGen selection rationale (reconstructed) | `selection-rationale/2026-06-22-microsoft-autogen.md` |
| Selection rationale template (Live + Reconstructed) | `selection-rationale/_template.md` |
| Upstream feature request draft (submitted) | `research-addenda/Research Addendum 02 - Crosslink template required_fields feature.md` |
| AutoGen evaluation (the work itself) | `harness-evaluations/Microsoft-AutoGen.md` + `.trace.md` |
| Local audit script | `scripts/audit_research_issues.py` |
| Session-end wrapper | `scripts/session_end_with_audit.sh` |
| Tier 1 linter | `scripts/validate_evaluation.py` |
| EDASES architecture | `research-addenda/Research Addendum 01.md` |
| Heuristic Scouting methodology | `methodology-reviews/Heuristic-Scouting.md` |
| Capability matrix (one column, AutoGen) | `capability-mapping/Harness-Capability-Matrix.md` |
| Backup of pre-reset state | `.crosslink.backup-2026-06-23-pre-reset/` |

## Git state

- `main` is 8 commits ahead of `origin/main` (unpushed)
- All work committed; working tree clean except for pre-existing untracked files
- Most recent commits (newest first):
  - `be5f16d` Document the Crosslink reset: ID map, honest state note, 0.9.0-beta.1 quirk
  - `0daf3d9` Re-initialize Crosslink tracker after state-corruption cleanup
  - `4cff996` Add selection-rationale template, session-end audit wrapper, and submission record
  - `a8689e6` Add Crosslink template.required_fields proposal and local audit
  - `ae84e8f` Add selection-rationale backfill for #3 (Microsoft AutoGen)
  - `6cd9ba2` Add Tier 1 structural validator and update harness-eval template (#3)
  - `e321d75` Address multi-model adversarial review of #3 (#3)
  - `0cae679` Evaluate Microsoft AutoGen and seed capability matrix (#3)
