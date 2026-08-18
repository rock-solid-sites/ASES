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
last_updated: 2026-08-18
---

# Model Feedback: opencode/mimo-v2.5-free (Zen) / opencode-go/mimo-v2.5 (paid)

## Identification
- Model: mimo-v2.5 (v2.5-free variant observed; v2.5 and v2.5-pro paid variants exist)
- Provider: opencode (Zen free tier observed)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #183 (re-review verdict r2, design round 2), #364 (remediation round-2 review), #404 (third verification, pp3g-gUUV), #407 (failure-matrix update, pp3g-ATNS), #408 (inventory pp3g-Fsyf + recovery pp3g-JRTy), #410 (fix pp3g-qO5v)

## Task Categories Evaluated
- [x] Adversarial re-review (design round 2 #183)
- [x] Plan remediation review (#364)
- [x] Infrastructure verification audit (#404 third verification, pp3g-gUUV)
- [x] Failure-matrix update (#407, pp3g-ATNS)
- [x] Inventory generation across 10 repos (#408, pp3g-Fsyf)
- [x] Inventory recovery and posting (#408, pp3g-JRTy)
- [x] Inventory correction and posting (#410, pp3g-qO5v)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 5 | #183 verified all round-1 findings against #180; #404 found 10 precise factual corrections (F1-F10) including script-count misattribution and enforcement-mechanism errors — verified all 9 infra files against inventory claims |
| Completeness | 5 | #183 covered every focus area; #404 read all 9 infra files (1220+108+415+237+46+151+455+86+363 lines); #408 produced 39-entry inventory across 10 repos |
| Consistency | 5 | Systematic findings-by-finding verification structure (#183, #404); reliable completion across 5/5 dispatched tasks on 2026-08-18 |
| Robustness | 5 | Completed every dispatched task — 5/5 on 2026-08-18; no failures, no stalls, no scope drift |
| Explainability | 5 | Excellent verification tables with file:line citations (#183, #404); structured inventory format (#408) |
| Efficiency | 4 | #183 verdict ~5 min; #404 third verification produced CONDITIONAL PASS with 10 findings; pp3g-qO5v applied 4 corrections |
| Collaboration | 5 | Posted corrected inventory on #391 (#410); isolated-channel discipline held across all sessions |
| Instruction Adherence | 5 | Followed independent-re-derivation instruction (#183); posted ONE verdict; completed all 5 dispatched tasks per instructions |

## Observed Strengths
- STRUCTURED PASS-VERDICT RE-REVIEWER: #183 is the cleanest PASS in the dataset — verified each finding against the revised design with section citations and confirmed the change-log was accurate - Evidence: #183
- Rapid but thorough: full B1-B3/F4-F13/R1-R3 verification in ~5 min - Evidence: #183 timestamps
- Independent verification spirit: did not trust the change-log; checked each item (though less deeply than hy3 #182) - Evidence: #183 'I re-derived each checkable claim'
- Concrete-design-proposal strength: #364 proposed the concrete 3-state enforcement state machine (State 0/1/2 with --promote transition) + git-only atomicity for the B3/B5 blockers — actionable remediation, not just critique - Evidence: #364 BF-1/BF-3
- 100% completion rate under pressure: 5/5 dispatched tasks completed on 2026-08-18 while other models (big-pickle, deepseek-flash-free, laguna) repeatedly stalled — reliable completion when free models fail - Evidence: #404 (pp3g-gUUV), #407 (pp3g-ATNS), #408 (pp3g-Fsyf, pp3g-JRTy), #410 (pp3g-qO5v)
- Infrastructure verification depth: #404 (pp3g-gUUV) read all 9 infra files and produced 10 precise factual corrections with file:line evidence — caught misattribution of enforcement mechanisms - Evidence: #404 FINDINGS 1-10
- Inventory generation across 10 repos: #408 (pp3g-Fsyf) produced 39-entry inventory; #408 (pp3g-JRTy) recovered and posted it; #410 (pp3g-qO5v) applied corrections — multi-step deliverable completed across sessions - Evidence: #408, #410

## Observed Weaknesses
- PASSED a design that hy3 #182 found 5 compile-level blockers in (V1-V5): mimo's #183 verification did NOT catch that Patch B does not compile (V1), harness param contradiction (V2), absolute-cap timer unsound (V3). Depth of source-level verification is SHALLOWER than hy3 - Evidence: #183 PASS vs #182 V1-V5 (both reviewed #180 independently)
- Finalization gap observed across sessions (pp3g-Jo2n, pp3g-gUUV, pp3g-Fsyf, pp3g-qO5v, pp3g-ATNS) — but this is a role-permission issue (auditor role blocks session start/comment posting/.kickoff-status writes), NOT mimo-specific. Mimo recovered from the gap when orchestrator intervened; other models stalled outright. - Evidence: #398/#355 role-permission tracking; #404 pp3g-gUUV recovered from pane; #408 pp3g-JRTy recovered inventory

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
- Response latency: ~5 min (varies by task complexity)
- Throughput: High
- Reliability: High (7/7 across all sessions: 2 historical + 5 on 2026-08-18)
- Determinism: High (structured verdicts, consistent completion)

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
| Controlled experiment | #183 findings-by-finding verification; #404 10-finding infrastructure audit (9 files) | Replicated |
| Independent reviewer agreement | #183 PASS vs #182 CONDITIONAL (V1-V5) — divergence documented | Disagreement (documented) |
| Completion rate | 5/5 tasks completed 2026-08-18 (#404/#407/#408/#410) while free models stalled | Replicated |
| Multi-session deliverable | #408 inventory (pp3g-Fsyf) -> recovery (pp3g-JRTy) -> correction (pp3g-qO5v) — cross-session completion | Observed |

## Confidence Assessment
- Level: High (7 sessions, 5/5 completion on 2026-08-18)
- Reviewer: evidence-gathering draft (#190); updated 2026-08-18 (issue #411: #404/#407/#408/#410 evidence)
- Date: 2026-08-18
- Evidence considered: #183, #364, #154 synthesis, #182 comparison, #404 (pp3g-gUUV), #407 (pp3g-ATNS), #408 (pp3g-Fsyf, pp3g-JRTy), #410 (pp3g-qO5v)
- Significant changes from prior assessment: First mimo profile; flagged verification-depth gap vs hy3. Session #27 added concrete-design-proposal strength. 2026-08-18: 5/5 task completion rate while free models stalled; infrastructure verification depth; finalization gap attributed to role-permission, not model-specific.

## Last Review
- Date: 2026-08-18
- Reviewer: issue #411 (pp3g-w8pi builder agent)
- Evidence considered: #183, #364, #154 synthesis, #182 comparison, #404, #407, #408, #410
- Significant changes: Added #404/#407/#408/#410 evidence; reliability raised to High (7/7); confidence raised to High; finalization gap attributed to role-permission not model-specific
