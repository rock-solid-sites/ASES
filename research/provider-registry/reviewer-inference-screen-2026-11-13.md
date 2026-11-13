---
title: "Cross-family static reviewer route screen"
version: 0.2.0-research
status: provider-research-no-live-inference-test
authority: derived
scope: ASES-owned code reviews
last_updated: 2026-11-13
supersedes: none
---

# Cross-family static reviewer screen (2026-11-13)

**Workload:** Sol/Luna-built ASES code review with frozen contract, pinned diff/selected source, adversarial falsification, and a bounded model output. This phase **does not need shell tools, a VM, GPU, Codex agent, or separate OpenCode cloud sandbox**. The Luna dispatcher gathers/filters source, calls another model family in a provider-approved fashion, and archives a raw review. Executable falsifiers run in a separate verifier.

## Database audit

- **29 known accounts**, now including user-confirmed Northflank, OpenRouter **$5 reported recurring monthly credits**, and an NVIDIA NIM API key. The current available credit/requests and credentials in Codex Cloud remain unknown. A user-reported account does not prove API entitlement.
- **60 discovery providers**, with six *new candidate entries* — Groq, Cohere, Z.ai, Cerebras, SambaNova, Ollama — and **no claimed signup or paid resource**. Unchanged **26 offers/comparators** have no verified awarded spendable credits.
- Relevant owned inference accounts: OpenCode (paid Go account confirmed, precise tier/remaining allowance and Codex Cloud credential access unknown), OpenRouter, NVIDIA NIM, Google AI Studio (user previously reported a working key with intermittent quota exhaustion), Cloudflare Workers AI (under existing Cloudflare account; product entitlement untested), Mistral, DeepSeek, Xiaomi/MiMo, Hugging Face, Phoenix Grove. User access to GitHub/GitLab/Northflank/Modal/E2B/Daytona/Vercel/Codespaces is relevant **only for executable review**, not static inference.
- Storage-only accounts IDrive/Box/Backblaze/MEGA/pCloud/TeraBox/iCloud and networking Tailscale are not new inference or runtime routes.

## Ranked static inference routes

| Candidate | Account state | Actual public entitlement / caveat | Decision |
| --- | --- | --- | --- |
| **OpenCode Go** | **Paid subscription operator-confirmed**; exact tier/remaining usage and Codex Cloud credential placement not verified | Go accepts coding-agent clients beyond OpenCode. The operator identifies affordable normal Go models **DeepSeek V4.1 Flash, MiMo V2.6 Flash and GLM-5.3 Flash**; these are paid-plan models, not Console free variants | **Fallback with existing allowance** if free Console-from-Codex route fails or is costly to bootstrap. Check model-family independence and remaining Go allowance, do not confuse with API wallet credits |
| **OpenCode Console free** | Existing OpenCode account; **Codex Cloud→OpenCode CLI launch is the unresolved experiment** | GLM-5.3-Flash Free, DeepSeek V4.1 Flash Free and MiniMax M3.1 Flash Free currently offered for limited time, documented zero-retention/no-training; **free chat endpoints require OpenCode CLI**, not arbitrary Codex API clients | **First focused capability test**: a Luna agent invokes a tool-disabled OpenCode CLI reviewer with one harmless tiny prompt, bounded usage, authorized auth/permissions; no shell delegation back to Sol |
| **OpenRouter** | User-confirmed existing account with claimed $5 monthly credits; *current* credited balance unknown | Many model families with exact pinned IDs, including paid Claude Sonnet 5.5 ($2/M input, $10/M output at checked date); free models have 50/day unless qualifying all-time purchases raise cap; `provider.zdr=true` can restrict provider retention | **Best high-capability independent escalation** using existing credit, if balance positive and routing to ZDR/nontraining endpoint verified |
| **Cloudflare Workers AI** | Existing Cloudflare account; Workers AI API token/key access unverified | Workers Free includes 10,000 neurons/day. Selected stronger DeepSeek/GLM/Kimi models require Paid or prepaid AI Gateway; free models must be selected by SKU | Good limited extra family if the chosen free model is strong enough |
| **NVIDIA NIM** | User-confirmed key exists | Free prototyping endpoint (rate limits often up to 40 RPM); **trial terms caution not to submit confidential source**; may log data for product improvement | Use for public/sanitized invariant review, **not default for raw private ASES code** |
| **Google AI Studio/Gemini** | User reported working key historically, may hit limits | Certain models free, project quotas variable; unpaid prompts can be used to improve products and read by human reviewers | **No raw private repository code** to free tier without explicit authorization; paid API may change data use terms |
| **Mistral, DeepSeek direct, Xiaomi/MiMo, Phoenix Grove, Hugging Face** | Existing account claims, specific API/plan/current quota unknown | Mistral Free mode has no general developer API without pay-as-you-go; HF Free inference credit is inconsistently documented across provider pages; other accounts may require paid API plan or have data restrictions | Not first use; inspect account-specific meters before asserting a free route |
| **Groq** | NEW discoverable free signup; account **not observed** | Free API, e.g. Qwen3.8-27B with 30 RPM/1000 RPD but 8k TPM, limiting large source packets; zero-data-retention controls available | **Best low-friction NEW no-card alternative** for small segmented source packets |
| **Z.ai** | NEW discoverable free signup; account **not observed** | Official GLM-4.7-Flash input/output free, 200k context; exact account throttling/data terms require check | Promising NEW direct API for substantial code packets, pending privacy/route preflight |
| **Cohere** | NEW discoverable trial signup; account **not observed** | Evaluation keys free with 1000 calls/month and 20 RPM chat, evaluation-only; data policy differs from paid | Evaluation-only fallback when terms fit; not raw private default without privacy check |
| **Cerebras / SambaNova / Ollama Cloud** | Not recorded as existing accounts | Cerebras now requires verified payment method for $5/30-day trial; SambaNova free docs conflict with plans requiring credits; Ollama Cloud pricing currently pay-per-token, no verified ongoing no-cost quota | **Defer**; user already has more capable/reliable free or included alternatives |

## Priority clarification: free OpenCode models *inside Codex*

The operator's main request is to test access to **OpenCode Console free models from within Codex Cloud**. The fact that the operator has paid Go is already established. Do not spend time rediscovering Go or treat the normal paid-plan Flash models as free. The strictly delegated probe is: Luna checks CLI availability and authorized login, launches an OpenCode CLI agent with tools disabled and a fixed Console free model on a harmless prompt, records API/model route and cost/usage; if impossible, returns one short failure report and switches to existing Go **DeepSeek V4.1 Flash / MiMo 2.6 Flash / GLM 5.3 Flash** based on available Go quota, not another long environment-provisioning detour. Do not conflate host Codex's native subagents with a separately launched OpenCode client.

## Cost example (illustrative)

One static challenge of **20,000 input + 4,000 output tokens** with **Claude Sonnet 5.5 via OpenRouter** at the published $2/M input and $10/M output rates would consume **about $0.08** of OpenRouter model credits (before any routing changes, taxes, provider-specific fees, retries or hidden reasoning tokens). This is a *pricing illustration*, NOT an observed debit or guarantee of current monthly $5 credit availability. A cheap GLM/DeepSeek/MiniMax free reviewer can run first; a Claude-family critique can be reserved for high-value integration/authority disputes.

## Verification model

Sol freezes claim, success/refusal requirements and critical falsifiers BEFORE builder work. Builder Luna returns its results; independent tool-free reviewer receives frozen claim and only necessary source, but not builder narrative/green history, and generates counterexamples. Verifier Luna then turns material counterexamples into executable tests with hashes and negative controls; Sol judges ACCEPT / REVISE / UNVERIFIED from both source-pinned reports. Tool-free model critique is not a proof of executable behavior and does not replace cross-runner CI.

## Admission and privacy checks

At launch, Luna must verify (1) exact provider account/plan and usable *current* quota/credits; (2) authorized secret placement and API/CLI access inside the actual Codex Cloud worker environment; (3) fixed model identity/family from provider metadata; (4) model/input privacy settings appropriate to private repository code; (5) small nonsensitive smoke call with receipts, latency and observed cost; (6) no unlimited retries, no provider/model silent fallback; (7) log source packet hashes, reviewer output and real cost in Work Notes. Free SSO account signups are low friction but require operator authorization, and must not be represented as already owned. No actual invocation was made in this research sweep.

## Current official sources

- OpenCode Console and free/no-training models: https://opencode.ai/docs/console/models/
- OpenCode Go and supported agent clients: https://opencode.ai/docs/console/go/
- OpenCode CLI tool-disabled agent: https://opencode.ai/docs/agents/ and https://opencode.ai/docs/cli/
- OpenRouter limits: https://openrouter.ai/docs/api_reference/limits
- OpenRouter ZDR: https://openrouter.ai/docs/guides/features/zdr
- OpenRouter Claude Sonnet 5.5 pricing: https://openrouter.ai/compare/anthropic/claude-sonnet-5.5/minimax/minimax-m3.1-flash
- NVIDIA NIM free trial: https://build.nvidia.com/search
- Gemini API unpaid privacy: https://aistudio.google.com/docs/terms
- Cloudflare Workers AI free neurons: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Groq rate limits and ZDR: https://console.groq.com/docs/rate-limits and https://console.groq.com/docs/your-data
- Cohere trial: https://docs.cohere.com/docs/rate-limits
- Z.ai Flash free: https://docs.z.ai/guides/overview/pricing
- Cerebras trial: https://cerebras-inference.mintlify.app/support/rate-limits
- SambaNova contradictory free: https://cloud.sambanova.ai/plans and https://docs.sambanova.ai/docs/en/models/rate-limits
- Ollama Cloud paygo: https://ollama.com/pricing
- Mistral API free restriction: https://docs.mistral.ai/admin/billing-usage/usage-limits
- GitHub Models retired 2026-07-30: https://docs.github.com/en/github-models
