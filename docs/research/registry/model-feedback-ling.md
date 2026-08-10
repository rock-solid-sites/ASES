---
title: "Model Feedback: opencode/ling-3.0-flash-free"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - AI Evaluation Protocol
  - AI Capability Registry Specification

consumed_by:
  - Model Routing Matrix

related_documents:
  - AI Capability Registry Specification

supersedes: []
last_updated: 2026-08-10
---

# Model Feedback: opencode/ling-3.0-flash-free

## Identification
- Model: ling-3.0-flash-free
- Provider: opencode (Zen free tier)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #128 (orchestrator allowlist review), #151 (wrapSSE patch review). NOTE: #131 was created for a second ling allowlist verdict but contains NO comments — verdict was not posted (unknown cause; possibly duplicate dispatch).

## Task Categories Evaluated
- [x] Adversarial review (allowlist #128, binary patch #151)
- [x] Permission/policy review (#128)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 4 | #128 tool recommendations correct and adopted in final spec (#127); #151 analysis matched other reviewers' conclusions (no breakage, ambiguity removed) |
| Completeness | 4 | #128 covered all 4 categories (monitoring/verification/coordination/system health) + explicit rejections; #151 covered 4 focus areas |
| Consistency | 4 | Structured category-driven style in both |
| Robustness | 4 | Reliable; completed #128 in the same window where laguna #129 hung (same free tier) |
| Explainability | 4 | Clear grouped verdict with rationale per tool; #128 has tool-by-tool justification |
| Efficiency | 5 | FAST: #128 verdict ~25 min after dispatch (02:00 -> 02:00); #151 handoff within 3 min of creation (21:12 -> 21:15) |
| Collaboration | 4 | Clean isolated-channel verdicts |
| Instruction Adherence | 5 | Held ONE-verdict and read-only rules in both sessions |

## Observed Strengths
- FAST CONVERGENT STYLE (signature): #151 reviewed the #145 patch in under 3 minutes (21:12 issue created, 21:15 handoff) — fastest reviewer in the dataset - Evidence: #151 timestamps
- Category-driven completeness: #128 systematically covered monitoring (ps #1 priority), verification (grep/diff/tail/head/wc/stat), coordination (none needed), system health (free/df/uptime/date), and debugging (which/env) - Evidence: #128
- Conservative rejection of mutation-risk tools: explicitly rejected curl, ssh, sqlite3, find -exec, kill - Evidence: #128 'Tools NOT recommended'
- Precise priority-setting: 'ps is the #1 priority' matching the playbook's stalled-agent detection mandate - Evidence: #128
- Balanced verdict on #145: confirmed patch improves non-SSE case, noted safer alternative exists but current patch verified and simpler - Evidence: #151 handoff

## Observed Weaknesses
- Terse: #151's verdict content is not fully retrievable (only handoff summary in the record; no full finding details visible) — documentation quality of the verdict was thin - Evidence: #151
- Shorter verdicts than big-pickle/luna: less depth on edge cases - Evidence: #128/#151 compared to #137/#150
- #131 empty dispatch (no verdict posted) is a minor reliability signal — dispatch completed but comment lost/not posted - Evidence: #131

## Failure Modes Observed
- None catastrophic. #131: verdict issue created but zero comments (no verdict posted) — either never started or comment post failed; not classified as hang - Evidence: #131 (closed, no comments)

## Context Behavior
- Large context: Handled full allowlist config + playbook context (#128)
- Context recovery: N/A
- Instruction retention: High
- Long-term consistency: High

## Cost Characteristics
- Relative token consumption: LOW (terse verdicts)
- Cost efficiency: Excellent (free tier + fast)
- Typical interaction overhead: Low

## Performance Characteristics
- Response latency: VERY FAST (< 5 min typical)
- Throughput: High
- Reliability: High (completed where laguna hung, #129 comparison)
- Determinism: High

## Tool Integration
- External tools: read-only analysis
- APIs: opencode CLI
- Repositories: read-only access
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A
- Instruction following: Excellent
- Resistance to ambiguity: High
- Responsiveness to critique: N/A
- Recovery from mistakes: N/A

## Protocol Adherence
- Negative constraint respect: PASS (both sessions)
- Negative constraint violations: 0
- Fallback behavior on error: N/A
- Model substitution without consent: 0
- Process control compliance: Excellent

## Suitable Tasks (evidence-backed)
- Fast independent review where a quick, correct verdict is needed (#151: 3-min patch review) - evidence: #151
- Permission/policy allowlist review with structured categories (#128) - evidence: #128
- Cheap triage reviews on free tier - evidence: #128/#151

## Unsuitable Tasks (evidence-backed)
- Deep edge-case adversarial review (terse style; #151 lacked the detail big-pickle #150 provided) - evidence: #151 vs #150
- Live-system infrastructure verification (style is convergent, not investigative) - evidence: absence in #137-class tasks

## Dependencies
- Works well with: tight scope, explicit review categories, fast gates; pairs with deeper reviewers for edge cases

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Project observation | #128 verdict adopted into final allowlist spec | Repeated |
| Independent reviewer agreement | #151 conclusions consistent with #150/#152/#153 | Agreement |
| Project observation | #131 empty verdict (no comments) | Observed |

## Confidence Assessment
- Level: Moderate
- Reviewer: evidence-gathering draft (#190)
- Date: 2026-08-06
- Evidence considered: #128, #151, #131
- Significant changes from prior assessment: First ling profile (was not previously documented)

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: #128, #151, #131
- Significant changes: First profile; fast-convergent style + #131 empty-verdict reliability signal documented
