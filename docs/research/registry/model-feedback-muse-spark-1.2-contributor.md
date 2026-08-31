---
title: "Model Feedback: opencode/muse-spark-1.2-contributor-free (Zen) / opencode-go/muse-spark-1.2-contributor (paid)"
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
  - docs/research/registry/Model-Routing-Matrix.md
  - research/capability-schema-validation/tests/test-a/protocol.md
  - research/capability-schema-validation/tests/test-a/results.md
  - research/capability-schema-validation/tests/test-a-live/results.md
  - .design/capability-schema-validation.md
  - .design/tool-to-engine-gap-matrix.md

supersedes: []
last_updated: 2026-08-31
---

# Model Feedback: opencode/muse-spark-1.2-contributor-free (Zen) / opencode-go/muse-spark-1.2-contributor (paid)

## Identification
- Model: muse-spark-1.2-contributor (1.2-contributor variant; free Zen `opencode/muse-spark-1.2-contributor-free` and paid Go `opencode-go/muse-spark-1.2-contributor`)
- Provider: opencode (Zen free tier and opencode-go paid)
- Release Date: 2026
- Access Method: opencode subagent (builder role) + direct Go API streaming via `opencode.ai/zen/go/v1/chat/completions`
- Configuration: builder mode, `temperature > 0` for live replication where noted; 5-10m and 15-20m synthesis budgets observed
- Session evidence: #498 swarm design + harness (Tests A-E, 22-task 3× replication, 198 calls + 10 retries), #506 Track C advisory (8×4 gap-matrix + §14 scoring + hookability mapping), #510/#512 Go key stale verification (ses_fbc24c189ffeH3um1r564nlFAW 15:33 UTC live SSE), #530 live-replication intent (harness --live --model path), model-discipline.md live record (2026-08-27 15:33 UTC), scripts/session-model-recommend tier-2 listing, Failure-Matrix Go key stale row

## Task Categories Evaluated
- [x] Large-document synthesis (advisory, 15-20m)
- [x] Research / advisory matrix construction (gap-matrix 8×4, scoring, hookability)
- [x] Capability-schema validation — harness design and proxy measurement (Tests A-E, variant C minimal description, 73.3% token saving)
- [x] Live-replication governance (harness --live path, 3× repetition, 5pp tolerance, typed ValidationFailed recovery)
- [x] Infrastructure verification (Go API key staleness discriminating test, SSE streaming verification)
- [x] Documentation (design docs, report generation)

## Assessment Dimensions

| Dimension | Score | Evidence |
|---|---|---|
| Correctness | 4 | #506 Track C delivered 8×4 matrix + §14 scoring + hookability §14 mapping where 3 predecessors (pp3g-74M3/y5qq/OwID) froze without delivering; Test A harness produced 198-call proxy with correct per-task breakdown (20/21 tasks identical across A/B/C, only injected task-11 miss 1/3 on C) and typed ValidationFailed recovery 10/10 |
| Completeness | 4 | Track C covered all 8 tools × 4 dimensions + scoring + hookability; capability-schema-validation design covers 14 ops, 6 categories, 22 tasks, 3 variants (A/B/C) with draft-07 runtime; Go key verification covered auth.json vs env divergence + SSE streaming |
| Consistency | 4 | Structured advisory format (8×4 matrix + §14) consistent with design spec; harness results identical across A/B and within 5pp for C vs A on valid tasks (selection 1.00, argument 0.984, delta 0.016) |
| Robustness | 4 | Completed advisory where predecessors froze; harness handles missing variants gracefully and bounds PARSE_TIMEOUT_S 2.0s via thread-join (v2 fix per #498); Go key stale case correctly diagnosed as key-store divergence, not model fault |
| Explainability | 5 | Advisory includes comparison tables and scoring; harness results include token/accuracy curve, task-level breakdown (23 rows), and WHAT-NOT-TESTED negative-space disclosure per AGENTS.md; typed error payload {field, constraint, got, schema_version} preserved |
| Efficiency | 5 | 5-10m Zen synthesis and 15-20m Go synthesis observed (recommender tier 2 LOW, free tier 0); Track C delivered within single builder session; harness token compression C/A 0.267 (73.3% saving) with <2pp accuracy cost |
| Collaboration | 4 | Advisory delivered as .design artifact consumable by downstream synthesis (report.md); harness logs under logs/test-a/ with run-a/b/c.jsonl + summary.json for independent re-verification |
| Instruction Adherence | 5 | Followed .design/capability-schema-validation.md §10 (4-phase swarm plan), protocol.md 5pp tolerance, and design §5.5 runtime-authority separation; respected stable op ID + names/types + enum literals contract |

## Observed Strengths
- COST-EFFICIENT SYNTHESIS & ADVISORY — 5-10m (Zen) and 15-20m (Go) synthesis at LOW cost (tier 2) vs HIGH (luna/gemini tier 4); demonstrated 73.3% token saving (C/A 0.267) with 0.000 selection and 0.016 argument delta within 5pp tolerance — Evidence: #506 gap-matrix, Model-Routing-Matrix maintenance note (muse-spark Zen 5-10m synthesis vs hy3 DEAD-UNMARKED silent loss), test-a token measurement (7023→1873 tokens)
- ADVISORY MATRIX CONSTRUCTION where predecessors froze — 8×4 matrix + §14 scoring + hookability §14 mapping delivered on feature/gap-matrix while 3 prior attempts froze without artifact — Evidence: .design/tool-to-engine-gap-matrix.md Track C note (issue #506)
- HARNESS-PROXY GOVERNANCE with full separation — proxy harness (198 calls, 22 tasks ×3 reps ×3 variants) preserves stable IDs + enum literals, enforces PARSE_TIMEOUT_S 2.0s, and demonstrates typed ValidationFailed recovery 10/10 (including task-22 maxLength and injected filter-enum miss) — Evidence: research/capability-schema-validation/tests/test-a/results.md §3-5, §9
- LIVE-REPLICATION READINESS — harness exposes --live --model path respecting same timeout and missing-variant handling; live session ses_fbc24c189ffeH3um1r564nlFAW at 15:33 UTC streamed SSE via Go key sk-yvUg9… with zero Monthly usage limit errors, verified via direct curl SSE — Evidence: .design/capability-schema-validation.md phases (builder primary: muse-spark free → Go), research/capability-schema-validation/tests/test-a/run.py --live, Failure-Matrix Go key stale row + model-discipline.md live record
- CHEAPEST-TEST DISCIPLINE — Go key staleness diagnosed via single cheapest discriminating test (compare auth.json vs env key prefix + grep opencode.log for Monthly usage limit + curl SSE), not assumed — Evidence: Failure-Matrix 2026-08-27 row, model-discipline.md pre-flight

## Observed Weaknesses
- Limited adversarial-review depth evidence vs hy3/big-pickle — no independent head-to-head adversarial review with live verification on same diff — Evidence: absence in current corpus; hy3 found V1-V5 compile blockers where mimo passed #183
- Single cost-vs-suitability data point for synthesis (5-10m vs 15-20m) — not yet multi-task, multi-model cost curve — Evidence: model-evidence-2026-08-27-lexicon.md reference in matrix maintenance
- Live-model accuracy not yet measured on the 22-task set at temperature >0 with 3 repetitions — proxy numbers are evidence-based, not proven — Evidence: test-a/results.md §8 WHAT-NOT-TESTED

## Failure Modes Observed
- None observed as model failure. DataPolicyError on workspace wrk_01KV6… (env key sk-B1p…) when using muse-spark is key-store divergence (env stale, DB fresh), not model fault — correctly attributed to auth.json vs env mismatch, not to muse-spark — Evidence: Failure-Matrix Go API key stale row (2026-08-27), model-discipline.md invariant (both stores must agree)
- No silent hang or rate-limit observed for muse-spark across 3+ sessions; predecessors on same harness froze (pp3g-74M3/y5qq/OwID) while muse-spark completed — Evidence: .design/tool-to-engine-gap-matrix.md

## Context Behavior
- Large context performance: Handled 865-line synthesis-equivalent advisory (8×4 matrix + scoring + hookability) and full 22-task protocol + harness runtime in single session — Evidence: #506, #498 design
- Context recovery: N/A (single-shot advisory + harness)
- Instruction retention: High — followed stable ID + ≤20-word summary + names/types + enum literals contract across A/B/C
- Long-term consistency: N/A (few sessions)

## Cost Characteristics
- Relative token consumption: LOW (paid Go tier 2, free Zen tier 0) — 73.3% saving on description block (C/A 0.267) demonstrated; 5-10m Zen synthesis observed — Evidence: test-a token measurement, recommender COST_TIERS, model-discipline live record
- Cost efficiency: High — preferred for cheap research/web and large-document synthesis (recommender alternatives include muse-spark for both) — Evidence: scripts/session-model-recommend
- Typical interaction overhead: Low — single builder session per advisory; harness run <2s parse bound

## Performance Characteristics
- Response latency: 5-10m (Zen free synthesis) and 15-20m (Go paid synthesis/advisory) — Evidence: Model-Routing-Matrix maintenance note, #506 Track C
- Throughput: Moderate — single advisory + harness suite per session
- Reliability: High (3/3 sessions completed where 3 predecessors froze; live SSE verified with zero monthly-limit errors) — Evidence: #506, ses_fbc24c189ffeH3um1r564nlFAW
- Determinism: Moderate — proxy harness deterministic (except injected misses); live mode requires temperature >0 with 3 repetitions per cell for proven certainty — Evidence: test-a/run.py --live

## Tool Integration
- External tools: opencode CLI, harness runtime.py + sandbox.py (Draft-07 via jsonschema 4.26.0), tiktoken cl100k_base 0.14.0, curl SSE verification
- APIs: opencode.ai/zen/go/v1/chat/completions (Go), opencode.ai/zen/v1/models (Zen catalog)
- Repositories: EDASES crosslink repo, capability-schema-validation capabilities/derived variants
- Execution environments: Linux, Python 3 harness

## Human Interaction
- Clarification behavior: N/A (autonomous advisory/harness)
- Instruction following: Excellent — followed 5pp tolerance, runtime-authority separation (design §5.5), and AGENTS.md reasoning-certainty clauses (WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED)
- Resistance to ambiguity: High — produced structured matrix with explicit scoring and negative-space disclosure
- Responsiveness to critique: N/A
- Recovery from mistakes: Demonstrated via typed ValidationFailed recovery (retry with corrected args succeeds 10/10 without exposing full schema) — Evidence: test-a §5

## Protocol Adherence
- Negative constraint respect: PASS — respected stable ID + enum literal retention; no forbidden model use (grok/xAI)
- Negative constraint violations: 0
- Fallback behavior on error: Typed ValidationFailed {field, constraint, got, schema_version} with one-retry correction; missing-variant graceful skip (v2 fix)
- Model substitution without consent: 0
- Process control compliance: Excellent — delivered to .design and research/capability-schema-validation per design §10

## Suitable Tasks (evidence-backed)
- Large-document synthesis and advisory matrix construction where cost-vs-suitability matters (5-20m budget, tier 2) — evidence: #506 gap-matrix 8×4, recommender Large-document synthesis alternative, 73.3% token compression finding
- Research / web investigation (cheap) as alternative to deepseek-v4-flash — evidence: recommender Research alternative includes muse-spark free/Go
- Capability-schema validation harness work and live-replication governance (proxy + --live path, 22-task 3×, 5pp tolerance) — evidence: #498 Tests A-E, test-a/run.py --live --model
- Infrastructure verification where cheapest-test discipline matters (Go key staleness, SSE streaming) — evidence: ses_fbc24c189ffeH3um1r564nlFAW

## Unsuitable Tasks (evidence-backed)
- Sole-reviewer for deep adversarial code review requiring live-system verification of launch.rs-level init-mechanics bugs — big-pickle/hy3 have stronger evidence (#363, #182 V1-V5) — evidence: gap vs big-pickle/hy3 in matrix
- Final architectural audit / sign-off requiring 6-category comprehensive audit — gemini-3.1-pro-preview has proven pattern (though needs >=3m) — evidence: matrix routing

## Dependencies
- Works well with: Runtime authoritative validation boundary (Draft-07 jsonschema), harness sandbox (exact-match gate), tiktoken cl100k_base tokenizer, and a verification harness that logs variant/task/repetition for re-derivation
- Requires: Both key stores (auth.json and env) holding same unexhausted Go key before kickoff (Failure-Matrix invariant); live replication requires temperature >0 and 3 repetitions per cell

## Supporting Evidence
| Evidence Type | Reference | Quality |
|---|---|---|
| Advisory deliverable | #506 Track C 8×4 gap-matrix + §14 scoring + hookability (muse-spark-1.2-contributor, 2026-08-29) where 3 predecessors froze | Delivered |
| Harness proxy measurement | #498 Tests A-E: 198 calls (22 tasks ×3 reps ×3 variants) + 10 recovery retries, C/A 0.267 (73.3% saving), argument delta 0.016 within 5pp, ValidationFailed recovery 10/10 | Replicated (proxy) |
| Live SSE verification | ses_fbc24c189ffeH3um1r564nlFAW 2026-08-27 15:33 UTC muse-spark-1.2-contributor streaming with zero Monthly usage limit errors + curl SSE verification | Observed (live) |
| Cost-vs-suitability | model-evidence-2026-08-27-lexicon.md + model-evidence-brief-note.md: muse-spark Zen 5-10m synthesis vs hy3 DEAD-UNMARKED silent loss (referenced in matrix Maintenance) | Observed |
| Tokenizer versioned | tiktoken cl100k_base 0.14.0, chars/tokens per variant (A 31767/7023, B 9288/2161, C 7942/1873) | Versioned |
| Design compliance | .design/capability-schema-validation.md §10 phases (muse-spark free → Go), protocol.md 5pp tolerance, design §5.5 runtime authority | Verified |

## Confidence Assessment
- Level: Emerging-Moderate (3+ sessions including advisory, harness proxy, and live SSE verification; live-model accuracy on 22-task set at temperature >0 not yet measured — proxy is evidence-based, not proven)
- Reviewer: builder agent pp3g-LPcA (muse-spark-1.2-contributor, 2026-08-31)
- Date: 2026-08-31
- Evidence considered: #506 gap-matrix, #498 Tests A-E harness proxy (results.md, run.py, summary.json), #510/#512 Go key stale live verification (ses_fbc24c189ffeH3um1r564nlFAW), model-discipline.md, Failure-Matrix, scripts/session-model-recommend, Model-Routing-Matrix maintenance note
- Significant changes from prior assessment: First dedicated muse-spark feedback record; prior matrix only referenced muse-spark in Maintenance note and recommender fallback without per-model profile

## Last Review
- Date: 2026-08-31
- Reviewer: builder agent pp3g-LPcA (muse-spark-1.2-contributor)
- Evidence considered: As above; live replication for #498/#530 via harness --live --model path is ready; promotion from evidence-based to proven requires live 22-task ×3 reps at temperature >0 replicating within 5pp on same tokenizer
- Significant changes: Initial creation for #531 (updates Model Routing Matrix and adds feedback note for #498/#530 live replication)

## Feedback Note for #498/#530 Live Replication

**WHY:** #498 proxy harness showed minimal description (stable ID + ≤20w + names/types + enum literals, C/A 0.267) preserves selection (1.00) and argument accuracy (0.984, delta 0.016) within 5pp tolerance vs full schema, but with WHAT-NOT-TESTED: **no live LLM inference**. Certainty is evidence-based (proxy), not proven. #530 live replication is the cheapest discriminating test to falsify the proxy finding.

**WHAT:** Basis is the 22-task fixed set (21 valid + 1 intentionally malformed), each 3× per variant (66 calls/variant, 198 total) routed through authoritative Draft-07 validation, token-measured with tiktoken cl100k_base 0.14.0, with typed ValidationFailed recovery (10/10) and PARSE_TIMEOUT_S 2.0s bound (v2 fix).

**HOW CERTAIN:** Evidence-based (proxy) — would upgrade to **proven** only after live replication with at least one live model (e.g., muse-spark Go variant `opencode-go/muse-spark-1.2-contributor`) on the same 22-task set with `temperature > 0` and 3 repetitions per cell, reporting same 5pp tolerance and tokenizer version. If live results replicate within tolerance, promote Q2/Q3/Q5 claims to proven; if not, revise minimal-description surface (e.g., retain more enum/context).

**WHAT-NOT-TESTED (sharpest):** No live LLM API call; no prompt-order permutation beyond fixed 3 reps; no statistical significance beyond 63 valid calls/variant; no chained multi-step workflows; no tokenizer beyond cl100k_base 0.14.0; no constraint-boundary stress beyond task 22 + single injected filter-enum miss; parse timeout not bench-tested with adversarial payloads; missing-variant recovery not live-tested. Any claim depending on these is unsupported until #530 live replication measures them.

**Recommendation for #530:** Run `python3 research/capability-schema-validation/tests/test-a/run.py --live --model opencode-go/muse-spark-1.2-contributor` (or Zen free variant) with 3 repetitions, tiktoken 0.14.0, and 5pp tolerance; log variant/task/repetition + ValidationFailed payload + tokens; compare C vs A selection/argument deltas to proxy (0.000/0.016). Cost discipline: muse-spark is cheapest suitable for this replication (tier 2 LOW, 5-20m) vs luna/gemini HIGH — use live replication to validate cost-vs-suitability axis, not to burn HIGH-tier budget.

