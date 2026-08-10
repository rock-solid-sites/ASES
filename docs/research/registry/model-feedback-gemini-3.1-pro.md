---
title: "Model Feedback: google-vertex/gemini-3.1-pro-preview — MERGED (existing doc + corroborating evidence)"
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

# Model Feedback: google-vertex/gemini-3.1-pro-preview — MERGED (existing doc + corroborating evidence)

## Identification
- Model: Gemini 3.1 Pro Preview
- Provider: Google Vertex AI
- Release Date: 2026
- Access Method: opencode run --model google-vertex/gemini-3.1-pro-preview
- Configuration: temperature 0.2, pure mode, audit subagent
- Session evidence: existing doc (2026-07-11, 17-file audit) + docs/project-completion-report-crosslink-model-agnostic.md (corroboration, same session set)

## Task Categories Evaluated
- [x] Architectural Audit
- [x] Adversarial Review
- [ ] Implementation

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 5 | Verified all 6 check categories, 0 findings (existing doc); corroborated by project-completion-report §8 (audit completed, 0 findings) |
| Completeness | 5 | Checked all 6 categories across 17 modified files |
| Consistency | 5 | Applied same rigor across all 6 check categories |
| Robustness | 3 | Found 0 issues despite deep code inspection; 2 timeout incidents (2-min limit on first attempt; project-completion-report §7: timeout on 2nd audit attempt, 3-min limit) |
| Explainability | 5 | Structured report with severity/evidence matrix |
| Efficiency | 3 | Slow (2+ min), hit timeout on BOTH observed attempts (existing doc + project-completion-report §7) |
| Collaboration | 4 | Clear PASS/FAIL per category with evidence; performed correctly when orchestration failed (project-completion-report §9) |

## Observed Strengths
- Comprehensive - checked all 6 check categories thoroughly
- Deep code inspection - read actual implementation, not just diffs
- Structured output - clear severity/evidence matrix per category
- Found no issues despite deep inspection (confirms implementation quality)
- Identified minor nits (design_cmd.rs fallback, container.rs model hardcode) correctly
- Corroborated by project-completion-report §8: audit completed with 0 findings, cross-validated by North Mini Code adversarial consensus

## Observed Weaknesses
- Slow - 2+ minutes per audit, hit 2-min timeout on first attempt
- Verbose output - very detailed, could be more concise
- Hit timeout on first attempt (2 min limit) - needed 3 min timeout
- Timeout at 3-min limit on 2nd attempt confirms the timeout sensitivity is systemic, not a one-off (project-completion-report §7)
- Doesn't explicitly flag "minor nits" separately from findings
- Note: The orchestration failures (direct coding instead of subagent delegation, ignoring NVIDIA NIM requirement, etc.) were ORCHESTRATOR failures, not Gemini behavior. Gemini performed correctly when dispatched (project-completion-report §9).

## Failure Modes Observed
- Timeout on BOTH observed audit attempts (2-min and 3-min limits) — requires >=3 min budget and is the binding constraint on usage (existing doc + project-completion-report §7)
- Missed some "minor nits" (design_cmd.rs fallback, container.rs model hardcode) in initial summary

## Context Behavior
- Large context performance: Good - handled full 17-file diff
- Context recovery: N/A (single-shot audit)
- Instruction retention: High - followed all 6 check categories exactly
- Long-term consistency: N/A (single audit)

## Cost Characteristics
- Relative token consumption: High (comprehensive audit)
- Cost efficiency: Medium (google-vertex/gemini-3.1-pro-preview paid tier)
- Typical interaction overhead: High

## Performance Characteristics
- Response latency: Slow (~2-3 min)
- Throughput: Low (single audit takes minutes)
- Reliability: Medium (timeout on 2 of 2 observed attempts — systemic, not a one-off)
- Determinism: High (reproducible findings)

## Tool Integration
- External tools: rg, cat, git (via opencode)
- APIs: opencode run
- Repositories: Crosslink repo (read access)
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A (autonomous audit)
- Instruction following: Excellent - followed all 6 check categories exactly
- Resistance to ambiguity: High - produced clear PASS/FAIL per category
- Responsiveness to critique: N/A
- Recovery from mistakes: N/A (no mistakes)

## Protocol Adherence
- Negative constraint respect: N/A (no negative constraints given)
- Negative constraint violations: 0
- Fallback behavior on error: N/A (no errors)
- Model substitution without consent: 0
- Process control compliance: Excellent - followed all 6 check categories exactly
- Timeout handling: **Failed** - hit timeout on 2 of 2 attempts (2-min and 3-min limits), needs >=3 min budget

## Suitable Tasks (evidence-backed)
- Final architectural audit / sign-off
- Deep code inspection for security/correctness
- Comprehensive cross-cutting concern verification
- Final sign-off before release

## Unsuitable Tasks (evidence-backed)
- Fast CI gate reviews (too slow)
- Incremental PR reviews (too slow)
- High-volume review queues (too slow)
- Iterative design feedback (too slow)

## Dependencies
- Works well with: Fast reviewer (North Mini Code) for triage, then Gemini for deep audit
- Requires: >=3 min timeout budget (project-completion-report §7)

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---| 
| Controlled experiment | Reviewed 17 modified files | Replicated |
| Independent reviewer agreement | North Mini Code: 0 issues | Agreement |
| Project observation | 0 findings in production code; timeout on 2nd attempt | Observed (2x timeout) |

## Confidence Assessment
- Level: High
- Reviewer: Self-assessment (existing doc); evidence-gathering draft (#190) — updated
- Date: 2026-08-06 (updated from 2026-07-11)
- Evidence considered: 6 check categories across 17 files, 0 findings, cross-validated by North Mini Code + project-completion-report (2 independent records, same session set)
- Significant changes from prior assessment: Timeout sensitivity now documented as 2-of-2 (systemic, not one-off); no other changes to existing assessment

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: existing doc + project-completion-report-crosslink-model-agnostic.md
- Significant changes: Corroboration added; timeout documented as 2-of-2 systemic
