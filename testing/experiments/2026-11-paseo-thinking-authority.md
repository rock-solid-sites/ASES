---
title: Paseo Runtime Thinking-Mode Authority — Transfer Experiment
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - testing/README.md
related_documents:
  - testing/methods/selection-candidate.md
  - testing/lessons/2026-11-cross-project-lessons.md
last_updated: 2026-11-19
---

# Transfer experiment: runtime authorization versus configured launch intent

**New target:** [Paseo control bridge](https://github.com/rock-solid-sites/ases-plugins/tree/main/connectors/paseo-control) in `rock-solid-sites/ases-plugins`, original source commit `20d81f339ec3731df02824ee2e89bba400f1be6d`. This is neither the ASES Rust resource solver, HMS finance nor Trip'n booking code.

## Claim, baseline and discriminating test

**Claim under examination:** once a bridge has recorded an agent's approved role, subsequent status and follow-up operations must not silently accept an inspected runtime `Thinking` value conflicting with the role's configured `thinking` mode. This is important for permission/model-route identity and authorized inference settings.

The existing [Paseo tests](https://github.com/rock-solid-sites/ases-plugins/blob/20d81f339ec3731df02824ee2e89bba400f1be6d/connectors/paseo-control/bridge-core.test.mjs) checked workspace, provider and model identity, role revocation, locks and archival evidence, but `checkOwnedSnapshot` did not compare the normalized `thinking` field with `record.thinking`.

**Independent control:** create a bridge with an isolated fake CLI; valid reported `Thinking:'none'` must pass. Flip *only* the observed `Thinking` to `low` for the same agent, workspace, provider and model; require both status and follow-up to reject without sending an instruction. No real provider CLI, VPS or paid model call.

## Executed evidence and result

- [Owner draft PR #77](https://github.com/rock-solid-sites/ases-plugins/pull/77), initial test-only commit `f1584c25b9083eac5dd3aac71dfaf709dd5bb193`. [Expected-red CI 44570572887](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570572887) ran 18 Node tests: **17 passed, one failed**, specifically the new check with `Missing expected rejection`. This establishes a real *bridge validation gap under explicit mismatched inspect data*, not necessarily a provider-side misconfiguration.
- Minimal change at commit `a2eabdf4b8bd0f20617d00db6693280aeae4fa32`: `checkOwnedSnapshot` rejects non-null inspected `thinking` when it differs from the approved ownership record. No product-facing deployment. [Green CI 44570781671](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570781671) ran **18/18 Node tests** and the fake-CLI MCP protocol smoke successfully.
- Owner's implementation remains a **draft/unmerged** PR; result applies to the current code branch and test doubles, not live production behavior.

**Outcome:** `CONFIRMED_DISCREPANCY` in source-level authorization validation under an explicitly reported mismatch; `REPAIRED_IN_DRAFT` with reproducible red→green evidence.

## What the testing method gained

The extra test was a *single* targeted state comparison, not a generalized property-testing engine. The consequential invariant was **observed runtime mode must match configured/owned authority**. The paired controls changed only one semantic property and exposed a gap missed by a larger existing green suite. This supports retaining cheap independent negative controls before escalating to more expensive generation or multiple reviewers.

**Limits / WHAT-NOT-TESTED:** The original CLI `run` output may omit thinking mode, and the current patch only checks an explicit non-null inspected mode; absence of the `Thinking` field still cannot establish compliance. No real running Paseo instance, actual remote launch, cross-process race, service trust boundary or production/installation was tested. The broader policy for missing/ambiguous inspect fields requires separately qualified decisions and upstream CLI contract checks. Do **not** label this complete runtime authority enforcement.

## Independent Phoenix Grove review (three attempts, only one valid report)

[Three-job run 44575756540](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44575756540), source SHA `a2eabdf4b8bd0f20617d00db6693280aeae4fa32`, used a frozen clean-room packet and one `pgs2` invocation each of DeepSeek, GLM and MiMo. The [full source-screened synthesis](https://github.com/rock-solid-sites/ases-plugins/blob/review/paseo-thinking-pgs2-20261119/docs/reviews/results/20261119-paseo-thinking-pgs2/SYNTHESIS.md) remains with the code owner.

- **DeepSeek** produced one substantive report. Source screening confirms the explicit missing-thinking-field gate permits unverified mode and `validateLaunch` ignores returned model/mode. These are *source validation gaps*, not proven live CLI substitutions. Activity freshness and external TOCTOU are plausible but remain unexecuted hypotheses.
- **GLM** reached the provider but its 1,754-byte response failed the substantive review gate and claimed code changes/tests that were not performed. **No valid review verdict.**
- **MiMo** reached the provider but returned zero review bytes after an SSE idle disconnect, exit 1. **No verdict.** No retries were authorized or performed.

**Method lesson:** Three reviewer *invocations* are not three independent *findings*. The correct accounting is **1 validated report / 3 attempts**, with conclusions additionally screened against source and then requiring executable discrimination. Reuse existing [lesson L05](../lessons/2026-11-cross-project-lessons.md) rather than creating a duplicate rule. Provider billed amount/tokens unknown; read-only sandbox is not independently verified deny-all.

**Next independent assessment:** a reviewer should verify real Paseo inspect-field presence and semantics, decide the appropriate fail-closed behavior for missing values, and test a second authorization dimension with a distinct fixture or real isolated CLI when approved. Method promotion remains gated by Work Notes `WNASES-10`; execution pilot `WNASES-15`.
