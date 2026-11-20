---
name: review-launch
version: 1.0.4
description: Launch independent AI reviews with the smallest verified execution route, fixed source revision, explicit model and durable evidence.
status: current
---

# Independent ASES reviews

**Authoritative operational recipe (read fresh):**
`rock-solid-sites/ases-plugins/docs/INDEPENDENT-REVIEWER-WORKING-RECIPE.md` on `main`.
Separate Phoenix Grove provider configuration (**route evidence, not unlimited spend authorization**): `rock-solid-sites/ases-plugins/.github/reviewers/phoenix-grove.env.example`.
Historical route detail: `rock-solid-sites/ASES/docs/methodology/Agent Model Launch Routes.md` (dated; do not assume the old VPS is available).

## Mandatory model/billing admission

Before preparing or triggering any independent reviewer workflow, apply the current **ChatGPT coordination launch convention** and its **funding/entitlement types** in `skills/current/agent-launch/SKILL.md`. Declare the exact model/provider/account/funding route. **For OpenCode reviews**, eligible **Go subscription** and verified **zero-price Zen** remain approved; separately operator-approved NVIDIA, OpenRouter, Vercel or other API routes may also be used with an explicit bounded subscription, promotional/free-credit, purchased API-credit or free-tier entitlement. The presence of a key, credits, or a model in the catalog does not itself authorize spend. This OpenCode entitlement rule **does not ban Phoenix Grove**. **For separately authorized Phoenix Grove/Codex reviews**, pin the independent `pgs2` provider, exact PGS model, supported Codex CLI configuration, host, scoped authorization, runtime/allowance and `fallback: none`; verify provider credential presence and retain usage/cost uncertainty. Historical successful runs establish reachability, not unlimited spending permission. If the chosen route is unverified or unauthorized, stop before dispatch; do not silently switch models/providers. No invocation is necessary merely to test these instructions.

**Per-model and per-funding admission:** A mixed provider catalog (including OpenCode Go/Zen, NVIDIA, OpenRouter or Vercel AI Gateway) is never approved wholesale. Track the **selected funding source** separately from the model's price: (1) included subscription allowance, (2) purchased/prepaid API credits, (3) promotional/free credits, (4) genuinely free model/free-tier inference. A provider can offer several at once. Verify current entitlement, actual balance/limits, credit expiration, authorized budget and overflow/fallback behavior for the exact account/model/endpoint. Stop on unknown or automatic paid promotion; an authorized *bounded* prepaid-credit route is not equivalent to unapproved API spending. This does **not** revoke separately authorized Phoenix Grove PGS2 reviews or confer blanket authorization on any provider.

## Select the execution class

- **Bounded, read-only review:** GitHub Actions with a pinned repository commit/diff, one authorized model, a restrictive effective permission configuration, bounded CLI execution, validated nonempty report, and GitHub run summary. Use the existing working recipe, not a newly invented launcher. Run independent reviewers in isolated jobs; no automatic paid retries or silent model substitution.
- **Deep source/runtime investigation:** GitHub Codespaces, Modal, or another approved disposable environment when the agent needs to inspect a whole codebase, repeatedly run tests or reproduce a site/app bug. Keep source pinned, permissions appropriate to the target and effects bounded. Preserve verified checkpoints/commits and independent verification evidence. This is a placement guideline, **not** a claim that a generic deep-investigation launcher is deployed.

## Review execution

1. Specify the question, source repository, exact commit, relevant tests, desired independence and approved model/provider. Do not provide previous reviewers' verdicts as undisclosed anchors.
2. Before launching, read the current reviewer recipe and verify the selected workflow, available secret, runner, CLI, capability limits, and model route. Do not claim the three Phoenix Grove models work based solely on the older DeepSeek connectivity probe: the operator separately confirmed all three produced reviews on 2026-11-17; cite actual run evidence when available.
3. Read-only reviews must not run untrusted code or expose secrets to a model by default. Distinguish a prompt saying "do not use tools" from enforced deny-all permissions.
4. Bound runtime; classify zero-byte success, timeout, explicit errors and quota exhaustion as failed review. Keep partial/incomplete output separate from verified findings.
5. Preserve source SHA, model, workflow run, prompt/context hash where available, raw report, findings with falsifying tests, and honest limitations. Cost or provider token accounting is `unknown` unless verified.
6. Re-review changes only when warranted; submit material findings to concrete tests. Stop on failed credentials or depleted provider quota; request approval before fallback.

No GitHub, OpenCode Go or Phoenix Grove credentials should be copied into the skill. Never make an additional paid invocation solely to prove this document was read.
