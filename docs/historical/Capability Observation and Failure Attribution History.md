---
title: Capability Observation and Failure Attribution History
version: 2026-11-24.2
program: ASES
layer: Research
document_type: Research Record
status: Historical
authority: Derived
canonical_repository: ases
last_updated: 2026-11-24
---

# Capability observation and failure attribution history

The August 2026 EDASES model profiles record particular tasks, provider routes, configurations, outcomes and contemporaneous interpretations. They are useful for generating hypotheses about assignment, review strengths and reliability, not for establishing current availability, authorization or intrinsic model capability. The original bodies and owner are preserved. The [Evaluation Framework](../research/frameworks/Evaluation%20Framework.md), [AI Evaluation Protocol](../research/protocols/AI%20Evaluation%20Protocol.md) and [AI Capability Registry Specification](../research/registry/AI%20Capability%20Registry%20Specification.md) remain separate research sources; upstream currency is unverified.

**Operator clarification (2026-11-24):** These profiles often summarize larger series of observations; their qualitative judgments remain useful cumulative evidence for matching model capabilities and tasks. The following qualifications address the limits of particular claims and causal attribution, not a replacement scoring of the original profiles or an instruction to disregard their broader evidence. A new failure can qualify a reliability estimate without negating previous demonstrated task capability. The Model Routing Matrix remains an active derived capability-tracking register with dated observations; it is neither a definitive selection guide nor dispatch authorization.

## Earlier observations and qualifications

- [big-pickle](../research/registry/model-feedback-big-pickle.md): Recorded review strengths and scope drift are task-specific; the startup stall does not establish the failed component.
- [deepseek-v4-flash](../research/registry/model-feedback-deepseek-v4-flash.md): Historical no-output hangs and the non-SSE timeout-bypass reproduction are distinct observations. Provider-side attribution is not established merely by silence, and the old reproduction does not establish the cause of later stalls.
- [gemini-3.1-pro](../research/registry/model-feedback-gemini-3.1-pro.md): The two bounded audit timeouts establish those runs did not finish within their budgets, not a generally sufficient three-minute timeout or a model-intrinsic cause.
- [gpt-5.6-luna](../research/registry/model-feedback-gpt-5.6-luna.md): The observed review strengths remain historical; this OpenCode route is not authorized by the current launch policy. Absence of hangs in the sampled runs is not a reliability guarantee.
- [hy3](../research/registry/model-feedback-hy3.md): Retain the task-specific review and implementation-readiness findings; the recorded correction of a syntax error is not authorization for a provider/model fallback.
- [laguna](../research/registry/model-feedback-laguna.md): No response, no logged errors and other concurrent successes do not establish provider-side causation or rule out other failure boundaries; the observed timeouts remain valid.
- [ling](../research/registry/model-feedback-ling.md): Retain the narrow review observations. A missing verdict alone does not distinguish a launch, execution or reporting failure.
- [mimo-v2.5](../research/registry/model-feedback-mimo-v2.5.md): The five completed August tasks and role-permission finalization gap are scoped observations, not a universal completion rate or assurance about later versions/routes.
- [muse-spark-1.2-contributor](../research/registry/model-feedback-muse-spark-1.2-contributor.md): Distinguish proxy/corpus token compression results, observed model outputs, and live-route checks. The later same-run Go no-text outcome is additional evidence, not a contradiction of the earlier successful sessions or proof of model failure.
- [nemotron](../research/registry/model-feedback-nemotron.md): The two recorded 502 upstream errors establish failures on that route at that time, not current unavailability or model deficiency. The historical paid-fallback recommendation is not authorization.
- [north-mini-code](../research/registry/model-feedback-north-mini-code.md): Retain the observed concise verification results; zero false positives in a small historical sample does not establish general correctness or current service availability.

The [Model Routing Matrix](../research/registry/Model-Routing-Matrix.md) tracks cumulative capability evidence for tentative job routing, including its dated historical assessments. Neither it nor this record authorizes a route: use the [current launch skill](../../skills/current/agent-launch/SKILL.md) and [review-launch skill](../../skills/current/review-launch/SKILL.md).

## November diagnostic evidence

The ongoing investigation is independently owned by Work Notes WNASES-21 and Projektor ASES-21. This is a source map and bounded retrospective, not a new registry or replacement for the diagnostic report. Do not repeat accepted fixtures or invoke models based on this record.

- [Stage 1 run 44728498241](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44728498241): DeepSeek Go and Muse Spark on one runner emitted step_start but no answer text by unequal 90s and 50s cutoffs. HTTP headers and upstream content were unobserved.
- [Stage 2 run 44729384486](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44729384486): same 2,774-byte prompt completed via Phoenix Grove/Codex (2,675 output characters, 16.73s). Changed harness, gateway, runner and time prevent causal isolation. The task is not inherently impossible; no general provider verdict follows.
- [M5-2 route-attempt report, pinned](https://github.com/rock-solid-sites/ases-plugins/blob/050226a9e652c708d26b84afd846b64a688c5db6/diagnostics/model-stalls/M5-2-ROUTE-ATTEMPT.md): OpenCode v2.4.1 synthetic request/header/body boundary instrumentation verified in scoped fixtures. One proposed retry was vetoed in each negative case; no real provider calls. Dummy route construction does not establish authenticated configuration, actual network delivery, or universal retry suppression.
- [M5-3 run 45372297792](https://github.com/rock-solid-sites/ases-plugins/actions/runs/45372297792), recorded in the [pinned M5-4 report](https://github.com/rock-solid-sites/ases-plugins/blob/eec34f2eccaa708e6b99b7c077e9199a8c637c37/diagnostics/model-stalls/M5-4-SSE-BOUNDARY.md): one admitted primary HTTP hook attempt, HTTP 200 headers after 18.133s, first body 1.924ms later; at least 913,672 bytes / 4,784 chunks by 89.669s after request, maximum sampled progress gap 0.842s. CLI step_start only, no answer text or finish; watchdog exit 143 after 90.106s; exact session persisted interrupted, zero assistant text, no orphan or observed second request. **Idle transport stall is contradicted for this run.** Wire bytes alone do not identify semantic content, decoded events or cause. Token usage and monetary cost unknown. This does not diagnose other incidents.
- At this review cutoff, M5-4 was staged to discriminate wire semantics, native decoded event feed, CLI events and persisted parts. The Work Notes checkpoint records an F03 mock origin-audit timing correction after three other fixture passes, with a gated live probe pending. [Initial CI](https://github.com/rock-solid-sites/ases-plugins/actions/runs/45407513672), [correction CI](https://github.com/rock-solid-sites/ases-plugins/actions/runs/45446096059). No later result is asserted here; consult WNASES-21 and the source report for current position.

## Transferable implications

Keep observations at the boundary actually measured: preflight and authorization; request preparation versus delivery; headers; body progress; wire semantics; decoded events; CLI output; terminal status; persisted task-valid result. A timeout, step_start, process liveness, no text, or HTTP success alone is not a root cause or task success. Separate model behavior, route/provider behavior, harness behavior, infrastructure and instrument defects; mark attribution unknown when evidence cannot discriminate. A synthetic reproduction establishes the mechanism in its tested configuration, not all subsequent symptoms. Prefer the cheapest test that distinguishes remaining hypotheses; retain negative findings and compare like-for-like configurations before making causal claims. These are applications of the existing evidence-based orchestration method, not a new global debugging procedure or production enforcement claim.
