---
title: Minimal Assurance Counterexample Index — November 2026
program: EDASES
layer: Research
document_type: Registry
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - testing/experiments/2026-11-cross-project-pilot.md
last_updated: 2026-11-19
---

# Minimal counterexamples, not duplicated test suites

This is a **locator index** for reproducible discriminating cases whose code and raw evidence remain in their owning repositories. A failing case is not necessarily a product defect. Each entry identifies the real/test-only object and the independently observed classification.

| ID | Case / smallest claim to discriminate | Classification | Replay/evidence pointer |
| --- | --- | --- | --- |
| CE-001 | HMS 1 minor unit, frozen 1/3 FX ratio: compare `-0` versus `0` in sign-symmetry oracle | **REJECTED_ORACLE**; no product defect established | [Original failure CI](https://github.com/rock-solid-sites/HMS/actions/runs/44440078585), [corrected replay](https://github.com/rock-solid-sites/HMS/actions/runs/44440191933), [fixture/seed path](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-hms-20261119/research/property-testing/OBSERVATION-FINANCE-2026-11-19.md) |
| CE-002 | Experimental SQLite payment with frozen FX, reopen: persisted payment omits original FX evidence | **CONFIRMED_CANDIDATE_DISCREPANCY**, fixed on draft branch | [Expected-red CI](https://github.com/rock-solid-sites/HMS/actions/runs/44454132005), [red→green PR](https://github.com/rock-solid-sites/HMS/pull/23), [owner report](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-sqlite-repairs-20261119/research/property-testing/OBSERVATION-FINANCE-REPAIR-2026-11-19.md) |
| CE-003 | Experimental SQLite `throw-after-commit`: reopen proves paired durable effect but caller received `ok:false` | **CONFIRMED_CANDIDATE_DISCREPANCY**, fixed on draft branch; response vs effect | [Expected-red CI](https://github.com/rock-solid-sites/HMS/actions/runs/44455709255), [repair red CI](https://github.com/rock-solid-sites/HMS/actions/runs/44459787811), [green CI](https://github.com/rock-solid-sites/HMS/actions/runs/44460235430) |
| CE-004 | Shipped Trip'n booking JS: search four adults, choose three dorm beds, legacy cart handoff encodes three | **SHIPPED_SOURCE_DISCREPANCY**; no deployed repair | [Source/negative tests](https://github.com/TripN-Chill-Zone/tripn-astro/blob/experiment/ases-booking-contract-20261119/docs/assurance/2026-11-19-chill-zone-booking-contract-pilot.md), [known-bad controlled CI](https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/44465080572) |
| CE-005 | Dorm 567219, Nov 20–22: public same-stay offer €30 for 1 adult versus €120 for 4; legacy quote displayed/multiplied as per-bed | **NARROW EXTERNAL-CONTRACT OBSERVATION + SHIPPED SOURCE MECHANISM**; full hosted checkout not verified | [Request/response evidence](https://github.com/TripN-Chill-Zone/tripn-astro/blob/experiment/ases-booking-contract-20261119/docs/assurance/2026-11-19-chill-zone-booking-contract-pilot.md), [draft adapter tests](https://github.com/TripN-Chill-Zone/tripn-astro/pull/30) |

| CE-006 | Paseo owned agent configured `thinking:none`; identical inspected agent reports `Thinking:low`, yet bridge `status` initially succeeds | **CONFIRMED SOURCE VALIDATION GAP**, patched in draft; live CLI missing-field behavior unverified | [Expected-red CI](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570572887), [green CI](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570781671), [owner PR #77](https://github.com/rock-solid-sites/ases-plugins/pull/77) |

## Reproduction rule

Open the **owner report** and pin its commit/branch before running anything. Replay the smallest existing test plus at least one control, confirm expected failing marker or semantic output, then run the recorded corrected variant if one exists. If source, dependency lock, provider state or CI is unavailable, classify `BLOCKED` or `INCONCLUSIVE` instead of copying the reported result as a new observation.

Never execute a production write, payment, reservation or other third-party side effect merely to reproduce an old report. ASES only stores the method lesson and pointer; owner repositories retain the actual test harness and test-output details.

**Known limits:** these five examples are **not** a complete mutation corpus, a universal set of guarantees or proof of which testing framework is best. Additional counterexamples should only be indexed when they reveal a distinct reusable failure class.
