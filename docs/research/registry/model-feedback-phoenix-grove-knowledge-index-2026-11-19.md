---
title: Phoenix Grove Model Feedback - Knowledge Index Pilot 2026-11-19
program: EDASES
layer: Research
document_type: Research Record
status: Experimental
authority: Derived
canonical_repository: edases
depends_on:
  - AI Capability Registry Specification
related_documents:
  - adversarial-reviews/knowledge-index/2026-11-19-phoenix-grove-review.md
  - adversarial-reviews/knowledge-index/2026-11-19-postrepair-phoenix-grove-review.md
last_updated: 2026-11-19
---

# Phoenix Grove reviewer evidence — ASES knowledge index pilot

**Purpose:** a compact, empirical model-feedback entry from one source-pinned knowledge-index prototype review cycle. This is descriptive evidence for the [AI Capability Registry](AI%20Capability%20Registry%20Specification.md), **not** a new routing policy or review methodology. Each reviewer examined **different bounded sources and lenses**; comparisons are not controlled head-to-head model rankings.

## Source, review boundary and observed outcome

- Target: [ASES PR #61](https://github.com/rock-solid-sites/ASES/pull/61), initially reviewed at pinned commit `bef2782144ca5553b1632c6f0747169d5933e1ff`; subsequent three-model review pinned `2c7bdb2a624b53e41f08bf23dffe496e19d7e6e0`. Source excerpts were read-only, line-numbered, and bounded. The reviewer models did not execute regressions, and no hosted-service permissions were tested.
- First batch: [Phoenix Grove run 44577774247](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247): DeepSeek and GLM delivered substantive source-inspection findings. MiMo v2.6 timed out with no verdict; subsequent repeated same-prompt retries also timed out. A separate [focused MiMo run 44580649550](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580649550) delivered a substantive narrow security report. Do not count failed MiMo calls as independent verdicts.
- Fresh post-repair batch: [run 44586794355](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355): all **three** jobs delivered reports. DeepSeek and MiMo reported **no material findings in their respective bounded source packets**; GLM found two candidate defects. An agent then independently reproduced both in [failing regression run 44587686163](https://github.com/rock-solid-sites/ASES/actions/runs/44587686163), fixed them and verified [49/49 tests in run 44587792625](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625). The models were **not** asked to re-review those final repairs.
- Full unmodified reviewer bodies, invocation metadata, negative tests and triage: [initial record](../../../adversarial-reviews/knowledge-index/2026-11-19-phoenix-grove-review.md) and [fresh three-model record](../../../adversarial-reviews/knowledge-index/2026-11-19-postrepair-phoenix-grove-review.md). The evidence exists in the owning ASES repository; this entry does not copy entire transcripts.

## Per-model observations

| Requested provider model, reviewer lens | Observed capability | Limits and failure modes | Confidence |
| --- | --- | --- | --- |
| **Phoenix Grove `deepseek-v4.1-flash-1017`**, importer/identity correctness | Initial review identified code-path candidates including unsafe source-path selection, synthetic `meta:` visibility, reserved IDs and malformed input. Multiple were reproduced in independent regression tests and repaired. Fresh bounded source review delivered a no-material-findings verdict. | Initial exploratory output contained self-retracted guesses; final fresh inspection missed a later-discovered JSONL reserved-ID issue because task/source coverage was bounded. Do not present a clean scoped review as codebase-wide clearance. | **Emerging**, one experiment and a repeat source-pinned review |
| **Phoenix Grove `mimo-v2.6-flash`**, disclosure and graph-output safety | Successful focused review identified out-of-root JSONL ingestion (corroborating DeepSeek) and an unescaped Markdown authority field; these were subsequently tested and repaired. Fresh bounded security review delivered a no-material-findings verdict. | Original large prompt produced repeated **250-second timeouts and zero review outputs**. A reduced/specific source packet succeeded; causation (prompt size vs service intermittency) is **unverified**. No service-level ACL, revocation, browser execution or timing side-channel assurance was established. | **Emerging**, successful bounded reviews but observed invocation failures |
| **Phoenix Grove `glm-5.3-flash`**, architecture/integration | Initial review identified registry-missing behavior and evidence/provenance-design gaps. Fresh post-repair source reading identified a **confirmed JSONL reserved-ID impersonation** in partial indexes and a namespace-input validation issue. Both reproduced red then passed green. | A proposed no-slash namespace example was already rejected; a *different*, embedded-space case was confirmed. Some reported design gaps were future production gates, not defects of the disposable experiment. Model output is hypothesis generation, not approval. | **Emerging**, one experiment and a repeat source-pinned review |

## Review method and measurement limits

**Tool route:** Codex CLI in GitHub Actions configured for Phoenix Grove pgs2, each reviewer on an isolated model job, read-only checkout and source packet. The requested model IDs are in the workflow and logs; provider-side model identity was **not independently attested**. No authorized write to the reviewed checkout or production environment occurred. The exact provider billing, input/output/reasoning/cache token breakdown and authoritative USD charge were **unknown**, not zero; do not infer cost from GitHub minutes, response length or claimed subscription price.

**Useful transferable observations:**

1. Bounded independent source inspection can produce high-value **test hypotheses**, but source-reading alone does not prove a bug. The meaningful signal was a reproducing red test followed by a passing regression—not the model verdict or number of reviewers.
2. Reviewer assignments were intentionally different, so three model outcomes cannot support a model-ranking or an agreement percentage. In particular, a no-findings report is scoped, not an absence-of-defects proof.
3. Empty/timeout outputs are failed invocations, not negative findings. Keep provenance for each attempt, timeout and retry; focus reduction may be a practical recovery candidate but has not been causally evaluated here.
4. Preserve **one concise feedback record plus source-linked original reports** rather than duplicating full model outputs in routing matrices or session handoffs.

## Follow-up and authority

- **Projektor ASES-10** tracks the separate reusable reviewer-launch service and token/cost ledger. This experiment supplies requirements evidence, not authorization to build another launcher here.
- **Projektor ASES-19 / Work Notes WNASES-16** own the knowledge-index retrieval benchmark. The reviewer experiment is already concluded; do not relaunch these models merely for more agreement.
- The earlier DeepSeek v4 and MiMo v2.5 registry entries refer to **different model versions/routes** and must not have their historical confidence or costs silently overwritten by this Phoenix Grove v4.1/v2.6 observation.

**Disposition:** empirical model-feedback captured; suitable for future registry synthesis. No automatic routing rule or canonical methodology change.
