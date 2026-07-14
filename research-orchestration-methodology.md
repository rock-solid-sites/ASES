---
title: "Research Programme Orchestration Methodology"
tags: ["methodology", "orchestration", "research", "multi-agent"]
sources: []
contributors: ["OL2r"]
created: 2026-07-14
updated: 2026-07-14
---

# Research Programme Orchestration Methodology

## Overview

This document describes the orchestrator-subagent-synthesizer-reviewer pipeline used for EDASES research programmes. This pattern was developed and validated during the Execution-Engine UI research programme (2026-07-14).

## Pipeline Architecture

```
Orchestrator (mimo-v2.5-pro)
      │
      ▼
Research Subagents (hy3, parallel, 2-3 concurrent)
      │
      ▼
Reports repository (reports/)
      │
      ▼
Synthesizer (mimo-v2.5-pro)
      │
      ▼
Reviewer (mimo-v2.5, fidelity-only)
      │
      ▼
PASS / FAIL
      │
      ▼
Human
```

## Roles

### Orchestrator
- **Model**: mimo-v2.5-pro (planning, delegation, synthesis oversight)
- **Responsibility**: Minimize human attention, maximize parallelism, enforce scope boundaries
- **Does NOT**: Perform research, write reports, or evaluate conclusions

### Research Subagents
- **Model**: hy3 (free, fast, sufficient for evidence gathering)
- **Responsibility**: Investigate one specific technology or question, produce evidence-only reports
- **Constraint**: No recommendations, no implementation proposals
- **Report template**: Question, Scope, Evidence, Findings, Rejected options, Unknowns, Confidence, References

### Synthesizer
- **Model**: mimo-v2.5-pro (needs reasoning depth across all reports)
- **Responsibility**: Read all reports, identify agreements/disagreements/uncertainties, answer which hypotheses have evidence
- **Constraint**: Does NOT perform additional research. Every conclusion must cite a report by filename.

### Reviewer
- **Model**: mimo-v2.5 (fidelity check, not correctness)
- **Responsibility**: Judge whether the synthesis accurately represents the reports
- **Criteria**: Accurate representation? No invention? No omission of conflicting evidence? Unsupported conclusions labelled?
- **Output**: PASS or FAIL with one-paragraph justification per criterion

## Concurrency Protocol

1. **Canary wave**: Run 1 subagent alone. Record `free -h` before/after.
2. **Concurrent waves**: Run 2-3 subagents concurrently. Record `free -h` at start, midpoint, and end.
3. **Abort threshold**: If available memory drops below ~1 GB, fall back to serial.
4. **Empirical, not computed**: Concurrency limits are determined by observation, not by estimating from memory figures.

## MCP Scoping

Subagents do not need the full MCP server stack. Scope MCP grants per role:
- **Research subagents**: fetch (web search) + filesystem (write to reports/ only)
- **Synthesizer**: filesystem (read reports/, write synthesis/)
- **Reviewer**: filesystem (read reports/ + synthesis/, write review/)

This is achieved via project-level `opencode.json` override that disables unnecessary MCP servers.

## Scope Boundaries

Every research programme should define explicit scope exclusions. Subagents should note excluded topics as "deferred" in their reports rather than investigating them.

## Validation

The methodology was validated during the Execution-Engine UI programme:
- 18 research subagents across 7 research questions
- Synthesis passed review on first submission (all 4 fidelity criteria satisfied)
- 2-3 concurrent subagents stable with MCP scoping
- Wall-clock time: ~2.5 hours for full programme

## Source

Derived from the Execution-Engine UI research programme orchestration (2026-07-14). See `research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md` for the synthesis that validated this methodology.
