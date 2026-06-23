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

### Fixed

### Changed
- Revised `harness-evaluations/_template.md` §4 with mandatory verification-status tag convention (`[verified-directly | per-subagent | inferred-from-code]`)
- Revised `harness-evaluations/Microsoft-AutoGen.md` addressing 10 issues from multi-model adversarial review (3 models: gemini-pro-reviewer, explore, deepseek-flash)
