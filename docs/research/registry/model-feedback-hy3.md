---
title: "Model Feedback: opencode-go/hy3 — MERGED (existing doc + new session evidence)"
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

# Model Feedback: opencode-go/hy3 — MERGED (existing doc + new session evidence)

## Identification
- Model: hy3
- Provider: opencode-go (paid) — NOTE: existing doc says opencode/hy3-free; model-discipline.md lists opencode-go/hy3 under Go paid. Treat as opencode-go/hy3 (paid) with a free variant history.
- Release Date: 2026
- Access Method: opencode subagent
- Configuration: temperature 0.2, subagent mode
- Session evidence: existing doc (2026-07-11: 3 parallel impl tasks, 2817 tests), NEW: #153 (wrapSSE patch review), #176 (design review round 1, r1), #182 (design re-review round 2, r1), #154 synthesis (design-review synthesis)

## Task Categories Evaluated
- [x] Implementation (existing doc: 3 parallel tasks)
- [x] Refactoring (existing doc)
- [x] Multi-file editing (existing doc)
- [x] Adversarial review (#153, #176, #182)
- [x] Design re-review with source re-derivation (#182)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 5 | #153 findings F1-F4 independently matched luna #150 MUST-FIX/SHOULD-CONSIDER items; #182 V1-V5 caught REAL compile/parameter defects in the #180 design (Patch B does not compile; harness params contradiction) — all subsequently adopted in #186 |
| Completeness | 5 | #153 gave 5 severity-rated findings + 4 focus-question answers + safer alternatives; #182 verified ~20 source citations independently against v1.18.13 checkout and found V1-V5 blockers |
| Consistency | 5 | EDGE-CASE lens consistent: #153 F2 (slow-but-legit non-SSE false abort), F4 (ctl abort blast radius); #182 V1 (undeclared bodyIdleAbortCtl), V2 (harness param contradiction), V3 (absolute-cap timer unsound) |
| Robustness | 5 | No failures across implementation doc + 3 review sessions; high reliability |
| Explainability | 5 | Severity-rated, independently source-verified verdicts (#182 method section is exemplary) |
| Efficiency | 4 | #153 verdict ~11 min; #182 deep source re-verification in ~18 min |
| Collaboration | 5 | Isolated-channel discipline held; #154 synthesis shows hy3 (r1) was the most rigorous reviewer |
| Instruction Adherence | 5 | #182 explicitly did NOT trust the change-log — re-derived from source as instructed; existing-doc protocol failures were ORCHESTRATOR failures, not hy3 |

## Observed Strengths
- NOVEL EDGE-CASE LENS (signature): consistently finds failure modes other reviewers miss — #153 F2 (slow non-SSE false abort regression), F4 (shared AbortController blast radius), #176 B2 (Option B total-completion deadline WRONG shape -> idle-progress), #182 V1-V5 (compile errors, parameter contradictions, timer lifecycle) - Evidence: #153/#176/#182
- Independent source re-derivation: #182 did not accept the change-log; re-verified provider.ts:40, aisdk.ts:29, retry.ts:176-199, llm.ts:373, build.ts:192-199 against a v1.18.13 checkout with ~20 citations - Evidence: #182 method table
- Fast parallel implementation (existing doc): 3 independent tasks in ~5 min, 2817 tests pass, 0 findings from 2 reviewers - Evidence: existing model-feedback-hy3.md
- Correct pattern adherence + clean handoffs (existing doc) - Evidence: existing doc
- Progressive rigor in review rounds: #176 (round 1: 3 blockers + 13 findings) -> #182 (round 2: V1-V5 compile-level, architecture accepted) — appropriate escalation as design matured - Evidence: #154 synthesis + #182

## Observed Weaknesses
- Occasional syntax errors in complex multi-file refactors (existing doc: container.rs missing brace caught by cargo check) - Evidence: existing doc
- Design-blocker findings sometimes implementation-level rather than architectural (V1-V5 in #182 are patch-code issues) — could frustrate design authors - Evidence: #182
- Generic error messages when build checks fail (existing doc) - Evidence: existing doc

## Failure Modes Observed
- Syntax error in container.rs during refactor (missing brace) — caught by cargo check, recovered immediately - Evidence: existing doc
- None in review sessions (#153/#176/#182 all successful)
- NOTE: existing-doc protocol failures (direct coding instead of subagent delegation) were attributed to ORCHESTRATOR, not hy3

## Context Behavior
- Large context: Good (handled 17-file diff in existing doc; full design + source checkout in #182)
- Context recovery: Good (recovered from syntax error without losing context)
- Instruction retention: High (#182 followed 'do not trust change-log' instruction)
- Long-term consistency: High (consistent edge-case rigor across #153/#176/#182)

## Cost Characteristics
- Relative token consumption: Moderate (deep source re-verification is token-heavy)
- Cost efficiency: Good (paid tier but high-value findings; existing doc rated excellent on free variant)
- Typical interaction overhead: Low-Moderate

## Performance Characteristics
- Response latency: ~10-20 min for deep reviews
- Throughput: High (parallel impl in existing doc)
- Reliability: High
- Determinism: High (reproducible source-verified findings)

## Tool Integration
- External tools: cargo check/test (impl), rg/git/read (review, #182 source verification)
- APIs: opencode CLI
- Repositories: crosslink, opencode source checkout (/tmp/opencode/opencode-upstream-r3)
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A (autonomous)
- Instruction following: Excellent (#182 is the best example)
- Resistance to ambiguity: High (made sensible choices where underspecified per existing doc)
- Responsiveness to critique: N/A
- Recovery from mistakes: Good (existing doc fixed syntax error immediately)

## Protocol Adherence
- Negative constraint respect: Existing doc: FAILED (3x bash when told to use subagent — orchestration-context failure); review sessions: PASS
- Negative constraint violations: 3 (existing doc, High severity, orchestration-related); 0 in #153/#176/#182
- Fallback behavior on error: Autonomous (fixed syntax error immediately)
- Model substitution without consent: 0
- Process control compliance: Existing doc: FAILED (did not use subagent when instructed — orchestration failure); reviews: excellent

## Suitable Tasks (evidence-backed)
- Novel edge-case hunting in designs/patches (#153 F2/F4, #176 B2, #182 V1-V5) - evidence: three successful reviews
- Source-level verification of design claims (does not trust change-logs) - evidence: #182
- Parallel implementation of independent features (existing doc) - evidence: existing doc
- Design review rounds (r1 role in #154 rounds) - evidence: #154 synthesis

## Unsuitable Tasks (evidence-backed)
- Complex architectural design (no evidence of design-generation capability; strength is critique) - evidence: absence
- Open-ended research (no evidence) - evidence: absence

## Dependencies
- Works well with: real source checkouts for verification; complements luna (durability) and big-pickle (breadth); reviewer-r1 role in multi-round design review

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Controlled experiment | #153 5 findings; #182 ~20 source re-verifications | Replicated |
| Project observation | #154 synthesis (r1 = most rigorous); #186 adopted V1-V5 | Repeated |
| Independent reviewer agreement | #153 F1-F4 matches luna #150; #176/#182 findings adopted | Agreement |

## Confidence Assessment
- Level: High
- Reviewer: North Mini Code (review), Gemini 3.1 Pro (audit) — original; evidence-gathering draft (#190) — updated
- Date: 2026-08-06 (updated from 2026-07-11)
- Evidence considered: 2817 tests pass, 0 findings from 2 reviewers (existing doc) + #153, #176, #182, #154 synthesis
- Significant changes from prior assessment: Expanded from implementation-only to include the strongest review-lens profile (edge-case hunter); provider corrected to opencode-go (paid)

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: existing doc + #153, #176, #182, #154 synthesis
- Significant changes: Review-session evidence added; provider corrected to opencode-go (paid)
