# Experiment 3 — pre-registered confirmation of the explicit-unknown signal

- **Issue:** #570 · **Status:** design frozen BEFORE any case selection or API spend
- **Subject:** direct TypeSafe `jev-1.13.0` at `api.typesafe.ai/v1/systemone`
- **Fixed infrastructure (not redesigned):** the verified Phase-2 corpus and
  case set, the freeze process, the schema gates, the matched-denominator
  analysis, `harness/`, and `model-discipline.md`

## Objective

Test whether the explicit-unknown signal observed in Experiment 1 **survives on
fresh data when the decision rule is fixed before execution**.

## Pre-registered rules — FIXED, NOT TUNED

### Primary rule (explicit unknown)

```
p(insufficient_evidence) >= 0.05
```

Applied verbatim. If fresh data shows a different optimum, that is the result.
The threshold is **not** revised, replaced, or supplemented after seeing
anything.

### Comparison rule (generic external gate)

Arm A is the same forced `{yes, no}` judgment. The generic external gate acts
iff

```
p(ground_truth_option) >= 0.86
```

and abstains on an unanswerable case iff `max(p(yes), p(no)) < 0.86`.

**τ = 0.86 is carried from Experiment 1**, where it was the best point on that
grid. It is therefore **pre-registered from prior data and applied out of
sample here**, which is the whole point: it is a parameter already chosen, being
tested on cases it was not chosen on. **It is not re-tuned.** The fresh-data
threshold curve may be *reported* descriptively, but **no threshold may be
selected from it**, and it may not replace τ = 0.86 in the primary comparison.

τ = 0.86 was itself a post-hoc maximum on a 10-point grid over n=10 unanswerable
cases in Experiment 1, so it is fragile. That fragility is the test: if a
parameter tuned on 10 cases does not transfer, the generic gate should lose.

## Freshness — what "fresh" means here, and why it is stricter than a new id

Experiment 1 drew on **all 67** frozen cases. So no case from `frozen/cases.json`
may be reused. Freshness is enforced on the *underlying selection*, not the
label: a new `case_id` pointing at the same `(caller, callee)`, `(fn, param)`,
import, or nesting target is a reused case wearing a new name.

Excluded by construction, and asserted mechanically:

1. every `case_id` in `frozen/cases.json`;
2. every `(caller, callee)` pair used by Experiment 1's `direct_call` cases;
3. every `(fn, param)` pair used by Experiment 1's `param_rebound` cases;
4. every import token used by Experiment 1's `unused_import` cases;
5. every `(target, callee)` used by Experiment 1's `nesting_conjunction` cases;
6. every function used by Experiment 1's unanswerable cases.

**The unanswerable coupling that must be broken.** Experiment 1's ten
unanswerable cases used only **five distinct functions** — one per module, with
the same function serving both the semantic and the runtime class. So the
unanswerable signal rested on five subjects, not ten. Fresh unanswerable cases
use **two different functions per module**, giving ten distinct subjects, and the
two classes never share a function.

## Case types

Answerable, drawn from the fresh pool:

| type | ground truth | admissible under `raw`? |
|---|---|---|
| `direct_call` | edge present/absent in the intra-module call graph | yes |
| `param_rebound` | parameter appears in the function's assigned locals | yes |
| `nesting_conjunction` | ∃ function with `max_nesting > t` **and** calling `z` | yes |
| `unused_import` | import token never referenced by name | yes |
| `string_literal_probe` | literal present in the function's recorded source | yes |

Unanswerable, with no ground truth by construction:

| type | question | why not derivable |
|---|---|---|
| `unanswerable_semantic` | is `F` safe to call concurrently? | semantic property, absent from source and structure |
| `unanswerable_runtime` | how many times is `F` called per request? | runtime property |
| `unanswerable_version` | which version of library `L` does this code require? | the representation records no version constraint |
| `unanswerable_intent` | why was `F` written? | intent is not in the code |

The two new classes widen the unanswerable probe beyond the two Experiment 1
used, so the confirmation is not confined to the classes that produced the
original signal.

## Recorded separately — never substituted for one another

For every fresh case, recorded as **distinct fields**:

1. `normal_answer_correct` — on answerable cases only;
2. `explicit_unknown_detected` — `p(insufficient_evidence) >= 0.05` on
   unanswerable cases. This is the **primary** measurement;
3. `false_unknown` — that same rule firing on an answerable case;
4. `false_confidence` — arm B emitting `yes`/`no` on an unanswerable case;
5. `argmax_selected_insufficient` — whether `insufficient_evidence` is actually
   the argmax. **This is a different measurement from (2) and is never reported
   as a substitute for it.** Experiment 1 showed they diverge sharply: 0.30 by
   argmax against 1.00 by probability.

Also recorded, for both arms: `probabilities`, `p_selected`, `max_prob`,
`provider_confidence`, `derived_confidence`, `latency_ms`, `usage`. Probability
and provider confidence stay separate; per Phase 1 `INSTRUMENT-VALIDATION.md`
the provider's confidence is a derived function of the probability vector and is
not independent evidence.

## Primary question

**Does the pre-registered explicit-unknown probability rule continue to
distinguish answerable from unanswerable cases on unseen data, and does it
outperform the existing generic external gate without increasing false-unknowns
materially?**

## Execution contract

- Existing hardened path only. No parallel tooling.
- **Phase A** constructs the complete planned batch, validates schemas and
  cross-field invariants, and **asserts every rendered request contains the
  intended case question, the intended evidence, the intended answer
  alternatives and the intended arm** — all before any API spend.
- Freeze covering every result-affecting component, declared and verified before
  Phase B. Any post-freeze change requires a newly declared freeze.
- Matched denominators throughout; cost/token consistency check retained.
- Only routes permitted by `model-discipline.md`. No substitution.

## Stop condition

Frozen packet, executed, scored, reproducible from committed material, and
**independently verified** — with the verifier deriving the final statistics from
raw records, inspecting representative rendered requests and fresh-case
derivability, confirming the pre-registration was honoured, and adversarially
checking that no post-hoc tuning, ground-truth leakage, Experiment-1 case reuse
or arm contamination occurred.
