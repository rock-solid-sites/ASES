---
title: "Model Feedback: opencode/nemotron-3-ultra-free"
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

# Model Feedback: opencode/nemotron-3-ultra-free

## Identification
- Model: nemotron-3-ultra-free
- Provider: opencode (Zen free tier)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #132 (orchestrator allowlist review — replacement for laguna #129), #140-adjacent (free-tier reliability comparison)

## Task Categories Evaluated
- [x] Adversarial review (allowlist #132)
- [x] Replacement/backup reviewer duty (#132 after laguna hang #129)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 3 | #132 recommendations were BROADER but LESS CONSERVATIVE than ling #128/big-pickle #130: recommended find, awk/sed, less, curl -I which the final spec (#127) REJECTED (find mutation flags, sed -i edits files, less redundant, curl body risk) |
| Completeness | 4 | #132 covered 8 tool categories (process, tmux, log, search/filter, system health, file metadata, env, network) |
| Consistency | 4 | Structured category-driven verdict |
| Robustness | 5 | Completed the allowlist review in the SAME window where laguna #129 hung (02:20 -> 02:22, ~2 min) — the only fully reliable free reviewer that window |
| Explainability | 3 | Rationale present but less security-precise (recommended mutation-capable tools) |
| Efficiency | 5 | FASTEST allowlist verdict: plan 02:20, verdict 02:21 (~1 min) |
| Collaboration | 4 | Accepted replacement duty cleanly; one verdict as instructed |
| Instruction Adherence | 5 | Held one-verdict read-only |

## Observed Strengths
- RELIABILITY UNDER FREE-TIER PRESSURE: the only reviewer of the 4-dispatch allowlist wave (ling/big-pickle/nemotron/laguna) that completed with zero reliability issues AND fastest — and it was the REPLACEMENT for the hung laguna - Evidence: #132 timestamps vs #129 hang
- Fast turnaround: ~1 min from plan to verdict - Evidence: #132
- Broad coverage: enumerated 8 categories including pgrep, less, awk/sed, curl -I that others missed - Evidence: #132
- System-health awareness: free/df/uptime/date for OOM/disk prevention - Evidence: #132

## Observed Weaknesses
- LESS SECURITY-CONSERVATIVE than peers: recommended `find` (has -delete/-exec mutation flags), `awk`/`sed` (sed -i edits files), `less`, and `curl -I/--head` (network surface) — all rejected in the final spec #127 - Evidence: #132 recommendations vs #127 FINAL ALLOWLIST SPEC
- Verdict depth lower than big-pickle #130 (no exact prefix scoping, no two-layer permission analysis) - Evidence: #132 vs #130
- Did not flag the guard's pipeline-segment mechanics that big-pickle identified (#130: isAllowedBash requires every pipe segment allowed) - Evidence: #132 vs #130

## Failure Modes Observed
- None observed (1/1 successful). The failure-discrimination rule (#140) does not mention nemotron-specific incidents.

## Context Behavior
- Large context: Handled playbook + ORCHESTRATOR.md + hook-config context (#132)
- Context recovery: N/A
- Instruction retention: High
- Long-term consistency: N/A (single session)

## Cost Characteristics
- Relative token consumption: Low (free tier, moderate length)
- Cost efficiency: Excellent (free + fast + reliable)
- Typical interaction overhead: Low

## Performance Characteristics
- Response latency: VERY FAST (~1-2 min)
- Throughput: High
- Reliability: High (in observed window; free-tier caveats apply)
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
- Negative constraint respect: PASS
- Negative constraint violations: 0
- Fallback behavior on error: N/A
- Model substitution without consent: 0
- Process control compliance: Excellent

## Suitable Tasks (evidence-backed)
- RELIABLE BACKUP REVIEWER when primary hangs (#129 -> #132 replacement) - evidence: #132
- Fast allowlist/permission reviews where breadth is valued - evidence: #132
- Free-tier review tasks needing high completion probability - evidence: #132 completion vs #129 hang

## Unsuitable Tasks (evidence-backed)
- Security-sensitive permission scoping WITHOUT human review of recommendations: recommended mutation-capable tools (find/awk/sed) - evidence: #132 vs #127 rejection
- Precision-scoping tasks (exact prefix/allowlist engineering) — lacked the two-layer mechanics analysis of #130 - evidence: #132

## Dependencies
- Works well with: human/operator synthesis of recommendations (#127 final spec filtered #132's over-broad set), backup-reviewer role

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Project observation | #132 completed where #129 hung (same window, same tier) | Repeated |
| Independent reviewer agreement | #132 partially adopted; find/awk/sed/less/curl rejected in #127 | Agreement (partial) |

## Confidence Assessment
- Level: Emerging-Moderate (single session)
- Reviewer: evidence-gathering draft (#190)
- Date: 2026-08-06
- Evidence considered: #132, #127 final spec, #140
- Significant changes from prior assessment: First nemotron profile

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: #132, #127 final spec, #140
- Significant changes: First profile; backup-reviewer reliability + less-conservative scoping documented
