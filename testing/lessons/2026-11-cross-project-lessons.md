---
title: Transferable Testing Lessons — November 2026 Pilots
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - testing/experiments/2026-11-cross-project-pilot.md
related_documents:
  - testing/methods/selection-candidate.md
  - testing/counterexamples/README.md
last_updated: 2026-11-19
---

# Lessons that change the next test

Each entry states a **failure class → changed practice → evidence → transfer limit**. These are bounded empirical learnings, not mandatory ASES-wide policy. Keep the smallest independent reproduction and decision rather than the chronological history of attempts.

### L01 — The oracle itself can be wrong

**Failure class:** Generated HMS FX sign-symmetry produced a minimized 1-unit, 1/3-rate mismatch solely because the test expected `-0` and the implementation returned `0`.

**Changed practice:** Before modifying source, inspect the minimized case for a false requirement, representation equivalence or invalid fixture. Maintain deliberate good/bad controls and preserve `REJECTED_ORACLE` as a successful research outcome.

**Evidence:** [HMS original failure](https://github.com/rock-solid-sites/HMS/actions/runs/44440078585), [corrected replay](https://github.com/rock-solid-sites/HMS/actions/runs/44440191933), [source record](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-hms-20261119/research/property-testing/OBSERVATION-FINANCE-2026-11-19.md).

**Limit:** No HMS production defect was demonstrated by this case. Shrinking cannot validate the claim it was given.

### L02 — Green generated tests can be vacuous

**Failure class:** A generator can run hundreds of cases while rarely or never exercising disputed paths.

**Changed practice:** Require named semantic classes (accepted/rejected/refund/replay/wrong-property/stale/reopen) and nonzero exercise of classes needed for the claim; count transitions, not just test cases. Use explicit known-bad controls.

**Evidence:** [HMS finance observation](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-hms-20261119/research/property-testing/OBSERVATION-FINANCE-2026-11-19.md) and [locked-install CI](https://github.com/rock-solid-sites/HMS/actions/runs/44441390129).

**Limit:** Counts and fixed seeds do not prove completeness or control concurrent scheduling.

### L03 — A committed effect is not an acknowledgment

**Failure class:** A transaction can commit and then return a false failure, or commit before the process dies without delivering a response.

**Changed practice:** Test storage effects, process exit windows, caller-visible result and exact-payload retry semantics separately. Reopen real storage after SIGKILL; distinguish before/after COMMIT. Never treat wrapper response as the only oracle.

**Evidence:** [HMS expected-red](https://github.com/rock-solid-sites/HMS/actions/runs/44455709255), [repair red→green](https://github.com/rock-solid-sites/HMS/pull/23), [repair report](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-sqlite-repairs-20261119/research/property-testing/OBSERVATION-FINANCE-REPAIR-2026-11-19.md).

**Limit:** Experiment used a new file-backed SQLite finance *candidate*, not real HMS D1/processor settlement.

### L04 — Exact evidence provenance matters across storage boundaries

**Failure class:** The candidate persisted payment and ledger rows but discarded FX provenance when reopening a payment; an isolated negative control exposed orphan-ledger vulnerability under direct SQL.

**Changed practice:** Assert preservation of decision evidence, not just numerical balance. Pair records under actual transactional authority, inject corruption/abort, and verify observed state after reopening. Test both payment and refund failure windows.

**Evidence:** [FX expected-red](https://github.com/rock-solid-sites/HMS/actions/runs/44454132005), [HMS correction and limitations](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-sqlite-repairs-20261119/research/property-testing/OBSERVATION-FINANCE-REPAIR-2026-11-19.md).

**Limit:** Positive wrapper checks do not prohibit bypassing that wrapper or establish tenant permissions, schema constraints, D1 semantics or provider authority.

### L05 — A model report is not a verified review finding

**Failure class:** Phoenix Grove returned plausible but false code interpretations; GLM report was truncated; an initial MiMo invocation timed out. Later MiMo independently identified a separately falsified post-COMMIT result bug.

**Changed practice:** Track transport, complete retained output, factual source support and independently executable falsification independently. Freeze source packets, record rejected claims, require explicit retry authorization and preserve *failed* invocations in budget accounting.

**Evidence:** [reviewer synthesis](https://github.com/rock-solid-sites/ases-plugins/blob/review/hms-sqlite-finance-pgs2-20261119/docs/reviews/results/20261119-hms-finance-sqlite-pgs2/SYNTHESIS.md), [MiMo retry run](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44454971218).

**Limit:** Three delivered reports required four calls; provider tokens/cost unknown. Model diversity alone does not provide independence or correctness.

### L06 — An assumed external quote must become an observed contract

**Failure class:** Trip'n's legacy client treated a group-stay dorm quote as a per-bed rate, while its cart could send fewer guests than searched.

**Changed practice:** Establish price basis, count and stay interval from actual read-only provider-backed observations before encoding a price oracle. Track search→selection→handoff identity separately, then test the actual browser/provider boundary before allowing paid traffic.

**Evidence:** [Trip'n scoped report](https://github.com/TripN-Chill-Zone/tripn-astro/blob/experiment/ases-booking-contract-20261119/docs/assurance/2026-11-19-chill-zone-booking-contract-pilot.md), [protected source CI](https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/44465080572), [draft repair](https://github.com/TripN-Chill-Zone/tripn-astro/pull/30).

**Limit:** Room 567219 EUR quotes for 2026-11-20–22 do **not** define every Beds24 offer's pricing contract. UI unit tests do not prove hosted checkout parity; production remains unverified.

### L07 — Evidence survival is a separate verification dimension

**Failure class:** GitHub Actions artifact quota prevented ZIP upload; initially missing npm lock evidence and temporary CI output could undermine reproducibility despite a green test.

**Changed practice:** Pin source, dependencies and seed; preserve the minimal replay and negative evidence under approved durable storage, independent of transient CI artifact quotas. Audit observed workflow result separately from artifact archival result.

**Evidence:** [HMS locked-install verification](https://github.com/rock-solid-sites/HMS/actions/runs/44441390129) and [owner's evidence discussion](https://github.com/rock-solid-sites/HMS/blob/experiment/assurance-finance-hms-20261119/research/property-testing/OBSERVATION-FINANCE-2026-11-19.md).

**Limit:** Source pin + lock + seed improve replayability but do not freeze entire runner images or nondeterministic process schedules. Avoid bulk historical retention when a compact counterexample is sufficient.

### L08 — Preserve source identity and guarantee boundaries

**Failure class:** The ASES pilot mixed real Rust Store tests, a synthetic Kernel-0 model, a newly written HMS SQLite adapter and actual shipped Trip'n JS; naive aggregation would count these as equivalent product assurance.

**Changed practice:** Label the tested object **SHIPPED / EXISTING / CANDIDATE / MUTANT / SYNTHETIC**, and separately label whether evidence crosses storage, provider, authorization or deployment boundaries. Reusable ASES techniques do not inherit product guarantees.

**Evidence:** [ASES pilot PR #58](https://github.com/rock-solid-sites/ASES/pull/58), [real-Store PR #59](https://github.com/rock-solid-sites/ASES/pull/59), [HMS draft PR #23](https://github.com/rock-solid-sites/HMS/pull/23), [Trip'n draft PR #30](https://github.com/TripN-Chill-Zone/tripn-astro/pull/30).

**Limit:** These projects demonstrate *applicability*, not statistically measured superiority or production readiness.

### L09 — Runtime identity must match recorded authority

**Failure class:** Paseo's bridge validated the inspected agent ID, workspace, provider and model, but accepted an explicit `Thinking:'low'` report after the role had authorized `thinking:'none'`.

**Changed practice:** When an authorization claim spans configuration, ownership record and observed runtime, independently compare *every relevant authority dimension*. A paired fake-CLI control should vary only the inspected value and assert that no follow-up command is sent. Add the check at the status/control boundary, not merely during configuration validation.

**Evidence:** [Paseo test/fix PR #77](https://github.com/rock-solid-sites/ases-plugins/pull/77), [expected-red CI](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570572887) (17 pass, 1 missing-rejection failure), [green CI](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570781671) (18/18 pass and protocol smoke), [experiment card](../experiments/2026-11-paseo-thinking-authority.md).

**Limit:** The repair is draft-only and rejects mismatches only when the runtime `Thinking` field is present; missing-field semantics and actual live CLI behavior remain unverified.

## Promotion and retirement

A new lesson should specify what an agent will do **differently** on the next project, its simplest test and its evidence. If an experiment produces no transferable change, leave a bounded result in its owner repo without adding a lasting ASES lesson. Work Notes `WNASES-10` decides which findings merit an independently reviewed edit to the **existing** active method; neither this file nor the experimental selection candidate is a second authority.
