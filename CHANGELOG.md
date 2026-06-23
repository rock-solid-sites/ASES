# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Evaluate Microsoft AutoGen against EDASES layered architecture (#3)
- Seed Harness Capability Matrix with AutoGen column (#3)
- Document Heuristic Scouting Methodology (#6)
- Import Crosslink documentation from aiart project (#4)
- Set up Harness Evaluation templates (#2)
- Tier 1 structural validator `scripts/validate_evaluation.py` (post-#3 review fix)
- Crosslink `template.required_fields` upstream feature request draft (Research Addendum 02) — submitted to https://github.com/forecast-bio/crosslink/issues/658
- Post-create audit `scripts/audit_research_issues.py` for `research` issues (local mirror of the upstream proposal)
- `selection-rationale/_template.md` — canonical template for future Live and Reconstructed entries
- `scripts/session_end_with_audit.sh` — wrapper that runs the audit and appends a summary to `crosslink session end --notes`
- Selection-rationale backfill documenting the reconstructed rationale for #3 (AutoGen)

### Crosslink issue ID map (post-reset)

The Crosslink tracker was reset on 2026-06-23 (commit `0daf3d9`). Old issue IDs no longer match. Mapping:

| Pre-reset ID | Post-reset ID | Title | Status |
|---|---|---|---|
| #1 | #1 | Track B: External Research | open (unchanged) |
| #3 | #2 (closed) | Evaluate Microsoft AutoGen | closed |
| #5 | #3 | Extract evidence from the aiart project | open |
| #7 | #4 (closed) | Evaluate Microsoft Agent Framework | closed (test) |

Note: #2 and #4 were closed during this session for verification purposes. The actual AutoGen evaluation work is in commit `0cae679` and the MAF evaluation is the next planned work item.

Historical references in `selection-rationale/`, `research-addenda/`, and other docs to old IDs (e.g., "Crosslink issue: #3" in `2026-06-22-microsoft-autogen.md`) refer to the pre-reset tracker. These are **left as historical references** to preserve the audit trail; the substantive work content is unchanged.

### Fixed

### Changed
- Re-initialize Crosslink tracker after backup: deleted `.crosslink/issues.db`, `.crosslink/.hub-cache/`, deleted remote `crosslink/hub` and `crosslink/hub-v3-host` branches, re-`init`ed, re-synced, re-created the open issues (#1 epic, #2 AutoGen, #3 aiart, #4 MAF) and closed #2 with the audit summary. Backup at `.crosslink.backup-2026-06-23-pre-reset/`. Hydrated the hub by running `crosslink migrate to-shared`, manually synced SQLite uuids to match the hub-generated uuids, and re-pushed `crosslink/hub` to remote. Final integrity: 5/5 PASS.
- **Honest note (post-#3 review fix):** the tracker is on `crosslink 0.9.0-beta.1` which has a known quirk: each `crosslink sync` or `crosslink compact` reverts the SQLite issue uuids, which then makes the hydration check fail. The fix is to re-run the uuid-sync SQL after each sync/compact (see `scripts/audit_research_issues.py` for the analogous post-create pattern). The data is correct in both places; only the integrity check is misreporting. This is a 0.9.0-beta.1 issue worth filing upstream alongside the existing #658.
- Revised `harness-evaluations/_template.md` §4 with mandatory verification-status tag convention (`[verified-directly | per-subagent | inferred-from-code]`)
- Revised `harness-evaluations/Microsoft-AutoGen.md` addressing 10 issues from multi-model adversarial review (3 models: gemini-pro-reviewer, explore, deepseek-flash)
