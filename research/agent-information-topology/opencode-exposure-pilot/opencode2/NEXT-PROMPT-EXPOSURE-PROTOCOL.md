---
title: WNASES-19 - OpenCode V2 Prompt-Exposure Test Protocol
program: ASES
layer: Research
document_type: Test Plan
status: Draft
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-20
---

# Next discriminating OpenCode V2 exposure test

**Not yet executed.** This protocol extends the executed discovery and behavioral runs in this directory. Do not treat it as evidence that prompt bytes have been captured.

## Question

When OpenCode V2 is launched from a clean project versus an identical project containing a retired discoverable skill, what exact *metadata or body markers* reach the model request, as opposed to merely appearing in the filesystem or a skill catalog?

The prior paired model test returned the same approved label for both fixtures. That tests behavior, not prompt inclusion.

## Controls

Use the exact OpenCode V2 binary version and a pinned, explicitly authorized model/route. Run each fixture in a fresh isolated session with separate data/config/cache directories, the same agent, task and runtime settings. Record version and source commit; no default model or fallback.

Before any real model request, verify that the chosen provider and exact model remain included in the operator's OpenCode Go subscription, or have a verified zero-price Zen route; confirm Go Extra Usage is disabled and no unrelated paid API credentials are passed. If not verified, **stop without invoking a model**. Never select OpenAI API, a paid Zen model, Phoenix Grove or a different host to work around a failed route.

Use only synthetic source trees and harmless canary strings. Do not place canaries in the actual ASES checkout or any other operational repository.

| Fixture | AGENTS root | Current skill | Retired skill |
| --- | --- | --- | --- |
| A clean | `ACTIVE_PINE` | metadata containing `CURRENT_META_PINE`, body containing `CURRENT_BODY_PINE` | absent |
| B cluttered | identical | identical | metadata containing `RETIRED_META_STONE`, body containing `RETIRED_BODY_STONE` |
| C explicit skill access | identical to B | identical | same, but task explicitly requests the retired skill for an observation-only query |

Only fixture C explicitly authorizes reading the retired skill. Its purpose is to distinguish an on-demand body load from automatic injection; it must not follow the conflicting instruction.

## Observation method

**Preferred:** instrument the existing harness at the last request-assembly boundary before sending to the selected provider. Verify the hook or code path against the *pinned CLI version* and whether it sees the actual outgoing request. Store only local boolean/number observations for four marker strings by request number and message role. Never print raw prompt text, authentication headers, user secrets, or full provider responses. Request capture must be nonblocking and make no network calls beyond the already authorized provider request.

If no suitable, verified request-assembly interception exists, report that as a blocker. Do not substitute model self-reports such as "what was in your system prompt" for direct observations.

Record independently:

1. Filesystem presence of each marker.
2. What `debug skill` / equivalent discoverability API enumerates, including names and descriptions.
3. Whether the *actual outgoing request* includes each marker; separate current/retired metadata from the corresponding body string and separate roles/message types.
4. Only if authorized, a model answer to the original neutral task, compared between fixtures A and B.

A minimal outcome table should contain fixture, CLI revision, source revision, selected approved provider/model/host/billing route, capture boundary, discovery flags, pre-send marker flags, run exit, answer canary (if an actual model was invoked), and evidence link. If the request is streamed or modified upstream by a service beyond the observation point, state that limitation; no claim of full provider-received bytes.

## Falsification and outcomes

- Retired metadata appears in B's pre-send request but retired body does not: **catalog visibility without demonstrated body injection**.
- Retired body appears in B before any explicit skill read: **automatic legacy-content exposure**.
- Retired body appears only in C after explicit read: **on-demand body loading**, under the tested harness/version.
- Neither marker appears in B pre-send despite file discovery: **filesystem discovery differs from model request assembly**.
- Two attempts yield inconsistent traces, no verified interception boundary, or an unauthorized route: **unresolved**.

No single behavioral answer can prove absence of unwanted instruction exposure. Run at least two independent sessions per fixture if the provider route is authorized and inexpensive; otherwise retain the single-shot evidence and its limitation.

## Evidence and authority

The experiment belongs to WNASES-19 and the existing ASES PR #63 branch. A negative result is not permission to remove historical instructions or declare universal safety. Reconcile with independent Codex policy-publication work only after its own first-pass evidence is frozen. Do not build the Resource Solver, modify current skill source, or adopt a third-party prompt logger without inspecting its code and permissions.

Reference previous runs: OpenCode 1.19.6 discovery [44664779334](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44664779334), OpenCode V2 paired behavior [44674313983](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44674313983). The current ASES launch authorization convention is in `skills/current/agent-launch/SKILL.md`.
