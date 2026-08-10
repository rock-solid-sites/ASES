# Harness Evaluation: [Harness Name]

**Date:** YYYY-MM-DD
**Evaluator:** [Agent/User]
**Source/URL:** [GitHub link or paper]

## 1. Overview
[Brief description of the harness and its primary stated goal. Is it a coding harness, a general-purpose agent framework, or something else?]

## 2. Architectural Alignment
*Evaluate against EDASES multi-layer architecture (Principal, Organizational, Capability, Verification, Execution).*

*   **Organizational Layer:** [Does it manage memory, roles, task breakdown? e.g., Crosslink]
*   **Execution Layer:** [Does it just generate code? e.g., OpenCode, OpenClaudia]
*   **Verification Layer:** [Does it orchestrate testing/CI?]

## 3. Key Capabilities & Features
*   [Capability 1]
*   [Capability 2]

## 4. Observations
*Keep these atomic and objective. Avoid interpretation.*
*   **OBS-01:** [Observation] (Source: [Link/File]) `[verification-status]`
*   **OBS-02:** [Observation] (Source: [Link/File]) `[verification-status]`

**Verification status tag convention** (mandatory, appended after `(Source: ...)`):

*   `[verified-directly]` — Orchestrator fetched the source and confirmed the OBS. Default for Scout-phase facts and any OBS read in this session.
*   `[per-subagent]` — Reported by a Heuristic-Scouting Verify subagent without direct Orchestrator confirmation. **Disallowed for any OBS cited by a FIN-*** (high-stakes claim; see `scripts/validate_evaluation.py` check C6).
*   `[inferred-from-code]` — Stated in a code or config example on the cited page rather than in prose documentation. Mark when the path/version/field is shown only in a usage example.

If the status is unknown, default to `[per-subagent]` and the linter will flag any high-stakes use.

## 5. Findings
*Conclusions derived from observations.*
*   **FIN-01:** [Finding based on OBS-01]

## 6. Gaps against EDASES Requirements
[What is missing to make this a complete evidence-driven organizational system?]
