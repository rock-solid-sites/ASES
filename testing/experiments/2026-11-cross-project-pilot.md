---
title: November 2026 Cross-Project Assurance Pilot — Bounded Experiment
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - testing/README.md
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
related_documents:
  - testing/lessons/2026-11-cross-project-lessons.md
  - testing/counterexamples/README.md
last_updated: 2026-11-19
---

# Cross-project pilot: test the assurance process, not just the software

**Question:** Does a claim-first, cheapest-discriminating-test approach with generated histories, negative controls and selectively independent review produce defensible extra evidence across different software objects? **Status:** bounded observations, not a measured general improvement, not an approved method.

## Discriminating observations

| Context and object | Added evidence | Independent boundary and limitation |
| --- | --- | --- |
| HMS real finance domain, [draft PR #21](https://github.com/rock-solid-sites/HMS/pull/21) | Generated payment/refund/FX/snapshot histories; minimized signed-zero failure proved an **oracle mistake**, not a product defect. [Initial fail CI](https://github.com/rock-solid-sites/HMS/actions/runs/44440078585); [corrected green CI](https://github.com/rock-solid-sites/HMS/actions/runs/44440191933) | Domain functions and synchronous session snapshot port only; no live storage, multi-tenant or settlement proof. [Owner evidence](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-hms-20261119/research/property-testing/OBSERVATION-FINANCE-2026-11-19.md) |
| ASES actual Rust/SQLite resource Store, [draft PR #59](https://github.com/rock-solid-sites/ASES/pull/59) | Independent budget oracle and generated reservation histories against actual `Store::reserve`, persistence/reopen, rejection and replay | Bounded histories; concurrency, complete failure space and comparative framework efficiency unproven. PR is a descendant research branch, not mainline |
| HMS **new** test-only SQLite finance candidate, [draft PRs #22–23](https://github.com/rock-solid-sites/HMS/pull/23) | Separate-process races and SIGKILL, negative orphan-row control; reviewer-inspired FX loss and post-COMMIT false response, both **expected-red before repair** ([CI](https://github.com/rock-solid-sites/HMS/actions/runs/44459787811)); [18/18 green](https://github.com/rock-solid-sites/HMS/actions/runs/44460235430) | Real SQLite *candidate wrapper*, NOT HMS production finance, D1, provider receipts or permissions. [Owner repair evidence](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-sqlite-repairs-20261119/research/property-testing/OBSERVATION-FINANCE-REPAIR-2026-11-19.md) |
| Phoenix Grove independent code review on frozen HMS candidate | Two independently reproduced candidate findings; false positive and source-misread claims rejected. First MiMo attempt timed out; separately authorized retry delivered a report. [Reviewer synthesis](https://github.com/rock-solid-sites/ases-plugins/blob/review/hms-sqlite-finance-pgs2-20261119/docs/reviews/results/20261119-hms-finance-sqlite-pgs2/SYNTHESIS.md) | Three delivered reports across **four invocations**; no models executed source; GLM output truncated; token/billing totals unknown |
| Trip'n actual shipped legacy booking bundle and experimental Astro wrapper, [draft PR #30](https://github.com/TripN-Chill-Zone/tripn-astro/pull/30) | Known-bad 4-searched/3-selected handoff; actual read-only public offer quotes €30 for 1 adult and €120 for 4 adults (two nights, 2026-11-20–22, room 567219). 16/16 source tests pass ([CI](https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/44465080572)). | Verified *narrow* external quote semantics; no browser/CSP/hosted Beds24 parity, deployment or paid booking verification. [Owner evidence](https://github.com/TripN-Chill-Zone/tripn-astro/blob/experiment/ases-booking-contract-20261119/docs/assurance/2026-11-19-chill-zone-booking-contract-pilot.md) |

## Reusable conclusion within these samples

- **Supported:** source-derived claims can be translated into independently falsifiable cases; generated histories and real persistence expose different risks; human-screened model review can find gaps that a first harness missed; external observation can correct a previously assumed oracle.
- **Also observed:** a compelling minimized failure can be the *test's* mistake; a source-correct finding does not imply deployed impact; passing controls show sensitivity only to those injected violations. A model that exited successfully can still invent code paths.
- **Not established:** universal superiority over conventional deterministic tests, Hegel versus proptest performance, production finance/checkout assurance, full interleaving coverage, statistically meaningful marginal value/cost, or repeatable cross-team adoption.

**Next decisive evaluation:** independently critique the [selection candidate](../methods/selection-candidate.md) and apply it to a different high-consequence object whose most likely failure and cheapest test are not known in advance. Pre-register a deterministic baseline, explicit coverage/risk delta, verification cost, false positives and abandonment condition. If no useful delta appears, simplify or reject the candidate rather than growing the process.

Primary comprehensive research remains the [ASES cross-project pilot in draft PR #58](https://github.com/rock-solid-sites/ASES/pull/58); this page is a compact *decision-oriented index*. Project-specific code and detailed evidence stay with their owners. Work Notes `WNASES-10` tracks independent review; `WNASES-14` tracks this folder.
