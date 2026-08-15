---
title: "Model Feedback: opencode-go/deepseek-v4-flash"
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

# Model Feedback: opencode-go/deepseek-v4-flash

## Identification
- Model: deepseek-v4-flash
- Provider: opencode-go (paid; opencode/deepseek-v4-flash-free Zen free variant also exists)
- Access Method: opencode subagent / kickoff default agent (sentinel.default_agent.model = opencode-go/deepseek-v4-flash per hook-config)
- Configuration: default opencode-go provider config (timeout 3600000ms, headerTimeout 300000ms, chunkTimeout 300000ms per #140)
- Session evidence: pp3g-K6yV (#138), pp3g-OZWZ (#142), Tier-1 experiment (#144), wrapSSE binary patch (#145), launch-chain fix (#173), doc updates (#140), operator routing rule (#147), zero-context plan B1-B6 (#361), zero-context plan revision C1-C4 (#365), one-shot reviews synthesis (#373)

## Task Categories Evaluated
- [x] Implementation (fork Rust fix #138; hook-config + plugin TS fix #173)
- [x] Debugging (deep source investigation #144/#145)
- [x] Research (hydration mechanism #142; web research routing #147)
- [x] Documentation (model-discipline + playbook updates #140)
- [x] Binary/byte-level engineering (wrapSSE patch #145)
- [x] Zero-context planning (#361 B1-B6 remediation plan, #365 C1-C4 revision)
- [x] Large-document synthesis (#373 865-line synthesis of 7 one-shot reviews)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 4 | #138 fork fix + tests committed and work preserved (799ce67); #173 fix verified end-to-end with runtime proof; #144 verdict matched #145 controlled repro; but #142 produced NO deliverable |
| Completeness | 4 | #145 patch covered BOTH guard copies (offsets 97992444 + 99193204); #173 covered config + plugin + verification; #142 delivered nothing (stall) |
| Consistency | 5 | Same rigorous method across #138/#144/#145/#173: evidence-first, controlled repro, file:line citations |
| Robustness | 3 | Reliable while running, but 2 confirmed provider-side silent-hangs (#138 10.5h, #142 10.9h) with flags lying as RUNNING |
| Explainability | 5 | #144 verdict had exact reproduction tables; #145 had diff + verification matrix + rebuild instructions; #173 had guard-log evidence chains |
| Efficiency | 4 | Fast when working (#145 patch found+patched+verified in ~1h); low cost; but stalls waste 10h+ of wall-clock |
| Collaboration | 4 | Clean handoff of preserved work (#138 commit before stall); #173 coordinated with operator restarts |
| Instruction Adherence | 4 | Followed read-only constraints (#142, #144 read-only research); #173 stayed in scope (exactly 2 files) |

## Observed Strengths
- Deep source-level investigation: traced config propagation through claude wrapper + systemd-run (#144), located compiled-binary guards at byte offsets and patched both (#145) - Evidence: #144/#145 results
- Rigorous controlled reproduction: fake hanging SSE server with 3 content-type modes proved chunkTimeout bypass (#144) - Evidence: #144 verdict
- Preserves work before failure: #138 committed 163-insertion fork fix + tests BEFORE stalling - Evidence: #138 result
- Verified end-to-end: #173 four-stage evolution (BLOCK -> BLOCK stale -> generic-allow -> GATED) each with guard-log evidence - Evidence: #173
- Zero-context planning grounded on disk: #361 B1-B6 remediation plan (rules ownership matrix, hook logic delta, wrapper deltas all verified read-only), #365 C1-C4 revision (fork init source semantics, NEW skills-inversion finding) - Evidence: #361/#365 result comments
- Large-document synthesis: #373 865-line synthesis of 7 one-shot reviews, corrected reviewer count (7 labeled, not 8+unlabeled), every claim cited reviewer+section - Evidence: #373
- Cheap enough for research/web tasks - per operator routing rule #147

## Observed Weaknesses
- Silent provider-side hangs: 2 confirmed (pp3g-K6yV #138, pp3g-OZWZ #142) - last outgoing stream never returns, zero ERROR entries, process alive, flags RUNNING - Evidence: #138/#142 stall records
- Stall discards the deliverable: #142 was read-only research; the answer was lost with the hang (partial evidence only from pane capture) - Evidence: #142 result
- No recovery from hung stream without external kill/relaunch - Evidence: #138/#142 (both killed by operator)

## Failure Modes Observed
- Silent provider hang (application/json body bypass): last 'stream' never returns, zero ERROR, process alive, flags lie as RUNNING; only outer timeout or operator kill recovers - Evidence: #138 (10.5h), #142 (10.9h), root cause in #144 (chunkTimeout bypassed by non-SSE content-type)
- Killed without commit on read-only tasks: #142 delivered nothing; only pane capture preserved partial findings - Evidence: #142

## Context Behavior
- Large context: Handled 17-file diff contexts and multi-step source archaeology (#145: 179MB binary, offset math)
- Context recovery: Good pre-hang; no in-hang recovery possible (stream-level fault)
- Instruction retention: High (read-only respected #142/#144; scope held #173)
- Long-term consistency: Strong across multiple sessions (#138/#144/#145/#173 consistent method)

## Cost Characteristics
- Relative token consumption: Low (preferred for research/web per #147)
- Cost efficiency: Excellent value; operator rule: 'deepseek-v4-flash is the PREFERRED model for research/web tasks; gpt-5.6-luna is RESERVED for coding/adversarial/audits' (#147)
- Typical interaction overhead: Low

## Performance Characteristics
- Response latency: Fast
- Throughput: High (#145 full patch cycle ~1h; #138 163-insertion fix before stall)
- Reliability: MEDIUM - 2 confirmed hangs in ~5 dispatched sessions (40%)
- Determinism: High when working

## Tool Integration
- External tools: git, cargo check/test (fork fix #138), tsc (plugin #173), python harness + fake server (#144/#145)
- APIs: opencode CLI (run), claude wrapper chain
- Repositories: crosslink fork source (#138), ASES config/plugins (#173), opencode binary (#145)
- Execution environments: Linux, tmux, systemd-run

## Human Interaction
- Clarification behavior: N/A (autonomous)
- Instruction following: Excellent (#173 exactly 2 files; #142/#144 read-only)
- Resistance to ambiguity: High (made and documented decisions, e.g. #145 chose binary patch over source rebuild for interim)
- Responsiveness to critique: N/A
- Recovery from mistakes: Good pre-hang (#145 first offset pass then corrected to 2 copies)

## Protocol Adherence
- Negative constraint respect: PASS (read-only constraints held #142/#144; scope held #173)
- Negative constraint violations: 0
- Fallback behavior on error: None for hangs (needs external kill/relaunch per #146)
- Model substitution without consent: 0
- Process control compliance: Excellent (plan/checkpoint/result discipline in all sessions)

## Suitable Tasks (evidence-backed)
- Deep source/mechanism investigation with controlled repro (#144/#145) - evidence: two successful verdicts
- Fork/plugin implementation with verification (#138, #173) - evidence: commits 799ce67, 17a1960, a73d12f
- Research + web tasks per operator routing (#147) - evidence: operator rule
- Documentation updates (#140) - evidence: mirrored to tripn-astro
- Zero-context planning / remediation plan authoring (#361/#365) - evidence: both plans grounded on disk, revised through two review rounds
- Large-document synthesis (#373) - evidence: 865-line synthesis, corrected reviewer count

## Unsuitable Tasks (evidence-backed)
- Long-running unattended tasks with no watchdog: hangs are silent and un-recoverable without external kill (#138/#142) - evidence: 2 stalls
- Any task where 10h+ stall is unacceptable without Tier-1/watcher protection (#146 prerequisite) - evidence: #138/#142
- Tasks needing guaranteed delivery under short cap: #142 ran past 15-min cap and still delivered nothing - evidence: #142

## Dependencies
- Works well with: controlled repro harnesses, opencode provider timeout config (defense-in-depth), #135/#146 watcher kill/restart as recovery safety net
- Needs: external watchdog until silent-hang fix (#154/#146) lands

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Controlled experiment | #144 fake-server repro; #145 verification table | Replicated |
| Project observation | #138/#142 stalls (2x) | Repeated |
| Independent reviewer agreement | #150-#153 consensus on #145 patch (directionally correct) | Agreement |

## Confidence Assessment
- Level: Moderate-High
- Reviewer: evidence-gathering draft (#190); updated 2026-08-15 (session #27 evidence: #361/#365/#373)
- Date: 2026-08-06
- Evidence considered: #138/#142/#144/#145/#173/#140/#147/#361/#365/#373
- Significant changes from prior assessment: First consolidated flash profile; prior model-discipline only listed flash as paid Go model without capability evidence. Session #27 added zero-context planning + large-document synthesis strengths.

## Last Review
- Date: 2026-08-15
- Reviewer: session #27 update (#374)
- Evidence considered: #138/#142/#144/#145/#173/#140/#147/#361/#365/#373 (9 sessions)
- Significant changes: Added zero-context planning (#361/#365) and large-document synthesis (#373) strengths; confidence raised to Moderate-High.
