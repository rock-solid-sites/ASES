---
title: Model Routing Matrix
program: EDASES
layer: Research
document_type: Registry
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - AI Capability Registry Specification

consumed_by:
  - SESSION-START.md
  - docs/SESSION-END.md

related_documents:
  - Model Feedback (per-model registry entries)

supersedes: []
last_updated: 2026-08-15
---

# Model Routing Matrix — DIMENSIONED

**Date:** 2026-08-06
**Source:** evidence-gathering draft #190 — sessions documented in issues #128-#153, #173, #144/#145/#154 design rounds, existing model-feedback docs, docs/project-completion-report-crosslink-model-agnostic.md, model-discipline.md.
**Convention:** rows = models; columns = routing dimensions. This matrix captures QUALITATIVE differences (review style/lens, strengths, blind spots, failure modes, cost) for routing decisions. Evidence refs per cell.

---

## Per-Model Profiles

### opencode-go/deepseek-v4-flash (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | Evidence-first investigator: controlled repro, file:line citations, verification tables (#144/#145); zero-context planning grounded in on-disk verification (#361/#365) |
| Strengths by task-type | Deep source/mechanism investigation (#144), binary/byte-level engineering (#145), fork/plugin implementation with verification (#138/#173), research/web tasks (operator rule #147), documentation (#140), zero-context planning/remediation-planning (#361 B1-B6 plan, #365 C1-C4 revision), large-document synthesis (#373 865-line synthesis of 7 one-shot reviews) |
| Blind spots | None observed while working; the failure is availability not cognition |
| Failure modes | SILENT PROVIDER HANG: non-SSE body bypasses chunkTimeout -> last stream never returns, zero ERROR, flags lie RUNNING, 10h+ stall (#138 10.5h, #142 10.9h; root cause #144) |
| Token cost profile | LOW (preferred for research/web per operator #147) |
| Confidence + evidence | Moderate-High; 9 sessions, 2 hangs. Evidence: #138/#142/#144/#145/#173/#361/#365/#373/#147 |

### opencode-go/gpt-5.6-luna (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | SYSTEMS/DURABILITY: lifecycle safety, state-machine invariants, leases, idempotency, races; conditional verdicts with named preconditions (#136/#150); concise MUST-FIX/SHOULD-CONSIDER/NITS taxonomy on plan reviews (#358) |
| Strengths by task-type | Adversarial review of safety/state-machine designs (#136), fragile-patch code review (#150), design re-review rounds (#177), final audit/sign-off, plan adversarial review rounds (#358/#362), open-ended architectural review with decisive cost/benefit-aware proposal (#368: versioned distribution source, Option B) |
| Blind spots | Leaves ship/no-ship to operator (conditional verdicts); overkill for cheap research |
| Failure modes | None observed (not stress-tested for hang class) |
| Token cost profile | HIGHER — operator reserves for high-value work (#147) |
| Confidence + evidence | Moderate-High; 6 sessions, 0 failures. Evidence: #136/#150/#177/#358/#362/#368/#147 |

### opencode/big-pickle (Zen free)
| Dimension | Value |
|---|---|
| Review Style / Lens | BREADTH + ADVERSARIAL + LIVE-SYSTEM: verifies claims against running system; systemic/race/security thinking (#130/#137); independently RE-VERIFIES every drift claim before reviewing (#359); source-level adversarial reading (#363) |
| Strengths by task-type | Deep adversarial review with live verification (#137 -> found #138 bug; #359 re-verified every drift claim; #363 M1 found the CRITICAL init-mechanics bug in fork source that broke plan step-5 — the single most valuable catch of the whole wave), permission/policy review with exact scoping (#130), design review rounds (#178/#184), root-cause hunting, self-recheck APPROVED with 3 SHOULD-CONSIDER (#366), open-ended architecture with three-class artifact locus Option D — most concrete proposal (#371) |
| Blind spots | Scope containment: drifts into adjacent/forbidden territory when task is open-ended (#149) |
| Failure modes | SCOPE DRIFT into security-sensitive territory (fork internals + identity-override exploration), agent killed (#149) |
| Token cost profile | HIGH for a free model (very long verdicts) but free tier = zero cash |
| Confidence + evidence | High; 9 sessions, 1 aborted. Evidence: #130/#137/#149/#178/#184/#359/#363/#366/#371 |

### opencode/ling-3.0-flash-free (Zen free)
| Dimension | Value |
|---|---|
| Review Style / Lens | FAST CONVERGENT: quick structured verdicts, category-driven, conservative on mutation risk (#128/#151) |
| Strengths by task-type | Fast independent reviews (3-min patch review #151), permission/policy allowlist review (#128), cheap triage on free tier |
| Blind spots | Terse — thin verdict detail (#151), not for deep edge-case hunting (#151 vs #150 depth) |
| Failure modes | #131 empty verdict (issue closed with no comments) — minor reliability blip, not classified hang |
| Token cost profile | LOW (terse, fast, free tier) |
| Confidence + evidence | Moderate; 2 completed sessions + 1 empty. Evidence: #128/#151/#131 |

### opencode/laguna-s-2.1-free (Zen free)
| Dimension | Value |
|---|---|
| Review Style / Lens | CAREFUL-WHEN-WORKING: precise severity-rated reviews (#152) — but availability is the binding constraint |
| Strengths by task-type | Structured focus-question reviews (#152), severity-rated edge-case analysis |
| Blind spots | None cognitive; availability dominates |
| Failure modes | SILENT PROVIDER HANG (not rate limit): outgoing stream never returns, zero ERROR, went undetected until log check (#129); historical rate limits July 23-26 (#140) |
| Token cost profile | LOW (free tier) but dispatch-slot waste when hung |
| Confidence + evidence | Moderate; 2 sessions (1 hang, 1 success) + historical. Evidence: #129/#152/#140 |

### opencode/nemotron-3-ultra-free (Zen free)
| Dimension | Value |
|---|---|
| Review Style / Lens | BROAD-CATEGORY, LESS CONSERVATIVE: enumerated 8 tool categories including mutation-capable tools others rejected (#132) |
| Strengths by task-type | Fast breadth review; free-tier tasks needing high completion probability (was RELIABLE BACKUP reviewer when primary hung #129 -> #132, but see failure modes) |
| Blind spots | Security precision: recommended find/awk/sed/less/curl -I (all rejected in final spec #127) |
| Failure modes | **2/2 FAILURES on 2026-08-14** — 'Streaming response failed: [502] Upstream error from Nvidia: Internal server error' (free-tier Nvidia endpoint unavailable; agents pp3g-Iwzk + pp3g-klf4, no verdict delivered, #360). Do NOT use free-tier Nemotron for deadline-critical reviews. |
| Token cost profile | LOW (fast, free) |
| Confidence + evidence | Downgraded: Emerging-Moderate on 1/1 success (#132), but 2/2 free-tier failures (#360) make it unreliable for deadline-critical work. Evidence: #132/#127/#360 |

### opencode-go/hy3 (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | NOVEL EDGE-CASES + SOURCE RE-DERIVATION: finds failure modes others miss; does not trust change-logs, re-verifies from source (#153/#176/#182) |
| Strengths by task-type | Edge-case hunting in designs/patches (#153 F2/F4, #176 B2, #182 V1-V5), source-level verification of design claims (#182 ~20 citations), parallel implementation (existing doc), design-review r1 role (#154 rounds) |
| Blind spots | Findings sometimes implementation-level rather than architectural (V1-V5 are patch-code issues) — may frustrate design authors |
| Failure modes | Syntax error in container.rs refactor (existing doc, recovered); none in review sessions |
| Token cost profile | Moderate (paid tier; deep source verification is token-heavy) |
| Confidence + evidence | High; implementation doc + 3 review sessions. Evidence: existing doc + #153/#176/#182 |

### opencode/mimo-v2.5-free (Zen) / opencode-go/mimo-v2.5 (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | STRUCTURED PASS-VERDICT RE-REVIEWER: findings-by-finding verification with section citations (#183); concrete-design-proposal strength (#364) |
| Strengths by task-type | Design re-review PASS/CONDITIONAL gates (#183), fast second opinion, structured verification tables, remediation review with concrete design proposals (#364: proposed the 3-state enforcement state machine + git-only atomicity for B3/B5 blockers) |
| Blind spots | Verification depth SHALLOWER than hy3: PASSed a design hy3 found 5 compile-level blockers in (V1-V5) — #183 vs #182 divergence |
| Failure modes | Verification-depth false-negative (missed compile-level defects), not a system failure |
| Token cost profile | LOW-Moderate (free variant observed) |
| Confidence + evidence | Emerging (2 sessions). Evidence: #183/#364 + #182 comparison |

### google-vertex/gemini-3.1-pro-preview (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | COMPREHENSIVE ARCHITECTURAL AUDITOR: deep code inspection, 6-category check, severity/evidence matrix (existing doc + project-completion-report) |
| Strengths by task-type | Final architectural audit/sign-off, deep security/correctness inspection, cross-cutting verification |
| Blind spots | Verbose; minor nits not always flagged separately |
| Failure modes | TIMEOUT on 2 of 2 audit attempts (2-min and 3-min limits) — needs >=3 min budget |
| Token cost profile | HIGH (comprehensive audit, paid Vertex) |
| Confidence + evidence | High; 2 independent records (existing doc + project-completion-report). Evidence: both |

### cohere/north-mini-code-1-0 (Cohere)
| Dimension | Value |
|---|---|
| Review Style / Lens | EXTREMELY CONCISE VERIFIER: zero fluff, zero false positives, PASS/FAIL only (existing doc + project-completion-report) |
| Strengths by task-type | Implementation verification, regression detection, pattern compliance, fast triage/CI gates, adversarial-consensus partner |
| Blind spots | No design critique, no improvement suggestions, no complex system reasoning |
| Failure modes | None observed |
| Token cost profile | VERY LOW (fastest reviewer, ~30s) |
| Confidence + evidence | High; 2 independent records. Evidence: existing doc + project-completion-report |

### opencode-go/glm-5.2 (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | DECISIVE OPTION-A ARCHITECT: open-ended architectural verdict with comparison-table format, addresses feasibility head-on (#367) |
| Strengths by task-type | Open-ended architectural review (#367: proposed 'binary embedding' Option A — decisive comparison-table format, addressed feasibility of extending crosslink binary embedding to all tooling) |
| Blind spots | Single session — confidence limited; no security/policy review evidence yet |
| Failure modes | None observed (1/1) |
| Token cost profile | Paid tier (opencode-go) |
| Confidence + evidence | Emerging; single session. Evidence: #367 |

### opencode-go/qwen3.7-plus (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | DECISIVE VERDICT + STRONG COMPARISON TABLE: 'FUNDAMENTALLY FLAWED' verdict with comparison-to-proposed-fix table (#370) |
| Strengths by task-type | Open-ended architectural review (#370: 'FUNDAMENTALLY FLAWED' verdict on copy-out, binary-embedding Option A, strong comparison-to-proposed-fix table) |
| Blind spots | Single session — confidence limited; no security/policy review evidence yet |
| Failure modes | None observed (1/1) |
| Token cost profile | Paid tier (opencode-go) |
| Confidence + evidence | Emerging; single session. Evidence: #370 |

---

## ROUTING TABLE — task/review-need -> recommended model + rationale

| Task / Review Need | Recommended Model | Rationale (one line) |
|---|---|---|
| Research / web investigation (cheap) | opencode-go/deepseek-v4-flash | Operator rule #147: preferred for research/web; cheap; deep investigation proven (#144) |
| Deep source/mechanism investigation + controlled repro | opencode-go/deepseek-v4-flash | Evidence-first method with verification tables (#144/#145) |
| Fork/plugin implementation with verification | opencode-go/deepseek-v4-flash | Proven Rust + TS implementation with tests (#138/#173) |
| Design review: safety/state-machine/durability | opencode-go/gpt-5.6-luna | Systems/durability lens with named preconditions (#136/#362) |
| Fragile/emergency patch code review | opencode-go/gpt-5.6-luna | MUST-FIX/SHOULD-CONSIDER taxonomy + long-horizon risk (#150/#358) |
| High-value adversarial review / audit | opencode-go/gpt-5.6-luna | Operator reservation for high-value work (#147); plan + remediation rounds (#358/#362); open-ended architecture Option B (#368) |
| Deep adversarial review with live-system verification | opencode/big-pickle | Breadth+adversarial, verified launch.rs live, found #138 bug (#137); source-level catch of init-mechanics bug (#363); recheck APPROVED (#366) |
| Permission/allowlist policy review | opencode/big-pickle (primary) | Exact prefix scoping + two-layer analysis (#130) |
| Design review rounds (r1: edge cases, source verification) | opencode-go/hy3 | Finds what others miss; re-derives from source (#176/#182) |
| Implementation-readiness gate on patch code | opencode-go/hy3 (primary) | Catches compile-level blockers (V1-V5, #182) |
| Fast independent review (minutes) | opencode/ling-3.0-flash-free | 3-min patch review (#151); category-structured (#128) |
| Cheap free-tier triage | opencode/ling-3.0-flash-free | Fast, reliable, free (#128) — nemotron dropped: 2/2 free-tier failures (#360) |
| Backup reviewer when primary hangs | opencode-go/deepseek-v4-flash (paid fallback) or opencode-go/gpt-5.6-luna (high-value) | nemotron free-tier failed 2/2 (#360); use paid fallback (flash cheap, luna high-value) |
| Fast design re-review PASS/CONDITIONAL gate | opencode/mimo-v2.5-free | Structured findings-by-finding verification (#183/#364) — pair with hy3 as primary |
| Final architectural audit / sign-off | google-vertex/gemini-3.1-pro-preview | Comprehensive 6-category audit; 0 findings (existing doc) — budget >=3 min |
| Open-ended architectural review (reject/replace verdict) | opencode-go/glm-5.2 or opencode-go/qwen3.7-plus | Decisive Option-A verdicts with comparison tables (#367/#370); big-pickle for most concrete three-class Option D (#371) |
| Zero-context planning / plan remediation | opencode-go/deepseek-v4-flash | B1-B6 plan (#361) + C1-C4 revision (#365), grounded on disk |
| Large-document synthesis | opencode-go/deepseek-v4-flash | 865-line synthesis of 7 one-shot reviews (#373) |
| CI gate / implementation verification (fast) | cohere/north-mini-code-1-0 | ~30s, zero false positives (existing doc + project-completion-report) |
| Two-tier review pipeline (triage -> deep) | north-mini-code then gemini-3.1-pro | Fast triage then deep audit (existing doc pattern) |
| HIGH-RISK long unattended task (no watchdog) | AVOID free-tier + AVOID flash until #146 watcher lands | Silent-hang class (#129/#138/#142) unrecoverable without external kill |

---

## Cross-model convergence note (session #27, 2026-08-14/15)

Five independent dispatched reviewers (#367-#371: glm-5.2, luna, kimi-k2.7-code, qwen3.7-plus, big-pickle) **all independently rejected copy-out distribution** and converged near 'single source + three-class artifact locus' (Option D) — a strong convergence finding. Synthesis: `docs/research/Tools Distribution Architecture Synthesis.md` (#373).

---

## Routing principles distilled from evidence

0. **FORBIDDEN MODELS (#347): xAI / Grok is strictly and permanently
   forbidden.** xAI models (grok-4.5 and the grok family) must never be
   routed to any task. Violation precedent: #249 ('never use Grok/xAI').
   The models are patched out of the model catalog (user-level plugin
   `~/.config/opencode/plugins/plugin.ts`) — `opencode models` must not list
   them. **Kimi is NOT forbidden** — `opencode-go/kimi-k2.7-code` is usable
   (used on #317/#322; #369: open-ended architecture review — REJECT copy
   model, proposed reference-based symlink/submodule consumption; consistent
   with usable); only `kimi-k3` is extremely expensive (cost-based
   caution, not a ban). See `.crosslink/knowledge/model-discipline.md`.

1. **Match the lens to the review need**: durability-critical designs -> luna; edge-case/implementation-readiness -> hy3; breadth+live-system -> big-pickle; fast triage -> ling/north-mini-code; final audit -> gemini; open-ended architecture -> glm-5.2/qwen3.7-plus.
2. **Cost discipline**: research/web/cheap tasks -> flash (operator rule #147); high-value review/audit -> luna. Do not burn luna on cheap research.
3. **Reliability gates**: free-tier models (laguna esp., nemotron 2/2 on 2026-08-14 #360) and flash have a confirmed silent-hang/failure class — do not use for deadline-critical or unattended tasks until the #146 watcher / #154 durable fix lands. Free-tier Nemotron should NOT be used for deadline-critical reviews.
4. **Backup discipline**: always dispatch a backup reviewer for free-tier primary (#129 -> #132 pattern), but prefer a PAID fallback — nemotron (the original free-tier backup) failed 2/2 on 2026-08-14 (#360).
5. **Scope discipline**: big-pickle needs tight scope + checkpoints (#149 scope-drift lesson); re-scope or kill early on visible drift.
6. **Two-tier pipelines**: fast verifier (north-mini-code/ling) for triage + deep reviewer (gemini/luna/hy3) for audit — the proven adversarial-consensus pattern (project-completion-report §8).
