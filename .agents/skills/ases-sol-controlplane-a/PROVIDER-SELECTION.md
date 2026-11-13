---
title: "ASES reviewer provider selection from recorded accounts"
version: 0.3.1-experimental
status: ranked-preflight-required
authority: run-scoped-research
run_id: ASES-SOL-CTRL-A-20261113
source_inventory_ref: cf10333db1d23383eb14c555f9e04d636d4a845a
review_date: 2026-11-13
---

# Select from the provider registry, not an arbitrary example list

**Decision:** The **specific unsolved experiment** is invoking OpenCode's free Console models through a Luna-owned **OpenCode CLI process inside Codex Cloud**. The user **already has paid OpenCode Go**; don't rediscover its account, but the Go Flash versions are affordable fallbacks. For the simple **tool-free** review of a bounded, private ASES code/contract packet, prefer **existing OpenCode Console/Go** (different underlying model families) and **OpenRouter's $5 reported monthly credit** over provisioning any cloud compute service. Model identity, privacy, plan and credentials in the chosen Luna environment must be verified. New free signup options such as Groq/Z.ai merit consideration if existing routes fail. **Do not send raw private ASES code to NVIDIA's free prototyping endpoints or Google's unpaid Gemini API by default**, because the services permit data use/review beyond our zero-training expectation. GitHub Actions is the proven *test runner*, while Northflank/Modal/GitLab and other sandbox providers are only needed if the external verifier itself requires tools or a repository checkout. No model call or compute launch was executed in this research.

## What the inventory actually says

Pinned registry in `research/provider-registry/`:
- `known_accounts_v1.json`: **29 account records**, ranging from `tool_observed` or `user_confirmed` to `user_reported`. All have `usage.status=unknown`; none has a live remaining-balance observation.
- `candidate_inventory_v0.json`: **60 discovery providers**. All product routes remain unverified; the six new *inference-only* discovery providers are Groq, Cohere, Z.ai, Cerebras, SambaNova and Ollama, **not owned accounts**. Northflank is independently user-confirmed as an **existing account**, while its manual-job/sandbox product entitlement remains unverified.
- `potential_offers_v1.json`: **26 offers/comparators**, with no verified current awarded/remaining promo balance. Do not treat prospective credits as available.
- PR #44 documentation describes 17 source-backed launch routes, all still `account_access=unverified`, `adapter_state=not_implemented` and `launch_test=not_run` in the discovery plane. This is not contradictory to observed GitHub Actions runs; it means no dedicated provider-registry adapter has been validated.

Ranking weighs (a) **verified effective cost and usable quota**, (b) model/executor suitability, (c) tested automation/launch path, (d) privacy and model provenance, (e) isolation and reproducibility, and (f) **realistic onboarding time**. Existing account access is an advantage but not a prerequisite: GitHub/Google SSO free signups can be completed quickly by the operator. Keep *account exists*, *account is quickly obtainable*, *product entitlement verified*, and *job launched* as separate evidence states. Absent quotas/costs are UNKNOWN, never $0.

## Tool-free external-family reviewer: first-use order

| Priority | Provider / actual account | Specific route and cost state | Privacy/verification gate |
| --- | --- | --- | --- |
| **Fallback** | **OpenCode Go** (`opencode`, **paid subscription operator-confirmed**) | The ordinary **DeepSeek V4.1 Flash, MiMo V2.6 Flash and GLM-5.3 Flash** models are available under Go. Exact tier, remaining allowance and credential availability in Codex Cloud still unknown | If Console free CLI cannot be launched economically, use a normal Go Flash model via an authorized Go-compatible route. Distinguish plan-included usage from fully free calls; choose different underlying family from builder |
| **First capability test** | **OpenCode Console free** (`opencode`, already held) | **GLM-5.3 Flash Free, DeepSeek V4.1 Flash Free and MiniMax M3.1 Flash Free** are temporary no-charge offers through the **OpenCode CLI**; they are **not generally callable directly as Codex third-party API clients** | Luna attempts a single harmless, bounded **CLI-only** review process within Codex Cloud, with tools disabled and secret-safe auth; stop after a concrete failure, do not waste Sol quota on environment work; no self-verifier model family |
| **2** | **OpenRouter** (`openrouter`, user-confirmed account, $5/month credit claimed) | Fixed-model direct API. Strong *Claude Sonnet 5.5* costs about **$0.08** for a 20k-input/4k-output example at $2/$10 per million. Other inexpensive models available. Free `:free` quotas vary with lifetime purchases | Confirm current **remaining** balance, model, provider **ZDR/no training** and source packet privacy. Choose exact model, prohibit silent fallback across families |
| **3** | **Groq** (NEW candidate; not an observed account) | Free API suitable for small Qwen/Llama packet reviews; official Free plan Qwen3.8-27B sample: 30 RPM, 1k RPD but only 8k TPM | Fast free SSO signup candidate, per-account quotas and **ZDR controls**; chunk long source packet if necessary |
| **3** | **Cloudflare Workers AI** (`cloudflare`, existing account) | Published 10,000 free neurons/day; suitable free models depend on exact SKU | Check Workers AI token/API and SKU; strongest Kimi/GLM/DeepSeek models listed on pricing often require paid billing |
| **4** | **Z.ai** (NEW candidate; not an observed account) | Official **GLM-4.7-Flash** free input/output with 200k context, attractive for long source packets | Confirm signup, model entitlement, account limits and especially confidential-source/data terms |
| **Conditional** | **NVIDIA NIM** (`nvidia`, user-confirmed key) | Free prototyping for model families including Nemotron and open weights; account rate limit needs live check | Free hosted trial **must not receive private/confidential source** by default; sanitized/public invariants only |
| **Conditional** | **Google AI Studio/Gemini** (`google`, previously working API key reported) | Powerful free-tier models where enabled; exact project rate limits may be exhausted | Google's **unpaid** API terms allow product-improvement use and human review; no raw private ASES source by default |
| **Conditional** | **Cohere** (NEW, no observed account) | Evaluation-only API key, free up to **1000 calls/month** and typically 20 RPM per chat model | Confirm data-use terms and signup; not a substitute for production/privacy commitments |
| **Defer** | `mistral`, `hugging-face`, direct `deepseek`/`xiaomi-mimo`, `phoenix-grove`, newly discovered Cerebras/SambaNova/Ollama Cloud | Existing products either lack a verified free API entitlement or have payment/credit/privacy constraints. Mistral Free mode has no general API; Cerebras trial requires payment method; SambaNova docs conflict; Ollama Cloud now pay-per-token | Use only if actual verified account entitlement beats top routes; do not invent free credits |

**Family independence** means underlying model provenance, not provider reseller identity. A prior DeepSeek builder should not use DeepSeek as its only verifier; GLM, Kimi, MiniMax or Claude would provide better cross-family challenge. Static no-tools reviewers generate falsifiers but not executable proof.

## Executable review: eligibility-ranked candidates, not a fixed provider favorite

| Tier | Provider/account | Recorded state | Next measurement |
| --- | --- | --- | --- |
| **Proven baseline** | GitHub Actions (`github`) | `tool_observed`: a real ASES workflow ran on Nov 12, with actionable failed-test logs; quota/biller and arbitrary workflow trigger not yet validated | Actual workflow dispatch, source isolation, minutes/runner policy, model API secret path and output artifacts |
| **First sandbox comparison** | **Northflank** (`northflank`) | **Existing account user-confirmed Nov 13**. Manual-job API documented; actual plan/free jobs, card requirement and API access unverified | Read-only plan/entitlement check followed by a strictly bounded authorized job if known free/approved, with cleanup/receipts |
| **First sandbox comparison** | Modal (`modal`) | Existing account user-confirmed, local CLI previously worked; current Codex Cloud-to-Modal route/allowance unknown | Same small job as Northflank on measured startup, cost, cleanup and external-model support |
| **First CI comparison** | GitLab CI (`gitlab`) | User-reported account and prior CI experimentation; project API/quota unknown | Verify hosted runner minutes, Git access, pipeline trigger and result pickup |
| **Conditional existing** | GitHub Codespaces, Daytona, E2B, Vercel, Cloudflare Sandbox | Existing user/tool-reported account for the broader provider, but product-specific free execution not established | Product-specific quota/payment/remote launcher probe; Codespaces may suit persistent work more than one-shot tests |
| **Fast SSO signup candidates** | Other recorded discovery choices including Blaxel, Runloop, Fly, Render, Koyeb, Railway, CodeSandbox, Cursor, Replit, CircleCI/Buildkite/Azure DevOps, etc. | Many have no current recorded account, **not disqualified** | Determine which actually offer applicable free GitHub/Google SSO, without card or payment, plus an API launch mechanism; operator signup only if the measured option wins |
| **Constrained/deprioritized** | HOSTKEY VPS and generic paid VM trials | VPS sustained CPU limitation; offers unredeemed, no verified available balance | Use only if a bounded approved route is actually preferable; do not disrupt user backups |

Northflank and Modal are **peers to evaluate**, not a predetermined #1/#2. GitHub Actions' executed job proves runner use in the repo, not that it is always the fastest or cheapest execution provider. The complete provider catalogue remains in the 54-entry registry and should be screened without silently discarding new signup options.

## Source reference for newly discovered options

The detailed versioned provider screening, exact official URLs and privacy disqualifiers are in **PR #44** `research/provider-registry/reviewer-inference-screen-2026-11-13.md` v0.1.0. It distinguishes the 29 recorded accounts, six new unowned inference candidates, 60 total discovery providers and 26 unredeemed offer/comparator records. Model pricing and promotional free access are time-sensitive; recheck first-use availability.

## Execution policy

**First goal:** no extra cloud machine at all. Luna specifically tests **OpenCode Console free through its CLI inside Codex Cloud**, then uses the user's **already-paid Go** normal Flash models (or OpenRouter) rather than treating Go as an undiscovered entitlement with known free or authorized allowance and confirmed private-code data terms. The already-held NVIDIA key and Google's free API are **not** default private-source routes. A tiny nonsensitive capability check must precede real source packet submission. The reviewer returns falsifiers, not self-certification.

If the claim requires actual tests, use an independent Luna to turn findings into tests. GitHub Actions is a known runner baseline; **compare Northflank, Modal and GitLab CI** (plus suitable quick-SSO eligible candidates) on account-specific entitlement, one tiny reproducible launch, startup duration, review usefulness, model cost and cleanup before promoting any as the preferred sandbox. Signup is an operator action, not an automatic agent power.

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

**Unknown:** exact paid OpenCode Go tier/remaining allowance and whether OpenCode Console/Go credentials, OpenRouter, NVIDIA or Google keys are available in a **worker-approved** Codex Cloud execution environment; actual quota/credit; provider-specific model privacy; API egress; and executable sandbox readiness. The first Luna probe must answer those questions with exact tool and account evidence; do not overstate this report as a live capability test.
