---
name: review-launch
version: 1.0.1
description: Launch independent AI reviews with the smallest verified execution route, fixed source revision, explicit model and durable evidence.
status: current
---

# Independent ASES reviews

**Authoritative operational recipe (read fresh):**
`rock-solid-sites/ases-plugins/docs/INDEPENDENT-REVIEWER-WORKING-RECIPE.md` on `main`.
Historical Phoenix Grove provider configuration (**not current spend authorization**): `rock-solid-sites/ases-plugins/.github/reviewers/phoenix-grove.env.example`.
Historical route detail: `rock-solid-sites/ASES/docs/methodology/Agent Model Launch Routes.md` (dated; do not assume the old VPS is available).

## Mandatory model/billing admission

Before preparing or triggering any independent reviewer workflow, apply the current **ChatGPT coordination launch convention** in `skills/current/agent-launch/SKILL.md`. For OpenCode review execution, select only an exact currently verified **OpenCode Go subscription** model or independently verified **zero-price Zen** model. Historical successful Phoenix Grove/paid-provider Actions runs demonstrate technical reachability, **not current spending authorization**. Do not select a default, paid provider, unknown model, free-sounding but unverified model, or fallback. If the subscription/free route is unavailable, stop before dispatch. A model launch is not necessary to test these rules.

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
