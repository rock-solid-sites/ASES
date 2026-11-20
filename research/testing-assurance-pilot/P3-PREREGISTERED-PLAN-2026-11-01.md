---
title: EDASES Pilot P3 — Control Coverage Across Unselected Invariants
program: EDASES
layer: Research
document_type: Preregistered Experiment Plan
status: Frozen Before P3 Mutation Execution
authority: Experimental
date_frozen: 2026-11-01
---

# P3 — Are existing controls discriminating outside their selected targets?

**Research objective:** Compare the five P1 frozen examples with the preexisting 1,025-case language-evaluation corpus and with *new independently specified boundary-neighbor examples*. Do not infer a general mutation score from 3 selected operations, and do not change production authorization, CI policies or language choice.

## Frozen candidate fault classes

The P1 pilot focused on paid consent and false rejection. P3 selects different **existing** risk domains, not faults chosen to be caught by P1's five examples:

1. **Capacity:** disable the guard rejecting `reserved > capacity` or `requested > capacity - reserved`. A request exactly filling remaining capacity must be admitted; one unit over must be denied.
2. **Prepaid wallet floor:** disable the guard enforcing `wallet >= wallet_floor + charge`. A charge exactly using the permitted remaining prepaid balance must be admitted; one cent beyond must be denied.
3. **Postpaid spend cap:** disable the guard enforcing `liability + charge <= spend_cap`. Exact-cap compliant use must pass; one cent over must be denied.

Each fault is introduced in a disposable source copy into the **same** normal decision function in Rust and Haskell, for six compiled mutants. The original binaries and mutable source files are not changed by the test.

## Pre-observation predictions and falsifiers

| Test | Prediction | Falsifier |
| --- | --- | --- |
| A | Both original languages accept all three valid neighbors and deny all three invalid neighbors with specified reason and zero authorized charge | Either baseline disagrees with the fixed boundary expectations |
| B | The five P1 controls miss at least one of these three faults in both languages | All three faults are detected by the five P1 controls |
| C | The 25 handwritten + 1,001 deterministic generated tests detect at least one fault absent from the P1 controls | No additional fault is detected |
| D | The newly frozen neighboring pairs detect all three relevant mutants while retaining each matching valid admission | A matching invalid neighbor is admitted by baseline, the mutant is not detected, or valid neighbor is falsely rejected |
| E | Build/execute cost and output-evidence size are recorded per variant; compilation, fixture or transport faults are labeled ERROR, not credited as mutant kills | Missing cost / provenance, unexplained exit or data mismatch counted as success |
| F | Post-run outcomes and experiment claims can be reconstructed from the source version, expected control values and emitted full observations | Only the author's pass flag exists or evidence missing |

**Independent requirements:** Hand-specified P3 boundary expected outputs are:
- `capacity-exact-p3`: admitted, charge 0; `capacity-over-p3`: capacity-exceeded, charge 0.
- `wallet-exact-p3`: admitted, charge 40; `wallet-over-p3`: wallet-floor-exceeded, charge 0.
- `spend-exact-p3`: admitted, charge 40; `spend-over-p3`: spend-cap-exceeded, charge 0.

Specific scalar inputs derive from the initial free-covered corpus exemplar and are then overridden explicitly: capacity/reserved/requested 16/4/12 or /13; prepaid usage=20/rate=2/wallet_floor=10/wallet=50 or 49, paid_opt_in=true; postpaid usage=20/rate=2/liability=60 or 61/spend_cap=100, paid_opt_in=true. All other provider states remain active, verified and current.

## Method

1. Compile normal Rust release and Haskell -O2 binaries with the GitLab pinned Rust/Haskell toolchains and run their new exact boundary fixtures before mutation.
2. Build each of six single-site mutations from the same checked-out ASES revision using exact-match source anchors. Keep original files intact, preserve exact substitution and source hash.
3. Run P1's original five frozen fixtures, then the existing handwritten 25 + deterministic 1,001 fixture corpus, then the six new boundary fixtures on each mutant. Note both **which specific tests differ from baseline** and the difference between the three detection sets.
4. Compare existing corpus to established handwritten golden outputs and deterministic oracle; freeze the old oracle and generator unchanged. New six manual boundary expectations are **not computed from the code being evaluated**.
5. Record instrument errors separately from behavioral violations; print and retain structured per-mutant outcomes and minimum observed counterexamples with stable IDs.
6. Measure gross execution and build cost; do not infer total agent cost or universal engineering effort from a single CI job.
7. Retain GitLab native artifacts and externally copy a machine-readable evidence summary into public ASES (no secrets). Mark the full CI artifact archive **NOT_VERIFIED** unless it is separately recovered and hash-checked.

## Gates and decisions

The selected faults are known and chosen deliberately; these checks only establish *relative sensitivity across three suites on three risk domains*. A 6/6 kill is not a general mutation score. The prior P1 and P2 results are not overwritten. No independent reviewer has yet evaluated these experiments; method adoption remains **DEFER**. Real distributed reservations, account settlement and state-machine/solver alternatives are **NOT_TESTED**.
