---
title: "Session Handoff 2026-08-15 — Tools distribution architecture (EPIC #382)"
tags: ["design-doc"]
sources: []
contributors: ["OL2r"]
created: 2026-08-15
updated: 2026-08-15
---


## Design Specification

### done (session #27)

- **EPIC #382 created** — Tools distribution architecture: Phase-1 (decide+test, DONE), Phase-0 (implementation, PENDING), Phase-2 (toolkit bootstrap, carried from #164).
- **7 operator decisions (#354)** recorded; ontology #353 kept open.
- **Two review rounds** (#361/#365 plans) + **synthesis of 7 one-shot reviews** (ChatGPT, DeepSeek, Claude Sonnet, Gemini, GLM-5.2, Kimi, Qwen) -> docs/research/Tools Distribution Architecture Synthesis.md.
- **Decision Test Framework** (docs/research/Tools Distribution Architecture Decision Test Framework.md) + **4 amendments**: A1 (D1 forward-only, D5 prospective, scaffolding framing), A2 (D7 surviving-mechanism, Phase-0 fix verifications), A3 (D6 decision: Policy A + B-watchdog), A4 (provider visibility policy).
- **Empirical tests**: D2 symlink-loading PASS, D3 user-level loading PASS, gap-9 init-does-NOT-deploy-guard-plugins, D6 A/B whitelist PASS (Policy A wins; fork binary caps visible set).
- **Model-Routing-Matrix** updated with session #27 evidence (#374, merged) — nemotron 2/2 Nvidia-502 failures recorded; glm-5.2/qwen3.7-plus rows added.
- **Close-out**: 24 thread issues closed (#358-#381), #164 superseded, evidence file committed (e65ada78), all worktrees cleaned.

### open (next session)

- **#382 EPIC (the single forward item)** — Phase-0 implementation: (1) plugin.ts/dynamic-models.ts consolidation + D6 Policy-A mechanism + B-watchdog + provider manifest (Amendment 4); (2) hook-config precedence fix (#9 class: by_type gated must beat global blocked) + schema-level blocked∩gated overlap rejection; (3) models-cache regeneration; (4) one-time reverse-sync seed (live/ASES newest -> Tools canonical); (5) D7 surviving push mechanism (tools link/install/doctor/promote); (6) run remaining gates: D1-forward flow verification, D4 drift window, Phase-0 fix verifications (2.1-2.3).
- **#354** kept open (decisions record), **#353** kept open (ontology record).

### gotchas (this session's lessons)

- Kickoff worktrees for read-only reviewers leave unmerged branches if content only lives in shared worktree state — verify every claimed commit is on main before close-out (caught #374 unmerged + #383 untracked evidence file).
- `--no-changelog` on bulk issue close avoids changelog noise.
- Free-tier Nemotron: 2/2 Nvidia-502 failures — do NOT use for deadline-critical reviews (recorded in matrix).
- D1 historical audit confounded (Tools dormant ~month); forward-only measurement required.

### reference map

- EPIC #382 (forward work); #354 (decisions); #353 (ontology); #164 (superseded)
- docs/research/Tools Distribution Architecture Synthesis.md (converged architecture)
- docs/research/Tools Distribution Architecture Decision Test Framework.md (+ 4 amendments)
- docs/research/tools-distribution-architecture-review-input.md + Tools Distribution Architecture Reviews.md (evidence)
- docs/research/registry/Model-Routing-Matrix.md (+ model-feedback-*.md, session #27 evidence)

