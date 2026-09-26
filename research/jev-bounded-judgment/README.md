# Jev bounded-judgment evaluation (EDASES reconnaissance)

**Issue:** #565 · **Status:** `in progress` · **Phase:** 1 of 4 (diagnostic)
**Started:** 2026-09-26

## Question

Does a bounded probabilistic judgment model earn a place in the EDASES decision
hierarchy, and if so where?

Hierarchy under test (not assumed — designed to be falsified):

```
reuse → deterministic computation → specialized reflex
      → generic bounded judgment → cheap general inference → stronger inference
```

Subject: **Jev** (`jev-1.13-free`, TypeSafe AI "System One", served on
`https://opencode.ai/zen/v1/systemone`). Free, ~0.6 s per call.

## Why this is not a generic-classification study

Generic bounded classification is already known to work. The open questions are
*economic and operational*:

1. Which decisions now given to general models are actually bounded judgments?
2. When does Jev beat the cheapest mechanism that precedes it in the hierarchy?
3. Can its uncertainty drive reliable abstention/escalation at a stated error budget?
4. Does deterministic structural preprocessing (AST etc.) reduce required inference?
5. Can repeated successful Jev judgments be compiled down to cheaper reflexes?
6. Which failure modes must an EDASES bounded-judgment layer account for?

The primary metric is **incremental gain over the cheapest preceding mechanism**
and **coverage at a fixed empirical error budget** — not aggregate accuracy.

## Phase 1 scope (~60 cases)

| Area | Content |
|---|---|
| A | Cheap-baseline comparison: measured prior → deterministic rule → lexical baseline → Jev → cheap general model |
| B | Abstention/escalation: coverage vs error at 0.70/0.80/0.90/0.95; coverage at 1/5/10% error budgets |
| C | Contrastive/causal pairs (one deciding fact flips the answer) + irrelevant-change controls |
| D | Foreman-like routing over build/review/investigate/repair/redesign/escalate, legality computed **before** Jev sees the state |

Adversarial controls across A–D where meaningful: option reorder · opaque label
rename · semantically suggestive distractors · evidence removal · noise injection.

## Rules that constrain the work

- Deterministic tooling builds, runs, scores, logs, and compares. Models author
  cases and interpret; they do not compute the numbers.
- **Raw Jev output is preserved, never reduced to pass/fail.** Distribution,
  reported confidence, and selected answer are separate fields.
- Probability ≠ reported confidence ≠ empirical calibration ≠ correctness.
- Ground truth is deterministic or human. **Jev output is never ground truth**;
  any Jev-proposed label is independently validated before use.
- Negative and failed results are preserved, not discarded.
- Contrastive pairs and source families stay in one split (no leakage).
- No extrapolation beyond what a ~60-case sample supports.
- No secrets or personal content. Phase 1 is fully synthetic.
- Do not tune the benchmark to make Jev look good.

## Layout

```
research/jev-bounded-judgment/
  README.md                     # this file
  handoff/RECONNAISSANCE.md     # interface contract, measured, pre-dispatch
  handoff/                      # durable checkpoints
  cases/schema.json             # case + result format (reused by Phases 2–4)
  cases/phase1/                 # ~60 cases
  harness/                      # client, runner, baselines, scorer, NDJSON log
  results/                      # raw + summary
  findings/                     # supported / provisional / limits / counterexamples
```

## Dispatch plan (pending operator approval)

| # | Deliverable | Model | Cost | Rationale |
|---|---|---|---|---|
| W1 | Case/result schema; `systemone` client; runner; rule + lexical baselines; scorer; NDJSON logger | `deepseek-flash` (Zen free) | $0 | well-specified code, little reasoning depth needed |
| W2 | Cases A+B (~30) with deterministic ground truth | `nemotron-general` (Zen free) | $0 | free; family distinct from Jev |
| W3 | Cases C+D (~30): contrastive/control pairs + routing legality | `laguna-general` (Zen free) | $0 | second author family → independence |
| W4 | "Cheap general model" comparison arm | `space-bunny` (Go free) | $0, unlimited, 0-day retention | this is the *evaluated* baseline |
| W5 | Analysis: coverage@error-budget, calibration, order-stability, contrastive flips | deterministic Python; interpretation by `space-bunny` | $0 | evidence-first |
| W6 | Independent review of every material claim | `space-bunny` (≠ W2/W3 family) | $0 | policy: cross-family verdict required |

Catalog refreshed 2026-09-26 (`opencode models --verbose --refresh`).
All six are free-tier; Jev is never used to author the cases that judge it.

## Resume

See `handoff/RECONNAISSANCE.md` for the verified interface contract — in
particular that **Jev is not a chat model** and must be called directly on
`/zen/v1/systemone`, and that `confidence` is a derived function of the
probability vector rather than an independent signal.

**Next step:** operator approval of W1–W6, then dispatch.
