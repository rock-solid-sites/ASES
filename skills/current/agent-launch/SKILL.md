---
name: agent-launch
version: 1.0.2
description: Resolve and verify ASES agent execution routes across GitHub Actions, Codespaces, Modal, and authorized model providers before launching.
status: current
---

# Agent launch and route selection

Resolve **controller**, **execution host**, **launcher**, **target provider/model**, **permissions**, **source revision**, **resource/time budget** and **durable result location** before launch. Model identity belongs in trusted caller-side settings, not in the recipient's self-identification prompt. Never silently substitute models or execution hosts.

## ChatGPT coordination launch convention (active)

**No inferred model selection, no default models, no delegated model selection.** Before authoring a manual-launch task or calling a tool/workflow that can invoke any model, the coordinator must establish the exact caller-side `provider/model` ID, execution host, entitlement/billing route, and `fallback: none`. Display a compact launch declaration in chat (one line is enough), for example: `OpenCode Go subscription | <exact catalog-verified opencode-go/model> | host verified | paid API: forbidden | fallback: none`. Do not place model choice in the receiving agent's discretion.

**Current OpenCode authorization:** only models explicitly verified as included in the operator's **OpenCode Go subscription** (exact `opencode-go/...` ID), or independently verified **zero-price OpenCode Zen** models on the exact `opencode/...` route. Zen is not uniformly free; neither the provider namespace nor a model name containing "free" alone proves zero cost. Revalidate model identity and free status for the actual execution route. Unknown availability, cost, authentication, quota, or entitlement means **STOP without invocation**. Do not use a general OpenAI API, paid Zen route, OpenRouter, Phoenix Grove, or other token-billed provider for OpenCode orchestration/reviews under this policy, even if a key is present or a historical run succeeded.

**Luna route exclusion (cost rule):** GPT-6 Luna is reserved for the operator's existing **ChatGPT Plus/Codex subscription**. **Do not select `opencode-go/gpt-6-luna` or any other OpenCode, Go, Zen, API or third-party Luna route**, even if the model appears in a catalog or succeeds on another provider. A Codex Cloud Luna task is permitted only when the operator's authenticated subscription, chosen model, and execution environment are confirmed; otherwise report the blocker and do non-model work. Never substitute OpenCode Go Luna for an unavailable Codex Cloud environment. ChatGPT subscription access does not authorize an OpenAI API call.

**Other model execution:** use OpenCode only for *non-Luna* models whose exact Go-subscription or independently verified zero-price Zen route is authorized as above. A model bearing a familiar name on another provider is not the same authorized billing route.

**Stop rule:** Never use automatic model fallback, paid overages/Extra Usage, inferred substitutes, or a default model to work around a missing route. If the allowed exact model cannot be verified or launched, report the blocked route and continue only with non-model work. Do not run a model just to test the validity of model selection. The same rule applies to manual launch prompts, delegated agents, GitHub Actions recipes and diagnostic probes. The coordinator owns model choice; the receiving agent must not be asked to choose it.

**Scope and assurance:** This is a conversation/dispatch procedure, not a claimed universal mechanical enforcement boundary. Existing picker-label plugins and historical Crosslink Task gates do not enforce it. A model-facing prohibition is weaker than host-side credential restrictions; do not claim an agent cannot bypass a convention. Future centralized admission control belongs with the separately planned Resource Solver.

For independent reviews, use `skills/current/review-launch/SKILL.md` and the current `ases-plugins` reviewer recipe. GitHub Actions is proven for short, bounded one-shot reviews; Codespaces/Modal are candidates for deep investigations, with workload-specific readiness to verify.

The old IT3812/VPS and Crosslink environment mentioned in `docs/methodology/Agent Model Launch Routes.md` is **historical** and must not be assumed connected or executable. Use that document only for model-provider compatibility details explicitly corroborated in current runs. Historical Phoenix Grove reviewer routes and credentials are documented separately; prior successful tests are not spending authorization under the current Go/free-Zen launch convention.

Check the actual connected tools before claiming a remote launch can happen. Prefer the smallest approved test. On missing tool, route, account, secret or authorisation, report the precise blocker; no silent fallback. For long-running tasks, preserve durable commits/position records and validate progress rather than treating a live process as proof of work.
