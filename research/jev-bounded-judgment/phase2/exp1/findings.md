# Experiment 1 findings — explicit unknown vs external probability gating

- **Issue:** #570 · **Model:** direct `jev-1.13.0` · **Representation:** `raw`
- **Verified by:** `opencode/muse-spark-1.3-contributor-free` (`muse-free`),
  cross-family from the producer — `verification.md`, **PASS WITH FINDINGS**
- **Requests:** 134 (67 cases × 2 arms), 0 transport/parse errors
- **Freeze:** v12, verified before and after execution

## Answer

**Yes — when unanswerability is represented explicitly, Jev identifies missing
evidence more reliably than an external probability threshold alone.**

| | unknown detection | false-unknown | answerable coverage retained |
|---|---|---|---|
| arm B, explicit unknown, best zero-false-unknown point (θ=0.03) | **10/10 = 1.00** | **0/57 = 0.00** | 1.00 (it acts on all answerable) |
| arm C, external threshold, best point (τ=0.86) | 9/10 = 0.90 | — | **0.667** (abstains on 33%) |
| arm A, forced | 0/10 = 0.00 *by construction* | 0/57 *by construction* | 1.00 |

Arm B's `p(insufficient_evidence)` **perfectly separates** the two populations
on this sample:

- every one of the 57 answerable cases: p(insufficient) ≤ **0.02**
- every one of the 10 unanswerable cases: p(insufficient) ≥ **0.10**

A threshold anywhere in the 0.02–0.10 gap yields 100% detection at 0%
false-unknowns. The external threshold cannot reach that operating point at any
τ: its detection is bought by discarding a third of the answerable cases.

### The finding my first report got wrong, and why

An earlier version of this document reported the **opposite** conclusion —
"external gating dominates, arm B has no usable operating point". That was
wrong, in a way worth recording precisely:

- The θ sweep grid began at **0.50**. Arm B's entire signal lives *below* 0.50
  (max on answerable 0.02, min on unanswerable 0.10). The grid therefore
  excluded it, and the sweep showed detection *falling* as θ rose, which read as
  "no usable operating point" when it was really "the grid missed the signal".
- I then reported the **argmax selection rate** (0.30) as arm B's detection
  figure. That is a different quantity: it is how often the model *chooses* the
  option, not what its probability *supports*. The two disagree sharply here,
  and the probability is the more useful one.

A sweep grid chosen without looking at where the probability mass sits can
invert a conclusion. It did. The independent verifier caught it.

## Secondary findings

1. **Adding the option slightly improved answerable accuracy**: arm B 49/57
   (0.8596) vs arm A 47/57 (0.8246). Step 1 of the verification shows this is
   arm B fixing 3 of arm A's errors and introducing 1 new one. At n=57 this is
   not a capability claim, and it is plausibly a calibration artefact of a
   3-way distribution partitioning probability mass differently.
2. **The model does not act on its own best signal.** It selects
   `insufficient_evidence` on only 3 of 10 unanswerable cases while its
   probability cleanly separates all 10. An operator reading the selected label
   would capture 0.30 of the available 1.00.
3. **`choice` is not degenerate here.** 0 of 67 rows are one-hot; probabilities
   span 0.0–1.0. This does **not** refute `followup-04`'s one-hot observation —
   different questions, same route — but it does mean the earlier degeneracy
   cannot be assumed for this question class.
4. **Provider confidence replicates the derived formula** to within 0.015 across
   both arms, consistent with Phase 1 `INSTRUMENT-VALIDATION.md`. It is
   therefore not independent evidence and is reported beside the probabilities,
   never merged with them.

## Kept separate, never combined

Probability, provider confidence, measured calibration, correctness and
abstention are stored in separate fields and reported in separate tables.
Calibration is binned descriptively with **no reliability claim** — n is far too
small, and the bins are ours, not the provider's.

## Limitations

1. **n = 10 unanswerable.** The headline rests on 10 detected vs 9 detected out
   of 10. That difference is one case. It is directionally consistent and the
   separation margin is wide (0.02 vs 0.10), but it is a small-n result.
2. **Both operating points are post-hoc.** τ=0.86 and θ=0.03 were selected after
   seeing the data. Reported as observed, with selection bias flagged but not
   corrected. A pre-registered-threshold replication is required before either
   becomes a reliability claim.
3. **Representation fixed to `raw`.** Nothing here shows the effect survives the
   structure representation, which is where Phase 2 found evidence removal.
4. **One corpus, one mechanism, one wording.** The 0.02/0.10 gap may be
   wording-specific; Step 3 of the verification judged the instruction sound but
   noted a less leading formulation is conceivable.
5. **No repeat measurement.** Cell-level nondeterminism is unquantified.
6. **Not tested:** whether an external threshold on arm B's *own* probability
   (rather than the argmax label) would do as well — it would, trivially, since
   that is exactly what θ is.

## Two harness defects found and fixed before these results existed

1. `build_question`'s `choice` branch never included the case question, so both
   arms asked the model to choose a label over the state with **no question
   present**. It returned a near-constant answer (67/67 identical per arm).
   Quarantined as `VOIDED-no-question-in-request.ndjson`; encoding check **E6**
   added, which now asserts the rendered instruction contains the case question.
2. The packet send-flag was keyed on condition rather than `case_id`, so it
   never matched and every case fell back to the Phase 2 admissibility gate —
   which excludes exactly the unanswerable cases this experiment exists to
   measure. 10 of 10 unanswerable cases would have been dropped silently.
   `send` and `score_for_correctness` are now separate fields.

## Smallest justified next experiment

**Replicate the explicit-unknown result with a pre-registered threshold and a
larger unanswerable set.** Nothing else.

The finding is currently one corpus, one wording, one mechanism, ten
unanswerable cases, and a post-hoc threshold. The cheapest discriminating test
is to fix θ = 0.05 *in advance* and re-run on a fresh set of unanswerable cases
authored without reference to these results. If the 0.02/0.10 separation holds,
explicit unknown earns a place; if it collapses, Experiment 1's answer reverses
and the external threshold is the honest default.

Explicitly **not** proposed: Experiment 2 has not been executed and this result
does not bear on its question; no corpus scaling; no second judgment mechanism;
no historical-session replay.
