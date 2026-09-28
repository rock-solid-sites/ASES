# Experiment 1 — explicit unknown vs external probability gating

- **Issue:** #570 · **Status:** design frozen before execution
- **Subject:** direct TypeSafe `jev-1.13.0` at `api.typesafe.ai/v1/systemone`
- **Inputs (fixed, not re-derived):** the frozen Phase-2 case set
  `phase2/frozen/cases.json` (sha256 `0e8585f8…`) and the Phase-2 admissibility
  matrix. No new cases, no new corpus, no re-run of Phase 1 or Phase 2.

## Question

**When unanswerability is represented explicitly, can Jev identify missing
evidence more reliably than an external probability threshold alone?**

## Feasibility check run first (cheapest-test-first)

Before designing, two live probes established that the `choice` primitive is
usable on the direct route. This matters because `followup-04` had recorded
`choice` as degenerate (one-hot, `confidence` exactly 1.0 on 36/36 calls), which
would have crippled an explicit-unknown arm built on `choice`.

| probe | result |
|---|---|
| `choice` over `{yes, no}` | `choice=yes`, `probabilities={yes:0.64, no:0.36}`, `confidence=0.29` |
| `choice` over `{yes, no, insufficient_evidence}` | `choice=yes`, `probabilities={yes:0.48, no:0.15, insufficient_evidence:0.37}`, `confidence=0.22` |

Two findings, both recorded because they change the design:

1. **`choice` is NOT degenerate here.** The `followup-04` one-hot result does
   **not** reproduce on this question set. It is not claimed to be refuted in
   general — different questions, same route. Recorded as
   non-reproduction on this set, not as a refutation.
2. **The derived-confidence formula replicates exactly.**
   n=2: `(2·0.64−1)/1 = 0.28` vs reported 0.29 (2-dp rounding).
   n=3: `(3·0.48−1)/2 = 0.22` vs reported 0.22 (exact).
   Consistent with `INSTRUMENT-VALIDATION.md`. Therefore `confidence` is logged
   beside `probabilities` and is **never** treated as independent evidence.

## Arms — three, differing only by the declared variable

All three use the `choice` primitive over the identical state, so the arms do
not differ by primitive. The declared variable is the **representation of
unanswerability**.

| arm | request | options | new API calls |
|---|---|---|---|
| **A** forced | one `choice` question | `yes`, `no` | yes |
| **B** explicit unknown | one `choice` question | `yes`, `no`, `insufficient_evidence` | yes |
| **C** external gate | **identical to arm A** | — | **none** |

Arm C is a re-analysis of arm A's own returned distribution under an external
threshold. It is free by construction, and because A and C are the *same
requests*, any difference between them is attributable to the threshold and to
nothing else. That is the comparison the question actually asks.

### The explicit-unknown instruction

The wording is the experiment. It must ask whether the **representation
contains the evidence**, and must not encode the answer or restate low
confidence.

> Answer with exactly one of: `yes`, `no`, `insufficient_evidence`.
> Choose `insufficient_evidence` **only if the material above does not contain
> the information needed to decide** — for example because the fact is absent,
> or because the material is ambiguous or self-contradictory.
> Do **not** choose `insufficient_evidence` merely because you are unsure or
> because the question is difficult. If the material contains enough to decide,
> you must choose `yes` or `no`.

Two properties are enforced mechanically at freeze time (see "Leak and
encoding checks"):

- the instruction contains **no** reference to confidence, probability,
  uncertainty, or hedging;
- it does **not** name the case's own ground truth or any case-specific fact.

Arm A's instruction is the same text with the `insufficient_evidence` option and
its paragraph removed, so the two differ only in the option set and the minimum
text needed to define that option.

## Scoring, frozen before execution

Kept strictly separate, as required. These are five different quantities and are
never combined into one "score":

1. **Correctness** — on **answerable** cases only (50 in the frozen set):
   correct iff the selected option equals the ground truth. Selecting
   `insufficient_evidence` on an answerable case is **wrong**, not a partial
   credit.
2. **Explicit-unknown detection** — on **unanswerable** cases only (14):
   correct iff arm B selects `insufficient_evidence`. Arms A and C cannot
   express this, so their detection rate is 0 **by construction**, not by
   performance.
3. **False-unknown rate** — on **answerable** cases: fraction where arm B
   selects `insufficient_evidence` despite the evidence being present. This is
   the cost side of arm B.
4. **False-confidence rate** — on **unanswerable** cases: fraction where a
   positive label (`yes`/`no`) is emitted rather than abstaining. Defined for
   all three arms.
5. **Coverage / error trade-off for external gating** — arm C's threshold
   sweep, and arm B's equivalent sweep over `p(insufficient_evidence)`, on one
   matched cell set.

**Raw probability**, **provider confidence**, **measured calibration**,
**correctness** and **abstention** are stored in separate fields and reported in
separate tables. No composite is computed.

### External gating rule (arm C)

A case is *acted on* iff the arm-A decision is confident:

```
acted  ⟺  p(gt_option) ≥ τ          τ swept over {0.50,0.55,…,0.95}
abstain otherwise
```

Coverage is computed on the **matched cell set** (cases admissible and answered
under both A and B), never across conditions with different cell counts. Per
`RECON.md` §6, only cases admissible in **both** conditions enter the
comparison; the unanswerable set is scored on its own identical cell set.

### Arm B's equivalent operating curve

To compare like with like, arm B is also swept: `abstain ⟺
p(insufficient_evidence) ≥ θ`. Both arms are then plotted on the same
axes — unknown-detection vs false-unknown — so the comparison is of
*operating curves*, not of a single arbitrary operating point.

## Calibration

Reported as our own measurement, binned, and clearly labelled as **not** the
provider's claim. Given n=50 answerable plus 14 unanswerable, calibration is
reported descriptively and **no reliability claim is made**.

## Leak and encoding checks (run at freeze time, before any API call)

1. The arm-B instruction contains no confidence/probability/uncertainty token.
2. The arm-B instruction does not contain the case's ground-truth answer string
   as a standalone instruction to select it.
3. Arm A and arm B differ **only** by the option set and the `insufficient_evidence`
   definition paragraph — asserted by diffing the rendered instruction with the
   option list and that paragraph removed.
4. Every arm-B row's state is byte-identical to its arm-A counterpart's state
   (same case, same representation).
5. Question semantics are byte-identical across arms except for the declared
   difference.

## Execution contract

- Extend the existing hardened path minimally: `harness/run_jev.py` gains a
  question-plan capability (it is currently hardcoded to a single `noul`), and
  `harness/score.py` gains an experiment-1 summariser. No parallel tooling.
- **Phase A** constructs and schema-validates the entire planned batch with
  **zero API spend**; **Phase B** executes only after all gates pass.
- Freeze v5 is declared covering all 17+ result-affecting components and
  verified immediately before and after execution.
- Matched denominators throughout; the cost/token consistency check is retained
  and a disagreement is an analysis failure.

## Stop condition for Experiment 1

Frozen, executed, scored, reproducible from committed material, and
**independently verified** — with the verifier reproducing the final statistics
from raw evidence, inspecting representative matched requests, and confirming
the arms differ only by the declared variable — before Experiment 2 begins.
