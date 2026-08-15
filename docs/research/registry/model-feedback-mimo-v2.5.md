---
title: "Model Feedback: opencode/mimo-v2.5-free (Zen) / opencode-go/mimo-v2.5 (paid)"
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
last_updated: 2026-08-15
---

# Model Feedback: opencode/mimo-v2.5-free (Zen) / opencode-go/mimo-v2.5 (paid)

## Identification
- Model: mimo-v2.5 (v2.5-free variant observed; v2.5 and v2.5-pro paid variants exist)
- Provider: opencode (Zen free tier observed)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #183 (re-review verdict r2, design round 2), #364 (remediation round-2 review)

## Task Categories Evaluated
- [x] Adversarial re-review (design round 2 #183)
- [x] Plan remediation review (#364)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 4 | #183 verified all round-1 findings (B1-B3, F4-F13, R1-R3) against #180 and issued PASS; each finding-by-finding check is detailed and cites design sections |
| Completeness | 5 | #183 covered every focus area (B1 both guard copies, B2 numeric chain, B3 off-by-one, F4-F12, R2/R3 test params, matrix sufficiency) |
| Consistency | 5 | Systematic findings-by-finding verification structure |
| Robustness | 5 | No failures observed |
| Explainability | 5 | Excellent verification table with design-section citations per finding |
| Efficiency | 4 | #183 verdict ~5 min after plan (23:05 -> 23:08) |
| Collaboration | 4 | Isolated-channel discipline held |
| Instruction Adherence | 5 | Followed independent-re-derivation instruction; posted ONE verdict |

## Observed Strengths
- STRUCTURED PASS-VERDICT RE-REVIEWER: #183 is the cleanest PASS in the dataset — verified each finding against the revised design with section citations and confirmed the change-log was accurate - Evidence: #183
- Rapid but thorough: full B1-B3/F4-F13/R1-R3 verification in ~5 min - Evidence: #183 timestamps
- Independent verification spirit: did not trust the change-log; checked each item (though less deeply than hy3 #182) - Evidence: #183 'I re-derived each checkable claim'
- Concrete-design-proposal strength: #364 proposed the concrete 3-state enforcement state machine (State 0/1/2 with --promote transition) + git-only atomicity for the B3/B5 blockers — actionable remediation, not just critique - Evidence: #364 BF-1/BF-3

## Observed Weaknesses
- PASSED a design that hy3 #182 found 5 compile-level blockers in (V1-V5): mimo's #183 verification did NOT catch that Patch B does not compile (V1), harness param contradiction (V2), absolute-cap timer unsound (V3). Depth of source-level verification is SHALLOWER than hy3 - Evidence: #183 PASS vs #182 V1-V5 (both reviewed #180 independently)
- Single-session evidence base: only 1 observed session — confidence is limited - Evidence: #183 only

## Failure Modes Observed
- Verification-depth gap: issued PASS where a peer found 5 blockers (false-negative in review depth, not a system failure) - Evidence: #183 vs #182 comparison

## Context Behavior
- Large context: Handled full revised design + baseline + verdicts (#183)
- Context recovery: N/A
- Instruction retention: High
- Long-term consistency: N/A (single session)

## Cost Characteristics
- Relative token consumption: Low-Moderate (free tier)
- Cost efficiency: Good (free + fast)
- Typical interaction overhead: Low

## Performance Characteristics
- Response latency: ~5 min
- Throughput: High
- Reliability: High (1/1)
- Determinism: High (structured verdict)

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
- Negative constraint respect: PASS
- Negative constraint violations: 0
- Fallback behavior on error: N/A
- Model substitution without consent: 0
- Process control compliance: Excellent

## Suitable Tasks (evidence-backed)
- Design re-review where a structured PASS/CONDITIONAL verdict is needed quickly (#183) - evidence: #183
- Second-opinion review after a rigorous primary reviewer (hy3) - evidence: #183 complementary to #182
- Plan remediation review with concrete design proposals (#364) - evidence: 3-state enforcement state machine + git-only atomicity

## Unsuitable Tasks (evidence-backed)
- Sole-reviewer on implementation-readiness of patch code: missed compile-level blockers that hy3 caught (V1-V5) - evidence: #183 vs #182
- Source-level correctness gate for executable patch code - evidence: #183 verification depth

## Dependencies
- Works well with: a rigorous source-verifying reviewer (hy3) as primary; mimo as fast second opinion

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Controlled experiment | #183 findings-by-finding verification | Replicated |
| Independent reviewer agreement | #183 PASS vs #182 CONDITIONAL (V1-V5) — divergence documented | Disagreement (documented) |

## Confidence Assessment
- Level: Emerging (2 sessions)
- Reviewer: evidence-gathering draft (#190); updated 2026-08-15 (session #27 evidence: #364)
- Date: 2026-08-06
- Evidence considered: #183, #364, #154 synthesis, #182 comparison
- Significant changes from prior assessment: First mimo profile; flagged verification-depth gap vs hy3. Session #27 added concrete-design-proposal strength.

## Last Review
- Date: 2026-08-15
- Reviewer: session #27 update (#374)
- Evidence considered: #183, #364, #154 synthesis, #182 comparison
- Significant changes: Added #364 remediation-review evidence (concrete 3-state enforcement + git-only atomicity proposals)
