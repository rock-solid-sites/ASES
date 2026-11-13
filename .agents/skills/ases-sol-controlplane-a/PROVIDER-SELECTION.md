---
title: "ASES reviewer provider selection from recorded accounts"
version: 0.2.0-experimental
status: ranked-preflight-required
authority: run-scoped-research
run_id: ASES-SOL-CTRL-A-20261113
source_inventory_ref: 5903b7b9ce3f1d9499a08f794775c3faf40a5d3d
review_date: 2026-11-13
---

# Select from the provider registry, not an arbitrary example list

**Decision:** For static falsification, test **the already-held NVIDIA NIM key and OpenRouter account with reported $5 monthly credits** before asking the operator to register elsewhere. For executable review, **GitHub Actions** supplies an observed baseline, but **Northflank, Modal, GitLab, and eligible free GitHub/Google SSO providers must compete on measured launchability, actual free quota, speed and total expense**—not an arbitrary existing-account shortlist. The operator can obtain eligible free SSO accounts in minutes; this makes signup a low-friction conditional route, **not** proof that any particular service offers SSO, free compute or no payment-card requirement. No provider has been launched by this document.

## What the inventory actually says

Pinned registry in `research/provider-registry/`:
- `known_accounts_v1.json`: **29 account records**, ranging from `tool_observed` or `user_confirmed` to `user_reported`. All have `usage.status=unknown`; none has a live remaining-balance observation.
- `candidate_inventory_v0.json`: **54 discovery providers**. All product routes remain unverified; Northflank is now independently user-confirmed as an **existing account**, while its manual-job/sandbox product entitlement remains unverified.
- `potential_offers_v1.json`: **26 offers/comparators**, with no verified current awarded/remaining promo balance. Do not treat prospective credits as available.
- PR #44 documentation describes 17 source-backed launch routes, all still `account_access=unverified`, `adapter_state=not_implemented` and `launch_test=not_run` in the discovery plane. This is not contradictory to observed GitHub Actions runs; it means no dedicated provider-registry adapter has been validated.

Ranking weighs (a) **verified effective cost and usable quota**, (b) model/executor suitability, (c) tested automation/launch path, (d) privacy and model provenance, (e) isolation and reproducibility, and (f) **realistic onboarding time**. Existing account access is an advantage but not a prerequisite: GitHub/Google SSO free signups can be completed quickly by the operator. Keep *account exists*, *account is quickly obtainable*, *product entitlement verified*, and *job launched* as separate evidence states. Absent quotas/costs are UNKNOWN, never $0.

## Tool-free external-family reviewer: qualified first probes

| Tier | Provider | Evidence from account registry | Practical action / unresolved gate |
| --- | --- | --- | --- |
| **First** | `nvidia` — NVIDIA NIM | **User-confirmed API key possession** (2026-11-13); actual model access and limits unknown | Luna checks whether key can be used *in the chosen executor* and pins a non-OpenAI reviewer model. **Do not ask again whether a key exists, store the value, or claim a successful call before testing.** |
| **First** | `openrouter` — OpenRouter | **User-confirmed account and $5 recurring monthly credits**; credited amount in the current period and balance unverified | Luna checks remaining credit/allowed model IDs and selects a fixed external-family model. $5/month is an **allowance claim**, not current spendable balance or infinite free inference. |
| **Second** | `google` — Google AI Studio/Gemini | Recorded user account; API project/key and free-tier entitlement unverified | Model/project-specific free tier could be suitable. A Google login is not itself a developer API key. |
| **Conditional** | `mistral`, `deepseek`, `xiaomi-mimo`, `opencode`, `hugging-face` | Mixed user-confirmed or user-reported accounts; API wallets/models not checked | Evaluate actual family, cost, API entitlement and privacy as alternatives. A model subscription and API billing are separate. |
| **Quick onboarding** | Other suitable external-family inference providers | Not necessarily existing accounts | **Do not automatically discard.** If the operator can open a genuinely free, applicable account with GitHub/Google SSO in minutes, include it in the shortlist after verifying service-specific SSO, payment and API conditions. |
| Less useful for this goal | OpenAI-family inference via `openai` | Existing product plan recorded | Provides less family independence for review of a Sol/Luna-produced change. |

**Model independence means actual underlying model family**, not just a distinct reseller. Pin provider-returned model/routing metadata, source SHA and packet digest; reviewer self-identification is insufficient.

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

## Execution policy

**First goal:** no cloud machine at all. Luna prepares a bounded blind review packet and probes the user-confirmed NVIDIA NIM key and OpenRouter account **in the environment where they will be used**, without assuming the credentials are already present there. Verify a small nonsensitive call under known free or approved cost, then dispatch a fixed-model critique. The reviewer returns falsifiers, not a self-certification.

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

**Unknown:** whether the already-held NVIDIA/OpenRouter credentials are present in an approved executor, current paid/free quota and remaining balance, provider-specific data retention, reviewer API ingress from Codex Cloud, external model entitlements, and which sandbox actually offers best usable free launch. The first Luna probe must answer those questions with exact tool and account evidence; do not overstate this report as a live capability test.
