---
title: "Model Feedback: opencode/laguna-s-2.1-free"
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

# Model Feedback: opencode/laguna-s-2.1-free

## Identification
- Model: laguna-s-2.1-free
- Provider: opencode (Zen free tier)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #129 (allowlist review — FAILED silent hang), #152 (wrapSSE patch review — SUCCESS). Historical rate-limit incidents July 23-26 (#140).

## Task Categories Evaluated
- [x] Adversarial review (allowlist #129 — failed; wrapSSE patch #152 — success)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 4 | #152 verdict correct and consistent with other reviewers (patch reasonable minimal fix; silent retry loop not addressed) |
| Completeness | 4 | #152 covered 4 focus questions + fragility + regression risk with severity ratings |
| Consistency | 4 | Structured severity-based style (#152) |
| Robustness | 2 | Confirmed silent provider-side hang (#129) + historical rate-limit incidents; reliability is the dominant weakness |
| Explainability | 4 | #152 is well-structured with severity per finding |
| Efficiency | 3 | #152 verdict ~6 min after plan (21:12 -> 21:18); #129 failed entirely |
| Collaboration | 3 | #129 produced NO verdict (replacement needed from nemotron #132) |
| Instruction Adherence | 4 | #152 held one-verdict read-only; #129 failed via hang not noncompliance |

## Observed Strengths
- CAREFUL-WHEN-WORKING: #152 is a precise, severity-rated review (Finding 1 severity None, Finding 2 Low, Finding 3 Medium, Finding 4 Low + fragility Medium + regression Low) with exact edge-case analysis - Evidence: #152
- Correct understanding of the retry-loop dynamics: noted the patch makes non-SSE consistent with SSE (not a worsening), and that the silent loop is the unresolved root cause - Evidence: #152 Finding 3
- Structured answers to prescribed focus questions - Evidence: #152 final section

## Observed Weaknesses
- RELIABILITY: silent provider-side hang (#129) — NOT a rate limit (zero ERROR entries, last event outgoing message=stream, ling/big-pickle/nemotron completed same task same window) - Evidence: #129 observation + #140 failure-discrimination rule
- Historical rate-limit incidents (July 23-26) logged 'Provider rate limit exceeded' — a second, distinct failure class - Evidence: #140
- No verdict = wasted dispatch slot (#129 required replacement from nemotron) - Evidence: #129/#132

## Failure Modes Observed
- SILENT PROVIDER-SIDE HANG (primary): outgoing 'message=stream' at 02:01:30, no response, zero ERROR entries, never completed; indistinguishable from working without log inspection - Evidence: #129 (session ses_03aa886c0ffeXKFRLMhDrbTNyd)
- Rate limit (historical): 'Provider rate limit exceeded' / 429 — distinct signature from hang - Evidence: #140

## Context Behavior
- Large context: N/A (no successful large-context task observed beyond #152)
- Context recovery: N/A
- Instruction retention: High (#152)
- Long-term consistency: N/A

## Cost Characteristics
- Relative token consumption: Low (free tier, moderate verdict length)
- Cost efficiency: Poor when hangs are counted (dispatch slot wasted); good when it completes
- Typical interaction overhead: Low

## Performance Characteristics
- Response latency: ~6 min when working (#152)
- Throughput: Moderate
- Reliability: LOW (1 confirmed hang + historical rate limits)
- Determinism: High when working

## Tool Integration
- External tools: read-only analysis
- APIs: opencode CLI
- Repositories: read-only access
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A
- Instruction following: Excellent (#152)
- Resistance to ambiguity: High
- Responsiveness to critique: N/A
- Recovery from mistakes: N/A

## Protocol Adherence
- Negative constraint respect: PASS (#152)
- Negative constraint violations: 0
- Fallback behavior on error: NONE — hang provides no error, needs external watchdog/kill - Evidence: #129
- Model substitution without consent: 0
- Process control compliance: Good (#152)

## Suitable Tasks (evidence-backed)
- Low-priority reviews where a hang can be tolerated (replacement model exists) - evidence: #152 success / #129 hang pattern
- Tasks with external watchdog protection (#146) once deployed - evidence: #129

## Unsuitable Tasks (evidence-backed)
- Any task with a hard delivery deadline: hang risk is real and silent (#129) - evidence: #129
- Sole-reviewer dependency: REQUIRES a backup reviewer (#132 nemotron replaced #129) - evidence: #129/#132
- Unattended overnight tasks: hang went undetected until operator log check - evidence: #129

## Dependencies
- Works well with: backup reviewer (nemotron #132), failure-discrimination procedure (#140), watchdog (#146)
- Needs: external recovery mechanism before reliable dispatch

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Project observation | #129 hang (silent, zero ERROR) + #152 success | Repeated |
| Historical observation | July 23-26 rate-limit incidents | Observed |
| Independent reviewer agreement | #152 consistent with #150/#151/#153 | Agreement |

## Confidence Assessment
- Level: Moderate
- Reviewer: evidence-gathering draft (#190)
- Date: 2026-08-06
- Evidence considered: #129, #152, #140
- Significant changes from prior assessment: Prior model-discipline treated free-model failures as rate limits; #129/#140 established the silent-hang class distinct from rate limits

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: #129, #152, #140
- Significant changes: Silent-hang class distinguished from rate-limit class; reliability flagged as binding constraint
