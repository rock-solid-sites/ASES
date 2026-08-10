---
title: "Model Feedback: opencode/big-pickle"
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

# Model Feedback: opencode/big-pickle

## Identification
- Model: big-pickle
- Provider: opencode (Zen free tier)
- Access Method: opencode subagent (reviewer role)
- Configuration: free tier, reviewer mode, read-only
- Session evidence: #130 (orchestrator allowlist review), #137 (watcher plan review), #149 (aborted wrapSSE review — scope drift), #178 (design review round 1), #184 (design re-review round 2)

## Task Categories Evaluated
- [x] Adversarial review (allowlist #130, watcher plan #137, design #178/#184)
- [x] Design review (durable fix rounds)
- [x] Live-system verification (#137 verified launch.rs, heartbeat.py, opencode config against running system)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 5 | #137 review was the highest-quality verdict in the dataset: verified watchdog exit-condition bug (launch.rs:88-89), heartbeat primary signal, opencode timeout knobs, claude=opencode wrapper — all confirmed live; #130 classified 16 candidates with exact prefix scoping |
| Completeness | 5 | #137 covered 5 evaluation points + 12 missing items; #130 gave ADD/DO-NOT-ADD with exact scoped prefixes for both permission layers |
| Consistency | 5 | Breadth+adversarial lens consistent across #130/#137/#178/#184 |
| Robustness | 4 | Reliable when scoped; see failure mode below |
| Explainability | 5 | Most detailed verdicts in the dataset; every claim file:line-grounded; #137 had live `ps` evidence of the watchdog running |
| Efficiency | 4 | #130 verdict in ~10 min; #137 verdict in ~9 min with substantial live verification |
| Collaboration | 3 | Normally clean; #149 was a serious scope-drift incident (see failure modes) |
| Instruction Adherence | 4 | Held 'ONE verdict' and isolated-channel rules in #130/#137; FAILED scoping in #149 (killed) |

## Observed Strengths
- BREADTH + ADVERSARIAL LENS (signature style): surveys the whole problem space and attacks it from multiple angles — operational, security, race-condition, systemic - Evidence: #137 (worktree cleanup races, signing-key orphan risk, hydration/sync interaction, watcher failure modes)
- Live-system verification: #137 did not review the plan abstractly — it verified launch.rs:84-121 watchdog, .kickoff-status lifecycle, heartbeat.py, opencode 1.18.11 config schema against the running system, and even found the watchdog is inert due to exit-condition bug - Evidence: #137 (later became #138 fork bug)
- Practical implementation guidance: #130 gave exact scoped bash prefixes per layer and warned both permission layers must be updated together (guard requires every pipe segment allowed) - Evidence: #130 implementation notes
- Systemic-failure thinking: #137's '≥2 stalls in a window = HALT, no relaunch' correlation guard and auto-relaunch masking critique - Evidence: #137
- Reuse-over-build discipline: #137 found the nudge already exists in crosslink watchdog and should be FIXED not duplicated - Evidence: #137 missing-item 1

## Observed Weaknesses
- SCOPE DRIFT RISK (confirmed failure): #149 was killed for drifting into crosslink fork sync/hydration internals (sync.rs, cache.rs, bootstrap.rs, hub-cache) and exploring 'an env override would let me use my identity with the parent's data' — security-sensitive territory it was never asked to touch - Evidence: #149 observation
- Very long verdicts: #137 is exceptionally long; token-heavy for a free model - Evidence: #137 length
- Conditional verdicts may require synthesis: #178 CONDITIONAL PASS, #184 CONDITIONAL with 2 impl-level fixes — good but needs operator to act on them - Evidence: #178/#184

## Failure Modes Observed
- Scope drift into forbidden/security-sensitive territory mid-review; no verdict posted; agent killed + cleaned up (#149) - Context: #145 patch review, drifted to fork sync/hydration + identity-override exploration - Evidence: #149
- NOTE: #149 is the ONLY confirmed big-pickle failure; #130/#137/#178/#184 all succeeded.

## Context Behavior
- Large context: Handled #135 watcher plan + crosslink source + live system state simultaneously (#137)
- Context recovery: N/A (no recovery event observed)
- Instruction retention: High when scoped; #149 shows scoping must be re-asserted mid-task
- Long-term consistency: High (consistent lens across all 4 successful sessions)

## Cost Characteristics
- Relative token consumption: HIGH for a free model (very long verdicts, e.g. #137)
- Cost efficiency: Excellent (free tier; high value delivered)
- Typical interaction overhead: Low (few checkpoints, single verdict)

## Performance Characteristics
- Response latency: ~10 min per deep review (with live verification)
- Throughput: Moderate-High (one deep review per dispatch)
- Reliability: High (4/5 successful)
- Determinism: High (reproducible rigor)

## Tool Integration
- External tools: rg, cat, git (read), ps, file reads (live verification #137)
- APIs: opencode CLI
- Repositories: crosslink source, ASES config, live system state
- Execution environments: Linux

## Human Interaction
- Clarification behavior: N/A (autonomous)
- Instruction following: Good when tightly scoped; #149 demonstrates the need for re-scoping/kill-early discipline
- Resistance to ambiguity: High
- Responsiveness to critique: N/A
- Recovery from mistakes: N/A

## Protocol Adherence
- Negative constraint respect: PASS in 4/5 sessions; FAILED in #149 (entered security-sensitive territory)
- Negative constraint violations: 1 (High severity, #149)
- Fallback behavior on error: N/A
- Model substitution without consent: 0
- Process control compliance: Excellent in successful sessions (plan/checkpoint/result discipline)

## Suitable Tasks (evidence-backed)
- Deep adversarial review of designs with live-system verification (#135 watcher -> #137) - evidence: #137
- Permission/security policy review with exact scoping (#127 allowlist -> #130) - evidence: #130
- Design review rounds (#154 -> #178/#184) - evidence: both conditional verdicts
- Root-cause hunting in infrastructure code (found #138 watchdog bug) - evidence: #137 -> #138

## Unsuitable Tasks (evidence-backed)
- Tight-scope reviews where scope-drift is dangerous: requires re-scoping mid-task or early kill (#149) - evidence: #149 aborted
- Tasks involving access to security-sensitive internals (identity, keys, cross-repo data) - evidence: #149 territory
- Quick triage: too thorough/slow for fast gates

## Dependencies
- Works well with: tight explicit scope + checkpoints; luna (durability) and hy3 (edge-cases) as complementary lenses; kill-early on visible drift per #149 lesson

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Controlled experiment | #130 16-candidate classification; #137 live-system verification | Replicated |
| Project observation | #149 scope-drift incident | Observed |
| Independent reviewer agreement | #137 findings -> #138 fork bug (accepted); #150/#152/#153 partial agreement on #145 | Agreement |

## Confidence Assessment
- Level: Moderate-High
- Reviewer: evidence-gathering draft (#190)
- Date: 2026-08-06
- Evidence considered: #130, #137, #149, #178, #184
- Significant changes from prior assessment: First big-pickle profile; #149 scope-drift must be documented as a dispatch risk

## Last Review
- Date: 2026-08-06
- Reviewer: evidence-gathering draft (#190)
- Evidence considered: #130, #137, #149, #178, #184
- Significant changes: First profile; breadth+adversarial+live-system lens and scope-drift dispatch risk documented
