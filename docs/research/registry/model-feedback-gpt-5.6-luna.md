---
title: "Model Feedback: opencode-go/gpt-5.6-luna"
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

# Model Feedback: opencode-go/gpt-5.6-luna

## Identification
- Model: gpt-5.6-luna
- Provider: opencode-go (paid)
- Access Method: opencode subagent / kickoff
- Configuration: default opencode-go provider config; reserved for high-value work per #147
- Session evidence: #136 (watcher plan review), #150 (wrapSSE patch review), #177 (design re-review round 1)

## Task Categories Evaluated
- [x] Adversarial review (watcher design #136, binary patch #150)
- [x] Design review (durable fix #177)
- [x] Systems/durability analysis (both reviews)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 5 | #150 identified exact MUST-FIX items (offset fragility, retry loop broadening) independently confirmed by hy3 #153 (F3) + laguna #152 (fragility Medium); #136 controls analysis matches big-pickle #137 hardening list |
| Completeness | 5 | #136 enumerated missing gates (identity, leases, idempotency, ledger, backoff, budget, fault injection, HALT exception); #150 covered edge cases + safer alternatives |
| Consistency | 5 | Same systems/durability lens across both verdicts; severity-ranked structured output |
| Robustness | 4 | No failures observed; reliable |
| Explainability | 5 | Severity-ranked with explicit MUST FIX / SHOULD CONSIDER / NIT taxonomy (#150); conditional verdicts with named preconditions (#136) |
| Efficiency | 4 | ~1-2 min per verdict; appropriate for depth delivered |
| Collaboration | 4 | Clean isolated-channel verdicts; no scope drift |
| Instruction Adherence | 5 | Read-only review constraints held; posted ONE verdict per issue as instructed |

## Observed Strengths
- SYSTEMS/DURABILITY LENS (signature style): evaluates lifecycle safety, state-machine invariants, races, leases, idempotency — not just code correctness - Evidence: #136 (atomic status schema, single-writer/lease ownership, recovery ledger, fault-injection tests)
- Conditional verdicts with named preconditions: 'adopt for observation, do not enable autonomous recovery until controls specified AND fault-tested' (#136); 'SHOULD NOT ship as the durable fix without hardening' (#150)
- Precise failure taxonomy: MUST FIX / SHOULD CONSIDER / NIT with concrete remedies - Evidence: #150
- Long-horizon risk identification: binary patch fragility (any upgrade silently re-introduces bug), retry budget, per-request ctl verification - Evidence: #150 findings F1-F4 mirror hy3 #153 F3/F4 independently

## Observed Weaknesses
- Requires high-value work to justify cost: operator rule reserves luna for coding/adversarial/audits and explicitly says 'don't burn it on cheap research' (#147) - Evidence: #147 operator routing rule
- Conditional verdicts may lack decisive direction (leaves implementation decision to operator) - Evidence: #136/#177 are both CONDITIONAL without a firm ship/no-ship

## Failure Modes Observed
- None observed in reviewed sessions (no hangs, no drift). Not yet stress-tested for the silent-hang class.

## Context Behavior
- Large context: Handled complex multi-part designs (#135 watcher plan, #145 binary patch evidence)
- Context recovery: N/A (no failure observed)
- Instruction retention: High
- Long-term consistency: High (consistent lens across #136 and #150)

## Cost Characteristics
- Relative token consumption: HIGHER than flash (operator explicitly reserves it for high-value work) - Evidence: #147
- Cost efficiency: Good when used for what it is reserved for (review/audit); poor value for cheap research - Evidence: #147
- Typical interaction overhead: Moderate (2 progress checkpoints per review)

## Performance Characteristics
- Response latency: ~1-2 min per verdict
- Throughput: Moderate (deep single reviews, not high-volume)
- Reliability: High (no failures observed)
- Determinism: High (structured, repeatable taxonomy)

## Tool Integration
- External tools: read-only analysis (no writes)
- APIs: opencode CLI
- Repositories: read-only access
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A (autonomous)
- Instruction following: Excellent
- Resistance to ambiguity: High (produced concrete preconditions and remedy lists)
- Responsiveness to critique: N/A
- Recovery from mistakes: N/A (no mistakes observed)

## Protocol Adherence
- Negative constraint respect: PASS (read-only; one verdict per issue)
- Negative constraint violations: 0
- Fallback behavior on error: N/A
- Model substitution without consent: 0
- Process control compliance: Excellent

## Suitable Tasks (evidence-backed)
- Adversarial review of designs with safety/state-machine implications (#135 watcher, #136) - evidence: #136
- Code review of fragile/emergency patches (#145, #150) - evidence: #150
- Design re-review rounds (#177) - evidence: round-1 verdict
- Final audit/sign-off where systems durability matters

## Unsuitable Tasks (evidence-backed)
- Cheap research/web tasks (operator routing rule #147) - evidence: operator direction
- High-volume quick triage (cost:value imbalance) - evidence: #147

## Dependencies
- Works well with: big-pickle/hy3 as complementary lenses (luna=durability, big-pickle=breadth+adversarial, hy3=edge-cases); #154 design iteration as the durable-fix vehicle

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Independent reviewer agreement | #150 MUST-FIX items independently confirmed by hy3 #153 (F3 ephemeral patch) + laguna #152 (fragility Medium) | Agreement |
| Project observation | #136 controls list matches big-pickle #137 hardening list | Repeated |

## Confidence Assessment
- Level: Moderate
- Reviewer: evidence-gathering draft (#190)
- Date: 2026-08-06
- Evidence considered: #136, #150, #177, #147 (operator routing)
- Significant changes from prior assessment: First luna profile (was not previously documented)

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: #136, #150, #177, #147
- Significant changes: First profile; systems/durability lens + operator cost-reservation rule documented
