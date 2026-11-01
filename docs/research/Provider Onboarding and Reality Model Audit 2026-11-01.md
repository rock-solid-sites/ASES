# Provider onboarding and reality-model audit — 2026-11-01

**Status: provisional research design.** No scheduler or provider integration is declared production ready.

## Core correction

Providers are not interchangeable machines. Separate provider, product, account/entitlement, execution surface, environment instance, supported configuration, model route, quota meter, billing cycle, policy, and runtime observations. A job may simultaneously consume multiple independent meters: e.g. Codespaces compute-hours, Codespaces storage GB-hours, and a separate inference provider allowance. Never substitute units or accounts implicitly.

## Official documentation reviewed (2026-11-01)

- Codex Cloud: https://help.openai.com/en/articles/20001545-using-codex-cloud ; https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- Codespaces: https://docs.github.com/en/billing/concepts/product-billing/github-codespaces ; https://docs.github.com/en/codespaces/setting-your-user-preferences/setting-your-timeout-period-for-github-codespaces
- GitHub Actions: https://docs.github.com/en/billing/concepts/product-billing/github-actions ; https://docs.github.com/en/actions/concepts/billing-and-usage
- Workers: https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/workers/platform/pricing/
- Pages: https://developers.cloudflare.com/pages/platform/limits/

## Reality gaps by product

**Codex Cloud**: managed, isolated tasks; no separate standard cloud VM charge at launch; model usage counts toward Codex allowances, which can be shared with other ChatGPT product surfaces. Model availability depends on plan, settings, rollout and selected task environment. No right to choose arbitrary VM sizes or model capabilities. Published environment updates apply to new tasks; existing tasks retain state. Saved VM state generally recoverable for up to seven days. Distinguish published environment template from individual task workspace. Do not assume exact available models, remaining limits, concurrency or hardware without account observation.

**GitHub Codespaces**: discrete machine types; compute measured as active instance time and weighted by core count; storage separately measured in GB-hours even while not actively computing. Personal GitHub Free includes 120 core-hours and 15 GB-month, Pro 180 core-hours and 20 GB-month; organization plans have different treatment. Default idle timeout 30 minutes, configurable 5–240 minutes; maximum lifetime 12 hours. Prebuilds also consume Actions compute. A Codespace provides execution but **not** an AI model allowance; OpenCode, API or other model routes charge their own provider/account budgets. Owner of repository and billing account must be resolved separately. Pausing, deleting and resizing have distinct accounting consequences.

**GitHub Actions**: ephemeral runners and job executions, not continuously available shared machines. Standard runners in public repositories are free; private repositories draw from plan-specific included minutes and storage. Larger runners charged even for public repositories. Billing owner, runner OS/SKU, job time, artifact retention, cache and workflow concurrency are distinct. Prebuilds and reusable workflows introduce cross-product billing relationships. Do not model Actions as a persistent VPS or assume a running job can host unrelated sessions.

**Cloudflare Workers**: event-driven isolates, not ordinary VMs. Free requests 100,000/day reset at midnight UTC, CPU per request 10 ms, 128 MB memory; paid model includes monthly requests and CPU milliseconds, with separate per-invocation limits. CPU time excludes waiting on network I/O; wall-time limits depend on invocation type (HTTP, cron, queue, etc.). Pages Functions consume Workers allowances. R2, KV, D1, Durable Objects, Queues and Workers Builds each require product-specific meters/constraints, not one generic Cloudflare balance. Free Worker route fail-open behavior may bypass code; security-sensitive workloads require explicit fail-closed policy.

**Cloudflare Pages**: builds/month, build concurrency, 20-minute build timeout, file/project limits; Free includes 500 builds/month and one concurrent build. Pages Functions count toward Workers. Pages build compute is not interchangeable with Workers invocation CPU.

**VPS/local machines**: fixed or provider-supported resize options, paid lease time, storage and traffic rules, background OS consumption, actual contention, uptime and access policy. CPU is shared and oversubscription is not automatically invalid. Memory/disk headroom and throttling require runtime measurements.

## Provider onboarding contract (provisional)

1. **Identity**: stable provider/product/account IDs, ownership, payer, workspace/repository eligibility, region and credential scopes.
2. **Execution semantics**: persistent/ephemeral/event-driven/managed-agent; launch, pause, resume, resize, stop, retention, max lifetime, job duration, network and filesystem constraints.
3. **Discrete configurations**: enumerate allowed machine/runner types or explicitly mark opaque managed compute; never invent CPU/RAM values.
4. **Capability routes**: languages, tools, repositories, network access, model families, reasoning options and allowed task types; record capability version and observation time.
5. **Meters**: typed quantity, billing owner, product, unit, reset timezone and cadence, hard/soft limits, reserve, prepaid/postpaid and pricing; explicitly declare which operations debit which meters.
6. **Cross-product dependencies**: e.g. Codespaces + external model provider; Pages Functions + Workers; Codespaces prebuild + Actions; separate quotas remain separate even when the same vendor bills both.
7. **Observability**: provider-reported balance/usage, refresh time, confidence, stale-data policy, settlement event IDs, discrepancy handling, and forecast error.
8. **Lifecycle**: proposed -> verified -> active -> degraded -> draining -> retired; removal must preserve historical ledger IDs, active commitments and audit records. Re-onboarding increments capability revision, never silently reuses a changed entitlement.
9. **Admission**: bind immutable provider catalog revision, current account entitlements, selected configuration, policy and all quota claims atomically; reject unknown capabilities or insufficiently fresh observations.
10. **Testing**: contract fixtures from documentation, red-green invalid/valid boundary pairs, mutation kills, provider-specific accounting examples, restart/concurrency, catalog change, provider loss and re-entry, model withdrawal, quota reset and cross-product consumption.

## Critical design rules

- Separate **hard upper bounds** (unsupported models, unavailable configurations, per-invocation CPU limits, account quotas) from **soft performance predictions** (CPU contention, throughput, queueing).
- A provider's published quota is not proof of the user's current remaining allowance or eligibility.
- Never equate wall-clock runtime, billed compute time, CPU milliseconds, token consumption and model request counts.
- A job's feasibility is the intersection of **execution surface**, **model route**, **account authorization**, **time window**, **environment configuration**, **all dependent meters**, and **policy**.
- Distinguish provider-declared constraints from observed operational performance and locally assumed estimates; mark unknowns explicitly.
- No automatic paid overage or credential sharing; permission to borrow an account's entitlement must be explicit and independently auditable.

## Recommended next build sequence

Create versioned provider manifests and an independent manifest validator first. Add fixtures for Codex Cloud, Codespaces, Actions, Workers, Pages and the existing VPS, with unknown account-specific values marked unresolved. Test catalog lifecycle and multi-meter claims using synthetic provider observations. Only then adapt SQLite gate and planner to this normalized model; preserve existing tests as historical checks against the earlier assumptions.

This is a modeling specification, not a claim that all actual account quotas, configurations or model lists have been verified.
