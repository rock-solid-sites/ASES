---
title: EDASES Pilot P1 — Testing Instrument Qualification
program: EDASES
layer: Research
document_type: Preregistered Experiment Plan
status: Frozen Before New Pilot Execution
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Testing and Assurance Method - Proposal.md (proposal branch; not adopted)
  - research/language-eval/README.md
related_documents:
  - research/language-eval/RESULTS-2026-11-01.md
date_frozen: 2026-11-01
---

# EDASES Pilot P1 — test-instrument qualification and evidence integrity

**This plan is the pre-observation record for NEW pilot tests.** Earlier Rust/Haskell test outcomes are prior evidence, not pilot results. The testing-and-assurance methodology remains **DRAFT, not adopted**. No language, state-machine realization, CI provider, or retention policy is selected by this experiment.

## Object and attributed claims

- Object: the ASES research-only provider-admission input/output contract defined in `research/language-eval/README.md`, implemented separately by the conventional Rust and Haskell reference programs. The claim is from the ASES experiment specification, *not* from a production billing provider.
- **C1:** Given a positive would-be charge and `paid_opt_in=false`, the admission decision must reject it as `paid-opt-in-required` and authorize zero cents. A paired paid-authorized request with sufficient spend cap must pass.
- **C2:** An admissible request should not be rejected merely to satisfy a safety test. The free-covered request and the properly authorized paid request are positive neighbors.
- **C3:** Test execution results and independent-archive integrity are separate conclusions; a missing or altered artifact must cause an explicit archival-integrity failure, even if the underlying behavior checks are green.
- **C4 (methodological):** Targeted mutation and positive-neighbor controls can qualify at least the listed C1/C2 test checks and reveal a defect that a green-only report obscures, at an identifiable incremental cost.

The test oracle is the frozen expected corpus and dedicated boundary expectations, not the implementation's own output. Both languages share assumptions and the original corpus; correlated specification errors remain possible.

## Pre-observation hypotheses and falsifiers

| ID | Prediction to test | What would challenge it |
| --- | --- | --- |
| P1 | Baseline Rust and Haskell both reject unauthorised positive spend and admit the paid-authorised neighbor | Either implementation disagrees with frozen expectations |
| P2 | Disabling the `paid_opt_in` guard in either language makes the targeted negative control fail while its positive neighbor still passes | Mutant is accepted by the control suite, or positive neighbor fails |
| P3 | A mutant rejecting a valid admitted request fails the positive-neighbor control in each language | Mutant passes both positive neighbors |
| P4 | An archive checker accepts a complete hash-verified manifest and rejects both a missing file and a silently modified file | Any missing/corrupt artifact is classified as complete, or a complete manifest is rejected |
| P5 | Evidence emitted by CI permits a later reader to identify source SHA, frozen plan, mutant edits, expected vs observed outcomes, toolchain, CI status, and archive status separately | Any item cannot be reconstructed from retained evidence; lack of an independent review remains UNRESOLVED |
| P6 | Targeted qualification has measurable but bounded additional runner time and evidence volume; measure rather than assert an optimal cost | Missing cost measurement or nonreproducible workload |

No numerical performance threshold is set for language choice. The pilot will report **what it cost**, not claim that a one-off experiment establishes lower long-run project cost. CI run setup and dependency installation are measured separately from qualification where feasible.

## Method selection: cheapest discriminating controls

Chosen: **source-level targeted mutations with paired controls** on two compiled language implementations. They are cheaper and more targeted for C1/C2 than redesigning a full state machine or conducting real provider billing. For C3, a **synthetic hash-verified archive fixture with fault injection** is cheaper and safer than deleting actual CI evidence.

Mutation operators are exact, one-location substitutions in a disposable checkout only:

1. `bypass-paid-guard`: make the `paid_opt_in` rejection predicate false. Control: positive-charge without approval must be rejected; valid authorized request remains accepted.
2. `reject-valid`: change final successful admission into a denial. Control: compliant free-covered and paid-approved cases must remain accepted.

Compile four mutants (2 implementations × 2 operators), run the controls on all original and mutated binaries, record actual outputs, and label failures of compilation or fixture setup **ERROR**, not `RED` or target detection. Mutants must be built from the same frozen source revision, and after execution must not replace production or reference code.

For archive fault injection, use a private disposable directory containing innocuous test data only; never delete original provider artifacts. Store manifest containing SHA-256/size, verify valid, deleted, corrupted cases, and report artifact failures **separately** from test result.

## Qualifying success and legitimate non-results

- Baseline complies with C1 and C2 and both mutants per language are killed by the **intended** control, not an unrelated compile/import/setup failure.
- Positive-neighbor tests must pass for baseline and for bypass-guard mutation.
- Archive check accepts complete artifact set and identifies missing and corrupted files independently.
- Structured outcome, CI job source SHA and toolchain versions, frozen plan link, mutant exact diff, observed verdicts, and overhead estimate are retained.
- CI pass alone is not method validation. A competent **independent reviewer reconstruction exercise** is required before adopting the proposed method; no reviewer is assumed.
- Unknown outside-program billing or provider behavior remains **NOT_TESTED**.
- The pilot is one substrate. The proposal's second unlike substrate (e.g. Trip'n Action) and a real independent archive-export integration remain **outstanding**.

## Baseline evidence and planned measurement

Historical green baseline: GitLab pipeline `3015126277` (both language corpora and wire checks); subsequent optimized/single-source-change baseline: pipeline `3015249025`. Those were run before this plan and are not retroactively classified as its pre-registered tests.

Record pilot test per-language results, per-mutant compile/execute time, bytes in results, instrument controls, total pipeline duration, setup time, and storage/archive-completeness status. New CI generated artifacts have a finite native retention; a GitHub commit containing a trace-derived pilot summary **does not by itself establish complete external archival of all raw artifacts**.

## Evidence and decision handling

- Execution: PASS / FAIL / ERROR / INCONCLUSIVE / BLOCKED / CANCELLED / SKIPPED / NOT_RUN.
- Claim assessment: SUPPORTED_WITHIN_SCOPE / CONTRADICTED / UNRESOLVED.
- Evidence qualification: QUALIFIED / PARTIALLY_QUALIFIED / UNQUALIFIED; archive completeness tracked independently.
- Acceptance: **DEFER** until independent review and second substrate. Only the authorized human may promote an ASES method or language choice.

Preserve the original plan without retroactive edits; append post-observation findings in a separate result file.
