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
last_updated: 2026-08-15
---

# Model Feedback: opencode/nemotron-3-ultra-free

## Identification
- Model: nemotron-3-ultra-free
- Provider: opencode (Zen free tier)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #132 (orchestrator allowlist review — replacement for laguna #129), #140-adjacent (free-tier reliability comparison), #360 (2/2 FAILURES — free-tier Nvidia endpoint unavailable)

## Task Categories Evaluated
- [x] Adversarial review (allowlist #132)
- [x] Replacement/backup reviewer duty (#132 after laguna hang #129)
- [x] Reliability under free-tier provider pressure (#360 — failed 2/2)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 3 | #132 recommendations were BROADER but LESS CONSERVATIVE than ling #128/big-pickle #130: recommended find, awk/sed, less, curl -I which the final spec (#127) REJECTED (find mutation flags, sed -i edits files, less redundant, curl body risk) |
| Completeness | 4 | #132 covered 8 tool categories (process, tmux, log, search/filter, system health, file metadata, env, network) |
| Consistency | 4 | Structured category-driven verdict |
| Robustness | 2 | Historical: completed allowlist review in the SAME window where laguna #129 hung (#132, ~2 min) — but 2/2 FAILURES on 2026-08-14 (#360, free-tier Nvidia 502) supersede the single success; endpoint availability is the binding constraint |
| Explainability | 3 | Rationale present but less security-precise (recommended mutation-capable tools) |
| Efficiency | 5 | FASTEST allowlist verdict: plan 02:20, verdict 02:21 (~1 min) |
| Collaboration | 4 | Accepted replacement duty cleanly; one verdict as instructed |
| Instruction Adherence | 5 | Held one-verdict read-only |

## Observed Strengths
- RELIABILITY UNDER FREE-TIER PRESSURE (HISTORICAL, #132): the only reviewer of the 4-dispatch allowlist wave (ling/big-pickle/nemotron/laguna) that completed with zero reliability issues AND fastest — and it was the REPLACEMENT for the hung laguna - Evidence: #132 timestamps vs #129 hang. **Superseded by #360 2/2 failures — no longer a reliable backup.**
- Fast turnaround: ~1 min from plan to verdict - Evidence: #132
- Broad coverage: enumerated 8 categories including pgrep, less, awk/sed, curl -I that others missed - Evidence: #132
- System-health awareness: free/df/uptime/date for OOM/disk prevention - Evidence: #132

## Observed Weaknesses
- LESS SECURITY-CONSERVATIVE than peers: recommended `find` (has -delete/-exec mutation flags), `awk`/`sed` (sed -i edits files), `less`, and `curl -I/--head` (network surface) — all rejected in the final spec #127 - Evidence: #132 recommendations vs #127 FINAL ALLOWLIST SPEC
- Verdict depth lower than big-pickle #130 (no exact prefix scoping, no two-layer permission analysis) - Evidence: #132 vs #130
- Did not flag the guard's pipeline-segment mechanics that big-pickle identified (#130: isAllowedBash requires every pipe segment allowed) - Evidence: #132 vs #130

## Failure Modes Observed
- **2/2 FAILURES on 2026-08-14 (#360)**: 'Streaming response failed: [502] Upstream error from Nvidia: Internal server error' — free-tier Nvidia endpoint unavailable; agents pp3g-Iwzk + pp3g-klf4 both failed, no verdict delivered. This SUPERSEDES the earlier 1/1 success: the free-tier Nvidia endpoint is not a reliable dependency, and free-tier Nemotron should NOT be used for deadline-critical reviews.
- Prior to #360: None observed (1/1 successful, #132). The failure-discrimination rule (#140) did not mention nemotron-specific incidents.

## Context Behavior
- Large context: Handled playbook + ORCHESTRATOR.md + hook-config context (#132)
- Context recovery: N/A
- Instruction retention: High
- Long-term consistency: N/A (single success, then 2/2 failures)

## Cost Characteristics
- Relative token consumption: Low (free tier, moderate length)
- Cost efficiency: Good when endpoint available (free + fast); poor when endpoint down (2/2 #360)
- Typical interaction overhead: Low

## Performance Characteristics
- Response latency: VERY FAST (~1-2 min)
- Throughput: High
- Reliability: LOW for deadline-critical (2/2 failures 2026-08-14 #360); historical 1/1 success #132
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
- Fast allowlist/permission reviews where breadth is valued - evidence: #132
- Free-tier review tasks needing high completion probability — CAVEAT: 2/2 failures on 2026-08-14 (#360); verify endpoint availability before deadline-critical use

## Unsuitable Tasks (evidence-backed)
- Deadline-critical reviews: free-tier Nvidia endpoint failed 2/2 with 502 (#360)
- Backup reviewer duty for hung primary: failed 2/2 (#360) — use a paid fallback instead
- Security-sensitive permission scoping WITHOUT human review of recommendations: recommended mutation-capable tools (find/awk/sed) - evidence: #132 vs #127 rejection
- Precision-scoping tasks (exact prefix/allowlist engineering) — lacked the two-layer mechanics analysis of #130 - evidence: #132

## Dependencies
- Works well with: human/operator synthesis of recommendations (#127 final spec filtered #132's over-broad set); NO LONGER backup-reviewer role (#360 2/2 failures — use paid fallback)

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Project observation | #132 completed where #129 hung (same window, same tier) | Repeated |
| Independent reviewer agreement | #132 partially adopted; find/awk/sed/less/curl rejected in #127 | Agreement (partial) |

## Confidence Assessment
- Level: Downgraded (Emerging-Moderate on 1/1 success #132; 2/2 failures #360 make it unreliable for deadline-critical work)
- Reviewer: evidence-gathering draft (#190); updated 2026-08-15 (session #27 evidence: #360)
- Date: 2026-08-06
- Evidence considered: #132, #127 final spec, #140, #360
- Significant changes from prior assessment: First nemotron profile; #360 2/2 free-tier failures added — removed from backup-reviewer recommendation

## Last Review
- Date: 2026-08-15
- Reviewer: session #27 update (#374)
- Evidence considered: #132, #127 final spec, #140, #360
- Significant changes: 2/2 Nvidia 502 failures on 2026-08-14 (#360); removed from backup-reviewer routing; free-tier Nemotron NOT for deadline-critical reviews
