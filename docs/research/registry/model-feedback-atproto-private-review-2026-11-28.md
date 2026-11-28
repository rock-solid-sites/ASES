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

## Beam Free follow-up — same pinned packet, 2026-11-28

`opencode-go/beam-free`, OpenCode 2.4.2, low reasoning, identical 77,698-byte packet, 32,768 cap, 240s, one request. Authenticated zero input/output/cache pricing, training=false, ZDR=false. Completed 14.159s; 20,763 prompt / 1,436 completion / 1,427 reasoning tokens provider-reported, $0 provider-reported. Visible report exactly 21 bytes: "NO MATERIAL FINDINGS." Normal terminal stop/done, no transport failure. Original prompt expressly allowed this verdict; this is **not** evidence of disobedience. Source-specific rationale absent, so coordinator does not count it toward operator's two-substantive-review minimum. Raw receipt retained in private project; WNASES-20. No conclusion about depth of actual internal analysis or model quality from a terse answer. Next authorized model is paid MiMo 2.6 Flash within verified Go subscription allowance, with an explicit requirement for source-specific justification even if no findings.

## MiMo V2.6 Flash follow-up — 2026-11-28

`opencode-go/mimo-v2.6-flash`, OpenCode 2.4.2, default native reasoning, same pinned source/tests with explicit source-specific rationale requirement (77,983-byte packet). Authenticated Go subscription catalog and headroom gate passed, expected $0.14/$0.28 per million input/output tokens, $60 model-equivalent monthly allowance, training=false/ZDR=true. One request, 32,768 completion cap, 240s watchdog, $0 separate cash authorized, no retry/fallback. HTTP 200 SSE; 33,581 wire reasoning chars / 33,823 decoded event-feed chars, zero visible report, no stop/done or terminal usage, watchdog at 240.154s, CLI 143, no orphan. No substantive verdict; actual allowance consumption and cash settlement unknown (no terminal usage fields), not assumed zero. Exact permit closed; raw receipt in authorized private project, WNASES-20. This is an observed route/configuration outcome, not proof of model incapability. Compared with Beam, report requirements and reasoning mode also differ. No additional invocation authorized.

## Operator-authorized fresh-session retries — 2026-11-28 06:20 UTC

Operator reports intermittent provider streaming failures and authorizes bounded fresh-session retries; root cause of each prior timeout remains unproven. Beam retry used the same pinned source/test data with strengthened source-specific rationale requirement. Exact `opencode-go/beam-free`, OpenCode 2.4.2, low reasoning, one request, 32,768 cap, 240s, zero-price catalog and dry qualification, training=false/ZDR=false. Completed 26.069s, HTTP 200 SSE stop/done, 20,807 prompt / 2,206 completion / 1,647 reasoning tokens, 2,377 UTF-8 report bytes, SHA-256 verified, $0 provider-reported cost. No material findings with three source-specific checks; coordinator verified predicates, with minor imprecision in media test attribution (existing legacy suite, not new finite-domain tests). Accepted second substantive review, not proof of defect absence. Different prompt means not a controlled comparison with first Beam response. HungerG retry canceled before inference; revoked permit returned OP01_PERMIT=BLOCKED_KeyError. No MiMo retry necessary. Both permits closed. Private receipts at WNASES-20.
