---
title: "ASES reviewer provider selection from recorded accounts"
version: 0.1.0-experimental
status: ranked-preflight-required
authority: run-scoped-research
run_id: ASES-SOL-CTRL-A-20261113
source_inventory_ref: 9a122c6c840c39dbe0cefbfc3cf2970b3d0a5a2f
review_date: 2026-11-13
---

# Select from the provider registry, not an arbitrary example list

**Decision:** Use a **fixed-model, tool-free external-family inference endpoint** for routine static falsification and **GitHub Actions** as the first independently observable executable-review environment. At session start Luna must compare all relevant accounts against current usage/entitlement evidence and promote a route only after actual preflight. Secondary execution candidates are **Modal** and **GitLab CI**; their current launch/account status requires verification. No provider has been launched by this document.

## What the inventory actually says

Pinned registry in `research/provider-registry/`:
- `known_accounts_v1.json`: **28 account records**, ranging from `tool_observed` or `user_confirmed` to `user_reported`. All have `usage.status=unknown`; none has a live remaining-balance observation.
- `candidate_inventory_v0.json`: **54 discovery providers**. All entries say `unverified_candidate`, even when official API launch documentation is recorded.
- `potential_offers_v1.json`: **26 offers/comparators**, with no verified current awarded/remaining promo balance. Do not treat prospective credits as available.
- PR #44 documentation describes 17 source-backed launch routes, all still `account_access=unverified`, `adapter_state=not_implemented` and `launch_test=not_run` in the discovery plane. This is not contradictory to observed GitHub Actions runs; it means no dedicated provider-registry adapter has been validated.

Ranking weighs (a) evidence that **this account exists and has a working path**, (b) task fit, (c) no additional signup/spend, (d) direct API/workflow launch, (e) reproducibility and correct model provenance, (f) privacy, (g) setup cost. The absence of verified quota, credentials and cost is an explicit gate, not a zero-cost claim.

## Tool-free external-family reviewer: candidate order

| Order | Provider/account record | Account evidence | Published model/access route | Decision and gate |
| --- | --- | --- | --- | --- |
| **1** | `nvidia` — NVIDIA build/NIM | `user_reported` | Developer Program offers free prototyping API endpoints; fixed open model IDs can give separate model-family review | **First tiny no-code API capability test** if a usable preexisting credential is available in the approved executor; confirm fixed model identity, quota, privacy terms and egress; never infer live entitlement from account record |
| **2** | `google` — Google AI Studio / Gemini API | `user_reported` | Gemini Developer API free tier is model/project dependent | **Independent-family fallback or second opinion**; verify this specific AI Studio project/key and current limits; a Google/Drive account is not an API entitlement |
| **3** | `openrouter` — OpenRouter | `user_reported` | Some explicitly named `:free` API models can be used without a credit purchase; current free-model cap published as 50/day at unfunded tier | **Flexible fallback and model catalog**, if a verified API key exists. Pin exact model/provider; do not silently use `openrouter/free` auto-routing when independent-model provenance matters; keep fallback list free-only |
| **4** | `mistral` — Mistral API | `user_confirmed` signup | Mistral's current API usage documentation says free mode does **not include API access** without pay-as-you-go activation, although an Aug 2026 support article describes free-mode limits. Treat as conflicting/stale docs | **Conditional**; request actual billing/limits observation before use. Signup and a Vibe subscription are not API credits |
| **5** | `deepseek`, `xiaomi-mimo`, `opencode` | `user_reported` | Different-family inference may be available through existing subscriptions/APIs; paid plans or separate wallet scopes vary | **Paid or quota-dependent fallbacks**, only after account-specific model ID, credit/usage meter and spending approval are observed. OpenCode account is a harness/model subscription, not generic third-party compute |
| Further | `hugging-face`, `phoenix-grove`, `openai` | `user_reported` | Some inference or hosted offerings; model routes unknown | Not first choice: no verified targeted reviewer endpoint; OpenAI-family is weaker for the required cross-family comparison |

**Selection is of the actual model family, not just the reseller.** Two routes serving the same model do not constitute two independent families. The fixed model name, provider's response metadata and exact prompt/source SHA must be recorded. A model's self-description is not independent provider verification.

## Executable review: candidate order

| Order | Provider/account record | Account evidence | Fit and current evidence | Gate before a new job |
| --- | --- | --- | --- | --- |
| **1** | `github` — GitHub Actions | `tool_observed` | An actual ASES workflow executed on Nov 12 (job `131445439283`) and produced useful failed-test logs. GitHub Free publishes 2,000 included private-repo minutes/month; public-repo standard-runner policy differs. Excellent for pinned, finite tests/artifact logs | Check actual billing owner/remaining minutes and workflow dispatch path. Existing CI execution does **not** imply arbitrary reviewer launch adapter already works or is free |
| **2** | `modal` — Modal sandboxes | `user_confirmed` and local CLI previously reported working | Serverless sandbox API with short-lived containers; Starter advertises $30 monthly included compute, including Sandboxes; no current account balance or remote Codex-to-Modal launch evidence | Read-only entitlement/credential/egress preflight, explicit bounded sandbox/job, verified cleanup and non-billable/approved cost. Do not treat historical local CLI as Cloud credentials |
| **3** | `gitlab` — GitLab CI | `user_reported` | API-triggered CI with independent runner environment; GitLab.com Free publishes 400 compute minutes/month | Validate actual GitLab account/project runner/quota, private source access, API route, mirror/checkout complexity and minute accounting |
| **4** | `github` — GitHub Codespaces | `tool_observed` account, Codespaces-specific entitlement unknown | Interactive persistent dev session is overkill for finite batch reviews, useful when the review needs retained checkout/session state | Verify personal/org billing and remote create/exec/reconnect route; not first for quick reproducible CI |
| **5** | `daytona`, `e2b`, `vercel` | `user_reported` | Purpose-built sandboxes or short-lived compute; may fit independent tests better than persistent VM | No current entitlement/API credential or demonstrated launcher; execute only after a cheaper preflight shows one works |
| **6** | `cloudflare` — Sandbox/Containers | `user_confirmed` for Workers/Pages, not Sandbox entitlement | SDK launches containers through Workers but **current Sandbox docs say Workers Paid plan required** | Check actual Paid plan and specific Sandbox entitlement; Workers Free usage does not imply container access |
| Conditional | `hostkey` VPS | `user_confirmed` | Existing remote Linux host could run OpenCode | CPU sustained-use constraint and user migration/backup make it a poor default for reviews |
| Discovery only | `northflank`, `blaxel`, `runloop`, `fly`, `render`, `koyeb`, `railway`, `codesandbox`, `cursor`, `replit`, `coder`, `devpod`, `bunnyshell`, `eclipse_che`, `circleci`, `buildkite`, `azuredevops`, etc. | **No corresponding recorded eligible account** in the 28-account snapshot | Some have documented APIs and can be excellent future choices | **Not eligible for first round as an already-accessible provider**; re-rank if an actual account, entitlement and launch path are observed |
| Other account classes | Drive/IDrive/B2/Box/MEGA/pCloud/TeraBox/iCloud; Mistral/DeepSeek inference; generic new AWS/Azure/GCP/Oracle/VPS candidates | mixed | Storage, inference, or new-billing surfaces do not provide a verified generic executable reviewer | Exclude unless a concrete previously verified execution account/product and approved meter emerges |

The available **26 offers** are not substituted for working accounts. No signup, preauthorization, secret copying or paid capacity is part of this ranking.

## Execution policy

**First goal:** no cloud machine at all. Luna prepares a tightly bounded blind review packet, verifies an approved external provider endpoint with a tiny nonsensitive call only if credentials and zero/approved cost are known, then dispatches a fixed-model tool-free critique. The reviewer returns falsifiers, not a self-certification.

If the claim requires actual tests, use an independent Luna to turn findings into tests on a known executor. Start with GitHub Actions (existing demonstrated runner) when the workflow can be run under known quota. If source/tool exploration is needed beyond CI, test Modal's controlled sandbox route next; GitLab CI is a distinct execution-provider fallback.

For every dispatch, record `source_inventory_rev`, `provider_account_id`, `model_id`, `model_family`, `executor`, `billing_owner`, `quota_snapshot`, `prompt_hash`, `source_ref`, `started_at`, `result_ref`, `cost_actual_or_unknown`, and `cleanup`. If a hard unknown exists, **NO_LIVE_ROUTE**, not `$0`.

Private source disclosure requires an authorized destination and data-handling terms; no full-repo upload just because a free model exists. No credentials, identity claims, tokens, private billing accounts or secret values in Git or reviewer prompts.

## Public documentation verified at review time

- NVIDIA NIM Developer Program: https://docs.api.nvidia.com/nim/docs/product
- Google AI Studio limits: https://aistudio.google.com/docs/rate-limits
- OpenRouter free model caps and exact model IDs: https://openrouter.ai/collections/free-models
- Mistral current usage limits: https://docs.mistral.ai/admin/billing-usage/usage-limits
- Mistral Aug 2026 support FAQ: https://help.mistral.ai/en/articles/698531-why-am-i-hitting-api-rate-limits-and-how-do-i-increase-them
- GitHub Actions private-runner specs: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- GitHub Free included Actions minutes: https://github.com/pricing
- Modal sandbox pricing/Starter: https://modal.com/pricing
- GitLab.com Free CI quota: https://docs.gitlab.com/ci/pipelines/compute_minutes/
- Cloudflare Sandbox plan gate: https://developers.cloudflare.com/sandbox/

**Unknown:** model API keys/actual quotas, provider-specific data retention, reviewer API ingress from Codex Cloud, external model entitlements, whether an approved low-cost remote launcher is authenticated and callable from the session. The first Luna probe must answer those questions with exact tool and account evidence; do not overstate this report as a live capability test.
