---
title: Recurring Coordination Failures — Initial Classification
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-26
---

# Recurring coordination failures: initial field-trial classification

Purpose: reduce recurring operator intervention across projects by distinguishing observed behavior from its cause. This is a provisional evaluation vocabulary, not a mandatory issue template, new policy, or measured frequency ranking. Cases can carry more than one label. Compare behavior with the applicable source, tool availability and authorization **at the time of the incident**, not rules adopted later.

## Observable failure classes

| ID | Symptom | Discriminator |
| --- | --- | --- |
| F1 | Premature termination | A feasible, authorized diagnostic or correction remained, but the agent returned instead of pursuing it. |
| F2 | Unproductive repetition | Same check or retry with no relevant changed input, hypothesis, discriminator or justified transient-fault budget. |
| F3 | False blocker | Claimed impossibility despite an available authorized route; distinguish genuine tool, permission, resource and host limits. |
| F4 | Context and authority failure | Wrong source, revision, subject owner, obsolete guidance or omitted applicable method. |
| F5 | Objective displacement | Subordinate tooling, infrastructure, process or documentation becomes the deliverable instead of the requested outcome. |
| F6 | Verification failure | A proxy, intermediate outcome or passing but non-discriminating test is reported as satisfaction of the actual acceptance condition. |
| F7 | Persistence failure | Material result, reasoning, dependency, next action or unresolved operation is lost, duplicated, misrouted or stale. |
| F8 | Authorization failure | Unnecessary escalation of already authorized work, or execution beyond the authorized effect, route, budget or scope. |

## Causal classification (independent of symptom)

- C0 — actual capability/authority/resource limit: a genuine blocked transition, not intrinsically agent failure. Judge how the agent handles it.
- C1 — missing guidance: necessary behavior was not specified at incident time.
- C2 — defective guidance: contradictory, obsolete, excessively broad, misleading or harmful even when followed.
- C3 — discovery/admission failure: applicable guidance exists but does not reach the agent's effective task context.
- C4 — application failure: evidence shows the applicable guidance was received but not followed.
- C5 — ineffective control: guidance was followed yet the intended outcome was not achieved, or purported mechanical protection did not actually constrain behavior.
- CU — unresolved: evidence does not distinguish causes. Do not convert a plausible diagnosis into fact.

Separate consequence (operator interruption, repeated compute, delay, wrong result, loss of recoverability, unauthorized effect) from cause. A frequent inconvenience and a rare irreversible safety failure are not interchangeable. Recurrence requires independent incidents, or a repeat of the same material failure after a correction; do not infer recurrence merely from multiple descriptions of one incident. Where evidence permits, record prior rule/version, observable behavior, effect, corrective action, later comparable opportunity and whether it passed. No extra record is required when an existing research or execution record suffices.

## Bounded evidence and controls

1. **F4/C2, evidenced source-selection defect:** [November 20 prompt-source field trial](PROMPT-SOURCE-ADMISSION-2026-11-20.md) and [PR #73](https://github.com/rock-solid-sites/ASES/pull/73). Applicable preparation method existed; selection guidance did not reliably require it for the actual work product. Static source correction is not proof of autonomous selection or correct application. Avoid generic conclusions about all later runs.
2. **F1 and F2, qualitative recurring correction:** routine failures returned prematurely; converse risk is repeated unchanged attempts. Current [orchestration skill](https://github.com/rock-solid-sites/ASES/blob/main/skills/current/workflow-orchestration/SKILL.md) v1.0.8 and [general escalation correction](https://github.com/rock-solid-sites/ASES/commit/bfeb9ba8ee4e092fd4a6086157d2c90e5517c3e7) distinguish diagnosis, smallest justified correction, bounded rerun and genuine escalation. Historical causes remain case-specific; do not diagnose nonadherence merely from a current rule existing.
3. **Positive recovery control:** [T03 final result](https://github.com/rock-solid-sites/extensions-comparative/blob/main/results/2026-11-26-t03-http-final.md) is a completed corrected run with explicit native/composed limits. Earlier setup failure and correction are documented by the owner. Success after operator intervention is recovery evidence, not proof that recovery began autonomously.
4. **Valid stop control:** a bounded model batch can hit its declared attempt/output limit without producing a usable result. Diagnosing that limit and retaining evidence without unauthorized continuation is correct behavior; it must not be counted as F1 simply because the result is red. The private execution records retain the concrete case.
5. **F7/CU versus F7/C2:** stale current pointers and excessive append-only notes have been observed; an obsolete runbook can actively prescribe repeating an accepted gate. Correct the current locator and retain history. A record updated while a worker is still executing is not automatically a per-turn omission; the actual turn boundary matters.
6. **F3, F5, F6 and F8:** qualitative cross-project incident families identified during retrospective review. Individual root cause, actual applicable instructions, alternatives, severity and repeat-after-correction require case-level evidence. No claim of frequency, exhaustive archive review or measured compliance.

## Investigation order

First examine recurring F1–F3 (premature return, unchanged retry, false blocker) together: did the agent have a permitted next action, and did the next attempt discriminate or progress? Next F4/F7 (authority and recoverability), then F5/F6 (goal and acceptance), and F8 at each boundary independently. Prioritize actual irreversible, privacy, authorization or resource risks regardless of recurrence. Existing [task-scoped method](https://github.com/rock-solid-sites/ASES/blob/main/docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md), current skills and local project boundaries already address much of this; do not automatically add more guidance. Correct the smallest owner source for C1/C2, test discovery for C3, consider narrow enforcement for demonstrated C4/C5, and investigate CU. ASES-23 owns broader ordinary-use evaluation; WNASES-23 owns skill-selection behavior. Raw or private incident evidence stays in authorized private records. No runtime test, new policy, mandatory schema, or independent full-transcript reconstruction in this increment.
