---
title: Private connector review feedback 2026-11-28
program: EDASES
layer: Research
document_type: Research Record
status: Experimental
authority: Derived
canonical_repository: edases
last_updated: 2026-11-28
---

# Bounded private connector source review — 2026-11-28

Privacy-safe model capability intake from a private owner repository. Exact source, full report, prompt, run and qualification receipts retained in the authorized private project; operational locator WNASES-20. No private code, credentials or account meter values reproduced here.

Same source-pinned 77,698-byte packet (Worker and two discovery test files), OpenCode CLI 2.4.2, protected GitLab runner, authenticated free Go routes with zero price and privacy flags verified, one inference request per model, default reasoning setting, 32,768 completion cap and 240s deadline, no retry/fallback. Wire preflight passed. Prior separate 8,192-cap admission review returned no visible answer for both models; task and input differ, so this is not a controlled comparison or proof of causal cap effect.

| Route | Observed result | Interpretation limits |
| --- | --- | --- |
| opencode-go/hy4-flash-free | Completed 110.788s; 21,227 prompt / 21,302 completion / 20,665 provider-reported reasoning tokens; 2,680 UTF-8 visible report bytes, hash verified, explicit no-material-findings verdict and four lower-impact robustness observations; provider reported zero cost. | Source review only; no execution, no proof of absence of defects; findings require coordinator triage. Actual model family/version beyond selected route and invoice cost not independently established. |
| opencode-go/hungerg-free | Watchdog at 240.134s, CLI 143, one admitted request, HTTP 200 SSE, 60,345 observed reasoning characters (60,646 decoded event-feed characters), zero visible answer, no terminal stop/done, no orphan. | Incomplete; no review verdict. Streaming interim zero usage fields are not terminal token accounting. Provider settlement and cost unknown; no automatic retry. |

This record does not rank models or establish that larger caps are universally optimal. Both exact permits closed after terminal receipts. Hy4 completion versus HungerG timeout is a workload/configuration observation, not a controlled ranking or proof of intrinsic model quality. No further inference authorized.
