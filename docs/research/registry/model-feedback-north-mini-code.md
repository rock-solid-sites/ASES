---
title: "Model Feedback: cohere/north-mini-code-1-0 — MERGED (existing doc + corroborating evidence)"
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

# Model Feedback: cohere/north-mini-code-1-0 — MERGED (existing doc + corroborating evidence)

## Identification
- Model: North Mini Code (cohere/north-mini-code-1-0)
- Provider: Cohere
- Release Date: 2026
- Access Method: opencode run --model cohere/north-mini-code-1-0
- Configuration: temperature 0.2, subagent mode, read-only
- Session evidence: existing doc (2026-07-11, 17-file review) + docs/project-completion-report-crosslink-model-agnostic.md (corroboration)

## Task Categories Evaluated
- [x] Code Review
- [ ] Implementation
- [ ] Design Critique

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 5 | Identified 0 issues in 17 modified files; zero false positives (existing doc + project-completion-report §8 adversarial consensus) |
| Completeness | 5 | Verified all 5 check categories |
| Consistency | 5 | Applied same rigor across all 4 fixes |
| Robustness | 5 | Checked gating logic, test updates, call sites; no failures observed |
| Explainability | 5 | Extremely concise, zero fluff |
| Efficiency | 5 | Review completed in ~30 seconds |
| Collaboration | 5 | Clear PASS/FAIL format; performed correctly when orchestration failed (project-completion-report §9) |

## Observed Strengths
- Extremely concise - reports only findings, no fluff
- Zero false positives - confirmed all 4 fixes correct
- Applied same rigor across all 4 fixes consistently
- Checked gating logic, test updates, and call sites
- Completed review in ~30 seconds
- Corroborated by project-completion-report §8: adversarial-consensus partner to the Gemini deep audit, 0 issues

## Observed Weaknesses
- Extremely terse - may miss nuance in complex architectural issues
- No design-level critique (only implementation verification)
- No suggestions for improvement (only pass/fail)
- Not suited as sole reviewer for architectural decisions (project-completion-report §8: role was verification, paired with Gemini audit)
- Note: The orchestration failures (direct coding instead of subagent delegation, ignoring NVIDIA NIM requirement, etc.) were ORCHESTRATOR failures, not north-mini-code behavior. north-mini-code performed correctly when dispatched (project-completion-report §9).

## Failure Modes Observed
- None observed - zero false positives, zero false negatives (existing doc + project-completion-report)

## Context Behavior
- Large context performance: Good - handled 17-file diff
- Context recovery: N/A (single-shot review)
- Instruction retention: High - followed all 6 verification items exactly
- Long-term consistency: N/A (single review)

## Cost Characteristics
- Relative token consumption: Very low (cohere/north-mini-code-1-0)
- Cost efficiency: Excellent (free tier)
- Typical interaction overhead: Very low

## Performance Characteristics
- Response latency: Very fast (~30s)
- Throughput: Very high
- Reliability: High
- Determinism: High (reproducible PASS)

## Tool Integration
- External tools: git diff, rg, cat (via opencode)
- APIs: opencode run
- Repositories: Crosslink repo (read access)
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A (autonomous review)
- Instruction following: Excellent - followed all 6 verification items
- Resistance to ambiguity: High - reported clear PASS/FAIL
- Responsiveness to critique: N/A
- Recovery from mistakes: N/A (no mistakes)

## Protocol Adherence
- Negative constraint respect: N/A (no negative constraints given)
- Negative constraint violations: 0
- Fallback behavior on error: N/A (no errors)
- Model substitution without consent: 0
- Process control compliance: Excellent - followed all 6 verification items exactly

## Suitable Tasks (evidence-backed)
- Implementation verification (code matches plan)
- Regression detection (code matches tests)
- Pattern compliance checking
- Fast triage reviews
- CI gate reviews
- Adversarial-consensus partner to deep audit (project-completion-report §8)

## Unsuitable Tasks (evidence-backed)
- Architectural design critique (no evidence)
- Novel vulnerability discovery (no evidence)
- Design iteration / improvement suggestions (no evidence)
- Complex system reasoning (no evidence)

## Dependencies
- Works well with: git diff, rg for context, cargo check for verification; Gemini 3.1 Pro as the deep-audit counterpart

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Controlled experiment | Reviewed 17 modified files | Replicated |
| Independent reviewer agreement | Gemini 3.1 Pro audit: 0 issues | Agreement |
| Project observation | 0 findings in production code | Observed |

## Confidence Assessment
- Level: High
- Reviewer: Self-assessment (existing doc); evidence-gathering draft (#190) — updated
- Date: 2026-08-06 (updated from 2026-07-11)
- Evidence considered: 17 modified files reviewed, 0 findings, cross-validated by Gemini audit + project-completion-report (2 independent records)
- Significant changes from prior assessment: No substantive changes; corroborated by project-completion-report adversarial consensus

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: existing doc + project-completion-report-crosslink-model-agnostic.md
- Significant changes: Corroboration added; adversarial-consensus role documented
