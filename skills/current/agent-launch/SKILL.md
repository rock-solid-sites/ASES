---
name: agent-launch
version: 1.0.3
description: Resolve and verify ASES agent execution routes across GitHub Actions, Codespaces, Modal, and authorized model providers before launching.
status: current
---

# Agent launch and route selection

Resolve **controller**, **execution host**, **launcher**, **target provider/model**, **permissions**, **source revision**, **resource/time budget** and **durable result location** before launch. Model identity belongs in trusted caller-side settings, not in the recipient's self-identification prompt. Never silently substitute models or execution hosts.

## ChatGPT coordination launch convention (active)

**No inferred model selection, no default models, no delegated model selection.** Before authoring a manual-launch task or calling a tool/workflow that can invoke any model, the coordinator must establish the exact caller-side `provider/model` ID, execution host, entitlement/billing route, and `fallback: none`. Display a compact launch declaration in chat (one line is enough), for example: `OpenCode Go subscription | <exact catalog-verified opencode-go/model> | host verified | paid API: forbidden | fallback: none`. Do not place model choice in the receiving agent's discretion.

**OpenCode Go/Zen restriction (not a provider-wide ban):** for the operator's OpenCode Go subscription, select only exact approved `opencode-go/...` model IDs; for OpenCode Zen, select only independently verified **zero-price** `opencode/...` models. Zen is not uniformly free, and a `-free` suffix is not sufficient proof. An unknown, paid, or unapproved **OpenCode Go/Zen model** is denied. Revalidate the exact model and route rather than relying on defaults, aliases or historical success.

**Phoenix Grove is separately authorized, not banned.** When the operator requests Phoenix Grove independent reviewers, the established Phoenix Grove route (including the existing PGS2 GitHub Actions reviewer workflow) is permitted. Resolve its **exact model and provider route** in caller-side settings, verify the current credential, allowance/billing conditions and job limits, and use no silent substitute or unapproved fallback. This permission is not limited or revoked merely because the reviewer is invoked by a Codex or OpenCode CLI. Do not confuse the **OpenCode Go/Zen account restriction** with a ban on a separately approved Phoenix Grove provider. A Phoenix Grove credential does not authorize a general OpenAI API charge.

**General OpenAI API billing:** the operator has not authorized pay-as-you-go OpenAI API credits. ChatGPT Plus and OpenCode Go subscriptions do not grant that authority. Unknown entitlement, cost, authentication or quota means stop that specific route and report it; never assume a different provider is allowed.

**Luna route exclusion (cost rule):** GPT-6 Luna is reserved for the operator's existing **ChatGPT Plus/Codex subscription**. **Do not select `opencode-go/gpt-6-luna` or any other OpenCode, Go, Zen, API or third-party Luna route**, even if the model appears in a catalog or succeeds on another provider. A Codex Cloud Luna task is permitted only when the operator's authenticated subscription, chosen model, and execution environment are confirmed; otherwise report the blocker and do non-model work. Never substitute OpenCode Go Luna for an unavailable Codex Cloud environment. ChatGPT subscription access does not authorize an OpenAI API call.

**Other model execution:** use OpenCode with approved Go/zero-price Zen models, **or the explicitly requested Phoenix Grove reviewer route** for approved non-Luna models. Do not silently convert an OpenCode Go task into Phoenix Grove usage or vice versa. A familiar model name on a different provider is a different route and must be explicitly selected.

**Stop rule:** Never use automatic model fallback, OpenCode Go Extra Usage/pay-as-you-go overages, inferred substitutes, or a default model to work around a missing route. If the authorized exact route cannot be verified or launched, report the blocked route and continue only with non-model work. Do not run a model just to test the validity of model selection. The same rule applies to manual launch prompts, delegated agents, GitHub Actions recipes and diagnostic probes. The coordinator owns model choice; the receiving agent must not be asked to choose it. A user-requested Phoenix Grove review is a valid explicit route selection, not a fallback violation.

**Scope and assurance:** This is a conversation/dispatch procedure, not a claimed universal mechanical enforcement boundary. Existing picker-label plugins and historical Crosslink Task gates do not enforce it. A model-facing prohibition is weaker than host-side credential restrictions; do not claim an agent cannot bypass a convention. Future centralized admission control belongs with the separately planned Resource Solver.

For independent reviews, use `skills/current/review-launch/SKILL.md` and the current `ases-plugins` reviewer recipe. GitHub Actions is proven for short, bounded one-shot reviews; Codespaces/Modal are candidates for deep investigations, with workload-specific readiness to verify.

The old IT3812/VPS and Crosslink environment mentioned in `docs/methodology/Agent Model Launch Routes.md` is **historical** and must not be assumed connected or executable. Use that document only for model-provider compatibility details explicitly corroborated in current runs. Phoenix Grove reviewer routes and credentials are documented in the established `ases-plugins` reviewer recipe. Phoenix Grove is approved for operator-requested reviewer work; historical tests establish technical reachability but do not by themselves prove current account allowance or a particular invocation's success.

Check the actual connected tools before claiming a remote launch can happen. Prefer the smallest approved test. On missing tool, route, account, secret or authorisation, report the precise blocker; no silent fallback. For long-running tasks, preserve durable commits/position records and validate progress rather than treating a live process as proof of work.
