---
title: "Model Routing Matrix"
tags: ["models", "routing", "opencode", "capability", "session-evidence"]
sources:
  - url: "https://github.com/edases/ASES/issues/190"
    title: ""
    accessed_at: "2026-08-06"
contributors: ["pp3g-H4ni-write-the-comprehensive-model-capability-registry-6974", "OL2r"]
created: 2026-08-06
updated: 2026-08-10
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
| Review Style / Lens | Evidence-first investigator: controlled repro, file:line citations, verification tables (#144/#145) |
| Strengths by task-type | Deep source/mechanism investigation (#144), binary/byte-level engineering (#145), fork/plugin implementation with verification (#138/#173), research/web tasks (operator rule #147), documentation (#140) |
| Blind spots | None observed while working; the failure is availability not cognition |
| Failure modes | SILENT PROVIDER HANG: non-SSE body bypasses chunkTimeout -> last stream never returns, zero ERROR, flags lie RUNNING, 10h+ stall (#138 10.5h, #142 10.9h; root cause #144) |
| Token cost profile | LOW (preferred for research/web per operator #147) |
| Confidence + evidence | Moderate; 6 sessions, 2 hangs. Evidence: #138/#142/#144/#145/#173/#147 |

### opencode-go/gpt-5.6-luna (paid)
| Dimension | Value |
|---|---|
| Review Style / Lens | SYSTEMS/DURABILITY: lifecycle safety, state-machine invariants, leases, idempotency, races; conditional verdicts with named preconditions (#136/#150) |
| Strengths by task-type | Adversarial review of safety/state-machine designs (#136), fragile-patch code review (#150), design re-review rounds (#177), final audit/sign-off |
| Blind spots | Leaves ship/no-ship to operator (conditional verdicts); overkill for cheap research |
| Failure modes | None observed (not stress-tested for hang class) |
| Token cost profile | HIGHER — operator reserves for high-value work (#147) |
| Confidence + evidence | Moderate; 3 sessions, 0 failures. Evidence: #136/#150/#177/#147 |

### opencode/big-pickle (Zen free)
| Dimension | Value |
|---|---|
| Review Style / Lens | BREADTH + ADVERSARIAL + LIVE-SYSTEM: verifies claims against running system; systemic/race/security thinking (#130/#137) |
| Strengths by task-type | Deep adversarial review with live verification (#137 -> found #138 bug), permission/policy review with exact scoping (#130), design review rounds (#178/#184), root-cause hunting |
| Blind spots | Scope containment: drifts into adjacent/forbidden territory when task is open-ended (#149) |
| Failure modes | SCOPE DRIFT into security-sensitive territory (fork internals + identity-override exploration), agent killed (#149) |
| Token cost profile | HIGH for a free model (very long verdicts) but free tier = zero cash |
| Confidence + evidence | Moderate-High; 5 sessions, 1 aborted. Evidence: #130/#137/#149/#178/#184 |

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
| Strengths by task-type | RELIABLE BACKUP reviewer (completed where laguna hung, #132), fast breadth review, free-tier tasks needing high completion probability |
| Blind spots | Security precision: recommended find/awk/sed/less/curl -I (all rejected in final spec #127) |
| Failure modes | None observed (1/1) |
| Token cost profile | LOW (fast, free) |
| Confidence + evidence | Emerging-Moderate; single session. Evidence: #132/#127 |

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
| Review Style / Lens | STRUCTURED PASS-VERDICT RE-REVIEWER: findings-by-finding verification with section citations (#183) |
| Strengths by task-type | Design re-review PASS/CONDITIONAL gates (#183), fast second opinion, structured verification tables |
| Blind spots | Verification depth SHALLOWER than hy3: PASSed a design hy3 found 5 compile-level blockers in (V1-V5) — #183 vs #182 divergence |
| Failure modes | Verification-depth false-negative (missed compile-level defects), not a system failure |
| Token cost profile | LOW-Moderate (free variant observed) |
| Confidence + evidence | Emerging (single session). Evidence: #183 + #182 comparison |

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

---

## ROUTING TABLE — task/review-need -> recommended model + rationale

| Task / Review Need | Recommended Model | Rationale (one line) |
|---|---|---|
| Research / web investigation (cheap) | opencode-go/deepseek-v4-flash | Operator rule #147: preferred for research/web; cheap; deep investigation proven (#144) |
| Deep source/mechanism investigation + controlled repro | opencode-go/deepseek-v4-flash | Evidence-first method with verification tables (#144/#145) |
| Fork/plugin implementation with verification | opencode-go/deepseek-v4-flash | Proven Rust + TS implementation with tests (#138/#173) |
| Design review: safety/state-machine/durability | opencode-go/gpt-5.6-luna | Systems/durability lens with named preconditions (#136) |
| Fragile/emergency patch code review | opencode-go/gpt-5.6-luna | MUST-FIX/SHOULD-CONSIDER taxonomy + long-horizon risk (#150) |
| High-value adversarial review / audit | opencode-go/gpt-5.6-luna | Operator reservation for high-value work (#147) |
| Deep adversarial review with live-system verification | opencode/big-pickle | Breadth+adversarial, verified launch.rs live, found #138 bug (#137) |
| Permission/allowlist policy review | opencode/big-pickle (primary) | Exact prefix scoping + two-layer analysis (#130) |
| Design review rounds (r1: edge cases, source verification) | opencode-go/hy3 | Finds what others miss; re-derives from source (#176/#182) |
| Implementation-readiness gate on patch code | opencode-go/hy3 (primary) | Catches compile-level blockers (V1-V5, #182) |
| Fast independent review (minutes) | opencode/ling-3.0-flash-free | 3-min patch review (#151); category-structured (#128) |
| Cheap free-tier triage | opencode/ling-3.0-flash-free or opencode/nemotron-3-ultra-free | Fast, reliable, free (#128/#132) |
| Backup reviewer when primary hangs | opencode/nemotron-3-ultra-free | Completed where laguna hung; fastest allowlist verdict (#132) |
| Fast design re-review PASS/CONDITIONAL gate | opencode/mimo-v2.5-free | Structured findings-by-finding verification (#183) — pair with hy3 as primary |
| Final architectural audit / sign-off | google-vertex/gemini-3.1-pro-preview | Comprehensive 6-category audit; 0 findings (existing doc) — budget >=3 min |
| CI gate / implementation verification (fast) | cohere/north-mini-code-1-0 | ~30s, zero false positives (existing doc + project-completion-report) |
| Two-tier review pipeline (triage -> deep) | north-mini-code then gemini-3.1-pro | Fast triage then deep audit (existing doc pattern) |
| HIGH-RISK long unattended task (no watchdog) | AVOID free-tier + AVOID flash until #146 watcher lands | Silent-hang class (#129/#138/#142) unrecoverable without external kill |

---

## Routing principles distilled from evidence

1. **Match the lens to the review need**: durability-critical designs -> luna; edge-case/implementation-readiness -> hy3; breadth+live-system -> big-pickle; fast triage -> ling/north-mini-code; final audit -> gemini.
2. **Cost discipline**: research/web/cheap tasks -> flash (operator rule #147); high-value review/audit -> luna. Do not burn luna on cheap research.
3. **Reliability gates**: free-tier models (laguna esp.) and flash have a confirmed silent-hang failure class — do not use for deadline-critical or unattended tasks until the #146 watcher / #154 durable fix lands.
4. **Backup discipline**: always dispatch a backup reviewer for free-tier primary (#129 -> #132 pattern).
5. **Scope discipline**: big-pickle needs tight scope + checkpoints (#149 scope-drift lesson); re-scope or kill early on visible drift.
6. **Two-tier pipelines**: fast verifier (north-mini-code/ling) for triage + deep reviewer (gemini/luna/hy3) for audit — the proven adversarial-consensus pattern (project-completion-report §8).

## Session evidence 2026-08-06 (#192 fork fix verification)\n- Agent pp3g-AJtB ran on opencode-go/deepseek-v4-flash for the #192 live-kickoff verification (issue #210): completed cleanly, no hang, correct report, checkpoint comments posted. Positive data point against the documented SILENT-HANG failure mode for this model (no hang in this short 2m-guide session).\n



## Session evidence addendum — 2026-08-06 (#196 ToolRegistry lazy-MCP validation)

**Models exercised (all in their matrix-designated roles):**
- `opencode-go/deepseek-v4-flash` (builder, 3 dispatches #196/#204/#211): built the full 5-test evidence package, applied the 5 MUST FIX + 2 Also-Fix revision exactly, and executed the docstring+capture-script follow-up. Zero scope drift, all commits verified by independent re-review. Strengthens the evidence-first-implementation profile (#144/#145). Evidence: ebe07b3, b40c980, 88f9022.
- `opencode-go/hy3` (reviewer #199): 5 MUST FIX, all correct and each independently re-derived; reviewer noted "citation discipline of this quality is rare". Confirms the source-re-derivation lens (#153/#176/#182).
- `opencode/big-pickle` (reviewer #200 + re-review #205): original review PASS with 2 non-blocking SHOULD-CONSIDERs that were both later fixed; re-review PASS after confirming the new initialize-capture artifact byte-consistent with SDK wire model. Live re-run blocked by reviewer bash allowlist (see note below). Confirms breadth+live-system lens (#130/#137).
- `opencode-go/mimo-v2.5-pro` (reviewer #204 re-review): structural findings-by-findings re-review, PASS with every item re-derived from raw artifacts. Strong showing for a re-review gate; consistent with the #183 pattern (structured verification tables). New paid-variant observation: verification depth here was on par with hy3 on this doc-type task (differed from the #182-vs-#183 depth gap, which was a design/code-review context).

**Infrastructure finding worth propagating:** the reviewer-role bash allowlist (`.opencode/agents/reviewer.md`) denies `python ` even though hook-config allowed_bash_prefixes permits it — live re-verification by reviewers is therefore blocked by a config gap, not a deliverable defect (big-pickle #200/#205 logged interventions). If independent live re-runs are wanted from reviewers, grant `Bash(python *)` to the reviewer map or route live re-runs to builder-role agents.

# Session evidence addendum — 2026-08-08 (session #19: workflow-topology design delivery + reliability closeout)

**Models exercised (role-designated use):**
- `opencode-go/deepseek-v4-flash` (builder, multi-dispatch, session-approved): produced the full workflow-topology operationalization across AGENTS.md / docs/ORCHESTRATOR.md / SESSION-START.md / playbook (#258), applied the auditor-semantics correction exactly (#259, c13c381f), produced the verbatim conversation addendum extraction from opencode.db (#261, bacaffa0, 1636 lines / 129 messages), and corrected the tripn-astro mirror staging pre-commit (#260). Zero scope drift, all merges verified on main. Strong additional positive evidence for the evidence-first profile (#144/#145/#196) with NO silent-hang occurrence across the whole session — noteworthy because this model is on the hang-class watchlist; the #154 durable-fork install would remove the residual risk.
- `opencode-go/hy3` (reviewer #248): produced a long multi-part verdict that hit the streaming idle limit (504) — the stream cut mid-verdict. WORKAROUND PROVEN: chunked posting (4-part verdict landed, all parts preserved on hub). NEW OPERATIONAL DATA POINT for the hy3 profile: long verdicts (> streaming idle budget) will 504 mid-stream; chunk the review output into N parts before posting. Cost profile implication: the deep source-verification lens is token-heavy AND now known to exceed streaming limits on the longest outputs — plan chunking at dispatch time for hy3 review tasks.
- **Discipline reinforcement (not a model-capability data point but routing-relevant):** operator rule confirmed — Grok/xAI products are NEVER to be used for any role (#249 violation corrected mid-session). Model catalog verification via `opencode models <provider>` is mandatory before every launch (no stale-doc model IDs).


# Session evidence addendum — 2026-08-08 (session #20: hydration epic #157 closeout)

**Models exercised (role-designated use, two-phase Auditor model per Workflow Topology §5.3):**
- `opencode/big-pickle` (Phase-1 in-flight divergence verifier, #125 r3, pp3g-cXmI): NEW ROLE VALIDATED. Pre-positioned alongside the Builder, it monitored the structured-position stream and fired 4 triggers: caught 2 real silent-hang stalls (neHg zero-positions; re-affirmed staleness), corrected an ORCHESTRATOR attribution error (nudged the wrong agent's timeline — hub events.log ground truth), and correctly did NOT escalate a cadence-breach that was a legitimate long test build. Zero artifact divergence missed in the committed state. This is strong evidence for big-pickle as the divergence-verifier lens (breadth + live evidence joins; cf. #130/#137) — with the same scope-discipline caveat as before (#149): the monitor mandate must stay narrow (position-vs-artifact join only).
- `opencode-go/gpt-5.6-luna` (Phase-2 post-hoc auditor, #125 r3, pp3g-ndGC): NEW ROLE VALIDATED. Delivered the outcome-vs-process split exactly per design: OUTCOME APPROVE (independent git audit of a87bd513 vs r2 boundary, file:line citations), PROCESS CONDITIONAL (MEDIUM: 3 builder silent-hangs — systemic reliability; LOW: claim-field discipline, tree qualification, warning-test depth). Confirms the systems/durability lens (#136/#150) transfers cleanly to the post-hoc final gate; conditional verdicts with named preconditions as documented.
- `opencode-go/deepseek-v4-flash` (builder, #125 r3 — 3 dispatches: neHg, R99p, SzyI + earlier T1jj): SYSTEMIC HANG PATTERN CONFIRMED — 3 silent-hangs in one task lifecycle (T1jj died post-plan, neHg died zero-positions, R99p silent-hung post-commit). All caught by positions + divergence verifier with zero artifact loss, but recurrence confirms the hang class is systemic for unattended flash tasks (already on watchlist; #154/#146). Positive counterpoints: when it completes, output quality is high (r2 boundary 5ada263a + r3 8a87bd513 fully verified; SzyI's verification tail exemplary — per-item evidence, WHAT-NOT-TESTED, certainty). OOM caveat: long bin-suite builds need CARGO_BUILD_JOBS=1 (machine constraint, not model).
- `cohere/north-mini-code-1-0` + `opencode/north-mini-code-free` (fast triage reviewer, #125 r1 review): TWO silent-stall data points (fs00 Cohere, EnMl Zen — no output, zero comments, killed). Consistent with the known silent-hang class for this model profile; triage role remains useful ONLY with tight timeout + fallback.
- `opencode-go/hy3` (adversarial reviewer, #125 r1, pp3g-KHMD): mutation-matrix review caught the r1 gate's non-discriminating tests (test b positive-by-construction, test c lenient-passing) — the finding that triggered the r2 revision. Confirms the source-re-derivation lens (#153/#176/#182); final-verdict post stalled but findings were preserved in VERIFY checkpoints (chunking lesson from #248 applies).

**Workflow-topology validation (not model-specific but routing-relevant):** the two-phase Auditor model (Phase 1 in-flight big-pickle + Phase 2 post-hoc luna) worked end-to-end on #125 r3: 3 stalls caught with zero artifact loss, orchestrator attribution error corrected, process-reliability evidence fed to #154/#146. Recommendation: keep positions + ~10min heartbeat cadence + pre-positioned verification for long unattended builds until #154 durable-fork lands.

## Session Evidence — 2026-08-08 (tripn-astro: CI 3-model review + PSI epic + in-flight auditing)

### opencode-go/deepseek-v4-pro (NEW row)
| Dimension | Value |
|---|---|
| Review Style / Lens | PROCESS+ARCHITECTURAL AUDITOR: catches systemic/process issues and incidental production bugs; structured verdicts with evidence tables (#410, #429) |
| Strengths by task-type | Post-hoc Phase-2 audits (STRONG verdict on PSI epic), pipeline design review (NOT-SUFFICIENT with exact minimum lists: node-version-file, npm ci, concurrency, notifications — #410), cross-repo review |
| Blind spots | Reads code cold — flagged an INTENTIONAL operator decision (OG insta mirror, data-property=landing) as a HIGH bug and proposed an invalid slug ('original' vs 'og'); needs decision-context before acting |
| Failure modes | None observed (2 sessions, 0 failures) |
| Token cost profile | Moderate-High (paid) |
| Confidence + evidence | Emerging-Moderate; 2 sessions. Evidence: #410/#429 (tripn-astro) |

### opencode-go/mimo-v2.5-pro (NEW row — PRO variant of mimo-v2.5)
| Dimension | Value |
|---|---|
| Review Style / Lens | STRUCTURED EVIDENCE-VERIFIER: independently re-verifies every claimed artifact (diff stat exact match, greps, dist checks) before passing (#425); balanced verdicts |
| Strengths by task-type | Pre-consumption review gates (APPROVE-WITH-NITS, claims-not-inferred evidence tables — #425), Phase-2 audits (ship-ready verdict, caught OG/PB missing preloads — #430), CI design review (NOT-SUFFICIENT, precise minimums — #408) |
| Blind spots | None material observed; occasionally flags LOWs a maintainer might skip |
| Failure modes | None observed (3 sessions, 0 failures) |
| Token cost profile | Moderate (paid) |
| Confidence + evidence | Emerging-Moderate; 3 sessions. Evidence: #408/#425/#430 (tripn-astro) |

### google-vertex/gemini-3.5-flash (NEW row — current flash line; see 3.1-pro row above)
| Dimension | Value |
|---|---|
| Review Style / Lens | ADVERSARIAL BREADTH: enumerates findings incl. config/cleanup items others miss (#409: obsolete workflows) |
| Strengths by task-type | CI/pipeline design review (NOT-SUFFICIENT with 4 minimum changes — #409), breadth passes |
| Blind spots | Context-sensitivity: recommended a root 'sharp' install that contradicted the recorded design decision (declined) — misread intentional architecture as a gap |
| Failure modes | None observed (1 session) |
| Token cost profile | Moderate (paid Vertex) |
| Confidence + evidence | Emerging; 1 session. Evidence: #409 (tripn-astro) |

### opencode/big-pickle — session update
Pre-positioned Phase-1 in-flight divergence auditor (x2): caught the orchestrator-guard write-block divergence mid-flight and verified every builder position against artifacts; the pre-positioned model (launched alongside the builder, acts on trigger, model-varied from builder) proved high value. Evidence: #421/#427 (tripn-astro). Blind spot noted: can over-flag (secondary 'collateral-reversion' watch needed verification).

### opencode-go/deepseek-v4-flash — session update
Reliable implementation agent through chaos (all in-session + kickoff edits this session); NOTE: slow session startup (~6 min) and one empty Task-tool return (API flakiness, environment not cognition). Evidence: tripn-astro session 2026-08-08.

### ROUTING additions
| Task / Review Need | Recommended Model | Rationale |
|---|---|---|
| CI/pipeline design review (multi-model) | trio: deepseek-v4-pro + mimo-v2.5-pro + gemini-3.5-flash | 3-model adversarial review (2026-08-08) produced convergent NOT-SUFFICIENT verdicts + complementary findings |
| Pre-consumption review gate | opencode-go/mimo-v2.5-pro | Independent claims-not-inferred verification (#425) |
| Phase-2 post-hoc audit | opencode-go/deepseek-v4-pro or opencode-go/mimo-v2.5-pro | Process+architectural lens (STRONG / ship-ready verdicts — #429/#430) |
| In-flight divergence monitor (Phase 1) | opencode/big-pickle (different model than builder) | Pre-positioned auditor caught real divergence (#421/#427)

Session evidence addendum 2026-08-10 (session #341 doc-restructure, Phase-1 pre-positioned auditor): opencode/big-pickle (Phase-1 in-flight divergence verifier, #343, pp3g-lT7u) STRONG showing — cadence flag at 10-min staleness correctly refined to durability-risk-not-stall via worktree forensics; self-corrected its own stale position (claimed 0 commits 21s after builder committed); independently verified all 5 plan steps by direct file reads; caught builder AC4 overclaim (3 broken path refs the builder's no-stale-refs claim missed, root-caused to sweep ordering); flag-only discipline throughout. Verdict CONDITIONAL PASS, finding remediated. opencode-go/deepseek-v4-flash (builder #341) 9 incremental commits, healthy cadence after one 14-min gap, claim-discipline weak spot (no-stale-refs overreach). opencode-go/hy3 (plan reviewer #341, 2 passes) v1 caught inverted classification + unsatisfiable AC; v2 confirmed R1-R6 discharged. Workflow-topology validation: Phase-1 auditor held end-to-end — 1 cadence flag, 1 claim-mismatch flag, 1 self-correction, zero false escalations, zero artifact loss.
