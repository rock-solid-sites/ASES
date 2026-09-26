# Instrument validation: confidence semantics and option-order sensitivity

- **Issue:** #565 · **Date:** 2026-09-26 · **Status:** complete (pre-dispatch)
- **Model:** `jev-1.13-free` via `POST https://opencode.ai/zen/v1/systemone`
- **Calls:** 3 (choice), plus earlier single-scenario noul probes
- **Why:** two design questions had to be answered before building 60 cases,
  because both change how results must be computed and reported.

---

## Harness fact discovered first: the free tier gates on client identity

`urllib` with a default `Python-urllib/3.10` User-Agent → **403 Forbidden**.
`curl` → **200 OK**. Same key, same endpoint, same body.

Fix: send a self-identifying UA and a stable session header, per the Zen/Go
client guidance.

```
User-Agent: edas-bounded-judgment-eval/0.1 (+opencode; research)
x-opencode-session: jev-eval-<random hex>
```

**Consequence for the harness:** it must send these headers on every call, and
must keep one stable session id per conversation. Any 403 in a later run should
be read as a *harness* defect, not as a model or account problem. Recorded here
so this is not rediscovered as a false negative.

---

## Q1 — Is `confidence` independent information?

**Answer: No. It is a deterministic function of the probability vector.**
Reproduced to within output-rounding error on 3/3 calls.

Hypothesis under test: `confidence ≈ (n·max(p) − 1) / (n − 1)`, clamped to [0,1]
(documented by the vendor, who describe it as an approximation for n=3).

State (identical for all three calls):

> CI pipeline run 4821 finished. Job 'build' exited 0. 318 tests passed, 0 failed.
> The deploy step is still queued and has not started.

Six-option Choice: "Which workflow route should be taken next?"

| options[0] | selected | reported `confidence` | `max(p)` reported | formula on reported p | gap | p(max) implied by reported conf |
|---|---|---|---|---|---|---|
| `build` | review | 0.61 | 0.67 | 0.604 | 0.006 | 0.675 |
| `escalate` | review | 0.47 | 0.55 | 0.460 | 0.010 | 0.5583 |
| `repair` | review | 0.54 | 0.61 | 0.532 | 0.008 | 0.6167 |

Raw distributions:

```
order[0]=build     {build .20, repair .00, review .67, escalate .02, redesign .00, investigate .10}
order[0]=escalate  {redesign .00, escalate .01, repair .00, build .34, review .55, investigate .09}
order[0]=repair    {investigate .12, escalate .03, repair .00, redesign .00, review .61, build .24}
```

In every row, inverting the documented formula against the *reported* confidence
yields an unrounded `max(p)` consistent with the rounded probability actually
returned (0.675→0.67, 0.5583→0.55/0.56, 0.6167→0.61). The residual gap is
**entirely explained by 2-decimal rounding of `probabilities` in the response**,
not by a different formula.

### What this means for the program

1. `confidence` carries **no information beyond** `max(probabilities)`. For a
   fixed option count a confidence threshold is a monotone rescaling of a
   max-probability threshold.
2. Its only genuine value is normalising across *differing* option counts — which
   is real, and matters for pooling Area A/B (binary) with Area D (6-way routing)
   into one coverage-at-error-budget curve.
3. Therefore: **never report confidence and max-probability as two corroborating
   signals.** Report both, but state that one is derived from the other. The
   brief's four-way distinction (distribution / reported confidence / empirical
   calibration / correctness) survives — but the *confidence* axis collapses into
   the *distribution* axis. Empirical calibration remains wholly separate and is
   measured by us, not by Jev.
4. Practical corollary: for `noul` there is no confidence field at all, so binary
   decisions have no independent certainty channel. Jev's own docs concede the
   single scalar "is the answer and the certainty in one."

---

## Q4 — Is it order-invariant?

**Answer: the argmax selection was stable; the distribution and confidence were
NOT.** This is the more consequential half.

Three different orderings of the same six options, same state, same question:

| options[0] | selected | `max(p)` | `confidence` |
|---|---|---|---|
| `build` | review | 0.67 | 0.61 |
| `escalate` | review | 0.55 | 0.47 |
| `repair` | review | 0.61 | 0.54 |

- **Selection: STABLE** — `review` in all three. On a clear-cut state, reordering
  options did not change the decision. Encouraging.
- **Distribution: NOT stable** — top probability moved 0.67 → 0.55 → 0.61, a
  **12-point swing** from option ordering alone.
- **Confidence: NOT stable** — 0.61 → 0.47 → 0.54, a **14-point swing**.

### Why this matters more than it first appears

Under a confidence-thresholded abstention policy — the exact policy TypeSafe
recommends, and the one Area B is built to test — this single case would be
**"act" at threshold 0.60 in ordering 1 and "escalate" in orderings 2 and 3.**

So: *argmax stability is not sufficient for operational stability.* A system can
make the same decision every time and still flip between acting and escalating
purely because the options were serialised in a different order. Any EDASES
bounded-judgment interface must therefore either (a) fix a canonical option
order, or (b) threshold on something order-robust, or (c) aggregate over
orderings — and this experiment says which of those is *necessary*, at least for
a 6-way routing decision.

**Caveat, stated plainly:** n=3 orderings, one state, one question type, and the
state was clear-cut with an obvious winner. This is a *mechanism* demonstration
(distribution is order-dependent), **not** an estimate of how often it matters.
The clear-cut case may be the best case for order stability; the near-uniform
ambiguous case in Area D is where instability should be worst, and that is
untested. Do not quote a rate from this.

---

## Status of the open questions from RECONNAISSANCE.md

| # | Question | Status |
|---|---|---|
| Q1 | Does the confidence formula reproduce returned `confidence`? | **Answered: yes, within rounding.** Confidence is derived, not independent. |
| Q2 | Is 0.50-on-no-evidence robust? | **Still open.** Only 1 probe. Needs the Area-B unknowable set. |
| Q3 | Is `noul` calibrated in the frequentist sense? | **Still open.** Needs the full labelled set. |
| Q4 | Order-invariant? | **Partially answered.** argmax stable on a clear-cut case; distribution and confidence demonstrably order-dependent. Rate unknown. |
| Q5 | Latency vs state size | **Still open.** Only ~0.6 s at small sizes observed. |

---

## Next step

Blocked on operator approval of W1–W6. The schema and scorer should encode the
Q1 result from the start: log `probabilities`, `confidence`, and
`confidence_recomputed` side by side, so the derived-ness is auditable in the raw
record rather than asserted in prose.
