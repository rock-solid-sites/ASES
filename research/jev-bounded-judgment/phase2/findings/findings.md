# Phase 2 findings — does deterministic code structure help bounded judgment?

- **Issue:** #570 (subissue of #565) · **Date:** 2026-09-27
- **Subject:** direct TypeSafe `jev-1.13.0` at `api.typesafe.ai/v1/systemone`
- **Frozen inputs:** `frozen/MANIFEST.md` (all digests asserted at run time)
- **Execution:** 218 scored cells, 40 observation-only unanswerable cells,
  **0 transport errors, 0 parse errors**
- **Scorer:** `harness/score.py`, deterministic

## 0. Headline

**Structure's clear, measurable benefit is efficiency, not accuracy.**

Efficiency gains are exact and carry no sampling uncertainty: structure is
**1.92× smaller in state bytes, 1.49× fewer input tokens, 1.63× cheaper**, with
a slightly lower median latency. These are measurements over identical case
sets, so there is no confidence interval to compute.

Accuracy gains are **directionally positive and not statistically supported** at
this sample size. Every paired accuracy comparison fails to reach significance:

| comparison | n | correct only in first | correct only in second | exact McNemar p |
|---|---|---|---|---|
| raw vs struct | 52 | 2 | 4 | **0.6875** |
| raw_ic vs struct_ic | 52 | 2 | 9 | **0.0654** |
| raw vs raw_ic | 57 | 4 | 0 | **0.1250** |
| struct vs struct_ic | 52 | 1 | 2 | **1.0000** |

Structure is at or above raw in every comparison, which is a consistent
direction. Consistency across four comparisons is not significance, and Phase 1
already recorded the lesson that a consistent direction on a small sample is not
a finding. **This benchmark does not establish that structure improves
accuracy.**

## 1. Measurements

| condition | n_adm | accuracy | state bytes | input tokens | median ms | p95 ms | cost USD |
|---|---|---|---|---|---|---|---|
| `raw` | 57 | 0.8070 | 32782 | 7925 | 337.8 | 426.6 | 0.018973 |
| `raw_ic` | 57 | 0.7368 | 60363 | 15945 | 386.1 | 451.9 | 0.038173 |
| `struct` | 52 | 0.8846 | 17085 | 5334 | 324.9 | 381.4 | 0.011650 |
| `struct_ic` | 52 | 0.9038 | 33748 | 10179 | 344.2 | 407.1 | 0.022230 |

`raw` and `struct` have different denominators (57 vs 52) because five cases are
unanswerable from structure. **Only the paired comparisons on the 52 shared
cases are interpretable**; the marginal accuracies above are not directly
comparable to each other.

Tariff: $0.042 / 1M input tokens, output free, as recorded in followup-04 from
TypeSafe docs fetched 2026-09-26. A tariff change moves the cost column only.

## 2. Efficiency — supported, exact

| axis | raw | struct | ratio |
|---|---|---|---|
| state bytes (mean) | 32782 | 17085 | **1.92× smaller** |
| input tokens (mean) | 7925 | 5334 | **1.49× fewer** |
| cost per run | $0.018973 | $0.011650 | **1.63× cheaper** |
| median latency | 337.8 ms | 324.9 ms | 1.04× faster |
| p95 latency | 426.6 ms | 381.4 ms | 1.12× better |

**WHY this is the solid result:** these are exact counts over the same 52
comparable cases, not estimates. There is no seed, no sampling and no
confidence interval. The direction cannot be an artefact of the sample.

**WHAT-NOT-TESTED:** whole-module structure only. A tool that indexed a
repository once and then queried a subgraph would have a far better ratio than
whole-module rendering, because the cost here is dominated by emitting all 88
functions and 260 edges of `configparser` when a question concerns one function.
**The measured 1.92× is a floor for this representation strategy, not a ceiling
for structural preprocessing.** It measures "structure instead of source", not
"targeted query instead of bulk".

## 3. Accuracy — directionally positive, NOT established

Paired on the 52 comparable cases:

| intrinsic group | n | raw | struct | only raw | only struct |
|---|---|---|---|---|---|
| `judgment_under_both` | 27 | 0.7778 | 0.8148 | 1 | 2 |
| `lookup_under_struct` | 25 | 0.9200 | 0.9600 | 1 | 2 |
| **all comparable** | **52** | **0.8462** | **0.8846** | **2** | **4** |

### 3.1 The lookup concern did not materialise — but the effect is too small to matter either way

The design's central honesty risk was that structure would turn a judgment into
a lookup, and that any gain would be trivialisation rather than better judgment.
Splitting by intrinsic group was built to detect exactly that.

It did not fire: the `lookup_under_struct` group gained +4.0pp and the
`judgment_under_both` group gained +3.7pp. **The gains are the same size in both
groups**, so the improvement is not concentrated in the cases structure
trivialised.

But the honest reading is weaker than it looks: with only 2 and 4 discordant
cells in total, this benchmark **cannot distinguish** "structure improves
judgment" from "structure improves lookup" from "nothing happened". The absence
of a lookup concentration is consistent with all three. This is a
**non-result on a question the design was built to answer**, and it is the
strongest argument for a larger n.

## 4. Robustness to irrelevant context — directionally the most interesting signal

Appending 27 KB of real unrelated code (`uuid`, zero symbol overlap) to both
representations:

| condition | clean | + irrelevant | lost | gained | exact p |
|---|---|---|---|---|---|
| `raw` | 46/57 | 42/57 | **4** | **0** | 0.1250 |
| `struct` | 46/52 | 47/52 | 1 | 2 | 1.0000 |

Under the distractor, the representation gap widens sharply:

| | clean | + irrelevant |
|---|---|---|
| gap (struct − raw), paired n=52 | +3.8pp | **+13.5pp** |

Per case type, the mechanism is visible:

| ctype | raw | struct | raw_ic | struct_ic |
|---|---|---|---|---|
| `nesting_conjunction` | 0.8 | 0.8 | **0.4** | 0.8 |
| `param_rebound` | 0.8 | 1.0 | 0.7 | 1.0 |
| `direct_call` | 0.92 | 0.96 | 0.88 | 1.0 |
| `call_path2` | 0.714 | 0.714 | 0.714 | **0.571** |
| `unused_import` | 0.8 | **0.6** | 0.8 | 0.8 |

`nesting_conjunction` is the clearest case: it requires composing two facts
(a nesting depth and a call edge). Raw halves under distraction, 0.8 → 0.4,
while structure holds at 0.8. That is exactly the predicted failure mode —
brittle composition over a long raw surface — and it is the one per-type result
that matches the mechanism the hypothesis proposes.

**But:** p=0.125 for raw's 4-0 degradation, and n=5 per case type. This is a
suggestive sign pattern, **not a supported result**.

## 5. Where structure HURTS — two real costs

### 5.1 Structure destroys a question class outright

The designed evidence-removal probe fired. Five `string_literal_probe` cases ask
whether a function body contains a given string literal.

- **raw: 2/5 correct (0.40)** — the answer is a substring test, and the source is present.
- **struct: unanswerable** — structure carries no string literals by design.

So for literal-presence questions, structure does not make the model better or
worse; it makes the question **unaskable**. A preprocessing layer that silently
drops the evidence a downstream judgment needs is a correctness hazard, not a
speedup. This is measured, not hypothesised, and it is the strongest argument
in Phase 2 for treating structure as a *representation to be paired with its
evidence*, never as a replacement for it.

Note also that raw itself only manages 0.40 here, so the question is hard for the
model even with the evidence present.

### 5.2 Structure is worse on `unused_import`

`unused_import` requires intersecting the import list with the names actually
referenced. Raw 0.8, **struct 0.6** under both clean and distractor conditions.
Structure emits both sides of the intersection separately and faithfully, so this
is not an extraction defect — it is a case where a more compact representation
made the composition *harder to get right*. n=5, so this is a flag for
enlargement, not a claim.

### 5.3 Structure does not fix compositional path reasoning

`call_path2` (is there a function A calls which in turn calls B) sits at
0.571–0.714 under **every** condition. The call-edge list gives the model the
ingredients, and it still cannot reliably do the two-hop composition. This is
consistent with Phase 1's finding that graded probability output was unusable,
and it bounds the claim: **structure supplies facts; it does not supply
reasoning over them.**

## 6. Probability behaviour

| condition | mean noul | min | max | exactly 0 or 1 | near 0.5 (0.4–0.6) |
|---|---|---|---|---|---|
| `raw` | 0.4509 | 0.01 | 0.99 | **0** | 7 |
| `struct` | 0.5075 | 0.02 | 0.98 | **0** | 3 |
| `raw_ic` | 0.4323 | 0.02 | 0.98 | **0** | 8 |
| `struct_ic` | 0.5146 | 0.03 | 0.98 | **0** | 5 |

Two observations:

1. **No degenerate outputs.** Zero cells returned exactly 0.0 or 1.0. This
   differs from followup-04's one-hot `choice` degeneracy, but those were
   `choice` questions and these are `noul`, so the two are **not** directly
   comparable and no contradiction is claimed.
2. **Structure reduces indecision.** Near-0.5 outputs drop from 7–8 under raw to
   3–5 under structure. Structure makes the model more decisive, and the
   reduced indecision coincides with the (non-significant) accuracy gain. This is
   suggestive, not established.

## 7. Unanswerable behaviour — replicates Phase 1, and adds a new finding

40 unanswerable cells were sent **for behaviour observation only** and are never
scored (`ground_truth` is `None`, so the scorer cannot mark them right or
wrong).

**Everything was answered. 40/40. Zero abstentions.** This replicates Phase 1's
finding that no mechanism abstained, now on real code and across all four
representations.

The new finding is that **uncertainty is class-dependent**:

| unanswerable class | mean noul | decided (\|p−0.5\|>0.2) |
|---|---|---|
| `unanswerable_runtime` (runtime call frequency) | 0.426 – 0.502 | **0/5 in every condition** |
| `unanswerable_semantic` (thread safety) | 0.322 – 0.400 | **2–3 of 5 in every condition** |

On a question no representation supports, the model produces a calibrated-looking
≈0.5 for the *runtime* class and a **confident answer for the semantic class**.
So uncertainty does **not** track derivability uniformly.

**Consequence for EDASES:** a confidence-gated abstention policy keyed on
`max(probability)` would look well-behaved on the runtime class and would
confidently proceed on the semantic class. Phase 1 already showed `confidence`
is a derived function of the probability vector and therefore carries no
information beyond `max(p)`; this adds that neither carries information about
**derivability from the given representation**. A gate needs an explicit
derivability check, which is exactly what `validate_cases.py` does mechanically
and what no probability signal substitutes for.

## 8. Verdict

| axis | verdict |
|---|---|
| input size / cost | **structure helps**, exactly and substantially (1.92× / 1.49× / 1.63×) |
| latency | structure marginally better (1.04× median, 1.12× p95); not the interesting axis |
| accuracy, clean representation | **unresolved** — direction favours structure, p=0.69 |
| accuracy under irrelevant context | **unresolved** — direction favours structure, p=0.065 |
| robustness to irrelevant context | **suggestive** — raw degrades 4-0, structure 1-2, p=0.125 |
| lookup vs judgment | **non-result** — gains equal in both groups, sample cannot discriminate |
| compositional reasoning | **structure does not help** (`call_path2` flat or worse) |
| evidence completeness | **structure hurts** — destroys the string-literal question class |
| intrinsic abstention | **absent** — 40/40 answered, replicating Phase 1 |

**Where structural preprocessing helps:** cost and input size, unambiguously.
**Where it hurts:** it removes evidence a downstream judgment can need, and it
does not help compositional reasoning at all.
**Where it remains unresolved:** whether it improves accuracy, and whether the
robustness advantage is real.

## 9. Limitations

1. **n = 52 comparable cases.** Every accuracy comparison is underpowered. Four
   comparisons, zero significant. No claim of improved accuracy is made.
2. **One mechanism only.** Direct `jev-1.13.0`. Phase 1's central lesson was
   that a single-mechanism measurement cannot generalise; the same applies here.
   "Does structure help bounded judgment" is a claim about judgments, and only
   one bounded-judgment mechanism was measured. The Zen free chat route is 403
   for free models, so a second mechanism would have to come through the agent
   route and inherit the followup-05 transport confound.
3. **Whole-module representations only.** No targeted subgraph query, so §2 is a
   floor. R3 (structure + minimal source) was deliberately not built: the design
   made it conditional on materially testing the hypothesis, and the R1/R2 result
   did not justify spending the remaining budget there.
4. **One language, one corpus style.** Python stdlib, vendored. Real code, but
   homogeneous and mature. Effect sizes may not transfer to other languages or
   to a young, actively-changed codebase.
5. **Five cases per type** for most types. Per-type rows are indicative only.
6. **The distractor is one module.** `uuid`, chosen for zero symbol overlap. A
   distractor with overlapping names would create ambiguity this design avoids
   by construction, so the robustness result is a best case for cleanly
   separable distractors.
7. **Case questions are template-generated** from real code. The *code* is real
   (addressing Phase 1's Q4); the *questions* are not organically arising
   developer queries. This is a partial, not full, answer to Q4.
8. **Tariff-dependent cost column.** $0.042/1M input recorded 2026-09-26.
9. **Single run per cell, no repeats.** Phase 1's followup-04 measured repeat
   stability for Jev at 16/16; no repeat measurement was made here, so cell-level
   nondeterminism is unquantified.

## 10. Failures and things that did not work

- **`gen_path2` initially produced 2 cases instead of 7.** A bare-name constraint
  on the intermediate function was too strict for stdlib, where most callees are
  dotted. Relaxed.
- **The admissibility gate caught a benchmark with no comparable cases at all**
  before any run. Required-evidence predicates read `c["caller"]` while the
  schema nests those under `c["params"]`; every predicate raised and was caught
  as `False`, making `struct` admissibility 0/67. This is the strongest
  available evidence that the gate is load-bearing rather than decorative.
- **The gate caught 10 wrong ground truths.** `direct_call` FALSE cases were
  built by enumerating *existing* call edges and labelling them `no`. Every one
  was a real edge.
- **A scorer bug would have hidden the most important comparison.** Pairing on
  the condition-relative `classification` silently dropped all 25
  `lookup_under_struct` cases, because a case that is a `lookup` under structure
  is not `lookup` under raw. The comparison that matters most — judgment
  converted to lookup — was absent from the output until the grouping was made
  intrinsic to the case.
- **Nested-function call edges were initially attributed to the enclosing
  method**, which would have made "does X directly call Y" true whenever a
  closure inside X called Y.

## 11. Smallest justified next experiment

**Enlarge `n` on the two questions that are directionally positive and
underpowered, and add the one mechanism that makes the claim generalisable.
Nothing else.**

Concretely:

1. **Scale the comparable set to ~300 cases** by widening the case-type
   generators (more modules, more call chains, more conjunction targets) rather
   than by loosening the admissibility gate. The pre-registered read stays the
   McNemar exact test on the paired comparable set; with ~300 cases a 3.8pp gap
   becomes detectable, and if it does not survive, that is a real negative.
2. **Add one second bounded-judgment mechanism** so "structure helps judgment"
   is not a statement about `jev-1.13.0` alone. Because the Zen free chat route
   refuses free models, this needs either the direct TypeSafe route with a
   different model id, or the agent route with the followup-05 transport control
   re-measured. The control is mandatory if the agent route is used.
3. **Fix the one mechanism-level weakness first:** `string_literal_probe` shows
   structure can remove required evidence. Before scaling, decide whether the
   intended EDASES pattern is *structure paired with its evidence* — i.e. keep
   the literals in the structural representation. That is a design decision with
   a correctness consequence, and scaling the benchmark before settling it would
   measure the wrong thing.

Deliberately **not** proposed: building R3 (structure + minimal source) before
the accuracy question is resolved; replaying historical sessions; or touching
EDASES architecture. Each would spend budget on a question this phase did not
open.
