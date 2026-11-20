---
name: review-launch
version: 1.0.2
description: Launch independent AI reviews with the smallest verified execution route, fixed source revision, explicit model and durable evidence.
status: current
---

# Independent ASES reviews

**Authoritative operational recipe (read fresh):**
`rock-solid-sites/ases-plugins/docs/INDEPENDENT-REVIEWER-WORKING-RECIPE.md` on `main`.
Established Phoenix Grove provider configuration for operator-requested reviews: `rock-solid-sites/ases-plugins/.github/reviewers/phoenix-grove.env.example` (example config only; credentials remain in GitHub Actions secrets).
Historical route detail: `rock-solid-sites/ASES/docs/methodology/Agent Model Launch Routes.md` (dated; do not assume the old VPS is available).

## Mandatory model/billing admission

Before preparing or triggering any independent reviewer workflow, apply the current **ChatGPT coordination launch convention** in `skills/current/agent-launch/SKILL.md`.

- **OpenCode Go/Zen routes:** only exact, approved Go-subscription model IDs or independently verified zero-price Zen model IDs; no unknown, paid, unapproved or default Go/Zen model, and no unapproved Extra Usage.
- **Phoenix Grove route:** **approved when specifically requested by the operator**, using the established `ases-plugins` independent-reviewer workflow and current Phoenix Grove credentials. Confirm the exact requested Phoenix Grove model, configured provider, permission boundary, job budget/allowance and intended output before launch. The CLI used for a Phoenix Grove review (Codex or OpenCode) does **not** turn that reviewer into an unauthorized Go/Zen model. Avoid automatic paid retries or model fallback; record an intermittent transport failure separately from model/prompt defects.
- **Codex Cloud Luna:** only through the authenticated ChatGPT Plus/Codex subscription, never an OpenCode Luna route or an inferred OpenAI API bill.

Do not invent or silently substitute a model, paid route, provider or host. Existing successful Phoenix Grove runs are useful technical evidence and do not constitute a categorical prohibition; they do not eliminate the need to verify conditions for the specific run. A model invocation is not needed to validate this policy.

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
